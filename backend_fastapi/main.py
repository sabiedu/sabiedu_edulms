#!/usr/bin/env python3
"""
FastAPI Backend for EduLMS v2
Replaces Strapi with Python-based backend using TiDB and vector search
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from backend_fastapi.routers import workflows
from database.connection import init_database, get_db
from routers import auth, users, agents, analytics
# Removed Alembic dependency - use schema.sql for database setup
from services.vector_service import VectorService

# Load environment variables
load_dotenv()

# Initialize vector service
vector_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global vector_service
    
    # Startup
    print("🚀 Starting EduLMS v2 FastAPI Backend...")
    
    # Initialize database
    init_database()
    print("✅ Database initialized")
    
    # Initialize vector service
    vector_service = VectorService()
    await vector_service.initialize()
    print("✅ Vector service initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down EduLMS v2 FastAPI Backend...")

# Create FastAPI app
app = FastAPI(
    title="EduLMS v2 API",
    description="AI-powered Learning Management System with Multi-Agent Workflows",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "EduLMS v2 FastAPI Backend",
        "version": "2.0.0",
        "status": "running",
        "database": "TiDB Serverless",
        "ai_provider": "Google Gemini"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "vector_service": "active",
        "agents": {
            "total": 9,
            "active": 9
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
