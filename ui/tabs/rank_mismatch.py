"""Rank Mismatch tab — Apollo styled."""

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
    "RANGE_GAP": 0,
    "MEDIUM_RANGE_GAP": 1,
    "LOW_RANGE_GAP": 2,
    "NO_ONLINE_SIGNAL": 3,
    "BALANCED": 4,
}

_ACTION_BANNERS: list[tuple[str, str, str, str, str]] = [
    (
        "RANGE_GAP",
        "action-high",
        "🚨",
        "Step-change store depth — reset shelf and window planogram",
        "Ranked highly online but poorly stocked in-store. "
        "Urgently increase depth, reset shelf space, and align the store planogram with online demand.",
    ),
    (
        "MEDIUM_RANGE_GAP",
        "action-med",
        "📈",
        "Increase store allocation and facings; widen size curve",
        "Moderate gap between online rank and in-store availability. "
        "Expand allocation and broaden the size curve to better match customer demand.",
    ),
    (
        "LOW_RANGE_GAP",
        "action-low",
        "↕️",
        "Nudge min display depth; test end-cap or cross-sell bundle",
        "Small rank gap — low urgency but worth a marginal improvement. "
        "Trial an end-cap position or cross-sell to surface the product better.",
    ),
    (
        "NO_ONLINE_SIGNAL",
        "action-low",
        "📡",
        "No online benchmark available — monitor manually",
        "Product has no online sales signal, so rank comparison is not possible. "
        "Check if the product is listed online and why it has no demand signal.",
    ),
    (
        "BALANCED",
        "action-good",
        "✅",
        "Maintain current strategy — balanced online and in-store profile",
        "Online rank and in-store availability are well aligned. "
        "No action needed; continue current stocking strategy.",
    ),
]


def _kpis(df: pd.DataFrame) -> list[kpi_cards.KPI]:
    counts = (
        df["insight_type"].value_counts()
        if "insight_type" in df
        else pd.Series(dtype=int)
    )
    return [
        kpi_cards.KPI("Total rows", f"{len(df):,}", "Product × location pairs"),
        kpi_cards.KPI.from_count(
            "Range gaps",
            int(counts.get("RANGE_GAP", 0)),
            "High-demand, low in-store",
            "RANGE_GAP",
        ),
        kpi_cards.KPI.from_count(
            "Medium gaps",
            int(counts.get("MEDIUM_RANGE_GAP", 0)),
            "Moderate rank mismatch",
            "MEDIUM_RANGE_GAP",
        ),
        kpi_cards.KPI.from_count(
            "No online signal",
            int(counts.get("NO_ONLINE_SIGNAL", 0)),
            "Missing online baseline",
            "NO_ONLINE_SIGNAL",
        ),
        kpi_cards.KPI.from_count(
            "Balanced", int(counts.get("BALANCED", 0)), "Online = in-store", "BALANCED"
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
        st.info("No data for Rank Mismatch.")
        return
    if summary:
        st.markdown(f'<div class="rm-exec">{summary}</div>', unsafe_allow_html=True)

    section_mark("Online vs in-store rank")
    kpi_cards.render_strip(_kpis(df))

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    _action_banners(df)

    # ── Table ─────────────────────────────────────────────────────────────────
    section_mark("All range gaps")
    sorted_df = df.copy()
    sorted_df["_priority"] = sorted_df["insight_type"].map(_PRIORITY).fillna(99)
    if "percentile_gap" in sorted_df.columns:
        sorted_df = sorted_df.sort_values(
            ["_priority", "percentile_gap"], ascending=[True, False]
        )
    else:
        sorted_df = sorted_df.sort_values("_priority")
    sorted_df = sorted_df.drop(columns=["_priority"])
    tables.render(
        sorted_df,
        [
            ("product_name", "Product"),
            ("product_category", "Category"),
            ("location_name", "Location"),
            ("online_rank_label", "Online Rank"),
            ("store_rank_label", "Store Rank"),
            ("insight_type", "Insight"),
            ("recommended_action", "Action"),
        ],
        title="Range gap candidates",
        subtitle="Sorted by priority: largest gaps first.",
        top_n=20,
        pill_columns={"insight_type"},
        filter_dims=_FILTER_DIMS,
        tab_key="rm_gaps",
    )

    # ── Charts ────────────────────────────────────────────────────────────────
    section_mark("Distribution")
    charts.donut(df, "insight_type", "", "Insight breakdown", "By rank gap category")
    charts.grouped_bar_by(
        df,
        "product_category",
        "insight_type",
        "",
        "Gaps by category",
        "Top categories by gap count",
    )
    charts.grouped_bar_by(
        df,
        "location_name",
        "insight_type",
        "",
        "Gaps by location",
        "Stores with highest rank mismatches",
        top_n=12,
    )
