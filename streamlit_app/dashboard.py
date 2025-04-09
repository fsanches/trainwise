import streamlit as st
import requests
import pandas as pd
import os
import json

st.set_page_config(page_title="TrainWise | Strava Viewer", layout="wide")
st.title("🏊🚴🏃 TrainWise - Triathlon Activity Viewer")

# Mostra dados do atleta
token_path = "tokens/strava_token.json"
if os.path.exists(token_path):
    with open(token_path) as f:
        token_data = json.load(f)
        athlete = token_data.get("athlete", {})
        first_name = athlete.get("firstname", "Athlete")
        profile_url = athlete.get("profile", "")

        st.markdown(f"### 👋 Welcome, {first_name}!")
        if profile_url and not profile_url.endswith("avatar/athlete/large.png"):
            st.image(profile_url, width=100)
else:
    st.warning("⚠️ No athlete data available. Please authenticate via `/strava/login`.")
    st.stop()

# Carrega atividades da API local
try:
    response = requests.get("http://localhost:8000/strava/sync")
    data = response.json()

    if isinstance(data, list):
        df = pd.DataFrame(data)
        st.success(f"✅ {len(df)} activities loaded")

        df["distance_km"] = df["distance"] / 1000
        df = df.sort_values("start_date", ascending=False)

        # Divide por tipo
        run_df = df[df["type"] == "Run"]
        ride_df = df[df["type"] == "Ride"]
        swim_df = df[df["type"] == "Swim"]
        other_df = df[~df["type"].isin(["Run", "Ride", "Swim"])]

        with st.expander("🏃 Runs"):
            st.dataframe(run_df[["name", "distance_km", "moving_time", "start_date"]])

        with st.expander("🚴 Rides"):
            st.dataframe(ride_df[["name", "distance_km", "moving_time", "start_date"]])

        with st.expander("🏊 Swims"):
            st.dataframe(swim_df[["name", "distance_km", "moving_time", "start_date"]])

        with st.expander("🧩 Others"):
            st.dataframe(other_df[["name", "type", "distance_km", "moving_time", "start_date"]])

    else:
        st.error("❌ Error loading activities.")
        st.json(data)

except Exception as e:
    st.error("🚫 Could not connect to FastAPI backend.")
    st.exception(e)
