import streamlit as st
def render_tax_optimization():
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>💸 מחשבון אופטימיזציית מיסים ועמלות.</b></div>', unsafe_allow_html=True)
    profit = st.number_input("רווח גולמי מעסקה (₪):", value=1000)
    st.success(f"רווח נטו לאחר עמלות ברוקר (10₪) ומס רווח הון (25%): ₪{((profit - 10) * 0.75):.2f}")
