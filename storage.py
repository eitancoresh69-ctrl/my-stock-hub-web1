#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Storage System with:
- Persistent sessions
- Security questions for password recovery
- Database backup and recovery
- Logging system
- Health checks
"""

import json
import os
import hashlib
import time
import pickle
import base64
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

STORAGE_FILE = "trading_data.json"
DATABASE_FILE = "trading_system.db"
LOGS_FILE = "system.log"
BACKUP_DIR = "backups"

# Create backup directory
Path(BACKUP_DIR).mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

def init_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            created TIMESTAMP,
            subscription TEXT,
            cash REAL DEFAULT 100000,
            api_key TEXT,
            last_login TIMESTAMP
        )
    ''')
    
    # Agents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY,
            username TEXT,
            agent_name TEXT,
            status TEXT,
            cash REAL DEFAULT 5000,
            portfolio_value REAL DEFAULT 0,
            trades_count INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            last_run TIMESTAMP,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    # Trades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            username TEXT,
            agent_name TEXT,
            symbol TEXT,
            action TEXT,
            price REAL,
            quantity INTEGER,
            profit_loss REAL,
            timestamp TIMESTAMP,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            token TEXT,
            created TIMESTAMP,
            expires TIMESTAMP,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    # Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            username TEXT,
            event_type TEXT,
            message TEXT,
            timestamp TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize on startup
init_database()

# ═══════════════════════════════════════════════════════════════
# CORE STORAGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load(key, default=None):
    """Load data from JSON storage"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return default
        
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get(key, default)
    except:
        return default

def save(key, value):
    """Save data to JSON storage"""
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
    except:
        return False

# ═══════════════════════════════════════════════════════════════
# PERSISTENT SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class SessionManager:
    """Manage persistent sessions that survive browser refresh"""
    
    @staticmethod
    def create_session(username):
        """Create persistent session"""
        token = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()
        expires = datetime.now() + timedelta(days=30)
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (username, token, created, expires)
            VALUES (?, ?, ?, ?)
        ''', (username, token, datetime.now(), expires))
        
        conn.commit()
        conn.close()
        
        log_system(username, "SESSION_CREATED", f"Session created with 30-day expiry")
        return token
    
    @staticmethod
    def validate_session(username, token):
        """Validate persistent session"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sessions 
            WHERE username = ? AND token = ? AND expires > ?
        ''', (username, token, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    @staticmethod
    def get_stored_username():
        """Get last logged in username from database"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username FROM sessions 
                WHERE expires > ? 
                ORDER BY created DESC LIMIT 1
            ''', (datetime.now(),))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except:
            return None
    
    @staticmethod
    def clear_session(username):
        """Clear session on logout"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE username = ?', (username,))
        conn.commit()
        conn.close()

# ═══════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class UserManager:
    """User management with database"""
    
    @staticmethod
    def hash_password(password):
        """Hash password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register_user(username, password, security_q="", security_a=""):
        """Register new user with security question"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return False, "User already exists"
            
            api_key = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()[:32]
            hashed_answer = hashlib.sha256(security_a.encode()).hexdigest() if security_a else ""
            
            cursor.execute('''
                INSERT INTO users (username, password, created, subscription, cash, api_key)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, UserManager.hash_password(password), datetime.now(), "basic", 100000.0, api_key))
            
            # Save security question
            cursor.execute('''
                INSERT INTO logs (username, event_type, message, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (username, "SECURITY_Q", f"{security_q}|{hashed_answer}", datetime.now()))
            
            conn.commit()
            conn.close()
            
            log_system(username, "USER_REGISTERED", "New user registered")
            
            # Initialize agents for user
            AgentManager.initialize_user_agents(username)
            
            return True, "User registered"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def login(username, password):
        """Login user"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            if user[2] != UserManager.hash_password(password):
                return False, "Wrong password"
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE username = ?', 
                         (datetime.now(), username))
            conn.commit()
            conn.close()
            
            # Create persistent session
            token = SessionManager.create_session(username)
            log_system(username, "LOGIN", "User logged in")
            
            return True, {
                "username": user[1],
                "subscription": user[4],
                "cash": user[5],
                "api_key": user[6],
                "token": token
            }
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_security_question(username):
        """Get user's security question"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT message FROM logs 
                WHERE username = ? AND event_type = 'SECURITY_Q'
                LIMIT 1
            ''', (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                parts = result[0].split('|')
                if len(parts) == 2:
                    return (parts[0], parts[1])
            return None
        except:
            return None
    
    @staticmethod
    def reset_password(username, security_answer, new_password):
        """Reset password with security answer"""
        try:
            security_info = UserManager.get_security_question(username)
            if not security_info:
                return False, "User not found"
            
            _, stored_answer = security_info
            provided_answer = hashlib.sha256(security_answer.encode()).hexdigest()
            
            if provided_answer != stored_answer:
                return False, "Answer incorrect"
            
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET password = ? WHERE username = ?
            ''', (UserManager.hash_password(new_password), username))
            
            conn.commit()
            conn.close()
            
            log_system(username, "PASSWORD_RESET", "Password reset via security question")
            return True, "Password reset successfully"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_user(username):
        """Get user data"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    "username": user[1],
                    "subscription": user[4],
                    "cash": user[5],
                    "api_key": user[6],
                    "created": user[3],
                    "last_login": user[7]
                }
            return {}
        except:
            return {}

# ═══════════════════════════════════════════════════════════════
# AGENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class AgentManager:
    """Manage trading agents with persistent state"""
    
    AGENT_NAMES = ["ValueAgent", "DayTraderAgent", "MLAgent", "TrendAgent"]
    INITIAL_CASH = 5000.0
    
    @staticmethod
    def initialize_user_agents(username):
        """Initialize agents for new user"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            for agent_name in AgentManager.AGENT_NAMES:
                cursor.execute('''
                    INSERT INTO agents (username, agent_name, status, cash, portfolio_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, agent_name, "RUNNING", AgentManager.INITIAL_CASH, 0))
            
            conn.commit()
            conn.close()
            
            log_system(username, "AGENTS_INIT", f"Initialized {len(AgentManager.AGENT_NAMES)} agents with ₪{AgentManager.INITIAL_CASH} each")
        except:
            pass
    
    @staticmethod
    def get_all_agents(username):
        """Get all user agents"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM agents WHERE username = ?
            ''', (username,))
            
            agents = cursor.fetchall()
            conn.close()
            
            result = []
            for agent in agents:
                result.append({
                    "agent_name": agent[2],
                    "status": agent[3],
                    "cash": agent[4],
                    "portfolio_value": agent[5],
                    "trades_count": agent[6],
                    "wins": agent[7]
                })
            
            return result
        except:
            return []

# ═══════════════════════════════════════════════════════════════
# LOGGING SYSTEM
# ═══════════════════════════════════════════════════════════════

def log_system(username, event_type, message):
    """Log system events"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (username, event_type, message, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (username, event_type, message, datetime.now()))
        
        conn.commit()
        conn.close()
    except:
        pass

def get_logs(username, limit=100):
    """Get logs for user"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_type, message, timestamp FROM logs 
            WHERE username = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (username, limit))
        
        logs = cursor.fetchall()
        conn.close()
        
        return [{"type": log[0], "msg": log[1], "time": log[2]} for log in logs]
    except:
        return []

# ═══════════════════════════════════════════════════════════════
# BACKUP & RECOVERY
# ═══════════════════════════════════════════════════════════════

def backup_database():
    """Create database backup"""
    try:
        if os.path.exists(DATABASE_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{BACKUP_DIR}/trading_system_{timestamp}.db"
            
            import shutil
            shutil.copy(DATABASE_FILE, backup_file)
            
            log_system("SYSTEM", "BACKUP_CREATED", f"Backup created: {backup_file}")
            return True
    except:
        pass
    return False

# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK SYSTEM
# ═══════════════════════════════════════════════════════════════

class HealthChecker:
    """Check system health"""
    
    @staticmethod
    def check_all():
        """Full health check"""
        health = {
            "database": HealthChecker.check_database(),
            "storage": HealthChecker.check_storage(),
            "agents": HealthChecker.check_agents(),
            "timestamp": datetime.now().isoformat()
        }
        return health
    
    @staticmethod
    def check_database():
        """Check database integrity"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            users = cursor.fetchone()[0]
            conn.close()
            return {"status": "OK", "users": users}
        except:
            return {"status": "ERROR", "users": 0}
    
    @staticmethod
    def check_storage():
        """Check storage file"""
        if os.path.exists(STORAGE_FILE):
            size = os.path.getsize(STORAGE_FILE) / 1024
            return {"status": "OK", "size_kb": size}
        return {"status": "OK", "size_kb": 0}
    
    @staticmethod
    def check_agents():
        """Check agents status"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'RUNNING'")
            running = cursor.fetchone()[0]
            conn.close()
            return {"status": "OK", "running": running}
        except:
            return {"status": "ERROR", "running": 0}

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_all():
    """Get all data"""
    try:
        if not os.path.exists(STORAGE_FILE):
            return {}
        
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

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

def export_data():
    """Export all data"""
    return json.dumps(get_all(), ensure_ascii=False, indent=2)

def load_ai_portfolio(session_state):
    """Load AI portfolio from storage"""
    portfolio = load("ai_portfolio", {})
    if portfolio:
        session_state["ai_portfolio"] = portfolio

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
# ML & EXECUTION FUNCTIONS
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

def save_execution_log(log_entry):
    """Save execution log"""
    logs = load("execution_logs", [])
    logs.append(log_entry)
    save("execution_logs", logs)

def load_execution_logs():
    """Load execution logs"""
    return load("execution_logs", [])

def save_failsafe_settings(settings):
    """Save failsafe settings"""
    save("failsafe_settings", settings)

def load_failsafe_settings():
    """Load failsafe settings"""
    return load("failsafe_settings", {})

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

# Initialize system on import
backup_database()
