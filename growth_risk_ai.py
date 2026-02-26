import streamlit as st
import pandas as pd

def render_growth_and_risk(df_all):
    st.markdown('### 🚀 סוכן מניות צמיחה')
    
    rev_col = next((c for c in ['צמיחה', 'RevGrowth', 'Revenue Growth'] if c in df_all.columns), None)
    rsi_col = next((c for c in ['RSI', 'rsi'] if c in df_all.columns), None)
    
    if rev_col and rsi_col:
        df_all[rev_col] = pd.to_numeric(df_all[rev_col], errors='coerce')
        df_all[rsi_col] = pd.to_numeric(df_all[rsi_col], errors='coerce')
        growth = df_all[(df_all[rev_col] >= 20) & (df_all[rsi_col] > 55)]
        st.dataframe(growth)
    else:
        st.warning("נתוני צמיחה או RSI חסרים.")
