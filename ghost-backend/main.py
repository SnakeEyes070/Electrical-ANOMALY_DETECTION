# main.py - COMPLETE with all endpoints including WebSocket
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import asyncio

sys.path.append(str(Path(__file__).parent))

# Load environment manually
def load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        print("✅ Environment loaded")

load_env()

# Now import FastAPI and WebSocket
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from database import mongodb  # Your MongoDB connection

# ============ WEBSOCKET MANAGER ============
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"📤 WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# ============ LIFESPAN ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*50)
    print("🚀 GHOST BACKEND WITH MONGODB & WEBSOCKETS")
    print("="*50)
    
    await mongodb.connect()
    
    # Start background task for broadcasting sensor data
    asyncio.create_task(broadcast_sensor_data())
    
    yield
    
    # Shutdown
    await mongodb.close()
    print("\n👋 Backend shutdown complete")

# ============ BACKGROUND TASK ============
async def broadcast_sensor_data():
    """Background task to broadcast sensor data to all WebSocket clients"""
    while True:
        try:
            # Get latest data from MongoDB
            collection = mongodb.db.sensor_data
            cursor = collection.find().sort("timestamp", -1).limit(1)
            
            latest_data = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                latest_data.append(doc)
            
            if latest_data:
                # Broadcast to all connected clients
                await manager.broadcast(json.dumps({
                    "type": "sensor_update",
                    "data": latest_data[0],
                    "timestamp": datetime.utcnow().isoformat()
                }))
            
            await asyncio.sleep(3)  # Broadcast every 3 seconds
            
        except Exception as e:
            print(f"WebSocket broadcast error: {e}")
            await asyncio.sleep(5)

# ============ FASTAPI APP ============
app = FastAPI(
    title="GHOST API - Complete Version",
    description="Grid Health Optimization & Security Tracker with WebSockets",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ WEBSOCKET ENDPOINT ============
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for any message from client (optional)
            data = await websocket.receive_text()
            # You can handle client messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ============ REST API ENDPOINTS ============

@app.get("/")
async def root():
    return {
        "message": "🚀 GHOST API with MongoDB & WebSockets",
        "status": "online",
        "endpoints": {
            "rest_api": "/docs",
            "websocket": "/ws",
            "health": "/health",
            "dashboard": "/api/dashboard/summary",
            "sensor_data": "/api/sensor-data/latest",
            "anomalies": "/api/anomalies",
            "nodes": "/api/dashboard/nodes"
        }
    }

@app.get("/health")
async def health_check():
    try:
        await mongodb.db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "websocket_connections": len(manager.active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/sensor-data/latest")
async def get_latest_sensor_data(limit: int = 60):
    """Get latest sensor data FROM MONGODB"""
    try:
        collection = mongodb.db.sensor_data
        
        cursor = collection.find().sort("timestamp", -1).limit(limit)
        
        data = []
        async for document in cursor:
            document["_id"] = str(document["_id"])
            data.append(document)
        
        return {
            "count": len(data),
            "data": data,
            "source": "mongodb"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary FROM MONGODB"""
    try:
        collection = mongodb.db.sensor_data
        
        # Get data from last 24 hours
        time_24h_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Count total readings
        total_readings = await collection.count_documents({
            "timestamp": {"$gte": time_24h_ago.isoformat()}
        })
        
        # Get latest 100 readings
        cursor = collection.find().sort("timestamp", -1).limit(100)
        latest_data = []
        async for doc in cursor:
            latest_data.append(doc)
        
        # Calculate averages
        if latest_data:
            voltages = [d.get('voltage', 0) for d in latest_data if d.get('voltage') is not None]
            currents = [d.get('current', 0) for d in latest_data if d.get('current') is not None]
            temps = [d.get('temperature', 0) for d in latest_data if d.get('temperature') is not None]
            
            avg_voltage = sum(voltages) / len(voltages) if voltages else 0
            avg_current = sum(currents) / len(currents) if currents else 0
            avg_temp = sum(temps) / len(temps) if temps else 0
            avg_power = avg_voltage * avg_current
        else:
            avg_voltage = avg_current = avg_temp = avg_power = 0
        
        # Count distinct active sensors (last 1 hour)
        time_1h_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Using aggregation for distinct count
        pipeline = [
            {"$match": {"timestamp": {"$gte": time_1h_ago.isoformat()}}},
            {"$group": {"_id": "$sensor_id"}},
            {"$count": "active_sensors"}
        ]
        
        active_result = await collection.aggregate(pipeline).to_list(length=1)
        active_sensors = active_result[0]["active_sensors"] if active_result else 0
        
        # Get anomaly count
        anomaly_count = await mongodb.db.anomalies.count_documents({"status": "active"})
        
        return {
            "total_readings_24h": total_readings,
            "active_sensors": active_sensors,
            "active_alerts": anomaly_count,
            "average_health_score": 85.5,
            "average_voltage": round(avg_voltage, 2),
            "average_current": round(avg_current, 2),
            "average_temperature": round(avg_temp, 2),
            "average_power": round(avg_power, 2),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/anomalies")
async def get_anomalies(limit: int = 10):
    """Get latest anomalies/alerts FROM MONGODB"""
    try:
        collection = mongodb.db.anomalies
        
        # Check if collection exists, if not create mock data
        collections = await mongodb.db.list_collection_names()
        
        if "anomalies" not in collections:
            # Return mock data if collection doesn't exist
            return {
                "count": 2,
                "data": [
                    {
                        "alert_id": "ALERT_001",
                        "sensor_id": "ESP32_001",
                        "alert_type": "voltage_drop",
                        "severity": "high",
                        "message": "Voltage dropped below threshold",
                        "value": 198.5,
                        "threshold": 200,
                        "timestamp": datetime.utcnow().isoformat(),
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
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "active"
                    }
                ],
                "note": "Using mock data - anomalies collection not found"
            }
        
        # Get real data from MongoDB
        cursor = collection.find({"status": "active"}).sort("timestamp", -1).limit(limit)
        
        anomalies = []
        async for document in cursor:
            document["_id"] = str(document["_id"])
            anomalies.append(document)
        
        return {
            "count": len(anomalies),
            "data": anomalies,
            "source": "mongodb"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/dashboard/nodes")
async def get_all_nodes():
    """Get all nodes with latest data FROM MONGODB"""
    try:
        collection = mongodb.db.sensor_data
        
        # Get unique nodes with their latest reading
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$node_id",
                "latest": {"$first": "$$ROOT"},
                "location": {"$first": "$location"}
            }},
            {"$project": {
                "node_id": "$_id",
                "location": 1,
                "voltage": "$latest.voltage",
                "current": "$latest.current",
                "temperature": "$latest.temperature",
                "power": "$latest.power",
                "timestamp": "$latest.timestamp",
                "_id": 0
            }}
        ]
        
        nodes = await collection.aggregate(pipeline).to_list(length=None)
        
        # Add health score
        for node in nodes:
            voltage = node.get("voltage", 0)
            temp = node.get("temperature", 0)
            
            # Simple health calculation
            health = 100
            if voltage < 200 or voltage > 250:
                health -= 30
            if temp > 60:
                health -= 20
            
            node["health_score"] = max(min(health, 100), 0)
        
        return nodes if nodes else []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/sensor-data/add")
async def add_sensor_data(data: dict):
    """Add sensor data TO MONGODB"""
    try:
        collection = mongodb.db.sensor_data
        
        # Add timestamp
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        
        # Calculate power if not provided
        if "power" not in data and "voltage" in data and "current" in data:
            data["power"] = data["voltage"] * data["current"]
        
        # Insert into MongoDB
        result = await collection.insert_one(data)
        
        # Check for anomalies
        await check_for_anomalies(data)
        
        # Broadcast update via WebSocket
        await manager.broadcast(json.dumps({
            "type": "new_sensor_data",
            "data": data,
            "mongodb_id": str(result.inserted_id)
        }))
        
        return {
            "message": "✅ Data saved to MongoDB Atlas!",
            "mongodb_id": str(result.inserted_id),
            "timestamp": data["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def check_for_anomalies(data: dict):
    """Check for anomalies and save to anomalies collection"""
    try:
        anomalies_collection = mongodb.db.anomalies
        
        # Ensure collection exists
        collections = await mongodb.db.list_collection_names()
        if "anomalies" not in collections:
            await mongodb.db.create_collection("anomalies")
        
        voltage = data.get("voltage", 0)
        current = data.get("current", 0)
        temperature = data.get("temperature", 0)
        sensor_id = data.get("sensor_id", "unknown")
        
        # Check for voltage anomaly
        if voltage < 200 or voltage > 250:
            anomaly = {
                "alert_id": f"ALERT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "sensor_id": sensor_id,
                "alert_type": "voltage_anomaly",
                "severity": "critical" if voltage < 180 or voltage > 260 else "high",
                "message": f"Voltage anomaly detected: {voltage}V",
                "value": voltage,
                "threshold": 230,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active",
                "location": data.get("location", {})
            }
            await anomalies_collection.insert_one(anomaly)
        
        # Check for current overload
        if current > 80:
            anomaly = {
                "alert_id": f"ALERT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "sensor_id": sensor_id,
                "alert_type": "overload",
                "severity": "critical",
                "message": f"Current overload detected: {current}A",
                "value": current,
                "threshold": 80,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active",
                "location": data.get("location", {})
            }
            await anomalies_collection.insert_one(anomaly)
        
        # Check for high temperature
        if temperature > 60:
            anomaly = {
                "alert_id": f"ALERT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "sensor_id": sensor_id,
                "alert_type": "temperature",
                "severity": "high",
                "message": f"High temperature detected: {temperature}°C",
                "value": temperature,
                "threshold": 60,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active",
                "location": data.get("location", {})
            }
            await anomalies_collection.insert_one(anomaly)
            
    except Exception as e:
        print(f"Anomaly detection error: {e}")

# ============ START SERVER ============
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n🌐 Server starting on: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"⚡ WebSocket: ws://localhost:{port}/ws")
    print(f"📡 MongoDB: Connected to Atlas")
    print("\n" + "="*50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )