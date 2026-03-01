# storage.py — הוסף קובץ חדש זה לפרויקט
import sqlite3, json, os

DB_PATH = os.path.join(os.path.dirname(__file__), "hub_data.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def save_state(key: str, value):
    """שמירה של כל ערך מ-session_state לדיסק"""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS state 
            (key TEXT PRIMARY KEY, value TEXT)
        """)
        conn.execute(
            "INSERT OR REPLACE INTO state (key, value) VALUES (?,?)",
            (key, json.dumps(value, default=str))
        )

def load_state(key: str, default=None):
    """טעינה מחדש בכל פתיחת האפליקציה"""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS state 
            (key TEXT PRIMARY KEY, value TEXT)
        """)
        row = conn.execute(
            "SELECT value FROM state WHERE key=?", (key,)
        ).fetchone()
    return json.loads(row[0]) if row else default
