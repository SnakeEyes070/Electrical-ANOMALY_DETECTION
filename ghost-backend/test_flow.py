# test_flow.py
import requests
import json
import time

def test_complete_flow():
    print("🧪 Testing Complete Data Flow\n")
    
    # 1. Send data to backend
    print("1. Sending data to backend...")
    data = {
        "sensor_id": "ESP32_TEST_001",
        "voltage": 235.7,
        "current": 12.8,
        "temperature": 38.4,
        "node_id": "node_test_001",
        "location": {"lat": 23.2599, "lng": 77.4126}
    }
    
    response = requests.post(
        "http://localhost:8000/api/sensor-data/add",
        json=data
    )
    
    print(f"   Response: {response.json()}\n")
    
    # 2. Wait a moment
    print("2. Waiting for data to be processed...")
    time.sleep(2)
    
    # 3. Check if data appears in API
    print("3. Fetching latest data from API...")
    response = requests.get("http://localhost:8000/api/sensor-data/latest?limit=5")
    api_data = response.json()
    
    print(f"   Found {api_data.get('count', 0)} readings")
    if api_data.get('data'):
        latest = api_data['data'][0]
        print(f"   Latest: {latest.get('sensor_id')} - {latest.get('voltage')}V")
    
    # 4. Check dashboard
    print("\n4. Checking dashboard data...")
    response = requests.get("http://localhost:8000/api/dashboard/summary")
    dashboard = response.json()
    
    print(f"   Active sensors: {dashboard.get('active_sensors')}")
    print(f"   Average voltage: {dashboard.get('average_voltage')}V")
    print(f"   Data source: {dashboard.get('data_source', 'Unknown')}")
    
    print("\n✅ Test complete!")
    print("\n📊 Now check your React dashboard at: http://localhost:3000")
    print("   It should show the live voltage and current values.")

if __name__ == "__main__":
    test_complete_flow()