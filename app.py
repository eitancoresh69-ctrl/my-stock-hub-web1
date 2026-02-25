# העתק רק את החלקים האלו לתוך app.py במקומות המתאימים:

with tab1:
    st.markdown('<div class="ai-card"><b>ניהול התיק שלי ומדדי ה-PDF:</b> כאן מרוכזים כל 6 הקריטריונים. לחץ על הטבלה כדי להזין מחיר קנייה (BuyPrice) וכמות (Qty).</div>', unsafe_allow_html=True)
    if 'portfolio' not in st.session_state:
        gold_from_scan = df_all[(df_all['Score'] >= 5) & (df_all['Symbol'].isin(SCAN_LIST))]['Symbol'].tolist() if not df_all.empty else []
        initial_list = list(set(MY_STOCKS_BASE + gold_from_scan))
        st.session_state.portfolio = pd.DataFrame([{"Symbol": t, "BuyPrice": 0.0, "Qty": 0} for t in initial_list])
    
    edited = st.data_editor(st.session_state.portfolio, num_rows="dynamic")
    if not edited.empty and not df_all.empty:
        merged = pd.merge(edited, df_all, on="Symbol")
        merged['PL'] = (merged['Price'] - merged['BuyPrice']) * merged['Qty']
        merged['Yield'] = merged.apply(lambda row: ((row['Price'] / row['BuyPrice']) - 1) * 100 if row['BuyPrice'] > 0 else 0, axis=1)
        
        st.dataframe(
            merged[["Symbol", "PriceStr", "BuyPrice", "Qty", "PL", "Yield", "Score", "RevGrowth", "EarnGrowth", "Margin", "ROE", "CashVsDebt", "ZeroDebt", "Action", "AI_Logic"]],
            column_config={
                "Symbol": "סימול",
                "PriceStr": "מחיר שוק",
                "BuyPrice": st.column_config.NumberColumn("מחיר קנייה"),
                "Qty": st.column_config.NumberColumn("כמות"),
                "PL": st.column_config.NumberColumn("רווח/הפסד", format="%.2f"),
                "Yield": st.column_config.NumberColumn("תשואה %", format="%.1f%%"),
                "Score": st.column_config.NumberColumn("⭐ ציון PDF"),
                "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%"),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1%"),
                "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1%"),
                "ROE": st.column_config.NumberColumn("ROE", format="%.1%"),
                "CashVsDebt": st.column_config.TextColumn("מזומן>חוב"),
                "ZeroDebt": st.column_config.TextColumn("חוב 0"),
                "Action": st.column_config.TextColumn("המלצת AI"),
                "AI_Logic": st.column_config.TextColumn("ניתוח פעולה", width="large")
            }, use_container_width=True, hide_index=True
        )

with tab2:
    st.markdown('<div class="ai-card"><b>סורק ה-PDF החכם:</b> מציג מניות מובילות (ציון 4 ומעלה).</div>', unsafe_allow_html=True)
    if not df_all.empty:
        scanner = df_all[(df_all['Symbol'].isin(SCAN_LIST)) & (df_all['Score'] >= 4)].sort_values(by="Score", ascending=False)
        st.dataframe(
            scanner[["Symbol", "PriceStr", "Score", "RevGrowth", "EarnGrowth", "Margin", "Action"]],
            column_config={
                "PriceStr": "מחיר", "Score": "⭐ ציון איכות", "RevGrowth": st.column_config.NumberColumn("צמיחת מכירות", format="%.1%"),
                "EarnGrowth": st.column_config.NumberColumn("צמיחת רווחים", format="%.1%"), "Margin": st.column_config.NumberColumn("שולי רווח", format="%.1%"), "Action": "המלצת AI"
            }, use_container_width=True, hide_index=True)
