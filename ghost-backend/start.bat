@echo off
echo ========================================
echo   GHOST Backend Startup Script
echo ========================================
echo.

REM Check if in correct directory
if not exist "main.py" (
    echo ❌ ERROR: main.py not found!
    echo Please run this from E:\newghost\ghost-backend
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call ..\ghost_env\Scripts\activate

REM Start the backend
echo Starting FastAPI backend...
echo.
echo 🌐 API will be available at: http://localhost:8000
echo 📚 Documentation: http://localhost:8000/docs
echo 🩺 Health check: http://localhost:8000/health
echo.
echo ========================================
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python main.py

pause