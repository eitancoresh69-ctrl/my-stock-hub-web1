# tax_fees_ai.py - אופטימיזציית מיסים ועמלות
import streamlit as st
import pandas as pd

# שיעורי מס ישראל 2025
TAX_CAPITAL_GAINS = 0.25   # 25% מס רווח הון
TAX_DIVIDEND_IL = 0.25      # 25% מס על דיבידנד
TAX_DIVIDEND_US = 0.15      # 15% ניכוי מס במקור ארה"ב

BROKER_FEES = {
    "אינטראקטיב ברוקרס": {"min_fee": 0.35, "per_share": 0.005, "min_monthly": 0, "currency": "USD"},
    "מייטב טרייד": {"min_fee": 12.0, "per_share": 0.0, "min_monthly": 15, "currency": "ILS"},
    "פסגות טרייד":  {"min_fee": 15.0, "per_share": 0.0, "min_monthly": 15, "currency": "ILS"},
    "אקסלנס טרייד": {"min_fee": 14.0, "per_share": 0.0, "min_monthly": 10, "currency": "ILS"},
    "eToro":         {"min_fee": 0.0,  "per_share": 0.0, "min_monthly": 0,  "currency": "USD", "spread": 0.005},
}

def _calc_tax(profit, is_dividend=False, is_us_stock=False):
    """חישוב מס ישראלי מדויק"""
    if profit <= 0:
        return 0.0
    rate = TAX_DIVIDEND_IL if is_dividend else TAX_CAPITAL_GAINS
    # אם מניה אמריקאית — מנכים 15% במקור, ומשלמים עוד 10% בישראל
    if is_us_stock and is_dividend:
        already_withheld = profit * TAX_DIVIDEND_US
        additional_il = profit * (TAX_DIVIDEND_IL - TAX_DIVIDEND_US)
        return round(already_withheld + additional_il, 2)
    return round(profit * rate, 2)

def _calc_fee(broker_name, total_value, qty):
    """חישוב עמלת ברוקר"""
    b = BROKER_FEES.get(broker_name, BROKER_FEES["מייטב טרייד"])
    if "spread" in b:
        return round(total_value * b["spread"], 2)
    fee = max(b["min_fee"], b["per_share"] * qty)
    return round(fee, 2)

def render_tax_optimization():
    st.markdown('<div class="ai-card" style="border-right-color: #4caf50;"><b>💸 מחשבון אופטימיזציית מיסים ועמלות</b> — מחשב את הרווח האמיתי שלך לאחר מס רווח הון ישראלי (25%), ניכוי מקור אמריקאי ועמלות ברוקר.</div>', unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🧮 מחשבון רווח נטו", "📊 השוואת ברוקרים", "📅 תכנון מס שנתי"])

    with t1:
        st.subheader("🧮 חישוב רווח נטו אחרי מיסים ועמלות")

        col1, col2 = st.columns(2)
        with col1:
            stock_type = st.selectbox("🌍 סוג מניה", ["מניה אמריקאית (ארה\"ב)", "מניה ישראלית (TASE)"], key="tax_type")
            income_type = st.selectbox("💰 סוג הכנסה", ["רווח הון (מכירת מניה)", "דיבידנד"], key="tax_income")
            gross_profit = st.number_input("💵 רווח גולמי (₪)", min_value=0.0, value=5000.0, step=100.0, key="tax_gross")
            broker = st.selectbox("🏦 ברוקר", list(BROKER_FEES.keys()), key="tax_broker")

        with col2:
            qty_sold = st.number_input("🔢 מספר מניות שנמכרו", min_value=1, value=50, key="tax_qty")
            entry_price = st.number_input("💲 מחיר קנייה ממוצע ($)", min_value=0.01, value=100.0, step=1.0, key="tax_entry")
            exit_price = st.number_input("💲 מחיר מכירה ($)", min_value=0.01, value=110.0, step=1.0, key="tax_exit")
            usd_rate = st.number_input("💱 שער דולר/שקל", min_value=2.0, value=3.75, step=0.05, key="tax_usd")

        if st.button("🧮 חשב רווח נטו", type="primary", key="tax_calc"):
            is_us = "אמריקא" in stock_type
            is_div = "דיבידנד" in income_type

            # חישוב מהמחירים שהוזנו
            profit_usd = (exit_price - entry_price) * qty_sold
            profit_ils = profit_usd * usd_rate if profit_usd > 0 else gross_profit
            if gross_profit != 5000.0:  # משתמש הזין ידנית
                profit_ils = gross_profit

            # עמלות
            total_value = exit_price * qty_sold * usd_rate
            fee_entry = _calc_fee(broker, entry_price * qty_sold * usd_rate, qty_sold)
            fee_exit  = _calc_fee(broker, total_value, qty_sold)
            total_fees = round((fee_entry + fee_exit) * (usd_rate if BROKER_FEES[broker]["currency"] == "USD" else 1), 2)

            # מיסים
            tax = _calc_tax(profit_ils, is_div, is_us)
            net_profit = round(profit_ils - tax - total_fees, 2)
            effective_tax_rate = round((tax / profit_ils) * 100, 1) if profit_ils > 0 else 0

            st.success("✅ **תוצאת החישוב:**")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 רווח גולמי", f"₪{profit_ils:,.2f}")
            m2.metric("🏛️ מס", f"₪{tax:,.2f}", delta=f"-{effective_tax_rate:.1f}%", delta_color="inverse")
            m3.metric("🏦 עמלות", f"₪{total_fees:,.2f}", delta_color="inverse")
            m4.metric("✅ רווח נטו אמיתי", f"₪{net_profit:,.2f}")

            # פירוט
            with st.expander("📋 פירוט מלא של החישוב"):
                breakdown = [
                    {"סעיף": "רווח גולמי לפני הכל", "סכום (₪)": f"₪{profit_ils:,.2f}"},
                    {"סעיף": f"מס {'דיבידנד' if is_div else 'רווח הון'} ({effective_tax_rate:.0f}%)", "סכום (₪)": f"-₪{tax:,.2f}"},
                    {"סעיף": f"עמלת קנייה ({broker})", "סכום (₪)": f"-₪{fee_entry*(usd_rate if BROKER_FEES[broker]['currency']=='USD' else 1):,.2f}"},
                    {"סעיף": f"עמלת מכירה ({broker})", "סכום (₪)": f"-₪{fee_exit*(usd_rate if BROKER_FEES[broker]['currency']=='USD' else 1):,.2f}"},
                    {"סעיף": "✅ **רווח נטו סופי**", "סכום (₪)": f"**₪{net_profit:,.2f}**"},
                ]
                st.table(pd.DataFrame(breakdown))

                if is_us and is_div:
                    st.info("ℹ️ **הסבר מס אמריקאי:** ארה\"ב מנכה 15% במקור על דיבידנד. בישראל חייב ב-25% סה\"כ, אז תשלם עוד 10% נוספים לרשות המיסים הישראלית.")

    with t2:
        st.subheader("📊 השוואת עמלות ברוקרים לעסקה שלך")

        c1, c2, c3 = st.columns(3)
        with c1:
            cmp_value = st.number_input("שווי עסקה ($)", min_value=100.0, value=5000.0, step=500.0, key="cmp_val")
        with c2:
            cmp_qty = st.number_input("כמות מניות", min_value=1, value=50, key="cmp_qty")
        with c3:
            cmp_usd = st.number_input("שער דולר", min_value=2.0, value=3.75, step=0.05, key="cmp_usd")

        comparison = []
        for broker_name, params in BROKER_FEES.items():
            val_ils = cmp_value * cmp_usd
            fee = _calc_fee(broker_name, val_ils, cmp_qty)
            if params["currency"] == "USD":
                fee_ils = fee * cmp_usd
            else:
                fee_ils = fee
            fee_pct = (fee_ils / val_ils) * 100 if val_ils > 0 else 0
            comparison.append({
                "🏦 ברוקר": broker_name,
                "עמלה לעסקה (₪)": f"₪{fee_ils:.2f}",
                "% מהעסקה": f"{fee_pct:.3f}%",
                "עמלה שנתית מינימום": f"₪{params['min_monthly']*12:,}" if params['min_monthly'] > 0 else "—",
                "מטבע": params["currency"]
            })
        df_cmp = pd.DataFrame(comparison).sort_values("עמלה לעסקה (₪)")
        st.dataframe(df_cmp, use_container_width=True, hide_index=True)

        cheapest = df_cmp.iloc[0]["🏦 ברוקר"]
        st.success(f"💡 **הזול ביותר לעסקה זו: {cheapest}**")

    with t3:
        st.subheader("📅 מחשבון חבות מס שנתית (Tax Loss Harvesting)")
        st.write("הזן את כל העסקאות שלך השנה כדי לחשב את חבות המס הצפויה ולמצוא עסקאות לקיזוז הפסד.")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            annual_gains = st.number_input("סך רווחי הון גולמי השנה (₪)", min_value=0.0, value=20000.0, step=1000.0, key="annual_gains")
            annual_dividends = st.number_input("סך דיבידנדים שהתקבלו (₪)", min_value=0.0, value=3000.0, step=100.0, key="annual_div")
            annual_losses = st.number_input("סך הפסדים מוכרים לקיזוז (₪)", min_value=0.0, value=2000.0, step=100.0, key="annual_loss")

        with col_t2:
            st.markdown("#### 📊 סיכום מס שנתי")
            net_gains = annual_gains - annual_losses
            tax_on_gains = max(net_gains * TAX_CAPITAL_GAINS, 0)
            tax_on_div = annual_dividends * TAX_DIVIDEND_IL
            total_annual_tax = round(tax_on_gains + tax_on_div, 2)
            after_tax_total = round(net_gains + annual_dividends - total_annual_tax, 2)

            st.metric("📈 רווח הון נטו לאחר קיזוז הפסדים", f"₪{net_gains:,.2f}")
            st.metric("🏛️ מס רווח הון (25%)", f"₪{tax_on_gains:,.2f}")
            st.metric("💰 מס על דיבידנדים (25%)", f"₪{tax_on_div:,.2f}")
            st.metric("☠️ סך חבות מס שנתית", f"₪{total_annual_tax:,.2f}", delta_color="inverse")
            st.metric("✅ נטו אחרי מיסים", f"₪{after_tax_total:,.2f}")

        if annual_losses > 0:
            st.info(f"💡 **Tax Loss Harvesting:** קיזזת ₪{annual_losses:,.2f} הפסדים — חסכת ₪{annual_losses * TAX_CAPITAL_GAINS:,.2f} במיסים!")

        st.warning("⚠️ **אזהרה חשובה:** החישובים כאן הם לצרכי מידע בלבד ואינם ייעוץ מס מקצועי. פנה לרואה חשבון לדיווח מדויק לרשות המיסים.")
