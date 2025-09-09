# Helper module for the API to load the pipeline and call these functiosn so you don't have to repeat this logic in the endpoint

from pathlib import Path
import joblib, json # loads model
import pandas as pd

ARTIFACTS = Path("artifacts")
MODEL_PATH = ARTIFACTS / "model.joblib"
META_PATH  = ARTIFACTS / "meta.json"

def load_model():
    model = joblib.load(MODEL_PATH) # loads model 
    meta = {"model_version": "unknown"} # incase the labelling of metadata does not exist 

    # if model exists, read the json metadata
    if META_PATH.exists():
        meta = json.loads(META_PATH.read_text())
    return model, meta

def predict_batch(model, records: list[dict]) -> list[float]:
    # records: [{"station":..., "line":..., "hour":..., "day_type":...}, ...]
    df = pd.DataFrame(records, columns=["station", "line", "hour", "day_type"])
    preds = model.predict(df)
    return preds.tolist()
