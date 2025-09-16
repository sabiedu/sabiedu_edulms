#!/usr/bin/env python3
"""
Vector Service for TiDB Vector Search
Following TiDB + AI via Python documentation
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from sqlalchemy import text
from database.connection import async_engine
from models.content import Content

class VectorService:
    def __init__(self):
        self.model_name = "gemini-embedding-001"
        self.embedding_dimension = 768  # Gemini embedding dimension
        
    async def initialize(self):
        """Initialize the vector service"""
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Test connection and create vector index if needed
        await self._ensure_vector_index()
        
    async def _ensure_vector_index(self):
        """Ensure vector index exists for content embeddings"""
        try:
            async with async_engine.begin() as conn:
                # Check if vector index exists
                check_index = text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.statistics 
                    WHERE table_name = 'content' 
                    AND index_name = 'idx_content_embedding'
                """)
                result = await conn.execute(check_index)
                index_exists = result.scalar() > 0
                
                if not index_exists:
                    # Create vector index for content embeddings
                    create_index = text(f"""
                        ALTER TABLE content 
                        ADD INDEX idx_content_embedding (
                            (CAST(embedding AS VECTOR({self.embedding_dimension}))) 
                        ) USING HNSW
                    """)
                    await conn.execute(create_index)
                    print("✅ Vector index created for content embeddings")
                else:
                    print("✅ Vector index already exists")
                    
        except Exception as e:
            print(f"⚠️  Vector index creation failed (may not be supported): {e}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Gemini"""
        try:
            result = genai.embed_content(
                model=f"{self.model_name}",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    async def store_content_with_embedding(
        self, 
        title: str,
        content_text: str,
        content_type: str,
        content_data: Dict[str, Any] = None,
        difficulty_level: str = "intermediate",
        subject: str = None,
        tags: List[str] = None,
        created_by: str = "system"
    ) -> int:
        """Store content with vector embedding"""
        
        # Generate embedding
        embedding = await self.generate_embedding(content_text)
        
        async with async_engine.begin() as conn:
            # Insert content with embedding
            insert_query = text("""
                INSERT INTO content (
                    title, content_type, content_text, content_data,
                    embedding, embedding_model, difficulty_level, 
                    subject, tags, created_by, is_published
                ) VALUES (
                    :title, :content_type, :content_text, :content_data,
                    :embedding, :embedding_model, :difficulty_level,
                    :subject, :tags, :created_by, :is_published
                )
            """)
            
            result = await conn.execute(insert_query, {
                "title": title,
                "content_type": content_type,
                "content_text": content_text,
                "content_data": json.dumps(content_data or {}),
                "embedding": json.dumps(embedding),
                "embedding_model": self.model_name,
                "difficulty_level": difficulty_level,
                "subject": subject,
                "tags": json.dumps(tags or []),
                "created_by": created_by,
                "is_published": True
            })
            
            return result.lastrowid
    
    async def vector_search(
        self, 
        query_text: str, 
        limit: int = 10,
        content_type: str = None,
        difficulty_level: str = None,
        subject: str = None
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        
        # Generate query embedding
        query_embedding = await self.generate_embedding(query_text)
        
        async with async_engine.begin() as conn:
            # Build search query with filters
            where_conditions = []
            params = {
                "query_embedding": json.dumps(query_embedding),
                "limit": limit
            }
            
            if content_type:
                where_conditions.append("content_type = :content_type")
                params["content_type"] = content_type
                
            if difficulty_level:
                where_conditions.append("difficulty_level = :difficulty_level")
                params["difficulty_level"] = difficulty_level
                
            if subject:
                where_conditions.append("subject = :subject")
                params["subject"] = subject
            
            where_clause = " AND ".join(where_conditions)
            if where_clause:
                where_clause = f"WHERE {where_clause} AND"
            else:
                where_clause = "WHERE"
            
            # Vector similarity search query
            search_query = text(f"""
                SELECT 
                    id, title, content_type, content_text, content_data,
                    difficulty_level, subject, tags, created_by,
                    VEC_COSINE_DISTANCE(
                        CAST(embedding AS VECTOR({self.embedding_dimension})),
                        CAST(:query_embedding AS VECTOR({self.embedding_dimension}))
                    ) AS distance,
                    created_at, updated_at
                FROM content
                {where_clause} is_published = true
                ORDER BY distance ASC
                LIMIT :limit
            """)
            
            result = await conn.execute(search_query, params)
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append({
                    "id": row.id,
                    "title": row.title,
                    "contentType": row.content_type,
                    "contentText": row.content_text,
                    "contentData": json.loads(row.content_data) if row.content_data else {},
                    "difficultyLevel": row.difficulty_level,
                    "subject": row.subject,
                    "tags": json.loads(row.tags) if row.tags else [],
                    "createdBy": row.created_by,
                    "distance": float(row.distance),
                    "similarity": 1 - float(row.distance),  # Convert distance to similarity
                    "createdAt": row.created_at.isoformat() if row.created_at else None,
                    "updatedAt": row.updated_at.isoformat() if row.updated_at else None
                })
            
            return results
    
    async def get_similar_content(
        self, 
        content_id: int, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar content to a given content item"""
        
        async with async_engine.begin() as conn:
            # Get the embedding of the reference content
            get_embedding_query = text("""
                SELECT embedding FROM content WHERE id = :content_id
            """)
            result = await conn.execute(get_embedding_query, {"content_id": content_id})
            row = result.fetchone()
            
            if not row or not row.embedding:
                return []
            
            reference_embedding = json.loads(row.embedding)
            
            # Find similar content
            similarity_query = text(f"""
                SELECT 
                    id, title, content_type, content_text,
                    difficulty_level, subject, tags,
                    VEC_COSINE_DISTANCE(
                        CAST(embedding AS VECTOR({self.embedding_dimension})),
                        CAST(:reference_embedding AS VECTOR({self.embedding_dimension}))
                    ) AS distance
                FROM content
                WHERE id != :content_id AND is_published = true
                ORDER BY distance ASC
                LIMIT :limit
            """)
            
            result = await conn.execute(similarity_query, {
                "reference_embedding": json.dumps(reference_embedding),
                "content_id": content_id,
                "limit": limit
            })
            
            rows = result.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "id": row.id,
                    "title": row.title,
                    "contentType": row.content_type,
                    "contentText": row.content_text,
                    "difficultyLevel": row.difficulty_level,
                    "subject": row.subject,
                    "tags": json.loads(row.tags) if row.tags else [],
                    "distance": float(row.distance),
                    "similarity": 1 - float(row.distance)
                })
            
            return results
