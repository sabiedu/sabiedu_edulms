#!/usr/bin/env python3
"""
Analytics Model for Learning Data and Events
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event information
    action_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(50), index=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), index=True)
    
    # Context
    course_id = Column(Integer)
    lesson_id = Column(Integer)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    agent_session_id = Column(String(100))
    
    # Data
    event_metadata = Column(JSON)  # Additional event data
    performance_score = Column(Float)  # 0.0 to 1.0
    duration = Column(Integer)  # seconds
    
    # Tracking
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")
    
    def to_dict(self):
        """Convert analytics to dictionary for API responses"""
        return {
            "id": self.id,
            "actionType": self.action_type,
            "eventCategory": self.event_category,
            "userId": self.user_id,
            "sessionId": self.session_id,
            "courseId": self.course_id,
            "lessonId": self.lesson_id,
            "workflowId": self.workflow_id,
            "agentSessionId": self.agent_session_id,
            "metadata": self.event_metadata or {},
            "performanceScore": self.performance_score,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }
