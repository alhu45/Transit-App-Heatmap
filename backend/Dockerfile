FROM python:3.12.2-slim

WORKDIR /backend

COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6767

WORKDIR /backend/ttc_rider_api

CMD ["uvicorn", "ttc_rider_api.main:app", "--host", "0.0.0.0", "--port", "6767"]



