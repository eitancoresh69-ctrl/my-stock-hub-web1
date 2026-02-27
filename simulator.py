# simulator.py — מסחר דמו עם נתוני בורסה בזמן אמת
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

USD_RATE_DEFAULT = 3.75


def _get_usd_rate() -> float:
    """שולף שער דולר/שקל חי."""
    try:
        h = yf.Ticker("USDILS=X").history(period="1d")
        if not h.empty:
            return float(h["Close"].iloc[-1])
    except Exception:
        pass
    return USD_RATE_DEFAULT


def _get_live_price(symbol: str) -> float | None:
    """שולף מחיר חי של מניה."""
    try:
        h = yf.Ticker(symbol).history(period="1d", interval="1m")
        if not h.empty:
            return float(h["Close"].iloc[-1])
    except Exception:
        pass
    return None


def _init_demo_state(prefix: str, initial_ils: float = 5000.0):
    """מאתחל Session State לסוכן דמו."""
    for key, val in [
        (f"{prefix}_cash_ils", initial_ils),
        (f"{prefix}_portfolio", []),
        (f"{prefix}_trades_log", []),
        (f"{prefix}_initial_ils", initial_ils),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val


def _calc_portfolio_value(prefix: str, usd_rate: float) -> float:
    """מחשב שווי תיק נוכחי לפי מחירים חיים."""
    total = 0.0
    for p in st.session_state.get(f"{prefix}_portfolio", []):
        live_px = _get_live_price(p["Symbol"]) or p["Buy_Price_Raw"]
        if p["Currency"] == "$":
            total += live_px * usd_rate * p["Qty"]
        else:
            total += (live_px / 100) * p["Qty"]
    return total


def _show_portfolio_table(prefix: str, usd_rate: float):
    """מציג טבלת פוזיציות עם מחירים חיים."""
    port = st.session_state.get(f"{prefix}_portfolio", [])
    if not port:
        return
    rows = []
    for p in port:
        live_px = _get_live_price(p["Symbol"]) or p["Buy_Price_Raw"]
        buy_raw = p["Buy_Price_Raw"]
        if p["Currency"] == "$":
            px_ils = live_px * usd_rate
            buy_ils = buy_raw * usd_rate
        else:
            px_ils = live_px / 100
            buy_ils = buy_raw / 100
        pl = (px_ils - buy_ils) * p["Qty"]
        pl_pct = ((px_ils / buy_ils) - 1) * 100 if buy_ils > 0 else 0
        rows.append({
            "📌 מניה": p["Symbol"],
            "כמות": p["Qty"],
            "מחיר קנייה": f"{p['Currency']}{buy_raw:.2f}",
            "מחיר נוכחי (חי🔴)": f"{p['Currency']}{live_px:.2f}",
            "שווי כולל ₪": f"₪{px_ils * p['Qty']:,.2f}",
            "רווח/הפסד": f"{'🟢 +' if pl >= 0 else '🔴 '}₪{abs(pl):,.2f}",
            "תשואה %": f"{'🟢 +' if pl_pct >= 0 else '🔴 '}{pl_pct:.1f}%",
            "🤖 סיבת כניסה": p.get("Reason", "—"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# סוכן השקעות ערך
# ─────────────────────────────────────────────
def render_value_agent(df_all: pd.DataFrame):
    st.markdown(
        '<div class="ai-card" style="border-right-color: #2e7d32;">'
        '<b>💼 סוכן השקעות ערך — מסחר דמו בנתוני זמן אמת</b><br>'
        'סורק מניות "זהב" (ציון PDF 5-6) וקונה לפי מחיר שוק חי.</div>',
        unsafe_allow_html=True,
    )

    _init_demo_state("val")
    usd_rate = _get_usd_rate()

    port_ils = _calc_portfolio_value("val", usd_rate)
    initial = st.session_state["val_initial_ils"]
    total = st.session_state["val_cash_ils"] + port_ils
    pnl = total - initial
    pnl_pct = (pnl / initial) * 100 if initial > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 מזומן", f"₪{st.session_state['val_cash_ils']:,.2f}")
    c2.metric("💼 שווי מניות (חי)", f"₪{port_ils:,.2f}")
    c3.metric("📊 שווי כולל", f"₪{total:,.2f}")
    c4.metric("📈 רווח/הפסד", f"{'🟢 +' if pnl >= 0 else '🔴 '}₪{abs(pnl):,.2f}",
              delta=f"{pnl_pct:.1f}%")
    st.caption(f"💱 שער דולר/שקל חי: ₪{usd_rate:.3f}")

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("🚀 הפעל סוכן ערך", type="primary", key="val_run"):
            if st.session_state["val_cash_ils"] > 100 and not df_all.empty:
                gold = df_all[df_all["Score"] >= 5]
                if gold.empty:
                    st.error("ה-AI לא מצא מניות 'זהב' (ציון 5+) כרגע.")
                else:
                    budget = st.session_state["val_cash_ils"]
                    inv_per = budget / len(gold)
                    new_port = []
                    for _, r in gold.iterrows():
                        live_px = _get_live_price(r["Symbol"]) or r["Price"]
                        if r["Currency"] == "$":
                            qty = (inv_per / usd_rate) / live_px
                        else:
                            qty = inv_per / (live_px / 100)
                        qty = round(qty, 4)
                        reason = (
                            f"ציון PDF {r['Score']}/6 | "
                            f"שולי רווח {r['Margin']:.1f}% | "
                            f"RSI {r['RSI']:.0f} | "
                            f"כניסה חי: {r['Currency']}{live_px:.2f}"
                        )
                        new_port.append({
                            "Symbol": r["Symbol"],
                            "Currency": r["Currency"],
                            "Buy_Price_Raw": live_px,
                            "Buy_Time": datetime.now().strftime("%H:%M:%S"),
                            "Qty": qty,
                            "Reason": reason,
                        })
                        st.session_state["val_trades_log"].insert(0, {
                            "⏰ זמן": datetime.now().strftime("%H:%M:%S"),
                            "📌 סימול": r["Symbol"],
                            "↔️": "קנייה 🟢",
                            "💰 מחיר חי": f"{r['Currency']}{live_px:.2f}",
                            "🔢 כמות": round(qty, 4),
                            "💵 ₪": f"₪{inv_per:,.2f}",
                        })
                    st.session_state["val_portfolio"] = new_port
                    st.session_state["val_cash_ils"] = 0
                    st.success(f"✅ נקנו {len(new_port)} מניות!")
                    st.rerun()
            else:
                st.warning("אין מזומן מספיק או נתונים.")

    with b2:
        if st.session_state["val_portfolio"]:
            if st.button("💸 מכור הכל", key="val_sell"):
                final = _calc_portfolio_value("val", usd_rate)
                pnl_f = (final + st.session_state["val_cash_ils"]) - initial
                for p in st.session_state["val_portfolio"]:
                    lp = _get_live_price(p["Symbol"]) or p["Buy_Price_Raw"]
                    st.session_state["val_trades_log"].insert(0, {
                        "⏰ זמן": datetime.now().strftime("%H:%M:%S"),
                        "📌 סימול": p["Symbol"],
                        "↔️": "מכירה 🔴",
                        "💰 מחיר חי": f"{p['Currency']}{lp:.2f}",
                        "🔢 כמות": p["Qty"],
                        "💵 ₪": "—",
                    })
                st.session_state["val_cash_ils"] = final + st.session_state["val_cash_ils"]
                st.session_state["val_portfolio"] = []
                sign = "🟢 רווח" if pnl_f >= 0 else "🔴 הפסד"
                st.success(f"{sign}: ₪{abs(pnl_f):,.2f} ({(pnl_f/initial)*100:.1f}%)")
                st.rerun()

    with b3:
        if st.button("🔄 איפוס", key="val_reset"):
            st.session_state["val_cash_ils"] = 5000.0
            st.session_state["val_portfolio"] = []
            st.session_state["val_trades_log"] = []
            st.session_state["val_initial_ils"] = 5000.0
            st.rerun()

    if st.session_state["val_portfolio"]:
        st.markdown("### 📋 פוזיציות פתוחות (מחירים חיים):")
        _show_portfolio_table("val", usd_rate)

    if st.session_state["val_trades_log"]:
        with st.expander(f"📜 לוג עסקאות ({len(st.session_state['val_trades_log'])})"):
            st.dataframe(pd.DataFrame(st.session_state["val_trades_log"]),
                         use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# סוכן מסחר יומי
# ─────────────────────────────────────────────
def render_day_trade_agent(df_all: pd.DataFrame):
    st.markdown(
        '<div class="ai-card" style="border-right-color: #d32f2f;">'
        '<b>⚡ סוכן מסחר יומי — דמו עם נתוני זמן אמת</b><br>'
        'מומנטום RSI. קונה בנפילות, מוכר בזינוקים. מחירים חיים מהבורסה.</div>',
        unsafe_allow_html=True,
    )

    _init_demo_state("day")
    usd_rate = _get_usd_rate()

    port_ils = _calc_portfolio_value("day", usd_rate)
    initial = st.session_state["day_initial_ils"]
    total = st.session_state["day_cash_ils"] + port_ils
    pnl = total - initial
    pnl_pct = (pnl / initial) * 100 if initial > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 מזומן יומי", f"₪{st.session_state['day_cash_ils']:,.2f}")
    c2.metric("💼 שווי פוזיציות (חי)", f"₪{port_ils:,.2f}")
    c3.metric("📊 שווי כולל", f"₪{total:,.2f}")
    c4.metric("⚡ תשואה", f"{'🟢 +' if pnl >= 0 else '🔴 '}₪{abs(pnl):,.2f}",
              delta=f"{pnl_pct:.1f}%")
    st.caption(f"💱 שער דולר/שקל: ₪{usd_rate:.3f}")

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("⚡ הפעל סוכן יומי", type="primary", key="day_run"):
            if st.session_state["day_cash_ils"] > 100 and not df_all.empty:
                momentum = df_all[(df_all["RSI"] < 35) | (df_all["RSI"] > 65)].head(3)
                if momentum.empty:
                    st.warning("השוק שקט. אין מומנטום ברור כרגע.")
                else:
                    budget = st.session_state["day_cash_ils"]
                    inv_per = budget / len(momentum)
                    new_port = []
                    for _, r in momentum.iterrows():
                        live_px = _get_live_price(r["Symbol"]) or r["Price"]
                        if r["Currency"] == "$":
                            qty = (inv_per / usd_rate) / live_px
                        else:
                            qty = inv_per / (live_px / 100)
                        qty = round(qty, 4)
                        if r["RSI"] < 35:
                            reason = f"🟢 RSI {r['RSI']:.0f} — מכירת יתר. ציפייה להיפוך. כניסה חי: {r['Currency']}{live_px:.2f}"
                        else:
                            reason = f"🚀 RSI {r['RSI']:.0f} — פריצת מומנטום. כניסה חי: {r['Currency']}{live_px:.2f}"
                        new_port.append({
                            "Symbol": r["Symbol"],
                            "Currency": r["Currency"],
                            "Buy_Price_Raw": live_px,
                            "Buy_Time": datetime.now().strftime("%H:%M:%S"),
                            "Qty": qty,
                            "Reason": reason,
                        })
                        st.session_state["day_trades_log"].insert(0, {
                            "⏰ זמן": datetime.now().strftime("%H:%M:%S"),
                            "📌 סימול": r["Symbol"],
                            "↔️": "קנייה 🟢",
                            "💰 מחיר חי": f"{r['Currency']}{live_px:.2f}",
                            "🔢 כמות": round(qty, 4),
                            "💵 ₪": f"₪{inv_per:,.2f}",
                        })
                    st.session_state["day_portfolio"] = new_port
                    st.session_state["day_cash_ils"] = 0
                    st.success(f"⚡ נפתחו {len(new_port)} פוזיציות!")
                    st.rerun()
            else:
                st.warning("אין מזומן מספיק.")

    with b2:
        if st.session_state["day_portfolio"]:
            if st.button("💸 סגור פוזיציות", key="day_sell"):
                final = _calc_portfolio_value("day", usd_rate)
                pnl_f = (final + st.session_state["day_cash_ils"]) - initial
                for p in st.session_state["day_portfolio"]:
                    lp = _get_live_price(p["Symbol"]) or p["Buy_Price_Raw"]
                    st.session_state["day_trades_log"].insert(0, {
                        "⏰ זמן": datetime.now().strftime("%H:%M:%S"),
                        "📌 סימול": p["Symbol"],
                        "↔️": "מכירה 🔴",
                        "💰 מחיר חי": f"{p['Currency']}{lp:.2f}",
                        "🔢 כמות": p["Qty"],
                        "💵 ₪": "—",
                    })
                st.session_state["day_cash_ils"] = final + st.session_state["day_cash_ils"]
                st.session_state["day_portfolio"] = []
                sign = "🟢 רווח" if pnl_f >= 0 else "🔴 הפסד"
                st.success(f"{sign} יומי: ₪{abs(pnl_f):,.2f} ({(pnl_f/initial)*100:.1f}%)")
                st.rerun()

    with b3:
        if st.button("🔄 איפוס יומי", key="day_reset"):
            st.session_state["day_cash_ils"] = 5000.0
            st.session_state["day_portfolio"] = []
            st.session_state["day_trades_log"] = []
            st.session_state["day_initial_ils"] = 5000.0
            st.rerun()

    if st.session_state["day_portfolio"]:
        st.markdown("### 📋 פוזיציות פתוחות (מחירים חיים):")
        _show_portfolio_table("day", usd_rate)

    if st.session_state["day_trades_log"]:
        with st.expander(f"📜 לוג עסקאות ({len(st.session_state['day_trades_log'])})"):
            st.dataframe(pd.DataFrame(st.session_state["day_trades_log"]),
                         use_container_width=True, hide_index=True)
