import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer  
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.impute import SimpleImputer  
import joblib, json, time
from pathlib import Path
from ttc_rider_api.transformers import clean_df, is_service_hour
from datetime import datetime
import re
import matplotlib.pyplot as plt

# This function helps tranform "messy" hour formats and coerce them into 24 hour
def _coerce_hour_minute(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    raw = series.astype(str)
    norm = (raw.str.lower()
                 .str.strip()
                 .str.replace("\u2013", "-", regex=False)  
                 .str.replace("\u2014", "-", regex=False)  
                 .str.replace("\u2212", "-", regex=False)  
                 .str.replace(".", "", regex=False)        
                 .str.replace(r"\s+", " ", regex=True))    

    hour = pd.Series(np.nan, index=norm.index, dtype="float64")
    minute = pd.Series(np.nan, index=norm.index, dtype="float64")

    # Ranges such as 7-8pm changes to 19:00
    mask = hour.isna()
    if mask.any():
        m = norm[mask].str.extract(r"^\s*(\d{1,2})\s*-\s*(\d{1,2})\s*(am|pm)\s*$")
        ok = m[0].notna() & m[2].notna()
        if ok.any():
            start = pd.to_numeric(m.loc[ok, 0], errors="coerce")
            ampm = m.loc[ok, 2]
            def _h12_to_24(h, ap):
                h = int(h)
                if ap == "am":
                    return 0 if h == 12 else h
                else:  # pm
                    return 12 if h == 12 else h + 12
            conv = [ _h12_to_24(h, ap) if pd.notna(h) else np.nan for h, ap in zip(start, ampm) ]
            hour.loc[start.index] = conv
            minute.loc[start.index] = 0

    # 12 Hour Clock
    mask = hour.isna()
    if mask.any():
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
    
    # 24 Hour Clock 
    mask = hour.isna()
    if mask.any():
        m = norm[mask].str.extract(r"^\s*(\d{1,2})\s*:\s*(\d{1,2})\s*$")
        ok = m[0].notna() & m[1].notna()
        if ok.any():
            hh = pd.to_numeric(m.loc[ok, 0], errors="coerce")
            mm = pd.to_numeric(m.loc[ok, 1], errors="coerce")
            hour.loc[hh.index] = hh
            minute.loc[mm.index] = mm.clip(lower=0, upper=59)

    # Plain Integer Hour like "7"
    mask = hour.isna()
    if mask.any():
        hh = pd.to_numeric(norm[mask], errors="coerce")
        hour.loc[hh.index] = hh
        minute.loc[hh.index] = minute.loc[hh.index].fillna(0)

    minute = minute.clip(lower=0, upper=59)

    return hour, minute
#----------------------------------------------------------------------------------------------------------------------------
def most_common_line_for_station(df_like: pd.DataFrame, station_name: str) -> str:
    s_l = df_like[df_like["station"].astype(str).str.strip().str.lower() == station_name.lower()]
    if not s_l.empty and s_l["line"].notna().any():
        return s_l["line"].mode().iloc[0]
    # fallback: most common line overall
    return df_like["line"].mode().iloc[0]

def hourly_profile_dataframe(station: str, line: str, day_type: str) -> pd.DataFrame:
    # Build whole-hour grid that respects start time for the given day_type
    hours = hours_for_daytype(day_type)
    grid = pd.DataFrame({
        "station": [station] * len(hours),
        "line":    [line] * len(hours),
        "day_type":[day_type] * len(hours),
        "hour":    hours,
        "minute":  [0] * len(hours),
    })
    # Ensure exact rule (keeps 01:00, drops 02:00+)
    return grid[service_open_mask(grid)]

def plot_station_day(pipe, station: str, line: str, day_type: str):
    grid = hourly_profile_dataframe(station, line, day_type)
    preds = pipe.predict(grid)
    fig = plt.figure()
    plt.plot(grid["hour"], preds, marker="o")
    plt.title(f"{station} — Estimated riders by hour ({day_type.title()})")
    plt.xlabel("Hour of day (24h)")
    plt.ylabel("Predicted riders")
    plt.xticks(range(0,24,2))
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()
#----------------------------------------------------------------------------------------------------------------------------

# Open Subway Hours Logic
WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday", "friday"}
WEEKENDS = {"saturday", "sunday"}

# This function helps determine the open hour rows within the excel spreadsheet
def service_open_mask(df_like: pd.DataFrame) -> pd.Series:
    """
    Row-aware mask using day_type, hour, and minute.
    Mon–Fri: open 06:00–23:59 same day + 00:00–01:30 next day
    Sat–Sun: open 08:00–23:59 same day + 00:00–01:30 next day
    """
    day = df_like["day_type"].astype(str).str.strip().str.lower()
    h = pd.to_numeric(df_like["hour"], errors="coerce")
    m = pd.to_numeric(df_like.get("minute", 0), errors="coerce").fillna(0)

    # start hour depends on weekday/weekend
    start_hour = np.where(day.isin(list(WEEKDAYS)), 6, 8)

    same_day_open = (h >= start_hour) & (h <= 23)
    after_midnight_open = (h == 0) | ((h == 1) & (m <= 30))

    return same_day_open | after_midnight_open

def hours_for_daytype(day_type: str) -> list[int]:
    """Whole-hour samples for plotting (01:00 included; 02:00 excluded)."""
    start = 6 if day_type.lower() in WEEKDAYS else 8
    return list(range(start, 24)) + [0, 1]

# Opens DF
df = pd.read_csv("TTC_Ridership_Long_Format.csv")

# Basic cleaning / normalization see everything uppercase or lowercase is treated the same
df["day_type"] = df["day_type"].str.lower().str.strip()
df["station"] = df["station"].str.strip()
df["line"] = df["line"].str.strip()

# Features & target
X = df[["station", "line", "hour", "day_type"]].copy()  # copy to avoid view issues
y = df["riders"].astype(float) # Y value is the value we want to predict

# Using the function I created, standardizes time
hours, minutes = _coerce_hour_minute(X["hour"])
X["hour"] = hours
X["minute"] = minutes.fillna(0)

# Debug prints to see what's in your data
# print("DEBUG — first 12 raw hour values:", df["hour"].head(12).tolist())
# parsed_hours_sample = pd.to_numeric(X["hour"], errors="coerce").dropna().unique().tolist()
# try:
#     parsed_hours_sample = sorted(parsed_hours_sample)[:40]
# except TypeError:
#     parsed_hours_sample = parsed_hours_sample[:40]
# print("DEBUG — parsed unique hours (sorted, sample):", parsed_hours_sample)
# print("DEBUG — rows before service-hours filter:", len(X))

# Drop rows where hour couldn't be parsed at all
X = X.dropna(subset=["hour"])
y = y.loc[X.index].copy()

# Filter to TTC service hours ONLY (day-aware; handles the 01:30 cutoff)
mask = service_open_mask(X)
n_before = len(X)
n_after = int(mask.sum())
print(f"DEBUG — rows after service-hours filter: {n_after} (from {n_before})")

if n_after == 0:
    print("WARNING — service-hours filter removed all rows. Falling back to [0..23].")
    mask = X["hour"].between(0, 23, inclusive="both")

X = X[mask]
y = y[mask]


if len(X) == 0:
    raise RuntimeError(
        "No rows left after hour parsing and fallback filter. "
        "Check the 'hour' column format in the CSV — see DEBUG printouts above."
    )

# Model pipeline
cleaner = FunctionTransformer(clean_df) # Gets df from the transformer from the user
cat_features = ["station", "line", "day_type"]  # Categorical pipeline 
num_features = ["tod_sin", "tod_cos"] # Number pipeline   

cat_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),    
    ("ohe", OneHotEncoder(handle_unknown="ignore")),
])

num_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="mean")),        
])

pre = ColumnTransformer(
    transformers=[
        ("cat", cat_pipeline, cat_features),
        ("num", num_pipeline, num_features),
    ]
)

pipe = Pipeline(steps=[
    ("clean", cleaner),   
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

# === Visualization for Finch: Monday & Sunday ===
station_name = "Union"
line = most_common_line_for_station(X_train.assign(station=X_train["station"]),
                                              station_name=station_name)

# Monday
plot_station_day(pipe, station_name, line, day_type="monday")

# Sunday
plot_station_day(pipe, station_name, line, day_type="sunday")
