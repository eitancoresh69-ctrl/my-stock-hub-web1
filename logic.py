# logic.py
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import streamlit as st

def evaluate_pdf_metrics(info):
    score = 0
    details = {}
    try:
        rev_growth = info.get('revenueGrowth')
        if rev_growth and rev_growth >= 0.10: score += 1
        details['RevGrowth'] = (rev_growth or 0) * 100

        earn_growth = info.get('earningsGrowth')
        if earn_growth and earn_growth >= 0.10: score += 1
        details['EarnGrowth'] = (earn_growth or 0) * 100

        margin = info.get('profitMargins')
        if margin and margin >= 0.10: score += 1
        details['Margin'] = (margin or 0) * 100

        roe = info.get('returnOnEquity')
        if roe and roe >= 0.15: score += 1
        details['ROE'] = (roe or 0) * 100

        cash = info.get('totalCash') or 0
        debt = info.get('totalDebt') or 0
        if cash > debt: score += 1
        if debt == 0: score += 1
        details['Cash'] = cash
        details['Debt'] = debt
    except: pass
    return score, details

def get_ai_logic(price, fv, score, currency):
    if not fv or fv <= 0: return "בבדיקה 🔍", "חסרים נתוני תזרים."
    gap = (fv - price) / price if price > 0 else 0
    if score >= 5:
        if gap > 0.05: return "קנייה חזקה 💎", "מניית 'זהב'. נסחרת בהנחה."
        return "קנייה 📈", "חברה איכותית ביותר במחיר הוגן."
    elif score >= 3:
        if gap > 0.10: return "איסוף 🛒", "חברה טובה במחיר 'מבצע'."
        return "החזק ⚖️", "המחיר משקף את השווי האמיתי."
    return "מכירה 🔴", "ציון איכות נמוך יחסית לסיכון."

def _fetch_single(t, now):
    try:
        s = yf.Ticker(t)

        h = None
        for period in ["6mo", "3mo", "1mo"]:
            try:
                h = s.history(period=period, timeout=15)
                if not h.empty and len(h) >= 5:
                    break
            except:
                continue

        if h is None or h.empty or len(h) < 5:
            return None

        px = float(h['Close'].iloc[-1])
        prev_px = float(h['Close'].iloc[-2]) if len(h) >= 2 else px

        try:
            delta = h['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_val = rs.iloc[-1]
            rsi = float(100 - (100 / (1 + rsi_val))) if not np.isnan(rsi_val) and rsi_val != 0 else 50.0
        except:
            rsi = 50.0

        try:
            ma50 = float(h['Close'].rolling(window=min(50, len(h))).mean().iloc[-1])
        except:
            ma50 = px

        try:
            inf = s.info or {}
        except:
            inf = {}

        score, details = evaluate_pdf_metrics(inf)

        fcf = inf.get('freeCashflow') or 0
        shares = inf.get('sharesOutstanding') or 1
        fv = (fcf * 15) / shares if shares > 0 else 0

        currency = "אג'" if str(t).endswith(".TA") else "$"
        price_str = f"{currency}{px:,.2f}"
        action, logic = get_ai_logic(px, fv, score, currency)

        target_price = inf.get('targetMeanPrice') or 0
        target_upside = ((target_price / px) - 1) * 100 if px > 0 and target_price > 0 else 0
        insider_percent = (inf.get('heldPercentInsiders') or 0) * 100
        sector = inf.get('sector') or ('שוק ישראלי (TASE)' if str(t).endswith(".TA") else 'טכנולוגיה')

        earning_date_str = "לא ידוע"
        days_to_earnings = -1
        try:
            cal = s.calendar
            if isinstance(cal, dict) and 'Earnings Date' in cal and len(cal['Earnings Date']) > 0:
                edate = cal['Earnings Date'][0]
                if hasattr(edate, 'date'):
                    earning_date_str = edate.strftime('%d/%m/%Y')
                    days_to_earnings = (edate.date() - now.date()).days
        except:
            pass

        change = ((px / prev_px) - 1) * 100 if prev_px > 0 else 0.0

        return {
            "Symbol": t, "Price": px, "PriceStr": price_str, "Currency": currency,
            "FairValue": fv, "Change": change,
            "Score": score, "RSI": rsi, "MA50": ma50, "Action": action, "AI_Logic": logic,
            "RevGrowth": details.get('RevGrowth', 0), "EarnGrowth": details.get('EarnGrowth', 0),
            "Margin": details.get('Margin', 0), "ROE": details.get('ROE', 0),
            "CashVsDebt": "✅" if details.get('Cash', 0) > details.get('Debt', 0) else "❌",
            "ZeroDebt": "✅" if details.get('Debt', 0) == 0 else "❌",
            "DivYield": (inf.get('dividendYield') or 0) * 100,
            "DivRate": inf.get('dividendRate') or 0,
            "FiveYrDiv": inf.get('fiveYearAvgDividendYield') or 0,
            "PayoutRatio": (inf.get('payoutRatio') or 0) * 100,
            "ExDate": inf.get('exDividendDate'),
            "TargetUpside": target_upside, "InsiderHeld": insider_percent, "Sector": sector,
            "EarningsDate": earning_date_str, "DaysToEarnings": days_to_earnings,
            "Info": inf
        }
    except:
        return None

EMPTY_COLUMNS = [
    "Symbol", "Price", "PriceStr", "Currency", "FairValue", "Change",
    "Score", "RSI", "MA50", "Action", "AI_Logic",
    "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt",
    "DivYield", "DivRate", "FiveYrDiv", "PayoutRatio", "ExDate",
    "TargetUpside", "InsiderHeld", "Sector", "EarningsDate", "DaysToEarnings", "Info"
]

@st.cache_data(ttl=300)
def fetch_master_data(tickers):
    now = datetime.datetime.now()
    rows = []

    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(_fetch_single, t, now): t for t in tickers}
            for future in concurrent.futures.as_completed(futures, timeout=60):
                try:
                    result = future.result(timeout=20)
                    if result:
                        rows.append(result)
                except:
                    continue
    except:
        for t in tickers:
            result = _fetch_single(t, now)
            if result:
                rows.append(result)

    if not rows:
        return pd.DataFrame(columns=EMPTY_COLUMNS)

    return pd.DataFrame(rows)
