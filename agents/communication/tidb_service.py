"""
TiDB Communication Service for Agent Messaging

This module provides the core TiDB-based communication infrastructure for the multi-agent system.
It handles message passing, caching, session management, and task queuing using database tables.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.pooling import MySQLConnectionPool
import mysql.connector.pooling
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class MessageCallback:
    """Callback interface for message processing."""
    
    def __call__(self, message: Dict[str, Any]) -> None:
        """Process received message."""
        pass


@dataclass
class AgentMessage:
    """Agent message data structure."""
    id: Optional[int] = None
    channel: str = ""
    sender_agent: str = ""
    recipient_agent: Optional[str] = None
    message: Dict[str, Any] = None
    priority: int = 5
    created_at: Optional[datetime] = None
    processed: bool = False
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None

    def __post_init__(self):
        if self.message is None:
            self.message = {}


@dataclass
class AgentTask:
    """Agent task data structure."""
    id: Optional[int] = None
    task_id: str = ""
    agent_name: str = ""
    task_type: str = ""
    parameters: Dict[str, Any] = None
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if not self.task_id:
            self.task_id = str(uuid.uuid4())


@dataclass
class AgentSessionData:
    """Agent session data structure."""
    id: Optional[int] = None
    session_id: str = ""
    user_id: str = ""
    agents_involved: List[str] = None
    session_state: Dict[str, Any] = None
    conversation_history: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.agents_involved is None:
            self.agents_involved = []
        if self.session_state is None:
            self.session_state = {}
        if self.conversation_history is None:
            self.conversation_history = []
        if self.metadata is None:
            self.metadata = {}
        if not self.session_id:
            self.session_id = str(uuid.uuid4())


class TiDBCommunicationService:
    """
    TiDB-based communication service for multi-agent coordination.
    
    Provides message passing, caching, session management, and task queuing
    using TiDB database tables for reliable, queryable agent communication.
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        pool_name: str = "agent_pool",
        pool_size: int = 10,
        ssl_disabled: bool = False,
    ):
        """
        Initialize TiDB communication service.
        
        Args:
            host: TiDB host
            port: TiDB port
            user: Database user
            password: Database password
            database: Database name
            pool_name: Connection pool name
            pool_size: Maximum connections in pool
            ssl_disabled: Whether to disable SSL
        """
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "autocommit": True,
            "charset": "utf8mb4",
            "use_unicode": True,
            "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO",
        }
        
        if ssl_disabled:
            self.config["ssl_disabled"] = True
        
        self.pool_name = pool_name
        self.pool_size = pool_size
        self.pool: Optional[MySQLConnectionPool] = None
        
        # Initialize connection pool
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize MySQL connection pool."""
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=self.pool_name,
                pool_size=self.pool_size,
                pool_reset_session=True,
                **self.config
            )
            logger.info(f"Initialized TiDB connection pool '{self.pool_name}' with {self.pool_size} connections")
        except MySQLError as e:
            logger.error(f"Failed to initialize TiDB connection pool: {e}")
            raise

    def _get_connection(self):
        """Get connection from pool."""
        if not self.pool:
            raise RuntimeError("Connection pool not initialized")
        return self.pool.get_connection()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None, 
        fetch: bool = False,
        fetch_one: bool = False
    ) -> Optional[Union[List[tuple], tuple]]:
        """
        Execute database query with retry logic.
        
        Args:
            query: SQL query
            params: Query parameters
            fetch: Whether to fetch results
            fetch_one: Whether to fetch only one result
            
        Returns:
            Query results if fetch=True, None otherwise
        """
        connection = None
        cursor = None
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Log query execution
            start_time = datetime.now()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = None
            if fetch:
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
            
            connection.commit()
            
            # Log successful operation
            await self._log_operation(
                agent_name="system",
                operation_type="database_query",
                operation_data={
                    "query_type": query.split()[0].upper(),
                    "execution_time_ms": execution_time,
                    "rows_affected": cursor.rowcount if not fetch else len(result) if result else 0
                },
                execution_time_ms=int(execution_time),
                success=True
            )
            
            return result
            
        except MySQLError as e:
            logger.error(f"Database query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            
            # Log failed operation
            await self._log_operation(
                agent_name="system",
                operation_type="database_query",
                operation_data={
                    "query_type": query.split()[0].upper(),
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Message Operations
    async def send_message(
        self, 
        channel: str, 
        sender_agent: str, 
        message: Dict[str, Any],
        recipient_agent: Optional[str] = None,
        priority: int = 5
    ) -> str:
        """
        Send message to a channel.
        
        Args:
            channel: Target channel
            sender_agent: Sending agent name
            message: Message content
            recipient_agent: Specific recipient (optional)
            priority: Message priority (1-10, lower is higher priority)
            
        Returns:
            Message ID
        """
        query = """
        INSERT INTO agent_messages (channel, sender_agent, recipient_agent, message, priority)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        params = (
            channel,
            sender_agent,
            recipient_agent,
            json.dumps(message),
            priority
        )
        
        try:
            await self._execute_query(query, params)
            
            # Get the inserted message ID
            id_query = "SELECT LAST_INSERT_ID() as id"
            result = await self._execute_query(id_query, fetch=True, fetch_one=True)
            message_id = str(result["id"]) if result else str(uuid.uuid4())
            
            # Log operation
            await self._log_operation(
                agent_name=sender_agent,
                operation_type="send_message",
                operation_data={
                    "message_id": message_id,
                    "channel": channel,
                    "recipient": recipient_agent,
                    "priority": priority,
                    "message_type": message.get("type", "unknown")
                },
                success=True
            )
            
            logger.debug(f"Message sent: {sender_agent} -> {channel} (ID: {message_id})")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            await self._log_operation(
                agent_name=sender_agent,
                operation_type="send_message",
                operation_data={
                    "channel": channel,
                    "recipient": recipient_agent,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def poll_messages(
        self, 
        channel: str, 
        agent_name: str,
        limit: int = 10,
        include_processed: bool = False
    ) -> List[AgentMessage]:
        """
        Poll messages from a channel for a specific agent.
        
        Args:
            channel: Channel to poll
            agent_name: Agent name for filtering
            limit: Maximum messages to retrieve
            include_processed: Whether to include already processed messages
            
        Returns:
            List of agent messages
        """
        # Build query based on subscription type
        base_query = """
        SELECT m.* FROM agent_messages m
        WHERE m.channel = %s
        AND (m.recipient_agent IS NULL OR m.recipient_agent = %s)
        """
        
        params = [channel, agent_name]
        
        if not include_processed:
            base_query += " AND m.processed = FALSE"
        
        base_query += " ORDER BY m.priority ASC, m.created_at ASC LIMIT %s"
        params.append(limit)
        
        try:
            results = await self._execute_query(base_query, tuple(params), fetch=True)
            
            messages = []
            if results:
                for row in results:
                    message = AgentMessage(
                        id=row["id"],
                        channel=row["channel"],
                        sender_agent=row["sender_agent"],
                        recipient_agent=row["recipient_agent"],
                        message=json.loads(row["message"]) if row["message"] else {},
                        priority=row["priority"],
                        created_at=row["created_at"],
                        processed=row["processed"],
                        processed_at=row["processed_at"],
                        processed_by=row["processed_by"]
                    )
                    messages.append(message)
            
            # Log operation
            await self._log_operation(
                agent_name=agent_name,
                operation_type="receive_message",
                operation_data={
                    "channel": channel,
                    "messages_retrieved": len(messages),
                    "include_processed": include_processed
                },
                success=True
            )
            
            logger.debug(f"Polled {len(messages)} messages for {agent_name} from {channel}")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to poll messages: {e}")
            await self._log_operation(
                agent_name=agent_name,
                operation_type="receive_message",
                operation_data={
                    "channel": channel,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def mark_message_processed(
        self, 
        message_id: int, 
        processed_by: str
    ) -> None:
        """
        Mark a message as processed.
        
        Args:
            message_id: Message ID to mark as processed
            processed_by: Agent that processed the message
        """
        query = """
        UPDATE agent_messages 
        SET processed = TRUE, processed_at = NOW(), processed_by = %s
        WHERE id = %s AND processed = FALSE
        """
        
        try:
            await self._execute_query(query, (processed_by, message_id))
            logger.debug(f"Message {message_id} marked as processed by {processed_by}")
            
        except Exception as e:
            logger.error(f"Failed to mark message as processed: {e}")
            raise

    async def get_unprocessed_message_count(self, channel: str, agent_name: str) -> int:
        """
        Get count of unprocessed messages for an agent in a channel.
        
        Args:
            channel: Channel name
            agent_name: Agent name
            
        Returns:
            Number of unprocessed messages
        """
        query = """
        SELECT COUNT(*) as count FROM agent_messages
        WHERE channel = %s 
        AND (recipient_agent IS NULL OR recipient_agent = %s)
        AND processed = FALSE
        """
        
        try:
            result = await self._execute_query(query, (channel, agent_name), fetch=True, fetch_one=True)
            return result["count"] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get unprocessed message count: {e}")
            return 0

    async def _log_operation(
        self,
        agent_name: str,
        operation_type: str,
        operation_data: Dict[str, Any],
        execution_time_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log agent communication operation.
        
        Args:
            agent_name: Agent performing the operation
            operation_type: Type of operation
            operation_data: Operation details
            execution_time_ms: Execution time in milliseconds
            success: Whether operation succeeded
            error_message: Error message if failed
        """
        query = """
        INSERT INTO agent_communication_logs 
        (agent_name, operation_type, operation_data, execution_time_ms, success, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            agent_name,
            operation_type,
            json.dumps(operation_data),
            execution_time_ms,
            success,
            error_message
        )
        
        try:
            # Use a separate connection to avoid recursion in logging
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            cursor.close()
            connection.close()
            
        except Exception as e:
            # Don't raise exceptions from logging to avoid infinite loops
            logger.warning(f"Failed to log operation: {e}")

    async def close(self) -> None:
        """Close all connections and cleanup resources."""
        if self.pool:
            # Close all connections in the pool
            try:
                # Note: mysql-connector-python doesn't have a direct way to close all pool connections
                # The connections will be closed when the pool is garbage collected
                self.pool = None
                logger.info("TiDB connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the database connection.
        
        Returns:
            Health status information
        """
        try:
            start_time = datetime.now()
            result = await self._execute_query("SELECT 1 as health_check", fetch=True, fetch_one=True)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy" if result and result["health_check"] == 1 else "unhealthy",
                "response_time_ms": response_time,
                "timestamp": datetime.now().isoformat(),
                "pool_name": self.pool_name,
                "pool_size": self.pool_size
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "pool_name": self.pool_name,
                "pool_size": self.pool_size
            }
    # Cache Operations
    async def set_cache(
        self, 
        key: str, 
        result: Any, 
        ttl_seconds: int,
        agent_name: str,
        result_type: Optional[str] = None
    ) -> None:
        """
        Store result in cache with TTL.
        
        Args:
            key: Cache key
            result: Result to cache
            ttl_seconds: Time to live in seconds
            agent_name: Agent storing the cache
            result_type: Type of cached result
        """
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        query = """
        INSERT INTO agent_cache (cache_key, agent_name, result, result_type, expires_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        result = VALUES(result),
        result_type = VALUES(result_type),
        expires_at = VALUES(expires_at),
        access_count = access_count + 1,
        last_accessed = NOW()
        """
        
        params = (
            key,
            agent_name,
            json.dumps(result),
            result_type,
            expires_at
        )
        
        try:
            await self._execute_query(query, params)
            
            # Log operation
            await self._log_operation(
                agent_name=agent_name,
                operation_type="cache_set",
                operation_data={
                    "cache_key": key,
                    "result_type": result_type,
                    "ttl_seconds": ttl_seconds,
                    "expires_at": expires_at.isoformat()
                },
                success=True
            )
            
            logger.debug(f"Cache set: {key} by {agent_name} (TTL: {ttl_seconds}s)")
            
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            await self._log_operation(
                agent_name=agent_name,
                operation_type="cache_set",
                operation_data={
                    "cache_key": key,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def get_cache(self, key: str, agent_name: str) -> Optional[Any]:
        """
        Retrieve result from cache.
        
        Args:
            key: Cache key
            agent_name: Agent requesting the cache
            
        Returns:
            Cached result or None if not found/expired
        """
        query = """
        SELECT result, result_type, expires_at, access_count
        FROM agent_cache
        WHERE cache_key = %s AND expires_at > NOW()
        """
        
        try:
            result = await self._execute_query(query, (key,), fetch=True, fetch_one=True)
            
            if result:
                # Update access tracking
                update_query = """
                UPDATE agent_cache 
                SET access_count = access_count + 1, last_accessed = NOW()
                WHERE cache_key = %s
                """
                await self._execute_query(update_query, (key,))
                
                cached_data = json.loads(result["result"]) if result["result"] else None
                
                # Log operation
                await self._log_operation(
                    agent_name=agent_name,
                    operation_type="cache_get",
                    operation_data={
                        "cache_key": key,
                        "result_type": result["result_type"],
                        "access_count": result["access_count"] + 1,
                        "cache_hit": True
                    },
                    success=True
                )
                
                logger.debug(f"Cache hit: {key} for {agent_name}")
                return cached_data
            else:
                # Log cache miss
                await self._log_operation(
                    agent_name=agent_name,
                    operation_type="cache_get",
                    operation_data={
                        "cache_key": key,
                        "cache_hit": False
                    },
                    success=True
                )
                
                logger.debug(f"Cache miss: {key} for {agent_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            await self._log_operation(
                agent_name=agent_name,
                operation_type="cache_get",
                operation_data={
                    "cache_key": key,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def invalidate_cache(self, pattern: str, agent_name: str) -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Cache key pattern (supports SQL LIKE syntax)
            agent_name: Agent performing invalidation
            
        Returns:
            Number of invalidated entries
        """
        query = "DELETE FROM agent_cache WHERE cache_key LIKE %s"
        
        try:
            await self._execute_query(query, (pattern,))
            
            # Get affected row count
            count_query = "SELECT ROW_COUNT() as count"
            result = await self._execute_query(count_query, fetch=True, fetch_one=True)
            invalidated_count = result["count"] if result else 0
            
            # Log operation
            await self._log_operation(
                agent_name=agent_name,
                operation_type="cache_invalidate",
                operation_data={
                    "pattern": pattern,
                    "invalidated_count": invalidated_count
                },
                success=True
            )
            
            logger.debug(f"Cache invalidated: {pattern} by {agent_name} ({invalidated_count} entries)")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            await self._log_operation(
                agent_name=agent_name,
                operation_type="cache_invalidate",
                operation_data={
                    "pattern": pattern,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def cleanup_expired_cache(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of cleaned entries
        """
        query = "DELETE FROM agent_cache WHERE expires_at <= NOW()"
        
        try:
            await self._execute_query(query)
            
            # Get affected row count
            count_query = "SELECT ROW_COUNT() as count"
            result = await self._execute_query(count_query, fetch=True, fetch_one=True)
            cleaned_count = result["count"] if result else 0
            
            logger.debug(f"Cleaned up {cleaned_count} expired cache entries")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache: {e}")
            raise

    # Session Operations
    async def create_session(self, session_data: AgentSessionData) -> str:
        """
        Create a new agent session.
        
        Args:
            session_data: Session data
            
        Returns:
            Session ID
        """
        if not session_data.session_id:
            session_data.session_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO agent_sessions 
        (session_id, user_id, agents_involved, session_state, conversation_history, metadata, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            session_data.session_id,
            session_data.user_id,
            json.dumps(session_data.agents_involved),
            json.dumps(session_data.session_state),
            json.dumps(session_data.conversation_history),
            json.dumps(session_data.metadata),
            session_data.status
        )
        
        try:
            await self._execute_query(query, params)
            
            logger.debug(f"Session created: {session_data.session_id} for user {session_data.user_id}")
            return session_data.session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    async def update_session(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> None:
        """
        Update an existing session.
        
        Args:
            session_id: Session ID to update
            updates: Fields to update
        """
        # Build dynamic update query
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in ["agents_involved", "session_state", "conversation_history", "metadata"]:
                set_clauses.append(f"{field} = %s")
                params.append(json.dumps(value))
            elif field in ["status", "user_id"]:
                set_clauses.append(f"{field} = %s")
                params.append(value)
            elif field == "completed_at" and value is True:
                set_clauses.append("completed_at = NOW()")
        
        if not set_clauses:
            return
        
        set_clauses.append("updated_at = NOW()")
        params.append(session_id)
        
        query = f"""
        UPDATE agent_sessions 
        SET {', '.join(set_clauses)}
        WHERE session_id = %s
        """
        
        try:
            await self._execute_query(query, tuple(params))
            logger.debug(f"Session updated: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[AgentSessionData]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        query = """
        SELECT * FROM agent_sessions WHERE session_id = %s
        """
        
        try:
            result = await self._execute_query(query, (session_id,), fetch=True, fetch_one=True)
            
            if result:
                return AgentSessionData(
                    id=result["id"],
                    session_id=result["session_id"],
                    user_id=result["user_id"],
                    agents_involved=json.loads(result["agents_involved"]) if result["agents_involved"] else [],
                    session_state=json.loads(result["session_state"]) if result["session_state"] else {},
                    conversation_history=json.loads(result["conversation_history"]) if result["conversation_history"] else [],
                    metadata=json.loads(result["metadata"]) if result["metadata"] else {},
                    status=result["status"],
                    created_at=result["created_at"],
                    updated_at=result["updated_at"],
                    completed_at=result["completed_at"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            raise

    async def get_active_sessions_for_user(self, user_id: str) -> List[AgentSessionData]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active sessions
        """
        query = """
        SELECT * FROM agent_sessions 
        WHERE user_id = %s AND status = 'active'
        ORDER BY created_at DESC
        """
        
        try:
            results = await self._execute_query(query, (user_id,), fetch=True)
            
            sessions = []
            if results:
                for row in results:
                    session = AgentSessionData(
                        id=row["id"],
                        session_id=row["session_id"],
                        user_id=row["user_id"],
                        agents_involved=json.loads(row["agents_involved"]) if row["agents_involved"] else [],
                        session_state=json.loads(row["session_state"]) if row["session_state"] else {},
                        conversation_history=json.loads(row["conversation_history"]) if row["conversation_history"] else [],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                        status=row["status"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        completed_at=row["completed_at"]
                    )
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get active sessions for user: {e}")
            raise 
   # Task Queue Operations
    async def enqueue_task(
        self,
        agent_name: str,
        task_type: str,
        parameters: Dict[str, Any],
        priority: int = 5,
        max_retries: int = 3
    ) -> str:
        """
        Enqueue a task for an agent.
        
        Args:
            agent_name: Target agent name
            task_type: Type of task
            parameters: Task parameters
            priority: Task priority (1-10, lower is higher priority)
            max_retries: Maximum retry attempts
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO agent_tasks 
        (task_id, agent_name, task_type, parameters, priority, max_retries)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            task_id,
            agent_name,
            task_type,
            json.dumps(parameters),
            priority,
            max_retries
        )
        
        try:
            await self._execute_query(query, params)
            
            # Log operation
            await self._log_operation(
                agent_name="system",
                operation_type="task_enqueue",
                operation_data={
                    "task_id": task_id,
                    "agent_name": agent_name,
                    "task_type": task_type,
                    "priority": priority
                },
                success=True
            )
            
            logger.debug(f"Task enqueued: {task_id} for {agent_name} ({task_type})")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            await self._log_operation(
                agent_name="system",
                operation_type="task_enqueue",
                operation_data={
                    "agent_name": agent_name,
                    "task_type": task_type,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def dequeue_task(self, agent_name: str) -> Optional[AgentTask]:
        """
        Dequeue the next task for an agent.
        
        Args:
            agent_name: Agent name
            
        Returns:
            Next task or None if no tasks available
        """
        # Get the highest priority pending task
        query = """
        SELECT * FROM agent_tasks
        WHERE agent_name = %s AND status = 'pending'
        ORDER BY priority ASC, created_at ASC
        LIMIT 1
        FOR UPDATE
        """
        
        try:
            result = await self._execute_query(query, (agent_name,), fetch=True, fetch_one=True)
            
            if result:
                # Mark task as processing
                task_id = result["task_id"]
                update_query = """
                UPDATE agent_tasks 
                SET status = 'processing', started_at = NOW()
                WHERE task_id = %s
                """
                await self._execute_query(update_query, (task_id,))
                
                task = AgentTask(
                    id=result["id"],
                    task_id=result["task_id"],
                    agent_name=result["agent_name"],
                    task_type=result["task_type"],
                    parameters=json.loads(result["parameters"]) if result["parameters"] else {},
                    priority=result["priority"],
                    status=TaskStatus.PROCESSING,
                    result=json.loads(result["result"]) if result["result"] else None,
                    error_message=result["error_message"],
                    retry_count=result["retry_count"],
                    max_retries=result["max_retries"],
                    created_at=result["created_at"],
                    started_at=datetime.now(),
                    completed_at=result["completed_at"]
                )
                
                # Log operation
                await self._log_operation(
                    agent_name=agent_name,
                    operation_type="task_dequeue",
                    operation_data={
                        "task_id": task_id,
                        "task_type": result["task_type"],
                        "priority": result["priority"]
                    },
                    success=True
                )
                
                logger.debug(f"Task dequeued: {task_id} by {agent_name}")
                return task
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue task: {e}")
            await self._log_operation(
                agent_name=agent_name,
                operation_type="task_dequeue",
                operation_data={
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update task status and result.
        
        Args:
            task_id: Task ID
            status: New status
            result: Task result (for completed tasks)
            error_message: Error message (for failed tasks)
        """
        set_clauses = ["status = %s"]
        params = [status.value]
        
        if status == TaskStatus.COMPLETED:
            set_clauses.append("completed_at = NOW()")
            if result is not None:
                set_clauses.append("result = %s")
                params.append(json.dumps(result))
        elif status == TaskStatus.FAILED:
            set_clauses.append("completed_at = NOW()")
            if error_message:
                set_clauses.append("error_message = %s")
                params.append(error_message)
        elif status == TaskStatus.RETRYING:
            set_clauses.append("retry_count = retry_count + 1")
            set_clauses.append("started_at = NULL")
            if error_message:
                set_clauses.append("error_message = %s")
                params.append(error_message)
        
        params.append(task_id)
        
        query = f"""
        UPDATE agent_tasks 
        SET {', '.join(set_clauses)}
        WHERE task_id = %s
        """
        
        try:
            await self._execute_query(query, tuple(params))
            logger.debug(f"Task status updated: {task_id} -> {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            raise

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status and details.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """
        query = """
        SELECT task_id, agent_name, task_type, status, result, error_message,
               retry_count, max_retries, created_at, started_at, completed_at
        FROM agent_tasks
        WHERE task_id = %s
        """
        
        try:
            result = await self._execute_query(query, (task_id,), fetch=True, fetch_one=True)
            
            if result:
                return {
                    "task_id": result["task_id"],
                    "agent_name": result["agent_name"],
                    "task_type": result["task_type"],
                    "status": result["status"],
                    "result": json.loads(result["result"]) if result["result"] else None,
                    "error_message": result["error_message"],
                    "retry_count": result["retry_count"],
                    "max_retries": result["max_retries"],
                    "created_at": result["created_at"].isoformat() if result["created_at"] else None,
                    "started_at": result["started_at"].isoformat() if result["started_at"] else None,
                    "completed_at": result["completed_at"].isoformat() if result["completed_at"] else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise

    async def get_pending_task_count(self, agent_name: str) -> int:
        """
        Get count of pending tasks for an agent.
        
        Args:
            agent_name: Agent name
            
        Returns:
            Number of pending tasks
        """
        query = """
        SELECT COUNT(*) as count FROM agent_tasks
        WHERE agent_name = %s AND status = 'pending'
        """
        
        try:
            result = await self._execute_query(query, (agent_name,), fetch=True, fetch_one=True)
            return result["count"] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get pending task count: {e}")
            return 0

    async def retry_failed_task(self, task_id: str) -> bool:
        """
        Retry a failed task if retries are available.
        
        Args:
            task_id: Task ID to retry
            
        Returns:
            True if task was queued for retry, False otherwise
        """
        # Check if task can be retried
        query = """
        SELECT retry_count, max_retries, status FROM agent_tasks
        WHERE task_id = %s
        """
        
        try:
            result = await self._execute_query(query, (task_id,), fetch=True, fetch_one=True)
            
            if not result:
                return False
            
            if result["status"] != "failed":
                return False
            
            if result["retry_count"] >= result["max_retries"]:
                return False
            
            # Reset task to pending for retry
            await self.update_task_status(task_id, TaskStatus.RETRYING)
            
            # Set back to pending
            retry_query = """
            UPDATE agent_tasks 
            SET status = 'pending', error_message = NULL
            WHERE task_id = %s
            """
            await self._execute_query(retry_query, (task_id,))
            
            logger.debug(f"Task queued for retry: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry task: {e}")
            return False

    async def batch_process_tasks(self, tasks: List[AgentTask]) -> List[Dict[str, Any]]:
        """
        Process multiple tasks in a batch operation.
        
        Args:
            tasks: List of tasks to process
            
        Returns:
            List of processing results
        """
        results = []
        
        # Start transaction for batch processing
        connection = None
        cursor = None
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            connection.start_transaction()
            
            for task in tasks:
                try:
                    # Update task status to processing
                    update_query = """
                    UPDATE agent_tasks 
                    SET status = 'processing', started_at = NOW()
                    WHERE task_id = %s AND status = 'pending'
                    """
                    cursor.execute(update_query, (task.task_id,))
                    
                    if cursor.rowcount > 0:
                        results.append({
                            "task_id": task.task_id,
                            "status": "processing",
                            "success": True
                        })
                    else:
                        results.append({
                            "task_id": task.task_id,
                            "status": "failed",
                            "success": False,
                            "error": "Task not found or not in pending status"
                        })
                        
                except Exception as e:
                    results.append({
                        "task_id": task.task_id,
                        "status": "failed",
                        "success": False,
                        "error": str(e)
                    })
            
            connection.commit()
            
            # Log batch operation
            await self._log_operation(
                agent_name="system",
                operation_type="batch_process_tasks",
                operation_data={
                    "task_count": len(tasks),
                    "successful": len([r for r in results if r["success"]]),
                    "failed": len([r for r in results if not r["success"]])
                },
                success=True
            )
            
            logger.debug(f"Batch processed {len(tasks)} tasks")
            return results
            
        except Exception as e:
            if connection:
                connection.rollback()
            
            logger.error(f"Failed to batch process tasks: {e}")
            await self._log_operation(
                agent_name="system",
                operation_type="batch_process_tasks",
                operation_data={
                    "task_count": len(tasks),
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()