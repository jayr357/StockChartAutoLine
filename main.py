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

    # Calculate default dates
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365)

    # Chart configuration options
    st.sidebar.subheader("Chart Settings")
    chart_height = st.sidebar.slider("Chart Height", 600, 1500, 900, 50)
    price_volume_ratio = st.sidebar.slider("Price/Volume Ratio", 0.5, 0.9, 0.7, 0.1)
    vertical_spacing = st.sidebar.slider("Chart Spacing", 0.05, 0.2, 0.1, 0.01)

    # Grid style options
    grid_color = st.sidebar.color_picker("Grid Color", "#483C32")
    grid_width = st.sidebar.slider("Grid Width", 1, 3, 1)
    grid_style = st.sidebar.selectbox("Grid Style", ["solid", "dot", "dash", "longdash"], index=1)

    grid_config = {
        'color': grid_color,
        'width': grid_width,
        'dash': grid_style
    }

    # Updated timeframe selection with supported intervals
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
    if timeframe == '1m':
        # For 1-minute data, limit to last 7 days
        min_date = end_date - datetime.timedelta(days=7)
        start_date = max(start_date, min_date)
    elif timeframe in ['3m', '15m']:
        # For intraday data, limit to last 60 days
        min_date = end_date - datetime.timedelta(days=60)
        start_date = max(start_date, min_date)

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(start_date.date(), end_date.date()),
        min_value=start_date.date() if timeframe in ['1m', '3m', '15m'] else None,
        max_value=end_date.date()
    )

    # Main content
    st.title("Stock Technical Analysis")

    if len(date_range) == 2:
        start_date, end_date = date_range
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(end_date, datetime.datetime.max.time())

        # Fetch and cache data
        with st.spinner("Fetching stock data..."):
            df = cache_data(symbol, start_date, end_date, timeframe)

        if df is not None and not df.empty:
            # Calculate technical indicators with timeframe parameter
            support_resistance = calculate_support_resistance(df, timeframe)
            trend_data = calculate_trend(df, timeframe)

            # Create main price chart with user configuration
            fig = create_price_chart(
                df,
                symbol,
                support_resistance,
                trend_data,
                timeframe,
                chart_height=chart_height,
                price_volume_ratio=price_volume_ratio,
                vertical_spacing=vertical_spacing,
                grid_style=grid_config
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display additional metrics
            col1, col2, col3, col4 = st.columns(4)
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
            with col4:
                if 'volatility' in trend_data:
                    st.metric(
                        "Volatility",
                        f"{trend_data['volatility'].iloc[-1]*100:.2f}%"
                    )
        else:
            st.error(f"Unable to fetch data for {symbol}. Please verify the symbol and try again.")

if __name__ == "__main__":
    main()