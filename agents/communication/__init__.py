"""
Agent Communication Module

This module provides comprehensive TiDB-based communication infrastructure
for the multi-agent system, including messaging, caching, session management,
task queuing, and real-time notifications.
"""

from .tidb_service import (
    TiDBCommunicationService,
    AgentMessage,
    AgentTask,
    AgentSessionData,
    TaskStatus,
    MessageCallback
)

from .cache_manager import (
    CacheManager,
    CacheEntry,
    CacheStats
)

from .session_manager import (
    SessionManager,
    ConversationTurn,
    SessionMetrics,
    SessionSummary,
    SessionStatus
)

from .task_queue_manager import (
    TaskQueueManager,
    TaskPriority,
    BatchResult,
    TaskQueueStats,
    TaskFilter
)

from .notification_service import (
    TriggerNotificationService,
    MessagePollingService,
    SubscriptionType,
    Subscription,
    NotificationEvent
)

__all__ = [
    # Core service
    "TiDBCommunicationService",
    "AgentMessage",
    "AgentTask", 
    "AgentSessionData",
    "TaskStatus",
    "MessageCallback",
    
    # Cache management
    "CacheManager",
    "CacheEntry",
    "CacheStats",
    
    # Session management
    "SessionManager",
    "ConversationTurn",
    "SessionMetrics",
    "SessionSummary",
    "SessionStatus",
    
    # Task queue management
    "TaskQueueManager",
    "TaskPriority",
    "BatchResult",
    "TaskQueueStats",
    "TaskFilter",
    
    # Notification services
    "TriggerNotificationService",
    "MessagePollingService",
    "SubscriptionType",
    "Subscription",
    "NotificationEvent"
]


class AgentCommunicationHub:
    """
    Unified communication hub that integrates all communication services.
    
    Provides a single interface for all agent communication needs including
    messaging, caching, sessions, task queuing, and notifications.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        pool_size: int = 10,
        ssl_disabled: bool = False
    ):
        """
        Initialize the communication hub.
        
        Args:
            host: TiDB host
            port: TiDB port
            user: Database user
            password: Database password
            database: Database name
            pool_size: Connection pool size
            ssl_disabled: Whether to disable SSL
        """
        # Initialize core communication service
        self.comm_service = TiDBCommunicationService(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            pool_size=pool_size,
            ssl_disabled=ssl_disabled
        )
        
        # Initialize specialized managers
        self.cache_manager = CacheManager(self.comm_service)
        self.session_manager = SessionManager(self.comm_service)
        self.task_queue_manager = TaskQueueManager(self.comm_service)
        self.notification_service = TriggerNotificationService(self.comm_service)
        self.polling_service = MessagePollingService(self.comm_service)
    
    async def start(self) -> None:
        """Start all communication services."""
        await self.cache_manager.start_cleanup_scheduler()
        await self.notification_service.start_notification_service()
        await self.polling_service.start_polling_service()
    
    async def stop(self) -> None:
        """Stop all communication services."""
        await self.cache_manager.stop_cleanup_scheduler()
        await self.notification_service.stop_notification_service()
        await self.polling_service.stop_polling_service()
        await self.comm_service.close()
    
    async def health_check(self) -> dict:
        """
        Perform comprehensive health check on all services.
        
        Returns:
            Health status for all services
        """
        return await self.comm_service.health_check()


# Convenience function for creating communication hub
def create_communication_hub(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    **kwargs
) -> AgentCommunicationHub:
    """
    Create and return a configured communication hub.
    
    Args:
        host: TiDB host
        port: TiDB port
        user: Database user
        password: Database password
        database: Database name
        **kwargs: Additional configuration options
        
    Returns:
        Configured AgentCommunicationHub instance
    """
    return AgentCommunicationHub(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        **kwargs
    )