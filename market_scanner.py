# market_scanner.py — סורק שוק אוטונומי | S&P500 + NASDAQ100 + TASE + Mid-Cap
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ─── רשימות מניות מקיפות ───────────────────────────────────────────────────
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
    "OKTA","NET","CFLT","GTLB","HUBS","BILL","ASAN","SAMSARA","DUOL",
    "ABNB","DASH","LYFT","UBER","PINS","SNAP","HOOD","SOFI","AFRM",
]

MID_SMALL_CAP = [
    "AXON","TMDX","APLS","INSM","RDNT","IRTC","PRVA","ACVA",
    "APPN","RELY","PSTG","PCVX","PRCT","IONQ","QUBT","SOUN",
    "LUNR","RKLB","ASTS","ACHR","JOBY","LILM",
]

TASE_STOCKS = [
    "ENLT.TA","POLI.TA","LUMI.TA","TEVA.TA","ICL.TA",
    "NICE.TA","CHKP.TA","AMDOCS.TA","WIZE.TA","CEVA.TA",
    "MGDL.TA","SPNS.TA","FTAL.TA","ONE.TA","HLAN.TA",
]

DIVIDEND_KINGS = [
    "JNJ","PG","KO","MMM","T","VZ","IBM","XOM","CVX","PFE",
    "MO","PM","BTI","ABBV","BMY","MRK","AMGN","GILD",
    "O","STAG","NNN","EPR","WPC","MAIN","ARCC","GLAD",
]

ALL_UNIVERSE = list(set(
    SP500_TOP + NASDAQ_GROWTH + MID_SMALL_CAP + TASE_STOCKS + DIVIDEND_KINGS
))


# ─── שליפת מניה בודדת לסריקה מהירה ────────────────────────────────────────
def _scan_single(ticker: str) -> dict | None:
    """שולף נתוני מניה בודדת מהירים לסריקה."""
    try:
        s   = yf.Ticker(ticker)
        inf = s.info
        h   = s.history(period="3mo")

        if h.empty or len(h) < 15:
            return None

        px = float(h["Close"].iloc[-1])
        if px <= 0:
            return None

        # RSI
        delta = h["Close"].diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean().replace(0, 1e-10)
        rsi   = float(100 - (100 / (1 + (gain / loss).iloc[-1])))

        # תנודה ומומנטום
        chg1d = float(((px / h["Close"].iloc[-2]) - 1) * 100) if len(h) >= 2 else 0
        chg1m = float(((px / h["Close"].iloc[-22]) - 1) * 100) if len(h) >= 22 else 0
        chg3m = float(((px / h["Close"].iloc[0])  - 1) * 100)

        # מדדי איכות
        rev_growth  = (inf.get("revenueGrowth")  or 0) * 100
        earn_growth = (inf.get("earningsGrowth") or 0) * 100
        margin      = (inf.get("profitMargins")  or 0) * 100
        roe         = (inf.get("returnOnEquity") or 0) * 100
        cash        = inf.get("totalCash",  0) or 0
        debt        = inf.get("totalDebt",  0) or 0
        div_yield   = (inf.get("dividendYield")  or 0) * 100
        payout      = (inf.get("payoutRatio")    or 0) * 100
        insider_pct = (inf.get("heldPercentInsiders") or 0) * 100
        target_px   = inf.get("targetMeanPrice", 0) or 0
        upside      = float(((target_px / px) - 1) * 100) if px > 0 and target_px > 0 else 0
        market_cap  = inf.get("marketCap", 0) or 0
        volume      = int(h["Volume"].iloc[-1]) if not h["Volume"].empty else 0

        # ציון PDF
        score = 0
        if rev_growth  >= 10: score += 1
        if earn_growth >= 10: score += 1
        if margin      >= 10: score += 1
        if roe         >= 15: score += 1
        if cash > debt:       score += 1
        if debt == 0:         score += 1

        # ──── ניקוד לטווח קצר (מומנטום + RSI) ────
        short_score = 0
        if rsi < 35:           short_score += 3   # מכירת יתר — הזדמנות
        elif rsi < 45:         short_score += 2
        if chg1m < -8:         short_score += 2   # ירידה חדה — bounce
        elif chg1m < -4:       short_score += 1
        if upside > 15:        short_score += 2
        if rev_growth > 15:    short_score += 1
        if volume > 1_000_000: short_score += 1

        # ──── ניקוד לטווח ארוך (יסודות + צמיחה) ────
        long_score = 0
        long_score += score                        # ציון PDF 0-6
        if rev_growth  >= 20: long_score += 2
        elif rev_growth >= 10: long_score += 1
        if earn_growth >= 20: long_score += 2
        elif earn_growth >= 10: long_score += 1
        if upside > 20:       long_score += 2
        elif upside > 10:     long_score += 1
        if div_yield > 2 and payout < 60 and cash > debt:
            long_score += 2                        # דיבידנד בטוח
        if insider_pct >= 5:  long_score += 1
        if chg3m > 10:        long_score += 1      # מומנטום ארוך

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
            "MarketCap":    market_cap,
            "Volume":       volume,
            "CashVsDebt":   "✅" if cash > debt else "❌",
            "Action": (
                "קנייה חזקה 💎" if long_score >= 10 else
                "קנייה 📈"      if long_score >= 7  else
                "החזק ⚖️"       if long_score >= 4  else
                "בבדיקה 🔍"
            ),
        }
    except Exception:
        return None


# ─── סריקה מקבילית ──────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)   # cache 30 דקות
def run_market_scan(universe: list, max_workers: int = 20) -> pd.DataFrame:
    """סורק את כל היקום במקביל. מחזיר DataFrame ממוין."""
    results = []
    progress = st.progress(0, text="🔍 סורק את השוק...")
    total = len(universe)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_scan_single, t): t for t in universe}
        done = 0
        for fut in as_completed(futures):
            done += 1
            progress.progress(done / total,
                text=f"🔍 סורק... {done}/{total} מניות")
            res = fut.result()
            if res:
                results.append(res)

    progress.empty()
    if not results:
        return pd.DataFrame()
    df = pd.DataFrame(results)
    df = df.sort_values("LongScore", ascending=False).reset_index(drop=True)
    return df


# ─── UI: טאב סורק שוק ───────────────────────────────────────────────────────
def render_market_scanner():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #7c4dff;">'
        '<b>🌐 סורק שוק אוטונומי:</b> סורק מאות מניות מ-S&P500, NASDAQ, TASE ו-Mid-Cap '
        'ומדרג אותן לפי פוטנציאל לטווח קצר וארוך.</div>',
        unsafe_allow_html=True,
    )

    # בחירת יקום
    col1, col2, col3 = st.columns(3)
    with col1:
        universe_choice = st.selectbox(
            "🌍 יקום לסריקה",
            ["S&P500 Top 100", "NASDAQ צמיחה", "כל השוק (מלא)", "ת\"א (TASE)", "דיבידנדים"],
            key="scanner_universe",
        )
    with col2:
        horizon = st.selectbox(
            "⏱️ אופק השקעה",
            ["טווח קצר (ימים-שבועות)", "טווח ארוך (חודשים-שנים)", "שניהם"],
            key="scanner_horizon",
        )
    with col3:
        top_n = st.slider("📊 כמה מניות להציג", 5, 50, 20, key="scanner_topn")

    universe_map = {
        "S&P500 Top 100":       SP500_TOP,
        "NASDAQ צמיחה":         NASDAQ_GROWTH + MID_SMALL_CAP,
        "כל השוק (מלא)":        ALL_UNIVERSE,
        "ת\"א (TASE)":          TASE_STOCKS,
        "דיבידנדים":            DIVIDEND_KINGS,
    }
    chosen_universe = universe_map[universe_choice]

    if st.button("🚀 הפעל סריקה", type="primary", key="scanner_run"):
        with st.spinner(""):
            df = run_market_scan(chosen_universe)
        if df.empty:
            st.error("לא ניתן לשאוב נתונים כרגע.")
            return
        st.session_state["scan_results"] = df
        st.session_state["scan_time"] = datetime.now().strftime("%H:%M:%S")
        st.success(f"✅ נסרקו {len(df)} מניות בהצלחה!")

    if "scan_results" not in st.session_state:
        st.info("👆 בחר יקום ולחץ 'הפעל סריקה' כדי לגלות הזדמנויות.")
        return

    df = st.session_state["scan_results"]
    st.caption(f"🕒 עדכון אחרון: {st.session_state.get('scan_time','—')} | "
               f"{len(df)} מניות נסרקו")

    # ─── תצוגה לפי אופק ───
    if horizon in ["טווח קצר (ימים-שבועות)", "שניהם"]:
        st.markdown("### ⚡ TOP — טווח קצר (מומנטום + RSI)")
        short_df = df.sort_values("ShortScore", ascending=False).head(top_n)
        _show_scan_table(short_df, "short")

    if horizon in ["טווח ארוך (חודשים-שנים)", "שניהם"]:
        st.markdown("### 💎 TOP — טווח ארוך (יסודות + צמיחה)")
        long_df = df.sort_values("LongScore", ascending=False).head(top_n)
        _show_scan_table(long_df, "long")

    # ─── כפתור: שלח לסוכנים ───
    st.divider()
    st.markdown("### 🤖 שלח את הממצאים לסוכנים")
    ca, cb, cc = st.columns(3)
    with ca:
        if st.button("📤 עדכן סוכן ערך", key="send_to_value"):
            top_long = df.sort_values("LongScore", ascending=False).head(30)
            st.session_state["agent_universe_df"] = top_long
            st.success(f"✅ {len(top_long)} מניות נשלחו לסוכן ערך!")
    with cb:
        if st.button("📤 עדכן סוכן יומי", key="send_to_day"):
            top_short = df.sort_values("ShortScore", ascending=False).head(30)
            st.session_state["agent_universe_df"] = top_short
            st.success(f"✅ {len(top_short)} מניות נשלחו לסוכן יומי!")
    with cc:
        if st.button("📤 עדכן כל הסוכנים", key="send_to_all"):
            st.session_state["agent_universe_df"] = df.head(50)
            st.success(f"✅ {min(50, len(df))} מניות נשלחו לכל הסוכנים!")

    if "agent_universe_df" in st.session_state:
        n = len(st.session_state["agent_universe_df"])
        st.info(f"🤖 הסוכנים כרגע עובדים עם **{n} מניות** מהסריקה האוטונומית.")


def _show_scan_table(df: pd.DataFrame, key_suffix: str):
    """מציג טבלת תוצאות סריקה."""
    if df.empty:
        st.info("אין תוצאות.")
        return

    display_cols = {
        "Symbol":       "סימול",
        "PriceStr":     "מחיר",
        "ShortScore":   "⚡ קצר",
        "LongScore":    "💎 ארוך",
        "Score":        "⭐ PDF",
        "RSI":          "RSI",
        "Chg1D":        "שינוי יום %",
        "Chg1M":        "שינוי חודש %",
        "RevGrowth":    "מכירות %",
        "EarnGrowth":   "רווחים %",
        "DivYield":     "דיבידנד %",
        "TargetUpside": "אפסייד %",
        "Action":       "המלצה AI",
    }
    show = [c for c in display_cols if c in df.columns]
    st.dataframe(
        df[show].rename(columns=display_cols),
        column_config={
            "⚡ קצר":       st.column_config.NumberColumn("⚡ קצר",  format="%d"),
            "💎 ארוך":      st.column_config.NumberColumn("💎 ארוך", format="%d"),
            "⭐ PDF":        st.column_config.NumberColumn("⭐ PDF",  format="%d"),
            "RSI":           st.column_config.NumberColumn("RSI",    format="%.1f"),
            "שינוי יום %":  st.column_config.NumberColumn("יום %",  format="%.2f%%"),
            "שינוי חודש %": st.column_config.NumberColumn("חודש %", format="%.2f%%"),
            "מכירות %":     st.column_config.NumberColumn("מכירות %", format="%.1f%%"),
            "רווחים %":     st.column_config.NumberColumn("רווחים %", format="%.1f%%"),
            "דיבידנד %":    st.column_config.NumberColumn("דיב %",   format="%.2f%%"),
            "אפסייד %":     st.column_config.NumberColumn("אפסייד%", format="%.1f%%"),
        },
        use_container_width=True, hide_index=True,
    )
