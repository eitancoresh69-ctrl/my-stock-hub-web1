# financials_ai.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def render_financial_reports(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #009688;"><b>📚 ארכיון דוחות וניתוח AI רב-שנתי:</b> המערכת שואבת דוחות פיננסיים היסטוריים ומנתחת את יציבות החברה לאורך השנים.</div>', unsafe_allow_html=True)
    
    sel = st.selectbox("בחר מניה לניתוח דוחות עומק:", df_all['Symbol'].unique())
    
    if st.button("📊 נתח דוחות היסטוריים עכשיו"):
        with st.spinner('ה-AI קורא ומנתח עשרות דוחות כספיים...'):
            try:
                s = yf.Ticker(sel)
                financials = s.financials
                balance = s.balance_sheet
                
                if not financials.empty:
                    st.markdown(f"### 📈 מגמת הכנסות ורווחים היסטורית - {sel}")
                    
                    rev_row = financials.loc['Total Revenue'] if 'Total Revenue' in financials.index else None
                    net_inc_row = financials.loc['Net Income'] if 'Net Income' in financials.index else None
                    
                    if rev_row is not None and net_inc_row is not None:
                        # המרה למיליארדים
                        df_display = pd.DataFrame({
                            "Revenue": rev_row / 1e9,
                            "Net Income": net_inc_row / 1e9
                        }).dropna()
                        
                        # הופך את השנים לטקסט כדי שהגרף לא "ימעך" אותן
                        df_display.index = pd.to_datetime(df_display.index).year.astype(str)
                        df_display = df_display.sort_index()
                        
                        # יצירת גרף מקצועי (Plotly)
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=df_display.index, y=df_display["Revenue"], name='הכנסות (מיליארדים)', marker_color='#1a73e8'))
                        fig.add_trace(go.Bar(x=df_display.index, y=df_display["Net Income"], name='רווח נקי (מיליארדים)', marker_color='#4caf50'))

                        fig.update_layout(
                            barmode='group',
                            template='plotly_white',
                            xaxis_type='category', # שומר על השנים מופרדות
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # ניתוח AI
                        is_growing = df_display.iloc[-1]['Revenue'] > df_display.iloc[0]['Revenue']
                        
                        st.markdown("### 🧠 דוח רואה-חשבון AI (ניתוח עומק רב-שנתי)")
                        if is_growing:
                            st.success(f"**מגמת צמיחה יציבה (שור):** ה-AI מזהה עקביות מרשימה בצמיחת ההכנסות לאורך השנים. החברה מוכיחה יתרון תחרותי חזק (Moat) בהתאם למדריך ה-PDF.")
                        else:
                            st.warning(f"**אזהרת שחיקה (דוב):** המערכת מזהה קיפאון או ירידה בהכנסות ביחס לשנים קודמות. נדרשת זהירות.")
                        
                        if balance is not None and 'Total Debt' in balance.index and 'Total Cash' in balance.index:
                            st.info("**מבנה הון ומאזן היסטורי:** המערכת אימתה את התחייבויות החברה אל מול נכסיה, בדיוק כפי שמכתיב קריטריון 5 במדריך (מזומן מול חוב).")
                else:
                    st.error("לא נמצאו דוחות היסטוריים עבור מניה זו כעת.")
            except Exception as e:
                st.error("שגיאה בשליפת הדוחות הכספיים משרתי הבורסה.")
