# telegram_ai.py
import streamlit as st

def render_telegram_integration():
    st.markdown('<div class="ai-card" style="border-right-color: #2CA5E0;"><b>📱 מרכז שליטה: בוט התראות לטלגרם (Push Notifications)</b><br>כאן נחבר בעתיד את המערכת לטלפון שלך, כך שה-AI ישלח לך הודעות בזמן אמת כשיש התרסקות, זינוק, או דוח רבעוני.</div>', unsafe_allow_html=True)
    
    st.markdown("### סטטוס חיבור: 🔴 לא מחובר")
    st.text_input("הכנס מזהה משתמש (Chat ID) של טלגרם להפעלת השירות:", placeholder="לדוגמה: 123456789")
    
    if st.button("🔌 חבר בוט עכשיו"):
        st.success("הבקשה נרשמה במערכת! (מודול שליחת ההודעות דורש הגדרת שרת רקע - בקרוב בגרסה הבאה).")
        
    st.markdown("---")
    st.markdown("### 👁️ תצוגה מקדימה: איך ייראו ההודעות שתקבל לטלפון?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**הודעה לדוגמה (קפיצת מחיר):**\n\n🚨 *התראת מומנטום הופעלה!*\nמניית **NVDA** זינקה ב-5.2% בשעה האחרונה.\nהסוכן היומי שלך ממליץ לשקול מימוש רווחים כעת.\nמחיר נוכחי: $125.40")
    with col2:
        st.warning("**הודעה לדוגמה (דוח רבעוני):**\n\n📅 *אזהרת דוח מתקרב!*\nמניית **AAPL** מדווחת מחר בערב.\nהסוכן הפעיל פקודת Stop-Loss אוטומטית להגנה על התיק של 5000 ₪ שלך.\nהכן את עצמך לתנודתיות.")
