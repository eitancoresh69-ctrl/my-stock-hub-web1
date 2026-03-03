# storage.py — Cloud Edition (PostgreSQL / SQLite) עם סנכרון נתונים מלא
import os
import json
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# ─── חיבור למסד הנתונים בענן (או מקומי) ─────────────────────────────────────────
# אם המערכת רצה ב-Render, היא תקרא את ה-URL אוטומטית. אחרת, תיצור קובץ DB מקומי.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local_hub_data.db")

# תיקון קטן שדרוש ל-Render ול-SQLAlchemy:
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ─── סכמת טבלת הנתונים ───────────────────────────────────────────────────────
class KVPair(Base):
    __tablename__ = "storage_kv"
    key = Column(String, primary_key=True, index=True)
    value = Column(Text)  # שומרים את ה-JSON כטקסט

# יצירת הטבלה אם אינה קיימת
Base.metadata.create_all(bind=engine)

# ─── פונקציות ליבה (שמירה וקריאה מול הענן) ────────────────────────────────────
def load(key, default=None):
    """שולף נתונים ממסד הנתונים בענן"""
    with SessionLocal() as db:
        record = db.query(KVPair).filter(KVPair.key == key).first()
        if record and record.value:
            try:
                return json.loads(record.value)
            except:
                return default
        return default

def save(key, value):
    """שומר נתונים באופן מאובטח למסד הנתונים"""
    with SessionLocal() as db:
        record = db.query(KVPair).filter(KVPair.key == key).first()
        val_str = json.dumps(value, ensure_ascii=False)
        if record:
            record.value = val_str
        else:
            new_record = KVPair(key=key, value=val_str)
            db.add(new_record)
        db.commit()
        return True

def delete(key):
    with SessionLocal() as db:
        record = db.query(KVPair).filter(KVPair.key == key).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False

def clear_all():
    with SessionLocal() as db:
        db.query(KVPair).delete()
        db.commit()
        return True

def get_all():
    result = {}
    with SessionLocal() as db:
        records = db.query(KVPair).all()
        for r in records:
            try:
                result[r.key] = json.loads(r.value)
            except:
                pass
    return result

def export_data():
    return json.dumps(get_all(), ensure_ascii=False, indent=2)

def import_data(json_data):
    try:
        data = json.loads(json_data)
        for k, v in data.items():
            save(k, v)
        return True
    except:
        return False

# ─── פונקציות ייעודיות לאפליקציה ולסוכנים ─────────────────────────────────────
def load_all_to_session(session_state):
    keys_to_load = ["kill_switch_active", "circuit_breaker_triggered", "daily_loss_pct"]
    for k in keys_to_load:
        if k not in session_state:
            session_state[k] = load(k, False if "active" in k or "triggered" in k else 0.0)

def load_ai_portfolio(session_state):
    if "aip_enabled" not in session_state:
        session_state["aip_enabled"] = load("aip_enabled", False)
    if "aip_cash" not in session_state:
        session_state["aip_cash"] = load("aip_cash", 100000.0)
    if "aip_positions" not in session_state:
        session_state["aip_positions"] = load("aip_positions", [])

def save_simulator(session_state, mode="day"):
    if mode == "day":
        save("day_cash_ils", session_state.get("day_cash_ils", 100000.0))
        save("day_portfolio", session_state.get("day_portfolio", []))
        save("day_trades_log", session_state.get("day_trades_log", []))
    else:
        save("val_cash_ils", session_state.get("val_cash_ils", 100000.0))
        save("val_portfolio", session_state.get("val_portfolio", []))
        save("val_trades_log", session_state.get("val_trades_log", []))

def reset_simulator(session_state, mode="day"):
    if mode == "day":
        session_state["day_cash_ils"] = 100000.0
        session_state["day_portfolio"] = []
        session_state["day_trades_log"] = []
        save_simulator(session_state, "day")
    else:
        session_state["val_cash_ils"] = 100000.0
        session_state["val_portfolio"] = []
        session_state["val_trades_log"] = []
        save_simulator(session_state, "val")

def save_ml(data):
    save("ml_data", data)
