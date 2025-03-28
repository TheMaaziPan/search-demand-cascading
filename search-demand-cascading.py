import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --------------------------
# 1. Generate Mock Trend Data
# --------------------------
def generate_mock_data():
    np.random.seed(42)
    date_range = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    
    # Simulate trend cascading with different frequencies
    base_trend = np.sin(np.linspace(0, 2*np.pi, len(date_range))) * 50 + 50
    
    data = {
        "date": date_range,
        "hourly": base_trend + np.random.normal(0, 15, len(date_range)),  # High volatility
        "daily": base_trend + np.random.normal(0, 10, len(date_range)),
        "weekly": base_trend + np.random.normal(0, 5, len(date_range)),
        "monthly": base_trend  # Smoothest trend
    }
    
    df = pd.DataFrame(data)
    
    # Clip negative values and normalize
    for col in data.keys():
        if col != "date":
            df[col] = df[col].clip(lower=0)
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * 100
            
    return df

# --------------------------
# 2. Streamlit UI Configuration
# --------------------------
st.set_page_config(layout="wide", page_title="Animated Trend Visualizer")

# Title
st.title("📊 Animated Bar Chart: Search Demand Over Time")
st.markdown("Watch how trends evolve across different time frames")

# --------------------------
# 3. Data Processing
# --------------------------
df = generate_mock_data()

# Melt data for Plotly animation
df_melted = df.melt(
    id_vars=["date"], 
    value_vars=["hourly", "daily", "weekly", "monthly"],
    var_name="time_frame", 
    value_name="demand"
)

# --------------------------
# 4. Animated Bar Chart
# --------------------------
fig = px.bar(
    df_melted,
    x="time_frame",
    y="demand",
    color="time_frame",
    animation_frame=df_melted["date"].astype(str),  # Convert dates to strings
    range_y=[0, 100],
    title="Animated Demand by Time Frame (Daily Progression)",
    labels={"demand": "Normalized Demand (0-100)", "time_frame": "Time Frame"},
    template="plotly_white"
)

# Speed up animation (milliseconds between frames)
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 100
fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 50

# Display the plot
st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 5. Line Chart for Comparison
# --------------------------
st.subheader("Trend Lines (Static View)")
time_frames = st.multiselect(
    "Select time frames to compare:",
    ["hourly", "daily", "weekly", "monthly"],
    default=["daily", "weekly", "monthly"]
)

if time_frames:
    fig_line = px.line(
        df,
        x="date",
        y=time_frames,
        title="Trend Lines Over Time",
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --------------------------
# 6. Data Explorer
# --------------------------
with st.expander("📁 View Raw Data"):
    st.dataframe(df.sort_values("date", ascending=False))
