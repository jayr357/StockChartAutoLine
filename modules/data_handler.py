import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol: str, start_date, end_date, interval: str = "1d") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance with caching
    """
    try:
        # Convert dates to datetime if they're not already
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # For intraday data (intervals < 1d), limit the date range
        if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
            # Yahoo finance only provides 7 days of 1-minute data
            max_days = 7 if interval == '1m' else 60
            current_date = datetime.now()
            start_date = max(start_date, current_date - timedelta(days=max_days))

        stock = yf.Ticker(symbol)
        df = stock.history(
            start=start_date,
            end=end_date,
            interval=interval
        )

        if df.empty:
            st.warning(f"No data available for {symbol} in the selected date range.")
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