import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO

# Configure page
st.set_page_config(
    page_title="Keyword Demand Animator",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("🔍 Animated Keyword Search Demand")
st.markdown("Upload your keyword data to visualize weekly demand trends with animations")

# File upload section
st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV file",
    type=["csv"],
    help="Format should include: 'keyword', date column, and search volume column"
)

# Sample data generator
@st.cache_data
def generate_sample_data():
    keywords = ["AI Tools", "ChatGPT", "Bard AI", "LLM"]
    date_range = pd.date_range(start="2023-01-01", periods=12, freq="W")
    
    data = []
    for kw in keywords:
        base = np.random.randint(50, 150)
        for date in date_range:
            data.append({
                "keyword": kw,
                "week_start_date": date.strftime("%d/%m/%Y"),  # Using day-first format
                "search_volume": base * (0.8 + 0.4 * np.random.random())
            })
    
    return pd.DataFrame(data)

# Date format detector
def parse_dates(series):
    for fmt in ('%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d'):
        try:
            return pd.to_datetime(series, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(series, dayfirst=True, errors='coerce')

# Main app logic
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File successfully uploaded!")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        st.info("Using sample data instead")
        df = generate_sample_data()
else:
    st.info("Using sample data. Upload a CSV to visualize your own.")
    df = generate_sample_data()

# Data validation and processing
try:
    # Handle date column
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'week' in col.lower():
            date_col = col
            break
    
    if date_col:
        df['week_start_date'] = parse_dates(df[date_col])
        df.drop(columns=[date_col], inplace=True, errors='ignore')
    else:
        st.error("No date column found. Please include a date column in your CSV.")
        st.stop()
    
    # Handle search volume column
    if 'search_volume' not in df.columns:
        volume_col = st.selectbox(
            "Select search volume column", 
            [c for c in df.columns if c not in ['keyword', 'week_start_date']]
        )
        df.rename(columns={volume_col: 'search_volume'}, inplace=True)
    
    # Normalize data
    df['normalized_volume'] = df.groupby('keyword')['search_volume'].transform(
        lambda x: (x - x.min()) / (x.max() - x.min()) * 100
    )
    
    # Filter out any rows with invalid dates
    df = df.dropna(subset=['week_start_date'])
    
except Exception as e:
    st.error(f"Data processing error: {str(e)}")
    st.stop()

# Animation controls
st.sidebar.header("Animation Settings")
selected_keywords = st.sidebar.multiselect(
    "Select keywords to show:",
    df['keyword'].unique(),
    default=df['keyword'].unique()[:3]
)

animation_speed = st.sidebar.slider(
    "Animation speed:",
    min_value=50,
    max_value=1000,
    value=200,
    step=50,
    help="Milliseconds between frames"
)

# Filter data
plot_df = df[df['keyword'].isin(selected_keywords)] if selected_keywords else df

# Create animated chart
if not plot_df.empty:
    fig = px.bar(
        plot_df,
        x="keyword",
        y="normalized_volume",
        color="keyword",
        animation_frame="week_start_date",
        range_y=[0, 100],
        title="<b>Weekly Search Demand Animation</b>",
        labels={
            "normalized_volume": "Normalized Demand (0-100)",
            "week_start_date": "Week Starting"
        },
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        hovermode="x unified",
        showlegend=False,
        title_x=0.3,
        font=dict(size=12),
        margin=dict(t=100)
    )
    
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = animation_speed
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = animation_speed // 2
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Trend Lines Over Time")
    trend_fig = px.line(
        plot_df,
        x="week_start_date",
        y="normalized_volume",
        color="keyword",
        markers=True,
        template="plotly_white"
    )
    st.plotly_chart(trend_fig, use_container_width=True)
else:
    st.warning("No data available for selected keywords")

# Data explorer section
with st.expander("📁 View Processed Data"):
    st.dataframe(plot_df.sort_values(["keyword", "week_start_date"]))

# Download sample template
st.sidebar.download_button(
    label="Download Sample CSV",
    data=generate_sample_data().to_csv(index=False).encode(),
    file_name="keyword_search_demand_sample.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.caption("""
Tip: For best results, include columns named 'keyword', a date column, and 'search_volume'.
Date formats automatically detected (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, etc.)
""")
