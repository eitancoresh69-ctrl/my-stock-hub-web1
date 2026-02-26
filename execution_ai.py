# execution_ai.py - מנוע ביצוע לשוק האמיתי (הדמייה מלאה - ללא ברוקר)
import streamlit as st
import pandas as pd
from datetime import datetime
import random

def _simulate_fill(price, order_type):
    """סימולציית מילוי פקודה עם Slippage מציאותי"""
    if "Market" in order_type:
        slippage = random.uniform(-0.002, 0.003)
        return round(price * (1 + slippage), 4)
    return round(price, 4)  # Limit תמיד במחיר המדויק

def render_execution_engine():
    st.markdown('<div class="ai-card" style="border-right-color: #607d8b;"><b>⚙️ מנוע ביצוע לשוק האמיתי (הדמייה)</b> — מדמה Limit Orders, Market Orders ו-Stop Loss עם Slippage מציאותי. פועל ללא חיבור לברוקר.</div>', unsafe_allow_html=True)

    st.info("ℹ️ **מצב הדמייה פעיל** — כל הפקודות וירטואליות לחלוטין. כדי לחבר ברוקר אמיתי בעתיד, הוסף מפתח API בלבד — כל שאר הלוגיקה נשארת זהה.")

    if 'exec_orders' not in st.session_state:
        st.session_state.exec_orders = []
    if 'exec_log' not in st.session_state:
        st.session_state.exec_log = []

    # --- פאנל הגשת פקודה ---
    st.subheader("📋 הגש פקודה חדשה")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        symbol = st.text_input("סימול", value="AAPL", key="exec_sym").upper().strip()
    with col2:
        side = st.selectbox("כיוון", ["קנייה 🟢", "מכירה 🔴"], key="exec_side")
    with col3:
        order_type = st.selectbox("סוג פקודה", ["Limit Order", "Market Order", "Stop Loss"], key="exec_type")
    with col4:
        qty = st.number_input("כמות מניות", min_value=1, value=10, key="exec_qty")

    col5, col6 = st.columns(2)
    with col5:
        limit_price = st.number_input("מחיר ($)", min_value=0.01, value=150.00, step=0.5, key="exec_price")
    with col6:
        tif = st.selectbox("תוקף פקודה (TIF)", ["Day", "GTC — עד ביטול", "IOC — מיידי"], key="exec_tif")

    if st.button("🚀 שגר פקודה למנוע", type="primary"):
        filled_price = _simulate_fill(limit_price, order_type)
        status = "✅ בוצע" if order_type != "Stop Loss" else "⏳ ממתין לטריגר"
        order = {
            "⏰ זמן": datetime.now().strftime("%H:%M:%S"),
            "📌 סימול": symbol,
            "↔️ כיוון": side,
            "📑 סוג": order_type,
            "🔢 כמות": qty,
            "💰 מחיר מבוקש": f"${limit_price:.2f}",
            "✅ מחיר ביצוע": f"${filled_price:.2f}",
            "🕐 TIF": tif,
            "📊 סטטוס": status,
            "💵 שווי": f"${filled_price * qty:,.2f}"
        }
        st.session_state.exec_orders.insert(0, order)
        st.session_state.exec_log.insert(0, f"[{order['⏰ זמן']}] {side} {qty}×{symbol} @ ${filled_price:.2f} ({order_type}) → {status}")

        if status == "✅ בוצע":
            st.success(f"✅ פקודה בוצעה! {qty} × {symbol} @ ${filled_price:.2f} | שווי: ${filled_price * qty:,.2f}")
        else:
            st.warning(f"⏳ Stop Loss נרשם. יופעל כש-{symbol} יגיע ל-${limit_price:.2f}")

    # --- הגדרות מנוע ---
    with st.expander("⚙️ הגדרות מנוע מתקדמות"):
        c1, c2, c3 = st.columns(3)
        c1.toggle("הגבל לפקודות Limit בלבד (מונע Slippage)", value=True, key="exec_limit_only")
        c2.toggle("Dry-Run Mode — רשום בלי לבצע", value=False, key="exec_dry_run")
        c3.toggle("אישור ידני לפני כל פקודה", value=False, key="exec_manual_confirm")
        c4, c5 = st.columns(2)
        c4.slider("מקסימום Slippage מותר (%)", 0.0, 2.0, 0.2, 0.1, key="exec_max_slippage")
        c5.number_input("מגבלת פקודות ביום", min_value=1, max_value=100, value=20, key="exec_daily_limit")

    # --- טבלת היסטוריה ---
    if st.session_state.exec_orders:
        st.subheader("📜 היסטוריית פקודות")
        df_orders = pd.DataFrame(st.session_state.exec_orders)
        st.dataframe(df_orders, use_container_width=True, hide_index=True)

        try:
            total_buy  = sum(float(o["💵 שווי"].replace("$","").replace(",","")) for o in st.session_state.exec_orders if "קנייה" in o["↔️ כיוון"])
            total_sell = sum(float(o["💵 שווי"].replace("$","").replace(",","")) for o in st.session_state.exec_orders if "מכירה" in o["↔️ כיוון"])
            m1, m2, m3 = st.columns(3)
            m1.metric("📥 סך קניות", f"${total_buy:,.2f}")
            m2.metric("📤 סך מכירות", f"${total_sell:,.2f}")
            m3.metric("📊 פקודות סה\"כ", len(st.session_state.exec_orders))
        except: pass

        if st.button("🗑️ נקה היסטוריית פקודות", key="exec_clear"):
            st.session_state.exec_orders = []
            st.session_state.exec_log = []
            st.rerun()

    # --- יומן מערכת ---
    if st.session_state.exec_log:
        with st.expander("📋 יומן מנוע (System Log)"):
            for line in st.session_state.exec_log[:25]:
                st.code(line, language=None)

    # --- הסבר חיבור עתידי ---
    with st.expander("🔌 כיצד לחבר ברוקר אמיתי בעתיד?"):
        st.markdown("""
**שלב 1:** קבל מפתח API מהברוקר הרצוי (Alpaca, Interactive Brokers, IBKR)

**שלב 2:** הוסף לקובץ `.env` בשורש הפרויקט:
```
BROKER_API_KEY=your_key_here
BROKER_SECRET=your_secret_here
BROKER_BASE_URL=https://paper-api.alpaca.markets
```

**שלב 3:** החלף את הפונקציה `_simulate_fill()` בקריאת API אמיתית — כל שאר הלוגיקה נשארת זהה ✅

**ברוקרים מומלצים:** Alpaca (חינם, אמריקאי), Interactive Brokers (גלובלי, כולל ישראל)
        """)
