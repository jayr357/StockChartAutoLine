import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def calculate_support_resistance(df: pd.DataFrame, window: int = 20):
    """
    Calculate support and resistance levels using local minima/maxima
    """
    df = df.copy()
    
    # Find local minima and maxima
    df['min'] = df.iloc[argrelextrema(df['Low'].values, np.less_equal, order=window)[0]]['Low']
    df['max'] = df.iloc[argrelextrema(df['High'].values, np.greater_equal, order=window)[0]]['High']
    
    # Get significant levels
    support_levels = df['min'].dropna().unique()
    resistance_levels = df['max'].dropna().unique()
    
    # Filter levels to reduce noise
    support_levels = np.percentile(support_levels, np.linspace(0, 100, 3))
    resistance_levels = np.percentile(resistance_levels, np.linspace(0, 100, 3))
    
    return {
        'support': support_levels,
        'resistance': resistance_levels
    }

def calculate_trend(df: pd.DataFrame, window: int = 20):
    """
    Calculate trend indicators
    """
    df = df.copy()
    
    # Calculate moving averages
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    
    # Determine trend
    current_price = df['Close'].iloc[-1]
    sma20 = df['SMA20'].iloc[-1]
    sma50 = df['SMA50'].iloc[-1]
    
    if current_price > sma20 and sma20 > sma50:
        trend = "Uptrend"
    elif current_price < sma20 and sma20 < sma50:
        trend = "Downtrend"
    else:
        trend = "Sideways"
    
    return {
        'trend': trend,
        'sma20': df['SMA20'],
        'sma50': df['SMA50']
    }
