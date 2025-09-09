import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer  # NEW: FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.impute import SimpleImputer  # NEW: imputer so OHE and numerics never see NaN
import joblib, json, time
from pathlib import Path

# NEW: shared cleaner (picklable) + service-hour rule
from ttc_rider_api.transformers import clean_df, is_service_hour

# ------------------------- NEW: helpers to robustly parse hour/minute -------------------------
from datetime import datetime
import re

def _coerce_hour_minute(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    Parse hour/minute from messy strings.

    Supports:
      - "6–7 a.m.", "7-8 p.m.", "12–1 am"  (range; uses START hour)
      - "8 AM", "3 PM", "12:35 am", "3pm"
      - "08:00", "20:15" (24h)
      - "8", "15"       (hour only)

    Returns (hour_series, minute_series) as float dtype (NaN where unparseable).
    """
    raw = series.astype(str)

    # Normalize: lowercase, strip, remove dots, normalize dashes, collapse spaces
    norm = (raw.str.lower()
                 .str.strip()
                 .str.replace("\u2013", "-", regex=False)  # en dash
                 .str.replace("\u2014", "-", regex=False)  # em dash
                 .str.replace("\u2212", "-", regex=False)  # minus sign
                 .str.replace(".", "", regex=False)        # a.m. -> am
                 .str.replace(r"\s+", " ", regex=True))     # collapse spaces

    hour = pd.Series(np.nan, index=norm.index, dtype="float64")
    minute = pd.Series(np.nan, index=norm.index, dtype="float64")

    # ---------- 1) Range with am/pm: "6-7 am", "7-8 pm" ----------
    # Use the START hour as representative for the interval
    mask = hour.isna()
    if mask.any():
        m = norm[mask].str.extract(r"^\s*(\d{1,2})\s*-\s*(\d{1,2})\s*(am|pm)\s*$")
        ok = m[0].notna() & m[2].notna()
        if ok.any():
            start = pd.to_numeric(m.loc[ok, 0], errors="coerce")
            ampm = m.loc[ok, 2]
            # convert 12h -> 24h
            def _h12_to_24(h, ap):
                h = int(h)
                if ap == "am":
                    return 0 if h == 12 else h
                else:  # pm
                    return 12 if h == 12 else h + 12
            conv = [ _h12_to_24(h, ap) if pd.notna(h) else np.nan for h, ap in zip(start, ampm) ]
            hour.loc[start.index] = conv
            minute.loc[start.index] = 0

    # ---------- 2) Single am/pm: "3 pm", "12:35 am", "3pm" ----------
    mask = hour.isna()
    if mask.any():
        # allow optional :mm
        m = norm[mask].str.extract(r"^\s*(\d{1,2})(?::(\d{1,2}))?\s*(am|pm)\s*$")
        ok = m[0].notna() & m[2].notna()
        if ok.any():
            hh = pd.to_numeric(m.loc[ok, 0], errors="coerce")
            mm = pd.to_numeric(m.loc[ok, 1], errors="coerce").fillna(0)
            ap = m.loc[ok, 2]
            def _h12_to_24(h, ap):
                h = int(h)
                if ap == "am":
                    return 0 if h == 12 else h
                else:
                    return 12 if h == 12 else h + 12
            conv = [ _h12_to_24(h, a) if pd.notna(h) else np.nan for h, a in zip(hh, ap) ]
            hour.loc[hh.index] = conv
            minute.loc[mm.index] = mm.clip(lower=0, upper=59)

    # ---------- 3) 24h "HH:MM" ----------
    mask = hour.isna()
    if mask.any():
        m = norm[mask].str.extract(r"^\s*(\d{1,2})\s*:\s*(\d{1,2})\s*$")
        ok = m[0].notna() & m[1].notna()
        if ok.any():
            hh = pd.to_numeric(m.loc[ok, 0], errors="coerce")
            mm = pd.to_numeric(m.loc[ok, 1], errors="coerce")
            hour.loc[hh.index] = hh
            minute.loc[mm.index] = mm.clip(lower=0, upper=59)

    # ---------- 4) Bare numeric hour ----------
    mask = hour.isna()
    if mask.any():
        hh = pd.to_numeric(norm[mask], errors="coerce")
        hour.loc[hh.index] = hh
        minute.loc[hh.index] = minute.loc[hh.index].fillna(0)

    # final minute clamp
    minute = minute.clip(lower=0, upper=59)

    return hour, minute

# ---------------------------------------------------------------------------------------------

df = pd.read_csv("TTC_Ridership_Long_Format.csv")

# Basic cleaning / normalization see everything uppercase or lowercase is treated the same
df["day_type"] = df["day_type"].str.lower().str.strip()
df["station"] = df["station"].str.strip()
df["line"] = df["line"].str.strip()

# Features & target
X = df[["station", "line", "hour", "day_type"]].copy()  # copy to avoid view issues
y = df["riders"].astype(float) # Y value is the value we want to predict

# ------------------------- NEW: robustly parse hour/minute before filtering -------------------
# Coerce 'hour' to numeric so the service-hour filter can work (supports "8", "08:00", "3 PM", etc.)
hours, minutes = _coerce_hour_minute(X["hour"])
X["hour"] = hours
# (optional) stash minute to be used later by the cleaner's cyclical features; default to 0
X["minute"] = minutes.fillna(0)

# DEBUG prints to see what's in your data
print("DEBUG — first 12 raw hour values:", df["hour"].head(12).tolist())
parsed_hours_sample = pd.to_numeric(X["hour"], errors="coerce").dropna().unique().tolist()
try:
    parsed_hours_sample = sorted(parsed_hours_sample)[:40]
except TypeError:
    # safety if mixed types sneak in
    parsed_hours_sample = parsed_hours_sample[:40]
print("DEBUG — parsed unique hours (sorted, sample):", parsed_hours_sample)
print("DEBUG — rows before service-hours filter:", len(X))

# Drop rows where hour couldn't be parsed at all
X = X.dropna(subset=["hour"])
y = y.loc[X.index].copy()

# Filter to TTC service hours ONLY so model never learns closed hours
mask = X["hour"].apply(is_service_hour)
n_before = len(X)
n_after = int(mask.sum())
print(f"DEBUG — rows after service-hours filter: {n_after} (from {n_before})")

if n_after == 0:
    # Fallback so you can train + inspect while we figure out the hours format/rule
    print("WARNING — service-hours filter removed all rows. "
          "Falling back to keeping rows with hour in [0..23] for now.")
    mask = X["hour"].between(0, 23, inclusive="both")
    n_after = int(mask.sum())
    print(f"DEBUG — rows after fallback [0..23] filter: {n_after}")

X = X[mask]
y = y[mask]

if len(X) == 0:
    raise RuntimeError(
        "No rows left after hour parsing and fallback filter. "
        "Check the 'hour' column format in the CSV — see DEBUG printouts above."
    )
# ---------------------------------------------------------------------------------------------

# ---------- NEW: Put the SAME cleaning logic into the pipeline (train == infer) ----------
cleaner = FunctionTransformer(clean_df)

# Linear Regression cannot take strings, convert them into binary so it can be read
# ---------- NEW: We'll OneHot the categoricals and feed time-of-day sin/cos as numeric ----------
cat_features = ["station", "line", "day_type"]  # hour handled via sin/cos
num_features = ["tod_sin", "tod_cos"]           # NEW: cyclical time features

cat_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),    # NEW
    ("ohe", OneHotEncoder(handle_unknown="ignore")),
])

num_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="mean")),             # NEW: fill missing numeric
    # no scaler needed for LinearRegression but you could add StandardScaler()
])

pre = ColumnTransformer(
    transformers=[
        ("cat", cat_pipeline, cat_features),
        ("num", num_pipeline, num_features),
    ]
)

# Building pipeline: turns your text inputs (station, line, hour, day_type) into numbers and fits the model in one object
pipe = Pipeline(steps=[
    ("clean", cleaner),      # NEW: embed cleaning + sin/cos so predict-time matches train-time
    ("pre", pre),
    ("reg", LinearRegression())
])

# Train/test split
# Testing is used to give the model something to learn off of
# Tesitng is to see how well the model works with the new data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Training
pipe.fit(X_train, y_train)

# Evaluate
y_pred = pipe.predict(X_test) # predicted ridership numbers for the test set
r2  = r2_score(y_test, y_pred) # how much variation in ridership is explained by the model (1.0 = perfect fit)
rmse = np.sqrt(mean_squared_error(y_test, y_pred)) # average error size in riders
mae  = mean_absolute_error(y_test, y_pred) # average absolute error in riders

print(f"R²:  {r2:.3f}")
print(f"RMSE:{rmse:.1f}")
print(f"MAE: {mae:.1f}")

# This section saves the model and metadata so the FastAPI API can load it later on 
# Create a folder to save the model and info about it
artifacts = Path("artifacts") 
artifacts.mkdir(exist_ok=True)

# Defines model path
MODEL_PATH = artifacts / "model.joblib" # The trained model pipeline
META_PATH  = artifacts / "meta.json" # Metadata about model

# Saves Pipeline object into artifacts, where the API laods instead of retraining model every single time 
joblib.dump(pipe, MODEL_PATH)

# Info about the model
meta = {
    "model_version": time.strftime("v%Y.%m.%d.%H%M"),
    "features": ["station", "line", "day_type", "tod_sin", "tod_cos"],  # NEW
    "algo": "LinearRegression + OneHotEncoder (station/line/day) + cyclical time features",  # NEW
    "service_hours_rule": "hours in {6..23, 0, 1}; outside = closed",  # NEW
    "metrics": {"r2": float(r2), "rmse": float(rmse), "mae": float(mae)},
}

# Saves info into JSON data
META_PATH.write_text(json.dumps(meta, indent=2))

print(f"Saved model → {MODEL_PATH}")
print(f"Saved meta  → {META_PATH}")
