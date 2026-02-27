# failsafes_ai.py — Kill Switch + Circuit Breaker
import streamlit as st
from datetime import datetime


def _log(msg):
    if "failsafe_log" not in st.session_state:
        st.session_state.failsafe_log = []
    st.session_state.failsafe_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def _stepper(label: str, key: str, min_val, max_val, default, step, unit: str = "%",
             color: str = "#d32f2f"):
    """
    ווידג'ט stepper: לייבל + ➖/➕ + ערך גדול + סליידר לגרירה.
    """
    if key not in st.session_state:
        st.session_state[key] = default

    st.markdown(f"**{label}**")
    c_minus, c_val, c_plus = st.columns([1, 2, 1])

    with c_minus:
        if st.button("➖", key=f"{key}_minus", use_container_width=True):
            st.session_state[key] = max(min_val, round(st.session_state[key] - step, 10))
            st.rerun()
    with c_val:
        disp = (f"{st.session_state[key]:.0f}"
                if isinstance(step, int) or step >= 1
                else f"{st.session_state[key]:.1f}")
        st.markdown(
            f"<div style='text-align:center;font-size:2rem;font-weight:700;"
            f"color:{color};background:#fff3f3;border-radius:10px;"
            f"padding:4px 0;margin:0;'>{disp}{unit}</div>",
            unsafe_allow_html=True,
        )
    with c_plus:
        if st.button("➕", key=f"{key}_plus", use_container_width=True):
            st.session_state[key] = min(max_val, round(st.session_state[key] + step, 10))
            st.rerun()

    new_val = st.slider(
        label, min_val, max_val,
        value=st.session_state[key],
        step=step,
        key=f"{key}_slider",
        label_visibility="collapsed",
    )
    if new_val != st.session_state[key]:
        st.session_state[key] = new_val
        st.rerun()

    return st.session_state[key]


def render_failsafes():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #d32f2f;">'
        '<b>🛡️ מנגנון הגנה:</b> Kill Switch, Circuit Breaker, Stop Loss אוטומטי.</div>',
        unsafe_allow_html=True,
    )

    for key, default in [
        ("kill_switch_active", False), ("failsafe_log", []),
        ("daily_loss_pct", 0.0), ("circuit_breaker_triggered", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state.kill_switch_active:
        st.error("🚨 **מתג ההשמדה פעיל!** כל המסחר מושהה.")
    elif st.session_state.circuit_breaker_triggered:
        st.warning("⚡ **Circuit Breaker הופעל!**")
    else:
        st.success("✅ **מערכת ההגנה תקינה.**")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📉 הפסד יומי", f"{st.session_state.daily_loss_pct:.1f}%", delta_color="inverse")
    m2.metric("🛡️ Kill Switch", "🔴 פעיל" if st.session_state.kill_switch_active else "🟢 כבוי")
    m3.metric("⚡ Circuit Breaker", "🔴 הופעל" if st.session_state.circuit_breaker_triggered else "🟢 תקין")
    m4.metric("📝 אירועי אבטחה", len(st.session_state.failsafe_log))

    # ── הגדרות עם steppers ──────────────────────────────────────
    st.subheader("⚙️ הגדרות הגנה")
    col1, col2, col3 = st.columns(3)

    with col1:
        max_loss = _stepper(
            "🚫 הפסד יומי מקסימלי",
            "fs_maxloss", 1.0, 20.0, 5.0, 0.5,
            unit="%", color="#d32f2f",
        )
        st.caption("⛔ Circuit Breaker מופעל כשמגיעים לערך זה")
        st.markdown("")
        _stepper(
            "🛑 Stop Loss לעסקה",
            "fs_stoploss", 1.0, 15.0, 5.0, 0.5,
            unit="%", color="#e53935",
        )
        st.caption("עצור הפסד אוטומטי לכל פוזיציה בודדת")

    with col2:
        _stepper(
            "🎯 Take Profit",
            "fs_tp", 1.0, 30.0, 10.0, 0.5,
            unit="%", color="#2e7d32",
        )
        st.caption("מכור אוטומטית כשמגיעים לרווח זה")
        st.markdown("")
        _stepper(
            "💼 פוזיציה מקסימלית",
            "fs_maxpos", 5.0, 50.0, 20.0, 5.0,
            unit="%", color="#1565c0",
        )
        st.caption("אחוז מקסימלי מהתיק לעסקה אחת")

    with col3:
        vix_halt = _stepper(
            "😨 עצור אם VIX >",
            "fs_vix", 20, 80, 40, 5,
            unit="", color="#e65100",
        )
        st.caption(f"VIX מעל {vix_halt} = שוק פאניקה, עוצר מסחר")
        st.markdown("")
        max_pos = st.number_input(
            "📊 מקסימום פוזיציות פתוחות",
            min_value=1, max_value=20, value=5,
            key="fs_maxpositions",
        )
        st.caption(f"לא יותר מ-{max_pos} עסקאות בו-זמנית")

    # ── סימולציות ───────────────────────────────────────────────
    st.subheader("🔧 סימולציות")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("📉 הדמה -3%", key="fs_sim3"):
            st.session_state.daily_loss_pct = 3.0
            _log("הדמיית הפסד -3%")
            if 3.0 >= max_loss:
                st.session_state.circuit_breaker_triggered = True
                _log("⚡ Circuit Breaker!")
            st.rerun()
    with b2:
        if st.button("📉 הדמה -7%", key="fs_sim7"):
            st.session_state.daily_loss_pct = 7.0
            st.session_state.circuit_breaker_triggered = True
            _log("🚨 הפסד קריטי -7%!")
            st.rerun()
    with b3:
        if st.button("😨 הדמה VIX 45", key="fs_vix45"):
            st.session_state.circuit_breaker_triggered = True
            _log("⚠️ VIX הגיע ל-45")
            st.rerun()
    with b4:
        if st.button("🔄 איפוס יום", key="fs_resetday"):
            st.session_state.daily_loss_pct = 0.0
            st.session_state.circuit_breaker_triggered = False
            _log("✅ איפוס יומי")
            st.rerun()

    # ── Kill Switch ──────────────────────────────────────────────
    st.divider()
    st.subheader("☢️ מתג השמדה")
    ck1, ck2 = st.columns(2)
    with ck1:
        if not st.session_state.kill_switch_active:
            if st.button("🚨 הפעל מתג השמדה!", type="primary", key="fs_killswitch"):
                st.session_state.kill_switch_active = True
                for k in ["val_portfolio","day_portfolio","div_portfolio","ins_portfolio","deep_portfolio"]:
                    if k in st.session_state:
                        st.session_state[k] = []
                _log("🚨 KILL SWITCH! כל הפוזיציות נסגרו!")
                st.rerun()
        else:
            if st.button("✅ איפוס — חזרה לפעולה", key="fs_resume"):
                st.session_state.kill_switch_active = False
                st.session_state.circuit_breaker_triggered = False
                st.session_state.daily_loss_pct = 0.0
                _log("✅ מערכת אופסה")
                st.rerun()
    with ck2:
        st.markdown("""
        🔴 כל הסוכנים נעצרים מיידית  
        🔴 כל הפוזיציות נסגרות למזומן  
        🔴 לא ניתן לפתוח פקודות חדשות  
        🟢 נתונים נשמרים  
        🟢 ניתן לאפס בלחיצה
        """)

    # ── כללים נוספים ────────────────────────────────────────────
    st.subheader("⚙️ כללים נוספים")
    r1, r2 = st.columns(2)
    with r1:
        st.toggle("🔒 מנע Pre-Market",    value=True,  key="fs_pre")
        st.toggle("🔒 מנע After-Hours",   value=True,  key="fs_after")
        st.toggle("⚠️ אשר עסקאות >$5K",  value=True,  key="fs_big")
    with r2:
        st.toggle("📊 ניטור VIX",          value=True,  key="fs_vix_toggle")
        st.toggle("🔄 Rebalance בסוף יום", value=False, key="fs_rebal")
        st.toggle("📱 התראה לטלגרם",       value=False, key="fs_tg")

    # ── יומן ────────────────────────────────────────────────────
    if st.session_state.failsafe_log:
        with st.expander(f"📋 יומן ({len(st.session_state.failsafe_log)} אירועים)"):
            for ev in st.session_state.failsafe_log[:40]:
                icon = "🔴" if any(x in ev for x in ["KILL","קריטי","Circuit"]) else "🟡" if "הדמ" in ev else "🟢"
                st.markdown(f"{icon} `{ev}`")
            if st.button("🗑️ נקה יומן", key="fs_clearlog"):
                st.session_state.failsafe_log = []
                st.rerun()
