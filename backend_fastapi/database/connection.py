#!/usr/bin/env python3
"""
Database connection and configuration for TiDB Serverless
"""

import os
import asyncio
from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import logging
import pymysql

# Load environment variables
load_dotenv()

# Create declarative base
Base = declarative_base()

# Database configuration - Direct values for TiDB Serverless
TIDB_HOST = os.getenv("TIDB_HOST")  
TIDB_PORT = os.getenv("TIDB_PORT")
TIDB_USER = os.getenv("TIDB_USER")
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
TIDB_DATABASE = os.getenv("TIDB_DATABASE")

# Extract prefix from username if it contains a dot
if "." in TIDB_USER:
    TIDB_USER_PREFIX = TIDB_USER.split(".")[0]
    TIDB_USER_BASE = TIDB_USER.split(".")[1]
else:
    TIDB_USER_PREFIX = ""
    TIDB_USER_BASE = TIDB_USER

TIDB_USERNAME_FULL = TIDB_USER  # Use the full username as provided

def get_db_engine():
    """Create database engine with proper SSL configuration"""
    connect_args = {
        "ssl": {
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        }
    }
    
    # Check for SSL certificate file
    ssl_ca_path = os.getenv("SSL_CA_PATH", "")
    ca_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "isrgrootx1.pem")
    if ssl_ca_path and os.path.exists(ssl_ca_path):
        connect_args["ssl"]["ssl_ca"] = ssl_ca_path
    elif os.path.exists(ca_path):
        connect_args["ssl"]["ssl_ca"] = ca_path
    else:
        logger.warning("No SSL CA found; connection may be insecure. Download isrgrootx1.pem for TiDB Cloud.")
        connect_args["ssl"] = {"ssl_ca": None, "ssl_verify_cert": False}  # Insecure fallback; avoid in prod
    
    return create_engine(
        URL.create(
            drivername="mysql+pymysql",
            username=TIDB_USERNAME_FULL,  # Use prefixed username, e.g., 3pTAoNNegb47Uc8.root
            password=TIDB_PASSWORD,
            host=TIDB_HOST,
            port=TIDB_PORT,
            database=TIDB_DATABASE,
        ),
        connect_args=connect_args,
        poolclass=NullPool,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )

# Create engine and session maker
engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# For backward compatibility, create an async_engine alias
async_engine = engine

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database connection"""
    try:
        with engine.begin() as conn:
            # Test connection
            conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            logger.info("Database initialized successfully (tables should be created manually using schema.sql)")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def get_sync_db():
    """Get synchronous database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise

def test_connection():
    """Test database connection"""
    try:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test connection
    test_connection()