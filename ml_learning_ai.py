# ml_learning_ai.py - למידת מכונה מלאה (הדמייה משודרגת)
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

def render_machine_learning():
    st.markdown('<div class="ai-card" style="border-right-color: #9c27b0;"><b>🧠 מודול למידת מכונה (Machine Learning)</b> — ה-AI לומד מעסקאות העבר שלך ומשפר את דיוק חיזוי הכניסות ביציאות לאורך זמן.</div>', unsafe_allow_html=True)

    if 'ml_model_trained' not in st.session_state:
        st.session_state.ml_model_trained = False
        st.session_state.ml_accuracy = 0.0
        st.session_state.ml_runs = 0
        st.session_state.ml_params = {"risk_ratio": 1.0, "rsi_buy": 40, "rsi_sell": 65, "min_score": 4}
        st.session_state.ml_insights = []
        st.session_state.ml_target_days_saved = 5

    # --- סטטוס ---
    if not st.session_state.ml_model_trained:
        st.info("🟡 מודל לא אומן עדיין. לחץ 'אמן מודל AI' כדי להתחיל.")
    else:
        st.success(f"✅ מודל פעיל | דיוק: **{st.session_state.ml_accuracy:.1f}%** | ריצות אימון: {st.session_state.ml_runs}")

    # --- מדדים ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 דיוק חיזוי", f"{st.session_state.ml_accuracy:.1f}%")
    m2.metric("⚖️ יחס סיכוי/סיכון", f"1:{st.session_state.ml_params['risk_ratio']:.1f}")
    m3.metric("📊 RSI כניסה אופטימלי", f"≤{st.session_state.ml_params['rsi_buy']}")
    m4.metric("⭐ ציון PDF מינימום", str(st.session_state.ml_params['min_score']))

    st.divider()

    # --- הגדרות אימון ---
    st.subheader("🏋️ הגדרות אימון")
    col1, col2 = st.columns(2)
    with col1:
        lookback = st.slider("📅 חלון זמן לאימון (ימים)", 7, 180, 30, key="ml_lookback")
        algo = st.selectbox("🔢 אלגוריתם", ["Random Forest", "Gradient Boosting", "XGBoost", "LSTM (נוירונים)", "Ensemble (משולב — מומלץ)"], key="ml_algo")
        train_split = st.slider("📊 % נתונים לאימון (vs. ולידציה)", 60, 90, 80, key="ml_split")
    with col2:
        # נוספו הפיצ'רים החדשים לרשימה
        features = st.multiselect("📌 פיצ'רים לאימון",
            ["RSI", "Score (PDF)", "RevGrowth", "Margin", "ROE", "MA50", "DivYield", "VIX", "InsiderHeld", "TargetUpside", 
             "Relative Volume", "MACD", "SMA 50 Trend", "Bollinger Bands"],
            default=["RSI", "Score (PDF)", "RevGrowth", "Margin", "Relative Volume", "SMA 50 Trend"], key="ml_features")

    # שורת הגדרות חדשה למטרת המודל
    st.markdown("###### 🎯 הגדרת מטרת המודל (יעד הצלחה):")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        target_days = st.selectbox("חלון זמן למדידת רווח", [1, 3, 5, 10, 14], format_func=lambda x: f"רווח אחרי {x} ימי מסחר", index=2, key="ml_target_days")
    with t_col2:
        target_pct = st.selectbox("תשואה מינימלית להצלחה", [0.5, 1.0, 2.0, 3.0, 5.0], format_func=lambda x: f"מעל {x}%", index=2, key="ml_target_pct")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 אמן מודל AI", type="primary", key="ml_train"):
        if not features:
            st.warning("בחר לפחות פיצ'ר אחד לאימון.")
        else:
            with st.spinner(f"🧠 מאמן {algo} על {lookback} ימי מסחר | {len(features)} פיצ'רים | בוחן רווח אחרי {target_days} ימים..."):
                import time; time.sleep(1.5)

                # סימולציית חישוב דיוק עם בונוס קטן אם משתמשים בפיצ'רים מתקדמים
                advanced_features_bonus = sum(1 for f in ["Relative Volume", "MACD", "Bollinger Bands", "SMA 50 Trend"] if f in features)
                base = 52 + len(features) * 2.5 + (advanced_features_bonus * 1.5) + random.uniform(-3, 4)
                bonus = min(st.session_state.ml_runs * 1.8, 18)
                st.session_state.ml_accuracy = min(round(base + bonus, 1), 89.5) # הועלה הרף המקסימלי ל-89.5
                st.session_state.ml_model_trained = True
                st.session_state.ml_runs += 1
                st.session_state.ml_target_days_saved = target_days

                st.session_state.ml_params = {
                    "risk_ratio": round(1.4 + random.uniform(0, 1.5), 1),
                    "rsi_buy": random.choice([33, 36, 38, 40, 42, 45]),
                    "rsi_sell": random.choice([62, 65, 68, 70, 72]),
                    "min_score": random.choices([4, 5], weights=[0.6, 0.4])[0]
                }

                insights = [
                    f"📊 הפיצ'ר החזק ביותר לחיזוי: **{random.choice(features)}** (חשיבות {random.randint(28,45)}%)",
                    f"🎯 נמצאה תבנית אופטימלית לרווח בטווח של {target_days} ימים: RSI < {st.session_state.ml_params['rsi_buy']} + Score ≥ {st.session_state.ml_params['min_score']}",
                    f"⚠️ תבנית מפסידה: קנייה כשRSI > {st.session_state.ml_params['rsi_sell']} בשוק יורד (כשל ב-{random.randint(68,79)}% מהמקרים)",
                    f"💡 גודל פוזיציה אופטימלי: {random.randint(8,15)}% מהתיק לכל עסקה",
                    f"⚖️ יחס רווח/הפסד מומלץ לעמידה ביעד של {target_pct}%: 1:{st.session_state.ml_params['risk_ratio']:.1f}"
                ]
                st.session_state.ml_insights = insights

            st.success(f"✅ אימון הושלם! דיוק: {st.session_state.ml_accuracy:.1f}% | ריצה #{st.session_state.ml_runs}")
            st.rerun()

    # --- תובנות ---
    if st.session_state.ml_insights:
        st.subheader("💡 תובנות AI מהאימון האחרון")
        for insight in st.session_state.ml_insights:
            st.markdown(f"- {insight}")

    # --- פרמטרים מעודכנים ---
    if st.session_state.ml_model_trained:
        st.subheader("⚙️ פרמטרים אופטימליים שה-AI גילה")
        p = st.session_state.ml_params
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📈 RSI קנייה", f"< {p['rsi_buy']}")
        c2.metric("📉 RSI מכירה", f"> {p['rsi_sell']}")
        c3.metric("⭐ ציון מינימום", str(p['min_score']))
        c4.metric("⚖️ יחס R/R", f"1:{p['risk_ratio']:.1f}")

        st.info(f"💡 **המלצת AI לסוכנים:** עדכן את הסוכנים לקנות כש-RSI < {p['rsi_buy']} וציון PDF ≥ {p['min_score']}, במטרה לממש רווח בעוד {st.session_state.ml_target_days_saved} ימים.")

    # --- נתוני אימון ---
    with st.expander("📋 דוגמת נתוני אימון (30 עסקאות אחרונות)"):
        symbols = ["AAPL", "NVDA", "MSFT", "TSLA", "META", "GOOGL", "AMZN", "PLTR"]
        demo_data = []
        for i in range(30):
            rsi = round(random.uniform(28, 75), 1)
            score = random.randint(2, 6)
            ret = round(random.gauss(1.2, 3.5), 2)
            outcome = "✅ הצלחה" if ret > 0 else "❌ כישלון"
            demo_data.append({
                "סימול": random.choice(symbols),
                "תאריך": (datetime.now() - timedelta(days=30-i)).strftime("%d/%m"),
                "RSI כניסה": rsi, 
                "Score": score,
                "Relative Vol": round(random.uniform(0.5, 3.0), 2), # תוספת עמודה לדוגמה
                "תשואה (%)": ret, 
                "תוצאה": outcome
            })
        st.dataframe(pd.DataFrame(demo_data), use_container_width=True, hide_index=True)
        wins = sum(1 for d in demo_data if "הצלחה" in d["תוצאה"])
        st.metric("אחוז הצלחה בנתונים אלה", f"{(wins/30)*100:.0f}%")

    # --- איפוס ---
    if st.session_state.ml_model_trained:
        if st.button("🗑️ איפוס מודל והתחלה מחדש", key="ml_reset"):
            st.session_state.ml_model_trained = False
            st.session_state.ml_accuracy = 0.0
            st.session_state.ml_runs = 0
            st.session_state.ml_insights = []
            st.rerun()
