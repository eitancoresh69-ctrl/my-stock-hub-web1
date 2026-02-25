# simulator.py
import streamlit as st
import pandas as pd

def render_paper_trading(df_all):
    st.markdown('<div class="ai-card"><b>🤖 סוכן מסחר חכם (Paper Trading):</b> הסוכן קיבל 5,000 ש"ח. הוא יקנה מניות לפי עקרונות ה-PDF, ויסביר את תחזית הרווח וזמן ההמתנה.</div>', unsafe_allow_html=True)
    
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

    if st.button("🚀 הפעל סוכן AI להשקעה אוטומטית (5,000 ₪)"):
        if st.session_state.cash_ils > 100:
            gold_stocks = df_all[df_all['Score'] >= 5]
            if not gold_stocks.empty:
                st.success("הסוכן זיהה מניות מעולות! מבצע רכישה...")
                invest_per_stock_usd = cash_usd / len(gold_stocks)
                new_portfolio = []
                for _, row in gold_stocks.iterrows():
                    price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    
                    # חישוב רווח ומסגרת זמן (Timeframe)
                    if row['FairValue'] > row['Price']:
                        exp_profit = ((row['FairValue'] / row['Price']) - 1) * 100
                        # הערכת זמן מבוססת השקעות ערך: רווח גדול דורש יותר זמן בשלות
                        if exp_profit > 30:
                            timeframe = "1.5 עד 3 שנים"
                        elif exp_profit > 15:
                            timeframe = "12 עד 18 חודשים"
                        else:
                            timeframe = "6 עד 12 חודשים"
                    else:
                        exp_profit = 12.0 # רווח סולידי למניית צמיחה מעולה
                        timeframe = "1 עד 2 שנים"
                        
                    reason = f"החברה עומדת ב-{row['Score']}/6 קריטריוני ה-PDF. נרכשה ב-{row['PriceStr']}. צפי לעלייה של 🟢 {exp_profit:.1f}% כדי להגיע לשווי ההוגן. צפי זמן לבשלות: ⏳ {timeframe}."
                    
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Raw_Buy_Price": row['Price'], 
                        "Buy_Price": row['PriceStr'], "Qty": round(qty, 2), 
                        "Expected_Profit": f"+{exp_profit:.1f}%", "AI_Explanation": reason
                    })
                st.session_state.ai_portfolio = new_portfolio
                st.session_state.cash_ils = 0
                st.rerun()
            else:
                st.error("ה-AI לא מצא כרגע חברות שעומדות בציון 5 או 6. הכסף נשמר במזומן.")

    if st.session_state.ai_portfolio:
        st.markdown("### 📊 תיק הסוכן ותחזיות (מבוסס השקעות ערך):")
        display_df = pd.DataFrame(st.session_state.ai_portfolio)[["Symbol", "Buy_Price", "Expected_Profit", "AI_Explanation"]]
        st.dataframe(
            display_df, 
            column_config={
                "Symbol": "סימול",
                "Buy_Price": "קנייה",
                "Expected_Profit": "יעד רווח",
                "AI_Explanation": st.column_config.TextColumn("למה ה-AI קנה? (כולל צפי זמן)", width="large")
            }, 
            use_container_width=True, hide_index=True
        )
        if st.button("💸 ממש רווחים והחזר למזומן"):
            st.session_state.cash_ils = port_value_usd * usd_rate
            st.session_state.ai_portfolio = []
            st.rerun()
