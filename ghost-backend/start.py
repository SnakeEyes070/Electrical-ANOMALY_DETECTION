# start.py - Simple start script
import subprocess
import sys
import os

def start_backend():
    print("🚀 Starting GHOST Backend...")
    
    # Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check for main.py
    if not os.path.exists("main.py"):
        print("❌ main.py not found in current directory!")
        print("Please run this script from E:\\newghost\\ghost-backend")
        return
    
    # Start the backend
    try:
        print("⚡ Launching FastAPI server...")
        print("📡 API will be available at: http://localhost:8000")
        print("📚 Documentation: http://localhost:8000/docs")
        print("\n" + "="*50)
        print("Press Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        # Run the server
        subprocess.run([sys.executable, "main.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_backend()