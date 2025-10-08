import joblib
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Loading the model
model = joblib.load("artifacts/model.joblib")

venues = [
    "KovZpZAFFE1A",  # Scotiabank Arena (Max Capacity: 20 000)
    "KovZpZAEkkIA",  # Budweiser Stage (Max Capacity: 17 000)
    "KovZpa3Bbe",    # Rogers Centre (Max Capacity: 40 000)
    "KovZpZAE77aA",  # BMO Field (Max Capacity: 30 000)
    "KovZpZAEdJIA",  # Sobeys Stadium (Max Capacity: 12 500)
    "KovZpZAFFEJA",  # Meridian Hall (Max Capacity: 3200)
    "KovZpZAFnlnA",  # Massey Hall (Max Capacity: 2800)
    "KovZpZAJt7FA"   # Coca-Cola Coliseum (Max Capacity: 9000)
]
venue_query = ",".join(venues)

today = datetime.now().date()
start = f"{today}T00:00:00Z"
end = f"{today}T23:59:59Z"

load_dotenv()
weather_key = os.getenv('weather')
weather_url = f"http://api.weatherapi.com/v1/current.json?key={weather_key}&q=Toronto"

res_weather = requests.get(weather_url)

if res_weather.status_code == 200:
    data = res_weather.json()
    temp = data["current"]["temp_c"]
    condition = data["current"]["condition"]["text"]
    print(f"Temperature: {temp}°C")
    print(f"Condition: {condition}")
else:
    print(f"Error {res_weather.status_code}: {res_weather.text}")

ticketmaster_key = os.getenv('ticketmaster')
# ticketmaster_url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={ticketmaster_key}&geoPoint=dpxnxn&radius=25&unit=km&size=100"

ticketmaster_url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={ticketmaster_key}&venueId={venue_query}&startDateTime={start}&endDateTime={end}&size=100"

res_ticketmaster = requests.get(ticketmaster_url)

if res_ticketmaster.status_code == 200:
    data = res_ticketmaster.json()
    events = data.get("_embedded", {}).get("events", [])

    for e in events:
        name = e.get("name")
        date = e.get("dates", {}).get("start", {}).get("localDate")
        time = e.get("dates", {}).get("start", {}).get("localTime")
        venue = e.get("_embedded", {}).get("venues", [{}])[0].get("name")
        lat = e.get("_embedded", {}).get("venues", [{}])[0].get("location", {}).get("latitude")
        lon = e.get("_embedded", {}).get("venues", [{}])[0].get("location", {}).get("longitude")

        print(f"{date} {time} — {name} @ {venue} ({lat},{lon})")

def TTC_Hours(day: str, hour: int) -> bool:
    day = day.lower()
    if day in ["saturday", "sunday"]:
        # Weekends Hours (8:00 AM to 1:30 AM)
        return (8 <= hour <= 23) or (hour in [0, 1])
    else:
        # Weekdays Hours (6:00 AM to 1:30 AM)
        return (6 <= hour <= 23) or (hour in [0, 1])

# Fetching prediciton from model
sample = pd.DataFrame([{
    "station": "Union",
    "line": "1",
    "day": "tuesday",
    "hour": 6,
    "minute": 0,
    "is_weekend": 0
}])

day = sample.loc[0, "day"]
hour = int(sample.loc[0, "hour"])

prediction = model.predict(sample)
if not TTC_Hours(day, hour):
    print(f"TTC is closed at {hour}:00 on {day}. Predicted ridership: 0 riders")
else:
    prediction = model.predict(sample)
    print(f"Predicted ridership: {prediction[0]:,.0f}")