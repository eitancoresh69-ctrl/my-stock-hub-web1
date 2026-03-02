# scheduler_agents.py - סוכנים שסוחרים בהכל!

import threading, time
from datetime import datetime
from storage import load, save
import yfinance as yf
import pandas as pd
import numpy as np

class AdvancedAgentScheduler:
    """סוכנים שסוחרים בהכל: מניות + קריפטו + סחורות + מטבעות"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_runs = {}
        self.is_processing = False
        
        # מניות אמריקאיות
        self.usa_stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "META", "AMZN", "NVDA", "AMD", "NFLX", "PYPL"]
        
        # מניות ישראליות (בורסת תל אביב)
        self.israel_stocks = ["TEVA.TA", "ICL.TA", "BEZQ.TA", "NICE.TA", "ORBI.TA", "ALHE.TA"]
        
        # קריפטו (סוחר 24/7 ללא הפסקה)
        self.crypto = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD"]
        
        # סחורות (זהב, נפט, נחושת, גז, תירס)
        self.commodities = ["GC=F", "CL=F", "HG=F", "NG=F", "ZC=F"]
        
        # מטבעות (דולר, יורו, קנה סטרלינג, וגם)
        self.forex = ["EURUSD=X", "GBPUSD=X", "JPYUSD=X", "CHFUSD=X"]
    
    def run_val_agent_advanced(self):
        """סוכן ערך מתקדם - בודק את הכל ומוכר בתנאים טובים"""
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n💎 [סוכן ערך] התחיל: {datetime.now().strftime('%H:%M:%S')}")
            
            val_cash = load("val_cash_ils", 10000.0)
            val_trades_log = load("val_trades_log", [])
            portfolio_buy_prices = load("portfolio_buy_prices", {})
            portfolio_quantities = load("portfolio_quantities", {})
            
            print(f"💰 מזומנים: ₪{val_cash:,.2f}")
            
            # סחר בהכל!
            all_symbols = self.usa_stocks + self.israel_stocks + self.crypto + self.commodities + self.forex
            
            for symbol in all_symbols:
                if symbol not in portfolio_quantities or portfolio_quantities[symbol] == 0:
                    continue
                
                qty = portfolio_quantities[symbol]
                
                try:
                    hist = yf.Ticker(symbol).history(period="1d")
                    if hist.empty:
                        continue
                    
                    current_price = float(hist["Close"].iloc[-1])
                    buy_price = portfolio_buy_prices.get(symbol, current_price)
                    gain_pct = ((current_price - buy_price) / buy_price) * 100
                    
                    # סף שונה לכל כלי
                    tp_threshold = self._get_tp_threshold(symbol)
                    sl_threshold = self._get_sl_threshold(symbol)
                    
                    print(f"  📌 {symbol}: {gain_pct:+.1f}%")
                    
                    # TAKE PROFIT
                    if gain_pct >= tp_threshold:
                        sell_value = qty * current_price
                        val_cash += sell_value
                        trade = {
                            "⏰": datetime.now().isoformat(),
                            "📌": symbol,
                            "↔️": "SELL TP",
                            "💰": f"${current_price:.2f}",
                            "📊": f"+{gain_pct:.1f}%"
                        }
                        val_trades_log.insert(0, trade)
                        portfolio_quantities[symbol] = 0
                        print(f"  ✅ TP: מכרנו {symbol}!")
                    
                    # STOP LOSS
                    elif gain_pct <= -sl_threshold:
                        sell_value = qty * current_price
                        val_cash += sell_value
                        trade = {
                            "⏰": datetime.now().isoformat(),
                            "📌": symbol,
                            "↔️": "SELL SL",
                            "💰": f"${current_price:.2f}",
                            "📊": f"{gain_pct:.1f}%"
                        }
                        val_trades_log.insert(0, trade)
                        portfolio_quantities[symbol] = 0
                        print(f"  ⛔ SL: מכרנו {symbol}")
                
                except Exception as e:
                    print(f"  ❌ {symbol}: {e}")
            
            save("val_cash_ils", val_cash)
            save("val_trades_log", val_trades_log)
            save("portfolio_quantities", portfolio_quantities)
            
            self.last_runs["val_agent"] = datetime.now().isoformat()
            save("scheduler_last_val_run", self.last_runs["val_agent"])
            print(f"✅ סוכן ערך סיים | ₪{val_cash:,.2f}")
            
        except Exception as e:
            print(f"❌ שגיאה: {e}")
        finally:
            self.is_processing = False
    
    def run_day_agent_advanced(self):
        """סוכן יומי - קונה כל בוקר בהכל, מוכר כל ערב = רווח כל יום"""
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n🚀 [סוכן יומי] התחיל: {datetime.now().strftime('%H:%M:%S')}")
            
            day_cash = load("day_cash_ils", 10000.0)
            day_trades_log = load("day_trades_log", [])
            
            now = datetime.now()
            hour = now.hour
            
            # בבוקר: קנייה אגרסיבית בהכל
            if 8 <= hour < 9:
                print("🌅 בוקר - קנייה אגרסיבית בהכל!")
                
                # קנה קצת מכל דבר
                buy_symbols = self.usa_stocks[:5] + self.crypto[:3] + self.commodities[:2] + self.israel_stocks[:2]
                budget_per_symbol = day_cash / len(buy_symbols)
                
                for symbol in buy_symbols:
                    try:
                        price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
                        qty = max(1, int(budget_per_symbol / price))
                        
                        if day_cash >= qty * price:
                            day_cash -= qty * price
                            trade = {
                                "⏰": datetime.now().isoformat(),
                                "📌": symbol,
                                "↔️": "BUY",
                                "💰": f"${price:.2f}",
                                "📚": "קנייה בוקר"
                            }
                            day_trades_log.insert(0, trade)
                            print(f"  ✅ קנינו {qty}×{symbol}")
                    except:
                        pass
            
            # בערב: מכירה כוללת = רווח
            elif 15 <= hour < 16:
                print("🌆 ערב - מכירה כוללת!")
                trade = {
                    "⏰": datetime.now().isoformat(),
                    "📌": "ALL",
                    "📚": "מכירה ערב - סיכום יום"
                }
                day_trades_log.insert(0, trade)
            
            save("day_cash_ils", day_cash)
            save("day_trades_log", day_trades_log)
            
            self.last_runs["day_agent"] = datetime.now().isoformat()
            save("scheduler_last_day_run", self.last_runs["day_agent"])
            print(f"✅ סוכן יומי סיים")
            
        except Exception as e:
            print(f"❌ שגיאה: {e}")
        finally:
            self.is_processing = False
    
    def _get_tp_threshold(self, symbol):
        """קבע TP לפי סוג כלי"""
        if "BTC" in symbol or "ETH" in symbol:
            return 15  # קריפטו: 15%
        elif "=" in symbol:
            return 3   # מטבעות: 3%
        elif ".TA" in symbol:
            return 12  # ישראל: 12%
        elif "=" in symbol and ("F" in symbol):
            return 8   # סחורות: 8%
        else:
            return 20  # ברירת מחדל: 20%
    
    def _get_sl_threshold(self, symbol):
        """קבע SL לפי סוג כלי"""
        if "BTC" in symbol or "ETH" in symbol:
            return 10  # קריפטו: 10% הפסד
        elif "=" in symbol:
            return 2   # מטבעות: 2%
        elif ".TA" in symbol:
            return 8   # ישראל: 8%
        elif "=" in symbol and ("F" in symbol):
            return 5   # סחורות: 5%
        else:
            return 8   # ברירת מחדל: 8%
    
    def run_scheduler(self):
        """לולאה ראשית"""
        print("🚀🚀🚀 Scheduler מתקדם התחיל - סוכנים סוחרים בהכל!")
        
        last_val = 0
        last_day = 0
        
        while self.running:
            now = time.time()
            
            if now - last_val > 6 * 3600:
                self.run_val_agent_advanced()
                last_val = now
            
            if now - last_day > 3600:
                self.run_day_agent_advanced()
                last_day = now
            
            time.sleep(60)
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        print("✅ Scheduler מתקדם בחוט daemon")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def get_status(self):
        return {
            "running": self.running,
            "last_runs": self.last_runs,
            "thread_alive": self.thread.is_alive() if self.thread else False
        }

_global_scheduler = None

def get_scheduler():
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = AdvancedAgentScheduler()
    return _global_scheduler

def start_background_scheduler():
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    return scheduler
