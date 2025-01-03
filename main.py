import streamlit as st
from modules.data_handler import fetch_stock_data, cache_data
from modules.technical_analysis import calculate_support_resistance, calculate_trend
from modules.visualization import create_price_chart
from modules.utils import setup_page
import datetime

def main():
    setup_page()

    # Sidebar inputs
    st.sidebar.title("Settings")
    symbol = st.sidebar.text_input("Stock Symbol", value="AAPL").upper()

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365)

    # Updated timeframe selection with more options
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ["1m", "3m", "15m", "1d", "1mo", "max"],
        index=3,
        help="1m = 1 Minute (last 7 days)\n"
             "3m = 3 Minutes (last 60 days)\n"
             "15m = 15 Minutes (last 60 days)\n"
             "1d = Daily\n"
             "1mo = Monthly\n"
             "max = Maximum available history"
    )

    # Adjust date picker based on timeframe
    if timeframe in ['1m']:
        # For 1-minute data, limit to last 7 days
        min_date = end_date - datetime.timedelta(days=7)
        start_date = max(start_date, min_date)
    elif timeframe in ['3m', '15m']:
        # For intraday data, limit to last 60 days
        min_date = end_date - datetime.timedelta(days=60)
        start_date = max(start_date, min_date)

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(start_date, end_date),
        min_value=start_date if timeframe in ['1m', '3m', '15m'] else None,
        max_value=end_date
    )

    # Main content
    st.title("Stock Technical Analysis")

    if len(date_range) == 2:
        start_date, end_date = date_range

        # Fetch and cache data
        with st.spinner("Fetching stock data..."):
            df = cache_data(symbol, start_date, end_date, timeframe)

        if df is not None and not df.empty:
            # Calculate technical indicators
            support_resistance = calculate_support_resistance(df)
            trend_data = calculate_trend(df)

            # Create main price chart
            fig = create_price_chart(
                df,
                symbol,
                support_resistance,
                trend_data
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display additional metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Current Price",
                    f"${df['Close'].iloc[-1]:.2f}",
                    f"{((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100:.2f}%"
                )
            with col2:
                st.metric(
                    "Volume",
                    f"{df['Volume'].iloc[-1]:,.0f}"
                )
            with col3:
                st.metric(
                    "Trend",
                    trend_data['trend']
                )
        else:
            st.error(f"Unable to fetch data for {symbol}. Please verify the symbol and try again.")

if __name__ == "__main__":
    main()