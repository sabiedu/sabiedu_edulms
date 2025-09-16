#!/usr/bin/env python3
"""
User Model with Agent Session Support
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(50))
    last_name = Column(String(50))
    bio = Column(Text)
    avatar_url = Column(String(255))
    
    # Role and permissions
    role = Column(String(20), default="student")  # student, instructor, admin
    is_active = Column(Boolean, default=True)
    
    # Learning preferences
    skill_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    learning_preferences = Column(JSON)  # JSON object for learning style, pace, etc.
    
    # Agent integration
    agent_preferences = Column(JSON)  # JSON object for agent communication preferences
    agent_sessions = Column(JSON)  # JSON array of active agent sessions
    last_agent_interaction = Column(DateTime(timezone=True))
    
    # Tracking
    login_count = Column(Integer, default=0)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflows = relationship("Workflow", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "bio": self.bio,
            "avatar": self.avatar_url,
            "role": self.role,
            "skillLevel": self.skill_level,
            "learningPreferences": self.learning_preferences or {},
            "agentPreferences": self.agent_preferences or {},
            "agentSessions": self.agent_sessions or [],
            "isActive": self.is_active,
            "loginCount": self.login_count,
            "lastLoginAt": self.last_login_at.isoformat() if self.last_login_at else None,
            "lastAgentInteraction": self.last_agent_interaction.isoformat() if self.last_agent_interaction else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self):
        """Convert user to public dictionary (no sensitive info)"""
        return {
            "id": self.id,
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "bio": self.bio,
            "avatar": self.avatar_url,
            "role": self.role,
            "skillLevel": self.skill_level,
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }
