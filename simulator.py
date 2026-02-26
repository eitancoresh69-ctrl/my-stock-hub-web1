import streamlit as st
import pandas as pd

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>💼 סוכן השקעות ערך</b></div>', unsafe_allow_html=True)
    
    score_col = next((c for c in ['ציון', 'Score', 'score'] if c in df_all.columns), None)
    
    if score_col:
        df_all[score_col] = pd.to_numeric(df_all[score_col], errors='coerce')
        gold = df_all[df_all[score_col] >= 5]
        if not gold.empty:
            st.success(f"🏆 נמצאו {len(gold)} מניות זהב!")
            st.dataframe(gold)
    else:
        st.warning("עמודת ציון חסרה בטבלה.")

def render_day_trade_agent(df_all):
    st.markdown('### ⚡ סוכן מסחר יומי')
    st.info("ניתוח הזדמנויות לטווח קצר.")
