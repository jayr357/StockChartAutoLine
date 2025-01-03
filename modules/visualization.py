import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_price_chart(df, symbol, support_resistance, trend_data):
    """
    Create an interactive price chart with technical indicators
    """
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} Price', 'Volume'),
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
            y=trend_data['sma20'],
            name='SMA20',
            line=dict(color='blue', width=1)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=trend_data['sma50'],
            name='SMA50',
            line=dict(color='orange', width=1)
        ),
        row=1,
        col=1
    )

    # Add support lines
    for level in support_resistance['support']:
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color="green",
            opacity=0.5,
            row=1,
            col=1
        )

    # Add resistance lines
    for level in support_resistance['resistance']:
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color="red",
            opacity=0.5,
            row=1,
            col=1
        )

    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume'
        ),
        row=2,
        col=1
    )

    # Update layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        title_text=f"{symbol} Technical Analysis",
        yaxis_title="Price",
        yaxis2_title="Volume"
    )

    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    
    return fig
