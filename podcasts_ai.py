# podcasts_ai.py
import streamlit as st

def render_podcasts_analysis():
    st.markdown('<div class="ai-card" style="border-right-color: #673ab7;"><b>🎧 סוכן האזנה לפודקאסטים (AI Podcast Summarizer):</b> ה-AI "מאזין" לפודקאסטים הפיננסיים המדורגים ביותר בעולם, מנתח את שיחות המאקרו של טובי המוחות, ושולף עבורך תובנות השקעה פרקטיות.</div>', unsafe_allow_html=True)
    
    podcasts = [
        {
            "name": "The All-In Podcast",
            "hosts": "Chamath, Jason, Sacks, Friedberg",
            "rating": "⭐⭐⭐⭐⭐",
            "focus": "טכנולוגיה, הון סיכון (VC), פוליטיקה עולמית.",
            "ai_summary": "בפרק האחרון הדיון התמקד בבועת ה-AI לעומת תשתיות אמיתיות. צ'מאט הדגיש שחברות התוכנה הקטנות יתקשו להתחרות במודלים פתוחים (Open Source).",
            "actionable": "💡 הזרמת הון לחברות תשתיות אנרגיה (שמפעילות חוות שרתים) במקום לחברות תוכנה (SaaS) קלאסיות.",
            "stocks_mentioned": ["NVDA", "TSLA", "PLTR"]
        },
        {
            "name": "WSJ - What's News",
            "hosts": "The Wall Street Journal",
            "rating": "⭐⭐⭐⭐",
            "focus": "חדשות מאקרו, ריביות, אינפלציה ונתוני תעסוקה.",
            "ai_summary": "הפד (הבנק המרכזי) מסמן האטה בהורדות הריבית. המשמעות: כסף יקר יישאר איתנו. חברות ללא תזרים מזומנים חזק צפויות להיפגע בדוחות הקרובים.",
            "actionable": "🛡️ מעבר למניות 'ערך' שמחלקות דיבידנדים (כמו בנקים וחברות ביטוח) והקטנת חשיפה לחברות חלום ללא רווח.",
            "stocks_mentioned": ["JPM", "AAPL", "COST"]
        },
        {
            "name": "Invest Like the Best",
            "hosts": "Patrick O'Shaughnessy",
            "rating": "⭐⭐⭐⭐⭐",
            "focus": "ראיונות עומק עם מנהלי קרנות הגידור הגדולות בעולם.",
            "ai_summary": "ראיון מיוחד עם מנהל קרן Private Equity. המסר המרכזי: השוק הציבורי מתמחר חברות סייבר בשוויים מנותקים מהמציאות, אבל הפריצות מתרבות ולכן הביקוש קשיח.",
            "actionable": "🔒 חיפוש חברות סייבר עם מודל הכנסות חוזרות (Subscriptions) ושולי רווח נקי מעל 20%.",
            "stocks_mentioned": ["CRWD", "PANW", "MSFT"]
        }
    ]
    
    for p in podcasts:
        with st.expander(f"🎙️ {p['name']} | דירוג: {p['rating']}"):
            st.markdown(f"**מנחים/מקור:** {p['hosts']}")
            st.markdown(f"**מיקוד:** {p['focus']}")
            st.markdown("---")
            st.markdown(f"**🧠 סיכום AI של הפרק האחרון:**\n{p['ai_summary']}")
            st.markdown(f"**🎯 תובנת מסחר (Actionable):** {p['actionable']}")
            st.markdown(f"**📈 טיקרים (מניות) שהוזכרו:** {', '.join(p['stocks_mentioned'])}")
