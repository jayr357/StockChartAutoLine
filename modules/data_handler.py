import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol: str, start_date, end_date, interval: str = "1d") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance with caching
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(
            start=start_date,
            end=end_date,
            interval=interval
        )
        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
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
