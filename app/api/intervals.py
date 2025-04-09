from fastapi import APIRouter
from app.services.intervals import get_this_week_plan
import requests

router = APIRouter()

@router.get("/intervals/plan")
def intervals_plan():
    try:
        return get_this_week_plan()
    except requests.RequestException as e:
        return {"error": "Failed to fetch Intervals.icu plan", "detail": str(e)}
