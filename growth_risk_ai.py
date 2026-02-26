import streamlit as st
import pandas as pd

def render_growth_and_risk(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #e91e63;"><b>🚀 סוכן מניות צמיחה (CAN SLIM)</b> — חיפוש מניות חזקות עם צמיחה מהירה.</div>', unsafe_allow_html=True)
    st.divider()

    # סורק חכם למציאת עמודות (RevGrowth, RSI, Price, MA50)
    rev_col = next((c for c in ['צמיחה בהכנסות', 'צמיחה', 'RevGrowth', 'Revenue Growth'] if c in df_all.columns), None)
    rsi_col = next((c for c in ['RSI', 'rsi', 'מדד עוצמה יחסית'] if c in df_all.columns), None)
    price_col = next((c for c in ['מחיר', 'מחיר נוכחי', 'Price', 'Close'] if c in df_all.columns), None)
    ma50_col = next((c for c in ['ממוצע נע 50', 'MA50', 'SMA50'] if c in df_all.columns), None)

    # בדיקה האם חסרים נתונים
    missing = []
    if not rev_col: missing.append("צמיחה")
    if not rsi_col: missing.append("RSI")
    if not price_col: missing.append("מחיר")
    if not ma50_col: missing.append("ממוצע נע 50")

    if missing:
        st.error(f"❌ שגיאה: לא ניתן להפעיל את הסוכן. חסרות העמודות: {', '.join(missing)}")
        st.info(f"💡 עמודות קיימות בטבלה: {', '.join(df_all.columns)}")
        return

    try:
        # המרה למספרים למניעת קריסות
        df_safe = df_all.copy()
        for col in [rev_col, rsi_col, price_col, ma50_col]:
            df_safe[col] = pd.to_numeric(df_safe[col], errors='coerce')

        # סינון מניות (צמיחה > 20%, RSI > 55, מחיר מעל ממוצע 50)
        growth_stocks = df_safe[
            (df_safe[rev_col] >= 20) & 
            (df_safe[rsi_col] > 55) & 
            (df_safe[price_col] > df_safe[ma50_col])
        ].sort_values(by=rev_col, ascending=False)

        if not growth_stocks.empty:
            st.success(f"✅ נמצאו {len(growth_stocks)} מניות צמיחה חזקות!")
            st.dataframe(growth_stocks, use_container_width=True, hide_index=True)
        else:
            st.info("לא נמצאו מניות העונות על כל קריטריוני הצמיחה כרגע.")
            
    except Exception as e:
        st.error(f"אירעה שגיאה בחישוב הנתונים: {e}")
