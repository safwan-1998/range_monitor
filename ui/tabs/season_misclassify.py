"""Season Misclassify tab — Apollo styled."""

from __future__ import annotations
import pandas as pd
import streamlit as st
from ui import charts, kpi_cards, tables
from ui.tables import FilterDim
from ui.theme import colour_for, section_mark

_FILTER_DIMS = [
    FilterDim("product_category", "Category"),
    FilterDim("product_season", "Season"),
    FilterDim("insight_type", "Insight"),
]

_PRIORITY = {"SEASON_MISMATCH": 0, "MID_MISMATCH": 1, "NO_SIGNAL": 2, "SEASONAL_OK": 3}

_ACTION_BANNERS: list[tuple[str, str, str, str, str]] = [
    (
        "SEASON_MISMATCH",
        "action-high",
        "🍂",
        "Reclassify as continuity — update ranging and reorder plan",
        "Product sells consistently across seasons, contradicting its seasonal label. "
        "Reclassify to continuity, update the range plan, and ensure year-round replenishment.",
    ),
    (
        "MID_MISMATCH",
        "action-med",
        "⚡",
        "Review seasonal label — consider continuity trial",
        "Borderline season signal: product sells outside its labelled window but not consistently enough to confirm. "
        "Trial continuity stocking for one season and monitor sell-through.",
    ),
    (
        "NO_SIGNAL",
        "action-low",
        "📡",
        "Insufficient data — monitor next season before acting",
        "Too little sales history to determine whether the seasonal label is correct. "
        "Hold current classification and revisit after next full season of data.",
    ),
    (
        "SEASONAL_OK",
        "action-good",
        "✅",
        "Seasonal label correct — maintain current range plan",
        "Sales pattern aligns with the product's labelled season. "
        "No reclassification needed; continue existing range strategy.",
    ),
]


def _kpis(df: pd.DataFrame) -> list[kpi_cards.KPI]:
    counts = (
        df["insight_type"].value_counts()
        if "insight_type" in df
        else pd.Series(dtype=int)
    )
    return [
        kpi_cards.KPI("Total seasonal", f"{len(df):,}", "Seasonal products analysed"),
        kpi_cards.KPI.from_count(
            "Season mismatch",
            int(counts.get("SEASON_MISMATCH", 0)),
            "Should be continuity",
            "SEASON_MISMATCH",
        ),
        kpi_cards.KPI.from_count(
            "Mid mismatch",
            int(counts.get("MID_MISMATCH", 0)),
            "Borderline reclassify",
            "MID_MISMATCH",
        ),
        kpi_cards.KPI.from_count(
            "Seasonal OK",
            int(counts.get("SEASONAL_OK", 0)),
            "Correctly classified",
            "SEASONAL_OK",
        ),
        kpi_cards.KPI.from_count(
            "No signal",
            int(counts.get("NO_SIGNAL", 0)),
            "Too little data to tell",
            "NO_SIGNAL",
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
        st.info("No data for Season Misclassify.")
        return
    if summary:
        st.markdown(f'<div class="rm-exec">{summary}</div>', unsafe_allow_html=True)

    section_mark("Seasonal classification accuracy")
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
            ("product_season", "Labelled Season"),
            ("insight_type", "Insight"),
            ("recommended_action", "Action"),
        ],
        title="Season reclassify candidates",
        subtitle="Sorted by priority: mismatches first.",
        top_n=20,
        pill_columns={"insight_type"},
        filter_dims=_FILTER_DIMS,
        tab_key="ss_cands",
    )

    # ── Charts full-width below ───────────────────────────────────────────────
    section_mark("Distribution")
    charts.donut(
        df, "insight_type", "", "Insight breakdown", "By misclassification type"
    )
    charts.grouped_bar_by(
        df,
        "product_category",
        "insight_type",
        "",
        "Mismatches by category",
        "Categories with most misclassified items",
    )
