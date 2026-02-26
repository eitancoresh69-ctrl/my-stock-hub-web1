# ml_learning_ai.py - מחובר לנתוני אמת (Yahoo Finance + Scikit-Learn)
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta

# פונקציה לחישוב אינדיקטורים טכניים (פיצ'רים)
def calculate_features(df):
    data = df.copy()
    
    # חישוב MA50 (ממוצע נע 50)
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['Price_Above_MA50'] = np.where(data['Close'] > data['MA50'], 1, 0)
    
    # חישוב מחזור יחסי (Relative Volume)
    data['Vol_Avg_20'] = data['Volume'].rolling(window=20).mean()
    data['Relative_Volume'] = data['Volume'] / data['Vol_Avg_20']
    
    # חישוב RSI (14 ימים)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    return data.dropna()

def render_machine_learning():
    st.markdown('<div class="ai-card" style="border-right-color: #9c27b0;"><b>🧠 מודול למידת מכונה (Real Data)</b> — ה-AI לומד מנתוני אמת של הבורסה ומשפר את דיוק החיזוי.</div>', unsafe_allow_html=True)

    if 'ml_model_trained' not in st.session_state:
        st.session_state.ml_model_trained = False
        st.session_state.ml_accuracy = 0.0
        st.session_state.ml_runs = 0
        st.session_state.ml_insights = []
        st.session_state.recent_trades = pd.DataFrame()

    # --- סטטוס ---
    if not st.session_state.ml_model_trained:
        st.info("🟡 מודל לא אומן. בחר הגדרות ולחץ 'אמן מודל AI' כדי להתחיל להוריד נתונים חיים.")
    else:
        st.success(f"✅ מודל פעיל (מבוסס נתוני אמת) | דיוק: **{st.session_state.ml_accuracy:.1f}%** | ריצות אימון: {st.session_state.ml_runs}")

    # --- הגדרות אימון ---
    st.subheader("🏋️ הגדרות אימון מבוסס נתוני אמת")
    col1, col2 = st.columns(2)
    with col1:
        # כדי לאמן AI צריך שנים של נתונים, אז שיניתי את זה לכמות שנות היסטוריה
        years_history = st.slider("📅 שנות היסטוריה ללמידה (Data Size)", 1, 5, 2, key="ml_years")
        train_split = st.slider("📊 % נתונים לאימון (vs. ולידציה)", 60, 90, 80, key="ml_split")
    with col2:
        # בחרתי פיצ'רים טכניים שאפשר לחשב מיד על נתוני מחיר
        features_selected = st.multiselect("📌 פיצ'רים לאימון",
            ["RSI", "Price_Above_MA50", "Relative_Volume"],
            default=["RSI", "Price_Above_MA50", "Relative_Volume"], key="ml_features")

    st.markdown("###### 🎯 הגדרת מטרת המודל (יעד הצלחה):")
    target_days = st.selectbox("חלון זמן למדידת רווח", [1, 3, 5, 10], format_func=lambda x: f"רווח אחרי {x} ימי מסחר", index=2)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 אמן מודל AI על נתוני אמת", type="primary", key="ml_train"):
        if not features_selected:
            st.warning("בחר לפחות פיצ'ר אחד לאימון.")
        else:
            with st.spinner("מוריד נתוני אמת מ-Yahoo Finance (QQQ)..."):
                # 1. הורדת נתונים (נדגים על מדד הנאסד"ק כדי שהלמידה תהיה יציבה)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=years_history * 365)
                df = yf.download("QQQ", start=start_date, end=end_date, progress=False)
                
            with st.spinner("מחשב אינדיקטורים טכניים ובונה מודל..."):
                # טיפול בבעיית ריבוי רמות (MultiIndex) שמגיעה מ-yfinance בגרסאות חדשות
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # 2. חישוב פיצ'רים
                df = calculate_features(df)
                
                # 3. הגדרת המטרה (Target): האם המחיר בעוד X ימים גבוה מהמחיר היום?
                df['Future_Return'] = df['Close'].shift(-target_days) / df['Close'] - 1
                # 1 = רווח, 0 = הפסד
                df['Target'] = np.where(df['Future_Return'] > 0, 1, 0)
                
                df = df.dropna() # ניקוי שורות אחרונות שאין להן עתיד עדיין
                
                # 4. הכנת הנתונים למודל
                X = df[features_selected]
                y = df['Target']
                
                # חלוקה לנתוני אימון ובדיקה
                X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_split/100, shuffle=False)
                
                # 5. אימון מודל יער אקראי (Random Forest) אמיתי!
                model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
                model.fit(X_train, y_train)
                
                # 6. בדיקת ביצועים
                predictions = model.predict(X_test)
                accuracy = accuracy_score(y_test, predictions) * 100
                
                # 7. חילוץ חשיבות הפיצ'רים (מה באמת משפיע על המניה?)
                feature_importances = pd.Series(model.feature_importances_, index=features_selected).sort_values(ascending=False)
                best_feature = feature_importances.index[0]
                best_feature_weight = feature_importances.iloc[0] * 100
                
                # שמירת הנתונים ל-Session State
                st.session_state.ml_accuracy = accuracy
                st.session_state.ml_model_trained = True
                st.session_state.ml_runs += 1
                
                # יצירת תובנות אמיתיות
                insights = [
                    f"📊 הפיצ'ר בעל ההשפעה הגדולה ביותר במציאות: **{best_feature}** (משקל בהחלטה: {best_feature_weight:.1f}%)",
                    f"🎯 מתוך נתוני הבדיקה, המודל צדק ב-{accuracy:.1f}% מהעסקאות לטווח של {target_days} ימים.",
                    f"⚠️ שים לב: המודל מזהה ש-QQQ נוטה לכיוון חיובי כברירת מחדל (Buy and Hold bias), ולכן נדרש לשלב אותו עם ניתוח פונדמנטלי (PDF Score)."
                ]
                st.session_state.ml_insights = insights
                
                # 8. הכנת טבלת דוגמה של הימים האחרונים עם חיזוי המודל האמיתי
                recent_data = df.tail(15).copy()
                recent_preds = model.predict(recent_data[features_selected])
                
                display_df = pd.DataFrame({
                    "תאריך": recent_data.index.strftime('%Y-%m-%d'),
                    "מחיר סגירה": recent_data['Close'].round(2),
                    "RSI": recent_data['RSI'].round(1),
                    "המלצת מודל (היום)": ["✅ קנייה" if p == 1 else "❌ הימנעות" for p in recent_preds],
                    "תשואה בפועל (%)": (recent_data['Future_Return'] * 100).round(2)
                })
                st.session_state.recent_trades = display_df.iloc[::-1] # הפיכת הסדר כדי שהכי חדש יהיה למעלה

            st.success(f"✅ אימון על נתוני אמת הושלם! דיוק: {st.session_state.ml_accuracy:.1f}%")
            st.rerun()

    # --- תובנות ---
    if st.session_state.ml_insights:
        st.subheader("💡 תובנות AI מהשוק האמיתי")
        for insight in st.session_state.ml_insights:
            st.markdown(f"- {insight}")

    # --- נתוני אמת וחיזויים אחרונים ---
    if st.session_state.ml_model_trained and not st.session_state.recent_trades.empty:
        with st.expander("📋 חיזוי המודל על 15 ימי המסחר האחרונים (נתוני אמת)"):
            st.dataframe(st.session_state.recent_trades, use_container_width=True, hide_index=True)

    # --- איפוס ---
    if st.session_state.ml_model_trained:
        st.divider()
        if st.button("🗑️ איפוס מודל", key="ml_reset"):
            st.session_state.ml_model_trained = False
            st.session_state.ml_accuracy = 0.0
            st.session_state.ml_runs = 0
            st.session_state.ml_insights = []
            st.rerun()
