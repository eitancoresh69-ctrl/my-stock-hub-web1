# alerts_ai.py
import streamlit as st
import pandas as pd

def render_smart_alerts(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ff9800;"><b>🔔 מוקד התראות חכמות (Smart Alerts):</b> סוכן ה-AI סורק את השוק 24/7 ומחפש תנודות מחיר חריגות ודוחות כספיים מתקרבים שעשויים לייצר תנודתיות אלימה.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 תנודות מחיר חריגות (היום)")
        # מחפש מניות שזזו יותר מ-3% למעלה או למטה
        volatile = df_all[(df_all['Change'] > 3.0) | (df_all['Change'] < -3.0)].sort_values(by="Change", ascending=False)
        
        if not volatile.empty:
            for _, row in volatile.iterrows():
                if row['Change'] > 0:
                    st.success(f"🚀 **{row['Symbol']}** מזנקת ב- **{row['Change']:.1f}%**! (מחיר: {row['PriceStr']})")
                else:
                    st.error(f"📉 **{row['Symbol']}** צוללת ב- **{row['Change']:.1f}%**! (מחיר: {row['PriceStr']})")
        else:
            st.info("😴 השוק רגוע כרגע. אין תנודות חריגות מעל 3%.")

    with col2:
        st.markdown("### 📅 אזהרת דוחות רבעוניים (Earnings)")
        st.markdown("*מניות שיפרסמו דוח כספי ב-14 הימים הקרובים:*")
        
        # מחפש מניות שהדוח שלהן בטווח של שבועיים
        upcoming_earnings = df_all[(df_all['DaysToEarnings'] >= 0) & (df_all['DaysToEarnings'] <= 14)].sort_values(by="DaysToEarnings")
        
        if not upcoming_earnings.empty:
            for _, row in upcoming_earnings.iterrows():
                days = row['DaysToEarnings']
                if days <= 7:
                    st.warning(f"⚠️ **{row['Symbol']}** מדווחת בעוד **{int(days)} ימים**! ({row['EarningsDate']})\n\n*סוכן ה-AI ממליץ להדק פקודות Stop-Loss לפני פרסום הדוח.*")
                else:
                    st.info(f"🗓️ **{row['Symbol']}** מדווחת בעוד **{int(days)} ימים** ({row['EarningsDate']}).")
        else:
            st.success("✅ אין דוחות רבעוניים מסוכנים בשבועיים הקרובים למניות ברדאר שלך.")
