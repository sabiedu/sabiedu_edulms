"""
Session Manager for Agent Communication

This module provides comprehensive session management for multi-agent interactions,
including conversation history, state management, and session analytics.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

from .tidb_service import TiDBCommunicationService, AgentSessionData

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConversationTurn:
    """Individual conversation turn data structure."""
    agent_name: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    processing_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SessionMetrics:
    """Session performance metrics."""
    total_turns: int
    agents_involved: List[str]
    avg_response_time_ms: float
    total_duration_seconds: float
    message_types: Dict[str, int]
    error_count: int
    success_rate: float


@dataclass
class SessionSummary:
    """Session summary for analytics."""
    session_id: str
    user_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    agents_involved: List[str]
    total_messages: int
    outcome: Optional[str]


class SessionManager:
    """
    Comprehensive session manager for multi-agent interactions.
    
    Provides session lifecycle management, conversation tracking,
    state persistence, and session analytics with full SQL query capabilities.
    """

    def __init__(self, communication_service: TiDBCommunicationService):
        """
        Initialize session manager.
        
        Args:
            communication_service: TiDB communication service instance
        """
        self.comm_service = communication_service
        self.active_sessions: Dict[str, AgentSessionData] = {}
        self.session_timeout = 3600  # 1 hour default timeout

    async def create_session(
        self,
        user_id: str,
        agents_involved: List[str],
        initial_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create a new agent session.
        
        Args:
            user_id: User ID for the session
            agents_involved: List of agents that will participate
            initial_state: Initial session state
            metadata: Additional session metadata
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session_data = AgentSessionData(
            session_id=session_id,
            user_id=user_id,
            agents_involved=agents_involved,
            session_state=initial_state or {},
            conversation_history=[],
            metadata=metadata or {},
            status=SessionStatus.ACTIVE.value
        )
        
        # Store in database
        created_session_id = await self.comm_service.create_session(session_data)
        
        # Cache in memory for quick access
        self.active_sessions[created_session_id] = session_data
        
        logger.info(f"Session created: {created_session_id} for user {user_id} with agents {agents_involved}")
        return created_session_id

    async def get_session(self, session_id: str) -> Optional[AgentSessionData]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        # Check memory cache first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Fetch from database
        session_data = await self.comm_service.get_session(session_id)
        
        # Cache if active
        if session_data and session_data.status == SessionStatus.ACTIVE.value:
            self.active_sessions[session_id] = session_data
        
        return session_data

    async def update_session_state(
        self,
        session_id: str,
        state_updates: Dict[str, Any],
        merge: bool = True
    ) -> None:
        """
        Update session state.
        
        Args:
            session_id: Session ID
            state_updates: State updates to apply
            merge: Whether to merge with existing state or replace
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if merge:
            session.session_state.update(state_updates)
        else:
            session.session_state = state_updates
        
        # Update in database
        await self.comm_service.update_session(session_id, {
            "session_state": session.session_state
        })
        
        # Update memory cache
        if session_id in self.active_sessions:
            self.active_sessions[session_id].session_state = session.session_state
        
        logger.debug(f"Session state updated: {session_id}")

    async def add_conversation_turn(
        self,
        session_id: str,
        agent_name: str,
        message_type: str,
        content: Dict[str, Any],
        processing_time_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a conversation turn to the session.
        
        Args:
            session_id: Session ID
            agent_name: Agent that generated the turn
            message_type: Type of message
            content: Message content
            processing_time_ms: Processing time in milliseconds
            metadata: Additional turn metadata
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        turn = ConversationTurn(
            agent_name=agent_name,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            processing_time_ms=processing_time_ms,
            metadata=metadata or {}
        )
        
        # Add to conversation history
        session.conversation_history.append(asdict(turn))
        
        # Update in database
        await self.comm_service.update_session(session_id, {
            "conversation_history": session.conversation_history
        })
        
        # Update memory cache
        if session_id in self.active_sessions:
            self.active_sessions[session_id].conversation_history = session.conversation_history
        
        logger.debug(f"Conversation turn added to session {session_id} by {agent_name}")

    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
        agent_filter: Optional[str] = None,
        message_type_filter: Optional[str] = None
    ) -> List[ConversationTurn]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of turns to return
            agent_filter: Filter by specific agent
            message_type_filter: Filter by message type
            
        Returns:
            List of conversation turns
        """
        session = await self.get_session(session_id)
        if not session:
            return []
        
        turns = []
        for turn_data in session.conversation_history:
            # Apply filters
            if agent_filter and turn_data.get("agent_name") != agent_filter:
                continue
            if message_type_filter and turn_data.get("message_type") != message_type_filter:
                continue
            
            turn = ConversationTurn(
                agent_name=turn_data["agent_name"],
                message_type=turn_data["message_type"],
                content=turn_data["content"],
                timestamp=datetime.fromisoformat(turn_data["timestamp"]) if isinstance(turn_data["timestamp"], str) else turn_data["timestamp"],
                processing_time_ms=turn_data.get("processing_time_ms"),
                metadata=turn_data.get("metadata", {})
            )
            turns.append(turn)
        
        # Apply limit
        if limit:
            turns = turns[-limit:]
        
        return turns

    async def pause_session(self, session_id: str, reason: Optional[str] = None) -> None:
        """
        Pause an active session.
        
        Args:
            session_id: Session ID
            reason: Optional reason for pausing
        """
        await self._update_session_status(
            session_id, 
            SessionStatus.PAUSED, 
            {"pause_reason": reason} if reason else None
        )

    async def resume_session(self, session_id: str) -> None:
        """
        Resume a paused session.
        
        Args:
            session_id: Session ID
        """
        await self._update_session_status(session_id, SessionStatus.ACTIVE)

    async def complete_session(
        self,
        session_id: str,
        outcome: Optional[str] = None,
        final_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Complete a session.
        
        Args:
            session_id: Session ID
            outcome: Session outcome description
            final_state: Final session state
        """
        updates = {"completed_at": True}
        
        if outcome:
            session = await self.get_session(session_id)
            if session:
                session.metadata["outcome"] = outcome
                updates["metadata"] = session.metadata
        
        if final_state:
            updates["session_state"] = final_state
        
        await self._update_session_status(session_id, SessionStatus.COMPLETED, updates)
        
        # Remove from active sessions cache
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    async def fail_session(
        self,
        session_id: str,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Mark a session as failed.
        
        Args:
            session_id: Session ID
            error_message: Error description
            error_details: Additional error details
        """
        session = await self.get_session(session_id)
        if session:
            session.metadata.update({
                "error_message": error_message,
                "error_details": error_details or {},
                "failed_at": datetime.now().isoformat()
            })
            
            await self._update_session_status(
                session_id, 
                SessionStatus.FAILED, 
                {"metadata": session.metadata, "completed_at": True}
            )
        
        # Remove from active sessions cache
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    async def _update_session_status(
        self,
        session_id: str,
        status: SessionStatus,
        additional_updates: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update session status and additional fields.
        
        Args:
            session_id: Session ID
            status: New status
            additional_updates: Additional fields to update
        """
        updates = {"status": status.value}
        if additional_updates:
            updates.update(additional_updates)
        
        await self.comm_service.update_session(session_id, updates)
        
        # Update memory cache
        if session_id in self.active_sessions:
            self.active_sessions[session_id].status = status.value

    async def get_active_sessions_for_user(self, user_id: str) -> List[AgentSessionData]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active sessions
        """
        return await self.comm_service.get_active_sessions_for_user(user_id)

    async def get_session_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        """
        Calculate session performance metrics.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session metrics or None if session not found
        """
        session = await self.get_session(session_id)
        if not session:
            return None
        
        conversation_history = session.conversation_history
        if not conversation_history:
            return SessionMetrics(
                total_turns=0,
                agents_involved=session.agents_involved,
                avg_response_time_ms=0.0,
                total_duration_seconds=0.0,
                message_types={},
                error_count=0,
                success_rate=1.0
            )
        
        # Calculate metrics
        total_turns = len(conversation_history)
        agents_involved = list(set(turn.get("agent_name", "") for turn in conversation_history))
        
        # Response times
        response_times = [
            turn.get("processing_time_ms", 0) 
            for turn in conversation_history 
            if turn.get("processing_time_ms") is not None
        ]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Duration
        start_time = datetime.fromisoformat(conversation_history[0]["timestamp"]) if isinstance(conversation_history[0]["timestamp"], str) else conversation_history[0]["timestamp"]
        end_time = datetime.fromisoformat(conversation_history[-1]["timestamp"]) if isinstance(conversation_history[-1]["timestamp"], str) else conversation_history[-1]["timestamp"]
        total_duration = (end_time - start_time).total_seconds()
        
        # Message types
        message_types = {}
        error_count = 0
        for turn in conversation_history:
            msg_type = turn.get("message_type", "unknown")
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
            
            if "error" in msg_type.lower() or turn.get("content", {}).get("error"):
                error_count += 1
        
        success_rate = (total_turns - error_count) / total_turns if total_turns > 0 else 1.0
        
        return SessionMetrics(
            total_turns=total_turns,
            agents_involved=agents_involved,
            avg_response_time_ms=avg_response_time,
            total_duration_seconds=total_duration,
            message_types=message_types,
            error_count=error_count,
            success_rate=success_rate
        )

    async def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old inactive sessions.
        
        Args:
            max_age_hours: Maximum age for inactive sessions
            
        Returns:
            Number of cleaned sessions
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        query = """
        UPDATE agent_sessions 
        SET status = 'failed', completed_at = NOW(),
            metadata = JSON_SET(COALESCE(metadata, '{}'), '$.cleanup_reason', 'expired')
        WHERE status IN ('active', 'paused') 
        AND created_at < %s
        """
        
        try:
            await self.comm_service._execute_query(query, (cutoff_time,))
            
            # Get affected row count
            count_query = "SELECT ROW_COUNT() as count"
            result = await self.comm_service._execute_query(count_query, fetch=True, fetch_one=True)
            cleaned_count = result["count"] if result else 0
            
            # Remove from active sessions cache
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.created_at and session.created_at < cutoff_time
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            logger.info(f"Cleaned up {cleaned_count} expired sessions (older than {max_age_hours} hours)")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            raise

    async def get_session_summaries(
        self,
        user_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SessionSummary]:
        """
        Get session summaries for analytics.
        
        Args:
            user_id: Filter by user ID
            status_filter: Filter by session status
            limit: Maximum sessions to return
            offset: Offset for pagination
            
        Returns:
            List of session summaries
        """
        where_clauses = []
        params = []
        
        if user_id:
            where_clauses.append("user_id = %s")
            params.append(user_id)
        
        if status_filter:
            where_clauses.append("status = %s")
            params.append(status_filter)
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT session_id, user_id, status, created_at, completed_at,
               agents_involved, metadata,
               JSON_LENGTH(conversation_history) as total_messages,
               TIMESTAMPDIFF(SECOND, created_at, COALESCE(completed_at, NOW())) as duration_seconds
        FROM agent_sessions
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        
        try:
            results = await self.comm_service._execute_query(query, tuple(params), fetch=True)
            
            summaries = []
            if results:
                for row in results:
                    summary = SessionSummary(
                        session_id=row["session_id"],
                        user_id=row["user_id"],
                        status=row["status"],
                        created_at=row["created_at"],
                        completed_at=row["completed_at"],
                        duration_seconds=row["duration_seconds"],
                        agents_involved=row["agents_involved"] if isinstance(row["agents_involved"], list) else [],
                        total_messages=row["total_messages"] or 0,
                        outcome=row.get("metadata", {}).get("outcome") if row.get("metadata") else None
                    )
                    summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get session summaries: {e}")
            raise

    async def search_sessions_by_content(
        self,
        search_term: str,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[str]:
        """
        Search sessions by conversation content.
        
        Args:
            search_term: Term to search for in conversation history
            user_id: Optional user ID filter
            limit: Maximum sessions to return
            
        Returns:
            List of session IDs matching the search
        """
        where_clauses = ["JSON_SEARCH(conversation_history, 'one', %s) IS NOT NULL"]
        params = [f"%{search_term}%"]
        
        if user_id:
            where_clauses.append("user_id = %s")
            params.append(user_id)
        
        where_clause = "WHERE " + " AND ".join(where_clauses)
        
        query = f"""
        SELECT session_id FROM agent_sessions
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        params.append(limit)
        
        try:
            results = await self.comm_service._execute_query(query, tuple(params), fetch=True)
            
            return [row["session_id"] for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Failed to search sessions by content: {e}")
            raise