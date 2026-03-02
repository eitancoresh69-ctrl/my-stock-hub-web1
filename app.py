# app.py — Investment Hub Elite 2026 — Multi-User Version with Authentication
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION SYSTEM - ADD THIS AT THE TOP BEFORE ANYTHING ELSE
# ═══════════════════════════════════════════════════════════════════════════════

from storage import UserManager, load, save

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# LOGIN/REGISTER SCREEN
if not st.session_state.logged_in:
    st.set_page_config(
        page_title="Investment Hub Elite 2026",
        page_icon="🤖",
        layout="centered"
    )
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 50px 0;">
    <h1 style="color: #1976d2; font-size: 48px;">🤖 Investment Hub Elite 2026</h1>
    <p style="color: #666; font-size: 18px;">Multi-User Trading & Investment System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register Tabs
    tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        
        login_user = st.text_input("Username", key="login_username", placeholder="Enter your username")
        login_pass = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        if st.button("🔓 Login", use_container_width=True):
            if login_user and login_pass:
                success, data = UserManager.login(login_user, login_pass)
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.success("✅ Logged in successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {data}")
            else:
                st.warning("⚠️ Please enter username and password")
    
    with tab2:
        st.markdown("### Create New Account")
        
        reg_user = st.text_input("Choose Username", key="reg_username", placeholder="Pick a username")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_password", placeholder="Create a password")
        reg_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm", placeholder="Confirm password")
        
        if st.button("📝 Register", use_container_width=True):
            if not reg_user or not reg_pass:
                st.warning("⚠️ Username and password required")
            elif reg_pass != reg_pass_confirm:
                st.error("❌ Passwords don't match")
            elif len(reg_pass) < 4:
                st.error("❌ Password must be at least 4 characters")
            else:
                success, msg = UserManager.register_user(reg_user, reg_pass)
                
                if success:
                    st.success("✅ Account created! Now login with your credentials.")
                else:
                    st.error(f"❌ {msg}")
    
    st.stop()  # STOP HERE - Don't load rest of app if not logged in

# ═══════════════════════════════════════════════════════════════════════════════
# USER IS LOGGED IN - LOAD THE APP
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Investment Hub Elite 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load all data to session
from storage import load_all_to_session, load_ai_portfolio

load_all_to_session(st.session_state)
try:
    load_ai_portfolio(st.session_state)
except Exception:
    pass

# ═══════════════════════════════════════════════════════════════════════════════
# USER INFO IN SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 👤 User Account")
    st.write(f"**Username:** {st.session_state.username}")
    
    user_data = UserManager.get_user(st.session_state.username)
    st.write(f"**Cash:** ₪{user_data.get('cash', 100000):,.0f}")
    st.write(f"**Plan:** {user_data.get('subscription', 'basic').title()}")
    
    # API Key
    with st.expander("🔑 API Key"):
        api_key = user_data.get('api_key', 'N/A')
        st.code(api_key, language="text")
    
    st.divider()
    
    # Logout Button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP CONTENT - YOUR ORIGINAL CODE GOES HERE
# ═══════════════════════════════════════════════════════════════════════════════

# Import all modules
try:
    from config import (HELP, MY_STOCKS_BASE, SCAN_LIST,
                        COMMODITIES_SYMBOLS, CRYPTO_SYMBOLS, TASE_SCAN)
    from logic import fetch_master_data
    from tooltips_he import inject_tooltip_css, tooltip, render_glossary
    from scheduler_agents import start_background_scheduler, get_scheduler
    
    import realtime_data, market_ai, bull_bear, simulator
    import podcasts_ai, alerts_ai, financials_ai, crypto_ai
    import news_ai, telegram_ai, analytics_ai, pro_tools_ai
    import premium_agents_ai, growth_risk_ai, backtest_ai
    import execution_ai, failsafes_ai, ml_learning_ai
    import social_sentiment_ai, tax_fees_ai, market_scanner
    import ai_portfolio, commodities_tab, pattern_ai, portfolio_optimizer
    
    # CSS and Tooltips
    inject_tooltip_css()
    
    # Header
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
    
    # Welcome Header
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
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # MAIN TABS - YOUR EXISTING TABS GO HERE
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # Create 30+ tabs (as in original)
    tabs = st.tabs([
        "📊 Dashboard", "📈 Real-time", "🎯 Market AI", "📰 News", "🎙️ Podcasts",
        "🔔 Alerts", "💰 Portfolio", "📉 Analytics", "🇮🇱 TASE", "🇺🇸 US Stocks",
        "🪙 Crypto", "📦 Commodities", "💎 Premium", "🚀 Pro Tools", "📊 ML Learning",
        "⚡ Execution", "🛡️ Failsafes", "📋 AI Portfolio", "💹 Backtest", "🎨 Pattern",
        "📑 Report", "⚙️ Settings", "🔐 Security", "📞 Support", "ℹ️ About",
        "🏆 Rankings", "💬 Community", "📚 Education", "🔧 Tools", "✨ AI Hub"
    ])
    
    # Tab 1: Dashboard
    with tabs[0]:
        st.subheader("📊 Dashboard")
        realtime_data.show_dashboard()
    
    # Tab 2: Real-time Data
    with tabs[1]:
        st.subheader("📈 Real-time Market Data")
        realtime_data.show_realtime()
    
    # Tab 3: Market AI
    with tabs[2]:
        st.subheader("🎯 Market AI Predictions")
        market_ai.show_market_analysis()
    
    # Tab 4: News
    with tabs[3]:
        st.subheader("📰 AI-Powered News")
        news_ai.show_news()
    
    # Tab 5: Podcasts
    with tabs[4]:
        st.subheader("🎙️ Investment Podcasts")
        podcasts_ai.show_podcasts()
    
    # Tab 6: Alerts
    with tabs[5]:
        st.subheader("🔔 Smart Alerts")
        alerts_ai.show_alerts()
    
    # Tab 7: Portfolio
    with tabs[6]:
        st.subheader("💰 My Portfolio")
        ai_portfolio.show_portfolio(st.session_state.username)
    
    # Tab 8: Analytics
    with tabs[7]:
        st.subheader("📉 Advanced Analytics")
        analytics_ai.show_analytics()
    
    # Tab 9: TASE
    with tabs[8]:
        st.subheader("🇮🇱 TASE (Israeli Stocks)")
        market_scanner.show_tase_scan()
    
    # Tab 10: US Stocks
    with tabs[9]:
        st.subheader("🇺🇸 US Stocks Tracker")
        market_scanner.show_us_scan()
    
    # Tab 11: Crypto
    with tabs[10]:
        st.subheader("🪙 Cryptocurrency")
        crypto_ai.show_crypto()
    
    # Tab 12: Commodities
    with tabs[11]:
        st.subheader("📦 Commodities Trading")
        commodities_tab.show_commodities()
    
    # Tab 13: Premium
    with tabs[12]:
        st.subheader("💎 Premium Features")
        premium_agents_ai.show_premium()
    
    # Tab 14: Pro Tools
    with tabs[13]:
        st.subheader("🚀 Pro Tools")
        pro_tools_ai.show_pro_tools()
    
    # Tab 15: ML Learning
    with tabs[14]:
        st.subheader("📊 Machine Learning")
        ml_learning_ai.show_ml_learning()
    
    # Tab 16: Execution
    with tabs[15]:
        st.subheader("⚡ Trade Execution")
        execution_ai.show_execution()
    
    # Tab 17: Failsafes
    with tabs[16]:
        st.subheader("🛡️ Risk Failsafes")
        failsafes_ai.show_failsafes()
    
    # Tab 18: AI Portfolio
    with tabs[17]:
        st.subheader("📋 AI Portfolio Manager")
        ai_portfolio.show_ai_portfolio_manager(st.session_state.username)
    
    # Tab 19: Backtest
    with tabs[18]:
        st.subheader("💹 Backtesting Engine")
        backtest_ai.show_backtest()
    
    # Tab 20: Pattern
    with tabs[19]:
        st.subheader("🎨 Chart Patterns")
        pattern_ai.show_patterns()
    
    # Tab 21: Report
    with tabs[20]:
        st.subheader("📑 Performance Report")
        analytics_ai.show_report()
    
    # Tab 22: Settings
    with tabs[21]:
        st.subheader("⚙️ Settings")
        st.write("Configure your preferences here")
    
    # Tab 23: Security
    with tabs[22]:
        st.subheader("🔐 Security Settings")
        st.write("Manage your account security")
    
    # Tab 24: Support
    with tabs[23]:
        st.subheader("📞 Support & Help")
        st.write("Get help and support here")
    
    # Tab 25: About
    with tabs[24]:
        st.subheader("ℹ️ About Investment Hub")
        st.markdown("""
        **Investment Hub Elite 2026** - Multi-User Trading System
        
        ✨ Features:
        - Multi-user authentication
        - AI-powered trading signals
        - Real-time market data
        - Portfolio management
        - Advanced analytics
        - Risk management
        
        Made with ❤️ by AI Trading Team
        """)
    
    # Tab 26: Rankings
    with tabs[25]:
        st.subheader("🏆 Leaderboard")
        st.write("Top traders and portfolios")
    
    # Tab 27: Community
    with tabs[26]:
        st.subheader("💬 Community")
        st.write("Connect with other traders")
    
    # Tab 28: Education
    with tabs[27]:
        st.subheader("📚 Trading Education")
        st.write("Learn trading strategies")
    
    # Tab 29: Tools
    with tabs[28]:
        st.subheader("🔧 Additional Tools")
        st.write("Extra utilities and tools")
    
    # Tab 30: AI Hub
    with tabs[29]:
        st.subheader("✨ AI Hub")
        st.write("AI-powered features")
    
    # Start background scheduler
    start_background_scheduler()
    
except ImportError as e:
    st.error(f"❌ Module import error: {e}")
    st.info("Some modules are missing. Make sure all required files are in the same directory.")
except Exception as e:
    st.error(f"❌ Application error: {e}")
    import traceback
    st.write(traceback.format_exc())
