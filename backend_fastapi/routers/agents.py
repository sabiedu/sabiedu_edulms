#!/usr/bin/env python3
"""
Agents Router for Multi-Agent Communication
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from database.connection import get_db
from routers.auth import get_current_user
from models.user import User
from models.agent_session import AgentSession
from services.agent_service import AgentService

router = APIRouter()

# Pydantic models
class AgentSessionRequest(BaseModel):
    agentTypes: List[str]
    contextData: Optional[Dict[str, Any]] = {}

class AgentMessageRequest(BaseModel):
    sessionId: str
    message: str
    agentType: Optional[str] = None

class AgentSessionResponse(BaseModel):
    session: Dict[str, Any]

class AgentMessageResponse(BaseModel):
    response: Dict[str, Any]

class AgentStatusResponse(BaseModel):
    agents: Dict[str, Any]

@router.post("/sessions", response_model=AgentSessionResponse)
async def create_agent_session(
    request: AgentSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent session"""
    
    session_id = str(uuid.uuid4())
    
    # Create agent session
    agent_session = AgentSession(
        session_id=session_id,
        user_id=current_user.id,
        agent_types=request.agentTypes,
        status="active",
        conversation_history=[],
        context_data=request.contextData
    )
    
    db.add(agent_session)
    await db.commit()
    await db.refresh(agent_session)
    
    # Update user's agent sessions
    current_sessions = current_user.agent_sessions or []
    current_sessions.append({
        "id": session_id,
        "agentTypes": request.agentTypes,
        "status": "active",
        "createdAt": datetime.utcnow().isoformat()
    })
    
    stmt = update(User).where(User.id == current_user.id).values(
        agent_sessions=current_sessions,
        last_agent_interaction=datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    
    return AgentSessionResponse(session=agent_session.to_dict())

@router.get("/sessions/{session_id}", response_model=AgentSessionResponse)
async def get_agent_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent session details"""
    
    stmt = select(AgentSession).where(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent session not found"
        )
    
    return AgentSessionResponse(session=session.to_dict())

@router.post("/sessions/{session_id}/message", response_model=AgentMessageResponse)
async def send_agent_message(
    session_id: str,
    request: AgentMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send message to agent session"""
    
    # Get agent session
    stmt = select(AgentSession).where(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent session not found"
        )
    
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent session is not active"
        )
    
    # Process message through agent service
    agent_service = AgentService()
    response = await agent_service.process_message(
        session_id=session_id,
        message=request.message,
        agent_type=request.agentType,
        user_id=current_user.id,
        context_data=session.context_data
    )
    
    # Update conversation history
    conversation_history = session.conversation_history or []
    conversation_history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "type": "user_message",
        "content": request.message,
        "userId": current_user.id
    })
    conversation_history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "type": "agent_response",
        "content": response.get("message", ""),
        "agentType": response.get("agent_type", "unknown"),
        "metadata": response.get("metadata", {})
    })
    
    # Update session
    stmt = update(AgentSession).where(AgentSession.id == session.id).values(
        conversation_history=conversation_history,
        last_activity=datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    
    return AgentMessageResponse(response=response)

@router.post("/sessions/{session_id}/close")
async def close_agent_session(
    session_id: str,
    reason: Optional[str] = "User closed session",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Close agent session"""
    
    stmt = select(AgentSession).where(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent session not found"
        )
    
    # Update session status
    stmt = update(AgentSession).where(AgentSession.id == session.id).values(
        status="closed",
        close_reason=reason,
        closed_at=datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Agent session closed successfully"}

@router.get("/sessions", response_model=List[Dict[str, Any]])
async def list_agent_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's agent sessions"""
    
    stmt = select(AgentSession).where(
        AgentSession.user_id == current_user.id
    ).order_by(AgentSession.created_at.desc())
    
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    return [session.to_dict() for session in sessions]

@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """Get agent system status"""
    
    agent_service = AgentService()
    status = await agent_service.get_system_status()
    
    return AgentStatusResponse(agents=status)

@router.post("/execute")
async def execute_agent_action(
    action: str,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Execute direct agent action"""
    
    agent_service = AgentService()
    result = await agent_service.execute_action(
        action=action,
        data={**data, "user_id": current_user.id}
    )
    
    return result
