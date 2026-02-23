GHOST: Intelligent Monitoring & Predictive Maintenance System

GHOST (Generic Hardware Observation & Smart Telemetry) is a full‑stack IoT platform that collects sensor data from edge devices, analyzes it using machine learning for anomaly detection and predictive maintenance, and provides a real‑time dashboard for visualization and alerting. The system is designed for industrial monitoring, smart infrastructure, and research applications.

Features
Real‑time Telemetry – Collect and visualize sensor data (voltage, current, temperature, etc.) from multiple devices.

Anomaly Detection – Isolation Forest model to detect abnormal patterns in telemetry streams.

Predictive Maintenance – LSTM‑based forecasting to predict potential equipment failures.

Dual‑Impedance Fault Detection – Calculate and monitor line impedance for cable fault identification.

Live Dashboard – Next.js frontend with WebSocket updates, charts, and alert management.

Device Management – Register, update, and monitor edge devices (ESP32, Arduino Uno).

MQTT Integration – Lightweight communication between edge devices and the cloud backend.

Simulated Data Generator – Test the system with synthetic telemetry when hardware is unavailable.

Architecture Overview

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Edge Devices  │────▶│   MQTT Broker   │────▶│  FastAPI Backend │
│  (ESP32/Arduino)│     │   (Mosquitto)   │     │   (cloud_backend)│
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PostgreSQL DB  │◀───▶│   ML Models     │     │  WebSocket      │
│   (timeseries)  │     │(Isolation Forest│     │  (real‑time)    │
└─────────────────┘     │    & LSTM)      │     └────────┬────────┘
                        └─────────────────┘              │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js       │◀────│   REST API      │     │  React Dashboard│
│   Frontend      │     │   & WebSocket   │     │  (live charts)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘

Technology Stack
Component	Technology
Backend API	FastAPI (Python 3.10+), SQLAlchemy, Pydantic
Database	PostgreSQL (with TimescaleDB extension for time‑series)
Real‑time	WebSocket (via FastAPI’s WebSocket), Socket.IO client
Message Broker	Mosquitto MQTT
Machine Learning	scikit‑learn (Isolation Forest), TensorFlow/Keras (LSTM)
Frontend	Next.js (React), TypeScript, Tailwind CSS, Recharts, React Query
Edge Devices	Arduino Uno, ESP32 (C++ sketches)
Simulator	Python script generating synthetic telemetry
Deployment	Docker, Heroku (Procfile), GitHub Actions
Prerequisites
Python 3.10+

Node.js 18+ and npm

PostgreSQL (with TimescaleDB recommended)

Mosquitto MQTT broker (or any MQTT broker)

Arduino IDE (for uploading sketches to edge devices)

Git

Installation
1. Clone the Repository
bash
git clone https://github.com/yourusername/ghost-project.git
cd ghost-project
2. Set Up Python Virtual Environment
bash
python -m venv ghost_env
# On Windows
ghost_env\Scripts\activate
# On Linux/Mac
source ghost_env/bin/activate
3. Install Backend Dependencies
bash
pip install -r requirements.txt
4. Configure Environment Variables
Copy the example environment file and edit it with your settings:

bash
cp .env.example .env
.env example:

env
DATABASE_URL=postgresql://user:password@localhost/ghost_db
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
SECRET_KEY=your-secret-key-here
5. Set Up the Database
Run the following commands to create the database and apply migrations (you may need to adjust based on your migration tool – here we assume Alembic or raw SQL):

bash
# If using Alembic
alembic upgrade head
# Or manually create tables with provided SQL script
6. Install Frontend Dependencies
bash
cd dashboard
npm install
7. ML Model Setup (Optional – Pre‑trained models included)
If you want to retrain the models:

bash
cd ml_models
python -m anomaly_detection.trainer
python -m predictive_maintenance.trainer
Pre‑trained models are already saved in ml_models/saved_models/.

Running the Project
Start the MQTT Broker
Make sure Mosquitto is running (or use a cloud broker). On Windows:

bash
mosquitto -v
Start the FastAPI Backend
From the project root (with virtual environment activated):

bash
cd cloud_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The API will be available at http://localhost:8000. Interactive docs at http://localhost:8000/docs.
