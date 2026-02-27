# analytics_ai.py — מפת חום סקטורים + יומן מאקרו
import streamlit as st
import yfinance as yf
import pandas as pd


def render_analytics_dashboard():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #ff5722;">'
        '<b>📊 אנליטיקה מתקדמת:</b> ביצועי סקטורים חיים + יומן מאקרו.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🗺️ מפת חום ענפית (חיה)")
        sectors = {
            "טכנולוגיה (XLK)": "XLK",
            "פיננסים (XLF)":   "XLF",
            "אנרגיה (XLE)":    "XLE",
            "בריאות (XLV)":    "XLV",
            "צריכה (XLY)":     "XLY",
            "תעשיה (XLI)":     "XLI",
            "חומרי גלם (XLB)": "XLB",
        }
        rows = []
        with st.spinner("שואב..."):
            for name, ticker in sectors.items():
                try:
                    h = yf.Ticker(ticker).history(period="5d")
                    if not h.empty and len(h) >= 2:
                        chg = ((h["Close"].iloc[-1] / h["Close"].iloc[-2]) - 1) * 100
                        rows.append({"סקטור": name, "שינוי %": chg,
                                     "מגמה": "🟢" if chg > 0 else "🔴"})
                except Exception:
                    pass

        if rows:
            df = pd.DataFrame(rows).sort_values("שינוי %", ascending=False)
            st.dataframe(df, column_config={
                "שינוי %": st.column_config.NumberColumn("שינוי %", format="%.2f%%"),
            }, use_container_width=True, hide_index=True)
            st.info("💡 **AI:** חפש מניות זהב מהסקטור המוביל.")

    with col2:
        st.markdown("### 📅 יומן אירועי מאקרו")
        events = [
            {"תאריך": "12 לחודש", "אירוע": "CPI — אינפלציה",
             "חשיבות": "⭐⭐⭐⭐⭐", "AI": "גבוה = ירידה בטכנולוגיה. נמוך = זינוק."},
            {"תאריך": "18 לחודש", "אירוע": "החלטת ריבית הפד",
             "חשיבות": "⭐⭐⭐⭐⭐", "AI": "הורדה = דלק לשוק. העלאה = לחץ על צמיחה."},
            {"תאריך": "שישי ראשון", "אירוע": "דוח תעסוקה (NFP)",
             "חשיבות": "⭐⭐⭐⭐", "AI": "שוק חזק = ריבית גבוהה יותר."},
            {"תאריך": "אמצע החודש", "אירוע": "עונת דוחות — בנקים",
             "חשיבות": "⭐⭐⭐", "AI": "הבנקים מכתיבים את הטון לשאר הדוחו
