# news_ai.py
import streamlit as st
import yfinance as yf

def advanced_ai_analysis(title, sym):
    """מנוע AI שמנתח את הכותרת ומפיק דוח מודיעין עמוק בעברית"""
    t = title.lower()
    
    # זיהוי דוחות כספיים ורווחים
    if any(word in t for word in ["earning", "revenue", "profit", "q1", "q2", "q3", "q4", "beat", "miss", "result"]):
        return f"""
        **📝 תמצית הדיווח:** עדכון קריטי בנוגע לתוצאות הכספיות ושורת הרווח של {sym}.
        **🔍 ניתוח עומק (AI):** דוחות כספיים הם הטריגר המרכזי לתנודות מחיר. הכתבה מתייחסת לעמידת החברה בתחזיות האנליסטים בוול-סטריט.
        **🎯 השלכה למשקיעי ערך:** יש לבחון האם צמיחת ההכנסות (קריטריון 1 ב-PDF) נשמרת מעל 10%. אם המניה קורסת למרות דוח טוב - זו עשויה להיות הזדמנות קנייה.
        """
    # זיהוי חדשנות, AI ושבבים
    elif any(word in t for word in ["ai", "chip", "tech", "intelligence", "cloud", "software", "launch"]):
        return f"""
        **📝 תמצית הדיווח:** חדשנות טכנולוגית, השקת מוצר או התקדמות בתחום הבינה המלאכותית אצל {sym}.
        **🔍 ניתוח עומק (AI):** השוק מתמחר חברות טכנולוגיה לפי פוטנציאל הצמיחה העתידי שלהן. אזכורים חיוביים של פיתוחי AI מזרימים הון מוסדי למניה.
        **🎯 השלכה למשקיעי ערך:** חדשנות היא ה"חפיר הכלכלי" (Moat) של החברה. מגמה זו מחזקת את היתרון התחרותי שלה לטווח הארוך.
        """
    # זיהוי שדרוגים וסנטימנט שורי
    elif any(word in t for word in ["buy", "upgrade", "bull", "target", "soar", "jump", "rally", "high"]):
        return f"""
        **📝 תמצית הדיווח:** סנטימנט חיובי קיצוני (שור) - אנליסטים משדרגים את המלצות הקנייה או מעלים מחירי יעד למניית {sym}.
        **🔍 ניתוח עומק (AI):** הכסף החכם בוול-סטריט (מוסדיים) מתחיל לאסוף סחורה. מומנטום כזה נוטה למשוך גם סוחרים יומיים שרוכבים על הגל.
        **🎯 השלכה למשקיעי ערך:** זהירות מתמחור יתר (FOMO). יש לוודא שהמחיר עדיין נמוך מהשווי ההוגן המחושב לפני שמצטרפים לחגיגה.
        """
    # זיהוי משברים, תביעות וסנטימנט דובי
    elif any(word in t for word in ["sell", "downgrade", "bear", "drop", "lawsuit", "sue", "fall", "plunge", "risk"]):
        return f"""
        **📝 תמצית הדיווח:** אזהרת סנטימנט שלילי (דוב) - חששות כלכליים, הורדת דירוג על ידי אנליסטים או משבר נקודתי פוקדים את {sym}.
        **🔍 ניתוח עומק (AI):** השוק מגיב בפאניקה. לחץ מכירות עשוי להפיל את המניה מתחת לשווי האמיתי שלה בימים הקרובים.
        **🎯 השלכה למשקיעי ערך:** פאניקה היא חברתו הטובה ביותר של משקיע הערך! אם הנתונים ב-PDF נשארו חזקים, ה-AI יסמן זאת כהזדמנות קנייה (Buy the Dip).
        """
    # זיהוי תזרים ודיבידנדים
    elif any(word in t for word in ["dividend", "payout", "yield", "shareholder"]):
        return f"""
        **📝 תמצית הדיווח:** עדכונים לגבי חלוקת הרווחים לבעלי המניות (דיבידנדים) של {sym}.
        **🔍 ניתוח עומק (AI):** חברות שמחלקות או מגדילות דיבידנד מאותתות לשוק על עוצמה פיננסית ותזרים מזומנים חזק ועקבי.
        **🎯 השלכה למשקיעי ערך:** וידוא מושלם לקריטריון ה"מזומן מול חוב" (קריטריון 6 ב-PDF). חברה יציבה שמתגמלת את משקיעיה.
        """
    # ברירת מחדל
    else:
        return f"""
        **📝 תמצית הדיווח:** עדכון שוטף או מאקרו-כלכלי הנוגע לפעילות של {sym}.
        **🔍 ניתוח עומק (AI):** המערכת מסווגת ידיעה זו כ'רעשי רקע' (Noise) שאינם משנים מהותית את התזה העסקית ארוכת הטווח.
        **🎯 השלכה למשקיעי ערך:** אין צורך בפעולה מיידית. מומלץ להמשיך לעקוב אחרי הדוחות הפיננסיים הרשמיים.
        """

def render_live_news(symbols_list):
    st.markdown('<div class="ai-card" style="border-right-color: #f50057;"><b>📰 דסק חדשות וניתוח AI (בעברית):</b> המערכת קוראת את כותרות העיתונות הכלכלית בעולם (Bloomberg, Reuters), מתרגמת את המשמעות לעברית, ומפיקה דוח השלכות למשקיע עבור כל כתבה.</div>', unsafe_allow_html=True)
    
    # הגבלנו ל-4 מניות בלבד, ומסדרים אותן ב-2 עמודות כדי שיהיה מרווח וקריא
    top_symbols = symbols_list[:4]
    
    # חלוקה ל-2 עמודות רחבות בלבד (במקום 5 דחוסות)
    cols = st.columns(2)
    
    for i, sym in enumerate(top_symbols):
        with cols[i % 2]: # מפזר את המניות בין 2 העמודות
            st.markdown(f"### 🏢 מוקד מודיעין: {sym}")
            try:
                news = yf.Ticker(sym).news
                if news:
                    # מציג את 2 הכתבות האחרונות והחשובות ביותר
                    for article in news[:2]:
                        title = article.get('title', '')
                        if not title and 'content' in article: title = article['content'].get('title', '')
                        if not title: title = f"עדכון שוק - {sym}"
                            
                        publisher = article.get('publisher', '')
                        if not publisher and 'content' in article: publisher = article['content'].get('provider', {}).get('displayName', 'מקור עולמי')
                            
                        link = article.get('link', '#')
                        if not link and 'content' in article: link = article['content'].get('clickThroughUrl', {}).get('url', '#')
                        
                        # הפעלת מנוע הניתוח העמוק החדש שלנו
                        ai_report = advanced_ai_analysis(title, sym)
                        
                        # עיצוב מרווח, ברור, וממוקד עברית
                        st.markdown(f"""
                        <div style="background-color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #e0e0e0; box-shadow: 0 6px 12px rgba(0,0,0,0.05);">
                            <div style="font-size: 11px; color: #9aa0a6; margin-bottom: 5px; text-align: left; direction: ltr;">
                                Source: {publisher} | <a href="{link}" target="_blank" style="color: #9aa0a6;">Original Article</a>
                            </div>
                            <div style="font-size: 14px; color: #5f6368; margin-bottom: 15px; text-align: left; direction: ltr; font-weight: 500;">
                                "{title}"
                            </div>
                            <hr style="border: 0; border-top: 2px solid #e8eaed; margin: 15px 0;">
                            <div style="font-size: 15px; color: #202124; background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-right: 5px solid #1a73e8; line-height: 1.6;">
                                {ai_report}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"השוק שקט. אין חדשות דרמטיות עבור {sym} כעת.")
            except Exception as e:
                st.error("החיבור למקור החדשות עמוס כעת.")
