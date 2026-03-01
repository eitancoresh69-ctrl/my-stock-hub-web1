# alerts_ai.py
import streamlit as st
from datetime import datetime

def render_smart_alerts(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ff9800;"><b>🔔 מרכז התראות AI חכם:</b> המערכת סורקת אירועי דוחות, הזדמנויות טכניות ופעילות חריגה של בעלי עניין (מנכ"לים).</div>', unsafe_allow_html=True)
    
    if df_all.empty:
        st.warning("אין נתונים להצגת התראות.")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 דוחות ואירועים קרובים")
        # התראות דוחות (Earnings)
        earnings_soon = df_all[df_all['DaysToEarnings'].between(0, 14)]
        if not earnings_soon.empty:
            for _, row in earnings_soon.iterrows():
                st.warning(f"**{row['Symbol']}** מפרסמת דוח בעוד **{row['DaysToEarnings']}** ימים ({row['EarningsDate']}). צפויה תנודתיות גבוהה.")
        else:
            st.info("אין דוחות כספיים קרובים ב-14 הימים הקרובים.")

    with col2:
        st.markdown("### 🔍 מודיעין בעלי עניין (Insiders)")
        # התראות על אחזקות מנכ"לים גבוהות (מעל 5% נחשב חזק מאוד לחברה גדולה)
        high_insider = df_all[df_all['InsiderHeld'] > 5.0]
        if not high_insider.empty:
            for _, row in high_insider.iterrows():
                st.markdown(f"""
                <div style="background-color: #f3e5f5; padding: 10px; border-radius: 8px; border-right: 5px solid #9c27b0; margin-bottom: 10px;">
                    <b style="color: #4a148c;">🚨 איתות אמון הנהלה: {row['Symbol']}</b><br>
                    בעלי עניין מחזיקים ב-<b>{row['InsiderHeld']:.2f}%</b> מהחברה. 
                    כאשר המנכ"ל מושקע אישית, האינטרס שלו זהה לשלך.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("לא זוהתה אחזקת בעלי עניין חריגה כרגע.")

    st.markdown("---")
    st.markdown("### 📈 הזדמנויות טכניות וערך")
    
    # התראות RSI (מכירת יתר / קניית יתר)
    oversold = df_all[df_all['RSI'] < 30]
    overbought = df_all[df_all['RSI'] > 70]
    
    c1, c2 = st.columns(2)
    with c1:
        if not oversold.empty:
            for _, row in oversold.iterrows():
                st.success(f"**{row['Symbol']}** ב-RSI נמוך ({row['RSI']:.0f}). ייתכן שהמניה ב'מכירת יתר' ומתקרבת לנקודת היפוך.")
        else:
            st.write("אין מניות במצב 'מכירת יתר' קיצוני.")
            
    with c2:
        if not overbought.empty:
            for _, row in overbought.iterrows():
                st.error(f"**{row['Symbol']}** ב-RSI גבוה ({row['RSI']:.0f}). סכנת 'קניית יתר' ותיקון מחיר כלפי מטה.")
        else:
            st.write("אין מניות במצב 'קניית יתר' קיצוני.")

    # התראת "זהב" משולבת (גם ציון PDF גבוה וגם אפסייד אנליסטים)
    st.markdown("### 🏆 התראות זהב משולבות")
    gold_alerts = df_all[(df_all['Score'] >= 5) & (df_all['TargetUpside'] > 15)]
    if not gold_alerts.empty:
        for _, row in gold_alerts.iterrows():
            st.balloons() if st.button(f"חלוץ הזדמנות עבור {row['Symbol']}") else None
            st.info(f"💎 **הזדמנות זהב:** {row['Symbol']} קיבלה ציון {row['Score']} ב-PDF והאנליסטים צופים לה אפסייד של {row['TargetUpside']:.1f}%.")
