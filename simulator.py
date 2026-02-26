# simulator.py
import streamlit as st
import pandas as pd

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2e7d32;"><b>💼 סוכן השקעות ערך (טווח ארוך):</b> סורק את ה-PDF ומחפש מניות יציבות בנקודת כניסה טכנית טובה.</div>', unsafe_allow_html=True)
    
    if 'val_cash_ils' not in st.session_state:
        st.session_state.val_cash_ils, st.session_state.val_portfolio = 5000.0, []
    
    if 'val_receipt' in st.session_state: 
        st.info(st.session_state.val_receipt)

    usd_rate = 3.8 
    cash_usd = st.session_state.val_cash_ils / usd_rate
    port_value_usd = 0
    if st.session_state.val_portfolio:
        for p in st.session_state.val_portfolio:
            stock_data = df_all[df_all['Symbol'] == p['Symbol']]
            if not stock_data.empty:
                current_price = stock_data['Price'].iloc[0]
                if p['Currency'] != "$": current_price = (current_price / 100) / usd_rate
                port_value_usd += p['Qty'] * current_price

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 יתרת מזומן", f"₪{st.session_state.val_cash_ils:,.2f}")
    c2.metric("💼 שווי התיק (דולר)", f"${port_value_usd:,.2f}")
    c3.metric("📈 תשואה פתוחה", f"{((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0:.1f}%")

    if st.button("🚀 הפעל סוכן ערך"):
        if st.session_state.val_cash_ils > 100:
            if 'val_receipt' in st.session_state: del st.session_state.val_receipt
            # סינון מניות איכותיות (ציון 5 ומעלה)
            gold_stocks = df_all[df_all['Score'] >= 5]
            if not gold_stocks.empty:
                inv_per_stock = cash_usd / len(gold_stocks)
                new_port = []
                for _, r in gold_stocks.iterrows():
                    px_usd = r['Price'] if r['Currency'] == "$" else (r['Price']/100)/usd_rate
                    qty = inv_per_stock / px_usd if px_usd > 0 else 0
                    new_port.append({"Symbol": r['Symbol'], "Currency": r['Currency'], "Buy_Price": r['PriceStr'], "Qty": round(qty, 2)})
                st.session_state.val_portfolio = new_port
                st.session_state.val_cash_ils = 0
                st.rerun()
            else:
                st.error("ה-AI לא מצא חברות חזקות מספיק העומדות בקריטריונים כרגע.")

    if st.session_state.val_portfolio:
        if st.button("💸 סגור עסקאות וחשב רווח/הפסד"):
            profit_ils = (port_value_usd * usd_rate) - 5000.0
            st.session_state.val_cash_ils, st.session_state.val_portfolio = 5000.0, []
            st.session_state.val_receipt = f"✅ התיק נסגר. סך רווח/הפסד נטו: ₪{profit_ils:.2f}"
            st.rerun()

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>⚡ סוכן מסחר יומי (Day Trader):</b> מתמקד במומנטום ותנודתיות.</div>', unsafe_allow_html=True)
    
    if 'day_cash_ils' not in st.session_state:
        st.session_state.day_cash_ils, st.session_state.day_portfolio = 5000.0, []
    
    if 'day_receipt' in st.session_state: 
        st.info(st.session_state.day_receipt)

    usd_rate = 3.8 
    cash_usd = st.session_state.day_cash_ils / usd_rate
    port_value_usd = 0
    if st.session_state.day_portfolio:
        for p in st.session_state.day_portfolio:
            stock_data = df_all[df_all['Symbol'] == p['Symbol']]
            if not stock_data.empty:
                current_price = stock_data['Price'].iloc[0]
                if p['Currency'] != "$": current_price = (current_price / 100) / usd_rate
                port_value_usd += p['Qty'] * current_price

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 מזומן יומי", f"₪{st.session_state.day_cash_ils:,.2f}")
    c2.metric("💼 שווי פוזיציות", f"${port_value_usd:,.2f}")
    c3.metric("📈 תשואה יומית", f"{((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0:.1f}%")

    if st.button("⚡ הפעל סוכן יומי"):
        if st.session_state.day_cash_ils > 100:
            if 'day_receipt' in st.session_state: del st.session_state.day_receipt
            # סינון מניות לפי RSI (מומנטום)
            momentum_stocks = df_all[(df_all['RSI'] < 40) | (df_all['RSI'] > 65)].head(3)
            if not momentum_stocks.empty:
                inv_per_stock = cash_usd / len(momentum_stocks)
                new_port = []
                for _, r in momentum_stocks.iterrows():
                    px_usd = r['Price'] if r['Currency'] == "$" else (r['Price']/100)/usd_rate
                    qty = inv_per_stock / px_usd if px_usd > 0 else 0
                    new_port.append({"Symbol": r['Symbol'], "Currency": r['Currency'], "Buy_Price": r['PriceStr'], "Qty": round(qty, 2)})
                st.session_state.day_portfolio = new_port
                st.session_state.day_cash_ils = 0
                st.rerun()
            else:
                st.warning("השוק לא מספק כרגע איתותים ברורים למסחר יומי.")

    if st.session_state.day_portfolio:
        if st.button("💸 סגור פוזיציות יומיות"):
            profit_ils = (port_value_usd * usd_rate) - 5000.0
            st.session_state.day_cash_ils, st.session_state.day_portfolio = 5000.0, []
            st.session_state.day_receipt = f"⚡ הטרייד נסגר. סך רווח/הפסד: ₪{profit_ils:.2f}"
            st.rerun()
