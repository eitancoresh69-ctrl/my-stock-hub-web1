# logic.py
import yfinance as yf
import pandas as pd
import streamlit as st

def evaluate_pdf_metrics(info):
    score = 0
    try:
        if (info.get('revenueGrowth', 0) or 0) >= 0.10: score += 1
        if (info.get('earningsGrowth', 0) or 0) >= 0.10: score += 1
        if (info.get('profitMargins', 0) or 0) >= 0.10: score += 1
        if (info.get('returnOnEquity', 0) or 0) >= 0.15: score += 1
        cash, debt = info.get('totalCash', 0) or 0, info.get('totalDebt', 0) or 0
        if cash > debt: score += 1
        if debt == 0: score += 1
    except: pass
    return score

def get_ai_logic(price, fv, score):
    if not fv or fv == 0: return "בבדיקה 🔍", "חסרים נתונים לחישוב שווי הוגן."
    gap = (fv - price) / price
    if score >= 5:
        if gap > 0.05: return "קנייה חזקה 💎", f"מניית זהב (ציון {score}). הנחה של {abs(gap):.1%} משוויה."
        return "קנייה 📈", "חברה איכותית ביותר במחיר הוגן."
    elif score >= 3:
        if gap > 0.10: return "איסוף 🛒", "חברה טובה במחיר 'מבצע'."
        return "החזק ⚖️", "מחיר משקף שווי אמיתי."
    return "מכירה/המתנה 🔴", "ציון איכות נמוך יחסית לסיכון."

@st.cache_data(ttl=600)
def fetch_master_data(tickers):
    rows = []
    for t in tickers:
        try:
            s = yf.Ticker(t)
            inf = s.info
            h = s.history(period="2d")
            if h.empty: continue
            px = h['Close'].iloc[-1]
            score = evaluate_pdf_metrics(inf)
            
            fcf = inf.get('freeCashflow', 0) or 0
            shares = inf.get('sharesOutstanding', 1) or 1
            fv = (fcf * 15) / shares
            action, logic = get_ai_logic(px, fv, score)
            
            cash = inf.get('totalCash', 0) or 0
            debt = inf.get('totalDebt', 0) or 0
            
            rows.append({
                "Symbol": t, "Price": px, "Change": ((px / h['Close'].iloc[-2]) - 1) * 100,
                "Score": score, "Action": action, "AI_Logic": logic,
                "RevGrowth": (inf.get('revenueGrowth', 0) or 0),
                "EarnGrowth": (inf.get('earningsGrowth', 0) or 0),
                "Margins": (inf.get('profitMargins', 0) or 0),
                "ROE": (inf.get('returnOnEquity', 0) or 0),
                "CashVsDebt": "✅" if cash > debt else "❌",
                "ZeroDebt": "✅" if debt == 0 else "❌",
                "DivYield": inf.get('dividendYield', 0), 
                "ExDate": inf.get('exDividendDate'),
                "Info": inf
            })
        except: continue
        
    if not rows:
        return pd.DataFrame(columns=["Symbol", "Price", "Change", "Score", "Action", "AI_Logic", "RevGrowth", "EarnGrowth", "Margins", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "ExDate", "Info"])
    return pd.DataFrame(rows)
