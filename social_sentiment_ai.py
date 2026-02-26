# social_sentiment_ai.py - מודיעין רשתות חברתיות
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# נתוני מודיעין מדומים לכל מניה
_SOCIAL_DATA = {
    "NVDA": {
        "sentiment": 88, "trend": "📈 עולה", "buzz": "🔥 חם מאוד",
        "reddit_mentions": 2847, "twitter_mentions": 15420, "wsb_rank": 2,
        "top_reddit": "NVDA breaking ATH again — AI super-cycle just getting started",
        "top_twitter": "NVDA כבר לא מניית גיימינג — זה תשתית ה-AI של המאה ה-21",
        "institutional": "ביל אקמן הגדיל פוזיציה ב-3%",
        "signal": "🟢 שורי", "signal_strength": "חזק מאוד"
    },
    "TSLA": {
        "sentiment": 52, "trend": "↔️ מעורב", "buzz": "🌡️ פושר",
        "reddit_mentions": 4120, "twitter_mentions": 22100, "wsb_rank": 1,
        "top_reddit": "Tesla robotaxi launch delayed again... buying the dip?",
        "top_twitter": "טסלה — בין גאון לבין שגעון. מחכה לרובוטקסי",
        "institutional": "ARK מכרה ב-2 ימים האחרונים",
        "signal": "🟡 ניטרלי", "signal_strength": "בינוני"
    },
    "AAPL": {
        "sentiment": 74, "trend": "📈 יציב חיובי", "buzz": "📊 נורמלי",
        "reddit_mentions": 1230, "twitter_mentions": 8900, "wsb_rank": 8,
        "top_reddit": "Apple services revenue hits new record — this company is a cash machine",
        "top_twitter": "אפל — הכסף הבטוח של 2025. מכפיל גבוה אבל מוצדק",
        "institutional": "באפט ממשיך להחזיק (ורקשייר לא מכרה)",
        "signal": "🟢 שורי", "signal_strength": "מתון"
    },
    "META": {
        "sentiment": 79, "trend": "📈 עולה", "buzz": "🔥 חם",
        "reddit_mentions": 1890, "twitter_mentions": 12300, "wsb_rank": 5,
        "top_reddit": "Meta's AI investment is finally paying off — Zuckerberg was right",
        "top_twitter": "מטא — זאקרברג הוכיח שהמהמר הגדול ביותר בטק הוא גם הנכון ביותר",
        "institutional": "סורוס הוסיף $200M",
        "signal": "🟢 שורי", "signal_strength": "חזק"
    },
    "MSFT": {
        "sentiment": 81, "trend": "📈 יציב", "buzz": "📊 נורמלי",
        "reddit_mentions": 980, "twitter_mentions": 7200, "wsb_rank": 12,
        "top_reddit": "MSFT is the most boring great stock — slow and steady wins",
        "top_twitter": "מיקרוסופט + OpenAI = משחק גמור לכולם. אקסל לא הולך לשום מקום",
        "institutional": "וואנגארד הגדיל פוזיציה",
        "signal": "🟢 שורי", "signal_strength": "מתון"
    },
    "PLTR": {
        "sentiment": 85, "trend": "📈 עולה חזק", "buzz": "🔥 חם מאוד",
        "reddit_mentions": 3450, "twitter_mentions": 18700, "wsb_rank": 3,
        "top_reddit": "PLTR getting government AI contracts left and right — sleeper pick",
        "top_twitter": "פלנטיר — ה-AI של הממשלה. כשארה''ב משקיעה בביון, פלנטיר מרוויחה",
        "institutional": "קאתי וד (ARK) הוסיפה 1.2M מניות",
        "signal": "🟢 שורי חזק", "signal_strength": "חזק מאוד"
    }
}

def _get_data(symbol):
    if symbol in _SOCIAL_DATA:
        return _SOCIAL_DATA[symbol]
    # ברירת מחדל למניות שאין להן נתונים מותאמים
    return {
        "sentiment": random.randint(40, 75), "trend": "↔️ מעורב", "buzz": "📊 נורמלי",
        "reddit_mentions": random.randint(100, 1000), "twitter_mentions": random.randint(500, 5000),
        "wsb_rank": random.randint(10, 50),
        "top_reddit": f"Watching {symbol} — interesting setup here",
        "top_twitter": f"מסתכל על {symbol} לפריצה פוטנציאלית",
        "institutional": "לא זוהתה פעילות מוסדית חריגה",
        "signal": "🟡 ניטרלי", "signal_strength": "חלש"
    }

def render_social_intelligence():
    st.markdown('<div class="ai-card" style="border-right-color: #03a9f4;"><b>🐦 מודיעין רשתות חברתיות</b> — סריקת Reddit, Twitter/X, ו-WallStreetBets לזיהוי הייפ מוקדם, סנטימנט מוסדי ומניות שהולכות להתפוצץ.</div>', unsafe_allow_html=True)

    # --- דאשבורד סנטימנט כללי ---
    st.subheader("🌡️ מד סנטימנט שוק כללי")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("🐂 סנטימנט כללי", "שורי 72%", delta="+4% מאתמול")
    col_s2.metric("🔥 מניה הכי חמה", "PLTR", delta="WSB #3")
    col_s3.metric("📉 מניה הכי קרה", "COST", delta="מעט דיון")
    col_s4.metric("⚡ אירוע ויראלי", "Earnings NVDA", delta="עוד 3 ימים")

    st.divider()

    # --- סורק סנטימנט לפי מניה ---
    st.subheader("🔍 סורק סנטימנט לפי מניה")

    # בנה רשימת מניות מ-session_state
    known_symbols = list(_SOCIAL_DATA.keys()) + ["AMZN", "GOOGL", "AMD", "LLY", "TSM"]
    selected = st.selectbox("בחר מניה לניתוח:", known_symbols, key="social_sel")

    if st.button("🔍 נתח סנטימנט עכשיו", type="primary", key="social_analyze"):
        data = _get_data(selected)
        with st.spinner("🔎 סורק Reddit, Twitter/X, WallStreetBets..."):
            import time; time.sleep(0.8)

        st.markdown(f"### 📊 דוח סנטימנט: {selected}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡️ ציון סנטימנט", f"{data['sentiment']}/100", delta=data['trend'])
        c2.metric("🔥 רמת ההייפ", data['buzz'])
        c3.metric("💬 Reddit (24h)", f"{data['reddit_mentions']:,}")
        c4.metric("🐦 Twitter/X (24h)", f"{data['twitter_mentions']:,}")

        # תרשים סנטימנט
        sentiment_val = data['sentiment']
        bar_color = "🟢" if sentiment_val >= 70 else "🟡" if sentiment_val >= 45 else "🔴"
        filled = int(sentiment_val / 10)
        bar = bar_color * filled + "⬜" * (10 - filled)
        st.markdown(f"**מד סנטימנט:** {bar} **{sentiment_val}%**")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("#### 👾 Reddit — פוסט מוביל")
            st.info(f'"{data["top_reddit"]}"')
            st.caption(f"WSB Rank: #{data['wsb_rank']} | Upvotes: {random.randint(500, 8000):,}")

        with col_r2:
            st.markdown("#### 🐦 Twitter/X — ציוץ מוביל")
            st.info(f'"{data["top_twitter"]}"')
            st.caption(f"Likes: {random.randint(200, 5000):,} | Retweets: {random.randint(50, 1000):,}")

        st.markdown("#### 🏛️ פעילות מוסדית (Smart Money)")
        st.warning(f"📋 {data['institutional']}")

        # סיגנל סופי
        sig = data['signal']
        strength = data['signal_strength']
        if "שורי" in sig:
            st.success(f"### {sig} | עוצמה: {strength}\n\nה-AI זיהה סנטימנט חיובי ברשתות עם גיבוי מוסדי. שקול כניסה בתנאים הנכונים לפי ה-PDF.")
        elif "דובי" in sig or "שלילי" in sig:
            st.error(f"### {sig} | עוצמה: {strength}\n\nה-AI זיהה לחץ מכירות ברשתות. המתן לאישות תחתית לפני כניסה.")
        else:
            st.info(f"### {sig} | עוצמה: {strength}\n\nסנטימנט מעורב. המתן לכיוון ברור יותר לפני פעולה.")

    st.divider()

    # --- טרנדים כלליים ---
    st.subheader("🔥 טרנדים ויראליים כרגע")
    trends = [
        {"נושא": "AI Earnings Season", "עוצמה": "🔥🔥🔥🔥🔥", "מניות": "NVDA, MSFT, META", "סנטימנט": "🟢 +87%"},
        {"נושא": "Fed Rate Decision", "עוצמה": "🔥🔥🔥🔥", "מניות": "JPM, GS, KRE", "סנטימנט": "🟡 +52%"},
        {"נושא": "EV Price War China", "עוצמה": "🔥🔥🔥", "מניות": "TSLA, GM", "סנטימנט": "🔴 -31%"},
        {"נושא": "Biotech Breakthrough", "עוצמה": "🔥🔥", "מניות": "LLY, MRNA, AMGN", "סנטימנט": "🟢 +71%"},
        {"נושא": "Crypto Bull Market", "עוצמה": "🔥🔥🔥🔥", "מניות": "COIN, MSTR", "סנטימנט": "🟢 +79%"},
    ]
    st.dataframe(pd.DataFrame(trends), use_container_width=True, hide_index=True)

    # --- WSB Watch List ---
    st.subheader("👾 WallStreetBets — Top 5 מניות שנדונות ביותר היום")
    wsb_data = [
        {"#": 1, "מניה": "TSLA", "אזכורים": "4,120", "כיוון": "↔️ מעורב"},
        {"#": 2, "מניה": "NVDA", "אזכורים": "2,847", "כיוון": "🟢 שורי"},
        {"#": 3, "מניה": "PLTR", "אזכורים": "3,450", "כיוון": "🟢 שורי חזק"},
        {"#": 4, "מניה": "AMD",  "אזכורים": "1,980", "כיוון": "🟢 שורי"},
        {"#": 5, "מניה": "META", "אזכורים": "1,890", "כיוון": "🟢 שורי"},
    ]
    st.dataframe(pd.DataFrame(wsb_data), use_container_width=True, hide_index=True)
    st.caption("⚠️ נתוני רשתות חברתיות הם הדמייה מבוססת תבניות אמיתיות. אל תסמוך עליהם לבד — השתמש תמיד יחד עם ניתוח PDF.")
