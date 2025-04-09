import requests
import time

def fetch_activities(access_token: str, limit: int = 30, days: int = 365) -> list:
    """
    Fetches activities from the Strava API within the last `days`.

    Args:
        access_token (str): Strava access token.
        limit (int): Number of activities to fetch (max 100).
        days (int): Time range in days to filter activities.

    Returns:
        list: List of activity dictionaries or empty list on error.
    """
    if not access_token:
        print("❌ Error: Access token is missing.")
        return []

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = "https://www.strava.com/api/v3/athlete/activities"

    now = int(time.time())
    after = now - (days * 24 * 60 * 60)

    params = {
        "per_page": min(limit, 100),
        "page": 1,
        "after": after
    }

    print("🔍 Requesting activities from Strava...")
    print(f"🔗 URL: {url}")
    print(f"📦 Params: {params}")

    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"🔍 Status code: {response.status_code}")
        print(f"🧾 Raw response: {response.text[:200]}...")  # Preview first 200 chars

        response.raise_for_status()
        activities = response.json()
        print(f"✅ Successfully fetched {len(activities)} activities.")
        return activities

    except requests.exceptions.RequestException as e:
        print("❌ Fetch error:", e)
        return []
