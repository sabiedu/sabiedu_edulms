#!/usr/bin/env python3
"""
Agent Session Model for Multi-Agent Communication
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base

class AgentSession(Base):
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Agent information
    agent_types = Column(JSON)  # Array of agent types involved
    status = Column(String(20), default="active")  # active, closed, expired
    
    # Session data
    conversation_history = Column(JSON)  # Array of messages
    context_data = Column(JSON)  # Session context and state
    
    # Metadata
    close_reason = Column(String(100))
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    
    def to_dict(self):
        """Convert agent session to dictionary for API responses"""
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "userId": self.user_id,
            "agentTypes": self.agent_types or [],
            "status": self.status,
            "conversationHistory": self.conversation_history or [],
            "contextData": self.context_data or {},
            "closeReason": self.close_reason,
            "lastActivity": self.last_activity.isoformat() if self.last_activity else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "closedAt": self.closed_at.isoformat() if self.closed_at else None
        }
