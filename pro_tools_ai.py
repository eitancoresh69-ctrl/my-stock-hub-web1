# pro_tools_ai.py
import streamlit as st
import pandas as pd
import plotly.express as px

def get_smart_money_ai(upside, insider):
    if insider > 10 and upside > 15:
        return "🔥 שורי מאוד: בעלי העניין מחזיקים נתח ענק מהחברה (אמון מלא), והאנליסטים צופים זינוק חד."
    elif insider > 5 and upside > 5:
        return "🟢 חיובי: הלימה טובה של אינטרסים בין ההנהלה למשקיעים, פלוס אופטימיות בוול-סטריט."
    elif insider < 1 and upside < 0:
        return "🔴 אזהרה: ההנהלה כמעט לא מחזיקה מניות של עצמה, והאנליסטים צופים ירידת מחיר."
    elif upside > 20:
        return "📈 אופטימיות יתר?: האנליסטים מאוהבים במניה. יש לבדוק אם המספרים ב-PDF מצדיקים זאת."
    else:
        return "⚖️ ניטרלי: אין תנועות חריגות של 'כסף חכם' במניה זו כרגע."

def render_pro_tools(df_all, portfolio_df):
    st.markdown('<div class="ai-card" style="border-right-color: #3f51b5;"><b>🧰 ארגז הכלים המקצועי (Pro Tools):</b> מעקב אחרי "הכסף החכם" (פעולות מנכ"לים ותחזיות בנקים) וניתוח סיכונים (רנטגן) לתיק ההשקעות האישי שלך.</div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🕵️‍♂️ מעקב 'כסף חכם' (Insiders & Analysts)", "🩻 רנטגן לתיק (X-Ray)"])
    
    with t1:
        st.markdown("### 🕵️‍♂️ סורק 'הכסף החכם'")
        st.write("סורק זה פועל *בנוסף* לסורק ה-PDF, ומתמקד אך ורק במה שעושים המקושרים והמומחים.")
        
        if not df_all.empty:
            smart_df = df_all.copy()
            smart_df['AI_SmartMoney'] = smart_df.apply(lambda row: get_smart_money_ai(row['TargetUpside'], row['InsiderHeld']), axis=1)
            
            # מציג רק מניות עם אפסייד חיובי או אחזקות פנים משמעותיות
            smart_df = smart_df[(smart_df['TargetUpside'] > 5) | (smart_df['InsiderHeld'] > 2)].sort_values(by="TargetUpside", ascending=False)
            
            st.dataframe(
                smart_df[["Symbol", "PriceStr", "TargetUpside", "InsiderHeld", "AI_SmartMoney"]],
                column_config={
                    "Symbol": "סימול",
                    "PriceStr": "מחיר שוק",
                    "TargetUpside": st.column_config.NumberColumn("קונצנזוס אנליסטים (צפי %)", format="+%.1f%%"),
                    "InsiderHeld": st.column_config.NumberColumn("אחזקות הנהלה", format="%.2f%%"),
                    "AI_SmartMoney": st.column_config.TextColumn("ניתוח AI (מעקב)", width="large")
                },
                use_container_width=True, hide_index=True
            )
            
    with t2:
        st.markdown("### 🩻 צילום רנטגן לתיק (פיזור סיכונים)")
        if not portfolio_df.empty and not df_all.empty:
            # מיזוג התיק עם המידע של המניות (כדי לקבל מחיר וסקטור)
            merged = pd.merge(portfolio_df, df_all, on="Symbol")
            merged = merged[merged['Qty'] > 0] # רק מניות שבאמת קנינו
            
            if not merged.empty:
                merged['TotalValue'] = merged['Price'] * merged['Qty']
                total_portfolio_value = merged['TotalValue'].sum()
                
                # קיבוץ לפי סקטור
                sector_dist = merged.groupby('Sector')['TotalValue'].sum().reset_index()
                sector_dist['Percent'] = (sector_dist['TotalValue'] / total_portfolio_value) * 100
                
                col_chart, col_ai = st.columns(2)
                
                with col_chart:
                    fig = px.pie(sector_dist, values='TotalValue', names='Sector', title='פיזור התיק לפי סקטורים', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_ai:
                    st.markdown("#### 🧠 דוח ניהול סיכונים (AI)")
                    max_sector = sector_dist.loc[sector_dist['Percent'].idxmax()]
                    
                    if max_sector['Percent'] > 60:
                        st.error(f"**⚠️ אזהרת ריכוזיות חמורה!**\n\n {max_sector['Percent']:.1f}% מהכסף שלך מושקע בסקטור אחד בלבד ({max_sector['Sector']}). חשיפת יתר כזו מסוכנת. ה-AI ממליץ בחום לפזר השקעות לסקטורים דיפנסיביים (כמו בריאות או צריכה בסיסית) כדי להגן על התיק מקריסה נקודתית.")
                    elif max_sector['Percent'] > 40:
                        st.warning(f"**⚖️ ריכוזיות בינונית:** התיק נוטה בחוזקה לסקטור ה-{max_sector['Sector']} ({max_sector['Percent']:.1f}%). זה מעולה כשהסקטור עולה, אבל מגדיל את התנודתיות של התיק. מומלץ לשים לב.")
                    else:
                        st.success(f"**🛡️ פיזור מעולה:** התיק שלך מאוזן היטב. הסקטור הגדול ביותר ({max_sector['Sector']}) מהווה רק {max_sector['Percent']:.1f}% מהתיק. ניהול סיכונים מצוין שעומד בסטנדרטים של וול-סטריט.")
            else:
                st.info("הזן כמות (Qty) גדולה מ-0 בטבלת 'התיק שלי' כדי שה-AI יוכל לצלם את התיק.")
        else:
            st.info("אין נתונים לתיק. אנא ודא שהוספת מניות לתיק.")
