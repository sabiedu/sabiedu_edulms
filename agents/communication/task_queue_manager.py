"""
Task Queue Manager for Agent Communication

This module provides comprehensive task queue management for agent coordination,
including priority queuing, batch processing, retry mechanisms, and task analytics.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

from .tidb_service import TiDBCommunicationService, AgentTask, TaskStatus

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 5
    LOW = 8
    BACKGROUND = 10


@dataclass
class BatchResult:
    """Batch processing result."""
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None


@dataclass
class TaskQueueStats:
    """Task queue statistics."""
    total_tasks: int
    pending_tasks: int
    processing_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_processing_time_ms: float
    success_rate: float
    agents: Dict[str, int]
    task_types: Dict[str, int]


@dataclass
class TaskFilter:
    """Task filtering criteria."""
    agent_name: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority_min: Optional[int] = None
    priority_max: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class TaskQueueManager:
    """
    Comprehensive task queue manager for agent coordination.
    
    Provides priority queuing, batch processing, retry mechanisms,
    and comprehensive task analytics using database tables.
    """

    def __init__(self, communication_service: TiDBCommunicationService):
        """
        Initialize task queue manager.
        
        Args:
            communication_service: TiDB communication service instance
        """
        self.comm_service = communication_service
        self.task_processors: Dict[str, Callable] = {}
        self.batch_size = 100
        self.retry_delays = [1, 5, 15, 60, 300]  # Exponential backoff in seconds
        self.processing_timeout = 300  # 5 minutes default timeout

    def register_task_processor(
        self,
        task_type: str,
        processor: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """
        Register a task processor function.
        
        Args:
            task_type: Type of task to process
            processor: Async function to process the task
        """
        self.task_processors[task_type] = processor
        logger.info(f"Registered task processor for type: {task_type}")

    async def enqueue_task(
        self,
        agent_name: str,
        task_type: str,
        parameters: Dict[str, Any],
        priority: Union[TaskPriority, int] = TaskPriority.NORMAL,
        max_retries: int = 3,
        delay_seconds: int = 0,
        depends_on: Optional[List[str]] = None
    ) -> str:
        """
        Enqueue a task for processing.
        
        Args:
            agent_name: Target agent name
            task_type: Type of task
            parameters: Task parameters
            priority: Task priority
            max_retries: Maximum retry attempts
            delay_seconds: Delay before task becomes available
            depends_on: List of task IDs this task depends on
            
        Returns:
            Task ID
        """
        priority_value = priority.value if isinstance(priority, TaskPriority) else priority
        
        # Add dependency information to parameters
        if depends_on:
            parameters["_dependencies"] = depends_on
        
        # Add delay information
        if delay_seconds > 0:
            parameters["_delay_until"] = (datetime.now() + timedelta(seconds=delay_seconds)).isoformat()
        
        task_id = await self.comm_service.enqueue_task(
            agent_name=agent_name,
            task_type=task_type,
            parameters=parameters,
            priority=priority_value,
            max_retries=max_retries
        )
        
        logger.debug(f"Task enqueued: {task_id} for {agent_name} ({task_type}, priority: {priority_value})")
        return task_id

    async def enqueue_batch_tasks(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Enqueue multiple tasks in a batch operation.
        
        Args:
            tasks: List of task definitions
                  Each task should have: agent_name, task_type, parameters
                  Optional: priority, max_retries, delay_seconds, depends_on
                  
        Returns:
            List of task IDs
        """
        task_ids = []
        
        # Use transaction for batch insert
        connection = None
        cursor = None
        
        try:
            connection = self.comm_service._get_connection()
            cursor = connection.cursor()
            connection.start_transaction()
            
            for task_def in tasks:
                task_id = str(uuid.uuid4())
                priority = task_def.get("priority", TaskPriority.NORMAL.value)
                if isinstance(priority, TaskPriority):
                    priority = priority.value
                
                parameters = task_def["parameters"].copy()
                
                # Handle dependencies
                if task_def.get("depends_on"):
                    parameters["_dependencies"] = task_def["depends_on"]
                
                # Handle delay
                if task_def.get("delay_seconds", 0) > 0:
                    delay_until = datetime.now() + timedelta(seconds=task_def["delay_seconds"])
                    parameters["_delay_until"] = delay_until.isoformat()
                
                insert_query = """
                INSERT INTO agent_tasks 
                (task_id, agent_name, task_type, parameters, priority, max_retries)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    task_id,
                    task_def["agent_name"],
                    task_def["task_type"],
                    json.dumps(parameters),
                    priority,
                    task_def.get("max_retries", 3)
                ))
                
                task_ids.append(task_id)
            
            connection.commit()
            
            # Log batch operation
            await self.comm_service._log_operation(
                agent_name="system",
                operation_type="batch_enqueue_tasks",
                operation_data={
                    "task_count": len(tasks),
                    "task_ids": task_ids[:10]  # Log first 10 IDs
                },
                success=True
            )
            
            logger.info(f"Batch enqueued {len(tasks)} tasks")
            return task_ids
            
        except Exception as e:
            if connection:
                connection.rollback()
            
            logger.error(f"Failed to batch enqueue tasks: {e}")
            await self.comm_service._log_operation(
                agent_name="system",
                operation_type="batch_enqueue_tasks",
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

    async def dequeue_task(
        self,
        agent_name: str,
        task_types: Optional[List[str]] = None
    ) -> Optional[AgentTask]:
        """
        Dequeue the next available task for an agent.
        
        Args:
            agent_name: Agent name
            task_types: Optional list of task types to filter by
            
        Returns:
            Next available task or None
        """
        # Build query with optional task type filtering
        where_clauses = ["agent_name = %s", "status = 'pending'"]
        params = [agent_name]
        
        if task_types:
            placeholders = ",".join(["%s"] * len(task_types))
            where_clauses.append(f"task_type IN ({placeholders})")
            params.extend(task_types)
        
        # Check for delay and dependencies
        where_clauses.append("""
            (JSON_EXTRACT(parameters, '$._delay_until') IS NULL 
             OR STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(parameters, '$._delay_until')), '%Y-%m-%dT%H:%i:%s') <= NOW())
        """)
        
        query = f"""
        SELECT * FROM agent_tasks
        WHERE {' AND '.join(where_clauses)}
        ORDER BY priority ASC, created_at ASC
        LIMIT 1
        FOR UPDATE
        """
        
        try:
            result = await self.comm_service._execute_query(query, tuple(params), fetch=True, fetch_one=True)
            
            if result:
                # Check dependencies if any
                parameters = json.loads(result["parameters"]) if result["parameters"] else {}
                dependencies = parameters.get("_dependencies", [])
                
                if dependencies:
                    # Check if all dependencies are completed
                    dep_check_query = """
                    SELECT COUNT(*) as incomplete_count FROM agent_tasks
                    WHERE task_id IN ({}) AND status != 'completed'
                    """.format(",".join(["%s"] * len(dependencies)))
                    
                    dep_result = await self.comm_service._execute_query(
                        dep_check_query, tuple(dependencies), fetch=True, fetch_one=True
                    )
                    
                    if dep_result and dep_result["incomplete_count"] > 0:
                        # Dependencies not met, skip this task
                        return None
                
                # Mark task as processing
                task_id = result["task_id"]
                update_query = """
                UPDATE agent_tasks 
                SET status = 'processing', started_at = NOW()
                WHERE task_id = %s
                """
                await self.comm_service._execute_query(update_query, (task_id,))
                
                task = AgentTask(
                    id=result["id"],
                    task_id=result["task_id"],
                    agent_name=result["agent_name"],
                    task_type=result["task_type"],
                    parameters=parameters,
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
                
                logger.debug(f"Task dequeued: {task_id} by {agent_name}")
                return task
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue task: {e}")
            raise

    async def complete_task(
        self,
        task_id: str,
        result: Any,
        processing_time_ms: Optional[int] = None
    ) -> None:
        """
        Mark a task as completed with result.
        
        Args:
            task_id: Task ID
            result: Task result
            processing_time_ms: Processing time in milliseconds
        """
        await self.comm_service.update_task_status(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            result=result
        )
        
        # Log processing time if provided
        if processing_time_ms is not None:
            await self.comm_service._log_operation(
                agent_name="system",
                operation_type="task_completed",
                operation_data={
                    "task_id": task_id,
                    "processing_time_ms": processing_time_ms
                },
                execution_time_ms=processing_time_ms,
                success=True
            )
        
        logger.debug(f"Task completed: {task_id}")

    async def fail_task(
        self,
        task_id: str,
        error_message: str,
        retry: bool = True
    ) -> bool:
        """
        Mark a task as failed and optionally retry.
        
        Args:
            task_id: Task ID
            error_message: Error description
            retry: Whether to attempt retry if retries available
            
        Returns:
            True if task will be retried, False if permanently failed
        """
        if retry:
            # Check if retries are available
            task_status = await self.comm_service.get_task_status(task_id)
            if task_status and task_status["retry_count"] < task_status["max_retries"]:
                # Calculate retry delay
                retry_count = task_status["retry_count"]
                delay_seconds = self.retry_delays[min(retry_count, len(self.retry_delays) - 1)]
                
                # Update task for retry with delay
                await self.comm_service.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.RETRYING,
                    error_message=error_message
                )
                
                # Schedule retry by updating parameters with delay
                retry_query = """
                UPDATE agent_tasks 
                SET status = 'pending', 
                    parameters = JSON_SET(parameters, '$._delay_until', %s)
                WHERE task_id = %s
                """
                
                delay_until = (datetime.now() + timedelta(seconds=delay_seconds)).isoformat()
                await self.comm_service._execute_query(retry_query, (delay_until, task_id))
                
                logger.info(f"Task scheduled for retry: {task_id} (attempt {retry_count + 1}, delay: {delay_seconds}s)")
                return True
        
        # Permanently fail the task
        await self.comm_service.update_task_status(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error_message=error_message
        )
        
        logger.warning(f"Task permanently failed: {task_id} - {error_message}")
        return False

    async def cancel_task(self, task_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel a pending task.
        
        Args:
            task_id: Task ID to cancel
            reason: Optional cancellation reason
            
        Returns:
            True if task was cancelled, False if not found or already processing
        """
        cancel_query = """
        UPDATE agent_tasks 
        SET status = 'failed', 
            error_message = %s,
            completed_at = NOW()
        WHERE task_id = %s AND status = 'pending'
        """
        
        error_message = f"Cancelled: {reason}" if reason else "Cancelled"
        
        try:
            await self.comm_service._execute_query(cancel_query, (error_message, task_id))
            
            # Check if any rows were affected
            count_query = "SELECT ROW_COUNT() as count"
            result = await self.comm_service._execute_query(count_query, fetch=True, fetch_one=True)
            cancelled = (result["count"] if result else 0) > 0
            
            if cancelled:
                logger.info(f"Task cancelled: {task_id} - {reason}")
            
            return cancelled
            
        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            return False

    async def process_batch_tasks(
        self,
        agent_name: str,
        batch_size: Optional[int] = None,
        task_types: Optional[List[str]] = None,
        timeout_seconds: int = 300
    ) -> List[BatchResult]:
        """
        Process multiple tasks in batch for an agent.
        
        Args:
            agent_name: Agent name
            batch_size: Number of tasks to process (default: self.batch_size)
            task_types: Optional task type filter
            timeout_seconds: Timeout for batch processing
            
        Returns:
            List of batch processing results
        """
        if batch_size is None:
            batch_size = self.batch_size
        
        results = []
        processed_count = 0
        start_time = datetime.now()
        
        try:
            while processed_count < batch_size:
                # Check timeout
                if (datetime.now() - start_time).total_seconds() > timeout_seconds:
                    logger.warning(f"Batch processing timeout reached for {agent_name}")
                    break
                
                # Dequeue next task
                task = await self.dequeue_task(agent_name, task_types)
                if not task:
                    break  # No more tasks available
                
                # Process task
                task_start_time = datetime.now()
                try:
                    # Check if we have a registered processor
                    if task.task_type in self.task_processors:
                        processor = self.task_processors[task.task_type]
                        result = await processor(task.parameters)
                        
                        processing_time = int((datetime.now() - task_start_time).total_seconds() * 1000)
                        
                        await self.complete_task(task.task_id, result, processing_time)
                        
                        results.append(BatchResult(
                            task_id=task.task_id,
                            success=True,
                            result=result,
                            processing_time_ms=processing_time
                        ))
                        
                    else:
                        # No processor registered, fail the task
                        error_msg = f"No processor registered for task type: {task.task_type}"
                        await self.fail_task(task.task_id, error_msg, retry=False)
                        
                        results.append(BatchResult(
                            task_id=task.task_id,
                            success=False,
                            error=error_msg
                        ))
                
                except Exception as e:
                    processing_time = int((datetime.now() - task_start_time).total_seconds() * 1000)
                    error_msg = f"Task processing error: {str(e)}"
                    
                    await self.fail_task(task.task_id, error_msg)
                    
                    results.append(BatchResult(
                        task_id=task.task_id,
                        success=False,
                        error=error_msg,
                        processing_time_ms=processing_time
                    ))
                
                processed_count += 1
            
            # Log batch processing results
            successful = len([r for r in results if r.success])
            failed = len(results) - successful
            
            await self.comm_service._log_operation(
                agent_name=agent_name,
                operation_type="batch_process_tasks",
                operation_data={
                    "processed_count": processed_count,
                    "successful": successful,
                    "failed": failed,
                    "batch_size": batch_size
                },
                success=True
            )
            
            logger.info(f"Batch processed {processed_count} tasks for {agent_name} ({successful} successful, {failed} failed)")
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed for {agent_name}: {e}")
            await self.comm_service._log_operation(
                agent_name=agent_name,
                operation_type="batch_process_tasks",
                operation_data={
                    "error": str(e),
                    "processed_count": processed_count
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def get_queue_stats(
        self,
        agent_name: Optional[str] = None,
        task_filter: Optional[TaskFilter] = None
    ) -> TaskQueueStats:
        """
        Get comprehensive queue statistics.
        
        Args:
            agent_name: Optional agent filter
            task_filter: Optional task filtering criteria
            
        Returns:
            Queue statistics
        """
        where_clauses = []
        params = []
        
        if agent_name:
            where_clauses.append("agent_name = %s")
            params.append(agent_name)
        
        if task_filter:
            if task_filter.agent_name:
                where_clauses.append("agent_name = %s")
                params.append(task_filter.agent_name)
            
            if task_filter.task_type:
                where_clauses.append("task_type = %s")
                params.append(task_filter.task_type)
            
            if task_filter.status:
                where_clauses.append("status = %s")
                params.append(task_filter.status.value)
            
            if task_filter.priority_min is not None:
                where_clauses.append("priority >= %s")
                params.append(task_filter.priority_min)
            
            if task_filter.priority_max is not None:
                where_clauses.append("priority <= %s")
                params.append(task_filter.priority_max)
            
            if task_filter.created_after:
                where_clauses.append("created_at >= %s")
                params.append(task_filter.created_after)
            
            if task_filter.created_before:
                where_clauses.append("created_at <= %s")
                params.append(task_filter.created_before)
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        stats_query = f"""
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
            COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_tasks,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks,
            AVG(CASE WHEN completed_at IS NOT NULL AND started_at IS NOT NULL 
                THEN TIMESTAMPDIFF(MICROSECOND, started_at, completed_at) / 1000 
                END) as avg_processing_time_ms,
            agent_name,
            task_type
        FROM agent_tasks
        {where_clause}
        GROUP BY agent_name, task_type
        """
        
        try:
            results = await self.comm_service._execute_query(stats_query, tuple(params), fetch=True)
            
            total_tasks = 0
            pending_tasks = 0
            processing_tasks = 0
            completed_tasks = 0
            failed_tasks = 0
            total_processing_time = 0
            processing_count = 0
            agents = {}
            task_types = {}
            
            if results:
                for row in results:
                    total_tasks += row["total_tasks"]
                    pending_tasks += row["pending_tasks"] or 0
                    processing_tasks += row["processing_tasks"] or 0
                    completed_tasks += row["completed_tasks"] or 0
                    failed_tasks += row["failed_tasks"] or 0
                    
                    if row["avg_processing_time_ms"]:
                        total_processing_time += row["avg_processing_time_ms"] * (row["completed_tasks"] or 0)
                        processing_count += row["completed_tasks"] or 0
                    
                    agent = row["agent_name"]
                    task_type = row["task_type"]
                    
                    agents[agent] = agents.get(agent, 0) + row["total_tasks"]
                    task_types[task_type] = task_types.get(task_type, 0) + row["total_tasks"]
            
            avg_processing_time = total_processing_time / processing_count if processing_count > 0 else 0.0
            success_rate = completed_tasks / (completed_tasks + failed_tasks) if (completed_tasks + failed_tasks) > 0 else 1.0
            
            return TaskQueueStats(
                total_tasks=total_tasks,
                pending_tasks=pending_tasks,
                processing_tasks=processing_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                avg_processing_time_ms=avg_processing_time,
                success_rate=success_rate,
                agents=agents,
                task_types=task_types
            )
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            raise

    async def cleanup_completed_tasks(self, retention_days: int = 7) -> int:
        """
        Clean up old completed and failed tasks.
        
        Args:
            retention_days: Number of days to retain completed tasks
            
        Returns:
            Number of cleaned tasks
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleanup_query = """
        DELETE FROM agent_tasks 
        WHERE status IN ('completed', 'failed') 
        AND completed_at < %s
        """
        
        try:
            await self.comm_service._execute_query(cleanup_query, (cutoff_date,))
            
            # Get affected row count
            count_query = "SELECT ROW_COUNT() as count"
            result = await self.comm_service._execute_query(count_query, fetch=True, fetch_one=True)
            cleaned_count = result["count"] if result else 0
            
            logger.info(f"Cleaned up {cleaned_count} old tasks (older than {retention_days} days)")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup completed tasks: {e}")
            raise

    async def get_task_dependencies(self, task_id: str) -> List[str]:
        """
        Get task dependencies.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of dependency task IDs
        """
        query = """
        SELECT parameters FROM agent_tasks WHERE task_id = %s
        """
        
        try:
            result = await self.comm_service._execute_query(query, (task_id,), fetch=True, fetch_one=True)
            
            if result and result["parameters"]:
                parameters = json.loads(result["parameters"])
                return parameters.get("_dependencies", [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get task dependencies: {e}")
            return []

    async def get_dependent_tasks(self, task_id: str) -> List[str]:
        """
        Get tasks that depend on the given task.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of dependent task IDs
        """
        query = """
        SELECT task_id FROM agent_tasks 
        WHERE JSON_SEARCH(parameters, 'one', %s, NULL, '$._dependencies[*]') IS NOT NULL
        """
        
        try:
            results = await self.comm_service._execute_query(query, (task_id,), fetch=True)
            
            return [row["task_id"] for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Failed to get dependent tasks: {e}")
            return []