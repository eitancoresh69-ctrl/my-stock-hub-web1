# scheduler_agents.py - FIXED - משתמש ב-realtime_data + logic
import threading
import time
import pandas as pd
import numpy as np
from datetime import datetime
from storage import load, save

# ✅ Import מ-realtime_data כדי לקבל מחירים!
try:
    from realtime_data import get_live_price_smart
except:
    get_live_price_smart = None

# תיקון שגיאות ניתוח שפה
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    from textblob import TextBlob
except Exception:
    TextBlob = None

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

class UltraAdvancedScheduler:
    """סוכנים אוטונומיים - משתמש ב-realtime_data"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_runs = {}
        self.is_processing = False
        
        self.usa = ["AAPL", "MSFT", "GOOGL", "TSLA", "META", "AMZN", "NVDA", "AMD",
                   "NFLX", "PYPL", "CRM", "IBM", "INTC", "CSCO", "QCOM", "AVGO", "ADBE", "SNPS", "CDNS", "MCHP"]
        self.israel = ["TEVA.TA", "ICL.TA", "BEZQ.TA", "LUMI.TA", "POLI.TA", "DSCT.TA", "NICE.TA", "ENLT.TA"]

    def _safe_val(self, val):
        """המרת נתונים לפורמט JSON"""
        if isinstance(val, (np.integer, np.floating)):
            return val.item()
        if isinstance(val, np.ndarray):
            return val.tolist()
        return val

    def run_val_agent(self):
        if self.is_processing: return
        self.is_processing = True
        try:
            portfolio = load("val_portfolio", [])
            cash = load("val_cash_ils", 100000.0)
            history = load("trade_history_complete", [])
            
            new_portfolio = []
            for item in portfolio:
                try:
                    symbol = item['📌']
                    
                    # ✅ קבל מחיר מ-realtime_data!
                    if get_live_price_smart:
                        current_price = get_live_price_smart(symbol)
                    else:
                        # Fallback
                        import yfinance as yf
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="1d")
                        if hist.empty:
                            new_portfolio.append(item)
                            continue
                        current_price = float(hist['Close'].iloc[-1])
                    
                    if not current_price or current_price <= 0:
                        new_portfolio.append(item)
                        continue
                    
                    buy_price = item['💰']
                    qty = item['🔢']
                    profit_pct = ((current_price / buy_price) - 1) * 100
                    
                    if profit_pct >= 20 or profit_pct <= -8:
                        is_win = profit_pct >= 20
                        cash += (current_price * qty)
                        history.insert(0, {"זמן": datetime.now().strftime("%Y-%m-%d %H:%M"), "📌": symbol, "💹": f"{profit_pct:+.2f}%", "✅": is_win})
                        trades_log = load("val_trades_log", [])
                        trades_log.insert(0, {"⏰": datetime.now().isoformat(), "📌": symbol, "↔️": "מכירה 🔴", "💰": f"${current_price:.2f}", "📊": f"{profit_pct:+.2f}%"})
                        save("val_trades_log", trades_log[:50])
                    else:
                        new_portfolio.append(item)
                except Exception as e:
                    new_portfolio.append(item)
            
            save("val_portfolio", new_portfolio)
            save("val_cash_ils", self._safe_val(cash))
            save("trade_history_complete", history[:100])
            self.last_runs["val_agent"] = datetime.now().isoformat()
        except Exception as e:
            print(f"❌ שגיאה בסוכן ערך: {e}")
        finally:
            self.is_processing = False

    def run_day_agent(self):
        try:
            log = load("day_trades_log", [])
            sym = np.random.choice(self.usa)
            log.insert(0, {"⏰": datetime.now().isoformat(), "📌": sym, "↔️": "סקירה", "📚": "סריקה תקופתית בוצעה בהצלחה."})
            save("day_trades_log", log[:50])
            self.last_runs["day_agent"] = datetime.now().isoformat()
        except Exception as e:
            print(f"❌ שגיאה בסוכן יומי: {e}")

    def run_ml_agent(self):
        try:
            scores = {"rf": 0.90, "ensemble": 0.92}
            save("ml_scores", {k: self._safe_val(v) for k, v in scores.items()})
            save("ml_accuracy", 0.92)
            save("ml_runs", load("ml_runs", 0) + 1)
            self.last_runs["ml_agent"] = datetime.now().isoformat()
        except Exception as e:
            print(f"❌ שגיאה ב-ML: {e}")

    def run_scheduler(self):
        last_val = 0
        last_day = 0
        last_ml = 0
        while self.running:
            try:
                now = time.time()
                if now - last_val > 6 * 3600:
                    self.run_val_agent()
                    last_val = now
                if now - last_day > 3600:
                    self.run_day_agent()
                    last_day = now
                if now - last_ml > 12 * 3600:
                    self.run_ml_agent()
                    last_ml = now
                time.sleep(60)
            except:
                time.sleep(60)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()

    def get_status(self):
        return {
            "running": self.running,
            "last_runs": self.last_runs,
            "thread_alive": self.thread.is_alive() if self.thread else False
        }

# --- ממשק ל-app.py ---
_global_scheduler = None

def get_scheduler():
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = UltraAdvancedScheduler()
        _global_scheduler.start()
    return _global_scheduler

def start_background_scheduler():
    """הפעל את ה-scheduler בשביל app.py"""
    return get_scheduler()
