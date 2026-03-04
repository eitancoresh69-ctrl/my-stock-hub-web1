# logic.py — לוגיקה מרכזית עם integration ל-realtime_data
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import streamlit as st
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from config import COMMODITIES, CRYPTO_SYMBOLS
except ImportError:
    COMMODITIES = {}
    CRYPTO_SYMBOLS = {}

# ⭐ CRITICAL: Import from realtime_data!
try:
    from realtime_data import get_full_quote_smart, get_live_price_smart
    HAS_REALTIME = True
except Exception as e:
    HAS_REALTIME = False
    get_full_quote_smart = None
    get_live_price_smart = None

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})

EMPTY_COLUMNS = [
    "Symbol", "Name", "Type", "Currency", "Emoji", "Price", "PriceStr", 
    "Change", "MA50", "MA200", "RSI", "Score", "RevGrowth", "EarnGrowth", 
    "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "Action", "AI_Logic"
]

def _fetch_single_symbol(symbol: str) -> dict:
    try:
        # ⭐ Step 1: Try to get LIVE PRICE from realtime_data!
        live_price = None
        if HAS_REALTIME and get_full_quote_smart:
            try:
                quote = get_full_quote_smart(symbol)
                if quote and quote.get("price", 0) > 0:
                    live_price = quote.get("price", 0)
            except:
                pass
        
        # Step 2: Get historical data from yfinance
        if symbol.endswith(".TA"):
            try:
                ticker = yf.Ticker(symbol, session=session)
                hist = ticker.history(period="1y", timeout=10)
                if hist.empty:
                    symbol_clean = symbol.replace(".TA", "")
                    ticker = yf.Ticker(symbol_clean, session=session)
                    hist = ticker.history(period="1y", timeout=10)
            except:
                symbol_clean = symbol.replace(".TA", "")
                ticker = yf.Ticker(symbol_clean, session=session)
                hist = ticker.history(period="1y", timeout=10)
        else:
            ticker = yf.Ticker(symbol, session=session)
            hist = ticker.history(period="1y", timeout=10)
        
        # Try shorter periods if empty
        if hist.empty:
            hist = ticker.history(period="3mo", timeout=10)
        if hist.empty:
            hist = ticker.history(period="1mo", timeout=10)
        if hist.empty:
            hist = ticker.history(period="1d", timeout=10)
        
        if hist.empty: 
            return None
        
        # ⭐ Use LIVE PRICE if we got it, otherwise use history
        if live_price and live_price > 0:
            px = live_price
        else:
            px = float(hist["Close"].iloc[-1])
        
        if px <= 0:
            return None
        
        # Get company info
        try:
            info = ticker.info if ticker.info else {}
        except:
            info = {}
        
        # Calculate metrics
        rev_g = 0
        try:
            if info.get("revenueGrowth"):
                rev_g = float(info.get("revenueGrowth", 0)) * 100
        except:
            rev_g = 0
        
        margin = 0
        try:
            if info.get("profitMargins"):
                margin = float(info.get("profitMargins", 0)) * 100
        except:
            margin = 0
        
        roe = 0
        try:
            if info.get("returnOnEquity"):
                roe = float(info.get("returnOnEquity", 0)) * 100
        except:
            roe = 0
        
        div_yield = 0
        try:
            if info.get("dividendYield"):
                div_yield = float(info.get("dividendYield", 0)) * 100
        except:
            div_yield = 0
        
        # Score
        score = 0
        if rev_g > 10: score += 1
        if margin > 10: score += 1
        if roe > 15: score += 1
        if div_yield > 2: score += 1
        
        # Change
        change = 0
        change_pct = 0
        if len(hist) > 1:
            try:
                prev_close = float(hist["Close"].iloc[-2])
                change = ((px / prev_close) - 1) * 100
                change_pct = change
            except:
                pass
        
        # MA
        ma50 = px
        ma200 = px
        try:
            if len(hist) >= 50:
                ma50 = float(hist["Close"].tail(50).mean())
            if len(hist) >= 200:
                ma200 = float(hist["Close"].tail(200).mean())
        except:
            pass
        
        # RSI
        rsi = 50.0
        try:
            if len(hist) >= 14:
                closes = hist["Close"].tail(14).values
                deltas = np.diff(closes)
                gains = np.where(deltas > 0, deltas, 0).mean()
                losses = np.where(deltas < 0, -deltas, 0).mean()
                if losses != 0:
                    rs = gains / losses
                    rsi = 100 - (100 / (1 + rs))
        except:
            rsi = 50.0
        
        # Action
        if score >= 5:
            action = "קנה 🟢"
        elif score >= 3:
            action = "תחזיק ⚪"
        else:
            action = "מכור 🔴"
        
        if px > ma50 > ma200:
            action = "קנה 🟢"
        elif px < ma50 < ma200:
            action = "מכור 🔴"
        
        return {
            "Symbol": symbol,
            "Name": info.get("longName", symbol),
            "Type": "Stock",
            "Currency": "$",
            "Emoji": "📈",
            "Price": px,
            "PriceStr": f"${px:.2f}",
            "Change": change_pct,
            "MA50": ma50,
            "MA200": ma200,
            "RSI": rsi,
            "Score": score,
            "RevGrowth": round(rev_g, 2),
            "EarnGrowth": round(info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else 0, 2),
            "Margin": round(margin, 2),
            "ROE": round(roe, 2),
            "CashVsDebt": "כן" if info.get("totalCash", 0) > info.get("totalDebt", 1) else "לא",
            "ZeroDebt": "כן" if info.get("totalDebt", 0) == 0 else "לא",
            "DivYield": round(div_yield, 2),
            "Action": action,
            "AI_Logic": f"Score:{score}|RSI:{rsi:.0f}|${px:.2f}"
        }
    except Exception as e:
        return None

@st.cache_data(ttl=600)
def fetch_master_data(tickers: list, max_workers: int = 5) -> pd.DataFrame:
    if not tickers:
        return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    rows = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(tickers))) as executor:
        futures = {executor.submit(_fetch_single_symbol, t): t for t in set(tickers)}
        for future in as_completed(futures):
            try:
                res = future.result(timeout=15)
                if res:
                    rows.append(res)
            except:
                pass
    
    if rows:
        try:
            df = pd.DataFrame(rows)
            return df
        except:
            return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    return pd.DataFrame(columns=EMPTY_COLUMNS)

def get_asset_type(s):
    if s.endswith(".TA"):
        return "Stocks (TA)"
    elif "BTC" in s or "ETH" in s or s.endswith("-USD"):
        return "Crypto"
    elif "=" in s:
        return "Commodity"
    return "Stock"

def get_asset_currency(s):
    if "BTC" in s or "ETH" in s:
        return "₿"
    elif s.endswith(".TA"):
        return "₪"
    return "$"
