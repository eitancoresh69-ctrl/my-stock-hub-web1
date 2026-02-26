# failsafes_ai.py - מנגנון הגנה וניתוק מתקדם (הדמייה מלאה - ללא ברוקר)
import streamlit as st
import pandas as pd
from datetime import datetime

def _log(msg):
    if 'failsafe_log' not in st.session_state:
        st.session_state.failsafe_log = []
    st.session_state.failsafe_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def render_failsafes():
    st.markdown('<div class="ai-card" style="border-right-color: #d32f2f;"><b>🛡️ מנגנון הגנה וניתוק (הדמייה)</b> — רשת ביטחון שכבות-על-שכבות: Kill Switch, Circuit Breaker, Stop Loss אוטומטי. פועל ללא חיבור לברוקר.</div>', unsafe_allow_html=True)

    # אתחול session state
    for key, default in [
        ('kill_switch_active', False),
        ('failsafe_log', []),
        ('daily_loss_pct', 0.0),
        ('circuit_breaker_triggered', False),
        ('trading_paused_until', None)
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # --- סטטוס מערכת ---
    if st.session_state.kill_switch_active:
        st.error("🚨 **מתג ההשמדה פעיל!** כל המסחר מושהה. לחץ 'איפוס מערכת' כדי לחזור לפעולה.")
    elif st.session_state.circuit_breaker_triggered:
        st.warning("⚡ **Circuit Breaker הופעל!** הגבלת מסחר יומי בתוקף עקב הפסד חריג.")
    else:
        st.success("✅ **מערכת ההגנה תקינה** — כל המנגנונים פעילים ומוכנים.")

    # --- מדדים ---
    st.subheader("📊 ניטור סיכונים בזמן אמת")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📉 הפסד יומי", f"{st.session_state.daily_loss_pct:.1f}%", delta_color="inverse")
    m2.metric("🛡️ Kill Switch", "🔴 פעיל" if st.session_state.kill_switch_active else "🟢 כבוי")
    m3.metric("⚡ Circuit Breaker", "🔴 הופעל" if st.session_state.circuit_breaker_triggered else "🟢 תקין")
    m4.metric("📝 אירועי אבטחה", len(st.session_state.failsafe_log))

    # --- הגדרות סף ---
    st.subheader("⚙️ הגדרות הגנה אוטומטית")
    col1, col2 = st.columns(2)
    with col1:
        max_daily_loss = st.slider("🚫 הפסד יומי מקסימלי (%) לפני עצירה", 1.0, 20.0, 5.0, 0.5, key="fs_max_loss")
        max_position = st.slider("💼 מקסימום פוזיציה בודדת (% מהתיק)", 5.0, 50.0, 20.0, 5.0, key="fs_max_pos")
        stop_loss_pct = st.slider("🛑 Stop Loss אוטומטי לפוזיציה (%)", 1.0, 15.0, 5.0, 0.5, key="fs_sl")
    with col2:
        take_profit_pct = st.slider("🎯 Take Profit אוטומטי (%)", 1.0, 30.0, 10.0, 0.5, key="fs_tp")
        vix_halt = st.slider("😨 השהה מסחר אם VIX עולה על:", 20, 80, 40, 5, key="fs_vix")
        max_open_positions = st.number_input("📊 מקסימום פוזיציות פתוחות בו-זמנית", 1, 20, 5, key="fs_max_open")

    # --- כפתורי בדיקה ---
    st.subheader("🔧 סימולציות ובדיקות")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("📉 הדמה הפסד 3%", key="fs_sim3"):
            st.session_state.daily_loss_pct = 3.0
            _log("הדמיית הפסד יומי: -3.0%")
            if 3.0 >= max_daily_loss:
                st.session_state.circuit_breaker_triggered = True
                _log("⚡ Circuit Breaker הופעל!")
            st.rerun()
    with b2:
        if st.button("📉 הדמה הפסד 7%", key="fs_sim7"):
            st.session_state.daily_loss_pct = 7.0
            st.session_state.circuit_breaker_triggered = True
            _log("🚨 הפסד קריטי 7.0% — Circuit Breaker!")
            st.rerun()
    with b3:
        if st.button("😨 הדמה VIX 45", key="fs_simvix"):
            _log(f"⚠️ VIX הגיע ל-45 (מעל הסף {vix_halt}) — המסחר מושהה!")
            st.session_state.circuit_breaker_triggered = True
            st.rerun()
    with b4:
        if st.button("🔄 איפוס נתוני יום", key="fs_reset_day"):
            st.session_state.daily_loss_pct = 0.0
            st.session_state.circuit_breaker_triggered = False
            _log("✅ נתוני יום אופסו.")
            st.rerun()

    # --- מתג השמדה (Kill Switch) ---
    st.divider()
    st.subheader("☢️ מתג השמדה (Kill Switch)")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if not st.session_state.kill_switch_active:
            if st.button("🚨 הפעל מתג השמדה — עצור הכל!", type="primary", key="fs_kill"):
                st.session_state.kill_switch_active = True
                # סוגר את כל פוזיציות הסוכנים
                for k in ['val_portfolio', 'day_portfolio', 'div_portfolio', 'ins_portfolio', 'deep_portfolio']:
                    if k in st.session_state:
                        st.session_state[k] = []
                _log("🚨 KILL SWITCH הופעל! כל הפוזיציות נסגרו למזומן!")
                st.rerun()
        else:
            if st.button("✅ איפוס מלא — חזרה לפעולה נורמלית", key="fs_reset_kill"):
                st.session_state.kill_switch_active = False
                st.session_state.circuit_breaker_triggered = False
                st.session_state.daily_loss_pct = 0.0
                _log("✅ המערכת אופסה וחזרה לפעולה מלאה.")
                st.rerun()

    with col_k2:
        st.markdown("""
        **מה קורה כשמתג ההשמדה מופעל?**

        🔴 כל סוכני ה-AI נעצרים מיידית  
        🔴 כל הפוזיציות הפתוחות נסגרות למזומן (וירטואלית)  
        🔴 לא ניתן לפתוח פקודות חדשות  
        🔴 Circuit Breaker מופעל במקביל  
        🟢 כל ההיסטוריה והנתונים נשמרים  
        🟢 ניתן לאפס ידנית בלחיצה אחת
        """)

    # --- כללים נוספים ---
    st.subheader("📋 כללי הגנה נוספים")
    r1, r2 = st.columns(2)
    with r1:
        st.toggle("🔒 מניעת מסחר Pre-Market (לפני 9:30)", value=True, key="fs_no_premarket")
        st.toggle("🔒 מניעת מסחר After-Hours (אחרי 16:00)", value=True, key="fs_no_afterhours")
        st.toggle("⚠️ אישור לעסקאות גדולות (מעל $5,000)", value=True, key="fs_big_confirm")
    with r2:
        st.toggle("📊 ניטור VIX אוטומטי", value=True, key="fs_vix_monitor")
        st.toggle("🔄 Rebalance אוטומטי בסוף יום", value=False, key="fs_rebalance")
        st.toggle("📱 שלח התראה לטלגרם בעצירה", value=False, key="fs_telegram_alert")

    # --- יומן ---
    if st.session_state.failsafe_log:
        with st.expander(f"📋 יומן אירועי אבטחה ({len(st.session_state.failsafe_log)} אירועים)"):
            for event in st.session_state.failsafe_log[:40]:
                icon = "🔴" if any(x in event for x in ["KILL", "קריטי", "Circuit"]) else "🟡" if "אזהרה" in event or "הדמ" in event else "🟢"
                st.markdown(f"{icon} `{event}`")
            if st.button("🗑️ נקה יומן", key="fs_clear_log"):
                st.session_state.failsafe_log = []
                st.rerun()
