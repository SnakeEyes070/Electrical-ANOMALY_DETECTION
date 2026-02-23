from fastapi import APIRouter
from datetime import datetime, timedelta
import asyncio
from database import mongodb

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_dashboard_summary():
    """
    Get dashboard summary data (KPIs)
    """
    sensor_collection = mongodb.db.sensor_data
    alerts_collection = mongodb.db.anomalies
    health_collection = mongodb.db.health_scores
    
    # Get latest readings count (last 24 hours)
    time_24h_ago = datetime.utcnow() - timedelta(hours=24)
    
    # Count active sensors (with data in last hour)
    time_1h_ago = datetime.utcnow() - timedelta(hours=1)
    
    # Run queries concurrently
    tasks = [
        sensor_collection.count_documents({
            "timestamp": {"$gte": time_24h_ago}
        }),
        sensor_collection.distinct("sensor_id", {
            "timestamp": {"$gte": time_1h_ago}
        }),
        alerts_collection.count_documents({
            "status": "active"
        }),
        get_average_health_score()
    ]
    
    [total_readings, active_sensors, active_alerts, avg_health] = await asyncio.gather(*tasks)
    
    # Get latest voltage and current averages
    latest_data_cursor = sensor_collection.aggregate([
        {"$sort": {"timestamp": -1}},
        {"$limit": 100},
        {"$group": {
            "_id": None,
            "avg_voltage": {"$avg": "$voltage"},
            "avg_current": {"$avg": "$current"},
            "avg_temperature": {"$avg": "$temperature"},
            "avg_power": {"$avg": "$power"}
        }}
    ])
    
    latest_data = await latest_data_cursor.to_list(length=1)
    
    summary = {
        "total_readings_24h": total_readings,
        "active_sensors": len(active_sensors),
        "active_alerts": active_alerts,
        "average_health_score": avg_health,
        "average_voltage": latest_data[0]["avg_voltage"] if latest_data else 0,
        "average_current": latest_data[0]["avg_current"] if latest_data else 0,
        "average_temperature": latest_data[0]["avg_temperature"] if latest_data else 0,
        "average_power": latest_data[0]["avg_power"] if latest_data else 0,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    return summary

async def get_average_health_score():
    """Calculate average health score across all nodes"""
    health_collection = mongodb.db.health_scores
    
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$node_id",
            "latest_score": {"$first": "$score"}
        }},
        {"$group": {
            "_id": None,
            "avg_score": {"$avg": "$latest_score"}
        }}
    ]
    
    result = await health_collection.aggregate(pipeline).to_list(length=1)
    return result[0]["avg_score"] if result else 0

@router.get("/nodes")
async def get_all_nodes():
    """
    Get all nodes with their latest data
    """
    sensor_collection = mongodb.db.sensor_data
    
    # Get latest reading for each node
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$node_id",
            "latest_data": {"$first": "$$ROOT"},
            "location": {"$first": "$location"}
        }},
        {"$project": {
            "node_id": "$_id",
            "location": 1,
            "voltage": "$latest_data.voltage",
            "current": "$latest_data.current",
            "temperature": "$latest_data.temperature",
            "power": "$latest_data.power",
            "timestamp": "$latest_data.timestamp",
            "_id": 0
        }}
    ]
    
    nodes = await sensor_collection.aggregate(pipeline).to_list(length=None)
    
    # Get health score for each node
    health_collection = mongodb.db.health_scores
    for node in nodes:
        health = await health_collection.find_one(
            {"node_id": node["node_id"]},
            sort=[("timestamp", -1)]
        )
        node["health_score"] = health["score"] if health else None
    
    return nodes