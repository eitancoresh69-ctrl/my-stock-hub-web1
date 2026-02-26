# bull_bear.py
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from config import HEBREW_SUMMARIES

@st.cache_data(ttl=3600)
def get_historical_data(symbol, years):
    return yf.Ticker(symbol).history(period=f"{years}y")

def render_bull_bear(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #9c27b0;"><b>⚖️ מעבדת שור/דוב דינמית (AI בעברית):</b> ניתוח עומק מבוסס הנתונים של ה-PDF והטכני.</div>', unsafe_allow_html=True)
    
    sel = st.selectbox("בחר מניה לניתוח AI מקיף:", df_all['Symbol'].unique())
    row = df_all[df_all['Symbol'] == sel].iloc[0]
    
    st.markdown(f"### 🏢 זירת המסחר: {sel}")
    
    # הכרחת שימוש בעברית מתוך קובץ ה-config בלבד!
    summary = HEBREW_SUMMARIES.get(sel, "ה-AI ממשיך לאסוף נתונים אודות חברה זו. הניתוח מתבצע על בסיס הנתונים הפיננסיים.")
    st.info(f"**פרופיל החברה:** {summary}")
    st.markdown("---")
    
    col_bull, col_bear = st.columns(2)
    
    bull_args = f"1. **איכות (PDF):** ציון של {row['Score']}/6.\n"
    if row['RevGrowth'] > 10: bull_args += f"2. **צמיחה:** הכנסות מזנקות ב-{row['RevGrowth']:.1f}%.\n"
    if row['RSI'] < 40: bull_args += f"3. **טכני:** RSI ברמת {row['RSI']:.0f} (מכירת יתר - נקודת כניסה נוחה).\n"
    if row['FairValue'] > row['Price']: bull_args += f"4. **תמחור:** שווי הוגן {row['Currency']}{row['FairValue']:.2f}. פוטנציאל לעלייה."
    
    bear_args = "1. **מאקרו:** סביבת הריבית עשויה לאתגר את המודל העסקי.\n"
    if row['ZeroDebt'] == "❌": bear_args += "2. **חובות:** לחברה יש חוב במאזן שעלול להכביד עליה.\n"
    if row['RSI'] > 65: bear_args += f"3. **סכנת שיא:** RSI גבוה ({row['RSI']:.0f}). המניה התנפחה לאחרונה ויש סיכון לתיקון.\n"
    if row['FairValue'] <= row['Price'] and row['FairValue'] > 0: bear_args += f"4. **יקרה מדי:** נסחרת מעל השווי הכלכלי ({row['Currency']}{row['FairValue']:.2f})."
    
    with col_bull:
        st.success("**🐂 תזת השור (AI Bull Case)**")
        st.markdown(bull_args)
        
    with col_bear:
        st.error("**🐻 תזת הדוב (AI Bear Case)**")
        st.markdown(bear_args)
    
    yrs = st.slider("טווח שנים לגרף היסטורי:", 1, 10, 5)
    try:
        hist = get_historical_data(sel, yrs)
        fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#1a73e8', width=2), fill='tozeroy', fillcolor='rgba(26, 115, 232, 0.1)'))
        fig.update_layout(title=f"התנהגות מחיר - {sel}", height=300, template="plotly_white", margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig, use_container_width=True)
    except:
        pass
