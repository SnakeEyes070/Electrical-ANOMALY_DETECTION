# test_encoding.py
import os

print("🔍 Testing .env file encoding...")

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check if .env exists
env_path = ".env"
if os.path.exists(env_path):
    print(f"✅ .env file exists at: {env_path}")
    
    # Try to read with different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'utf-16']
    
    for encoding in encodings:
        try:
            with open(env_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"✅ Successfully read with {encoding}")
            print(f"First 100 chars: {content[:100]}")
            break
        except UnicodeDecodeError as e:
            print(f"❌ Failed with {encoding}: {e}")
        except Exception as e:
            print(f"⚠️  Error with {encoding}: {e}")
else:
    print("❌ .env file not found")

# List all files
print("\n📂 Files in current directory:")
for file in os.listdir('.'):
    print(f"  - {file}")