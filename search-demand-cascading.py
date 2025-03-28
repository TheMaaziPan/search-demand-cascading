import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO

# Configure page
st.set_page_config(
    page_title="Meeting Places Over Time",
    page_icon="💑",
    layout="wide"
)

# Title and description
st.title("💑 How Couples Met Over Time")
st.markdown("Animated visualization of how meeting places changed across decades")

# Create sample data based on your table
@st.cache_data
def generate_data():
    categories = [
        "School", "Friends", "Neighbours", "Church",
        "Bar/Restaurant", "College", "Coworkers", "Online"
    ]
    
    # Base percentages (2024 data from your table)
    final_values = [22.32, 21.49, 19.66, 9.53, 8.54, 4.03, 3.59, 0.00]
    
    # Generate decade data from 1930 to 2020
    decades = range(1930, 2030, 10)
    data = []
    
    for decade in decades:
        decade_factor = (decade - 1930) / (2020 - 1930)  # 0 in 1930, 1 in 2020
        for cat, final_val in zip(categories, final_values):
            # Simulate growth over time
            if cat == "Online":
                # Online starts appearing only after 1990
                if decade < 1990:
                    value = 0
                else:
                    online_years = decade - 1990
                    max_online_years = 2020 - 1990
                    value = final_val * (online_years / max_online_years) ** 2
            else:
                # Other categories decline as online grows
                decline_factor = 1 - (0.7 * (decade - 1990)/(2020-1990)) if decade > 1990 and cat != "Online" else 1
                value = final_val * decade_factor * decline_factor if decline_factor > 0 else 0
            
            data.append({
                "Decade": decade,
                "Category": cat,
                "Percentage": max(0, min(100, round(value, 2)))  # Clamp between 0-100
            )
    
    return pd.DataFrame(data)

df = generate_data()

# Animation controls
st.sidebar.header("Settings")
animation_speed = st.sidebar.slider(
    "Animation speed:",
    min_value=100,
    max_value=1500,
    value=500,
    help="Milliseconds between frames"
)

highlight_color = st.sidebar.color_picker(
    "Highlight color:",
    "#000000"
)

# Create animated chart
fig = px.bar(
    df,
    x="Category",
    y="Percentage",
    color="Category",
    animation_frame="Decade",
    range_y=[0, 30],
    title="<b>How Couples Met by Decade</b>",
    labels={"Percentage": "Percentage of Couples (%)"},
    color_discrete_sequence=px.colors.qualitative.Pastel,
    category_orders={"Category": df['Category'].unique().tolist()}
)

# Customize animation and layout
fig.update_layout(
    hovermode="x unified",
    showlegend=True,
    title_x=0.5,
    font=dict(size=12),
    margin=dict(t=100),
    xaxis_title=None,
    yaxis_title="Percentage of Couples",
    transition={'duration': animation_speed//2}
)

fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = animation_speed

# Add decade labels
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

# Add source citation
st.caption("""
Source: Diana Bussotti, Rosenfeld, Michael J. Dunbar, Thomas, and Kevin Houser. 2012
New Couples Meet and Stop Together. 2012-2020 2022 combined sponsor.
""")

# Display the animation
st.plotly_chart(fig, use_container_width=True)

# Show data table
with st.expander("📊 View Data Table"):
    pivot_df = df.pivot(index="Category", columns="Decade", values="Percentage")
    st.dataframe(pivot_df.style.format("{:.2f}%"))

# Add download button
st.sidebar.download_button(
    label="Download Data",
    data=df.to_csv(index=False).encode(),
    file_name="how_couples_met.csv",
    mime="text/csv"
)
