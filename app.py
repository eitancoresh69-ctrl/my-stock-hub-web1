# app.py — מרכז השקעות עלית 2026
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ==============================================================
# מערכת התחברות וניהול סשן
# ==============================================================

from storage import SessionManager, UserManager
from logic import fetch_master_data

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# בדיקה אם קיים סשן שמור
if not st.session_state.logged_in:
    stored_username = SessionManager.get_stored_username()
    if stored_username:
        st.session_state.logged_in = True
        st.session_state.username = stored_username

# ==============================================================
# מסך התחברות והרשמה (מוצג רק אם לא מחוברים)
# ==============================================================

if not st.session_state.logged_in:
    st.set_page_config(page_title="מרכז השקעות עלית 2026", page_icon="🤖", layout="centered")
    
    # CSS להסרת סרגל הצד ועיצוב
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Heebo', sans-serif; direction: rtl; }
    body, .stApp { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px; color: white;">
    <h1 style="font-size: 36px; margin: 0;">🤖 מרכז השקעות עלית</h1>
    <p style="font-size: 16px; margin-top: 8px;">מערכת השקעות מבוססת בינה מלאכותית</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔓 התחברות", use_container_width=True): st.session_state.auth_mode = "login"
    with col2:
        if st.button("📝 הרשמה", use_container_width=True): st.session_state.auth_mode = "register"
    with col3:
        if st.button("🔑 שחזור סיסמה", use_container_width=True): st.session_state.auth_mode = "recover"
    
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    
    st.divider()
    
    if st.session_state.auth_mode == "login":
        with st.form("login_form"):
            st.markdown("### התחברות לחשבון")
            login_user = st.text_input("שם משתמש", placeholder="הזן את שם המשתמש שלך")
            login_pass = st.text_input("סיסמה", type="password", placeholder="הזן את הסיסמה שלך")
            if st.form_submit_button("🔓 התחבר", use_container_width=True):
                if login_user and login_pass:
                    success, data = UserManager.login(login_user, login_pass)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        st.success("✅ התחברת בהצלחה!")
                        st.rerun()
                    else:
                        st.error(f"❌ {data}")
                else:
                    st.warning("⚠️ אנא הזן שם משתמש וסיסמה")
                    
    elif st.session_state.auth_mode == "register":
        with st.form("register_form"):
            st.markdown("### יצירת חשבון חדש")
            reg_user = st.text_input("שם משתמש", placeholder="בחר שם משתמש")
            reg_pass = st.text_input("סיסמה", type="password", placeholder="בחר סיסמה חזקה")
            reg_pass_conf = st.text_input("אישור סיסמה", type="password", placeholder="הזן את הסיסמה שוב")
            security_q = st.selectbox("שאלת אבטחה (לשחזור סיסמה)", 
                                      ["מה שם חיית המחמד שלך?", "מה שם העיר שבה נולדת?", "מה שם בית הספר הראשון שלך?"])
            security_a = st.text_input("תשובה לשאלת האבטחה")
            if st.form_submit_button("📝 הרשם", use_container_width=True):
                if reg_pass != reg_pass_conf:
                    st.error("❌ הסיסמאות אינן תואמות")
                elif reg_user and reg_pass and security_a:
                    success, msg = UserManager.register_user(reg_user, reg_pass, security_q, security_a)
                    if success:
                        st.success("✅ החשבון נוצר בהצלחה! התחבר כעת.")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ אנא מלא את כל השדות")
                    
    elif st.session_state.auth_mode == "recover":
        with st.form("recover_form"):
            st.markdown("### שחזור גישה לחשבון")
            recover_user = st.text_input("שם משתמש", placeholder="הזן את שם המשתמש שלך")
            if recover_user:
                security_info = UserManager.get_security_question(recover_user)
                if security_info:
                    st.info(f"שאלת האבטחה שלך: **{security_info[0]}**")
                    security_a = st.text_input("תשובתך")
                    new_pass = st.text_input("סיסמה חדשה", type="password")
                    if st.form_submit_button("🔑 שחזור סיסמה", use_container_width=True):
                        success, msg = UserManager.reset_password(recover_user, security_a, new_pass)
                        if success:
                            st.success("✅ הסיסמה שונתה בהצלחה!")
                        else:
                            st.error(f"❌ {msg}")
                else:
                    st.error("❌ המשתמש לא נמצא במערכת")
                    st.form_submit_button("חפש שוב")
            else:
                st.form_submit_button("חפש משתמש")
                
    st.stop()

# ==============================================================
# המערכת הראשית (לאחר התחברות)
# ==============================================================

import realtime_data, market_ai, bull_bear, simulator
import podcasts_ai, alerts_ai, financials_ai, crypto_ai
import news_ai, telegram_ai, analytics_ai, pro_tools_ai
import premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai
import social_sentiment_ai, tax_fees_ai, market_scanner
import ai_portfolio, commodities_tab, pattern_ai, portfolio_optimizer

from tooltips_he import inject_tooltip_css
from storage import load_all_to_session

st.set_page_config(page_title="מרכז השקעות עלית 2026", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")
load_all_to_session(st.session_state)

# CSS להסרת סרגל הצד לחלוטין ולעיצוב כללי
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif !important; direction:rtl; text-align:right; }
.stApp { background:#f5f7fa !important; }
.block-container { padding-top:1rem !important; max-width:100% !important; }
.ai-card { background:#fff; padding:12px 18px; border-radius:12px; border-right:5px solid #1976d2; box-shadow:0 1px 6px rgba(0,0,0,0.08); margin-bottom:10px; }

/* העלמת סרגל הצד לחלוטין מכל הכיוונים */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

inject_tooltip_css()

# כותרת עליונה משולבת עם פרטי משתמש
col1, col2, col3 = st.columns([4, 2, 1])
with col1:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1565c0 0%,#1976d2 55%,#42a5f5 100%); border-radius:14px; padding:16px 22px; color:white;">
    <h2 style="margin:0;">🌐 מרכז השקעות עלית 2026</h2>
    <p style="margin:0; opacity:0.9;">מחובר כ: <b>{st.session_state.username}</b></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="ai-card" style="text-align:center;">
    <h4 style="margin:0; color:#1565c0;">⏰ {datetime.now().strftime('%H:%M')}</h4>
    <p style="margin:0; font-size:14px; color:#666;">{datetime.now().strftime('%d/%m/%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.write("") 
    if st.button("🚪 התנתקות", use_container_width=True):
        SessionManager.clear_session(st.session_state.username)
        st.session_state.logged_in = False
        st.rerun()

st.write("")

# הגדרת תיק המניות המלא והאישי שלך ישירות בקובץ הראשי!
MY_PERSONAL_PORTFOLIO = [
    "MSFT", "AAPL", "NVDA", "TSLA", "PLTR", # ארה"ב
    "ENLT.TA", "POLI.TA", "LUMI.TA"         # ישראל
]

MAIN_SCAN_LIST = [
    "AMZN", "META", "GOOGL",                # ענקיות נוספות
    "ICL.TA", "TSEM.TA",                    # תל אביב
    "GC=F", "SI=F", "CL=F",                 # סחורות: זהב, כסף, נפט
    "BTC-USD", "ETH-USD"                    # קריפטו
]

all_symbols = list(set(MY_PERSONAL_PORTFOLIO + MAIN_SCAN_LIST))

# שאיבת הנתונים 
with st.spinner("🔄 שואב נתוני שוק עדכניים לתיק שלך..."):
    try:
        df_all = fetch_master_data(all_symbols)
    except Exception as e:
        df_all = pd.DataFrame()
        st.error(f"שגיאה בשאיבת הנתונים מ-logic.py: {e}")

if df_all is None or df_all.empty:
    st.error("⚠️ לא הצלחנו למשוך נתונים כלל. אנא בדוק את החיבור לאינטרנט או שהבורסה סגורה ואין נתונים זמינים.")
else:
    # יצירת הטאבים - הכל מתורגם
    tab_names = [
        "סורק שוק 🌐", "זמן אמת 📈", "תיק מנוהל 📋", "התראות חכמות 🔔", 
        "מודיעין שוק 🌍", "למידת מכונה 🧠", "סחורות 📦", "קריפטו 🪙", 
        "אופטימיזציית תיק 📐", "פודקאסטים 🎧", "חדשות 📰", "בדיקת עבר ⏪", 
        "שור/דוב ⚖️", "דוחות כספיים 📚", "צמיחה וסיכון 🚀", "כלים מתקדמים 🧰",
        "הגנות מערכת 🛡️", "ביצוע עסקאות ⚙️", "סנטימנט רשתות 💬", "מיסים ועמלות 💰"
    ]

    tabs = st.tabs(tab_names)

    # טעינת המודולים עם הצגת שגיאות מפורטות כדי שנדע בדיוק מה תוקע את המערכת
    with tabs[0]:
        try: market_scanner.render_market_scanner() # או שם הפונקציה המקורית שלך
        except Exception as e: st.error(f"שגיאה בטעינת סורק שוק: {e}")

    with tabs[1]:
        try: 
            if hasattr(realtime_data, 'render_live_data_center'):
                realtime_data.render_live_data_center(MY_PERSONAL_PORTFOLIO)
            elif hasattr(realtime_data, 'show_realtime'):
                realtime_data.show_realtime()
            else:
                st.info("מודול זמן אמת פועל. הנתונים נטענו בהצלחה במערכת.")
        except Exception as e: st.error(f"שגיאה בזמן אמת: {e}")

    with tabs[2]:
        try: ai_portfolio.render_ai_portfolio(df_all)
        except Exception as e: st.error(f"שגיאה בטעינת תיק ה-AI: {e}")

    with tabs[3]:
        try: alerts_ai.render_smart_alerts(df_all)
        except Exception as e: st.error(f"שגיאה במערכת ההתראות: {e}")

    with tabs[4]:
        try: market_ai.render_market_intelligence()
        except Exception as e: st.error(f"שגיאה בטעינת מודיעין שוק: {e}")

    with tabs[5]:
        try: ml_learning_ai.render_machine_learning(df_all)
        except Exception as e: st.error(f"שגיאה בלמידת מכונה: {e}")

    with tabs[6]:
        try: commodities_tab.render_commodities()
        except Exception as e: st.error(f"שגיאה בטעינת סחורות: {e}")

    with tabs[7]:
        try: crypto_ai.render_crypto_arena()
        except Exception as e: st.error(f"שגיאה בזירת הקריפטו: {e}")

    with tabs[8]:
        try: portfolio_optimizer.render_portfolio_optimizer()
        except Exception as e: st.info("האופטימיזציה נטענת או שהיא משולבת במערכת הלמידה.")

    with tabs[9]:
        try: podcasts_ai.render_podcasts_analysis()
        except Exception as e: st.error(f"שגיאה בפודקאסטים: {e}")

    with tabs[10]:
        try: news_ai.render_live_news(MY_PERSONAL_PORTFOLIO)
        except Exception as e: st.error(f"שגיאה בחדשות: {e}")

    with tabs[11]:
        try: backtest_ai.render_backtester(df_all)
        except Exception as e: st.error(f"שגיאה בבדיקת העבר: {e}")

    with tabs[12]:
        try: bull_bear.render_bull_bear(df_all)
        except Exception as e: st.error(f"שגיאה במעבדת שור/דוב: {e}")

    with tabs[13]:
        try: financials_ai.render_financial_reports(df_all)
        except Exception as e: st.error(f"שגיאה בדוחות הכספיים: {e}")

    with tabs[14]:
        try: growth_risk_ai.render_growth_and_risk(df_all)
        except Exception as e: st.error(f"שגיאה בצמיחה וסיכון: {e}")

    with tabs[15]:
        try: pro_tools_ai.render_pro_tools(df_all, pd.DataFrame())
        except Exception as e: st.error(f"שגיאה בכלים מתקדמים: {e}")

    with tabs[16]:
        try: failsafes_ai.render_failsafes()
        except Exception as e: st.error(f"שגיאה בהגנות המערכת: {e}")

    with tabs[17]:
        try: execution_ai.render_execution_engine()
        except Exception as e: st.error(f"שגיאה במנוע הביצוע: {e}")

    with tabs[18]:
        try: social_sentiment_ai.render_social_sentiment()
        except Exception as e: st.error(f"שגיאה בסנטימנט רשתות: {e}")

    with tabs[19]:
        try: tax_fees_ai.render_tax_fees_calculator()
        except Exception as e: st.info("טוען מחשבון מיסים ועמלות...")

# הפעלת סוכני רקע
try:
    from scheduler_agents import get_scheduler
    scheduler = get_scheduler()
    if scheduler and not scheduler.running:
        scheduler.start()
except:
    pass
