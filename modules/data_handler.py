import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol: str, start_date, end_date, interval: str = "1d") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance with caching and proper handling of intraday data
    """
    try:
        # Debug logging
        st.write(f"Debug: Fetching {interval} data for {symbol}")
        st.write(f"Debug: Start date: {start_date}, End date: {end_date}")

        # Convert dates to datetime if they're not already
        if not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
            st.write(f"Debug: Converted start_date to {start_date}")
        if not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
            st.write(f"Debug: Converted end_date to {end_date}")

        # Handle special cases
        if interval == 'max':
            interval = '1d'
        elif interval == '3m':
            # For 3min data, we'll fetch 1min data and resample it
            return fetch_and_resample_three_min(symbol, start_date, end_date)

        # For intraday data, enforce date range limitations
        current_date = datetime.now()
        if interval == '1m':
            max_days = 7
            start_date = max(start_date, current_date - timedelta(days=max_days))
            st.write(f"Debug: Adjusted 1m start_date to {start_date}")
        elif interval == '15m':
            max_days = 60
            start_date = max(start_date, current_date - timedelta(days=max_days))
            st.write(f"Debug: Adjusted 15m start_date to {start_date}")

        # Ensure end_date is not in the future
        end_date = min(end_date, current_date)
        st.write(f"Debug: Final date range - Start: {start_date}, End: {end_date}")

        try:
            # Create Ticker object and fetch data
            stock = yf.Ticker(symbol)
            df = stock.history(
                start=start_date,
                end=end_date,
                interval=interval,
                prepost=False
            )

            if df.empty:
                st.warning(f"No data available for {symbol} in the selected date range with {interval} interval.")
                return pd.DataFrame()

            # Reset index to make date a column and ensure proper datetime format
            df = df.reset_index()

            # Debug logging for column names
            st.write(f"Debug: Available columns: {df.columns.tolist()}")

            # Handle different date column names
            date_column = 'Datetime' if 'Datetime' in df.columns else 'Date'
            if date_column in df.columns:
                df['Date'] = pd.to_datetime(df[date_column])
                if date_column == 'Datetime':
                    df = df.drop('Datetime', axis=1)
            else:
                st.error(f"No date column found. Available columns: {df.columns.tolist()}")
                return pd.DataFrame()

            # Verify required columns exist
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_columns):
                missing_cols = [col for col in required_columns if col not in df.columns]
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                return pd.DataFrame()

            return df

        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            st.write(f"Debug: Full error details: {type(e).__name__}: {str(e)}")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error processing dates: {str(e)}")
        st.write(f"Debug: Full error details: {type(e).__name__}: {str(e)}")
        return pd.DataFrame()

def fetch_and_resample_three_min(symbol: str, start_date, end_date) -> pd.DataFrame:
    """
    Custom function to create 3-minute data by resampling 1-minute data
    """
    try:
        st.write(f"Debug: Fetching 1-minute data for 3-minute resampling")

        # Calculate the maximum allowed range for 1-minute data (7 days)
        max_range = timedelta(days=7)
        current_date = datetime.now()

        # Adjust the date range to fetch only the last 7 days of data
        adjusted_start = max(start_date, current_date - max_range)
        adjusted_end = min(end_date, current_date)

        st.write(f"Debug: Adjusted date range for 3min - Start: {adjusted_start}, End: {adjusted_end}")

        # Fetch 1-minute data
        stock = yf.Ticker(symbol)
        df = stock.history(
            start=adjusted_start,
            end=adjusted_end,
            interval='1m',
            prepost=False
        )

        if df.empty:
            st.warning(f"No data available for {symbol} in the selected date range for 3-minute intervals.")
            return pd.DataFrame()

        # Debug logging for column names
        st.write(f"Debug: Available columns before resampling: {df.reset_index().columns.tolist()}")

        # Reset index to make date a column
        df = df.reset_index()
        date_column = 'Datetime' if 'Datetime' in df.columns else 'Date'
        if date_column in df.columns:
            df['Date'] = pd.to_datetime(df[date_column])
            if date_column == 'Datetime':
                df = df.drop('Datetime', axis=1)
        else:
            st.error(f"No date column found for 3min data. Available columns: {df.columns.tolist()}")
            return pd.DataFrame()

        # Resample to 3-minute intervals
        df.set_index('Date', inplace=True)
        resampled = df.resample('3T').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        # Reset index to make date a column again
        resampled = resampled.reset_index()

        # Debug logging for final resampled data
        st.write(f"Debug: Final resampled columns: {resampled.columns.tolist()}")

        return resampled

    except Exception as e:
        st.error(f"Error creating 3-minute data for {symbol}: {str(e)}")
        st.write(f"Debug: Full error details: {type(e).__name__}: {str(e)}")
        return pd.DataFrame()

def cache_data(symbol: str, start_date, end_date, interval: str = "1d") -> pd.DataFrame:
    """
    Wrapper function to handle data caching and preprocessing
    """
    df = fetch_stock_data(symbol, start_date, end_date, interval)

    if not df.empty:
        # Ensure all required columns exist
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Missing required columns in cached data: {', '.join([col for col in required_columns if col not in df.columns])}")
            return pd.DataFrame()

        return df
    return pd.DataFrame()