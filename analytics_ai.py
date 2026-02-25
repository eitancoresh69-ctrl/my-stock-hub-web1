# analytics_ai.py
import streamlit as st
import yfinance as yf
import pandas as pd

# שומר את מפת החום בזיכרון לשעה
@st.cache_data(ttl=3600)
def get_sector_performance():
    sectors = {
        "טכנולוגיה (XLK)": "XLK", "פיננסים (XLF)": "XLF",
        "אנרגיה (XLE)": "XLE", "בריאות (XLV)": "XLV", "צריכה מחזורית (XLY)": "XLY"
    }
    rows = []
    for name, ticker in sectors.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if not hist.empty:
                change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100
                trend = "🟢 חיובי" if change > 0 else "🔴 שלילי"
                rows.append({"סקטור": name, "שינוי יומי": change, "מגמה": trend})
        except: pass
    return pd.DataFrame(rows)

def render_analytics_dashboard():
    st.markdown('<div class="ai-card" style="border-right-color: #ff5722;"><b>📊 מרכז אנליטיקה (Cached):</b> מפת חום המציגה לאן זורם "הכסף החכם", נטענת במהירות הבזק.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🗺️ מפת חום ענפית")
        df_sectors = get_sector_performance()
        
        if not df_sectors.empty:
            df_sectors = df_sectors.sort_values(by="שינוי יומי", ascending=False)
            st.dataframe(df_sectors, column_config={"שינוי יומי": st.column_config.NumberColumn("שינוי (%)", format="%.2f%%")}, use_container_width=True, hide_index=True)
            st.info("💡 **תובנת AI:** חפש מניות זהב מהסקטור שמוביל את השוק.")

    with col2:
        st.markdown("### 📅 יומן אירועי מאקרו")
        events = [
            {"תאריך": "12 לחודש", "אירוע": "מדד CPI (אינפלציה)", "חשיבות": "⭐⭐⭐⭐⭐", "צפי": "תנודתיות גבוהה."},
            {"תאריך": "18 לחודש", "אירוע": "החלטת ריבית פד", "חשיבות": "⭐⭐⭐⭐⭐", "צפי": "קריטי לכלל השוק."},
            {"תאריך": "שישי ראשון", "אירוע": "דוח תעסוקה NFP", "חשיבות": "⭐⭐⭐⭐", "צפי": "משפיע על הדולר."}
        ]
        for e in events:
            st.markdown(f"**{e['אירוע']} ({e['תאריך']})** | חשיבות: {e['חשיבות']}<br>ניתוח: {e['צפי']}<hr style='margin:5px 0;'>", unsafe_allow_html=True)
