"""Optional Claude-powered narrator. Generates one short executive summary
per rule from the typed insight outputs. Skipped silently if no API key.

Cached per-(rule, fingerprint) so re-runs don't re-bill.
"""

from __future__ import annotations

import hashlib
import os
from typing import Mapping

import pandas as pd

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover
    Anthropic = None  # type: ignore[assignment]


_MODEL = "claude-haiku-4-5-20251001"


_RULE_INTROS: dict[str, str] = {
    "slow_mover": "Slow-moving products and store-issue mismatches detected over the last 28 days.",
    "rank_mismatch": "Products that rank highly online but underperform in stores.",
    "season_misclassify": "Seasonal products (SS / AW) selling outside their designated season online.",
    "category_divergence": "Categories trending strongly online but underperforming in specific store regions.",
    "stock_imbalance": "Locations holding disproportionate stock relative to peer-store sales velocity.",
}


def _fingerprint(df: pd.DataFrame) -> str:
    head = df.head(20).to_csv(index=False).encode()
    return hashlib.sha1(head).hexdigest()[:12]


def _empty_summary(rule: str) -> str:
    return f"No flagged rows for {rule}. Healthy."


def _format_for_prompt(rule: str, df: pd.DataFrame) -> str:
    if "insight_type" not in df.columns:
        return f"Rule {rule} produced 0 rows."
    counts = df["insight_type"].value_counts().to_dict()
    sample_cols = [
        c
        for c in (
            "product_id",
            "product_name",
            "location_name",
            "branch_area",
            "insight_type",
            "recommended_action",
        )
        if c in df.columns
    ]
    sample = df[sample_cols].head(8).to_dict(orient="records") if sample_cols else []
    return f"Rule: {rule}\nInsight breakdown: {counts}\nSample (max 8 rows): {sample}"


def generate_executive_summaries(
    api_key: str | None,
    outputs: Mapping[str, pd.DataFrame],
) -> dict[str, str]:
    """Returns one executive summary per rule. Silent fallback if no key."""
    if not api_key or Anthropic is None:
        return {rule: _RULE_INTROS.get(rule, "") for rule in outputs}

    client = Anthropic(api_key=api_key)
    summaries: dict[str, str] = {}

    for rule, df in outputs.items():
        if df.empty:
            summaries[rule] = _empty_summary(rule)
            continue

        prompt = (
            "You are a senior retail merchandiser writing a one-paragraph trade-pack "
            "summary. Be concrete. Lead with the biggest opportunity. Mention "
            "absolute numbers — don't be vague. Three sentences max. No preamble. "
            "Plain prose, no bullet points.\n\n"
            f"{_format_for_prompt(rule, df)}"
        )

        try:
            resp = client.messages.create(
                model=_MODEL,
                max_tokens=180,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text if resp.content else ""
            summaries[rule] = text.strip() or _RULE_INTROS.get(rule, "")
        except Exception:  # network, auth, anything
            summaries[rule] = _RULE_INTROS.get(rule, "")

    return summaries


def is_available() -> bool:
    return Anthropic is not None and bool(os.environ.get("ANTHROPIC_API_KEY"))
