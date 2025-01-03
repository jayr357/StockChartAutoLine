import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol: str, start_date, end_date, interval: str = "1d") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance with caching

    Interval options:
    - 1m, 2m, 15m: Intraday data with limitations
    - 1d: Daily data
    - 1mo: Monthly data
    - max: Maximum available history
    """
    try:
        # Convert dates to datetime if they're not already
        if not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        if not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())

        # Handle special case for 'max' timeframe
        if interval == 'max':
            interval = '1d'  # Use daily data for maximum history

        # For intraday data, enforce date range limitations
        current_date = datetime.now()
        if interval == '1m':
            # Yahoo finance only provides 7 days of 1-minute data
            max_days = 7
            start_date = max(start_date, current_date - timedelta(days=max_days))
        elif interval in ['2m', '15m']:
            # Limit other intraday data to 60 days
            max_days = 60
            start_date = max(start_date, current_date - timedelta(days=max_days))

        # Ensure end_date is not in the future
        end_date = min(end_date, current_date)

        # Create Ticker object
        stock = yf.Ticker(symbol)

        # Fetch historical data
        df = stock.history(
            start=start_date,
            end=end_date,
            interval=interval,
            prepost=False  # Exclude pre/post market data for consistency
        )

        if df.empty:
            st.warning(f"No data available for {symbol} in the selected date range with {interval} interval.")
            return pd.DataFrame()

        # Reset index to make date a column
        df = df.reset_index()

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