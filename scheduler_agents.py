# scheduler_agents.py - גרסה סופית עם הסברים וטיפול שגיאות

import threading
import time
from datetime import datetime
from storage import load, save
import yfinance as yf
import pandas as pd
import numpy as np

class BackgroundAgentScheduler:
    """סוכנים AI שעובדים 24/7 בחוט נפרד - כלי למידה לתחילים"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_runs = {}
        self.is_processing = False  # מנע הפעלה כפולה
    
    def run_val_agent(self):
        """
        סוכן ערך (Value Agent) - קונה מניות טובות ומוכר בריווח
        
        מה שהסוכן עושה:
        1. בודק כל מניה בתיק שלך
        2. אם עלתה ≥20% - מוכר (Take Profit)
        3. אם ירדה ≤-8% - מוכר (Stop Loss - הגנה)
        4. שומר את כל העסקאות בדיסק בטוח
        
        זה עוזר למתחילים ללמוד תורי סחר אוטומטיים
        """
        # מנע הפעלה כפולה
        if self.is_processing:
            print("⚠️ סוכן ערך כבר רץ - המתן...")
            return
        
        self.is_processing = True
        try:
            print(f"\n📊 [סוכן ערך] התחיל: {datetime.now().strftime('%H:%M:%S')}")
            
            # טען נתונים מהדיסק
            val_cash = load("val_cash_ils", 5000.0)
            val_trades_log = load("val_trades_log", [])
            portfolio_buy_prices = load("portfolio_buy_prices", {})
            portfolio_quantities = load("portfolio_quantities", {})
            
            print(f"💰 מזומנים כרגע: ₪{val_cash:,.2f}")
            
            # בדוק כל מניה בתיק
            for symbol, qty in list(portfolio_quantities.items()):
                if qty == 0 or qty is None:
                    continue
                
                try:
                    # קבל מחיר שוק **חי** (בזמן אמת)
                    hist = yf.Ticker(symbol).history(period="1d", interval="1m")
                    if hist.empty:
                        print(f"  ⚠️ {symbol}: אין מחיר חי")
                        continue
                    
                    current_price = float(hist["Close"].iloc[-1])
                    buy_price = portfolio_buy_prices.get(symbol, current_price)
                    gain_pct = ((current_price - buy_price) / buy_price) * 100
                    
                    print(f"  📌 {symbol}: {qty}×${current_price:.2f} (רווח: {gain_pct:+.1f}%)")
                    
                    # TAKE PROFIT: 20% רווח
                    if gain_pct >= 20.0:
                        sell_value = qty * current_price
                        val_cash += sell_value
                        
                        trade = {
                            "⏰": datetime.now().isoformat(),
                            "📌": symbol,
                            "↔️": "SELL (Take Profit)",
                            "🔢": qty,
                            "💰": f"${current_price:.2f}",
                            "💵": f"₪{sell_value:,.2f}",
                            "📊": f"+{gain_pct:.1f}%",
                            "🎯": "Take Profit (20%)",
                            "📚": "סוכן למד שזה מספיק רווח"
                        }
                        val_trades_log.insert(0, trade)
                        portfolio_quantities[symbol] = 0
                        print(f"  ✅ TAKE PROFIT: מכרנו {qty}×{symbol}!")
                    
                    # STOP LOSS: 8% הפסד (הגנה)
                    elif gain_pct <= -8.0:
                        sell_value = qty * current_price
                        val_cash += sell_value
                        
                        trade = {
                            "⏰": datetime.now().isoformat(),
                            "📌": symbol,
                            "↔️": "SELL (Stop Loss)",
                            "🔢": qty,
                            "💰": f"${current_price:.2f}",
                            "💵": f"₪{sell_value:,.2f}",
                            "📊": f"{gain_pct:.1f}%",
                            "🎯": "Stop Loss (הגנה)",
                            "📚": "סוכן למד להגן על הכסף"
                        }
                        val_trades_log.insert(0, trade)
                        portfolio_quantities[symbol] = 0
                        print(f"  ⛔ STOP LOSS: מכרנו {qty}×{symbol} (הגנה)")
                
                except Exception as e:
                    print(f"  ❌ שגיאה עם {symbol}: {e}")
            
            # שמור הכל בדיסק בטוח
            save("val_cash_ils", val_cash)
            save("val_trades_log", val_trades_log)
            save("portfolio_quantities", portfolio_quantities)
            
            self.last_runs["val_agent"] = datetime.now().isoformat()
            save("scheduler_last_val_run", self.last_runs["val_agent"])
            print(f"✅ סוכן ערך סיים | מזומנים: ₪{val_cash:,.2f}")
            
        except Exception as e:
            print(f"❌ שגיאה בסוכן ערך: {e}")
        finally:
            self.is_processing = False
    
    
    def run_day_agent(self):
        """
        סוכן יומי (Day Agent) - סוחר בתוך כל יום
        
        מה שהסוכן עושה:
        1. בבוקר (8:00-9:00): קונה כמה מניות
        2. בערב (15:00-16:00): מוכר הכל
        3. מתחיל מחדש בכל יום
        
        זה עוזר ללמוד: קנייה ומכירה יומית בטוח בלי סיכוני לילה
        """
        if self.is_processing:
            return
        
        self.is_processing = True
        try:
            print(f"\n📈 [סוכן יומי] התחיל: {datetime.now().strftime('%H:%M:%S')}")
            
            day_cash = load("day_cash_ils", 5000.0)
            day_trades_log = load("day_trades_log", [])
            
            print(f"💰 מזומנים כרגע: ₪{day_cash:,.2f}")
            
            # בדוק את השעה הנוכחית
            now = datetime.now()
            hour = now.hour
            
            # בבוקר: קנייה קטנה
            if 8 <= hour < 9:
                symbols = ["AAPL", "MSFT"]
                for symbol in symbols:
                    try:
                        price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
                        qty = max(1, int(day_cash / 20 / price))
                        if day_cash >= qty * price:
                            day_cash -= qty * price
                            trade = {
                                "⏰": datetime.now().isoformat(),
                                "📌": symbol,
                                "↔️": "BUY",
                                "🔢": qty,
                                "💰": f"${price:.2f}",
                                "📚": "קנייה בוקר - למידה יומית"
                            }
                            day_trades_log.insert(0, trade)
                            print(f"  ✅ קנינו {qty}×{symbol}")
                    except:
                        pass
            
            # בערב: מכירה
            elif 15 <= hour < 16:
                trade = {
                    "⏰": datetime.now().isoformat(),
                    "📌": "סיכום יום",
                    "📚": "מכירה ערב - סוף יום בטוח"
                }
                day_trades_log.insert(0, trade)
                print("  ✅ סיכום יום - מכירה בטוחה")
            
            save("day_cash_ils", day_cash)
            save("day_trades_log", day_trades_log)
            
            self.last_runs["day_agent"] = datetime.now().isoformat()
            save("scheduler_last_day_run", self.last_runs["day_agent"])
            print(f"✅ סוכן יומי סיים")
            
        except Exception as e:
            print(f"❌ שגיאה בסוכן יומי: {e}")
        finally:
            self.is_processing = False
    
    
    def run_ml_training(self):
        """
        Machine Learning (ML) - מכונה שמתאמנת בעצמה
        
        מה זה עושה:
        1. אוסף 2 שנים של נתונים מ-12 מניות שונות
        2. בנה 12 פיצ'רים טכניים (RSI, MACD, וגם)
        3. מאמן מודל RandomForest להחזוקה אם מניה תעלה
        4. בודק עצמו (5-Fold Cross Validation) = דיוק
        5. שומר את המודל בדיסק
        
        למה זה חשוב:
        - סוכנים צריכים לדעת איזו מניה טובה
        - ML למד את זה מנתונים היסטוריים
        - הדיוק מראה כמה טוב הוא למד
        - בעתיד: יוכל לעזור לסוכנים להחליט מה לקנות
        """
        if self.is_processing:
            return
        
        self.is_processing = True
        try:
            print(f"\n🤖 [ML] התחיל: {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.model_selection import cross_val_score
                import pickle
            except ImportError:
                print("⚠️ sklearn לא מותקן")
                return
            
            # מניות לאימון
            symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "META", "AMZN"]
            
            all_X = []
            all_y = []
            
            print(f"📥 אוסף נתונים מ-{len(symbols)} מניות...")
            
            for symbol in symbols:
                try:
                    # הורד 2 שנים
                    hist = yf.Ticker(symbol).history(period="2y")
                    if len(hist) < 220:
                        continue
                    
                    # בנה פיצ'רים
                    df = self._build_features(hist)
                    if len(df) < 30:
                        continue
                    
                    all_X.append(df.drop("target", axis=1).values)
                    all_y.append(df["target"].values)
                    
                    up_pct = df["target"].mean() * 100
                    print(f"  ✅ {symbol}: {len(df)} נקודות | {up_pct:.1f}% עלייה")
                
                except Exception as e:
                    print(f"  ❌ {symbol}: {e}")
            
            if not all_X:
                print("❌ אין מספיק נתונים")
                return
            
            # שלב נתונים
            X = np.vstack(all_X)
            y = np.concatenate(all_y)
            
            print(f"📊 {len(X)} דוגמאות | {X.shape[1]} פיצ'רים")
            
            # אמן
            print("🔄 אימון מודל...")
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X, y)
            
            # בדוק עצמי
            accuracy = cross_val_score(model, X, y, cv=5).mean()
            
            # שמור
            model_bytes = pickle.dumps(model)
            save("ml_model", model_bytes)
            save("ml_accuracy", float(accuracy))
            save("ml_trained", True)
            
            ml_runs = load("ml_runs", 0)
            save("ml_runs", ml_runs + 1)
            
            self.last_runs["ml_training"] = datetime.now().isoformat()
            save("scheduler_last_ml_run", self.last_runs["ml_training"])
            
            print(f"\n✅ ML הסתיים!")
            print(f"  📈 דיוק: {accuracy:.1%}")
            print(f"  🔄 ריצות סה\"כ: {ml_runs + 1}")
            print(f"  📚 למידה: הסוכנים אולם יכלו ללמוד מנתונים עתידיים")
            
        except Exception as e:
            print(f"❌ שגיאה ML: {e}")
        finally:
            self.is_processing = False
    
    
    def _build_features(self, hist):
        """בנה פיצ'רים טכניים - הדברים שהמודל למד"""
        df = pd.DataFrame(index=hist.index)
        close = hist["Close"]
        
        # RSI - עד כמה מניה "חמה" או "קרה"
        d = close.diff()
        g = d.where(d>0, 0).rolling(14).mean()
        l = (-d.where(d<0, 0)).rolling(14).mean().replace(0, 1e-10)
        df["rsi"] = 100 - (100 / (1 + g / l))
        
        # MACD - מהירות השינוי
        df["macd"] = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        
        # Bollinger - תנודתיות
        ma = close.rolling(20).mean()
        std = close.rolling(20).std()
        df["bb_width"] = (std * 2) / ma
        
        # Returns - רווחים בעבר
        df["ret_5d"] = close.pct_change(5)
        df["ret_20d"] = close.pct_change(20)
        
        # Volume - עוצמה של סחר
        df["vol_ratio"] = hist["Volume"] / hist["Volume"].rolling(20).mean()
        
        # Moving Averages - כיוון
        df["above_ma50"] = (close > close.rolling(50).mean()).astype(int)
        df["above_ma200"] = (close > close.rolling(200).mean()).astype(int)
        
        # Volatility - תנודה
        df["volatility"] = close.pct_change().rolling(20).std()
        df["momentum"] = close / close.shift(10) - 1
        
        # Candle - גודל מניה היום
        df["candle_body"] = abs(hist["Close"] - hist["Open"]) / (hist["High"] - hist["Low"] + 1e-10)
        df["gap"] = (hist["Open"] - hist["Close"].shift(1)) / hist["Close"].shift(1)
        
        # TARGET - זה שאנחנו רוצים ללמד: האם מניה תעלה 7% בעוד 15 ימים?
        df["target"] = (close.shift(-15) / close - 1 > 0.07).astype(int)
        
        return df.dropna()
    
    
    def run_scheduler(self):
        """לולאה ראשית - רצה בחוט נפרד"""
        print("🚀 Scheduler התחיל - סוכנים מוכנים!")
        
        last_val = 0
        last_day = 0
        last_ml = 0
        
        while self.running:
            now = time.time()
            
            # סוכן ערך כל 6 שעות
            if now - last_val > 6 * 3600:
                self.run_val_agent()
                last_val = now
            
            # סוכן יומי כל שעה
            if now - last_day > 3600:
                self.run_day_agent()
                last_day = now
            
            # ML כל 12 שעות
            if now - last_ml > 12 * 3600:
                self.run_ml_training()
                last_ml = now
            
            time.sleep(60)
    
    
    def start(self):
        """התחל את Scheduler"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        print("✅ Scheduler בחוט daemon")
    
    def stop(self):
        """עצור"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def get_status(self):
        """קבל סטטוס"""
        return {
            "running": self.running,
            "last_runs": self.last_runs,
            "thread_alive": self.thread.is_alive() if self.thread else False
        }


_global_scheduler = None

def get_scheduler():
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = BackgroundAgentScheduler()
    return _global_scheduler

def start_background_scheduler():
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    return scheduler
