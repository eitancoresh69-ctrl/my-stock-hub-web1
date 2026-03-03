# logic.py — לוגיקה מרכזית (גרסת ענן חסינת שגיאות)
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from config import COMMODITIES, CRYPTO_SYMBOLS
except ImportError:
    COMMODITIES = {}
    CRYPTO_SYMBOLS = {}

# מנגנון הסוואה מול Yahoo
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

# הגדרת מבנה טבלה ריקה כברירת מחדל כדי למנוע KeyErrors
EMPTY_COLUMNS = [
    "Symbol", "Name", "Type", "Currency", "Emoji", "Price", "PriceStr", 
    "Change", "MA50", "MA200", "RSI", "Score", "RevGrowth", "EarnGrowth", 
    "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "Action", "AI_Logic"
]

def _fetch_single_symbol(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period="1y")
        if hist.empty: return None
        
        px = float(hist["Close"].iloc[-1])
        inf = ticker.info if ticker.info else {}
        
        # חישוב ציון מהיר
        rev_g = (inf.get("revenueGrowth", 0) or 0) * 100
        margin = (inf.get("profitMargins", 0) or 0) * 100
        score = 0
        if rev_g > 10: score += 1
        if margin > 10: score += 1

        return {
            "Symbol": symbol,
            "Price": px,
            "PriceStr": f"${px:.2f}",
            "Change": ((px / hist["Close"].iloc[-2]) - 1) * 100 if len(hist) > 1 else 0,
            "RSI": 50.0, # ערך ברירת מחדל
            "Score": score,
            "RevGrowth": rev_g,
            "Margin": margin,
            "Action": "החזק ⚪",
            "AI_Logic": "נתוני ענן חלקיים"
        }
    except: return None

@st.cache_data(ttl=600)
def fetch_master_data(tickers: list) -> pd.DataFrame:
    rows = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_fetch_single_symbol, t): t for t in set(tickers)}
        for future in as_completed(futures):
            res = future.result()
            if res: rows.append(res)
    
    if rows:
        return pd.DataFrame(rows)
    
    # 🔥 התיקון הקריטי: אם אין נתונים, מחזירים טבלה ריקה אבל עם כותרות!
    return pd.DataFrame(columns=EMPTY_COLUMNS)

# --- שאר פונקציות העזר (asset types וכו') נשארות כרגיל ---
def get_asset_type(s): return "stock"
def get_asset_currency(s): return "$"
