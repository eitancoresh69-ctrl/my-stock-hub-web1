# bull_bear.py
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

def render_bull_bear(df_all):
    st.markdown('<div class="ai-card"><b>⚖️ מעבדת שור ודוב (Deep Analysis):</b> בחר מניה כדי לקבל ניתוח AI מפורט על הסיכויים (שור) והסיכונים (דוב) שלה, כולל גרף היסטורי גמיש.</div>', unsafe_allow_html=True)
    
    sel = st.selectbox("בחר מניה לניתוח עומק:", df_all['Symbol'].unique())
    row = df_all[df_all['Symbol'] == sel].iloc[0]
    
    st.markdown(f"### 🏢 פרופיל עסקי: {sel}")
    st.write(row["Info"].get("longBusinessSummary", "מידע בטעינה...")[:1000] + "...")
    
    col_bull, col_bear = st.columns(2)
    with col_bull: 
        st.markdown(f'<div class="bull-box"><b>🐂 תזת השור (למה לקנות?):</b><br>1. צמיחת הכנסות חזקה של {row["RevGrowth"]:.1%}.<br>2. עמידה ב-{row["Score"]} מתוך 6 קריטריוני ה-PDF.<br>3. נהנית ממגמות המאקרו של הסקטור.</div>', unsafe_allow_html=True)
    with col_bear: 
        st.markdown(f'<div class="bear-box"><b>🐻 תזת הדוב (למה להיזהר?):</b><br>1. השוק תנודתי ויש סיכון למשיכת כספים מסקטור הטכנולוגיה.<br>2. תחרות גוברת עשויה לפגוע בשולי הרווח בעתיד.</div>', unsafe_allow_html=True)
    
    yrs = st.slider("טווח שנים לגרף:", 1, 10, 5)
    try:
        hist = yf.Ticker(sel).history(period=f"{yrs}y")
        fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#1a73e8', width=2), fill='tozeroy'))
        fig.update_layout(title=f"ביצועי מניית {sel} ל-{yrs} שנים", height=350, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("שגיאה בטעינת הגרף מ-Yahoo.")
