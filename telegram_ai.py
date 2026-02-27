# telegram_ai.py — אינטגרציית טלגרם
import streamlit as st


def render_telegram_integration():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #2CA5E0;">'
        '<b>📱 בוט טלגרם:</b> חיבור עתידי לשליחת התראות Push לטלפון.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### סטטוס: 🔴 לא מחובר")
    chat_id = st.text_input("Chat ID:", placeholder="123456789", key="tg_chatid")
    if st.button("🔌 חבר", key="tg_connect"):
        if chat_id:
            st.success("הבקשה נרשמה! (דורש שרת רקע — בקרוב).")
        else:
            st.error("הכנס Chat ID.")

    st.markdown("---")
    st.markdown("### 👁️ תצוגה מקדימה")
    c1, c2 = st.columns(2)
    with c1:
        st.info("**🚨 מומנטום:**\n\n**NVDA** זינקה ב-5.2%\nמחיר: $125.40\nשקול מימוש רווחים.")
    with c2:
        st.warning("**📅 דוח קרוב:**\n\n**AAPL** מדווחת מחר.\nStop-Loss הופעל אוטומטית.\nהכן לתנודתיות!")
