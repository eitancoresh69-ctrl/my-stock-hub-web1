# backtest_ai.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

@st.cache_data(ttl=3600)
def run_simple_backtest(symbol, initial_capital):
    try:
        hist = yf.Ticker(symbol).history(period="2y")
        if hist.empty: return None, None
        
        # חישוב אסטרטגיית קנה והחזק (Buy & Hold)
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        shares_bought = initial_capital / start_price
        final_value = shares_bought * end_price
        profit_pct = ((final_value / initial_capital) - 1) * 100
        
        # חישוב אסטרטגיית מומנטום (RSI - קנה בנפילות)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().replace(0, 1e-10)
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        return hist, {"BuyHold_Profit": profit_pct, "Final_Value": final_value}
    except:
        return None, None

def render_backtester(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>⏪ מכונת זמן פיננסית (Backtesting):</b> בדוק איך המניות שלך היו מתנהגות בשנתיים האחרונות עם סכום השקעה התחלתי.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sel = st.selectbox("בחר מניה לסימולציית עבר:", df_all['Symbol'].unique())
    with col2:
        capital = st.number_input("סכום השקעה התחלתי ($/₪):", min_value=1000, value=10000, step=1000)
        
    if st.button("⏪ הרץ בדיקת עבר (שנתיים אחורה)"):
        with st.spinner("מריץ אלפי חישובים לאחור..."):
            hist, results = run_simple_backtest(sel, capital)
            
            if hist is not None and results is not None:
                st.success(f"**תוצאות הסימולציה ל-{sel}:**")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("השקעה התחלתית", f"{capital:,.0f}")
                c2.metric("שווי סופי כיום", f"{results['Final_Value']:,.0f}")
                c3.metric("תשואה כוללת (%)", f"{results['BuyHold_Profit']:.1f}%")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='מחיר מניה', line=dict(color='#1a73e8')))
                fig.update_layout(title="מסע המחיר לאורך הסימולציה", height=300, template="plotly_white", margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **תובנת AI:** אסטרטגיית קנה-והחזק (Buy & Hold) של חברות שעומדות בקריטריוני ה-PDF היא לרוב רווחית יותר לאורך זמן מאשר מסחר יומי קופצני המלווה בעמלות.")
            else:
                st.error("לא ניתן להריץ סימולציה למניה זו. חסרים נתוני עבר מספקים.")
