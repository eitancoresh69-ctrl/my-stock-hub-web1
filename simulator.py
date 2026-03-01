# simulator.py — סוכני מסחר חכמים

import streamlit as st
import pandas as pd

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ffc107;">'
                '<b>⚡ סוכן יומי (Momentum):</b> סריקת הזדמנויות בבורסה.</div>', 
                unsafe_allow_html=True)
    
    # --- התיקון הקריטי לשגיאה מהתמונה ---
    msg = "" 
    
    if df_all.empty:
        st.warning("אין נתונים לסריקה כרגע.")
        return

    # הסוכן סורק את כל רשימת ה-SCAN_LIST (ת"א, סחורות, עולם)
    # מחפש מניות ב"מכירת יתר" (RSI נמוך) או עם ציון AI גבוה מאוד
    opportunities = df_all[
        (df_all["RSI"] < 35) | (df_all["Score"] >= 5)
    ].sort_values("RSI")

    if not opportunities.empty:
        st.write("🎯 **הזדמנויות שזוהו בזמן אמת:**")
        st.dataframe(
            opportunities[["Symbol", "Price", "RSI", "Action", "AI_Logic"]],
            use_container_width=True, hide_index=True
        )
        msg = f"הסוכן זיהה {len(opportunities)} הזדמנויות כניסה בנכסים שונים."
    else:
        msg = "לא נמצאו הזדמנויות מומנטום קריטיות כרגע."

    # הדפסה בטוחה של הודעת ה-AI (שורה 346 המקורית)
    if msg:
        st.success(f"🤖 **סוכן יומי:** {msg}")

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;">'
                '<b>📈 סוכן ערך (Long Term):</b> חברות איכותיות לטווח ארוך.</div>', 
                unsafe_allow_html=True)
    
    # סינון למניות "זהב" (ציון 5 ומעלה)
    value_picks = df_all[df_all["Score"] >= 5].sort_values("Score", ascending=False)
    
    if not value_picks.empty:
        st.dataframe(
            value_picks[["Symbol", "Price", "Score", "RevGrowth", "Action"]],
            use_container_width=True, hide_index=True
        )
        st.info("💡 המלצת AI: אלו המניות החזקות ביותר בתיק להחזקה ארוכה.")
    else:
        st.warning("לא נמצאו מניות העונות לקריטריון 'ערך גבוה' כרגע.")
