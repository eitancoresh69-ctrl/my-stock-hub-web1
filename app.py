# app.py — Investment Hub Elite 2026 — גרסה סופית מלאה
# ══════════════════════════════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

from config import (HELP, MY_STOCKS_BASE, SCAN_LIST,
                    COMMODITIES_SYMBOLS, CRYPTO_SYMBOLS, TASE_SCAN)
from logic   import fetch_master_data
from storage import load_all_to_session, save, load

# ─── ייבוא מודולים ────────────────────────────────────────────────────────────
import realtime_data, market_ai, bull_bear, simulator
import podcasts_ai, alerts_ai, financials_ai, crypto_ai
import news_ai, telegram_ai, analytics_ai, pro_tools_ai
import premium_agents_ai, growth_risk_ai, backtest_ai
import execution_ai, failsafes_ai, ml_learning_ai
import social_sentiment_ai, tax_fees_ai, market_scanner
import ai_portfolio, commodities_tab, pattern_ai, portfolio_optimizer

# ─── הגדרות עמוד ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Investment Hub Elite 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── טעינה מדיסק (פעם אחת בכל הפעלה) ────────────────────────────────────────
load_all_to_session(st.session_state)
try:
    from storage import load_ai_portfolio
    load_ai_portfolio(st.session_state)
except Exception:
    pass

# ─── עיצוב RTL מתקדם ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Heebo', sans-serif;
    direction: rtl;
    text-align: right;
}
.stApp { background: linear-gradient(160deg, #0f1629 0%, #1a2340 40%, #0d1b2a 100%); }
.block-container { padding-top: 0.5rem !important; max-width: 100% !important; }

/* כרטיסי AI */
.ai-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 14px 18px; border-radius: 14px;
    border-right: 5px solid #1a73e8;
    margin-bottom: 12px;
    color: #e8eaf6;
}

/* כותרת ראשית */
.hub-header {
    background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #0d47a1 100%);
    border-radius: 16px; padding: 18px 24px; margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

/* metric cards */
.metric-row > div {
    background: rgba(255,255,255,0.07);
    border-radius: 10px; padding: 8px 12px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* טאבים */
div[data-testid="stTabs"] button {
    font-weight: 700; font-size: 11px;
    color: #90caf9 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #fff !important;
    border-bottom: 3px solid #42a5f5 !important;
}

/* טבלאות */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th {
    padding: 5px 10px !important;
    font-size: 13px !important;
    color: #e8eaf6 !important;
}
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 8px;
}

/* טקסט כללי */
p, span, label, div { color: #cfd8dc; }
h1,h2,h3,h4 { color: #e8eaf6 !important; }
.stMarkdown { color: #cfd8dc; }

/* כפתורים */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'Heebo', sans-serif !important;
}

/* metric */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border-radius: 10px; padding: 8px 12px;
    border: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stMetricLabel"] { color: #90caf9 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #e8eaf6 !important; font-size: 22px !important; }
[data-testid="stMetricDelta"] { font-size: 13px !important; }

/* expander */
.streamlit-expanderHeader { color: #90caf9 !important; font-weight: 700; }

/* success/warning/error */
.stSuccess { background: rgba(46,125,50,0.2) !important; border: 1px solid #2e7d32 !important; color: #a5d6a7 !important; border-radius: 8px; }
.stWarning { background: rgba(230,115,0,0.2) !important; border: 1px solid #e65100 !important; color: #ffcc80 !important; border-radius: 8px; }
.stError   { background: rgba(198,40,40,0.2) !important; border: 1px solid #c62828 !important; color: #ef9a9a !important; border-radius: 8px; }
.stInfo    { background: rgba(21,101,192,0.2) !important; border: 1px solid #1565c0 !important; color: #90caf9 !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── שליפת נתונים ─────────────────────────────────────────────────────────────
ALL_TICKERS = list(set(MY_STOCKS_BASE + SCAN_LIST + TASE_SCAN))
try:
    with st.spinner("☁️ שואב נתוני שוק — מניות · סחורות · ת\"א · קריפטו..."):
        df_all = fetch_master_data(ALL_TICKERS)
except Exception:
    st.error("⚠️ שגיאה זמנית בטעינה. מציג נתונים חלקיים.")
    df_all = pd.DataFrame()

# ─── כותרת ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hub-header">
    <div style="display:flex;align-items:center;gap:14px;">
        <div style="font-size:38px;">🌐</div>
        <div>
            <div style="font-size:22px;font-weight:900;color:#fff;letter-spacing:-0.5px;">
                Investment Hub Elite 2026
            </div>
            <div style="font-size:13px;color:#90caf9;margin-top:2px;">
                מניות · סחורות · קריפטו · תל אביב · AI Manager · ML · Telegram
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("kill_switch_active"):
    st.error("🚨 **מתג ההשמדה פעיל!** גש לטאב '🛡️ הגנה' לאיפוס.")

# ─── מדדים עליונים ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _top_metrics():
    try: vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
    except: vix = 0.0
    try: ta35 = yf.Ticker("^TA35.TA").history(period="1d")["Close"].iloc[-1]
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
c1.metric("📊 VIX",             f"{vix:.1f}",
          delta="גבוה" if vix>25 else "תקין", delta_color="inverse")
c2.metric("🇮🇱 TA-35",          f"{ta35:,.0f}")
c3.metric("🇺🇸 S&P 500",        f"{spy_chg:+.2f}%",
          delta_color="normal" if spy_chg>=0 else "inverse")
c4.metric("₿ Bitcoin",          f"{btc_chg:+.2f}%",
          delta_color="normal" if btc_chg>=0 else "inverse")
c5.metric("💎 מניות זהב",       len(df_all[df_all["Score"]>=5]) if not df_all.empty else 0)
c6.metric("🕒 עדכון",           datetime.now().strftime("%H:%M"))
c7.metric("🛡️ מצב",            "🔴 KILL" if st.session_state.get("kill_switch_active") else "🟢 OK")

# ─── Fear & Greed + מחירים חיים ───────────────────────────────────────────────
with st.expander("📡 Fear & Greed Index + מחירים חיים", expanded=True):
    fg_col, px_col = st.columns([1,2])
    with fg_col:
        realtime_data.render_fear_greed_widget()
    with px_col:
        realtime_data.render_live_prices_strip(MY_STOCKS_BASE[:6] + SCAN_LIST[:4])

# ─── Badge תיק AI + סוכנים ────────────────────────────────────────────────────
aip_on  = st.session_state.get("aip_enabled", False)
aip_cash= st.session_state.get("aip_cash", 0)
aip_pos = len(st.session_state.get("aip_positions", []))
if aip_on:
    st.markdown(
        f'<div style="background:rgba(46,125,50,0.2);border:1px solid #2e7d32;'
        f'border-radius:8px;padding:8px 16px;margin:6px 0;color:#a5d6a7;font-weight:700;">'
        f'🤖 תיק AI פעיל | מזומן: ₪{aip_cash:,.0f} | פוזיציות: {aip_pos}</div>',
        unsafe_allow_html=True,
    )

market_scanner.maybe_auto_scan()

n_long  = len(st.session_state.get("agent_universe_df",      pd.DataFrame()))
n_short = len(st.session_state.get("agent_universe_short_df",pd.DataFrame()))
if n_long>0 or n_short>0:
    st.info(f"🤖 סוכן ערך ← {n_long} | סוכן יומי ← {n_short} | עדכון: {st.session_state.get('last_auto_push','—')}")

# ═══════════════════════════════════════════════════════════════════════════════
# ═══ טאבים ════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📌 התיק",           # 0
    "🤖 AI מנהל",        # 1
    "📐 אופטימיזציה",    # 2
    "🏅 סחורות",         # 3
    "₿ קריפטו",          # 4
    "🇮🇱 תל אביב",       # 5
    "🔍 סורק PDF",       # 6
    "🔬 דפוסי Chart",    # 7
    "🚀 צמיחה",          # 8
    "💼 רנטגן",          # 9
    "📚 דוחות",          # 10
    "💰 דיבידנדים",      # 11
    "🔔 התראות",         # 12
    "📈 סוכן ערך",       # 13
    "⚡ סוכן יומי",      # 14
    "🤖 פרימיום",        # 15
    "🌐 סורק שוק",       # 16
    "⏪ בק-טסט",         # 17
    "🌍 מאקרו",          # 18
    "⚖️ שור/דוב",        # 19
    "📰 חדשות",          # 20
    "📊 אנליטיקה",       # 21
    "📱 טלגרם",          # 22
    "🛡️ הגנה",           # 23
    "🧠 ML",             # 24
    "📡 נתונים חיים",    # 25
    "💸 מיסים",          # 26
])

# ══ 0: התיק האישי ══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="ai-card"><b>📌 התיק שלי</b> — לחץ פעמיים לעדכון</div>',
                unsafe_allow_html=True)

    # הוסף נכס
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
                    new = pd.DataFrame([{"Symbol":ns,"BuyPrice":nb,"Qty":nq}])
                    st.session_state.portfolio = pd.concat([port,new],ignore_index=True)
                    save("portfolio_buy_prices",dict(zip(st.session_state.portfolio["Symbol"],
                                                         st.session_state.portfolio["BuyPrice"])))
                    save("portfolio_quantities", dict(zip(st.session_state.portfolio["Symbol"],
                                                          st.session_state.portfolio["Qty"])))
                    st.success(f"✅ {ns} נוסף!"); st.rerun()

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
            lambda r: r.get("PriceStr","") or f"${r['Price']:.2f}", axis=1)
        merged["PL"]  = (merged["Price"]-merged["BuyPrice"])*merged["Qty"]
        merged["Yield"] = merged.apply(
            lambda r: ((r["Price"]/r["BuyPrice"])-1)*100 if r["BuyPrice"]>0 else 0, axis=1)
        merged["Emoji"] = merged["Symbol"].apply(
            lambda s: "🥇" if "GC" in s else "🛢️" if any(x in s for x in ["CL","BZ","NG"]) else
                      "₿" if "BTC" in s else "Ξ" if "ETH" in s else
                      "🇮🇱" if s.endswith(".TA") else "📈")

        score_col = merged["Score"] if "Score" in merged.columns else pd.Series([0]*len(merged))
        action_col= merged["Action"] if "Action" in merged.columns else pd.Series(["—"]*len(merged))
        disp = merged[["Symbol","Emoji","PriceStr","BuyPrice","Qty","PL","Yield"]].copy()
        disp["Score"]  = score_col.values
        disp["Action"] = action_col.values

        edited = st.data_editor(
            disp,
            column_config={
                "Symbol":   st.column_config.TextColumn("סימול", disabled=True),
                "Emoji":    st.column_config.TextColumn("סוג",   disabled=True),
                "PriceStr": st.column_config.TextColumn("מחיר חי", disabled=True),
                "BuyPrice": st.column_config.NumberColumn("קנייה ✏️"),
                "Qty":      st.column_config.NumberColumn("כמות ✏️"),
                "PL":       st.column_config.NumberColumn("P/L ₪", format="%.2f", disabled=True),
                "Yield":    st.column_config.NumberColumn("תשואה %", format="%.1f%%", disabled=True),
                "Score":    st.column_config.NumberColumn("⭐",     disabled=True),
                "Action":   st.column_config.TextColumn("המלצה",   disabled=True),
            },
            use_container_width=True, hide_index=True,
        )
        st.session_state.portfolio = edited[["Symbol","BuyPrice","Qty"]]
        save("portfolio_buy_prices", dict(zip(edited["Symbol"], edited["BuyPrice"])))
        save("portfolio_quantities",  dict(zip(edited["Symbol"], edited["Qty"])))

        active = merged[merged["Qty"]>0].copy()
        if not active.empty:
            active["PL"] = (active["Price"]-active["BuyPrice"])*active["Qty"]
            total_pl  = active["PL"].sum()
            total_val = (active["Price"]*active["Qty"]).sum()
            st.divider()
            s1,s2,s3,s4 = st.columns(4)
            s1.metric("📊 נכסים פעילים", len(active))
            s2.metric("💼 שווי תיק",     f"${total_val:,.0f}")
            s3.metric("📈 רווח/הפסד",   f"{'🟢 +' if total_pl>=0 else '🔴 '}${abs(total_pl):,.0f}")
            s4.metric("⭐ ציון ממוצע",  f"{active['Score'].mean():.1f}/6" if "Score" in active else "—")

# ══ 1: תיק AI מנוהל ════════════════════════════════════════════════════════════
with tabs[1]:
    ai_portfolio.render_ai_portfolio(df_all)

# ══ 2: אופטימיזציית תיק ════════════════════════════════════════════════════════
with tabs[2]:
    portfolio_df = st.session_state.get("portfolio")
    portfolio_optimizer.render_portfolio_optimizer(portfolio_df)

# ══ 3: סחורות ══════════════════════════════════════════════════════════════════
with tabs[3]:
    commodities_tab.render_commodities()

# ══ 4: קריפטו ══════════════════════════════════════════════════════════════════
with tabs[4]:
    crypto_ai.render_crypto_arena()

# ══ 5: תל אביב ═════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown(
        '<div class="ai-card" style="border-right-color:#0052cc;">'
        '<b>🇮🇱 בורסת תל אביב — TASE</b><br>'
        '<small>מניות תל אביב 35, דיבידנדים ישראלים, בנקים וחברות ענן</small></div>',
        unsafe_allow_html=True,
    )
    if not df_all.empty:
        tase_df = df_all[df_all["AssetType"]=="tase"].copy() if "AssetType" in df_all.columns else df_all[df_all["Symbol"].str.endswith(".TA")].copy()
        if not tase_df.empty:
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("📋 מניות ת\"א", len(tase_df))
            c2.metric("🏆 ציון ≥4", len(tase_df[tase_df["Score"]>=4]))
            c3.metric("🟢 עולים היום", len(tase_df[tase_df["Change"]>0]))
            c4.metric("💰 דיבידנד ממוצע", f"{tase_df['DivYield'].mean():.1f}%")

            cols_show = [c for c in ["Symbol","PriceStr","Change","Score","RSI","DivYield","Action","AI_Logic"] if c in tase_df.columns]
            st.dataframe(
                tase_df[cols_show].sort_values("Score",ascending=False),
                column_config={
                    "Symbol":"סימול","PriceStr":"מחיר (אג')",
                    "Change": st.column_config.NumberColumn("שינוי %",format="%.2f%%"),
                    "Score":  st.column_config.NumberColumn("⭐ ציון"),
                    "RSI":    st.column_config.NumberColumn("RSI",format="%.0f"),
                    "DivYield":st.column_config.NumberColumn("דיבידנד %",format="%.2f%%"),
                    "Action":"המלצה","AI_Logic":"לוגיקה",
                },
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("הוסף מניות .TA לרשימה ב-config.py")

# ══ 6: סורק PDF ════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="ai-card"><b>🔍 סורק PDF</b> — מניות עם ציון ≥ 4 מרשימת הסריקה</div>',
                unsafe_allow_html=True)
    if not df_all.empty:
        is_stock = df_all["Symbol"].isin(SCAN_LIST+TASE_SCAN)
        if "AssetType" in df_all.columns:
            is_stock = df_all["AssetType"].isin(["stock","tase"])
        scanner = df_all[is_stock & (df_all["Score"]>=4)].sort_values("Score",ascending=False)
        if not scanner.empty:
            cols_s = [c for c in ["Symbol","PriceStr","Score","RevGrowth","EarnGrowth","Margin","RSI","Action","AI_Logic"] if c in scanner.columns]
            st.dataframe(scanner[cols_s], use_container_width=True, hide_index=True)
        else:
            st.info("לא נמצאו מניות ציון 4+ ברשימת הסריקה.")

# ══ 7: דפוסי Chart + Regime ════════════════════════════════════════════════════
with tabs[7]:
    pattern_ai.render_pattern_analysis(df_all)

# ══ 8–11: כלים בסיסיים ════════════════════════════════════════════════════════
with tabs[8]:  growth_risk_ai.render_growth_and_risk(df_all)

with tabs[9]:
    if "portfolio" in st.session_state and not df_all.empty:
        pro_tools_ai.render_pro_tools(df_all, st.session_state.portfolio)
    else:
        st.info("הוסף מניות לתיק קודם.")

with tabs[10]:
    if not df_all.empty: financials_ai.render_financial_reports(df_all)

with tabs[11]:
    st.markdown('<div class="ai-card"><b>💰 ניתוח דיבידנדים</b></div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all["DivYield"]>0].copy()
        if not div_df.empty:
            def _div_safe(row):
                if row["PayoutRatio"]<=0: return "לא ידוע"
                if row["PayoutRatio"]>80: return "⚠️ סכנת קיצוץ"
                if row["PayoutRatio"]<60 and row["CashVsDebt"]=="✅": return "🛡️ בטוח"
                return "✅ יציב"
            div_df["Safety"] = div_df.apply(_div_safe,axis=1)
            div_df["ExDateClean"] = div_df["ExDate"].apply(
                lambda x: pd.Timestamp(x,unit="s").strftime("%d/%m/%Y") if pd.notnull(x) else "—")
            cols_d = [c for c in ["Symbol","DivYield","DivRate","FiveYrDiv","PayoutRatio","Safety","ExDateClean"] if c in div_df.columns]
            st.dataframe(div_df.sort_values("DivYield",ascending=False)[cols_d],
                         use_container_width=True, hide_index=True)

# ══ 12: התראות ═════════════════════════════════════════════════════════════════
with tabs[12]: alerts_ai.render_smart_alerts(df_all)

# ══ 13–16: סוכנים ══════════════════════════════════════════════════════════════
with tabs[13]: simulator.render_value_agent(df_all)
with tabs[14]: simulator.render_day_trade_agent(df_all)
with tabs[15]: premium_agents_ai.render_premium_agents(df_all)
with tabs[16]: market_scanner.render_market_scanner()

# ══ 17–21: כלים מתקדמים ════════════════════════════════════════════════════════
with tabs[17]:
    if not df_all.empty: backtest_ai.render_backtester(df_all)

with tabs[18]: market_ai.render_market_intelligence()

with tabs[19]:
    if not df_all.empty: bull_bear.render_bull_bear(df_all)

with tabs[20]: news_ai.render_live_news(MY_STOCKS_BASE)
with tabs[21]: analytics_ai.render_analytics_dashboard()

# ══ 22: טלגרם ══════════════════════════════════════════════════════════════════
with tabs[22]: telegram_ai.render_telegram_integration()

# ══ 23–26: מערכת ═══════════════════════════════════════════════════════════════
with tabs[23]: failsafes_ai.render_failsafes()
with tabs[24]: ml_learning_ai.render_machine_learning(df_all)
with tabs[25]: realtime_data.render_full_realtime_panel(list(set(MY_STOCKS_BASE+SCAN_LIST)))
with tabs[26]: tax_fees_ai.render_tax_optimization()
