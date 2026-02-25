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
            
            # עמודות ה-PDF הספציפיות שביקשת להחזיר
            cash = inf.get('totalCash', 0) or 0
            debt = inf.get('totalDebt', 0) or 0
            
            rows.append({
                "Symbol": t, "Price": px, "Change": ((px / h['Close'].iloc[-2]) - 1) * 100,
                "Score": score, 
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
        return pd.DataFrame(columns=["Symbol", "Price", "Change", "Score", "RevGrowth", "EarnGrowth", "Margins", "ROE", "CashVsDebt", "ZeroDebt"])
    return pd.DataFrame(rows)
