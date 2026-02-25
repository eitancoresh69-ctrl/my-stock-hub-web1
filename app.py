# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ייבוא מהמודולים האחרים
from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
import market_ai
import bull_bear
import simulator

st.set_page_config(page_title="Investment Hub Elite 2026", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<script>setInterval(function(){ window.location.reload(); }, 900000);</script>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f4f6f9; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 14px !important; }
    .ai-card { background: white; padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }
    [data-testid="stMetric"] { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-bottom: 3px solid #1a73e8; }
    </style>
""", unsafe_allow_html=True)

# משיכת הנתונים מהמוח
df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))

st.title("🌐 Investment Hub Elite 2026")
st.markdown("מערכת השקעות ערך ומודיעין AI (מבוססת PDF)")

c1, c2, c3 = st.columns(3)
try: vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except: vix = 0.0
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות 'זהב' בסורק (ציון 5-6)", len(df_all[(df_all["Score"] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]) if not df_all.empty else 0)
c3.metric("🕒 עדכון אחרון (אוטומטי)", datetime.now().strftime("%H:%M"))

# כל 6 הטאבים
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📌 ניהול התיק שלי (מדדי PDF)", "🔍 סורק מניות זהב", "💰 לוח דיבידנדים", "🤖 סוכן AI (Paper Trading)", "🌍 מודיעין מאקרו", "⚖️ ניתוח שור ודוב"])

with tab1:
    st.markdown('<div class="ai-card"><b>ניהול התיק שלי ומדדי ה-PDF:</b> כאן מרוכזים כל 6 הקריטריונים לבחינת חברה מעולה. לחץ על הטבלה כדי להזין מחיר קנייה (BuyPrice) וכמות (Qty).</div>', unsafe_allow_html=True)
    
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    edited = st.data_editor(st.session_state.portfolio, num_rows="dynamic")
    
    if not edited.empty and not df_all.empty:
        merged = pd.merge(edited, df_all, on="Symbol")
        # חישוב רווח והפסד
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        
        # הצגת הטבלה עם כל העמודות המבוקשות
        st.dataframe(
            merged[["Symbol", "Price", "BuyPrice", "Qty", "PL", "Yield", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "Action", "AI_Logic"]],
            column_config={
                "Symbol": "סימול",
                "Price": st.column_config.NumberColumn("מחיר שוק", help=HELP.get("price")),
                "BuyPrice": st.column_config.NumberColumn("מחיר קנייה"),
                "Qty": st.column_config.NumberColumn("כמות"),
                "PL": st.column_config.NumberColumn("רווח/הפסד ($)", format="%.2f", help=HELP.get("pl")),
                "Yield": st.column_config.NumberColumn("תשואה %", format="%.1f%%", help=HELP.get("yield")),
                "Score": st.column_config.NumberColumn("⭐ ציון PDF", help=HELP.get("score")),
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%"),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1%"),
                "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1%"),
                "ROE": st.column_config.NumberColumn("ROE", format="%.1%"),
                "CashVsDebt": st.column_config.TextColumn("מזומן>חוב"),
                "ZeroDebt": st.column_config.TextColumn("חוב 0"),
                "Action": st.column_config.TextColumn("המלצת AI", help=HELP.get("action")),
                "AI_Logic": st.column_config.TextColumn("ניתוח פעולה", width="large")
            }, use_container_width=True, hide_index=True
        )
    else:
        st.info("טוען נתונים מהבורסה, אנא המתן...")

with tab2:
    st.markdown('<div class="ai-card"><b>סורק ה-PDF החכם:</b> מערכת AI סורקת מניות מובילות ומדרגת אותן לפי 6 הקריטריונים מהמדריך. רק מניות עם ציון 4 ומעלה מוצגות כאן.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(
            scanner[["Symbol", "Price", "Score", "RevGrowth", "EarnGrowth", "Margin", "Action"]],
            column_config={
                "Price": "מחיר", "Score": "⭐ ציון איכות", "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%"),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1%"), "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1%"), "Action": "המלצת AI"
            }, use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="ai-card"><b>לוח דיבידנדים (תזרים מזומנים):</b> חברות שמחלקות את הרווחים שלהן.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all['DivYield'] > 0].sort_values(by="DivYield", ascending=False)
        div_df['ExDateClean'] = div_df['ExDate'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y') if pd.notnull(x) else "לא ידוע")
        st.dataframe(div_df[["Symbol", "DivYield", "ExDateClean"]], column_config={"Symbol": "סימול", "DivYield": st.column_config.NumberColumn("תשואה שנתית %", format="%.2f%%"), "ExDateClean": "תאריך קובע (אקס)"}, use_container_width=True, hide_index=True)

with tab4:
    simulator.render_paper_trading(df_all)

with tab5:
    market_ai.render_market_intelligence()

with tab6:
    if not df_all.empty:
        bull_bear.render_bull_bear(df_all)
