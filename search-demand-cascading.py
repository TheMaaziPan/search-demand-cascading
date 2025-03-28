import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Check for required packages
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    st.error("Critical packages missing! Please install with:\n\n"
             "`pip install plotly streamlit pandas numpy`")
    st.stop()

# Configure page
st.set_page_config(
    page_title="Animated Trend Analyzer",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("🚀 Animated Search Demand Visualizer")
st.markdown("""
Explore how search demand trends cascade across different time frames with this interactive animation.
""")

# Generate realistic mock data
@st.cache_data
def generate_mock_data():
    np.random.seed(42)
    date_range = pd.date_range(start="2023-01-01", end="2023-03-31", freq="D")
    
    # Base trend with seasonality
    x = np.linspace(0, 4*np.pi, len(date_range))
    base_trend = (np.sin(x) * 30 + 50) * (1 + 0.2 * np.sin(x/4))
    
    data = {
        "date": date_range,
        "hourly": base_trend * (0.8 + 0.4*np.random.random(len(date_range))),
        "daily": base_trend * (0.9 + 0.2*np.random.random(len(date_range))),
        "weekly": base_trend,
        "monthly": np.convolve(base_trend, np.ones(30)/30, mode='same')
    }
    
    df = pd.DataFrame(data)
    
    # Normalize to 0-100 scale
    for col in data.keys():
        if col != "date":
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * 100
            
    return df

# Load data
df = generate_mock_data()

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    time_frames = st.multiselect(
        "Select time frames:",
        ["hourly", "daily", "weekly", "monthly"],
        default=["daily", "weekly", "monthly"]
    )
    
    animation_speed = st.slider(
        "Animation speed:",
        min_value=50,
        max_value=500,
        value=200,
        help="Milliseconds between frames"
    )
    
    show_raw = st.checkbox("Show raw data", False)

# Prepare data for animation
df_melted = df.melt(
    id_vars=["date"], 
    value_vars=time_frames,
    var_name="time_frame", 
    value_name="demand"
)

# Create animated bar chart
if time_frames:
    fig = px.bar(
        df_melted,
        x="time_frame",
        y="demand",
        color="time_frame",
        animation_frame="date",
        range_y=[0, 100],
        title="<b>Daily Demand by Time Frame</b>",
        labels={"demand": "Normalized Demand (0-100)", "time_frame": "Time Frame"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    # Customize animation
    fig.update_layout(
        hovermode="x unified",
        showlegend=False,
        title_x=0.5,
        font=dict(size=12)
    )
    
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = animation_speed
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = animation_speed//2
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add trend line chart
    st.markdown("---")
    st.subheader("Trend Lines Over Time")
    fig_lines = px.line(
        df,
        x="date",
        y=time_frames,
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_lines.update_layout(hovermode="x unified")
    st.plotly_chart(fig_lines, use_container_width=True)
else:
    st.warning("Please select at least one time frame from the sidebar")

# Show raw data if requested
if show_raw:
    st.markdown("---")
    st.subheader("Raw Data")
    st.dataframe(df.sort_values("date", ascending=False), height=300)

# Footer
st.markdown("---")
st.caption("""
Created with Streamlit | Data is simulated for demonstration purposes
""")
