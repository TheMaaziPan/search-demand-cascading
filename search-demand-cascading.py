import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
st.set_page_config(layout="wide", page_title="Trend Cascading Visualizer")

# Title
st.title("🔍 Cascading Time Frames of Search Demand")
st.markdown("Compare how trends appear across different time granularities")

# --------------------------
# 3. Sidebar Controls
# --------------------------
with st.sidebar:
    st.header("Controls")
    
    # Time frame selection
    time_frames = st.multiselect(
        "Select time frames to compare:",
        ["hourly", "daily", "weekly", "monthly"],
        default=["daily", "weekly", "monthly"]
    )
    
    # Smoothing control
    smoothing_window = st.slider(
        "Smoothing window (days):",
        min_value=1,
        max_value=30,
        value=7,
        help="Rolling average window to reduce noise"
    )
    
    # Annotation options
    st.subheader("Annotations")
    show_peaks = st.checkbox("Highlight peaks", True)
    show_events = st.checkbox("Show example events", True)

# --------------------------
# 4. Data Processing
# --------------------------
df = generate_mock_data()

# Apply smoothing
for tf in time_frames:
    df[f"{tf}_smooth"] = df[tf].rolling(window=smoothing_window).mean()

# Sample events data (replace with your real events)
events = {
    "Product Launch": "2023-03-15",
    "Major Update": "2023-06-22",
    "News Feature": "2023-09-10",
    "Holiday Season": "2023-12-20"
}

# --------------------------
# 5. Visualization
# --------------------------
fig, ax = plt.subplots(figsize=(14, 7))

# Plot each selected time frame
line_styles = {"hourly": ":", "daily": "--", "weekly": "-", "monthly": "-"}
line_widths = {"hourly": 1, "daily": 1.5, "weekly": 2, "monthly": 2.5}

for tf in time_frames:
    col_name = f"{tf}_smooth" if smoothing_window > 1 else tf
    sns.lineplot(
        data=df,
        x="date",
        y=col_name,
        label=f"{tf.capitalize()} {'(smoothed)' if smoothing_window > 1 else ''}",
        linestyle=line_styles[tf],
        linewidth=line_widths[tf],
        ax=ax
    )

# Add peak annotations
if show_peaks:
    for tf in time_frames:
        col_name = f"{tf}_smooth" if smoothing_window > 1 else tf
        peak_idx = df[col_name].idxmax()
        peak_date = df.loc[peak_idx, "date"]
        peak_value = df.loc[peak_idx, col_name]
        
        ax.annotate(
            f"Peak ({tf})",
            xy=(peak_date, peak_value),
            xytext=(10, 10),
            textcoords="offset points",
            arrowprops=dict(
                arrowstyle="->",
                connectionstyle="arc3,rad=.2",
                color="gray"
            ),
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8)
        )

# Add event markers
if show_events:
    for event, date_str in events.items():
        event_date = pd.to_datetime(date_str)
        ax.axvline(x=event_date, color="red", linestyle="--", alpha=0.5)
        ax.text(
            event_date,
            95,
            f"⚡ {event}",
            rotation=90,
            va="top",
            ha="center",
            backgroundcolor="white"
        )

# Styling
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Normalized Search Demand (0-100)", fontsize=12)
ax.set_title("Trend Cascading Across Time Frames", fontsize=16)
ax.grid(True, linestyle="--", alpha=0.3)
ax.legend(loc="upper left")

plt.tight_layout()

# Display the plot
st.pyplot(fig)

# --------------------------
# 6. Data Explorer Section
# --------------------------
st.subheader("📊 Data Explorer")
with st.expander("View raw data"):
    st.dataframe(df.sort_values("date", ascending=False))

# --------------------------
# 7. Trend Metrics
# --------------------------
st.subheader("📈 Trend Statistics")
if time_frames:
    cols = st.columns(len(time_frames))
    for idx, tf in enumerate(time_frames):
        col_name = f"{tf}_smooth" if smoothing_window > 1 else tf
        with cols[idx]:
            st.metric(
                label=f"Max {tf} demand",
                value=f"{df[col_name].max():.1f}",
                delta=f"{df[col_name].mean():.1f} (avg)"
            )

# --------------------------
# 8. How to Use Instructions
# --------------------------
with st.expander("ℹ️ How to use this dashboard"):
    st.markdown("""
    1. **Select time frames** in the sidebar to compare trends
    2. Adjust the **smoothing window** to reduce noise
    3. Toggle **annotations** to understand key moments
    4. Hover over the data explorer table for details
    """)

# Add footer
st.markdown("---")
st.caption("Trend Cascading Visualizer | Created with Streamlit")
