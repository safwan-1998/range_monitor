"""Page 3 — dashboard. KPI strip + 5 tabs, Apollo styled."""

from __future__ import annotations
import pandas as pd
import streamlit as st
from ui.tabs import (
    slow_mover,
    rank_mismatch,
    season_misclassify,
    category_divergence,
    stock_imbalance,
)
from ui import kpi_cards
from ui.theme import logo_b64

_TAB_LABELS = [
    "Slow Mover",
    "Rank Mismatch",
    "Season Misclassify",
    "Category Divergence",
    "Stock Imbalance",
]


def _flagged(df: pd.DataFrame, types: set[str]) -> int:
    if df.empty or "insight_type" not in df:
        return 0
    return int(df["insight_type"].isin(types).sum())


def _top_strip(outputs: dict[str, pd.DataFrame]) -> None:
    sm = outputs.get("slow_mover", pd.DataFrame())
    rm = outputs.get("rank_mismatch", pd.DataFrame())
    ss = outputs.get("season_misclassify", pd.DataFrame())
    cd = outputs.get("category_divergence", pd.DataFrame())
    si = outputs.get("stock_imbalance", pd.DataFrame())

    items = [
        kpi_cards.KPI(
            "Slow mover",
            f"{_flagged(sm, {'SLOW_MOVER', 'STORE_ISSUE', 'DEAD_STOCK'}):,}",
            "Flagged store-product pairs",
            "high",
        ),
        kpi_cards.KPI(
            "Rank mismatch",
            f"{_flagged(rm, {'RANGE_GAP', 'MEDIUM_RANGE_GAP', 'LOW_RANGE_GAP'}):,}",
            "Range-gap candidates",
            "high",
        ),
        kpi_cards.KPI(
            "Season misclassify",
            f"{_flagged(ss, {'SEASON_MISMATCH', 'MID_MISMATCH'}):,}",
            "Reclassify candidates",
            "med",
        ),
        kpi_cards.KPI(
            "Category divergence",
            f"{_flagged(cd, {'CATEGORY_DIVERGENCE', 'MEDIUM_DIVERGENCE'}):,}",
            "Region × category gaps",
            "med",
        ),
        kpi_cards.KPI(
            "Stock imbalance",
            f"{_flagged(si, {'STOCK_OVERSTOCK', 'STOCK_UNDERSTOCK'}):,}",
            "Over- and understock pairs",
            "med",
        ),
    ]
    kpi_cards.render_strip(items)


def render() -> None:
    outputs = st.session_state.get("outputs") or {}
    summaries = st.session_state.get("summaries") or {}

    if not outputs:
        st.session_state.stage = "upload"
        st.rerun()
        return

    nav_l, nav_r = st.columns([5, 1])
    with nav_r:
        if st.button("← New analysis", key="back_to_upload", use_container_width=True):
            st.session_state.stage = "upload"
            st.session_state.outputs = None
            st.session_state.summaries = None
            st.rerun()

    logo = logo_b64()
    st.markdown(
        f'<div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid var(--border);margin-bottom:1.5rem">'
        f'<img src="data:image/svg+xml;base64,{logo}" class="rm-uipath-logo" alt="UiPath" />'
        f'<div class="rm-hero-title">Range <em>Monitor.</em></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    _top_strip(outputs)

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    tabs = st.tabs(_TAB_LABELS)

    with tabs[0]:
        slow_mover.render(
            outputs.get("slow_mover", pd.DataFrame()),
            summary=summaries.get("slow_mover", ""),
        )
    with tabs[1]:
        rank_mismatch.render(
            outputs.get("rank_mismatch", pd.DataFrame()),
            summary=summaries.get("rank_mismatch", ""),
        )
    with tabs[2]:
        season_misclassify.render(
            outputs.get("season_misclassify", pd.DataFrame()),
            summary=summaries.get("season_misclassify", ""),
        )
    with tabs[3]:
        category_divergence.render(
            outputs.get("category_divergence", pd.DataFrame()),
            summary=summaries.get("category_divergence", ""),
        )
    with tabs[4]:
        stock_imbalance.render(
            outputs.get("stock_imbalance", pd.DataFrame()),
            summary=summaries.get("stock_imbalance", ""),
        )
