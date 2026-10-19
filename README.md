# Business Intelligence Dashboard

A 5-KPI regional sales performance dashboard built in Streamlit + Plotly, with drill-down from region to category and YTD-vs-target tracking.

**Live demo:** _https://executive-sales-analytics-dashboard-x3msee7ljwb8zhoqttjcyi.streamlit.app/_

**Author:** Fatima Hassan — [github.com/Fatimahassan-analytics](https://github.com/Fatimahassan-analytics)

---

## Problem

A regional sales director needs a single dashboard they can open every Monday morning to see last week's performance, identify underperforming stores, and decide where to send attention. The dashboard answers **five business questions**:

1. What was total sales last week vs the previous week and vs target?
2. Which regions are over- or under-performing?
3. Which product categories are driving changes?
4. What is the impact of shipping mode / customer segment?
5. How is YTD tracking against annual target?

## Dataset

- **Source:** Tableau Superstore sample data — freely available, ~10,000 rows.
- **Schema:** `OrderID, OrderDate, ShipMode, Segment, Region, Category, SubCategory, Sales, Quantity, Discount, Profit`.
- **Backup:** A 5,000-row synthetic sample (`data/raw/superstore_sample.csv`) is bundled with this repo so the dashboard runs end-to-end without downloading. Run `python download_data.py` to attempt to fetch the real Superstore dataset.

## Approach

1. **Data prep** — derive Year, Quarter, Month, Week, YearMonth, ProfitMargin columns.
2. **KPIs** — total sales, total profit, profit margin, WoW change, average order value.
3. **Visuals**:
   - Sales + profit time series (monthly) — Plotly dual-line chart
   - Sales by region — bar chart coloured by profit
   - Sales by category — stacked bar chart (sub-category drill-down)
   - Sales by segment — pie chart
   - Sales by ship mode — bar chart
   - YTD vs previous year — progress bar
4. **Filters** — region, category, year (all multi-select).
5. **Design rationale** — single page, KPI strip at top, 2-column visual grid, footer with raw data table + CSV download.

## Results

| KPI                       | Sample (synthetic) | Real Superstore |
|---------------------------|-------------------|-----------------|
| Total sales               | ~$2.4M            | ~$2.3M          |
| Profit margin             | ~22%              | ~12%            |
| Avg order value            | ~$480             | ~$460           |
| Top region                | West              | West            |
| Top category              | Technology        | Technology      |

> Numbers above are illustrative; re-execute the notebook to see your exact values.

## Live Demo

After deploying to [Streamlit Cloud](https://share.streamlit.io), paste your URL at the top of this README. The app lets you:
- Filter by region, category, and year.
- See all 5 KPIs update in real time.
- Download the filtered dataset as CSV.

## Screenshots

_Add 1–2 screenshots or a GIF of the Streamlit app here after your first run._

## How to Run

```bash
# 1. Clone
git clone https://github.com/Fatimahassan-analytics/business-intelligence-dashboard.git
cd business-intelligence-dashboard

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Download the real Superstore dataset
python download_data.py
# Dashboard will fall back to the bundled synthetic sample if this step is skipped.

# 5. Run the notebooks
jupyter lab notebooks/01_eda.ipynb
jupyter lab notebooks/02_modeling.ipynb      # KPI definitions + aggregations
jupyter lab notebooks/03_evaluation.ipynb    # Design rationale walkthrough

# 6. Launch the Streamlit dashboard
streamlit run app.py
```

## Tech Stack

- **Language:** Python 3.10+
- **Data:** pandas, NumPy
- **Visualisation:** Plotly (interactive), matplotlib + seaborn (notebook-static)
- **App:** Streamlit
- **Design system:** 5-KPI strip + 2-column visual grid + filter sidebar

## Repository Structure

```
business-intelligence-dashboard/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── download_data.py
├── app.py
├── data/
│   ├── raw/
│   │   └── superstore_sample.csv   # bundled 5k-row synthetic sample
│   └── processed/
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_modeling.ipynb           # KPI definitions + aggregations
│   └── 03_evaluation.ipynb         # design rationale walkthrough
├── src/
│   ├── data.py                     # data loading + synthetic generator
│   ├── model.py                    # KPI computations + aggregations
│   └── utils.py                    # static-plot helpers
└── artefacts/                      # auto-created; saved plots
```

## Design Rationale

**Why 5 KPIs and not 10?** A regional sales director's Monday-morning scan should be answerable in 30 seconds. Five KPIs fit on one screen row; ten would force a second row that gets ignored.

**Why Plotly over Altair or Bokeh?** Plotly gives interactive hover, zoom, and filter without custom JavaScript, and renders cleanly on Streamlit Cloud without extra config.

**Why stacked bar for category drill-down?** A regional director can answer "which sub-category is dragging down Office Supplies?" in one glance, without clicking.

**Why YTD vs prior-year total as the target?** Real sales targets are usually negotiated; without access to that data, prior-year total is the most defensible benchmark and is what most regional directors actually use as a sanity check.

## License

MIT — see [LICENSE](LICENSE).
