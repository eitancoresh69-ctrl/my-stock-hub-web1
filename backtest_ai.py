import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_backtester(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ff9800;"><b>⏪ מודול בק-טסט (Backtesting)</b> — סימולציית אסטרטגיות מסחר על נתוני אמת מהעבר.</div>', unsafe_allow_html=True)
    st.divider()

    # סורק חכם
    symbol_col = next((col for col in ['סימול', 'Symbol', 'symbol', 'Ticker', 'ticker'] if col in df_all.columns), None)
    
    if symbol_col is None:
        st.error("❌ שגיאה: לא מצאתי עמודה המכילה את סימולי המניות בטבלה הראשית.")
        return
        
    symbols_list = df_all[symbol_col].dropna().unique().tolist()
    
    if not symbols_list:
        st.warning("⚠️ לא נמצאו מניות בטבלה.")
        return

    sel = st.selectbox("בחר מניה לסימולציה:", symbols_list)
    
    if sel:
        st.markdown(f"#### הגדרות אסטרטגיה עבור: **{sel}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            years = st.slider("תקופת הבדיקה (שנים אחרונות)", 1, 10, 3)
        with col2:
            fast_ma = st.number_input("ממוצע נע מהיר (ימים)", min_value=5, max_value=50, value=20)
        with col3:
            slow_ma = st.number_input("ממוצע נע איטי (ימים)", min_value=50, max_value=250, value=50)

        st.info(f"💡 **האסטרטגיה (SMA Crossover):** המערכת 'תקנה' את המניה כשהממוצע של {fast_ma} ימים יחצה כלפי מעלה את הממוצע של {slow_ma} ימים, ו'תמכור' כשיחצה מטה.")

        if st.button("🚀 הרץ סימולציה (Backtest)", type="primary"):
            with st.spinner("מוריד נתונים היסטוריים ומחשב סימולציה..."):
                # הורדת נתונים
                end_date = datetime.now()
                start_date = end_date - timedelta(days=years * 365)
                df = yf.download(sel, start=start_date, end=end_date, progress=False)
                
                if df.empty:
                    st.error("לא הצלחתי להוריד נתונים עבור המניה הזו.")
                else:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    # חישוב הממוצעים הנעים
                    df['Fast_MA'] = df['Close'].rolling(window=fast_ma).mean()
                    df['Slow_MA'] = df['Close'].rolling(window=slow_ma).mean()
                    
                    # יצירת איתותי קנייה/מכירה (1 = קנייה/החזקה, 0 = בחוץ)
                    df['Signal'] = np.where(df['Fast_MA'] > df['Slow_MA'], 1, 0)
                    
                    # חישוב תשואות יומיות
                    df['Daily_Return'] = df['Close'].pct_change()
                    
                    # תשואת האסטרטגיה (איתות של אתמול כפול התשואה של היום)
                    df['Strategy_Return'] = df['Signal'].shift(1) * df['Daily_Return']
                    
                    # חישוב תשואה מצטברת (השקעה של 100$)
                    df['Buy_Hold_Equity'] = (1 + df['Daily_Return']).cumprod() * 100
                    df['Strategy_Equity'] = (1 + df['Strategy_Return']).cumprod() * 100
                    
                    df = df.dropna()

                    # --- הצגת תוצאות ---
                    buy_hold_total = (df['Buy_Hold_Equity'].iloc[-1] - 100)
                    strategy_total = (df['Strategy_Equity'].iloc[-1] - 100)
                    
                    st.subheader("📊 תוצאות הסימולציה")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("תשואת האסטרטגיה", f"{strategy_total:.2f}%", f"{strategy_total - buy_hold_total:.2f}% מול השוק")
                    m2.metric("תשואת קנה והחזק", f"{buy_hold_total:.2f}%")
                    
                    # שרטוט גרף התשואות
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Buy_Hold_Equity'], mode='lines', name='קנה והחזק (Buy & Hold)', line=dict(color='gray', dash='dot')))
                    fig.add_trace(go.Scatter(x=df.index, y=df['Strategy_Equity'], mode='lines', name='אסטרטגיה', line=dict(color='#ff9800', width=2)))
                    
                    fig.update_layout(title="צמיחת תיק השקעות (התחלה מ-$100)", template='plotly_white', xaxis_title="תאריך", yaxis_title="שווי התיק ($)")
                    st.plotly_chart(fig, use_container_width=True)
