"""Stock Imbalance tab — Apollo styled."""

from __future__ import annotations
import pandas as pd
import streamlit as st
from ui import charts, kpi_cards, tables
from ui.tables import FilterDim
from ui.theme import colour_for, section_mark

_FILTER_DIMS = [
    FilterDim("product_category", "Category"),
    FilterDim("branch_area", "Region"),
    FilterDim("location_name", "Location"),
    FilterDim("insight_type", "Insight"),
]

_PRIORITY = {
    "STOCK_OVERSTOCK": 0,
    "STOCK_UNDERSTOCK": 1,
    "NO_PEER_DATA": 2,
    "BALANCED": 3,
}

_ACTION_BANNERS: list[tuple[str, str, str, str, str]] = [
    (
        "STOCK_OVERSTOCK",
        "action-high",
        "📦",
        "Reduce stock — transfer surplus to understocked locations",
        "This location is holding significantly more stock than peer stores for this product. "
        "Arrange inter-store transfers or apply a promotional markdown to clear the excess.",
    ),
    (
        "STOCK_UNDERSTOCK",
        "action-high",
        "⚡",
        "Increase stock urgently — replenish from surplus locations or supplier",
        "This location is holding far less stock than peer stores relative to demand. "
        "Prioritise replenishment; check if stock is available in overstocked locations before ordering.",
    ),
    (
        "NO_PEER_DATA",
        "action-low",
        "📡",
        "No peer comparison available — review stock manually",
        "Insufficient peer location data to benchmark this product's stock level. "
        "Review stock against forecast or historical demand until more peer data is available.",
    ),
    (
        "BALANCED",
        "action-good",
        "✅",
        "Stock well distributed — no rebalancing needed",
        "Stock levels are proportionate across peer locations. "
        "Continue current replenishment strategy and monitor for drift.",
    ),
]


def _kpis(df: pd.DataFrame) -> list[kpi_cards.KPI]:
    counts = (
        df["insight_type"].value_counts()
        if "insight_type" in df
        else pd.Series(dtype=int)
    )
    return [
        kpi_cards.KPI(
            "Total rows", f"{len(df):,}", "Product × location pairs with stock"
        ),
        kpi_cards.KPI.from_count(
            "Overstock",
            int(counts.get("STOCK_OVERSTOCK", 0)),
            "Holding too much vs peers",
            "STOCK_OVERSTOCK",
        ),
        kpi_cards.KPI.from_count(
            "Understock",
            int(counts.get("STOCK_UNDERSTOCK", 0)),
            "Holding too little vs peers",
            "STOCK_UNDERSTOCK",
        ),
        kpi_cards.KPI.from_count(
            "No peer data",
            int(counts.get("NO_PEER_DATA", 0)),
            "Can't compare to peers",
            "NO_PEER_DATA",
        ),
    ]


def _action_banners(df: pd.DataFrame) -> None:
    counts = (
        df["insight_type"].value_counts()
        if "insight_type" in df
        else pd.Series(dtype=int)
    )
    present = {k for k in counts.index if counts[k] > 0}
    if not present:
        return
    st.markdown(
        '<div class="rm-action-group"><div class="rm-action-group-label">Recommended actions by insight type</div>',
        unsafe_allow_html=True,
    )
    for insight, modifier, icon, title, desc in _ACTION_BANNERS:
        if insight not in present:
            continue
        n = int(counts.get(insight, 0))
        c = colour_for(insight)
        pill = (
            f'<span class="rm-pill" style="background:{c["soft"]};color:{c["primary"]};'
            f'border-color:{c["primary"]}40;margin-right:0.5rem">{insight}</span>'
        )
        st.markdown(
            f'<div class="rm-action-banner {modifier}">'
            f'<div class="rm-action-icon">{icon}</div>'
            f'<div class="rm-action-body">'
            f'<div class="rm-action-title">{pill}{title}</div>'
            f'<div class="rm-action-desc">{desc}</div>'
            f"</div>"
            f'<div class="rm-action-count">{n:,} rows</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render(df: pd.DataFrame, summary: str = "") -> None:
    if df.empty:
        st.info("No data for Stock Imbalance.")
        return
    if summary:
        st.markdown(f'<div class="rm-exec">{summary}</div>', unsafe_allow_html=True)

    section_mark("Stock balance vs peer stores")
    kpi_cards.render_strip(_kpis(df))

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    _action_banners(df)

    # ── Table ─────────────────────────────────────────────────────────────────
    section_mark("All products")
    sorted_df = df.copy()
    sorted_df["_priority"] = sorted_df["insight_type"].map(_PRIORITY).fillna(99)
    sorted_df = sorted_df.sort_values("_priority").drop(columns=["_priority"])
    tables.render(
        sorted_df,
        [
            ("product_name", "Product"),
            ("product_category", "Category"),
            ("location_name", "Location"),
            ("insight_type", "Insight"),
            ("recommended_action", "Action"),
        ],
        title="Stock rebalance candidates",
        subtitle="Sorted by priority: overstock and understock first.",
        top_n=20,
        pill_columns={"insight_type"},
        filter_dims=_FILTER_DIMS,
        tab_key="si_imbal",
    )

    # ── Charts full-width below ───────────────────────────────────────────────
    section_mark("Distribution")
    charts.donut(df, "insight_type", "", "Insight breakdown", "By stock balance type")
    charts.grouped_bar_by(
        df,
        "product_category",
        "insight_type",
        "",
        "Imbalances by category",
        "Categories with highest imbalance counts",
    )
    charts.grouped_bar_by(
        df,
        "location_name",
        "insight_type",
        "",
        "Imbalances by location",
        "Stores with most over/understock pairs",
        top_n=12,
    )
