# simulator.py
import streamlit as st
import pandas as pd

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2e7d32;"><b>💼 סוכן השקעות ערך (טווח ארוך):</b> סורק את ה-PDF ומחפש מניות יציבות.</div>', unsafe_allow_html=True)
    
    if 'val_cash_ils' not in st.session_state:
        st.session_state.val_cash_ils = 5000.0
        st.session_state.val_portfolio = []

    if 'val_last_receipt' in st.session_state:
        st.info(st.session_state.val_last_receipt)

    usd_rate = 3.8 
    cash_usd = st.session_state.val_cash_ils / usd_rate
    port_value_usd = sum([p['Qty'] * (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] if p['Currency'] == "$" else (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] / 100) / usd_rate) for p in st.session_state.val_portfolio]) if st.session_state.val_portfolio else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 יתרת מזומן", f"₪{st.session_state.val_cash_ils:,.2f}")
    c2.metric("💼 שווי התיק (דולר)", f"${port_value_usd:,.2f}")
    c3.metric("📈 תשואה פתוחה", f"{((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0:.1f}%")

    if st.button("🚀 הפעל סוכן ערך (השקע 5,000 ₪)"):
        if st.session_state.val_cash_ils > 100:
            if 'val_last_receipt' in st.session_state: del st.session_state.val_last_receipt
            gold_stocks = df_all[(df_all['Score'] >= 5) & (df_all['RSI'] > 35)]
            if not gold_stocks.empty:
                invest_per_stock_usd = cash_usd / len(gold_stocks)
                new_portfolio = []
                for _, row in gold_stocks.iterrows():
                    price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    stop_loss = row['Price'] * 0.85 
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Currency": row['Currency'], "Buy_Price": row['PriceStr'], 
                        "Qty": round(qty, 2), "StopLoss": f"{row['Currency']}{stop_loss:.2f}"
                    })
                st.session_state.val_portfolio = new_portfolio
                st.session_state.val_cash_ils = 0
                st.rerun()
            else:
                st.error("ה-AI לא מצא חברות מספיק חזקות כרגע.")

    if st.session_state.val_portfolio:
        for p in st.session_state.val_portfolio:
            st.write(f"**{p['Symbol']}** | קנייה: {p['Buy_Price']} | הגנה: {p['StopLoss']}")
        if st.button("💸 ממש הכל וסגור עסקאות"):
            final_value_ils = port_value_usd * usd_rate
            net_profit = final_value_ils - 5000.0
            st.session_state.val_cash_ils = 5000.0 # מחזיר לתקציב התחלתי
            st.session_state.val_portfolio = []
            if net_profit >= 0:
                st.session_state.val_last_receipt = f"✅ העסקאות נסגרו ברווח של ₪{net_profit:.2f}!"
            else:
                st.session_state.val_last_receipt = f"🔻 העסקאות נסגרו בהפסד של ₪{abs(net_profit):.2f}."
            st.rerun()

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>⚡ סוכן מסחר יומי (Day Trader):</b> מתמקד רק במומנטום ותנודתיות.</div>', unsafe_allow_html=True)
    
    if 'day_cash_ils' not in st.session_state:
        st.session_state.day_cash_ils = 5000.0
        st.session_state.day_portfolio = []

    if 'day_last_receipt' in st.session_state:
        st.info(st.session_state.day_last_receipt)

    usd_rate = 3.8 
    cash_usd = st.session_state.day_cash_ils / usd_rate
    port_value_usd = sum([p['Qty'] * (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] if p['Currency'] == "$" else (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] / 100) / usd_rate) for p in st.session_state.day_portfolio]) if st.session_state.day_portfolio else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 מזומן יומי", f"₪{st.session_state.day_cash_ils:,.2f}")
    c2.metric("💼 שווי פוזיציות", f"${port_value_usd:,.2f}")
    c3.metric("📈 תשואה יומית", f"{((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0:.1f}%")

    if st.button("⚡ הפעל סוכן יומי"):
        if st.session_state.day_cash_ils > 100:
            if 'day_last_receipt' in st.session_state: del st.session_state.day_last_receipt
            momentum_stocks = df_all[(df_all['RSI'] < 40) | ((df_all['RSI'] > 65) & (df_all['Price'] > df_all['MA50']))].head(3)
            if not momentum_stocks.empty:
                invest_per_stock_usd = cash_usd / len(momentum_stocks)
                new_portfolio = []
                for _, row in momentum_stocks.iterrows():
                    price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Currency": row['Currency'], "Buy_Price": row['PriceStr'], "Qty": round(qty, 2)
                    })
                st.session_state.day_portfolio = new_portfolio
                st.session_state.day_cash_ils = 0
                st.rerun()

    if st.session_state.day_portfolio:
        for p in st.session_state.day_portfolio:
            st.write(f"**{p['Symbol']}** | קנייה: {p['Buy_Price']}")
        if st.button("💸 סגור פוזיציות יומיות"):
            final_value_ils = port_value_usd * usd_rate
            net_profit = final_value_ils - 5000.0
            st.session_state.day_cash_ils = 5000.0
            st.session_state.day_portfolio = []
            if net_profit >= 0:
                st.session_state.day_last_receipt = f"⚡ הטרייד היומי נסגר ברווח של ₪{net_profit:.2f}!"
            else:
                st.session_state.day_last_receipt = f"🔻 הטרייד היומי נחתך בהפסד של ₪{abs(net_profit):.2f} (הגנת הון הופעלה)."
            st.rerun()
