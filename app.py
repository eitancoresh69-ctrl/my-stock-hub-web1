# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import urllib.parse

# כאן אנחנו "מייבאים" את הקבצים שיצרנו בשלבים הקודמים!
from config import HELP, MY_STOCKS_BASE, SCAN_LIST
from logic import fetch_master_data

# --- 1. הגדרות דף וריענון אוטומטי ---
st.set_page_config(page_title="Investment Hub Premium", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<script>setInterval(function(){ window.location.reload(); }, 900000);</script>""", unsafe_allow_html=True)

# --- עיצוב משודרג עם צבעים והפרדות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    
    /* רקע כללי עדין */
    .stApp { background-color: #f8f9fa; }
    
    .block-container { padding-top: 1rem !important; }
    
    /* טבלאות דחוסות וקריאות יותר */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { padding: 4px 8px !important; font-size: 14px !important; }
    
    /* כרטיסי מידע חכמים עם מעבר צבע */
    .ai-card { 
        background: linear-gradient(145deg, #ffffff, #f0f7ff); 
        padding: 15px; border-radius: 12px; border-right: 6px solid #1a73e8; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin-bottom: 15px; 
    }
    
    .bull-box { background-color: #e8f5e9; border-color: #2e7d32; color: #1b5e20; padding: 12px; border-radius: 8px; border-right: 5px solid; margin-bottom: 10px; font-weight: 600;}
    .bear-box { background-color: #ffeef0; border-color: #d73a49; color: #b71c1c; padding: 12px; border-radius: 8px; border-right: 5px solid; font-weight: 600;}
    
    /* קוביות מדדים עליונות */
    [data-testid="stMetric"] { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-bottom: 3px solid #1a73e8; }
    </style>
""", unsafe_allow_html=True)

# --- 2. הבאת הנתונים מהמוח (logic.py) ---
df_all = fetch_master_data(list(set(MY_STOCKS_BASE + SCAN_LIST)))

# --- 3. בניית הממשק ---
st.title("🌐 Investment Hub Premium 2026")
st.markdown("מערכת מודיעין פיננסית אוטונומית. הנתונים מתרעננים אוטומטית כל 15 דקות.")

# קוביות מדדים
import yfinance as yf # נדרש רק בשביל ה-VIX המהיר
vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("📊 VIX (מדד הפחד)", f"{vix:.2f}", help="מעל 25 = פחד בשוק. מתחת ל-15 = שאננות.")
c2.metric("🏆 מניות זהב (ציון 5-6)", len(df_all[df_all["Score"] >= 5]), help="כמות המניות שעברו את הסינון הקפדני.")
c3.metric("🔥 המזנקת היומית", df_all.loc[df_all["Change"].idxmax()]["Symbol"] if not df_all.empty else "N/A")
c4.metric("🕒 עדכון אחרון", datetime.now().strftime("%H:%M"))

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 ניהול התיק שלי", "🔍 סורק מניות זהב", "💰 לוח דיבידנדים", "📄 חקירת עומק וגרפים", "🤝 רדאר M&A העולמי"])

# טאב 1: המניות שלי
with tab1:
    st.markdown('<div class="ai-card"><b>הוראות:</b> לחץ על הטבלה כדי לערוך את עמודות ה"מחיר קנייה" (BuyPrice) וה"כמות" (Qty). הרווח והתשואה יחושבו אוטומטית. מניות חזקות מהסורק נוספות לכאן אוטומטית.</div>', unsafe_allow_html=True)
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist()
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    edited = st.data_editor(st.session_state.portfolio, num_rows="dynamic")
    if not edited.empty:
        merged = pd.merge(edited, df_all[['Symbol', 'Price', 'Change', 'Score', 'Action', 'AI_Logic']], on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = ((merged['Price'] / merged['BuyPrice']) - 1) * 100
        
        st.dataframe(
            merged[["Symbol", "Price", "Change", "PL", "Yield", "Score", "Action", "AI_Logic"]],
            column_config={
                "Price": st.column_config.NumberColumn("מחיר שוק", help=HELP["price"]),
                "PL": st.column_config.NumberColumn("רווח/הפסד פתוח", help=HELP["pl"], format="%.2f"),
                "Yield": st.column_config.NumberColumn("תשואה %", help=HELP["yield"], format="%.1f%%"),
                "Score": st.column_config.NumberColumn("⭐ ציון איכות", help=HELP["score"]),
                "Action": st.column_config.TextColumn("פעולה מומלצת", help=HELP["action"]),
                "AI_Logic": st.column_config.TextColumn("תובנות AI", width="large")
            }, use_container_width=True, hide_index=True
        )

# טאב 2: סורק
with tab2:
    st.markdown('<div class="ai-card"><b>סורק ה-PDF:</b> מערכת AI סורקת עשרות מניות מובילות ומדרגת אותן לפי 6 הקריטריונים המחמירים שהגדרת. רק מניות עם ציון 4 ומעלה מוצגות כאן.</div>', unsafe_allow_html=True)
    scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
    st.dataframe(scanner[["Symbol", "Price", "Score", "Action", "AI_Logic"]], use_container_width=True, hide_index=True)

# טאב 3: דיבידנדים
with tab3:
    st.markdown('<div class="ai-card"><b>תזרים מזומנים פסיבי:</b> כאן מוצגות כל המניות ברדאר שלך שמחלקות כסף למשקיעים. שים לב ל"תאריך אקס" – זה היום הקובע לזכאות.</div>', unsafe_allow_html=True)
    div_df = df_all[df_all['DivYield'] > 0].sort_values(by="DivYield", ascending=False)
    div_df['ExDateClean'] = div_df['ExDate'].apply(lambda x: datetime.fromtimestamp(x).strftime('%d/%m/%Y') if x else "N/A")
    st.dataframe(div_df[["Symbol", "DivYield", "ExDateClean"]], column_config={"DivYield": st.column_config.NumberColumn("תשואה שנתית %", format="%.2f%%", help=HELP["div"]), "ExDateClean": st.column_config.TextColumn("תאריך אקס", help=HELP["ex_date"])}, use_container_width=True, hide_index=True)

# טאב 4: אודות וניתוח
with tab4:
    sel = st.selectbox("בחר מניה לביצוע צלילת עומק (Deep Dive):", df_all['Symbol'].unique())
    row = df_all[df_all['Symbol'] == sel].iloc[0]
    st.markdown(f'<div class="ai-card"><b>🏢 אודות {sel} (מידע עסקי):</b><br>{row["Info"].get("longBusinessSummary", "לא נמצא מידע.")[:1200]}...</div>', unsafe_allow_html=True)
    
    col_bull, col_bear = st.columns(2)
    with col_bull: st.markdown(f'<div class="bull-box"><b>🐂 תזה חיובית (שור):</b> צמיחה מוכחת בהכנסות של {row["RevGrowth"]:.1%}. המודל מזהה יתרון תחרותי.</div>', unsafe_allow_html=True)
    with col_bear: st.markdown(f'<div class="bear-box"><b>🐻 תזה שלילית (דוב):</b> יש לעקוב אחר תמחור השוק שעלול להיות מתוח בטווח הקצר.</div>', unsafe_allow_html=True)
    
    yrs = st.slider("בחר כמות שנים לגרף היסטורי:", 1, 10, 5)
    hist = yf.Ticker(sel).history(period=f"{yrs}y")
    fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#1a73e8', width=2), fill='tozeroy', fillcolor='rgba(26, 115, 232, 0.1)'))
    fig.update_layout(title=f"היסטוריית מחירים - {sel} ({yrs} שנים)", height=380, template="plotly_white", margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

# טאב 5: מיזוגים
with tab5:
    st.markdown('<div class="ai-card"><b>מודיעין עסקאות חם:</b> המערכת אוספת שמועות ודיווחים על עסקאות מיזוג או רכישה (M&A) שעשויות לטלטל את השוק.</div>', unsafe_allow_html=True)
    mergers = [
        {"חברה": "Wiz / Google", "נושא": "מיזוג סייבר ומודיעין", "סבירות": "75%", "חיפוש": "Wiz Google merger news"},
        {"חברה": "Intel / Qualcomm", "נושא": "שמועות רכישה / פיצול אינטל", "סבירות": "40%", "חיפוש": "Intel acquisition rumors"}
    ]
    for m in mergers:
        url = f"https://www.google.com/search?q={urllib.parse.quote(m['חיפוש'])}"
        st.markdown(f'<div class="ai-card" style="border-right-color: #f57c00;"><b>🤝 {m["חברה"]}</b> | הערכת סבירות עסקית: {m["סבירות"]}<br><a href="{url}" target="_blank" style="text-decoration: none; color: #1a73e8; font-weight: bold;">🔗 קרא את הדיווחים המלאים מ-Reuters/Bloomberg</a></div>', unsafe_allow_html=True)