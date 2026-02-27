# alerts_ai.py — מרכז התראות חכם
import streamlit as st


def render_smart_alerts(df_all):
    st.markdown(
        '<div class="ai-card" style="border-right-color: #ff9800;">'
        '<b>🔔 מרכז התראות AI:</b> דוחות, הזדמנויות טכניות, בעלי עניין.</div>',
        unsafe_allow_html=True,
    )

    if df_all.empty:
        st.warning("אין נתונים.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📅 דוחות קרובים (14 ימים)")
        soon = df_all[df_all["DaysToEarnings"].between(0, 14)]
        if not soon.empty:
            for _, r in soon.iterrows():
                st.warning(f"**{r['Symbol']}** — דוח בעוד **{r['DaysToEarnings']}** ימים ({r['EarningsDate']})")
        else:
            st.info("אין דוחות ב-14 הימים הקרובים.")

    with col2:
        st.markdown("### 🏛️ מודיעין בעלי עניין")
        high = df_all[df_all["InsiderHeld"] > 5.0]
        if not high.empty:
            for _, r in high.iterrows():
                st.markdown(
                    f'<div style="background
