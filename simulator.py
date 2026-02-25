# simulator.py
import streamlit as st
import pandas as pd

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2e7d32;"><b>💼 סוכן השקעות ערך (פונדמנטלי + טכני):</b> דורש חברה שעומדת ב-PDF, אבל נכנס לעסקה רק אם הניתוח הטכני מסמן שהתחתית מאחורינו (RSI יציב ומגמה חיובית).</div>', unsafe_allow_html=True)
    
    if 'val_cash_ils' not in st.session_state:
        st.session_state.val_cash_ils = 5000.0
        st.session_state.val_portfolio = []

    usd_rate = 3.8 
    cash_usd = st.session_state.val_cash_ils / usd_rate
    port_value_usd = sum([p['Qty'] * (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] if p['Currency'] == "$" else (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] / 100) / usd_rate) for p in st.session_state.val_portfolio]) if st.session_state.val_portfolio else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 יתרת מזומן", f"₪{st.session_state.val_cash_ils:,.2f}")
    c2.metric("💼 שווי התיק", f"${port_value_usd:,.2f}")
    c3.metric("📈 תשואה", f"{((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0:.1f}%")

    if st.button("🚀 הפעל סוכן ערך חכם (5,000 ₪)"):
        if st.session_state.val_cash_ils > 100:
            # ה-AI מוסיף פילטר טכני: רוצה מניות זהב (5-6) שלא נמצאות בהתרסקות מוחלטת (RSI > 35)
            gold_stocks = df_all[(df_all['Score'] >= 5) & (df_all['RSI'] > 35)]
            if not gold_stocks.empty:
                invest_per_stock_usd = cash_usd / len(gold_stocks)
                new_portfolio = []
                for _, row in gold_stocks.iterrows():
                    price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    
                    exp_profit = ((row['FairValue'] / row['Price']) - 1) * 100 if row['FairValue'] > row['Price'] else 15.0
                    stop_loss = row['Price'] * 0.85 
                    
                    reason = f"עומדת ב-{row['Score']}/6 ב-PDF. מבחינה טכנית, ה-RSI הוא {row['RSI']:.0f} (לא בתמחור יתר מסוכן). המחיר הוא {row['PriceStr']} ויש לה צפי עלייה של {exp_profit:.1f}%."
                    
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Currency": row['Currency'], "Raw_Buy_Price": row['Price'], 
                        "Buy_Price": row['PriceStr'], "Qty": round(qty, 2), "Expected_Profit": exp_profit, 
                        "StopLoss": f"{row['Currency']}{stop_loss:.2f}", "AI_Explanation": reason
                    })
                st.session_state.val_portfolio = new_portfolio
                st.session_state.val_cash_ils = 0
                st.rerun()
            else:
                st.error("ה-AI לא מצא הזדמנויות שעומדות גם ב-PDF וגם בנקודת כניסה טכנית טובה. ממתין במזומן.")

    if st.session_state.val_portfolio:
        for p in st.session_state.val_portfolio:
            with st.expander(f"דוח רכישה: {p['Symbol']} | יעד: +{p['Expected_Profit']:.1f}%"):
                st.markdown(f"**ניתוח משולב:** {p['AI_Explanation']}\n\n**הגנת הון (Stop-Loss):** ימכור אוטומטית בירידה ל-{p['StopLoss']}.")
        if st.button("ממש הכל (סוכן ערך)"):
            st.session_state.val_cash_ils = port_value_usd * usd_rate
            st.session_state.val_portfolio = []
            st.rerun()

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>⚡ סוכן מסחר יומי (Technical Day Trader):</b> הסוכן הזה מחפש עיוותים טכניים בלבד. מניות שנמכרו באגרסיביות (RSI נמוך) לפול-באק מהיר, או מניות שפרצו התנגדות.</div>', unsafe_allow_html=True)
    
    if 'day_cash_ils' not in st.session_state:
        st.session_state.day_cash_ils = 5000.0
        st.session_state.day_portfolio = []

    usd_rate = 3.8 
    cash_usd = st.session_state.day_cash_ils / usd_rate
    port_value_usd = sum([p['Qty'] * (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] if p['Currency'] == "$" else (df_all[df_all['Symbol'] == p['Symbol']]['Price'].iloc[0] / 100) / usd_rate) for p in st.session_state.day_portfolio]) if st.session_state.day_portfolio else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 מזומן יומי", f"₪{st.session_state.day_cash_ils:,.2f}")
    c2.metric("💼 שווי פוזיציות", f"${port_value_usd:,.2f}")
    c3.metric("📈 תשואה יומית", f"{((port_value_usd / (5000 / usd_rate)) - 1) * 100 if port_value_usd > 0 else 0.0:.1f}%")

    if st.button("⚡ הפעל סוכן יומי מבוסס מומנטום טכני"):
        if st.session_state.day_cash_ils > 100:
            # מחפש מניות "מכורות יתר" (RSI < 40) לתיקון מהיר, או מומנטום חזק מאוד (RSI > 65)
            momentum_stocks = df_all[(df_all['RSI'] < 40) | ((df_all['RSI'] > 65) & (df_all['Price'] > df_all['MA50']))].head(3)
            
            if not momentum_stocks.empty:
                invest_per_stock_usd = cash_usd / len(momentum_stocks)
                new_portfolio = []
                for _, row in momentum_stocks.iterrows():
                    price_usd = row['Price'] if row['Currency'] == "$" else (row['Price'] / 100) / usd_rate
                    qty = invest_per_stock_usd / price_usd if price_usd > 0 else 0
                    
                    stop_loss = row['Price'] * 0.96 # סטופ צמוד של 4% בלבד!
                    take_profit = row['Price'] * 1.08 # לקיחת רווח ב-8%
                    
                    reason = f"כניסה טכנית: ה-RSI כרגע {row['RSI']:.0f}. " + ("מניה במכירת-יתר, מצפה לתיקון." if row['RSI'] < 40 else "מניה במומנטום חזק מעל ממוצע 50 יום.")
                    
                    new_portfolio.append({
                        "Symbol": row['Symbol'], "Currency": row['Currency'], "Buy_Price": row['PriceStr'], 
                        "Qty": round(qty, 2), "Logic": reason,
                        "StopLoss": f"{row['Currency']}{stop_loss:.2f}", "TakeProfit": f"{row['Currency']}{take_profit:.2f}"
                    })
                st.session_state.day_portfolio = new_portfolio
                st.session_state.day_cash_ils = 0
                st.rerun()
            else:
                st.warning("הסוכן לא זיהה תבניות טכניות ברורות היום למסחר יומי.")

    if st.session_state.day_portfolio:
        for p in st.session_state.day_portfolio:
            with st.expander(f"פוזיציה יומית: {p['Symbol']}"):
                st.markdown(f"**סיבת כניסה:** {p['Logic']}\n**ניהול סיכונים צמוד:** לקיחת רווח ב-{p['TakeProfit']} | קטיעת הפסד אגרסיבית ב-{p['StopLoss']}.")
        if st.button("סגור פוזיציות יומיות"):
            st.session_state.day_cash_ils = port_value_usd * usd_rate
            st.session_state.day_portfolio = []
            st.rerun()
