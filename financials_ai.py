import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

def render_financial_reports(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2196f3;"><b>📊 ניתוח דוחות פיננסיים (Financials AI)</b> — ניתוח עומק של דוחות החברה ונתוני אמת.</div>', unsafe_allow_html=True)
    st.divider()

    symbol_col = next((col for col in ['סימול', 'Symbol', 'symbol', 'Ticker', 'ticker'] if col in df_all.columns), None)
    
    if symbol_col is None:
        st.error("❌ שגיאה: לא מצאתי עמודה המכילה את סימולי המניות בטבלה.")
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
                st.success(f"✅ נתונים נטענו בהצלחה מ-Yahoo Finance עבור: **{company_name}**")
                
                st.subheader("💡 מדדי מפתח (Key Metrics)")
                c1, c2, c3, c4 = st.columns(4)
                
                market_cap = info.get('marketCap')
                market_cap_str = f"${market_cap / 1e9:.2f}B" if market_cap else "N/A"
                
                pe_ratio = info.get('trailingPE')
                pe_str = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A"
                
                profit_margin = info.get('profitMargins')
                pm_str = f"{profit_margin * 100:.2f}%" if profit_margin else "N/A"
                
                rev_growth = info.get('revenueGrowth')
                rg_str = f"{rev_growth * 100:.2f}%" if rev_growth else "N/A"
                
                c1.metric("שווי שוק", market_cap_str)
                c2.metric("מכפיל רווח (P/E)", pe_str)
                c3.metric("שולי רווח נקי", pm_str)
                c4.metric("צמיחה בהכנסות", rg_str)
                
                st.divider()
                
                st.subheader("📈 מגמת הכנסות ורווחים (שנתי)")
                financials = ticker.financials
                if financials is not None and not financials.empty:
                    if 'Total Revenue' in financials.index and 'Net Income' in financials.index:
                        rev = financials.loc['Total Revenue'].dropna() / 1e9
                        net_income = financials.loc['Net Income'].dropna() / 1e9
                        
                        rev = rev.sort_index()
                        net_income = net_income.sort_index()
                        years = [str(date.year) for date in rev.index]

                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=years, y=rev.values, name='הכנסות (מיליארדים $)', marker_color='#2196f3'))
                        fig.add_trace(go.Bar(x=years, y=net_income.values, name='רווח נקי (מיליארדים $)', marker_color='#4caf50'))
                        
                        fig.update_layout(barmode='group', template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("הדוחות קיימים אך חסרות שורות של רווח והכנסות.")
                else:
                    st.info("לא נמצאו דוחות היסטוריים מלאים ב-Yahoo Finance עבור מניה זו.")

            except Exception as e:
                st.error(f"❌ אירעה שגיאה קריטית בעת משיכת הנתונים מ-Yahoo: {e}")
