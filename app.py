import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Business Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Dark sidebar */
section[data-testid="stSidebar"] {
    background: #0f1117;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stMultiSelect span { color: #0f1117 !important; }

/* KPI cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
div[data-testid="metric-container"] label { color: #94a3b8 !important; font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 600; font-size: 1.7rem; }
div[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.82rem; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: #1e293b; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 6px 20px; color: #94a3b8; font-weight: 500; }
.stTabs [aria-selected="true"] { background: #3b82f6 !important; color: white !important; }

/* Section headers */
h2, h3 { color: #f1f5f9; }

/* Dataframe */
div[data-testid="stDataFrame"] { border: 1px solid #334155; border-radius: 10px; }

/* Download button */
.stDownloadButton button {
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    padding: 0.4rem 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Chart theme ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0f172a",
    "axes.facecolor":    "#1e293b",
    "axes.edgecolor":    "#334155",
    "axes.labelcolor":   "#94a3b8",
    "xtick.color":       "#64748b",
    "ytick.color":       "#64748b",
    "text.color":        "#e2e8f0",
    "grid.color":        "#1e293b",
    "grid.linewidth":    0.5,
    "font.family":       "sans-serif",
})

PALETTE   = ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899"]
BLUE      = "#3b82f6"
GREEN     = "#10b981"
AMBER     = "#f59e0b"
RED       = "#ef4444"

# ─── Load & clean data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\rajas\OneDrive\Desktop\project mini\Bussiness Analysis\business_dataset_1000.csv")
    df.columns = df.columns.str.strip()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Year"]       = df["Order_Date"].dt.year
    df["Month"]      = df["Order_Date"].dt.month
    df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
    df["Quarter"]    = df["Order_Date"].dt.to_period("Q").astype(str)
    df["Week"]       = df["Order_Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeek"]  = df["Order_Date"].dt.day_name()

    # Fill missing with column median (safe)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Cost"]  = pd.to_numeric(df["Cost"],  errors="coerce")
    df["Price"].fillna(df["Price"].median(), inplace=True)
    df["Cost"].fillna(df["Cost"].median(),   inplace=True)

    df["Revenue"]       = df["Units_Sold"] * df["Price"]
    df["Profit"]        = (df["Price"] - df["Cost"]) * df["Units_Sold"]
    df["Profit_Margin"] = np.where(df["Revenue"] != 0,
                                   df["Profit"] / df["Revenue"] * 100, 0)
    df["Cost_Ratio"]    = df["Cost"] / df["Price"]
    return df

df = load_data()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    sel_years = st.multiselect("📅 Year", years, default=years)

    regions = sorted(df["Region"].unique())
    sel_regions = st.multiselect("🌍 Region", regions, default=regions)

    products = sorted(df["Product"].unique())
    sel_products = st.multiselect("📦 Product", products, default=products)

    st.markdown("---")
    st.markdown("### 📊 Display Options")
    show_raw   = st.checkbox("Show Raw Data",      value=False)
    show_corr  = st.checkbox("Correlation Heatmap", value=True)

    st.markdown("---")
    st.caption("Business Analytics Pro v2.0")

# ─── Filtered data ─────────────────────────────────────────────────────────────
fdf = df[
    df["Year"].isin(sel_years) &
    df["Region"].isin(sel_regions) &
    df["Product"].isin(sel_products)
].copy()

if fdf.empty:
    st.warning("⚠️ No data matches the current filters. Please adjust your selections.")
    st.stop()

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Business Analytics Dashboard")
st.caption(f"Showing **{len(fdf):,}** orders · {fdf['Order_Date'].min().date()} → {fdf['Order_Date'].max().date()}")
st.markdown("---")

# ─── KPI row ───────────────────────────────────────────────────────────────────
total_rev    = fdf["Revenue"].sum()
total_profit = fdf["Profit"].sum()
total_units  = fdf["Units_Sold"].sum()
avg_margin   = fdf["Profit_Margin"].mean()
avg_order    = fdf["Revenue"].mean()
total_orders = len(fdf)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("💰 Revenue",      f"₹{total_rev:,.0f}")
k2.metric("📈 Profit",       f"₹{total_profit:,.0f}")
k3.metric("📦 Units Sold",   f"{total_units:,}")
k4.metric("📉 Avg Margin",   f"{avg_margin:.1f}%")
k5.metric("🛒 Orders",       f"{total_orders:,}")
k6.metric("🧾 Avg Order Val",f"₹{avg_order:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Trends",
    "🗺️ Regional",
    "📦 Products",
    "🔬 Deep Dive",
    "⚠️ Anomalies",
    "📥 Export",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.subheader("Revenue & Profit Trends")

    # Monthly aggregation
    monthly = (
        fdf.groupby(["Year", "Month"])
        .agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"), Orders=("Order_ID","count"))
        .reset_index()
    )
    monthly["Period"] = pd.to_datetime(monthly[["Year","Month"]].assign(day=1))
    monthly.sort_values("Period", inplace=True)

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.fill_between(monthly["Period"], monthly["Revenue"], alpha=0.15, color=BLUE)
        ax.plot(monthly["Period"], monthly["Revenue"], color=BLUE, lw=2, marker="o", markersize=3)
        ax.set_title("Monthly Revenue", fontweight="bold", pad=10)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x/1e6:.1f}M"))
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(7, 3.6))
        colors = [GREEN if v >= 0 else RED for v in monthly["Profit"]]
        ax.bar(monthly["Period"], monthly["Profit"], color=colors, width=20)
        ax.axhline(0, color="#475569", lw=0.8)
        ax.set_title("Monthly Profit", fontweight="bold", pad=10)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x/1e6:.1f}M"))
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Quarterly summary
    st.markdown("#### Quarterly Performance")
    quarterly = (
        fdf.groupby("Quarter")
        .agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"), Orders=("Order_ID","count"))
        .reset_index()
    )
    quarterly["Margin %"] = (quarterly["Profit"] / quarterly["Revenue"] * 100).round(1)
    quarterly["Revenue"]  = quarterly["Revenue"].map(lambda x: f"₹{x:,.0f}")
    quarterly["Profit"]   = quarterly["Profit"].map(lambda x: f"₹{x:,.0f}")
    st.dataframe(quarterly, use_container_width=True, hide_index=True)

    # Day-of-week
    st.markdown("#### Orders by Day of Week")
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = fdf.groupby("DayOfWeek")["Revenue"].sum().reindex(dow_order)

    fig, ax = plt.subplots(figsize=(10, 3))
    bars = ax.bar(dow.index, dow.values, color=PALETTE[:len(dow)], width=0.6, edgecolor="#0f172a", linewidth=0.5)
    ax.set_title("Revenue by Day of Week", fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x/1e6:.1f}M"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x()+b.get_width()/2, h+h*0.01, f"₹{h/1e6:.2f}M",
                ha="center", va="bottom", fontsize=8, color="#94a3b8")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – REGIONAL
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("Regional Performance")

    region_df = (
        fdf.groupby("Region")
        .agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"),
             Orders=("Order_ID","count"), Units=("Units_Sold","sum"))
        .reset_index()
    )
    region_df["Margin %"] = (region_df["Profit"] / region_df["Revenue"] * 100).round(1)
    region_df["Avg Order"] = region_df["Revenue"] / region_df["Orders"]

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        explode = [0.04] * len(region_df)
        wedges, texts, autotexts = ax.pie(
            region_df["Revenue"], labels=region_df["Region"],
            autopct="%1.1f%%", colors=PALETTE[:len(region_df)],
            explode=explode, startangle=140,
            wedgeprops=dict(edgecolor="#0f172a", linewidth=1.5)
        )
        for at in autotexts:
            at.set_fontsize(9); at.set_color("#f1f5f9")
        ax.set_title("Revenue Share by Region", fontweight="bold", pad=12)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.arange(len(region_df))
        w = 0.35
        b1 = ax.bar(x - w/2, region_df["Revenue"]/1e6, w, color=BLUE, label="Revenue (M)", alpha=0.9)
        b2 = ax.bar(x + w/2, region_df["Profit"]/1e6,  w, color=GREEN, label="Profit (M)",  alpha=0.9)
        ax.set_xticks(x); ax.set_xticklabels(region_df["Region"])
        ax.set_title("Revenue vs Profit by Region", fontweight="bold")
        ax.set_ylabel("₹ Millions")
        ax.legend(framealpha=0.3)
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Margin heatmap by region + product
    st.markdown("#### Margin % Heatmap — Region × Product")
    pivot = fdf.groupby(["Region","Product"]).apply(
        lambda g: g["Profit"].sum() / g["Revenue"].sum() * 100
    ).round(1).unstack()

    fig, ax = plt.subplots(figsize=(8, 3.5))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn", linewidths=0.5,
                linecolor="#1e293b", ax=ax, cbar_kws={"shrink":0.7},
                annot_kws={"size":10})
    ax.set_title("Profit Margin % by Region & Product", fontweight="bold", pad=10)
    ax.set_xlabel(""); ax.set_ylabel("")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Table
    st.markdown("#### Regional Summary Table")
    display_r = region_df.copy()
    display_r["Revenue"]   = display_r["Revenue"].map(lambda x: f"₹{x:,.0f}")
    display_r["Profit"]    = display_r["Profit"].map(lambda x: f"₹{x:,.0f}")
    display_r["Avg Order"] = display_r["Avg Order"].map(lambda x: f"₹{x:,.0f}")
    st.dataframe(display_r, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("Product Performance")

    prod_df = (
        fdf.groupby("Product")
        .agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"),
             Units=("Units_Sold","sum"), Orders=("Order_ID","count"),
             Avg_Price=("Price","mean"), Avg_Cost=("Cost","mean"))
        .reset_index()
    )
    prod_df["Margin %"] = (prod_df["Profit"] / prod_df["Revenue"] * 100).round(1)

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sorted_p = prod_df.sort_values("Revenue", ascending=True)
        bars = ax.barh(sorted_p["Product"], sorted_p["Revenue"]/1e6,
                       color=PALETTE[:len(sorted_p)], edgecolor="#0f172a")
        ax.set_title("Revenue by Product", fontweight="bold")
        ax.set_xlabel("₹ Millions")
        for b in bars:
            w = b.get_width()
            ax.text(w + 0.02, b.get_y() + b.get_height()/2,
                    f"₹{w:.1f}M", va="center", fontsize=9, color="#94a3b8")
        ax.grid(True, axis="x", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(6, 4))
        scatter = ax.scatter(
            prod_df["Units"], prod_df["Margin %"],
            s=prod_df["Revenue"]/10000,
            c=PALETTE[:len(prod_df)], alpha=0.85, edgecolors="#0f172a", linewidths=0.8
        )
        for _, row in prod_df.iterrows():
            ax.annotate(row["Product"],
                        (row["Units"], row["Margin %"]),
                        textcoords="offset points", xytext=(5,5), fontsize=9)
        ax.set_xlabel("Units Sold"); ax.set_ylabel("Profit Margin %")
        ax.set_title("Volume vs Margin (bubble = revenue)", fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.axhline(prod_df["Margin %"].mean(), color=AMBER, lw=1, ls="--", alpha=0.7)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Monthly product trend
    st.markdown("#### Monthly Revenue per Product")
    prod_monthly = (
        fdf.groupby(["Year","Month","Product"])["Revenue"].sum()
        .reset_index()
    )
    prod_monthly["Period"] = pd.to_datetime(prod_monthly[["Year","Month"]].assign(day=1))

    fig, ax = plt.subplots(figsize=(12, 4))
    for i, p in enumerate(sorted(prod_monthly["Product"].unique())):
        pdata = prod_monthly[prod_monthly["Product"] == p].sort_values("Period")
        ax.plot(pdata["Period"], pdata["Revenue"]/1e3, lw=2, marker="o",
                markersize=3, color=PALETTE[i], label=f"Product {p}")
    ax.set_title("Monthly Revenue Trend by Product", fontweight="bold")
    ax.set_ylabel("₹ Thousands")
    ax.legend(loc="upper left", framealpha=0.3)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("Statistical Deep Dive")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Price Distribution by Product")
        fig, ax = plt.subplots(figsize=(6, 4))
        for i, p in enumerate(sorted(fdf["Product"].unique())):
            data = fdf[fdf["Product"] == p]["Price"].dropna()
            ax.hist(data, bins=20, alpha=0.55, color=PALETTE[i], label=f"Product {p}", edgecolor="#0f172a")
        ax.set_xlabel("Price"); ax.set_ylabel("Count")
        ax.set_title("Price Distribution", fontweight="bold")
        ax.legend(framealpha=0.3)
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        st.markdown("#### Profit Margin Distribution")
        fig, ax = plt.subplots(figsize=(6, 4))
        data = fdf["Profit_Margin"].dropna()
        ax.hist(data, bins=30, color=GREEN, alpha=0.8, edgecolor="#0f172a")
        ax.axvline(data.mean(),   color=AMBER, lw=2, ls="--", label=f"Mean {data.mean():.1f}%")
        ax.axvline(data.median(), color=RED,   lw=2, ls=":",  label=f"Median {data.median():.1f}%")
        ax.set_xlabel("Profit Margin %"); ax.set_ylabel("Count")
        ax.set_title("Margin Distribution", fontweight="bold")
        ax.legend(framealpha=0.3)
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Correlation
    if show_corr:
        st.markdown("#### Correlation Matrix")
        num_cols = ["Units_Sold","Price","Cost","Revenue","Profit","Profit_Margin"]
        corr = fdf[num_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 5))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                    vmin=-1, vmax=1, linewidths=0.5, linecolor="#1e293b",
                    ax=ax, annot_kws={"size":9})
        ax.set_title("Pearson Correlation Matrix", fontweight="bold", pad=10)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Price vs Profit regression
    st.markdown("#### Price vs Profit — Regression")
    clean = fdf[["Price","Profit"]].dropna()
    slope, intercept, r, p_val, _ = stats.linregress(clean["Price"], clean["Profit"])

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(clean["Price"], clean["Profit"], alpha=0.35, s=15, color=BLUE, edgecolors="none")
    x_line = np.linspace(clean["Price"].min(), clean["Price"].max(), 200)
    ax.plot(x_line, slope*x_line+intercept, color=AMBER, lw=2, label=f"OLS (R²={r**2:.3f})")
    ax.axhline(0, color="#475569", lw=0.7)
    ax.set_xlabel("Price"); ax.set_ylabel("Profit")
    ax.set_title("Price vs Profit (OLS Regression)", fontweight="bold")
    ax.legend(framealpha=0.3)
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    col_s, _ = st.columns([1,2])
    with col_s:
        st.info(f"""
**Regression Stats**  
• Slope: `{slope:.3f}`  
• Intercept: `{intercept:.2f}`  
• R²: `{r**2:.4f}`  
• p-value: `{p_val:.4e}`  
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – ANOMALIES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("Anomaly & Outlier Detection")

    detect_col = st.selectbox("Column to analyze", ["Price","Profit","Revenue","Units_Sold","Profit_Margin"])
    method     = st.radio("Detection method", ["IQR (Tukey)", "Z-Score (σ > 3)"], horizontal=True)

    series = fdf[detect_col].dropna()

    if method == "IQR (Tukey)":
        Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
        IQR    = Q3 - Q1
        lo, hi = Q1 - 1.5*IQR, Q3 + 1.5*IQR
        mask   = (fdf[detect_col] < lo) | (fdf[detect_col] > hi)
    else:
        z      = np.abs(stats.zscore(series))
        lo, hi = series.mean() - 3*series.std(), series.mean() + 3*series.std()
        mask   = fdf.index.isin(series.index[z > 3])

    outliers_df = fdf[mask].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("Outliers Found",    f"{len(outliers_df)}")
    c2.metric("% of Dataset",      f"{len(outliers_df)/len(fdf)*100:.1f}%")
    c3.metric("Avg Outlier Value", f"{outliers_df[detect_col].mean():,.1f}" if len(outliers_df) else "—")

    # Box plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].boxplot(series.dropna(), patch_artist=True,
                    boxprops=dict(facecolor="#1e3a5f", color=BLUE),
                    medianprops=dict(color=AMBER, lw=2),
                    whiskerprops=dict(color="#94a3b8"),
                    capprops=dict(color="#94a3b8"),
                    flierprops=dict(marker="o", color=RED, alpha=0.5, markersize=4))
    axes[0].set_title(f"Box Plot – {detect_col}", fontweight="bold")
    axes[0].set_xticks([])
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.4)

    axes[1].hist(series, bins=40, color=BLUE, alpha=0.7, edgecolor="#0f172a")
    axes[1].axvline(lo, color=RED,   lw=2, ls="--", label=f"Lower ({lo:,.1f})")
    axes[1].axvline(hi, color=AMBER, lw=2, ls="--", label=f"Upper ({hi:,.1f})")
    axes[1].set_title(f"Distribution + Bounds – {detect_col}", fontweight="bold")
    axes[1].set_xlabel(detect_col); axes[1].set_ylabel("Count")
    axes[1].legend(framealpha=0.3)
    axes[1].grid(True, axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    if len(outliers_df):
        st.markdown(f"#### {len(outliers_df)} Outlier Records")
        st.dataframe(
            outliers_df[["Order_ID","Order_Date","Product","Region",
                          "Units_Sold","Price","Cost","Revenue","Profit"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.success("✅ No outliers detected with current method and filters.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 – EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.subheader("Export Data")

    st.markdown("#### 📋 Summary Report")
    summary = pd.DataFrame({
        "Metric": ["Total Revenue","Total Profit","Total Units","Total Orders",
                   "Avg Profit Margin","Avg Order Value","Best Region","Best Product"],
        "Value": [
            f"₹{total_rev:,.0f}",
            f"₹{total_profit:,.0f}",
            f"{total_units:,}",
            f"{total_orders:,}",
            f"{avg_margin:.1f}%",
            f"₹{avg_order:,.0f}",
            fdf.groupby("Region")["Profit"].sum().idxmax(),
            fdf.groupby("Product")["Profit"].sum().idxmax(),
        ]
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        st.markdown("**Filtered Dataset**")
        csv_full = fdf.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Filtered CSV", csv_full, "filtered_business_data.csv", "text/csv")

    with col_dl2:
        st.markdown("**Summary Report**")
        csv_sum = summary.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Summary CSV", csv_sum, "business_summary.csv", "text/csv")

# ─── Raw Data ──────────────────────────────────────────────────────────────────
if show_raw:
    with st.expander("📄 Raw Data Viewer", expanded=False):
        st.dataframe(fdf, use_container_width=True)
