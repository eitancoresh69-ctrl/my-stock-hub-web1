import streamlit as st
import pandas as pd

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>💼 סוכן השקעות ערך (טווח ארוך)</b> — סורק את ה-PDF ומחפש מניות יציבות בנקודת כניסה טובה.</div>', unsafe_allow_html=True)
    st.divider()

    # סורק חכם למציאת עמודת הציון מבלי לקרוס
    score_col = next((c for c in ['Score', 'ציון', 'score', 'PDF Score'] if c in df_all.columns), None)
    
    if score_col:
        # ממיר למספרים למקרה שהטקסט נקלט בצורה משובשת מה-PDF
        df_all[score_col] = pd.to_numeric(df_all[score_col], errors='coerce')
        
        # סינון מניות הזהב (ציון 5 ומעלה)
        gold_stocks = df_all[df_all[score_col] >= 5].dropna(subset=[score_col])
        
        if not gold_stocks.empty:
            st.success(f"🏆 נמצאו {len(gold_stocks)} מניות 'זהב' עם ציון 5 ומעלה!")
            st.dataframe(gold_stocks, use_container_width=True, hide_index=True)
        else:
            st.info("לא נמצאו מניות עם ציון 5 ומעלה כרגע.")
    else:
        st.warning("⚠️ לא נמצאה עמודת ציון (Score) בטבלה הראשית. לא ניתן לסנן מניות 'זהב'.")
        st.info(f"💡 העמודות שהמערכת מזהה כרגע הן: {', '.join(df_all.columns)}")
