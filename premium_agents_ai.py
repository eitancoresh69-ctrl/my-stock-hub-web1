# premium_agents_ai.py
import streamlit as st
import pandas as pd

def render_premium_agents(df_all):
    st.markdown('<div class="ai-card" style="border-right-color: #ffd700;"><b>🤖 סוכני השקעה פרימיום (Premium AI Models):</b> סוכנים מיוחדים בעלי אסטרטגיות נישה מחמירות מוול-סטריט. כל סוכן מקבל 5,000 ש"ח ומחפש עיוותי שוק ספציפיים.</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["👑 סוכן אריסטוקרטים (דיבידנד)", "🕵️‍♂️ סוכן פנימי (Insiders)", "🚑 סוכן משברים (Deep Value)"])
    usd_rate = 3.8
    
    with t1:
        st.markdown("### 👑 סוכן אריסטוקרטים (Dividend Growth)")
        st.write("מאתר חברות עם תזרים מזומנים מפלצתי שמחלקות ומגדילות דיבידנד, תוך שמירה על יחס חלוקה בריא.")
        if 'div_cash_ils' not in st.session_state:
            st.session_state.div_cash_ils = 5000.0
            st.session_state.div_portfolio = []
            
        col1, col2 = st.columns(2)
        col1.metric("💵 תקציב סוכן דיבידנד", f"₪{st.session_state.div_cash_ils:,.2f}")
        port_val = sum([p['Total_Value'] for p in st.session_state.div_portfolio]) if st.session_state.div_portfolio else 0
        col2.metric("💼 שווי מניות דיבידנד (דולר)", f"${port_val:,.2f}")

        if st.button("🚀 הפעל סוכן אריסטוקרטים"):
            if st.session_state.div_cash_ils > 100:
                # סינון: תשואה מעל 2%, יחס חלוקה מתחת ל-60% למען בטיחות, ויותר מזומן מחוב
                candidates = df_all[(df_all['DivYield'] > 2.0) & (df_all['PayoutRatio'] > 0) & (df_all['PayoutRatio'] < 60) & (df_all['CashVsDebt'] == "✅")]
                if not candidates.empty:
                    st.success("הסוכן מצא 'פרות חולבות' איכותיות!")
                    inv_per_stock = (st.session_state.div_cash_ils / usd_rate) / len(candidates)
                    new_port = []
                    for _, row in candidates.iterrows():
                        px_usd = row['Price'] if row['Currency'] == "$" else (row['Price']/100)/usd_rate
                        qty = inv_per_stock / px_usd if px_usd > 0 else 0
                        reason = f"תשואת דיבידנד של {row['DivYield']:.1f}%. יחס החלוקה עומד על {row['PayoutRatio']:.1f}% בלבד (דיבידנד בטוח עם פוטנציאל הגדלה). מאזן: קריטריון 6 מה-PDF עבר בהצלחה."
                        new_port.append({"Symbol": row['Symbol'], "Price": row['PriceStr'], "Qty": round(qty, 2), "Total_Value": inv_per_stock, "Reason": reason})
                    st.session_state.div_portfolio = new_port
                    st.session_state.div_cash_ils = 0
                    st.rerun()
                else:
                    st.error("לא נמצאו מניות דיבידנד בטוחות העומדות בקריטריונים הנוקשים כרגע.")
        
        if st.session_state.div_portfolio:
            for p in st.session_state.div_portfolio:
                st.info(f"**{p['Symbol']}**: {p['Reason']}")
            if st.button("מכור תיק דיבידנד"):
                st.session_state.div_cash_ils = port_val * usd_rate
                st.session_state.div_portfolio = []
                st.rerun()
                
    with t2:
        st.markdown("### 🕵️‍♂️ סוכן המעקב (Insider Trading Clone)")
        st.write("סוכן שעוקב אחרי ההנהלה. קונה רק מניות שבהן מנכ\"לים מחזיקים נתח ענק מכספם הפרטי, פלוס קונצנזוס אנליסטים חיובי.")
        if 'ins_cash_ils' not in st.session_state:
            st.session_state.ins_cash_ils = 5000.0
            st.session_state.ins_portfolio = []
            
        col1, col2 = st.columns(2)
        col1.metric("💵 תקציב סוכן מעקב", f"₪{st.session_state.ins_cash_ils:,.2f}")
        port_val = sum([p['Total_Value'] for p in st.session_state.ins_portfolio]) if st.session_state.ins_portfolio else 0
        col2.metric("💼 שווי תיק (דולר)", f"${port_val:,.2f}")

        if st.button("🚀 הפעל סוכן מעקב מנכ\"לים"):
            if st.session_state.ins_cash_ils > 100:
                # סינון: הנהלה מחזיקה מעל 2% מהחברה ויש אפסייד של מעל 10%
                candidates = df_all[(df_all['InsiderHeld'] >= 2) & (df_all['TargetUpside'] > 10)]
                if not candidates.empty:
                    st.success("הסוכן זיהה פעילות והלימה של 'כסף חכם' בהנהלות!")
                    inv_per_stock = (st.session_state.ins_cash_ils / usd_rate) / len(candidates)
                    new_port = []
                    for _, row in candidates.iterrows():
                        px_usd = row['Price'] if row['Currency'] == "$" else (row['Price']/100)/usd_rate
                        qty = inv_per_stock / px_usd if px_usd > 0 else 0
                        reason = f"הנהלת החברה מחזיקה {row['InsiderHeld']:.1f}% מהמניות. במקביל, קונצנזוס האנליסטים צופה זינוק של {row['TargetUpside']:.1f}%. ה-AI מזהה שילוב עוצמתי של אמון פנימי ותמיכה חיצונית."
                        new_port.append({"Symbol": row['Symbol'], "Price": row['PriceStr'], "Qty": round(qty, 2), "Total_Value": inv_per_stock, "Reason": reason})
                    st.session_state.ins_portfolio = new_port
                    st.session_state.ins_cash_ils = 0
                    st.rerun()
                else:
                    st.error("לא נמצאו איתותים משמעותיים מבעלי העניין ואנליסטים בשוק כרגע.")
                    
        if st.session_state.ins_portfolio:
            for p in st.session_state.ins_portfolio:
                st.warning(f"**{p['Symbol']}**: {p['Reason']}")
            if st.button("מכור תיק Insiders"):
                st.session_state.ins_cash_ils = port_val * usd_rate
                st.session_state.ins_portfolio = []
                st.rerun()

    with t3:
        st.markdown("### 🚑 סוכן משברים (Deep Value)")
        st.write("מחפש חברות נהדרות (לפי ה-PDF) שנמצאות ב'פאניקה זמנית' של השוק (RSI נמוך מאוד) ונחתכו במחיר.")
        if 'deep_cash_ils' not in st.session_state:
            st.session_state.deep_cash_ils = 5000.0
            st.session_state.deep_portfolio = []
            
        col1, col2 = st.columns(2)
        col1.metric("💵 תקציב סוכן משברים", f"₪{st.session_state.deep_cash_ils:,.2f}")
        port_val = sum([p['Total_Value'] for p in st.session_state.deep_portfolio]) if st.session_state.deep_portfolio else 0
        col2.metric("💼 שווי תיק משברים (דולר)", f"${port_val:,.2f}")

        if st.button("🚀 הפעל סוכן קניית פאניקה (Deep Value)"):
            if st.session_state.deep_cash_ils > 100:
                # סינון: ציון פדף 3 ומעלה, RSI התרסק מתחת ל-35, אבל מזומן עדיין עולה על חוב!
                candidates = df_all[(df_all['Score'] >= 3) & (df_all['RSI'] < 35) & (df_all['CashVsDebt'] == "✅")]
                if not candidates.empty:
                    st.success("נמצאו הזדמנויות של מכירות-יתר במניות איכותיות! הסוכן קונה את הדיפ.")
                    inv_per_stock = (st.session_state.deep_cash_ils / usd_rate) / len(candidates)
                    new_port = []
                    for _, row in candidates.iterrows():
                        px_usd = row['Price'] if row['Currency'] == "$" else (row['Price']/100)/usd_rate
                        qty = inv_per_stock / px_usd if px_usd > 0 else 0
                        reason = f"השוק מעניש את המניה (RSI התרסק ל-{row['RSI']:.0f}). עם זאת, ציון ה-PDF יציב ({row['Score']}/6) והמאזן נקי מחובות (קריטריון 6). ה-AI מנצל את הפאניקה."
                        new_port.append({"Symbol": row['Symbol'], "Price": row['PriceStr'], "Qty": round(qty, 2), "Total_Value": inv_per_stock, "Reason": reason})
                    st.session_state.deep_portfolio = new_port
                    st.session_state.deep_cash_ils = 0
                    st.rerun()
                else:
                    st.error("השוק לא נמצא במצב של מכירות יתר בחברות בעלות מאזן חזק כרגע.")
                    
        if st.session_state.deep_portfolio:
            for p in st.session_state.deep_portfolio:
                st.error(f"**{p['Symbol']}**: {p['Reason']}")
            if st.button("מכור תיק משברים"):
                st.session_state.deep_cash_ils = port_val * usd_rate
                st.session_state.deep_portfolio = []
                st.rerun()
