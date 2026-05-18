"""HTML table renderer with Apollo pills, CSV download, inline filters, and pagination."""

from __future__ import annotations
import base64
import math
from dataclasses import dataclass
import pandas as pd
import streamlit as st
from ui.theme import colour_for


@dataclass
class FilterDim:
    column: str
    label: str


def _pill(value: str) -> str:
    c = colour_for(value)
    return (
        f'<span class="rm-pill" '
        f'style="background:{c["soft"]};color:{c["primary"]};border-color:{c["primary"]}40">'
        f"{value}</span>"
    )


def _csv_link(df: pd.DataFrame, label: str) -> str:
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return (
        f'<a class="rm-dl-link" '
        f'href="data:text/csv;base64,{b64}" '
        f'download="{label.lower().replace(" ", "_")}.csv">'
        f"↓ CSV</a>"
    )


def render(
    df: pd.DataFrame,
    columns: list[tuple[str, str]],
    title: str,
    subtitle: str,
    top_n: int = 20,
    pill_columns: set[str] | None = None,
    filter_dims: list[FilterDim] | None = None,
    tab_key: str = "tbl",
) -> None:
    if df.empty:
        st.info(f"No rows for {title}.")
        return

    pill_columns = pill_columns or set()
    page_key = f"{tab_key}_page"

    # ── Table card header: title + CSV ────────────────────────────────────────
    st.markdown(
        f'<div class="rm-tbl-card">'
        f'<div class="rm-tbl-header">'
        f"<div>"
        f'<p class="rm-tbl-title">{title}</p>'
        f'<p class="rm-tbl-subtitle">{subtitle}</p>'
        f"</div>"
        f"{_csv_link(df, title)}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Filters rendered as Streamlit widgets (inside the card visually) ──────
    filtered = df.copy()
    if filter_dims:
        active_dims = [fd for fd in filter_dims if fd.column in filtered.columns]
        if active_dims:
            f_cols = st.columns(len(active_dims), gap="small")
            for col, fd in zip(f_cols, active_dims):
                opts = sorted(filtered[fd.column].dropna().unique().tolist())
                sel = col.multiselect(
                    fd.label,
                    opts,
                    key=f"{tab_key}_{fd.column}",
                    placeholder=f"All {fd.label.lower()}s",
                )
                if sel:
                    filtered = filtered[filtered[fd.column].isin(sel)]
            # Reset to page 1 whenever filters change
            filter_state = str(
                [st.session_state.get(f"{tab_key}_{fd.column}") for fd in active_dims]
            )
            prev_filter_key = f"{tab_key}_prev_filter"
            if st.session_state.get(prev_filter_key) != filter_state:
                st.session_state[page_key] = 1
            st.session_state[prev_filter_key] = filter_state

    total_rows = len(filtered)
    total_pages = max(1, math.ceil(total_rows / top_n))

    # Clamp current page into valid range
    current_page = int(st.session_state.get(page_key, 1))
    current_page = max(1, min(current_page, total_pages))
    st.session_state[page_key] = current_page

    start = (current_page - 1) * top_n
    display = filtered.iloc[start : start + top_n]

    # ── HTML table ────────────────────────────────────────────────────────────
    th_row = "".join(f'<th class="rm-th">{lbl}</th>' for _, lbl in columns)
    rows = []
    for _, row in display.iterrows():
        cells = []
        for col, _ in columns:
            val = row.get(col, "")
            val_str = "" if pd.isna(val) else str(val)
            if col in pill_columns and val_str:
                cells.append(f'<td class="rm-td">{_pill(val_str)}</td>')
            else:
                cells.append(f'<td class="rm-td">{val_str}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")

    row_start = start + 1
    row_end = start + len(display)
    count_note = f"Showing {row_start}–{row_end} of {total_rows} rows"

    st.markdown(
        f'<div class="rm-tbl-wrap">'
        f'<table class="rm-tbl"><thead><tr>{th_row}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table>"
        f'<div class="rm-tbl-footer">{count_note}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Pagination controls (inside the card) ─────────────────────────────────
    if total_pages > 1:
        st.markdown('<div class="rm-pagination">', unsafe_allow_html=True)
        pg_left, pg_mid, pg_right = st.columns([1, 2, 1])
        with pg_left:
            if st.button("← Prev", key=f"{tab_key}_prev", disabled=current_page <= 1):
                st.session_state[page_key] = current_page - 1
                st.rerun()
        with pg_mid:
            st.markdown(
                f'<div class="rm-page-indicator">Page {current_page} of {total_pages}</div>',
                unsafe_allow_html=True,
            )
        with pg_right:
            if st.button(
                "Next →", key=f"{tab_key}_next", disabled=current_page >= total_pages
            ):
                st.session_state[page_key] = current_page + 1
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close rm-tbl-card
