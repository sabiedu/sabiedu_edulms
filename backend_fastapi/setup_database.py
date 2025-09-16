#!/usr/bin/env python3
"""
Database setup script for EduLMS v2
Executes the schema.sql file to create tables
"""

import asyncio
import os
from sqlalchemy import text
from database.connection import async_engine, logger
from dotenv import load_dotenv

load_dotenv()

async def setup_database():
    """Setup database using schema.sql"""
    try:
        # Read schema.sql file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split SQL statements (simple split by semicolon)
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        async with async_engine.begin() as conn:
            logger.info("Setting up database...")
            
            for statement in statements:
                if statement and not statement.startswith('--') and statement.strip():
                    try:
                        await conn.execute(text(statement))
                        logger.info(f"✓ Executed: {statement[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.info(f"⚠ Skipped (already exists): {statement[:50]}...")
                        else:
                            logger.error(f"✗ Failed: {statement[:50]}... - {e}")
            
            logger.info("Database setup completed successfully!")
            
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_database())
