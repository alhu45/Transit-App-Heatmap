import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

venues = [
    "KovZpZAFFE1A",
    "KovZpZAEkkIA",
    "KovZpa3Bbe",
    "KovZpa3Bbe",
    "KovZpZAE77aA",
    "KovZpZAEdJIA",
    "KovZpZAFFEJA",
    "KovZpZAFnlnA",
    "KovZpZAJt7FA"
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

        