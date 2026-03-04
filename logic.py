# logic.py — לוגיקה מרכזית עם Fallback מרובות ותקני Streamlit 1.30
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

# מנגנון הסוואה מול Yahoo עם headers טובים
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
})

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                         MAIN DATA FETCHING FUNCTION                          ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

EMPTY_COLUMNS = [
    "Symbol", "Name", "Type", "Currency", "Emoji", "Price", "PriceStr", 
    "Change", "MA50", "MA200", "RSI", "Score", "RevGrowth", "EarnGrowth", 
    "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "Action", "AI_Logic"
]

def _fetch_single_symbol(symbol: str, retries: int = 3) -> dict | None:
    """
    שולף נתונים עבור סימול בודד עם retries וfallback.
    """
    for attempt in range(retries):
        try:
            # אם זה סימול ישראלי, נסה קודם עם .TA
            if symbol.endswith(".TA"):
                try:
                    ticker = yf.Ticker(symbol, session=session)
                    hist = ticker.history(period="1y", timeout=10)
                    if hist.empty:
                        # נסה בלי .TA
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
            
            # אם אין נתונים, נסה שוב עם פרק זמן קצר יותר
            if hist.empty:
                hist = ticker.history(period="3mo", timeout=10)
            if hist.empty:
                hist = ticker.history(period="1mo", timeout=10)
            if hist.empty:
                hist = ticker.history(period="1d", timeout=10)
            
            if hist.empty: 
                if attempt < retries - 1:
                    time.sleep(0.5)  # חכה לפני retry
                    continue
                return None
            
            # חילוץ נתונים בסיסיים
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
            
            # 3. ROE (Return on Equity)
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
            
            # 5. חישוב Score
            score = 0
            if rev_g > 10: score += 1
            if margin > 10: score += 1
            if roe > 15: score += 1
            if div_yield > 2: score += 1
            
            # 6. חישוב שינוי יומי
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
            
            # 8. RSI (Simple)
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
            
            # 9. Action Recommendation
            if score >= 5:
                action = "קנה 🟢"
            elif score >= 3:
                action = "תחזיק ⚪"
            else:
                action = "מכור 🔴"
            
            # בדוק אם יש עיד ארוך מ-MA50/200
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
                "AI_Logic": f"Score:{score} | RSI:{rsi:.0f} | RevGr:{rev_g:.0f}%"
            }
        
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5)  # חכה לפני retry
                continue
            # Return None בכישלון סופי
            return None
    
    return None


@st.cache_data(ttl=600)  # 10 דקות cache
def fetch_master_data(tickers: list, max_workers: int = 5) -> pd.DataFrame:
    """
    שולף נתונים עבור רשימת mTickets בעיוות מקבילה.
    עם retry logic וfallback הגדרה.
    """
    if not tickers:
        return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    rows = []
    
    # השתמש בThreadPoolExecutor עם max_workers מעט יותר גדול
    with ThreadPoolExecutor(max_workers=min(max_workers, len(tickers))) as executor:
        # הגש את כל הsymbols בו-זמנית
        futures = {executor.submit(_fetch_single_symbol, t): t for t in set(tickers)}
        
        # אסוף תוצאות כשהן מוכנות
        for future in as_completed(futures):
            try:
                res = future.result(timeout=15)  # 15 שניות per symbol
                if res:
                    rows.append(res)
            except Exception:
                # Skip symbols that fail
                pass
    
    # אם יש נתונים, בנה DataFrame
    if rows:
        try:
            df = pd.DataFrame(rows)
            return df
        except Exception:
            return pd.DataFrame(columns=EMPTY_COLUMNS)
    
    # אם אין נתונים, בחזור ל-DataFrame ריקה אבל עם כותרות
    return pd.DataFrame(columns=EMPTY_COLUMNS)


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                          ASSET TYPE HELPERS                                  ║
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
