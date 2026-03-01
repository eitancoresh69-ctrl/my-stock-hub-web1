# storage.py — שמירת נתונים קבועה ב-SQLite
# הנתונים שמורים בקובץ hub_data.db ולא נמחקים כשסוגרים את הדפדפן

import sqlite3
import json
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "hub_data.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS state (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT
        )
    """)
    conn.commit()
    return conn


# ──────────────────────────────────────────────
# פונקציות בסיסיות
# ──────────────────────────────────────────────

def save(key: str, value) -> bool:
    """שומר ערך לדיסק. תומך ב: list, dict, int, float, str, DataFrame"""
    try:
        if isinstance(value, pd.DataFrame):
            serialized = {"__type__": "dataframe", "data": value.to_dict(orient="records")}
        else:
            serialized = value
        with _get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO state (key, value, updated_at) VALUES (?,?,?)",
                (key, json.dumps(serialized, default=str), datetime.now().isoformat())
            )
        return True
    except Exception as e:
        print(f"[storage] שגיאת שמירה '{key}': {e}")
        return False


def load(key: str, default=None):
    """טוען ערך מהדיסק. מחזיר default אם לא קיים."""
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT value FROM state WHERE key=?", (key,)
            ).fetchone()
        if row is None:
            return default
        data = json.loads(row[0])
        if isinstance(data, dict) and data.get("__type__") == "dataframe":
            return pd.DataFrame(data["data"])
        return data
    except Exception as e:
        print(f"[storage] שגיאת טעינה '{key}': {e}")
        return default


def delete(key: str):
    """מוחק ערך מהדיסק."""
    try:
        with _get_conn() as conn:
            conn.execute("DELETE FROM state WHERE key=?", (key,))
    except Exception:
        pass


def delete_prefix(prefix: str):
    """מוחק את כל המפתחות שמתחילים ב-prefix (למשל: 'val_')"""
    try:
        with _get_conn() as conn:
            conn.execute("DELETE FROM state WHERE key LIKE ?", (f"{prefix}%",))
    except Exception:
        pass


# ──────────────────────────────────────────────
# פונקציות נוחות לשימוש ב-session_state
# ──────────────────────────────────────────────

def init_from_disk(st_session, key: str, default=None):
    """
    אם המפתח לא קיים ב-session_state — טוען מהדיסק.
    השתמש בזה בתחילת כל טעינה.
    """
    if key not in st_session:
        st_session[key] = load(key, default)


def sync_to_disk(st_session, key: str):
    """שומר ערך מ-session_state לדיסק."""
    if key in st_session:
        save(key, st_session[key])


# ──────────────────────────────────────────────
# קיצורי דרך לפרויקט הספציפי הזה
# ──────────────────────────────────────────────

PORTFOLIO_KEYS = [
    # תיק ראשי
    "portfolio_buy_prices",   # dict: {Symbol: BuyPrice}
    "portfolio_quantities",   # dict: {Symbol: Qty}
    # סוכן ערך
    "val_cash_ils",
    "val_portfolio",
    "val_trades_log",
    "val_initial_ils",
    "val_closed_trades",
    # סוכן יומי
    "day_cash_ils",
    "day_portfolio",
    "day_trades_log",
    "day_initial_ils",
    "day_closed_trades",
    # ML
    "ml_trained",
    "ml_accuracy",
    "ml_runs",
    "ml_params",
    "ml_insights",
    # הגדרות
    "kill_switch_active",
    "auto_scan_interval",
]

PORTFOLIO_DEFAULTS = {
    "portfolio_buy_prices":   {},
    "portfolio_quantities":   {},
    "val_cash_ils":           5000.0,
    "val_portfolio":          [],
    "val_trades_log":         [],
    "val_initial_ils":        5000.0,
    "val_closed_trades":      [],
    "day_cash_ils":           5000.0,
    "day_portfolio":          [],
    "day_trades_log":         [],
    "day_initial_ils":        5000.0,
    "day_closed_trades":      [],
    "ml_trained":             False,
    "ml_accuracy":            0.0,
    "ml_runs":                0,
    "ml_params":              {"risk_ratio": 1.0, "rsi_buy": 40, "rsi_sell": 65, "min_score": 4},
    "ml_insights":            [],
    "kill_switch_active":     False,
    "auto_scan_interval":     0,
}


def load_all_to_session(st_session):
    """
    טוען את כל הנתונים השמורים לתוך session_state בפעם אחת.
    קרא לזה בתחילת app.py.
    """
    for key in PORTFOLIO_KEYS:
        if key not in st_session:
            default = PORTFOLIO_DEFAULTS.get(key)
            st_session[key] = load(key, default)


def save_portfolio(st_session):
    """שומר את נתוני התיק הראשי לדיסק."""
    for key in ["portfolio_buy_prices", "portfolio_quantities"]:
        sync_to_disk(st_session, key)


def save_simulator(st_session, prefix: str):
    """שומר נתוני סוכן (val / day) לדיסק."""
    for suffix in ["cash_ils", "portfolio", "trades_log", "initial_ils", "closed_trades"]:
        key = f"{prefix}_{suffix}"
        sync_to_disk(st_session, key)


def save_ml(st_session):
    """שומר נתוני ML לדיסק."""
    for key in ["ml_trained", "ml_accuracy", "ml_runs", "ml_params", "ml_insights"]:
        sync_to_disk(st_session, key)


def reset_simulator(st_session, prefix: str, initial_ils: float = 5000.0):
    """מאפס סוכן ומוחק מהדיסק."""
    keys = [f"{prefix}_cash_ils", f"{prefix}_portfolio", f"{prefix}_trades_log",
            f"{prefix}_initial_ils", f"{prefix}_closed_trades"]
    for k in keys:
        st_session.pop(k, None)
        delete(k)
    # הגדרות ברירת מחדל
    st_session[f"{prefix}_cash_ils"]     = initial_ils
    st_session[f"{prefix}_portfolio"]    = []
    st_session[f"{prefix}_trades_log"]   = []
    st_session[f"{prefix}_initial_ils"]  = initial_ils
    st_session[f"{prefix}_closed_trades"] = []
    save_simulator(st_session, prefix)


# ─── מפתחות נוספים לתיק AI ───────────────────────────────────────────────────
AI_PORTFOLIO_KEYS = [
    "aip_capital", "aip_cash", "aip_positions", "aip_trades",
    "aip_decisions", "aip_performance", "aip_settings", "aip_enabled",
]

def load_ai_portfolio(st_session):
    """טוען את כל נתוני התיק המנוהל."""
    from ai_portfolio import (KEY_CAPITAL, KEY_CASH, KEY_POSITIONS,
                               KEY_TRADES, KEY_DECISIONS, KEY_PERF,
                               KEY_SETTINGS, KEY_ENABLED)
    defaults = {
        KEY_CAPITAL:  10000.0, KEY_CASH:     10000.0,
        KEY_POSITIONS: [],     KEY_TRADES:    [],
        KEY_DECISIONS: [],     KEY_PERF:      [],
        KEY_SETTINGS:  {
            "max_position_pct":20.0,"stop_loss_pct":8.0,
            "take_profit_pct":20.0,"min_score":4,
            "use_ml":True,"risk_level":"medium",
        },
        KEY_ENABLED: False,
    }
    for k, d in defaults.items():
        if k not in st_session:
            st_session[k] = load(k, d)
