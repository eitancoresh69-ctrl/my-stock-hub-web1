import streamlit as st
from storage import UserManager

# ==============================================================================
# מערכת התחברות
# ==============================================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    st.set_page_config(page_title="מרכז השקעות עלית 2026", page_icon="🤖", layout="centered")
    
    st.markdown("<h1 style='text-align: center; color: #1976d2;'>🤖 מרכז השקעות עלית 2026</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔓 התחברות", "📝 הרשמה"])
    
    with tab1:
        st.markdown("### התחבר לחשבונך")
        login_user = st.text_input("שם משתמש", placeholder="הזן שם משתמש")
        login_pass = st.text_input("סיסמה", type="password", placeholder="הזן סיסמה")
        
        if st.button("🔓 התחברות", use_container_width=True):
            if login_user and login_pass:
                success, data = UserManager.login(login_user, login_pass)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.success("✅ התחברת בהצלחה!")
                    st.rerun()
                else:
                    st.error(f"❌ {data}")
    
    with tab2:
        st.markdown("### צור חשבון חדש")
        reg_user = st.text_input("שם משתמש (הרשמה)", placeholder="בחר שם משתמש")
        reg_pass = st.text_input("סיסמה (הרשמה)", type="password", placeholder="צור סיסמה")
        
        if st.button("📝 הרשמה", use_container_width=True):
            if reg_user and reg_pass:
                success, msg = UserManager.register_user(reg_user, reg_pass)
                if success:
                    st.success("✅ נרשמת בהצלחה! תוכל להתחבר כעת.")
                else:
                    st.error(f"❌ {msg}")
    
    st.stop()

# ==============================================================================
# קוד האפליקציה המקורי
# ==============================================================================

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
    page_title="מרכז השקעות עלית 2026",
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

# הוספת פרטי משתמש לסרגל הצד
with st.sidebar:
    st.markdown("### 👤 משתמש")
    st.write(f"**{st.session_state.username}**")
    if st.button("🚪 התנתק"):
        st.session_state.logged_in = False
        st.rerun()

# עיצוב + Tooltips
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

# כותרת עליונה
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
    <div class="hub-header">
    <h2>🌐 מרכז השקעות עלית 2026</h2>
    <p>ברוך שובך, <b>{st.session_state.username}!</b></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="ai-card">
    <h4>⏰ {datetime.now().strftime('%H:%M')}</h4>
    <p>{datetime.now().strftime('%d/%m/%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# כרטיסיות ראשיות
tabs = st.tabs([
    "📊 לוח בקרה", "📈 זמן אמת", "🎯 בינה מלאכותית", "📰 חדשות", "🎙️ פודקאסטים",
    "🔔 התראות", "💰 תיק השקעות", "📉 אנליטיקה", "🇮🇱 בורסת ת\"א", "🇺🇸 מניות ארה\"ב",
    "🪙 קריפטו", "📦 סחורות", "💎 פרימיום", "🚀 כלי פרו", "📊 למידת מכונה",
    "⚡ ביצוע", "🛡️ הגנות", "📋 תיק AI", "💹 טסטים (Backtest)", "🎨 תבניות",
    "📑 דוחות", "⚙️ הגדרות", "🔐 אבטחה", "📞 תמיכה", "ℹ️ אודות",
    "🏆 דירוגים", "💬 קהילה", "📚 חינוך", "🔧 כלים", "✨ מרכז AI"
])

try:
    with tabs[0]:
        st.subheader("📊 לוח בקרה")
        try:
            realtime_data.show_dashboard()
        except:
            st.write("טוען לוח בקרה...")
    
    with tabs[1]:
        st.subheader("📈 נתוני שוק בזמן אמת")
        try:
            realtime_data.show_realtime()
        except:
            st.write("טוען נתוני זמן אמת...")
    
    with tabs[2]:
        st.subheader("🎯 ניתוח שוק - בינה מלאכותית")
        try:
            market_ai.show_market_analysis()
        except:
            st.write("טוען בינה מלאכותית לשוק...")
    
    with tabs[3]:
        st.subheader("📰 חדשות")
        try:
            news_ai.show_news()
        except:
            st.write("טוען חדשות...")
    
    with tabs[4]:
        st.subheader("🎙️ פודקאסטים")
        try:
            podcasts_ai.show_podcasts()
        except:
            st.write("טוען פודקאסטים...")
    
    with tabs[5]:
        st.subheader("🔔 התראות")
        try:
            alerts_ai.show_alerts()
        except:
            st.write("טוען התראות...")
    
    with tabs[6]:
        st.subheader("💰 תיק השקעות")
        try:
            ai_portfolio.show_portfolio()
        except:
            st.write("טוען תיק השקעות...")
    
    with tabs[7]:
        st.subheader("📉 אנליטיקה")
        try:
            analytics_ai.show_analytics()
        except:
            st.write("טוען אנליטיקה...")
    
    with tabs[8]:
        st.subheader("🇮🇱 בורסת תל אביב")
        try:
            market_scanner.show_tase()
        except:
            st.write("טוען נתוני בורסת תל אביב...")
    
    with tabs[9]:
        st.subheader("🇺🇸 מניות ארה\"ב")
        try:
            market_scanner.show_us()
        except:
            st.write("טוען נתוני מניות ארה\"ב...")
    
    with tabs[10]:
        st.subheader("🪙 קריפטו")
        try:
            crypto_ai.show_crypto()
        except:
            st.write("טוען קריפטו...")
    
    with tabs[11]:
        st.subheader("📦 סחורות")
        try:
            commodities_tab.show_commodities()
        except:
            st.write("טוען סחורות...")
    
    with tabs[12]:
        st.subheader("💎 אזור פרימיום")
        try:
            premium_agents_ai.show_premium()
        except:
            st.write("טוען כלי פרימיום...")
    
    with tabs[13]:
        st.subheader("🚀 כלי פרו")
        try:
            pro_tools_ai.show_pro_tools()
        except:
            st.write("טוען כלי פרו...")
    
    with tabs[14]:
        st.subheader("📊 למידת מכונה (ML)")
        try:
            ml_learning_ai.show_ml_learning()
        except:
            st.write("טוען מודלי למידת מכונה...")
    
    with tabs[15]:
        st.subheader("⚡ ביצוע פעולות")
        try:
            execution_ai.show_execution()
        except:
            st.write("טוען מסך ביצוע...")
    
    with tabs[16]:
        st.subheader("🛡️ מנגנוני הגנה")
        try:
            failsafes_ai.show_failsafes()
        except:
            st.write("טוען מנגנוני הגנה...")
    
    with tabs[17]:
        st.subheader("📋 תיק מבוסס בינה מלאכותית")
        try:
            ai_portfolio.show_ai_portfolio()
        except:
            st.write("טוען תיק בינה מלאכותית...")
    
    with tabs[18]:
        st.subheader("💹 בדיקת ביצועי עבר (Backtest)")
        try:
            backtest_ai.show_backtest()
        except:
            st.write("טוען מערכת בדיקת עבר...")
    
    with tabs[19]:
        st.subheader("🎨 תבניות טכניות")
        try:
            pattern_ai.show_patterns()
        except:
            st.write("טוען זיהוי תבניות...")
    
    with tabs[20]:
        st.subheader("📑 דוחות")
        try:
            analytics_ai.show_report()
        except:
            st.write("טוען מערכת דוחות...")
    
    with tabs[21]:
        st.subheader("⚙️ הגדרות")
        st.write("כאן תוכל לנהל את ההגדרות שלך")
    
    with tabs[22]:
        st.subheader("🔐 אבטחה")
        st.write("ניהול הגדרות אבטחה")
    
    with tabs[23]:
        st.subheader("📞 תמיכה")
        st.write("קבלת עזרה ותמיכה טכנית")
    
    with tabs[24]:
        st.subheader("ℹ️ אודות")
        st.write("אודות מרכז השקעות עלית 2026")
    
    with tabs[25]:
        st.subheader("🏆 דירוגים")
        st.write("טבלת מובילים ודירוגי סוחרים")
    
    with tabs[26]:
        st.subheader("💬 קהילה")
        st.write("פיצ'רים של הקהילה ושיתופי פעולה")
    
    with tabs[27]:
        st.subheader("📚 חינוך")
        st.write("תוכן לימודי ומדריכים")
    
    with tabs[28]:
        st.subheader("🔧 כלים")
        st.write("כלים נוספים למסחר")
    
    with tabs[29]:
        st.subheader("✨ מרכז בינה מלאכותית")
        st.write("מרכז הפיצ'רים המבוססים על בינה מלאכותית")

except Exception as e:
    st.error(f"שגיאה בטעינת הכרטיסיות: {e}")

# הפעלת תזמון ברקע
try:
    start_background_scheduler()
except:
    pass
