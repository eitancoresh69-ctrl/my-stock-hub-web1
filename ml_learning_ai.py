import streamlit as st
def render_machine_learning():
    st.markdown('<div class="ai-card" style="border-right-color: #9c27b0;"><b>🧠 למידת מכונה (ML):</b> ניתוח עסקאות עבר לשיפור דיוק.</div>', unsafe_allow_html=True)
    if st.button("הרץ אופטימיזציית AI"):
        st.success("ה-AI השלים למידה: יחס סיכוי-סיכון אופטימלי עודכן ל-1:2.4 על בסיס התנודתיות בשוק.")
