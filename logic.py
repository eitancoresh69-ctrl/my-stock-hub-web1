# logic.py - TRULY FINAL - WITH ALL COLUMNS TRADERS NEED
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
    """Fetch ALL columns that traders expect"""
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
        volume = int(hist["Volume"].iloc[-1]) if len(hist) > 0 else 0
        
        # Calculate ALL indicators
        rsi = _calc_rsi(close)
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        change = ((close.iloc[-1] / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
        
        # Financial metrics
        currency = "ILS" if str(ticker).endswith(".TA") else "USD"
        price_str = f"{currency}{price:,.2f}"
        
        insider = float(info.get("heldPercentInsiders", 0)) * 100
        target_price = float(info.get("targetMeanPrice", price))
        target_upside = ((target_price / price) - 1) * 100 if price > 0 else 0
        payout = float(info.get("payoutRatio", 0)) * 100
        
        # MORE columns traders need
        div_yield = float(info.get("dividendYield", 0)) * 100 if info.get("dividendYield") else 0
        margin = float(info.get("profitMargins", 0)) * 100 if info.get("profitMargins") else 0
        roe = float(info.get("returnOnEquity", 0)) * 100 if info.get("returnOnEquity") else 0
        earn_growth = float(info.get("earningsGrowth", 0)) * 100 if info.get("earningsGrowth") else 0
        rev_growth = float(info.get("revenueGrowth", 0)) * 100 if info.get("revenueGrowth") else 0
        
        cash = float(info.get("totalCash", 0)) if info.get("totalCash") else 0
        debt = float(info.get("totalDebt", 0)) if info.get("totalDebt") else 0
        cash_vs_debt = "OK" if cash > debt else "Risk"
        
        # Calculate scores
        score = 0
        if rev_growth >= 10: score += 1
        if earn_growth >= 10: score += 1
        if margin >= 10: score += 1
        if roe >= 15: score += 1
        if cash > debt: score += 1
        
        short_score = 0
        if rsi < 35: short_score += 3
        elif rsi < 45: short_score += 2
        if change < -8: short_score += 2
        elif change < -4: short_score += 1
        if target_upside > 15: short_score += 2
        if rev_growth > 15: short_score += 1
        if volume > 1000000: short_score += 1
        
        long_score = score
        if rev_growth >= 20: long_score += 2
        elif rev_growth >= 10: long_score += 1
        if earn_growth >= 20: long_score += 2
        elif earn_growth >= 10: long_score += 1
        if target_upside > 20: long_score += 2
        elif target_upside > 10: long_score += 1
        if div_yield > 2 and payout < 60 and cash > debt: long_score += 2
        if insider >= 5: long_score += 1
        
        action = "Strong Buy" if long_score >= 10 else "Buy" if long_score >= 7 else "Hold" if long_score >= 4 else "Analyze"
        
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
            "DivYield": round(float(div_yield), 2),
            "Volume": volume,
            "Margin": round(float(margin), 2),
            "ROE": round(float(roe), 2),
            "EarnGrowth": round(float(earn_growth), 2),
            "RevGrowth": round(float(rev_growth), 2),
            "CashVsDebt": cash_vs_debt,
            "ShortScore": short_score,
            "LongScore": long_score,
            "Action": action,
        }
    except Exception as e:
        return None

def _calc_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1]) if not rsi.iloc[-1] is np.nan else 50.0

def fetch_master_data(tickers=None, max_workers: int = 3) -> pd.DataFrame:
    """Fetch master data with ALL columns"""
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
