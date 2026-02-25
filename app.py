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
import podcasts_ai 
import alerts_ai
import financials_ai 

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
    div[data-testid="stTabs"] button { font-weight: bold; font-size: 15px; }
    </style>
""", unsafe_allow_html=True)

df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))

st.title("🌐 Investment Hub Elite 2026")
c1, c2, c3 = st.columns(3)
try: 
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
except: 
    vix = 0.0
    
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}")
c2.metric("🏆 מניות 'זהב' (ציון 5-6)", len(df_all[df_all["Score"] >= 5]) if not df_all.empty else 0)
c3.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))

# 10 טאבים עוצמתיים
tab1, tab2, tab_fin, tab3, tab_alerts, tab_val, tab_day, tab_pod, tab_mac, tab_bb = st.tabs([
    "📌 התיק", "🔍 סורק", "📚 דוחות היסטוריים", "💰 דיבידנדים", "🔔 התראות", 
    "💼 סוכן ערך", "⚡ סוכן יומי", "🎧 פודקאסטים", "🌍 מאקרו", "⚖️ שור/דוב"
])

with tab1:
    st.markdown('<div class="ai-card"><b>התיק שלי (Mega-Table):</b> לחץ פעמיים על מחיר קנייה וכמות כדי לעדכן. רחף מעל הכותרות להסברים בעברית.</div>', unsafe_allow_html=True)
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        
        edited = st.data_editor(
            merged[["Symbol", "PriceStr", "BuyPrice", "Qty", "PL", "Yield", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt"]],
            column_config={
                "Symbol": st.column_config.TextColumn("סימול", disabled=True, help=HELP["symbol"]),
                "PriceStr": st.column_config.TextColumn("מחיר", disabled=True, help=HELP["price"]),
                "BuyPrice": st.column_config.NumberColumn("קנייה ✏️", help=HELP["buy_price"]),
                "Qty": st.column_config.NumberColumn("כמות ✏️", help=HELP["qty"]),
                "PL": st.column_config.NumberColumn("P/L", format="%.2f", disabled=True, help=HELP["pl"]),
                "Yield": st.column_config.NumberColumn("תשואה %", format="%.1f%%", disabled=True, help=HELP["yield"]),
                "Score": st.column_config.NumberColumn("⭐ ציון", disabled=True, help=HELP["score"]),
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1f%%", disabled=True, help=HELP["rev_growth"]),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1f%%", disabled=True, help=HELP["earn_growth"]),
                "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1f%%", disabled=True, help=HELP["margin"]),
                "ROE": st.column_config.NumberColumn("ROE", format="%.1f%%", disabled=True, help=HELP["roe"]),
                "CashVsDebt": st.column_config.TextColumn("מזומן>חוב", disabled=True, help=HELP["cash_debt"]),
                "ZeroDebt": st.column_config.TextColumn("חוב 0", disabled=True, help=HELP["zero_debt"])
            }, use_container_width=True, hide_index=True
        )
        st.session_state.portfolio = edited[["Symbol", "BuyPrice", "Qty"]]

with tab2:
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(scanner[["Symbol", "PriceStr", "Score", "RevGrowth", "Margin", "RSI", "MA50"]], column_config={"PriceStr": "מחיר", "Score": "⭐ ציון", "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1f%%"), "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1f%%"), "RSI": st.column_config.NumberColumn("RSI טכני", format="%.1f"), "MA50": st.column_config.NumberColumn("ממוצע נע 50", format="%.2f")}, use_container_width=True, hide_index=True)

with tab_fin:
    financials_ai.render_financial_reports(df_all)

with tab3:
    st.markdown('<div class="ai-card"><b>ניתוח תזרים מזומנים פסיבי (דיבידנדים לעומק):</b> הנתונים המלאים חזרו! שילוב של קצבה שנתית, יחס חלוקה וממוצע היסטורי.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all['DivYield'] > 0].copy()
        
        def assess_div_safety(row):
            if row['PayoutRatio'] <= 0: return "לא ידוע"
            if row['PayoutRatio'] > 80.0: return "⚠️ סכנת קיצוץ"
            if row['PayoutRatio'] < 60.0 and row['CashVsDebt'] == "✅": return "🛡️ בטוח מאוד"
            return "✅ יציב"
            
        div_df['Safety'] = div_df.apply(assess_div_safety, axis=1)
        div_df['ExDateClean'] = div_df['ExDate'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y') if pd.notnull(x) else "לא ידוע")
        
        # כאן הוחזרו כל העמודות של הדיבידנדים כפי שביקשת!
        st.dataframe(div_df.sort_values(by="DivYield", ascending=False)[["Symbol", "DivYield", "DivRate", "FiveYrDiv", "PayoutRatio", "Safety", "ExDateClean"]], 
        column_config={
            "Symbol": "סימול", 
            "DivYield": st.column_config.NumberColumn("תשואה נוכחית %", format="%.2f%%", help="תשואת הדיבידנד כיום"), 
            "DivRate": st.column_config.NumberColumn("קצבה שנתית ($)", format="$%.2f", help="הסכום הדולרי שתקבל בשנה על כל מניה"),
            "FiveYrDiv": st.column_config.NumberColumn("ממוצע 5 שנים %", format="%.2f%%", help="עוזר לדעת אם התשואה היום גבוהה מהממוצע"),
            "PayoutRatio": st.column_config.NumberColumn("יחס חלוקה %", format="%.1f%%", help="אחוז מתוך הרווח שמחולק כדיבידנד"),
            "Safety": "רמת בטיחות (AI)",
            "ExDateClean": "תאריך אקס"
        }, use_container_width=True, hide_index=True)

with tab_alerts: alerts_ai.render_smart_alerts(df_all)
with tab_val: simulator.render_value_agent(df_all)
with tab_day: simulator.render_day_trade_agent(df_all)
with tab_pod: podcasts_ai.render_podcasts_analysis()
with tab_mac: market_ai.render_market_intelligence()
with tab_bb:
    if not df_all.empty: bull_bear.render_bull_bear(df_all)
