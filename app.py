# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ייבוא המודלים מהקבצים האחרים
from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
import market_ai
import bull_bear
import simulator

st.set_page_config(page_title="Investment Hub Premium", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<script>setInterval(function(){ window.location.reload(); }, 900000);</script>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f0f2f6; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 13px !important; }
    .ai-card { background: linear-gradient(145deg, #ffffff, #e6f0fa); padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))

st.title("🌐 Investment Hub Premium 2026")

c1, c2, c3, c4 = st.columns(4)
try: vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except: vix = 0
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות זהב בסורק", len(df_all[(df_all["Score"] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]) if not df_all.empty else 0)
c3.metric("🔥 המזנקת היומית", df_all.loc[df_all["Change"].idxmax()]["Symbol"] if not df_all.empty else "N/A")
c4.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))

# כל 6 הטאבים שביקשת מופיעים כאן!
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📌 המניות שלי", "🔍 סורק מניות זהב", "💰 דיבידנדים", "🤖 סימולטור מסחר", "🌍 מודיעין מאקרו", "⚖️ ניתוח שור/דוב"])

with tab1:
    st.markdown('<div class="ai-card"><b>ניהול התיק שלי (Mega-Table):</b> כאן מרוכזים כל נתוני ה-PDF יחד עם הרווח/הפסד שלך. ערוך את מחיר הקנייה (BuyPrice) והכמות (Qty) כדי שהמערכת תחשב לך את התשואה. מניות שזוהו כ"זהב" בסורק נוספות לכאן אוטומטית.</div>', unsafe_allow_html=True)
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    edited = st.data_editor(st.session_state.portfolio, num_rows="dynamic")
    if not edited.empty and not df_all.empty:
        merged = pd.merge(edited, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        
        # תצוגת כל העמודות כפי שביקשת
        st.dataframe(
            merged[["Symbol", "Price", "Change", "BuyPrice", "Qty", "PL", "Yield", "Score", "Action", "RevGrowth", "EarnGrowth", "Margins", "ROE", "CashVsDebt", "ZeroDebt", "AI_Logic"]],
            column_config={
                "Price": st.column_config.NumberColumn("מחיר שוק", help=HELP.get("price")),
                "Change": st.column_config.NumberColumn("שינוי %", format="%.2f%%"),
                "BuyPrice": st.column_config.NumberColumn("מחיר קנייה"),
                "Qty": st.column_config.NumberColumn("כמות"),
                "PL": st.column_config.NumberColumn("רווח/הפסד", format="%.2f", help=HELP.get("pl")),
                "Yield": st.column_config.NumberColumn("תשואה %", format="%.1f%%", help=HELP.get("yield")),
                "Score": st.column_config.NumberColumn("⭐ ציון איכות"),
                "Action": st.column_config.TextColumn("פעולה מומלצת"),
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%"),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווח", format="%.1%"),
                "Margins": st.column_config.NumberColumn("שולי רווח", format="%.1%"),
                "ROE": st.column_config.NumberColumn("ROE", format="%.1%"),
                "CashVsDebt": st.column_config.TextColumn("מזומן>חוב"),
                "ZeroDebt": st.column_config.TextColumn("חוב 0"),
                "AI_Logic": st.column_config.TextColumn("תובנות AI", width="large")
            }, use_container_width=True, hide_index=True
        )

with tab2:
    st.markdown('<div class="ai-card"><b>סורק ה-PDF החכם:</b> מערכת AI סורקת מניות מובילות ומדרגת אותן לפי 6 הקריטריונים. רק מניות עם ציון 4 ומעלה מוצגות כאן.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(scanner[["Symbol", "Price", "Score", "RevGrowth", "EarnGrowth", "ROE", "Action", "AI_Logic"]], use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="ai-card"><b>לוח תזרים מזומנים פסיבי (דיבידנדים):</b></div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all['DivYield'] > 0].sort_values(by="DivYield", ascending=False)
        div_df['ExDateClean'] = div_df['ExDate'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y') if x and pd.notnull(x) else "N/A")
        st.dataframe(div_df[["Symbol", "DivYield", "ExDateClean"]], column_config={"DivYield": st.column_config.NumberColumn("תשואה שנתית %", format="%.2f%%"), "ExDateClean": st.column_config.TextColumn("תאריך אקס")}, use_container_width=True, hide_index=True)

with tab4:
    simulator.render_paper_trading(df_all)

with tab5:
    market_ai.render_market_intelligence()

with tab6:
    if not df_all.empty:
        bull_bear.render_bull_bear(df_all)
