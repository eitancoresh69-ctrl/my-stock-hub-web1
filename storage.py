#!/usr/bin/env python3
# storage.py - Enhanced with Global ML System
import json
import os
import hashlib
import time
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
# USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class UserManager:
    """User management with security"""
    
    @staticmethod
    def hash_password(password):
        """Hash password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register_user(username, password):
        """Register new user"""
        users = load("users_data", {})
        
        if username in users:
            return False, "User exists"
        
        users[username] = {
            "password": UserManager.hash_password(password),
            "created": datetime.now().isoformat(),
            "subscription": "basic",
            "portfolio": {},
            "api_key": hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()[:32]
        }
        
        save("users_data", users)
        return True, "Registered"
    
    @staticmethod
    def login(username, password):
        """Login user"""
        users = load("users_data", {})
        
        if username not in users:
            return False, "Not found"
        
        if users[username]["password"] != UserManager.hash_password(password):
            return False, "Wrong password"
        
        return True, users[username]

# ═══════════════════════════════════════════════════════════════
# GLOBAL ML SYSTEM
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
        """Get global insights"""
        global_trades = load("global_trades_all_users", [])
        user_trades = load("user_trades_by_user", {})
        
        if not global_trades:
            return {
                "total_trades": 0,
                "total_users": 0,
                "avg_profit": 0,
                "win_rate": 0
            }
        
        profits = [t.get("profit", 0) for t in global_trades]
        wins = sum(1 for p in profits if p > 0)
        
        return {
            "total_trades": len(global_trades),
            "total_users": len(user_trades),
            "avg_profit": sum(profits) / len(profits) if profits else 0,
            "win_rate": wins / len(global_trades) if global_trades else 0
        }

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
    """Export all data"""
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
