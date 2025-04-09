# 📁 app/insights/performance.py
import pandas as pd

def evolution_summary(df: pd.DataFrame) -> str:
    try:
        summary = df.copy()
        summary['start_date'] = pd.to_datetime(summary['start_date'])
        summary = summary[summary['type'].isin(['Run', 'Ride', 'Swim'])]
        summary['week'] = summary['start_date'].dt.isocalendar().week

        trends = summary.groupby(['week', 'type'])[['average_speed', 'moving_time']].mean().reset_index()
        result = []
        for t in ['Run', 'Ride', 'Swim']:
            trend = trends[trends['type'] == t]
            if len(trend) >= 2:
                last = trend.iloc[-1]['average_speed']
                prev = trend.iloc[-2]['average_speed']
                diff = round(last - prev, 2)
                change = "increased" if diff > 0 else "decreased"
                result.append(f"{t}: speed {change} by {abs(diff):.2f} km/h")
        return "\n".join(result) if result else "Not enough data to show performance trend."
    except Exception:
        return "Could not compute performance evolution."
