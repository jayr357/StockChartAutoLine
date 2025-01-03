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

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(start_date, end_date),
        max_value=end_date
    )

    # Updated timeframe options to match yfinance supported intervals
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ["1d", "1h", "5m"],
        index=0,
        help="1d = Daily, 1h = Hourly, 5m = 5 Minutes"
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