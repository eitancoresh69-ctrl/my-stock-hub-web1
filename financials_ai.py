import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

def render_financial_reports(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2196f3;"><b>📊 ניתוח דוחות פיננסיים (Financials AI)</b> — ניתוח עומק של דוחות החברה ונתוני אמת.</div>', unsafe_allow_html=True)
    st.divider()

    symbol_col = next((col for col in ['סימול', 'Symbol', 'symbol', 'Ticker', 'ticker'] if col in df_all.columns), None)
    if symbol_col is None:
        st.error("❌ שגיאה: לא מצאתי עמודה המכילה את סימולי המניות בטבלה הראשית.")
        return
        
    symbols_list = df_all[symbol_col].dropna().unique().tolist()
    if not symbols_list:
        st.warning("⚠️ לא נמצאו מניות בטבלה.")
        return

    sel = st.selectbox("🎯 בחר מניה לניתוח דוחות עומק:", symbols_list)
    if sel:
        with st.spinner(f"מושך נתונים עבור {sel}..."):
            try:
                ticker = yf.Ticker(sel)
                info = ticker.info if hasattr(ticker, 'info') else {}
                company_name = info.get('longName', sel)
                st.success(f"✅ נתונים נטענו בהצלחה עבור: **{company_name}**")
                
                st.subheader("💡 מדדי מפתח (Key Metrics)")
                c1, c2, c3, c4 = st.columns(4)
                
                market_cap = info.get('marketCap')
                c1.metric("שווי שוק", f"${market_cap / 1e9:.2f}B" if market_cap else "N/A")
                pe_ratio = info.get('trailingPE')
                c2.metric("מכפיל רווח (P/E)", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
                profit_margin = info.get('profitMargins')
                c3.metric("שולי רווח נקי", f"{profit_margin * 100:.2f}%" if profit_margin else "N/A")
                rev_growth = info.get('revenueGrowth')
                c4.metric("צמיחה בהכנסות", f"{rev_growth * 100:.2f}%" if rev_growth else "N/A")
                
            except Exception as e:
                st.error(f"❌ אירעה שגיאה בעת משיכת הנתונים: {e}")
