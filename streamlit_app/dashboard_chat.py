import streamlit as st
import requests
import pandas as pd
import os
import json
import time
from datetime import datetime, timedelta, timezone
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
from app.insights.performance import evolution_summary
from app.insights.cardio import detect_fatigue
from app.insights.planning import predict_next_week
from app.insights.modality import swim_consistency, run_consistency, bike_consistency


# --- Load environment and OpenAI client ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Setup UI ---
st.set_page_config(page_title="TrainWise", layout="wide")
st.title("🧠💬 TrainWise - Your AI Coach")

# --- Token check and login flow ---
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
                st.success("🔄 Login successful! Reloading chat...")
                time.sleep(1)
                st.rerun()

    st.stop()

# --- Athlete info ---
athlete = token_data.get("athlete", {})
first_name = athlete.get("firstname", "Athlete")
profile_url = athlete.get("profile", "")
if profile_url.endswith("avatar/athlete/large.png"):
    profile_url = ""

st.markdown(f"### 👋 Welcome, {first_name}!")
if profile_url:
    st.image(profile_url, width=100)

# --- Load plan ---
@st.cache_data
def load_intervals_plan():
    try:
        response = requests.get("http://localhost:8000/intervals/plan")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- Load activities ---
@st.cache_data
def load_activities():
    try:
        response = requests.get("http://localhost:8000/strava/sync")
        return response.json()
    except Exception as e:
        return []

activities = load_activities()

# --- Weekly summary for context ---
def summarize_week(activities: list) -> str:
    if not activities:
        return "No activities found this week."

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)

    recent = [
        a for a in activities 
        if datetime.strptime(a["start_date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) > one_week_ago
    ]

    if not recent:
        return "No activities in the past 7 days."

    summary = {}
    total_distance = 0
    total_time = 0

    for a in recent:
        activity_type = a["type"]
        summary[activity_type] = summary.get(activity_type, 0) + 1
        total_distance += a.get("distance", 0)
        total_time += a.get("moving_time", 0)

    total_distance_km = round(total_distance / 1000, 1)
    total_time_hours = round(total_time / 3600, 1)

    activity_summary = ", ".join(f"{count} {atype.lower()}(s)" for atype, count in summary.items())
    return f"This week: {activity_summary}, total distance {total_distance_km} km in {total_time_hours} hours."

# --- Generate AI week intro ---
def generate_week_intro(activities: list) -> str:
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)

    recent = [
        a for a in activities
        if datetime.strptime(a["start_date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) > one_week_ago
    ]

    if not recent:
        return "Hi! I haven’t seen any activities from you this week. Ready to train? 🏋"

    intro = "👀 Here's what I noticed in your week:\n"
    for a in recent:
        title = a.get("name", "Untitled")
        distance_km = round(a.get("distance", 0) / 1000, 2)
        duration_min = a.get("moving_time", 1) / 60
        hr = a.get("average_heartrate", "–")

        if a.get("type") == "Swim":
            distance_100m = a.get("distance", 0) / 100
            pace = duration_min / (distance_100m or 1)
            pace_min = int(pace)
            pace_sec = int(round((pace - pace_min) * 60))
            pace_str = f"{pace_min}:{pace_sec:02d} min/100m"
        else:
            pace = duration_min / (distance_km or 1)
            pace_min = int(pace)
            pace_sec = int(round((pace - pace_min) * 60))
            pace_str = f"{pace_min}:{pace_sec:02d} min/km"

        intro += f"- **{title}**: {distance_km} km, pace {pace_str}, Avg HR {hr} bpm\n"
    return intro

# --- Generate AI response ---
def generate_ai_response(prompt: str, activity_summary: str) -> str:
    df = pd.DataFrame(activities)

    # Parse dates with UTC awareness
    df["start_date"] = pd.to_datetime(df["start_date"], utc=True)
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    df = df[df["start_date"] > one_week_ago]

    # Derived metrics
    df["distance_km"] = df["distance"] / 1000
    df["pace_min_km"] = (df["moving_time"] / 60) / df["distance_km"]

    df.loc[df["type"] == "Swim", "pace_swim_min_100m"] = (
        (df["moving_time"] / 60) / (df["distance"] / 100)
    )

    # Build context
    context = f"""
        Weekly Summary:
        {summarize_week(activities)}

        Performance Trend:
        {evolution_summary(df)}

        Fatigue Check:
        {detect_fatigue(df)}

        Next Week Prediction:
        {predict_next_week(df)}

        Swim Consistency:
        {swim_consistency(df)}

        Run Consistency:
        {run_consistency(df)}

        Bike Consistency:
        {bike_consistency(df)}
    """

    system_prompt = (
        "You are a professional triathlon coach. Use the athlete's training context to respond with feedback "
        "or suggestions for training improvement. Using short bullet points.\n\n"
        f"Context: {context}"
    )

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8
    )

    return response.choices[0].message.content.strip()  # type: ignore


# --- Chat session ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": generate_week_intro(activities)})

coach_avatar = "https://cdn-icons-png.flaticon.com/512/4712/4712106.png"
weekly_summary = summarize_week(activities)

# --- Show chat history ---
for msg in st.session_state.messages:
    avatar = profile_url if msg["role"] == "user" else coach_avatar
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Handle user input ---
if prompt := st.chat_input("Ask your AI Coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=profile_url):
        st.markdown(prompt)

    response = generate_ai_response(prompt, weekly_summary)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant", avatar=coach_avatar):
        st.markdown(response)