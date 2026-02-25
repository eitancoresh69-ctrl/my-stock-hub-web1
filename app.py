# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data
import market_ai
import bull_bear
import simulator

st.set_page_config(page_title="Investment Hub Elite", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<script>setInterval(function(){ window.location.reload(); }, 900000);</script>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f4f6f9; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 14px !important; }
    .ai-card { background: white; padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))

st.title("🌐 Investment Hub Elite 2026")
c1, c2, c3 = st.columns(3)
try: vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except: vix = 0.0
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות 'זהב' (ציון 5-6)", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))

# פיצלנו את הסימולטור לשני טאבים: סוכן ערך וסוכן יומי
tab1, tab2, tab3, tab_val, tab_day, tab6, tab7 = st.tabs(["📌 המניות שלי (Mega-Table)", "🔍 סורק מניות חכם", "💰 דיבידנדים לעומק", "💼 סוכן AI (ערך)", "⚡ סוכן AI (יומי)", "🌍 מודיעין עולמי", "⚖️ ניתוח שור/דוב"])

with tab1:
    st.markdown('<div class="ai-card"><b>ניהול התיק שלי (Mega-Table):</b> עמוד עם העכבר על כותרות הטבלה כדי לקבל הסבר מפורט בעברית על כל נתון.</div>', unsafe_allow_html=True)
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        
        edited = st.data_editor(
            merged[["Symbol", "PriceStr", "BuyPrice", "Qty", "PL", "Yield", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "Action"]],
            column_config={
                "Symbol": st.column_config.TextColumn("סימול", disabled=True, help=HELP["symbol"]),
                "PriceStr": st.column_config.TextColumn("מחיר שוק", disabled=True, help=HELP["price"]),
                "BuyPrice": st.column_config.NumberColumn("מחיר קנייה ✏️", help=HELP["buy_price"]),
                "Qty": st.column_config.NumberColumn("כמות ✏️", help=HELP["qty"]),
                "PL": st.column_config.NumberColumn("רווח/הפסד", format="%.2f", disabled=True, help=HELP["pl"]),
                "Yield": st.column_config.NumberColumn("תשואה %", format="%.1f%%", disabled=True, help=HELP["yield"]),
                "Score": st.column_config.NumberColumn("⭐ ציון PDF", disabled=True, help=HELP["score"]),
                # פורמט חדש שלא קורס:
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1f%%", disabled=True, help=HELP["rev_growth"]),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1f%%", disabled=True, help=HELP["earn_growth"]),
                "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1f%%", disabled=True, help=HELP["margin"]),
                "ROE": st.column_config.NumberColumn("ROE/ROIC", format="%.1f%%", disabled=True, help=HELP["roe"]),
                "CashVsDebt": st.column_config.TextColumn("מזומן>חוב", disabled=True, help=HELP["cash_debt"]),
                "ZeroDebt": st.column_config.TextColumn("חוב 0", disabled=True, help=HELP["zero_debt"]),
                "Action": st.column_config.TextColumn("המלצת AI", disabled=True, help=HELP["action"])
            }, use_container_width=True, hide_index=True
        )
        st.session_state.portfolio = edited[["Symbol", "BuyPrice", "Qty"]]

with tab2:
    st.markdown('<div class="ai-card"><b>סורק מניות חכם:</b> עמוד עם העכבר על הכותרות לקבלת הסבר מפורט.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(scanner[["Symbol", "PriceStr", "Score", "RevGrowth", "EarnGrowth", "Margin", "Action"]], 
        column_config={
            "Symbol": st.column_config.TextColumn("סימול", help=HELP["symbol"]),
            "PriceStr": st.column_config.TextColumn("מחיר שוק", help=HELP["price"]),
            "Score": st.column_config.NumberColumn("⭐ ציון", help=HELP["score"]),
            "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1f%%", help=HELP["rev_growth"]),
            "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1f%%", help=HELP["earn_growth"]),
            "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1f%%", help=HELP["margin"]),
            "Action": st.column_config.TextColumn("המלצת AI", help=HELP["action"])
        }, use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="ai-card"><b>לוח תזרים מזומנים (דיבידנדים):</b> עמוד על הכותרות להסברים.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all['DivYield'] > 0].copy()
        def assess_div_safety(row):
            if row['PayoutRatio'] <= 0: return "לא ידוע"
            if row['PayoutRatio'] > 80.0: return "⚠️ בסכנת קיצוץ"
            if row['PayoutRatio'] < 60.0 and row['CashVsDebt'] == "✅": return "🛡️ בטוח מאוד"
            return "✅ יציב"
            
        div_df['Safety'] = div_df.apply(assess_div_safety, axis=1)
        div_df['ExDateClean'] = div_df['ExDate'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y') if pd.notnull(x) else "לא ידוע")
        
        st.dataframe(div_df.sort_values(by="DivYield", ascending=False)[["Symbol", "DivYield", "PayoutRatio", "Safety", "ExDateClean"]], 
        column_config={
            "Symbol": st.column_config.TextColumn("סימול", help=HELP["symbol"]),
            "DivYield": st.column_config.NumberColumn("תשואה %", format="%.2f%%", help=HELP["div"]), 
            "PayoutRatio": st.column_config.NumberColumn("יחס חלוקה", format="%.1f%%", help=HELP["payout"]),
            "Safety": st.column_config.TextColumn("בטיחות (AI)", help=HELP["safety"]),
            "ExDateClean": st.column_config.TextColumn("תאריך אקס", help=HELP["ex_date"])
        }, use_container_width=True, hide_index=True)

with tab_val:
    simulator.render_value_agent(df_all)

with tab_day:
    simulator.render_day_trade_agent(df_all)

with tab6:
    market_ai.render_market_intelligence()

with tab7:
    if not df_all.empty:
        bull_bear.render_bull_bear(df_all)
