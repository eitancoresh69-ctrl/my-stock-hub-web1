import streamlit as st
import pandas as pd

def render_backtester(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ff9800;"><b>⏪ מודול בק-טסט (Backtesting)</b> — סימולציית מסחר על נתוני עבר.</div>', unsafe_allow_html=True)
    st.divider()

    symbol_col = next((col for col in ['סימול', 'Symbol', 'symbol', 'Ticker', 'ticker'] if col in df_all.columns), None)
    if symbol_col is None:
        st.error(f"❌ שגיאה: לא מצאתי עמודה המכילה את סימולי המניות.")
        return
        
    symbols_list = df_all[symbol_col].dropna().unique().tolist()
    
    if not symbols_list:
        st.warning("⚠️ לא נמצאו מניות בטבלה.")
        return

    sel = st.selectbox("בחר מניה לסימולציה עבור:", symbols_list)
    if sel:
        st.success(f"✅ נבחרה מניה לסימולציה: **{sel}**")
        st.info("כאן יוצגו נתוני הבק-טסט של המניה.")
