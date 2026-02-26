import streamlit as st
import pandas as pd

def render_value_agent(df_all):
    """פונקציית סוכן ערך"""
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>💼 סוכן השקעות ערך (טווח ארוך)</b> — מחפש מניות יציבות עם ציון גבוה מה-PDF.</div>', unsafe_allow_html=True)
    
    # חיפוש עמודת הציון (Score) בעברית או אנגלית
    score_col = next((c for c in ['ציון', 'Score', 'score', 'PDF Score'] if c in df_all.columns), None)
    
    if score_col:
        df_all[score_col] = pd.to_numeric(df_all[score_col], errors='coerce')
        gold_stocks = df_all[df_all[score_col] >= 5].dropna(subset=[score_col])
        
        if not gold_stocks.empty:
            st.success(f"🏆 נמצאו {len(gold_stocks)} מניות 'זהב' עם ציון 5 ומעלה!")
            st.dataframe(gold_stocks, use_container_width=True, hide_index=True)
        else:
            st.info("לא נמצאו מניות עם ציון 5 ומעלה כרגע.")
    else:
        st.warning("⚠️ לא נמצאה עמודת ציון (Score/ציון) בטבלה. ודא שה-PDF נטען כהלכה.")

def render_day_trade_agent(df_all):
    """פונקציה לסוכן יום (כדי למנוע את שגיאת ה-AttributeError שראינו בסרטון)"""
    st.markdown('<div class="ai-card" style="border-right-color: #ff5722;"><b>⚡ סוכן מסחר יומי</b> — ניתוח הזדמנויות לטווח קצר מאוד.</div>', unsafe_allow_html=True)
    st.info("כאן יופיעו המלצות למסחר יומי המבוססות על תנודתיות ו-RSI.")
    # כאן אפשר להוסיף לוגיקה נוספת בעתיד
