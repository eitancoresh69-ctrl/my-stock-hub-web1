# bull_bear.py — מעבדת שור/דוב דינמית
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf


def render_bull_bear(df_all):
    st.markdown(
        '<div class="ai-card" style="border-right-color: #9c27b0;">'
        '<b>⚖️ מעבדת שור/דוב:</b> ה-AI בונה כתב תביעה והגנה דינמי.</div>',
        unsafe_allow_html=True,
    )

    sel = st.selectbox("בחר מניה:", df_all["Symbol"].unique(), key="bullbear_sym")
    row = df_all[df_all["Symbol"] == sel].iloc[0]
    st.markdown(f"### 🏢 {sel}")

    bull_args = f"1. **ציון PDF:** {row['Score']}/6\n"
    if row["RevGrowth"] > 10:
        bull_args += f"2. **צמיחה:** הכנסות +{row['RevGrowth']:.1f}%\n"
    if row["RSI"] < 40:
        bull_args += f"3. **טכני:** RSI {row['RSI']:.0f} — מכירת יתר, נקודת כניסה.\n"
    if row["FairValue"] > row["Price"]:
        bull_args += f"4. **תמחור:** שווי הוגן {row['Currency']}{row['FairValue']:.2f} — בהנחה!\n"
    if row["CashVsDebt"] == "✅":
        bull_args += "5. **מאזן:** מזומן עולה על חוב.\n"

    bear_args = "1. **מאקרו:** ריבית גבוהה מאיטה צמיחה.\n"
    if row["ZeroDebt"] == "❌":
        bear_args += "2. **חוב:** יש חוב — סיכון בריבית גבוהה.\n"
    if row["RSI"] > 65:
        bear_args += f"3. **שיא:** RSI {row['RSI']:.0f} — קניית יתר, סכנת תיקון.\n"
    if row["FairValue"] > 0 and row["FairValue"] <= row["Price"]:
        bear_args += f"4. **יקר:** מעל שווי הוגן ({row['Currency']}{row['FairValue']:.2f}).\n"
    if row["Margin"] < 10:
        bear_args += f"5. **שולי רווח:** {row['Margin']:.1f}% — מתחת לסטנדרט.\n"

    col_bull, col_bear = st.columns(2)
    with col_bull:
        st.success("**🐂 תזת השור**")
        st.markdown(bull_args)
    with col_bear:
        st.error("**🐻 תזת הדוב**")
        st.markdown(bear_args)

    st.markdown("---")
    yrs = st.slider("טווח שנים:", 1, 10, 5, key="bullbear_yrs")
    try:
        hist = yf.Ticker(sel).history(period=f"{yrs}y")
        fig = go.Figure(go.Scatter(
            x=hist.index, y=hist["Close"],
            line=dict(color="#1a73e8", width=2),
            fill="tozeroy", fillcolor="rgba(26,115,232,0.1)",
        ))
        fig.update_layout(title=f"מחיר — {sel}", height=320, template="plotly_white",
                          margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.warning("הגרף לא זמין.")
