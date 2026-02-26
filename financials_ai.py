import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

def render_financial_reports(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #2196f3;"><b>📊 ניתוח דוחות פיננסיים (Financials AI)</b> — ניתוח עומק של דוחות החברה ונתוני אמת.</div>', unsafe_allow_html=True)
    st.divider()

    # סורק חכם למציאת עמודת הסימול מבלי לקרוס
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
        with st.spinner(f"מושך נתונים פיננסיים בזמן אמת עבור {sel} משרתי Yahoo Finance..."):
            try:
                ticker = yf.Ticker(sel)
                info = ticker.info
                financials = ticker.financials
                
                if not info or financials is None or financials.empty:
                    st.warning(f"⚠️ לא נמצאו דוחות פיננסיים מלאים זמינים עבור המניה {sel}.")
                else:
                    company_name = info.get('longName', sel)
                    st.success(f"✅ נתונים נטענו בהצלחה עבור: **{company_name}**")
                    
                    # --- מדדי מפתח ---
                    st.subheader("💡 מדדי מפתח (Key Metrics)")
                    c1, c2, c3, c4 = st.columns(4)
                    
                    market_cap = info.get('marketCap', 0) / 1e9 if info.get('marketCap') else 0
                    pe_ratio = info.get('trailingPE', 'N/A')
                    profit_margin = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
                    rev_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
                    
                    c1.metric("שווי שוק", f"${market_cap:.2f}B" if market_cap else "N/A")
                    c2.metric("מכפיל רווח (P/E)", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio)
                    c3.metric("שולי רווח נקי", f"{profit_margin:.2f}%")
                    c4.metric("צמיחה בהכנסות (YoY)", f"{rev_growth:.2f}%")
                    
                    st.divider()
                    
                    # --- גרף הכנסות מול רווחים ---
                    st.subheader("📈 מגמת הכנסות ורווחים (שנתי)")
                    
                    # בדיקה שיש את הנתונים בדוח
                    if 'Total Revenue' in financials.index and 'Net Income' in financials.index:
                        rev = financials.loc['Total Revenue'].dropna() / 1e9 # הפיכה למיליארדים
                        net_income = financials.loc['Net Income'].dropna() / 1e9
                        
                        # סידור התאריכים מהישן לחדש
                        rev = rev.sort_index()
                        net_income = net_income.sort_index()
                        years = [str(date.year) for date in rev.index]

                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=years, y=rev.values, name='הכנסות (מיליארדים $)', marker_color='#2196f3'))
                        fig.add_trace(go.Bar(x=years, y=net_income.values, name='רווח נקי (מיליארדים $)', marker_color='#4caf50'))
                        
                        fig.update_layout(barmode='group', template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("נתוני ההכנסות השנתיים חסרים או לא בפורמט צפוי ב-Yahoo Finance עבור מניה זו.")

                    # --- תקציר החברה ---
                    with st.expander("📖 פרופיל החברה (מידע כללי)"):
                        st.write(info.get('longBusinessSummary', 'לא קיים תיאור לחברה זו.'))
                        
            except Exception as e:
                st.error(f"אירעה שגיאה במשיכת הנתונים: {e}")
