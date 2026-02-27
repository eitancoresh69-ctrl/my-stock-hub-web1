# ml_learning_ai.py — למידת מכונה (הדמייה)
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta


def render_machine_learning():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #9c27b0;">'
        '<b>🧠 למידת מכונה:</b> ה-AI לומד מעסקאות העבר ומשפר דיוק חיזוי.</div>',
        unsafe_allow_html=True,
    )

    for key, default in [
        ("ml_trained", False), ("ml_accuracy", 0.0), ("ml_runs", 0),
        ("ml_params", {"risk_ratio": 1.0, "rsi_buy": 40, "rsi_sell": 65, "min_score": 4}),
        ("ml_insights", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if not st.session_state.ml_trained:
        st.info("🟡 מודל לא אומן עדיין.")
    else:
        st.success(f"✅ מודל פעיל | דיוק: **{st.session_state.ml_accuracy:.1f}%** | ריצות: {st.session_state.ml_runs}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 דיוק", f"{st.session_state.ml_accuracy:.1f}%")
    m2.metric("⚖️ R/R", f"1:{st.session_state.ml_params['risk_ratio']:.1f}")
    m3.metric("📊 RSI כניסה", f"≤{st.session_state.ml_params['rsi_buy']}")
    m4.metric("⭐ ציון מינימום", str(st.session_state.ml_params["min_score"]))

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        algo = st.selectbox("🔢 אלגוריתם", [
            "Random Forest", "Gradient Boosting", "XGBoost",
            "LSTM (נוירונים)", "Ensemble (משולב — מומלץ)"
        ])
        st.slider("📅 חלון אימון (ימים)", 7, 180, 30, key="ml_window")
    with col2:
        features = st.multiselect("📌 פיצ'רים", [
            "RSI", "Score (PDF)", "RevGrowth", "Margin", "ROE",
            "MA50", "DivYield", "VIX", "InsiderHeld", "TargetUpside"
        ], default=["RSI", "Score (PDF)", "RevGrowth", "Margin"])

    if st.button("🚀 אמן מודל", type="primary", key="ml_train"):
        if not features:
            st.warning("בחר פיצ'ר אחד לפחות.")
        else:
            with st.spinner(f"מאמן {algo}..."):
                import time; time.sleep(1.5)
                base = 52 + len(features) * 2.5 + random.uniform(-3, 4)
                bonus = min(st.session_state.ml_runs * 1.8, 18)
                st.session_state.ml_accuracy = min(round(base + bonus, 1), 83.0)
                st.session_state.ml_trained = True
                st.session_state.ml_runs += 1
                st.session_state.ml_params = {
                    "risk_ratio": round(1.4 + random.uniform(0, 1.2), 1),
                    "rsi_buy":    random.choice([33, 36, 38, 40, 42]),
                    "rsi_sell":   random.choice([62, 65, 68, 70]),
                    "min_score":  random.choices([4, 5], weights=[0.6, 0.4])[0],
                }
                st.session_state.ml_insights = [
                    f"📊 פיצ'ר חזק: **{random.choice(features)}** ({random.randint(28,45)}%)",
                    f"📈 כניסה מנצחת: RSI<{st.session_state.ml_params['rsi_buy']} + Score≥{st.session_state.ml_params['min_score']}",
                    f"⚠️ כניסה מפסידה: RSI>{st.session_state.ml_params['rsi_sell']} בשוק יורד",
                    f"💡 גודל פוזיציה: {random.randint(8,15)}% מהתיק",
                    f"🎯 R/R: 1:{st.session_state.ml_params['risk_ratio']:.1f}",
                ]
            st.success(f"✅ דיוק: {st.session_state.ml_accuracy:.1f}%")
            st.rerun()

    if st.session_state.ml_insights:
        st.subheader("💡 תובנות")
        for ins in st.session_state.ml_insights:
            st.markdown(f"- {ins}")

    if st.session_state.ml_trained:
        p = st.session_state.ml_params
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("RSI קנייה", f"< {p['rsi_buy']}")
        c2.metric("RSI מכירה", f"> {p['rsi_sell']}")
        c3.metric("ציון מינימום", str(p["min_score"]))
        c4.metric("R/R", f"1:{p['risk_ratio']:.1f}")

    with st.expander("📋 נתוני אימון (30 עסקאות)"):
        symbols = ["AAPL", "NVDA", "MSFT", "TSLA", "META", "PLTR"]
        demo = []
        for i in range(30):
            ret = round(random.gauss(1.2, 3.5), 2)
            demo.append({
                "סימול": random.choice(symbols),
                "תאריך": (datetime.now() - timedelta(days=30-i)).strftime("%d/%m"),
                "RSI": round(random.uniform(28, 75), 1),
                "Score": random.randint(2, 6),
                "תשואה %": ret,
                "תוצאה": "✅" if ret > 0 else "❌",
            })
        st.dataframe(pd.DataFrame(demo), use_container_width=True, hide_index=True)
        wins = sum(1 for d in demo if d["תוצאה"] == "✅")
        st.metric("אחוז הצלחה", f"{(wins/30)*100:.0f}%")

    if st.session_state.ml_trained:
        if st.button("🗑️ איפוס מודל", key="ml_reset"):
            st.session_state.ml_trained = False
            st.session_state.ml_accuracy = 0.0
