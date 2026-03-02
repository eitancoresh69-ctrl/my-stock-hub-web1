# AI Trading System - Integrated Version

## 📊 New Features Added (2026 Update)

### ✨ Multi-User Support with Global Learning
- User authentication and private portfolios
- Encrypted passwords (SHA256)
- Each user's trades remain private
- Global ML learns from all users combined
- Session management with API keys per user

### 🎙️ Podcast Tracking System
- Israeli podcasts (גלזברוק, היום בהנדלה וגם)
- Global podcasts (Pomp Podcast, WSJ Journal וגם)
- Sentiment analysis on podcast content
- Trending topics detection
- Symbol extraction from transcripts

### 🔔 Advanced Alert System  
- Telegram integration
- Email alerts
- Push notifications
- Smart alert rules (ML prediction, Breakout, Sentiment, Portfolio)
- Alert throttling (no spam)

### 🤖 Enhanced ML System
- XGBoost and LightGBM integration
- Feature selection (SelectKBest)
- Data augmentation for better training
- 10-fold cross-validation
- Ensemble methods (Voting + Stacking)
- Global learning from all community trades

### 💎 Premium System
- 3 tier subscription (Basic, Premium, Pro)
- Feature availability per plan
- Unlimited symbols, alerts, and more

### 👥 Community Dashboard
- Global statistics
- Community insights
- Top traded symbols
- Win rate tracking

## 📁 New Files Added

- `user_manager.py` - User authentication and management
- `global_ml_system.py` - Global machine learning
- `podcast_tracker.py` - Podcast analysis
- `alert_system.py` - Advanced alerts

## 🔄 Modified Files

- `app.py` - Added multi-user support and new dashboards
- `storage.py` - Enhanced with user data and global ML
- `scheduler_agents.py` - Upgraded agents with improvements

## 🚀 Getting Started

1. Install requirements: `pip install -r requirements.txt`
2. Run: `streamlit run app.py`
3. Register a new account
4. Click "RUN ALL AGENTS" to start trading

## 💾 Data Structure

All data persisted in `trading_data.json`:
- User accounts (encrypted passwords)
- Trade history
- Portfolio data
- Global learning data
- Settings

## 🔐 Security

✅ Passwords hashed with SHA256
✅ Each user's data isolated
✅ Global learning anonymized
✅ API keys per user
✅ Session management

## 📊 Supported Instruments (67 Total)

- 20 USA Stocks
- 8 Israeli Stocks
- 12 Cryptocurrencies (24/7)
- 8 Commodities
- 7 Energy
- 6 Forex
- 8 ETFs

## 🎯 Features Summary

| Feature | Status |
|---------|--------|
| Multi-user login | ✅ |
| Private portfolios | ✅ |
| Global ML learning | ✅ |
| News sentiment | ✅ |
| Podcast tracking | ✅ |
| Advanced alerts | ✅ |
| API keys | ✅ |
| Premium system | ✅ |
| 3 autonomous agents | ✅ |
| 67 symbols | ✅ |
| 7 dashboards | ✅ |

## 📞 Support

For issues or questions, check the DEPLOY_GUIDE.md

---

**Version:** 2026 Elite
**Last Updated:** 2026
**Author:** AI Trading Team
