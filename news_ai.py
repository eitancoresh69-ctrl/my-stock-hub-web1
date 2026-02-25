# news_ai.py
import streamlit as st
import yfinance as yf

def render_live_news(symbols_list):
    st.markdown('<div class="ai-card" style="border-right-color: #000000;"><b>📰 חדר חדשות Live:</b> ה-AI סורק את הכותרות הכלכליות האחרונות (באנגלית) מ-Yahoo Finance, Reuters ו-Bloomberg עבור המניות ברדאר שלך.</div>', unsafe_allow_html=True)
    
    # ניקח רק את 5 המניות הראשונות ברשימה כדי לא להעמיס על השרת
    top_symbols = symbols_list[:5]
    
    cols = st.columns(len(top_symbols))
    
    for i, sym in enumerate(top_symbols):
        with cols[i]:
            st.markdown(f"### 🏢 {sym}")
            try:
                news = yf.Ticker(sym).news
                if news:
                    # מציג את 2 הכתבות האחרונות לכל מניה
                    for article in news[:2]:
                        title = article.get('title', 'ללא כותרת')
                        publisher = article.get('publisher', 'מקור לא ידוע')
                        link = article.get('link', '#')
                        
                        st.markdown(f"""
                        <div style="background-color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e0e0e0;">
                            <a href="{link}" target="_blank" style="text-decoration: none; color: #1a73e8; font-weight: bold; font-size: 14px;">{title}</a><br>
                            <span style="font-size: 12px; color: #757575;">מקור: {publisher}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("אין חדשות חמות כרגע.")
            except:
                st.write("שגיאה בטעינת חדשות.")
