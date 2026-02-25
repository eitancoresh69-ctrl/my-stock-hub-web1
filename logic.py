# logic.py
import yfinance as yf
import pandas as pd
import streamlit as st

def evaluate_pdf_metrics(info):
    """
    חישוב 6 הקריטריונים בדיוק לפי ה-PDF של אלון הזה.
    """
    score = 0
    details = {}
    
    try:
        # 1. צמיחת מכירות מעל 10%
        rev_growth = info.get('revenueGrowth')
        if rev_growth is not None and rev_growth >= 0.10: score += 1
        details['RevGrowth'] = rev_growth if rev_growth else 0
        
        # 2. צמיחת רווחים מעל 10%
        earn_growth = info.get('earningsGrowth')
        if earn_growth is not None and earn_growth >= 0.10: score += 1
        details['EarnGrowth'] = earn_growth if earn_growth else 0
        
        # 3. שולי רווח נקי מעל 10%
        margin = info.get('profitMargins')
        if margin is not None and margin >= 0.10: score += 1
        details['Margin'] = margin if margin else 0
        
        # 4+5. ROIC ורווחיות (נשתמש ב-ROE כאינדיקציה לאיכות הנהלה > 15%)
        roe = info.get('returnOnEquity')
        if roe is not None and roe >= 0.15: score += 1
        details['ROE'] = roe if roe else 0
        
        # 6. מזומן מול חוב
        cash = info.get('totalCash', 0) or 0
        debt = info.get('totalDebt', 0) or 0
        if cash > debt: score += 1
        if debt == 0: score += 1
        details['Cash'] = cash
        details['Debt'] = debt
        
    except Exception as e:
        pass
        
    return score, details

def get_ai_logic(price, fv, score):
    if not fv or fv <= 0: return "בבדיקה 🔍", "חסרים נתוני תזרים לחישוב מדויק."
    gap = (fv - price) / price if price > 0 else 0
    if score >= 5:
        if gap > 0.05: return "קנייה חזקה 💎", f"מניית 'זהב' (ציון {score}). נסחרת בהנחה משוויה."
        return "קנייה 📈", "חברה איכותית ביותר במחיר הוגן."
    elif score >= 3:
        if gap > 0.10: return "איסוף 🛒", "חברה טובה שנסחרת במחיר 'מבצע'."
        return "החזק ⚖️", "החברה יציבה אך המחיר משקף את השווי האמיתי."
    return "מכירה/המתנה 🔴", "ציון איכות נמוך יחסית."

@st.cache_data(ttl=600)
def fetch_master_data(tickers):
    rows = []
    for t in tickers:
        try:
            s = yf.Ticker(t)
            inf = s.info
            
            # שליפת מחיר בטוחה יותר נגד קריסות של יאהו
            px = inf.get('currentPrice') or inf.get('regularMarketPrice')
            if not px:
                h = s.history(period="1d")
                if not h.empty: px = h['Close'].iloc[-1]
                else: px = 0.0
                
            if px == 0.0: continue # מדלג רק אם באמת אין מחיר בכלל
            
            # חישוב ה-PDF
            score, details = evaluate_pdf_metrics(inf)
            
            # שווי הוגן בסיסי (DCF)
            fcf = inf.get('freeCashflow', 0) or 0
            shares = inf.get('sharesOutstanding', 1) or 1
            fv = (fcf * 15) / shares if shares > 0 else 0
            
            action, logic = get_ai_logic(px, fv, score)
            
            rows.append({
                "Symbol": t, 
                "Price": px,
                "Score": score, 
                "Action": action, 
                "AI_Logic": logic,
                "RevGrowth": details.get('RevGrowth', 0),
                "EarnGrowth": details.get('EarnGrowth', 0),
                "Margin": details.get('Margin', 0),
                "ROE": details.get('ROE', 0),
                "CashVsDebt": "✅ כן" if details.get('Cash', 0) > details.get('Debt', 0) else "❌ לא",
                "ZeroDebt": "✅ כן" if details.get('Debt', 0) == 0 else "❌ לא",
                "DivYield": inf.get('dividendYield', 0) or 0, 
                "ExDate": inf.get('exDividendDate'),
                "Info": inf
            })
        except Exception as e:
            # אם יש שגיאה במניה ספציפית, נדלג עליה ולא נקריס את האתר
            continue
            
    # מחזיר טבלה מלאה, או מבנה ריק תקין אם אין נתונים בכלל
    if not rows:
        return pd.DataFrame(columns=["Symbol", "Price", "Score", "Action", "AI_Logic", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "DivYield", "ExDate", "Info"])
    return pd.DataFrame(rows)
