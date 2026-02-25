# simulator.py
import streamlit as st
import pandas as pd

def render_paper_trading(df_all):
    st.markdown('<div class="ai-card"><b>🤖 סוכן המסחר האישי שלך (Paper Trading):</b> הופקדו 5,000 ש"ח וירטואליים. ה-AI מנתח את השוק ומרכיב עבורך את התיק האופטימלי בזמן אמת.</div>', unsafe_allow_html=True)
    
    # הגדרת תקציב ראשוני
    if 'cash_ils' not in st.session_state:
        st.session_state.cash_ils = 5000.0
        st.session_state.ai_portfolio = []

    usd_rate = 3.8 # שער חליפין משוער
    cash_usd = st.session_state.cash_ils / usd_rate
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 יתרת מזומן (שקלים)", f"₪{st.session_state.cash_ils:,.2f}")
    col2.metric("💵 כוח קנייה (דולרים)", f"${cash_usd:,.2f}")
    col3.metric("💼 שווי התיק המושקע", f"${sum([p['Total_Value'] for p in st.session_state.ai_portfolio]):,.2f}")

    if st.button("🚀 הפעל סוכן AI להשקעה אוטומטית (Invest Now)"):
        if st.session_state.cash_ils > 100:
            # ה-AI בוחר את מניות הזהב (ציון 5-6)
            gold_stocks = df_all[df_all['Score'] >= 5]
            if not gold_stocks.empty:
                st.success("הסוכן סרק את השוק ומצא הזדמנויות! מבצע קנייה...")
                invest_per_stock = cash_usd / len(gold_stocks)
                
                new_portfolio = []
                for _, row in gold_stocks.iterrows():
                    qty = invest_per_stock / row['Price']
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Buy_Price": row['Price'], 
                        "Qty": qty, "Total_Value": invest_per_stock
                    })
                
                st.session_state.ai_portfolio = new_portfolio
                st.session_state.cash_ils = 0 # כל הכסף הושקע
                st.rerun()
            else:
                st.error("ה-AI לא מצא מניות שעומדות בקריטריונים כרגע. הכסף נשאר במזומן.")

    if st.session_state.ai_portfolio:
        st.markdown("### 📊 התיק שהסוכן בנה עבורך:")
        st.dataframe(pd.DataFrame(st.session_state.ai_portfolio), use_container_width=True)
        if st.button("💸 מכור הכל והחזר למזומן"):
            st.session_state.cash_ils = sum([p['Total_Value'] for p in st.session_state.ai_portfolio]) * usd_rate
            st.session_state.ai_portfolio = []
            st.rerun()
