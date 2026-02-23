# check_data.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    url = "mongodb+srv://billoreparth80_db_user:Kyv8bP9XXT1BJKUx@ghostapi.3qe1pdk.mongodb.net/?appName=GHOSTapi"
    
    client = AsyncIOMotorClient(url)
    db = client.ghost_db
    
    # Check collections
    collections = await db.list_collection_names()
    print(f"📊 Collections: {collections}")
    
    # Count sensor data
    sensor_count = await db.sensor_data.count_documents({})
    print(f"📈 Sensor data count: {sensor_count}")
    
    # Show latest sensor data
    cursor = db.sensor_data.find().sort("timestamp", -1).limit(3)
    docs = await cursor.to_list(length=3)
    
    if docs:
        print("\n🎯 Latest sensor readings:")
        for doc in docs:
            print(f"  {doc.get('sensor_id')}: {doc.get('voltage')}V, {doc.get('current')}A")
    
    # Check anomalies
    if "anomalies" in collections:
        anomaly_count = await db.anomalies.count_documents({})
        print(f"\n⚠️  Anomalies count: {anomaly_count}")
    
    client.close()

asyncio.run(check())