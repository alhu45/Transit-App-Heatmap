# ttc_rider_api/transformers.py
import math
import pandas as pd

def clean_df(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Shared cleaner used in training and inference.
    - Standardize strings (strip/lower) and treat empty/placeholder as missing
    - Coerce hour to numeric
    - Create minute_of_day assuming minutes=0 if not provided
    - Add cyclical time features (sin/cos) so minutes-of-day can be modeled smoothly
    """
    df = df_in.copy()

    for col in ["station", "line", "day"]:
        s = df[col].astype(str).str.strip().str.lower()
        df[col] = s.replace(to_replace={...}, value=None)



    if "hour" in df.columns:
        df["hour"] = pd.to_numeric(df["hour"], errors="coerce")

    # If caller sent 'minute', coerce; else default 0
    if "minute" not in df.columns:
        df["minute"] = 0
    df["minute"] = pd.to_numeric(df["minute"], errors="coerce").fillna(0).clip(0, 59)

    # minute_of_day = hour*60 + minute (if hour NaN, keep NaN so imputer can handle)
    df["minute_of_day"] = df["hour"] * 60 + df["minute"]

    # cyclical encoding (handle NaN safely)
    def _sin_m(m): 
        return math.sin(2 * math.pi * (m / 1440.0)) if pd.notna(m) else None
    def _cos_m(m): 
        return math.cos(2 * math.pi * (m / 1440.0)) if pd.notna(m) else None

    df["tod_sin"] = df["minute_of_day"].apply(_sin_m)
    df["tod_cos"] = df["minute_of_day"].apply(_cos_m)

    # ensure target numeric if present
    if "riders" in df.columns:
        df["riders"] = pd.to_numeric(df["riders"], errors="coerce")

    return df

def is_service_hour(hour) -> bool:
    """
    Return True if hour is within TTC service window.
    Robust to hour being str/None/NaN.
    Simple rule: service if hour in {6..23, 0, 1}.
    """
    try:
        h = int(hour)
    except (TypeError, ValueError):
        return False
    return (h >= 6) or (h in (0, 1))

