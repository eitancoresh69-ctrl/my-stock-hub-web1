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
import analytics_ai   
import pro_tools_ai 
import premium_agents_ai 
import growth_risk_ai 
import backtest_ai 

# --- הייבוא של 5 המודולים החדשים שיצרנו הרגע ---
import execution_ai
import failsafes_ai
import ml_learning_ai
import social_sentiment_ai
import tax_fees_ai

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

try:
    with st.spinner("שואב נתוני עתק מוול סטריט..."):
        df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))
except Exception as e:
    st.error("⚠️ אירעה שגיאה זמנית בחיבור לשרתי הבורסה.")
    df_all = pd.DataFrame()

# בדיקת מתג השמדה לפני בניית האתר
if 'kill_switch_active' in st.session_state and st.session_state.kill_switch_active:
    st.error("🚨 המערכת במצב חירום עקב הפעלת מתג השמדה! כל הסוכנים מוקפאים.")

st.title("🌐 Investment Hub Elite 2026")
c1, c2, c3 = st.columns(3)
try: vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except: vix = 0.0
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות 'זהב'", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))

# 21 טאבים שמכסים עכשיו כל יכולת של קרן גידור בעולם
tabs = st.tabs([
    "📌 התיק", "🔍 סורק PDF", "🚀 צמיחה", "💼 רנטגן", "📚 דוחות", "💰 דיבידנדים", "🔔 התראות", 
    "📈 סוכן ערך", "⚡ סוכן יומי", "🤖 סוכני פרימיום", "⏪ בק-טסט", "🎧 פודקאסטים", "⚖️ שור/דוב", 
    "₿ קריפטו", "📰 חדשות", "📊 אנליטיקה", "⚙️ מנוע מסחר", "🛡️ הגנות (Kill Switch)", "🧠 למידת מכונה", "🐦 רשתות חברתיות", "💸 מיסים נטו"
])

with tabs[0]: 
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in list(set(MY_STOCKS_BASE))])
    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        edited = st.data_editor(merged[["Symbol", "PriceStr", "BuyPrice", "Qty", "PL", "Score", "RevGrowth"]], hide_index=True, use_container_width=True)
        st.session_state.portfolio = edited[["Symbol", "BuyPrice", "Qty"]]

with tabs[1]: 
    if not df_all.empty:
        st.dataframe(df_all[(df_all['Score'] >= 4)][["Symbol", "PriceStr", "Score", "RevGrowth", "Action"]], hide_index=True, use_container_width=True)

with tabs[2]: growth_risk_ai.render_growth_and_risk(df_all)
with tabs[3]: 
    if 'portfolio' in st.session_state and not df_all.empty: pro_tools_ai.render_pro_tools(df_all, st.session_state.portfolio)
with tabs[4]: financials_ai.render_financial_reports(df_all)
with tabs[5]: 
    if not df_all.empty: st.dataframe(df_all[df_all['DivYield'] > 0][["Symbol", "DivYield", "DivRate"]], hide_index=True)
with tabs[6]: alerts_ai.render_smart_alerts(df_all)
with tabs[7]: simulator.render_value_agent(df_all)
with tabs[8]: simulator.render_day_trade_agent(df_all)
with tabs[9]: premium_agents_ai.render_premium_agents(df_all)
with tabs[10]: backtest_ai.render_backtester(df_all)
with tabs[11]: podcasts_ai.render_podcasts_analysis()
with tabs[12]: 
    if not df_all.empty: bull_bear.render_bull_bear(df_all)
with tabs[13]: crypto_ai.render_crypto_arena()
with tabs[14]: news_ai.render_live_news(MY_STOCKS_BASE)
with tabs[15]: analytics_ai.render_analytics_dashboard()

# --- חיבור הטאבים החדשים! ---
with tabs[16]: execution_ai.render_execution_engine()
with tabs[17]: failsafes_ai.render_failsafes()
with tabs[18]: ml_learning_ai.render_machine_learning()
with tabs[19]: social_sentiment_ai.render_social_intelligence()
with tabs[20]: tax_fees_ai.render_tax_optimization()
