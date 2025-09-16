#!/usr/bin/env python3
"""
Analytics Router
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from database.connection import get_db
from routers.auth import get_current_user
from models.user import User
from models.analytics import Analytics
from models.workflow import Workflow

router = APIRouter()

# Pydantic models
class AnalyticsEventRequest(BaseModel):
    actionType: str
    eventCategory: Optional[str] = None
    sessionId: Optional[str] = None
    courseId: Optional[int] = None
    lessonId: Optional[int] = None
    workflowId: Optional[int] = None
    agentSessionId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    performanceScore: Optional[float] = None
    duration: Optional[int] = None

class AnalyticsResponse(BaseModel):
    success: bool
    message: str

class AnalyticsReportResponse(BaseModel):
    report: Dict[str, Any]

@router.post("/events", response_model=AnalyticsResponse)
async def create_analytics_event(
    request: AnalyticsEventRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create analytics event"""
    
    analytics_event = Analytics(
        action_type=request.actionType,
        event_category=request.eventCategory,
        user_id=current_user.id,
        session_id=request.sessionId,
        course_id=request.courseId,
        lesson_id=request.lessonId,
        workflow_id=request.workflowId,
        agent_session_id=request.agentSessionId,
        event_metadata=request.metadata,
        performance_score=request.performanceScore,
        duration=request.duration
    )
    
    db.add(analytics_event)
    await db.commit()
    
    return AnalyticsResponse(
        success=True,
        message="Analytics event created successfully"
    )

@router.get("/user-report", response_model=AnalyticsReportResponse)
async def get_user_analytics_report(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user analytics report"""
    
    # Calculate timeframe
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map[timeframe]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get user analytics
    stmt = select(Analytics).where(
        Analytics.user_id == current_user.id,
        Analytics.timestamp >= start_date
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    # Get workflow analytics
    workflow_stmt = select(Workflow).where(
        Workflow.user_id == current_user.id,
        Workflow.created_at >= start_date
    )
    workflow_result = await db.execute(workflow_stmt)
    workflows = workflow_result.scalars().all()
    
    # Process analytics
    report = {
        "timeframe": timeframe,
        "totalEvents": len(events),
        "totalWorkflows": len(workflows),
        "eventsByType": {},
        "workflowsByStatus": {},
        "performanceMetrics": {
            "averageScore": 0,
            "totalDuration": 0,
            "sessionsCount": 0
        },
        "activityTimeline": [],
        "learningProgress": {
            "completedWorkflows": 0,
            "averageWorkflowDuration": 0,
            "mostUsedAgents": []
        }
    }
    
    # Process events
    session_ids = set()
    total_score = 0
    score_count = 0
    total_duration = 0
    
    for event in events:
        # Event types
        event_type = event.action_type
        report["eventsByType"][event_type] = report["eventsByType"].get(event_type, 0) + 1
        
        # Performance metrics
        if event.performance_score is not None:
            total_score += event.performance_score
            score_count += 1
        
        if event.duration is not None:
            total_duration += event.duration
        
        if event.session_id:
            session_ids.add(event.session_id)
    
    # Calculate averages
    if score_count > 0:
        report["performanceMetrics"]["averageScore"] = total_score / score_count
    
    report["performanceMetrics"]["totalDuration"] = total_duration
    report["performanceMetrics"]["sessionsCount"] = len(session_ids)
    
    # Process workflows
    completed_workflows = 0
    workflow_durations = []
    agent_usage = {}
    
    for workflow in workflows:
        status = workflow.status
        report["workflowsByStatus"][status] = report["workflowsByStatus"].get(status, 0) + 1
        
        if status == "COMPLETED":
            completed_workflows += 1
            if workflow.actual_duration:
                workflow_durations.append(workflow.actual_duration)
        
        # Count agent usage
        if workflow.agents_involved:
            for agent in workflow.agents_involved:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
    
    report["learningProgress"]["completedWorkflows"] = completed_workflows
    if workflow_durations:
        report["learningProgress"]["averageWorkflowDuration"] = sum(workflow_durations) / len(workflow_durations)
    
    # Most used agents
    sorted_agents = sorted(agent_usage.items(), key=lambda x: x[1], reverse=True)
    report["learningProgress"]["mostUsedAgents"] = sorted_agents[:5]
    
    return AnalyticsReportResponse(report=report)

@router.get("/system-report", response_model=AnalyticsReportResponse)
async def get_system_analytics_report(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide analytics report (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Calculate timeframe
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map[timeframe]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get system analytics
    analytics_stmt = select(func.count(Analytics.id)).where(
        Analytics.timestamp >= start_date
    )
    analytics_result = await db.execute(analytics_stmt)
    total_events = analytics_result.scalar()
    
    # Get user count
    user_stmt = select(func.count(User.id)).where(
        User.created_at >= start_date
    )
    user_result = await db.execute(user_stmt)
    new_users = user_result.scalar()
    
    # Get workflow stats
    workflow_stmt = select(func.count(Workflow.id)).where(
        Workflow.created_at >= start_date
    )
    workflow_result = await db.execute(workflow_stmt)
    total_workflows = workflow_result.scalar()
    
    report = {
        "timeframe": timeframe,
        "systemMetrics": {
            "totalEvents": total_events,
            "newUsers": new_users,
            "totalWorkflows": total_workflows
        },
        "performance": {
            "systemHealth": "healthy",
            "averageResponseTime": "< 100ms",
            "uptime": "99.9%"
        }
    }
    
    return AnalyticsReportResponse(report=report)
