"""KPI card strip — Apollo styled. Same interface as range_monitor/ui/kpi_cards.py."""

from __future__ import annotations
from dataclasses import dataclass
import streamlit as st
from ui.theme import severity_for


@dataclass
class KPI:
    label: str
    value: str
    sub: str
    severity: str = "neutral"

    @classmethod
    def from_count(cls, label: str, count: int, sub: str, insight_type: str) -> "KPI":
        return cls(
            label=label,
            value=f"{count:,}",
            sub=sub,
            severity=severity_for(insight_type),
        )


def render_strip(items: list[KPI]) -> None:
    cols = st.columns(len(items), gap="small")
    for i, (col, kpi) in enumerate(zip(cols, items)):
        with col:
            st.markdown(
                f'<div class="rm-kpi-card severity-{kpi.severity} delay-{i}">'
                f'<div class="rm-kpi-value">{kpi.value}</div>'
                f'<div class="rm-kpi-label"><strong>{kpi.label}</strong><br>{kpi.sub}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
