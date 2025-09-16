#!/usr/bin/env python3
"""
Workflow Model for Multi-Agent Orchestration
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
from enum import Enum

class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    CRASHED = "CRASHED"

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    template_name = Column(String(100), nullable=False, index=True)
    
    # Status and execution
    status = Column(String(20), default=WorkflowStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Timing
    estimated_duration = Column(Integer)  # seconds
    actual_duration = Column(Integer)  # seconds
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Configuration
    parameters = Column(JSON)  # Input parameters
    results = Column(JSON)  # Output results
    agents_involved = Column(JSON)  # List of agent names
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_session_id = Column(String(100))  # UUID of agent session
    
    # Error handling
    error_message = Column(Text)
    cancel_reason = Column(String(255))
    retry_count = Column(Integer, default=0)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    
    def to_dict(self):
        """Convert workflow to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "templateName": self.template_name,
            "status": self.status,
            "progress": self.progress,
            "estimatedDuration": self.estimated_duration,
            "actualDuration": self.actual_duration,
            "parameters": self.parameters or {},
            "results": self.results or {},
            "agentsInvolved": self.agents_involved or [],
            "userId": self.user_id,
            "agentSessionId": self.agent_session_id,
            "errorMessage": self.error_message,
            "cancelReason": self.cancel_reason,
            "retryCount": self.retry_count,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "cancelledAt": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
