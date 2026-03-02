#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
storage.py - Complete Storage System with Multi-User Support
Ready for GitHub - Copy and paste directly
"""

import json
import os
import hashlib
import time
import pickle
import base64
from datetime import datetime

STORAGE_FILE = "trading_data.json"

# ═══════════════════════════════════════════════════════════════
# CORE STORAGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load(key, default=None):
    """Load data from storage"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return default
        
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get(key, default)
    except:
        return default

def save(key, value):
    """Save data to storage"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        data[key] = value
        
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Storage error: {e}")
        return False

def delete(key):
    """Delete data from storage"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if key in data:
                del data[key]
            
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
    except:
        return False

def load_all_to_session(session_state):
    """Load all data to Streamlit session"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for key, value in data.items():
                if key not in session_state:
                    session_state[key] = value
    except:
        pass

# ═══════════════════════════════════════════════════════════════
# USER MANAGEMENT - MULTI-USER SYSTEM
# ═══════════════════════════════════════════════════════════════

class UserManager:
    """User management with authentication"""
    
    @staticmethod
    def hash_password(password):
        """Hash password with SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register_user(username, password):
        """Register new user"""
        users = load("users_data", {})
        
        if not username or not password:
            return False, "Username and password required"
        
        if username in users:
            return False, "User already exists"
        
        users[username] = {
            "password": UserManager.hash_password(password),
            "created": datetime.now().isoformat(),
            "subscription": "basic",
            "portfolio": {},
            "cash": 100000.0,
            "trades": [],
            "api_key": hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()[:32]
        }
        
        save("users_data", users)
        return True, "User registered successfully"
    
    @staticmethod
    def login(username, password):
        """Login user"""
        users = load("users_data", {})
        
        if username not in users:
            return False, "User not found"
        
        if users[username]["password"] != UserManager.hash_password(password):
            return False, "Wrong password"
        
        return True, users[username]
    
    @staticmethod
    def get_user(username):
        """Get user data"""
        users = load("users_data", {})
        return users.get(username, {})
    
    @staticmethod
    def save_user_data(username, user_data):
        """Save user data"""
        users = load("users_data", {})
        if username in users:
            users[username] = user_data
            save("users_data", users)
            return True
        return False

# ═══════════════════════════════════════════════════════════════
# GLOBAL ML SYSTEM - LEARN FROM ALL USERS
# ═══════════════════════════════════════════════════════════════

class GlobalMLSystem:
    """Global machine learning from all users"""
    
    @staticmethod
    def add_trade(username, trade):
        """Add trade to global learning"""
        global_trades = load("global_trades_all_users", [])
        user_trades = load("user_trades_by_user", {})
        
        if username not in user_trades:
            user_trades[username] = []
        
        user_trades[username].append(trade)
        global_trades.append(trade)
        
        save("global_trades_all_users", global_trades)
        save("user_trades_by_user", user_trades)
    
    @staticmethod
    def get_global_insights():
        """Get global insights from all users"""
        global_trades = load("global_trades_all_users", [])
        user_trades = load("user_trades_by_user", {})
        
        if not global_trades:
            return {
                "total_trades": 0,
                "total_users": 0,
                "avg_profit": 0,
                "win_rate": 0
            }
        
        profits = [t.get("profit", 0) for t in global_trades if isinstance(t, dict)]
        wins = sum(1 for p in profits if p > 0)
        
        return {
            "total_trades": len(global_trades),
            "total_users": len(user_trades),
            "avg_profit": sum(profits) / len(profits) if profits else 0,
            "win_rate": wins / len(global_trades) if global_trades else 0,
            "most_traded": self._get_most_traded(global_trades)
        }
    
    @staticmethod
    def _get_most_traded(trades):
        """Get most traded symbols"""
        symbols = {}
        for trade in trades:
            if isinstance(trade, dict) and "symbol" in trade:
                sym = trade["symbol"]
                symbols[sym] = symbols.get(sym, 0) + 1
        return dict(sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:5])

# ═══════════════════════════════════════════════════════════════
# ML FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def save_ml(model_data):
    """Save ML model and data"""
    try:
        if isinstance(model_data, dict):
            save("ml_model_data", model_data)
        else:
            serialized = base64.b64encode(pickle.dumps(model_data)).decode()
            save("ml_model_serialized", serialized)
        return True
    except:
        return False

def load_ml(key="ml_model_data"):
    """Load ML model or data"""
    return load(key, {})

def save_ml_results(results):
    """Save ML training results"""
    save("ml_results", results)

def load_ml_results():
    """Load ML training results"""
    return load("ml_results", {})

# ═══════════════════════════════════════════════════════════════
# SIMULATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def save_simulator(state):
    """Save simulator state"""
    save("simulator_state", state)

def reset_simulator():
    """Reset simulator"""
    delete("simulator_state")
    save("simulator_reset", True)

def load_simulator():
    """Load simulator state"""
    return load("simulator_state", {})

# ═══════════════════════════════════════════════════════════════
# EXECUTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def save_execution_log(log_entry):
    """Save execution log"""
    logs = load("execution_logs", [])
    logs.append(log_entry)
    save("execution_logs", logs)

def load_execution_logs():
    """Load execution logs"""
    return load("execution_logs", [])

# ═══════════════════════════════════════════════════════════════
# FAILSAFE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def save_failsafe_settings(settings):
    """Save failsafe settings"""
    save("failsafe_settings", settings)

def load_failsafe_settings():
    """Load failsafe settings"""
    return load("failsafe_settings", {})

# ═══════════════════════════════════════════════════════════════
# PORTFOLIO FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load_ai_portfolio(session_state):
    """Load AI portfolio from storage"""
    portfolio = load("ai_portfolio", {})
    if portfolio:
        session_state["ai_portfolio"] = portfolio

def save_ai_portfolio(portfolio):
    """Save AI portfolio"""
    save("ai_portfolio", portfolio)

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def clear_all():
    """Clear all data"""
    try:
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
        return True
    except:
        return False

def get_all():
    """Get all data"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return {}
        
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def export_data():
    """Export all data as JSON"""
    return json.dumps(get_all(), ensure_ascii=False, indent=2)

def import_data(json_data):
    """Import data from JSON"""
    try:
        data = json.loads(json_data)
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_user_portfolio(username):
    """Get specific user's portfolio"""
    user = UserManager.get_user(username)
    return user.get("portfolio", {})

def save_user_portfolio(username, portfolio):
    """Save specific user's portfolio"""
    user = UserManager.get_user(username)
    if user:
        user["portfolio"] = portfolio
        UserManager.save_user_data(username, user)
        return True
    return False

def get_user_cash(username):
    """Get user's cash"""
    user = UserManager.get_user(username)
    return user.get("cash", 100000.0)

def save_user_cash(username, cash):
    """Save user's cash"""
    user = UserManager.get_user(username)
    if user:
        user["cash"] = cash
        UserManager.save_user_data(username, user)
        return True
    return False
