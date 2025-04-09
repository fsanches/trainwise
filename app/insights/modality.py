# 📁 app/insights/modality.py
import pandas as pd

def swim_consistency(df: pd.DataFrame) -> str:
    try:
        swims = df[df['type'] == 'Swim']
        if swims.empty:
            return "No swim sessions this week."
        pace = swims['pace_swim_min_100m'].mean()
        return f"🏊 {len(swims)} swim sessions this week. Avg pace: {pace:.2f} min/100m"
    except Exception:
        return "Could not analyze swim data."

def run_consistency(df: pd.DataFrame) -> str:
    try:
        runs = df[df['type'] == 'Run']
        if runs.empty:
            return "No run sessions this week."
        avg_pace = runs['pace_min_km'].mean()
        pace_std = runs['pace_min_km'].std()
        return f"🏃 {len(runs)} run sessions. Avg pace: {avg_pace:.2f} min/km (std: {pace_std:.2f})"
    except Exception:
        return "Could not analyze run consistency."


def bike_consistency(df: pd.DataFrame) -> str:
    try:
        rides = df[df['type'] == 'Ride']
        if rides.empty:
            return "No ride sessions this week."
        avg_speed = rides['average_speed'].mean()
        speed_std = rides['average_speed'].std()
        return f"🚴 {len(rides)} ride sessions. Avg speed: {avg_speed:.2f} km/h (std: {speed_std:.2f})"
    except Exception:
        return "Could not analyze ride consistency."