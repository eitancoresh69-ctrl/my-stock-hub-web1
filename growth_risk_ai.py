# growth_risk_ai.py
import streamlit as st
import pandas as pd

def render_growth_and_risk(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #e91e63;"><b>🚀 מעבדת צמיחה וניהול סיכונים:</b> השלמה לאסטרטגיית ה-PDF. כאן אנחנו צדים "מפלצות צמיחה" ומנהלים את הסיכון המתמטי של התיק.</div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🚀 סוכן צמיחה אגרסיבית (Hyper-Growth)", "🧮 מחשבון ניהול סיכונים (Position Sizing)"])
    
    with t1:
        st.markdown("### 🚀 סוכן מניות צמיחה (בהשראת CAN SLIM)")
        st.write("בניגוד לסוכן הערך (PDF) שמרן, סוכן זה מחפש חברות טכנולוגיה וחדשנות שצומחות בקצב מסחרר. הוא מוכן לקבל חובות ושולי רווח נמוכים, כל עוד ההכנסות טסות והמומנטום בגרף חיובי.")
        
        if st.button("🚀 הפעל סורק צמיחה מואצת"):
            # סינון: צמיחת מכירות מעל 20%, ומומנטום טכני חיובי (RSI מעל 55 ומחיר מעל ממוצע 50)
            growth_stocks = df_all[(df_all['RevGrowth'] >= 20) & (df_all['RSI'] > 55) & (df_all['Price'] > df_all['MA50'])].sort_values(by="RevGrowth", ascending=False)
            
            if not growth_stocks.empty:
                st.success(f"ה-AI איתר {len(growth_stocks)} מניות צמיחה על הרדאר!")
                st.dataframe(
                    growth_stocks[["Symbol", "PriceStr", "RevGrowth", "RSI", "TargetUpside"]],
                    column_config={
                        "Symbol": "סימול",
                        "PriceStr": "מחיר פריצה",
                        "RevGrowth": st.column_config.NumberColumn("זינוק בהכנסות 🚀", format="%.1f%%"),
                        "RSI": st.column_config.NumberColumn("עוצמת מומנטום", format="%.1f"),
                        "TargetUpside": st.column_config.NumberColumn("פוטנציאל לפי אנליסטים", format="+%.1f%%")
                    },
                    use_container_width=True, hide_index=True
                )
                st.info("💡 **טיפ מסוכן הצמיחה:** מניות צמיחה הן תנודתיות מאוד. חובה להשתמש ב-Stop-Loss של מקסימום 7%-10% ממחיר הכניסה כדי לחתוך הפסדים מוקדם.")
            else:
                st.warning("השוק חלש כרגע. לא נמצאו מניות עם מומנטום צמיחה אגרסיבי.")

    with t2:
        st.markdown("### 🧮 מחשבון סיכונים של וול-סטריט (Position Sizing)")
        st.write("הכנס את הנתונים כדי לדעת **בדיוק** כמה מניות לקנות, כך שלעולם לא תמחק את התיק שלך בעסקה כושלת אחת.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_capital = st.number_input("💵 גודל התיק הכולל שלך ($):", min_value=100, value=10000, step=1000)
            risk_percent = st.number_input("🚨 סיכון לעסקה (ממליץ 1%-2%):", min_value=0.1, max_value=10.0, value=1.0, step=0.5)
        with col2:
            entry_price = st.number_input("🎯 מחיר קנייה מתוכנן למניה ($):", min_value=0.1, value=100.0, step=1.0)
            stop_loss = st.number_input("🛑 מחיר עצירת הפסד (Stop-Loss $):", min_value=0.1, value=90.0, step=1.0)
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True) # ריווח
            if st.button("🧮 חשב פוזיציה מדויקת"):
                if entry_price <= stop_loss:
                    st.error("מחיר ה-Stop-Loss חייב להיות נמוך ממחיר הקנייה (לעסקאות לונג)!")
                else:
                    risk_amount_dollars = total_capital * (risk_percent / 100)
                    risk_per_share = entry_price - stop_loss
                    shares_to_buy = risk_amount_dollars / risk_per_share
                    total_investment = shares_to_buy * entry_price
                    
                    st.success("✅ **תוצאות החישוב של ה-AI:**")
                    st.markdown(f"כדי לסכן בדיוק **${risk_amount_dollars:,.2f}** (שהם {risk_percent}% מהתיק שלך):")
                    st.markdown(f"👉 עליך לקנות **{int(shares_to_buy)} מניות**.")
                    st.markdown(f"💰 סך ההשקעה שתידרש בעסקה: **${total_investment:,.2f}**.")
