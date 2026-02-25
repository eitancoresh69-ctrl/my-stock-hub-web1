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
        if gap > 0.05: return "קנייה חזקה 💎", f"מניית 'זהב'. נסחרת בהנחה משוויה ההוגן ({currency}{fv:,.2f})."
        return "קנייה 📈", "חברה איכותית ביותר במחיר הוגן."
    elif score >= 3:
        if gap > 0.10: return "איסוף 🛒", f"חברה טובה במחיר 'מבצע'."
        return "החזק ⚖️", "המחיר משקף את השווי האמיתי."
    return "מכירה 🔴", "ציון איכות נמוך יחסית לסיכון."

@st.cache_data(ttl=600)
def fetch_master_data(tickers):
    rows = []
    now = datetime.datetime.now()
    
    for t in tickers:
        try:
            s = yf.Ticker(t)
            inf = s.info
            
            h = s.history(period="6mo")
            if h.empty or len(h) < 20: continue 
            
            px = h['Close'].iloc[-1]
            
            # טכני
            delta = h['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1])) if not np.isnan(rs.iloc[-1]) else 50
            ma50 = h['Close'].rolling(window=50).mean().iloc[-1]
            
            score, details = evaluate_pdf_metrics(inf)
            fcf = inf.get('freeCashflow') or 0
            shares = inf.get('sharesOutstanding') or 1
            fv = (fcf * 15) / shares if shares > 0 else 0
            
            currency = "אג'" if str(t).endswith(".TA") else "$"
            price_str = f"{currency}{px:,.2f}"
            action, logic = get_ai_logic(px, fv, score, currency)
            
            # דיבידנדים לעומק
            div_yield = (inf.get('dividendYield') or 0) * 100
            div_rate = inf.get('dividendRate') or 0
            five_yr_div = (inf.get('fiveYearAvgDividendYield') or 0)
            payout_ratio = (inf.get('payoutRatio', 0) or 0) * 100
            
            # משיכת תאריכי דוחות (Earnings) וחישוב מרחק
            earning_date_str = "לא ידוע"
            days_to_earnings = -1
            try:
                cal = s.calendar
                if isinstance(cal, dict) and 'Earnings Date' in cal and len(cal['Earnings Date']) > 0:
                    edate = cal['Earnings Date'][0]
                    # מוודא שזה פורמט תאריך נכון
                    if hasattr(edate, 'date'):
                        earning_date_str = edate.strftime('%d/%m/%Y')
                        # חישוב הימים שנותרו
                        days_to_earnings = (edate.date() - now.date()).days
            except: pass

            rows.append({
                "Symbol": t, "Price": px, "PriceStr": price_str, "Currency": currency,
                "FairValue": fv, "Change": ((px / h['Close'].iloc[-2]) - 1) * 100,
                "Score": score, "RSI": rsi, "MA50": ma50, "Action": action, "AI_Logic": logic,
                "RevGrowth": details.get('RevGrowth', 0), "EarnGrowth": details.get('EarnGrowth', 0),
                "Margin": details.get('Margin', 0), "ROE": details.get('ROE', 0),
                "CashVsDebt": "✅" if details.get('Cash', 0) > details.get('Debt', 0) else "❌",
                "ZeroDebt": "✅" if details.get('Debt', 0) == 0 else "❌",
                "DivYield": div_yield, "DivRate": div_rate, "FiveYrDiv": five_yr_div, 
                "PayoutRatio": payout_ratio, "ExDate": inf.get('exDividendDate'),
                "EarningsDate": earning_date_str, "DaysToEarnings": days_to_earnings,
                "Info": inf
            })
        except: continue
    
    if not rows:
        return pd.DataFrame(columns=["Symbol", "Price", "PriceStr", "Currency", "FairValue", "Change", "Score", "RSI", "MA50", "Action", "AI_Logic", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "DivRate", "FiveYrDiv", "PayoutRatio", "ExDate", "EarningsDate", "DaysToEarnings", "Info"])
    return pd.DataFrame(rows)
