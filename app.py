# app.py — Investment Hub Elite 2026 | גרסה מלאה + כל התוספות החדשות
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ---- ייבוא כל המודולים ----
from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
import market_ai
import bull_bear
import simulator
import podcasts_ai
import alerts_ai
import financials_ai
import crypto_ai
import news_ai
import telegram_ai
import analytics_ai
import pro_tools_ai
import premium_agents_ai
import growth_risk_ai
import backtest_ai

# ---- מודולים חדשים ----
import execution_ai
import failsafes_ai
import ml_learning_ai
import social_sentiment_ai
import tax_fees_ai

# ---- הגדרות עמוד ----
st.set_page_config(page_title="Investment Hub Elite 2026", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<script>setInterval(function(){ window.location.reload(); }, 900000);</script>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f4f6f9; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 14px !important; }
    .ai-card { background: white; padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }
    div[data-testid="stTabs"] button { font-weight: bold; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

# ---- שליפת נתונים ----
try:
    with st.spinner("שואב נתוני עתק מוול סטריט..."):
        df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))
except Exception as e:
    st.error("⚠️ אירעה שגיאה זמנית בחיבור לשרתי הבורסה. מציג נתונים חלקיים.")
    df_all = pd.DataFrame()

# ---- כותרת ראשית ----
st.title("🌐 Investment Hub Elite 2026")

# בנר אזהרה אם Kill Switch פעיל
if st.session_state.get('kill_switch_active', False):
    st.error("🚨 **מתג ההשמדה פעיל!** כל המסחר מושהה. גש לטאב '🛡️ הגנה' לאיפוס.")

c1, c2, c3, c4 = st.columns(4)
try:
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except:
    vix = 0.0
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות 'זהב' (Score≥5)", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))
c4.metric("🛡️ מצב מערכת", "🔴 Kill Switch" if st.session_state.get('kill_switch_active', False) else "🟢 תקין")

# ---- 21 טאבים ----
tabs = st.tabs([
    # טאבים מקוריים (17)
    "📌 התיק",          # 0
    "🔍 סורק PDF",      # 1
    "🚀 צמיחה",         # 2
    "💼 רנטגן",         # 3
    "📚 דוחות",         # 4
    "💰 דיבידנדים",     # 5
    "🔔 התראות",        # 6
    "📈 סוכן ערך",      # 7
    "⚡ סוכן יומי",     # 8
    "🤖 פרימיום",       # 9
    "⏪ בק-טסט",        # 10
    "🎧 פודקאסטים",     # 11
    "🌍 מאקרו",         # 12
    "⚖️ שור/דוב",       # 13
    "₿ קריפטו",         # 14
    "📰 חדשות",         # 15
    "📊 אנליטיקה",      # 16
    # טאבים חדשים (4)
    "⚙️ מנוע ביצוע",    # 17
    "🛡️ הגנה",          # 18
    "🧠 למידת מכונה",   # 19
    "🐦 רשתות חברתיות", # 20
    "💸 מיסים ועמלות",  # 21
])

# ---- טאב 0: התיק ----
with tabs[0]:
    st.markdown('<div class="ai-card"><b>התיק שלי (Mega-Table):</b> לחץ פעמיים על מחיר קנייה וכמות כדי לעדכן. המערכת תשמור את הנתונים לחישוב הרנטגן.</div>', unsafe_allow_html=True)
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])

    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        edited = st.data_editor(
            merged[["Symbol", "PriceStr", "BuyPrice", "Qty", "PL", "Yield", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt"]],
            column_config={
                "Symbol":    st.column_config.TextColumn("סימול", disabled=True),
                "PriceStr":  st.column_config.TextColumn("מחיר", disabled=True),
                "BuyPrice":  st.column_config.NumberColumn("קנייה ✏️"),
                "Qty":       st.column_config.NumberColumn("כמות ✏️"),
                "PL":        st.column_config.NumberColumn("P/L", format="%.2f", disabled=True),
                "Yield":     st.column_config.NumberColumn("תשואה %", format="%.1f%%", disabled=True),
                "Score":     st.column_config.NumberColumn("⭐ ציון PDF", disabled=True),
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1f%%", disabled=True),
                "EarnGrowth":st.column_config.NumberColumn("צמיחת רווחים", format="%.1f%%", disabled=True),
                "Margin":    st.column_config.NumberColumn("שולי רווח", format="%.1f%%", disabled=True),
                "ROE":       st.column_config.NumberColumn("ROE", format="%.1f%%", disabled=True),
                "CashVsDebt":st.column_config.TextColumn("מזומן>חוב", disabled=True),
                "ZeroDebt":  st.column_config.TextColumn("חוב 0", disabled=True)
            }, use_container_width=True, hide_index=True
        )
        st.session_state.portfolio = edited[["Symbol", "BuyPrice", "Qty"]]

# ---- טאב 1: סורק PDF ----
with tabs[1]:
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(scanner[["Symbol", "PriceStr", "Score", "RevGrowth", "Margin", "RSI", "MA50", "Action"]],
            column_config={
                "PriceStr": "מחיר", "Score": "⭐ ציון",
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1f%%"),
                "Margin":    st.column_config.NumberColumn("שולי רווח", format="%.1f%%"),
                "RSI":       st.column_config.NumberColumn("RSI", format="%.1f"),
                "MA50":      st.column_config.NumberColumn("MA50", format="%.2f"),
                "Action":    "המלצת AI"
            }, use_container_width=True, hide_index=True)

# ---- טאב 2: צמיחה וסיכונים ----
with tabs[2]:
    growth_risk_ai.render_growth_and_risk(df_all)

# ---- טאב 3: רנטגן ----
with tabs[3]:
    if 'portfolio' in st.session_state and not df_all.empty:
        pro_tools_ai.render_pro_tools(df_all, st.session_state.portfolio)

# ---- טאב 4: דוחות ----
with tabs[4]:
    financials_ai.render_financial_reports(df_all)

# ---- טאב 5: דיבידנדים ----
with tabs[5]:
    st.markdown('<div class="ai-card"><b>ניתוח תזרים מזומנים פסיבי (דיבידנדים לעומק):</b> שילוב של קצבה שנתית, יחס חלוקה וממוצע היסטורי.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all['DivYield'] > 0].copy()
        def assess_div_safety(row):
            if row['PayoutRatio'] <= 0: return "לא ידוע"
            if row['PayoutRatio'] > 80.0: return "⚠️ סכנת קיצוץ"
            if row['PayoutRatio'] < 60.0 and row['CashVsDebt'] == "✅": return "🛡️ בטוח מאוד"
            return "✅ יציב"
        div_df['Safety'] = div_df.apply(assess_div_safety, axis=1)
        div_df['ExDateClean'] = div_df['ExDate'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y') if pd.notnull(x) else "לא ידוע")
        st.dataframe(
            div_df.sort_values(by="DivYield", ascending=False)[["Symbol", "DivYield", "DivRate", "FiveYrDiv", "PayoutRatio", "Safety", "ExDateClean"]],
            column_config={
                "Symbol":      "סימול",
                "DivYield":    st.column_config.NumberColumn("תשואה %", format="%.2f%%"),
                "DivRate":     st.column_config.NumberColumn("קצבה ($)", format="$%.2f"),
                "FiveYrDiv":   st.column_config.NumberColumn("ממוצע 5 שנים %", format="%.2f%%"),
                "PayoutRatio": st.column_config.NumberColumn("יחס חלוקה %", format="%.1f%%"),
                "Safety":      "בטיחות (AI)",
                "ExDateClean": "תאריך אקס"
            }, use_container_width=True, hide_index=True)

# ---- טאב 6: התראות ----
with tabs[6]:
    alerts_ai.render_smart_alerts(df_all)

# ---- טאב 7: סוכן ערך ----
with tabs[7]:
    simulator.render_value_agent(df_all)

# ---- טאב 8: סוכן יומי ----
with tabs[8]:
    simulator.render_day_trade_agent(df_all)

# ---- טאב 9: פרימיום ----
with tabs[9]:
    premium_agents_ai.render_premium_agents(df_all)

# ---- טאב 10: בק-טסט ----
with tabs[10]:
    backtest_ai.render_backtester(df_all)

# ---- טאב 11: פודקאסטים ----
with tabs[11]:
    podcasts_ai.render_podcasts_analysis()

# ---- טאב 12: מאקרו ----
with tabs[12]:
    market_ai.render_market_intelligence()

# ---- טאב 13: שור/דוב ----
with tabs[13]:
    if not df_all.empty:
        bull_bear.render_bull_bear(df_all)

# ---- טאב 14: קריפטו ----
with tabs[14]:
    crypto_ai.render_crypto_arena()

# ---- טאב 15: חדשות ----
with tabs[15]:
    news_ai.render_live_news(MY_STOCKS_BASE)

# ---- טאב 16: אנליטיקה ----
with tabs[16]:
    analytics_ai.render_analytics_dashboard()

# ---- טאב 17: מנוע ביצוע (חדש) ----
with tabs[17]:
    execution_ai.render_execution_engine()

# ---- טאב 18: מנגנון הגנה (חדש) ----
with tabs[18]:
    failsafes_ai.render_failsafes()

# ---- טאב 19: למידת מכונה (חדש) ----
with tabs[19]:
    ml_learning_ai.render_machine_learning()

# ---- טאב 20: רשתות חברתיות (חדש) ----
with tabs[20]:
    social_sentiment_ai.render_social_intelligence()

# ---- טאב 21: מיסים ועמלות (חדש) ----
with tabs[21]:
    tax_fees_ai.render_tax_optimization()
