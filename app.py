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
    .div-safe { color: #1b5e20; font-weight: bold; background-color: #e8f5e9; padding: 3px 8px; border-radius: 5px;}
    .div-warn { color: #b71c1c; font-weight: bold; background-color: #ffeef0; padding: 3px 8px; border-radius: 5px;}
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📌 המניות שלי (P/L)", "🔍 סורק מניות חכם", "💰 דיבידנדים לעומק", "🤖 סוכן AI (סימולטור)", "🌍 מודיעין עולמי מורחב", "⚖️ ניתוח שור ודוב"])

with tab1:
    st.markdown('<div class="ai-card"><b>ניהול התיק שלי (Mega-Table חכמה):</b> שילבנו הכל לטבלה אחת! הקלק פעמיים על המספרים בעמודות <b>"מחיר קנייה"</b> או <b>"כמות"</b> כדי לעדכן אותם. ה-P/L והתשואה יתעדכנו מיד.</div>', unsafe_allow_html=True)
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    if not df_all.empty:
        merged = pd.merge(st.session_state.portfolio, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        
        # טבלה אחת שמאפשרת עריכה רק לעמודות הספציפיות
        edited = st.data_editor(
            merged[["Symbol", "PriceStr", "BuyPrice", "Qty", "PL", "Yield", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "Action"]],
            column_config={
                "Symbol": st.column_config.TextColumn("סימול", disabled=True),
                "PriceStr": st.column_config.TextColumn("מחיר שוק", disabled=True),
                "BuyPrice": st.column_config.NumberColumn("מחיר קנייה ✏️", help="לחץ כדי לערוך"),
                "Qty": st.column_config.NumberColumn("כמות ✏️", help="לחץ כדי לערוך"),
                "PL": st.column_config.NumberColumn("רווח/הפסד", format="%.2f", disabled=True),
                "Yield": st.column_config.NumberColumn("תשואה %", format="%.1f%%", disabled=True),
                "Score": st.column_config.NumberColumn("⭐ ציון PDF", disabled=True),
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%", disabled=True),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1%", disabled=True),
                "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1%", disabled=True),
                "ROE": st.column_config.NumberColumn("ROIC/ROE", format="%.1%", disabled=True),
                "CashVsDebt": st.column_config.TextColumn("מזומן>חוב", disabled=True),
                "ZeroDebt": st.column_config.TextColumn("חוב 0", disabled=True),
                "Action": st.column_config.TextColumn("המלצת AI", disabled=True)
            }, use_container_width=True, hide_index=True
        )
        # שמירת השינויים שהמשתמש עשה בטבלה
        st.session_state.portfolio = edited[["Symbol", "BuyPrice", "Qty"]]

with tab2:
    st.markdown('<div class="ai-card"><b>סורק מניות (PDF + AI):</b> רק חברות חזקות עם ציון 4 ומעלה.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(scanner[["Symbol", "PriceStr", "Score", "RevGrowth", "EarnGrowth", "Margin", "Action"]], column_config={"PriceStr": "מחיר", "Score": "⭐ ציון", "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%"), "EarnGrowth": st.column_config.NumberColumn("צמיחת רווח", format="%.1%"), "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1%"), "Action": "המלצת AI"}, use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="ai-card"><b>ניתוח תזרים מזומנים פסיבי (דיבידנדים לעומק):</b> מעבר לתשואה, הוספנו את "יחס החלוקה" (Payout Ratio). ככל שהיחס נמוך מ-60%, כך הדיבידנד בטוח יותר ויש לחברה מקום להגדיל אותו בעתיד.</div>', unsafe_allow_html=True)
    if not df_all.empty:
        div_df = df_all[df_all['DivYield'] > 0].copy()
        
        # לוגיקת AI לבטיחות דיבידנד
        def assess_div_safety(row):
            if row['PayoutRatio'] <= 0: return "לא ידוע"
            if row['PayoutRatio'] > 0.80: return "⚠️ בסכנת קיצוץ (מחלקת יותר מדי)"
            if row['PayoutRatio'] < 0.60 and row['CashVsDebt'] == "✅": return "🛡️ בטוח מאוד (תזרים חזק)"
            return "✅ יציב"
            
        div_df['Safety'] = div_df.apply(assess_div_safety, axis=1)
        div_df['ExDateClean'] = div_df['ExDate'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y') if pd.notnull(x) else "לא ידוע")
        
        st.dataframe(
            div_df.sort_values(by="DivYield", ascending=False)[["Symbol", "DivYield", "PayoutRatio", "Safety", "ExDateClean"]], 
            column_config={
                "Symbol": "סימול", 
                "DivYield": st.column_config.NumberColumn("תשואת דיבידנד %", format="%.2f%%"), 
                "PayoutRatio": st.column_config.NumberColumn("יחס חלוקה (מתוך הרווח)", format="%.1%"),
                "Safety": "רמת בטיחות (AI)",
                "ExDateClean": "תאריך אקס"
            }, use_container_width=True, hide_index=True)

with tab4:
    simulator.render_paper_trading(df_all)

with tab5:
    market_ai.render_market_intelligence()

with tab6:
    if not df_all.empty:
        bull_bear.render_bull_bear(df_all)
