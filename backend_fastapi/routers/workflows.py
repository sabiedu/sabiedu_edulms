from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.workflow import Workflow, WorkflowStatus
from schemas.workflow_schema import WorkflowCreate, Workflow as WorkflowSchema
from services.workflow_service import create_workflow_from_template, get_workflows_by_user
from config.workflow_templates import WORKFLOW_TEMPLATES
from models.api_responses import (
    WorkflowAvailableResponse,
    WorkflowExecuteRequest,
    WorkflowExecuteResponse,
    WorkflowHistoryResponse,
    WorkflowStatusResponse,
    ErrorResponse
)
from services.data_transformer import (
    transform_template_to_frontend_format,
    transform_execution_result,
    transform_history_data
)


router = APIRouter(prefix="/workflows", tags=["workflows"])

# --- New Endpoints for Frontend-Backend API Alignment ---

@router.get(
    "/templates",
    response_model=WorkflowAvailableResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get Available Workflows"
)
def get_available_workflows():
    """
    (Task 3)
    Retrieves a list of available workflow templates formatted for the frontend.
    """
    try:
        if not WORKFLOW_TEMPLATES:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No workflow templates found.")
        
        transformed_data = transform_template_to_frontend_format(WORKFLOW_TEMPLATES)
        return WorkflowAvailableResponse(data=transformed_data)
    except Exception as e:
        # Basic error handling for template loading/transformation failures
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load templates: {str(e)}")

@router.post(
    "/",
    response_model=WorkflowExecuteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Execute a Workflow"
)
def execute_workflow(request: WorkflowExecuteRequest, db: Session = Depends(get_db)):
    """
    (Task 4)
    Executes a workflow based on a template and initial data.
    """
    try:
        workflow = create_workflow_from_template(
            db=db,
            template_name=request.workflow_name,
            user_id=request.user_id,
            parameters=request.initial_data
        )
        # NOTE: Assuming the workflow execution is synchronous for this implementation.
        # If execution is async, the status would be 'PENDING' or 'RUNNING'.
        
        # This transformation assumes the workflow object is complete after creation.
        transformed_result = transform_execution_result(workflow)
        return WorkflowExecuteResponse(data=transformed_result)
    except ValueError as e:
        # Raised from create_workflow_from_template if template not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        # Catch-all for other execution errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Workflow execution failed: {str(e)}")

@router.get(
    "/",
    response_model=WorkflowHistoryResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Get Workflow History"
)
def get_workflow_history(
    user_id: Optional[str] = Query(None, description="The ID of the user to retrieve history for."),
    limit: int = Query(10, gt=0, le=100, description="The maximum number of records to return."),
    skip: int = Query(0, ge=0, description="The number of records to skip."),
    db: Session = Depends(get_db)
):
    """
    (Task 5)
    Retrieves the execution history of workflows.
    If user_id is provided, retrieves history for that specific user.
    Otherwise, retrieves a list of all workflows.
    """
    try:
        if user_id:
            workflows = get_workflows_by_user(db, user_id=user_id, limit=limit, skip=skip)
        else:
            workflows = db.query(Workflow).offset(skip).limit(limit).all()
            
        transformed_data = transform_history_data(workflows)
        return WorkflowHistoryResponse(data=transformed_data)
    except Exception as e:
        # Handle database errors or other unexpected issues
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve workflow history: {str(e)}")

@router.get(
    "/{workflow_id}",
    response_model=WorkflowStatusResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Get Workflow Status"
)
def get_workflow_status(workflow_id: str, db: Session = Depends(get_db)):
    """
    (Task 6)
    Retrieves the status and details of a specific workflow execution.
    """
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")
        
        transformed_data = transform_execution_result(workflow)
        return WorkflowStatusResponse(data=transformed_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve workflow status: {str(e)}")