import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Business Delivery Intelligence", layout="wide", page_icon="🚀")

# --- DATA LOADING & PREP ---
@st.cache_data
def load_data():
    # The dataset has no headers, so we define them explicitly
    columns = [
        'order_id', 'restaurant_id', 'time_taken', 'rating', 
        'del_lat', 'del_lon', 'res_lat', 'res_lon', 'date', 
        'weather', 'traffic', 'multiple_deliveries', 'type_of_order', 
        'vehicle_type', 'promo_code', 'is_sponsored', 'city_type', 
        'delivery_person_age', 'city_code', 'day_of_month', 'month', 
        'day_of_week', 'is_holiday', 'time_start', 'time_end', 
        'time_of_day', 'distance', 'distance_category'
    ]
    
    # Load data (Ensure your file is named delivery_data.csv in the repo)
    df = pd.read_csv("delivery_data.csv", header=None, names=columns)
    
    # Convert date and numeric columns
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    numeric_cols = ['time_taken', 'rating', 'multiple_deliveries', 'delivery_person_age', 
                    'day_of_month', 'month', 'is_holiday', 'time_start', 'time_end', 'distance']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Feature Engineering
    df['year'] = df['date'].dt.year
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    
    # Define On-Time: <= 30 minutes
    target_time = 30
    df['is_on_time'] = (df['time_taken'] <= target_time).astype(int)
    
    # Fill NAs in categorical columns
    for col in ['weather', 'traffic', 'type_of_order', 'vehicle_type', 'city_code']:
        df[col] = df[col].fillna('Unknown')
    
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")
cities = ["All"] + sorted(df['city_code'].dropna().unique().tolist())
selected_cities = st.sidebar.multiselect("Select City", cities, default=["All"])

order_types = ["All"] + sorted(df['type_of_order'].dropna().unique().tolist())
selected_order_types = st.sidebar.multiselect("Order Type", order_types, default=["All"])

months = ["All"] + sorted(df['month'].dropna().unique().astype(int).astype(str).tolist())
selected_months = st.sidebar.multiselect("Month", months, default=["All"])

# Filter dataframe
df_filtered = df.copy()
if "All" not in selected_cities:
    df_filtered = df_filtered[df_filtered['city_code'].isin(selected_cities)]
if "All" not in selected_order_types:
    df_filtered = df_filtered[df_filtered['type_of_order'].isin(selected_order_types)]
if "All" not in selected_months:
    df_filtered = df_filtered[df_filtered['month'].astype(int).astype(str).isin(selected_months)]

# --- KPI CALCULATIONS ---
total_orders = len(df_filtered)
on_time_rate = df_filtered['is_on_time'].mean() if total_orders > 0 else 0
avg_delivery_time = df_filtered['time_taken'].mean() if total_orders > 0 else 0
avg_distance = df_filtered['distance'].mean() if total_orders > 0 else 0
late_orders = total_orders - int(total_orders * on_time_rate)

target_on_time_rate = 0.85
wow_change = (on_time_rate - 0.80) * 100  # Mock WoW for demonstration

# --- DASHBOARD UI ---
st.title("🚀 Business Delivery Intelligence Dashboard")
st.markdown("### A 5-KPI regional delivery performance dashboard built in Streamlit + Plotly")
st.markdown("**Author:** Karne Siddhartha")
st.markdown("---")

# 1. KPI Strip
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Orders", f"{total_orders:,}", f"{wow_change:+.1f}% vs target")
col2.metric("On-Time Rate", f"{on_time_rate:.1%}", f"{(on_time_rate - target_on_time_rate):+.1%} vs 85% target")
col3.metric("Avg Delivery Time", f"{avg_delivery_time:.1f} min")
col4.metric("Avg Distance", f"{avg_distance:.1f} km")
col5.metric("Late Orders", f"{late_orders}")

st.markdown("---")

# 2. Visuals Grid
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📈 Delivery Time & On-Time Rate (Monthly)")
    monthly_stats = df_filtered.groupby('year_month').agg(
        avg_time=('time_taken', 'mean'),
        on_time_rate=('is_on_time', 'mean')
    ).reset_index().dropna()
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=monthly_stats['year_month'], y=monthly_stats['avg_time'], 
                              mode='lines+markers', name='Avg Time (min)', yaxis='y1'))
    fig1.add_trace(go.Scatter(x=monthly_stats['year_month'], y=monthly_stats['on_time_rate'], 
                              mode='lines+markers', name='On-Time Rate', yaxis='y2'))
    fig1.update_layout(
        yaxis=dict(title='Avg Time (min)'),
        yaxis2=dict(title='On-Time Rate', overlaying='y', side='right', tickformat='.0%'),
        xaxis=dict(title='Month'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("🏙️ Avg Delivery Time by City")
    city_stats = df_filtered.groupby('city_code').agg(
        avg_time=('time_taken', 'mean'),
        on_time_rate=('is_on_time', 'mean')
    ).reset_index().sort_values('avg_time', ascending=False).dropna()
    
    fig2 = px.bar(city_stats, x='city_code', y='avg_time', color='on_time_rate',
                  color_continuous_scale='RdYlGn', title="Avg Delivery Time by City (Colored by On-Time Rate)")
    fig2.update_layout(coloraxis_colorbar=dict(title="On-Time Rate", tickformat='.0%'))
    st.plotly_chart(fig2, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("🍔 Orders by Type & Vehicle")
    type_vehicle_stats = df_filtered.groupby(['type_of_order', 'vehicle_type']).size().reset_index(name='count')
    fig3 = px.bar(type_vehicle_stats, x='type_of_order', y='count', color='vehicle_type',
                  title="Order Volume by Type and Vehicle", barmode='stack')
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("🌦️ Order Distribution by Weather")
    weather_counts = df_filtered['weather'].value_counts().reset_index()
    weather_counts.columns = ['weather', 'count']
    fig4 = px.pie(weather_counts, values='count', names='weather', 
                  title="Order Distribution by Weather")
    st.plotly_chart(fig4, use_container_width=True)

col_e, col_f = st.columns(2)

with col_e:
    st.subheader("🚦 Impact of Traffic on Delivery Time")
    traffic_stats = df_filtered.groupby('traffic')['time_taken'].mean().reset_index().dropna()
    fig5 = px.bar(traffic_stats, x='traffic', y='time_taken', 
                  title="Avg Delivery Time by Traffic Condition", color='time_taken',
                  color_continuous_scale='Blues')
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    st.subheader("🎯 YTD On-Time Performance vs Target")
    ytd_on_time = df_filtered['is_on_time'].mean() * 100 if total_orders > 0 else 0
    fig6 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ytd_on_time,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "YTD On-Time Rate (%)", 'font': {'size': 24}},
        delta={'reference': target_on_time_rate * 100, 'increasing': {'color': "Green"}, 'decreasing': {'color': "Red"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 85], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target_on_time_rate * 100}}))
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# 3. Footer: Raw Data Table + Download
st.subheader("📊 Sample Raw Data")
st.dataframe(df_filtered.head(50), use_container_width=True)

csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name='business_delivery_filtered.csv',
    mime='text/csv',
)