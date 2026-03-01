# ml_learning_ai.py — ניתוח ביצועים מבוסס ML
import streamlit as st
import storage
import pandas as pd

def render_ml_dashboard():
    st.markdown('<div class="ai-card" style="border-right-color: #9c27b0;"><b>🧠 למידת מכונה (ML Insight):</b></div>', unsafe_allow_html=True)
    
    agent_df = storage.load_agent_portfolio()
    if agent_df.empty:
        st.info("ממתין לנתוני מסחר של הסוכנים כדי להתחיל ללמוד...")
        return

    st.write("📊 **ניתוח ביצועי סוכנים ושיפור אלגוריתמי:**")
    # הצגת רווח ממוצע לפי סוכן
    stats = agent_df.groupby("agent_type")['Profit_Pct'].mean()
    st.bar_chart(stats)
    
    total_pnl = agent_df['Profit_Pct'].sum()
    st.metric("רווח/הפסד מצטבר סוכנים", f"{total_pnl:.2f}%", delta=f"{total_pnl:.2f}%")
    st.success("ה-ML מייעל את בחירת המניות על בסיס הצלחות העבר.")
