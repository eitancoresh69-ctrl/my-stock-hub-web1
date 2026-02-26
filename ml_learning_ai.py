import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta

def calculate_features(df):
    data = df.copy()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['Price_Above_MA50'] = np.where(data['Close'] > data['MA50'], 1, 0)
    data['Vol_Avg_20'] = data['Volume'].rolling(window=20).mean()
    data['Relative_Volume'] = data['Volume'] / data['Vol_Avg_20']
    
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

    if not st.session_state.ml_model_trained:
        st.info("🟡 מודל לא אומן. בחר הגדרות ולחץ 'אמן מודל AI' כדי להתחיל להוריד נתונים חיים.")
    else:
        st.success(f"✅ מודל פעיל (מבוסס נתוני אמת) | דיוק: **{st.session_state.ml_accuracy:.1f}%** | ריצות: {st.session_state.ml_runs}")

    st.subheader("🏋️ הגדרות אימון מבוסס נתוני אמת")
    
    # בחירת המניה לאימון
    target_ticker = st.text_input("🔍 הקלד סימול מניה לאימון (למשל: QQQ, TSLA, AAPL):", value="QQQ").upper()
    
    col1, col2 = st.columns(2)
    with col1:
        years_history = st.slider("📅 שנות היסטוריה ללמידה (Data Size)", 1, 5, 2, key="ml_years")
        train_split = st.slider("📊 % נתונים לאימון (vs. ולידציה)", 60, 90, 80, key="ml_split")
    with col2:
        features_selected = st.multiselect("📌 פיצ'רים לאימון",
            ["RSI", "Price_Above_MA50", "Relative_Volume"],
            default=["RSI", "Price_Above_MA50", "Relative_Volume"], key="ml_features")

    st.markdown("###### 🎯 הגדרת מטרת המודל (יעד הצלחה):")
    target_days = st.selectbox("חלון זמן למדידת רווח", [1, 3, 5, 10], format_func=lambda x: f"רווח אחרי {x} ימי מסחר", index=2)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 אמן מודל AI על נתוני אמת", type="primary", key="ml_train"):
        if not features_selected:
            st.warning("בחר לפחות פיצ'ר אחד לאימון.")
        elif not target_ticker:
            st.warning("אנא הזן סימול מניה.")
        else:
            with st.spinner(f"מוריד נתוני אמת מ-Yahoo Finance עבור {target_ticker}..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=years_history * 365)
                df = yf.download(target_ticker, start=start_date, end=end_date, progress=False)
                
            if df.empty:
                st.error(f"❌ לא נמצאו נתונים עבור הסימול {target_ticker}. אנא ודא שהסימול תקין.")
            else:
                with st.spinner("מחשב אינדיקטורים טכניים ובונה מודל..."):
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    df = calculate_features(df)
                    df['Future_Return'] = df['Close'].shift(-target_days) / df['Close'] - 1
                    df['Target'] = np.where(df['Future_Return'] > 0, 1, 0)
                    df = df.dropna()
                    
                    if len(df) < 50:
                        st.error("❌ אין מספיק נתוני היסטוריה לאימון המודל. נסה להגדיל את שנות ההיסטוריה.")
                    else:
                        X = df[features_selected]
                        y = df['Target']
                        
                        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_split/100, shuffle=False)
                        
                        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
                        model.fit(X_train, y_train)
                        
                        predictions = model.predict(X_test)
                        accuracy = accuracy_score(y_test, predictions) * 100
                        
                        feature_importances = pd.Series(model.feature_importances_, index=features_selected).sort_values(ascending=False)
                        best_feature = feature_importances.index[0]
                        best_feature_weight = feature_importances.iloc[0] * 100
                        
                        st.session_state.ml_accuracy = accuracy
                        st.session_state.ml_model_trained = True
                        st.session_state.ml_runs += 1
                        
                        insights = [
                            f"📊 הפיצ'ר המשפיע ביותר על מניית **{target_ticker}**: **{best_feature}** (משקל: {best_feature_weight:.1f}%)",
                            f"🎯 מתוך נתוני המבחן, המודל צדק ב-{accuracy:.1f}% מהעסקאות לטווח של {target_days} ימים.",
                        ]
                        st.session_state.ml_insights = insights
                        
                        recent_data = df.tail(15).copy()
                        recent_preds = model.predict(recent_data[features_selected])
                        
                        display_df = pd.DataFrame({
                            "תאריך": recent_data.index.strftime('%Y-%m-%d'),
                            "מחיר סגירה": recent_data['Close'].round(2),
                            "RSI": recent_data['RSI'].round(1),
                            "המלצת מודל (היום)": ["✅ קנייה" if p == 1 else "❌ הימנעות" for p in recent_preds],
                        })
                        st.session_state.recent_trades = display_df.iloc[::-1]

                st.success(f"✅ אימון הושלם עבור {target_ticker}! דיוק: {st.session_state.ml_accuracy:.1f}%")
                st.rerun()

    if st.session_state.ml_insights:
        st.subheader("💡 תובנות AI מהשוק האמיתי")
        for insight in st.session_state.ml_insights:
            st.markdown(f"- {insight}")

    if st.session_state.ml_model_trained and not st.session_state.recent_trades.empty:
        with st.expander("📋 חיזוי המודל על 15 ימי המסחר האחרונים (נתוני אמת)"):
            st.dataframe(st.session_state.recent_trades, use_container_width=True, hide_index=True)

    if st.session_state.ml_model_trained:
        st.divider()
        if st.button("🗑️ איפוס מודל", key="ml_reset"):
            st.session_state.ml_model_trained = False
            st.session_state.ml_accuracy = 0.0
            st.session_state.ml_runs = 0
            st.session_state.ml_insights = []
            st.rerun()
