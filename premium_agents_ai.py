# premium_agents_ai.py — סוכני פרימיום עם מחירים חיים
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime


def _get_agent_df(df_all: pd.DataFrame, prefer_short: bool = False) -> pd.DataFrame:
    """מחזיר תוצאות סריקה אוטונומית אם קיימות, אחרת watchlist."""
    needed = ["Symbol","Price","Currency","Score","RSI","Margin",
              "DivYield","PayoutRatio","CashVsDebt","InsiderHeld","TargetUpside"]
    scan_df = st.session_state.get("agent_universe_short_df" if prefer_short
                                    else "agent_universe_df")
    if scan_df is not None and not scan_df.empty:
        have = [c for c in needed if c in scan_df.columns]
        return scan_df[have].copy()
    return df_all



USD_DEFAULT = 3.75


@st.cache_data(ttl=300)
def _usd_rate() -> float:
    try:
        h = yf.Ticker("USDILS=X").history(period="1d")
        if not h.empty:
            return float(h["Close"].iloc[-1])
    except Exception:
        pass
    return USD_DEFAULT


@st.cache_data(ttl=60)
def _live(symbol: str, fallback: float = 0.0) -> float:
    try:
        h = yf.Ticker(symbol).history(period="1d", interval="1m")
        if not h.empty:
            return float(h["Close"].iloc[-1])
    except Exception:
        pass
    return fallback


def _port_val(portfolio, usd_rate):
    total = 0.0
    for p in portfolio:
        try:
            lp = _live(p["Symbol"], p.get("Price_Raw", 0))
            if p.get("Currency") == "$":
                total += lp * usd_rate * p["Qty"]
            else:
                total += (lp / 100) * p["Qty"]
        except Exception:
            pass
    return total


def _init(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


def _record_close_premium(prefix: str, portfolio: list, usd_rate: float, label: str):
    """שומר רווח/הפסד לכל מניה שנמכרה בסוכני פרימיום."""
    for p in portfolio:
        try:
            lp = _live(p["Symbol"], p.get("Price_Raw", 0))
            if p.get("Currency") == "$":
                sell_ils = lp * usd_rate * p["Qty"]
                buy_ils  = p["Price_Raw"] * usd_rate * p["Qty"]
            else:
                sell_ils = (lp / 100) * p["Qty"]
                buy_ils  = (p["Price_Raw"] / 100) * p["Qty"]
            pl     = sell_ils - buy_ils
            pl_pct = ((sell_ils / buy_ils) - 1) * 100 if buy_ils > 0 else 0
            st.session_state[f"{prefix}_closed"].insert(0, {
                "⏰ זמן סגירה":  datetime.now().strftime("%d/%m %H:%M"),
                "📌 סימול":      p["Symbol"],
                "סוכן":          label,
                "מחיר כניסה":   p.get("כניסה", "—"),
                "מחיר יציאה":   f"{p.get('Currency','$')}{lp:.2f}",
                "כמות":          p["Qty"],
                "רווח/הפסד ₪":  round(pl, 2),
                "תשואה %":       round(pl_pct, 2),
                "סטטוס":         "🟢 רווח" if pl >= 0 else "🔴 הפסד",
            })
        except Exception:
            pass


def _show_pnl_premium(prefix: str):
    """מציג לוח סיכום רווח/הפסד של עסקאות סגורות."""
    closed = st.session_state.get(f"{prefix}_closed", [])
    if not closed:
        return
    st.divider()
    st.markdown("### 📊 סיכום עסקאות סגורות")
    total_pnl = sum(t.get("רווח/הפסד ₪", 0) for t in closed)
    wins      = sum(1 for t in closed if t.get("רווח/הפסד ₪", 0) >= 0)
    avg_pct   = sum(t.get("תשואה %", 0) for t in closed) / len(closed)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 רווח/הפסד מצטבר",
                f"{'🟢 +' if total_pnl >= 0 else '🔴 '}₪{abs(total_pnl):,.2f}")
    col2.metric("📈 תשואה ממוצעת",
                f"{'🟢 +' if avg_pct >= 0 else '🔴 '}{abs(avg_pct):.1f}%")
    col3.metric("✅ מרוויחות", str(wins))
    col4.metric("❌ מפסידות",  str(len(closed) - wins))

    with st.expander(f"📋 פירוט עסקאות ({len(closed)})", expanded=False):
        st.dataframe(pd.DataFrame(closed), use_container_width=True, hide_index=True)


def _agent_block(prefix, label, title, desc, run_key, sell_key, reset_key,
                 df_all, usd, filter_fn, reason_fn):
    """בלוק גנרי לכל סוכן פרימיום."""
    _init(f"{prefix}_cash_ils", 5000.0)
    _init(f"{prefix}_portfolio", [])
    _init(f"{prefix}_closed", [])
    _init(f"{prefix}_initial_ils", 5000.0)

    st.markdown(f"### {title}")
    st.caption(desc)

    pv      = _port_val(st.session_state[f"{prefix}_portfolio"], usd)
    initial = st.session_state[f"{prefix}_initial_ils"]
    total   = st.session_state[f"{prefix}_cash_ils"] + pv
    pnl     = total - initial
    pnl_pct = (pnl / initial) * 100 if initial > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 מזומן",         f"₪{st.session_state[f'{prefix}_cash_ils']:,.2f}")
    c2.metric("💼 שווי (חי)",     f"₪{pv:,.2f}")
    c3.metric("📊 שווי כולל",     f"₪{total:,.2f}")
    c4.metric("📈 רווח/הפסד",
              f"{'🟢 +' if pnl >= 0 else '🔴 '}₪{abs(pnl):,.2f}",
              delta=f"{pnl_pct:.1f}%")

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🚀 הפעל", key=run_key, type="primary"):
            if st.session_state[f"{prefix}_cash_ils"] > 100:
                try:
                    cands = filter_fn(df_all)
                except Exception:
                    cands = pd.DataFrame()
                if cands.empty:
                    st.error("לא נמצאו מניות מתאימות.")
                else:
                    inv = (st.session_state[f"{prefix}_cash_ils"] / usd) / len(cands)
                    port, errors = [], []
                    for _, r in cands.iterrows():
                        try:
                            lp  = _live(r["Symbol"], r["Price"])
                            px_u = lp if r["Currency"] == "$" else (lp / 100) / usd
                            qty = round(inv / px_u, 4) if px_u > 0 else 0
                            port.append({"Symbol": r["Symbol"], "Currency": r["Currency"],
                                         "Price_Raw": lp, "Qty": qty,
                                         "כניסה": f"{r['Currency']}{lp:.2f}",
                                         "סיבה": reason_fn(r)})
                        except Exception:
                            errors.append(r["Symbol"])
                    st.session_state[f"{prefix}_portfolio"] = port
                    st.session_state[f"{prefix}_cash_ils"]  = 0
                    msg = f"✅ נקנו {len(port)} מניות!"
                    if errors: msg += f" (⚠️ נכשל: {', '.join(errors)})"
                    st.success(msg)
                    st.rerun()
            else:
                st.warning("אין מזומן מספיק.")

    with b2:
        if st.session_state[f"{prefix}_portfolio"]:
            if st.button("💸 מכור", key=sell_key):
                _record_close_premium(prefix,
                                      st.session_state[f"{prefix}_portfolio"],
                                      usd, label)
                final  = _port_val(st.session_state[f"{prefix}_portfolio"], usd)
                pnl_f  = (final + st.session_state[f"{prefix}_cash_ils"]) - initial
                st.session_state[f"{prefix}_cash_ils"] = (
                    final + st.session_state[f"{prefix}_cash_ils"])
                st.session_state[f"{prefix}_portfolio"] = []
                sign = "🟢 רווח" if pnl_f >= 0 else "🔴 הפסד"
                st.success(f"{sign}: ₪{abs(pnl_f):,.2f} ({(pnl_f/initial)*100:.1f}%)")
                st.rerun()

    with b3:
        if st.button("🔄 איפוס", key=reset_key):
            for k in [f"{prefix}_cash_ils", f"{prefix}_portfolio",
                      f"{prefix}_closed", f"{prefix}_initial_ils"]:
                st.session_state.pop(k, None)
            st.rerun()

    if st.session_state[f"{prefix}_portfolio"]:
        rows = []
        for p in st.session_state[f"{prefix}_portfolio"]:
            try:
                lp = _live(p["Symbol"], p["Price_Raw"])
                rows.append({"סימול": p["Symbol"],
                             "כניסה": p["כניסה"],
                             "נוכחי": f"{p['Currency']}{lp:.2f}",
                             "סיבה": p["סיבה"]})
            except Exception:
                rows.append({"סימול": p.get("Symbol","?"), "שגיאה": "לא ניתן לטעון"})
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    _show_pnl_premium(prefix)


def render_premium_agents(df_all):
    df_long  = _get_agent_df(df_all, prefer_short=False)
    df_short = _get_agent_df(df_all, prefer_short=True)
    st.markdown(
        '<div class="ai-card" style="border-right-color: #ffd700;">'
        '<b>🤖 סוכני פרימיום — מסחר דמו עם מחירים חיים.</b><br>'
        'כל סוכן מקבל ₪5,000 ומפעיל אסטרטגיה ייחודית.</div>',
        unsafe_allow_html=True,
    )

    if df_all.empty:
        st.warning("⚠️ אין נתוני מניות. הוסף מניות ל-Watchlist.")
        return

    usd = _usd_rate()
    t1, t2, t3 = st.tabs(["👑 סוכן דיבידנד", '🕵️ סוכן מנכ"לים', "🚑 סוכן משברים"])

    with t1:
        _agent_block(
            prefix="div", label="👑 דיבידנד",
            title="👑 סוכן דיבידנד — תשואה >2%, חלוקה <60%, מאזן נקי",
            desc="אסטרטגיה: חברות שמחלקות דיבידנד עקבי עם מאזן חזק.",
            run_key="div_run", sell_key="div_sell", reset_key="div_reset",
            df_all=df_long, usd=usd,
            filter_fn=lambda d: d[(d["DivYield"] > 2) &
                                   (d["PayoutRatio"].between(1, 60)) &
                                   (d["CashVsDebt"] == "✅")],
            reason_fn=lambda r: f"תשואה {r['DivYield']:.1f}% | חלוקה {r['PayoutRatio']:.0f}%",
        )

    with t2:
        _agent_block(
            prefix="ins", label='🕵️ מנכ"לים',
            title='🕵️ סוכן מנכ"לים — הנהלה >2% + אפסייד >10%',
            desc="אסטרטגיה: מנהלים שמחזיקים מניות — סימן לאמון בחברה.",
            run_key="ins_run", sell_key="ins_sell", reset_key="ins_reset",
            df_all=df_long, usd=usd,
            filter_fn=lambda d: d[(d["InsiderHeld"] >= 2) & (d["TargetUpside"] > 10)],
            reason_fn=lambda r: f"הנהלה {r['InsiderHeld']:.1f}% | אפסייד +{r['TargetUpside']:.1f}%",
        )

    with t3:
        _agent_block(
            prefix="deep", label="🚑 משברים",
            title="🚑 סוכן משברים — ציון 3+, RSI<35, מאזן נקי",
            desc="אסטרטגיה: קנייה בפאניקה. חברות איכותיות שנמכרות ביתר.",
            run_key="deep_run", sell_key="deep_sell", reset_key="deep_reset",
            df_all=df_short, usd=usd,
            filter_fn=lambda d: d[(d["Score"] >= 3) & (d["RSI"] < 35) &
                                   (d["CashVsDebt"] == "✅")],
            reason_fn=lambda r: f"RSI {r['RSI']:.0f} פאניקה | ציון {r['Score']}/6 | מאזן ✅",
        )
