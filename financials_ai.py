import streamlit as st
import pandas as pd

def render_financial_reports(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2196f3;"><b>📊 ניתוח דוחות פיננסיים (Financials AI)</b> — ניתוח עומק של דוחות החברה.</div>', unsafe_allow_html=True)
    st.divider()

    # 1. מנגנון חכם לאיתור שם עמודת הסימול בטבלה שלך מבלי לקרוס
    possible_names = ['סימול', 'Symbol', 'symbol', 'Ticker', 'ticker']
    symbol_col = None
    
    for col in possible_names:
        if col in df_all.columns:
            symbol_col = col
            break
            
    # הגנת קריסה: אם המערכת לא מוצאת את העמודה, היא תציג הודעה ברורה במקום מסך שגיאה אדום
    if symbol_col is None:
        st.error(f"❌ שגיאה: לא מצאתי עמודה המכילה את סימולי המניות.")
        st.info(f"העמודות שהמערכת זיהתה בטבלה שלך הן: {', '.join(df_all.columns)}")
        return
        
    # 2. משיכת רשימת המניות (ללא תאים ריקים)
    symbols_list = df_all[symbol_col].dropna().unique().tolist()
    
    if not symbols_list:
        st.warning("⚠️ לא נמצאו מניות בטבלה.")
        return

    # 3. תיבת הבחירה שתעבוד כעת בצורה חלקה
    sel = st.selectbox("🎯 בחר מניה לניתוח דוחות עומק:", symbols_list)
    
    # --- כאן יגיע המשך הקוד של ניתוח הדוחות ---
    if sel:
        st.success(f"✅ נבחרה מניה: **{sel}**")
        st.markdown("כאן יוצגו הנתונים הפיננסיים של החברה, מאזנים, דוחות רווח והפסד ועוד.")
        # הוסף כאן את שאר הלוגיקה שלך שמציגה את הדוחות (גרפים, טבלאות וכו')
