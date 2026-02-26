import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

def render_financial_reports(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2196f3;"><b>📊 ניתוח דוחות פיננסיים (Financials AI)</b> — ניתוח עומק של דוחות החברה.</div>', unsafe_allow_html=True)
    st.divider()

    # מנגנון איתור עמודת סימול
    symbol_col = next((c for c in ['סימול', 'Symbol', 'symbol', 'Ticker'] if c in df_all.columns), None)
    
    if not symbol_col:
        st.error("❌ לא נמצאה עמודת 'סימול' בטבלה.")
        return
        
    symbols = df_all[symbol_col].dropna().unique().tolist()
    sel = st.selectbox("🎯 בחר מניה לניתוח:", symbols)
    
    if sel:
        with st.spinner(f"טוען נתונים עבור {sel}..."):
            try:
                ticker = yf.Ticker(sel)
                info = ticker.info
                st.success(f"✅ נתונים עבור: **{info.get('longName', sel)}**")
                
                # מדדי מפתח
                c1, c2, c3 = st.columns(3)
                c1.metric("שווי שוק", f"${info.get('marketCap', 0)/1e9:.2f}B")
                c2.metric("מכפיל רווח", info.get('trailingPE', 'N/A'))
                c3.metric("תשואת דיבידנד", f"{info.get('dividendYield', 0)*100:.2f}%")
                
                # גרף הכנסות
                fin = ticker.financials
                if not fin.empty and 'Total Revenue' in fin.index:
                    rev = fin.loc['Total Revenue'].sort_index()
                    fig = go.Figure(go.Bar(x=rev.index.year, y=rev.values/1e9, marker_color='#2196f3'))
                    fig.update_layout(title="הכנסות שנתיות (במיליארדים $)", template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"שגיאה במשיכת נתונים: {e}")
