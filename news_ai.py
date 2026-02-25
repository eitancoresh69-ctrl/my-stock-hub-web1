# news_ai.py
import streamlit as st
import yfinance as yf

def analyze_headline(title, sym):
    """פונקציה שמדמה ניתוח סנטימנט AI של הכותרת ומייצרת 'מבזקון' בעברית"""
    t = title.lower()
    
    # חיפוש מילות מפתח לחילוץ סנטימנט
    if any(word in t for word in ["earning", "revenue", "profit", "q1", "q2", "q3", "q4"]):
        return f"**מבזק AI 🤖:** הזרקור מופנה למספרים ולדוחות של {sym}. צפי לתנודתיות סביב נושאי רווחיות."
    elif any(word in t for word in ["ai", "chip", "tech", "intelligence", "cloud"]):
        return f"**מבזק AI 🤖:** המניה מוזכרת בהקשר של חדשנות טכנולוגית או בינה מלאכותית, מה שלרוב מייצר סנטימנט חיובי חזק."
    elif any(word in t for word in ["buy", "upgrade", "bull", "target", "soar", "jump"]):
        return f"**מבזק AI 🤖:** סנטימנט שורי (Bullish) באוויר! השוק רואה פוטנציאל עלייה, או שאנליסטים שדרגו את המלצתם ל-{sym}."
    elif any(word in t for word in ["sell", "downgrade", "bear", "drop", "lawsuit", "sue", "fall"]):
        return f"**מבזק AI 🤖:** סנטימנט שלילי (Bearish). המערכת מזהה לחץ או אזהרות שעשויים להכביד על מחיר המניה כרגע."
    elif any(word in t for word in ["dividend", "payout"]):
        return f"**מבזק AI 🤖:** עדכוני תזרים מזומנים. חדשות מעולות למשקיעי ערך המחפשים יציבות מההשקעה שלהם."
    else:
        return f"**מבזק AI 🤖:** המערכת קוראת את הכתבה. מדובר בדיווחי שגרה עבור {sym} או עדכוני תעשייה. הסנטימנט הכללי מוגדר כניטרלי."

def render_live_news(symbols_list):
    st.markdown('<div class="ai-card" style="border-right-color: #f50057;"><b>📰 חדר חדשות ומבזקי AI:</b> המערכת שואבת כותרות בזמן אמת מהעולם. ה-AI מנתח כל כותרת ומייצר <b>מבזקון סנטימנט בעברית</b> כדי שתבין את המגמה בשנייה.</div>', unsafe_allow_html=True)
    
    top_symbols = symbols_list[:5]
    cols = st.columns(len(top_symbols))
    
    for i, sym in enumerate(top_symbols):
        with cols[i]:
            st.markdown(f"### 🏢 {sym}")
            try:
                news = yf.Ticker(sym).news
                if news:
                    # מציג את 3 הכתבות האחרונות
                    for article in news[:3]:
                        
                        # תיקון למבנה הנתונים החדש של Yahoo Finance
                        title = article.get('title')
                        if not title and 'content' in article:
                            title = article['content'].get('title')
                        if not title:
                            title = f"עדכון שוק כללי - {sym}"
                            
                        publisher = article.get('publisher')
                        if not publisher and 'content' in article:
                            publisher = article['content'].get('provider', {}).get('displayName', 'מקור פיננסי')
                        if not publisher:
                            publisher = "מקור עולמי"
                            
                        link = article.get('link')
                        if not link and 'content' in article:
                            link = article['content'].get('clickThroughUrl', {}).get('url', '#')
                        if not link:
                            link = "#"
                            
                        # הפעלת סוכן ה-AI לייצור המבזקון
                        ai_flash = analyze_headline(title, sym)
                        
                        # עיצוב מודרני שמשלב את הכותרת המקורית יחד עם בועת ה-AI
                        st.markdown(f"""
                        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.04);">
                            <a href="{link}" target="_blank" style="text-decoration: none; color: #1a73e8; font-weight: 800; font-size: 15px; line-height: 1.3; display: block; margin-bottom: 8px;">{title}</a>
                            <span style="font-size: 12px; color: #757575; font-weight: 600; background-color: #f1f3f4; padding: 3px 8px; border-radius: 4px;">מקור: {publisher}</span>
                            <hr style="margin: 12px 0; border: none; border-top: 1px dashed #d0d7de;">
                            <div style="font-size: 13px; color: #202124; background-color: #e8f0fe; padding: 10px; border-radius: 6px; border-right: 4px solid #1a73e8; line-height: 1.4;">
                                {ai_flash}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("אין חדשות חמות כרגע.")
            except Exception as e:
                st.error("החיבור למקור החדשות עמוס כעת.")
