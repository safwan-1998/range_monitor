"""Slow Mover tab — Apollo styled."""

from __future__ import annotations
import pandas as pd
import streamlit as st
from ui import charts, kpi_cards, tables
from ui.tables import FilterDim
from ui.theme import colour_for, section_mark

# Region intentionally excluded — not useful for slow-mover triage
_FILTER_DIMS = [
    FilterDim("product_category", "Category"),
    FilterDim("location_name", "Location"),
    FilterDim("insight_type", "Insight"),
]

# Priority sort order for the merged table
_PRIORITY = {
    "STORE_ISSUE": 0,
    "DEAD_STOCK": 1,
    "SLOW_MOVER": 2,
    "MEDIUM_MOVEMENT": 3,
    "FAST_MOVER": 4,
}

# Action banner config: insight_type -> (css_modifier, icon, title, description)
_ACTION_BANNERS: list[tuple[str, str, str, str, str]] = [
    (
        "STORE_ISSUE",
        "action-high",
        "📦",
        "Increase stock & improve in-store visibility",
        "These products sell well online but underperform in stores. "
        "Expand allocation, improve shelf placement, or trial in additional locations.",
    ),
    (
        "DEAD_STOCK",
        "action-high",
        "⚠️",
        "Reduce stock — apply markdown or consider discontinuation",
        "Zero or near-zero sell-through in stores with no online signal. "
        "Prioritise clearance; avoid replenishment until signal recovers.",
    ),
    (
        "SLOW_MOVER",
        "action-med",
        "🐢",
        "Reduce depth & monitor closely",
        "Below-threshold sell-through across all channels. "
        "Cut reorder quantities; consider promotional activity to shift existing stock.",
    ),
    (
        "MEDIUM_MOVEMENT",
        "action-low",
        "📊",
        "Monitor performance — optimise stock levels",
        "Mid-range sell-through. No immediate action required but worth watching "
        "for deterioration. Review again after next trade period.",
    ),
    (
        "FAST_MOVER",
        "action-good",
        "🚀",
        "Maintain or increase stock allocation",
        "Strong sell-through in stores. Ensure sufficient depth to avoid lost sales; "
        "consider expanding to additional locations.",
    ),
]


def _kpis(df: pd.DataFrame) -> list[kpi_cards.KPI]:
    counts = (
        df["insight_type"].value_counts()
        if "insight_type" in df
        else pd.Series(dtype=int)
    )
    return [
        kpi_cards.KPI("Total analysed", f"{len(df):,}", "Store-product pairs"),
        kpi_cards.KPI.from_count(
            "Store issues",
            int(counts.get("STORE_ISSUE", 0)),
            "Strong online · weak in-store",
            "STORE_ISSUE",
        ),
        kpi_cards.KPI.from_count(
            "Dead stock",
            int(counts.get("DEAD_STOCK", 0)),
            "Inventory at risk",
            "DEAD_STOCK",
        ),
        kpi_cards.KPI.from_count(
            "Slow movers",
            int(counts.get("SLOW_MOVER", 0)),
            "Cold everywhere",
            "SLOW_MOVER",
        ),
        kpi_cards.KPI.from_count(
            "Fast movers",
            int(counts.get("FAST_MOVER", 0)),
            "Maintain or expand",
            "FAST_MOVER",
        ),
    ]


def _str_pct(val: object) -> str:
    """Format a 0–1 STR decimal as a percentage string."""
    try:
        return f"{float(val):.0%}"  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "—"


def _action_banners(df: pd.DataFrame) -> None:
    """Render one action banner per insight type that has rows."""
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
        st.info("No data for Slow Mover.")
        return
    if summary:
        st.markdown(f'<div class="rm-exec">{summary}</div>', unsafe_allow_html=True)

    section_mark("Movement across the range")
    kpi_cards.render_strip(_kpis(df))

    # ── Action banners ────────────────────────────────────────────────────────
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    _action_banners(df)

    # ── Single merged table (all insight types, priority sorted) ─────────────
    section_mark("All products")
    merged = df.copy()
    merged["_priority"] = merged["insight_type"].map(_PRIORITY).fillna(99)
    merged = merged.sort_values(
        ["_priority", "store_str"], ascending=[True, True]
    ).drop(columns=["_priority"])

    # Format STR columns for display
    merged["store_str_pct"] = merged["store_str"].apply(_str_pct)
    merged["online_str_pct"] = merged["online_str"].apply(_str_pct)

    tables.render(
        merged,
        [
            ("product_name", "Product"),
            ("product_category", "Category"),
            ("location_name", "Location"),
            ("insight_type", "Insight"),
            ("store_str_pct", "Store STR"),
            ("online_str_pct", "Online STR"),
            ("recommended_action", "Action"),
        ],
        title="All store-product pairs",
        subtitle="Sorted by priority: store issues and dead stock first, fast movers last.",
        top_n=25,
        pill_columns={"insight_type"},
        filter_dims=_FILTER_DIMS,
        tab_key="sm_all",
    )

    # ── Charts full-width below ───────────────────────────────────────────────
    section_mark("Distribution")
    charts.donut(
        df, "insight_type", "", "Insight breakdown", "By movement classification"
    )
    charts.grouped_bar_by(
        df,
        "product_category",
        "insight_type",
        "",
        "Insights by category",
        "Top categories by flagged count",
    )
    charts.grouped_bar_by(
        df,
        "location_name",
        "insight_type",
        "",
        "Insights by location",
        "Stores ordered by flagged count",
        top_n=12,
    )
