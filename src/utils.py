"""Shared utilities for the BI Dashboard project."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.rcParams.update({
    "figure.figsize": (10, 5),
    "figure.dpi": 100,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
sns.set_style("whitegrid")


def save_fig(name: str, fig_dir: Path = Path("artefacts")) -> Path:
    fig_dir.mkdir(parents=True, exist_ok=True)
    path = fig_dir / name
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", dpi=120)
    plt.close()
    return path


def save_json(obj, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)
    return path


def plot_sales_over_time(df: pd.DataFrame, freq: str = "M"):
    s = (df.set_index("OrderDate").resample(freq)["Sales"].sum())
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(s.index, s.values, marker="o", linewidth=1.8, color="#216b91")
    ax.set_title(f"Total sales over time ({freq}-ly)")
    ax.set_xlabel("Date"); ax.set_ylabel("Sales ($)")
    return ax


def plot_sales_by_region(df: pd.DataFrame):
    by = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    by.plot(kind="bar", ax=ax, color="#216b91")
    ax.set_title("Total sales by region")
    ax.set_ylabel("Sales ($)")
    return ax


def plot_sales_by_category(df: pd.DataFrame):
    pivot = (df.pivot_table(index="Category", columns="SubCategory", values="Sales",
                            aggfunc="sum", fill_value=0))
    fig, ax = plt.subplots(figsize=(11, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
    ax.set_title("Sales by category and sub-category")
    ax.set_ylabel("Sales ($)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
    ax.legend(title="Sub-category", bbox_to_anchor=(1.02, 1), loc="upper left")
    return ax


def plot_profit_margin_by_segment(df: pd.DataFrame):
    g = (df.groupby("Segment")
           .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")))
    g["Margin"] = (g["Profit"] / g["Sales"] * 100).round(2)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    g["Margin"].plot(kind="bar", ax=ax, color="#b05b3e")
    ax.set_title("Profit margin by customer segment")
    ax.set_ylabel("Profit margin (%)")
    return ax
