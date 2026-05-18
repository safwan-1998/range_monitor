"""Category Divergence tab — Apollo styled."""

from __future__ import annotations
import pandas as pd
import streamlit as st
from ui import charts, kpi_cards, tables
from ui.tables import FilterDim
from ui.theme import colour_for, section_mark

_FILTER_DIMS = [
    FilterDim("product_category", "Category"),
    FilterDim("branch_area", "Region"),
    FilterDim("insight_type", "Insight"),
]

_PRIORITY = {
    "CATEGORY_DIVERGENCE": 0,
    "MEDIUM_DIVERGENCE": 1,
    "OVER_INDEXING": 2,
    "ALIGNED": 3,
}

_ACTION_BANNERS: list[tuple[str, str, str, str, str]] = [
    (
        "CATEGORY_DIVERGENCE",
        "action-high",
        "📉",
        "Expand in-store range in this category — realign with online demand",
        "This category is trending strongly online but significantly under-ranged in stores. "
        "Increase the number of SKUs, broaden the price ladder, and reset shelf space to match online demand.",
    ),
    (
        "MEDIUM_DIVERGENCE",
        "action-med",
        "🔍",
        "Review category depth — add 2-3 key lines to close the gap",
        "Moderate gap between online category share and in-store range. "
        "Identify the top-performing online SKUs not stocked in-store and trial them selectively.",
    ),
    (
        "OVER_INDEXING",
        "action-low",
        "🏪",
        "Review over-ranged category — consider reducing depth or reallocating space",
        "Stores are carrying more depth in this category than online demand justifies. "
        "Rationalise slower lines and reallocate space to higher-demand categories.",
    ),
    (
        "ALIGNED",
        "action-good",
        "✅",
        "Category well balanced — maintain current range strategy",
        "Online and in-store category mix are well aligned. "
        "No action needed; continue monitoring for drift.",
    ),
]


def _kpis(df: pd.DataFrame) -> list[kpi_cards.KPI]:
    counts = (
        df["insight_type"].value_counts()
        if "insight_type" in df
        else pd.Series(dtype=int)
    )
    return [
        kpi_cards.KPI("Total rows", f"{len(df):,}", "Category × region pairs"),
        kpi_cards.KPI.from_count(
            "Divergent",
            int(counts.get("CATEGORY_DIVERGENCE", 0)),
            "Online trending, store lagging",
            "CATEGORY_DIVERGENCE",
        ),
        kpi_cards.KPI.from_count(
            "Medium divergence",
            int(counts.get("MEDIUM_DIVERGENCE", 0)),
            "Moderate category gap",
            "MEDIUM_DIVERGENCE",
        ),
        kpi_cards.KPI.from_count(
            "Aligned",
            int(counts.get("ALIGNED", 0)),
            "Online = in-store proportion",
            "ALIGNED",
        ),
        kpi_cards.KPI.from_count(
            "Over-indexing",
            int(counts.get("OVER_INDEXING", 0)),
            "Stores over-range vs online",
            "OVER_INDEXING",
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
        st.info("No data for Category Divergence.")
        return
    if summary:
        st.markdown(f'<div class="rm-exec">{summary}</div>', unsafe_allow_html=True)

    section_mark("Category performance vs online")
    kpi_cards.render_strip(_kpis(df))

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    _action_banners(df)

    # ── Table ─────────────────────────────────────────────────────────────────
    section_mark("All categories")
    sorted_df = df.copy()
    sorted_df["_priority"] = sorted_df["insight_type"].map(_PRIORITY).fillna(99)
    sorted_df = sorted_df.sort_values("_priority").drop(columns=["_priority"])
    tables.render(
        sorted_df,
        [
            ("product_category", "Category"),
            ("branch_area", "Region"),
            ("insight_type", "Insight"),
            ("recommended_action", "Action"),
        ],
        title="Category divergence candidates",
        subtitle="Sorted by priority: divergent categories first.",
        top_n=20,
        pill_columns={"insight_type"},
        filter_dims=_FILTER_DIMS,
        tab_key="cd_divs",
    )

    # ── Charts full-width below ───────────────────────────────────────────────
    section_mark("Distribution")
    charts.donut(
        df, "insight_type", "", "Insight breakdown", "By category alignment type"
    )
    charts.grouped_bar_by(
        df,
        "product_category",
        "insight_type",
        "",
        "Divergence by category",
        "Categories with biggest online vs store gap",
    )
    if "branch_area" in df.columns:
        charts.grouped_bar_by(
            df,
            "branch_area",
            "insight_type",
            "",
            "Divergence by region",
            "Regions with most divergent category mix",
            top_n=10,
        )
