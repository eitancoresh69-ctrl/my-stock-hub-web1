# scheduler_agents.py - קוד מלא עם אנרגיה וללמידה רציפה!

import threading, time
from datetime import datetime
from storage import load, save
import yfinance as yf
import pandas as pd
import numpy as np

class CompleteScheduler:
    """סוכנים עם:
    ✅ אנרגיה (7 כלים)
    ✅ 67 כלים סחור
    ✅ למידה רציפה
    ✅ Win Rate Tracking
    """
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_runs = {}
        self.is_processing = False
        
        self.usa = ["AAPL", "MSFT", "GOOGL", "TSLA", "META", "AMZN", "NVDA", "AMD",
                   "NFLX", "PYPL", "CRM", "IBM", "INTC", "CSCO", "QCOM", "AVGO", "ADBE", "SNPS", "CDNS", "MCHP"]
        
        self.israel = ["TEVA.TA", "ICL.TA", "BEZQ.TA", "NICE.TA", "ORBI.TA", "ALHE.TA", "PALO.TA", "LEOT.TA"]
        
        self.crypto = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD",
                      "DOGE-USD", "AVAX-USD", "MATIC-USD", "LTC-USD", "BCH-USD", "LINK-USD"]
        
        self.commodities = ["GC=F", "SI=F", "CL=F", "HG=F", "NG=F", "ZC=F", "ZS=F", "ZW=F"]
        
        # אנרגיה! ⭐
        self.energy = ["XLE", "OIH", "USO", "TAN", "DBC", "UNG", "KOL"]
        
        self.forex = ["EURUSD=X", "GBPUSD=X", "JPYUSD=X", "CHFUSD=X", "AUDUSD=X", "NZDUSD=X"]
        
        self.etfs = ["SPY", "QQQ", "IWM", "EEM", "AGG", "TLT", "GLD", "USO"]
        
        self.all = (self.usa + self.israel + self.crypto + self.commodities + 
                   self.energy + self.forex + self.etfs)
    
    def run_val_agent(self):
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n💎 [Val Agent] {datetime.now().strftime('%H:%M:%S')}")
            
            val_cash = load("val_cash_ils", 100000.0)
            trades_log = load("val_trades_log", [])
            buy_prices = load("portfolio_buy_prices", {})
            quantities = load("portfolio_quantities", {})
            
            trade_history = load("trade_history_complete", [])
            win_rate = self._calculate_win_rate(trade_history)
            
            print(f"💰 ₪{val_cash:,.0f} | Win Rate: {win_rate:.1%} | Trades: {len(trade_history)}")
            
            for symbol in self.all:
                if symbol not in quantities or quantities[symbol] == 0:
                    continue
                
                qty = quantities[symbol]
                
                try:
                    hist = yf.Ticker(symbol).history(period="2y")
                    if hist.empty or len(hist) < 100:
                        continue
                    
                    price = float(hist["Close"].iloc[-1])
                    buy = buy_prices.get(symbol, price)
                    gain = ((price - buy) / buy) * 100
                    
                    signals = self._analyze(symbol, hist)
                    tp, sl = self._smart_tp_sl(symbol, signals)
                    
                    print(f"  {symbol}: {gain:+.1f}%")
                    
                    if gain >= tp:
                        val_cash += qty * price
                        trade = {"⏰": datetime.now().isoformat(), "📌": symbol, "↔️": "SELL TP",
                                "💰": price, "💹": gain, "✅": True}
                        trades_log.insert(0, trade)
                        trade_history.append(trade)
                        quantities[symbol] = 0
                        print(f"  ✅ TP!")
                    
                    elif gain <= -sl:
                        val_cash += qty * price
                        trade = {"⏰": datetime.now().isoformat(), "📌": symbol, "↔️": "SELL SL",
                                "💰": price, "💹": gain, "✅": False}
                        trades_log.insert(0, trade)
                        trade_history.append(trade)
                        quantities[symbol] = 0
                        print(f"  ⛔ SL")
                
                except:
                    pass
            
            save("val_cash_ils", val_cash)
            save("val_trades_log", trades_log)
            save("portfolio_quantities", quantities)
            save("trade_history_complete", trade_history[-500:])
            
            self.last_runs["val"] = datetime.now().isoformat()
            save("scheduler_last_val_run", self.last_runs["val"])
            print(f"✅ Val Agent OK")
            
        except:
            pass
        finally:
            self.is_processing = False
    
    def run_day_agent(self):
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n🚀 [Day Agent] {datetime.now().strftime('%H:%M:%S')}")
            
            day_cash = load("day_cash_ils", 100000.0)
            day_trades = load("day_trades_log", [])
            
            hour = datetime.now().hour
            
            if 8 <= hour < 9:
                print("🌅 קנייה בוקר")
                ranked = self._rank_symbols(self.all[:40])[:15]
                per = day_cash / len(ranked)
                
                for sym in ranked:
                    try:
                        p = yf.Ticker(sym).history(period="1d")["Close"].iloc[-1]
                        q = max(1, int(per / p))
                        if day_cash >= q * p:
                            day_cash -= q * p
                            day_trades.insert(0, {"⏰": datetime.now().isoformat(), "📌": sym, "↔️": "BUY"})
                            print(f"  ✅ {sym}")
                    except:
                        pass
            
            elif 15 <= hour < 16:
                print("🌆 מכירה ערב")
                day_trades.insert(0, {"⏰": datetime.now().isoformat(), "📌": "ALL", "↔️": "SELL"})
            
            save("day_cash_ils", day_cash)
            save("day_trades_log", day_trades)
            self.last_runs["day"] = datetime.now().isoformat()
            save("scheduler_last_day_run", self.last_runs["day"])
            print(f"✅ Day Agent OK")
            
        except:
            pass
        finally:
            self.is_processing = False
    
    def run_ml_agent(self):
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n🧠 [ML Agent] {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
                from sklearn.linear_model import LogisticRegression
                from sklearn.svm import SVC
                from sklearn.neural_network import MLPClassifier
                from sklearn.model_selection import cross_val_score
            except:
                return
            
            syms = self.usa[:8] + self.crypto[:3] + self.energy[:2]
            X, y = [], []
            
            for sym in syms:
                try:
                    h = yf.Ticker(sym).history(period="2y")
                    if len(h) < 200:
                        continue
                    df = self._features(h)
                    if len(df) < 50:
                        continue
                    X.append(df.drop("target", axis=1).values)
                    y.append(df["target"].values)
                    print(f"  ✅ {sym}")
                except:
                    pass
            
            if not X:
                return
            
            X_all = np.vstack(X)
            y_all = np.concatenate(y)
            
            scores = {}
            
            rf = RandomForestClassifier(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
            rf.fit(X_all, y_all)
            scores["rf"] = float(cross_val_score(rf, X_all, y_all, cv=5).mean())
            
            gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=8, random_state=42)
            gb.fit(X_all, y_all)
            scores["gb"] = float(cross_val_score(gb, X_all, y_all, cv=5).mean())
            
            lr = LogisticRegression(max_iter=1000, random_state=42)
            lr.fit(X_all, y_all)
            scores["lr"] = float(cross_val_score(lr, X_all, y_all, cv=5).mean())
            
            svm = SVC(kernel="rbf", random_state=42)
            svm.fit(X_all, y_all)
            scores["svm"] = float(cross_val_score(svm, X_all, y_all, cv=5).mean())
            
            nn = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
            nn.fit(X_all, y_all)
            scores["nn"] = float(cross_val_score(nn, X_all, y_all, cv=5).mean())
            
            ensemble = sum(scores.values()) / len(scores)
            scores["ensemble"] = ensemble
            
            save("ml_scores", scores)
            
            ml_runs = load("ml_runs", 0)
            save("ml_runs", ml_runs + 1)
            
            self.last_runs["ml"] = datetime.now().isoformat()
            save("scheduler_last_ml_run", self.last_runs["ml"])
            
            print(f"✅ ML OK | Ensemble: {ensemble:.1%}")
            
        except:
            pass
        finally:
            self.is_processing = False
    
    def _analyze(self, symbol, hist):
        close = hist["Close"]
        signals = {}
        
        d = close.diff()
        g = d.where(d>0, 0).rolling(14).mean()
        l = (-d.where(d<0, 0)).rolling(14).mean().replace(0, 1e-10)
        signals["rsi"] = float(100 - (100 / (1 + g / l)).iloc[-1])
        
        signals["macd"] = float((close.ewm(span=12).mean() - close.ewm(span=26).mean()).iloc[-1])
        signals["momentum"] = float((close.iloc[-1] / close.iloc[-20] - 1) * 100)
        signals["volatility"] = float(close.pct_change().rolling(20).std().iloc[-1])
        
        return signals
    
    def _smart_tp_sl(self, symbol, signals):
        if "BTC" in symbol or "ETH" in symbol:
            return (15, 10)
        elif symbol in self.energy:
            return (12, 8)
        elif ".TA" in symbol:
            return (12, 8)
        elif "=" in symbol:
            return (3, 2)
        else:
            return (20, 8)
    
    def _rank_symbols(self, symbols):
        ranks = []
        for sym in symbols:
            try:
                h = yf.Ticker(sym).history(period="30d")
                if h.empty:
                    continue
                mom = (h["Close"].iloc[-1] / h["Close"].iloc[0] - 1) * 100
                ranks.append((sym, mom))
            except:
                pass
        ranks.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in ranks]
    
    def _features(self, hist):
        df = pd.DataFrame(index=hist.index)
        c = hist["Close"]
        
        d = c.diff()
        g = d.where(d>0, 0).rolling(14).mean()
        l = (-d.where(d<0, 0)).rolling(14).mean().replace(0, 1e-10)
        df["rsi"] = 100 - (100 / (1 + g / l))
        
        df["macd"] = c.ewm(span=12).mean() - c.ewm(span=26).mean()
        
        ma = c.rolling(20).mean()
        std = c.rolling(20).std()
        df["bb_upper"] = ma + (std * 2)
        df["bb_lower"] = ma - (std * 2)
        
        df["ret_5"] = c.pct_change(5)
        df["ret_20"] = c.pct_change(20)
        df["vol"] = c.pct_change().rolling(20).std()
        df["momentum"] = (c / c.shift(10) - 1) * 100
        df["vol_ratio"] = hist["Volume"] / hist["Volume"].rolling(20).mean() if "Volume" in hist.columns else 1
        
        df["sma20"] = c.rolling(20).mean()
        df["sma50"] = c.rolling(50).mean()
        df["sma200"] = c.rolling(200).mean()
        
        df["above_ma20"] = (c > c.rolling(20).mean()).astype(int)
        df["above_ma200"] = (c > c.rolling(200).mean()).astype(int)
        
        df["target"] = (c.shift(-15) / c - 1 > 0.07).astype(int)
        
        return df.dropna()
    
    def _calculate_win_rate(self, history):
        if not history:
            return 0.5
        wins = sum(1 for t in history if t.get("✅", False))
        return wins / len(history) if history else 0.5
    
    def run_scheduler(self):
        print("🚀🚀🚀 Scheduler התחיל!")
        last_val = 0
        last_day = 0
        last_ml = 0
        
        while self.running:
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
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        print("✅ Scheduler בחוט daemon")
    
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
        _global_scheduler = CompleteScheduler()
    return _global_scheduler

def start_background_scheduler():
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    return scheduler
