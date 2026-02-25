# crypto_ai.py
import streamlit as st
import yfinance as yf
import pandas as pd

def render_crypto_arena():
    st.markdown('<div class="ai-card" style="border-right-color: #f7931a;"><b>₿ זירת הקריפטו (Crypto Pro):</b> ניתוח מטבעות מובילים כולל גרף התנהגות חי (Sparkline) של 7 הימים האחרונים.</div>', unsafe_allow_html=True)
    
    crypto_symbols = {"BTC-USD": "ביטקוין (BTC)", "ETH-USD": "אתריום (ETH)", "SOL-USD": "סולאנה (SOL)", "XRP-USD": "ריפל (XRP)"}
    
    with st.spinner("שואב נתוני בלוקצ'יין, מחזורי מסחר וגרפים..."):
        rows = []
        for sym, name in crypto_symbols.items():
            try:
                ticker = yf.Ticker(sym)
                # שואב 7 ימים כדי לייצר את הגרף הקטן בטבלה
                hist = ticker.history(period="7d")
                if not hist.empty and len(hist) >= 2:
                    px = hist['Close'].iloc[-1]
                    prev_px = hist['Close'].iloc[-2]
                    change = ((px / prev_px) - 1) * 100
                    vol = hist['Volume'].iloc[-1] / 1e9 # מיליארדים
                    
                    # רשימת המחירים לטובת ציור הגרף המיניאטורי
                    trend_data = hist['Close'].tolist()
                    
                    if change > 3: action = "מומנטום פריצה 🟢"
                    elif change < -3: action = "תיקון אגרסיבי 🔴"
                    else: action = "דשדוש יציב ⚪"
                    
                    rows.append({
                        "מטבע": name,
                        "מחיר נוכחי ($)": px,
                        "שינוי 24H": change,
                        "נפח מסחר (מיליארדים)": vol,
                        "גרף 7 ימים": trend_data,
                        "סטטוס AI": action
                    })
            except: pass
            
        if rows:
            df_crypto = pd.DataFrame(rows)
            
            # שימוש ביכולות החדשות של Streamlit לציור גרפים בתוך טבלה
            st.dataframe(
                df_crypto, 
                column_config={
                    "מטבע": st.column_config.TextColumn("מטבע", width="medium"),
                    "מחיר נוכחי ($)": st.column_config.NumberColumn("מחיר נוכחי", format="$%.2f"),
                    "שינוי 24H": st.column_config.NumberColumn("שינוי 24 שעות", format="%.2f%%"),
                    "נפח מסחר (מיליארדים)": st.column_config.NumberColumn("נפח מסחר (B)", format="$%.2fB"),
                    "גרף 7 ימים": st.column_config.LineChartColumn("מגמת מחיר (7 ימים) 📈", y_min=0),
                    "סטטוס AI": st.column_config.TextColumn("סטטוס AI")
                }, 
                use_container_width=True, 
                hide_index=True
            )
            
            st.info("💡 **אסטרטגיית קריפטו AI:** שימו לב ל'נפח המסחר'. עליית מחיר עם נפח מסחר נמוך עשויה להיות מלכודת (Fakeout). כניסה לטרייד בקריפטו דורשת נפח שמגבה את התנועה.")
