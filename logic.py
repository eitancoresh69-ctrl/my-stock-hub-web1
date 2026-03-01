# logic.py — לוגיקה מרכזית v3: מניות + סחורות + קריפטו + ת"א
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import streamlit as st
from config import COMMODITIES, CRYPTO_SYMBOLS

# ─── סיווג סוג נכס ──────────────────────────────────────────────────────────
def get_asset_type(symbol: str) -> str:
    if symbol in COMMODITIES:           return "commodity"
    if symbol in CRYPTO_SYMBOLS:        return "crypto"
    if symbol.endswith(".TA"):          return "tase"
    return "stock"

def get_asset_currency(symbol: str) -> str:
    if symbol.endswith(".TA"):  return "אג'"
    return "$"

def get_asset_emoji(symbol: str) -> str:
    if symbol in COMMODITIES:   return COMMODITIES[symbol]["emoji"]
    if symbol in CRYPTO_SYMBOLS: return CRYPTO_SYMBOLS[symbol]["emoji"]
    if symbol.endswith(".TA"):   return "🇮🇱"
    return "📈"

def get_asset_name(symbol: str) -> str:
    if symbol in COMMODITIES:    return COMMODITIES[symbol]["name"]
    if symbol in CRYPTO_SYMBOLS: return CRYPTO_SYMBOLS[symbol]["name"]
    return symbol

# ─── RSI ─────────────────────────────────────────────────────────────────────
def calc_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain  = delta.where(delta > 0, 0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(period).mean().replace(0, 1e-10)
    rs    = gain / loss
    rsi   = 100 - (100 / (1 + rs))
    val   = rsi.iloc[-1]
    return float(val) if not np.isnan(val) else 50.0

# ─── ציון PDF (מניות בלבד) ──────────────────────────────────────────────────
def evaluate_pdf_metrics(info: dict) -> tuple:
    score, details = 0, {}
    try:
        rg = info.get("revenueGrowth")
        if rg and rg >= 0.10: score += 1
        details["RevGrowth"] = (rg or 0) * 100

        eg = info.get("earningsGrowth")
        if eg and eg >= 0.10: score += 1
        details["EarnGrowth"] = (eg or 0) * 100

        margin = info.get("profitMargins")
        if margin and margin >= 0.10: score += 1
        details["Margin"] = (margin or 0) * 100

        roe = info.get("returnOnEquity")
        if roe and roe >= 0.15: score += 1
        details["ROE"] = (roe or 0) * 100

        cash = info.get("totalCash") or 0
        debt = info.get("totalDebt") or 0
        if cash > debt:  score += 1
        if debt == 0:    score += 1
        details["Cash"] = cash
        details["Debt"] = debt
    except Exception:
        pass
    return score, details

def get_ai_logic(price: float, fv: float, score: int, currency: str) -> tuple:
    if not fv or fv <= 0:
        return "בבדיקה 🔍", "חסרים נתוני תזרים מזומנים."
    gap = (fv - price) / price if price > 0 else 0
    if score >= 5:
        return ("קנייה חזקה 💎","מניית 'זהב'. בהנחה מהשווי ההוגן.") if gap > 0.05 else ("קנייה 📈","חברה איכותית במחיר הוגן.")
    elif score >= 3:
        return ("איסוף 🛒","חברה טובה במחיר 'מבצע'.") if gap > 0.10 else ("החזק ⚖️","המחיר משקף את השווי.")
    return "מכירה 🔴", "ציון איכות נמוך."

# ─── שליפת נכס בודד ─────────────────────────────────────────────────────────
def _fetch_single(symbol: str, now: datetime.datetime) -> dict | None:
    try:
        atype = get_asset_type(symbol)
        s     = yf.Ticker(symbol)
        h     = s.history(period="3mo")
        if h.empty or len(h) < 5:
            return None

        px         = float(h["Close"].iloc[-1])
        prev_close = float(h["Close"].iloc[-2]) if len(h) >= 2 else px
        change     = ((px / prev_close) - 1) * 100 if prev_close > 0 else 0
        rsi        = calc_rsi(h["Close"])
        ma50       = float(h["Close"].rolling(min(50, len(h))).mean().iloc[-1])
        currency   = get_asset_currency(symbol)
        emoji      = get_asset_emoji(symbol)
        aname      = get_asset_name(symbol)

        base = {
            "Symbol":       symbol,
            "AssetType":    atype,
            "AssetName":    aname,
            "Emoji":        emoji,
            "Price":        px,
            "PriceStr":     f"{currency}{px:,.2f}",
            "Currency":     currency,
            "Change":       change,
            "RSI":          rsi,
            "MA50":         ma50,
            "Score":        0,
            "Action":       "—",
            "AI_Logic":     "—",
            "RevGrowth":    0.0,
            "EarnGrowth":   0.0,
            "Margin":       0.0,
            "ROE":          0.0,
            "CashVsDebt":   "—",
            "ZeroDebt":     "—",
            "DivYield":     0.0,
            "DivRate":      0.0,
            "FiveYrDiv":    0.0,
            "PayoutRatio":  0.0,
            "ExDate":       None,
            "FairValue":    0.0,
            "TargetUpside": 0.0,
            "InsiderHeld":  0.0,
            "Sector":       "—",
            "EarningsDate": "—",
            "DaysToEarnings": -1,
            "Info":         {},
        }

        # ── סחורות: נתונים מינימליים ──────────────────────────────────────
        if atype == "commodity":
            base["Sector"] = "סחורות"
            unit = COMMODITIES.get(symbol, {}).get("unit", "$")
            # המלצת AI לסחורות לפי RSI + מגמה
            if rsi < 35:
                base["Action"]   = "קנייה 🛒"
                base["AI_Logic"] = f"RSI {rsi:.0f} — מכירת יתר. כניסה אפשרית."
            elif rsi > 65:
                base["Action"]   = "מכירה 🔴"
                base["AI_Logic"] = f"RSI {rsi:.0f} — קנייה יתר. שקול מימוש."
            else:
                base["Action"]   = "החזק ⚖️"
                base["AI_Logic"] = f"RSI {rsi:.0f} — ניטרלי."
            return base

        # ── קריפטו ────────────────────────────────────────────────────────
        if atype == "crypto":
            base["Sector"] = "קריפטו"
            vol_30d = float(h["Close"].pct_change().rolling(30).std().iloc[-1] * 100) if len(h) >= 30 else 0
            if rsi < 30:
                base["Action"]   = "קנייה חזקה 💎"
                base["AI_Logic"] = f"RSI {rsi:.0f} — פחד קיצוני. הזדמנות כניסה."
            elif rsi > 70:
                base["Action"]   = "מכירה 🔴"
                base["AI_Logic"] = f"RSI {rsi:.0f} — חמדנות קיצונית. שקול מימוש."
            elif px > ma50:
                base["Action"]   = "קנייה 📈"
                base["AI_Logic"] = "מחיר מעל MA50 — מגמה עולה."
            else:
                base["Action"]   = "החזק ⚖️"
                base["AI_Logic"] = "מחיר מתחת MA50 — המתן לאישור."
            base["Margin"] = round(vol_30d, 1)  # שימוש בשדה Margin לתנודתיות קריפטו
            return base

        # ── מניות ת"א + ארה"ב ─────────────────────────────────────────────
        inf  = s.info
        score, details = evaluate_pdf_metrics(inf)
        fcf    = inf.get("freeCashflow") or 0
        shares = inf.get("sharesOutstanding") or 1
        fv     = (fcf * 15) / shares if shares > 0 else 0
        action, logic = get_ai_logic(px, fv, score, currency)

        target_price  = inf.get("targetMeanPrice", 0)
        target_upside = ((target_price / px) - 1) * 100 if px > 0 and target_price > 0 else 0
        insider_pct   = (inf.get("heldPercentInsiders") or 0) * 100
        sector        = inf.get("sector", "לא ידוע")
        if symbol.endswith(".TA"):
            sector = "שוק ישראלי (TASE)"

        earning_date_str = "לא ידוע"
        days_to_earnings = -1
        try:
            cal = s.calendar
            if isinstance(cal, dict) and "Earnings Date" in cal and len(cal["Earnings Date"]) > 0:
                edate = cal["Earnings Date"][0]
                earning_date_str = edate.strftime("%d/%m/%Y")
                days_to_earnings = (edate.date() - now.date()).days
        except Exception:
            pass

        base.update({
            "Score":        score,
            "Action":       action,
            "AI_Logic":     logic,
            "RevGrowth":    details.get("RevGrowth", 0),
            "EarnGrowth":   details.get("EarnGrowth", 0),
            "Margin":       details.get("Margin", 0),
            "ROE":          details.get("ROE", 0),
            "CashVsDebt":   "✅" if details.get("Cash",0) > details.get("Debt",0) else "❌",
            "ZeroDebt":     "✅" if details.get("Debt",0) == 0 else "❌",
            "DivYield":     (inf.get("dividendYield") or 0) * 100,
            "DivRate":      inf.get("dividendRate") or 0,
            "FiveYrDiv":    inf.get("fiveYearAvgDividendYield") or 0,
            "PayoutRatio":  (inf.get("payoutRatio") or 0) * 100,
            "ExDate":       inf.get("exDividendDate"),
            "FairValue":    fv,
            "TargetUpside": target_upside,
            "InsiderHeld":  insider_pct,
            "Sector":       sector,
            "EarningsDate": earning_date_str,
            "DaysToEarnings": days_to_earnings,
            "Info":         inf,
        })
        return base
    except Exception:
        return None


@st.cache_data(ttl=600)
def fetch_master_data(tickers: list) -> pd.DataFrame:
    """שולף נתוני שוק מלאים. Cache 10 דקות. תומך בכל סוגי הנכסים."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    now  = datetime.datetime.now()
    rows = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(_fetch_single, t, now): t for t in tickers}
        for fut in as_completed(futures):
            result = fut.result()
            if result:
                rows.append(result)
    return pd.DataFrame(rows) if rows else pd.DataFrame()
