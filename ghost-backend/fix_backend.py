# fix_backend.py
print("🔧 Fixing backend to use MongoDB...")

# 1. Create proper database.py
database_code = '''
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            mongodb_url = "mongodb+srv://billoreparth80_db_user:Kyv8bP9XXT1BJKUx@ghostapi.3qe1pdk.mongodb.net/?appName=GHOSTapi"
            
            print(f"🔗 Connecting to MongoDB Atlas...")
            
            self.client = AsyncIOMotorClient(mongodb_url)
            self.db = self.client.ghost_db
            
            await self.db.command("ping")
            print("✅ Connected to MongoDB Atlas!")
            
        except Exception as e:
            print(f"❌ MongoDB Error: {e}")
            raise
    
    async def close(self):
        if self.client:
            self.client.close()
            print("📤 MongoDB connection closed")

mongodb = MongoDB()
'''

with open('database.py', 'w', encoding='utf-8') as f:
    f.write(database_code)
    print("✅ Updated database.py")

print("\n🎯 Now restart your backend:")
print("1. Press Ctrl+C to stop current backend")
print("2. Run: python main.py")
print("3. Send test data: python test_flow.py")
print("4. Check dashboard: http://localhost:3000")