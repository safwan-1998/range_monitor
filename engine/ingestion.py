"""CSV / Excel ingestion. Reads the four required uploads, normalises column
names to lowercase, validates the minimum required columns, returns canonical
pandas DataFrames keyed by ``stg__<entity>``.

The four entities (per CONTEXT_FOR_CLAUDE.md §7):
  - stg__products   product master
  - stg__locations  location master
  - stg__sales      sales transactions (online + in-store)
  - stg__stock      stock-on-hand snapshots
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

import pandas as pd


REQUIRED_COLUMNS: dict[str, set[str]] = {
    "stg__products": {"product_id", "product_name", "product_category"},
    "stg__locations": {"location_id", "location_name"},
    "stg__sales": {"product_id", "location_id", "day_date", "sales_units"},
    "stg__stock": {"product_id", "location_id", "day_date", "available_stock"},
}


@dataclass
class IngestionError(Exception):
    entity: str
    message: str

    def __str__(self) -> str:
        return f"[{self.entity}] {self.message}"


def _read_any(source: Path | IO[bytes] | IO[str], filename: str) -> pd.DataFrame:
    name = filename.lower()
    if name.endswith(".csv"):
        return pd.read_csv(source)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(source)
    raise IngestionError(entity=filename, message=f"Unsupported file type: {filename}")


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _validate(entity: str, df: pd.DataFrame) -> None:
    required = REQUIRED_COLUMNS[entity]
    missing = required - set(df.columns)
    if missing:
        raise IngestionError(
            entity=entity,
            message=f"Missing required columns: {sorted(missing)}",
        )


def _coerce_types(entity: str, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if entity in {"stg__sales", "stg__stock"}:
        df["day_date"] = pd.to_datetime(df["day_date"]).dt.date

    if entity == "stg__sales":
        df["sales_units"] = (
            pd.to_numeric(df["sales_units"], errors="coerce").fillna(0).astype(int)
        )
        if "sales_value" in df.columns:
            df["sales_value"] = pd.to_numeric(
                df["sales_value"], errors="coerce"
            ).fillna(0.0)
        else:
            df["sales_value"] = 0.0

    if entity == "stg__stock":
        df["available_stock"] = (
            pd.to_numeric(df["available_stock"], errors="coerce").fillna(0).astype(int)
        )

    if entity in {"stg__sales", "stg__stock"}:
        df["location_id"] = df["location_id"].astype(str).str.strip()
        df["product_id"] = df["product_id"].astype(str).str.strip()

    if entity == "stg__locations":
        df["location_id"] = df["location_id"].astype(str).str.strip()
        for col in ("branch_area", "store_type"):
            if col not in df.columns:
                df[col] = ""

    if entity == "stg__products":
        df["product_id"] = df["product_id"].astype(str).str.strip()
        for col in ("product_brand", "product_season", "range_tag"):
            if col not in df.columns:
                df[col] = ""
        if "price" not in df.columns:
            df["price"] = 0.0
        else:
            df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)

    return df


def load_uploads(uploads: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Load four uploads keyed by canonical entity.

    ``uploads`` maps each entity name to either a Path, a Streamlit
    UploadedFile, or any file-like object with a ``.name`` attribute.
    Returns a dict of cleaned DataFrames keyed by ``stg__*`` table name.
    """
    out: dict[str, pd.DataFrame] = {}
    for entity, source in uploads.items():
        if entity not in REQUIRED_COLUMNS:
            raise IngestionError(entity=entity, message=f"Unknown entity: {entity}")
        if source is None:
            raise IngestionError(entity=entity, message="No file provided")

        filename = getattr(source, "name", str(source))
        df = _read_any(source, filename)
        df = _normalise(df)
        _validate(entity, df)
        df = _coerce_types(entity, df)
        out[entity] = df
    return out


def load_sample_data(sample_dir: Path) -> dict[str, pd.DataFrame]:
    """Load the bundled sample CSVs from ``range_monitor/sample_data/``."""
    mapping = {
        "stg__products": sample_dir / "products.csv",
        "stg__locations": sample_dir / "locations.csv",
        "stg__sales": sample_dir / "sales.csv",
        "stg__stock": sample_dir / "stock.csv",
    }
    missing = [str(p) for p in mapping.values() if not p.exists()]
    if missing:
        raise IngestionError(
            entity="sample_data",
            message=f"Missing sample files — run sample_data/generate.py first. Missing: {missing}",
        )
    return load_uploads(mapping)
