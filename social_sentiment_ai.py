# social_sentiment_ai.py — מודיעין רשתות חברתיות
import streamlit as st
import pandas as pd
import random

_DATA = {
    "NVDA": {"s": 88, "t": "📈 עולה", "b": "🔥 חם מאוד", "r": 2847, "x": 15420, "w": 2,
             "tr": "NVDA breaking ATH — AI super-cycle just starting",
             "tx": "אנבידיה — תשתית ה-AI של המאה ה-21",
             "i": "BlackRock הגדיל ב-4%", "sig": "🟢 שורי", "str": "חזק מאוד"},
    "TSLA": {"s": 52, "t": "↔️ מעורב", "b": "🌡️ פושר", "r": 4120, "x": 22100, "w": 1,
             "tr": "Tesla robotaxi delayed... buying the dip?",
             "tx": "טסלה — בין גאון לשגעון",
             "i": "ARK מכרה ב-2 ימים", "sig": "🟡 ניטרלי", "str": "בינוני"},
    "AAPL": {"s": 74, "t": "📈 יציב", "b": "📊 נורמלי", "r": 1230, "x": 8900, "w": 8,
             "tr": "Apple services revenue record — cash machine",
             "tx": "אפל — הכסף הבטוח",
             "i": "באפט לא מכר", "sig": "🟢 שורי", "str": "מתון"},
    "META": {"s": 79, "t": "📈 עולה", "b": "🔥 חם", "r": 1890, "x": 12300, "w": 5,
             "tr": "Meta AI paying off — Zuckerberg was right",
             "tx": "מטא — זאקרברג הוכיח",
             "i": "סורוס הוסיף $200M", "sig": "🟢 שורי", "str": "חזק"},
    "PLTR": {"s": 85, "t": "📈 עולה חזק", "b": "🔥 חם מאוד", "r": 3450, "x": 18700, "w": 3,
             "tr": "PLTR getting government AI contracts — sleeper pick",
             "tx": "פלנטיר — ה-AI של הממשלה",
             "i": "ARK הוסיפה 1.2M מניות", "sig": "🟢 שורי חזק", "str": "חזק מאוד"},
}


def _get(sym):
    if sym in _DATA:
        d = _DATA[sym]
        return d
    return {"s": random.randint(40,75), "t": "↔️ מעורב", "b": "📊 נורמלי",
            "r": random.randint(100,1000), "x": random.randint(500,5000),
            "w": random.randint(10,50), "tr": f"Watching {sym}",
            "tx": f"עוקב אחרי {sym}", "i": "לא זוהתה פעילות מוסדית",
            "sig": "🟡 ניטרלי", "str": "חלש"}


def render_social_intelligence():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #03a9f4;">'
        '<b>🐦 מודיעין רשתות חברתיות:</b> Reddit, Twitter/X, WallStreetBets.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🐂 סנטימנט", "שורי 72%", delta="+4%")
    c2.metric("🔥 הכי חם", "PLTR", delta="WSB #3")
    c3.metric("📉 הכי קר", "COST")
    c4.metric("⚡ ויראלי", "NVDA Earnings")

    st.divider()
    known = list(_DATA.keys()) + ["AMZN", "GOOGL", "AMD", "MSFT"]
    sel = st.selectbox("בחר מניה:", known, key="social_sym")

    if st.button("🔍 נתח סנטימנט", type="primary", key="social_run"):
        import time; time.sleep(0.6)
        d = _get(sel)
        st.markdown(f"### 📊 {sel}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡️ ציון", f"{d['s']}/100", delta=d["t"])
        c2.metric("🔥 הייפ", d["b"])
        c3.metric("💬 Reddit", f"{d['r']:,}")
        c4.metric("🐦 Twitter", f"{d['x']:,}")

        filled = int(d["s"] / 10)
        color = "🟢" if d["s"] >= 70 else "🟡" if d["s"] >= 45 else "🔴"
        st.markdown(f"**מד:** {color * filled}{'⬜' * (10-filled)} **{d['s']}%**")

        col_r, col_t = st.columns(2)
        with col_r:
            st.markdown("#### 👾 Reddit")
            st.info(f'"{d["tr"]}"')
            st.caption(f"WSB #{d['w']} | Upvotes: {random.randint(500,8000):,}")
        with col_t:
            st.markdown("#### 🐦 Twitter")
            st.info(f'"{d["tx"]}"')
            st.caption(f"Likes: {random.randint(200,5000):,}")

        st.markdown("#### 🏛️ מוסדיים")
        st.warning(f"📋 {d['i']}")

        sig = d["sig"]
        if "שורי" in sig:
            st.success(f"### {sig} | {d['str']}")
        elif "דובי" in sig:
            st.error(f"### {sig} | {d['str']}")
        else:
            st.info(f"### {sig} | המתן לכיוון ברור.")

    st.divider()
    st.subheader("🔥 טרנדים ויראליים")
    st.dataframe(pd.DataFrame([
        {"נושא": "AI Earnings Season", "עוצמה": "🔥🔥🔥🔥🔥", "מניות": "NVDA,MSFT,META", "סנטימנט": "🟢 +87%"},
        {"נושא": "Fed Rate Decision",  "עוצמה": "🔥🔥🔥🔥",  "מניות": "JPM,GS",          "סנטימנט": "🟡 +52%"},
        {"נושא": "EV Price War",       "עוצמה": "🔥🔥🔥",    "מניות": "TSLA,GM",          "סנטימנט": "🔴 -31%"},
        {"נושא": "Crypto Bull Market", "עוצמה": "🔥🔥🔥🔥",  "מניות": "COIN,MSTR",        "סנטימנט": "🟢 +79%"},
    ]), use_container_width=True, hide_index=True)

    st.subheader("👾 WallStreetBets Top 5")
    st.dataframe(pd.DataFrame([
        {"#": 1, "מניה": "TSLA", "אזכורים": "4,120", "כיוון": "↔️ מעורב"},
        {"#": 2, "מניה": "NVDA", "אזכורים": "2,847", "כיוון": "🟢 שורי"},
        {"#": 3, "מניה": "PLTR", "אזכורים": "3,450", "כיוון": "🟢 שורי חזק"},
        {"#": 4, "מניה": "AMD",  "אזכורים": "1,980", "כיוון": "🟢 שורי"},
        {"#": 5, "מניה": "META", "אזכורים": "1,890", "כיוון": "🟢 שורי"},
    ]), use_container_width=True, hide_index=True)
    st.caption("⚠️ נתוני רשתות חברתיות הם הדמייה. השתמש תמיד יחד עם ניתוח PDF.")
