import json
import os

TOKEN_PATH = "tokens/strava_token.json"

def save_tokens(tokens: dict):
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(tokens, f, indent=4)
    print("✅ Tokens saved to", TOKEN_PATH)

def load_tokens():
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH, "r") as f:
        return json.load(f)
