#!/bin/bash

# EduLMS v2 Stop Development Services Script
# Stops FastAPI backend and Nuxt frontend development servers

echo "🛑 Stopping EduLMS v2 development services..."

# Stop development backend
if [ -f logs/backend-dev.pid ]; then
    BACKEND_PID=$(cat logs/backend-dev.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔴 Stopping FastAPI development server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm logs/backend-dev.pid
    else
        echo "⚠️  Backend development process not found"
    fi
else
    echo "⚠️  Backend development PID file not found"
fi

# Stop development frontend
if [ -f logs/frontend-dev.pid ]; then
    FRONTEND_PID=$(cat logs/frontend-dev.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🔴 Stopping Nuxt development server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm logs/frontend-dev.pid
    else
        echo "⚠️  Frontend development process not found"
    fi
else
    echo "⚠️  Frontend development PID file not found"
fi

# Stop any remaining development processes
pkill -f "python main.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

echo "✅ All development services stopped"
