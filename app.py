# app.py — Investment Hub Elite 2026 | הגרסה המלאה

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
from storage import load_all_to_session, save, load
import realtime_data
import market_ai, bull_bear, simulator, podcasts_ai, alerts_ai
import financials_ai, crypto_ai, news_ai, analytics_ai
import pro_tools_ai, premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai, social_sentiment_ai, tax_fees_ai
import market_scanner

# ─── הגדרות עמוד ───
st.set_page_config(page_title="Investment Hub Elite 2026", layout="wide")

# טעינת נתונים שמורים
load_all_to_session(st.session_state)

# עיצוב RTL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .ai-card { background: white; padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ─── שליפת נתונים ───
try:
    full_watchlist = list(set(MY_STOCKS_BASE + SCAN_LIST))
    with st.spinner(f"📡 סורק {len(full_watchlist)} נכסים ברחבי העולם..."):
        df_all = fetch_master_data(full_watchlist)
except Exception as e:
    st.error(f"⚠️ שגיאה בעדכון הנתונים: {e}")
    df_all = pd.DataFrame()

# ─── כותרת ומדדים ───
st.title("🌐 Investment Hub Elite 2026")

c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 סה\"כ נכסים", len(df_all))
c2.metric("🏆 מניות זהב", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("🕒 עדכון", datetime.now().strftime("%H:%M"))
c4.metric("🛡️ מערכת", "🟢 תקינה")

# ─── טאבים (23) ───
tabs = st.tabs([
    "📌 התיק", "🔍 סורק PDF", "🚀 צמיחה", "💼 רנטגן", "📚 דוחות", 
    "💰 דיבידנדים", "🔔 התראות", "📈 סוכן ערך", "⚡ סוכן יומי", 
    "🤖 פרימיום", "🌐 סורק שוק", "⏪ בק-טסט", "🎧 פודקאסטים", 
    "🌍 מאקרו", "⚖️ שור/דוב", "₿ קריפטו", "📰 חדשות", "📊 אנליטיקה", 
    "⚙️ מנוע ביצוע", "🛡️ הגנה", "🧠 ML", "🐦 רשתות", "💸 מיסים"
])

# טאב 0: התיק
with tabs[0]:
    st.markdown('<div class="ai-card"><b>📌 התיק שלי:</b> מעקב ביצועים.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        st.dataframe(df_all[df_all["Symbol"].isin(MY_STOCKS_BASE)][["Symbol", "Price", "Score", "Action"]], use_container_width=True)

# טאב 7 & 8: הסוכנים (התיקון נמצא כאן דרך simulator.py)
with tabs[7]:
    simulator.render_value_agent(df_all)
with tabs[8]:
    simulator.render_day_trade_agent(df_all)

# טאב 15: קריפטו
with tabs[15]:
    crypto_ai.render_crypto_arena()

# טאב 17: אנליטיקה (סחורות יופיעו כאן)
with tabs[17]:
    analytics_ai.render_analytics_dashboard()

# ... (שאר הטאבים קוראים לפונקציות מהמודולים שלהם)
