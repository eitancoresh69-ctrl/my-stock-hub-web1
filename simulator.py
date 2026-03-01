# simulator.py — סוכני מסחר חכמים

import streamlit as st
import pandas as pd

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ffc107;">'
                '<b>⚡ סוכן יומי (Momentum):</b> סורק הזדמנויות בבורסה.</div>', 
                unsafe_allow_html=True)
    
    # --- תיקון השגיאה מהתמונה (UnboundLocalError) ---
    msg = "" 
    
    if df_all.empty:
        st.warning("אין נתונים לסריקה כרגע.")
        return

    # סינון מניות במומנטום גבוה (RSI נמוך או פריצת מחיר)
    # הסוכן כעת סורק את כל ה-SCAN_LIST המורחב שלך
    opportunities = df_all[
        (df_all["RSI"] < 35) | (df_all["Score"] >= 5)
    ].sort_values("RSI")

    if not opportunities.empty:
        st.write("🎯 **הזדמנויות שזוהו:**")
        st.dataframe(
            opportunities[["Symbol", "Price", "RSI", "Action"]],
            use_container_width=True, hide_index=True
        )
        msg = f"הסוכן זיהה {len(opportunities)} נכסים בנקודת כניסה מעניינת."
    else:
        msg = "לא נמצאו הזדמנויות מומנטום קריטיות ב-Watchlist כרגע."

    # הדפסה בטוחה של הודעת ה-AI
    if msg:
        st.success(f"🤖 **AI Insight:** {msg}")

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;">'
                '<b>📈 סוכן ערך (Long Term):</b> חיפוש חברות חזקות מתחת לשווי.</div>', 
                unsafe_allow_html=True)
    
    # סינון למניות ערך (ציון גבוה ומכפיל רווח סביר במידה ויש)
    value_picks = df_all[df_all["Score"] >= 5].sort_values("Score", ascending=False)
    
    if not value_picks.empty:
        st.dataframe(
            value_picks[["Symbol", "Price", "Score", "RevGrowth", "Action"]],
            use_container_width=True, hide_index=True
        )
        st.info("💡 המלצה לטווח ארוך: התמקד בחברות עם ציון 5 ומעלה ששומרות על צמיחה.")
    else:
        st.warning("לא נמצאו מניות בציון 'ערך' גבוה כרגע.")
