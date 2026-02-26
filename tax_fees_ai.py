# tax_fees_ai.py
import streamlit as st

def render_tax_optimization():
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>💸 מחשבון נטו (מיסים ועמלות):</b> אלגוריתם שמוודא שהעמלות של הברוקר ומס רווח הון (25% בישראל) לא מוחקים לך את כל הרווח בעסקאות קטנות.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🧮 סימולציית רווח נטו")
        gross_profit = st.number_input("הזן רווח גולמי מעסקה (₪):", value=1000.0)
        trades_count = st.number_input("כמות פעולות (קנייה + מכירה):", value=2)
        broker_fee = st.number_input("עמלת ברוקר לפעולה (₪):", value=5.0)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        total_fees = trades_count * broker_fee
        profit_after_fees = gross_profit - total_fees
        tax = profit_after_fees * 0.25 if profit_after_fees > 0 else 0
        net_profit = profit_after_fees - tax
        
        st.markdown(f"**📉 עמלות ברוקר ששולמו:** ₪{total_fees:.2f}")
        st.markdown(f"**🏛️ מס רווח הון (25%):** ₪{tax:.2f}")
        st.success(f"**💰 רווח נטו לכיס:** ₪{net_profit:.2f}")
        
    st.info("🤖 **חוק של הבוט:** ה-AI חוסם אוטומטית כניסה לעסקאות שבהן הרווח הצפוי נמוך מ-50 שקלים, כי העמלות והמיסים יהפכו את הטרייד להפסדי בפועל.")
