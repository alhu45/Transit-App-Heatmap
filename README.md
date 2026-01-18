# TTC Ridership Heatmap System

A data engineering project that **predicts and visualizes crowding levels at TTC subway stations** using machine learning, enriched with contextual data like weather and major events. The system provides real-time prediction capabilities with an interactive frontend that helps users and planners understand congestion patterns across Toronto’s transit network.

---

## Project Overview

This project builds and serves a machine learning model trained on TTC ridership counts combined with external data sources. Predictions are exposed via a FastAPI backend and displayed on a React-based heatmap interface using Leaflet. The system is containerized for deployment and can scale using Kubernetes and Terraform-provisioned cloud resources.

---

## Key Features

### Machine Learning Predictions
- XGBoost regression model estimating subway station crowd levels.

### Weather & Event Data Fusion
- Weather API + Ticketmaster event scraping to improve prediction accuracy.

### FastAPI Backend
- Lightweight REST API to serve ML predictions in real time.

### Interactive Heatmap Frontend
- React + Leaflet map with color-coded congestion indicators.

### Dockerized Architecture
- Frontend and backend packaged into separate Docker containers.

### Cloud-Ready Deployment
- Supports deployment to AWS via Kubernetes.

### Infrastructure as Code
- Terraform manages cloud environment setup and provisioning.

---

## Tech Stack

| Component        | Tools / Technologies                                        |
|------------------|-------------------------------------------------------------|
| Machine Learning | Python, Pandas, Scikit-learn, XGBoost, Joblib               |
| Data Sources     | TTC Historical Data, Weather API, Ticketmaster Event Data   |
| Backend API      | FastAPI, Uvicorn                                            |
| Frontend UI      | React, Vite, Leaflet                                        |
| Containerization | Docker, Docker Compose                                      |
| Orchestration    | Kubernetes                                                  |
| Infrastructure   | Terraform, AWS EC2                                          |
| Version Control  | GitHub                                                      |
