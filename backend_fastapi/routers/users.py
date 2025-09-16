#!/usr/bin/env python3
"""
Users Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from database.connection import get_db
from routers.auth import get_current_user
from models.user import User

router = APIRouter()

# Pydantic models
class UserUpdateRequest(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    bio: Optional[str] = None
    skillLevel: Optional[str] = None
    learningPreferences: Optional[Dict[str, Any]] = None
    agentPreferences: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    user: Dict[str, Any]

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(user=current_user.to_dict())

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    
    update_data = {}
    
    if request.firstName is not None:
        update_data["first_name"] = request.firstName
    if request.lastName is not None:
        update_data["last_name"] = request.lastName
    if request.bio is not None:
        update_data["bio"] = request.bio
    if request.skillLevel is not None:
        update_data["skill_level"] = request.skillLevel
    if request.learningPreferences is not None:
        update_data["learning_preferences"] = request.learningPreferences
    if request.agentPreferences is not None:
        update_data["agent_preferences"] = request.agentPreferences
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        stmt = update(User).where(User.id == current_user.id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        
        # Refresh user data
        await db.refresh(current_user)
    
    return UserResponse(user=current_user.to_dict())

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (public profile)"""
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return public profile
    return UserResponse(user=user.to_public_dict())
