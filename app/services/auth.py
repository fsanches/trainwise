import os
import requests
from dotenv import load_dotenv
from app.services.token_store import load_tokens, save_tokens

load_dotenv()

def authenticate():
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")

    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        print("❌ No valid refresh token found.")
        return None

    refresh_token = tokens["refresh_token"]
    print("🔄 Refreshing access token...")

    try:
        response = requests.post("https://www.strava.com/oauth/token", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        })

        response.raise_for_status()
        new_tokens = response.json()
        save_tokens(new_tokens)
        print("✅ Token refreshed.")
        return new_tokens

    except requests.exceptions.RequestException as e:
        print(f"❌ Auth error: {e}")
        return None
