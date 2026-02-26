# simulator.py
import streamlit as st
import pandas as pd
from datetime import datetime

def _calc_port_value(portfolio, df_all, usd_rate):
    """חישוב שווי תיק נוכחי בדולרים"""
    total = 0
    for p in portfolio:
        rows = df_all[df_all['Symbol'] == p['Symbol']]
        if not rows.empty:
            price = rows.iloc[0]['Price']
            if p['Currency'] != "$":
                price = (price / 100) / usd_rate
            total += p['Qty'] * price
    return round(total, 2)

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2e7d32;"><b>💼 סוכן השקעות ערך (טווח ארוך):</b> סורק את ה-PDF, מנתח את <b>הדוחות הכספיים ההיסטוריים</b> של השנים האחרונות, ומחפש מניות יציבות בנקודת כניסה נוחה.</div>', unsafe_allow_html=True)

    # בדיקת מתג השמדה
    if st.session_state.get('kill_switch_active', False):
        st.error("🚨 מתג השמדה פעיל! סוכן הערך מושהה. גש לטאב 'מנגנון הגנה' כדי לאפס.")
        return

    if 'val_cash_ils' not in st.session_state:
        st.session_state.val_cash_ils = 5000.0
        st.session_state.val_portfolio = []
        st.session_state.val_start_capital = 5000.0
        st.session_state.val_sessions = []

    usd_rate = 3.8
    start_capital = st.session_state.val_start_capital
    cash_usd = st.session_state.val_cash_ils / usd_rate
    port_value_usd = _calc_port_value(st.session_state.val_portfolio, df_all, usd_rate) if st.session_state.val_portfolio and not df_all.empty else 0

    # חישוב רווח/הפסד בזמן אמת
    total_value_ils = (cash_usd + port_value_usd) * usd_rate
    total_pl_ils = total_value_ils - start_capital
    total_pct = (total_pl_ils / start_capital) * 100 if start_capital > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 יתרת מזומן", f"₪{st.session_state.val_cash_ils:,.2f}")
    c2.metric("💼 שווי התיק (דולר)", f"${port_value_usd:,.2f}")
    c3.metric("📈 רווח/הפסד פתוח", f"₪{total_pl_ils:,.2f}", delta=f"{total_pct:.1f}%")
    c4.metric("🏦 סך הכל", f"₪{total_value_ils:,.2f}")

    # הגדרת הון התחלתי
    col_cap, col_btn = st.columns(2)
    with col_cap:
        new_cap = st.number_input("💰 הון התחלתי (₪)", min_value=500.0, max_value=500000.0,
                                   value=float(start_capital), step=500.0, key="val_cap")
        if st.button("🔄 עדכן הון", key="val_update_cap"):
            st.session_state.val_start_capital = new_cap
            st.session_state.val_cash_ils = new_cap
            st.session_state.val_portfolio = []
            if 'val_receipt' in st.session_state: del st.session_state.val_receipt
            st.rerun()

    # הצג קבלה מסשן קודם
    if 'val_receipt' in st.session_state:
        st.success(st.session_state.val_receipt)

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if not st.session_state.val_portfolio:
            if st.button("🚀 הפעל סוכן ערך", type="primary", key="val_start"):
                if st.session_state.val_cash_ils > 100:
                    if 'val_receipt' in st.session_state: del st.session_state.val_receipt
                    gold_stocks = df_all[(df_all['Score'] >= 5) & (df_all['RSI'] > 35)]
                    if not gold_stocks.empty:
                        st.success("הסוכן סרק את הדוחות ההיסטוריים וזיהה מניות שעומדות במבחן הזמן! רוכש כעת...")
                        invest_per_stock_usd = cash_usd / len(gold_stocks)
                        new_portfolio = []
                        for _, row in gold_stocks.iterrows():
                            price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                            qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                            exp_profit = ((row['FairValue'] / row['Price']) - 1) * 100 if row['FairValue'] > row['Price'] else 15.0
                            stop_loss = row['Price'] * 0.85
                            reason = f"החברה קיבלה {row['Score']}/6 ב-PDF. סריקת דוחות העבר שלה מאשרת עמידות. ה-RSI הוא {row['RSI']:.0f} (כניסה בטוחה). יעד רווח: {exp_profit:.1f}%."
                            new_portfolio.append({
                                "Symbol": row['Symbol'], "Currency": row['Currency'],
                                "Raw_Buy_Price": row['Price'], "Buy_Price": row['PriceStr'],
                                "Qty": round(qty, 2), "Expected_Profit": exp_profit,
                                "StopLoss": f"{row['Currency']}{stop_loss:.2f}",
                                "AI_Explanation": reason,
                                "Buy_Time": datetime.now().strftime("%H:%M")
                            })
                        st.session_state.val_portfolio = new_portfolio
                        st.session_state.val_cash_ils = 0
                        st.rerun()
                    else:
                        st.error("ה-AI לא מצא חברות חזקות מספיק שעומדות בהיסטוריית הדוחות כרגע.")
        else:
            if st.button("💸 עצור מסחר והצג סיכום רווח/הפסד", type="primary", key="val_stop"):
                port_usd_now = _calc_port_value(st.session_state.val_portfolio, df_all, usd_rate)
                profit_usd = port_usd_now - (start_capital / usd_rate)
                profit_ils = profit_usd * usd_rate
                pct_final = (profit_usd / (start_capital / usd_rate)) * 100 if (start_capital / usd_rate) > 0 else 0

                # שמור סשן להיסטוריה
                session_record = {
                    "📅 תאריך": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "🏦 הון התחלתי": f"₪{start_capital:,.2f}",
                    "💰 שווי סיום": f"₪{port_usd_now * usd_rate:,.2f}",
                    "📈 רווח/הפסד": f"₪{profit_ils:,.2f}",
                    "📊 תשואה": f"{pct_final:.1f}%",
                    "🏷️ מניות": ", ".join([p['Symbol'] for p in st.session_state.val_portfolio])
                }
                st.session_state.val_sessions.insert(0, session_record)

                emoji = "🎉" if profit_ils >= 0 else "📉"
                st.session_state.val_receipt = (
                    f"{emoji} **סשן הסתיים!** | "
                    f"הון: ₪{start_capital:,.2f} → סיום: ₪{port_usd_now * usd_rate:,.2f} | "
                    f"**רווח/הפסד: ₪{profit_ils:,.2f} ({pct_final:+.1f}%)**"
                )
                st.session_state.val_cash_ils = start_capital
                st.session_state.val_portfolio = []
                st.rerun()

    # תיק פתוח
    if st.session_state.val_portfolio:
        st.subheader("📋 פוזיציות פתוחות — סוכן ערך")
        rows_display = []
        for p in st.session_state.val_portfolio:
            match = df_all[df_all['Symbol'] == p['Symbol']]
            if not match.empty:
                curr_price = match.iloc[0]['Price']
                buy_price = p['Raw_Buy_Price']
                pct_p = ((curr_price / buy_price) - 1) * 100 if buy_price > 0 else 0
                rows_display.append({
                    "סימול": p['Symbol'], "כמות": p['Qty'],
                    "מחיר קנייה": p['Buy_Price'], "מחיר נוכחי": match.iloc[0]['PriceStr'],
                    "תשואה": f"{pct_p:+.1f}%", "מגמה": "📈" if pct_p >= 0 else "📉",
                    "יעד": f"+{p['Expected_Profit']:.1f}%", "Stop Loss": p['StopLoss']
                })
        if rows_display:
            st.dataframe(pd.DataFrame(rows_display), use_container_width=True, hide_index=True)

        for p in st.session_state.val_portfolio:
            with st.expander(f"דוח רכישה מורחב: {p['Symbol']} | יעד: +{p['Expected_Profit']:.1f}%"):
                st.markdown(f"**ניתוח פונדמנטלי (PDF + דוחות היסטוריים):** {p['AI_Explanation']}\n\n**הגנת הון (Stop-Loss):** ימכור אוטומטית בירידה ל-{p['StopLoss']}.")

    # היסטוריית סשנים
    if st.session_state.val_sessions:
        with st.expander(f"📜 היסטוריית סשנים — סוכן ערך ({len(st.session_state.val_sessions)} סשנים)"):
            df_sessions = pd.DataFrame(st.session_state.val_sessions)
            st.dataframe(df_sessions, use_container_width=True, hide_index=True)
            try:
                total_profit = sum([float(s["📈 רווח/הפסד"].replace("₪","").replace(",","")) for s in st.session_state.val_sessions])
                st.metric("💰 רווח/הפסד מצטבר מכל הסשנים", f"₪{total_profit:,.2f}")
            except: pass
            if st.button("🗑️ נקה היסטוריה", key="val_clear_hist"):
                st.session_state.val_sessions = []
                st.rerun()


def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>⚡ סוכן מסחר יומי (Day Trader):</b> לא מתעניין בדוחות היסטוריים. מתמקד רק במומנטום, תנודתיות, פריצות RSI ומחזורי מסחר כדי לייצר רווח מהיר.</div>', unsafe_allow_html=True)

    # בדיקת מתג השמדה
    if st.session_state.get('kill_switch_active', False):
        st.error("🚨 מתג השמדה פעיל! סוכן המסחר היומי מושהה. גש לטאב 'מנגנון הגנה' כדי לאפס.")
        return

    if 'day_cash_ils' not in st.session_state:
        st.session_state.day_cash_ils = 5000.0
        st.session_state.day_portfolio = []
        st.session_state.day_start_capital = 5000.0
        st.session_state.day_sessions = []

    usd_rate = 3.8
    start_capital = st.session_state.day_start_capital
    cash_usd = st.session_state.day_cash_ils / usd_rate
    port_value_usd = _calc_port_value(st.session_state.day_portfolio, df_all, usd_rate) if st.session_state.day_portfolio and not df_all.empty else 0

    # חישוב רווח/הפסד בזמן אמת
    total_value_ils = (cash_usd + port_value_usd) * usd_rate
    total_pl_ils = total_value_ils - start_capital
    total_pct = (total_pl_ils / start_capital) * 100 if start_capital > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 מזומן יומי", f"₪{st.session_state.day_cash_ils:,.2f}")
    c2.metric("💼 שווי פוזיציות", f"${port_value_usd:,.2f}")
    c3.metric("⚡ רווח/הפסד פתוח", f"₪{total_pl_ils:,.2f}", delta=f"{total_pct:.1f}%")
    c4.metric("🏦 סך הכל", f"₪{total_value_ils:,.2f}")

    # הגדרת הון
    col_cap2, col_btn2 = st.columns(2)
    with col_cap2:
        new_cap2 = st.number_input("💰 הון (₪)", min_value=500.0, max_value=500000.0,
                                    value=float(start_capital), step=500.0, key="day_cap")
        if st.button("🔄 עדכן הון", key="day_update_cap"):
            st.session_state.day_start_capital = new_cap2
            st.session_state.day_cash_ils = new_cap2
            st.session_state.day_portfolio = []
            if 'day_receipt' in st.session_state: del st.session_state.day_receipt
            st.rerun()

    if 'day_receipt' in st.session_state:
        st.success(st.session_state.day_receipt)

    with col_btn2:
        st.markdown("<br>", unsafe_allow_html=True)
        if not st.session_state.day_portfolio:
            if st.button("⚡ הפעל סוכן יומי (מומנטום)", type="primary", key="day_start"):
                if st.session_state.day_cash_ils > 100:
                    if 'day_receipt' in st.session_state: del st.session_state.day_receipt
                    momentum_stocks = df_all[(df_all['RSI'] < 40) | ((df_all['RSI'] > 65) & (df_all['Price'] > df_all['MA50']))].head(3)
                    if not momentum_stocks.empty:
                        invest_per_stock_usd = cash_usd / len(momentum_stocks)
                        new_portfolio = []
                        for _, row in momentum_stocks.iterrows():
                            price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                            qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                            stop_loss = row['Price'] * 0.96
                            take_profit = row['Price'] * 1.06
                            reason = f"מומנטום טכני: RSI עומד על {row['RSI']:.0f}. " + ("מכירת יתר, צפי לפול-באק." if row['RSI'] < 40 else "פריצת התנגדות ומומנטום חיובי.")
                            new_portfolio.append({
                                "Symbol": row['Symbol'], "Currency": row['Currency'],
                                "Raw_Buy_Price": row['Price'], "Buy_Price": row['PriceStr'],
                                "Qty": round(qty, 2), "Logic": reason,
                                "StopLoss": f"{row['Currency']}{stop_loss:.2f}",
                                "TakeProfit": f"{row['Currency']}{take_profit:.2f}",
                                "Buy_Time": datetime.now().strftime("%H:%M")
                            })
                        st.session_state.day_portfolio = new_portfolio
                        st.session_state.day_cash_ils = 0
                        st.rerun()
                    else:
                        st.warning("השוק לא מספק כרגע תבניות ברורות למסחר יומי.")
        else:
            if st.button("💸 עצור מסחר יומי והצג סיכום", type="primary", key="day_stop"):
                port_usd_now = _calc_port_value(st.session_state.day_portfolio, df_all, usd_rate)
                profit_usd = port_usd_now - (start_capital / usd_rate)
                profit_ils = profit_usd * usd_rate
                pct_final = (profit_usd / (start_capital / usd_rate)) * 100 if (start_capital / usd_rate) > 0 else 0

                session_record = {
                    "📅 תאריך": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "🏦 הון התחלתי": f"₪{start_capital:,.2f}",
                    "💰 שווי סיום": f"₪{port_usd_now * usd_rate:,.2f}",
                    "📈 רווח/הפסד": f"₪{profit_ils:,.2f}",
                    "📊 תשואה": f"{pct_final:.1f}%",
                    "🏷️ מניות": ", ".join([p['Symbol'] for p in st.session_state.day_portfolio])
                }
                st.session_state.day_sessions.insert(0, session_record)

                emoji = "🎉" if profit_ils >= 0 else "📉"
                st.session_state.day_receipt = (
                    f"{emoji} **סשן יומי הסתיים!** | "
                    f"הון: ₪{start_capital:,.2f} → סיום: ₪{port_usd_now * usd_rate:,.2f} | "
                    f"**רווח/הפסד: ₪{profit_ils:,.2f} ({pct_final:+.1f}%)**"
                )
                st.session_state.day_cash_ils = start_capital
                st.session_state.day_portfolio = []
                st.rerun()

    # טריידים פתוחים
    if st.session_state.day_portfolio:
        st.subheader("📋 טריידים פתוחים — סוכן יומי")
        rows_display = []
        for p in st.session_state.day_portfolio:
            match = df_all[df_all['Symbol'] == p['Symbol']]
            if not match.empty:
                curr_price = match.iloc[0]['Price']
                buy_price = p['Raw_Buy_Price']
                pct_p = ((curr_price / buy_price) - 1) * 100 if buy_price > 0 else 0
                rows_display.append({
                    "סימול": p['Symbol'], "כמות": p['Qty'],
                    "כניסה": p['Buy_Price'], "נוכחי": match.iloc[0]['PriceStr'],
                    "P/L": f"{pct_p:+.1f}%", "": "📈" if pct_p >= 0 else "📉",
                    "Stop": p['StopLoss'], "יעד": p['TakeProfit']
                })
        if rows_display:
            st.dataframe(pd.DataFrame(rows_display), use_container_width=True, hide_index=True)

        for p in st.session_state.day_portfolio:
            with st.expander(f"טרייד יומי: {p['Symbol']}"):
                st.markdown(f"**סיבת כניסה:** {p['Logic']}\n\n**הגנות:** רווח ב-{p['TakeProfit']} | חיתוך הפסד ב-{p['StopLoss']}.")

    # היסטוריית סשנים
    if st.session_state.day_sessions:
        with st.expander(f"📜 היסטוריית טריידים יומיים ({len(st.session_state.day_sessions)} סשנים)"):
            df_sessions = pd.DataFrame(st.session_state.day_sessions)
            st.dataframe(df_sessions, use_container_width=True, hide_index=True)
            try:
                total_profit = sum([float(s["📈 רווח/הפסד"].replace("₪","").replace(",","")) for s in st.session_state.day_sessions])
                st.metric("💰 רווח/הפסד מצטבר", f"₪{total_profit:,.2f}")
            except: pass
            if st.button("🗑️ נקה היסטוריה", key="day_clear_hist"):
                st.session_state.day_sessions = []
                st.rerun()
