# app.py — Investment Hub Elite 2026 — עיצוב חדש מודרני
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# PERSISTENT SESSION
# ═══════════════════════════════════════════════════════════════

from storage import SessionManager, UserManager

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# בדוק אם יש session שמור
if not st.session_state.logged_in:
    stored_username = SessionManager.get_stored_username()
    if stored_username:
        st.session_state.logged_in = True
        st.session_state.username = stored_username

# מסך Login אם לא מחובר
if not st.session_state.logged_in:
    # CSS עיצוב מודרני
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Heebo', sans-serif; }
    
    body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
    
    .login-container {
        max-width: 500px;
        margin: auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin-top: 60px;
    }
    
    .logo-section {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .logo-section h1 {
        font-size: 36px;
        color: #667eea;
        margin: 0;
        font-weight: 800;
    }
    
    .logo-section p {
        color: #999;
        font-size: 14px;
        margin-top: 8px;
    }
    
    .tab-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 30px;
    }
    
    .tab-btn {
        flex: 1;
        padding: 10px;
        border: 2px solid #ddd;
        background: white;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 600;
        color: #999;
        transition: all 0.3s;
    }
    
    .tab-btn.active {
        border-color: #667eea;
        background: #f0f4ff;
        color: #667eea;
    }
    
    .input-group {
        margin-bottom: 16px;
    }
    
    .input-group label {
        display: block;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    .input-group input {
        width: 100%;
        padding: 12px;
        border: 2px solid #eee;
        border-radius: 10px;
        font-size: 14px;
        transition: all 0.3s;
    }
    
    .input-group input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .submit-btn {
        width: 100%;
        padding: 14px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s;
        margin-top: 20px;
    }
    
    .submit-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    .link-text {
        text-align: center;
        margin-top: 20px;
        color: #999;
        font-size: 14px;
    }
    
    .link-text a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # בחירת הכרטיסייה
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔓 התחברות", use_container_width=True, key="tab_login"):
            st.session_state.auth_mode = "login"
    
    with col2:
        if st.button("📝 הרשם", use_container_width=True, key="tab_register"):
            st.session_state.auth_mode = "register"
    
    with col3:
        if st.button("🔑 שחזור", use_container_width=True, key="tab_recover"):
            st.session_state.auth_mode = "recover"
    
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    
    st.divider()
    
    # ══════════════════════════════════════════════════════════
    # TAB 1: התחברות
    # ══════════════════════════════════════════════════════════
    
    if st.session_state.auth_mode == "login":
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #667eea; font-size: 32px; margin: 0;">🤖 Investment Hub</h1>
        <p style="color: #999; font-size: 14px; margin-top: 8px;">מערכת השקעות מתקדמת</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### התחברות לחשבון")
            
            login_user = st.text_input(
                "שם משתמש",
                placeholder="הכנס את שם המשתמש שלך",
                key="login_user"
            )
            
            login_pass = st.text_input(
                "סיסמא",
                type="password",
                placeholder="הכנס את הסיסמא שלך",
                key="login_pass"
            )
            
            submitted = st.form_submit_button(
                "🔓 התחבר",
                use_container_width=True
            )
            
            if submitted:
                if login_user and login_pass:
                    success, data = UserManager.login(login_user, login_pass)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        st.success("✅ התחברת בהצלחה!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {data}")
                else:
                    st.warning("⚠️ הכנס שם משתמש וסיסמא")
    
    # ══════════════════════════════════════════════════════════
    # TAB 2: הרשם
    # ══════════════════════════════════════════════════════════
    
    elif st.session_state.auth_mode == "register":
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #667eea; font-size: 32px; margin: 0;">🎉 הרשם עכשיו</h1>
        <p style="color: #999; font-size: 14px; margin-top: 8px;">בחינם לחלוטין</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("register_form"):
            st.markdown("### יצירת חשבון חדש")
            
            reg_user = st.text_input(
                "שם משתמש",
                placeholder="בחר שם משתמש ייחודי",
                key="reg_user"
            )
            
            reg_pass = st.text_input(
                "סיסמא",
                type="password",
                placeholder="בחר סיסמא חזקה",
                key="reg_pass"
            )
            
            reg_pass_conf = st.text_input(
                "אישור סיסמא",
                type="password",
                placeholder="אשר את הסיסמא",
                key="reg_pass_conf"
            )
            
            # שאלת ביטחון
            security_questions = [
                "בחר שאלת ביטחון",
                "מה שם חיית המחמד שלך?",
                "מה שם העיר שבה נולדת?",
                "מה שם בית הספר הראשון שלך?",
                "מה המשחק המועדף עליך?"
            ]
            
            security_q = st.selectbox(
                "בחר שאלת ביטחון (לשחזור סיסמא)",
                security_questions,
                key="security_q"
            )
            
            security_a = st.text_input(
                "תשובה לשאלת הביטחון",
                placeholder="הכנס את התשובה שלך",
                key="security_a"
            )
            
            submitted = st.form_submit_button(
                "📝 הרשם",
                use_container_width=True
            )
            
            if submitted:
                if not reg_user or not reg_pass:
                    st.warning("⚠️ הכנס שם משתמש וסיסמא")
                elif reg_pass != reg_pass_conf:
                    st.error("❌ הסיסמאות לא תואמות")
                elif security_q == "בחר שאלת ביטחון":
                    st.error("❌ בחר שאלת ביטחון")
                elif not security_a:
                    st.error("❌ הכנס תשובה לשאלת הביטחון")
                else:
                    success, msg = UserManager.register_user(reg_user, reg_pass, security_q, security_a)
                    if success:
                        st.success("✅ חשבון נוצר בהצלחה!")
                        st.info("כעת התחבר עם שם המשתמש והסיסמא שלך")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
    
    # ══════════════════════════════════════════════════════════
    # TAB 3: שחזור סיסמא
    # ══════════════════════════════════════════════════════════
    
    elif st.session_state.auth_mode == "recover":
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #667eea; font-size: 32px; margin: 0;">🔑 שחזור סיסמא</h1>
        <p style="color: #999; font-size: 14px; margin-top: 8px;">תשובה נכונה = סיסמא חדשה</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("recover_form"):
            st.markdown("### שחזור גישה לחשבון")
            
            recover_user = st.text_input(
                "שם משתמש",
                placeholder="הכנס את שם המשתמש שלך",
                key="recover_user"
            )
            
            if recover_user:
                # בדוק אם המשתמש קיים וקח את שאלת הביטחון
                security_info = UserManager.get_security_question(recover_user)
                if security_info:
                    security_q, _ = security_info
                    st.write(f"**שאלת הביטחון שלך:** {security_q}")
                    
                    security_a = st.text_input(
                        "תשובתך",
                        placeholder="הכנס את התשובה",
                        key="recover_answer"
                    )
                    
                    new_pass = st.text_input(
                        "סיסמא חדשה",
                        type="password",
                        placeholder="בחר סיסמא חדשה",
                        key="new_pass"
                    )
                    
                    submitted = st.form_submit_button(
                        "🔑 שחזור סיסמא",
                        use_container_width=True
                    )
                    
                    if submitted:
                        if not security_a or not new_pass:
                            st.warning("⚠️ מלא את כל השדות")
                        else:
                            success, msg = UserManager.reset_password(recover_user, security_a, new_pass)
                            if success:
                                st.success("✅ סיסמא חדשה נוצרה!")
                                st.info("כעת התחבר עם הסיסמא החדשה שלך")
                                st.session_state.auth_mode = "login"
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                else:
                    st.error("❌ משתמש לא נמצא")
    
    st.stop()

# ═══════════════════════════════════════════════════════════════
# הקוד המקורי שלך - כל הפונקציות
# ═══════════════════════════════════════════════════════════════

from config import (HELP, MY_STOCKS_BASE, SCAN_LIST,
                    COMMODITIES_SYMBOLS, CRYPTO_SYMBOLS, TASE_SCAN)
from logic   import fetch_master_data
from storage import load_all_to_session, save, load
from tooltips_he import inject_tooltip_css, tooltip, render_glossary
from scheduler_agents import get_scheduler

import realtime_data, market_ai, bull_bear, simulator
import podcasts_ai, alerts_ai, financials_ai, crypto_ai
import news_ai, telegram_ai, analytics_ai, pro_tools_ai
import premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai
import social_sentiment_ai, tax_fees_ai, market_scanner
import ai_portfolio, commodities_tab, pattern_ai, portfolio_optimizer

st.set_page_config(
    page_title="Investment Hub Elite 2026",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_all_to_session(st.session_state)
try:
    from storage import load_ai_portfolio
    load_ai_portfolio(st.session_state)
except Exception:
    pass

# הוסף מידע משתמש לsidebar
with st.sidebar:
    st.markdown("### 👤 חשבון")
    st.write(f"**{st.session_state.username}**")
    
    if st.button("🚪 התנתק"):
        SessionManager.clear_session(st.session_state.username)
        st.session_state.logged_in = False
        st.rerun()

# ─── עיצוב ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif !important; direction:rtl; text-align:right; }
.stApp { background:#f5f7fa !important; }
</style>
""", unsafe_allow_html=True)

inject_tooltip_css()

# ─── Header ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 14px; padding: 20px; color: white;">
    <h2>🌐 Investment Hub Elite 2026</h2>
    <p>ברוכים הבאים, <b>{st.session_state.username}!</b></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 15px; 
                border: 2px solid #667eea; text-align: center;">
    <h4>⏰ {datetime.now().strftime('%H:%M')}</h4>
    <p>{datetime.now().strftime('%d/%m/%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# ─── Main Tabs ────────────────────────────────────────────────────────────────

tab_names = [
    "📊 לוח בקרה", "📈 בזמן אמת", "🎯 AI שוק", "📰 חדשות", "🎙️ פודקאסטים",
    "🔔 התראות", "💰 תיק", "📉 ניתוח", "🇮🇱 בורסה", "🇺🇸 מניות US",
    "🪙 קריפטו", "📦 סחורות", "💎 פרימיום", "🚀 כלים", "📊 ML",
    "⚡ ביצוע", "🛡️ הגנה", "📋 תיק AI", "💹 בדיקה", "🎨 דפוסים",
    "📑 דוח", "⚙️ הגדרות", "🔐 אבטחה", "📞 תמיכה", "ℹ️ אודות"
]

tabs = st.tabs(tab_names)

# תוכן הטאבים
try:
    with tabs[0]:
        st.subheader("📊 לוח בקרה")
        try:
            realtime_data.show_dashboard()
        except:
            st.info("📈 טוען נתונים...")
    
    with tabs[1]:
        st.subheader("📈 נתונים בזמן אמת")
        try:
            realtime_data.show_realtime()
        except:
            st.info("📈 טוען...")
    
    with tabs[2]:
        st.subheader("🎯 Market AI")
        try:
            market_ai.show_market_analysis()
        except:
            st.info("🎯 טוען...")
    
    with tabs[3]:
        st.subheader("📰 חדשות")
        try:
            news_ai.show_news()
        except:
            st.info("📰 טוען...")
    
    with tabs[4]:
        st.subheader("🎙️ פודקאסטים")
        try:
            podcasts_ai.show_podcasts()
        except:
            st.info("🎙️ טוען...")
    
    with tabs[5]:
        st.subheader("🔔 התראות")
        try:
            alerts_ai.show_alerts()
        except:
            st.info("🔔 טוען...")
    
    with tabs[6]:
        st.subheader("💰 תיק השקעות")
        try:
            ai_portfolio.show_portfolio()
        except:
            st.info("💰 טוען...")
    
    with tabs[7]:
        st.subheader("📉 ניתוח")
        try:
            analytics_ai.show_analytics()
        except:
            st.info("📉 טוען...")
    
    with tabs[8]:
        st.subheader("🇮🇱 בורסה ישראלית")
        try:
            market_scanner.show_tase()
        except:
            st.info("🇮🇱 טוען...")
    
    with tabs[9]:
        st.subheader("🇺🇸 מניות US")
        try:
            market_scanner.show_us()
        except:
            st.info("🇺🇸 טוען...")
    
    with tabs[10]:
        st.subheader("🪙 קריפטו")
        try:
            crypto_ai.show_crypto()
        except:
            st.info("🪙 טוען...")
    
    with tabs[11]:
        st.subheader("📦 סחורות")
        try:
            commodities_tab.show_commodities()
        except:
            st.info("📦 טוען...")
    
    with tabs[12]:
        st.subheader("💎 תכניות פרימיום")
        try:
            premium_agents_ai.show_premium()
        except:
            st.info("💎 טוען...")
    
    with tabs[13]:
        st.subheader("🚀 כלים מתקדמים")
        try:
            pro_tools_ai.show_pro_tools()
        except:
            st.info("🚀 טוען...")
    
    with tabs[14]:
        st.subheader("📊 Machine Learning")
        try:
            ml_learning_ai.show_ml_learning()
        except:
            st.info("📊 טוען...")
    
    with tabs[15]:
        st.subheader("⚡ ביצוע עסקאות")
        try:
            execution_ai.show_execution()
        except:
            st.info("⚡ טוען...")
    
    with tabs[16]:
        st.subheader("🛡️ מנגנוני הגנה")
        try:
            failsafes_ai.show_failsafes()
        except:
            st.info("🛡️ טוען...")
    
    with tabs[17]:
        st.subheader("📋 תיק ניהול AI")
        try:
            ai_portfolio.show_ai_portfolio()
        except:
            st.info("📋 טוען...")
    
    with tabs[18]:
        st.subheader("💹 בדיקת עבר")
        try:
            backtest_ai.show_backtest()
        except:
            st.info("💹 טוען...")
    
    with tabs[19]:
        st.subheader("🎨 דפוסי גרף")
        try:
            pattern_ai.show_patterns()
        except:
            st.info("🎨 טוען...")
    
    with tabs[20]:
        st.subheader("📑 דוח ביצוע")
        try:
            analytics_ai.show_report()
        except:
            st.info("📑 טוען...")
    
    with tabs[21]:
        st.subheader("⚙️ הגדרות")
        st.write("הגדר את ההעדפות שלך כאן")
    
    with tabs[22]:
        st.subheader("🔐 אבטחה")
        st.write("נהל הגדרות אבטחה")
    
    with tabs[23]:
        st.subheader("📞 תמיכה")
        st.write("קבל עזרה ותמיכה")
    
    with tabs[24]:
        st.subheader("ℹ️ אודות")
        st.markdown("""
        **Investment Hub Elite 2026** - מערכת מולטי-משתמש לסחר בהשקעות
        
        ✨ תכונות:
        - התחברויות קבועות (30 ימים)
        - 4 סוכנים סוחרים אוטונומיים
        - שחזור סיסמא עם שאלות ביטחון
        - ניתוח מתקדם
        - ניהול סיכונים
        """)

except Exception as e:
    st.error(f"שגיאה בטעינת טאבים")

try:
    scheduler = get_scheduler()
    if scheduler and not scheduler.running:
        scheduler.start()
except:
    pass
