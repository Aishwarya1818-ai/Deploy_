import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set page title and favicon
st.set_page_config(
    page_title="Simple Streamlit App",
    page_icon="📊",
)

# Add a title and description
st.title("📊 Simple Data Visualization")
st.markdown("This is a simple Streamlit app that generates and visualizes random data.")

# Sidebar controls
st.sidebar.header("Settings")
num_points = st.sidebar.slider("Number of data points", 10, 1000, 100)
chart_type = st.sidebar.selectbox("Chart type", ["Line", "Bar", "Scatter", "Histogram"])
color = st.sidebar.color_picker("Chart color", "#1f77b4")

# Generate random data
if st.sidebar.button("Generate New Data"):
    st.session_state.data = pd.DataFrame({
        'x': range(num_points),
        'y': np.random.randn(num_points)
    })

# Initialize session state if not exists
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'x': range(num_points),
        'y': np.random.randn(num_points)
    })

# Display the data
st.subheader("Data Preview")
st.dataframe(st.session_state.data.head(10))

# Data statistics
st.subheader("Data Statistics")
st.write(st.session_state.data.describe())

# Visualize the data
st.subheader("Data Visualization")

fig, ax = plt.subplots(figsize=(10, 6))

if chart_type == "Line":
    ax.plot(st.session_state.data['x'], st.session_state.data['y'], color=color)
    ax.set_title("Line Chart of Random Data")

elif chart_type == "Bar":
    ax.bar(st.session_state.data['x'], st.session_state.data['y'], color=color)
    ax.set_title("Bar Chart of Random Data")

elif chart_type == "Scatter":
    ax.scatter(st.session_state.data['x'], st.session_state.data['y'], color=color)
    ax.set_title("Scatter Plot of Random Data")

elif chart_type == "Histogram":
    ax.hist(st.session_state.data['y'], bins=20, color=color)
    ax.set_title("Histogram of Random Data")

ax.set_xlabel("X value")
ax.set_ylabel("Y value")

st.pyplot(fig)

# Download the data
st.subheader("Download Data")
csv = st.session_state.data.to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="random_data.csv",
    mime="text/csv",
)

# Footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")
