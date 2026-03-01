# 🚀 מדריך התקנה והפעלה — Investment Hub Elite 2026

## ✅ דרישות מינימליות
- Python 3.10+
- חיבור אינטרנט
- ~200MB דיסק

---

## 🖥️ הרצה מקומית (מהיר ביותר)

```bash
# 1. פתח טרמינל בתיקיית הפרויקט
cd stock-hub-final

# 2. התקן תלויות
pip install -r requirements.txt

# 3. הרץ!
streamlit run app.py
```

הדפדפן ייפתח אוטומטית ב: http://localhost:8501

---

## ☁️ פריסה ל-Streamlit Cloud (חינם, אינטרנטי)

1. צור חשבון ב-https://streamlit.io
2. צור repo ב-GitHub והעלה את כל הקבצים
3. ב-Streamlit Cloud: New App → בחר את ה-repo → `app.py`
4. לחץ Deploy!

**⚠️ חשוב:** הנתונים נשמרים ב-SQLite מקומי. בענן — הנתונים מתאפסים עם כל deploy.
   פתרון: השתמש ב-st.secrets עם Supabase/PlanetScale לאחסון קבוע בענן.

---

## 🔑 הגדרות API (כולן חינמיות)

### 1. Finnhub — מחירים בזמן אמת
```
1. הרשם ב: https://finnhub.io (חינם, 60 קריאות/דקה)
2. קבל API Key
3. פתח realtime_data.py שורה 14:
   FINNHUB_API_KEY = "YOUR_KEY_HERE"
```

### 2. FRED — נתוני מאקרו
```
1. הרשם ב: https://fred.stlouisfed.org/docs/api/api_key.html
2. קבל API Key חינמי
3. פתח realtime_data.py שורה 156:
   FRED_API_KEY = "YOUR_KEY_HERE"
```

### 3. Telegram Bot — התראות לטלפון
```
1. פתח Telegram → חפש @BotFather
2. שלח /newbot ועקוב אחרי ההוראות
3. קבל TOKEN
4. שלח הודעה לבוט שלך
5. פתח: https://api.telegram.org/bot<TOKEN>/getUpdates
6. מצא את "id" בתוך "chat" — זה ה-Chat ID
7. הכנס Token + Chat ID בטאב "📱 טלגרם" באפליקציה
```

---

## 📁 מבנה קבצים

| קובץ | תיאור |
|------|--------|
| `app.py` | מרכז האפליקציה — 27 טאבים |
| `config.py` | רשימות מניות, סחורות, קריפטו, הגדרות |
| `logic.py` | שליפת נתונים — מניות/סחורות/קריפטו/ת"א |
| `storage.py` | שמירה ל-SQLite — נתונים לא נאבדים! |
| `ai_portfolio.py` | תיק מנוהל AI — קנייה/מכירה אוטומטית |
| `ml_learning_ai.py` | למידת מכונה אמיתית — Random Forest |
| `realtime_data.py` | Finnhub + Fear&Greed + FRED מאקרו |
| `pattern_ai.py` | זיהוי דפוסי Chart + Regime Detection |
| `portfolio_optimizer.py` | Markowitz MPT + Efficient Frontier |
| `telegram_ai.py` | בוט טלגרם — התראות Push |
| `commodities_tab.py` | סחורות: זהב, כסף, נפט |
| `hub_data.db` | מסד נתונים SQLite (נוצר אוטומטית) |

---

## 🔧 התאמה אישית

### הוסף מניות ל-Watchlist
פתח `config.py` ועדכן:
```python
MY_STOCKS_BASE = ["AAPL","NVDA","MSFT","TSLA",
                   "POLI.TA","LUMI.TA",  # ת"א
                   "GC=F",               # זהב
                   "BTC-USD"]            # קריפטו
```

### שנה הון תחלתי של תיק AI
```python
AI_PORTFOLIO_DEFAULTS = {
    "initial_capital": 10000.0,  # ₪
    "stop_loss_pct":   8.0,      # %
    "take_profit_pct": 20.0,     # %
}
```

---

## 🆘 פתרון תקלות נפוצות

**"ModuleNotFoundError: sklearn"**
```bash
pip install scikit-learn
```

**"yfinance timeout"**
- בדוק חיבור אינטרנט
- נסה שוב — yfinance לפעמים איטי

**"DataError: No objects to concatenate"**
- הרשימה ריקה — בדוק שיש מניות ב-config.py

**הנתונים מתאפסים**
- ודא שה-`hub_data.db` קיים בתיקייה
- אל תמחק קובץ זה!
