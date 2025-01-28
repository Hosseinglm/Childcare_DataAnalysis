import streamlit as st
import pandas as pd
import plotly.express as px
from utils import (
    load_and_process_data,
    get_nps_distribution,
    create_nps_distribution_chart,
    create_correlation_heatmap,
    analyze_feedback_categories,
    calculate_weekly_response_rate,
    create_monthly_trends
)

# Page config
st.set_page_config(
    page_title="Childcare Center Analytics Dashboard",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🏢 Childcare Center Analytics Dashboard")
st.markdown("""
This dashboard provides comprehensive insights into customer feedback and satisfaction metrics.
""")

# Load and cache data
@st.cache_data
def load_data():
    return load_and_process_data("attached_assets/df_clean.csv")

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Survey Response Date [GMT]'].min(), df['Survey Response Date [GMT]'].max()),
    key="date_range"
)

# City filter
cities = sorted(df['City'].unique())
selected_cities = st.sidebar.multiselect(
    "Select Cities",
    options=cities,
    default=[],
    key="cities"
)

# Apply filters
filtered_df = df.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Survey Response Date [GMT]'].dt.date >= date_range[0]) &
        (filtered_df['Survey Response Date [GMT]'].dt.date <= date_range[1])
    ]
if selected_cities:
    filtered_df = filtered_df[filtered_df['City'].isin(selected_cities)]

# Section 1: Key Metrics
st.header("📊 Key NPS Metrics")
nps_dist = get_nps_distribution(filtered_df)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Overall NPS Score", 
              f"{round((nps_dist['Promoters'] - nps_dist['Detractors']), 1)}%")
with col2:
    st.metric("Promoters", f"{round(nps_dist['Promoters'], 1)}%")
with col3:
    st.metric("Passives", f"{round(nps_dist['Passives'], 1)}%")
with col4:
    st.metric("Detractors", f"{round(nps_dist['Detractors'], 1)}%")

# NPS Distribution Chart
st.subheader("NPS Distribution")
nps_dist_chart = create_nps_distribution_chart(filtered_df)
st.plotly_chart(nps_dist_chart, use_container_width=True)

# Correlation Matrix
st.header("📈 Satisfaction Metrics Correlation")
corr_matrix = create_correlation_heatmap(filtered_df)
st.plotly_chart(corr_matrix, use_container_width=True)

# Feedback Categories
st.header("💬 Most Common Feedback Categories")
feedback_chart = analyze_feedback_categories(filtered_df)
st.plotly_chart(feedback_chart, use_container_width=True)

# Weekly Response Rate
st.header("📅 Weekly Response Rate")
response_rate = calculate_weekly_response_rate(filtered_df)
st.plotly_chart(response_rate, use_container_width=True)

# Monthly Trends
st.header("📈 Monthly Trends in Key Metrics")
monthly_trends = create_monthly_trends(filtered_df)
st.plotly_chart(monthly_trends, use_container_width=True)


# Footer
st.markdown("---")
st.markdown("""
**Note**: Use the filters in the sidebar to analyze specific time periods or locations.
Data is updated daily with new survey responses.
""")