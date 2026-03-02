# app.py — Investment Hub Elite 2026 — גרסה סופית + Tooltips עברית
import streamlit as st
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
    box-shadow:0 4px 18px rgba(21,101,192,0.22);
}
[data-testid="stMetric"] {
    background:#fff; border-radius:10px; padding:8px 14px;
    box-shadow:0 1px 5px rgba(0,0,0,0.07); border:1px solid #e8edf2;
}
[data-testid="stMetricLabel"] { color:#607d8b !important; font-size:11px !important; font-weight:700 !important; }
[data-testid="stMetricValue"] { color:#1a237e !important; font-size:20px !important; font-weight:800 !important; }
div[data-testid="stTabs"] button { font-weight:700 !important; font-size:11px !important; color:#546e7a !important; }
div[data-testid="stTabs"] button:hover { color:#1565c0 !important; background:#e3f2fd !important; }
div[data-testid="stTabs"] button[aria-selected="true"] {
    color:#1565c0 !important; border-bottom:3px solid #1565c0 !important; background:#fff !important;
}
[data-testid="stDataFrame"] th { background:#e3f2fd !important; color:#1565c0 !important; font-weight:700 !important; }
[data-testid="stDataFrame"] td { font-size:13px !important; }
.stButton > button { border-radius:8px !important; font-weight:700 !important; font-family:'Heebo',sans-serif !important; border:none !important; }
.stButton > button[kind="primary"] { background:linear-gradient(135deg,#1565c0,#1976d2) !important; color:#fff !important; }
.stButton > button[kind="secondary"] { background:#e3f2fd !important; color:#1565c0 !important; }
details summary { color:#1565c0 !important; font-weight:700 !important; }
hr { border-color:#e8edf2 !important; }
input, textarea, select { border-radius:8px !important; border:1px solid #cfd8dc !important; }
</style>
""", unsafe_allow_html=True)

inject_tooltip_css()   # ← מזריק CSS לטולטיפים

# ─── שליפת נתונים ─────────────────────────────────────────────────────────────
ALL_TICKERS = list(set(MY_STOCKS_BASE + SCAN_LIST + TASE_SCAN))
try:
    with st.spinner("☁️ שואב נתוני שוק..."):
        df_all = fetch_master_data(ALL_TICKERS)
except Exception:
    st.error("⚠️ שגיאה זמנית.")
    df_all = pd.DataFrame()

# ─── כותרת ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hub-header">
  <div style="display:flex;align-items:center;gap:14px;">
    <div style="font-size:36px;line-height:1;">🌐</div>
    <div>
      <div style="font-size:21px;font-weight:900;color:#fff;letter-spacing:-0.5px;">
        Investment Hub Elite 2026
      </div>
      <div style="font-size:12px;color:#bbdefb;margin-top:3px;">
        מניות · סחורות · קריפטו · תל אביב · AI Manager · ML · Telegram
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("kill_switch_active"):
    st.error("🚨 **מתג ההשמדה פעיל!** גש לטאב '🛡️ הגנה' לאיפוס.")

# ─── מדדים עליונים ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _top_metrics():
    try: vix = float(yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1])
    except: vix = 0.0
    try: ta35 = float(yf.Ticker("^TA35.TA").history(period="1d")["Close"].iloc[-1])
    except: ta35 = 0.0
    try:
        spy = yf.Ticker("SPY").history(period="2d")["Close"]
        spy_chg = (spy.iloc[-1]/spy.iloc[-2]-1)*100
    except: spy_chg = 0.0
    try:
        btc = yf.Ticker("BTC-USD").history(period="2d")["Close"]
        btc_chg = (btc.iloc[-1]/btc.iloc[-2]-1)*100
    except: btc_chg = 0.0
    return vix, ta35, spy_chg, btc_chg

vix, ta35, spy_chg, btc_chg = _top_metrics()
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
c1.metric("📊 VIX",          f"{vix:.1f}", delta="⚠️ גבוה" if vix>25 else "תקין", delta_color="inverse")
c2.metric("🇮🇱 TA-35",       f"{ta35:,.0f}")
c3.metric("🇺🇸 S&P 500",     f"{spy_chg:+.2f}%")
c4.metric("₿ Bitcoin",       f"{btc_chg:+.2f}%")
c5.metric("💎 מניות זהב",    len(df_all[df_all["Score"]>=5]) if not df_all.empty else 0)
c6.metric("🕒 עדכון",        datetime.now().strftime("%H:%M"))
c7.metric("🛡️ מצב",         "🔴 KILL" if st.session_state.get("kill_switch_active") else "🟢 OK")

# ─── VIX tooltip ──────────────────────────────────────────────────────────────
st.markdown(
    tooltip("ℹ️ מה זה VIX?","VIX") + "&nbsp;&nbsp;" +
    tooltip("ℹ️ Fear & Greed?","FearGreed") + "&nbsp;&nbsp;" +
    tooltip("ℹ️ מה זה ציון PDF?","Score"),
    unsafe_allow_html=True
)

# ─── Fear & Greed + מחירים ────────────────────────────────────────────────────
with st.expander("📡 Fear & Greed + מחירים חיים", expanded=True):
    fg_col, px_col = st.columns([1,2])
    with fg_col:
        realtime_data.render_fear_greed_widget()
    with px_col:
        realtime_data.render_live_prices_strip(MY_STOCKS_BASE[:6] + SCAN_LIST[:4])

aip_on   = st.session_state.get("aip_enabled", False)
aip_cash = st.session_state.get("aip_cash", 0)
aip_pos  = len(st.session_state.get("aip_positions", []))
if aip_on:
    st.success(f"🤖 תיק AI פעיל | מזומן: ₪{aip_cash:,.0f} | פוזיציות: {aip_pos}")

market_scanner.maybe_auto_scan()
n_long  = len(st.session_state.get("agent_universe_df",       pd.DataFrame()))
n_short = len(st.session_state.get("agent_universe_short_df", pd.DataFrame()))
if n_long>0 or n_short>0:
    st.info(f"🤖 סוכן ערך ← {n_long} | סוכן יומי ← {n_short}")

# ═════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📌 התיק",        # 0
    "🤖 AI מנהל",     # 1
    "📐 אופטימיזציה", # 2
    "🏅 סחורות",      # 3
    "₿ קריפטו",       # 4
    "🇮🇱 תל אביב",    # 5
    "🔍 סורק PDF",    # 6
    "🔬 Chart דפוסי", # 7
    "🚀 צמיחה",       # 8
    "💼 רנטגן",       # 9
    "📚 דוחות",       # 10
    "💰 דיבידנדים",   # 11
    "🔔 התראות",      # 12
    "📈 סוכן ערך",    # 13
    "⚡ סוכן יומי",   # 14
    "🤖 פרימיום",     # 15
    "🌐 סורק שוק",    # 16
    "⏪ בק-טסט",      # 17
    "🌍 מאקרו",       # 18
    "⚖️ שור/דוב",     # 19
    "📰 חדשות",       # 20
    "📊 אנליטיקה",    # 21
    "📱 טלגרם",       # 22
    "🛡️ הגנה",        # 23
    "🧠 ML",          # 24
    "📡 נתונים חיים", # 25
    "💸 מיסים",       # 26
    "📖 מדריך",       # 27 ← חדש!
])

# ══ 0: התיק האישי ═════════════════════════════════════════════════════════════
with tabs[0]:
    # Tooltips לתיק
    st.markdown(
        '<div class="ai-card"><b>📌 התיק שלי</b> — לחץ פעמיים לעדכון קנייה/כמות<br>'
        + tooltip("⬆️ מה זה P/L?","P/L","❓")
        + " &nbsp; "
        + tooltip("⬆️ מה זה תשואה?","Change","❓")
        + " &nbsp; "
        + tooltip("⬆️ מה זה ציון?","Score","❓")
        + "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("➕ הוסף נכס (מניה / סחורה / קריפטו / ת\"א)"):
        ca,cb,cc,cd = st.columns([2,1,1,1])
        ns = ca.text_input("סימול (AAPL / GC=F / BTC-USD / TEVA.TA)", key="ns").upper().strip()
        nb = cb.number_input("מחיר קנייה", 0.0, key="nb")
        nq = cc.number_input("כמות", 0.0, key="nq")
        if cd.button("✅ הוסף", key="nadd"):
            if ns:
                if "portfolio" not in st.session_state:
                    st.session_state.portfolio = pd.DataFrame(columns=["Symbol","BuyPrice","Qty"])
                port = st.session_state.portfolio
                if ns not in port["Symbol"].values:
                    new_row = pd.DataFrame([{"Symbol":ns,"BuyPrice":nb,"Qty":nq}])
                    st.session_state.portfolio = pd.concat([port,new_row],ignore_index=True)
                    save("portfolio_buy_prices", dict(zip(st.session_state.portfolio["Symbol"],
                                                          st.session_state.portfolio["BuyPrice"])))
                    save("portfolio_quantities",  dict(zip(st.session_state.portfolio["Symbol"],
                                                           st.session_state.portfolio["Qty"])))
                    st.success(f"✅ {ns} נוסף!")
                    st.rerun()

    if "portfolio" not in st.session_state:
        saved_prices = st.session_state.get("portfolio_buy_prices", {})
        saved_qty    = st.session_state.get("portfolio_quantities",  {})
        st.session_state.portfolio = pd.DataFrame([
            {"Symbol":t,"BuyPrice":saved_prices.get(t,0.0),"Qty":saved_qty.get(t,0)}
            for t in list(set(MY_STOCKS_BASE))
        ])

    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol", how="left")
        merged["Price"]    = merged["Price"].fillna(0)
        merged["PriceStr"] = merged.apply(
            lambda r: str(r.get("PriceStr","")) or f"${r['Price']:.2f}", axis=1)
        merged["PL"]    = (merged["Price"]-merged["BuyPrice"])*merged["Qty"]
        merged["Yield"] = merged.apply(
            lambda r: ((r["Price"]/r["BuyPrice"])-1)*100 if r["BuyPrice"]>0 else 0, axis=1)
        merged["Emoji"] = merged["Symbol"].apply(
            lambda s: "🥇" if "GC" in s else "🛢️" if any(x in s for x in ["CL","BZ","NG"]) else
                      "₿" if "BTC" in s else "Ξ" if "ETH" in s else
                      "🇮🇱" if s.endswith(".TA") else "📈")

        disp = merged[["Symbol","Emoji","PriceStr","BuyPrice","Qty","PL","Yield"]].copy()
        disp["Score"]  = merged["Score"].values  if "Score"  in merged.columns else 0
        disp["Action"] = merged["Action"].values if "Action" in merged.columns else "—"

        edited = st.data_editor(
            disp,
            column_config={
                "Symbol":   st.column_config.TextColumn("סימול",     help="סימול הנכס בבורסה (AAPL=אפל, GC=F=זהב)", disabled=True),
                "Emoji":    st.column_config.TextColumn("סוג",       help="📈=מניה | 🇮🇱=ת\"א | 🥇=זהב | 🛢️=נפט | ₿=קריפטו", disabled=True),
                "PriceStr": st.column_config.TextColumn("מחיר חי",  help="המחיר הנוכחי בשוק. מתעדכן כל 10 דקות.", disabled=True),
                "BuyPrice": st.column_config.NumberColumn("קנייה ✏️",help="המחיר ששילמת בקנייה. לחץ פעמיים לעדכון."),
                "Qty":      st.column_config.NumberColumn("כמות ✏️", help="כמה יחידות/מניות אתה מחזיק."),
                "PL":       st.column_config.NumberColumn("P/L 💰",  help="רווח/הפסד = (מחיר נוכחי - מחיר קנייה) × כמות. 🟢חיובי=רווח, 🔴שלילי=הפסד", format="%.2f", disabled=True),
                "Yield":    st.column_config.NumberColumn("תשואה %", help="אחוז הרווח/הפסד ממחיר הקנייה. 🟢חיובי=עלייה", format="%.1f%%", disabled=True),
                "Score":    st.column_config.NumberColumn("⭐ ציון",  help="ציון איכות 0-6. 5-6=זהב💎, 3-4=טוב✅, 0-2=סיכון⚠️", disabled=True),
                "Action":   st.column_config.TextColumn("המלצה AI",  help="המלצת הבינה המלאכותית: קנייה/החזק/מכירה", disabled=True),
            },
            use_container_width=True, hide_index=True,
        )
        st.session_state.portfolio = edited[["Symbol","BuyPrice","Qty"]]
        save("portfolio_buy_prices", dict(zip(edited["Symbol"], edited["BuyPrice"])))
        save("portfolio_quantities",  dict(zip(edited["Symbol"], edited["Qty"])))

        active = merged[merged["Qty"]>0].copy()
        if not active.empty:
            active["PL"] = (active["Price"]-active["BuyPrice"])*active["Qty"]
            total_pl     = active["PL"].sum()
            total_val    = (active["Price"]*active["Qty"]).sum()
            st.divider()
            s1,s2,s3,s4 = st.columns(4)
            s1.metric("📊 נכסים פעילים", len(active))
            s2.metric("💼 שווי תיק",     f"${total_val:,.0f}")
            s3.metric("📈 רווח/הפסד",
                      f"{'🟢 +' if total_pl>=0 else '🔴 '}${abs(total_pl):,.0f}")
            s4.metric("⭐ ציון ממוצע",
                      f"{active['Score'].mean():.1f}/6" if "Score" in active.columns else "—")

# ══ 1 ── תיק AI מנוהל ═════════════════════════════════════════════════════════
with tabs[1]:
    # Tooltips רלוונטיים
    st.markdown(
        tooltip("ℹ️ Stop-Loss","StopLoss") + " &nbsp; " +
        tooltip("ℹ️ Take-Profit","TakeProfit") + " &nbsp; " +
        tooltip("ℹ️ למידת מכונה","ML"),
        unsafe_allow_html=True,
    )
    ai_portfolio.render_ai_portfolio(df_all)

# ══ 2 ── אופטימיזציה ══════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown(
        tooltip("ℹ️ מה זה Efficient Frontier?","EfficientFrontier") + " &nbsp; " +
        tooltip("ℹ️ מה זה Sharpe Ratio?","Sharpe") + " &nbsp; " +
        tooltip("ℹ️ מה זה Beta?","Beta") + " &nbsp; " +
        tooltip("ℹ️ מה זה קורלציה?","Correlation"),
        unsafe_allow_html=True,
    )
    pf = st.session_state.get("portfolio")
    portfolio_optimizer.render_portfolio_optimizer(pf)

# ══ 3 ── סחורות ═══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown(
        tooltip("ℹ️ מה זה RSI?","RSI") + " &nbsp; " +
        tooltip("ℹ️ קורלציה","Correlation"),
        unsafe_allow_html=True,
    )
    commodities_tab.render_commodities()

# ══ 4–7 ═══════════════════════════════════════════════════════════════════════
with tabs[4]:  crypto_ai.render_crypto_arena()

with tabs[5]:
    st.markdown('<div class="ai-card" style="border-right-color:#0052cc;"><b>🇮🇱 בורסת תל אביב</b></div>',
                unsafe_allow_html=True)
    st.markdown(
        tooltip("ℹ️ ציון PDF","Score") + " &nbsp; " +
        tooltip("ℹ️ דיבידנד","DivYield") + " &nbsp; " +
        tooltip("ℹ️ RSI","RSI"),
        unsafe_allow_html=True,
    )
    if not df_all.empty:
        tase_df = df_all[df_all["Symbol"].str.endswith(".TA")].copy()
        if not tase_df.empty:
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("📋 מניות ת\"א", len(tase_df))
            c2.metric("🏆 ציון ≥4", len(tase_df[tase_df["Score"]>=4]))
            c3.metric("🟢 עולים", len(tase_df[tase_df["Change"]>0]))
            c4.metric("💰 דיבידנד ממוצע", f"{tase_df['DivYield'].mean():.1f}%")
            cols_t = [c for c in ["Symbol","PriceStr","Change","Score","RSI","DivYield","Action","AI_Logic"] if c in tase_df.columns]
            st.dataframe(
                tase_df[cols_t].sort_values("Score",ascending=False),
                column_config={
                    "Symbol":  st.column_config.TextColumn("סימול", help="סימול מניה בבורסה תל אביב (מסתיים ב-.TA)"),
                    "Change":  st.column_config.NumberColumn("שינוי % יומי",  format="%.2f%%", help="שינוי המחיר ביחס לאתמול"),
                    "Score":   st.column_config.NumberColumn("⭐ ציון 0-6",    help="6=כל הקריטריונים | 0=חלש"),
                    "RSI":     st.column_config.NumberColumn("RSI",            format="%.0f", help="מתחת 30=קנייה | מעל 70=מכירה"),
                    "DivYield":st.column_config.NumberColumn("דיבידנד %",     format="%.2f%%", help="אחוז הדיבידנד השנתי ממחיר המניה"),
                    "Action":  st.column_config.TextColumn("המלצת AI",         help="המלצת הבינה המלאכותית"),
                    "AI_Logic":st.column_config.TextColumn("הסבר",             help="הלוגיקה מאחורי ההמלצה"),
                },
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("הוסף מניות .TA לרשימה ב-config.py")

with tabs[6]:
    st.markdown('<div class="ai-card"><b>🔍 סורק PDF</b> — מניות עם ציון ≥ 4</div>',
                unsafe_allow_html=True)
    st.markdown(
        tooltip("ℹ️ ציון PDF","Score") + " &nbsp; " +
        tooltip("ℹ️ שולי רווח","Margin") + " &nbsp; " +
        tooltip("ℹ️ RSI","RSI") + " &nbsp; " +
        tooltip("ℹ️ צמיחת מכירות","RevGrowth"),
        unsafe_allow_html=True,
    )
    if not df_all.empty:
        scanner = df_all[(df_all["Symbol"].isin(SCAN_LIST+TASE_SCAN)) &
                         (df_all["Score"]>=4)].sort_values("Score",ascending=False)
        if not scanner.empty:
            cols_s = [c for c in ["Symbol","PriceStr","Score","RevGrowth","EarnGrowth",
                                   "Margin","RSI","Action","AI_Logic"] if c in scanner.columns]
            st.dataframe(
                scanner[cols_s],
                column_config={
                    "Score":     st.column_config.NumberColumn("⭐ ציון",       help="0-6. 5+=מניית זהב"),
                    "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1f%%", help=">10% = קריטריון עבר"),
                    "EarnGrowth":st.column_config.NumberColumn("צמיחת רווחים", format="%.1f%%", help=">10% = קריטריון עבר"),
                    "Margin":    st.column_config.NumberColumn("שולי רווח %",  format="%.1f%%", help=">10% = קריטריון עבר"),
                    "RSI":       st.column_config.NumberColumn("RSI",           format="%.0f",   help="<30=קנה | >70=מכור"),
                    "Action":    st.column_config.TextColumn("המלצה AI",        help="קנייה/החזק/מכירה"),
                },
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("לא נמצאו מניות ציון 4+ ברשימת הסריקה.")

with tabs[7]:
    st.markdown(
        tooltip("ℹ️ Golden Cross","GoldenCross") + " &nbsp; " +
        tooltip("ℹ️ Death Cross","DeathCross") + " &nbsp; " +
        tooltip("ℹ️ RSI","RSI") + " &nbsp; " +
        tooltip("ℹ️ MA50","MA50"),
        unsafe_allow_html=True,
    )
    pattern_ai.render_pattern_analysis(df_all)

# ══ 8–11 ══════════════════════════════════════════════════════════════════════
with tabs[8]:  growth_risk_ai.render_growth_and_risk(df_all)
with tabs[9]:
    if "portfolio" in st.session_state and not df_all.empty:
        pro_tools_ai.render_pro_tools(df_all, st.session_state.portfolio)
    else:
        st.info("הוסף מניות לתיק.")
with tabs[10]:
    if not df_all.empty: financials_ai.render_financial_reports(df_all)

with tabs[11]:
    st.markdown(
        tooltip("ℹ️ תשואת דיבידנד","DivYield") + " &nbsp; " +
        tooltip("ℹ️ PayoutRatio","PayoutRatio"),
        unsafe_allow_html=True,
    )
    if not df_all.empty:
        div_df = df_all[df_all["DivYield"]>0].copy()
        if not div_df.empty:
            def _div_safe(row):
                if row["PayoutRatio"]<=0: return "לא ידוע"
                if row["PayoutRatio"]>80: return "⚠️ סכנת קיצוץ"
                if row["PayoutRatio"]<60 and row["CashVsDebt"]=="✅": return "🛡️ בטוח"
                return "✅ יציב"
            div_df["Safety"] = div_df.apply(_div_safe, axis=1)
            div_df["ExDateClean"] = div_df["ExDate"].apply(
                lambda x: pd.Timestamp(x,unit="s").strftime("%d/%m/%Y") if pd.notnull(x) else "—")
            cols_d = [c for c in ["Symbol","DivYield","DivRate","FiveYrDiv",
                                   "PayoutRatio","Safety","ExDateClean"] if c in div_df.columns]
            st.dataframe(
                div_df.sort_values("DivYield",ascending=False)[cols_d],
                column_config={
                    "DivYield":   st.column_config.NumberColumn("תשואה %",      format="%.2f%%", help="אחוז הדיבידנד השנתי ממחיר המניה. מעל 4% = גבוה"),
                    "DivRate":    st.column_config.NumberColumn("קצבה ($)",      format="$%.2f",  help="כמה דולר מקבלים לכל מניה בשנה"),
                    "FiveYrDiv":  st.column_config.NumberColumn("ממוצע 5 שנים", format="%.2f%%", help="ממוצע הדיבידנד ב-5 שנים — האם יציב?"),
                    "PayoutRatio":st.column_config.NumberColumn("שיעור חלוקה %",format="%.1f%%", help="כמה % מהרווח מחולק. מעל 80% = מסוכן!"),
                    "Safety":     st.column_config.TextColumn("בטיחות AI",       help="הערכת AI לאמינות הדיבידנד"),
                    "ExDateClean":st.column_config.TextColumn("תאריך אקס",      help="יום אחרון לזכאות לדיבידנד הבא. לפניו חייב להחזיק!"),
                },
                use_container_width=True, hide_index=True,
            )

# ══ 12–26 ═════════════════════════════════════════════════════════════════════
with tabs[12]: alerts_ai.render_smart_alerts(df_all)
with tabs[13]: simulator.render_value_agent(df_all)
with tabs[14]: simulator.render_day_trade_agent(df_all)
with tabs[15]: premium_agents_ai.render_premium_agents(df_all)
with tabs[16]: market_scanner.render_market_scanner()
with tabs[17]:
    if not df_all.empty: backtest_ai.render_backtester(df_all)
with tabs[18]:
    st.markdown(
        tooltip("ℹ️ ריבית הפד","FedRate") + " &nbsp; " +
        tooltip("ℹ️ אינפלציה","Inflation") + " &nbsp; " +
        tooltip("ℹ️ עקום תשואה","YieldCurve") + " &nbsp; " +
        tooltip("ℹ️ VIX","VIX"),
        unsafe_allow_html=True,
    )
    market_ai.render_market_intelligence()
with tabs[19]:
    if not df_all.empty: bull_bear.render_bull_bear(df_all)
with tabs[20]: news_ai.render_live_news(MY_STOCKS_BASE)
with tabs[21]: analytics_ai.render_analytics_dashboard()
with tabs[22]: telegram_ai.render_telegram_integration()
with tabs[23]: failsafes_ai.render_failsafes()
with tabs[24]:
    st.markdown(
        tooltip("ℹ️ למידת מכונה","ML") + " &nbsp; " +
        tooltip("ℹ️ Cross Validation","CV") + " &nbsp; " +
        tooltip("ℹ️ Isolation Forest","IsolationForest"),
        unsafe_allow_html=True,
    )
    ml_learning_ai.render_machine_learning(df_all)
with tabs[25]: realtime_data.render_full_realtime_panel(list(set(MY_STOCKS_BASE+SCAN_LIST)))
with tabs[26]: tax_fees_ai.render_tax_optimization()

# ══ 27: מדריך + מילון מושגים ════════════════════════════════════════════════════
with tabs[27]:
    st.markdown("""
    <div class="ai-card" style="border-right-color: #ff6b6b;">
    <b>🔄 ניהול סוכנים 24/7 - כלי למידה לסוחרים מתחילים</b>
    </div>
    """, unsafe_allow_html=True)
    
    scheduler = get_scheduler()
    status = scheduler.get_status()
    
    # ─── סטטוס ───────────────────────────────────────────────────────
    st.subheader("⚙️ סטטוס ממוד")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        running_text = "✅ פעיל" if status["running"] else "❌ לא פעיל"
        st.metric("Scheduler", running_text, delta="חוט daemon" if status["running"] else "")
    
    with col2:
        thread_text = "✅ רץ" if status["thread_alive"] else "⏸️ השהוי"
        st.metric("חוט עבודה", thread_text)
    
    with col3:
        last_run = status["last_runs"].get("val_agent", "טרם הופעל")
        if isinstance(last_run, str) and "T" in last_run:
            display_time = last_run.split("T")[1][:5]
        else:
            display_time = "אין"
        st.metric("ריצה אחרונה", display_time)
    
    st.divider()
    
    # ─── הפעלה ידנית ───────────────────────────────────────────────────
    st.subheader("▶️ הפעל סוכנים ידנית")
    st.write("💡 לחץ על כפתור כדי להפעיל סוכן עכשיו (בדרך כלל רץ אוטומטית)")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("▶️ סוכן ערך עכשיו", key="manual_val_agent", use_container_width=True):
            with st.spinner("⏳ סוכן ערך רץ... (טיפול בעמדות וחיסכון)"):
                scheduler.run_val_agent()
            st.success("✅ סוכן ערך סיים - בדוק את היומן למטה")
    
    with col_b:
        if st.button("▶️ סוכן יומי עכשיו", key="manual_day_agent", use_container_width=True):
            with st.spinner("⏳ סוכן יומי רץ... (סחר בתוך היום)"):
                scheduler.run_day_agent()
            st.success("✅ סוכן יומי סיים")
    
    with col_c:
        if st.button("▶️ ML אימון עכשיו", key="manual_ml", use_container_width=True):
            with st.spinner("⏳ ML מתאמן... (זה יכול לקחת דקות)"):
                scheduler.run_ml_training()
            st.success("✅ ML סיים - בדוק דיוק למטה")
    
    st.divider()
    
    # ─── יומן עסקאות אחרונות ───────────────────────────────────────────
    st.subheader("📋 עסקאות אחרונות (למידה)")
    
    col_val_trades, col_day_trades = st.columns(2)
    
    with col_val_trades:
        st.markdown("### 💼 סוכן ערך - עסקאות יומיות")
        val_trades = load("val_trades_log", [])
        if val_trades:
            st.write(f"**סה\"כ עסקאות: {len(val_trades)}**")
            for i, trade in enumerate(val_trades[:3]):  # הראה 3 אחרונות
                with st.expander(f"עסקה #{i+1}: {trade.get('📌', '?')} - {trade.get('↔️', '?')}", expanded=(i==0)):
                    st.write(f"⏰ **זמן:** {trade.get('⏰', 'N/A')[:16]}")
                    st.write(f"📌 **מניה:** {trade.get('📌', 'N/A')}")
                    st.write(f"💰 **מחיר:** {trade.get('💰', 'N/A')}")
                    st.write(f"💵 **סכום:** {trade.get('💵', 'N/A')}")
                    st.write(f"📊 **רווח/הפסד:** {trade.get('📊', 'N/A')}")
                    st.write(f"🎯 **סיבה:** {trade.get('🎯', 'N/A')}")
                    st.write(f"📚 **מה למדנו:** {trade.get('📚', 'N/A')}")
        else:
            st.info("אין עדיין עסקאות - לחץ על 'הפעל סוכן ערך'")
    
    with col_day_trades:
        st.markdown("### 📈 סוכן יומי - עסקאות היום")
        day_trades = load("day_trades_log", [])
        if day_trades:
            st.write(f"**סה\"כ עסקאות היום: {len(day_trades)}**")
            for i, trade in enumerate(day_trades[:3]):
                with st.expander(f"עסקה #{i+1}: {trade.get('📌', '?')}", expanded=(i==0)):
                    st.write(f"⏰ **זמן:** {trade.get('⏰', 'N/A')[:16]}")
                    st.write(f"📌 **מניה/כל:** {trade.get('📌', 'N/A')}")
                    st.write(f"📚 **למידה:** {trade.get('📚', 'N/A')}")
        else:
            st.info("אין עדיין עסקאות יומיות")
    
    st.divider()
    
    # ─── ML - מכונה למידה ───────────────────────────────────────────────
    st.subheader("🤖 Machine Learning - למידה עצמית")
    
    col_ml_left, col_ml_right = st.columns(2)
    
    with col_ml_left:
        st.markdown("### 📊 ביצועי המודל")
        ml_accuracy = load("ml_accuracy", 0.0)
        ml_runs = load("ml_runs", 0)
        
        st.metric("🎯 דיוק (Accuracy)", f"{ml_accuracy:.1%}")
        st.metric("🔄 ריצות סה\"כ", f"{ml_runs}")
        
        if ml_accuracy > 0:
            st.success(f"✅ המודל מנחש נכון {ml_accuracy:.0%} מהעת")
    
    with col_ml_right:
        st.markdown("### 📚 הסברים למתחילים")
        st.write("""
        **דיוק (Accuracy):**
        - אם 60% = המודל צודק 6 מתוך 10 פעמים
        - אם 75% = המודל צודק 7.5 מתוך 10 פעמים
        
        **ריצות:**
        - כל ריצה = למידה מחדש מנתונים חדשים
        - יותר ריצות = מודל חזק יותר
        - רץ אוטומטית כל 12 שעות
        """)
    
    st.divider()
    
    # ─── הסברים עמוקים ───────────────────────────────────────────────
    with st.expander("📖 הבנה עמוקה - איך זה עובד?", expanded=False):
        
        tab1, tab2, tab3 = st.tabs(["💼 סוכן ערך", "📈 סוכן יומי", "🤖 ML"])
        
        with tab1:
            st.markdown("""
            ### 💼 סוכן ערך (Value Agent) - קונה ומוכר אוטומטית
            
            **מה הסוכן עושה:**
            1. **בודק** את כל מניה בתיק שלך
            2. **מחשב** את הרווח או ההפסד באחוז
            3. **מוכר אוטומטית** אם קרו שני דברים:
               - ✅ **TAKE PROFIT (TP):** מניה עלתה 20% → מוכר (מנצח רווח)
               - ⛔ **STOP LOSS (SL):** מניה ירדה 8% → מוכר (מונע הפסד גדול)
            
            **למה זה טוב למתחילים:**
            - לא צריך לשמור על המסך כל הזמן
            - אוטומטי מבטל רווחים טובים
            - אוטומטי מונע הפסדים גדולים
            - רץ כל 6 שעות 24/7
            """)
        
        with tab2:
            st.markdown("""
            ### 📈 סוכן יומי (Day Agent) - סוחר בתוך כל יום
            
            **מה הסוכן עושה:**
            1. **בבוקר (8:00-9:00):** קונה כמה מניות בהימורים קטנים
            2. **בערב (15:00-16:00):** מוכר הכל
            3. **בלילה:** משאיר נקודות פתוחות = בטוח יותר
            
            **למה זה טוב למתחילים:**
            - תרגול סחר יומי בטוח
            - בלי סיכון לתוספות לילה (פער מחירים)
            - מתחיל מחדש כל יום
            - רץ כל שעה בשעות עבודה
            """)
        
        with tab3:
            st.markdown("""
            ### 🤖 Machine Learning - מכונה שמתאמנת
            
            **מה זה עושה:**
            1. **אוסף נתונים:** 2 שנים מ-6 מניות
            2. **בונה מאפיינים (Features):** RSI, MACD, Bollinger, Volume, וגם
            3. **מאמן מודל:** RandomForest (כמו עץ החלטות)
            4. **בודק עצמו:** 5-Fold Cross-Validation
            5. **מחזיר דיוק:** אחוז הנחשות הנכונות
            
            **למה זה חשוב:**
            - סוכנים צריכים לדעת **איזו מניה טובה**
            - ML למד את זה מנתונים היסטוריים
            - בעתיד: יוכל לעזור לסוכנים להחליט מה לקנות
            """)
    
    st.divider()
    
    # ─── כלים רישום ───────────────────────────────────────────────────
    st.subheader("📊 ערכים נוכחיים")
    
    col_debug1, col_debug2 = st.columns(2)
    
    with col_debug1:
        st.write("**סוכן ערך:**")
        val_cash = load("val_cash_ils", 5000.0)
        st.metric("💰 מזומנים", f"₪{val_cash:,.2f}")
    
    with col_debug2:
        st.write("**סוכן יומי:**")
        day_cash = load("day_cash_ils", 5000.0)
        st.metric("💰 מזומנים", f"₪{day_cash:,.2f}")
