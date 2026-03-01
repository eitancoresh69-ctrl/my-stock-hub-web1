# simulator.py — סוכני מסחר עם יכולת ניהול תיק מדומה

import streamlit as st
import pandas as pd
from datetime import datetime

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ffc107;">'
                '<b>⚡ סוכן יומי (Momentum Agent):</b></div>', unsafe_allow_html=True)
    
    # --- תיקון השגיאה מהתמונה ---
    msg = "" 
    
    if df_all.empty:
        st.warning("אין נתונים לסריקה.")
        return

    # לוגיקת סריקה
    opps = df_all[(df_all["RSI"] < 35) | (df_all["Score"] >= 5)].copy()

    if not opps.empty:
        st.write("🎯 **המלצות הסוכן:**")
        # בחירת מניה לביצוע פעולה מדומה
        sel_sym = st.selectbox("בחר מניה לביצוע עסקת סוכן:", opps["Symbol"].tolist(), key="agent_day_sel")
        
        if st.button("🚀 הסוכן קונה לתיק המדומי", key="day_agent_buy"):
            row = opps[opps["Symbol"] == sel_sym].iloc[0]
            new_trade = {
                "Symbol": sel_sym,
                "Type": "Daily Momentum",
                "Price": row["Price"],
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Agent": "Daily Agent"
            }
            if "agent_portfolio" not in st.session_state:
                st.session_state.agent_portfolio = []
            st.session_state.agent_portfolio.append(new_trade)
            st.success(f"הסוכן הוסיף את {sel_sym} לתיק המדומה!")
            # כאן אמורה להיות קריאה ל-storage.save() אם קיים
        
        st.dataframe(opps[["Symbol", "Price", "RSI", "Action"]], use_container_width=True)
        msg = f"נמצאו {len(opps)} הזדמנויות."
    else:
        msg = "סריקה הושלמה - אין מומנטום קריטי."

    if msg:
        st.info(f"🤖 {msg}")

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;">'
                '<b>📈 סוכן ערך (Value Agent):</b></div>', unsafe_allow_html=True)
    
    value_picks = df_all[df_all["Score"] >= 5].copy()
    
    if not value_picks.empty:
        sel_sym = st.selectbox("בחר מניה להחזקה ארוכה:", value_picks["Symbol"].tolist(), key="agent_val_sel")
        
        if st.button("💰 הוסף לתיק ערך מדומה", key="val_agent_buy"):
            row = value_picks[value_picks["Symbol"] == sel_sym].iloc[0]
            new_trade = {
                "Symbol": sel_sym,
                "Type": "Long Term Value",
                "Price": row["Price"],
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Agent": "Value Agent"
            }
            if "agent_portfolio" not in st.session_state:
                st.session_state.agent_portfolio = []
            st.session_state.agent_portfolio.append(new_trade)
            st.success(f"סוכן הערך קנה את {sel_sym}!")
            
        st.dataframe(value_picks[["Symbol", "Price", "Score", "RevGrowth"]], use_container_width=True)
