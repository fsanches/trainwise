from fastapi import APIRouter, Request
from app.services.auth import authenticate
from app.services.fetch import fetch_activities
from app.services.process import process_activities
from app.services.token_store import save_tokens, load_tokens
from fastapi.responses import RedirectResponse


import os
import requests
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")

from fastapi import APIRouter
from app.services.auth import authenticate
import requests
import time

router = APIRouter()

@router.get("/sync")
def sync_activities():
    tokens = authenticate()
    if not tokens:
        return {"error": "Failed to authenticate with Strava"}

    access_token = tokens.get("access_token")
    if not access_token:
        return {"error": "Access token missing"}

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "per_page": 30,
        "page": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()  # 👉 retorna o JSON bruto

    except requests.exceptions.RequestException as e:
        return {
            "error": "Failed to fetch activities",
            "detail": str(e),
            "status": getattr(e.response, "status_code", "unknown")
        }

@router.get("/callback")
def handle_strava_callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error or not code:
        return {"error": "Authorization failed", "detail": error}

    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code"
    })

    if response.status_code != 200:
        return {"error": "Failed to get token", "detail": response.text}

    tokens = response.json()
    save_tokens(tokens)
    
    return {
        "message": "✅ Token received!",
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": tokens["expires_at"]
    }


@router.get("/login")
def login_with_strava():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "read,activity:read_all",
        "approval_prompt": "force"
    }
    url = f"https://www.strava.com/oauth/authorize?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return RedirectResponse(url)

@router.get("/me")
def get_athlete_profile():
    tokens = load_tokens()
    if not tokens or "access_token" not in tokens:
        return {"error": "No valid token found. Please login first."}

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}"
    }

    try:
        response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "error": "Failed to fetch athlete profile",
            "detail": str(e),
            "strava_response": e.response.text if e.response else "No response"
        }