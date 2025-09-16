#!/bin/bash

# EduLMS v2 Environment Setup Script
# Sets up development environment for FastAPI backend and Nuxt frontend

echo "🔧 Setting up EduLMS v2 Development Environment..."

# Check for required tools
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual credentials:"
    echo "   - TIDB_PASSWORD"
    echo "   - JWT_SECRET_KEY"
    echo "   - GOOGLE_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Setup FastAPI backend
echo "🐍 Setting up FastAPI backend..."
cd backend_fastapi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ FastAPI backend setup complete"
cd ..

# Setup Nuxt frontend
echo "🌐 Setting up Nuxt frontend..."
cd frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo "✅ Nuxt frontend setup complete"
cd ..

# Create logs directory
mkdir -p logs

echo "✅ EduLMS v2 environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run development servers: ./scripts/dev-start.sh"
echo "3. Or use Docker: docker-compose up -d"
echo ""
echo "📚 Documentation:"
echo "   - Backend: backend_fastapi/README.md"
echo "   - Frontend: frontend/README.md"
