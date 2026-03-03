# simulator.py — מסחר דמו רב-משתמשים + הגנת חסימת ענן v2026
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import numpy as np
from datetime import datetime
from storage import save, load  # שימוש בפונקציות הליבה לשמירה בענן

# ─── מנגנון הסוואה למניעת חסימות ב-Render ──────────────────────────────────
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def _get_agent_df(df_all: pd.DataFrame, prefer_short: bool = False) -> pd.DataFrame:
    needed = ["Symbol","Price","Currency","Score","RSI","Margin",
              "DivYield","PayoutRatio","CashVsDebt","InsiderHeld","TargetUpside"]
    scan_df = st.session_state.get("agent_universe_short_df" if prefer_short else "agent_universe_df")
    if scan_df is not None and not scan_df.empty:
        have = [c for c in needed if c in scan_df.columns]
        return scan_df[have].copy()
    return df_all

@st.cache_data(ttl=300)
def _get_usd_rate() -> float:
    try:
        h = yf.Ticker("USDILS=X", session=session).history(period="1d")
        return float(h["Close"].iloc[-1]) if not h.empty else 3.75
    except: return 3.75

@st.cache_data(ttl=60)
def _get_live_price(symbol: str) -> float:
    try:
        h = yf.Ticker(symbol, session=session).history(period="1d", interval="1m")
        return float(h["Close"].iloc[-1]) if not h.empty else 0.0
    except: return 0.0

def _safe_float(val):
    """המרת numpy float למספר רגיל למניעת שגיאות שמירה בענן"""
    if isinstance(val, (np.floating, np.integer)):
        return val.item()
    return val

# ─── לוגיקת משתמשים (Private Simulator) ────────────────────────────────────
def _get_user_key(prefix: str, key_name: str) -> str:
    user = st.session_state.get("current_user", "guest")
    return f"{user}_{prefix}_{key_name}"

def _init_demo_state(prefix: str, initial_ils: float = 5000.0):
    user = st.session_state.get("current_user", "guest")
    keys = [
        (f"{prefix}_cash_ils", initial_ils),
        (f"{prefix}_portfolio", []),
        (f"{prefix}_trades_log", []),
        (f"{prefix}_initial_ils", initial_ils),
        (f"{prefix}_closed_trades", [])
    ]
    for k_short, val in keys:
        full_key = _get_user_key(prefix, k_short)
        if full_key not in st.session_state:
            # מנסה לטעון מהענן (storage.py) או משתמש בברירת מחדל
            loaded_val = load(full_key, val)
            st.session_state[full_key] = loaded_val if loaded_val is not None else val

def _save_state(prefix: str):
    """שמירת כל נתוני הסימולטור של המשתמש הנוכחי לענן"""
    user = st.session_state.get("current_user", "guest")
    for k_short in ["cash_ils", "portfolio", "trades_log", "closed_trades"]:
        full_key = _get_user_key(prefix, k_short)
        save(full_key, st.session_state.get(full_key))

# ─── פונקציות עזר לתצוגה ──────────────────────────────────────────────────────
def _calc_total_val(prefix: str, usd_rate: float):
    port = st.session_state.get(_get_user_key(prefix, "portfolio"), [])
    total = 0.0
    for p in port:
        lp = _get_live_price(p["Symbol"]) or p["Buy_Price_Raw"]
        val = lp * p["Qty"]
        total += (val * usd_rate if p["Currency"] == "$" else val / 100)
    return total

def render_value_agent(df_all: pd.DataFrame):
    st.markdown('<div class="ai-card" style="border-right-color:#2e7d32;"><b>💼 סוכן השקעות ערך (פרטי)</b></div>', unsafe_allow_html=True)
    _init_demo_state("val")
    usd = _get_usd_rate()
    
    u_cash_key = _get_user_key("val", "cash_ils")
    u_port_key = _get_user_key("val", "portfolio")
    u_log_key  = _get_user_key("val", "trades_log")

    port_ils = _calc_total_val("val", usd)
    cash = st.session_state.get(u_cash_key, 5000.0)
    total = cash + port_ils
    initial = st.session_state.get(_get_user_key("val", "initial_ils"), 5000.0)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("💵 מזומן דמו", f"₪{cash:,.2f}")
    c2.metric("💼 שווי מניות", f"₪{port_ils:,.2f}")
    c3.metric("📊 סה\"כ הון", f"₪{total:,.2f}")
    c4.metric("📈 רווח/הפסד", f"₪{total-initial:,.2f}", delta=f"{(total/initial-1)*100:.1f}%")

    if st.button("🚀 הפעל סריקת ערך וקנייה", type="primary", key="v_run"):
        _df = _get_agent_df(df_all)
        gold = _df[_df["Score"] >= 5]
        if not gold.empty and cash > 500:
            inv = cash / len(gold)
            for _, r in gold.iterrows():
                lp = _get_live_price(r["Symbol"]) or r["Price"]
                qty = (inv/usd)/lp if r["Currency"] == "$" else inv/(lp/100)
                st.session_state[u_port_key].append({
                    "Symbol": r["Symbol"], "Qty": _safe_float(qty), "Buy_Price_Raw": _safe_float(lp),
                    "Currency": r["Currency"], "Reason": f"ציון {r['Score']} | RSI {r['RSI']:.0f}"
                })
                st.session_state[u_log_key].insert(0, {"זמן": datetime.now().strftime("%H:%M"), "📌": r["Symbol"], "↔️": "קנייה 🟢", "💰": f"{r['Currency']}{lp:.2f}"})
            st.session_state[u_cash_key] = 0
            _save_state("val")
            st.rerun()

    if st.session_state.get(u_port_key):
        st.write("### 📋 פוזיציות פתוחות")
        st.dataframe(pd.DataFrame(st.session_state.get(u_port_key, [])), use_container_width=True)
        if st.button("💸 מכור הכל ואסוף מזומן", key="v_sell"):
            st.session_state[u_cash_key] = total
            st.session_state[u_port_key] = []
            _save_state("val")
            st.rerun()

def render_day_trade_agent(df_all: pd.DataFrame):
    st.markdown('<div class="ai-card" style="border-right-color:#d32f2f;"><b>⚡ סוכן מסחר יומי (פרטי)</b></div>', unsafe_allow_html=True)
    _init_demo_state("day")
    usd = _get_usd_rate()
    
    u_cash_key = _get_user_key("day", "cash_ils")
    u_port_key = _get_user_key("day", "portfolio")
    
    cash = st.session_state.get(u_cash_key, 5000.0)
    port_val = _calc_total_val("day", usd)
    
    c1,c2,c3 = st.columns(3)
    c1.metric("💵 מזומן יומי", f"₪{cash:,.2f}")
    c2.metric("💼 שווי פוזיציות", f"₪{port_val:,.2f}")
    c3.metric("📈 סה\"כ", f"₪{cash + port_val:,.2f}")

    if st.button("⚡ הפעל סוכן יומי (מומנטום RSI)", type="primary", key="d_run"):
        _df = _get_agent_df(df_all, prefer_short=True)
        mo = _df[(_df["RSI"] < 35) | (_df["RSI"] > 65)].head(3)
        if not mo.empty and cash > 500:
            inv = cash / len(mo)
            for _, r in mo.iterrows():
                lp = _get_live_price(r["Symbol"]) or r["Price"]
                qty = (inv/usd)/lp if r["Currency"] == "$" else inv/(lp/100)
                st.session_state[u_port_key].append({
                    "Symbol": r["Symbol"], "Qty": _safe_float(qty), "Buy_Price_Raw": _safe_float(lp),
                    "Currency": r["Currency"], "Reason": f"מומנטום RSI {r['RSI']:.0f}"
                })
            st.session_state[u_cash_key] = 0
            _save_state("day")
            st.rerun()
            
    if st.session_state.get(u_port_key):
        st.write("### 📋 עסקאות יום פעילות")
        st.dataframe(pd.DataFrame(st.session_state.get(u_port_key, [])), use_container_width=True)
        if st.button("🔄 סגור יום וממש רווחים", key="d_sell"):
            st.session_state[u_cash_key] = cash + port_val
            st.session_state[u_port_key] = []
            _save_state("day")
            st.rerun()
