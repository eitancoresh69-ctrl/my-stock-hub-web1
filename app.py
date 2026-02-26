# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
import market_ai
import bull_bear
import simulator
import podcasts_ai 
import alerts_ai
import financials_ai 
import crypto_ai      
import news_ai        
import telegram_ai    
import analytics_ai   
import pro_tools_ai 
import premium_agents_ai 
import growth_risk_ai 
import backtest_ai # המודול החדש!

st.set_page_config(page_title="Investment Hub Elite", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<script>setInterval(function(){ window.location.reload(); }, 900000);</script>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f4f6f9; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 14px !important; }
    .ai-card { background: white; padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }
    div[data-testid="stTabs"] button { font-weight: bold; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

# תיקון קלוד #4: הגנה על ה-Top Level הקורס!
try:
    with st.spinner("שואב נתוני עתק מוול סטריט..."):
        df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))
except Exception as e:
    st.error("⚠️ אירעה שגיאה זמנית בחיבור לשרתי הבורסה. מציג נתונים חלקיים.")
    df_all = pd.DataFrame()

st.title("🌐 Investment Hub Elite 2026")
c1, c2, c3 = st.columns(3)
try: vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except: vix = 0.0
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות 'זהב' בסורק ה-PDF", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))

# 17 טאבים במערכת הפרודקשן המלאה
tabs = st.tabs([
    "📌 התיק", "🔍 סורק PDF", "🚀 צמיחה", "💼 רנטגן", "📚 דוחות", "💰 דיבידנדים", "🔔 התראות", 
    "📈 סוכן ערך", "⚡ סוכן יומי", "🤖 סוכני פרימיום", "⏪ בק-טסט", "🎧 פודקאסטים", "🌍 מאקרו", "⚖️ שור/דוב", 
    "₿ קריפטו", "📰 חדשות", "📊 אנליטיקה"
])

# הפעלת כל הטאבים...
with tabs[0]: # התיק
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        edited = st.data_editor(merged[["Symbol", "PriceStr", "BuyPrice", "Qty", "PL", "Yield", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt"]], hide_index=True, use_container_width=True)
        st.session_state.portfolio = edited[["Symbol", "BuyPrice", "Qty"]]

with tabs[1]: # סורק
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(scanner[["Symbol", "PriceStr", "Score", "RevGrowth", "Margin", "RSI", "MA50", "Action"]], hide_index=True, use_container_width=True)

with tabs[2]: growth_risk_ai.render_growth_and_risk(df_all)
with tabs[3]: 
    if 'portfolio' in st.session_state and not df_all.empty: pro_tools_ai.render_pro_tools(df_all, st.session_state.portfolio)
with tabs[4]: financials_ai.render_financial_reports(df_all)
with tabs[5]: 
    if not df_all.empty:
        div_df = df_all[df_all['DivYield'] > 0].copy()
        st.dataframe(div_df.sort_values(by="DivYield", ascending=False)[["Symbol", "DivYield", "DivRate", "PayoutRatio"]], hide_index=True, use_container_width=True)
with tabs[6]: alerts_ai.render_smart_alerts(df_all)
with tabs[7]: simulator.render_value_agent(df_all)
with tabs[8]: simulator.render_day_trade_agent(df_all)
with tabs[9]: premium_agents_ai.render_premium_agents(df_all)
with tabs[10]: backtest_ai.render_backtester(df_all) # הטאב החדש!
with tabs[11]: podcasts_ai.render_podcasts_analysis()
with tabs[12]: market_ai.render_market_intelligence()
with tabs[13]: 
    if not df_all.empty: bull_bear.render_bull_bear(df_all)
with tabs[14]: crypto_ai.render_crypto_arena()
with tabs[15]: news_ai.render_live_news(MY_STOCKS_BASE)
with tabs[16]: analytics_ai.render_analytics_dashboard()
