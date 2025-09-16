@echo off
REM EduLMS v2 Production Deployment Script for Windows
REM Deploys FastAPI backend and Nuxt frontend

echo 🚀 Starting EduLMS v2 Production Deployment...

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found. Please create one from .env.example
    exit /b 1
)

echo ✅ Environment file found

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Build and deploy FastAPI backend
echo 📦 Building FastAPI backend...
cd backend_fastapi

REM Install dependencies
pip install -r requirements.txt



REM Test database connection
echo 🔍 Testing database connection...
python -c "import asyncio; from database.connection import test_connection; asyncio.run(test_connection())"

if errorlevel 1 (
    echo ❌ Database connection failed
    exit /b 1
)

echo ✅ Database connection successful

REM Start FastAPI backend
echo 🚀 Starting FastAPI backend...
start /B uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > ..\logs\backend.log 2>&1

cd ..

REM Build and deploy frontend
echo 📦 Building Nuxt frontend...
cd frontend

REM Install dependencies
call npm ci

REM Build for production
call npm run build

REM Start frontend
echo 🚀 Starting Nuxt frontend...
start /B npm run preview > ..\logs\frontend.log 2>&1

cd ..

echo ✅ EduLMS v2 deployed successfully!
echo 📊 Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:3000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 📝 Logs:
echo    Backend: logs\backend.log
echo    Frontend: logs\frontend.log
echo.
echo 🛑 To stop services, close the command windows or use Task Manager

pause
