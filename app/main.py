from fastapi import FastAPI
from app.api import strava

app = FastAPI(title="TrainWise API", version="0.1.0")

# Register routes
app.include_router(strava.router, prefix="/strava", tags=["Strava"])
