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


# ✅ REQUIRED FUNCTIONS - חיוני שיהיה בקובץ!

def _should_auto_scan():
    """בדוק אם עבר מספיק זמן מהסריקה האחרונה"""
    last_scan = st.session_state.get("last_scan_dt")
    if not last_scan:
        return True
    elapsed = (datetime.now() - last_scan).total_seconds() / 60
    interval = st.session_state.get("auto_scan_interval_min", 30)
    return elapsed >= interval


def _push_to_agents(df, mode):
    """דחוף נתונים לסוכנים"""
    try:
        from storage import save
        if mode in ["שניהם", "סוכנים"]:
            save("scan_results", df.to_dict("records"))
    except:
        pass


def maybe_auto_scan():
    """קוראים לזה מapp.py - חיוני!"""
    if not _should_auto_scan():
        return
    universe_name = st.session_state.get("auto_scan_universe", "S&P500 Top 100")
    universe = UNIVERSE_MAP.get(universe_name, SP500_TOP)
    mode = st.session_state.get("auto_scan_mode", "שניהם")

    placeholder = st.empty()
    with placeholder.container():
        st.info(f"🔄 סריקה אוטומטית — {universe_name}")
        prog_ph = st.empty()
        df = _run_scan_raw(universe, prog_ph)

    placeholder.empty()

    if not df.empty:
        st.session_state["scan_results"] = df
        st.session_state["last_scan_dt"] = datetime.now()
        st.session_state["scan_time"] = datetime.now().strftime("%H:%M:%S")
        _push_to_agents(df, mode)


def render_market_scanner():
    """ממשק סורק שוק"""
    st.markdown("## 📊 סורק שוק")
    
    col1, col2 = st.columns(2)
    with col1:
        universe_name = st.selectbox("🌍 בחר יקום:", list(UNIVERSE_MAP.keys()))
    with col2:
        st.info(f"📈 {len(UNIVERSE_MAP[universe_name])} מניות")
    
    if st.button("🔍 סרוק עכשיו"):
        universe = UNIVERSE_MAP[universe_name]
        with st.spinner("🔄 סורק..."):
            df = _run_scan_raw(universe, st.empty())
            if not df.empty:
                st.dataframe(df[["Symbol", "Price", "RSI", "Score"]], hide_index=True)
                st.success(f"✅ סרוק - {len(df)} מניות")
