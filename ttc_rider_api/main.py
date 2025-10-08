# To start FastAPI: uvicorn ttc_rider_api.main:app

from typing import List, Optional, Tuple
from datetime import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ttc_rider_api.model import load_model, predict_batch

app = FastAPI(title="TTC Ridership API", version="0.2.0")
MODEL, META = load_model()

# TTC Service Hours
def is_service_hour(hour: int, day: str) -> bool:
    """Return True if TTC is open for the given hour/day."""
    day = day.lower()
    if day in ["saturday", "sunday"]:
        # Weekends: open 8 AM – 1 AM next day
        return (8 <= hour <= 23) or (hour in [0, 1])
    else:
        # Weekdays: open 6 AM – 1 AM next day
        return (6 <= hour <= 23) or (hour in [0, 1])

# Request/response models
class PredictRecord(BaseModel):
    station: str
    line: str
    day: str
    hour: int


class PredictRequest(BaseModel):
    records: List[PredictRecord] | PredictRecord


class PredictResponseItem(BaseModel):
    station: str
    line: str
    hour: int
    day: str
    riders: float


class PredictResponse(BaseModel):
    model_version: str
    predictions: List[PredictResponseItem]

# POST /predict
@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    recs = request.records if isinstance(request.records, list) else [request.records]
    items: List[PredictResponseItem] = []

    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    for r in recs:
        day = r.day.lower().strip()
        hour = int(r.hour)
        is_weekend = 1 if day in ["saturday", "sunday"] else 0

        if not is_service_hour(hour, day):
            riders = 0.0
        else:
            payload = {
                "station": r.station.strip(),
                "line": r.line.strip(),
                "day": day,
                "hour": hour,
                "minute": 0,
                "is_weekend": is_weekend
            }
            yhat = predict_batch(MODEL, [payload])[0]
            riders = float(yhat)

        items.append(PredictResponseItem(
            station=r.station.strip(),
            line=r.line.strip(),
            hour=hour,
            day=day,
            riders=riders
        ))

    return PredictResponse(
        model_version=META.get("model_version", "unknown"),
        predictions=items
    )

# GET /options — metadata for dropdowns or UIs
@app.get("/options")
def get_options():
    df = pd.read_csv("Ridership_Data.csv")
    return {
        "hours": list(range(24)),
        "days": sorted(df["Day"].dropna().astype(str).str.lower().str.strip().unique().tolist()),
        "stations": sorted(df["Station"].dropna().astype(str).str.strip().unique().tolist()),
        "lines": sorted(df["Line"].dropna().astype(str).str.strip().unique().tolist()),
    }

# GET /health
@app.get("/health")
def healthz():
    """Health check and model info."""
    return {
        "status": "ok",
        "model_version": META.get("model_version", "unknown")
    }
