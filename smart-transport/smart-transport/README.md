# 🚦 Smart Transportation Ecosystem

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-green.svg)](https://leafletjs.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange.svg)](https://www.chartjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-yellow.svg)](https://scikit-learn.org/)

An integrated, multi-modal urban transportation intelligence platform designed to reduce **traffic congestion, travel time, commuting costs, and carbon emissions** by combining live traffic monitoring, public transit tracking, smart parking allocation, air quality (AQI) monitoring, multi-modal route recommendation scoring, crowdsourced incident reporting, and an administrative operations command center with AI congestion forecasting.

---

## 1. Problem Statement & Solution

Rapid urban growth leads to severe traffic bottlenecks, high fuel consumption, escalating carbon emissions, unpredictable public transport ETAs, and parking scarcity. 

Traditional navigation apps focus solely on single-mode private vehicle navigation, exacerbating urban gridlock. The **Smart Transportation Ecosystem** unifies all urban transport dimensions into a single intelligent platform that recommends optimized, sustainable transit routes tailored to commuter preferences.

### System Flow
```text
                     COMMUTER / USER
                           │
                           ▼
                  ┌─────────────────┐
                  │    FRONTEND     │
                  │ HTML5 / CSS3 /  │
                  │ Leaflet.js /    │
                  │ Chart.js        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    FLASK API    │
                  │    BACKEND      │
                  └────────┬────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Traffic Module│    │Transit Module│    │Pollution Mod │
│  (Congestion)│    │(Buses/Metro) │    │  (AQI/PM2.5) │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Recommendation  │
                  │  & CO₂ Engine   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   SQLite DB     │
                  │ (transport.db)  │
                  └─────────────────┘
```

---

## 2. Core Features

### 🚦 2.1 Traffic Monitoring & Congestion Levels
Monitors major road arteries in real-time with classification metrics:
* **0–30%**: Low / Smooth Flow 🟢
* **31–60%**: Moderate Traffic 🟡
* **61–80%**: High Congestion 🟠
* **81–100%**: Severe Gridlock 🔴

### 🗺️ 2.2 Interactive Leaflet.js Map
* Dark-mode OpenStreetMap canvas with toggleable overlays.
* Live bus location markers with occupancy tooltips.
* Smart parking hubs displaying remaining available spots.
* Air quality monitoring heat circles.
* Incident warning pins and dynamic route polylines.

### 🚌 2.3 Public Transit & Multi-Modal Sync
* Live fleet tracking (MTC buses & CMRL Blue/Green Metro lines).
* Real-time ETA calculations and occupancy congestion indicators.
* Multi-modal combinations (e.g. *Walk → Feeder Bus → Metro Express → Walk*).

### 🅿️ 2.4 Smart Parking Hubs
* Live available spots vs total capacity tracking across major urban parking lots.
* Hourly tariff calculation and EV charging availability indicators.
* Automated nearest parking spot recommendation.

### 🌫️ 2.5 Air Quality (AQI) Monitoring
* Live station readings for AQI, PM2.5, PM10, and primary pollutants.
* Standard CPCB/EPA category classifications (Good, Moderate, Unhealthy for Sensitive, Unhealthy, Very Unhealthy, Hazardous).

### 🧠 2.6 Smart Route Recommendation Engine
Evaluates options against multi-criteria optimization weights:
$$\text{Score} = w_{\text{time}} \cdot S_{\text{time}} + w_{\text{cost}} \cdot S_{\text{cost}} + w_{\text{traffic}} \cdot S_{\text{traffic}} + w_{\text{emission}} \cdot S_{\text{emission}}$$

| Preference | Time Weight ($w_t$) | Cost Weight ($w_c$) | Traffic Weight ($w_{tr}$) | Emission Weight ($w_e$) |
| :--- | :---: | :---: | :---: | :---: |
| **⚡ Fastest** | 70% | 10% | 15% | 5% |
| **💰 Cheapest** | 15% | 70% | 10% | 5% |
| **🌱 Greenest** | 15% | 10% | 15% | 60% |
| **⚖️ Balanced** | 40% | 25% | 20% | 15% |

### 🌱 2.7 Environmental CO₂ Savings Calculator
* Computes emissions for Car (160 g/km), Bus (38 g/p-km), and Metro (18 g/p-km).
* Displays commuter monetary savings and net CO₂ emissions avoided compared to single-occupancy private cars.

### ⚠️ 2.8 Crowdsourced Incident Reporting
* Commuters report accidents, road construction, signal failures, vehicle breakdowns, or severe congestion.
* Instant dispatch notification and administrative resolution workflow.

### 👨‍💼 2.9 Admin Command Center & AI Traffic Prediction
* Live KPIs: Active buses, incident count, parking availability %, average AQI, total CO₂ saved today.
* Chart.js visualizations: Road congestion by artery, AQI zone distribution, 24-hour traffic trend vs AI forecast, incident categories, modal split.
* Interactive traffic load simulator to test dynamic re-routing.
* Machine Learning Random Forest traffic predictor (`/api/predict-traffic`).

---

## 3. Project Structure

```text
smart-transport/
├── backend/
│   ├── app.py              # Main Flask Application & Route Dispatcher
│   ├── database.py         # Database engine & automatic CSV seeding
│   ├── models.py           # SQLAlchemy database schemas
│   ├── traffic.py          # Traffic monitoring API
│   ├── transport.py        # Bus & Metro transit API
│   ├── parking.py          # Smart parking locator API
│   ├── pollution.py        # Air Quality (AQI) monitoring API
│   ├── emissions.py        # Carbon calculation & savings module
│   ├── recommendation.py   # Multi-modal route recommendation engine
│   ├── incidents.py        # Incident reporting & dispatch API
│   ├── auth.py             # User authentication & commuter profile
│   └── admin.py            # Operations analytics & chart feeds
├── frontend/
│   ├── index.html          # Commuter Hub & Journey Planner Dashboard
│   ├── admin.html          # Operations Command Center Dashboard
│   ├── css/
│   │   └── style.css       # Responsive theme & map styling
│   └── js/
│       ├── map.js          # Leaflet map & layer rendering
│       ├── traffic.js      # Live traffic feed controller
│       ├── transport.js    # Public transit fleet controller
│       ├── parking.js      # Smart parking controller
│       ├── pollution.js    # AQI monitoring controller
│       ├── route.js        # Journey planner & recommendation UI
│       ├── charts.js       # Admin Chart.js & simulator controller
│       └── app.js          # Main coordinator script
├── ml/
│   ├── train.py            # AI model training script
│   └── predict.py          # Traffic prediction inference API
├── data/
│   ├── traffic.csv         # Arterial road congestion dataset
│   ├── buses.csv           # Public transit fleet dataset
│   ├── parking.csv         # Smart parking facilities dataset
│   ├── pollution.csv       # AQI monitoring station dataset
│   ├── locations.csv       # Hub waypoints & coordinates
│   └── incidents.csv       # Road obstruction log
├── database/
│   └── transport.db        # SQLite database (auto-generated)
├── tests/
│   └── test_api.py         # Automated API & logic test suite
├── requirements.txt        # Python package dependencies
├── run.py                  # Single-command launcher
└── README.md
```

---

## 4. Quick Start & Setup

### 4.1 Prerequisites
* Python 3.11 or newer
* Git (optional)

### 4.2 Installation
1. Clone or navigate to the repository directory:
   ```bash
   cd smart-transport
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4.3 Run the Application
Start the integrated server with a single command:
```bash
python run.py
```

Open in your browser:
* 🌍 **Commuter Navigation Hub**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
* 👨‍💼 **Operations Admin Portal**: [http://127.0.0.1:5000/admin.html](http://127.0.0.1:5000/admin.html)
* 🔌 **REST API Root**: [http://127.0.0.1:5000/api](http://127.0.0.1:5000/api)

---

## 5. Event Presentation & Demonstration Scenario

### Step-by-Step Demo Flow:
1. **Scenario Selection**:
   * Origin: **VIT Chennai**
   * Destination: **Chennai International Airport**
2. **System Telemetry Assessment**:
   * Detects heavy corridor congestion on GST Road (61%) and OMR (82%).
   * Detects moderate-to-unhealthy AQI (142).
   * Identifies 245 open parking spots at Airport MLCP.
3. **Multi-Modal Evaluation**:
   * **Private Car**: 52 mins • ₹180 • 5.4 kg CO₂
   * **Public Bus**: 61 mins • ₹35 • 1.4 kg CO₂
   * **Metro Only**: 48 mins • ₹40 • 0.8 kg CO₂
   * **Bus + Metro (Multimodal)**: **43 mins • ₹40 • 0.9 kg CO₂**
4. **Recommendation Display**:
   * Crowned 🏆 **Bus + Metro** as the optimal winning route.
   * **Commuter Benefit**: **You save ₹140 and 4.5 kg CO₂** (83% carbon reduction).
5. **Interactive Layer Walkthrough**:
   * Toggle Buses, Parking, AQI circles, and Incidents on the Leaflet map.
6. **Admin & AI Demonstration**:
   * Switch to Admin Dashboard (`/admin.html`).
   * Show live Chart.js graphs, test the **AI Traffic Prediction** for 18:00 Rainy conditions, and use the **Traffic Simulator Slider** to trigger real-time road adjustments.

---

## 6. Automated Testing

Run the test suite to verify all endpoints, scoring weights, and emissions math:
```bash
python -m unittest tests/test_api.py
```

---

## 7. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api` | API Health & endpoint directory |
| `GET` | `/api/traffic` | Live road congestion and speeds |
| `POST` | `/api/traffic/update` | Simulated road congestion update |
| `GET` | `/api/buses` | Public bus fleet, occupancy & ETAs |
| `GET` | `/api/metro` | Metro transit lines & station list |
| `GET` | `/api/parking` | Smart parking capacity & pricing |
| `GET` | `/api/parking/nearest` | Nearest parking spot finder |
| `GET` | `/api/pollution` | AQI stations, PM2.5, PM10 & status |
| `GET`/`POST` | `/api/recommendation` | Smart route scoring & recommendation |
| `POST` | `/api/routes` | Route calculation & trip history log |
| `GET` | `/api/incidents` | List active traffic incidents |
| `POST` | `/api/incidents` | Submit crowdsourced incident report |
| `POST` | `/api/incidents/<id>/status` | Update incident resolution state |
| `POST` | `/api/predict-traffic` | AI model congestion forecast |
| `GET` | `/api/admin/statistics` | Aggregated system metrics |
| `GET` | `/api/admin/charts-data` | Formatted datasets for Chart.js |
