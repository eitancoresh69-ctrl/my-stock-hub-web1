# logic.py
import yfinance as yf
import pandas as pd
import numpy as np
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

@st.cache_data(ttl=600)
def fetch_master_data(tickers):
    rows = []
    for t in tickers:
        try:
            s = yf.Ticker(t)
            inf = s.info
            
            # שליפת היסטוריה חצי שנה אחורה לחישובים טכניים
            h = s.history(period="6mo")
            if h.empty or len(h) < 20: continue 
            
            px = h['Close'].iloc[-1]
            
            # חישוב RSI (14 ימים)
            delta = h['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1])) if not np.isnan(rs.iloc[-1]) else 50
            
            # חישוב ממוצע נע 50 ימים (50MA)
            ma50 = h['Close'].rolling(window=50).mean().iloc[-1]
            
            score, details = evaluate_pdf_metrics(inf)
            fcf = inf.get('freeCashflow') or 0
            shares = inf.get('sharesOutstanding') or 1
            fv = (fcf * 15) / shares if shares > 0 else 0
            
            currency = "אג'" if str(t).endswith(".TA") else "$"
            price_str = f"{currency}{px:,.2f}"
            
            payout_ratio = (inf.get('payoutRatio', 0) or 0) * 100
            
            rows.append({
                "Symbol": t, "Price": px, "PriceStr": price_str, "Currency": currency,
                "FairValue": fv, "Change": ((px / h['Close'].iloc[-2]) - 1) * 100,
                "Score": score, 
                "RSI": rsi, "MA50": ma50, # נתונים טכניים חדשים לסוכנים!
                "RevGrowth": details.get('RevGrowth', 0), "EarnGrowth": details.get('EarnGrowth', 0),
                "Margin": details.get('Margin', 0), "ROE": details.get('ROE', 0),
                "CashVsDebt": "✅" if details.get('Cash', 0) > details.get('Debt', 0) else "❌",
                "ZeroDebt": "✅" if details.get('Debt', 0) == 0 else "❌",
                "DivYield": (inf.get('dividendYield') or 0) * 100, "ExDate": inf.get('exDividendDate'), 
                "PayoutRatio": payout_ratio, "Info": inf
            })
        except: continue
    
    if not rows:
        return pd.DataFrame(columns=["Symbol", "Price", "PriceStr", "Currency", "FairValue", "Change", "Score", "RSI", "MA50", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "ExDate", "PayoutRatio", "Info"])
    return pd.DataFrame(rows)
