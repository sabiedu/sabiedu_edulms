#!/bin/bash

# EduLMS v2 Production Deployment Script
# Deploys FastAPI backend and Nuxt frontend

set -e

echo "🚀 Starting EduLMS v2 Production Deployment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$TIDB_HOST" ] || [ -z "$TIDB_PASSWORD" ] || [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Missing required environment variables. Check TIDB_HOST, TIDB_PASSWORD, and GOOGLE_API_KEY"
    exit 1
fi

echo "✅ Environment variables validated"

# Build and deploy FastAPI backend
echo "📦 Building FastAPI backend..."
cd backend_fastapi

# Install dependencies
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Test database connection
echo "🔍 Testing database connection..."
python -c "
import asyncio
from database.connection import test_connection
asyncio.run(test_connection())
"

echo "✅ Database connection successful"

# Start FastAPI backend
echo "🚀 Starting FastAPI backend..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid

cd ..

# Build and deploy frontend
echo "📦 Building Nuxt frontend..."
cd frontend

# Install dependencies
npm ci

# Build for production
npm run build

# Start frontend
echo "🚀 Starting Nuxt frontend..."
nohup npm run preview > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

cd ..

# Create logs directory if it doesn't exist
mkdir -p logs

echo "✅ EduLMS v2 deployed successfully!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend: logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🛑 To stop services:"
echo "   ./scripts/stop-services.sh"
