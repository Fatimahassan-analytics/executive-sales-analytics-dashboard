"""Business Intelligence Dashboard — KPI computation helpers."""
from __future__ import annotations
import pandas as pd
import numpy as np


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Year, quarter, month, week, YoY date columns."""
    out = df.copy()
    out["Year"]    = out["OrderDate"].dt.year
    out["Quarter"] = out["OrderDate"].dt.quarter
    out["Month"]   = out["OrderDate"].dt.month
    out["Week"]    = out["OrderDate"].dt.isocalendar().week.astype(int)
    out["YearMonth"] = out["OrderDate"].dt.to_period("M").astype(str)
    out["ProfitMargin"] = (out["Profit"] / out["Sales"]).round(4)
    return out


def kpis(df: pd.DataFrame) -> dict:
    """Compute the five headline KPIs the dashboard answers."""
    df = add_derived_columns(df)
    latest_week = df["OrderDate"].max() - pd.Timedelta(days=7)
    last_week = df[df["OrderDate"] > latest_week]
    prev_week = df[(df["OrderDate"] <= latest_week)
                    & (df["OrderDate"] > latest_week - pd.Timedelta(days=7))]
    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    profit_margin = (total_profit / total_sales * 100) if total_sales else 0.0
    sales_yoy_change = ((last_week["Sales"].sum() - prev_week["Sales"].sum())
                        / max(prev_week["Sales"].sum(), 1) * 100)
    n_orders = df["OrderID"].nunique()
    avg_order_value = total_sales / max(n_orders, 1)
    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "profit_margin_pct": profit_margin,
        "sales_wow_change_pct": sales_yoy_change,
        "n_orders": n_orders,
        "avg_order_value": avg_order_value,
    }


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("Region")
              .agg(Sales=("Sales", "sum"),
                   Profit=("Profit", "sum"),
                   Orders=("OrderID", "nunique"))
              .reset_index()
              .sort_values("Sales", ascending=False))


def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(["Category", "SubCategory"])
              .agg(Sales=("Sales", "sum"),
                   Profit=("Profit", "sum"),
                   Orders=("OrderID", "nunique"))
              .reset_index()
              .sort_values(["Category", "Sales"], ascending=[True, False]))


def sales_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("Segment")
              .agg(Sales=("Sales", "sum"),
                   Profit=("Profit", "sum"),
                   Orders=("OrderID", "nunique"))
              .reset_index()
              .sort_values("Sales", ascending=False))


def sales_over_time(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """freq: 'D', 'W', 'M', 'Q', 'Y'."""
    return (df.set_index("OrderDate")
              .resample(freq)
              .agg(Sales=("Sales", "sum"),
                   Profit=("Profit", "sum"),
                   Orders=("OrderID", "nunique"))
              .reset_index())


def sales_by_ship_mode(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("ShipMode")
              .agg(Sales=("Sales", "sum"),
                   Profit=("Profit", "sum"),
                   Orders=("OrderID", "nunique"))
              .reset_index()
              .sort_values("Sales", ascending=False))
