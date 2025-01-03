import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol: str, start_date, end_date, interval: str = "1d") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance with caching

    Interval options:
    - 1m, 3m, 15m: Intraday data with limitations
    - 1d: Daily data
    - 1mo: Monthly data
    - max: Maximum available history
    """
    try:
        # Convert dates to datetime if they're not already
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Handle special case for 'max' timeframe
        if interval == 'max':
            interval = '1d'  # Use daily data for maximum history

        # For intraday data, enforce date range limitations
        if interval == '1m':
            # Yahoo finance only provides 7 days of 1-minute data
            current_date = datetime.now()
            start_date = max(start_date, current_date - timedelta(days=7))
        elif interval in ['3m', '15m']:
            # Limit other intraday data to 60 days
            current_date = datetime.now()
            start_date = max(start_date, current_date - timedelta(days=60))

        # Create Ticker object
        stock = yf.Ticker(symbol)

        # Fetch historical data
        df = stock.history(
            start=start_date,
            end=end_date,
            interval=interval
        )

        if df.empty:
            st.warning(f"No data available for {symbol} in the selected date range with {interval} interval.")
            return pd.DataFrame()

        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

def cache_data(symbol: str, start_date, end_date, interval: str = "1d") -> pd.DataFrame:
    """
    Wrapper function to handle data caching and preprocessing
    """
    df = fetch_stock_data(symbol, start_date, end_date, interval)

    if not df.empty:
        # Reset index to make date a column
        df = df.reset_index()

        # Ensure all required columns exist
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                return pd.DataFrame()

        # Convert date column to datetime if it isn't already
        df['Date'] = pd.to_datetime(df['Date'])

        return df
    return pd.DataFrame()