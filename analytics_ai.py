# analytics_ai.py
import streamlit as st
import yfinance as yf
import pandas as pd

def render_analytics_dashboard():
    st.markdown('<div class="ai-card" style="border-right-color: #ff5722;"><b>📊 מרכז אנליטיקה מתקדמת:</b> מפת חום המציגה לאן זורם "הכסף החכם" בסקטורים השונים, ויומן אירועי מאקרו קריטיים שעלולים לטלטל את השוק כולו.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗺️ מפת חום ענפית (Sectors)")
        st.write("ביצועי הסקטורים המובילים (מבוסס על תעודות סל):")
        
        # תעודות הסל המייצגות את הסקטורים בוול סטריט
        sectors = {
            "טכנולוגיה (XLK)": "XLK",
            "פיננסים (XLF)": "XLF",
            "אנרגיה (XLE)": "XLE",
            "בריאות (XLV)": "XLV",
            "צריכה מחזורית (XLY)": "XLY"
        }
        
        rows = []
        with st.spinner('מחשב ביצועי סקטורים...'):
            for name, ticker in sectors.items():
                try:
                    t = yf.Ticker(ticker)
                    hist = t.history(period="5d")
                    if not hist.empty:
                        change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100
                        trend = "🟢 חיובי" if change > 0 else "🔴 שלילי"
                        rows.append({"סקטור": name, "שינוי יומי": change, "מגמה": trend})
                except: pass
        
        if rows:
            df_sectors = pd.DataFrame(rows)
            df_sectors = df_sectors.sort_values(by="שינוי יומי", ascending=False)
            
            st.dataframe(
                df_sectors,
                column_config={
                    "סקטור": "סקטור",
                    "שינוי יומי": st.column_config.NumberColumn("שינוי (%)", format="%.2f%%"),
                    "מגמה": "מגמה (כסף חכם)"
                },
                use_container_width=True, hide_index=True
            )
            
            st.info("💡 **תובנת AI:** חפש מניות זהב מהסקטור שמוביל את השוק. 'הכסף החכם' נוטה לזרום לסקטורים עם מומנטום חיובי ברור, וזה מגדיל את סיכויי ההצלחה של העסקה.")

    with col2:
        st.markdown("### 📅 יומן אירועי מאקרו (Calendar)")
        st.write("אירועים קרובים שעשויים להכתיב את כיוון הבורסה:")
        
        # יומן אירועי מאקרו מרכזיים
        events = [
            {"תאריך": "12 לחודש", "אירוע": "מדד המחירים לצרכן (CPI) - אינפלציה", "חשיבות": "⭐⭐⭐⭐⭐", "צפי": "תנודתיות גבוהה. אינפלציה גבוהה מהצפי תפיל את מניות הטכנולוגיה."},
            {"תאריך": "18 לחודש", "אירוע": "החלטת הריבית של הפד (FED)", "חשיבות": "⭐⭐⭐⭐⭐", "צפי": "קריטי. השוק מתמחר סביבת ריבית גבוהה. כל הפתעה תשנה את המגמה."},
            {"תאריך": "שישי הראשון בחודש", "אירוע": "דוח תעסוקה אמריקאי (NFP)", "חשיבות": "⭐⭐⭐⭐", "צפי": "שוק עבודה חזק עשוי לעכב הורדות ריבית, מה שיחזק את הדולר."},
            {"תאריך": "אמצע החודש", "אירוע": "פתיחת עונת הדוחות (בנקים)", "חשיבות": "⭐⭐⭐", "צפי": "הבנקים נותנים את הטון לגבי בריאות הצרכן האמריקאי לקראת שאר הדוחות."}
        ]
        
        for e in events:
            st.markdown(f"""
            <div style="background-color: white; padding: 12px; border-radius: 8px; margin-bottom: 12px; border-right: 4px solid #ff9800; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 15px; font-weight: bold; color: #202124;">{e['אירוע']} <span style="font-size: 12px; color: #757575;">({e['תאריך']})</span></div>
                <div style="font-size: 12px; color: #d32f2f; margin-bottom: 5px;">חשיבות: {e['חשיבות']}</div>
                <div style="font-size: 13px; color: #1a73e8; font-weight: 600;">ניתוח AI: <span style="color: #3c4043; font-weight: 400;">{e['צפי']}</span></div>
            </div>
            """, unsafe_allow_html=True)
