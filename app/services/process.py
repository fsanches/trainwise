def process_activities(activities):
    if not activities:
        return {"total_activities": 0, "metrics": {}, "activities_by_type": {}}

    cleaned = [clean_activity(a) for a in activities]
    return {
        "total_activities": len(cleaned),
        "metrics": calculate_metrics(cleaned),
        "activities_by_type": group_by_type(cleaned)
    }

def clean_activity(a):
    distance = a.get("distance", 0) / 1000
    time = a.get("moving_time", 0)
    return {
        "id": a.get("id"),
        "type": a.get("type"),
        "distance": distance,
        "moving_time": time,
        "pace": (time / 60 / distance) if distance else 0
    }

def calculate_metrics(activities):
    total = sum(a["distance"] for a in activities)
    return {
        "total_distance": round(total, 2),
        "average_pace": round(sum(a["pace"] for a in activities) / len(activities), 2)
    }

def group_by_type(activities):
    result = {}
    for a in activities:
        t = a["type"]
        if t not in result:
            result[t] = {"count": 0, "total_distance": 0}
        result[t]["count"] += 1
        result[t]["total_distance"] += a["distance"]
    return result
