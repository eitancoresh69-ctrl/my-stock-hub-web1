# user_manager.py — ניהול משתמשים, התחברות והצפנת סיסמאות
import streamlit as st
import json
import os
import hashlib

USERS_DB_FILE = "users_db.json"

def hash_password(password):
    """מצפין את הסיסמה בעזרת SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """טוען את מסד הנתונים של המשתמשים"""
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """שומר את מסד הנתונים של המשתמשים"""
    with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def register_user(username, password):
    """רושם משתמש חדש אם הוא לא קיים"""
    if not username or not password:
        return False, "שם משתמש וסיסמה אינם יכולים להיות ריקים."
        
    users = load_users()
    if username in users:
        return False, "שם המשתמש כבר קיים במערכת."
        
    users[username] = {
        "password": hash_password(password),
        "created_at": st.session_state.get("start_time", "Unknown"),
        "tier": "Basic" # הכנה למערכת הפרימיום העתידית
    }
    save_users(users)
    return True, "חשבון נוצר בהצלחה! התחבר כעת."

def authenticate(username, password):
    """בודק האם פרטי ההתחברות נכונים"""
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

def render_login_screen():
    """מצייר את מסך ההתחברות של המערכת"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; background:linear-gradient(135deg,#1565c0 0%,#1976d2 55%,#42a5f5 100%); padding: 30px; border-radius: 15px; color: white;'>
            <h1 style='margin:0; font-size: 3em;'>🌐</h1>
            <h1 style='margin:0;'>Investment Hub Elite 2026</h1>
            <p>התחבר כדי לגשת לתיק ההשקעות שלך ולסוכני ה-AI</p>
        </div>
        <br>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab_login, tab_register = st.tabs(["🔒 התחברות", "📝 הרשמה חדשה"])
        
        with tab_login:
            st.subheader("ברוך שובך!")
            login_user = st.text_input("שם משתמש", key="login_user")
            login_pass = st.text_input("סיסמה", type="password", key="login_pass")
            
            if st.button("הכנס למערכת", type="primary", use_container_width=True):
                if authenticate(login_user, login_pass):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = login_user
                    st.rerun()
                else:
                    st.error("❌ שם משתמש או סיסמה שגויים.")
                    
        with tab_register:
            st.subheader("צור חשבון משתמש")
            reg_user = st.text_input("בחר שם משתמש", key="reg_user")
            reg_pass = st.text_input("בחר סיסמה", type="password", key="reg_pass")
            reg_pass_verify = st.text_input("אמת סיסמה", type="password", key="reg_pass_v")
            
            if st.button("הרשם למערכת", use_container_width=True):
                if reg_pass != reg_pass_verify:
                    st.error("❌ הסיסמאות אינן תואמות.")
                else:
                    success, msg = register_user(reg_user, reg_pass)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
