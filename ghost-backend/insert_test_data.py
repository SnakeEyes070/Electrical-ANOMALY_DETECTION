# insert_test_data.py
import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api/sensor-data"

# Test nodes
nodes = ["node_001", "node_002", "node_003"]
sensors = ["ESP32_001", "ESP32_002", "ESP32_003"]

def add_sensor_data():
    """Add sample sensor data"""
    for i in range(10):
        data = {
            "sensor_id": random.choice(sensors),
            "voltage": random.uniform(220, 240),
            "current": random.uniform(10, 20),
            "temperature": random.uniform(30, 50),
            "node_id": random.choice(nodes),
            "transformer_id": f"transformer_{random.choice(['A', 'B', 'C'])}",
            "location": {
                "lat": 23.2599 + random.uniform(-0.01, 0.01),
                "lng": 77.4126 + random.uniform(-0.01, 0.01)
            }
        }
        
        response = requests.post(f"{BASE_URL}/add", json=data)
        if response.status_code == 200:
            print(f"✅ Added data {i+1}: {data['sensor_id']} - {data['voltage']}V")
        else:
            print(f"❌ Failed: {response.text}")

def add_anomaly_data():
    """Add sample anomaly data"""
    anomaly_url = "http://localhost:8000/api/alerts/add"
    
    anomalies = [
        {
            "alert_id": "ALERT_001",
            "sensor_id": "ESP32_001",
            "alert_type": "voltage_drop",
            "severity": "high",
            "message": "Voltage dropped below threshold",
            "value": 198.5,
            "threshold": 200,
            "location": {"lat": 23.2599, "lng": 77.4126},
            "status": "active"
        },
        {
            "alert_id": "ALERT_002",
            "sensor_id": "ESP32_002",
            "alert_type": "overload",
            "severity": "critical",
            "message": "Current overload detected",
            "value": 95.2,
            "threshold": 80,
            "location": {"lat": 23.2600, "lng": 77.4130},
            "status": "active"
        }
    ]
    
    for anomaly in anomalies:
        response = requests.post(anomaly_url, json=anomaly)
        print(f"Added anomaly: {anomaly['alert_type']}")

if __name__ == "__main__":
    print("📊 Adding test sensor data...")
    add_sensor_data()
    print("\n✅ Test data added successfully!")
    
    # Test retrieving data
    print("\n📡 Fetching latest data...")
    response = requests.get("http://localhost:8000/api/sensor-data/latest")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} sensor readings")
        for reading in data['data'][:3]:  # Show first 3
            print(f"  - {reading['sensor_id']}: {reading['voltage']}V, {reading['current']}A")