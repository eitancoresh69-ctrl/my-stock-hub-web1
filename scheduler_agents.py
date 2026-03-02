# scheduler_agents.py — סוכנים בזמן אמת 24/7 בחוט נפרד
# pip install schedule APScheduler

import threading
import time
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from storage import load, save, sync_to_disk
import json

class BackgroundAgentScheduler:
    """מנהל סוכנים שפועלים בחוט נפרד"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_runs = {}
        
    # ═══════════════════════════════════════════════════════════════
    # סוכן ערך (Value Agent) — סוחר יסודי
    # ═══════════════════════════════════════════════════════════════
    
    def run_val_agent(self):
        """סוכן ערך שפועל בחוט רקע - בדיקה יומית"""
        try:
            print(f"\n📊 [סוכן ערך] התחיל את הריצה ב-{datetime.now().strftime('%H:%M:%S')}")
            
            # טען סטאטוס נוכחי
            val_cash = load("val_cash_ils", 5000.0)
            val_portfolio = load("val_portfolio", [])
            val_trades_log = load("val_trades_log", [])
            portfolio_buy_prices = load("portfolio_buy_prices", {})
            portfolio_quantities = load("portfolio_quantities", {})
            
            print(f"💰 מזומנים כרגע: ₪{val_cash:,.2f}")
            
            # בדוק כל עמדה פתוחה
            for symbol, qty in list(portfolio_quantities.items()):
                if qty == 0 or qty is None:
                    continue
                
                try:
                    # קבל מחיר שוק חי
                    hist = yf.Ticker(symbol).history(period="1d", interval="1m")
                    if hist.empty:
                        print(f"⚠️ {symbol}: אין מחיר חי")
                        continue
                    
                    current_price = float(hist["Close"].iloc[-1])
                    buy_price = portfolio_buy_prices.get(symbol, current_price)
                    gain_pct = ((current_price - buy_price) / buy_price) * 100
                    
                    position_value = qty * current_price
                    
                    print(f"  📌 {symbol}: {qty}×${current_price:.2f} ({gain_pct:+.1f}%) = ₪{position_value:,.2f}")
                    
                    # ⏰ TAKE PROFIT: 20% רווח
                    if gain_pct >= 20.0:
                        sell_value = qty * current_price
                        val_cash += sell_value
                        
                        trade = {
                            "⏰": datetime.now().isoformat(),
                            "📌": symbol,
                            "↔️": "SELL",
                            "🔢": qty,
                            "💰": current_price,
                            "💵": sell_value,
                            "📊": f"+{gain_pct:.1f}%",
                            "🎯": "Take Profit (20%)",
                            "🤖": "val_agent"
                        }
                        val_trades_log.insert(0, trade)
                        portfolio_quantities[symbol] = 0
                        
                        print(f"  ✅ TAKE PROFIT: מכרנו {qty}×{symbol} ב-${current_price:.2f}")
                    
                    # ⛔ STOP LOSS: 8% הפסד
                    elif gain_pct <= -8.0:
                        sell_value = qty * current_price
                        val_cash += sell_value
                        
                        trade = {
                            "⏰": datetime.now().isoformat(),
                            "📌": symbol,
                            "↔️": "SELL",
                            "🔢": qty,
                            "💰": current_price,
                            "💵": sell_value,
                            "📊": f"{gain_pct:.1f}%",
                            "🎯": "Stop Loss (8%)",
                            "🤖": "val_agent"
                        }
                        val_trades_log.insert(0, trade)
                        portfolio_quantities[symbol] = 0
                        
                        print(f"  ⛔ STOP LOSS: מכרנו {qty}×{symbol} ב-${current_price:.2f}")
                
                except Exception as e:
                    print(f"  ❌ שגיאה בעדכון {symbol}: {e}")
            
            # שמור הכל בחזרה לדיסק
            save("val_cash_ils", val_cash)
            save("val_trades_log", val_trades_log)
            save("portfolio_quantities", portfolio_quantities)
            
            print(f"✅ סוכן ערך סיים בהצלחה | מזומנים: ₪{val_cash:,.2f}")
            self.last_runs["val_agent"] = datetime.now().isoformat()
            save("scheduler_last_val_run", self.last_runs["val_agent"])
            
        except Exception as e:
            print(f"❌ שגיאה בסוכן ערך: {e}")
    
    
    # ═══════════════════════════════════════════════════════════════
    # סוכן יומי (Day Agent) — סוחר תוך-יומי
    # ═══════════════════════════════════════════════════════════════
    
    def run_day_agent(self):
        """סוכן יומי שפועל בחוט רקע - בדיקה כל שעה"""
        try:
            print(f"\n📈 [סוכן יומי] התחיל את הריצה ב-{datetime.now().strftime('%H:%M:%S')}")
            
            day_cash = load("day_cash_ils", 5000.0)
            day_trades_log = load("day_trades_log", [])
            
            print(f"💰 מזומנים כרגע: ₪{day_cash:,.2f}")
            
            # דוגמה: תוך-יומי פשוט - קנה טכני בבוקר, מכור בערב
            symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "META"]
            
            # בדוק סוג היום
            now = datetime.now()
            hour = now.hour
            
            # בבוקר (8:00): קנה
            if 8 <= hour < 9:
                print("🌅 בוקר - קנייה קטנה")
                for symbol in symbols[:2]:  # רק 2 מניות
                    try:
                        price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
                        qty = int(day_cash / 10 / price)
                        if qty > 0:
                            day_cash -= qty * price
                            
                            trade = {
                                "⏰": datetime.now().isoformat(),
                                "📌": symbol,
                                "↔️": "BUY",
                                "🔢": qty,
                                "💰": price,
                                "💵": qty * price,
                                "🤖": "day_agent",
                                "🎯": "תוך-יומי קנייה"
                            }
                            day_trades_log.insert(0, trade)
                            print(f"  ✅ קנינו {qty}×{symbol} ב-${price:.2f}")
                    except Exception as e:
                        print(f"  ❌ שגיאה בקנייה {symbol}: {e}")
            
            # בערב (15:00): מכור
            elif 15 <= hour < 16:
                print("🌆 ערב - מכירה")
                # מכור הכל
                day_cash = load("day_cash_ils", 5000.0)
                
                trade = {
                    "⏰": datetime.now().isoformat(),
                    "📌": "ALL",
                    "↔️": "SELL",
                    "🎯": "סוף יום - לחיסול עמדות"
                }
                day_trades_log.insert(0, trade)
                print("  ✅ סיכום יום - הכנה לסגירה")
            
            save("day_cash_ils", day_cash)
            save("day_trades_log", day_trades_log)
            
            print(f"✅ סוכן יומי סיים בהצלחה")
            self.last_runs["day_agent"] = datetime.now().isoformat()
            save("scheduler_last_day_run", self.last_runs["day_agent"])
            
        except Exception as e:
            print(f"❌ שגיאה בסוכן יומי: {e}")
    
    
    # ═══════════════════════════════════════════════════════════════
    # מכונה למידה (ML) — אימון רציף
    # ═══════════════════════════════════════════════════════════════
    
    def run_ml_training(self):
        """הדריך ML מודל בחוט רקע"""
        try:
            print(f"\n🤖 [ML Training] התחיל את הריצה ב-{datetime.now().strftime('%H:%M:%S')}")
            
            try:
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.preprocessing import StandardScaler
                from sklearn.model_selection import cross_val_score
                import pickle
            except ImportError:
                print("⚠️ sklearn לא מותקן - דלג על ML")
                return
            
            # רשימת מניות לאימון
            symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "META", "AMZN", 
                      "NVDA", "AMD", "UBER", "ABNB", "NFLX", "PYPL"]
            
            all_X = []
            all_y = []
            
            print(f"📥 אסוף נתונים מ-{len(symbols)} מניות...")
            
            for i, symbol in enumerate(symbols):
                try:
                    # הורד 2 שנים של נתונים
                    hist = yf.Ticker(symbol).history(period="2y")
                    
                    if len(hist) < 220:
                        print(f"  ⚠️ {symbol}: מעט נתונים ({len(hist)} ימים)")
                        continue
                    
                    # בנה פיצ'רים
                    df = self._build_ml_features(hist)
                    
                    if len(df) < 30:
                        print(f"  ⚠️ {symbol}: מעט פיצ'רים ({len(df)} שורות)")
                        continue
                    
                    all_X.append(df.drop("target", axis=1).values)
                    all_y.append(df["target"].values)
                    
                    print(f"  ✅ {symbol}: {len(df)} שורות | P(up): {df['target'].mean():.1%}")
                
                except Exception as e:
                    print(f"  ❌ {symbol}: {e}")
            
            if not all_X or not all_y:
                print("❌ אין מספיק נתונים לאימון")
                return
            
            # שלב נתונים
            X = np.vstack(all_X)
            y = np.concatenate(all_y)
            
            print(f"📊 {len(X)} דוגמאות לאימון, {X.shape[1]} פיצ'רים")
            print(f"  | Class distribution: UP={y.mean():.1%}, DOWN={(1-y.mean()):.1%}")
            
            # אמן מודל
            print("🔄 אימון RandomForest...")
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X, y)
            
            # הערך
            print("📈 חישוב דיוק בק-5 fold CV...")
            accuracy = cross_val_score(model, X, y, cv=5, n_jobs=-1).mean()
            
            # שמור מודל
            model_bytes = pickle.dumps(model)
            feature_importance = dict(zip(
                ["rsi", "macd", "bb_width", "ret_5d", "ret_20d", "vol_ratio",
                 "above_ma50", "above_ma200", "volatility", "momentum", "candle_body", "gap"],
                model.feature_importances_
            ))
            
            save("ml_model", model_bytes)
            save("ml_accuracy", float(accuracy))
            save("ml_trained", True)
            save("ml_feature_importance", feature_importance)
            
            # עדכן מונה ריצות
            ml_runs = load("ml_runs", 0)
            save("ml_runs", ml_runs + 1)
            
            insights = {
                "timestamp": datetime.now().isoformat(),
                "accuracy": accuracy,
                "samples": len(X),
                "top_features": sorted(feature_importance.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:3],
                "data_symbols": symbols
            }
            
            ml_insights = load("ml_insights", [])
            ml_insights.insert(0, insights)
            save("ml_insights", ml_insights[-10:])  # שמור אחרון 10
            
            print(f"\n✅ ML אימון הסתיים בהצלחה!")
            print(f"  | דיוק: {accuracy:.2%}")
            print(f"  | ריצות סה"כ: {ml_runs + 1}")
            print(f"  | TOP 3 פיצ'רים:")
            for feat, imp in insights["top_features"]:
                print(f"    - {feat}: {imp:.1%}")
            
            self.last_runs["ml_training"] = datetime.now().isoformat()
            save("scheduler_last_ml_run", self.last_runs["ml_training"])
            
        except Exception as e:
            print(f"❌ שגיאה באימון ML: {e}")
            import traceback
            traceback.print_exc()
    
    
    def _build_ml_features(self, hist: pd.DataFrame) -> pd.DataFrame:
        """בנה פיצ'רים טכניים"""
        df = pd.DataFrame(index=hist.index)
        
        close = hist["Close"]
        
        # RSI
        d = close.diff()
        g = d.where(d>0, 0.0).rolling(14).mean()
        l = (-d.where(d<0, 0.0)).rolling(14).mean().replace(0, 1e-10)
        df["rsi"] = 100 - (100 / (1 + g / l))
        
        # MACD
        df["macd"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        
        # Bollinger
        ma = close.rolling(20).mean()
        std = close.rolling(20).std()
        df["bb_width"] = (std * 2) / ma
        
        # Returns
        df["ret_5d"] = close.pct_change(5)
        df["ret_20d"] = close.pct_change(20)
        
        # Volume
        df["vol_ratio"] = hist["Volume"] / hist["Volume"].rolling(20).mean()
        
        # MA crosses
        df["above_ma50"] = (close > close.rolling(50).mean()).astype(int)
        df["above_ma200"] = (close > close.rolling(200).mean()).astype(int)
        
        # Volatility
        df["volatility"] = close.pct_change().rolling(20).std()
        df["momentum"] = close / close.shift(10) - 1
        
        # Candle
        df["candle_body"] = abs(hist["Close"] - hist["Open"]) / (hist["High"] - hist["Low"] + 1e-10)
        df["gap"] = (hist["Open"] - hist["Close"].shift(1)) / hist["Close"].shift(1)
        
        # Target: up 7% בתוך 15 ימים?
        df["target"] = (close.shift(-15) / close - 1 > 0.07).astype(int)
        
        return df.dropna()
    
    
    # ═══════════════════════════════════════════════════════════════
    # בקרה על Scheduler
    # ═══════════════════════════════════════════════════════════════
    
    def run_scheduler(self):
        """לולאה ראשית של Scheduler"""
        print("🚀 Scheduler סוכנים התחיל...")
        
        last_val = 0
        last_day = 0
        last_ml = 0
        
        while self.running:
            now = time.time()
            
            # סוכן ערך: כל 6 שעות
            if now - last_val > 6 * 3600:
                self.run_val_agent()
                last_val = now
            
            # סוכן יומי: כל שעה
            if now - last_day > 3600:
                self.run_day_agent()
                last_day = now
            
            # ML: כל 12 שעות
            if now - last_ml > 12 * 3600:
                self.run_ml_training()
                last_ml = now
            
            time.sleep(60)  # בדוק כל דקה
    
    
    def start(self):
        """התחל את Scheduler בחוט נפרד"""
        if self.running:
            print("⚠️ Scheduler כבר רץ")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        print(f"✅ Scheduler החל כחוט daemon")
    
    
    def stop(self):
        """עצור את Scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⛔ Scheduler עצור")
    
    
    def get_status(self) -> dict:
        """קבל סטטוס Scheduler"""
        return {
            "running": self.running,
            "last_runs": self.last_runs,
            "thread_alive": self.thread.is_alive() if self.thread else False
        }


# ─────────────────────────────────────────────────────────────────
# יצא גלובלי לשימוש בـ app.py
# ─────────────────────────────────────────────────────────────────

_global_scheduler = None

def get_scheduler() -> BackgroundAgentScheduler:
    """קבל instance של Scheduler (Singleton)"""
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = BackgroundAgentScheduler()
    return _global_scheduler


def start_background_scheduler():
    """התחל את Scheduler בתחילת app"""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    return scheduler
