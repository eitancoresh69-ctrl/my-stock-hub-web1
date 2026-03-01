# logic.py — לוגיקה מרכזית: שליפת נתונים וניתוח AI
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import streamlit as st


def evaluate_pdf_metrics(info: dict) -> tuple:
    """מחשב ציון איכות 0-6 לפי 6 קריטריוני המדריך."""
    score = 0
    details = {}
    try:
        rev_growth = info.get("revenueGrowth")
        if rev_growth and rev_growth >= 0.10:
            score += 1
        details["RevGrowth"] = (rev_growth or 0) * 100

        earn_growth = info.get("earningsGrowth")
        if earn_growth and earn_growth >= 0.10:
            score += 1
        details["EarnGrowth"] = (earn_growth or 0) * 100

        margin = info.get("profitMargins")
        if margin and margin >= 0.10:
            score += 1
        details["Margin"] = (margin or 0) * 100

        roe = info.get("returnOnEquity")
        if roe and roe >= 0.15:
            score += 1
        details["ROE"] = (roe or 0) * 100

        cash = info.get("totalCash") or 0
        debt = info.get("totalDebt") or 0
        if cash > debt:
            score += 1
        if debt == 0:
            score += 1
        details["Cash"] = cash
        details["Debt"] = debt
    except Exception:
        pass
    return score, details


def get_ai_logic(price: float, fv: float, score: int, currency: str) -> tuple:
    """מחזיר המלצה ולוגיקת AI."""
    if not fv or fv <= 0:
        return "בבדיקה 🔍", "חסרים נתוני תזרים מזומנים."
    gap = (fv - price) / price if price > 0 else 0
    if score >= 5:
        if gap > 0.05:
            return "קנייה חזקה 💎", "מניית 'זהב'. נסחרת בהנחה מתחת לשווי ההוגן."
        return "קנייה 📈", "חברה איכותית ביותר במחיר הוגן."
    elif score >= 3:
        if gap > 0.10:
            return "איסוף 🛒", "חברה טובה במחיר 'מבצע'."
        return "החזק ⚖️", "המחיר משקף את השווי האמיתי."
    return "מכירה 🔴", "ציון איכות נמוך יחסית לסיכון."


@st.cache_data(ttl=600)
def fetch_master_data(tickers: list) -> pd.DataFrame:
    """שולף נתוני שוק מלאים. Cache 10 דקות."""
    rows = []
    now = datetime.datetime.now()

    for t in tickers:
        try:
            s = yf.Ticker(t)
            inf = s.info
            h = s.history(period="3mo")
            if h.empty or len(h) < 20:
                continue

            px = h["Close"].iloc[-1]

            # RSI
            delta = h["Close"].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean().replace(0, 1e-10)
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1])) if not np.isnan(rs.iloc[-1]) else 50

            ma50 = h["Close"].rolling(50).mean().iloc[-1]

            score, details = evaluate_pdf_metrics(inf)
            fcf = inf.get("freeCashflow") or 0
            shares = inf.get("sharesOutstanding") or 1
            fv = (fcf * 15) / shares if shares > 0 else 0

            currency = "אג'" if str(t).endswith(".TA") else "$"
            price_str = f"{currency}{px:,.2f}"
            action, logic = get_ai_logic(px, fv, score, currency)

            target_price = inf.get("targetMeanPrice", 0)
            target_upside = ((target_price / px) - 1) * 100 if px > 0 and target_price > 0 else 0
            insider_pct = (inf.get("heldPercentInsiders") or 0) * 100
            sector = inf.get("sector", "לא ידוע")
            if str(t).endswith(".TA"):
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

            prev_close = h["Close"].iloc[-2] if len(h) >= 2 else px
            change = ((px / prev_close) - 1) * 100

            rows.append({
                "Symbol": t,
                "Price": px,
                "PriceStr": price_str,
                "Currency": currency,
                "FairValue": fv,
                "Change": change,
                "Score": score,
                "RSI": rsi,
                "MA50": ma50,
                "Action": action,
                "AI_Logic": logic,
                "RevGrowth": details.get("RevGrowth", 0),
                "EarnGrowth": details.get("EarnGrowth", 0),
                "Margin": details.get("Margin", 0),
                "ROE": details.get("ROE", 0),
                "CashVsDebt": "✅" if details.get("Cash", 0) > details.get("Debt", 0) else "❌",
                "ZeroDebt": "✅" if details.get("Debt", 0) == 0 else "❌",
                "DivYield": (inf.get("dividendYield") or 0) * 100,
                "DivRate": inf.get("dividendRate") or 0,
                "FiveYrDiv": inf.get("fiveYearAvgDividendYield") or 0,
                "PayoutRatio": (inf.get("payoutRatio") or 0) * 100,
                "ExDate": inf.get("exDividendDate"),
                "TargetUpside": target_upside,
                "InsiderHeld": insider_pct,
                "Sector": sector,
                "EarningsDate": earning_date_str,
                "DaysToEarnings": days_to_earnings,
                "Info": inf,
            })
        except Exception:
            continue

    return pd.DataFrame(rows)
