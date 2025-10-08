import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer  
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.impute import SimpleImputer  
import joblib, json, time
from pathlib import Path
import matplotlib.pyplot as plt

# New ML Model: XGBoost
from xgboost import XGBRegressor

# Functions to graph our results 
#----------------------------------------------------------------------------------------------------------------------------
def most_common_line_for_station(df_like: pd.DataFrame, station_name: str) -> str:
    s_l = df_like[df_like["station"].astype(str).str.strip().str.lower() == station_name.lower()]
    if not s_l.empty and s_l["line"].notna().any():
        return s_l["line"].mode().iloc[0]
    # fallback: most common line overall
    return df_like["line"].mode().iloc[0]

def hourly_profile_dataframe(station: str, line: str, day: str) -> pd.DataFrame:
    hours = hours_for_daytype(day)
    grid = pd.DataFrame({
        "station": [station] * len(hours),
        "line":    [line] * len(hours),
        "day":     [day] * len(hours),   
        "hour":    hours,
        "minute":  [0] * len(hours),
    })
    grid = grid[service_open_mask(grid)].copy()
    grid["is_weekend"] = grid["day"].isin(["saturday", "sunday"]).astype(int)
    return grid

def plot_station_day(pipe, station: str, line: str, day: str):
    grid = hourly_profile_dataframe(station, line, day)
    preds = pipe.predict(grid)

    fig = plt.figure()
    plt.bar(grid["hour"], preds, width=0.8, align="center")  # swapped to bar chart
    plt.title(f"{station} — Estimated riders by hour ({day.title()})")
    plt.xlabel("Hour of day (24h)")
    plt.ylabel("Predicted riders")
    plt.xticks(range(0, 24, 2))  # show ticks every 2 hours
    plt.grid(True, which="both", axis="y", linestyle="--", alpha=0.4)  # keep only horizontal grid
    plt.tight_layout()
    plt.show()

#----------------------------------------------------------------------------------------------------------------------------

# Data to determine open subway hours
WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday", "friday"}
WEEKENDS = {"saturday", "sunday"}

def service_open_mask(df_like: pd.DataFrame) -> pd.Series:
    """
    Row-aware mask using day_type, hour, and minute.
    Mon–Fri: open 06:00–23:59 same day + 00:00–01:30 next day
    Sat–Sun: open 08:00–23:59 same day + 00:00–01:30 next day
    """
    day = df_like["day"].astype(str).str.strip().str.lower()
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

df = pd.read_csv("Ridership_Data.csv")
df.columns = df.columns.str.lower()

# Basic cleaning / normalization see everything uppercase or lowercase is treated the same
df["day"] = df["day"].str.lower().str.strip()
df["station"] = df["station"].str.strip()
df["line"] = df["line"].str.strip()

# Features & target (station, line, hour, day, and is_weekend)
X = df[["station", "line", "hour", "day"]].copy()
y = df["riders"].astype(float) # Y value is the value we want to predict
# Using the clean hour/minute directly from the CSV instead of old function
X["hour"] = X["hour"].replace(24, 0)  
X["minute"] = 0
# Adding a weekend flag -> Trees love numeric signals, helping the model split weekday V weekend for more nodes
X["is_weekend"] = X["day"].isin(["saturday", "sunday"]).astype(int)

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


# Categorical features still go through OHE
cat_features = ["station", "line", "day"]

# Give XGBoost the time signals + raw hour/minute + weekend flag
num_features = ["hour", "minute", "is_weekend"]

cat_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),    
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
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

# Pipeline with XGBoost settings now instead of Linear Regression
pipe = Pipeline(steps=[
    ("pre", pre),
    ("reg", XGBRegressor(
        n_estimators=600,        # number of trees
        max_depth=5,             # tree depth (controls complexity)
        learning_rate=0.05,      # shrinkage
        subsample=0.9,           # row sampling per tree
        colsample_bytree=0.9,    # column sampling per tree
        reg_lambda=1.0,          # L2 regularization
        objective="reg:squarederror",
        tree_method="hist",      # fast, memory-efficient CPU algorithm
        n_jobs=-1,               # use all cores
        random_state=42
    ))
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

print(f"R²:  {r2:.3f}") # Measures the models variability 
print(f"RMSE:{rmse:.1f}") # Root Mean Squared Error (Error in predicitions)
print(f"MAE: {mae:.1f}") # Mean Absoulte Error

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
    "features": ["station", "line", "day", "hour", "is_weekend"],
    "algo": "XGBoost + OHE(station/line/day) + time features (sin/cos, hour, minute, weekend)",
    "service_hours_rule": "Mon–Fri 06:00–01:30; Sat–Sun 08:00–01:30 (next day).",
    "metrics": {"r2": float(r2), "rmse": float(rmse), "mae": float(mae)},
}

# Saves info into JSON data
META_PATH.write_text(json.dumps(meta, indent=2))

print(f"Saved model → {MODEL_PATH}")
print(f"Saved meta  → {META_PATH}")

# Visualization for Stations
station_name = "Finch"
line = most_common_line_for_station(X_train.assign(station=X_train["station"]),
                                              station_name=station_name)

plot_station_day(pipe, station_name, line, day="monday")
plot_station_day(pipe, station_name, line, day="sunday")

mask = service_open_mask(X)
print(X[mask]["hour"].unique())
