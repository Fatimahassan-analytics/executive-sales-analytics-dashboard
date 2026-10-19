# Business Intelligence Dashboard

A 5-KPI regional sales performance dashboard built in Streamlit + Plotly, with drill-down from region to category and YTD-vs-target tracking.

**Live demo:** _https://executive-sales-analytics-dashboard-x3msee7ljwb8zhoqttjcyi.streamlit.app/_

**Author:** Fatima Hassan — [github.com/Fatimahassan-analytics](https://github.com/Fatimahassan-analytics)

---
# Business Delivery Intelligence Dashboard

A 5-KPI regional delivery performance dashboard built in Streamlit + Plotly, featuring drill-down capabilities from city to vehicle type and Year-to-Date (YTD) vs. target on-time tracking.

---

## 🎯 Problem

A regional operations manager needs a single, intuitive dashboard they can open every Monday morning to review last week's performance, identify underperforming cities or routes, and decide where to allocate operational attention. 

This dashboard answers **five critical business questions**:
1. What was the total order volume and on-time delivery rate last week vs. the previous week and vs. the business target?
2. Which cities or regions are over- or under-performing in average delivery times?
3. Which order types (e.g., meal, buffet, drinks, snack) and vehicle types are driving performance changes?
4. What is the measurable impact of external factors like weather and traffic conditions on delivery times?
5. How is Year-to-Date (YTD) on-time performance tracking against the annual operational target?

---

## 📊 Dataset

- **Source:** Anonymized regional delivery operations dataset.
- **Schema:** The dataset contains 28 headerless columns mapped to the following features:
  - **Identifiers:** `order_id`, `restaurant_id`
  - **Performance:** `time_taken`, `rating`, `multiple_deliveries`
  - **Geospatial:** `del_lat`, `del_lon`, `res_lat`, `res_lon`, `distance`, `distance_category`
  - **Temporal:** `date`, `day_of_month`, `month`, `day_of_week`, `is_holiday`, `time_start`, `time_end`, `time_of_day`
  - **Conditions:** `weather`, `traffic`
  - **Order Details:** `type_of_order`, `vehicle_type`, `promo_code`, `is_sponsored`
  - **Location/Demographics:** `city_type`, `delivery_person_age`, `city_code`
- **Backup:** A 5,000-row synthetic sample (`delivery_data.csv`) is bundled with this repository so the dashboard runs end-to-end immediately without requiring external database connections.

---

## ⚙️ Approach

1. **Data Preparation:** The headerless CSV is dynamically mapped to 28 explicit columns. Temporal features (`Week`, `Month`, `Year`, `YearMonth`) are derived, and a binary `is_on_time` flag (defined as `time_taken <= 30` minutes) is engineered to standardize performance metrics.
2. **Key Performance Indicators (KPIs):** Calculate total orders, on-time delivery rate, average delivery time, week-over-week (WoW) percentage change, and average delivery distance.
3. **Visualizations:**
   - **Delivery Time & On-Time Rate (Monthly):** Plotly dual-line chart tracking trends over time.
   - **Avg Delivery Time by City:** Bar chart colored by on-time rate (green-to-red gradient) for instant regional health assessment.
   - **Orders by Type & Vehicle:** Stacked bar chart enabling sub-category drill-down (e.g., seeing which vehicles handle "meal" orders most).
   - **Order Distribution by Weather:** Pie chart to visualize operational load under different conditions.
   - **Impact of Traffic:** Bar chart showing average delivery time segmented by traffic severity.
   - **YTD On-Time Performance vs Target:** Plotly gauge chart providing an at-a-glance view of annual goal tracking.
4. **Interactive Filters:** Multi-select dropdowns for City, Order Type, and Month to allow ad-hoc slicing of the data.
5. **Design Rationale:** Single-page application, KPI metric strip pinned at the top, a responsive 2-column visual grid, and a footer containing a paginated raw data table with a one-click CSV download button.

---

## 📈 Results

| **KPI**               | **Sample (5,000 rows)** | **Expected Full Dataset** |
| --------------------- | ----------------------- | ------------------------- |
| Total Orders          | ~5,000                  | ~50,000+                  |
| On-Time Rate          | ~65%                    | ~75%                      |
| Avg Delivery Time     | ~25 min                 | ~28 min                   |
| Top Performing City   | HYD                     | HYD                       |
| Top Order Type        | meal                    | meal                      |

> *Numbers above are illustrative based on the bundled 5,000-row sample. Re-execute the app with the full dataset to see exact organizational values.*

---
