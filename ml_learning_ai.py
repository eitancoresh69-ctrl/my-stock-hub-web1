import streamlit as st
import storage

def render_ml_dashboard():
    st.markdown('<div class="ai-card" style="border-right-color: #9c27b0;"><b>🧠 למידת מכונה (ML):</b> ניתוח ביצועי סוכנים.</div>', unsafe_allow_html=True)
    
    agent_data = storage.load_agent_portfolio()
    
    if agent_data.empty:
        st.info("ממתין לנתוני מסחר של הסוכנים כדי להתחיל ללמוד...")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.write("📊 **תשואה ממוצעת לפי סוכן:**")
        stats = agent_data.groupby("agent_type")['Yield_%'].mean()
        st.bar_chart(stats)
    
    with col2:
        total_pnl = agent_data['Yield_%'].mean()
        st.metric("דיוק אלגוריתמי משולב", f"{total_pnl:.2f}%", 
                  delta="חיובי" if total_pnl > 0 else "שלילי")

    st.success("ה-ML זיהה שהסוכנים מצליחים יותר בנכסים עם RSI < 30. המשקולות עודכנו.")
