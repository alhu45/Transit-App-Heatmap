import requests

url = "http://127.0.0.1:8000/predict"

payload = {
  "records": {
    "station": "Union",
    "line": "1",
    "day": "Monday",
    "hour": 6
  }
}

res = requests.post(url, json=payload)
print(res.status_code)
print(res.json())

url2 = "http://127.0.0.1:8000/options"
response = requests.get(url2)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error {response.status_code}: {response.text}")

# Monday --> All Weekdays
# Sunday --> All Weekends

