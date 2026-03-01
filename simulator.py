import streamlit as st
import storage

def render_day_trade_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ffc107;"><b>⚡ סוכן יומי:</b></div>', unsafe_allow_html=True)
    
    msg = "" # אתחול המשתנה למניעת השגיאה משורה 346
    
    if df_all.empty:
        st.warning("אין נתונים לסריקה.")
        return

    # סריקת הזדמנויות
    opps = df_all[(df_all["RSI"] < 35) | (df_all["Score"] >= 5)].copy()

    if not opps.empty:
        st.write("🎯 **המלצות הסוכן:**")
        st.dataframe(opps[["Symbol", "Price", "RSI", "Action"]], use_container_width=True)
        
        # בחירת מניה לקנייה מדומה
        col1, col2 = st.columns([2, 1])
        with col1:
            to_buy = st.selectbox("בחר נכס לקנייה ע\"י הסוכן:", opps["Symbol"].tolist(), key="day_agent_sel")
        with col2:
            if st.button("🚀 הסוכן מבצע קנייה", key="day_agent_btn"):
                price = opps[opps["Symbol"] == to_buy]["Price"].values[0]
                storage.save_agent_trade(to_buy, price, "Daily Momentum")
                st.success(f"הסוכן הוסיף את {to_buy} לתיק המדומה!")
        msg = f"זוהו {len(opps)} הזדמנויות כניסה."
    else:
        msg = "לא נמצאו הזדמנויות מומנטום כרגע."

    if msg:
        st.success(msg) # שורה 346 המקורית כעת בטוחה

def render_value_agent(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>📈 סוכן ערך:</b></div>', unsafe_allow_html=True)
    value_picks = df_all[df_all["Score"] >= 5].copy()
    
    if not value_picks.empty:
        st.dataframe(value_picks[["Symbol", "Price", "Score"]], use_container_width=True)
        to_buy_val = st.selectbox("בחר נכס להוספה לתיק ערך:", value_picks["Symbol"].tolist(), key="val_agent_sel")
        if st.button("💰 הוסף לתיק ערך", key="val_agent_btn"):
            price = value_picks[value_picks["Symbol"] == to_buy_val]["Price"].values[0]
            storage.save_agent_trade(to_buy_val, price, "Long Term Value")
            st.success(f"סוכן הערך הוסיף את {to_buy_val}!")
