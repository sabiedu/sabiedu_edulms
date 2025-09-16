#!/usr/bin/env python3
"""
Content Model with Vector Search Support
Following TiDB vector search documentation
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Index, Boolean
from sqlalchemy.sql import func
from database.connection import Base

class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False, index=True)  # lesson, quiz, assignment, etc.
    
    # Content data
    content_text = Column(Text)
    content_data = Column(JSON)  # Structured content data
    
    # Vector embeddings for search
    embedding = Column(JSON)  # Vector embedding as JSON array
    embedding_model = Column(String(50), default="text-embedding-004")
    
    # Metadata
    difficulty_level = Column(String(20), index=True)
    subject = Column(String(100), index=True)
    tags = Column(JSON)  # Array of tags
    
    # Authoring
    created_by = Column(String(100))  # Agent or user who created this
    source_url = Column(String(500))
    
    # Status
    is_published = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert content to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "contentType": self.content_type,
            "contentText": self.content_text,
            "contentData": self.content_data or {},
            "difficultyLevel": self.difficulty_level,
            "subject": self.subject,
            "tags": self.tags or [],
            "createdBy": self.created_by,
            "sourceUrl": self.source_url,
            "isPublished": self.is_published,
            "version": self.version,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }

# Create vector search index for embeddings
# This will be created via migration or manual SQL
# CREATE INDEX idx_content_embedding ON content ((CAST(embedding AS VECTOR(1536)))) USING HNSW;
