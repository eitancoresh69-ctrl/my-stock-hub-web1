# app.py — Investment Hub Elite 2026 | גרסה מלאה
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
import market_ai, bull_bear, simulator, podcasts_ai, alerts_ai
import financials_ai, crypto_ai, news_ai, telegram_ai, analytics_ai
import pro_tools_ai, premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai, social_sentiment_ai, tax_fees_ai

# ─── הגדרות עמוד ───
st.set_page_config(
    page_title="Investment Hub Elite 2026",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# רענון אוטומטי כל 15 דקות
st.markdown(
    "<script>setInterval(function(){ window.location.reload(); }, 900000);</script>",
    unsafe_allow_html=True,
)

# ─── עיצוב RTL ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Assistant', sans-serif;
    direction: rtl;
    text-align: right;
}
.stApp { background-color: #f4f6f9; }
.block-container { padding-top: 1rem !important; }
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 14px !important; }
.ai-card {
    background: white; padding: 15px; border-radius: 12px;
    border-right: 6px solid #1a73e8;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 15px;
}
div[data-testid="stTabs"] button { font-weight: bold; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ─── שליפת נתונים ───
try:
    with st.spinner("☁️ שואב נתוני עתק מוול סטריט..."):
        df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))
except Exception:
    st.error("⚠️ שגיאה זמנית. מציג נתונים חלקיים.")
    df_all = pd.DataFrame()

# ─── כותרת ───
st.title("🌐 Investment Hub Elite 2026")

if st.session_state.get("kill_switch_active", False):
    st.error("🚨 **מתג ההשמדה פעיל!** גש לטאב '🛡️ הגנה' לאיפוס.")

# ─── מדדים עליונים ───
c1, c2, c3, c4, c5 = st.columns(5)
try:
    vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
except Exception:
    vix = 0.0
c1.metric("📊 VIX", f"{vix:.2f}")
c2.metric("🏆 מניות זהב (ציון≥5)", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("📋 סה\"כ בניתוח", len(df_all) if not df_all.empty else 0)
c4.metric("🕒 עדכון", datetime.now().strftime("%H:%M"))
c5.metric("🛡️ מצב", "🔴 Kill Switch" if st.session_state.get("kill_switch_active", False) else "🟢 תקין")

# ─── 22 טאבים ───
tabs = st.tabs([
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
    "⚙️ מנוע ביצוע",    # 17
    "🛡️ הגנה",          # 18
    "🧠 למידת מכונה",   # 19
    "🐦 רשתות",         # 20
    "💸 מיסים",         # 21
])

# ── טאב 0: התיק ──
with tabs[0]:
    st.markdown(
        '<div class="ai-card"><b>📌 התיק שלי:</b> '
        'לחץ פעמיים על "קנייה" ו"כמות" לעדכון.</div>',
        unsafe_allow_html=True,
    )
    if "portfolio" not in st.session_state:
        gold_scan = (
            df_all[(df_all["Score"] >= 5) & (df_all["Symbol"].isin(SCAN_LIST))]["Symbol"].tolist()
            if not df_all.empty else []
        )
        st.session_state.portfolio = pd.DataFrame(
            [{"Symbol": t, "BuyPrice": 0.0, "Qty": 0}
             for t in list(set(MY_STOCKS_BASE + gold_scan))]
        )

    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol")
        merged["PL"] = (merged["Price"] - merged["BuyPrice"]) * merged["Qty"]
        merged["Yield"] = merged.apply(
            lambda r: ((r["Price"] / r["BuyPrice"]) - 1) * 100 if r["BuyPrice"] > 0 else 0, axis=1
        )
        edited = st.data_editor(
            merged[["Symbol","PriceStr","BuyPrice","Qty","PL","Yield",
                    "Score","RevGrowth","EarnGrowth","Margin","ROE",
                    "CashVsDebt","ZeroDebt","Action"]],
            column_config={
                "Symbol":     st.column_config.TextColumn("סימול", disabled=True),
                "PriceStr":   st.column_config.TextColumn("מחיר (חי)", disabled=True),
                "BuyPrice":   st.column_config.NumberColumn("קנייה ✏️"),
                "Qty":        st.column_config.NumberColumn("כמות ✏️"),
                "PL":         st.column_config.NumberColumn("P/L", format="%.2f", disabled=True),
                "Yield":      st.column_config.NumberColumn("תשואה %", format="%.1f%%", disabled=True),
                "Score":      st.column_config.NumberColumn("⭐ ציון", disabled=True),
                "RevGrowth":  st.column_config.NumberColumn("מכירות %", format="%.1f%%", disabled=True),
                "EarnGrowth": st.column_config.NumberColumn("רווחים %", format="%.1f%%", disabled=True),
                "Margin":     st.column_config.NumberColumn("שולי %", format="%.1f%%", disabled=True),
                "ROE":        st.column_config.NumberColumn("ROE %", format="%.1f%%", disabled=True),
                "CashVsDebt": st.column_config.TextColumn("מזומן>חוב", disabled=True),
                "ZeroDebt":   st.column_config.TextColumn("חוב 0", disabled=True),
                "Action":     st.column_config.TextColumn("המלצת AI", disabled=True),
            },
            use_container_width=True, hide_index=True,
        )
        st.session_state.portfolio = edited[["Symbol", "BuyPrice", "Qty"]]

        active = merged[merged["Qty"] > 0].copy()
        if not active.empty:
            active["PL"] = (active["Price"] - active["BuyPrice"]) * active["Qty"]
            total_pl = active["PL"].sum()
            st.markdown("---")
            s1, s2, s3 = st.columns(3)
            s1.metric("📊 מניות פעילות", len(active))
            s2.metric("📈 רווח/הפסד כולל",
                      f"{'🟢 +' if total_pl >= 0 else '🔴 '}₪{abs(total_pl):,.2f}")
            s3.metric("⭐ ממוצע ציון PDF", f"{active['Score'].mean():.1f}/6")

# ── טאב 1: סורק PDF ──
with tabs[1]:
    st.markdown(
        '<div class="ai-card"><b>🔍 סורק PDF:</b> מניות מרשימת הסריקה עם ציון ≥ 4.</div>',
        unsafe_allow_html=True,
    )
    if not df_all.empty:
        scanner = df_all[(df_all["Symbol"].isin(SCAN_LIST)) & (df_all["Score"] >= 4)].sort_values(
            "Score", ascending=False)
        if not scanner.empty:
            st.dataframe(
                scanner[["Symbol","PriceStr","Score","RevGrowth","Margin","RSI","MA50","Action","AI_Logic"]],
                column_config={
                    "Symbol":    "סימול",
                    "PriceStr":  "מחיר (חי)",
                    "Score":     st.column_config.NumberColumn("⭐ ציון", format="%.0f"),
                    "RevGrowth": st.column_config.NumberColumn("מכירות %", format="%.1f%%"),
                    "Margin":    st.column_config.NumberColumn("שולי %", format="%.1f%%"),
                    "RSI":       st.column_config.NumberColumn("RSI", format="%.1f"),
                    "MA50":      st.column_config.NumberColumn("MA50", format="%.2f"),
                    "Action":    "המלצה",
                    "AI_Logic":  "לוגיקה",
                },
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("לא נמצאו מניות בציון 4+ ברשימת הסריקה.")

with tabs[2]:
    growth_risk_ai.render_growth_and_risk(df_all)

with tabs[3]:
    if "portfolio" in st.session_state and not df_all.empty:
        pro_tools_ai.render_pro_tools(df_all, st.session_state.portfolio)
    else:
        st.info("הוסף מניות לתיק.")

with tabs[4]:
    if not df_all.empty:
        financials_ai.render_financial_reports(df_all)

with tabs[5]:
    st.markdown('<div class="ai-card"><b>💰 ניתוח דיבידנדים:</b></div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all["DivYield"] > 0].copy()
        def _div_safe(row):
            if row["PayoutRatio"] <= 0: return "לא ידוע"
            if row["PayoutRatio"] > 80: return "⚠️ סכנת קיצוץ"
            if row["PayoutRatio"] < 60 and row["CashVsDebt"] == "✅": return "🛡️ בטוח מאוד"
            return "✅ יציב"
        div_df["Safety"] = div_df.apply(_div_safe, axis=1)
        div_df["ExDateClean"] = div_df["ExDate"].apply(
            lambda x: pd.Timestamp(x, unit="s").strftime("%d/%m/%Y") if pd.notnull(x) else "לא ידוע"
        )
        st.dataframe(
            div_df.sort_values("DivYield", ascending=False)[
                ["Symbol","DivYield","DivRate","FiveYrDiv","PayoutRatio","Safety","ExDateClean"]],
            column_config={
                "Symbol":      "סימול",
                "DivYield":    st.column_config.NumberColumn("תשואה %", format="%.2f%%"),
                "DivRate":     st.column_config.NumberColumn("קצבה ($)", format="$%.2f"),
                "FiveYrDiv":   st.column_config.NumberColumn("ממוצע 5Y", format="%.2f%%"),
                "PayoutRatio": st.column_config.NumberColumn("חלוקה %", format="%.1f%%"),
                "Safety":      "בטיחות AI",
                "ExDateClean": "תאריך אקס",
            },
            use_container_width=True, hide_index=True,
        )

with tabs[6]:
    alerts_ai.render_smart_alerts(df_all)

with tabs[7]:
    simulator.render_value_agent(df_all)

with tabs[8]:
    simulator.render_day_trade_agent(df_all)

with tabs[9]:
    premium_agents_ai.render_premium_agents(df_all)

with tabs[10]:
    if not df_all.empty:
        backtest_ai.render_backtester(df_all)

with tabs[11]:
    podcasts_ai.render_podcasts_analysis()

with tabs[12]:
    market_ai.render_market_intelligence()

with tabs[13]:
    if not df_all.empty:
        bull_bear.render_bull_bear(df_all)

with tabs[14]:
    crypto_ai.render_crypto_arena()

with tabs[15]:
    news_ai.render_live_news(MY_STOCKS_BASE)

with tabs[16]:
    analytics_ai.render_analytics_dashboard()

with tabs[17]:
    execution_ai.render_execution_engine()

with tabs[18]:
    failsafes_ai.render_failsafes()

with tabs[19]:
    ml_learning_ai.render_machine_learning()

with tabs[20]:
    social_sentiment_ai.render_social_intelligence()

with tabs[21]:
    tax_fees_ai.render_tax_optimization()
