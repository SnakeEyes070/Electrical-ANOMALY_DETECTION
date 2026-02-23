from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
from models import SensorData
from database import mongodb
import json

router = APIRouter(prefix="/api/sensor-data", tags=["Sensor Data"])

@router.get("/latest")
async def get_latest_readings(node_id: Optional[str] = None, limit: int = 10):
    """
    Get latest sensor readings.
    If node_id provided, filter by node.
    """
    collection = mongodb.db.sensor_data
    query = {}
    if node_id:
        query["node_id"] = node_id
    
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    
    readings = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        readings.append(doc)
    
    return {"count": len(readings), "data": readings}

@router.get("/live/{sensor_id}")
async def get_live_sensor_data(sensor_id: str):
    """
    Get live data for a specific sensor
    """
    collection = mongodb.db.sensor_data
    
    # Get the most recent reading
    latest = await collection.find_one(
        {"sensor_id": sensor_id},
        sort=[("timestamp", -1)]
    )
    
    if not latest:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    latest["_id"] = str(latest["_id"])
    return latest

@router.get("/time-range")
async def get_time_range_data(
    start_time: datetime = Query(..., description="Start time in ISO format"),
    end_time: datetime = Query(..., description="End time in ISO format"),
    node_id: Optional[str] = None
):
    """
    Get sensor data within a time range for charts
    """
    collection = mongodb.db.sensor_data
    
    query = {
        "timestamp": {
            "$gte": start_time,
            "$lte": end_time
        }
    }
    
    if node_id:
        query["node_id"] = node_id
    
    cursor = collection.find(query).sort("timestamp", 1)
    
    data = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    
    return {"count": len(data), "data": data}

@router.post("/add")
async def add_sensor_data(data: SensorData):
    """
    Add new sensor reading (for IoT devices to POST data)
    """
    collection = mongodb.db.sensor_data
    
    # Convert Pydantic model to dict
    data_dict = data.model_dump(by_alias=True, exclude_unset=True)
    
    # Insert into MongoDB
    result = await collection.insert_one(data_dict)
    
    # Trigger anomaly detection
    await check_for_anomalies(data)
    
    return {
        "message": "Data added successfully",
        "id": str(result.inserted_id),
        "timestamp": data.timestamp
    }

async def check_for_anomalies(data: SensorData):
    """Placeholder for anomaly detection logic"""
    anomalies_collection = mongodb.db.anomalies
    
    # Example: Check for voltage anomalies
    if data.voltage < 200 or data.voltage > 250:
        anomaly = {
            "sensor_id": data.sensor_id,
            "timestamp": datetime.utcnow(),
            "alert_type": "voltage_anomaly",
            "severity": "high",
            "message": f"Voltage anomaly detected: {data.voltage}V",
            "value": data.voltage,
            "threshold": 230,
            "status": "active",
            "location": data.location if data.location else {}
        }
        await anomalies_collection.insert_one(anomaly)