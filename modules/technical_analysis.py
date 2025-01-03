import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def calculate_support_resistance(df: pd.DataFrame, timeframe: str = "1d"):
    """
    Calculate support and resistance levels using local minima/maxima
    Adjusted for different timeframes
    """
    df = df.copy()

    # Adjust window size based on timeframe
    if timeframe == "1m":
        window = 10  # Smaller window for 1-minute data
    elif timeframe in ["3m", "15m"]:
        window = 15  # Medium window for other intraday data
    else:
        window = 20  # Larger window for daily and above

    # Find local minima and maxima
    df['min'] = df.iloc[argrelextrema(df['Low'].values, np.less_equal, order=window)[0]]['Low']
    df['max'] = df.iloc[argrelextrema(df['High'].values, np.greater_equal, order=window)[0]]['High']

    # Get significant levels
    support_levels = df['min'].dropna().unique()
    resistance_levels = df['max'].dropna().unique()

    # Adjust number of levels based on timeframe
    num_levels = 5 if timeframe in ["1m", "3m", "15m"] else 3

    # Filter levels to reduce noise
    if len(support_levels) > num_levels:
        support_levels = np.percentile(support_levels, np.linspace(0, 100, num_levels))
    if len(resistance_levels) > num_levels:
        resistance_levels = np.percentile(resistance_levels, np.linspace(0, 100, num_levels))

    return {
        'support': support_levels,
        'resistance': resistance_levels
    }

def calculate_trend(df: pd.DataFrame, timeframe: str = "1d"):
    """
    Calculate trend indicators with timeframe-specific adjustments
    """
    df = df.copy()

    # Adjust moving average periods based on timeframe
    if timeframe == "1m":
        fast_ma = 5
        slow_ma = 15
    elif timeframe in ["3m", "15m"]:
        fast_ma = 10
        slow_ma = 30
    else:
        fast_ma = 20
        slow_ma = 50

    # Calculate moving averages
    df['SMA_fast'] = df['Close'].rolling(window=fast_ma).mean()
    df['SMA_slow'] = df['Close'].rolling(window=slow_ma).mean()

    # Calculate additional trend indicators
    df['Price_Change'] = df['Close'].pct_change()
    df['Volatility'] = df['Price_Change'].rolling(window=fast_ma).std()

    # Determine trend
    current_price = df['Close'].iloc[-1]
    sma_fast = df['SMA_fast'].iloc[-1]
    sma_slow = df['SMA_slow'].iloc[-1]
    volatility = df['Volatility'].iloc[-1]

    if current_price > sma_fast and sma_fast > sma_slow:
        trend = "Strong Uptrend" if volatility > df['Volatility'].mean() else "Uptrend"
    elif current_price < sma_fast and sma_fast < sma_slow:
        trend = "Strong Downtrend" if volatility > df['Volatility'].mean() else "Downtrend"
    else:
        trend = "High Volatility Sideways" if volatility > df['Volatility'].mean() else "Sideways"

    return {
        'trend': trend,
        'sma_fast': df['SMA_fast'],
        'sma_slow': df['SMA_slow'],
        'volatility': df['Volatility']
    }