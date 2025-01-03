import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_price_chart(df, symbol, support_resistance, trend_data, timeframe="1d", 
                      chart_height=900, price_volume_ratio=0.7, vertical_spacing=0.1,
                      grid_style={'color': '#483C32', 'width': 1, 'dash': 'dot'}):
    """
    Create an interactive price chart with technical indicators and configurable layout

    Parameters:
    - chart_height: Overall chart height in pixels
    - price_volume_ratio: Ratio of price chart to volume chart (0.5-0.9)
    - vertical_spacing: Spacing between subplots (0.05-0.2)
    - grid_style: Dictionary with grid styling options
    """
    # Validate and adjust input parameters
    chart_height = max(600, min(1500, chart_height))  # Limit height between 600-1500px
    price_volume_ratio = max(0.5, min(0.9, price_volume_ratio))  # Limit ratio between 0.5-0.9
    volume_ratio = 1 - price_volume_ratio
    vertical_spacing = max(0.05, min(0.2, vertical_spacing))  # Limit spacing between 0.05-0.2

    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=vertical_spacing,
        subplot_titles=(f'{symbol} Price ({timeframe})', 'Volume'),
        row_width=[price_volume_ratio, volume_ratio]
    )

    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color='#B87333',  # Copper color for up moves
            decreasing_line_color='#8B4513',  # Saddle brown for down moves
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
            line=dict(color='#DAA520', width=1)  # Golden rod color
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=trend_data['sma_slow'],
            name='Slow MA',
            line=dict(color='#CD853F', width=1)  # Peru color
        ),
        row=1,
        col=1
    )

    # Add support lines with labels
    for i, level in enumerate(support_resistance['support']):
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color="#228B22",  # Forest green
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
            line_color="#8B0000",  # Dark red
            opacity=0.5,
            row=1,
            col=1,
            annotation_text=f"Resistance {i+1}",
            annotation_position="left"
        )

    # Add volume bars with steampunk colors
    colors = ['#8B4513' if close < open else '#B87333' for close, open in zip(df['Close'], df['Open'])]
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
                y=trend_data['volatility'] * df['Volume'].mean(),
                name='Volatility',
                line=dict(color='#9370DB', width=1)  # Medium purple
            ),
            row=2,
            col=1
        )

    # Update layout with steampunk theme
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=chart_height,
        showlegend=True,
        title_text=f"{symbol} Technical Analysis ({timeframe})",
        title_x=0.5,
        yaxis_title="Price",
        yaxis2_title="Volume",
        margin=dict(t=100, b=50),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(50, 45, 40, 0.8)',  # Steampunk background
            bordercolor='#B87333',  # Copper border
            borderwidth=2
        ),
        paper_bgcolor='rgba(40, 35, 30, 0.9)',  # Dark steampunk background
        plot_bgcolor='rgba(45, 40, 35, 0.9)',   # Slightly lighter for plot
        font=dict(
            family="Copperplate Gothic, Georgia, serif",
            color="#D4AF37"  # Gold text
        )
    )

    # Update axes with steampunk grid style
    fig.update_xaxes(
        showgrid=True,
        gridwidth=grid_style['width'],
        gridcolor=grid_style['color'],
        griddash=grid_style.get('dash', 'solid'),
        linecolor='#B87333',  # Copper color for axis lines
        tickfont=dict(family="Copperplate Gothic")
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=grid_style['width'],
        gridcolor=grid_style['color'],
        griddash=grid_style.get('dash', 'solid'),
        linecolor='#B87333',  # Copper color for axis lines
        tickfont=dict(family="Copperplate Gothic")
    )

    return fig