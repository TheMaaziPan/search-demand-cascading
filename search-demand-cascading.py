import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Configure page
st.set_page_config(
    page_title="Trend Clustered Bars",
    page_icon="📶",
    layout="wide"
)

# Title and description
st.title("📊 Clustered Bar Chart: Search Demand Comparison")
st.markdown("Compare demand trends across different time frames using clustered bars")

# Generate realistic mock data
@st.cache_data
def generate_mock_data():
    np.random.seed(42)
    date_range = pd.date_range(start="2023-01-01", periods=12, freq="M")  # Monthly data
    
    data = {
        "month": date_range.strftime("%b %Y"),
        "Product A - Hourly": np.random.randint(40, 80, 12),
        "Product A - Daily": np.random.randint(50, 90, 12),
        "Product A - Weekly": np.random.randint(60, 95, 12),
        "Product B - Hourly": np.random.randint(30, 70, 12),
        "Product B - Daily": np.random.randint(40, 80, 12),
        "Product B - Weekly": np.random.randint(50, 90, 12),
        "Product C - Hourly": np.random.randint(20, 60, 12),
        "Product C - Daily": np.random.randint(30, 70, 12),
        "Product C - Weekly": np.random.randint(40, 80, 12),
    }
    
    df = pd.DataFrame(data).melt(id_vars="month", var_name="metric", value_name="demand")
    
    # Split metric into product and time frame
    df[['product', 'time_frame']] = df['metric'].str.split(' - ', expand=True)
    return df.drop(columns='metric')

df = generate_mock_data()

# Sidebar controls
with st.sidebar:
    st.header("Filters")
    selected_products = st.multiselect(
        "Select products:",
        df['product'].unique(),
        default=df['product'].unique()[:2]
    )
    
    selected_time_frames = st.multiselect(
        "Select time frames:",
        df['time_frame'].unique(),
        default=df['time_frame'].unique()
    )
    
    sort_order = st.selectbox(
        "Sort months:",
        ["Chronological", "Reverse", "Highest Demand"]
    )

# Filter data
filtered_df = df[
    (df['product'].isin(selected_products)) & 
    (df['time_frame'].isin(selected_time_frames))
]

# Sort data
if sort_order == "Reverse":
    filtered_df = filtered_df.sort_values('month', ascending=False)
elif sort_order == "Highest Demand":
    month_order = filtered_df.groupby('month')['demand'].sum().sort_values(ascending=False).index
    filtered_df['month'] = pd.Categorical(filtered_df['month'], categories=month_order, ordered=True)
    filtered_df = filtered_df.sort_values('month')

# Create clustered bar chart
if not filtered_df.empty:
    fig = px.bar(
        filtered_df,
        x="month",
        y="demand",
        color="time_frame",
        facet_col="product",
        barmode="group",
        title="<b>Search Demand Comparison</b>",
        labels={"demand": "Normalized Demand", "month": ""},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        height=500
    )
    
    # Customize layout
    fig.update_layout(
        hovermode="x unified",
        showlegend=True,
        legend_title="Time Frame",
        title_x=0.5,
        uniformtext_minsize=8,
        margin=dict(t=100)
    )
    
    # Remove facet titles and adjust spacing
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_xaxes(matches=None, showticklabels=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add summary statistics
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Products Compared", len(selected_products))
    with col2:
        st.metric("Time Frames", len(selected_time_frames))
    with col3:
        st.metric("Total Months", filtered_df['month'].nunique())
    
    # Show raw data
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df.sort_values(["product", "time_frame", "month"]))
else:
    st.warning("Please select at least one product and time frame")

# Footer
st.markdown("---")
st.caption("""
Data Visualization Dashboard • Data is simulated for demonstration purposes
""")
