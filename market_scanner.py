# market_scanner.py — סורק שוק אוטונומי עם עדכון אוטומטי לסוכנים
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# ─── יקומי מניות ─────────────────────────────────────────────────────────────
SP500_TOP = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","AVGO","LLY","V",
    "JPM","XOM","UNH","MA","JNJ","PG","HD","COST","ABBV","MRK",
    "CVX","ORCL","BAC","NFLX","KO","WMT","AMD","PEP","TMO","CSCO",
    "ACN","MCD","CRM","ABT","DHR","ADBE","NKE","TXN","LIN","MS",
    "PM","UNP","NEE","QCOM","RTX","AMGN","SPGI","BLK","GE","LOW",
    "INTU","CAT","ISRG","GS","BKNG","SYK","MDT","VRTX","REGN","NOW",
    "MMC","DE","PLD","GILD","AXP","LRCX","ADI","KLAC","SNPS","CDNS",
    "CME","EOG","SLB","FCX","HCA","CI","MCO","ZTS","ITW","USB",
    "TJX","AON","PNC","EMR","F","GM","DUK","SO","CL","EL",
    "BSX","HUM","MO","EW","DXCM","IDXX","BDX","ROK","CTAS","NSC",
]
NASDAQ_GROWTH = [
    "PLTR","CRWD","SNOW","DDOG","ZS","MDB","MELI","SHOP","CELH","TTD",
    "COIN","RBLX","U","RIVN","LCID","SMCI","ARM","ANET","PANW","FTNT",
    "OKTA","NET","CFLT","GTLB","HUBS","BILL","ASAN","DUOL",
    "ABNB","DASH","LYFT","UBER","PINS","SNAP","HOOD","SOFI","AFRM",
]
MID_SMALL_CAP = [
    "AXON","TMDX","APLS","INSM","RDNT","IRTC","PRVA","ACVA",
    "APPN","RELY","PSTG","PRCT","IONQ","QUBT","SOUN",
    "LUNR","RKLB","ASTS","ACHR","JOBY",
]
TASE_STOCKS = [
    "ENLT.TA","POLI.TA","LUMI.TA","TEVA.TA","ICL.TA",
    "NICE.TA","CHKP.TA","WIZE.TA","CEVA.TA",
    "MGDL.TA","SPNS.TA","FTAL.TA","ONE.TA","HLAN.TA",
]
DIVIDEND_KINGS = [
    "JNJ","PG","KO","MMM","T","VZ","IBM","XOM","CVX","PFE",
    "MO","PM","ABBV","BMY","MRK","AMGN","GILD",
    "O","STAG","NNN","WPC","MAIN","ARCC",
]
ALL_UNIVERSE = list(set(
    SP500_TOP + NASDAQ_GROWTH + MID_SMALL_CAP + TASE_STOCKS + DIVIDEND_KINGS
))

UNIVERSE_MAP = {
    "S&P500 Top 100":  SP500_TOP,
    "NASDAQ צמיחה":    NASDAQ_GROWTH + MID_SMALL_CAP,
    "כל השוק (מלא)":  ALL_UNIVERSE,
    'ת"א (TASE)':      TASE_STOCKS,
    "דיבידנדים":       DIVIDEND_KINGS,
}

# ─── מרווחי רענון אוטומטי (בדקות) ──────────────────────────────────────────
AUTO_INTERVALS = {
    "כל 30 דקות": 30,
    "כל שעה":     60,
    "כל 2 שעות":  120,
    "כל 4 שעות":  240,
    "ידני בלבד":   0,
}


# ─── סריקת מניה בודדת ────────────────────────────────────────────────────────
def _scan_single(ticker: str) -> dict | None:
    try:
        s   = yf.Ticker(ticker)
        inf = s.info
        h   = s.history(period="3mo")
        if h.empty or len(h) < 15:
            return None
        px = float(h["Close"].iloc[-1])
        if px <= 0:
            return None

        delta = h["Close"].diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean().replace(0, 1e-10)
        rsi   = float(100 - (100 / (1 + (gain / loss).iloc[-1])))

        chg1d = float(((px / h["Close"].iloc[-2]) - 1) * 100) if len(h) >= 2  else 0
        chg1m = float(((px / h["Close"].iloc[-22])- 1) * 100) if len(h) >= 22 else 0
        chg3m = float(((px / h["Close"].iloc[0])  - 1) * 100)

        rev_growth  = (inf.get("revenueGrowth")        or 0) * 100
        earn_growth = (inf.get("earningsGrowth")       or 0) * 100
        margin      = (inf.get("profitMargins")        or 0) * 100
        roe         = (inf.get("returnOnEquity")       or 0) * 100
        cash        =  inf.get("totalCash",  0)        or 0
        debt        =  inf.get("totalDebt",  0)        or 0
        div_yield   = (inf.get("dividendYield")        or 0) * 100
        payout      = (inf.get("payoutRatio")          or 0) * 100
        insider_pct = (inf.get("heldPercentInsiders")  or 0) * 100
        target_px   =  inf.get("targetMeanPrice", 0)  or 0
        upside      = float(((target_px / px) - 1) * 100) if px > 0 and target_px > 0 else 0
        volume      = int(h["Volume"].iloc[-1]) if not h["Volume"].empty else 0

        score = sum([
            rev_growth  >= 10,
            earn_growth >= 10,
            margin      >= 10,
            roe         >= 15,
            cash > debt,
            debt == 0,
        ])

        short_score = 0
        if rsi < 35:            short_score += 3
        elif rsi < 45:          short_score += 2
        if chg1m < -8:          short_score += 2
        elif chg1m < -4:        short_score += 1
        if upside > 15:         short_score += 2
        if rev_growth > 15:     short_score += 1
        if volume > 1_000_000:  short_score += 1

        long_score  = score
        long_score += 2 if rev_growth  >= 20 else (1 if rev_growth  >= 10 else 0)
        long_score += 2 if earn_growth >= 20 else (1 if earn_growth >= 10 else 0)
        long_score += 2 if upside > 20 else (1 if upside > 10 else 0)
        if div_yield > 2 and payout < 60 and cash > debt:
            long_score += 2
        if insider_pct >= 5:  long_score += 1
        if chg3m > 10:        long_score += 1

        currency = "אג'" if str(ticker).endswith(".TA") else "$"
        return {
            "Symbol":       ticker,
            "Price":        px,
            "PriceStr":     f"{currency}{px:,.2f}",
            "Currency":     currency,
            "RSI":          round(rsi, 1),
            "Chg1D":        round(chg1d, 2),
            "Chg1M":        round(chg1m, 2),
            "Chg3M":        round(chg3m, 2),
            "Score":        score,
            "ShortScore":   short_score,
            "LongScore":    long_score,
            "RevGrowth":    round(rev_growth, 1),
            "EarnGrowth":   round(earn_growth, 1),
            "Margin":       round(margin, 1),
            "ROE":          round(roe, 1),
            "DivYield":     round(div_yield, 2),
            "PayoutRatio":  round(payout, 1),
            "InsiderHeld":  round(insider_pct, 1),
            "TargetUpside": round(upside, 1),
            "CashVsDebt":   "✅" if cash > debt else "❌",
            "Volume":       volume,
            "Action": (
                "קנייה חזקה 💎" if long_score >= 10 else
                "קנייה 📈"      if long_score >= 7  else
                "החזק ⚖️"       if long_score >= 4  else
                "בבדיקה 🔍"
            ),
        }
    except Exception:
        return None


# ─── סריקה מקבילית (ללא cache — כי אנחנו מנהלים את ה-TTL ידנית) ─────────────
def _run_scan_raw(universe: list, progress_placeholder) -> pd.DataFrame:
    """סורק במקביל ומחזיר DataFrame. progress_placeholder = st.empty()"""
    results, total, done = [], len(universe), 0
    prog = progress_placeholder.progress(0, text="🔍 מתחיל סריקה...")
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(_scan_single, t): t for t in universe}
        for fut in as_completed(futures):
            done += 1
            prog.progress(done / total, text=f"🔍 סורק {done}/{total} מניות...")
            res = fut.result()
            if res:
                results.append(res)
    progress_placeholder.empty()
    if not results:
        return pd.DataFrame()
    return pd.DataFrame(results).sort_values("LongScore", ascending=False).reset_index(drop=True)


# ─── עדכון אוטומטי לסוכנים ───────────────────────────────────────────────────
def _push_to_agents(df: pd.DataFrame, mode: str):
    """מעדכן את session_state של הסוכנים לפי מצב הסריקה."""
    if df.empty:
        return
    if mode == "ארוך":
        st.session_state["agent_universe_df"]       = df.sort_values("LongScore",  ascending=False).head(40)
        st.session_state["agent_universe_short_df"] = df.sort_values("ShortScore", ascending=False).head(20)
    elif mode == "קצר":
        st.session_state["agent_universe_df"]       = df.sort_values("LongScore",  ascending=False).head(20)
        st.session_state["agent_universe_short_df"] = df.sort_values("ShortScore", ascending=False).head(40)
    else:  # שניהם
        st.session_state["agent_universe_df"]       = df.sort_values("LongScore",  ascending=False).head(40)
        st.session_state["agent_universe_short_df"] = df.sort_values("ShortScore", ascending=False).head(40)
    st.session_state["last_auto_push"] = datetime.now().strftime("%d/%m %H:%M:%S")


def _should_auto_scan() -> bool:
    """בודק אם הגיע הזמן לסריקה אוטומטית חדשה."""
    interval_min = st.session_state.get("auto_scan_interval", 0)
    if interval_min == 0:
        return False
    last = st.session_state.get("last_scan_dt")
    if last is None:
        return True
    return datetime.now() >= last + timedelta(minutes=interval_min)


def maybe_auto_scan():
    """
    קוראים לפונקציה זו מתוך app.py בכל טעינה.
    אם הגיע הזמן — מריץ סריקה ברקע ומעדכן את הסוכנים.
    """
    if not _should_auto_scan():
        return
    universe_name = st.session_state.get("auto_scan_universe", "S&P500 Top 100")
    universe      = UNIVERSE_MAP.get(universe_name, SP500_TOP)
    mode          = st.session_state.get("auto_scan_mode", "שניהם")

    placeholder = st.empty()
    with placeholder.container():
        st.info(f"🔄 **סריקה אוטומטית פעילה** — {universe_name} ({len(universe)} מניות)...")
        prog_ph = st.empty()
        df = _run_scan_raw(universe, prog_ph)

    placeholder.empty()

    if not df.empty:
        st.session_state["scan_results"] = df
        st.session_state["last_scan_dt"]  = datetime.now()
        st.session_state["scan_time"]     = datetime.now().strftime("%H:%M:%S")
        _push_to_agents(df, mode)
        # הצג הודעת הצלחה קצרה
        n_long  = len(st.session_state.get("agent_universe_df", []))
        n_short = len(st.session_state.get("agent_universe_short_df", []))
        st.toast(f"✅ סריקה הושלמה — {n_long} מניות לסוכן ערך | {n_short} לסוכן יומי", icon="🤖")


# ─── UI: טאב סורק שוק ────────────────────────────────────────────────────────
def render_market_scanner():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #7c4dff;">'
        '<b>🌐 סורק שוק אוטונומי:</b> סורק מאות מניות ומעדכן את הסוכנים אוטומטית.</div>',
        unsafe_allow_html=True,
    )

    # ══════════════════════════════════════════════════════
    # בלוק 1: הגדרות סריקה אוטומטית
    # ══════════════════════════════════════════════════════
    st.markdown("### ⚙️ הגדרות סריקה אוטומטית")

    cfg1, cfg2, cfg3, cfg4 = st.columns(4)
    with cfg1:
        auto_interval_label = st.selectbox(
            "🔄 רענון אוטומטי",
            list(AUTO_INTERVALS.keys()),
            index=1,          # ברירת מחדל: כל שעה
            key="auto_interval_select",
        )
        interval_min = AUTO_INTERVALS[auto_interval_label]
        st.session_state["auto_scan_interval"] = interval_min

    with cfg2:
        auto_universe = st.selectbox(
            "🌍 יקום לסריקה אוטומטית",
            list(UNIVERSE_MAP.keys()),
            key="auto_universe_select",
        )
        st.session_state["auto_scan_universe"] = auto_universe

    with cfg3:
        auto_mode = st.selectbox(
            "🎯 עדיפות לסוכנים",
            ["שניהם", "ארוך", "קצר"],
            key="auto_mode_select",
        )
        st.session_state["auto_scan_mode"] = auto_mode

    with cfg4:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        auto_on = st.toggle(
            "🟢 סריקה אוטומטית",
            value=st.session_state.get("auto_scan_interval", 60) > 0,
            key="auto_scan_toggle",
        )
        if not auto_on:
            st.session_state["auto_scan_interval"] = 0

    # סטטוס
    last_dt  = st.session_state.get("last_scan_dt")
    last_push= st.session_state.get("last_auto_push", "—")
    n_agents = len(st.session_state.get("agent_universe_df", pd.DataFrame()))

    if auto_on and interval_min > 0:
        next_scan = (last_dt + timedelta(minutes=interval_min)).strftime("%H:%M") if last_dt else "בקרוב"
        st.success(
            f"🟢 **סריקה אוטומטית פעילה** | "
            f"כל {interval_min} דקות | "
            f"עדכון אחרון: {last_push} | "
            f"סוכנים מקבלים: **{n_agents} מניות** | "
            f"סריקה הבאה: {next_scan}"
        )
    else:
        st.warning("🟡 סריקה אוטומטית **כבויה** — הסוכנים עובדים עם ה-Watchlist בלבד.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # בלוק 2: סריקה ידנית + הגדרות תצוגה
    # ══════════════════════════════════════════════════════
    st.markdown("### 🔍 סריקה ידנית")

    man1, man2, man3 = st.columns(3)
    with man1:
        manual_universe = st.selectbox(
            "🌍 יקום לסריקה ידנית",
            list(UNIVERSE_MAP.keys()),
            key="scanner_universe",
        )
    with man2:
        horizon = st.selectbox(
            "⏱️ אופק תצוגה",
            ["שניהם", "טווח קצר (ימים-שבועות)", "טווח ארוך (חודשים-שנים)"],
            key="scanner_horizon",
        )
    with man3:
        top_n = st.slider("📊 מניות להציג", 5, 50, 20, key="scanner_topn")

    btn1, btn2 = st.columns([1, 3])
    with btn1:
        run_now = st.button("🚀 סרוק עכשיו", type="primary", key="scanner_run")
    with btn2:
        if st.button("📤 שלח ממצאים לכל הסוכנים", key="send_to_all", type="secondary"):
            if "scan_results" in st.session_state:
                _push_to_agents(st.session_state["scan_results"], auto_mode)
                st.success(f"✅ סוכנים עודכנו! ({n_agents} מניות)")
            else:
                st.warning("הפעל סריקה תחילה.")

    if run_now:
        prog_ph = st.empty()
        df = _run_scan_raw(UNIVERSE_MAP[manual_universe], prog_ph)
        if df.empty:
            st.error("לא ניתן לשאוב נתונים כרגע.")
        else:
            st.session_state["scan_results"]  = df
            st.session_state["last_scan_dt"]  = datetime.now()
            st.session_state["scan_time"]     = datetime.now().strftime("%H:%M:%S")
            _push_to_agents(df, auto_mode)
            st.success(f"✅ נסרקו {len(df)} מניות | הסוכנים עודכנו אוטומטית!")

    # ══════════════════════════════════════════════════════
    # בלוק 3: תוצאות
    # ══════════════════════════════════════════════════════
    if "scan_results" not in st.session_state:
        st.info("👆 לחץ 'סרוק עכשיו' או הפעל סריקה אוטומטית.")
        return

    df = st.session_state["scan_results"]
    scan_time = st.session_state.get("scan_time", "—")

    st.divider()
    # כרטיסי סיכום
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("📋 נסרקו",         len(df))
    s2.metric("💎 הזדמנויות ארוך", len(df[df["LongScore"]  >= 8]))
    s3.metric("⚡ הזדמנויות קצר",  len(df[df["ShortScore"] >= 5]))
    s4.metric("⭐ ציון PDF 5+",    len(df[df["Score"]      >= 5]))
    s5.metric("🕒 עדכון אחרון",    scan_time)

    # תצוגת טבלאות
    if horizon in ["שניהם", "טווח קצר (ימים-שבועות)"]:
        st.markdown("### ⚡ TOP — טווח קצר (מומנטום + RSI נמוך)")
        _show_scan_table(df.sort_values("ShortScore", ascending=False).head(top_n))

    if horizon in ["שניהם", "טווח ארוך (חודשים-שנים)"]:
        st.markdown("### 💎 TOP — טווח ארוך (יסודות + צמיחה)")
        _show_scan_table(df.sort_values("LongScore", ascending=False).head(top_n))

    # מה הסוכנים מקבלים
    st.divider()
    st.markdown("### 🤖 מה הסוכנים מקבלים כרגע")
    ag1, ag2 = st.columns(2)
    with ag1:
        long_df = st.session_state.get("agent_universe_df")
        if long_df is not None and not long_df.empty:
            st.success(f"**💼 סוכן ערך + פרימיום:** {len(long_df)} מניות")
            st.dataframe(
                long_df[["Symbol","LongScore","Score","RevGrowth","TargetUpside","Action"]].head(10),
                use_container_width=True, hide_index=True,
            )
        else:
            st.warning("סוכן ערך: עובד עם Watchlist")
    with ag2:
        short_df = st.session_state.get("agent_universe_short_df")
        if short_df is not None and not short_df.empty:
            st.success(f"**⚡ סוכן יומי:** {short_df.shape[0]} מניות")
            st.dataframe(
                short_df[["Symbol","ShortScore","RSI","Chg1M","TargetUpside"]].head(10),
                use_container_width=True, hide_index=True,
            )
        else:
            st.warning("סוכן יומי: עובד עם Watchlist")


def _show_scan_table(df: pd.DataFrame):
    if df.empty:
        st.info("אין תוצאות.")
        return
    cols = ["Symbol","PriceStr","ShortScore","LongScore","Score","RSI",
            "Chg1D","Chg1M","RevGrowth","EarnGrowth","DivYield","TargetUpside","Action"]
    show = [c for c in cols if c in df.columns]
    st.dataframe(
        df[show].rename(columns={
            "Symbol":"סימול","PriceStr":"מחיר","ShortScore":"⚡ קצר",
            "LongScore":"💎 ארוך","Score":"⭐ PDF","RSI":"RSI",
            "Chg1D":"יום %","Chg1M":"חודש %","RevGrowth":"מכירות %",
            "EarnGrowth":"רווחים %","DivYield":"דיב %",
            "TargetUpside":"אפסייד %","Action":"המלצה",
        }),
        column_config={
            "⚡ קצר":    st.column_config.NumberColumn(format="%d"),
            "💎 ארוך":   st.column_config.NumberColumn(format="%d"),
            "⭐ PDF":     st.column_config.NumberColumn(format="%d"),
            "RSI":        st.column_config.NumberColumn(format="%.1f"),
            "יום %":      st.column_config.NumberColumn(format="%.2f%%"),
            "חודש %":     st.column_config.NumberColumn(format="%.2f%%"),
            "מכירות %":   st.column_config.NumberColumn(format="%.1f%%"),
            "רווחים %":   st.column_config.NumberColumn(format="%.1f%%"),
            "דיב %":      st.column_config.NumberColumn(format="%.2f%%"),
            "אפסייד %":   st.column_config.NumberColumn(format="%.1f%%"),
        },
        use_container_width=True, hide_index=True,
    )
