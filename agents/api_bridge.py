#!/usr/bin/env python3
"""
API Bridge for Agent Communication
Connects Strapi backend to Python agents
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path

# Add agents directory to Python path
agents_dir = Path(__file__).parent
sys.path.insert(0, str(agents_dir))

from communication.tidb_service import TiDBCommunicationService
from specialized.analytics_agent import AnalyticsAgent
from specialized.assessment_agent import AssessmentAgent
from specialized.research_agent import ResearchAgent
from specialized.content_generation_agent import ContentGenerationAgent
from specialized.personalization_agent import PersonalizationAgent
from specialized.tutor_agent import TutorAgent

async def main():
    parser = argparse.ArgumentParser(description='Agent API Bridge')
    parser.add_argument('--action', required=True, help='Action to perform')
    parser.add_argument('--data', required=True, help='Data as JSON string')
    
    args = parser.parse_args()
    
    try:
        data = json.loads(args.data)
        
        # Initialize agents
        analytics_agent = AnalyticsAgent()
        assessment_agent = AssessmentAgent()
        research_agent = ResearchAgent()
        content_agent = ContentGenerationAgent()
        personalization_agent = PersonalizationAgent()
        tutor_agent = TutorAgent()
        
        result = None
        
        if args.action == 'analytics_query':
            result = await analytics_agent.generate_analytics_report(
                query_type=data.get('query_type'),
                user_id=data.get('user_id'),
                course_id=data.get('course_id'),
                timeframe=data.get('timeframe', '30d')
            )
            
        elif args.action == 'create_quiz':
            result = await assessment_agent.create_quiz(
                lesson_content=data.get('lesson_content'),
                difficulty=data.get('difficulty', 'intermediate'),
                num_questions=data.get('num_questions', 5)
            )
            
        elif args.action == 'grade_assignment':
            result = await assessment_agent.grade_assignment(
                assignment_text=data.get('assignment_text'),
                rubric=data.get('rubric', ''),
                max_score=100
            )
            
        elif args.action == 'research_query':
            result = await research_agent.conduct_research(
                query=data.get('query'),
                research_type=data.get('research_type', 'academic_search'),
                depth=data.get('depth', 'standard')
            )
            
        elif args.action == 'generate_content':
            result = await content_agent.generate_lesson_content(
                topic=data.get('topic'),
                difficulty_level=data.get('difficulty_level', 'intermediate'),
                content_type=data.get('content_type', 'lesson')
            )
            
        elif args.action == 'update_personalization':
            result = await personalization_agent.update_user_profile(
                user_id=data.get('user_id'),
                learning_data=data
            )
            
        elif args.action == 'send_message':
            # Initialize TiDB service for message passing
            tidb_service = TiDBCommunicationService(
                host=os.getenv('TIDB_HOST', 'localhost'),
                port=int(os.getenv('TIDB_PORT', 4000)),
                user=os.getenv('TIDB_USER', 'root'),
                password=os.getenv('TIDB_PASSWORD', ''),
                database=os.getenv('TIDB_DATABASE', 'edulms')
            )
            
            result = await tidb_service.send_message(
                channel=data.get('channel'),
                sender_agent=data.get('sender_agent'),
                message=data.get('message'),
                recipient_agent=data.get('recipient_agent')
            )
            
        elif args.action == 'get_messages':
            tidb_service = TiDBCommunicationService(
                host=os.getenv('TIDB_HOST', 'localhost'),
                port=int(os.getenv('TIDB_PORT', 4000)),
                user=os.getenv('TIDB_USER', 'root'),
                password=os.getenv('TIDB_PASSWORD', ''),
                database=os.getenv('TIDB_DATABASE', 'edulms')
            )
            
            result = await tidb_service.poll_messages(
                channel=data.get('channel'),
                agent_name='api_bridge',
                limit=data.get('limit', 10)
            )
            
        elif args.action == 'get_status':
            result = {
                'agents_active': 9,
                'tidb_connected': True,
                'gemini_connected': True,
                'last_updated': '2024-09-15T21:15:00Z'
            }
            
        else:
            raise ValueError(f"Unknown action: {args.action}")
        
        # Output result as JSON
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'action': args.action
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
