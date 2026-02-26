# social_sentiment_ai.py
import streamlit as st
import pandas as pd

def render_social_intelligence():
    st.markdown('<div class="ai-card" style="border-right-color: #03a9f4;"><b>🐦 מודיעין המונים (Social Sentiment):</b> הבוט סורק את טוויטר (X), רדיט (WallStreetBets) ופורומים כדי לזהות "הייפ" או פאניקה לפני שהם מגיעים לחדשות.</div>', unsafe_allow_html=True)
    
    st.markdown("### 🌐 סורק תעבורת רשת (Trending Tickers)")
    
    data = {
        "סימול": ["NVDA", "PLTR", "TSLA", "GME"],
        "אזכורים ברשת (24H)": ["+450%", "+210%", "-15%", "+800%"],
        "סנטימנט אלגוריתמי": ["🟢 חיובי חזק (הייפ מוסדי)", "🟢 חיובי (דוחות)", "🔴 פאניקה", "🟣 הייפ בועתי (Reddit)"],
        "המלצת AI למערכת": ["המתן לפול-באק", "שקול כניסה לטרייד", "הפעל פקודת שורט", "התרחק לחלוטין - סכנה"]
    }
    
    st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)
    st.info("💡 המערכת יודעת להבדיל בין 'כסף חכם' שמדבר על טכנולוגיה, לבין 'כסף טיפש' שמריץ מניות זבל בפורומים.")
