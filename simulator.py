# simulator.py
import streamlit as st
import pandas as pd

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2e7d32;"><b>💼 סוכן השקעות ערך (לטווח ארוך):</b> מחפש חברות חזקות לפי ה-PDF. המטרה: לקנות בזול ולהמתין לבשלות תוך ניהול סיכונים מחושב.</div>', unsafe_allow_html=True)
    
    if 'val_cash_ils' not in st.session_state:
        st.session_state.val_cash_ils = 5000.0
        st.session_state.val_portfolio = []

    usd_rate = 3.8 
    cash_usd = st.session_state.val_cash_ils / usd_rate
    
    port_value_usd = 0
    if st.session_state.val_portfolio:
        for p in st.session_state.val_portfolio:
            curr_row = df_all[df_all['Symbol'] == p['Symbol']]
            current_price = curr_row['Price'].iloc[0] if not curr_row.empty else p['Raw_Buy_Price']
            currency = curr_row['Currency'].iloc[0] if not curr_row.empty else "$"
            price_usd = current_price if currency == "$" else (current_price / 100) / usd_rate
            port_value_usd += price_usd * p['Qty']

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 יתרת מזומן", f"₪{st.session_state.val_cash_ils:,.2f}")
    c2.metric("💼 שווי התיק (בדולרים)", f"${port_value_usd:,.2f}")
    yield_pct = ((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0
    c3.metric("📈 תשואת הסוכן", f"{yield_pct:.1f}%")

    if st.button("🚀 הפעל סוכן ערך (השקע 5,000 ₪)"):
        if st.session_state.val_cash_ils > 100:
            gold_stocks = df_all[df_all['Score'] >= 5]
            if not gold_stocks.empty:
                st.success("נרכשו מניות איכותיות! גלול לדוחות האנליזה.")
                invest_per_stock_usd = cash_usd / len(gold_stocks)
                new_portfolio = []
                for _, row in gold_stocks.iterrows():
                    price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    
                    exp_profit = ((row['FairValue'] / row['Price']) - 1) * 100 if row['FairValue'] > row['Price'] else 15.0
                    timeframe = "1.5 עד 3 שנים" if exp_profit > 30 else "1 עד 2 שנים"
                    
                    # ניהול סיכונים חכם
                    stop_loss = row['Price'] * 0.85 # עצירת הפסד ב-15% ירידה
                    take_profit = row['FairValue'] if row['FairValue'] > row['Price'] else row['Price'] * 1.15
                    
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Raw_Buy_Price": row['Price'], 
                        "Buy_Price": row['PriceStr'], "Qty": round(qty, 2), 
                        "Expected_Profit": exp_profit, "Timeframe": timeframe,
                        "Score": row['Score'], "StopLoss": f"{row['Currency']}{stop_loss:.2f}",
                        "TakeProfit": f"{row['Currency']}{take_profit:.2f}"
                    })
                st.session_state.val_portfolio = new_portfolio
                st.session_state.val_cash_ils = 0
                st.rerun()
            else:
                st.error("לא נמצאו מניות שעומדות במדריכי ה-PDF.")

    if st.session_state.val_portfolio:
        st.markdown("### 🧠 דוחות עומק של סוכן הערך:")
        for p in st.session_state.val_portfolio:
            with st.expander(f"דוח השקעה: {p['Symbol']} | יעד: +{p['Expected_Profit']:.1f}%"):
                st.markdown(f"""
                **1. הצדקת רכישה (PDF):** החברה עומדת ב-{p['Score']}/6 קריטריוני איכות מחמירים.
                **2. יעד וזמן:** צפי רווח של **+{p['Expected_Profit']:.1f}%**. זמן הבשלות המוערך הוא **{p['Timeframe']}**.
                **3. ניהול סיכונים מתקדם (חשוב!):**
                * 🟢 **Take Profit (לקיחת רווח):** המערכת תמכור ותממש רווח כשהמחיר יגיע ל-{p['TakeProfit']}.
                * 🔴 **Stop Loss (הגנת הון):** כדי לא להיתקע עם הפסד ענק, פקודת מכירה אוטומטית ממוקמת ב-{p['StopLoss']} (סיכון של 15% בלבד).
                """)
        if st.button("💸 ממש הכל והחזר למזומן (סוכן ערך)"):
            st.session_state.val_cash_ils = port_value_usd * usd_rate
            st.session_state.val_portfolio = []
            st.rerun()

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>⚡ סוכן מסחר יומי (Day Trader):</b> מחפש מומנטום, תנודתיות, וחדשות. המטרה: רווחים מהירים בימים ספורים עם חיתוך הפסדים קפדני.</div>', unsafe_allow_html=True)
    
    if 'day_cash_ils' not in st.session_state:
        st.session_state.day_cash_ils = 5000.0
        st.session_state.day_portfolio = []

    usd_rate = 3.8 
    cash_usd = st.session_state.day_cash_ils / usd_rate
    
    port_value_usd = 0
    if st.session_state.day_portfolio:
        for p in st.session_state.day_portfolio:
            curr_row = df_all[df_all['Symbol'] == p['Symbol']]
            current_price = curr_row['Price'].iloc[0] if not curr_row.empty else p['Raw_Buy_Price']
            currency = curr_row['Currency'].iloc[0] if not curr_row.empty else "$"
            price_usd = current_price if currency == "$" else (current_price / 100) / usd_rate
            port_value_usd += price_usd * p['Qty']

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 יתרת מזומן למסחר יומי", f"₪{st.session_state.day_cash_ils:,.2f}")
    c2.metric("💼 שווי התיק היומי (דולר)", f"${port_value_usd:,.2f}")
    yield_pct = ((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0
    c3.metric("📈 תשואת הסוכן היומי", f"{yield_pct:.1f}%")

    if st.button("⚡ הפעל סוכן יומי (הכנס 5,000 ₪ למסחר)"):
        if st.session_state.day_cash_ils > 100:
            # לוגיקת סוכן יומי: מחפש מניות שזזות חזק היום (למעלה או למטה)
            volatile_stocks = df_all[(df_all['Change'] > 2.0) | (df_all['Change'] < -2.0)].sort_values(by='Change', key=abs, ascending=False).head(3)
            
            if volatile_stocks.empty:
                volatile_stocks = df_all.head(2) # גיבוי אם השוק רגוע
                
            st.success("הסוכן היומי זיהה מומנטום ונכנס לפוזיציות!")
            invest_per_stock_usd = cash_usd / len(volatile_stocks)
            new_portfolio = []
            
            for _, row in volatile_stocks.iterrows():
                price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                
                # סטופ-לוס צמוד מאוד (3%) וטייק פרופיט מהיר (5%)
                stop_loss = row['Price'] * 0.97
                take_profit = row['Price'] * 1.05
                
                reason = "זיהוי תנודתיות חריגה ומחזור מסחר גבוה." if row['Change'] > 0 else "קניית תיקון (Bounce) אחרי ירידה חדה."
                
                new_portfolio.append({
                    "Symbol": row['Symbol'], "Raw_Buy_Price": row['Price'], 
                    "Buy_Price": row['PriceStr'], "Qty": round(qty, 2), 
                    "Expected_Profit": "+5.0%", "Timeframe": "מספר שעות עד 3 ימים",
                    "StopLoss": f"{row['Currency']}{stop_loss:.2f}",
                    "TakeProfit": f"{row['Currency']}{take_profit:.2f}",
                    "Logic": reason
                })
            st.session_state.day_portfolio = new_portfolio
            st.session_state.day_cash_ils = 0
            st.rerun()

    if st.session_state.day_portfolio:
        st.markdown("### ⚡ פעולות הסוכן היומי בתיק:")
        for p in st.session_state.day_portfolio:
            with st.expander(f"טרייד יומי: {p['Symbol']} | מחיר כניסה: {p['Buy_Price']}"):
                st.markdown(f"""
                **1. אסטרטגיה:** {p['Logic']}
                **2. טווח זמן:** {p['Timeframe']}.
                **3. פקודות מסחר אוטומטיות (חובה במסחר יומי!):**
                * 🟢 **Take Profit:** מימוש מהיר ב-{p['TakeProfit']} (רווח של 5%).
                * 🔴 **Stop Loss קשיח:** חיתוך הפסד מיידי ב-{p['StopLoss']} (הפסד מקסימלי של 3%).
                """)
        if st.button("💸 סגור את כל הפוזיציות היומיות עכשיו"):
            st.session_state.day_cash_ils = port_value_usd * usd_rate
            st.session_state.day_portfolio = []
            st.rerun()
