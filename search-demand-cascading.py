import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO

# Configure page
st.set_page_config(
    page_title="Keyword Demand Visualizer",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Search Demand Over Time")
st.markdown("Upload your keyword data to see animated demand trends")

# File upload section
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"],
    help="Should contain columns: 'keyword', 'date', and 'search_volume'"
)

# Sample data generator
@st.cache_data
def generate_sample_data():
    keywords = ["ChatGPT", "Bard", "Claude", "LLaMA"]
    date_range = pd.date_range(start="2023-01-01", periods=12, freq="MS")  # Monthly
    
    data = []
    for kw in keywords:
        base = np.random.randint(50, 150)
        for date in date_range:
            data.append({
                "keyword": kw,
                "date": date.strftime("%Y-%m-%d"),
                "search_volume": base * (0.8 + 0.4 * np.random.random())
            })
    return pd.DataFrame(data)

# Date parser with multiple format support
def parse_dates(df, date_column):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%m-%d-%Y'):
        try:
            df['date'] = pd.to_datetime(df[date_column], format=fmt)
            return df
        except:
            continue
    df['date'] = pd.to_datetime(df[date_column], errors='coerce')
    return df

# Load data
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        
        # Auto-detect date column
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        if not date_col:
            date_col = st.selectbox("Select date column", df.columns)
        
        df = parse_dates(df, date_col)
        
        # Auto-detect volume column
        if 'search_volume' not in df.columns:
            vol_col = next((col for col in df.columns if 'volume' in col.lower() or 'demand' in col.lower()), None)
            if not vol_col:
                vol_col = st.selectbox("Select search volume column", 
                                     [c for c in df.columns if c != date_col])
            df = df.rename(columns={vol_col: 'search_volume'})
        
        st.success("Data loaded successfully!")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Using sample data instead")
        df = generate_sample_data()
else:
    st.info("Using sample data - upload your CSV to visualize your own")
    df = generate_sample_data()

# Data processing
df = df.dropna(subset=['date', 'search_volume'])
df['normalized_volume'] = df.groupby('keyword')['search_volume'].transform(
    lambda x: (x - x.min()) / (x.max() - x.min()) * 100
)

# Animation controls
st.sidebar.header("Settings")
selected_keywords = st.sidebar.multiselect(
    "Select keywords:",
    df['keyword'].unique(),
    default=df['keyword'].unique()[:3]
)

animation_speed = st.sidebar.slider(
    "Animation speed:",
    100, 1500, 500,
    help="Milliseconds between frames"
)

# Create animated chart
plot_df = df[df['keyword'].isin(selected_keywords)] if selected_keywords else df

fig = px.bar(
    plot_df,
    x="keyword",
    y="normalized_volume",
    color="keyword",
    animation_frame="date",
    range_y=[0, 100],
    title="<b>Search Demand Over Time</b>",
    labels={
        "normalized_volume": "Normalized Demand (0-100)",
        "date": "Date"
    },
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# Customize layout
fig.update_layout(
    hovermode="x unified",
    showlegend=False,
    title_x=0.3,
    font=dict(size=12),
    margin=dict(t=100),
    xaxis_title=None,
    transition={'duration': animation_speed//2}
)

fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = animation_speed

# Display
st.plotly_chart(fig, use_container_width=True)

# Data table
with st.expander("📋 View Data"):
    st.dataframe(plot_df.sort_values(["keyword", "date"]))

# Footer
st.caption("Tip: For best results, include columns for 'keyword', 'date', and search volume")
