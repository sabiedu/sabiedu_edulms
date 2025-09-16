#!/usr/bin/env python3
"""
Agent Service for Multi-Agent Communication and Workflow Execution
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from pathlib import Path

class AgentService:
    def __init__(self):
        self.agents_path = Path(__file__).parent.parent.parent / "agents"
        self.api_bridge_path = self.agents_path / "api_bridge.py"
        
    async def execute_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action via Python subprocess"""
        try:
            # Prepare command
            cmd = [
                "python",
                str(self.api_bridge_path),
                "--action", action,
                "--data", json.dumps(data)
            ]
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.agents_path)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0
            )
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                return {
                    "success": True,
                    "result": result,
                    "action": action
                }
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return {
                    "success": False,
                    "error": error_msg,
                    "action": action
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Agent execution timeout",
                "action": action
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": action
            }
    
    async def execute_workflow(self, workflow_id: int, template_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow by orchestrating multiple agents"""
        
        workflow_actions = {
            "adaptive_learning_pipeline": [
                ("analytics_query", {"query_type": "user_performance", "user_id": parameters.get("user_id")}),
                ("update_personalization", {"user_id": parameters.get("user_id"), "learning_data": parameters}),
                ("generate_content", {"topic": "adaptive_content", "difficulty_level": "adaptive"})
            ],
            "content_discovery_workflow": [
                ("research_query", {"query": parameters.get("topic", ""), "research_type": "academic_search"}),
                ("generate_content", {"topic": parameters.get("topic", ""), "difficulty": parameters.get("difficulty", "intermediate")})
            ],
            "assessment_generation_workflow": [
                ("create_quiz", {"lesson_content": parameters.get("content", ""), "difficulty": parameters.get("difficulty", "intermediate")}),
                ("generate_content", {"content_type": "assessment", "topic": parameters.get("topic", "")})
            ],
            "research_to_content_workflow": [
                ("research_query", {"query": parameters.get("research_query", ""), "depth": "comprehensive"}),
                ("generate_content", {"topic": parameters.get("research_query", ""), "target_audience": parameters.get("target_audience", "general")})
            ],
            "personalized_study_plan": [
                ("analytics_query", {"query_type": "learning_patterns", "user_id": parameters.get("user_id")}),
                ("update_personalization", {"user_id": parameters.get("user_id"), "learning_goals": parameters.get("learning_goals", [])})
            ]
        }
        
        actions = workflow_actions.get(template_name, [])
        results = []
        
        for action, action_data in actions:
            result = await self.execute_action(action, action_data)
            results.append({
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "result": result
            })
            
            # Short delay between actions
            await asyncio.sleep(1)
        
        return {
            "workflow_id": workflow_id,
            "template_name": template_name,
            "results": results,
            "completed_at": datetime.utcnow().isoformat()
        }
    
    async def process_message(
        self, 
        session_id: str, 
        message: str, 
        agent_type: Optional[str] = None,
        user_id: int = None,
        context_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process message through appropriate agent"""
        
        # Determine agent action based on message content and agent type
        if agent_type == "tutor" or "help" in message.lower() or "explain" in message.lower():
            action = "send_message"
            data = {
                "channel": f"session_{session_id}",
                "sender_agent": "tutor-agent",
                "message": message,
                "user_id": user_id,
                "context": context_data
            }
        elif agent_type == "research" or "research" in message.lower() or "find" in message.lower():
            action = "research_query"
            data = {
                "query": message,
                "research_type": "academic_search",
                "user_id": user_id
            }
        elif agent_type == "assessment" or "quiz" in message.lower() or "test" in message.lower():
            action = "create_quiz"
            data = {
                "lesson_content": message,
                "difficulty": "intermediate",
                "num_questions": 5
            }
        else:
            # Default to general agent communication
            action = "send_message"
            data = {
                "channel": f"session_{session_id}",
                "sender_agent": "general-agent",
                "message": message,
                "user_id": user_id
            }
        
        result = await self.execute_action(action, data)
        
        return {
            "message": result.get("result", {}).get("response", "I'm processing your request..."),
            "agent_type": agent_type or "general",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "action": action,
                "success": result.get("success", False)
            }
        }
    
    async def get_workflow_logs(self, workflow_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get workflow execution logs"""
        
        # In a real implementation, this would fetch from a logging system
        # For now, return mock logs
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": f"Workflow {workflow_id} execution started",
                "agent": "orchestrator"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO", 
                "message": "Agent communication established",
                "agent": "system"
            }
        ]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get agent system status"""
        
        # Check agent system health
        status_result = await self.execute_action("get_status", {})
        
        if status_result.get("success"):
            return status_result.get("result", {})
        else:
            return {
                "agents_active": 0,
                "tidb_connected": False,
                "gemini_connected": False,
                "last_updated": datetime.utcnow().isoformat(),
                "error": status_result.get("error")
            }
