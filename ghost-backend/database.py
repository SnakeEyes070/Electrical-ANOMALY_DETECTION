# database.py
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            # Your MongoDB Atlas URL
            mongodb_url = "mongodb+srv://billoreparth80_db_user:Kyv8bP9XXT1BJKUx@ghostapi.3qe1pdk.mongodb.net/?appName=GHOSTapi"
            
            print("🔗 Connecting to MongoDB Atlas...")
            
            self.client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000
            )
            
            self.db = self.client.get_database("ghost_db")
            
            # Test connection
            await self.db.command("ping")
            print("✅ Connected to MongoDB Atlas successfully!")
            
            # Create indexes
            await self.db.sensor_data.create_index([("timestamp", -1)])
            await self.db.sensor_data.create_index([("sensor_id", 1)])
            
        except Exception as e:
            print(f"❌ MongoDB Connection Error: {e}")
            raise
    
    async def close(self):
        if self.client:
            self.client.close()
            print("📤 MongoDB connection closed")

mongodb = MongoDB()