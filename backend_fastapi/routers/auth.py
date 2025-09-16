#!/usr/bin/env python3
"""
Authentication Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from database.connection import get_db
from services.auth_service import AuthService
from models.user import User

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    identifier: str  # username or email
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class AuthResponse(BaseModel):
    jwt: str
    user: dict

class UserResponse(BaseModel):
    user: dict

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await AuthService.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/local", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login endpoint"""
    user = await AuthService.authenticate_user(db, request.identifier, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Update login tracking
    stmt = update(User).where(User.id == user.id).values(
        login_count=User.login_count + 1,
        last_login_at=datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    
    # Create access token
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        jwt=access_token,
        user=user.to_dict()
    )

@router.post("/local/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registration endpoint"""
    
    # Check if username exists
    existing_user = await AuthService.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = await AuthService.get_user_by_email(db, request.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(request.password)
    
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=hashed_password,
        first_name=request.firstName,
        last_name=request.lastName,
        role="student",
        is_active=True,
        login_count=0,
        learning_preferences={
            "learningStyle": "mixed",
            "difficultyPreference": "adaptive",
            "pacePreference": "self-paced"
        },
        agent_preferences={
            "preferredCommunicationStyle": "friendly",
            "enableProactiveHelp": True,
            "enableLearningAnalytics": True,
            "tutorPersonality": "encouraging"
        },
        agent_sessions=[]
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create access token
    access_token = AuthService.create_access_token(data={"sub": str(new_user.id)})
    
    return AuthResponse(
        jwt=access_token,
        user=new_user.to_dict()
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(user=current_user.to_dict())

@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Logged out successfully"}
