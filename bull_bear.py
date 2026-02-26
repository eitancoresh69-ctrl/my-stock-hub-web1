# bull_bear.py
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

def render_bull_bear(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #9c27b0;"><b>⚖️ מעבדת שור/דוב דינמית:</b> ה-AI מרכיב כתב תביעה והגנה על המניה בזמן אמת, מבוסס על נתוני ה-PDF, תמחור ומדדים טכניים.</div>', unsafe_allow_html=True)
    
    sel = st.selectbox("בחר מניה לקרב מוחות:", df_all['Symbol'].unique())
    row = df_all[df_all['Symbol'] == sel].iloc[0]
    
    st.markdown(f"### 🏢 זירת המסחר: {sel}")
    
    col_bull, col_bear = st.columns(2)
    
    # בניית תזת שור (למה לקנות) דינמית
    bull_args = f"1. **איכות (PDF):** החברה השיגה ציון מכובד של {row['Score']}/6.\n"
    if row['RevGrowth'] > 10: bull_args += f"2. **צמיחה:** הכנסות מזנקות ב-{row['RevGrowth']:.1f}%, עדות לשליטה בשוק.\n"
    if row['RSI'] < 40: bull_args += f"3. **תזמון טכני:** מדד ה-RSI עומד על {row['RSI']:.0f} (מכירת יתר). מחיר המניה נחתך לאחרונה, מה שיוצר נקודת כניסה זולה.\n"
    if row['FairValue'] > row['Price']: bull_args += f"4. **תמחור:** שווי הוגן מוערך ב-{row['Currency']}{row['FairValue']:.2f}. המניה נסחרת בהנחה (דיסקאונט) ומהווה הזדמנות למשקיעי ערך."
    
    # בניית תזת דוב (למה להיזהר) דינמית
    bear_args = "1. **סיכוני מאקרו:** סביבת ריבית מאתגרת עלולה להאט את קצב ההתרחבות של החברה.\n"
    if row['ZeroDebt'] == "❌": bear_args += "2. **חובות:** לחברה יש חוב במאזן, דבר שעלול להכביד עליה בתקופת מיתון (הפרה של קריטריון 6).\n"
    if row['RSI'] > 65: bear_args += f"3. **סכנת שיא:** מדד ה-RSI גבוה ({row['RSI']:.0f}). המניה התנפחה לאחרונה ויש סיכון ממשי לתיקון וירידת מחיר קרובה.\n"
    if row['FairValue'] <= row['Price'] and row['FairValue'] > 0: bear_args += f"4. **יקרה מדי:** המניה נסחרת מעל השווי ההוגן הכלכלי שלה ({row['Currency']}{row['FairValue']:.2f}). משקיעים משלמים 'פרמיית חלום'."
    
    with col_bull:
        st.success("**🐂 תזת השור (מנוע צמיחה וערך)**")
        st.markdown(bull_args)
        
    with col_bear:
        st.error("**🐻 תזת הדוב (תמרורי אזהרה)**")
        st.markdown(bear_args)
    
    # גרף
    st.markdown("---")
    yrs = st.slider("טווח שנים לגרף היסטורי:", 1, 10, 5)
    try:
        hist = yf.Ticker(sel).history(period=f"{yrs}y")
        fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#1a73e8', width=2), fill='tozeroy', fillcolor='rgba(26, 115, 232, 0.1)'))
        fig.update_layout(title=f"התנהגות מחיר - {sel}", height=300, template="plotly_white", margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("הגרף לא זמין כרגע.")
