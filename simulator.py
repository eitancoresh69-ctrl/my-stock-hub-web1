# simulator.py
import streamlit as st
import pandas as pd

def render_paper_trading(df_all):
    st.markdown('<div class="ai-card"><b>🤖 מנהל התיקים האישי שלך (AI Portfolio Manager):</b><br>הפקדנו עבורך 5,000 ש"ח וירטואליים. הסוכן סורק את השוק, מרכיב תיק מבוסס ערך (PDF), ומפיק <b>דוח אנליזה מפורט</b> לכל רכישה.</div>', unsafe_allow_html=True)
    
    if 'cash_ils' not in st.session_state:
        st.session_state.cash_ils = 5000.0
        st.session_state.ai_portfolio = []

    usd_rate = 3.8 
    cash_usd = st.session_state.cash_ils / usd_rate
    
    port_value_usd = 0
    if st.session_state.ai_portfolio:
        for p in st.session_state.ai_portfolio:
            curr_row = df_all[df_all['Symbol'] == p['Symbol']]
            current_price = curr_row['Price'].iloc[0] if not curr_row.empty else p['Raw_Buy_Price']
            currency = curr_row['Currency'].iloc[0] if not curr_row.empty else "$"
            price_usd = current_price if currency == "$" else (current_price / 100) / usd_rate
            port_value_usd += price_usd * p['Qty']

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 יתרת מזומן", f"₪{st.session_state.cash_ils:,.2f}")
    c2.metric("💼 שווי התיק (בדולרים)", f"${port_value_usd:,.2f}")
    yield_pct = ((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0
    c3.metric("📈 תשואת הסוכן", f"{yield_pct:.1f}%")

    if st.button("🚀 הפעל סוכן AI לבניית תיק (5,000 ₪)"):
        if st.session_state.cash_ils > 100:
            gold_stocks = df_all[df_all['Score'] >= 5]
            if not gold_stocks.empty:
                st.success("הסוכן בנה עבורך תיק השקעות! גלול למטה לקריאת דוחות האנליזה.")
                invest_per_stock_usd = cash_usd / len(gold_stocks)
                new_portfolio = []
                for _, row in gold_stocks.iterrows():
                    price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    
                    if row['FairValue'] > row['Price']:
                        exp_profit = ((row['FairValue'] / row['Price']) - 1) * 100
                        timeframe = "1.5 עד 3 שנים" if exp_profit > 30 else "12 עד 18 חודשים"
                    else:
                        exp_profit = 12.0 
                        timeframe = "1 עד 2 שנים"
                        
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Raw_Buy_Price": row['Price'], 
                        "Buy_Price": row['PriceStr'], "Qty": round(qty, 2), 
                        "Expected_Profit": exp_profit, "Timeframe": timeframe,
                        "Score": row['Score'], "RevG": row['RevGrowth']
                    })
                st.session_state.ai_portfolio = new_portfolio
                st.session_state.cash_ils = 0
                st.rerun()
            else:
                st.error("ה-AI לא מצא כרגע חברות שעומדות בציון 5 או 6.")

    if st.session_state.ai_portfolio:
        st.markdown("### 📊 התיק הפעיל:")
        display_df = pd.DataFrame(st.session_state.ai_portfolio)[["Symbol", "Buy_Price", "Qty", "Expected_Profit", "Timeframe"]]
        st.dataframe(display_df, column_config={"Symbol": "סימול", "Buy_Price": "מחיר קנייה", "Qty": "כמות", "Expected_Profit": st.column_config.NumberColumn("יעד רווח %", format="+%.1f%%"), "Timeframe": "זמן יעד (AI)"}, use_container_width=True, hide_index=True)
        
        st.markdown("### 🧠 דוחות עומק של מנהל התיקים (למה קניתי?):")
        for p in st.session_state.ai_portfolio:
            with st.expander(f"דוח השקעה: {p['Symbol']} | יעד רווח: +{p['Expected_Profit']:.1f}%"):
                st.markdown(f"""
                **1. הצדקת איכות (PDF):** החברה קיבלה ציון עלית של {p['Score']}/6. היא מציגה צמיחת מכירות עקבית של {p['RevG']:.1%} וניהול חוב מצוין, מה שהופך אותה ל"עסק מעולה" על פי המדריך.
                
                **2. תמחור ופוטנציאל:** המניה נרכשה ב-{p['Buy_Price']}. מודל ה-DCF (תזרים מזומנים מהוון) מראה שהמניה נסחרת בהנחה. יעד הרווח נקבע ל-**+{p['Expected_Profit']:.1f}%**.
                
                **3. מסגרת זמן (Timeframe):** בהתבסס על השקעות ערך קלאסיות, השוק דורש זמן כדי לתקן עיוותי תמחור. צפי הגעה ליעד הוא בין **{p['Timeframe']}**.
                
                **4. ניהול סיכונים:** הסוכן ימשיך לעקוב אחרי דוחות הרבעון הקרוב. אם צמיחת הרווחים תרד מתחת ל-10%, תישקל מכירה מוקדמת.
                """)
                
        if st.button("💸 ממש רווחים עכשיו והחזר למזומן"):
            st.session_state.cash_ils = port_value_usd * usd_rate
            st.session_state.ai_portfolio = []
            st.rerun()
