"""Plotly chart helpers — Apollo palette."""

from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ui.theme import PALETTE, colour_for

# ── Shared style constants (explicit hex — Plotly cannot default to white) ────
_BG = "#ffffff"
_GRID = "#e5e9ed"
_BORDER = "#c9d1d9"
_TEXT = "#526069"  # foreground-muted
_TEXT_DARK = "#182027"  # foreground-emp
_LEGEND_BG = "#f4f5f7"

_FONT = dict(
    family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=_TEXT, size=12
)
_TICK_FONT = dict(family="'Inconsolata', monospace", size=11, color=_TEXT)
_TICK_FONT_SM = dict(family="'Inconsolata', monospace", size=10, color=_TEXT)

_XAXIS = dict(
    gridcolor=_GRID,
    gridwidth=0.5,
    zerolinecolor=_BORDER,
    showline=True,
    linecolor=_BORDER,
    tickfont=_TICK_FONT,
    automargin=True,
)
_YAXIS = dict(
    gridcolor=_GRID,
    gridwidth=0.5,
    zerolinecolor=_BORDER,
    showline=False,
    tickfont=_TICK_FONT,
)
_COLORWAY = [
    PALETTE["brand"],
    PALETTE["success"],
    PALETTE["warning"],
    PALETTE["error"],
    PALETTE["neutral"],
    PALETTE["foreground_muted"],
]


def _chart_card(title: str, subtitle: str, fig: go.Figure) -> None:
    st.markdown(
        f'<div class="rm-chart-card">'
        f'<div class="rm-chart-title">{title}</div>'
        f'<div class="rm-chart-subtitle">{subtitle}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def donut(
    df: pd.DataFrame, column: str, eyebrow: str, title: str, subtitle: str
) -> None:
    if df.empty or column not in df.columns:
        st.info("No data.")
        return
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, "count"]
    colours = [colour_for(v)["primary"] for v in counts[column]]

    fig = go.Figure(
        go.Pie(
            labels=counts[column],
            values=counts["count"],
            hole=0.55,
            marker=dict(colors=colours, line=dict(color="#ffffff", width=2)),
            textinfo="percent",
            textposition="inside",
            textfont=dict(size=11, color="#ffffff"),
            insidetextorientation="radial",
        )
    )
    # Build layout fully inline — no **spread to avoid duplicate-key errors
    fig.update_layout(
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=_FONT,
        colorway=_COLORWAY,
        showlegend=True,
        legend=dict(
            bgcolor=_LEGEND_BG,
            bordercolor=_BORDER,
            borderwidth=1,
            font=dict(size=11, color=_TEXT_DARK),
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
        ),
        margin=dict(l=8, r=150, t=16, b=8),
        height=280,
    )
    _chart_card(title, subtitle, fig)


def grouped_bar_by(
    df: pd.DataFrame,
    x_col: str,
    group_col: str,
    eyebrow: str,
    title: str,
    subtitle: str,
    top_n: int = 12,
) -> None:
    if df.empty or x_col not in df.columns:
        st.info("No data.")
        return
    top_x = df[x_col].value_counts().head(top_n).index
    sub = df[df[x_col].isin(top_x)].copy()
    pivot = sub.groupby([x_col, group_col]).size().reset_index(name="count")
    groups = pivot[group_col].unique()
    colours = {g: colour_for(g)["primary"] for g in groups}

    fig = go.Figure()
    for g in groups:
        d = pivot[pivot[group_col] == g]
        fig.add_trace(
            go.Bar(
                name=g,
                x=d[x_col],
                y=d["count"],
                marker_color=colours.get(g, PALETTE["neutral"]),
                marker_line_width=0,
            )
        )

    tick_angle = -40 if len(top_x) > 6 else 0
    # Build layout fully inline — no **spread to avoid duplicate-key errors
    fig.update_layout(
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=_FONT,
        colorway=_COLORWAY,
        barmode="stack",
        bargap=0.25,
        height=320,
        margin=dict(l=32, r=32, t=16, b=90),
        xaxis=dict(
            gridcolor=_GRID,
            gridwidth=0.5,
            zerolinecolor=_BORDER,
            showline=True,
            linecolor=_BORDER,
            automargin=True,
            tickangle=tick_angle,
            tickfont=_TICK_FONT_SM,
        ),
        yaxis=_YAXIS,
        legend=dict(
            bgcolor=_LEGEND_BG,
            bordercolor=_BORDER,
            borderwidth=1,
            font=dict(size=11, color=_TEXT_DARK),
            orientation="h",
            yanchor="bottom",
            y=-0.45,
            xanchor="left",
            x=0,
        ),
    )
    _chart_card(title, subtitle, fig)
