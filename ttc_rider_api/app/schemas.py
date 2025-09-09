# What is schemas.py?
# Think of schemas.py as:
# Blueprints (contracts) for your API:
# “When someone calls /predict, this is the shape of the request body I expect.”
# “When I respond, this is the shape of the response I promise back.”
# Automatic error catcher:
# If the caller sends a bad request (hour: 50, missing station, wrong type, etc.), FastAPI won’t even run your function—it automatically returns a 422 with a helpful error message.
# That saves you from writing manual if checks.
# Docs generator:
# FastAPI reads those schemas and builds the interactive Swagger UI at /docs, where you (or anyone) can test requests and see example payloads.

from typing import List, Union
from pydantic import BaseModel, Field, conint

# Input record model, defines what one prediction model will look like 
class PredictRecord(BaseModel):
    station: str = Field(..., description="Station name as in training data")
    line: str = Field(..., description="Line label, e.g., 'Line 1'")
    hour: conint(ge=0, le=23)  # 0–23
    day_type: str              # e.g., 'weekday' or 'weekend'

# Wrapper schema for input request body (one or many records).
class PredictRequest(BaseModel):
    records: Union[PredictRecord, List[PredictRecord]]

# Response item mdoel, echoes the prediction back
class PredictResponseItem(BaseModel):
    station: str
    line: str
    hour: int
    day_type: str
    riders: float

# Wrapper schema for output response body (includes model version + predictions list).
class PredictResponse(BaseModel):
    model_version: str
    predictions: List[PredictResponseItem]

# Summary:
# PredictRecord = schema for input row.
# PredictRequest = wrapper schema for input request body (one or many records).
# PredictResponseItem = schema for one prediction output.
# PredictResponse = wrapper schema for output response body (includes model version + predictions list).
# Basically, this is how your API validates inputs and structures outputs so that:
# You don’t get invalid data (e.g., hour = 25 will be rejected automatically).
# Consumers of your API know exactly what format to expect.