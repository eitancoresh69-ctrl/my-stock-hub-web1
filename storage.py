#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
storage.py - מערכת אחסון מתקדמת עם בידוד נתונים למשתמשים (Multi-User Privacy)
"""

import json
import os
import hashlib
import time
import pickle
import base64
from datetime import datetime
import streamlit as st

STORAGE_FILE = "trading_data.json"

# ==============================================================================
# מנגנון בידוד נתונים (Privacy Engine)
# ==============================================================================

# רשימת מפתחות שחייבים להיות משותפים לכולם (משתמשים ולמידת מכונה של הקהילה)
GLOBAL_KEYS = [
    "users_data", 
    "global_trades_all_users", 
    "user_trades_by_user", 
    "ml_model_data", 
    "ml_model_serialized", 
    "ml_results"
]

def _get_scoped_key(key):
    """מזהה את המשתמש הנוכחי ומייצר מפתח שמור ייחודי עבורו כדי לבודד את התיק שלו"""
    if key in GLOBAL_KEYS:
        return key
        
    try:
        # אם יש משתמש מחובר, נוסיף את השם שלו כקידומת לכל שמירה כדי שהיא תהיה פרטית
        if "username" in st.session_state and st.session_state.username:
            return f"{st.session_state.username}_{key}"
    except:
        pass
        
    return key

# ==============================================================================
# פונקציות ליבה לשמירה וטעינה
# ==============================================================================

def load(key, default=None):
    """טעינת נתונים מהאחסון - מושך אוטומטית רק את הנתונים של המשתמש המחובר"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return default
        
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scoped_key = _get_scoped_key(key)
        return data.get(scoped_key, default)
    except:
        return default

def save(key, value):
    """שמירת נתונים לאחסון - נועל אוטומטית את הנתונים תחת שם המשתמש"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        scoped_key = _get_scoped_key(key)
        data[scoped_key] = value
        
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"שגיאת אחסון: {e}")
        return False

def delete(key):
    """מחיקת נתונים מהאחסון פרטי של המשתמש"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            scoped_key = _get_scoped_key(key)
            if scoped_key in data:
                del data[scoped_key]
            
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
    except:
        return False

def load_all_to_session(session_state):
    """טעינת הנתונים לסשן: שואב רק את הנתונים ששייכים למשתמש הספציפי שהתחבר"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            username = session_state.get("username", "")
            prefix = f"{username}_" if username else ""
            
            for key, value in data.items():
                # טעינת נתונים פרטיים של המשתמש (ומחיקת הקידומת כדי שהקוד יעבוד חלק)
                if prefix and key.startswith(prefix):
                    original_key = key[len(prefix):]
                    if original_key not in session_state:
                        session_state[original_key] = value
                
                # טעינת נתונים גלובליים (כמו למידת מכונה קהילתית)
                elif key in GLOBAL_KEYS:
                    if key not in session_state:
                        session_state[key] = value
    except:
        pass

# ==============================================================================
# ניהול התחברויות (Session & Auth)
# ==============================================================================

class SessionManager:
    @staticmethod
    def get_stored_username():
        """משיכת משתמש ששמור בסשן (מבוטל מטעמי אבטחה בגרסה זו כדי לחייב התחברות)"""
        return None
        
    @staticmethod
    def clear_session(username):
        """ניקוי הנתונים ביציאה"""
        pass

class UserManager:
    """ניהול משתמשים והתחברות"""
    
    @staticmethod
    def hash_password(password):
        """הצפנת סיסמה"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register_user(username, password, security_q="לא נבחר", security_a=""):
        """רישום משתמש חדש והכנת תיק ריק עבורו"""
        # משתמש בטעינה רגילה כי users_data נמצא ב-GLOBAL_KEYS
        users = load("users_data", {})
        
        if not username or not password:
            return False, "חובה להזין שם משתמש וסיסמה"
        
        if username in users:
            return False, "המשתמש כבר קיים במערכת"
        
        users[username] = {
            "password": UserManager.hash_password(password),
            "security_question": security_q,
            "security_answer": UserManager.hash_password(security_a.lower().strip()) if security_a else "",
            "created": datetime.now().isoformat(),
            "subscription": "basic",
            "cash": 100000.0,
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
    def get_security_question(username):
        """שליפת שאלת האבטחה לשחזור סיסמה"""
        users = load("users_data", {})
        user = users.get(username)
        if user and "security_question" in user:
            return user["security_question"], user.get("security_answer")
        return None

    @staticmethod
    def reset_password(username, security_answer, new_password):
        """איפוס סיסמה"""
        users = load("users_data", {})
        user = users.get(username)
        if not user:
            return False, "משתמש לא נמצא"
            
        hashed_answer = UserManager.hash_password(security_answer.lower().strip())
        if user.get("security_answer") != hashed_answer:
            return False, "התשובה לשאלת האבטחה שגויה"
            
        user["password"] = UserManager.hash_password(new_password)
        save("users_data", users)
        return True, "הסיסמה אופסה בהצלחה"

# ==============================================================================
# פונקציות למידת מכונה (Machine Learning)
# ==============================================================================

def save_ml(model_data):
    """שמירת נתוני מודל"""
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
    return load(key, {})

def save_ml_results(results):
    save("ml_results", results)

def load_ml_results():
    return load("ml_results", {})

# ==============================================================================
# פונקציות עזר (סימולטור והגנות)
# ==============================================================================

def save_simulator(state, sim_type="day"):
    save(f"simulator_state_{sim_type}", state.get(f"{sim_type}_portfolio", []))

def reset_simulator(state, sim_type="day"):
    delete(f"simulator_state_{sim_type}")
    if f"{sim_type}_portfolio" in state:
        state[f"{sim_type}_portfolio"] = []

def load_simulator():
    return load("simulator_state", {})

def save_execution_log(log_entry):
    logs = load("execution_logs", [])
    logs.append(log_entry)
    save("execution_logs", logs)

def load_execution_logs():
    return load("execution_logs", [])

def save_failsafe_settings(settings):
    save("failsafe_settings", settings)

def load_failsafe_settings():
    return load("failsafe_settings", {})

def load_ai_portfolio(session_state):
    portfolio = load("aip_positions", {})
    if portfolio:
        session_state["aip_positions"] = portfolio

def save_ai_portfolio(portfolio):
    save("aip_positions", portfolio)
