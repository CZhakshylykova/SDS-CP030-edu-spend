# app.py

import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# --- Page Config ---
st.set_page_config(page_title='International Education Budget Planner', layout='centered')
st.title("🎓 International Education Budget Planner")

# --- Load Data ---
data = pd.read_csv("data_full.csv")  # Ensure this CSV is in the same directory

# --- Load Pretrained Model Components ---
@st.cache_resource
def load_model_components():
    components_path = os.path.join(os.path.dirname(__file__), 'model_components.pkl')
    return joblib.load(components_path)

model_components = load_model_components()
encoder = model_components['encoder']
scaler = model_components['scaler']
regressor = model_components['regressor']

# --- Sidebar Inputs ---
st.sidebar.header("Input Parameters")
target_country = st.sidebar.selectbox("Select Country", data["Country"].unique())
level = st.sidebar.selectbox("Select Level", data["Level"].unique())
duration = st.sidebar.slider("Duration (Years)", min_value=1, max_value=6, value=4)

# Use most frequent options for placeholders
most_common_city = data.loc[data["Country"] == target_country, "City"].mode()[0]
most_common_university = data.loc[data["Country"] == target_country, "University"].mode()[0]
most_common_program = data["Program"].mode()[0]

# --- Define feature categories ---
categorical_features = ["Country", "City", "University", "Program", "Level"]
numeric_features = ["Tuition_USD", "Living_Cost_Index", "Rent_USD", "Visa_Fee_USD", "Insurance_USD", "Total_cost"]

# --- Prepare User Input ---
user_input = pd.DataFrame({
    "Country": [target_country],
    "City": [most_common_city],
    "University": [most_common_university],
    "Program": [most_common_program],
    "Level": [level],
    "Duration_Years": [duration],
    "Tuition_USD": [0],
    "Living_Cost_Index": [0],
    "Rent_USD": [0],
    "Visa_Fee_USD": [0],
    "Insurance_USD": [0],
    "Total_cost": [0]
})

# --- Encode and Scale ---
encoded_input = encoder.transform(user_input[categorical_features])
scaled_input = scaler.transform(user_input[numeric_features])
user_features = np.hstack([encoded_input, scaled_input])

# --- Predict ---
predicted_tca = regressor.predict(user_features)[0]
st.sidebar.markdown(f"### 💰 Predicted Total Cost of Attendance:\n**${predicted_tca:,.2f}**")

# --- Affordability Map ---
st.header("🌍 Affordability Map")
affordability_map = px.choropleth(
    data,
    locations="Country",
    locationmode="country names",
    color="Total_cost",
    title="Affordability by Country",
    color_continuous_scale="Viridis"
)
st.plotly_chart(affordability_map)

# --- Cluster Explorer ---
st.header("📊 Cluster Explorer")
cluster_option = st.selectbox("Select Cluster Type", ["KMeans_Cluster", "HDBSCAN_Cluster"])
cluster_data = data.groupby(cluster_option).mean(numeric_only=True).reset_index()
st.dataframe(cluster_data)

# --- Footer Instructions ---
st.markdown("""
---
### ℹ️ How to Use
1. Use the sidebar to input your target country, level, and duration.
2. View the predicted TCA and explore affordability maps and clusters.
3. Visit the [README](README.md) for more details.
""")
