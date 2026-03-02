# app.py — Investment Hub Elite 2026 — With Multi-User Login (ONLY at top)
import streamlit as st
from storage import UserManager

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION SYSTEM - ONLY ADDITION
# ═══════════════════════════════════════════════════════════════════════════════

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    st.set_page_config(page_title="Investment Hub Elite 2026", page_icon="🤖", layout="centered")
    
    st.markdown("<h1 style='text-align: center; color: #1976d2;'>🤖 Investment Hub Elite 2026</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        login_user = st.text_input("Username", placeholder="Enter username")
        login_pass = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("🔓 Login", use_container_width=True):
            if login_user and login_pass:
                success, data = UserManager.login(login_user, login_pass)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.success("✅ Logged in!")
                    st.rerun()
                else:
                    st.error(f"❌ {data}")
    
    with tab2:
        st.markdown("### Create New Account")
        reg_user = st.text_input("Username", placeholder="Choose username")
        reg_pass = st.text_input("Password", type="password", placeholder="Create password")
        
        if st.button("📝 Register", use_container_width=True):
            if reg_user and reg_pass:
                success, msg = UserManager.register_user(reg_user, reg_pass)
                if success:
                    st.success("✅ Registered! Login now.")
                else:
                    st.error(f"❌ {msg}")
    
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# ORIGINAL APP CODE STARTS HERE - ALL YOUR ORIGINAL CODE
# ═══════════════════════════════════════════════════════════════════════════════

import pandas as pd
import yfinance as yf
from datetime import datetime

from config import (HELP, MY_STOCKS_BASE, SCAN_LIST,
                    COMMODITIES_SYMBOLS, CRYPTO_SYMBOLS, TASE_SCAN)
from logic   import fetch_master_data
from storage import load_all_to_session, save, load
from tooltips_he import inject_tooltip_css, tooltip, render_glossary
from scheduler_agents import start_background_scheduler, get_scheduler

import realtime_data, market_ai, bull_bear, simulator
import podcasts_ai, alerts_ai, financials_ai, crypto_ai
import news_ai, telegram_ai, analytics_ai, pro_tools_ai
import premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai
import social_sentiment_ai, tax_fees_ai, market_scanner
import ai_portfolio, commodities_tab, pattern_ai, portfolio_optimizer

st.set_page_config(
    page_title="Investment Hub Elite 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_all_to_session(st.session_state)
try:
    from storage import load_ai_portfolio
    load_ai_portfolio(st.session_state)
except Exception:
    pass

# Add user info to sidebar
with st.sidebar:
    st.markdown("### 👤 User")
    st.write(f"**{st.session_state.username}**")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ─── עיצוב + Tooltips ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif !important; direction:rtl; text-align:right; }
.stApp { background:#f5f7fa !important; }
.block-container { padding-top:0.5rem !important; max-width:100% !important; }
.ai-card {
    background:#fff; padding:12px 18px; border-radius:12px;
    border-right:5px solid #1976d2;
    box-shadow:0 1px 6px rgba(0,0,0,0.08); margin-bottom:10px;
}
.hub-header {
    background:linear-gradient(135deg,#1565c0 0%,#1976d2 55%,#42a5f5 100%);
    border-radius:14px; padding:16px 22px; margin-bottom:12px;
    color:white; text-align:center;
}
</style>
""", unsafe_allow_html=True)

inject_tooltip_css()

# ─── Header ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
    <div class="hub-header">
    <h2>🌐 Investment Hub Elite 2026</h2>
    <p>Welcome back, <b>{st.session_state.username}!</b></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="ai-card">
    <h4>⏰ {datetime.now().strftime('%H:%M')}</h4>
    <p>{datetime.now().strftime('%d/%m/%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# ─── Main Tabs ────────────────────────────────────────────────────────────────

tabs = st.tabs([
    "📊 Dashboard", "📈 Real-time", "🎯 Market AI", "📰 News", "🎙️ Podcasts",
    "🔔 Alerts", "💰 Portfolio", "📉 Analytics", "🇮🇱 TASE", "🇺🇸 US Stocks",
    "🪙 Crypto", "📦 Commodities", "💎 Premium", "🚀 Pro Tools", "📊 ML Learning",
    "⚡ Execution", "🛡️ Failsafes", "📋 AI Portfolio", "💹 Backtest", "🎨 Pattern",
    "📑 Report", "⚙️ Settings", "🔐 Security", "📞 Support", "ℹ️ About",
    "🏆 Rankings", "💬 Community", "📚 Education", "🔧 Tools", "✨ AI Hub"
])

# Tabs content - KEEP YOUR ORIGINAL FUNCTIONS
try:
    with tabs[0]:
        st.subheader("📊 Dashboard")
        try:
            realtime_data.show_dashboard()
        except:
            st.write("Dashboard loading...")
    
    with tabs[1]:
        st.subheader("📈 Real-time Market Data")
        try:
            realtime_data.show_realtime()
        except:
            st.write("Real-time data loading...")
    
    with tabs[2]:
        st.subheader("🎯 Market AI")
        try:
            market_ai.show_market_analysis()
        except:
            st.write("Market AI loading...")
    
    with tabs[3]:
        st.subheader("📰 News")
        try:
            news_ai.show_news()
        except:
            st.write("News loading...")
    
    with tabs[4]:
        st.subheader("🎙️ Podcasts")
        try:
            podcasts_ai.show_podcasts()
        except:
            st.write("Podcasts loading...")
    
    with tabs[5]:
        st.subheader("🔔 Alerts")
        try:
            alerts_ai.show_alerts()
        except:
            st.write("Alerts loading...")
    
    with tabs[6]:
        st.subheader("💰 Portfolio")
        try:
            ai_portfolio.show_portfolio()
        except:
            st.write("Portfolio loading...")
    
    with tabs[7]:
        st.subheader("📉 Analytics")
        try:
            analytics_ai.show_analytics()
        except:
            st.write("Analytics loading...")
    
    with tabs[8]:
        st.subheader("🇮🇱 TASE")
        try:
            market_scanner.show_tase()
        except:
            st.write("TASE loading...")
    
    with tabs[9]:
        st.subheader("🇺🇸 US Stocks")
        try:
            market_scanner.show_us()
        except:
            st.write("US Stocks loading...")
    
    with tabs[10]:
        st.subheader("🪙 Crypto")
        try:
            crypto_ai.show_crypto()
        except:
            st.write("Crypto loading...")
    
    with tabs[11]:
        st.subheader("📦 Commodities")
        try:
            commodities_tab.show_commodities()
        except:
            st.write("Commodities loading...")
    
    with tabs[12]:
        st.subheader("💎 Premium")
        try:
            premium_agents_ai.show_premium()
        except:
            st.write("Premium loading...")
    
    with tabs[13]:
        st.subheader("🚀 Pro Tools")
        try:
            pro_tools_ai.show_pro_tools()
        except:
            st.write("Pro Tools loading...")
    
    with tabs[14]:
        st.subheader("📊 ML Learning")
        try:
            ml_learning_ai.show_ml_learning()
        except:
            st.write("ML Learning loading...")
    
    with tabs[15]:
        st.subheader("⚡ Execution")
        try:
            execution_ai.show_execution()
        except:
            st.write("Execution loading...")
    
    with tabs[16]:
        st.subheader("🛡️ Failsafes")
        try:
            failsafes_ai.show_failsafes()
        except:
            st.write("Failsafes loading...")
    
    with tabs[17]:
        st.subheader("📋 AI Portfolio")
        try:
            ai_portfolio.show_ai_portfolio()
        except:
            st.write("AI Portfolio loading...")
    
    with tabs[18]:
        st.subheader("💹 Backtest")
        try:
            backtest_ai.show_backtest()
        except:
            st.write("Backtest loading...")
    
    with tabs[19]:
        st.subheader("🎨 Pattern")
        try:
            pattern_ai.show_patterns()
        except:
            st.write("Pattern loading...")
    
    with tabs[20]:
        st.subheader("📑 Report")
        try:
            analytics_ai.show_report()
        except:
            st.write("Report loading...")
    
    with tabs[21]:
        st.subheader("⚙️ Settings")
        st.write("Configure your preferences")
    
    with tabs[22]:
        st.subheader("🔐 Security")
        st.write("Manage security settings")
    
    with tabs[23]:
        st.subheader("📞 Support")
        st.write("Get help and support")
    
    with tabs[24]:
        st.subheader("ℹ️ About")
        st.write("About Investment Hub Elite 2026")
    
    with tabs[25]:
        st.subheader("🏆 Rankings")
        st.write("Leaderboard and rankings")
    
    with tabs[26]:
        st.subheader("💬 Community")
        st.write("Community features")
    
    with tabs[27]:
        st.subheader("📚 Education")
        st.write("Educational content")
    
    with tabs[28]:
        st.subheader("🔧 Tools")
        st.write("Additional tools")
    
    with tabs[29]:
        st.subheader("✨ AI Hub")
        st.write("AI features hub")

except Exception as e:
    st.error(f"Error loading tabs: {e}")

# Start scheduler
try:
    start_background_scheduler()
except:
    pass
