import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO

# Configure page
st.set_page_config(
    page_title="MV Search Demand - Who is winning the race",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 MV Search Demand - Who is winning the race")
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
    
    # Generate more realistic data with trends
    data = []
    for kw in keywords:
        # Different starting points and growth patterns for each keyword
        if kw == "ChatGPT":
            base = 100
            growth_factor = 1.2
        elif kw == "Bard":
            base = 70
            growth_factor = 1.15
        elif kw == "Claude":
            base = 50
            growth_factor = 1.25
        else:
            base = 40
            growth_factor = 1.1
            
        volume = base
        for date in date_range:
            # Add some randomness to the growth
            random_factor = 0.8 + 0.4 * np.random.random()
            volume = volume * growth_factor * random_factor if np.random.random() > 0.3 else volume * 0.95
            
            data.append({
                "keyword": kw,
                "date": date.strftime("%Y-%m-%d"),
                "search_volume": round(volume, 1)
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
        
        # Check minimum data requirements
        if len(df) < 2:
            st.error("Uploaded file must contain at least 2 data points.")
            st.info("Using sample data instead")
            df = generate_sample_data()
        else:
            # Check for required columns
            required_columns = ['keyword', 'date', 'search_volume']
            missing_columns = [col for col in required_columns if not any(col in c.lower() for c in df.columns)]
            
            if missing_columns:
                st.warning(f"Some required columns may be missing: {', '.join(missing_columns)}")
                
                # Auto-detect date column
                date_col = next((col for col in df.columns if 'date' in col.lower()), None)
                if not date_col:
                    date_col = st.selectbox("Select date column", df.columns)
                
                df = parse_dates(df, date_col)
                
                # Auto-detect keyword column if missing
                if 'keyword' not in df.columns:
                    kw_col = next((col for col in df.columns if 'keyword' in col.lower() or 'term' in col.lower() or 'kw' in col.lower()), None)
                    if not kw_col:
                        kw_col = st.selectbox("Select keyword column", [c for c in df.columns if c != date_col])
                    df = df.rename(columns={kw_col: 'keyword'})
                
                # Auto-detect volume column if missing
                if 'search_volume' not in df.columns:
                    vol_col = next((col for col in df.columns if 'volume' in col.lower() or 'demand' in col.lower() or 'traffic' in col.lower()), None)
                    if not vol_col:
                        vol_col = st.selectbox("Select search volume column", [c for c in df.columns if c != date_col and c != 'keyword'])
                    df = df.rename(columns={vol_col: 'search_volume'})
            else:
                df = parse_dates(df, 'date')
            
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

# Ensure search_volume is numeric
df['search_volume'] = pd.to_numeric(df['search_volume'], errors='coerce')
df = df.dropna(subset=['search_volume'])

# Visualization settings
st.sidebar.header("Visualization Settings")

show_mode = st.sidebar.radio(
    "Display mode:",
    ["Normalized Values (0-100)", "Absolute Values", "Growth Rate (%)"]
)

smoothing = st.sidebar.slider(
    "Data smoothing (rolling average):",
    0, 5, 0,
    help="Apply rolling average to smooth the data"
)

# Apply smoothing if selected
if smoothing > 0:
    df['smoothed_volume'] = df.groupby('keyword')['search_volume'].transform(
        lambda x: x.rolling(window=smoothing, min_periods=1).mean()
    )
    value_column = 'smoothed_volume'
else:
    value_column = 'search_volume'

# Calculate values based on selected mode
if show_mode == "Normalized Values (0-100)":
    # Normalize values between 0-100 for each keyword
    df['display_value'] = df.groupby('keyword')[value_column].transform(
        lambda x: (x - x.min()) / (x.max() - x.min()) * 100 if x.max() > x.min() else 50
    )
    y_axis_title = "Normalized Demand (0-100)"
    chart_title = "<b>Normalized Search Demand Over Time</b>"
    
elif show_mode == "Growth Rate (%)":
    # Calculate percentage growth rate
    df = df.sort_values(['keyword', 'date'])
    df['display_value'] = df.groupby('keyword')[value_column].pct_change() * 100
    # Replace NaN with 0 for first entries
    df['display_value'] = df['display_value'].fillna(0)
    y_axis_title = "Growth Rate (%)"
    chart_title = "<b>Search Demand Growth Rate Over Time</b>"
    
else:  # Absolute Values
    df['display_value'] = df[value_column]
    y_axis_title = "Search Volume"
    chart_title = "<b>Absolute Search Demand Over Time</b>"

# Animation and selection controls
st.sidebar.header("Animation Controls")

selected_keywords = st.sidebar.multiselect(
    "Select keywords:",
    df['keyword'].unique(),
    default=df['keyword'].unique()[:4] if len(df['keyword'].unique()) >= 4 else df['keyword'].unique()
)

animation_speed = st.sidebar.slider(
    "Animation speed:",
    100, 1500, 500,
    help="Milliseconds between frames"
)

top_n = st.sidebar.number_input(
    "Show top N keywords per frame:",
    min_value=0,
    max_value=len(df['keyword'].unique()),
    value=min(10, len(df['keyword'].unique())),
    help="0 to show all keywords"
)

sort_bars = st.sidebar.checkbox(
    "Sort bars by value (racing effect)",
    True,
    help="Sort bars by value in each frame"
)

# Create filtered dataframe
plot_df = df
if selected_keywords:
    plot_df = df[df['keyword'].isin(selected_keywords)]

# Prepare data for racing bar chart
if top_n > 0:
    # For each date, get the top N keywords by value
    top_keywords_by_date = {}
    for date in plot_df['date'].unique():
        date_df = plot_df[plot_df['date'] == date]
        top_keywords = date_df.nlargest(top_n, 'display_value')['keyword'].unique()
        top_keywords_by_date[pd.Timestamp(date)] = top_keywords
    
    # Keep only keywords that appear in the top N for at least one date
    all_top_keywords = set()
    for keywords in top_keywords_by_date.values():
        all_top_keywords.update(keywords)
    
    plot_df = plot_df[plot_df['keyword'].isin(all_top_keywords)]

# Create a custom category order for the racing effect
all_dates = plot_df['date'].unique()
keyword_order = {}

if sort_bars:
    for date in all_dates:
        # Get data for this date and sort by value
        date_df = plot_df[plot_df['date'] == date]
        sorted_keywords = date_df.sort_values('display_value', ascending=False)['keyword'].tolist()
        keyword_order[pd.Timestamp(date)] = sorted_keywords

# Create animated chart
fig = px.bar(
    plot_df,
    x="keyword" if show_mode != "Growth Rate (%)" else "display_value",
    y="display_value" if show_mode != "Growth Rate (%)" else "keyword",
    color="keyword",
    animation_frame="date",
    title=chart_title,
    labels={
        "display_value": y_axis_title,
        "keyword": "Keyword",
        "date": "Date"
    },
    orientation="v" if show_mode != "Growth Rate (%)" else "h",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    text="keyword" if show_mode == "Growth Rate (%)" else None,
    range_y=[0, plot_df['display_value'].max() * 1.1] if show_mode != "Growth Rate (%)" else None,
    range_x=[plot_df['display_value'].min() * 1.1, plot_df['display_value'].max() * 1.1] if show_mode == "Growth Rate (%)" else None,
    category_orders={"keyword": keyword_order} if sort_bars and show_mode != "Growth Rate (%)" else None
)

# Customize layout
fig.update_layout(
    hovermode="closest",
    showlegend=True if len(selected_keywords) > 10 else False,
    title_x=0.3,
    font=dict(size=12),
    margin=dict(t=100, r=100),
    xaxis_title=None if show_mode != "Growth Rate (%)" else y_axis_title,
    yaxis_title=y_axis_title if show_mode != "Growth Rate (%)" else None,
    transition={'duration': animation_speed//2}
)

# Customize animation
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = animation_speed
fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = animation_speed//2

# Display
st.plotly_chart(fig, use_container_width=True)

# Show controls explanation
with st.expander("📋 How to use this visualization"):
    st.markdown("""
    ### Visualization Modes
    - **Normalized Values (0-100)**: Scales each keyword's data to a 0-100 range, making it easier to compare trends across keywords with different volumes
    - **Absolute Values**: Shows the raw search volume numbers
    - **Growth Rate (%)**: Shows the percentage change between consecutive time periods
    
    ### Animation Controls
    - **Select keywords**: Choose which keywords to display
    - **Animation speed**: Adjust how fast the animation plays
    - **Show top N**: Limit the display to only the top N keywords in each frame
    - **Sort bars**: Enable to create a "racing" effect where bars are sorted by value in each frame
    
    ### Data Smoothing
    - Apply a rolling average to smooth out short-term fluctuations and highlight longer-term trends
    """)

# Data table
with st.expander("📋 View Data"):
    st.dataframe(plot_df[['keyword', 'date', 'search_volume', 'display_value']].sort_values(["keyword", "date"]))

# Footer
st.caption("Tip: For best results, include columns for 'keyword', 'date', and search volume in your CSV file")
