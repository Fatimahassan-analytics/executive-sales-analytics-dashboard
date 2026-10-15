"""Business Intelligence Dashboard — data loading and sample generation.

Generates a synthetic sales dataset that mirrors the structure of the
Tableau Superstore sample, so the dashboard runs end-to-end without
requiring an external download.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SAMPLE_PATH = RAW_DIR / "superstore_sample.csv"
FULL_PATH = RAW_DIR / "superstore.csv"

RANDOM_SEED = 42

REGIONS = ["Central", "East", "West", "South"]
CATEGORIES = {
    "Furniture":   ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Storage", "Art", "Binders", "Appliances", "Paper", "Labels", "Envelopes"],
    "Technology":  ["Phones", "Accessories", "Machines", "Copiers"],
}
SHIPPING_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]


def generate_sample_data(n_orders: int = 5000, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Generate a synthetic Superstore-style sales dataset."""
    rng = np.random.default_rng(seed)
    start_date = pd.Timestamp("2022-01-01")
    end_date = pd.Timestamp("2024-12-31")

    orders = []
    for i in range(n_orders):
        date = pd.Timestamp(rng.integers(start_date.value // 10**9, end_date.value // 10**9),
                            unit="s").normalize()
        region = rng.choice(REGIONS)
        category = rng.choice(list(CATEGORIES.keys()))
        sub_cat = rng.choice(CATEGORIES[category])
        segment = rng.choice(SEGMENTS)
        ship_mode = rng.choice(SHIPPING_MODES, p=[0.59, 0.20, 0.15, 0.06])
        qty = int(rng.integers(1, 10))
        discount = float(rng.choice([0.0, 0.10, 0.15, 0.20, 0.30, 0.50],
                                    p=[0.50, 0.20, 0.12, 0.08, 0.06, 0.04]))
        unit_price = round(float(rng.uniform(10, 800)), 2)
        sales = round(qty * unit_price * (1 - discount), 2)
        cost = round(sales * rng.uniform(0.55, 0.85), 2)
        profit = round(sales - cost, 2)

        # Christmas & summer lifts
        if date.month == 12:
            sales = round(sales * 1.18, 2); profit = round(profit * 1.20, 2)
        if date.month in [6, 7]:
            sales = round(sales * 1.05, 2); profit = round(profit * 1.06, 2)

        orders.append({
            "OrderID":      f"ORD-{i:05d}",
            "OrderDate":    date.strftime("%Y-%m-%d"),
            "ShipMode":     ship_mode,
            "Segment":      segment,
            "Region":       region,
            "Category":     category,
            "SubCategory":   sub_cat,
            "Sales":        sales,
            "Quantity":     qty,
            "Discount":     discount,
            "Profit":       profit,
        })
    df = pd.DataFrame(orders)
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    return df.sort_values("OrderDate").reset_index(drop=True)


def load_data() -> pd.DataFrame:
    """Load data: prefer full Superstore CSV, fall back to bundled sample."""
    if FULL_PATH.exists():
        df = pd.read_csv(FULL_PATH, parse_dates=["OrderDate"])
    elif SAMPLE_PATH.exists():
        df = pd.read_csv(SAMPLE_PATH, parse_dates=["OrderDate"])
    else:
        df = generate_sample_data()
        df.to_csv(SAMPLE_PATH, index=False)
    return df


def save_processed(df: pd.DataFrame, name: str = "processed.csv") -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / name
    df.to_csv(out, index=False)
    return out


if __name__ == "__main__":
    df = generate_sample_data()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAMPLE_PATH, index=False)
    print(f"Wrote sample dataset: {SAMPLE_PATH} ({len(df)} rows)")
    print(f"Date range: {df.OrderDate.min()} to {df.OrderDate.max()}")
    print(f"Total sales: ${df.Sales.sum():,.0f} | Total profit: ${df.Profit.sum():,.0f}")
    print(df.head())
