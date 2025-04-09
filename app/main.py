from fastapi import FastAPI
from app.api import strava
from app.api import intervals

app = FastAPI(title="TrainWise API", version="0.1.0")

# Register routes
app.include_router(strava.router, prefix="/strava", tags=["Strava"])
app.include_router(intervals.router)