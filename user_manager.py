# user_manager.py — ניהול משתמשים, התחברות והצפנת סיסמאות
import streamlit as st
import json
import os
import hashlib
import uuid

USERS_DB_FILE = "users_db.json"

def hash_string(string):
    """מצפין מחרוזת בעזרת SHA256"""
    return hashlib.sha256(string.encode()).hexdigest()

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

def register_user(username, password, security_question, security_answer):
    """רושם משתמש חדש עם שאלת אבטחה"""
    if not username or not password or not security_answer:
        return False, "כל השדות הם חובה."
        
    users = load_users()
    if username in users:
        return False, "שם המשתמש כבר קיים במערכת."
        
    users[username] = {
        "password": hash_string(password),
        "security_question": security_question,
        # אנחנו מצפינים גם את התשובה כדי שאף אחד לא יוכל לקרוא אותה מקובץ ה-JSON
        "security_answer": hash_string(security_answer.strip().lower()),
        "session_token": "",
        "created_at": str(st.session_state.get("start_time", "Unknown")),
        "tier": "Basic"
    }
    save_users(users)
    return True, "חשבון נוצר בהצלחה! התחבר כעת בלשונית ההתחברות."

def authenticate(username, password):
    """בודק האם פרטי ההתחברות נכונים ויוצר טוקן התחברות"""
    users = load_users()
    if username in users and users[username]["password"] == hash_string(password):
        token = str(uuid.uuid4()) # יצירת מזהה ייחודי לסשן
        users[username]["session_token"] = token
        save_users(users)
        return True, token
    return False, None

def reset_password(username, security_answer, new_password):
    """מאפס סיסמה אם התשובה לשאלת האבטחה נכונה"""
    users = load_users()
    if username not in users:
        return False, "שם משתמש לא קיים במערכת."
        
    saved_answer = users[username].get("security_answer")
    if saved_answer == hash_string(security_answer.strip().lower()):
        users[username]["password"] = hash_string(new_password)
        users[username]["session_token"] = "" # מנתק את כל ההתחברויות הקודמות
        save_users(users)
        return True, "הסיסמה שונתה בהצלחה! התחבר כעת עם הסיסמה החדשה."
        
    return False, "התשובה לשאלת האבטחה שגויה."

def check_active_session():
    """בודק האם קיים טוקן פעיל בשורת הכתובת (URL) כדי למנוע ניתוק בריענון"""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        try:
            # שליפת הטוקן מה-URL
            if hasattr(st, "query_params"):
                token = st.query_params.get("session_token", None)
            else:
                params = st.experimental_get_query_params()
                token = params.get("session_token", [None])[0]

            if token:
                users = load_users()
                for user, data in users.items():
                    if data.get("session_token") == token:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = user
                        return True
        except:
            pass
            
    return st.session_state.get("logged_in", False)

def set_session_token_url(token):
    """שומר את הטוקן ב-URL של הדפדפן"""
    try:
        if hasattr(st, "query_params"):
            st.query_params["session_token"] = token
        else:
            st.experimental_set_query_params(session_token=token)
    except:
        pass

def clear_session_token_url():
    """מוחק את הטוקן מה-URL בזמן התנתקות"""
    try:
        if hasattr(st, "query_params"):
            if "session_token" in st.query_params:
                del st.query_params["session_token"]
        else:
            st.experimental_set_query_params()
    except:
        pass

def render_login_screen():
    """מצייר את מסך ההתחברות של המערכת"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; background:linear-gradient(135deg,#1565c0 0%,#1976d2 55%,#42a5f5 100%); padding: 30px; border-radius: 15px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
            <h1 style='margin:0; font-size: 3.5em;'>🌐</h1>
            <h1 style='margin:0; font-weight:900;'>Investment Hub Elite 2026</h1>
            <p style='font-size: 1.2em; opacity: 0.9;'>התחבר למערכת המסחר והאנליטיקה המתקדמת שלך</p>
        </div>
        <br><br>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab_login, tab_register, tab_forgot = st.tabs(["🔒 התחברות", "📝 הרשמה חדשה", "🔑 שכחתי סיסמה"])
        
        # ══ TAB: התחברות ══
        with tab_login:
            st.subheader("ברוך שובך!")
            login_user = st.text_input("שם משתמש", key="login_user")
            login_pass = st.text_input("סיסמה", type="password", key="login_pass")
            
            if st.button("הכנס למערכת", type="primary", use_container_width=True):
                success, token = authenticate(login_user, login_pass)
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = login_user
                    set_session_token_url(token) # שומר ב-URL כדי שלא יתנתק בריענון
                    st.rerun()
                else:
                    st.error("❌ שם משתמש או סיסמה שגויים.")
                    
        # ══ TAB: הרשמה ══
        with tab_register:
            st.subheader("צור חשבון משתמש")
            reg_user = st.text_input("בחר שם משתמש", key="reg_user")
            reg_pass = st.text_input("בחר סיסמה", type="password", key="reg_pass")
            reg_pass_verify = st.text_input("אמת סיסמה", type="password", key="reg_pass_v")
            
            st.markdown("##### הגדרת שחזור סיסמה")
            questions = [
                "מהו שם חיית המחמד הראשונה שלך?",
                "באיזה רחוב גדלת כילד?",
                "מהו שם בית הספר היסודי שלך?",
                "מהו הדגם של הרכב הראשון שלך?",
                "מהו שם הנעורים של אמך?"
            ]
            reg_q = st.selectbox("בחר שאלת אבטחה", questions, key="reg_q")
            reg_a = st.text_input("תשובה לשאלת האבטחה (זכור אותה היטב!)", key="reg_a")
            
            if st.button("הרשם למערכת", use_container_width=True):
                if reg_pass != reg_pass_verify:
                    st.error("❌ הסיסמאות אינן תואמות.")
                elif len(reg_pass) < 4:
                    st.error("❌ הסיסמה חייבת להיות לפחות 4 תווים.")
                else:
                    success, msg = register_user(reg_user, reg_pass, reg_q, reg_a)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                        
        # ══ TAB: שכחתי סיסמה ══
        with tab_forgot:
            st.subheader("שחזור סיסמה")
            st.info("הזן תחילה את שם המשתמש שלך כדי לראות את שאלת האבטחה שבחרת בהרשמה.")
            
            forgot_user = st.text_input("שם משתמש", key="forgot_user")
            
            users_db = load_users()
            if forgot_user in users_db:
                user_q = users_db[forgot_user].get("security_question", "שאלת אבטחה")
                st.markdown(f"**שאלת האבטחה שלך:** {user_q}")
                forgot_a = st.text_input("הזן את תשובתך", key="forgot_a")
                new_pass = st.text_input("בחר סיסמה חדשה", type="password", key="new_pass")
                
                if st.button("אפס סיסמה עכשיו", use_container_width=True):
                    if len(new_pass) < 4:
                        st.error("❌ הסיסמה החדשה חייבת להיות לפחות 4 תווים.")
                    else:
                        success, msg = reset_password(forgot_user, forgot_a, new_pass)
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
            elif forgot_user:
                st.warning("שם המשתמש לא נמצא במערכת.")
