# 📁 app/insights/cardio.py
import pandas as pd


def detect_fatigue(df: pd.DataFrame) -> str:
    try:
        if 'average_heartrate' not in df or 'pace_min_km' not in df:
            return "No HR or pace data available."
        fatigue = df[(df['average_heartrate'] > 150) & (df['pace_min_km'] > 6)]
        if not fatigue.empty:
            return f"🚨 Fatigue indicators detected in {len(fatigue)} sessions."
        return "✅ No fatigue patterns detected."
    except Exception:
        return "Could not evaluate fatigue."