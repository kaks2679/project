"""
src.visualization.charts
=========================
Reusable Plotly figure builders for Kenya Economic Pulse.
All functions return a plotly.graph_objects.Figure.
Author: Stephen Muema
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express       as px
from plotly.subplots import make_subplots

PALETTE = {
    "primary":    "#3498DB",
    "secondary":  "#27AE60",
    "danger":     "#E74C3C",
    "warning":    "#F39C12",
    "purple":     "#8E44AD",
    "bg":         "#0E1117",
    "card":       "#1C2833",
    "grid":       "#2C3E50",
}

_DARK_LAYOUT = dict(
    plot_bgcolor  = PALETTE["bg"],
    paper_bgcolor = PALETTE["bg"],
    font          = dict(color="white"),
    xaxis         = dict(gridcolor=PALETTE["grid"]),
    yaxis         = dict(gridcolor=PALETTE["grid"]),
)


def time_series_line(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list,
    title: str = "",
    height: int = 420,
) -> go.Figure:
    """Multi-line time series chart."""
    fig = go.Figure()
    colors = [PALETTE["primary"], PALETTE["secondary"], PALETTE["danger"],
              PALETTE["warning"], PALETTE["purple"]]
    for i, col in enumerate(y_cols):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col], y=df[col],
                mode="lines+markers", name=col,
                line=dict(color=colors[i % len(colors)], width=2.5),
                marker=dict(size=5),
            ))
    fig.update_layout(title=title, height=height, hovermode="x unified", **_DARK_LAYOUT)
    return fig


def dual_axis_chart(
    df: pd.DataFrame,
    x_col: str,
    bar_col: str,
    line_col: str,
    bar_label: str = "",
    line_label: str = "",
    title: str = "",
    height: int = 440,
) -> go.Figure:
    """Bar (primary y) + line (secondary y) dual-axis chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=df[x_col], y=df[bar_col],
        name=bar_label or bar_col,
        marker_color=PALETTE["secondary"], opacity=0.7,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[line_col],
        mode="lines+markers", name=line_label or line_col,
        line=dict(color=PALETTE["danger"], width=2.5),
        marker=dict(size=6),
    ), secondary_y=True)
    fig.update_layout(title=title, height=height,
                      hovermode="x unified", **_DARK_LAYOUT)
    return fig


def horizontal_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str = None,
    title: str = "",
    height: int = 400,
) -> go.Figure:
    """Horizontal bar chart, optionally coloured by a categorical column."""
    if color_col and color_col in df.columns:
        fig = px.bar(
            df, x=x_col, y=y_col, color=color_col,
            orientation="h", title=title,
        )
    else:
        fig = go.Figure(go.Bar(
            x=df[x_col], y=df[y_col],
            orientation="h",
            marker_color=PALETTE["primary"],
        ))
    fig.update_layout(title=title, height=height, **_DARK_LAYOUT)
    return fig


def gauge_chart(
    value: float,
    reference: float,
    title: str = "Indicator",
    max_val: float = 100,
    height: int = 300,
) -> go.Figure:
    """Gauge / indicator chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={"reference": reference,
               "increasing": {"color": PALETTE["danger"]},
               "decreasing": {"color": PALETTE["secondary"]}},
        number={"suffix": "%", "font": {"color": "white", "size": 34}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "white",
                     "tickfont": {"color": "white"}},
            "bar":  {"color": PALETTE["primary"]},
            "bgcolor": PALETTE["card"],
            "steps": [
                {"range": [0, max_val * 0.25], "color": "#1E8449"},
                {"range": [max_val * 0.25, max_val * 0.5], "color": "#F39C12"},
                {"range": [max_val * 0.5, max_val * 0.75], "color": "#E67E22"},
                {"range": [max_val * 0.75, max_val],        "color": "#E74C3C"},
            ],
        },
        title={"text": title, "font": {"color": "white", "size": 13}},
    ))
    fig.update_layout(height=height, **_DARK_LAYOUT)
    return fig


def scatter_bubble(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: str = None,
    color_col: str = None,
    hover_name: str = None,
    title: str = "",
    height: int = 440,
) -> go.Figure:
    """Bubble scatter chart using Plotly Express."""
    fig = px.scatter(
        df, x=x_col, y=y_col,
        size=size_col,
        color=color_col,
        hover_name=hover_name,
        trendline="ols",
        title=title,
    )
    fig.update_layout(height=height, **_DARK_LAYOUT)
    return fig
