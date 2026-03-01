# simulator.py — סוכני מסחר עם יכולת ביצוע
import streamlit as st
import storage

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ffc107;"><b>⚡ סוכן יומי:</b></div>', unsafe_allow_html=True)
    msg = "" # תיקון השגיאה מהתמונה
    
    if df_all.empty:
        st.warning("אין נתונים לסריקה.")
        return

    opps = df_all[(df_all["RSI"] < 35) | (df_all["Score"] >= 5)].copy()
    if not opps.empty:
        st.dataframe(opps[["Symbol", "Price", "RSI", "Action"]], use_container_width=True)
        to_buy = st.selectbox("בחר מניה לקנייה ע\"י הסוכן:", opps["Symbol"].tolist(), key="day_sel")
        if st.button("🚀 הסוכן קונה לתיק המדומה", key="btn_day_buy"):
            price = opps[opps["Symbol"] == to_buy]["Price"].values[0]
            storage.save_agent_trade(to_buy, price, "Daily Momentum")
            st.success(f"הסוכן קנה את {to_buy}!")
        msg = f"נמצאו {len(opps)} הזדמנויות."
    
    if msg: st.info(f"🤖 {msg}")

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>📈 סוכן ערך:</b></div>', unsafe_allow_html=True)
    value_picks = df_all[df_all["Score"] >= 5].copy()
    if not value_picks.empty:
        st.dataframe(value_picks[["Symbol", "Price", "Score"]], use_container_width=True)
        to_buy_val = st.selectbox("בחר מניה לתיק הערך:", value_picks["Symbol"].tolist(), key="val_sel")
        if st.button("💰 הוסף לתיק ערך", key="btn_val_buy"):
            price = value_picks[value_picks["Symbol"] == to_buy_val]["Price"].values[0]
            storage.save_agent_trade(to_buy_val, price, "Long Term Value")
            st.success(f"סוכן הערך הוסיף את {to_buy_val}!")
