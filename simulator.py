# simulator.py - FIXED - No unicode arrows
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from storage import load, save

try:
    from logic import fetch_master_data
    HAS_LOGIC = True
except:
    HAS_LOGIC = False

def run_simulator():
    """Stock trading simulator"""
    st.markdown("## Trading Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input("Initial Capital ($)", value=100000, min_value=1000)
    
    with col2:
        mode = st.selectbox("Mode", ["Buy & Hold", "Active Trading", "Swing Trading"])
    
    if st.button("Start Simulation"):
        st.info("Starting simulation...")
        
        # Get data
        if not HAS_LOGIC:
            st.error("Logic module not available")
            return
        
        tickers = ["AAPL", "MSFT", "GOOGL"]
        df = fetch_master_data(tickers)
        
        if df.empty:
            st.warning("No data available")
            return
        
        # Simple simulator
        portfolio = []
        cash = initial_capital
        
        for idx, row in df.iterrows():
            symbol = row['Symbol']
            price = row['Price']
            
            if cash > price * 10:
                portfolio.append({
                    "Symbol": symbol,
                    "Shares": 10,
                    "BuyPrice": price,
                    "CurrentPrice": price
                })
                cash -= price * 10
        
        # Display results
        st.success(f"Portfolio created with {len(portfolio)} stocks")
        st.metric("Remaining Cash", f"${cash:,.2f}")
        
        if portfolio:
            st.dataframe(pd.DataFrame(portfolio))

if __name__ != "__main__":
    run_simulator()
