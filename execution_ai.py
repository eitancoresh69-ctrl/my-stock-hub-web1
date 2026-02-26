# execution_ai.py
import streamlit as st

def render_execution_engine():
    st.markdown('<div class="ai-card" style="border-right-color: #607d8b;"><b>⚙️ מנוע ביצוע מסחר (Execution Engine):</b> מדמה את התנאים בעולם האמיתי (Slippage, פקודות Limit) לקראת חיבור לברוקר אמיתי.</div>', unsafe_allow_html=True)
    
    st.markdown("### 🚦 סימולטור פקודות שוק (Market vs. Limit)")
    st.write("בעולם האמיתי, הבוט לא יכול תמיד לקנות בדיוק במחיר שמופיע במסך (Slippage). כאן אנחנו מאמנים את הבוט להשתמש בפקודות הגבלה (Limit Orders).")
    
    col1, col2 = st.columns(2)
    with col1:
        order_type = st.selectbox("סוג פקודת רשת למערכת:", ["Market Order (קנה עכשיו בכל מחיר)", "Limit Order (קנה רק עד מחיר מסוים)"])
        simulated_slippage = st.slider("הדמיית החלקת מחיר (Slippage) באחוזים:", 0.0, 2.0, 0.5)
    with col2:
        if order_type == "Limit Order (קנה רק עד מחיר מסוים)":
            st.success("✅ מומלץ! הבוט מוגדר כעת לשלוח פקודת Limit לברוקר. זה מונע ממנו לשלם ביוקר במקרה של תנודה מהירה בפתיחת המסחר.")
        else:
            st.warning("⚠️ אזהרה: פקודת Market חושפת את הרובוט למניפולציות. אם המניה קופצת שנייה לפני הביצוע, נשלם את המחיר המופקע.")
            st.info(f"החלקת מחיר משוערת: תיקנס ב-{simulated_slippage}% על כל פעולת קנייה או מכירה במערכת הפנימית.")
