import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_price_chart(df, symbol, support_resistance, trend_data, timeframe="1d"):
    """
    Create an interactive price chart with technical indicators
    Enhanced for different timeframes
    """
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} Price ({timeframe})', 'Volume'),
        row_width=[0.7, 0.3]
    )

    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1,
        col=1
    )

    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=trend_data['sma_fast'],
            name='Fast MA',
            line=dict(color='blue', width=1)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=trend_data['sma_slow'],
            name='Slow MA',
            line=dict(color='orange', width=1)
        ),
        row=1,
        col=1
    )

    # Add support lines with labels
    for i, level in enumerate(support_resistance['support']):
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color="green",
            opacity=0.5,
            row=1,
            col=1,
            annotation_text=f"Support {i+1}",
            annotation_position="left"
        )

    # Add resistance lines with labels
    for i, level in enumerate(support_resistance['resistance']):
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color="red",
            opacity=0.5,
            row=1,
            col=1,
            annotation_text=f"Resistance {i+1}",
            annotation_position="left"
        )

    # Add volume bars with color based on price change
    colors = ['red' if close < open else 'green' for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2,
        col=1
    )

    # Add volatility as a line on volume subplot
    if 'volatility' in trend_data:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=trend_data['volatility'] * df['Volume'].mean(),  # Scale volatility to volume scale
                name='Volatility',
                line=dict(color='purple', width=1)
            ),
            row=2,
            col=1
        )

    # Update layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        title_text=f"{symbol} Technical Analysis ({timeframe})",
        yaxis_title="Price",
        yaxis2_title="Volume"
    )

    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')

    return fig