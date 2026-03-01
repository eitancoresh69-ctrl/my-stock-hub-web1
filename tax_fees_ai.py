# tax_fees_ai.py — מחשבון מיסים ועמלות
import streamlit as st
import pandas as pd

TAX_CG   = 0.25
TAX_DIV  = 0.25
TAX_US   = 0.15

BROKERS = {
    "אינטראקטיב ברוקרס": {"min": 0.35, "per": 0.005, "mo": 0,  "cur": "USD"},
    "מייטב טרייד":        {"min": 12.0, "per": 0.0,   "mo": 15, "cur": "ILS"},
    "פסגות טרייד":        {"min": 15.0, "per": 0.0,   "mo": 15, "cur": "ILS"},
    "אקסלנס טרייד":       {"min": 14.0, "per": 0.0,   "mo": 10, "cur": "ILS"},
    "eToro":              {"min": 0.0,  "per": 0.0,   "mo": 0,  "cur": "USD", "spread": 0.005},
}


def _tax(profit, is_div=False, is_us=False):
    if profit <= 0: return 0.0
    rate = TAX_DIV if is_div else TAX_CG
    return round(profit * rate, 2)


def _fee(broker, val, qty):
    b = BROKERS.get(broker, BROKERS["מייטב טרייד"])
    if "spread" in b:
        return round(val * b["spread"], 2)
    return round(max(b["min"], b["per"] * qty), 2)


def render_tax_optimization():
    st.markdown(
        '<div class="ai-card" style="border-right-color: #4caf50;">'
        '<b>💸 מחשבון מיסים ועמלות:</b> רווח נטו אחרי מס 25% ועמלות ברוקר.</div>',
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.tabs(["🧮 רווח נטו", "📊 השוואת ברוקרים", "📅 תכנון שנתי"])

    with t1:
        col1, col2 = st.columns(2)
        with col1:
            stype = st.selectbox("🌍 סוג מניה", ["מניה אמריקאית", "מניה ישראלית"], key="tax_stype")
            itype = st.selectbox("💰 סוג הכנסה", ["רווח הון", "דיבידנד"], key="tax_itype")
            broker = st.selectbox("🏦 ברוקר", list(BROKERS.keys()), key="tax_broker")
        with col2:
            qty = st.number_input("🔢 כמות", min_value=1, value=50)
            entry = st.number_input("💲 קנייה ($)", min_value=0.01, value=100.0, step=1.0)
            exit_ = st.number_input("💲 מכירה ($)", min_value=0.01, value=110.0, step=1.0)
            rate = st.number_input("💱 $/₪", min_value=2.0, value=3.75, step=0.05)

        if st.button("🧮 חשב", type="primary", key="tax_calc"):
            is_us  = "אמריקאית" in stype
            is_div = "דיבידנד" in itype
            profit_usd = (exit_ - entry) * qty
            profit_ils = profit_usd * rate

            b = BROKERS[broker]
            fe = _fee(broker, entry * qty * rate, qty)
            fx = _fee(broker, exit_ * qty * rate, qty)
            mult = rate if b["cur"] == "USD" else 1
            total_fees = round((fe + fx) * mult, 2)

            tax = _tax(profit_ils, is_div, is_us)
            net = round(profit_ils - tax - total_fees, 2)
            eff = round((tax / profit_ils) * 100, 1) if profit_ils > 0 else 0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 רווח גולמי", f"₪{profit_ils:,.2f}")
            m2.metric("🏛️ מס", f"₪{tax:,.2f}", delta=f"-{eff:.1f}%", delta_color="inverse")
            m3.metric("🏦 עמלות", f"₪{total_fees:,.2f}", delta_color="inverse")
            m4.metric("✅ נטו אמיתי", f"₪{net:,.2f}")

            if is_us and is_div:
                st.info("ℹ️ ארה\"ב מנכה 15% במקור. ישראל גובה 25% סה\"כ → תשלם עוד 10%.")

    with t2:
        c1, c2, c3 = st.columns(3)
        with c1: val_c = st.number_input("שווי ($)", min_value=100.0, value=5000.0, step=500.0)
        with c2: qty_c = st.number_input("כמות", min_value=1, value=50)
        with c3: rate_c = st.number_input("$/₪", min_value=2.0, value=3.75, step=0.05)

        rows = []
        for name, b in BROKERS.items():
            val_ils = val_c * rate_c
            fee = _fee(name, val_ils, qty_c)
            fee_ils = fee * rate_c if b["cur"] == "USD" else fee
            pct = (fee_ils / val_ils) * 100 if val_ils > 0 else 0
            rows.append({
                "🏦 ברוקר": name,
                "עמלה": f"₪{fee_ils:.2f}",
                "% מהעסקה": f"{pct:.3f}%",
                "מינימום שנתי": f"₪{b['mo']*12:,}" if b["mo"] > 0 else "—",
            })
        df = pd.DataFrame(rows).sort_values("עמלה")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.success(f"💡 הזול ביותר: **{df.iloc[0]['🏦 ברוקר']}**")

    with t3:
        c1, c2 = st.columns(2)
        with c1:
            gains  = st.number_input("רווחי הון (₪)", min_value=0.0, value=20000.0, step=1000.0)
            divs   = st.number_input("דיבידנדים (₪)", min_value=0.0, value=3000.0, step=100.0)
            losses = st.number_input("הפסדים לקיזוז (₪)", min_value=0.0, value=2000.0, step=100.0)
        with c2:
            net_g  = gains - losses
            tax_g  = max(net_g * TAX_CG, 0)
            tax_d  = divs * TAX_DIV
            total  = round(tax_g + tax_d, 2)
            after  = round(net_g + divs - total, 2)
            st.metric("רווח הון נטו", f"₪{net_g:,.2f}")
            st.metric("מס רווח הון 25%", f"₪{tax_g:,.2f}")
            st.metric("מס דיבידנד 25%", f"₪{tax_d:,.2f}")
            st.metric("☠️ חבות מס שנתית", f"₪{total:,.2f}", delta_color="inverse")
            st.metric("✅ נטו", f"₪{after:,.2f}")
        if losses > 0:
            st.info(f"💡 Tax Loss Harvesting: חסכת ₪{losses*TAX_CG:,.2f}!")
        st.warning("⚠️ לצרכי מידע בלבד. פנה לרואה חשבון.")
