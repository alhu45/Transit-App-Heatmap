# Helper module for the API to load the pipeline and call these functions so you don't have to repeat this logic in the endpoint

from pathlib import Path
import joblib, json # loads model
import pandas as pd

ARTIFACTS = Path("artifacts")
MODEL_PATH = ARTIFACTS / "model.joblib"
META_PATH  = ARTIFACTS / "meta.json"
# print(f"[DEBUG] MODEL_PATH.resolve() = {MODEL_PATH.resolve()}")


def load_model():
    model = joblib.load(MODEL_PATH) # loads model 
    meta = {"model_version": "unknown"} # incase the labelling of metadata does not exist 

    # if model exists, read the json metadata
    if META_PATH.exists():
        meta = json.loads(META_PATH.read_text())
    return model, meta

def predict_batch(model, records: list[dict]) -> list[float]:
    df = pd.DataFrame(records)

    print("\n[DEBUG] DataFrame going into model:")
    print(df)
    print(df.dtypes)
    print("----------------------------\n")


    preds = model.predict(df)
    return preds.tolist()
