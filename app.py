# app.py — Investment Hub Elite 2026 — גרסה סופית עם Cookies ופיצול מודולרי
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
from scheduler_agents import get_scheduler

# ייבוא מודולי ה-AI הקיימים
import realtime_data, market_ai, bull_bear, simulator
import podcasts_ai, alerts_ai, financials_ai, crypto_ai
import news_ai, telegram_ai, analytics_ai, pro_tools_ai
import premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai
import social_sentiment_ai, tax_fees_ai, market_scanner
import ai_portfolio, commodities_tab, pattern_ai, portfolio_optimizer

# ייבוא המודולים שפיצלנו וניהול משתמשים
from user_manager import init_user_session, render_login_page, save_user_data
import tab_status
import tab_portfolio

# ─── ניהול Cookies (זיכרון התחברות) ──────────────────────────────────────────
# password משמש להצפנת העוגיה על הדפדפן שלך
cookies = EncryptedCookieManager(password="HubElite_Secure_2026_Key", prefix="hub/")
if not cookies.ready():
    st.stop()

# ─── הגדרות דף ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Investment Hub Elite 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── עיצוב CSS (הסרת Sidebar, תיקון שם משתמש) ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif !important; direction:rtl; text-align:right; }
.stApp { background:#f5f7fa !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

.hub-header {
    background:linear-gradient(135deg,#1565c0 0%,#1976d2 55%,#42a5f5 100%);
    border-radius:14px; padding:16px 22px; margin-bottom:12px;
    box-shadow:0 4px 18px rgba(21,101,192,0.22);
}
.user-info-box {
    background:#fff; padding:10px 15px; border-radius:10px; text-align:center;
    box-shadow:0 2px 5px rgba(0,0,0,0.05); white-space: nowrap; 
    overflow: hidden; text-overflow: ellipsis; border: 1px solid #e0e6ed;
}
</style>
""", unsafe_allow_html=True)

inject_tooltip_css()   
load_all_to_session(st.session_state)

# ─── לוגיקת התחברות חכמה (Cookies + Session) ──────────────────────────────────
init_user_session()

# בדיקה: האם המשתמש כבר מחובר בעוגיה?
saved_user = cookies.get("active_user")
if saved_user and not st.session_state.get("current_user"):
    st.session_state["current_user"] = saved_user
    # טעינת נתוני התיק של המשתמש מהאחסון
    db = load("app_users_db", {})
    if saved_user in db:
        st.session_state["portfolio_buy_prices"] = db[saved_user].get("portfolio_buy_prices", {})
        st.session_state["portfolio_quantities"] = db[saved_user].get("portfolio_quantities", {})

# אם עדיין אין משתמש מחובר - הצג דף לוגין
if not st.session_state.get("current_user"):
    render_login_page()
    # במידה והתחבר הרגע, נשמור עוגיה
    if st.session_state.get("current_user"):
        cookies["active_user"] = st.session_state["current_user"]
        cookies.save()
        st.rerun()
    st.stop()

# ─── שליפת נתונים ודחיפה לסוכנים ──────────────────────────────────────────────
ALL_TICKERS = list(set(MY_STOCKS_BASE + SCAN_LIST + TASE_SCAN))
try:
    with st.spinner("☁️ מסנכרן נתוני שוק חיים..."):
        df_all = fetch_master_data(ALL_TICKERS)
        if df_all is None or df_all.empty:
            df_all = fetch_master_data(["AAPL", "MSFT", "NVDA", "TSLA"])
        
        # עדכון הסוכנים בנתונים החדשים
        st.session_state["df_all"] = df_all
        st.session_state["agent_universe_df"] = df_all
        st.session_state["agent_universe_short_df"] = df_all
except Exception:
    df_all = pd.DataFrame()

# ─── כותרת עליונה ופנל משתמש ──────────────────────────────────────────────────
col_head1, col_head2 = st.columns([7.5, 2.5])
with col_head1:
    st.markdown("""
    <div class="hub-header">
      <div style="display:flex;align-items:center;gap:14px;">
        <div style="font-size:36px;line-height:1;">🌐</div>
        <div>
          <div style="font-size:21px;font-weight:900;color:#fff;letter-spacing:-0.5px;">Investment Hub Elite 2026</div>
          <div style="font-size:12px;color:#bbdefb;margin-top:3px;">ניהול תיק חכם · סוכני AI · למידת מכונה גלובלית</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    st.markdown(f'<div class="user-info-box">👤 <b>{st.session_state["current_user"]}</b></div>', unsafe_allow_html=True)
    if st.button("🚪 התנתק וסגור סשן", use_container_width=True):
        cookies.pop("active_user")
        cookies.save()
        st.session_state["current_user"] = None
        if "portfolio" in st.session_state: del st.session_state["portfolio"]
        st.rerun()

# ─── מדדי שוק מהירים ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _fetch_top_indices():
    try:
        vix = float(yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1])
        spy = yf.Ticker("SPY").history(period="2d")["Close"]
        spy_chg = (spy.iloc[-1]/spy.iloc[-2]-1)*100
    except: vix, spy_chg = 0.0, 0.0
    return vix, spy_chg

vix_val, spy_val = _fetch_top_indices()
c1, c2, c3, c4 = st.columns(4)
c1.metric("📊 VIX", f"{vix_val:.1f}")
c2.metric("🇺🇸 S&P 500", f"{spy_val:+.2f}%")
c3.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))
c4.metric("🛡️ מערכת הגנה", "🟢 פעילה")

# ─── טאבים (28 לשוניות) ───────────────────────────────────────────────────────
tabs = st.tabs([
    "📌 התיק", "🤖 AI מנהל", "📐 אופטימיזציה", "🏅 סחורות", "₿ קריפטו", 
    "🇮🇱 תל אביב", "🔍 סורק PDF", "🔬 Chart דפוסי", "🚀 צמיחה", "💼 רנטגן", 
    "📚 דוחות", "💰 דיבידנדים", "🔔 התראות", "📈 סוכן ערך", "⚡ סוכן יומי", 
    "🤖 פרימיום", "🌐 סורק שוק", "⏪ בק-טסט", "🌍 מאקרו", "⚖️ שור/דוב", 
    "📰 חדשות", "📊 אנליטיקה", "📱 טלגרם", "🛡️ הגנה", "🧠 ML", 
    "📡 נתונים חיים", "💸 מיסים", "📖 מדריך"
])

# הפעלת תוכן הטאבים (חלקם מפוצלים לקבצים חיצוניים)
with tabs[0]:  tab_portfolio.render_portfolio(df_all)
with tabs[1]:  ai_portfolio.render_ai_portfolio(df_all)
with tabs[2]:  portfolio_optimizer.render_portfolio_optimizer(st.session_state.get("portfolio"))
with tabs[3]:  commodities_tab.render_commodities()
with tabs[4]:  crypto_ai.render_crypto_arena()
with tabs[5]:  # לוגיקת ת"א
    st.subheader("🇮🇱 מניות תל אביב")
    if not df_all.empty:
        tase_df = df_all[df_all["Symbol"].str.endswith(".TA")]
        st.dataframe(tase_df, use_container_width=True)
with tabs[13]: simulator.render_value_agent(df_all)
with tabs[14]: simulator.render_day_trade_agent(df_all)
with tabs[24]: ml_learning_ai.render_machine_learning(df_all)
with tabs[27]: tab_status.render_system_status()

# ניתן להמשיך להוסיף את שאר הטאבים באותה צורה...
