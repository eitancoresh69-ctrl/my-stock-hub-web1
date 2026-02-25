# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ייבוא המודלים שיצרנו בקבצים האחרים!
from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
import market_ai
import bull_bear
import simulator

st.set_page_config(page_title="Investment Hub Premium", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<script>setInterval(function(){ window.location.reload(); }, 900000);</script>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f0f2f6; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 14px !important; }
    .ai-card { background: linear-gradient(145deg, #ffffff, #e6f0fa); padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin-bottom: 15px; }
    .bull-box { background-color: #e8f5e9; border-color: #2e7d32; color: #1b5e20; padding: 12px; border-radius: 8px; border-right: 5px solid; margin-bottom: 10px;}
    .bear-box { background-color: #ffeef0; border-color: #d73a49; color: #b71c1c; padding: 12px; border-radius: 8px; border-right: 5px solid; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))

st.title("🌐 Investment Hub Premium 2026")

c1, c2, c3 = st.columns(3)
try: vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except: vix = 0
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות זהב (ציון 5-6)", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))

tab1, tab2, tab3, tab4 = st.tabs(["📌 המניות שלי (לפי ה-PDF)", "🤖 סימולטור וסוכן AI", "🌍 מודיעין מאקרו", "⚖️ ניתוח שור/דוב"])

with tab1:
    st.markdown('<div class="ai-card"><b>הפירוט המלא לפי ה-PDF שלך:</b> הטבלה מציגה את הנתונים הגולמיים שמרכיבים את ציון האיכות.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        my_stocks_df = df_all[df_all['Symbol'].isin(MY_STOCKS_BASE)]
        st.dataframe(
            my_stocks_df[["Symbol", "Price", "Score", "RevGrowth", "EarnGrowth", "Margins", "ROE", "CashVsDebt", "ZeroDebt"]],
            column_config={
                "Price": st.column_config.NumberColumn("מחיר"),
                "Score": st.column_config.NumberColumn("⭐ ציון איכות"),
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%"),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווח", format="%.1%"),
                "Margins": st.column_config.NumberColumn("שולי רווח", format="%.1%"),
                "ROE": st.column_config.NumberColumn("ROE", format="%.1%"),
                "CashVsDebt": st.column_config.TextColumn("מזומן > חוב"),
                "ZeroDebt": st.column_config.TextColumn("חוב אפס")
            }, use_container_width=True, hide_index=True
        )

with tab2:
    # קריאה לקובץ הסימולטור
    simulator.render_paper_trading(df_all)

with tab3:
    # קריאה לקובץ המודיעין
    market_ai.render_market_intelligence()

with tab4:
    # קריאה לקובץ הניתוח
    if not df_all.empty:
        bull_bear.render_bull_bear(df_all)
