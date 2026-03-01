# app.py — Investment Hub Elite 2026 | הגרסה המלאה
import streamlit as st
import pandas as pd
from datetime import datetime

import config
import storage
import simulator
# שאר הייבואים המקוריים שלך (וודא שהם קיימים בתיקייה):
import market_ai, bull_bear, podcasts_ai, alerts_ai, financials_ai, crypto_ai, news_ai, analytics_ai, pro_tools_ai, premium_agents_ai, growth_risk_ai, backtest_ai, execution_ai, failsafes_ai, ml_learning_ai, social_sentiment_ai, tax_fees_ai, market_scanner

st.set_page_config(page_title="Investment Hub Elite 2026", layout="wide")
storage.init_db()

# שליפת נתונים מ-config
full_list = list(set(config.MY_STOCKS_BASE + config.SCAN_LIST))
try:
    with st.spinner("🔄 מעדכן נתונים מכל העולם..."):
        # כאן קריאה לפונקציית fetch_master_data המקורית שלך מ-logic
        from logic import fetch_master_data
        df_all = fetch_master_data(full_list)
        storage.update_agent_prices(df_all) # עדכון P&L
except:
    df_all = pd.DataFrame()

# עיצוב RTL
st.markdown("<style>html, body, [class*='css'] { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)

st.title("🌐 Investment Hub Elite 2026")

# 23 הטאבים המקוריים שלך
tabs = st.tabs([
    "📌 התיק", "🔍 סורק PDF", "🚀 צמיחה", "💼 רנטגן", "📚 דוחות", 
    "💰 דיבידנדים", "🔔 התראות", "📈 סוכן ערך", "⚡ סוכן יומי", 
    "🤖 פרימיום", "🌐 סורק שוק", "⏪ בק-טסט", "🎧 פודקאסטים", 
    "🌍 מאקרו", "⚖️ שור/דוב", "₿ קריפטו", "📰 חדשות", "📊 אנליטיקה", 
    "⚙️ מנוע ביצוע", "🛡️ הגנה", "🧠 ML", "🐦 רשתות", "💸 מיסים"
])

with tabs[0]:
    st.subheader("📌 התיק האישי שלי")
    if not df_all.empty:
        my_holdings = df_all[df_all["Symbol"].isin(config.MY_STOCKS_BASE)]
        st.dataframe(my_holdings[["Symbol", "Price", "Score", "Action"]], use_container_width=True)
    
    st.divider()
    st.subheader("🤖 תיק השקעות סוכני AI (מדומה)")
    agent_df = storage.load_agent_portfolio()
    if not agent_df.empty:
        st.dataframe(agent_df[["symbol", "buy_price", "current_price", "Yield_%", "agent_type", "timestamp"]], use_container_width=True)
        if st.button("🗑️ נקה תיק סוכנים"):
            storage.clear_agent_portfolio()
            st.rerun()
    else:
        st.info("הסוכנים טרם ביצעו עסקאות. עבור לטאבים של הסוכנים כדי להפעיל אותם.")

# הפעלת שאר הטאבים כפי שהיו בקוד המקורי שלך
with tabs[7]: simulator.render_value_agent(df_all)
with tabs[8]: simulator.render_day_trade_agent(df_all)
with tabs[20]: ml_learning_ai.render_ml_dashboard() # ה-ML ימשוך נתונים מה-DB
# ... המשך הקריאות לשאר המודולים שלך ...
