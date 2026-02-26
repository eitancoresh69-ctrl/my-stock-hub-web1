# premium_agents_ai.py
import streamlit as st
import pandas as pd

def render_premium_agents(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ffd700;"><b>🤖 סוכני השקעה פרימיום:</b> מעקב חי וסיכום רווחים בכל סגירת פוזיציה.</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["👑 סוכן אריסטוקרטים", "🕵️‍♂️ סוכן פנימי", "🚑 סוכן משברים"])
    usd_rate = 3.8
    
    with t1:
        st.markdown("### 👑 סוכן אריסטוקרטים (Dividend)")
        if 'div_cash_ils' not in st.session_state:
            st.session_state.div_cash_ils, st.session_state.div_portfolio = 5000.0, []
        if 'div_receipt' in st.session_state: st.info(st.session_state.div_receipt)

        port_val = sum([p['Total_Value'] for p in st.session_state.div_portfolio]) if st.session_state.div_portfolio else 0
        st.write(f"שווי נוכחי (דולר): **${port_val:,.2f}**")

        if st.button("🚀 הפעל סוכן דיבידנד"):
            if st.session_state.div_cash_ils > 100:
                if 'div_receipt' in st.session_state: del st.session_state.div_receipt
                candidates = df_all[(df_all['DivYield'] > 2.0) & (df_all['PayoutRatio'] < 60) & (df_all['CashVsDebt'] == "✅")]
                if not candidates.empty:
                    inv = (st.session_state.div_cash_ils / usd_rate) / len(candidates)
                    st.session_state.div_portfolio = [{"Symbol": r['Symbol'], "Total_Value": inv} for _, r in candidates.iterrows()]
                    st.session_state.div_cash_ils = 0
                    st.rerun()
                    
        if st.session_state.div_portfolio:
            if st.button("מכור תיק דיבידנד"):
                profit = (port_val * usd_rate) - 5000.0
                st.session_state.div_cash_ils, st.session_state.div_portfolio = 5000.0, []
                st.session_state.div_receipt = f"💰 התיק נמכר. רווח/הפסד סופי: ₪{profit:.2f}"
                st.rerun()

    with t2:
        st.markdown("### 🕵️‍♂️ סוכן המעקב (Insiders)")
        if 'ins_cash_ils' not in st.session_state:
            st.session_state.ins_cash_ils, st.session_state.ins_portfolio = 5000.0, []
        if 'ins_receipt' in st.session_state: st.info(st.session_state.ins_receipt)

        port_val = sum([p['Total_Value'] for p in st.session_state.ins_portfolio]) if st.session_state.ins_portfolio else 0
        st.write(f"שווי נוכחי (דולר): **${port_val:,.2f}**")

        if st.button("🚀 הפעל סוכן מעקב"):
            if st.session_state.ins_cash_ils > 100:
                if 'ins_receipt' in st.session_state: del st.session_state.ins_receipt
                candidates = df_all[(df_all['InsiderHeld'] >= 2) & (df_all['TargetUpside'] > 10)]
                if not candidates.empty:
                    inv = (st.session_state.ins_cash_ils / usd_rate) / len(candidates)
                    st.session_state.ins_portfolio = [{"Symbol": r['Symbol'], "Total_Value": inv} for _, r in candidates.iterrows()]
                    st.session_state.ins_cash_ils = 0
                    st.rerun()

        if st.session_state.ins_portfolio:
            if st.button("מכור תיק Insiders"):
                profit = (port_val * usd_rate) - 5000.0
                st.session_state.ins_cash_ils, st.session_state.ins_portfolio = 5000.0, []
                st.session_state.ins_receipt = f"🕵️‍♂️ התיק נמכר. רווח/הפסד סופי: ₪{profit:.2f}"
                st.rerun()

    with t3:
        st.markdown("### 🚑 סוכן משברים (Deep Value)")
        if 'deep_cash_ils' not in st.session_state:
            st.session_state.deep_cash_ils, st.session_state.deep_portfolio = 5000.0, []
        if 'deep_receipt' in st.session_state: st.info(st.session_state.deep_receipt)

        port_val = sum([p['Total_Value'] for p in st.session_state.deep_portfolio]) if st.session_state.deep_portfolio else 0
        st.write(f"שווי נוכחי (דולר): **${port_val:,.2f}**")

        if st.button("🚀 הפעל סוכן פאניקה"):
            if st.session_state.deep_cash_ils > 100:
                if 'deep_receipt' in st.session_state: del st.session_state.deep_receipt
                candidates = df_all[(df_all['Score'] >= 3) & (df_all['RSI'] < 35) & (df_all['CashVsDebt'] == "✅")]
                if not candidates.empty:
                    inv = (st.session_state.deep_cash_ils / usd_rate) / len(candidates)
                    st.session_state.deep_portfolio = [{"Symbol": r['Symbol'], "Total_Value": inv} for _, r in candidates.iterrows()]
                    st.session_state.deep_cash_ils = 0
                    st.rerun()

        if st.session_state.deep_portfolio:
            if st.button("מכור תיק משברים"):
                profit = (port_val * usd_rate) - 5000.0
                st.session_state.deep_cash_ils, st.session_state.deep_portfolio = 5000.0, []
                st.session_state.deep_receipt = f"🚑 התיק נמכר. רווח/הפסד סופי: ₪{profit:.2f}"
                st.rerun()
