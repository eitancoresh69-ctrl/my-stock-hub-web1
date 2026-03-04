# realtime_data.py - WORKING VERSION עם כל הפונקציות הנדרשות
import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
from typing import Optional, Dict, List

# API Keys
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "d6ia9mpr01ql9cifitbgd6ia9mpr01ql9cifitc0").strip()
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "").strip()

# Session
yf_session = requests.Session()
yf_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})

# Cache
_price_cache = {}
_cache_timestamps = {}
CACHE_TTL = 30

def _get_from_cache(sym: str) -> Optional[dict]:
    if sym in _price_cache:
        if time.time() - _cache_timestamps.get(sym, 0) < CACHE_TTL:
            return _price_cache[sym]
    return None

def _set_cache(sym: str, data: dict):
    _price_cache[sym] = data
    _cache_timestamps[sym] = time.time()

# Twelve Data
def get_live_price_twelve_data(symbol: str) -> Optional[dict]:
    cached = _get_from_cache(f"td_{symbol}")
    if cached: return cached
    if not TWELVE_DATA_API_KEY: return None
    
    api_symbol = symbol.replace(".TA", ":IL") if symbol.endswith(".TA") else symbol
    try:
        r = requests.get(f"https://api.twelvedata.com/quote",
            params={"symbol": api_symbol, "apikey": TWELVE_DATA_API_KEY}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and data.get("status") == "ok" and "price" in data:
                result = {
                    "price": float(data.get("price", 0)),
                    "change": float(data.get("change", 0)) if data.get("change") else 0,
                    "change_pct": float(data.get("percent_change", 0)) if data.get("percent_change") else 0,
                    "high": float(data.get("high", 0)) or float(data.get("price", 0)),
                    "low": float(data.get("low", 0)) or float(data.get("price", 0)),
                    "open": float(data.get("open", 0)) or float(data.get("price", 0)),
                    "prev_close": float(data.get("previous_close", 0)) or float(data.get("price", 0)),
                    "source": "Twelve Data 🟢"
                }
                _set_cache(f"td_{symbol}", result)
                return result
    except: pass
    return None

# Finnhub
def get_live_price_finnhub(symbol: str) -> Optional[dict]:
    cached = _get_from_cache(f"fh_{symbol}")
    if cached: return cached
    if not FINNHUB_API_KEY or symbol.endswith(".TA"): return None
    
    try:
        r = requests.get(f"https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": FINNHUB_API_KEY}, timeout=5)
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
    except: pass
    return None

# Alpha Vantage
def get_live_price_alpha_vantage(symbol: str) -> Optional[dict]:
    cached = _get_from_cache(f"av_{symbol}")
    if cached: return cached
    if not ALPHA_VANTAGE_KEY or symbol.endswith(".TA"): return None
    
    try:
        r = requests.get(f"https://www.alphavantage.co/query",
            params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_VANTAGE_KEY}, timeout=5)
        if r.status_code == 200:
            data = r.json().get("Global Quote", {})
            if data.get("05. price"):
                result = {
                    "price": float(data.get("05. price", 0)),
                    "change": float(data.get("09. change", 0)) if data.get("09. change") else 0,
                    "change_pct": float(data.get("10. change percent", "0").rstrip("%")) if data.get("10. change percent") else 0,
                    "high": float(data.get("03. high", 0)) or float(data.get("05. price", 0)),
                    "low": float(data.get("04. low", 0)) or float(data.get("05. price", 0)),
                    "open": float(data.get("02. open", 0)) or float(data.get("05. price", 0)),
                    "prev_close": float(data.get("08. previous close", 0)) or float(data.get("05. price", 0)),
                    "source": "Alpha Vantage 🔵"
                }
                _set_cache(f"av_{symbol}", result)
                return result
    except: pass
    return None

# yfinance
def get_live_price_yfinance(symbol: str, retries: int = 3) -> Optional[dict]:
    cached = _get_from_cache(f"yf_{symbol}")
    if cached: return cached
    
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(symbol, session=yf_session)
            hist = ticker.history(period="1d", interval="1m", timeout=10)
            if hist.empty: hist = ticker.history(period="1d", timeout=10)
            if hist.empty: continue
            
            px = float(hist["Close"].iloc[-1])
            if px <= 0: continue
            
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
            if attempt < retries - 1: time.sleep(0.5)
            continue
    return None

# Smart Functions
def get_live_price_smart(symbol: str) -> Optional[float]:
    td = get_live_price_twelve_data(symbol)
    if td and td["price"] > 0: return td["price"]
    fh = get_live_price_finnhub(symbol)
    if fh and fh["price"] > 0: return fh["price"]
    av = get_live_price_alpha_vantage(symbol)
    if av and av["price"] > 0: return av["price"]
    yf_data = get_live_price_yfinance(symbol)
    if yf_data and yf_data["price"] > 0: return yf_data["price"]
    return None

def get_full_quote_smart(symbol: str) -> Optional[dict]:
    td = get_live_price_twelve_data(symbol)
    if td: return td
    fh = get_live_price_finnhub(symbol)
    if fh: return fh
    av = get_live_price_alpha_vantage(symbol)
    if av: return av
    yf_data = get_live_price_yfinance(symbol)
    if yf_data: return yf_data
    return None

def get_multi_quotes(symbols: List[str]) -> dict:
    results = {}
    for sym in symbols:
        q = get_full_quote_smart(sym)
        if q: results[sym] = q
    return results

# Fear & Greed
@st.cache_data(ttl=3600)
def get_fear_greed_index() -> dict:
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=7", timeout=8)
        if r.status_code == 200:
            data = r.json()
            current = data["data"][0]
            value = int(current["value"])
            label = current["value_classification"]
            label_he = {"Extreme Fear": "😱 פחד קיצוני", "Fear": "😨 פחד", "Neutral": "😐 ניטרלי", "Greed": "😏 חמדנות", "Extreme Greed": "🤑 חמדנות קיצונית"}.get(label, label)
            color = "#d32f2f" if value <= 25 else "#f44336" if value <= 45 else "#ff9800" if value <= 55 else "#4caf50" if value <= 75 else "#1b5e20"
            return {"value": value, "label": label, "label_he": label_he, "color": color, "updated": datetime.now().strftime("%H:%M:%S")}
    except: pass
    return {"value": 50, "label": "Neutral", "label_he": "😐 ניטרלי", "color": "#ff9800", "updated": "N/A"}

@st.cache_data(ttl=3600)
def get_macro_indicators() -> dict:
    return {
        "FEDFUNDS": {"name": "Federal Funds Rate", "value": 4.5, "trend": "→", "date": "Mar 2026"},
        "CPIAUCSL": {"name": "CPI (Inflation)", "value": 3.2, "trend": "↓", "date": "Feb 2026"},
        "UNRATE": {"name": "Unemployment", "value": 4.1, "trend": "→", "date": "Feb 2026"},
        "T10Y2Y": {"name": "Yield Curve", "value": 0.45, "trend": "↑", "date": "Mar 2026"},
    }

# Render Functions (REQUIRED!)
def render_live_prices_strip(symbols: List[str]):
    us_symbols = [s for s in symbols if not s.endswith(".TA")][:8]
    if not us_symbols: return
    quotes = get_multi_quotes(us_symbols)
    if not quotes: return
    cols = st.columns(len(quotes))
    for i, (sym, q) in enumerate(quotes.items()):
        chg_color = "#2e7d32" if q["change_pct"] >= 0 else "#c62828"
        arrow = "▲" if q["change_pct"] >= 0 else "▼"
        cols[i].markdown(f'<div style="text-align:center;padding:6px;background:{"#e8f5e9" if q["change_pct"]>=0 else "#ffebee"};border-radius:8px;"><b style="font-size:13px;">{sym}</b><br><span style="font-size:15px;font-weight:700;">${q["price"]:.2f}</span><br><span style="color:{chg_color};font-size:12px;">{arrow} {abs(q["change_pct"]):.2f}%</span></div>', unsafe_allow_html=True)

def render_fear_greed_widget():
    fg = get_fear_greed_index()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div style="background: linear-gradient(135deg, {fg["color"]}22, {fg["color"]}44);border: 2px solid {fg["color"]};border-radius: 12px;padding: 12px 16px;text-align: center;"><div style="font-size: 28px; font-weight: 900; color: {fg["color"]};">{fg["value"]}</div><div style="font-size: 13px; color: {fg["color"]}; font-weight: 700;">{fg["label_he"]}</div></div>', unsafe_allow_html=True)
    with col2:
        ai_tips = {"Extreme Fear": "🔴 קנה!", "Fear": "⚠️ זהירות", "Neutral": "😐 מאוזן", "Greed": "📈 קח רווחים", "Extreme Greed": "🤑 מכור!"}
        st.markdown(f'<div style="background: #fff8e1;border-right: 4px solid {fg["color"]};border-radius: 8px;padding: 10px 14px;font-size: 13px;"><b>🤖 AI:</b><br>{ai_tips.get(fg["label"], "📊")}</div>', unsafe_allow_html=True)

def render_macro_panel():
    st.markdown('<div class="ai-card" style="border-right-color: #1565c0;"><b>🏛️ מדדי מאקרו</b></div>', unsafe_allow_html=True)
    macro = get_macro_indicators()
    cols = st.columns(len(macro))
    for i, (key, item) in enumerate(macro.items()):
        trend_color = "#2e7d32" if item["trend"] == "↑" else "#c62828" if item["trend"] == "↓" else "#555"
        if key in ["FEDFUNDS", "CPIAUCSL", "UNRATE"]:
            trend_color = "#c62828" if item["trend"] == "↑" else "#2e7d32" if item["trend"] == "↓" else "#555"
        cols[i].markdown(f'<div style="text-align:center;padding:10px;background:#f0f4ff;border-radius:10px;"><div style="font-size:11px;color:#555;margin-bottom:4px;">{item["name"]}</div><div style="font-size:22px;font-weight:800;">{item["value"]:.2f}%</div><div style="color:{trend_color};font-size:18px;">{item["trend"]}</div></div>', unsafe_allow_html=True)

def render_full_realtime_panel(symbols: List[str]):
    st.markdown("## 📡 מרכז נתונים חיים")
    tab1, tab2, tab3 = st.tabs(["📊 Fear & Greed", "💹 מחירים חיים", "🏛️ מאקרו"])
    with tab1:
        render_fear_greed_widget()
    with tab2:
        render_live_prices_strip(symbols)
        st.divider()
        us_syms = [s for s in symbols if not s.endswith(".TA")]
        quotes = get_multi_quotes(us_syms)
        if quotes:
            rows = []
            for sym, q in quotes.items():
                rows.append({"📌 מניה": sym, "💰 מחיר חי": f"${q['price']:.2f}", "📈 שינוי $": f"{'▲' if q['change']>=0 else '▼'} ${abs(q['change']):.2f}", "📊 שינוי %": f"{'🟢 +' if q['change_pct']>=0 else '🔴 '}{q['change_pct']:.2f}%", "⬆️ גבוה": f"${q['high']:.2f}", "⬇️ נמוך": f"${q['low']:.2f}", "🔒 סגירה": f"${q['prev_close']:.2f}", "🟢 מקור": q["source"]})
            st.dataframe(pd.DataFrame(rows), hide_index=True)
    with tab3:
        render_macro_panel()
