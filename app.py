"""Range Monitor V2 — Apollo/UiPath design. Three-state Streamlit app."""

from __future__ import annotations
from pathlib import Path
import streamlit as st
from ui import dashboard, processing, theme, upload

SAMPLE_DATA_DIR = Path(__file__).parent / "assets" / "sample_data"


def _ensure_state() -> None:
    if "stage" not in st.session_state:
        st.session_state.stage = "upload"


def main() -> None:
    st.set_page_config(
        page_title="Range Monitor | UiPath",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    theme.inject_global_css()
    _ensure_state()

    stage = st.session_state.stage

    # Processing page gets a clean full-page slot so no upload widgets bleed through
    if stage == "processing":
        page = st.empty()
        with page.container():
            processing.render(SAMPLE_DATA_DIR)
        return

    if stage == "upload":
        upload.render(SAMPLE_DATA_DIR)
    elif stage == "dashboard":
        dashboard.render()
    else:
        st.session_state.stage = "upload"
        st.rerun()


if __name__ == "__main__":
    main()
