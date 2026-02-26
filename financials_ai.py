import streamlit as st
import pandas as pd

def render_financial_reports(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2196f3;"><b>📊 ניתוח דוחות פיננסיים (Financials AI)</b> — ניתוח עומק של דוחות החברה.</div>', unsafe_allow_html=True)
    st.divider()

    # סורק חכם למציאת עמודת הסימול מבלי לקרוס
    symbol_col = next((col for col in ['סימול', 'Symbol', 'symbol', 'Ticker', 'ticker'] if col in df_all.columns), None)
    
    if symbol_col is None:
        st.error(f"❌ שגיאה: לא מצאתי עמודה המכילה את סימולי המניות.")
        return
        
    symbols_list = df_all[symbol_col].dropna().unique().tolist()
    
    if not symbols_list:
        st.warning("⚠️ לא נמצאו מניות בטבלה.")
        return

    # תיבת הבחירה שעובדת חלק:
    sel = st.selectbox("🎯 בחר מניה לניתוח דוחות עומק:", symbols_list)
    
    if sel:
        st.success(f"✅ נבחרה מניה: **{sel}**")
        
        # 👇 הוסף את המשך הקוד המקורי שלך (הגרפים של הדוחות) מתחת לשורה זו 👇
