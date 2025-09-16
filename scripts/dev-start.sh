#!/bin/bash

# EduLMS v2 Development Start Script
# Starts FastAPI backend and Nuxt frontend in development mode

echo "🚀 Starting EduLMS v2 Development Environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    exit 1
fi

echo "✅ Environment file found"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start FastAPI backend in development mode
echo "🔧 Starting FastAPI backend (development)..."
cd backend_fastapi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start backend with auto-reload
echo "🚀 Starting FastAPI with auto-reload..."
nohup python main.py > ../logs/backend-dev.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend-dev.pid

cd ..

# Start Nuxt frontend in development mode
echo "🔧 Starting Nuxt frontend (development)..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend with auto-reload
echo "🚀 Starting Nuxt with auto-reload..."
nohup npm run dev > ../logs/frontend-dev.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend-dev.pid

cd ..

echo "✅ EduLMS v2 development environment started!"
echo "📊 Backend: http://localhost:8000 (auto-reload enabled)"
echo "🌐 Frontend: http://localhost:3000 (auto-reload enabled)"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Development Logs:"
echo "   Backend: logs/backend-dev.log"
echo "   Frontend: logs/frontend-dev.log"
echo ""
echo "🛑 To stop services:"
echo "   ./scripts/stop-dev.sh"
