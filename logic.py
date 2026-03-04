# logic.py - FINAL FIX - No caching, logging, robust
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from config import COMMODITIES, CRYPTO_SYMBOLS
except:
    COMMODITIES = {}
    CRYPTO_SYMBOLS = {}

try:
    from realtime_data import get_full_quote_smart, get_live_price_smart
    _HAS_REALTIME = True
except Exception as e:
    _HAS_REALTIME = False
    get_full_quote_smart = None
    get_live_price_smart = None

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})

EMPTY_COLUMNS = ["Symbol", "Name", "Type", "Currency", "Emoji", "Price", "PriceStr", "Change", "MA50", "MA200", "RSI", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "Action", "AI_Logic"]

def _fetch_single_symbol(symbol: str):
    try:
        # Try to get live price
        live_price = None
        if _HAS_REALTIME and get_full_quote_smart:
            try:
                quote = get_full_quote_smart(symbol)
                if quote and quote.get("price", 0) > 0:
                    live_price = quote.get("price", 0)
            except:
                pass
        
        # Get historical data
        try:
            if symbol.endswith(".TA"):
                ticker = yf.Ticker(symbol, session=session)
                hist = ticker.history(period="1y", timeout=10)
                if hist.empty:
                    ticker = yf.Ticker(symbol.replace(".TA", ""), session=session)
                    hist = ticker.history(period="1y", timeout=10)
            else:
                ticker = yf.Ticker(symbol, session=session)
                hist = ticker.history(period="1y", timeout=10)
        except:
            return None
        
        # Try shorter periods
        if hist.empty:
            hist = ticker.history(period="3mo", timeout=10)
        if hist.empty:
            hist = ticker.history(period="1mo", timeout=10)
        if hist.empty:
            hist = ticker.history(period="1d", timeout=10)
        
        if hist.empty: 
            return None
        
        # Get price
        px = live_price if (live_price and live_price > 0) else float(hist["Close"].iloc[-1])
        if px <= 0:
            return None
        
        # Get info
        try:
            info = ticker.info if ticker.info else {}
        except:
            info = {}
        
        # Metrics
        rev_g = float(info.get("revenueGrowth", 0)) * 100 if info.get("revenueGrowth") else 0
        margin = float(info.get("profitMargins", 0)) * 100 if info.get("profitMargins") else 0
        roe = float(info.get("returnOnEquity", 0)) * 100 if info.get("returnOnEquity") else 0
        div_yield = float(info.get("dividendYield", 0)) * 100 if info.get("dividendYield") else 0
        
        score = 0
        if rev_g > 10: score += 1
        if margin > 10: score += 1
        if roe > 15: score += 1
        if div_yield > 2: score += 1
        
        # Change
        change = 0
        if len(hist) > 1:
            try:
                prev_close = float(hist["Close"].iloc[-2])
                change = ((px / prev_close) - 1) * 100
            except:
                pass
        
        # MA
        ma50 = float(hist["Close"].tail(50).mean()) if len(hist) >= 50 else px
        ma200 = float(hist["Close"].tail(200).mean()) if len(hist) >= 200 else px
        
        # RSI
        rsi = 50.0
        if len(hist) >= 14:
            try:
                closes = hist["Close"].tail(14).values
                deltas = np.diff(closes)
                gains = np.where(deltas > 0, deltas, 0).mean()
                losses = np.where(deltas < 0, -deltas, 0).mean()
                if losses != 0:
                    rs = gains / losses
                    rsi = 100 - (100 / (1 + rs))
            except:
                pass
        
        # Action
        action = "קנה 🟢" if score >= 5 else "תחזיק ⚪" if score >= 3 else "מכור 🔴"
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
            "Change": change,
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

def fetch_master_data(tickers=None, max_workers: int = 5):
    """
    Fetch data for multiple tickers.
    
    Args:
        tickers: list of ticker symbols (required!)
        max_workers: number of parallel workers
    
    Returns:
        DataFrame with stock data or empty DataFrame
    """
    # Handle None or empty input
    if not tickers:
        return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    # Ensure it's a list
    if isinstance(tickers, str):
        tickers = [tickers]
    
    # Remove duplicates
    tickers = list(set(tickers))
    
    if not tickers:
        return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    rows = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(tickers))) as executor:
        futures = {executor.submit(_fetch_single_symbol, t): t for t in tickers}
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
        except Exception as e:
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
