"""Page 1 — upload. Apollo/UiPath styled hero, file slots, run button."""

from __future__ import annotations
from pathlib import Path
import streamlit as st
from ui.theme import logo_b64

_REQUIRED_COLS_DISPLAY = {
    "products": "product_id, product_name, product_category, product_brand,\nproduct_season, range_tag, price",
    "locations": "location_id, location_name, branch_area, store_type,\nis_store, is_dc",
    "sales": "product_id, location_id, day_date, sales_units, sales_value",
    "stock": "product_id, location_id, day_date, available_stock",
}
_DESCRIPTIONS = {
    "products": "Product master with category, brand, and season tags.",
    "locations": "Store and online channel master. Location 47 = online; 23 = warehouse.",
    "sales": "Daily online + in-store sales transactions over the analysis window.",
    "stock": "Daily stock-on-hand snapshots for the last ~28 days.",
}
_SLOT_ORDER = ["products", "locations", "sales", "stock"]


def _hero() -> None:
    logo = logo_b64()
    st.markdown(
        f'<div class="rm-hero">'
        f"<div>"
        f'<img src="data:image/svg+xml;base64,{logo}" class="rm-uipath-logo" alt="UiPath" />'
        f'<div class="rm-hero-title">Range<br><em>Monitor</em></div>'
        f"</div>"
        f'<div class="rm-hero-blurb">'
        f'<div class="rm-rules-list">'
        f'<div class="rm-rule-item"><span class="rm-rule-num">01</span><span class="rm-rule-name">Slow Mover</span><span class="rm-rule-desc">Products with low sell-through tying up shelf space and capital</span></div>'
        f'<div class="rm-rule-item"><span class="rm-rule-num">02</span><span class="rm-rule-name">Rank Mismatch</span><span class="rm-rule-desc">High online demand with poor in-store availability</span></div>'
        f'<div class="rm-rule-item"><span class="rm-rule-num">03</span><span class="rm-rule-name">Season Misclassify</span><span class="rm-rule-desc">Seasonal products selling year-round — candidates for continuity</span></div>'
        f'<div class="rm-rule-item"><span class="rm-rule-num">04</span><span class="rm-rule-name">Category Divergence</span><span class="rm-rule-desc">Category mix online vs in-store out of step by region</span></div>'
        f'<div class="rm-rule-item"><span class="rm-rule-num">05</span><span class="rm-rule-name">Stock Imbalance</span><span class="rm-rule-desc">Over- and understocked locations relative to peer stores</span></div>'
        f"</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


def _file_slot(label: str, key: str) -> None:
    st.markdown(
        f'<div class="rm-file-slot">'
        f"<h5>{label}</h5>"
        f'<div style="font-size:0.85rem;color:var(--foreground-muted);line-height:1.45">{_DESCRIPTIONS[key]}</div>'
        f'<div class="rm-required-cols">{_REQUIRED_COLS_DISPLAY[key].replace(chr(10), "<br>")}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    st.file_uploader(
        f"Upload {key}",
        type=["csv", "xlsx", "xls"],
        key=f"upload_{key}",
        label_visibility="collapsed",
    )


def render(sample_data_dir: Path) -> None:
    _hero()

    st.markdown(
        '<div class="rm-section-title">Optional</div>',
        unsafe_allow_html=True,
    )
    opt_l, opt_r = st.columns([1, 1], gap="large")
    with opt_l:
        st.text_input(
            "Anthropic API key (optional)",
            value=st.session_state.get("api_key", ""),
            type="password",
            key="api_key",
            help="If provided, Claude generates one-paragraph executive summaries per rule.",
        )
    with opt_r:
        st.toggle(
            "Use bundled sample data",
            value=st.session_state.get("use_sample", True),
            key="use_sample",
            help="Toggle off to upload your own four files below.",
        )

    if not st.session_state.get("use_sample", True):
        st.markdown(
            '<div class="rm-section">'
            '<div class="rm-section-title">Four files</div>'
            '<div class="rm-section-subtitle">CSV or Excel. Column names are normalised on read.</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2, gap="medium")
        for col, key in zip([c1, c2, c1, c2], _SLOT_ORDER):
            with col:
                _file_slot(key.title(), key)
    else:
        st.markdown(
            '<div class="rm-section">'
            '<div class="rm-section-title">Sample data ready</div>'
            '<div class="rm-section-subtitle">'
            "50 SKUs · 8 locations · 13.7K sales rows · 9.8K stock rows."
            "</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    if st.button(
        "Run analysis →", type="primary", use_container_width=True, key="run_btn"
    ):
        use_sample = st.session_state.get("use_sample", True)
        if not use_sample:
            missing = [
                k for k in _SLOT_ORDER if st.session_state.get(f"upload_{k}") is None
            ]
            if missing:
                st.error(f"Please upload all four files. Missing: {', '.join(missing)}")
                return
        st.session_state.stage = "processing"
        st.rerun()
