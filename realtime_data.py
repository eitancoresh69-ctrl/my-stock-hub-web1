# realtime_data.py — נתונים בזמן אמת: Multi-Source (Twelve Data + Finnhub + Alpha Vantage + yfinance)
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

FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "d6ia9mpr01ql9cifitbgd6ia9mpr01ql9cifitc0").strip()
FINNHUB_BASE = "https://finnhub.io/api/v1"

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "").strip()
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co"

FRED_API_KEY = os.environ.get("FRED_API_KEY", "").strip()

# Session לyfinance עם User-Agent proper
yf_session = requests.Session()
yf_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})

# ─── Local Cache Dictionary (In-Memory, כל session) ──────────────────────────
_price_cache = {}
_cache_timestamps = {}
CACHE_TTL = 30  # 30 שניות

def _get_from_cache(symbol: str) -> Optional[dict]:
    """קבל מחיר מהcache אם הוא עדיין תקף"""
    if symbol in _price_cache:
        if time.time() - _cache_timestamps.get(symbol, 0) < CACHE_TTL:
            return _price_cache[symbol]
    return None

def _set_cache(symbol: str, data: dict):
    """שמור מחיר בcache"""
    _price_cache[symbol] = data
    _cache_timestamps[symbol] = time.time()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 0: Twelve Data — מחירים חיים (אם יש API Key!)
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_twelve_data(symbol: str) -> Optional[dict]:
    """
    שולף מחיר חי מ-Twelve Data. הטוב ביותר אם יש API Key.
    מחזיר: {"price": 213.5, "change": 1.2, "change_pct": 0.57, "high": 215.0, "low": 212.1}
    """
    # בדוק cache קודם
    cached = _get_from_cache(f"td_{symbol}")
    if cached:
        return cached

    if not TWELVE_DATA_API_KEY:
        return None

    # סימולים ישראליים: AAPL.TA → AAPL:IL
    api_symbol = symbol.replace(".TA", ":IL") if symbol.endswith(".TA") else symbol

    try:
        r = requests.get(
            f"{TWELVE_DATA_BASE}/quote",
            params={
                "symbol": api_symbol,
                "apikey": TWELVE_DATA_API_KEY
            },
            timeout=5
        )
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and data.get("status") == "ok" and "price" in data:
                result = {
                    "price":      float(data.get("price", 0)),
                    "change":     float(data.get("change", 0)) if data.get("change") else 0,
                    "change_pct": float(data.get("percent_change", 0)) if data.get("percent_change") else 0,
                    "high":       float(data.get("high", 0)) if data.get("high") else float(data.get("price", 0)),
                    "low":        float(data.get("low", 0)) if data.get("low") else float(data.get("price", 0)),
                    "open":       float(data.get("open", 0)) if data.get("open") else float(data.get("price", 0)),
                    "prev_close": float(data.get("previous_close", 0)) if data.get("previous_close") else float(data.get("price", 0)),
                    "source":     "Twelve Data 🟢"
                }
                _set_cache(f"td_{symbol}", result)
                return result
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        pass
    except Exception:
        pass
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Finnhub — מחירים חיים (backup)
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_finnhub(symbol: str) -> Optional[dict]:
    """
    שולף מחיר חי מ-Finnhub. תמיד זמין (יש API Key default).
    """
    # בדוק cache קודם
    cached = _get_from_cache(f"fh_{symbol}")
    if cached:
        return cached

    if not FINNHUB_API_KEY:
        return None

    # אם זה סימול ישראלי, Finnhub לא תומך
    if symbol.endswith(".TA"):
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
                    "price":      data.get("c", 0),
                    "change":     data.get("d", 0),
                    "change_pct": data.get("dp", 0),
                    "high":       data.get("h", 0),
                    "low":        data.get("l", 0),
                    "open":       data.get("o", 0),
                    "prev_close": data.get("pc", 0),
                    "source":     "Finnhub 🟡"
                }
                _set_cache(f"fh_{symbol}", result)
                return result
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        pass
    except Exception:
        pass
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Alpha Vantage — כמחלופה (אם יש API Key)
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
                    "price":      float(data.get("05. price", 0)),
                    "change":     float(data.get("09. change", 0)) if data.get("09. change") else 0,
                    "change_pct": float(data.get("10. change percent", "0").rstrip("%")) if data.get("10. change percent") else 0,
                    "high":       float(data.get("03. high", 0)) if data.get("03. high") else float(data.get("05. price", 0)),
                    "low":        float(data.get("04. low", 0)) if data.get("04. low") else float(data.get("05. price", 0)),
                    "open":       float(data.get("02. open", 0)) if data.get("02. open") else float(data.get("05. price", 0)),
                    "prev_close": float(data.get("08. previous close", 0)) if data.get("08. previous close") else float(data.get("05. price", 0)),
                    "source":     "Alpha Vantage 🔵"
                }
                _set_cache(f"av_{symbol}", result)
                return result
    except Exception:
        pass
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: yfinance — Fallback סופי (עם retry ותקן)
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_yfinance(symbol: str, retries: int = 3) -> Optional[dict]:
    """
    שולף מחיר מ-yfinance עם retry logic וheaders proper.
    זה הfallback הסופי כשהכל אחר נכשל.
    """
    cached = _get_from_cache(f"yf_{symbol}")
    if cached:
        return cached

    for attempt in range(retries):
        try:
            # בנה ticker עם session מחודשת
            ticker = yf.Ticker(symbol, session=yf_session)
            
            # נסה אחרון 1d עם intraday (אם זמין)
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                # fallback ל-daily
                hist = ticker.history(period="1d")
            
            if hist.empty:
                continue  # retry
            
            px = float(hist["Close"].iloc[-1])
            if px <= 0:
                continue
            
            # חישוב שינוי
            prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else px
            change = px - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0
            
            result = {
                "price":      px,
                "change":     change,
                "change_pct": change_pct,
                "high":       float(hist["High"].max()),
                "low":        float(hist["Low"].min()),
                "open":       float(hist["Open"].iloc[0]),
                "prev_close": prev_close,
                "source":     "yfinance 🔴"
            }
            _set_cache(f"yf_{symbol}", result)
            return result
            
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5)  # קצת עיכוב לפני retry
            continue
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Smart Price Function — מנסה בכל המקורות
# ═══════════════════════════════════════════════════════════════════════════════

def get_live_price_smart(symbol: str) -> Optional[float]:
    """
    מחזיר מחיר חי — נסיון רשת מקורות בסדר עדיפות:
    1. Twelve Data (הטוב ביותר אם יש Key)
    2. Finnhub (תמיד זמין, מהיר)
    3. Alpha Vantage (אם יש Key)
    4. yfinance (fallback סופי, אבל עם retry)
    """
    # 1. Twelve Data
    td = get_live_price_twelve_data(symbol)
    if td and td["price"] > 0:
        return td["price"]
    
    # 2. Finnhub
    fh = get_live_price_finnhub(symbol)
    if fh and fh["price"] > 0:
        return fh["price"]
    
    # 3. Alpha Vantage
    av = get_live_price_alpha_vantage(symbol)
    if av and av["price"] > 0:
        return av["price"]
    
    # 4. yfinance (fallback סופי)
    yf_data = get_live_price_yfinance(symbol)
    if yf_data and yf_data["price"] > 0:
        return yf_data["price"]
    
    return None


def get_full_quote_smart(symbol: str) -> Optional[dict]:
    """מחזיר quote מלא עם כל הנתונים"""
    # 1. Twelve Data
    td = get_live_price_twelve_data(symbol)
    if td:
        return td
    
    # 2. Finnhub
    fh = get_live_price_finnhub(symbol)
    if fh:
        return fh
    
    # 3. Alpha Vantage
    av = get_live_price_alpha_vantage(symbol)
    if av:
        return av
    
    # 4. yfinance
    yf_data = get_live_price_yfinance(symbol)
    if yf_data:
        return yf_data
    
    return None


def get_multi_quotes(symbols: List[str]) -> dict:
    """שולף מחירים לרשימת מניות בעיוות מקבילה"""
    results = {}
    for sym in symbols:
        q = get_full_quote_smart(sym)
        if q:
            results[sym] = q
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Fear & Greed Index ו-Macro Indicators
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def get_fear_greed_index() -> dict:
    """שולף את מדד Fear & Greed של CNN Markets"""
    try:
        r = requests.get(
            "https://api.alternative.me/fng/?limit=7",
            timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            current = data["data"][0]
            history = data["data"][:7]

            value = int(current["value"])
            label = current["value_classification"]

            label_he = {
                "Extreme Fear":    "😱 פחד קיצוני",
                "Fear":            "😨 פחד",
                "Neutral":         "😐 ניטרלי",
                "Greed":           "😏 חמדנות",
                "Extreme Greed":   "🤑 חמדנות קיצונית",
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

            ai_tip = {
                "Extreme Fear": "🔴 זה זמן לקנות! גדול מון מחכים לצד. (מניות Value + Dividends)",
                "Fear": "⚠️ הזהירות גבוהה. קנה בדרגות. (Defensive stocks: Utilities, Consumer Staples)",
                "Neutral": "😐 שוק מאוזן. אחזק עמדה עקבית. (Buy & Hold, DCA)",
                "Greed": "📈 רגישות לתיקון. קח רווחים חלקיים. (Take Profits, אזור נמוך 20%)",
                "Extreme Greed": "🤑 סכנה! היוצא מה-Normal. קח רווחים גדולים! (Reduce Risk, טאקה בריא, מזומן 30%)",
            }.get(label, "📊 מקדמי את מיקומך בהתאם ללימוד שלך")

            return {
                "value": value,
                "label": label,
                "label_he": label_he,
                "color": color,
                "ai_tip": ai_tip,
                "history": [{"value": int(d["value"]), "date": d["timestamp"][:10]} for d in history],
                "updated": datetime.now().strftime("%H:%M:%S")
            }
    except Exception:
        pass
    
    # Demo mode אם יש בעיה
    return {
        "value": 50,
        "label": "Neutral",
        "label_he": "😐 ניטרלי",
        "color": "#ff9800",
        "ai_tip": "📊 חזור מאוחר יותר עבור נתונים עדכניים",
        "history": [],
        "updated": "N/A",
        "_demo": True
    }


@st.cache_data(ttl=3600)
def get_macro_indicators() -> dict:
    """שולף מדדי מאקרו מ-FRED (אם יש Key)"""
    try:
        if not FRED_API_KEY:
            # Demo data
            return {
                "FEDFUNDS": {"name": "Federal Funds Rate", "value": 4.5, "trend": "→", "date": "Feb 2026"},
                "CPIAUCSL": {"name": "CPI (Inflation)", "value": 3.2, "trend": "↓", "date": "Jan 2026"},
                "UNRATE": {"name": "Unemployment", "value": 4.1, "trend": "→", "date": "Jan 2026"},
                "T10Y2Y": {"name": "Yield Curve", "value": 0.45, "trend": "↑", "date": "Mar 2026"},
                "_demo": True
            }
        
        # אם יש Key, תן לזה חשמל
        indicators = {}
        for series_id in ["FEDFUNDS", "CPIAUCSL", "UNRATE", "T10Y2Y"]:
            r = requests.get(
                f"https://api.stlouisfed.org/fred/series/data",
                params={
                    "series_id": series_id,
                    "api_key": FRED_API_KEY,
                    "file_type": "json"
                },
                timeout=5
            )
            if r.status_code == 200:
                obs = r.json().get("observations", [])
                if obs:
                    latest = obs[-1]
                    indicators[series_id] = {
                        "value": float(latest.get("value", 0)),
                        "trend": "→",
                        "date": latest.get("date", "N/A"),
                        "name": {"FEDFUNDS": "Federal Funds Rate",
                                "CPIAUCSL": "CPI (Inflation)",
                                "UNRATE": "Unemployment",
                                "T10Y2Y": "Yield Curve"}.get(series_id, series_id)
                    }
        
        return indicators if indicators else get_macro_indicators()
    except Exception:
        return get_macro_indicators()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Widget Rendering Functions
# ═══════════════════════════════════════════════════════════════════════════════

def render_fear_greed_widget():
    """מציג את מדד Fear & Greed בצורה ויזואלית"""
    fg = get_fear_greed_index()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {fg['color']}22, {fg['color']}44);
                border: 2px solid {fg['color']};
                border-radius: 12px;
                padding: 12px 16px;
                text-align: center;
            ">
                <div style="font-size: 28px; font-weight: 900; color: {fg['color']};">{fg['value']}</div>
                <div style="font-size: 13px; color: {fg['color']}; font-weight: 700;">{fg['label_he']}</div>
                <div style="font-size: 10px; color: #888; margin-top: 4px;">עודכן: {fg['updated']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div style="
                background: #fff8e1;
                border-right: 4px solid {fg['color']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            ">
                <b>🤖 המלצת AI:</b><br>{fg['ai_tip']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # גרף היסטוריה
    if fg.get("history"):
        st.caption("📅 Fear & Greed — 7 ימים אחרונים:")
        hist_df = pd.DataFrame(fg["history"])
        cols = st.columns(len(hist_df))
        for i, (_, row) in enumerate(hist_df.iterrows()):
            v = row["value"]
            c = "#d32f2f" if v <= 25 else "#f44336" if v <= 45 else "#ff9800" if v <= 55 else "#4caf50" if v <= 75 else "#1b5e20"
            cols[i].markdown(
                f'<div style="text-align:center;background:{c}22;border-radius:8px;padding:4px 2px;">'
                f'<b style="color:{c};font-size:16px;">{v}</b><br>'
                f'<span style="font-size:10px;color:#666;">{row["date"]}</span></div>',
                unsafe_allow_html=True,
            )


def render_live_prices_strip(symbols: List[str]):
    """פס מחירים חיים בראש הדף"""
    us_symbols = [s for s in symbols if not s.endswith(".TA")][:8]
    if not us_symbols:
        return
    
    with st.spinner("📡 טוען מחירים חיים..."):
        quotes = get_multi_quotes(us_symbols)

    if not quotes:
        st.info("💡 לא היה אפשר להוביל מחירים כרגע. אנחנו עובדים על זה!")
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
            f'<span style="font-size:9px;color:#888;">({q["source"]})</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_macro_panel():
    """פאנל מדדי מאקרו"""
    st.markdown(
        '<div class="ai-card" style="border-right-color: #1565c0;">'
        '<b>🏛️ מדדי מאקרו — Federal Reserve Data</b></div>',
        unsafe_allow_html=True,
    )

    macro = get_macro_indicators()
    is_demo = macro.pop("_demo", False)

    if is_demo:
        st.info("💡 הוסף FRED API Key למשתנים סביבה לנתונים מעודכנים")

    cols = st.columns(len(macro))
    for i, (key, item) in enumerate(macro.items()):
        trend_color = "#2e7d32" if item["trend"] == "↑" else "#c62828" if item["trend"] == "↓" else "#555"
        if key in ["FEDFUNDS", "CPIAUCSL", "UNRATE", "BAMLH0A0HYM2"]:
            trend_color = "#c62828" if item["trend"] == "↑" else "#2e7d32" if item["trend"] == "↓" else "#555"

        cols[i].markdown(
            f'<div style="text-align:center;padding:10px;background:#f0f4ff;border-radius:10px;">'
            f'<div style="font-size:11px;color:#555;margin-bottom:4px;">{item["name"]}</div>'
            f'<div style="font-size:22px;font-weight:800;">{item["value"]:.2f}%</div>'
            f'<div style="color:{trend_color};font-size:18px;">{item["trend"]}</div>'
            f'<div style="font-size:10px;color:#888;">{item["date"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_full_realtime_panel(symbols: List[str]):
    """פאנל ראשי של כל נתוני הזמן-אמת"""
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
                rows.append({
                    "📌 מניה": sym,
                    "💰 מחיר חי": f"${q['price']:.2f}",
                    "📈 שינוי $": f"{'▲' if q['change']>=0 else '▼'} ${abs(q['change']):.2f}",
                    "📊 שינוי %": f"{'🟢 +' if q['change_pct']>=0 else '🔴 '}{q['change_pct']:.2f}%",
                    "⬆️ גבוה יומי": f"${q['high']:.2f}",
                    "⬇️ נמוך יומי": f"${q['low']:.2f}",
                    "🔒 סגירה קודמת": f"${q['prev_close']:.2f}",
                    "🟢 מקור": q["source"],
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True)
            st.caption(f"🔄 מחירים עם עיכוב < 30 שניות | עדכון אחרון: {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.warning("⚠️ לא יכול לטעון מחירים כרגע. נסה שוב בעוד דקה.")

    with tab3:
        render_macro_panel()
