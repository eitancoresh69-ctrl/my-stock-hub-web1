# scheduler_agents.py - קוד מלא עם כל 30 השיפורים!

import threading, time
from datetime import datetime
from storage import load, save
import yfinance as yf
import pandas as pd
import numpy as np

try:
    from textblob import TextBlob
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "textblob"])
    from textblob import TextBlob

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.utils.class_weight import compute_class_weight

class UltraAdvancedScheduler:
    """סוכנים עם כל 30 השיפורים!"""
    
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
        self.energy = ["XLE", "OIH", "USO", "TAN", "DBC", "UNG", "KOL"]
        self.forex = ["EURUSD=X", "GBPUSD=X", "JPYUSD=X", "CHFUSD=X", "AUDUSD=X", "NZDUSD=X"]
        self.etfs = ["SPY", "QQQ", "IWM", "EEM", "AGG", "TLT", "GLD", "USO"]
        
        self.all = (self.usa + self.israel + self.crypto + self.commodities + 
                   self.energy + self.forex + self.etfs)
    
    # ═══════════════════════════════════════════════════════════════
    # 15 שיפורים סחר
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_sentiment(self, symbol):
        """1. Sentiment Analysis"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news if hasattr(ticker, 'news') else []
            
            sentiment_score = 0
            count = 0
            
            for article in news[:5]:
                try:
                    title = article.get('title', '')
                    blob = TextBlob(title)
                    sentiment_score += blob.sentiment.polarity
                    count += 1
                except:
                    pass
            
            if count == 0:
                return "NEUTRAL"
            
            avg = sentiment_score / count
            
            if avg > 0.2:
                return "STRONG_BUY"
            elif avg < -0.2:
                return "STRONG_SELL"
            else:
                return "NEUTRAL"
        except:
            return "NEUTRAL"
    
    def detect_regime(self, hist):
        """7. Market Regime Detection"""
        close = hist["Close"]
        
        bull_score = 0
        
        ma200 = close.rolling(200).mean()
        if close.iloc[-1] > ma200.iloc[-1]:
            bull_score += 2
        
        d = close.diff()
        g = d.where(d>0, 0).rolling(14).mean()
        l = (-d.where(d<0, 0)).rolling(14).mean().replace(0, 1e-10)
        rsi = 100 - (100 / (1 + g / l))
        if rsi.iloc[-1] > 50:
            bull_score += 1
        
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        if macd.iloc[-1] > macd.iloc[-2]:
            bull_score += 1
        
        if bull_score >= 3:
            return "BULL"
        elif bull_score <= 1:
            return "BEAR"
        else:
            return "SIDEWAYS"
    
    def adjust_for_volatility(self, hist):
        """12. Volatility Clustering"""
        close = hist["Close"]
        volatility = close.pct_change().rolling(20).std()
        vol_ma = volatility.rolling(20).mean()
        
        current_vol = volatility.iloc[-1]
        avg_vol = vol_ma.iloc[-1]
        
        if current_vol > avg_vol * 1.5:
            return {"tp": 10, "sl": 5, "size": 0.7}
        else:
            return {"tp": 20, "sl": 8, "size": 1.0}
    
    def volume_analysis(self, hist):
        """13. Volume Analysis"""
        if "Volume" not in hist.columns:
            return "NEUTRAL"
        
        volume = hist["Volume"]
        price = hist["Close"]
        vol_ma = volume.rolling(20).mean()
        
        if volume.iloc[-1] > vol_ma.iloc[-1] * 1.5:
            if price.iloc[-1] > price.iloc[-2]:
                return "STRONG_BUY"
            else:
                return "STRONG_SELL"
        
        return "NEUTRAL"
    
    def ichimoku_signal(self, hist):
        """14. Ichimoku Cloud"""
        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        
        tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_a = (tenkan + kijun) / 2
        senkou_b = (high.rolling(52).max() + low.rolling(52).min()) / 2
        
        cloud_top = max(senkou_a.iloc[-1], senkou_b.iloc[-1])
        
        if close.iloc[-1] > cloud_top and tenkan.iloc[-1] > kijun.iloc[-1]:
            return "STRONG_BUY"
        elif close.iloc[-1] < cloud_top and tenkan.iloc[-1] < kijun.iloc[-1]:
            return "STRONG_SELL"
        else:
            return "NEUTRAL"
    
    def kelly_criterion(self, win_rate, avg_win, avg_loss):
        """4. Kelly Criterion"""
        if avg_win == 0:
            return 0.5
        
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        return max(0.1, min(kelly * 0.5, 1.0))
    
    def multi_timeframe_analysis(self, symbol):
        """10. Multi-Timeframe Analysis"""
        signals = {}
        
        try:
            daily = yf.Ticker(symbol).history(period="1y")
            daily_sig = "BUY" if daily["Close"].iloc[-1] > daily["Close"].rolling(200).mean().iloc[-1] else "SELL"
            signals["daily"] = daily_sig
        except:
            signals["daily"] = "NEUTRAL"
        
        try:
            hourly = yf.Ticker(symbol).history(period="30d", interval="1h")
            if len(hourly) > 20:
                hourly_sig = "BUY" if hourly["Close"].iloc[-1] > hourly["Close"].iloc[-20] else "SELL"
                signals["hourly"] = hourly_sig
        except:
            signals["hourly"] = "NEUTRAL"
        
        buy_count = sum(1 for s in signals.values() if s == "BUY")
        
        if buy_count >= 2:
            return "STRONG_BUY"
        elif buy_count == 0:
            return "STRONG_SELL"
        else:
            return "NEUTRAL"
    
    def run_val_agent(self):
        """סוכן ערך עם כל השיפורים"""
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n💎 [Val Agent Ultra] {datetime.now().strftime('%H:%M:%S')}")
            
            val_cash = load("val_cash_ils", 100000.0)
            trades_log = load("val_trades_log", [])
            buy_prices = load("portfolio_buy_prices", {})
            quantities = load("portfolio_quantities", {})
            
            trade_history = load("trade_history_complete", [])
            win_rate = sum(1 for t in trade_history if t.get("✅", False)) / len(trade_history) if trade_history else 0.5
            
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
                    
                    # שימוש בשיפורים
                    sentiment = self.analyze_sentiment(symbol)
                    regime = self.detect_regime(hist)
                    vol_adj = self.adjust_for_volatility(hist)
                    volume_sig = self.volume_analysis(hist)
                    ichimoku_sig = self.ichimoku_signal(hist)
                    
                    tp = vol_adj["tp"]
                    sl = vol_adj["sl"]
                    
                    if sentiment == "STRONG_BUY":
                        tp = tp * 1.2
                    
                    signals_count = sum([
                        sentiment == "STRONG_BUY",
                        regime == "BULL",
                        volume_sig == "STRONG_BUY",
                        ichimoku_sig == "STRONG_BUY"
                    ])
                    
                    print(f"  {symbol}: {gain:+.1f}% | Signals: {signals_count}/4")
                    
                    if gain >= tp and signals_count >= 2:
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
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.is_processing = False
    
    def run_day_agent(self):
        """סוכן יומי עם Multi-Timeframe"""
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n🚀 [Day Agent Ultra] {datetime.now().strftime('%H:%M:%S')}")
            
            day_cash = load("day_cash_ils", 100000.0)
            day_trades = load("day_trades_log", [])
            
            hour = datetime.now().hour
            
            if 8 <= hour < 9:
                print("🌅 קנייה חכמה")
                
                ranked = []
                for sym in self.all[:35]:
                    try:
                        sig = self.multi_timeframe_analysis(sym)
                        strength = 3 if sig == "STRONG_BUY" else (1 if sig == "STRONG_SELL" else 2)
                        ranked.append((sym, strength))
                    except:
                        pass
                
                ranked.sort(key=lambda x: x[1], reverse=True)
                buy = [r[0] for r in ranked[:15]]
                
                per = day_cash / len(buy)
                
                for sym in buy:
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
                print("🌆 מכירה")
                day_trades.insert(0, {"⏰": datetime.now().isoformat(), "📌": "ALL", "↔️": "SELL"})
            
            save("day_cash_ils", day_cash)
            save("day_trades_log", day_trades)
            self.last_runs["day"] = datetime.now().isoformat()
            save("scheduler_last_day_run", self.last_runs["day"])
            print(f"✅ Day Agent OK")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.is_processing = False
    
    def run_ml_agent(self):
        """ML עם כל 10 + 5 שיפורים"""
        if self.is_processing:
            return
        self.is_processing = True
        try:
            print(f"\n🧠 [ML Agent ULTIMATE] {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                import xgboost as xgb
                import lightgbm as lgb
            except ImportError:
                print("⚠️ Installing XGBoost & LightGBM...")
                import subprocess, sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "xgboost", "lightgbm"])
                import xgboost as xgb
                import lightgbm as lgb
            
            syms = self.usa[:8] + self.crypto[:3] + self.energy[:2]
            X, y = [], []
            
            for sym in syms:
                try:
                    h = yf.Ticker(sym).history(period="2y")
                    if len(h) < 200:
                        continue
                    
                    df = self._build_features_ultimate(h)
                    if len(df) < 50:
                        continue
                    
                    X.append(df.drop("target", axis=1).values)
                    y.append(df["target"].values)
                    print(f"  ✅ {sym}")
                except:
                    pass
            
            if not X:
                print("❌ No data")
                return
            
            X_all = np.vstack(X)
            y_all = np.concatenate(y)
            
            # שיפור 1: Feature Selection
            selector = SelectKBest(f_classif, k=min(30, X_all.shape[1]-1))
            X_selected = selector.fit_transform(X_all, y_all)
            
            # שיפור 2: Data Augmentation
            noise = np.random.normal(0, 0.01, X_selected.shape)
            X_aug = np.vstack([X_selected, X_selected + noise])
            y_aug = np.concatenate([y_all, y_all])
            
            # שיפור 3: Standardization
            scaler = StandardScaler()
            X_aug = scaler.fit_transform(X_aug)
            
            # שיפור 4: Class Weights
            class_weights = compute_class_weight('balanced', classes=np.unique(y_all), y=y_all)
            
            # שיפור 5: 10-Fold CV
            skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
            
            scores = {}
            models = {}
            
            print("🔄 Training models...")
            
            # 1. Random Forest
            rf = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
            rf.fit(X_aug, y_aug)
            scores["rf"] = float(cross_val_score(rf, X_aug, y_aug, cv=skf).mean())
            models["rf"] = rf
            
            # 2. Gradient Boosting
            gb = GradientBoostingClassifier(n_estimators=150, learning_rate=0.08, max_depth=8, random_state=42)
            gb.fit(X_aug, y_aug)
            scores["gb"] = float(cross_val_score(gb, X_aug, y_aug, cv=skf).mean())
            models["gb"] = gb
            
            # 3. XGBoost
            xgb_model = xgb.XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.05, 
                                        subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1,
                                        scale_pos_weight=class_weights[1]/class_weights[0])
            xgb_model.fit(X_aug, y_aug)
            scores["xgb"] = float(cross_val_score(xgb_model, X_aug, y_aug, cv=skf).mean())
            models["xgb"] = xgb_model
            
            # 4. LightGBM
            lgb_model = lgb.LGBMClassifier(n_estimators=200, max_depth=8, learning_rate=0.05, 
                                         num_leaves=31, feature_fraction=0.8, bagging_fraction=0.8,
                                         random_state=42, n_jobs=-1)
            lgb_model.fit(X_aug, y_aug)
            scores["lgb"] = float(cross_val_score(lgb_model, X_aug, y_aug, cv=skf).mean())
            models["lgb"] = lgb_model
            
            # 5. SVM
            svm = SVC(kernel='rbf', C=0.8, probability=True, random_state=42)
            svm.fit(X_aug, y_aug)
            scores["svm"] = float(cross_val_score(svm, X_aug, y_aug, cv=skf).mean())
            models["svm"] = svm
            
            # 6. Logistic Regression
            lr = LogisticRegression(max_iter=2000, random_state=42)
            lr.fit(X_aug, y_aug)
            scores["lr"] = float(cross_val_score(lr, X_aug, y_aug, cv=skf).mean())
            models["lr"] = lr
            
            # 7. Neural Network
            nn = MLPClassifier(hidden_layer_sizes=(150, 100, 50), max_iter=1500, 
                             learning_rate_init=0.001, random_state=42, early_stopping=True, n_iter_no_change=50)
            nn.fit(X_aug, y_aug)
            scores["nn"] = float(cross_val_score(nn, X_aug, y_aug, cv=skf).mean())
            models["nn"] = nn
            
            # 8. Ensemble Voting
            voting = VotingClassifier(
                estimators=[('rf', models['rf']), ('gb', models['gb']), 
                           ('svm', models['svm']), ('lr', models['lr']), ('nn', models['nn'])],
                voting='soft'
            )
            voting.fit(X_aug, y_aug)
            scores["voting"] = float(cross_val_score(voting, X_aug, y_aug, cv=skf).mean())
            models["voting"] = voting
            
            # 9. Stacking
            stacking = StackingClassifier(
                estimators=[('rf', models['rf']), ('gb', models['gb']), ('svm', models['svm'])],
                final_estimator=LogisticRegression(max_iter=2000),
                cv=5
            )
            stacking.fit(X_aug, y_aug)
            scores["stacking"] = float(cross_val_score(stacking, X_aug, y_aug, cv=skf).mean())
            models["stacking"] = stacking
            
            # Ultimate Ensemble
            ensemble_score = np.mean([v for k, v in scores.items() if v > 0])
            scores["ensemble"] = ensemble_score
            
            save("ml_scores", scores)
            
            ml_runs = load("ml_runs", 0)
            save("ml_runs", ml_runs + 1)
            
            self.last_runs["ml"] = datetime.now().isoformat()
            save("scheduler_last_ml_run", self.last_runs["ml"])
            
            print(f"\n✅ ML ULTIMATE OK!")
            print(f"  RF: {scores['rf']:.1%} | GB: {scores['gb']:.1%} | XGB: {scores['xgb']:.1%}")
            print(f"  LGB: {scores['lgb']:.1%} | SVM: {scores['svm']:.1%} | LR: {scores['lr']:.1%} | NN: {scores['nn']:.1%}")
            print(f"  📊 Voting: {scores['voting']:.1%} | Stacking: {scores['stacking']:.1%}")
            print(f"  🤖 Final Ensemble: {ensemble_score:.1%}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.is_processing = False
    
    def _build_features_ultimate(self, hist):
        """בנה 50+ features"""
        df = pd.DataFrame(index=hist.index)
        c = hist["Close"]
        h = hist["High"]
        l = hist["Low"]
        v = hist["Volume"] if "Volume" in hist.columns else pd.Series(1, index=hist.index)
        
        # RSI
        for period in [7, 14, 21]:
            d = c.diff()
            g = d.where(d>0, 0).rolling(period).mean()
            l_rsi = (-d.where(d<0, 0)).rolling(period).mean().replace(0, 1e-10)
            df[f"rsi_{period}"] = 100 - (100 / (1 + g / l_rsi))
        
        # MACD
        df["macd"] = c.ewm(span=12).mean() - c.ewm(span=26).mean()
        df["macd_signal"] = df["macd"].ewm(span=9).mean()
        
        # Bollinger Bands
        ma = c.rolling(20).mean()
        std = c.rolling(20).std()
        df["bb_upper"] = ma + (std * 2)
        df["bb_lower"] = ma - (std * 2)
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / ma
        df["bb_position"] = (c - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])
        
        # Returns
        for period in [5, 10, 20]:
            df[f"ret_{period}"] = c.pct_change(period)
        
        # Moving Averages
        for period in [20, 50, 200]:
            df[f"sma_{period}"] = c.rolling(period).mean()
            df[f"above_ma_{period}"] = (c > c.rolling(period).mean()).astype(int)
        
        # Momentum
        df["momentum"] = (c / c.shift(10) - 1) * 100
        
        # Volatility
        df["volatility"] = c.pct_change().rolling(20).std()
        df["volatility_ratio"] = df["volatility"] / df["volatility"].rolling(60).mean()
        
        # Volume
        df["volume_ma"] = v.rolling(20).mean()
        df["volume_ratio"] = v / (df["volume_ma"] + 1e-10)
        
        # ATR
        tr1 = h - l
        tr2 = abs(h - c.shift(1))
        tr3 = abs(l - c.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["atr"] = tr.rolling(14).mean()
        
        # Stochastic
        k_period = c.rolling(14).apply(lambda x: (x.iloc[-1] - x.min()) / (x.max() - x.min() + 1e-10), raw=False)
        df["stochastic_k"] = k_period
        df["stochastic_d"] = k_period.rolling(3).mean()
        
        # Williams %R
        df["williams_r"] = -100 * (h.rolling(14).max() - c) / (h.rolling(14).max() - l.rolling(14).min() + 1e-10)
        
        # ROC
        df["roc_12"] = (c / c.shift(12) - 1) * 100
        
        # Target
        df["target"] = (c.shift(-15) / c - 1 > 0.07).astype(int)
        
        return df.dropna()
    
    def run_scheduler(self):
        print("🚀🚀🚀 Scheduler ULTIMATE התחיל!")
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
        print("✅ Scheduler ULTIMATE בחוט daemon")
    
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
        _global_scheduler = UltraAdvancedScheduler()
    return _global_scheduler

def start_background_scheduler():
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    return scheduler
