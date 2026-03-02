#!/usr/bin/env python3
# storage.py - Complete with Multi-User Support and ML/Premium Persistence
import json
import os
import streamlit as st

def get_storage_file():
    """מחזיר את שם הקובץ הייעודי למשתמש המחובר כרגע"""
    if "username" in st.session_state:
        return f"trading_data_{st.session_state['username']}.json"
    return "trading_data_default.json"

# ═══════════════════════════════════════════════════════════════
# CORE STORAGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load(key, default=None):
    """Load data from storage"""
    try:
        current_file = get_storage_file()
        if not os.path.exists(current_file):
            return default
        
        with open(current_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get(key, default)
    except:
        return default

def save(key, value):
    """Save data to storage"""
    try:
        current_file = get_storage_file()
        if os.path.exists(current_file):
            with open(current_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        data[key] = value
        
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Storage error: {e}")
        return False

def delete(key):
    """Delete data from storage"""
    try:
        current_file = get_storage_file()
        if os.path.exists(current_file):
            with open(current_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if key in data:
                del data[key]
                with open(current_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
        return False
    except:
        return False

# ═══════════════════════════════════════════════════════════════
# SPECIFIC WRAPPERS (Required by other modules)
# ═══════════════════════════════════════════════════════════════

def load_all_to_session(session):
    """Loads specific keys to session state on startup"""
    # כאן הוספנו את כל מפתחות ה-ML וסוכני הפרימיום כדי שלא יתאפסו בריענון או סגירת דפדפן
    keys_to_load = [
        "portfolio_buy_prices", "portfolio_quantities", 
        "val_cash_ils", "day_cash_ils", "trade_history_complete", 
        "val_trades_log", "day_trades_log",
        
        # זיכרון ML
        "ml_scores", "ml_runs", "ml_accuracy", "ml_trained", 
        "ml_params", "ml_insights", "ml_model_type", "ml_cv_scores", 
        "ml_model_b64", "ml_scaler_b64", "ml_feat_imp", "ml_train_n",
        
        # זיכרון פרימיום והגדרות אחרות
        "premium_scans_history", "premium_active_agents",
        "agent_universe_df", "agent_universe_short_df",
        "telegram_alert_settings"
    ]
    for k in keys_to_load:
        if k not in session:
            val = load(k)
            if val is not None:
                session[k] = val

def load_ai_portfolio(session):
    """Loads AI Portfolio data to session"""
    keys = ["aip_capital", "aip_cash", "aip_positions", "aip_trades", "aip_decisions", "aip_performance", "aip_settings", "aip_enabled"]
    for k in keys:
        if k not in session:
            val = load(k)
            if val is not None:
                session[k] = val

def save_simulator(session, agent_type="day"):
    """Saves simulator portfolio data"""
    save(f"{agent_type}_portfolio", session.get(f"{agent_type}_portfolio", []))
    save(f"{agent_type}_cash_ils", session.get(f"{agent_type}_cash_ils", 100000.0))

def reset_simulator(session, agent_type="day"):
    """Resets simulator data"""
    session[f"{agent_type}_portfolio"] = []
    session[f"{agent_type}_cash_ils"] = 100000.0
    save_simulator(session, agent_type)

def save_ml(session):
    """Saves Machine Learning models and parameters"""
    keys = ["ml_trained", "ml_accuracy", "ml_runs", "ml_params", "ml_insights", "ml_model_type", "ml_cv_scores", "ml_model_b64", "ml_scaler_b64", "ml_feat_imp", "ml_train_n"]
    for k in keys:
        if k in session:
            save(k, session[k])

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def clear_all():
    """Clear all data for current user"""
    try:
        current_file = get_storage_file()
        if os.path.exists(current_file):
            os.remove(current_file)
        return True
    except:
        return False

def get_all():
    """Get all data for current user"""
    try:
        current_file = get_storage_file()
        if not os.path.exists(current_file):
            return {}
        
        with open(current_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def export_data():
    """Export all data as JSON string"""
    return json.dumps(get_all(), ensure_ascii=False, indent=2)

def import_data(json_data):
    """Import data from JSON string"""
    try:
        data = json.loads(json_data)
        current_file = get_storage_file()
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False
