import streamlit as st
import pandas as pd

def render_growth_and_risk(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #e91e63;"><b>🚀 סוכן מניות צמיחה (CAN SLIM)</b> — חיפוש מניות חזקות עם צמיחה מהירה.</div>', unsafe_allow_html=True)
    st.divider()

    # סורק חכם למציאת העמודות הרלוונטיות
    rev_col = next((c for c in ['RevGrowth', 'צמיחה בהכנסות', 'צמיחה', 'Revenue Growth'] if c in df_all.columns), None)
    rsi_col = next((c for c in ['RSI', 'rsi', 'מדד עוצמה יחסית', 'Rsi'] if c in df_all.columns), None)
    
    # בדיקה אם חסר משהו כדי לא לקרוס
    missing = []
    if not rev_col: missing.append("צמיחה (RevGrowth)")
    if not rsi_col: missing.append("RSI")

    if missing:
        st.warning(f"⚠️ חסרים נתונים בטבלה כדי להפעיל את סוכן הצמיחה: **{', '.join(missing)}**.")
        st.info(f"💡 העמודות שהמערכת מזהה כרגע בטבלה הן: {', '.join(df_all.columns)}")
        return

    try:
        # יצירת עותק בטוח לעבודה
        df_safe = df_all.copy()
        df_safe[rev_col] = pd.to_numeric(df_safe[rev_col], errors='coerce')
        df_safe[rsi_col] = pd.to_numeric(df_safe[rsi_col], errors='coerce')

        # סינון המניות (צמיחה מעל 20 וגם RSI מעל 55)
        growth_stocks = df_safe[(df_safe[rev_col] >= 20) & (df_safe[rsi_col] > 55)].sort_values(by=rev_col, ascending=False)

        if not growth_stocks.empty:
            st.success(f"✅ נמצאו {len(growth_stocks)} מניות צמיחה פוטנציאליות!")
            st.dataframe(growth_stocks, use_container_width=True, hide_index=True)
        else:
            st.info("לא נמצאו מניות העונות על קריטריוני הצמיחה (צמיחה > 20% ו-RSI > 55) כרגע.")
            
    except Exception as e:
        st.error(f"אירעה שגיאה בחישוב הנתונים: {e}")
