"""Streamlit app — Business Intelligence Dashboard.

Run locally:
    streamlit run app.py

The dashboard answers five business questions:
1. What was total sales last week vs the previous week?
2. Which regions are over- or under-performing?
3. Which product categories are driving changes?
4. What is the impact of shipping mode / customer segment?
5. How is YTD tracking against annual target?
"""
from __future__ import annotations
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent / "src"))
from data import load_data  # noqa: E402
from model import add_derived_columns, kpis, sales_by_region, sales_by_category, sales_by_segment, sales_over_time, sales_by_ship_mode  # noqa: E402


@st.cache_data(show_spinner="Loading data ...")
def get_data():
    df = load_data()
    return add_derived_columns(df)


def main():
    st.set_page_config(page_title="Business Intelligence Dashboard", page_icon=":bar_chart:",
                       layout="wide")
    st.title("Business Intelligence Dashboard")
    st.caption("5-KPI regional sales performance dashboard with drill-down and category analysis.")

    df = get_data()

    # ─── Filters ────────────────────────────────────────────────────────
    st.sidebar.header("Filters")
    regions = sorted(df["Region"].unique())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
    categories = sorted(df["Category"].unique())
    selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
    years = sorted(df["Year"].unique())
    selected_years = st.sidebar.multiselect("Year", years, default=years)

    filtered = df[
        df["Region"].isin(selected_regions)
        & df["Category"].isin(selected_categories)
        & df["Year"].isin(selected_years)
    ]

    # ─── KPI strip ──────────────────────────────────────────────────────
    k = kpis(filtered)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total sales",   f"${k['total_sales']:,.0f}")
    col2.metric("Total profit",  f"${k['total_profit']:,.0f}")
    col3.metric("Profit margin", f"{k['profit_margin_pct']:.1f}%")
    col4.metric("WoW sales change", f"{k['sales_wow_change_pct']:+.1f}%",
                delta_color="inverse" if k['sales_wow_change_pct'] < 0 else "normal")
    col5.metric("Avg order value", f"${k['avg_order_value']:,.0f}")

    st.divider()

    # ─── 1. Sales over time ─────────────────────────────────────────────
    st.subheader("1. Sales over time")
    s_over_time = sales_over_time(filtered, freq="M")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s_over_time["OrderDate"], y=s_over_time["Sales"],
                            mode="lines+markers", name="Sales",
                            line=dict(color="#216b91", width=2)))
    fig.add_trace(go.Scatter(x=s_over_time["OrderDate"], y=s_over_time["Profit"],
                            mode="lines+markers", name="Profit",
                            line=dict(color="#b05b3e", width=2)))
    fig.update_layout(xaxis_title="Month", yaxis_title="Amount ($)",
                      hovermode="x unified", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # ─── 2 + 3. Region + Category drill-down ────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("2. Sales by region")
        by_region = sales_by_region(filtered)
        fig = px.bar(by_region, x="Region", y="Sales", color="Profit",
                    color_continuous_scale="Viridis", text_auto=".2s")
        fig.update_layout(xaxis_title="Region", yaxis_title="Sales ($)", height=400)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("3. Sales by category")
        by_cat = sales_by_category(filtered)
        fig = px.bar(by_cat, x="Category", y="Sales", color="SubCategory",
                    title="Sales by category (drill-down to sub-category)")
        fig.update_layout(xaxis_title="Category", yaxis_title="Sales ($)", height=400,
                          legend_title="Sub-category")
        st.plotly_chart(fig, use_container_width=True)

    # ─── 4. Segment + ship mode ─────────────────────────────────────────
    st.subheader("4. Sales by customer segment & ship mode")
    col_c, col_d = st.columns(2)
    with col_c:
        seg = sales_by_segment(filtered)
        fig = px.pie(seg, values="Sales", names="Segment",
                    color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        sm = sales_by_ship_mode(filtered)
        fig = px.bar(sm, x="ShipMode", y="Sales", color="ShipMode",
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(xaxis_title="Ship mode", yaxis_title="Sales ($)", height=400,
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ─── 5. YTD vs target ───────────────────────────────────────────────
    st.subheader("5. YTD sales vs target")
    current_year = max(filtered["Year"].unique()) if len(filtered) else None
    if current_year is not None:
        ytd_sales = filtered[filtered["Year"] == current_year]["Sales"].sum()
        # Target = previous year's total sales (simple proxy)
        prev_year_sales = filtered[filtered["Year"] == current_year - 1]["Sales"].sum()
        if prev_year_sales > 0:
            pct = ytd_sales / prev_year_sales * 100
            st.metric(f"YTD {current_year} sales",
                      f"${ytd_sales:,.0f}",
                      f"{pct:.0f}% of {current_year - 1} total")
            st.progress(min(int(pct), 100))
        else:
            st.metric(f"YTD {current_year} sales", f"${ytd_sales:,.0f}")

    st.divider()
    st.subheader("Underlying data")
    st.dataframe(filtered.head(50), use_container_width=True)
    st.download_button("Download filtered CSV",
                       filtered.to_csv(index=False).encode("utf-8"),
                       file_name="filtered_sales.csv", mime="text/csv")


if __name__ == "__main__":
    main()
