import streamlit as st
import pandas as pd

def render_growth_and_risk(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #e91e63;"><b>🚀 סוכן מניות צמיחה (CAN SLIM)</b> — חיפוש מניות חזקות.</div>', unsafe_allow_html=True)
    st.divider()

    # 1. סורק חכם למציאת כל העמודות הנדרשות
    rev_col = next((c for c in ['RevGrowth', 'צמיחה בהכנסות', 'צמיחה', 'Revenue Growth'] if c in df_all.columns), None)
    rsi_col = next((c for c in ['RSI', 'rsi', 'מדד עוצמה יחסית', 'Rsi'] if c in df_all.columns), None)
    price_col = next((c for c in ['Price', 'מחיר', 'מחיר נוכחי', 'Close', 'מחיר סגירה'] if c in df_all.columns), None)
    ma50_col = next((c for c in ['MA50', 'ממוצע נע 50', 'ממוצע 50', 'SMA50'] if c in df_all.columns), None)

    # בדיקה האם משהו חסר
    missing_cols = []
    if not rev_col: missing_cols.append("צמיחה (RevGrowth)")
    if not rsi_col: missing_cols.append("RSI")
    if not price_col: missing_cols.append("מחיר (Price)")
    if not ma50_col: missing_cols.append("ממוצע נע 50 (MA50)")

    if missing_cols:
        st.error(f"❌ שגיאה: לא ניתן להפעיל את סוכן הצמיחה כי חסרות העמודות הבאות בטבלה: **{', '.join(missing_cols)}**")
        st.info(f"💡 העמודות שהמערכת מזהה כרגע בטבלה הן: {', '.join(df_all.columns)}")
        st.warning("אנא ודא שהטבלה הראשית שנטענת למערכת מכילה את הנתונים הללו.")
        return

    # 2. סינון הנתונים (עם המרה למספרים כדי למנוע קריסות אם יש שם טקסט בטעות)
    try:
        df_safe = df_all.copy()
        
        # המרה בטוחה למספרים
        df_safe[rev_col] = pd.to_numeric(df_safe[rev_col], errors='coerce')
        df_safe[rsi_col] = pd.to_numeric(df_safe[rsi_col], errors='coerce')
        df_safe[price_col] = pd.to_numeric(df_safe[price_col], errors='coerce')
        df_safe[ma50_col] = pd.to_numeric(df_safe[ma50_col], errors='coerce')

        # הלוגיקה המקורית שלך - כעת עובדת עם שמות העמודות הדינמיים!
        growth_stocks = df_safe[
            (df_safe[rev_col] > 20) & 
            (df_safe[rsi_col] > 55) & 
            (df_safe[price_col] > df_safe[ma50_col])
        ].sort_values(by=rev_col, ascending=False)
        
        if growth_stocks.empty:
            st.info("לא נמצאו מניות העונות על קריטריוני הצמיחה כרגע.")
        else:
            st.success(f"✅ נמצאו {len(growth_stocks)} מניות צמיחה פוטנציאליות!")
            # כאן תוכל להדפיס את הטבלה למסך כמו שעשית במקור
            st.dataframe(growth_stocks)
            
    except Exception as e:
        st.error(f"אירעה שגיאה בחישוב הנתונים: {e}")

    # 👇 הוסף את שאר הלוגיקה שלך (אם יש) מתחת 👇
