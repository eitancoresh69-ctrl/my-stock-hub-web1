# logic.py — לוגיקה מרכזית v3: מניות + סחורות + קריפטו + ת"א (גרסת ענן חסינה)
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

# ─── מנגנון הסוואה למניעת חסימות בענן מול Yahoo Finance ─────────────────────
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})

# ─── סיווג סוג נכס ──────────────────────────────────────────────────────────
def get_asset_type(symbol: str) -> str:
    if symbol in COMMODITIES:           return "commodity"
    if symbol in CRYPTO_SYMBOLS:        return "crypto"
    if symbol.endswith(".TA"):          return "tase"
    return "stock"

def get_asset_currency(symbol: str) -> str:
    if symbol.endswith(".TA"):   return "אג'"
    if symbol in CRYPTO_SYMBOLS: return "$"
    if symbol in COMMODITIES:    return "$"
    return "$"

def get_asset_emoji(symbol: str) -> str:
    if symbol in COMMODITIES:    return COMMODITIES[symbol].get("emoji", "📈")
    if symbol in CRYPTO_SYMBOLS: return CRYPTO_SYMBOLS[symbol].get("emoji", "₿")
    if symbol.endswith(".TA"):   return "🇮🇱"
    return "📈"

def get_asset_name(symbol: str) -> str:
    if symbol in COMMODITIES:    return COMMODITIES[symbol].get("name", symbol)
    if symbol in CRYPTO_SYMBOLS: return CRYPTO_SYMBOLS[symbol].get("name", symbol)
    return symbol

# ─── RSI חישוב ───────────────────────────────────────────────────────────────
def calc_rsi(series: pd.Series, period: int = 14) -> float:
    if len(series) < period + 1:
        return 50.0
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean().replace(0, 1e-10)
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

# ─── שאיבת נתונים מקיפה לנכס בודד ──────────────────────────────────────────
def _fetch_single_symbol(symbol: str) -> dict:
    try:
        # שימוש בסשן המוסווה כדי למנוע חסימה
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period="1y")
        
        if hist.empty or len(hist) < 20:
            return None

        px = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else px
        chg = ((px / prev) - 1) * 100

        # מדדים טכניים
        ma50 = float(hist["Close"].rolling(50).mean().iloc[-1]) if len(hist) >= 50 else px
        ma200 = float(hist["Close"].rolling(200).mean().iloc[-1]) if len(hist) >= 200 else px
        rsi = calc_rsi(hist["Close"])

        # נתוני יסוד (Fundamentals)
        inf = ticker.info if ticker.info else {}
        
        rev_growth  = (inf.get("revenueGrowth", 0) or 0) * 100
        earn_growth = (inf.get("earningsGrowth", 0) or 0) * 100
        margin      = (inf.get("profitMargins", 0) or 0) * 100
        roe         = (inf.get("returnOnEquity", 0) or 0) * 100
        cash        = inf.get("totalCash", 0) or 0
        debt        = inf.get("totalDebt", 0) or 0
        
        # חישוב ציון PDF 0-6
        score = 0
        if rev_growth > 10: score += 1
        if earn_growth > 10: score += 1
        if margin > 10: score += 1
        if roe > 15: score += 1
        if cash > debt: score += 1
        if debt == 0: score += 1

        target = inf.get("targetMeanPrice", 0) or 0
        target_upside = ((target / px) - 1) * 100 if target > px else 0
        
        insider_pct = (inf.get("heldPercentInsiders", 0) or 0) * 100

        # אריזת הנתונים למילון
        return {
            "Symbol":       symbol,
            "Name":         get_asset_name(symbol),
            "Type":         get_asset_type(symbol),
            "Currency":     get_asset_currency(symbol),
            "Emoji":        get_asset_emoji(symbol),
            "Price":        px,
            "PriceStr":     f"{get_asset_currency(symbol)}{px:.2f}",
            "Change":       chg,
            "MA50":         ma50,
            "MA200":        ma200,
            "RSI":          rsi,
            "Score":        score,
            "RevGrowth":    rev_growth,
            "EarnGrowth":   earn_growth,
            "Margin":       margin,
            "ROE":          roe,
            "CashVsDebt":   "✅" if cash > debt else "❌",
            "ZeroDebt":     "✅" if debt == 0 else "❌",
            "DivYield":     (inf.get("dividendYield", 0) or 0) * 100,
            "DivRate":      inf.get("dividendRate", 0) or 0,
            "PayoutRatio":  (inf.get("payoutRatio", 0) or 0) * 100,
            "ExDate":       inf.get("exDividendDate", None),
            "FairValue":    target,
            "TargetUpside": target_upside,
            "InsiderHeld":  insider_pct,
            "Sector":       inf.get("sector", "כללי"),
            # לוגיקה בסיסית לסוכנים
            "Action":       "קנייה 🟢" if (score >= 4 and rsi < 50) else "מכירה 🔴" if rsi > 70 else "החזק ⚪",
            "AI_Logic":     f"ציון {score}/6, סביבת RSI {rsi:.0f}"
        }
    except Exception as e:
        return None

# ─── פונקציית המאסטר (סריקה מקבילית) ───────────────────────────────────────
@st.cache_data(ttl=600) # שומר נתונים ל-10 דקות
def fetch_master_data(tickers: list) -> pd.DataFrame:
    rows = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_fetch_single_symbol, t): t for t in set(tickers)}
        for future in as_completed(futures):
            res = future.result()
            if res:
                rows.append(res)
    
    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame()
