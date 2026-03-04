# logic.py — לוגיקה מרכזית + Integration עם realtime_data + Traders Support
# ═══════════════════════════════════════════════════════════════════════════════════════════════════

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

# Import ה-Smart price function מ-realtime_data
try:
    from realtime_data import get_live_price_smart, get_full_quote_smart
    HAS_REALTIME = True
except ImportError:
    HAS_REALTIME = False

# Session עם headers טובים
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
})

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                         EMPTY COLUMNS DEFINITION                             ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

EMPTY_COLUMNS = [
    "Symbol", "Name", "Type", "Currency", "Emoji", "Price", "PriceStr", 
    "Change", "MA50", "MA200", "RSI", "Score", "RevGrowth", "EarnGrowth", 
    "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "Action", "AI_Logic"
]

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                    SINGLE SYMBOL FETCH WITH OPTIMIZATION                     ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def _fetch_single_symbol(symbol: str, retries: int = 2) -> dict | None:
    """
    שולף נתונים עבור סימול בודד עם:
    - קריאה ל-realtime_data כדי להביא מחיר חי
    - Retry logic
    - Timeout protection
    """
    for attempt in range(retries):
        try:
            # ─── שלב 1: קבל מחיר חי מ-realtime_data (אם זמין) ──────────────────
            
            live_price = None
            if HAS_REALTIME:
                try:
                    quote = get_full_quote_smart(symbol)
                    if quote:
                        live_price = quote.get("price", 0)
                except:
                    pass
            
            # ─── שלב 2: קבל נתונים מ-yfinance (אם צריך היסטוריה) ──────────────
            
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
            
            # אם אין נתונים, נסה תקופה קצרה יותר
            if hist.empty:
                hist = ticker.history(period="3mo", timeout=10)
            if hist.empty:
                hist = ticker.history(period="1mo", timeout=10)
            if hist.empty:
                hist = ticker.history(period="1d", timeout=10)
            
            if hist.empty:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None
            
            # ─── שלב 3: חילוץ נתונים בסיסיים ──────────────────────────────────
            
            # משתמש ב-live_price אם יש, אחרת מה-yfinance
            if live_price and live_price > 0:
                px = live_price
            else:
                px = float(hist["Close"].iloc[-1])
            
            if px <= 0:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None
            
            # חילוץ מידע מחברה
            try:
                info = ticker.info if ticker.info else {}
            except:
                info = {}
            
            # ─── חישוב מדדים ────────────────────────────────────────────────────
            
            # 1. Revenue Growth
            rev_g = 0
            try:
                if info.get("revenueGrowth"):
                    rev_g = float(info.get("revenueGrowth", 0)) * 100
                    if rev_g is None:
                        rev_g = 0
            except:
                rev_g = 0
            
            # 2. Profit Margin
            margin = 0
            try:
                if info.get("profitMargins"):
                    margin = float(info.get("profitMargins", 0)) * 100
                    if margin is None:
                        margin = 0
            except:
                margin = 0
            
            # 3. ROE
            roe = 0
            try:
                if info.get("returnOnEquity"):
                    roe = float(info.get("returnOnEquity", 0)) * 100
                    if roe is None:
                        roe = 0
            except:
                roe = 0
            
            # 4. Dividend Yield
            div_yield = 0
            try:
                if info.get("dividendYield"):
                    div_yield = float(info.get("dividendYield", 0)) * 100
                    if div_yield is None:
                        div_yield = 0
            except:
                div_yield = 0
            
            # 5. Score
            score = 0
            if rev_g > 10: score += 1
            if margin > 10: score += 1
            if roe > 15: score += 1
            if div_yield > 2: score += 1
            
            # 6. Change
            change = 0
            change_pct = 0
            if len(hist) > 1:
                try:
                    prev_close = float(hist["Close"].iloc[-2])
                    change = ((px / prev_close) - 1) * 100
                    change_pct = change
                except:
                    change = 0
                    change_pct = 0
            
            # 7. MA50 ו-MA200
            ma50 = px
            ma200 = px
            try:
                if len(hist) >= 50:
                    ma50 = float(hist["Close"].tail(50).mean())
                if len(hist) >= 200:
                    ma200 = float(hist["Close"].tail(200).mean())
            except:
                pass
            
            # 8. RSI
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
                    else:
                        rsi = 100 if gains > 0 else 50
            except:
                rsi = 50.0
            
            # 9. Action
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
            
            # ─── בנה תוצאה מלאה ────────────────────────────────────────────────
            
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
                "AI_Logic": f"Score:{score} | RSI:{rsi:.0f} | Price:${px:.2f}"
            }
        
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
            return None
    
    return None


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                         MASTER DATA FETCHING                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(ttl=600)  # 10 דקות cache
def fetch_master_data(tickers: list, max_workers: int = 5) -> pd.DataFrame:
    """
    שולף נתונים לרשימת mTickets בעיוות מקבילה.
    משלב realtime_data + yfinance.
    מחזיר DataFrame שהtraders יכולים להשתמש בו.
    """
    if not tickers:
        return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    rows = []
    
    # ThreadPool עם תיאום בין משימות
    with ThreadPoolExecutor(max_workers=min(max_workers, len(tickers))) as executor:
        futures = {executor.submit(_fetch_single_symbol, t): t for t in set(tickers)}
        
        for future in as_completed(futures):
            try:
                res = future.result(timeout=15)
                if res:
                    rows.append(res)
            except Exception:
                pass
    
    # בנה DataFrame אם יש נתונים
    if rows:
        try:
            df = pd.DataFrame(rows)
            return df
        except Exception:
            return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    # Return empty with columns
    return pd.DataFrame(columns=EMPTY_COLUMNS)


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                         HELPER FUNCTIONS                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def get_asset_type(s):
    """חזר סוג נכס"""
    if s.endswith(".TA"):
        return "Stocks (TA)"
    elif "BTC" in s or "ETH" in s or s.endswith("-USD"):
        return "Crypto"
    elif "=" in s:
        return "Commodity"
    return "Stock"

def get_asset_currency(s):
    """חזר מטבע"""
    if "BTC" in s or "ETH" in s:
        return "₿"
    elif s.endswith(".TA"):
        return "₪"
    return "$"

def get_asset_emoji(s):
    """חזר emoji"""
    if s.endswith(".TA"):
        return "🇮🇱"
    elif "BTC" in s:
        return "₿"
    elif "ETH" in s:
        return "Ξ"
    elif "=" in s:
        return "⛽"
    return "📈"

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                    TRADER COMPATIBILITY FUNCTIONS                            ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def get_price(symbol: str) -> float | None:
    """קבל מחיר בודד לטריידר"""
    if HAS_REALTIME:
        try:
            return get_live_price_smart(symbol)
        except:
            pass
    
    # Fallback ל-yfinance
    try:
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period="1d", timeout=5)
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except:
        pass
    
    return None

def get_multiple_prices(symbols: list) -> dict:
    """קבל מחירים מרובים לטריידרים"""
    results = {}
    for sym in symbols:
        price = get_price(sym)
        if price:
            results[sym] = price
    return results
