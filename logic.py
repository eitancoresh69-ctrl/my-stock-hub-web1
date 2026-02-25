# logic.py
import yfinance as yf
import pandas as pd
import streamlit as st

def evaluate_pdf_metrics(info):
    score = 0
    details = {}
    try:
        rev_growth = info.get('revenueGrowth')
        if rev_growth and rev_growth >= 0.10: score += 1
        details['RevGrowth'] = (rev_growth or 0) * 100 # הכפלה ב-100 לתיקון הפורמט
        
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
    if not fv or fv <= 0: return "בבדיקה 🔍", "חסרים נתוני תזרים לחישוב שווי הוגן."
    gap = (fv - price) / price if price > 0 else 0
    if score >= 5:
        if gap > 0.05: return "קנייה חזקה 💎", f"מניית 'זהב' (ציון {score}). נסחרת בהנחה משוויה ההוגן ({currency}{fv:,.2f})."
        return "קנייה 📈", "חברה איכותית ביותר במחיר הוגן."
    elif score >= 3:
        if gap > 0.10: return "איסוף 🛒", f"חברה טובה במחיר 'מבצע' מתחת לשווי של {currency}{fv:,.2f}."
        return "החזק ⚖️", "החברה יציבה אך המחיר משקף את השווי האמיתי."
    return "מכירה/המתנה 🔴", "ציון איכות נמוך יחסית לסיכון בשוק."

@st.cache_data(ttl=600)
def fetch_master_data(tickers):
    rows = []
    for t in tickers:
        try:
            s = yf.Ticker(t)
            inf = s.info
            px = inf.get('currentPrice') or inf.get('regularMarketPrice')
            if not px:
                h = s.history(period="1d")
                if not h.empty: px = h['Close'].iloc[-1]
                else: px = 0.0
            if px == 0.0: continue 
            
            score, details = evaluate_pdf_metrics(inf)
            fcf = inf.get('freeCashflow') or 0
            shares = inf.get('sharesOutstanding') or 1
            fv = (fcf * 15) / shares if shares > 0 else 0
            
            currency = "אג'" if str(t).endswith(".TA") else "$"
            price_str = f"{currency}{px:,.2f}"
            
            action, logic = get_ai_logic(px, fv, score, currency)
            payout_ratio = (inf.get('payoutRatio', 0) or 0) * 100
            
            rows.append({
                "Symbol": t, "Price": px, "PriceStr": price_str, "Currency": currency,
                "FairValue": fv, "Change": ((px / (inf.get('previousClose') or px)) - 1) * 100,
                "Score": score, "Action": action, "AI_Logic": logic,
                "RevGrowth": details.get('RevGrowth', 0), "EarnGrowth": details.get('EarnGrowth', 0),
                "Margin": details.get('Margin', 0), "ROE": details.get('ROE', 0),
                "CashVsDebt": "✅" if details.get('Cash', 0) > details.get('Debt', 0) else "❌",
                "ZeroDebt": "✅" if details.get('Debt', 0) == 0 else "❌",
                "DivYield": (inf.get('dividendYield') or 0) * 100, "ExDate": inf.get('exDividendDate'), 
                "PayoutRatio": payout_ratio, "Info": inf
            })
        except: continue
    
    if not rows:
        return pd.DataFrame(columns=["Symbol", "Price", "PriceStr", "Currency", "FairValue", "Change", "Score", "Action", "AI_Logic", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "ExDate", "PayoutRatio", "Info"])
    return pd.DataFrame(rows)
