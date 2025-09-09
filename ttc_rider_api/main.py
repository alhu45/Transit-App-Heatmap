# ttc_rider_api/main.py
from typing import List, Optional, Tuple
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Your existing schemas (kept)
from ttc_rider_api.app.schemas import (
    PredictRequest, PredictResponse, PredictResponseItem
)

# Model loader and batch predictor (kept)
from ttc_rider_api.model import load_model, predict_batch

# Shared utilities: service-hour rule (NEW – we use the same rule at inference)
from ttc_rider_api.transformers import is_service_hour

# -----------------------------------------------------------
# App + model bootstrap
# -----------------------------------------------------------
app = FastAPI(title="TTC Ridership API", version="0.1.0")

MODEL, META = load_model()

# -----------------------------------------------------------
# Helpers (NEW): parse human time strings -> (hour, minute)
# Accepts "3:05 PM", "3 PM", "15:05", "15"
# -----------------------------------------------------------
TIME_INPUT_FORMATS = [
    "%I:%M %p",  # "3:05 PM"
    "%I %p",     # "3 PM"
    "%H:%M",     # "15:05"
    "%H",        # "15"
]

def parse_time_to_hour_min(s: str) -> Optional[Tuple[int, int]]:
    """Try several common formats; return (hour, minute) in 24h if parsed, else None."""
    if s is None:
        return None
    s = s.strip()
    for fmt in TIME_INPUT_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.hour, dt.minute
        except ValueError:
            continue
    return None

# -----------------------------------------------------------
# POST /predict  (kept): uses your existing schemas
# NEW: adds service-hours guard to return 0 when closed
# -----------------------------------------------------------
@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Accepts either a single PredictRecord or a list (as defined in schemas.py).
    Returns 0 riders for hours outside TTC service window (fast guardrail).
    """
    recs = request.records if isinstance(request.records, list) else [request.records]
    items: List[PredictResponseItem] = []

    for r in recs:
        # API guardrail: If outside service hours, return 0 (model won't be called)
        # Simple policy: service if hour in {6..23, 0, 1}
        if not is_service_hour(int(r.hour)):
            riders = 0.0
        else:
            # Convert the Pydantic object to a dict and call the model
            payload = r.model_dump()  # pydantic v2
            # NOTE: Your training pipeline can use an optional 'minute' column.
            # If you later add 'minute' to schemas.py, it will be picked up here automatically.
            yhat = predict_batch(MODEL, [payload])[0]
            riders = float(yhat)

        items.append(PredictResponseItem(
            station=r.station,
            line=r.line,
            hour=r.hour,
            day_type=r.day_type,
            riders=riders
        ))

    return PredictResponse(
        model_version=META.get("model_version", "unknown"),
        predictions=items
    )

# -----------------------------------------------------------
# POST /predict_time (NEW): accepts a human time string
# Does NOT require changing your existing schemas.py
# -----------------------------------------------------------
class PredictTimeRecord(BaseModel):
    """
    Minimal request model for human time strings (no change to schemas.py needed).
    Example time strings: "5:30 am", "3 PM", "15:05".
    """
    station: str = Field(..., description="Station name as in training data")
    line: str = Field(..., description="Line label, e.g., 'Line 1'")
    day_type: str
    time: str = Field(..., description="e.g., '12:35 am', '3:00 pm', '15:05'")

class PredictTimeRequest(BaseModel):
    records: List[PredictTimeRecord] | PredictTimeRecord

@app.post("/predict_time", response_model=PredictResponse)
def predict_time(request: PredictTimeRequest):
    """
    Same as /predict but 'time' can be a human string.
    We parse it -> (hour, minute), enforce service hours, then call the model.
    """
    recs = request.records if isinstance(request.records, list) else [request.records]
    items: List[PredictResponseItem] = []

    for r in recs:
        hm = parse_time_to_hour_min(r.time)
        if hm is None:
            raise HTTPException(status_code=422, detail=f"Unrecognized time format: {r.time!r}")
        hour, minute = hm

        # Guardrail on service hours
        if not is_service_hour(int(hour)):
            riders = 0.0
        else:
            # Build payload for the model. The cleaner in your pipeline can use 'minute'
            payload = {
                "station": r.station,
                "line": r.line,
                "day_type": r.day_type,
                "hour": int(hour),
                "minute": int(minute),  # leveraged by your pipeline's cyclic time features (if present)
            }
            yhat = predict_batch(MODEL, [payload])[0]
            riders = float(yhat)

        items.append(PredictResponseItem(
            station=r.station,
            line=r.line,
            hour=int(hour),
            day_type=r.day_type,
            riders=riders
        ))

    return PredictResponse(
        model_version=META.get("model_version", "unknown"),
        predictions=items
    )

# -----------------------------------------------------------
# GET /options (NEW): safe unique values from CSV for UI dropdowns
# -----------------------------------------------------------
@app.get("/options")
def get_options():
    """
    Return valid input values the model was trained on.
    Reads from the CSV to avoid drift between UI and model, with NaN-safe coercions.
    """
    df = pd.read_csv("TTC_Ridership_Long_Format.csv")
    return {
        "hours": list(range(24)),
        "day_types": sorted(
            df["day_type"].dropna().astype(str).str.lower().str.strip().unique().tolist()
        ),
        "stations": sorted(
            df["station"].dropna().astype(str).str.strip().unique().tolist()
        ),
        "lines": sorted(
            df["line"].dropna().astype(str).str.strip().unique().tolist()
        ),
    }

# -----------------------------------------------------------
# Simple health check (kept)
# -----------------------------------------------------------
@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "model_version": META.get("model_version", "unknown")
    }
