"""
Multi-Agent Orchestrator for EduLMS v2
Implements multi-step agentic workflows with TiDB Serverless integration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..communication.tidb_service import TiDBCommunicationService, TaskStatus
from ..communication.gemini_client import get_gemini_client
from ..communication.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class WorkflowStep(Enum):
    """Workflow step types"""
    INGEST_DATA = "ingest_data"
    VECTOR_SEARCH = "vector_search"
    ANALYZE_CONTENT = "analyze_content"
    GENERATE_CONTENT = "generate_content"
    ASSESS_LEARNING = "assess_learning"
    PERSONALIZE = "personalize"
    RESEARCH = "research"
    MONITOR = "monitor"

@dataclass
class WorkflowTask:
    """Workflow task definition"""
    id: str
    workflow_id: str
    step_type: WorkflowStep
    agent_name: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None
    status: TaskStatus = TaskStatus.PENDING
    output_data: Dict[str, Any] = None
    error_message: str = None
    started_at: datetime = None
    completed_at: datetime = None

class MultiAgentOrchestrator:
    """
    Orchestrates multi-step workflows across EduLMS agents
    
    Implements the hackathon requirements:
    1. Ingest & Index Data - Content ingestion with vector embeddings
    2. Search Your Data - Vector and full-text search in TiDB
    3. Chain LLM Calls - Multi-agent AI collaboration
    4. Invoke External Tools - API integrations
    5. Build Multi-Step Flow - End-to-end automated workflows
    """
    
    def __init__(self):
        self.tidb_service = TiDBCommunicationService()
        self.gemini_client = get_gemini_client()
        self.cache_manager = CacheManager()
        
        # Agent registry
        self.agents = {
            'research_agent': 'research',
            'analytics_agent': 'analytics_request',
            'assessment_agent': 'assessment',
            'tutor_agent': 'demo',
            'content_generation_agent': 'content_request',
            'personalization_agent': 'profile_update',
            'content_curator_agent': 'content_curation',
            'learning_path_agent': 'learning_path',
            'monitoring_agent': 'monitoring_alert'
        }
        
        # Predefined workflows
        self.workflows = {
            'adaptive_learning_pipeline': self._create_adaptive_learning_workflow,
            'content_discovery_workflow': self._create_content_discovery_workflow,
            'assessment_generation_workflow': self._create_assessment_workflow,
            'research_to_content_workflow': self._create_research_content_workflow,
            'personalized_study_plan': self._create_study_plan_workflow
        }
    
    async def execute_workflow(self, workflow_name: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a predefined multi-step workflow"""
        try:
            workflow_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Starting workflow: {workflow_id}")
            
            # Create workflow tasks
            if workflow_name not in self.workflows:
                raise ValueError(f"Unknown workflow: {workflow_name}")
            
            tasks = await self.workflows[workflow_name](workflow_id, initial_data)
            
            # Execute workflow
            results = await self._execute_workflow_tasks(workflow_id, tasks)
            
            # Store workflow results in TiDB
            await self._store_workflow_results(workflow_id, workflow_name, initial_data, results)
            
            return {
                'workflow_id': workflow_id,
                'workflow_name': workflow_name,
                'status': 'completed',
                'results': results,
                'completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                'workflow_id': workflow_id if 'workflow_id' in locals() else 'unknown',
                'workflow_name': workflow_name,
                'status': 'failed',
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            }
    
    async def _create_adaptive_learning_workflow(self, workflow_id: str, data: Dict[str, Any]) -> List[WorkflowTask]:
        """
        Creates adaptive learning workflow:
        1. Analyze user performance (Analytics Agent)
        2. Search for similar learning patterns (Vector Search)
        3. Generate personalized recommendations (Personalization Agent)
        4. Create adaptive content (Content Generation Agent)
        5. Monitor progress (Monitoring Agent)
        """
        user_id = data.get('user_id')
        course_id = data.get('course_id')
        
        return [
            WorkflowTask(
                id=f"{workflow_id}_step1",
                workflow_id=workflow_id,
                step_type=WorkflowStep.ANALYZE_CONTENT,
                agent_name='analytics_agent',
                input_data={
                    'query_type': 'performance',
                    'user_id': user_id,
                    'course_id': course_id,
                    'timeframe': '30d'
                }
            ),
            WorkflowTask(
                id=f"{workflow_id}_step2",
                workflow_id=workflow_id,
                step_type=WorkflowStep.VECTOR_SEARCH,
                agent_name='vector_search',
                input_data={
                    'search_type': 'similar_learners',
                    'user_profile': 'from_step1'
                },
                dependencies=[f"{workflow_id}_step1"]
            ),
            WorkflowTask(
                id=f"{workflow_id}_step3",
                workflow_id=workflow_id,
                step_type=WorkflowStep.PERSONALIZE,
                agent_name='personalization_agent',
                input_data={
                    'user_id': user_id,
                    'performance_data': 'from_step1',
                    'similar_patterns': 'from_step2'
                },
                dependencies=[f"{workflow_id}_step1", f"{workflow_id}_step2"]
            ),
            WorkflowTask(
                id=f"{workflow_id}_step4",
                workflow_id=workflow_id,
                step_type=WorkflowStep.GENERATE_CONTENT,
                agent_name='content_generation_agent',
                input_data={
                    'content_type': 'adaptive_lesson',
                    'personalization_data': 'from_step3',
                    'difficulty_level': 'adaptive'
                },
                dependencies=[f"{workflow_id}_step3"]
            ),
            WorkflowTask(
                id=f"{workflow_id}_step5",
                workflow_id=workflow_id,
                step_type=WorkflowStep.MONITOR,
                agent_name='monitoring_agent',
                input_data={
                    'monitoring_type': 'learning_progress',
                    'user_id': user_id,
                    'workflow_id': workflow_id
                },
                dependencies=[f"{workflow_id}_step4"]
            )
        ]
    
    async def _create_content_discovery_workflow(self, workflow_id: str, data: Dict[str, Any]) -> List[WorkflowTask]:
        """
        Content discovery workflow:
        1. Research topic (Research Agent)
        2. Search existing content (Vector Search)
        3. Curate and filter content (Content Curator)
        4. Generate new content if needed (Content Generation)
        5. Index new content (Vector Embeddings)
        """
        topic = data.get('topic')
        difficulty = data.get('difficulty', 'intermediate')
        
        return [
            WorkflowTask(
                id=f"{workflow_id}_research",
                workflow_id=workflow_id,
                step_type=WorkflowStep.RESEARCH,
                agent_name='research_agent',
                input_data={
                    'query': topic,
                    'research_type': 'academic_search',
                    'depth': 'comprehensive'
                }
            ),
            WorkflowTask(
                id=f"{workflow_id}_search",
                workflow_id=workflow_id,
                step_type=WorkflowStep.VECTOR_SEARCH,
                agent_name='vector_search',
                input_data={
                    'query': topic,
                    'search_type': 'content_similarity',
                    'limit': 10
                }
            ),
            WorkflowTask(
                id=f"{workflow_id}_curate",
                workflow_id=workflow_id,
                step_type=WorkflowStep.ANALYZE_CONTENT,
                agent_name='content_curator_agent',
                input_data={
                    'task_type': 'assess_quality',
                    'research_data': 'from_research',
                    'existing_content': 'from_search'
                },
                dependencies=[f"{workflow_id}_research", f"{workflow_id}_search"]
            ),
            WorkflowTask(
                id=f"{workflow_id}_generate",
                workflow_id=workflow_id,
                step_type=WorkflowStep.GENERATE_CONTENT,
                agent_name='content_generation_agent',
                input_data={
                    'content_type': 'lesson',
                    'topic': topic,
                    'difficulty_level': difficulty,
                    'research_context': 'from_research',
                    'quality_requirements': 'from_curate'
                },
                dependencies=[f"{workflow_id}_curate"]
            ),
            WorkflowTask(
                id=f"{workflow_id}_index",
                workflow_id=workflow_id,
                step_type=WorkflowStep.INGEST_DATA,
                agent_name='vector_indexer',
                input_data={
                    'content': 'from_generate',
                    'metadata': {
                        'topic': topic,
                        'difficulty': difficulty,
                        'workflow_id': workflow_id
                    }
                },
                dependencies=[f"{workflow_id}_generate"]
            )
        ]
    
    async def _create_assessment_workflow(self, workflow_id: str, data: Dict[str, Any]) -> List[WorkflowTask]:
        """
        Assessment generation workflow:
        1. Analyze lesson content (Analytics)
        2. Search for similar assessments (Vector Search)
        3. Generate new assessment (Assessment Agent)
        4. Personalize difficulty (Personalization Agent)
        """
        lesson_content = data.get('lesson_content')
        user_id = data.get('user_id')
        
        return [
            WorkflowTask(
                id=f"{workflow_id}_analyze",
                workflow_id=workflow_id,
                step_type=WorkflowStep.ANALYZE_CONTENT,
                agent_name='analytics_agent',
                input_data={
                    'query_type': 'content_analysis',
                    'content': lesson_content
                }
            ),
            WorkflowTask(
                id=f"{workflow_id}_search_assessments",
                workflow_id=workflow_id,
                step_type=WorkflowStep.VECTOR_SEARCH,
                agent_name='vector_search',
                input_data={
                    'query': lesson_content,
                    'search_type': 'assessment_similarity',
                    'content_type': 'assessment'
                }
            ),
            WorkflowTask(
                id=f"{workflow_id}_generate_quiz",
                workflow_id=workflow_id,
                step_type=WorkflowStep.ASSESS_LEARNING,
                agent_name='assessment_agent',
                input_data={
                    'task_type': 'create_quiz',
                    'lesson_content': lesson_content,
                    'similar_assessments': 'from_search_assessments',
                    'content_analysis': 'from_analyze'
                },
                dependencies=[f"{workflow_id}_analyze", f"{workflow_id}_search_assessments"]
            ),
            WorkflowTask(
                id=f"{workflow_id}_personalize_difficulty",
                workflow_id=workflow_id,
                step_type=WorkflowStep.PERSONALIZE,
                agent_name='personalization_agent',
                input_data={
                    'user_id': user_id,
                    'assessment_data': 'from_generate_quiz',
                    'adaptation_type': 'difficulty'
                },
                dependencies=[f"{workflow_id}_generate_quiz"]
            )
        ]
    
    async def _create_research_content_workflow(self, workflow_id: str, data: Dict[str, Any]) -> List[WorkflowTask]:
        """Research to content creation workflow"""
        research_query = data.get('research_query')
        content_type = data.get('content_type', 'lesson')
        
        return [
            WorkflowTask(
                id=f"{workflow_id}_research",
                workflow_id=workflow_id,
                step_type=WorkflowStep.RESEARCH,
                agent_name='research_agent',
                input_data={
                    'query': research_query,
                    'research_type': 'literature_review'
                }
            ),
            WorkflowTask(
                id=f"{workflow_id}_content_gen",
                workflow_id=workflow_id,
                step_type=WorkflowStep.GENERATE_CONTENT,
                agent_name='content_generation_agent',
                input_data={
                    'content_type': content_type,
                    'research_data': 'from_research',
                    'topic': research_query
                },
                dependencies=[f"{workflow_id}_research"]
            )
        ]
    
    async def _create_study_plan_workflow(self, workflow_id: str, data: Dict[str, Any]) -> List[WorkflowTask]:
        """Personalized study plan creation workflow"""
        user_id = data.get('user_id')
        learning_goals = data.get('learning_goals', [])
        
        return [
            WorkflowTask(
                id=f"{workflow_id}_profile_analysis",
                workflow_id=workflow_id,
                step_type=WorkflowStep.ANALYZE_CONTENT,
                agent_name='analytics_agent',
                input_data={
                    'query_type': 'performance',
                    'user_id': user_id
                }
            ),
            WorkflowTask(
                id=f"{workflow_id}_personalize_plan",
                workflow_id=workflow_id,
                step_type=WorkflowStep.PERSONALIZE,
                agent_name='personalization_agent',
                input_data={
                    'user_id': user_id,
                    'learning_goals': learning_goals,
                    'performance_data': 'from_profile_analysis'
                },
                dependencies=[f"{workflow_id}_profile_analysis"]
            ),
            WorkflowTask(
                id=f"{workflow_id}_create_path",
                workflow_id=workflow_id,
                step_type=WorkflowStep.GENERATE_CONTENT,
                agent_name='learning_path_agent',
                input_data={
                    'task_type': 'generate_path',
                    'user_profile': 'from_personalize_plan',
                    'goals': learning_goals
                },
                dependencies=[f"{workflow_id}_personalize_plan"]
            )
        ]
    
    async def _execute_workflow_tasks(self, workflow_id: str, tasks: List[WorkflowTask]) -> Dict[str, Any]:
        """Execute workflow tasks with dependency management"""
        completed_tasks = {}
        task_outputs = {}
        
        # Create dependency graph
        remaining_tasks = {task.id: task for task in tasks}
        
        while remaining_tasks:
            # Find tasks with no pending dependencies
            ready_tasks = []
            for task_id, task in remaining_tasks.items():
                if not task.dependencies or all(dep in completed_tasks for dep in task.dependencies):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                raise RuntimeError("Circular dependency detected in workflow")
            
            # Execute ready tasks in parallel
            task_results = await asyncio.gather(
                *[self._execute_single_task(task, task_outputs) for task in ready_tasks],
                return_exceptions=True
            )
            
            # Process results
            for task, result in zip(ready_tasks, task_results):
                if isinstance(result, Exception):
                    logger.error(f"Task {task.id} failed: {result}")
                    task.status = TaskStatus.FAILED
                    task.error_message = str(result)
                else:
                    task.status = TaskStatus.COMPLETED
                    task.output_data = result
                    task_outputs[task.id] = result
                
                completed_tasks[task.id] = task
                del remaining_tasks[task.id]
        
        return {
            'workflow_id': workflow_id,
            'completed_tasks': len(completed_tasks),
            'task_results': task_outputs,
            'execution_summary': self._generate_execution_summary(completed_tasks)
        }
    
    async def _execute_single_task(self, task: WorkflowTask, previous_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow task"""
        try:
            task.started_at = datetime.now()
            logger.info(f"Executing task: {task.id} ({task.step_type.value})")
            
            # Resolve input data dependencies
            resolved_input = await self._resolve_task_inputs(task, previous_outputs)
            
            # Execute based on step type
            if task.step_type == WorkflowStep.VECTOR_SEARCH:
                result = await self._execute_vector_search(resolved_input)
            elif task.step_type == WorkflowStep.INGEST_DATA:
                result = await self._execute_data_ingestion(resolved_input)
            else:
                # Send to appropriate agent
                result = await self._send_to_agent(task.agent_name, resolved_input)
            
            task.completed_at = datetime.now()
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.id} - {e}")
            raise
    
    async def _resolve_task_inputs(self, task: WorkflowTask, previous_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve task input dependencies from previous task outputs"""
        resolved_input = task.input_data.copy()
        
        for key, value in resolved_input.items():
            if isinstance(value, str) and value.startswith('from_'):
                dependency_task = value.replace('from_', '')
                if dependency_task in previous_outputs:
                    resolved_input[key] = previous_outputs[dependency_task]
        
        return resolved_input
    
    async def _execute_vector_search(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute vector search in TiDB"""
        try:
            query = input_data.get('query', '')
            search_type = input_data.get('search_type', 'content_similarity')
            limit = input_data.get('limit', 10)
            
            # Generate query embedding
            embeddings = await self.gemini_client.generate_embeddings([query])
            query_vector = embeddings[0]
            
            # Execute vector search in TiDB
            search_query = """
            SELECT content_id, content_text, metadata,
                   VEC_COSINE_DISTANCE(embedding_vector, %s) as similarity_score
            FROM vector_embeddings
            WHERE content_type = %s
            ORDER BY similarity_score DESC
            LIMIT %s
            """
            
            results = await self.tidb_service._execute_query(
                search_query,
                (json.dumps(query_vector), search_type, limit),
                fetch=True
            )
            
            return {
                'search_results': results,
                'query': query,
                'search_type': search_type,
                'results_count': len(results) if results else 0
            }
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise
    
    async def _execute_data_ingestion(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest and index data with vector embeddings"""
        try:
            content = input_data.get('content', '')
            metadata = input_data.get('metadata', {})
            content_type = metadata.get('content_type', 'lesson')
            
            # Generate embeddings
            embeddings = await self.gemini_client.generate_embeddings([content])
            embedding_vector = embeddings[0]
            
            # Store in TiDB with vector embedding
            insert_query = """
            INSERT INTO vector_embeddings 
            (content_id, content_type, content_text, embedding_vector, metadata, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            content_id = f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            await self.tidb_service._execute_query(
                insert_query,
                (
                    content_id,
                    content_type,
                    content,
                    json.dumps(embedding_vector),
                    json.dumps(metadata),
                    datetime.now(),
                    datetime.now()
                )
            )
            
            return {
                'content_id': content_id,
                'indexed': True,
                'embedding_dimensions': len(embedding_vector),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            raise
    
    async def _send_to_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send task to specific agent and wait for response"""
        try:
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            channel = self.agents[agent_name]
            
            # Send message to agent
            await self.tidb_service.send_message(
                channel=channel,
                sender_agent='orchestrator',
                message=input_data,
                recipient_agent=agent_name,
                priority=5
            )
            
            # Poll for response
            response = await self._poll_for_agent_response(agent_name, channel)
            return response
            
        except Exception as e:
            logger.error(f"Agent communication failed: {agent_name} - {e}")
            raise
    
    async def _poll_for_agent_response(self, agent_name: str, channel: str, timeout: int = 60) -> Dict[str, Any]:
        """Poll for agent response with timeout"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            messages = await self.tidb_service.poll_messages(
                channel=f"{channel}_response",
                agent_name='orchestrator',
                limit=1
            )
            
            if messages:
                message = messages[0]
                # Mark as processed
                await self.tidb_service.mark_message_processed(
                    message_id=message.id,
                    processing_agent='orchestrator'
                )
                return message.message
            
            await asyncio.sleep(2)
        
        raise TimeoutError(f"Agent {agent_name} did not respond within {timeout} seconds")
    
    async def _store_workflow_results(self, workflow_id: str, workflow_name: str, 
                                    initial_data: Dict[str, Any], results: Dict[str, Any]):
        """Store workflow execution results in TiDB"""
        try:
            insert_query = """
            INSERT INTO workflow_executions 
            (workflow_id, workflow_name, initial_data, results, status, created_at, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            await self.tidb_service._execute_query(
                insert_query,
                (
                    workflow_id,
                    workflow_name,
                    json.dumps(initial_data),
                    json.dumps(results),
                    'completed',
                    datetime.now(),
                    datetime.now()
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to store workflow results: {e}")
    
    def _generate_execution_summary(self, completed_tasks: Dict[str, WorkflowTask]) -> Dict[str, Any]:
        """Generate execution summary"""
        successful = sum(1 for task in completed_tasks.values() if task.status == TaskStatus.COMPLETED)
        failed = sum(1 for task in completed_tasks.values() if task.status == TaskStatus.FAILED)
        
        return {
            'total_tasks': len(completed_tasks),
            'successful_tasks': successful,
            'failed_tasks': failed,
            'success_rate': (successful / len(completed_tasks)) * 100 if completed_tasks else 0,
            'task_details': {
                task_id: {
                    'status': task.status.value,
                    'step_type': task.step_type.value,
                    'agent': task.agent_name,
                    'duration': (task.completed_at - task.started_at).total_seconds() if task.completed_at and task.started_at else None,
                    'error': task.error_message
                }
                for task_id, task in completed_tasks.items()
            }
        }

# Factory function
def create_orchestrator() -> MultiAgentOrchestrator:
    """Create and return orchestrator instance"""
    return MultiAgentOrchestrator()
