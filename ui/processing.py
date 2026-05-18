"""Page 2 — processing. Apollo-styled step state machine.

Uses a single st.empty() container so ONLY the processing card is ever visible.
No other Streamlit elements are rendered, which eliminates the blurred ghost
components that appear when the page first mounts.
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Literal
import streamlit as st
from engine import ingestion, narrator, sql_runner

StepState = Literal["pending", "running", "done", "skipped"]

_STEPS = [
    ("01", "Reading files", "Parsing CSV / Excel uploads"),
    ("02", "Running SQL", "Executing 5 rule models on DuckDB"),
    ("03", "Generating insights", "Writing executive summaries with Claude"),
    ("04", "Building dashboard", "Composing the final view"),
]

_MARKER = {"pending": "○", "running": "◐", "done": "●", "skipped": "—"}
_LABEL = {
    "pending": "PENDING",
    "running": "RUNNING…",
    "done": "DONE",
    "skipped": "SKIPPED",
}


def _steps_html(states: list[StepState]) -> str:
    rows = []
    for (num, title, sub), state in zip(_STEPS, states):
        rows.append(
            f'<div class="rm-step">'
            f'<div class="rm-step-marker {state}">{_MARKER[state]}</div>'
            f'<div class="rm-step-num">{num}</div>'
            f"<div>"
            f'<div class="rm-step-title">{title}</div>'
            f'<div class="rm-step-sub">{sub}</div>'
            f"</div>"
            f'<div class="rm-step-state {state}">{_LABEL[state]}</div>'
            f"</div>"
        )
    return (
        # Outer centering wrapper — fills the viewport so nothing else is visible
        '<div style="min-height:70vh;display:flex;flex-direction:column;'
        'justify-content:center;max-width:640px;margin:0 auto;padding:2rem 0">'
        '<div class="rm-section" style="margin-bottom:1.5rem">'
        '<div class="rm-section-title">Building your dashboard</div>'
        '<div class="rm-section-subtitle">'
        "Reading files, applying five rules-based checks against DuckDB, composing the trade-pack."
        "</div></div>"
        '<div style="border:1px solid var(--border);background:var(--surface-raised);'
        'border-radius:var(--radius-lg);padding:0 1.5rem">' + "".join(rows) + "</div>"
        "</div>"
    )


def _update(slot: "st.delta_generator.DeltaGenerator", states: list[StepState]) -> None:
    slot.markdown(_steps_html(states), unsafe_allow_html=True)


def render(sample_data_dir: Path) -> None:
    # Single empty slot — the ONLY element on the page during processing
    slot = st.empty()
    states: list[StepState] = ["pending"] * 4
    _update(slot, states)

    api_key = (st.session_state.get("api_key") or "").strip()
    use_sample = st.session_state.get("use_sample", True)

    # Step 1 — read files
    states[0] = "running"
    _update(slot, states)
    try:
        if use_sample:
            frames = ingestion.load_sample_data(sample_data_dir)
        else:
            uploads = {
                "stg__products": st.session_state["upload_products"],
                "stg__locations": st.session_state["upload_locations"],
                "stg__sales": st.session_state["upload_sales"],
                "stg__stock": st.session_state["upload_stock"],
            }
            frames = ingestion.load_uploads(uploads)
    except Exception as e:
        slot.empty()
        st.error(f"Failed to read files: {e}")
        if st.button("← Back to upload", key="back_err1"):
            st.session_state.stage = "upload"
            st.rerun()
        return
    states[0] = "done"
    _update(slot, states)
    time.sleep(0.25)

    # Step 2 — run SQL
    states[1] = "running"
    _update(slot, states)
    try:
        outputs = sql_runner.run(frames)
    except Exception as e:
        slot.empty()
        st.error(f"SQL failed: {e}")
        if st.button("← Back to upload", key="back_err2"):
            st.session_state.stage = "upload"
            st.rerun()
        return
    states[1] = "done"
    _update(slot, states)
    time.sleep(0.25)

    # Step 3 — narrator (optional)
    if not api_key:
        states[2] = "skipped"
        _update(slot, states)
        summaries = narrator.generate_executive_summaries(api_key=None, outputs=outputs)
    else:
        states[2] = "running"
        _update(slot, states)
        summaries = narrator.generate_executive_summaries(
            api_key=api_key, outputs=outputs
        )
        states[2] = "done"
        _update(slot, states)
    time.sleep(0.25)

    # Step 4 — store and redirect
    states[3] = "running"
    _update(slot, states)
    st.session_state["outputs"] = dict(outputs)
    st.session_state["summaries"] = summaries
    states[3] = "done"
    _update(slot, states)
    time.sleep(0.4)

    st.session_state.stage = "dashboard"
    st.rerun()
