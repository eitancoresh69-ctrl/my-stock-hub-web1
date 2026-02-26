import streamlit as st
import pandas as pd

def render_backtester(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ff9800;"><b>⏪ מודול בק-טסט (Backtesting)</b></div>', unsafe_allow_html=True)
    
    symbol_col = next((c for c in ['סימול', 'Symbol', 'symbol', 'Ticker'] if c in df_all.columns), None)
    
    if symbol_col:
        symbols = df_all[symbol_col].dropna().unique().tolist()
        sel = st.selectbox("בחר מניה לסימולציה:", symbols)
        if sel:
            st.success(f"✅ נבחרה מניה לסימולציה: {sel}")
            st.info("כאן יופיעו תוצאות הסימולציה ההיסטורית.")
    else:
        st.error("עמודת סימול חסרה.")
