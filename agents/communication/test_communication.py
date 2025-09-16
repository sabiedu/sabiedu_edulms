"""
Basic test for TiDB communication infrastructure.

This module provides basic tests to verify the communication infrastructure
is working correctly with the database.
"""

import asyncio
import os
import logging
from datetime import datetime, timedelta

from . import (
    AgentCommunicationHub,
    TaskPriority,
    SubscriptionType,
    SessionStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_communication_infrastructure():
    """Test the basic functionality of the communication infrastructure."""
    
    # Database configuration (using environment variables)
    config = {
        "host": os.getenv("TIDB_HOST", "localhost"),
        "port": int(os.getenv("TIDB_PORT", "4000")),
        "user": os.getenv("TIDB_USER", "root"),
        "password": os.getenv("TIDB_PASSWORD", ""),
        "database": os.getenv("TIDB_DATABASE", "edulms_v2"),
        "ssl_disabled": True  # For local development
    }
    
    logger.info("Starting communication infrastructure test...")
    
    try:
        # Create communication hub
        hub = AgentCommunicationHub(**config)
        
        # Test database connection
        logger.info("Testing database connection...")
        health = await hub.health_check()
        logger.info(f"Database health: {health}")
        
        if health["status"] != "healthy":
            logger.error("Database connection failed!")
            return False
        
        # Test messaging
        logger.info("Testing messaging...")
        message_id = await hub.comm_service.send_message(
            channel="test",
            sender_agent="test-agent",
            message={"type": "test", "content": "Hello World!"},
            priority=5
        )
        logger.info(f"Message sent with ID: {message_id}")
        
        # Test message polling
        messages = await hub.comm_service.poll_messages("test", "test-agent", limit=5)
        logger.info(f"Polled {len(messages)} messages")
        
        if messages:
            # Mark first message as processed
            await hub.comm_service.mark_message_processed(messages[0].id, "test-agent")
            logger.info("Message marked as processed")
        
        # Test caching
        logger.info("Testing caching...")
        await hub.cache_manager.set(
            key="test-key",
            value={"data": "test-value", "timestamp": datetime.now().isoformat()},
            ttl_seconds=300,
            agent_name="test-agent",
            result_type="test"
        )
        
        cached_value = await hub.cache_manager.get("test-key", "test-agent")
        logger.info(f"Cached value retrieved: {cached_value}")
        
        # Test session management
        logger.info("Testing session management...")
        session_id = await hub.session_manager.create_session(
            user_id="test-user",
            agents_involved=["test-agent", "master-agent"],
            initial_state={"step": 1},
            metadata={"test": True}
        )
        logger.info(f"Session created with ID: {session_id}")
        
        # Add conversation turn
        await hub.session_manager.add_conversation_turn(
            session_id=session_id,
            agent_name="test-agent",
            message_type="greeting",
            content={"message": "Hello from test agent!"},
            processing_time_ms=150
        )
        logger.info("Conversation turn added")
        
        # Test task queue
        logger.info("Testing task queue...")
        task_id = await hub.task_queue_manager.enqueue_task(
            agent_name="test-agent",
            task_type="test-task",
            parameters={"input": "test-data"},
            priority=TaskPriority.NORMAL,
            max_retries=3
        )
        logger.info(f"Task enqueued with ID: {task_id}")
        
        # Test task dequeue
        task = await hub.task_queue_manager.dequeue_task("test-agent")
        if task:
            logger.info(f"Task dequeued: {task.task_id}")
            
            # Complete the task
            await hub.task_queue_manager.complete_task(
                task_id=task.task_id,
                result={"output": "test-result"},
                processing_time_ms=200
            )
            logger.info("Task completed")
        
        # Test notifications
        logger.info("Testing notifications...")
        await hub.notification_service.subscribe_agent(
            agent_name="test-agent",
            channel="test-notifications",
            subscription_type=SubscriptionType.ALL
        )
        logger.info("Agent subscribed to notifications")
        
        # Get statistics
        logger.info("Getting statistics...")
        cache_stats = await hub.cache_manager.get_cache_stats()
        logger.info(f"Cache stats: {cache_stats.total_entries} entries")
        
        queue_stats = await hub.task_queue_manager.get_queue_stats()
        logger.info(f"Queue stats: {queue_stats.total_tasks} total tasks")
        
        # Cleanup test data
        logger.info("Cleaning up test data...")
        await hub.cache_manager.invalidate_pattern("test-%", "test-agent")
        await hub.session_manager.complete_session(session_id, "test-completed")
        
        logger.info("✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    success = await test_communication_infrastructure()
    if success:
        print("\n🎉 Communication infrastructure test completed successfully!")
    else:
        print("\n💥 Communication infrastructure test failed!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())