# realtime_data.py — נתונים בזמן אמת: Multi-Source + Smart Cache + Retry Logic
# ═══════════════════════════════════════════════════════════════════════════════════════════════════

import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# ─── הגדרת API Keys מסביבת Render ──────────────────────────────────────────────
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
TWELVE_DATA_BASE = "https://api.twelvedata.com"

FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "").strip()
if not FINNHUB_API_KEY:
    FINNHUB_API_KEY = "d6ia9mpr01ql9cifitbgd6ia9mpr01ql9cifitc0"
FINNHUB_BASE = "https://finnhub.io/api/v1"

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "").strip()
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co"

# Session עם User-Agent טוב
yf_session = requests.Session()
yf_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})

# ─── Local Cache Dictionary (In-Memory) ──────────────────────────────────────
_price_cache = {}
_cache_timestamps = {}
CACHE_TTL = 30  # 30 שניות

def _get_from_cache(symbol: str) -> Optional[dict]:
    """קבל מחיר מהcache אם תקף"""
    if symbol in _price_cache:
        if time.time() - _cache_timestamps.get(symbol, 0) < CACHE_TTL:
            return _price_cache[symbol]
    return None

def _set_cache(symbol: str, data: dict):
    """שמור מחיר בcache"""
    _price_cache[symbol] = data
    _cache_timestamps[symbol] = time.time()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 0: Twelve Data — מחירים חיים (Priority 1)
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_twelve_data(symbol: str) -> Optional[dict]:
    """שולף מחיר חי מ-Twelve Data"""
    cached = _get_from_cache(f"td_{symbol}")
    if cached:
        return cached

    if not TWELVE_DATA_API_KEY:
        return None

    api_symbol = symbol.replace(".TA", ":IL") if symbol.endswith(".TA") else symbol

    try:
        r = requests.get(
            f"{TWELVE_DATA_BASE}/quote",
            params={"symbol": api_symbol, "apikey": TWELVE_DATA_API_KEY},
            timeout=5
        )
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and data.get("status") == "ok" and "price" in data:
                result = {
                    "price": float(data.get("price", 0)),
                    "change": float(data.get("change", 0)) if data.get("change") else 0,
                    "change_pct": float(data.get("percent_change", 0)) if data.get("percent_change") else 0,
                    "high": float(data.get("high", 0)) if data.get("high") else float(data.get("price", 0)),
                    "low": float(data.get("low", 0)) if data.get("low") else float(data.get("price", 0)),
                    "open": float(data.get("open", 0)) if data.get("open") else float(data.get("price", 0)),
                    "prev_close": float(data.get("previous_close", 0)) if data.get("previous_close") else float(data.get("price", 0)),
                    "source": "Twelve Data 🟢"
                }
                _set_cache(f"td_{symbol}", result)
                return result
    except:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Finnhub — מחירים חיים (Priority 2 - תמיד זמין!)
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_finnhub(symbol: str) -> Optional[dict]:
    """שולף מחיר חי מ-Finnhub"""
    cached = _get_from_cache(f"fh_{symbol}")
    if cached:
        return cached

    if not FINNHUB_API_KEY or symbol.endswith(".TA"):
        return None

    try:
        r = requests.get(
            f"{FINNHUB_BASE}/quote",
            params={"symbol": symbol, "token": FINNHUB_API_KEY},
            timeout=5
        )
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and data.get("c", 0) > 0:
                result = {
                    "price": data.get("c", 0),
                    "change": data.get("d", 0),
                    "change_pct": data.get("dp", 0),
                    "high": data.get("h", 0),
                    "low": data.get("l", 0),
                    "open": data.get("o", 0),
                    "prev_close": data.get("pc", 0),
                    "source": "Finnhub 🟡"
                }
                _set_cache(f"fh_{symbol}", result)
                return result
    except:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Alpha Vantage (Priority 3)
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_alpha_vantage(symbol: str) -> Optional[dict]:
    """שולף מחיר מ-Alpha Vantage"""
    cached = _get_from_cache(f"av_{symbol}")
    if cached:
        return cached

    if not ALPHA_VANTAGE_KEY or symbol.endswith(".TA"):
        return None

    try:
        r = requests.get(
            f"{ALPHA_VANTAGE_BASE}/query",
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": ALPHA_VANTAGE_KEY
            },
            timeout=5
        )
        
        if r.status_code == 200:
            data = r.json().get("Global Quote", {})
            if data.get("05. price"):
                result = {
                    "price": float(data.get("05. price", 0)),
                    "change": float(data.get("09. change", 0)) if data.get("09. change") else 0,
                    "change_pct": float(data.get("10. change percent", "0").rstrip("%")) if data.get("10. change percent") else 0,
                    "high": float(data.get("03. high", 0)) if data.get("03. high") else float(data.get("05. price", 0)),
                    "low": float(data.get("04. low", 0)) if data.get("04. low") else float(data.get("05. price", 0)),
                    "open": float(data.get("02. open", 0)) if data.get("02. open") else float(data.get("05. price", 0)),
                    "prev_close": float(data.get("08. previous close", 0)) if data.get("08. previous close") else float(data.get("05. price", 0)),
                    "source": "Alpha Vantage 🔵"
                }
                _set_cache(f"av_{symbol}", result)
                return result
    except:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: yfinance — Fallback סופי עם Retry (Priority 4)
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_yfinance(symbol: str, retries: int = 3) -> Optional[dict]:
    """שולף מחיר מ-yfinance עם retry"""
    cached = _get_from_cache(f"yf_{symbol}")
    if cached:
        return cached

    for attempt in range(retries):
        try:
            ticker = yf.Ticker(symbol, session=yf_session)
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                hist = ticker.history(period="1d")
            
            if hist.empty:
                continue
            
            px = float(hist["Close"].iloc[-1])
            if px <= 0:
                continue
            
            prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else px
            change = px - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0
            
            result = {
                "price": px,
                "change": change,
                "change_pct": change_pct,
                "high": float(hist["High"].max()),
                "low": float(hist["Low"].min()),
                "open": float(hist["Open"].iloc[0]),
                "prev_close": prev_close,
                "source": "yfinance 🔴"
            }
            _set_cache(f"yf_{symbol}", result)
            return result
        except:
            if attempt < retries - 1:
                time.sleep(0.5)
            continue
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Smart Price Function - מנסה בכל המקורות בסדר עדיפות
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_smart(symbol: str) -> Optional[float]:
    """מחזיר מחיר חי - נסיון Priority Chain"""
    td = get_live_price_twelve_data(symbol)
    if td and td["price"] > 0:
        return td["price"]
    
    fh = get_live_price_finnhub(symbol)
    if fh and fh["price"] > 0:
        return fh["price"]
    
    av = get_live_price_alpha_vantage(symbol)
    if av and av["price"] > 0:
        return av["price"]
    
    yf_data = get_live_price_yfinance(symbol)
    if yf_data and yf_data["price"] > 0:
        return yf_data["price"]
    
    return None


def get_full_quote_smart(symbol: str) -> Optional[dict]:
    """מחזיר quote מלא עם כל הנתונים"""
    td = get_live_price_twelve_data(symbol)
    if td:
        return td
    
    fh = get_live_price_finnhub(symbol)
    if fh:
        return fh
    
    av = get_live_price_alpha_vantage(symbol)
    if av:
        return av
    
    yf_data = get_live_price_yfinance(symbol)
    if yf_data:
        return yf_data
    
    return None


def get_multi_quotes(symbols: List[str]) -> dict:
    """שולף מחירים לרשימת מניות"""
    results = {}
    for sym in symbols:
        q = get_full_quote_smart(sym)
        if q:
            results[sym] = q
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Fear & Greed Index
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def get_fear_greed_index() -> dict:
    """שולף את מדד Fear & Greed"""
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=7", timeout=8)
        if r.status_code == 200:
            data = r.json()
            current = data["data"][0]
            
            value = int(current["value"])
            label = current["value_classification"]
            
            label_he = {
                "Extreme Fear": "😱 פחד קיצוני",
                "Fear": "😨 פחד",
                "Neutral": "😐 ניטרלי",
                "Greed": "😏 חמדנות",
                "Extreme Greed": "🤑 חמדנות קיצונית",
            }.get(label, label)
            
            if value <= 25:
                color = "#d32f2f"
            elif value <= 45:
                color = "#f44336"
            elif value <= 55:
                color = "#ff9800"
            elif value <= 75:
                color = "#4caf50"
            else:
                color = "#1b5e20"
            
            return {
                "value": value,
                "label": label,
                "label_he": label_he,
                "color": color,
                "updated": datetime.now().strftime("%H:%M:%S")
            }
    except:
        pass
    
    return {
        "value": 50,
        "label": "Neutral",
        "label_he": "😐 ניטרלי",
        "color": "#ff9800",
        "updated": "N/A"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Render Widgets
# ═══════════════════════════════════════════════════════════════════════════════

def render_live_prices_strip(symbols: List[str]):
    """פס מחירים חיים"""
    us_symbols = [s for s in symbols if not s.endswith(".TA")][:8]
    if not us_symbols:
        return
    
    with st.spinner("📡 טוען מחירים..."):
        quotes = get_multi_quotes(us_symbols)
    
    if not quotes:
        st.info("💡 טוען מחירים...")
        return
    
    cols = st.columns(len(quotes))
    for i, (sym, q) in enumerate(quotes.items()):
        chg_color = "#2e7d32" if q["change_pct"] >= 0 else "#c62828"
        arrow = "▲" if q["change_pct"] >= 0 else "▼"
        cols[i].markdown(
            f'<div style="text-align:center;padding:6px;background:{"#e8f5e9" if q["change_pct"]>=0 else "#ffebee"};border-radius:8px;">'
            f'<b style="font-size:13px;">{sym}</b><br>'
            f'<span style="font-size:15px;font-weight:700;">${q["price"]:.2f}</span><br>'
            f'<span style="color:{chg_color};font-size:12px;">{arrow} {abs(q["change_pct"]):.2f}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
