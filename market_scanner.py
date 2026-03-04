# market_scanner.py — סורק שוק - FIXED - משתמש ב-fetch_master_data
import streamlit as st
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# ✅ Import מ-logic!
try:
    from logic import fetch_master_data
    HAS_LOGIC = True
except:
    HAS_LOGIC = False
    import yfinance as yf

# ─── יקומים ─────────────────────────────────────────────────────────────
SP500_TOP = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","AVGO","LLY","V",
    "JPM","XOM","UNH","MA","JNJ","PG","HD","COST","ABBV","MRK",
]
NASDAQ_GROWTH = [
    "PLTR","CRWD","SNOW","DDOG","ZS","MDB","MELI","SHOP","CELH","TTD",
]
TASE_STOCKS = [
    "ENLT.TA","POLI.TA","LUMI.TA","TEVA.TA","ICL.TA",
]

ALL_UNIVERSE = list(set(SP500_TOP + NASDAQ_GROWTH + TASE_STOCKS))

UNIVERSE_MAP = {
    "S&P500 Top 100": SP500_TOP,
    "NASDAQ צמיחה": NASDAQ_GROWTH,
    "כל השוק": ALL_UNIVERSE,
    'ת"א': TASE_STOCKS,
}

def run_market_scanner():
    st.markdown("## 📊 סורק שוק")
    
    col1, col2 = st.columns(2)
    with col1:
        universe = st.selectbox("🌍 בחר יקום:", list(UNIVERSE_MAP.keys()))
    with col2:
        st.info(f"📈 {len(UNIVERSE_MAP[universe])} מניות")
    
    tickers = UNIVERSE_MAP[universe]
    
    if st.button("🔍 סרוק עכשיו"):
        with st.spinner("🔄 סורק..."):
            # ✅ קבל דטה מ-fetch_master_data!
            if HAS_LOGIC:
                df = fetch_master_data(tickers)
                if df.empty:
                    st.warning("⏳ מחכה לנתונים...")
                    return
            else:
                st.error("❌ logic module לא זמין")
                return
            
            # מין לפי Score
            df = df.sort_values("Score", ascending=False)
            
            # הצג תוצאות
            st.dataframe(
                df[["Symbol", "Price", "Change", "RSI", "Score", "Action"]],
                hide_index=True
            )
            
            st.success(f"✅ סרוק הסתיים - {len(df)} מניות")

# קריאה
if __name__ != "__main__":
    run_market_scanner()
