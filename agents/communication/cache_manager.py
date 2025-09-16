"""
Cache Manager for Agent Communication

This module provides advanced caching capabilities with TTL enforcement,
pattern matching, and automatic cleanup for the multi-agent system.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Pattern
from dataclasses import dataclass

from .tidb_service import TiDBCommunicationService

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry data structure."""
    key: str
    agent_name: str
    result: Any
    result_type: Optional[str]
    expires_at: datetime
    created_at: datetime
    access_count: int
    last_accessed: datetime


@dataclass
class CacheStats:
    """Cache statistics data structure."""
    total_entries: int
    expired_entries: int
    hit_rate: float
    miss_rate: float
    total_size_mb: float
    agents: Dict[str, int]
    result_types: Dict[str, int]


class CacheManager:
    """
    Advanced cache manager with TTL enforcement and pattern matching.
    
    Provides high-level caching operations with automatic cleanup,
    pattern-based invalidation, and comprehensive statistics.
    """

    def __init__(self, communication_service: TiDBCommunicationService):
        """
        Initialize cache manager.
        
        Args:
            communication_service: TiDB communication service instance
        """
        self.comm_service = communication_service
        self.cleanup_interval = 3600  # 1 hour default
        self.cleanup_task: Optional[asyncio.Task] = None
        self.running = False

    async def start_cleanup_scheduler(self, interval_seconds: int = 3600) -> None:
        """
        Start automatic cleanup scheduler.
        
        Args:
            interval_seconds: Cleanup interval in seconds
        """
        self.cleanup_interval = interval_seconds
        self.running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_scheduler())
        logger.info(f"Cache cleanup scheduler started (interval: {interval_seconds}s)")

    async def stop_cleanup_scheduler(self) -> None:
        """Stop automatic cleanup scheduler."""
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Cache cleanup scheduler stopped")

    async def _cleanup_scheduler(self) -> None:
        """Background cleanup scheduler task."""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                if self.running:
                    cleaned_count = await self.cleanup_expired()
                    if cleaned_count > 0:
                        logger.info(f"Automatic cleanup removed {cleaned_count} expired cache entries")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup scheduler: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int,
        agent_name: str,
        result_type: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> None:
        """
        Store value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            agent_name: Agent storing the value
            result_type: Type of cached result
            namespace: Optional namespace for key organization
        """
        cache_key = self._build_key(key, namespace)
        await self.comm_service.set_cache(
            key=cache_key,
            result=value,
            ttl_seconds=ttl_seconds,
            agent_name=agent_name,
            result_type=result_type
        )

    async def get(
        self,
        key: str,
        agent_name: str,
        namespace: Optional[str] = None
    ) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            agent_name: Agent requesting the value
            namespace: Optional namespace for key organization
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._build_key(key, namespace)
        return await self.comm_service.get_cache(cache_key, agent_name)

    async def delete(
        self,
        key: str,
        agent_name: str,
        namespace: Optional[str] = None
    ) -> bool:
        """
        Delete a specific cache entry.
        
        Args:
            key: Cache key to delete
            agent_name: Agent performing deletion
            namespace: Optional namespace
            
        Returns:
            True if entry was deleted, False if not found
        """
        cache_key = self._build_key(key, namespace)
        count = await self.comm_service.invalidate_cache(cache_key, agent_name)
        return count > 0

    async def invalidate_pattern(
        self,
        pattern: str,
        agent_name: str,
        namespace: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (SQL LIKE syntax)
            agent_name: Agent performing invalidation
            namespace: Optional namespace
            
        Returns:
            Number of invalidated entries
        """
        cache_pattern = self._build_key(pattern, namespace)
        return await self.comm_service.invalidate_cache(cache_pattern, agent_name)

    async def invalidate_by_agent(self, agent_name: str) -> int:
        """
        Invalidate all cache entries for a specific agent.
        
        Args:
            agent_name: Agent name
            
        Returns:
            Number of invalidated entries
        """
        query = "DELETE FROM agent_cache WHERE agent_name = %s"
        
        try:
            await self.comm_service._execute_query(query, (agent_name,))
            
            # Get affected row count
            count_query = "SELECT ROW_COUNT() as count"
            result = await self.comm_service._execute_query(count_query, fetch=True, fetch_one=True)
            invalidated_count = result["count"] if result else 0
            
            logger.debug(f"Invalidated {invalidated_count} cache entries for agent {agent_name}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache by agent: {e}")
            raise

    async def invalidate_by_type(self, result_type: str, agent_name: str) -> int:
        """
        Invalidate all cache entries of a specific type.
        
        Args:
            result_type: Result type to invalidate
            agent_name: Agent performing invalidation
            
        Returns:
            Number of invalidated entries
        """
        query = "DELETE FROM agent_cache WHERE result_type = %s"
        
        try:
            await self.comm_service._execute_query(query, (result_type,))
            
            # Get affected row count
            count_query = "SELECT ROW_COUNT() as count"
            result = await self.comm_service._execute_query(count_query, fetch=True, fetch_one=True)
            invalidated_count = result["count"] if result else 0
            
            # Log operation
            await self.comm_service._log_operation(
                agent_name=agent_name,
                operation_type="cache_invalidate_by_type",
                operation_data={
                    "result_type": result_type,
                    "invalidated_count": invalidated_count
                },
                success=True
            )
            
            logger.debug(f"Invalidated {invalidated_count} cache entries of type {result_type}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache by type: {e}")
            await self.comm_service._log_operation(
                agent_name=agent_name,
                operation_type="cache_invalidate_by_type",
                operation_data={
                    "result_type": result_type,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    async def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of cleaned entries
        """
        return await self.comm_service.cleanup_expired_cache()

    async def get_cache_stats(self) -> CacheStats:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Cache statistics
        """
        stats_query = """
        SELECT 
            COUNT(*) as total_entries,
            COUNT(CASE WHEN expires_at <= NOW() THEN 1 END) as expired_entries,
            AVG(access_count) as avg_access_count,
            SUM(CHAR_LENGTH(result)) as total_size_bytes,
            agent_name,
            result_type
        FROM agent_cache
        GROUP BY agent_name, result_type
        """
        
        try:
            results = await self.comm_service._execute_query(stats_query, fetch=True)
            
            total_entries = 0
            expired_entries = 0
            total_size_bytes = 0
            agents = {}
            result_types = {}
            
            if results:
                for row in results:
                    total_entries += row["total_entries"]
                    expired_entries += row["expired_entries"] or 0
                    total_size_bytes += row["total_size_bytes"] or 0
                    
                    agent_name = row["agent_name"]
                    result_type = row["result_type"] or "unknown"
                    
                    agents[agent_name] = agents.get(agent_name, 0) + row["total_entries"]
                    result_types[result_type] = result_types.get(result_type, 0) + row["total_entries"]
            
            # Calculate hit/miss rates (simplified - would need more detailed tracking)
            hit_rate = 0.8  # Placeholder - would need actual hit/miss tracking
            miss_rate = 1.0 - hit_rate
            
            return CacheStats(
                total_entries=total_entries,
                expired_entries=expired_entries,
                hit_rate=hit_rate,
                miss_rate=miss_rate,
                total_size_mb=total_size_bytes / (1024 * 1024),
                agents=agents,
                result_types=result_types
            )
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            raise

    async def get_entries_by_pattern(
        self,
        pattern: str,
        limit: int = 100,
        namespace: Optional[str] = None
    ) -> List[CacheEntry]:
        """
        Get cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (SQL LIKE syntax)
            limit: Maximum entries to return
            namespace: Optional namespace
            
        Returns:
            List of matching cache entries
        """
        cache_pattern = self._build_key(pattern, namespace)
        
        query = """
        SELECT cache_key, agent_name, result, result_type, expires_at, 
               created_at, access_count, last_accessed
        FROM agent_cache
        WHERE cache_key LIKE %s
        ORDER BY last_accessed DESC
        LIMIT %s
        """
        
        try:
            results = await self.comm_service._execute_query(
                query, (cache_pattern, limit), fetch=True
            )
            
            entries = []
            if results:
                for row in results:
                    entry = CacheEntry(
                        key=row["cache_key"],
                        agent_name=row["agent_name"],
                        result=row["result"],  # Keep as JSON string for inspection
                        result_type=row["result_type"],
                        expires_at=row["expires_at"],
                        created_at=row["created_at"],
                        access_count=row["access_count"],
                        last_accessed=row["last_accessed"]
                    )
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get entries by pattern: {e}")
            raise

    async def extend_ttl(
        self,
        key: str,
        additional_seconds: int,
        agent_name: str,
        namespace: Optional[str] = None
    ) -> bool:
        """
        Extend TTL for a cache entry.
        
        Args:
            key: Cache key
            additional_seconds: Additional seconds to add to TTL
            agent_name: Agent performing the operation
            namespace: Optional namespace
            
        Returns:
            True if TTL was extended, False if entry not found
        """
        cache_key = self._build_key(key, namespace)
        
        query = """
        UPDATE agent_cache 
        SET expires_at = DATE_ADD(expires_at, INTERVAL %s SECOND)
        WHERE cache_key = %s AND expires_at > NOW()
        """
        
        try:
            await self.comm_service._execute_query(query, (additional_seconds, cache_key))
            
            # Check if any rows were affected
            count_query = "SELECT ROW_COUNT() as count"
            result = await self.comm_service._execute_query(count_query, fetch=True, fetch_one=True)
            updated = (result["count"] if result else 0) > 0
            
            # Log operation
            await self.comm_service._log_operation(
                agent_name=agent_name,
                operation_type="cache_extend_ttl",
                operation_data={
                    "cache_key": cache_key,
                    "additional_seconds": additional_seconds,
                    "success": updated
                },
                success=True
            )
            
            if updated:
                logger.debug(f"Extended TTL for cache key {cache_key} by {additional_seconds}s")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to extend TTL: {e}")
            await self.comm_service._log_operation(
                agent_name=agent_name,
                operation_type="cache_extend_ttl",
                operation_data={
                    "cache_key": cache_key,
                    "error": str(e)
                },
                success=False,
                error_message=str(e)
            )
            raise

    def _build_key(self, key: str, namespace: Optional[str] = None) -> str:
        """
        Build cache key with optional namespace.
        
        Args:
            key: Base key
            namespace: Optional namespace
            
        Returns:
            Formatted cache key
        """
        if namespace:
            return f"{namespace}:{key}"
        return key

    async def warm_cache(
        self,
        entries: List[Dict[str, Any]],
        agent_name: str
    ) -> int:
        """
        Warm cache with multiple entries.
        
        Args:
            entries: List of cache entries to warm
                    Each entry should have: key, value, ttl_seconds, result_type (optional)
            agent_name: Agent performing the warming
            
        Returns:
            Number of entries successfully cached
        """
        successful = 0
        
        for entry in entries:
            try:
                await self.set(
                    key=entry["key"],
                    value=entry["value"],
                    ttl_seconds=entry["ttl_seconds"],
                    agent_name=agent_name,
                    result_type=entry.get("result_type"),
                    namespace=entry.get("namespace")
                )
                successful += 1
                
            except Exception as e:
                logger.error(f"Failed to warm cache entry {entry.get('key', 'unknown')}: {e}")
        
        logger.info(f"Cache warmed: {successful}/{len(entries)} entries by {agent_name}")
        return successful