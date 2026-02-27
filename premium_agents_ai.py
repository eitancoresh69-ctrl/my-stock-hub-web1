# premium_agents_ai.py — סוכני פרימיום עם מחירים חיים
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

USD_DEFAULT = 3.75


def _usd_rate():
    try:
        h = yf.Ticker("USDILS=X").history(period="1d")
        if not h.empty:
            return float(h["Close"].iloc[-1])
    except Exception:
        pass
    return USD_DEFAULT


def _live(symbol, fallback):
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
        lp = _live(p["Symbol"], p.get("Price_Raw", 0))
        if p.get("Currency") == "$":
            total += lp * usd_rate * p["Qty"]
        else:
            total += (lp / 100) * p["Qty"]
    return total


def _init(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


def render_premium_agents(df_all):
    st.markdown(
        '<div class="ai-card" style="border-right-color: #ffd700;">'
        '<b>🤖 סוכני פרימיום — מסחר דמו עם מחירים חיים.</b><br>'
        'כל סוכן מקבל ₪5,000 ומפעיל אסטרטגיה ייחודית.</div>',
        unsafe_allow_html=True,
    )

    usd = _usd_rate()
    t1, t2, t3 = st.tabs(["👑 סוכן דיבידנד", "🕵️ סוכן מנכ\"לים", "🚑 סוכן משברים"])

    # ─── דיבידנד ───
    with t1:
        _init("div_cash_ils", 5000.0); _init("div_portfolio", [])
        st.markdown("### 👑 סוכן דיבידנד — תשואה >2%, חלוקה <60%, מאזן נקי")
        pv = _port_val(st.session_state["div_portfolio"], usd)
        c1, c2 = st.columns(2)
        c1.metric("💵 מזומן", f"₪{st.session_state['div_cash_ils']:,.2f}")
        c2.metric("💼 שווי (חי)", f"₪{pv:,.2f}")

        if st.button("🚀 הפעל", key="div_run", type="primary"):
            if st.session_state["div_cash_ils"] > 100:
                cands = df_all[(df_all["DivYield"] > 2) & (df_all["PayoutRatio"].between(1, 60)) &
                               (df_all["CashVsDebt"] == "✅")]
                if not cands.empty:
                    inv = (st.session_state["div_cash_ils"] / usd) / len(cands)
                    port = []
                    for _, r in cands.iterrows():
                        lp = _live(r["Symbol"], r["Price"])
                        px_u = lp if r["Currency"] == "$" else (lp / 100) / usd
                        qty = round(inv / px_u, 4) if px_u > 0 else 0
                        port.append({"Symbol": r["Symbol"], "Currency": r["Currency"],
                                     "Price_Raw": lp, "Qty": qty,
                                     "כניסה": f"{r['Currency']}{lp:.2f}",
                                     "סיבה": f"תשואה {r['DivYield']:.1f}% | חלוקה {r['PayoutRatio']:.0f}%"})
                    st.session_state["div_portfolio"] = port
                    st.session_state["div_cash_ils"] = 0
                    st.success(f"✅ נקנו {len(port)} מניות דיבידנד!")
                    st.rerun()
                else:
                    st.error("לא נמצאו מניות בטוחות.")

        if st.session_state["div_portfolio"]:
            rows = [{"סימול": p["Symbol"], "כניסה": p["כניסה"],
                     "נוכחי": f"{p['Currency']}{_live(p['Symbol'], p['Price_Raw']):.2f}",
                     "סיבה": p["סיבה"]} for p in st.session_state["div_portfolio"]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            if st.button("💸 מכור", key="div_sell"):
                st.session_state["div_cash_ils"] = pv * usd
                st.session_state["div_portfolio"] = []
                st.rerun()

    # ─── מנכ"לים ───
    with t2:
        _init("ins_cash_ils", 5000.0); _init("ins_portfolio", [])
        st.markdown("### 🕵️ סוכן מנכ\"לים — הנהלה >2% + אפסייד >10%")
        pv = _port_val(st.session_state["ins_portfolio"], usd)
        c1, c2 = st.columns(2)
        c1.metric("💵 מזומן", f"₪{st.session_state['ins_cash_ils']:,.2f}")
        c2.metric("💼 שווי (חי)", f"₪{pv:,.2f}")

        if st.button("🚀 הפעל", key="ins_run", type="primary"):
            if st.session_state["ins_cash_ils"] > 100:
                cands = df_all[(df_all["InsiderHeld"] >= 2) & (df_all["TargetUpside"] > 10)]
                if not cands.empty:
                    inv = (st.session_state["ins_cash_ils"] / usd) / len(cands)
                    port = []
                    for _, r in cands.iterrows():
                        lp = _live(r["Symbol"], r["Price"])
                        px_u = lp if r["Currency"] == "$" else (lp / 100) / usd
                        qty = round(inv / px_u, 4) if px_u > 0 else 0
                        port.append({"Symbol": r["Symbol"], "Currency": r["Currency"],
                                     "Price_Raw": lp, "Qty": qty,
                                     "כניסה": f"{r['Currency']}{lp:.2f}",
                                     "סיבה": f"הנהלה {r['InsiderHeld']:.1f}% | אפסייד +{r['TargetUpside']:.1f}%"})
                    st.session_state["ins_portfolio"] = port
                    st.session_state["ins_cash_ils"] = 0
                    st.success(f"✅ נקנו {len(port)} מניות!")
                    st.rerun()
                else:
                    st.error("לא נמצאו מניות עם איתותי פנים.")

        if st.session_state["ins_portfolio"]:
            rows = [{"סימול": p["Symbol"], "כניסה": p["כניסה"],
                     "נוכחי": f"{p['Currency']}{_live(p['Symbol'], p['Price_Raw']):.2f}",
                     "סיבה": p["סיבה"]} for p in st.session_state["ins_portfolio"]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            if st.button("💸 מכור", key="ins_sell"):
                st.session_state["ins_cash_ils"] = pv * usd
                st.session_state["ins_portfolio"] = []
                st.rerun()

    # ─── משברים ───
    with t3:
        _init("deep_cash_ils", 5000.0); _init("deep_portfolio", [])
        st.markdown("### 🚑 סוכן משברים — ציון 3+, RSI<35, מאזן נקי")
        pv = _port_val(st.session_state["deep_portfolio"], usd)
        c1, c2 = st.columns(2)
        c1.metric("💵 מזומן", f"₪{st.session_state['deep_cash_ils']:,.2f}")
        c2.metric("💼 שווי (חי)", f"₪{pv:,.2f}")

        if st.button("🚀 הפעל", key="deep_run", type="primary"):
            if st.session_state["deep_cash_ils"] > 100:
                cands = df_all[(df_all["Score"] >= 3) & (df_all["RSI"] < 35) &
                               (df_all["CashVsDebt"] == "✅")]
                if not cands.empty:
                    inv = (st.session_state["deep_cash_ils"] / usd) / len(cands)
                    port = []
                    for _, r in cands.iterrows():
                        lp = _live(r["Symbol"], r["Price"])
                        px_u = lp if r["Currency"] == "$" else (lp / 100) / usd
                        qty = round(inv / px_u, 4) if px_u > 0 else 0
                        port.append({"Symbol": r["Symbol"], "Currency": r["Currency"],
                                     "Price_Raw": lp, "Qty": qty,
                                     "כניסה": f"{r['Currency']}{lp:.2f}",
                                     "סיבה": f"RSI {r['RSI']:.0f} פאניקה | ציון {r['Score']}/6 | מאזן ✅"})
                    st.session_state["deep_portfolio"] = port
                    st.session_state["deep_cash_ils"] = 0
                    st.success(f"✅ קנינו {len(port)} מניות בפאניקה!")
                    st.rerun()
                else:
                    st.error("לא נמצאו מניות בפאניקה מספיקה.")

        if st.session_state["deep_portfolio"]:
            rows = [{"סימול": p["Symbol"], "כניסה": p["כניסה"],
                     "נוכחי": f"{p['Currency']}{_live(p['Symbol'], p['Price_Raw']):.2f}",
                     "סיבה": p["סיבה"]} for p in st.session_state["deep_portfolio"]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            if st.button("💸 מכור", key="deep_sell"):
                st.session_state["deep_cash_ils"] = pv * usd
                st.session_state["deep_portfolio"] = []
                st.rerun()
