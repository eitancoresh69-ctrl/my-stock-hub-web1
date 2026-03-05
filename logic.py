# logic.py - FINAL - With ALL required columns
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime, timedelta

try:
    from realtime_data import get_live_price_smart
    HAS_REALTIME = True
except:
    HAS_REALTIME = False

def _fetch_single_symbol(ticker: str) -> dict | None:
    """Fetch with ALL columns that traders expect"""
    try:
        time.sleep(0.2)
        
        # Get price
        if HAS_REALTIME:
            price = get_live_price_smart(ticker)
        else:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="1y")
            if hist.empty:
                return None
            price = float(hist["Close"].iloc[-1])
        
        if not price or price <= 0:
            return None
        
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info or {}
        hist = ticker_obj.history(period="1y")
        
        if hist.empty or len(hist) < 50:
            return None
        
        close = hist["Close"]
        rsi = _calc_rsi(close)
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        change = ((close.iloc[-1] / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
        
        # All columns traders need
        currency = "ILS" if str(ticker).endswith(".TA") else "USD"
        price_str = f"{currency}{price:,.2f}"
        
        insider = float(info.get("heldPercentInsiders", 0)) * 100
        target_price = float(info.get("targetMeanPrice", price))
        target_upside = ((target_price / price) - 1) * 100 if price > 0 else 0
        payout = float(info.get("payoutRatio", 0)) * 100
        
        score = 0
        if info.get("revenueGrowth", 0) and info.get("revenueGrowth") > 0.1:
            score += 1
        if rsi < 70 and rsi > 30:
            score += 1
        if ma50 > ma200:
            score += 1
        
        action = "Strong Buy" if score >= 2 else "Buy" if score >= 1 else "Hold"
        
        return {
            "Symbol": ticker,
            "Price": float(price),
            "PriceStr": price_str,
            "Currency": currency,
            "Change": round(float(change), 2),
            "RSI": round(float(rsi), 1),
            "MA50": round(float(ma50), 2),
            "MA200": round(float(ma200), 2),
            "Score": score,
            "InsiderHeld": round(float(insider), 2),
            "TargetUpside": round(float(target_upside), 2),
            "PayoutRatio": round(float(payout), 2),
            "Action": action,
        }
    except Exception:
        return None

def _calc_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

def fetch_master_data(tickers=None, max_workers: int = 3) -> pd.DataFrame:
    """Fetch master data with all columns"""
    if not tickers:
        return pd.DataFrame()
    
    if isinstance(tickers, str):
        tickers = [tickers]
    
    tickers = list(set(tickers))
    
    results = []
    for ticker in tickers:
        try:
            result = _fetch_single_symbol(ticker)
            if result:
                results.append(result)
        except:
            pass
    
    if not results:
        return pd.DataFrame()
    
    return pd.DataFrame(results)
