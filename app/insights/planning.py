# 📁 app/insights/planning.py
import pandas as pd


def predict_next_week(df: pd.DataFrame) -> str:
    try:
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['week'] = df['start_date'].dt.isocalendar().week
        weekly_volume = df.groupby('week')['distance'].sum()
        if len(weekly_volume) < 2:
            return "Not enough data to predict next week."
        last = weekly_volume.iloc[-1]
        prev = weekly_volume.iloc[-2]
        trend = (last - prev) / prev * 100
        direction = "increase" if trend > 0 else "decrease"
        return f"📈 Predicted {direction} of {abs(trend):.1f}% in volume next week."
    except Exception:
        return "Prediction not available."