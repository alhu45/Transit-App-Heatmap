import joblib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load the trained model
model = joblib.load("artifacts/model.joblib")

# TTC operating hours function
def TTC_Hours(day: str, hour: int) -> bool:
    day = day.lower()
    if day in ["saturday", "sunday"]:
        # Weekends Hours (8:00 AM to 1:30 AM)
        return (8 <= hour <= 23) or (hour in [0, 1])
    else:
        # Weekdays Hours (6:00 AM to 1:30 AM)
        return (6 <= hour <= 23) or (hour in [0, 1])

# Define target station/day
station = "Finch"
line = "1"
day = "monday"

# Generate all 24 hours (0–23)
hours = list(range(0, 24))
predictions = []

for hour in hours:
    if TTC_Hours(day, hour):
        sample = pd.DataFrame([{
            "station": station,
            "line": line,
            "day": day,
            "hour": hour,
            "minute": 0,
            "is_weekend": 1 if day in ["saturday", "sunday"] else 0
        }])
        yhat = model.predict(sample)[0]
    else:
        yhat = 0  # Closed hours → 0 ridership
    predictions.append(yhat)

# Create a DataFrame for plotting
df_plot = pd.DataFrame({
    "day": day,
    "hour": hours,
    "predicted_ridership": predictions
})

# Plot
plt.figure(figsize=(10, 6))
plt.bar(df_plot["hour"], df_plot["predicted_ridership"], color="royalblue")
plt.title(f"Predicted Ridership by Hour — {station} Station (Monday)")
plt.xlabel("Hour of Day (24h)")
plt.ylabel("Predicted Riders")
plt.xticks(range(0, 24, 2))
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()

# Print data for quick reference
print(df_plot)
