#!/bin/bash

# EduLMS v2 Stop Services Script
# Stops FastAPI backend and Nuxt frontend

echo "🛑 Stopping EduLMS v2 services..."

# Stop backend
if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔴 Stopping FastAPI backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm logs/backend.pid
    else
        echo "⚠️  Backend process not found"
    fi
else
    echo "⚠️  Backend PID file not found"
fi

# Stop frontend
if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🔴 Stopping Nuxt frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm logs/frontend.pid
    else
        echo "⚠️  Frontend process not found"
    fi
else
    echo "⚠️  Frontend PID file not found"
fi

# Stop any remaining uvicorn processes
pkill -f "uvicorn main:app" 2>/dev/null || true

echo "✅ All services stopped"
