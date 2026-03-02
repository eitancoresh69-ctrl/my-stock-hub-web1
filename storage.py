#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
storage.py - Complete Storage System with Multi-User Support
"""

import json
import os
import hashlib
import time
import pickle
import base64
from datetime import datetime

STORAGE_FILE = "trading_data.json"

# ==============================================================================
# פונקציות ליבה לשמירה
# ==============================================================================

def load(key, default=None):
    """טעינת נתונים מהאחסון"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return default
        
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get(key, default)
    except:
        return default

def save(key, value):
    """שמירת נתונים לאחסון"""
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
        print(f"שגיאת אחסון: {e}")
        return False

def delete(key):
    """מחיקת נתונים מהאחסון"""
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
    """טעינת כל הנתונים לסשן של Streamlit"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for key, value in data.items():
                if key not in session_state:
                    session_state[key] = value
    except:
        pass

# ==============================================================================
# מערכת משתמשים - תמיכה בריבוי משתמשים
# ==============================================================================

class UserManager:
    """ניהול משתמשים והתחברות"""
    
    @staticmethod
    def hash_password(password):
        """הצפנת סיסמה"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register_user(username, password):
        """רישום משתמש חדש"""
        users = load("users_data", {})
        
        if not username or not password:
            return False, "חובה להזין שם משתמש וסיסמה"
        
        if username in users:
            return False, "המשתמש כבר קיים במערכת"
        
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
        return True, "המשתמש נרשם בהצלחה"
    
    @staticmethod
    def login(username, password):
        """התחברות משתמש"""
        users = load("users_data", {})
        
        if username not in users:
            return False, "המשתמש לא נמצא"
        
        if users[username]["password"] != UserManager.hash_password(password):
            return False, "סיסמה שגויה"
        
        return True, users[username]
    
    @staticmethod
    def get_user(username):
        """קבלת נתוני משתמש"""
        users = load("users_data", {})
        return users.get(username, {})
    
    @staticmethod
    def save_user_data(username, user_data):
        """שמירת נתוני משתמש"""
        users = load("users_data", {})
        if username in users:
            users[username] = user_data
            save("users_data", users)
            return True
        return False

# ==============================================================================
# מערכת למידת מכונה גלובלית
# ==============================================================================

class GlobalMLSystem:
    """למידת מכונה מכלל המשתמשים במערכת"""
    
    @staticmethod
    def add_trade(username, trade):
        """הוספת פעולת מסחר ללמידה הגלובלית"""
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
        """קבלת תובנות מכלל המשתמשים"""
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
            "most_traded": GlobalMLSystem._get_most_traded(global_trades)
        }
    
    @staticmethod
    def _get_most_traded(trades):
        """קבלת המניות הנסחרות ביותר"""
        symbols = {}
        for trade in trades:
            if isinstance(trade, dict) and "symbol" in trade:
                sym = trade["symbol"]
                symbols[sym] = symbols.get(sym, 0) + 1
        return dict(sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:5])

# ==============================================================================
# פונקציות למידת מכונה
# ==============================================================================

def save_ml(model_data):
    """שמירת נתוני המודל"""
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
    """טעינת נתוני מודל"""
    return load(key, {})

def save_ml_results(results):
    """שמירת תוצאות אימון"""
    save("ml_results", results)

def load_ml_results():
    """טעינת תוצאות אימון"""
    return load("ml_results", {})

# ==============================================================================
# פונקציות סימולטור
# ==============================================================================

def save_simulator(state):
    """שמירת מצב סימולטור"""
    save("simulator_state", state)

def reset_simulator():
    """איפוס סימולטור"""
    delete("simulator_state")
    save("simulator_reset", True)

def load_simulator():
    """טעינת מצב סימולטור"""
    return load("simulator_state", {})

# ==============================================================================
# פונקציות ביצוע פעולות
# ==============================================================================

def save_execution_log(log_entry):
    """שמירת יומן ביצוע"""
    logs = load("execution_logs", [])
    logs.append(log_entry)
    save("execution_logs", logs)

def load_execution_logs():
    """טעינת יומני ביצוע"""
    return load("execution_logs", [])

# ==============================================================================
# פונקציות מנגנוני הגנה
# ==============================================================================

def save_failsafe_settings(settings):
    """שמירת הגדרות הגנה"""
    save("failsafe_settings", settings)

def load_failsafe_settings():
    """טעינת הגדרות הגנה"""
    return load("failsafe_settings", {})

# ==============================================================================
# פונקציות תיק השקעות
# ==============================================================================

def load_ai_portfolio(session_state):
    """טעינת תיק בינה מלאכותית"""
    portfolio = load("ai_portfolio", {})
    if portfolio:
        session_state["ai_portfolio"] = portfolio

def save_ai_portfolio(portfolio):
    """שמירת תיק בינה מלאכותית"""
    save("ai_portfolio", portfolio)

# ==============================================================================
# פונקציות עזר
# ==============================================================================

def clear_all():
    """ניקוי כל הנתונים"""
    try:
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
        return True
    except:
        return False

def get_all():
    """קבלת כל הנתונים"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return {}
        
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def export_data():
    """ייצוא נתונים"""
    return json.dumps(get_all(), ensure_ascii=False, indent=2)

def import_data(json_data):
    """ייבוא נתונים"""
    try:
        data = json.loads(json_data)
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_user_portfolio(username):
    """קבלת תיק משתמש ספציפי"""
    user = UserManager.get_user(username)
    return user.get("portfolio", {})

def save_user_portfolio(username, portfolio):
    """שמירת תיק משתמש ספציפי"""
    user = UserManager.get_user(username)
    if user:
        user["portfolio"] = portfolio
        UserManager.save_user_data(username, user)
        return True
    return False

def get_user_cash(username):
    """קבלת יתרת משתמש"""
    user = UserManager.get_user(username)
    return user.get("cash", 100000.0)

def save_user_cash(username, cash):
    """שמירת יתרת משתמש"""
    user = UserManager.get_user(username)
    if user:
        user["cash"] = cash
        UserManager.save_user_data(username, user)
        return True
    return False
