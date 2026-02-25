# crypto_ai.py
import streamlit as st
import yfinance as yf
import pandas as pd

def render_crypto_arena():
    st.markdown('<div class="ai-card" style="border-right-color: #f7931a;"><b>₿ זירת הקריפטו (Crypto Arena):</b> מעקב חי אחרי המטבעות הדיגיטליים המובילים וניתוח מומנטום של סוכן ה-AI. קריפטו נסחר 24/7 ולכן הנתונים זזים כל הזמן.</div>', unsafe_allow_html=True)
    
    crypto_symbols = {"BTC-USD": "ביטקוין", "ETH-USD": "אתריום", "SOL-USD": "סולאנה"}
    
    with st.spinner("שואב נתוני בלוקצ'יין בזמן אמת..."):
        rows = []
        for sym, name in crypto_symbols.items():
            try:
                ticker = yf.Ticker(sym)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    px = hist['Close'].iloc[-1]
                    prev_px = hist['Close'].iloc[-2]
                    change = ((px / prev_px) - 1) * 100
                    
                    # המלצת מומנטום פשוטה לקריפטו
                    if change > 3: action, icon = "מומנטום חזק 🚀", "🟢"
                    elif change < -3: action, icon = "מכירת יתר (פאניקה) 🩸", "🔴"
                    else: action, icon = "דשדוש (המתנה) ⚖️", "⚪"
                    
                    rows.append({
                        "מטבע": name,
                        "סימול": sym,
                        "מחיר ($)": px,
                        "שינוי 24H (%)": change,
                        "מומנטום AI": f"{icon} {action}"
                    })
            except: pass
            
        if rows:
            df_crypto = pd.DataFrame(rows)
            st.dataframe(df_crypto, 
                         column_config={
                             "מחיר ($)": st.column_config.NumberColumn("מחיר ($)", format="$%.2f"),
                             "שינוי 24H (%)": st.column_config.NumberColumn("שינוי 24H (%)", format="%.2f%%")
                         }, use_container_width=True, hide_index=True)
            
            st.info("💡 **טיפ מסוכן הקריפטו:** השוק הדיגיטלי תנודתי פי 10 משוק המניות. לעולם אל תשקיע בקריפטו כסף שאתה צריך לטווח הקצר. אסטרטגיית 'החזק וקנה בירידות' (HODL) הוכיחה את עצמה כמשתלמת ביותר עד כה במטבעות הגדולים.")
