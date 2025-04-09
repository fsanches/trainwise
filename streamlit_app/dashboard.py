import streamlit as st
import requests
import pandas as pd
import os
import json
import time

# --- Token validation logic  ---
if "rerun_triggered" not in st.session_state:
    st.session_state.rerun_triggered = False

token_path = "tokens/strava_token.json"
token_valid = False
token_data = {}

if os.path.exists(token_path):
    with open(token_path) as f:
        token_data = json.load(f)
        expires_at = token_data.get("expires_at", 0)
        token_valid = time.time() < expires_at

if not token_valid:
    st.warning("⚠️ You are not connected to Strava or your token has expired.")
    st.markdown("""
    <a href='http://localhost:8000/strava/login' target='_self'>
        <button style='font-size:16px; padding:10px 20px; background-color:#f63366; color:white; border:none; border-radius:6px;'>
            🔐 Connect with Strava
        </button>
    </a>
    """, unsafe_allow_html=True)

    if os.path.exists(token_path):
        with open(token_path) as f:
            token_data = json.load(f)
            expires_at = token_data.get("expires_at", 0)
            if time.time() < expires_at and not st.session_state.rerun_triggered:
                st.session_state.rerun_triggered = True
                st.success("🔄 Login successful! Reloading dashboard...")
                time.sleep(1)
                st.rerun()

    st.stop()

st.set_page_config(page_title="TrainWise", layout="wide")
st.title("🏊🚴🏃 TrainWise - Your AI Coach")

if "rerun_triggered" not in st.session_state:
    st.session_state.rerun_triggered = False

# --- Token logic ---
token_path = "tokens/strava_token.json"
token_valid = False
token_data = {}

if os.path.exists(token_path):
    with open(token_path) as f:
        token_data = json.load(f)
        expires_at = token_data.get("expires_at", 0)
        token_valid = time.time() < expires_at

# --- Not connected yet ---
if not token_valid:
    st.warning("⚠️ You are not connected to Strava or your token has expired.")
    st.markdown("""
    <a href='http://localhost:8000/strava/login' target='_self'>
        <button style='font-size:16px; padding:10px 20px; background-color:#f63366; color:white; border:none; border-radius:6px;'>
            🔐 Connect with Strava
        </button>
    </a>
    """, unsafe_allow_html=True)


    # If token is now valid after returning from login
    if os.path.exists(token_path):
        with open(token_path) as f:
            token_data = json.load(f)
            expires_at = token_data.get("expires_at", 0)
            if time.time() < expires_at and not st.session_state.rerun_triggered:
                st.session_state.rerun_triggered = True
                st.success("🔄 Login successful! Reloading dashboard...")
                time.sleep(1)
                st.rerun()

    st.stop()

# --- Athlete info ---
athlete = token_data.get("athlete", {})
first_name = athlete.get("firstname", "Athlete")
profile_url = athlete.get("profile", "")

st.markdown(f"### 👋 Welcome, {first_name}!")
if profile_url and not profile_url.endswith("avatar/athlete/large.png"):
    st.image(profile_url, width=100)

# --- Fetch activities from API ---
try:
    response = requests.get("http://localhost:8000/strava/sync")
    data = response.json()

    if isinstance(data, list):
        df = pd.DataFrame(data)
        st.success(f"✅ {len(df)} activities loaded")

        df["distance_km"] = df["distance"] / 1000
        df = df.sort_values("start_date", ascending=False)

        # Group by type
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
        st.error("❌ Failed to load activities from the API.")
        st.json(data)

except Exception as e:
    st.error("🚫 Could not connect to the FastAPI backend.")
    st.exception(e)
