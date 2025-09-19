import requests
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('weatherapi_key')
weather_url = f"http://api.weatherapi.com/v1/current.json?key={key}&q=Toronto"

res_weather = requests.get(weather_url)

if res_weather.status_code == 200:
    data = res_weather.json()
    temp = data["current"]["temp_c"]
    condition = data["current"]["condition"]["text"]
    print(f"Temperature: {temp}°C")
    print(f"Condition: {condition}")
else:
    print(f"Error {res_weather.status_code}: {res_weather.text}")

