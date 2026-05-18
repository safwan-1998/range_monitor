"""Generate realistic synthetic sample data for the Range Monitor demo.

Produces four CSVs in this directory:
  - products.csv     50 SKUs across Footwear / Bags / Accessories / Apparel
  - locations.csv    8 locations: location 47 = online, 23 = warehouse, 6 stores
  - sales.csv        ~12 months daily sales (online + in-store) with patterns
                     baked in to surface every insight type
  - stock.csv        Last 28 days of stock-on-hand snapshots

Patterns engineered so the dashboard demo looks real:
  - 4 DEAD_STOCK products (no store sales, healthy stock)
  - 6 STORE_ISSUE products (strong online, dead in-store)
  - 8 SLOW_MOVER products (cold everywhere)
  - 5 SEASON_MISMATCH products (SS sold heavily in AW, vice versa)
  - 6 RANGE_GAP candidates (top decile online, mid/bottom in many stores)
  - 4 STOCK_OVERSTOCK locations (one store hoards 3x peer median)
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

HERE = Path(__file__).parent
TODAY = date(2026, 5, 9)
WINDOW_DAYS = 365

CATEGORIES = ["Footwear", "Bags", "Accessories", "Apparel"]
BRANDS = ["Pavers", "Hush Puppies", "Skechers", "Clarks", "Rieker", "Generic"]


def _spans(start: date, end: date):
    n = (end - start).days
    for i in range(n + 1):
        yield start + timedelta(days=i)


def _is_ss(d: date) -> bool:
    return 3 <= d.month <= 8


def write_products() -> list[dict]:
    products = []
    for i in range(1, 51):
        sku = f"SKU-{1000 + i}"
        cat = CATEGORIES[i % len(CATEGORIES)]
        brand = BRANDS[i % len(BRANDS)]
        # Roughly half SS, half AW for in-scope products; some explicitly NA
        if i % 7 == 0:
            season = ""
            tag = "continuity"
        elif i % 2 == 0:
            season = "SS"
            tag = "seasonal"
        else:
            season = "AW"
            tag = "seasonal"
        products.append(
            {
                "product_id": sku,
                "product_name": f"{brand} {cat} Style {i:03d}",
                "product_category": cat,
                "product_brand": brand,
                "product_season": season,
                "range_tag": tag,
                "price": round(19.99 + (i % 9) * 7.5, 2),
            }
        )
    return products


def write_locations() -> list[dict]:
    return [
        {
            "location_id": "47",
            "location_name": "Online DC",
            "branch_area": "Online",
            "store_type": "Online",
            "is_store": "false",
            "is_dc": "true",
        },
        {
            "location_id": "23",
            "location_name": "Central Warehouse",
            "branch_area": "Logistics",
            "store_type": "Warehouse",
            "is_store": "false",
            "is_dc": "true",
        },
        {
            "location_id": "101",
            "location_name": "Manchester Arndale",
            "branch_area": "North West",
            "store_type": "Pavers",
            "is_store": "true",
            "is_dc": "false",
        },
        {
            "location_id": "102",
            "location_name": "Liverpool One",
            "branch_area": "North West",
            "store_type": "Pavers",
            "is_store": "true",
            "is_dc": "false",
        },
        {
            "location_id": "103",
            "location_name": "Birmingham Bullring",
            "branch_area": "Midlands",
            "store_type": "Pavers",
            "is_store": "true",
            "is_dc": "false",
        },
        {
            "location_id": "104",
            "location_name": "Leeds Trinity",
            "branch_area": "Yorkshire",
            "store_type": "Pavers",
            "is_store": "true",
            "is_dc": "false",
        },
        {
            "location_id": "105",
            "location_name": "Glasgow Buchanan",
            "branch_area": "Scotland",
            "store_type": "Pavers",
            "is_store": "true",
            "is_dc": "false",
        },
        {
            "location_id": "106",
            "location_name": "Bristol Cabot",
            "branch_area": "South West",
            "store_type": "Pavers",
            "is_store": "true",
            "is_dc": "false",
        },
    ]


def write_sales(products: list[dict], locations: list[dict]) -> list[dict]:
    physical = [loc for loc in locations if loc["is_store"] == "true"]
    rows: list[dict] = []
    start = TODAY - timedelta(days=WINDOW_DAYS - 1)

    for idx, p in enumerate(products):
        sku = p["product_id"]
        season = p["product_season"]
        price = float(p["price"])

        # Behavioural archetypes — keyed off product index
        archetype: str
        if idx in {2, 7, 18, 33}:
            archetype = "DEAD_STOCK"
        elif idx in {1, 8, 14, 22, 31, 40}:
            archetype = "STORE_ISSUE"  # strong online, dead in-store
        elif idx in {3, 11, 17, 25, 28, 36, 42, 47}:
            archetype = "SLOW_MOVER"
        elif idx in {4, 19, 27, 38, 44}:
            archetype = "SEASON_MISMATCH"
        elif idx in {5, 12, 21, 29, 35, 41}:
            archetype = "RANGE_GAP"  # high online, mid/low in stores
        else:
            archetype = "BALANCED"

        # ONLINE TRAFFIC (location 47)
        for d in _spans(start, TODAY):
            if archetype == "DEAD_STOCK":
                continue
            if archetype == "STORE_ISSUE":
                if random.random() < 0.55:
                    units = random.randint(2, 8)
                    rows.append(
                        {
                            "product_id": sku,
                            "location_id": "47",
                            "day_date": d.isoformat(),
                            "sales_units": units,
                            "sales_value": round(units * price, 2),
                        }
                    )
            elif archetype == "SLOW_MOVER":
                if random.random() < 0.04:
                    units = 1
                    rows.append(
                        {
                            "product_id": sku,
                            "location_id": "47",
                            "day_date": d.isoformat(),
                            "sales_units": units,
                            "sales_value": round(units * price, 2),
                        }
                    )
            elif archetype == "SEASON_MISMATCH":
                # online sells year-round (unconstrained) — that's the signal
                if random.random() < 0.35:
                    units = random.randint(1, 4)
                    rows.append(
                        {
                            "product_id": sku,
                            "location_id": "47",
                            "day_date": d.isoformat(),
                            "sales_units": units,
                            "sales_value": round(units * price, 2),
                        }
                    )
            elif archetype == "RANGE_GAP":
                if random.random() < 0.65:
                    units = random.randint(3, 12)
                    rows.append(
                        {
                            "product_id": sku,
                            "location_id": "47",
                            "day_date": d.isoformat(),
                            "sales_units": units,
                            "sales_value": round(units * price, 2),
                        }
                    )
            else:  # BALANCED
                if random.random() < 0.20:
                    units = random.randint(1, 5)
                    rows.append(
                        {
                            "product_id": sku,
                            "location_id": "47",
                            "day_date": d.isoformat(),
                            "sales_units": units,
                            "sales_value": round(units * price, 2),
                        }
                    )

        # IN-STORE TRAFFIC (101–106)
        for store in physical:
            loc = store["location_id"]
            for d in _spans(start, TODAY):
                in_season = (
                    season == ""
                    or (season == "SS" and _is_ss(d))
                    or (season == "AW" and not _is_ss(d))
                )

                if archetype == "DEAD_STOCK":
                    continue
                if archetype == "STORE_ISSUE":
                    # almost no store sales despite strong online
                    if random.random() < 0.02:
                        units = 1
                        rows.append(
                            {
                                "product_id": sku,
                                "location_id": loc,
                                "day_date": d.isoformat(),
                                "sales_units": units,
                                "sales_value": round(units * price, 2),
                            }
                        )
                elif archetype == "SLOW_MOVER":
                    if random.random() < 0.03:
                        units = 1
                        rows.append(
                            {
                                "product_id": sku,
                                "location_id": loc,
                                "day_date": d.isoformat(),
                                "sales_units": units,
                                "sales_value": round(units * price, 2),
                            }
                        )
                elif archetype == "SEASON_MISMATCH":
                    # mismatches: when product is "SS" but selling in winter, etc.
                    if not in_season and random.random() < 0.15:
                        units = random.randint(1, 3)
                        rows.append(
                            {
                                "product_id": sku,
                                "location_id": loc,
                                "day_date": d.isoformat(),
                                "sales_units": units,
                                "sales_value": round(units * price, 2),
                            }
                        )
                    elif in_season and random.random() < 0.10:
                        units = random.randint(1, 2)
                        rows.append(
                            {
                                "product_id": sku,
                                "location_id": loc,
                                "day_date": d.isoformat(),
                                "sales_units": units,
                                "sales_value": round(units * price, 2),
                            }
                        )
                elif archetype == "RANGE_GAP":
                    # range-gap: only sells well at one or two stores, weak elsewhere
                    velocity = 0.45 if loc in {"101", "103"} else 0.05
                    if in_season and random.random() < velocity:
                        units = random.randint(1, 6)
                        rows.append(
                            {
                                "product_id": sku,
                                "location_id": loc,
                                "day_date": d.isoformat(),
                                "sales_units": units,
                                "sales_value": round(units * price, 2),
                            }
                        )
                else:  # BALANCED
                    if in_season and random.random() < 0.18:
                        units = random.randint(1, 4)
                        rows.append(
                            {
                                "product_id": sku,
                                "location_id": loc,
                                "day_date": d.isoformat(),
                                "sales_units": units,
                                "sales_value": round(units * price, 2),
                            }
                        )

    return rows


def write_stock(products: list[dict], locations: list[dict]) -> list[dict]:
    physical = [loc for loc in locations if loc["is_store"] == "true"]
    online_loc = "47"
    rows: list[dict] = []
    # Last 28 days of stock snapshots
    for d in _spans(TODAY - timedelta(days=27), TODAY):
        for idx, p in enumerate(products):
            sku = p["product_id"]
            # Online has stock for everything
            rows.append(
                {
                    "product_id": sku,
                    "location_id": online_loc,
                    "day_date": d.isoformat(),
                    "available_stock": random.randint(50, 200),
                }
            )
            for store in physical:
                loc = store["location_id"]
                # one store hoards stock for products idx 5..10 (overstock pattern)
                base = 25 if loc == "101" and 5 <= idx <= 10 else random.randint(2, 15)
                # understock pattern: one store with very low stock for idx 12..15
                if loc == "104" and 12 <= idx <= 15:
                    base = random.randint(0, 2)
                rows.append(
                    {
                        "product_id": sku,
                        "location_id": loc,
                        "day_date": d.isoformat(),
                        "available_stock": max(0, base + random.randint(-2, 2)),
                    }
                )
    return rows


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    products = write_products()
    locations = write_locations()
    sales = write_sales(products, locations)
    stock = write_stock(products, locations)

    _write_csv(
        HERE / "products.csv",
        products,
        [
            "product_id",
            "product_name",
            "product_category",
            "product_brand",
            "product_season",
            "range_tag",
            "price",
        ],
    )
    _write_csv(
        HERE / "locations.csv",
        locations,
        [
            "location_id",
            "location_name",
            "branch_area",
            "store_type",
            "is_store",
            "is_dc",
        ],
    )
    _write_csv(
        HERE / "sales.csv",
        sales,
        ["product_id", "location_id", "day_date", "sales_units", "sales_value"],
    )
    _write_csv(
        HERE / "stock.csv",
        stock,
        ["product_id", "location_id", "day_date", "available_stock"],
    )

    print(f"products  : {len(products):>6} rows")
    print(f"locations : {len(locations):>6} rows")
    print(f"sales     : {len(sales):>6} rows")
    print(f"stock     : {len(stock):>6} rows")


if __name__ == "__main__":
    main()
