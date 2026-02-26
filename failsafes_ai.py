import streamlit as st
def render_failsafes():
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>🛡️ מנגנון הגנה וניתוק:</b> רשת ביטחון וירטואלית.</div>', unsafe_allow_html=True)
    if st.button("🚨 מתג השמדה מדומה (Kill Switch)", type="primary"):
        st.session_state.kill_switch_active = True
        st.error("הופעל מתג השמדה! (הדמייה). במערכת חיה כל הפוזיציות היו נסגרות למזומן.")
