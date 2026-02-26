# failsafes_ai.py
import streamlit as st

def render_failsafes():
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>🛡️ מנגנוני הגנה והישרדות (Failsafes):</b> חגורות הבטיחות הקריטיות שמונעות מהרובוט למחוק את החשבון בזמן שאתה לא מול המסך.</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔴 מתג השמדה (Kill Switch)")
    st.write("במקרה של ברבור שחור (קריסת קורונה, אירוע בטחוני), לחיצה כאן תשלח פקודת Market מיידית לחיסול כל הפוזיציות ותקפיא את כל הסוכנים.")
    
    if st.button("🚨 הפעל מתג השמדה עכשיו (Liquidate All) 🚨", type="primary"):
        st.session_state.kill_switch_active = True
        st.error("מתג השמדה הופעל! המערכת עברה למצב חירום. כל הסוכנים הוקפאו. לא יישלחו פקודות רכש חדשות לברוקר עד לאיפוס המערכת.")
        
    st.markdown("---")
    st.markdown("### 📉 הגבלת הפסד יומית (Max Daily Drawdown)")
    max_loss = st.number_input("עצור את הרובוט אם התיק הכולל יורד היום ב (%):", min_value=1.0, max_value=20.0, value=3.0)
    st.info(f"פקודת הגנה הוגדרה בשרת: אם הבוט מזהה שהפסדת היום יותר מ-{max_loss}%, הוא ינתק את עצמו מהבורסה ויחזור לסחור רק מחר. ככה מונעים 'יום שחור' מלמחוק את החשבון.")
