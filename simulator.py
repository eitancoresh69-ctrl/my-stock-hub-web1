# simulator.py
import streamlit as st
import pandas as pd

def render_paper_trading(df_all):
    st.markdown('<div class="ai-card"><b>🤖 סוכן המסחר האישי שלך (Paper Trading):</b> הופקדו 5,000 ש"ח. ה-AI סורק את השוק, קונה מניות שעומדות במדריכי ה-PDF ומציג צפי רווח.</div>', unsafe_allow_html=True)
    
    if 'cash_ils' not in st.session_state:
        st.session_state.cash_ils = 5000.0
        st.session_state.ai_portfolio = []

    usd_rate = 3.8 # שער להמרה דולר-שקל
    cash_usd = st.session_state.cash_ils / usd_rate
    
    # חישוב שווי התיק העדכני
    port_value_usd = 0
    if st.session_state.ai_portfolio:
        for p in st.session_state.ai_portfolio:
            current_price = df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] if not df_all[df_all['Symbol'] == p['Symbol']].empty else p['Raw_Buy_Price']
            currency = df_all[df_all['Symbol'] == p['Symbol']]['Currency'].iloc[0] if not df_all[df_all['Symbol'] == p['Symbol']].empty else "$"
            
            # המרה לדולרים לשם השווי הכולל
            price_usd = current_price if currency == "$" else (current_price / 100) / usd_rate
            port_value_usd += price_usd * p['Qty']

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 יתרת מזומן פנוי", f"₪{st.session_state.cash_ils:,.2f}")
    col2.metric("💼 שווי התיק (בדולרים)", f"${port_value_usd:,.2f}")
    yield_pct = ((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0
    col3.metric("📈 תשואת הסוכן", f"{yield_pct:.1f}%")

    if st.button("🚀 הפעל סוכן AI להשקעה אוטומטית (Invest 5,000 ILS)"):
        if st.session_state.cash_ils > 100:
            gold_stocks = df_all[df_all['Score'] >= 5]
            if not gold_stocks.empty:
                st.success("הסוכן זיהה מניות שעומדות ב-5-6 קריטריונים מה-PDF! מבצע קנייה...")
                invest_per_stock_usd = cash_usd / len(gold_stocks)
                
                new_portfolio = []
                for _, row in gold_stocks.iterrows():
                    sym = row['Symbol']
                    price = row['Price']
                    currency = row['Currency']
                    fv = row.get('FairValue', 0)
                    score = row['Score']
                    
                    price_usd = price if currency == "$" else (price / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    
                    # חישוב רווח עתידי
                    if fv > price:
                        exp_profit_pct = ((fv / price) - 1) * 100
                    else:
                        exp_profit_pct = 15.0 # תחזית אופטימית למניות צמיחה
                        
                    # בניית הסבר מפורט שביקשת
                    reason = f"נרכשה כי עמדה ב-{score}/6 קריטריוני איכות. "
                    if fv > price:
                        reason += f"מתומחרת בחסר מול השווי ההוגן העומד על {currency}{fv:.2f}. "
                    reason += f"צפי רווח עתידי שמזהה ה-AI: 🟢 +{exp_profit_pct:.1f}%."

                    new_portfolio.append({
                        "Symbol": sym, 
                        "Raw_Buy_Price": price,
                        "Buy_Price": f"{currency}{price:,.2f}", 
                        "Qty": round(qty, 2), 
                        "Expected_Profit": f"+{exp_profit_pct:.1f}%",
                        "AI_Explanation": reason
                    })
                
                st.session_state.ai_portfolio = new_portfolio
                st.session_state.cash_ils = 0
                st.rerun()
            else:
                st.error("ה-AI לא מצא מניות שעומדות בקריטריונים המחמירים. הכסף נשמר במזומן.")

    if st.session_state.ai_portfolio:
        st.markdown("### 📊 התיק שהסוכן בנה עבורך והתחזיות שלו:")
        display_df = pd.DataFrame(st.session_state.ai_portfolio)[["Symbol", "Buy_Price", "Qty", "Expected_Profit", "AI_Explanation"]]
        st.dataframe(
            display_df, 
            column_config={
                "Symbol": "סימול",
                "Buy_Price": "מחיר קנייה (עם מטבע)",
                "Qty": "כמות",
                "Expected_Profit": "רווח עתידי צפוי %",
                "AI_Explanation": st.column_config.TextColumn("ניתוח פעולה (מדוע ה-AI קנה?)", width="large")
            },
            use_container_width=True, hide_index=True
        )
        if st.button("💸 ממש רווחים והחזר למזומן"):
            st.session_state.cash_ils = port_value_usd * usd_rate
            st.session_state.ai_portfolio = []
            st.rerun()
