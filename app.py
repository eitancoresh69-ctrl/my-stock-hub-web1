# app.py — Investment Hub Elite 2026 — Cloud Edition + 28 Tabs Full
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# ייבוא הגדרות ולוגיקה
from config import (MY_STOCKS_BASE, SCAN_LIST, TASE_SCAN)
from logic   import fetch_master_data
from storage import load_all_to_session, save, load
from tooltips_he import inject_tooltip_css, tooltip

# ייבוא מודולי ה-AI הקיימים
import realtime_data, market_ai, bull_bear, simulator
import podcasts_ai, alerts_ai, financials_ai, crypto_ai
import news_ai, telegram_ai, analytics_ai, pro_tools_ai
import premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai
import social_sentiment_ai, tax_fees_ai, market_scanner
import ai_portfolio, commodities_tab, pattern_ai, portfolio_optimizer

# מודולים שפיצלנו ומשתמשים
from user_manager import init_user_session, render_login_page, save_user_data
import tab_status
import tab_portfolio

# ─── ניהול Cookies (מניעת ניתוק ב-Render) ──────────────────────────────────
cookies = EncryptedCookieManager(password="HubElite_Secure_Cloud_Key_2026_Long_String", prefix="render_hub/")
if not cookies.ready():
    st.stop()

# ─── הגדרות דף ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Investment Hub Elite 2026",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif !important; direction:rtl; text-align:right; }
.stApp { background:#f5f7fa !important; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
.hub-header {
    background:linear-gradient(135deg,#1565c0 0%,#1976d2 55%,#42a5f5 100%);
    border-radius:14px; padding:16px 22px; margin-bottom:12px;
}
.user-info-box {
    background:#fff; padding:10px 15px; border-radius:10px; text-align:center;
    box-shadow:0 2px 5px rgba(0,0,0,0.05); color: #1565c0; font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

inject_tooltip_css()
load_all_to_session(st.session_state)

# ─── לוגיקת התחברות עם ענן ו-Cookies ────────────────────────────────────────
init_user_session()

saved_user = cookies.get("active_user")
if saved_user and not st.session_state.get("current_user"):
    st.session_state["current_user"] = saved_user
    db = load("app_users_db", {})
    if saved_user in db:
        st.session_state["portfolio_buy_prices"] = db[saved_user].get("portfolio_buy_prices", {})
        st.session_state["portfolio_quantities"] = db[saved_user].get("portfolio_quantities", {})

if not st.session_state.get("current_user"):
    render_login_page()
    if st.session_state.get("current_user"):
        cookies["active_user"] = st.session_state["current_user"]
        cookies.save()
        st.rerun()
    st.stop()

# ─── משיכת נתונים ────────────────────────────────────────────────────────────
ALL_TICKERS = list(set(MY_STOCKS_BASE + SCAN_LIST + TASE_SCAN))
try:
    with st.spinner("☁️ מסנכרן עם נתוני ענן..."):
        df_all = fetch_master_data(ALL_TICKERS)
        if df_all is None or df_all.empty:
            df_all = fetch_master_data(["AAPL", "MSFT", "NVDA", "TSLA"])
        st.session_state["df_all"] = df_all
        st.session_state["agent_universe_df"] = df_all
        st.session_state["agent_universe_short_df"] = df_all
except Exception:
    df_all = pd.DataFrame()

# ─── כותרת ופנל משתמש ────────────────────────────────────────────────────────
col_head1, col_head2 = st.columns([7.5, 2.5])
with col_head1:
    st.markdown("""
    <div class="hub-header">
      <div style="color:white; font-size:24px; font-weight:bold;">🌐 Investment Hub Elite 2026 — Cloud Edition</div>
      <div style="color:#bbdefb; font-size:12px;">מערכת מבוססת Render.com | מסד נתונים מאובטח | סנכרון גלובלי</div>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    st.markdown(f'<div class="user-info-box">👤 {st.session_state["current_user"]}</div>', unsafe_allow_html=True)
    if st.button("🚪 התנתק", use_container_width=True):
        cookies.pop("active_user")
        cookies.save()
        st.session_state["current_user"] = None
        st.rerun()

# ─── טאבים (כל ה-28) ────────────────────────────────────────────────────────
tabs = st.tabs([
    "📌 התיק", "🤖 AI מנהל", "📐 אופטימיזציה", "🏅 סחורות", "₿ קריפטו", 
    "🇮🇱 תל אביב", "🔍 סורק PDF", "🔬 Chart דפוסי", "🚀 צמיחה", "💼 רנטגן", 
    "📚 דוחות", "💰 דיבידנדים", "🔔 התראות", "📈 סוכן ערך", "⚡ סוכן יומי", 
    "🤖 פרימיום", "🌐 סורק שוק", "⏪ בק-טסט", "🌍 מאקרו", "⚖️ שור/דוב", 
    "📰 חדשות", "📊 אנליטיקה", "📱 טלגרם", "🛡️ הגנה", "🧠 ML", 
    "📡 נתונים חיים", "💸 מיסים", "📖 מדריך"
])

# הפעלת התוכן לכל טאב
with tabs[0]:  tab_portfolio.render_portfolio(df_all)
with tabs[1]:  ai_portfolio.render_ai_portfolio(df_all)
with tabs[2]:  portfolio_optimizer.render_portfolio_optimizer(st.session_state.get("portfolio"))
with tabs[3]:  commodities_tab.render_commodities()
with tabs[4]:  crypto_ai.render_crypto_arena()

# טאב 5 - תל אביב
with tabs[5]:
    st.markdown('<div class="ai-card" style="border-right-color:#0052cc;"><b>🇮🇱 בורסת תל אביב</b></div>', unsafe_allow_html=True)
    if not df_all.empty:
        tase_df = df_all[df_all["Symbol"].str.endswith(".TA")].copy()
        if not tase_df.empty:
            cols_t = [c for c in ["Symbol","PriceStr","Change","Score","RSI","DivYield","Action","AI_Logic"] if c in tase_df.columns]
            st.dataframe(tase_df[cols_t].sort_values("Score", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("הוסף מניות .TA לרשימה ב-config.py")

# טאב 6 - סורק PDF
with tabs[6]:
    st.markdown('<div class="ai-card"><b>🔍 סורק PDF</b> — מניות עם ציון ≥ 4</div>', unsafe_allow_html=True)
    if not df_all.empty:
        scanner = df_all[(df_all["Symbol"].isin(SCAN_LIST+TASE_SCAN)) & (df_all["Score"]>=4)].sort_values("Score",ascending=False)
        if not scanner.empty:
            cols_s = [c for c in ["Symbol","PriceStr","Score","RevGrowth","EarnGrowth","Margin","RSI","Action","AI_Logic"] if c in scanner.columns]
            st.dataframe(scanner[cols_s], use_container_width=True, hide_index=True)
        else:
            st.info("לא נמצאו מניות ציון 4+ כרגע.")

with tabs[7]:  pattern_ai.render_pattern_analysis(df_all)
with tabs[8]:  growth_risk_ai.render_growth_and_risk(df_all)
with tabs[9]:  pro_tools_ai.render_pro_tools(df_all, st.session_state.get("portfolio"))
with tabs[10]: financials_ai.render_financial_reports(df_all)

# טאב 11 - דיבידנדים
with tabs[11]:
    if not df_all.empty:
        div_df = df_all[df_all["DivYield"]>0].copy()
        if not div_df.empty:
            def _div_safe(row):
                if row.get("PayoutRatio", 0) <= 0: return "לא ידוע"
                if row.get("PayoutRatio", 0) > 80: return "⚠️ סכנת קיצוץ"
                if row.get("PayoutRatio", 0) < 60 and row.get("CashVsDebt") == "✅": return "🛡️ בטוח"
                return "✅ יציב"
            div_df["Safety"] = div_df.apply(_div_safe, axis=1)
            cols_d = [c for c in ["Symbol","DivYield","DivRate","FiveYrDiv","PayoutRatio","Safety"] if c in div_df.columns]
            st.dataframe(div_df.sort_values("DivYield",ascending=False)[cols_d], use_container_width=True, hide_index=True)

with tabs[12]: alerts_ai.render_smart_alerts(df_all)
with tabs[13]: simulator.render_value_agent(df_all)
with tabs[14]: simulator.render_day_trade_agent(df_all)
with tabs[15]: premium_agents_ai.render_premium_agents(df_all)
with tabs[16]: market_scanner.render_market_scanner()
with tabs[17]: backtest_ai.render_backtester(df_all)
with tabs[18]: market_ai.render_market_intelligence()
with tabs[19]: bull_bear.render_bull_bear(df_all)
with tabs[20]: news_ai.render_live_news(MY_STOCKS_BASE)
with tabs[21]: analytics_ai.render_analytics_dashboard()
with tabs[22]: telegram_ai.render_telegram_integration()
with tabs[23]: failsafes_ai.render_failsafes()
with tabs[24]: ml_learning_ai.render_machine_learning(df_all)
with tabs[25]: realtime_data.render_full_realtime_panel(list(set(MY_STOCKS_BASE+SCAN_LIST)))
with tabs[26]: tax_fees_ai.render_tax_optimization()

# טאב 27 - מדריך וסטטוס
with tabs[27]: tab_status.render_system_status()
