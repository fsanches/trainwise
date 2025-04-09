# 📁 app/services/intervals.py
import json
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("INTERVALS_API_KEY")

HEADERS = {"Authorization": f"Basic {API_KEY}"}

def get_training_plan():
    url = "https://intervals.icu/api/v1/athlete/0/training-plan"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_this_week_plan():
    all_sessions = get_training_plan()

    # Defensive: ensure we parse a JSON object if it came as string
    if isinstance(all_sessions, str):
        try:
            all_sessions = json.loads(all_sessions)
        except Exception:
            raise ValueError("Invalid JSON returned by API")

    now = datetime.now()
    start_week = now - timedelta(days=now.weekday())
    end_week = start_week + timedelta(days=7)

    this_week = []
    for s in all_sessions:
        try:
            if isinstance(s, dict) and "date" in s:
                date_obj = datetime.strptime(s["date"], "%Y-%m-%d").date()
                if start_week.date() <= date_obj < end_week.date():
                    this_week.append(s)
        except Exception as e:
            print(f"Skipping invalid session entry: {s} -- {e}")
            continue

    if not this_week:
        return {"message": "No planned workouts found for this week."}

    return this_week
