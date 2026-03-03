# app.py — Investment Hub Elite 2026 — Cloud Ready (Render.com)
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# ייבוא המודולים שפיצלנו
from config import (MY_STOCKS_BASE, SCAN_LIST, TASE_SCAN)
from logic   import fetch_master_data
from storage import load_all_to_session, save, load
from tooltips_he import inject_tooltip_css, tooltip
from user_manager import init_user_session, render_login_page, save_user_data

import tab_status
import tab_portfolio

# ─── ניהול Cookies (מניעת ניתוק ב-Render) ──────────────────────────────────
# הערה: password חייב להיות לפחות 32 תווים
cookies = EncryptedCookieManager(password="HubElite_Secure_Cloud_Key_2026_Long_String", prefix="render_hub/")
if not cookies.ready():
    st.stop()

# ─── הגדרות דף ועיצוב ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Investment Hub Elite 2026 | Cloud",
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

# ─── לוגיקת התחברות (בדיקת עוגיות קודם) ──────────────────────────────────────
init_user_session()

saved_user = cookies.get("active_user")
if saved_user and not st.session_state.get("current_user"):
    st.session_state["current_user"] = saved_user
    # כאן המערכת תמשוך נתונים ממסד הנתונים של Render בעתיד
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

# ─── טעינת נתונים ────────────────────────────────────────────────────────────
ALL_TICKERS = list(set(MY_STOCKS_BASE + SCAN_LIST + TASE_SCAN))
try:
    with st.spinner("☁️ מסנכרן עם נתוני ענן..."):
        df_all = fetch_master_data(ALL_TICKERS)
        st.session_state["df_all"] = df_all
        st.session_state["agent_universe_df"] = df_all
except Exception:
    df_all = pd.DataFrame()

# ─── כותרת ופנל משתמש ────────────────────────────────────────────────────────
col_head1, col_head2 = st.columns([7.5, 2.5])
with col_head1:
    st.markdown("""
    <div class="hub-header">
      <div style="color:white; font-size:24px; font-weight:bold;">🌐 Investment Hub Elite 2026 — Cloud Edition</div>
      <div style="color:#bbdefb; font-size:12px;">המערכת רצה כעת על שרתי Render.com | נתונים מאובטחים</div>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    st.markdown(f'<div class="user-info-box">👤 {st.session_state["current_user"]}</div>', unsafe_allow_html=True)
    if st.button("🚪 התנתק", use_container_width=True):
        cookies.pop("active_user")
        cookies.save()
        st.session_state["current_user"] = None
        st.rerun()

# ─── טאבים ──────────────────────────────────────────────────────────────────
tabs = st.tabs(["📌 התיק", "📈 סוכנים", "🧠 ML", "📖 מדריך"])

with tabs[0]: tab_portfolio.render_portfolio(df_all)
with tabs[1]: tab_status.render_system_status() # כולל את הסוכנים
with tabs[2]: 
    import ml_learning_ai
    ml_learning_ai.render_machine_learning(df_all)
with tabs[3]: 
    st.info("ברוך הבא לגרסת הענן! הנתונים שלך נשמרים כעת במסד נתונים חיצוני ולא על המחשב המקומי.")
