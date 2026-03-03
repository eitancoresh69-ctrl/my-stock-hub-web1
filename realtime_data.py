# realtime_data.py — נתונים בזמן אמת: Twelve Data (ראשי) + Finnhub (backup) + Fear & Greed
# ═══════════════════════════════════════════════════════════════════════════════════════════════════
# 🔑 הגדרה - Twelve Data API:
#    1. Render → Settings → Environment Variables
#    2. הוסף: TWELVE_DATA_API_KEY = [הקוד שלך מ-Twelve Data]
#    3. Deploy מחדש ואפליקציה תשתמש בנתונים החיים אוטומטית!
# ═══════════════════════════════════════════════════════════════════════════════════════════════════

import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# ─── הגדרת API Keys ──────────────────────────────────────────────────────────
# 🔑 Twelve Data API Key (נמצא בסביבה של Render)
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY", "")
TWELVE_DATA_BASE = "https://api.twelvedata.com"

# 🔑 Finnhub API Key (backup אם Twelve Data לא זמין)
FINNHUB_API_KEY = "d6ia9mpr01ql9cifitbgd6ia9mpr01ql9cifitc0"
FINNHUB_BASE    = "https://finnhub.io/api/v1"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 0: Twelve Data — מחירים חיים (בעדיפות גבוהה!)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=30)  # רענון כל 30 שניות!
def get_live_price_twelve_data(symbol: str) -> dict | None:
    """
    שולף מחיר חי מ-Twelve Data. מדויק וموثوק!
    מחזיר: {"price": 213.5, "change": 1.2, "change_pct": 0.57, "high": 215.0, "low": 212.1}
    """
    # אם אין Key, לא משתמשים
    if not TWELVE_DATA_API_KEY or TWELVE_DATA_API_KEY == "":
        return None

    # סימולים ישראליים דורשים סיומת מיוחדת ב-Twelve Data
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
        
        if r.status_code != 200:
            return None  # בעיה עם ה-API
            
        data = r.json()
        
        # בדיקה שהנתונים קיימים ותקינים
        if isinstance(data, dict) and "price" in data:
            price = float(data.get("price", 0))
            if price > 0:
                return {
                    "price":      price,
                    "change":     float(data.get("change", 0)) if data.get("change") else 0,
                    "change_pct": float(data.get("percent_change", 0)) if data.get("percent_change") else 0,
                    "high":       float(data.get("high", 0)) if data.get("high") else price,
                    "low":        float(data.get("low", 0)) if data.get("low") else price,
                    "open":       float(data.get("open", 0)) if data.get("open") else price,
                    "prev_close": float(data.get("previous_close", 0)) if data.get("previous_close") else price,
                    "source":     "Twelve Data 🟢 חי"
                }
    except requests.exceptions.RequestException:
        pass
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Finnhub — מחירים חיים (backup אם Twelve Data לא זמין)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=30)  # רענון כל 30 שניות!
def get_live_price_finnhub(symbol: str) -> dict | None:
    """
    שולף מחיר חי מ-Finnhub. מהיר ומדויק יותר מ-yfinance.
    מחזיר: {"price": 213.5, "change": 1.2, "change_pct": 0.57, "high": 215.0, "low": 212.1}
    """
    # אם אין Key תקין, פשוט חזור None
    if not FINNHUB_API_KEY or FINNHUB_API_KEY == "YOUR_FINNHUB_KEY_HERE":
        return None  # אין Key — חזור ל-yfinance

    # המרת סימולים ישראליים: AAPL.TA → לא נתמך ב-Finnhub, ממשיך ב-yfinance
    if symbol.endswith(".TA"):
        return None

    try:
        r = requests.get(
            f"{FINNHUB_BASE}/quote",
            params={"symbol": symbol, "token": FINNHUB_API_KEY},
            timeout=5
        )
        if r.status_code != 200:
            return None  # בעיה עם ה-API
            
        data = r.json()
        
        # בדיקה שהנתונים קיימים ותקינים
        if isinstance(data, dict) and data.get("c", 0) > 0:
            return {
                "price":      data.get("c", 0),   # current price
                "change":     data.get("d", 0),   # change in $
                "change_pct": data.get("dp", 0),  # change in %
                "high":       data.get("h", 0),   # high of day
                "low":        data.get("l", 0),   # low of day
                "open":       data.get("o", 0),   # open price
                "prev_close": data.get("pc", 0),  # previous close
                "source":     "finnhub 🟢 חי"
            }
    except requests.exceptions.RequestException:
        # בעיה ברשת - חזור None כדי שנשתמש ב-yfinance
        pass
    except Exception:
        # כל שגיאה אחרת - חזור None
        pass
    return None


@st.cache_data(ttl=30)
def get_live_price_smart(symbol: str) -> float | None:
    """
    מחזיר מחיר חי — מנסה Twelve Data קודם, אחר כך Finnhub, נפילה ל-yfinance.
    זה מחליף את _get_live_price() ב-simulator.py
    """
    # ניסיון Twelve Data קודם (הטוב ביותר!)
    td = get_live_price_twelve_data(symbol)
    if td:
        return td["price"]
    
    # ניסיון Finnhub (חלופה)
    fh = get_live_price_finnhub(symbol)
    if fh:
        return fh["price"]

    # נפילה ל-yfinance (15 דקות עיכוב)
    try:
        h = yf.Ticker(symbol).history(period="1d", interval="1m")
        if not h.empty:
            return float(h["Close"].iloc[-1])
    except Exception:
        pass
    return None


@st.cache_data(ttl=300)
def get_multi_quotes_finnhub(symbols: list) -> dict:
    """
    שולף מחירים לרשימת מניות בבת-אחת.
    מחזיר: {"AAPL": {"price": 213.5, ...}, "NVDA": {...}, ...}
    """
    results = {}
    for sym in symbols:
        if not sym.endswith(".TA"):
            # נסה Twelve Data קודם
            data = get_live_price_twelve_data(sym)
            if not data:
                # fallback ל-Finnhub
                data = get_live_price_finnhub(sym)
            if data:
                results[sym] = data
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Fear & Greed Index — מדד הפחד/חמדנות של CNN
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)  # רענון כל שעה
def get_fear_greed_index() -> dict:
    """
    שולף את מדד Fear & Greed של CNN Markets.
    0-25 = פחד קיצוני 😱 | 26-45 = פחד 😨 | 46-55 = ניטרלי 😐
    56-75 = חמדנות 😏 | 76-100 = חמדנות קיצונית 🤑
    """
    try:
        r = requests.get(
            "https://api.alternative.me/fng/?limit=7",
            timeout=8
        )
        data = r.json()
        current = data["data"][0]
        history = data["data"][:7]

        value = int(current["value"])
        label = current["value_classification"]

        # תרגום לעברית
        label_he = {
            "Extreme Fear":    "😱 פחד קיצוני",
            "Fear":            "😨 פחד",
            "Neutral":         "😐 ניטרלי",
            "Greed":           "😏 חמדנות",
            "Extreme Greed":   "🤑 חמדנות קיצונית",
        }.get(label, label)

        # צבע לפי ערך
        if value <= 25:
            color = "#d32f2f"   # אדום כהה
        elif value <= 45:
            color = "#f44336"   # אדום
        elif value <= 55:
            color = "#ff9800"   # כתום
        elif value <= 75:
            color = "#4caf50"   # ירוק
        else:
            color = "#1b5e20"   # ירוק כהה

        # היסטוריה של 7 ימים
        hist_values = [
            {
                "date":  datetime.fromtimestamp(int(h["timestamp"])).strftime("%d/%m"),
                "value": int(h["value"]),
                "label": h["value_classification"],
            }
            for h in reversed(history)
        ]

        # המלצת AI לפי מדד
        if value <= 25:
            ai_tip = "💎 פחד קיצוני = הזדמנות קנייה היסטורית. Buffett קונה בפחד."
        elif value <= 45:
            ai_tip = "🛒 שוק בפחד. חפש מניות זהב (ציון 5+) בהנחה."
        elif value <= 55:
            ai_tip = "⚖️ שוק מאוזן. עקוב אחר אסטרטגיית ה-PDF."
        elif value <= 75:
            ai_tip = "⚠️ חמדנות בשוק. הקטן פוזיציות בסיכון גבוה."
        else:
            ai_tip = "🔴 חמדנות קיצונית! זמן לממש רווחים ולהגדיל מזומן."

        return {
            "value":      value,
            "label":      label,
            "label_he":   label_he,
            "color":      color,
            "ai_tip":     ai_tip,
            "history":    hist_values,
            "updated":    datetime.now().strftime("%H:%M"),
            "ok":         True,
        }

    except Exception as e:
        return {
            "value":    50,
            "label":    "Neutral",
            "label_he": "😐 לא זמין",
            "color":    "#9e9e9e",
            "ai_tip":   "לא ניתן לטעון את מדד הפחד/חמדנות.",
            "history":  [],
            "updated":  "—",
            "ok":       False,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: מדדי מאקרו — FRED API (הפדרל ריזרב, חינם)
# ═══════════════════════════════════════════════════════════════════════════════

FRED_API_KEY = "YOUR_FRED_KEY_HERE"
# 🔑 הרשמה חינמית: https://fred.stlouisfed.org/docs/api/api_key.html

@st.cache_data(ttl=86400)  # רענון פעם ביום
def get_macro_indicators() -> dict:
    """
    שולף מדדי מאקרו מ-FRED (Federal Reserve Economic Data).
    ריבית, אינפלציה, אבטלה, GDP.
    """
    indicators = {
        "FEDFUNDS":  "ריבית הפד %",
        "CPIAUCSL":  "אינפלציה (CPI)",
        "UNRATE":    "אבטלה %",
        "T10Y2Y":    "עקום תשואות (10Y-2Y)",
        "BAMLH0A0HYM2": "מרווח אג\"ח זבל",
    }

    results = {}

    if FRED_API_KEY == "YOUR_FRED_KEY_HERE":
        # ערכים לדוגמה אם אין Key
        return {
            "FEDFUNDS":  {"name": "ריבית הפד %",       "value": 5.33, "date": "2025-01", "trend": "→"},
            "CPIAUCSL":  {"name": "אינפלציה (CPI)",    "value": 3.1,  "date": "2025-01", "trend": "↓"},
            "UNRATE":    {"name": "אבטלה %",            "value": 3.7,  "date": "2025-01", "trend": "→"},
            "T10Y2Y":    {"name": "עקום תשואות",        "value": 0.2,  "date": "2025-01", "trend": "↑"},
            "BAMLH0A0HYM2": {"name": "מרווח אג\"ח זבל", "value": 3.1, "date": "2025-01", "trend": "→"},
            "_demo": True,
        }

    for series_id, name in indicators.items():
        try:
            r = requests.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={
                    "series_id":     series_id,
                    "api_key":       FRED_API_KEY,
                    "file_type":     "json",
                    "sort_order":    "desc",
                    "limit":         2,
                    "observation_start": "2024-01-01",
                },
                timeout=8
            )
            obs = r.json().get("observations", [])
            if obs:
                curr = float(obs[0]["value"])
                prev = float(obs[1]["value"]) if len(obs) > 1 else curr
                trend = "↑" if curr > prev else ("↓" if curr < prev else "→")
                results[series_id] = {
                    "name":  name,
                    "value": curr,
                    "date":  obs[0]["date"][:7],
                    "trend": trend,
                }
        except Exception:
            pass

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Finnhub — חדשות חיות + סנטימנט לפי מניה
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)  # רענון כל 10 דקות
def get_finnhub_news(symbol: str, days_back: int = 3) -> list:
    """
    חדשות אחרונות עם ניתוח סנטימנט אמיתי מ-Finnhub.
    """
    if FINNHUB_API_KEY == "YOUR_FINNHUB_KEY_HERE" or symbol.endswith(".TA"):
        return []
    try:
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        to_date   = datetime.now().strftime("%Y-%m-%d")
        r = requests.get(
            f"{FINNHUB_BASE}/company-news",
            params={
                "symbol": symbol,
                "from":   from_date,
                "to":     to_date,
                "token":  FINNHUB_API_KEY,
            },
            timeout=8
        )
        news = r.json()
        if isinstance(news, list):
            return news[:5]
    except Exception:
        pass
    return []


@st.cache_data(ttl=3600)
def get_news_sentiment_finnhub(symbol: str) -> dict | None:
    """
    ניתוח סנטימנט חדשות מ-Finnhub (buzz + sentiment score אמיתי).
    """
    if FINNHUB_API_KEY == "YOUR_FINNHUB_KEY_HERE" or symbol.endswith(".TA"):
        return None
    try:
        r = requests.get(
            f"{FINNHUB_BASE}/news-sentiment",
            params={"symbol": symbol, "token": FINNHUB_API_KEY},
            timeout=8
        )
        data = r.json()
        if "buzz" in data:
            score       = data.get("companyNewsScore", 0)
            buzz_weekly = data.get("buzz", {}).get("weeklyAverage", 0)
            buzz_change = data.get("buzz", {}).get("buzz", 0)
            bullish     = data.get("sentiment", {}).get("bullishPercent", 0.5)
            bearish     = data.get("sentiment", {}).get("bearishPercent", 0.5)

            if score > 0.6:
                label = "🟢 חיובי מאוד"
            elif score > 0.4:
                label = "🟡 חיובי מעט"
            elif score > 0.2:
                label = "⚪ ניטרלי"
            else:
                label = "🔴 שלילי"

            return {
                "score":       round(score, 2),
                "label":       label,
                "bullish_pct": round(bullish * 100, 1),
                "bearish_pct": round(bearish * 100, 1),
                "buzz_weekly": round(buzz_weekly, 1),
                "buzz_change": round(buzz_change, 2),
            }
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)
def get_insider_transactions(symbol: str) -> list:
    """
    עסקאות insiders אמיתיות מ-Finnhub (מי קנה/מכר מניות ומתי).
    """
    if FINNHUB_API_KEY == "YOUR_FINNHUB_KEY_HERE" or symbol.endswith(".TA"):
        return []
    try:
        r = requests.get(
            f"{FINNHUB_BASE}/stock/insider-transactions",
            params={"symbol": symbol, "token": FINNHUB_API_KEY},
            timeout=8
        )
        data = r.json()
        transactions = data.get("data", [])
        result = []
        for t in transactions[:8]:
            result.append({
                "name":     t.get("name", ""),
                "shares":   t.get("share", 0),
                "value":    t.get("transactionPrice", 0),
                "type":     "🟢 קנייה" if t.get("transactionCode") in ["P", "A"] else "🔴 מכירה",
                "date":     t.get("transactionDate", ""),
                "title":    t.get("reportedTitle", ""),
            })
        return result
    except Exception:
        pass
    return []


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: SEC EDGAR — הגשות רשמיות (חינם לחלוטין, ללא Key)
# ═══════════════════════════════════════════════════════════════════════════════

# מיפוי סימולים ל-CIK (מספר זיהוי SEC)
TICKER_TO_CIK = {
    "AAPL":  "0000320193",
    "MSFT":  "0000789019",
    "NVDA":  "0001045810",
    "TSLA":  "0001318605",
    "META":  "0001326801",
    "AMZN":  "0001018724",
    "GOOGL": "0001652044",
    "PLTR":  "0001321655",
    "AMD":   "0000002488",
    "NFLX":  "0001065280",
}

@st.cache_data(ttl=86400)
def get_sec_filings(symbol: str) -> list:
    """
    הגשות SEC אחרונות (10-Q, 10-K, 8-K) ישירות ממאגר הממשלה.
    ללא API Key — ציבורי לחלוטין.
    """
    cik = TICKER_TO_CIK.get(symbol.upper())
    if not cik:
        return []
    try:
        r = requests.get(
            f"https://data.sec.gov/submissions/CIK{cik}.json",
            headers={"User-Agent": "StockHub contact@stockhub.com"},
            timeout=10
        )
        data = r.json()
        filings      = data.get("filings", {}).get("recent", {})
        forms        = filings.get("form", [])
        dates        = filings.get("filingDate", [])
        descriptions = filings.get("primaryDocument", [])
        accessions   = filings.get("accessionNumber", [])

        result = []
        relevant_forms = {"10-K", "10-Q", "8-K", "4"}
        for i, form in enumerate(forms[:30]):
            if form in relevant_forms:
                acc = accessions[i].replace("-", "")
                url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{descriptions[i]}"
                result.append({
                    "form":  form,
                    "date":  dates[i],
                    "desc":  descriptions[i],
                    "url":   url,
                    "label": {
                        "10-K": "📋 דוח שנתי",
                        "10-Q": "📊 דוח רבעוני",
                        "8-K":  "⚡ אירוע מהותי",
                        "4":    "👤 עסקת Insider",
                    }.get(form, form),
                })
                if len(result) >= 6:
                    break
        return result
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: ווידג'ט Fear & Greed + Live Prices לתצוגה ב-app.py
# ═══════════════════════════════════════════════════════════════════════════════

def render_fear_greed_widget():
    """
    מציג את מדד Fear & Greed בצורה ויזואלית בראש האפליקציה.
    קרא לזה ב-app.py ליד המדדים העליונים.
    """
    fg = get_fear_greed_index()

    # מד גרפי
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
    if fg["history"]:
        hist_df = pd.DataFrame(fg["history"])
        st.caption("📅 Fear & Greed — 7 ימים אחרונים:")
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


def render_live_prices_strip(symbols: list):
    """
    פס מחירים חיים בראש הדף — כמו Ticker Tape בטלוויזיה פיננסית.
    """
    if FINNHUB_API_KEY == "YOUR_FINNHUB_KEY_HERE":
        st.info("💡 הוסף Finnhub API Key ב-realtime_data.py לקבלת מחירים חיים (חינם בfinnhub.io)")
        return

    us_symbols = [s for s in symbols if not s.endswith(".TA")][:8]
    quotes     = get_multi_quotes_finnhub(us_symbols)

    if not quotes:
        return

    cols = st.columns(len(quotes))
    for i, (sym, q) in enumerate(quotes.items()):
        chg_color = "#2e7d32" if q["change_pct"] >= 0 else "#c62828"
        arrow     = "▲" if q["change_pct"] >= 0 else "▼"
        cols[i].markdown(
            f'<div style="text-align:center;padding:6px;background:{"#e8f5e9" if q["change_pct"]>=0 else "#ffebee"};border-radius:8px;">'
            f'<b style="font-size:13px;">{sym}</b><br>'
            f'<span style="font-size:15px;font-weight:700;">${q["price"]:.2f}</span><br>'
            f'<span style="color:{chg_color};font-size:12px;">{arrow} {abs(q["change_pct"]):.2f}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_macro_panel():
    """
    פאנל מדדי מאקרו — ריבית, אינפלציה, אבטלה.
    """
    st.markdown(
        '<div class="ai-card" style="border-right-color: #1565c0;">'
        '<b>🏛️ מדדי מאקרו — Federal Reserve Data (FRED)</b></div>',
        unsafe_allow_html=True,
    )

    macro = get_macro_indicators()
    is_demo = macro.pop("_demo", False)

    if is_demo:
        st.info("💡 הוסף FRED API Key ב-realtime_data.py לנתונים מעודכנים (חינם ב-fred.stlouisfed.org)")

    cols = st.columns(len(macro))
    for i, (key, item) in enumerate(macro.items()):
        trend_color = "#2e7d32" if item["trend"] == "↑" else "#c62828" if item["trend"] == "↓" else "#555"
        # ריבית ואינפלציה — "↑" זה רע! הפוך את הצבעים
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

    # ניתוח AI מהיר
    st.divider()
    macro_vals = list(macro.values())
    if macro_vals:
        fedfunds = next((v["value"] for k,v in macro.items() if k == "FEDFUNDS"), 5.0)
        cpi      = next((v["value"] for k,v in macro.items() if k == "CPIAUCSL"), 3.0)
        t10y2y   = next((v["value"] for k,v in macro.items() if k == "T10Y2Y"),  0.0)

        if fedfunds > 5.0:
            rate_msg = "⚠️ ריבית גבוהה — לחץ על מניות צמיחה. מועדף: דיבידנד + ערך."
        elif fedfunds < 3.0:
            rate_msg = "🚀 ריבית נמוכה — סביבה טובה לצמיחה. Tech ו-Growth מועדפים."
        else:
            rate_msg = "⚖️ ריבית מתונה — שוק מאוזן. ניתן לאזן Growth + Value."

        if t10y2y < 0:
            curve_msg = "🔴 עקום הפוך — סיגנל מיתון היסטורי! הגדל מזומן."
        elif t10y2y < 0.5:
            curve_msg = "⚠️ עקום שטוח — אזהרה כלכלית. זהירות מוגברת."
        else:
            curve_msg = "🟢 עקום תקין — כלכלה צומחת. Risk-On מוצדק."

        col1, col2 = st.columns(2)
        col1.markdown(f'<div class="ai-card">{rate_msg}</div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="ai-card">{curve_msg}</div>', unsafe_allow_html=True)


def render_full_realtime_panel(symbols: list):
    """
    פאנל ראשי של כל נתוני הזמן-אמת — קרא לזה מ-app.py
    """
    st.markdown("## 📡 מרכז נתונים חיים")

    tab1, tab2, tab3 = st.tabs(["📊 Fear & Greed", "💹 מחירים חיים", "🏛️ מאקרו"])

    with tab1:
        render_fear_greed_widget()

    with tab2:
        render_live_prices_strip(symbols)
        st.divider()

        # מחירים מפורטים עם Finnhub
        if FINNHUB_API_KEY != "YOUR_FINNHUB_KEY_HERE":
            us_syms = [s for s in symbols if not s.endswith(".TA")]
            quotes  = get_multi_quotes_finnhub(us_syms)
            if quotes:
                rows = []
                for sym, q in quotes.items():
                    rows.append({
                        "📌 מניה":        sym,
                        "💰 מחיר חי":     f"${q['price']:.2f}",
                        "📈 שינוי $":     f"{'▲' if q['change']>=0 else '▼'} ${abs(q['change']):.2f}",
                        "📊 שינוי %":     f"{'🟢 +' if q['change_pct']>=0 else '🔴 '}{q['change_pct']:.2f}%",
                        "⬆️ גבוה יומי":   f"${q['high']:.2f}",
                        "⬇️ נמוך יומי":   f"${q['low']:.2f}",
                        "🔒 סגירה קודמת": f"${q['prev_close']:.2f}",
                        "🟢 מקור":        q["source"],
                    })
                st.dataframe(pd.DataFrame(rows), hide_index=True)
                st.caption(f"🔄 מחירים עם עיכוב < 30 שניות | עדכון אחרון: {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.info("הוסף Finnhub API Key לקבלת מחירים חיים")

    with tab3:
        render_macro_panel()
