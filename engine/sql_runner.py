"""DuckDB-backed SQL execution layer.

Registers the four canonical DataFrames as views named ``stg__products``,
``stg__locations``, ``stg__sales``, ``stg__stock``. Reads each rule's SQL
file from ``engine/sql_models/`` and runs it, returning a dict of
``{rule_name: result_dataframe}``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import duckdb
import pandas as pd


SQL_MODELS_DIR = Path(__file__).parent / "sql_models"

RULE_FILES: dict[str, str] = {
    "slow_mover": "slow_mover.sql",
    "rank_mismatch": "rank_mismatch.sql",
    "season_misclassify": "season_misclassify.sql",
    "category_divergence": "category_divergence.sql",
    "stock_imbalance": "stock_imbalance.sql",
}


class SQLEngine:
    """Wraps a DuckDB in-memory connection that has the four staging tables
    registered as views.
    """

    def __init__(self) -> None:
        self.con = duckdb.connect(":memory:")

    def register(self, frames: Mapping[str, pd.DataFrame]) -> None:
        """Register canonical DataFrames as DuckDB views.

        Expected keys: ``stg__products``, ``stg__locations``, ``stg__sales``,
        ``stg__stock``.
        """
        for name, df in frames.items():
            # Cast location_id to integer for arithmetic comparisons (47, 23 etc.)
            local_df = df.copy()
            if "location_id" in local_df.columns:
                local_df["location_id"] = pd.to_numeric(
                    local_df["location_id"], errors="coerce"
                ).astype("Int64")
            self.con.register(name, local_df)

    def run_rule(self, rule: str) -> pd.DataFrame:
        if rule not in RULE_FILES:
            raise KeyError(f"Unknown rule: {rule}")
        sql_path = SQL_MODELS_DIR / RULE_FILES[rule]
        sql = sql_path.read_text()
        return self.con.execute(sql).df()

    def run_all(self) -> dict[str, pd.DataFrame]:
        return {rule: self.run_rule(rule) for rule in RULE_FILES}

    def close(self) -> None:
        self.con.close()


def run(frames: Mapping[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """One-shot helper: register frames, run every rule, return outputs."""
    engine = SQLEngine()
    try:
        engine.register(frames)
        return engine.run_all()
    finally:
        engine.close()
