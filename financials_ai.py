# financials_ai.py — דוחות כספיים היסטוריים
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


def render_financial_reports(df_all):
    st.markdown(
        '<div class="ai-card" style="border-right-color: #009688;">'
        '<b>📚 ניתוח דוחות היסטוריים:</b> הכנסות, רווחים ומאזן לאורך שנים.</div>',
        unsafe_allow_html=True,
    )

    sel = st.selectbox("בחר מניה:", df_all["Symbol"].unique())

    if st.button("📊 נתח דוחות", type="primary"):
        with st.spinner("שואב ומנתח..."):
            try:
                s = yf.Ticker(sel)
                financials = s.financials
                balance = s.balance_sheet

                if financials is not None and not financials.empty:
                    rev = financials.loc["Total Revenue"] if "Total Revenue" in financials.index else None
                    net = financials.loc["Net Income"] if "Net Income" in financials.index else None

                    if rev is not None and net is not None:
                        df_d = pd.DataFrame({"Revenue": rev / 1e9, "Net Income": net / 1e9}).dropna()
                        df_d.index = pd.to_datetime(df_d.index).year.astype(str)
                        df_d = df_d.sort_index()

                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=df_d.index, y=df_d["Revenue"],
                                             name="הכנסות ($B)", marker_color="#1a7
