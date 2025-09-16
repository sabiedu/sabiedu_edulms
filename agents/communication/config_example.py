"""
Configuration Example for TiDB Communication Infrastructure

This module provides example configurations for setting up the TiDB
communication infrastructure in different environments.
"""

import os
from typing import Dict, Any


def get_development_config() -> Dict[str, Any]:
    """
    Get development environment configuration.
    
    Returns:
        Development configuration dictionary
    """
    return {
        "host": os.getenv("TIDB_HOST", "localhost"),
        "port": int(os.getenv("TIDB_PORT", "4000")),
        "user": os.getenv("TIDB_USER", "root"),
        "password": os.getenv("TIDB_PASSWORD", ""),
        "database": os.getenv("TIDB_DATABASE", "edulms_v2"),
        "pool_size": 5,
        "ssl_disabled": True
    }


def get_production_config() -> Dict[str, Any]:
    """
    Get production environment configuration.
    
    Returns:
        Production configuration dictionary
    """
    return {
        "host": os.getenv("TIDB_HOST"),
        "port": int(os.getenv("TIDB_PORT", "4000")),
        "user": os.getenv("TIDB_USER"),
        "password": os.getenv("TIDB_PASSWORD"),
        "database": os.getenv("TIDB_DATABASE"),
        "pool_size": int(os.getenv("TIDB_POOL_SIZE", "20")),
        "ssl_disabled": False
    }


def get_test_config() -> Dict[str, Any]:
    """
    Get test environment configuration.
    
    Returns:
        Test configuration dictionary
    """
    return {
        "host": os.getenv("TIDB_TEST_HOST", "localhost"),
        "port": int(os.getenv("TIDB_TEST_PORT", "4000")),
        "user": os.getenv("TIDB_TEST_USER", "root"),
        "password": os.getenv("TIDB_TEST_PASSWORD", ""),
        "database": os.getenv("TIDB_TEST_DATABASE", "edulms_v2_test"),
        "pool_size": 3,
        "ssl_disabled": True
    }


# Environment variable template for .env file
ENV_TEMPLATE = """
# TiDB Configuration
TIDB_HOST=localhost
TIDB_PORT=4000
TIDB_USER=root
TIDB_PASSWORD=your_password_here
TIDB_DATABASE=edulms_v2
TIDB_POOL_SIZE=10

# Test Database Configuration
TIDB_TEST_HOST=localhost
TIDB_TEST_PORT=4000
TIDB_TEST_USER=root
TIDB_TEST_PASSWORD=your_test_password_here
TIDB_TEST_DATABASE=edulms_v2_test

# Agent Configuration
AGENT_COMMUNICATION_TIMEOUT=30000
CACHE_DEFAULT_TTL=3600
MAX_CONCURRENT_AGENTS=10
CLEANUP_INTERVAL=86400
MAX_MESSAGE_RETENTION_DAYS=30
BATCH_PROCESSING_SIZE=100

# Logging Configuration
LOG_LEVEL=INFO
"""


def create_env_file(filename: str = ".env") -> None:
    """
    Create a .env file with template configuration.
    
    Args:
        filename: Name of the environment file to create
    """
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(ENV_TEMPLATE)
        print(f"Created {filename} with template configuration")
    else:
        print(f"{filename} already exists")


# Usage examples
USAGE_EXAMPLES = """
# Basic Usage Example

from agents.communication import create_communication_hub
import asyncio

async def main():
    # Create communication hub
    hub = create_communication_hub(
        host="localhost",
        port=4000,
        user="root",
        password="password",
        database="edulms_v2"
    )
    
    # Start services
    await hub.start()
    
    # Send a message
    message_id = await hub.comm_service.send_message(
        channel="coordination",
        sender_agent="master-agent",
        message={"type": "task_assignment", "task": "analyze_content"}
    )
    
    # Cache a result
    await hub.cache_manager.set(
        key="analysis_result_123",
        value={"score": 0.85, "topics": ["python", "programming"]},
        ttl_seconds=3600,
        agent_name="content-curator-agent"
    )
    
    # Create a session
    session_id = await hub.session_manager.create_session(
        user_id="user_123",
        agents_involved=["master-agent", "tutor-agent"],
        initial_state={"learning_goal": "python_basics"}
    )
    
    # Enqueue a task
    task_id = await hub.task_queue_manager.enqueue_task(
        agent_name="assessment-agent",
        task_type="generate_quiz",
        parameters={"topic": "python_loops", "difficulty": "beginner"}
    )
    
    # Stop services
    await hub.stop()

if __name__ == "__main__":
    asyncio.run(main())
"""

if __name__ == "__main__":
    print("TiDB Communication Infrastructure Configuration")
    print("=" * 50)
    print("\nAvailable configurations:")
    print("- Development:", get_development_config())
    print("- Production:", get_production_config())
    print("- Test:", get_test_config())
    print("\nUsage Examples:")
    print(USAGE_EXAMPLES)