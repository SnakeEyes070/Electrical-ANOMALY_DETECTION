# check_mongodb_data.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

async def check_mongodb_data():
    # Use your actual MongoDB URL
    url = "mongodb+srv://billoreparth80_db_user:Kyv8bP9XXT1BJKUx@ghostapi.3qe1pdk.mongodb.net/?appName=GHOSTapi"
    
    client = AsyncIOMotorClient(url)
    db = client.ghost_db
    
    print("🔍 Checking MongoDB Atlas Data...")
    print("="*50)
    
    # Check collections
    collections = await db.list_collection_names()
    print(f"📚 Collections found: {collections}")
    
    # Count sensor data
    sensor_count = await db.sensor_data.count_documents({})
    print(f"📊 Total sensor readings: {sensor_count}")
    
    # Get latest 5 readings
    print("\n🎯 Latest 5 sensor readings:")
    cursor = db.sensor_data.find().sort("timestamp", -1).limit(5)
    
    async for doc in cursor:
        print(f"  ┌─ {doc.get('sensor_id', 'Unknown')}")
        print(f"  │  Voltage: {doc.get('voltage', 'N/A')}V")
        print(f"  │  Current: {doc.get('current', 'N/A')}A")
        print(f"  │  Temperature: {doc.get('temperature', 'N/A')}°C")
        print(f"  └─ Time: {doc.get('timestamp', 'N/A')}")
        print()
    
    # Check data from last 1 hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_count = await db.sensor_data.count_documents({
        "timestamp": {"$gte": one_hour_ago.isoformat()}
    })
    print(f"⏰ Readings in last hour: {recent_count}")
    
    client.close()
    
    return sensor_count

if __name__ == "__main__":
    count = asyncio.run(check_mongodb_data())
    if count > 0:
        print("✅ MongoDB has data! Your backend should display it.")
    else:
        print("❌ MongoDB is empty. No data to display yet.")