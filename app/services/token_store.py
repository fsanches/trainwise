import os
import json

TOKEN_PATH = "tokens/strava_token.json"

def save_tokens(new_data: dict):
    # Preserve existing athlete data if available
    athlete_data = {}

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "r") as f:
            existing = json.load(f)
            athlete_data = existing.get("athlete", {})

    # Replace athlete data if present in the new token
    if "athlete" in new_data:
        athlete_data = new_data["athlete"]

    # Save token + athlete together in a single file
    final = {
        "access_token": new_data["access_token"],
        "refresh_token": new_data["refresh_token"],
        "expires_at": new_data["expires_at"],
        "athlete": athlete_data
    }

    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(final, f, indent=4)
    
    print("✅ Tokens saved to", TOKEN_PATH)


def load_tokens():
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH, "r") as f:
        return json.load(f)