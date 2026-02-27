# pro_tools_ai.py — כסף חכם + רנטגן תיק
import streamlit as st
import pandas as pd
import plotly.express as px


def _smart_label(upside, insider):
    if insider > 10 and upside > 15:
        return "🔥 שורי מאוד: הנהלה מושקעת + אנליסטים אופטימיים"
    elif insider > 5 and upside > 5:
        return "🟢 חיובי: הלימת אינטרסים טובה"
    elif insider < 1 and upside < 0:
        return "🔴 אזהרה: הנהלה לא מחזיקה + אנליסטים שליליים"
    elif upside > 20:
        return "📈 אופטימיות: בדוק שהמספרים מצדיקים"
    return "⚖️ ניטרלי"


def render_pro_tools(df_all, portfolio_df):
    st.markdown(
        '<div class="ai-card" style="border-right-color: #3f51b5;">'
        '<b>🧰 כלים מקצועיים:</b> כסף חכם + רנטגן תיק.</div>',
        unsafe_all
