# 🚀 מדריך פריסה — Investment Hub Elite 2026

## ✅ מה השתנה בגרסה זו

### שמירת נתונים קבועה (הבעיה העיקרית — נפתרה!)
כל הנתונים הבאים **נשמרים אוטומטית** ולא נמחקים כשסוגרים הדפדפן:
- ✅ מחירי קנייה וכמויות בתיק הראשי
- ✅ מזומן ופוזיציות סוכן הערך
- ✅ מזומן ופוזיציות סוכן היומי
- ✅ לוג עסקאות מלא (היסטוריה)
- ✅ עסקאות סגורות + רווח/הפסד מצטבר
- ✅ הגדרות ML (דיוק, פרמטרים, תובנות)

הנתונים נשמרים בקובץ `hub_data.db` (SQLite) בתיקיית הפרויקט.

---

## 🖥️ הרצה מקומית (המחשב שלך)

```bash
# 1. התקן dependencies
pip install -r requirements.txt

# 2. הרץ
streamlit run app.py

# האתר יפתח בדפדפן: http://localhost:8501
```

---

## 🌐 פריסה לאינטרנט — Streamlit Community Cloud (חינם!)

### שלב 1: העלה ל-GitHub
1. צור חשבון חינמי ב-github.com
2. צור Repository חדש (שם: `stock-hub` למשל)
3. העלה את כל הקבצים:
   ```bash
   git init
   git add .
   git commit -m "first commit"
   git remote add origin https://github.com/YOUR_NAME/stock-hub.git
   git push -u origin main
   ```

### שלב 2: פרוס ב-Streamlit Cloud
1. היכנס ל: **https://share.streamlit.io**
2. לחץ "New app"
3. בחר את ה-Repository שיצרת
4. Main file path: `app.py`
5. לחץ "Deploy!" — האתר חי תוך 3 דקות! 🎉

### ⚠️ חשוב לגבי שמירת נתונים בענן
ב-Streamlit Cloud, קובץ `hub_data.db` נמחק כשהאפליקציה "מתעוררת" מחדש.
**פתרון** — הוסף מסד נתונים חיצוני חינמי:

#### אפשרות מומלצת: Supabase (PostgreSQL חינם)
1. צור חשבון ב-supabase.com
2. צור פרויקט חדש
3. קבל את ה-connection string
4. שנה ב-`storage.py` את `_get_conn()` לחיבור PostgreSQL

---

## 🔑 ניהול API Keys (לשלבים מתקדמים)

צור קובץ `.streamlit/secrets.toml`:
```toml
TELEGRAM_TOKEN = "your_token_here"
FINNHUB_KEY = "your_key_here"
```

וב-Streamlit Cloud — הוסף ב-Settings → Secrets.

---

## 📊 שדרוג ל-ML אמיתי (אופציונלי)

להוסיף ל-`requirements.txt`:
```
scikit-learn>=1.3.0
```

ואז ב-`ml_learning_ai.py` להחליף את הסימולציה ב:
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

def train_real_model(df_all):
    # מאמן על נתוני yfinance אמיתיים
    ...
```

---

## 🗂️ מבנה הקבצים לאחר העדכון

```
my-stock-hub-web1-main/
├── app.py              ← עודכן: טוען נתונים מהדיסק בהפעלה
├── simulator.py        ← עודכן: שומר אחרי כל פעולה
├── ml_learning_ai.py   ← עודכן: שומר אחרי אימון
├── storage.py          ← חדש: מנהל כל השמירה/טעינה
├── hub_data.db         ← נוצר אוטומטית: מסד הנתונים
├── requirements.txt    ← ללא שינוי (sqlite3 כלול ב-Python)
└── ... שאר הקבצים ללא שינוי
```
