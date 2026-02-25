# news_ai.py
import streamlit as st
import yfinance as yf

def advanced_ai_analysis(title, sym):
    t = title.lower()
    
    if any(word in t for word in ["earning", "revenue", "profit", "q1", "q2", "q3", "q4", "beat", "miss", "result"]):
        return f"**📝 תמצית:** עדכון תוצאות כספיות.\n\n**🔍 ניתוח AI:** השוק בוחן את עמידת החברה בתחזיות. למשקיעי ערך: ודא שצמיחת ההכנסות נשמרת מעל 10% (קריטריון 1 ב-PDF)."
    elif any(word in t for word in ["ai", "chip", "tech", "intelligence", "cloud", "software", "launch"]):
        return f"**📝 תמצית:** חדשנות או השקת מוצר.\n\n**🔍 ניתוח AI:** התפתחות טכנולוגית מחזקת את ה'חפיר הכלכלי' (Moat) של החברה, מה שעשוי למשוך הון מוסדי ולתמוך בצמיחה ארוכת טווח."
    elif any(word in t for word in ["buy", "upgrade", "bull", "target", "soar", "jump", "rally", "high"]):
        return f"**📝 תמצית:** סנטימנט חיובי (שור).\n\n**🔍 ניתוח AI:** שדרוג המלצות בוול-סטריט. אזהרה למשקיעי ערך: יש להיזהר מ-FOMO ולוודא שהמחיר הנוכחי עדיין נמוך מהשווי ההוגן."
    elif any(word in t for word in ["sell", "downgrade", "bear", "drop", "lawsuit", "sue", "fall", "plunge", "risk"]):
        return f"**📝 תמצית:** סנטימנט שלילי או משבר.\n\n**🔍 ניתוח AI:** פאניקה זמנית בשוק. למשקיע הערך זו עשויה להיות הזדמנות פז לאיסוף סחורה בזול, במידה ומאזן החברה נותר חזק."
    elif any(word in t for word in ["dividend", "payout", "yield", "shareholder"]):
        return f"**📝 תמצית:** חלוקת רווחים למשקיעים.\n\n**🔍 ניתוח AI:** איתות עוצמה. חברה המגדילה דיבידנד מאשרת את חוזק תזרים המזומנים שלה (תומך בקריטריון 6 ב-PDF)."
    else:
        return f"**📝 תמצית:** עדכון שוטף.\n\n**🔍 ניתוח AI:** חדשות מאקרו או רעשי רקע רגילים. מומלץ להמשיך לדבוק באסטרטגיית ה-PDF ללא פעולה פזיזה."

def render_live_news(symbols_list):
    st.markdown('<div class="ai-card" style="border-right-color: #f50057;"><b>📰 דסק חדשות וניתוח AI:</b> כותרות מהעולם, ללא באגים עיצוביים, עם ניתוח סנטימנט נקי וברור.</div>', unsafe_allow_html=True)
    
    top_symbols = symbols_list[:4]
    cols = st.columns(2)
    
    for i, sym in enumerate(top_symbols):
        with cols[i % 2]: 
            st.markdown(f"### 🏢 מוקד מודיעין: {sym}")
            try:
                news = yf.Ticker(sym).news
                if news:
                    for article in news[:2]:
                        title = article.get('title', '')
                        if not title and 'content' in article: title = article['content'].get('title', 'עדכון שוק')
                            
                        publisher = article.get('publisher', '')
                        if not publisher and 'content' in article: publisher = article['content'].get('provider', {}).get('displayName', 'מקור עולמי')
                            
                        link = article.get('link', '#')
                        if not link and 'content' in article: link = article['content'].get('clickThroughUrl', {}).get('url', '#')
                        
                        ai_report = advanced_ai_analysis(title, sym)
                        
                        # שימוש ברכיבי Streamlit מובנים למניעת באג ה- </div>
                        with st.container(border=True):
                            st.caption(f"מקור: {publisher} | [קרא את המקור באנגלית]({link})")
                            st.markdown(f"##### {title}")
                            st.info(ai_report)
                else:
                    st.info(f"אין חדשות דרמטיות עבור {sym} כעת.")
            except:
                st.error("חיבור למקור החדשות עמוס.")
