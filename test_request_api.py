import requests

url = "http://127.0.0.1:8000/predict_time"

payload = {
  "records": [
    {
      "station": "Union",
      "line": "Line 1",
      "day_type": "weekday",
      "time": "8:00 PM"
    }
  ]
}

res = requests.post(url, json=payload)
print(res.status_code)
print(res.json())
