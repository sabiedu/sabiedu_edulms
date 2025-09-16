"""
Learning Path Agent - Handles adaptive learning path recommendations and optimization
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..communication.tidb_service import TiDBCommunicationService
from ..communication.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

class LearningPathAgent:
    def __init__(self, agent_name: str = "LearningPathAgent"):
        self.agent_name = agent_name
        self.comm_service = TiDBCommunicationService()
        self.channel = "learning_path"
        self.gemini_client = get_gemini_client()
        
    async def start(self):
        """Start the learning path agent worker loop"""
        logger.info(f"{self.agent_name} starting...")
        
        while True:
            try:
                # Poll for learning path tasks
                messages = await self.comm_service.poll_messages(
                    channel=self.channel,
                    agent_name=self.agent_name,
                    limit=5
                )
                
                for message in messages:
                    await self.process_message(message)
                    
            except Exception as e:
                logger.error(f"{self.agent_name} error: {e}")
                await asyncio.sleep(5)
                
    async def process_message(self, message: Dict[str, Any]):
        """Process incoming learning path messages"""
        try:
            message_data = json.loads(message.get('message', '{}'))
            task_type = message_data.get('task_type')
            
            response = None
            
            if task_type == 'generate_path':
                response = await self.generate_learning_path(message_data)
            elif task_type == 'adapt_path':
                response = await self.adapt_learning_path(message_data)
            elif task_type == 'recommend_next':
                response = await self.recommend_next_lesson(message_data)
            elif task_type == 'analyze_progress':
                response = await self.analyze_progress(message_data)
            else:
                response = {
                    'error': f'Unknown task type: {task_type}',
                    'agent': self.agent_name
                }
            
            # Send response back
            if response:
                await self.comm_service.send_message(
                    channel=self.channel,
                    sender_agent=self.agent_name,
                    message=response,
                    recipient_agent=message.get('sender_agent', 'frontend')
                )
                
            # Mark message as processed
            await self.comm_service.mark_message_processed(
                message_id=message['id'],
                processing_agent=self.agent_name
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    async def generate_learning_path(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized learning path"""
        try:
            user_id = data.get('user_id')
            learning_goals = data.get('learning_goals', [])
            current_level = data.get('current_level', 'beginner')
            interests = data.get('interests', [])
            
            # Simple rule-based path generation
            recommended_courses = []
            
            # AI/ML focused path
            if any(goal.lower() in ['ai', 'machine learning', 'artificial intelligence'] for goal in learning_goals):
                recommended_courses.extend([
                    {
                        'course_id': 1,
                        'title': 'AI for Beginners: Agents and Prompting',
                        'priority': 1,
                        'reason': 'Foundational AI concepts and practical applications'
                    }
                ])
                
            # Programming focused path
            if any(goal.lower() in ['programming', 'coding', 'development'] for goal in learning_goals):
                recommended_courses.extend([
                    {
                        'course_id': 2,
                        'title': 'Python Programming Fundamentals',
                        'priority': 2,
                        'reason': 'Essential programming skills for AI development'
                    }
                ])
                
            # Data science path
            if any(goal.lower() in ['data', 'analytics', 'statistics'] for goal in learning_goals):
                recommended_courses.extend([
                    {
                        'course_id': 3,
                        'title': 'Data Analysis with Python',
                        'priority': 3,
                        'reason': 'Data manipulation and analysis skills'
                    }
                ])
                
            # Default path if no specific goals
            if not recommended_courses:
                recommended_courses.append({
                    'course_id': 1,
                    'title': 'AI for Beginners: Agents and Prompting',
                    'priority': 1,
                    'reason': 'Great starting point for AI learning'
                })
                
            # Generate learning milestones
            milestones = self.generate_milestones(recommended_courses, current_level)
            
            # Estimate timeline
            timeline = self.estimate_timeline(recommended_courses, current_level)
            
            return {
                'task_type': 'generate_path',
                'user_id': user_id,
                'recommended_courses': recommended_courses,
                'milestones': milestones,
                'timeline': timeline,
                'learning_goals': learning_goals,
                'current_level': current_level,
                'adaptation_strategy': self.get_adaptation_strategy(current_level),
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def adapt_learning_path(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt existing learning path based on progress"""
        try:
            user_id = data.get('user_id')
            current_progress = data.get('progress', {})
            performance_data = data.get('performance', {})
            struggling_areas = data.get('struggling_areas', [])
            
            adaptations = []
            
            # Check for struggling areas
            if struggling_areas:
                for area in struggling_areas:
                    adaptations.append({
                        'type': 'remedial_content',
                        'area': area,
                        'recommendation': f'Additional practice recommended for {area}',
                        'action': 'add_supplementary_lessons'
                    })
                    
            # Check progress speed
            avg_completion_time = performance_data.get('avg_completion_time', 0)
            if avg_completion_time > 0:
                if avg_completion_time < 0.5:  # Very fast
                    adaptations.append({
                        'type': 'acceleration',
                        'recommendation': 'Consider advanced content or skip basic concepts',
                        'action': 'suggest_advanced_track'
                    })
                elif avg_completion_time > 2.0:  # Very slow
                    adaptations.append({
                        'type': 'deceleration',
                        'recommendation': 'Break down content into smaller chunks',
                        'action': 'add_micro_lessons'
                    })
                    
            # Check engagement patterns
            engagement_score = performance_data.get('engagement_score', 0.5)
            if engagement_score < 0.3:
                adaptations.append({
                    'type': 'engagement',
                    'recommendation': 'Add more interactive content and gamification',
                    'action': 'increase_interactivity'
                })
                
            return {
                'task_type': 'adapt_path',
                'user_id': user_id,
                'adaptations': adaptations,
                'updated_timeline': self.adjust_timeline(performance_data),
                'next_actions': self.get_next_actions(adaptations),
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adapting learning path: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def recommend_next_lesson(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend the next best lesson for a user"""
        try:
            user_id = data.get('user_id')
            completed_lessons = data.get('completed_lessons', [])
            current_course_id = data.get('current_course_id')
            user_preferences = data.get('preferences', {})
            
            # Simple next lesson logic
            if current_course_id:
                # Find next lesson in current course
                next_lesson = self.get_next_lesson_in_course(current_course_id, completed_lessons)
                if next_lesson:
                    return {
                        'task_type': 'recommend_next',
                        'user_id': user_id,
                        'recommendation': next_lesson,
                        'reason': 'Continue current course progression',
                        'confidence': 0.9,
                        'agent': self.agent_name,
                        'timestamp': datetime.now().isoformat()
                    }
                    
            # Recommend based on learning style
            learning_style = user_preferences.get('learning_style', 'mixed')
            recommended_lesson = self.get_lesson_by_style(learning_style, completed_lessons)
            
            return {
                'task_type': 'recommend_next',
                'user_id': user_id,
                'recommendation': recommended_lesson,
                'reason': f'Matches your {learning_style} learning style',
                'confidence': 0.7,
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recommending next lesson: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def analyze_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's learning progress and provide insights"""
        try:
            user_id = data.get('user_id')
            progress_data = data.get('progress_data', [])
            time_period = data.get('time_period', 'week')
            
            # Calculate key metrics
            total_lessons = len(progress_data)
            completed_lessons = len([p for p in progress_data if p.get('completion_status') == 'completed'])
            avg_score = sum(p.get('score', 0) for p in progress_data) / max(total_lessons, 1)
            total_time_spent = sum(p.get('time_spent', 0) for p in progress_data)
            
            # Identify patterns
            strengths = []
            weaknesses = []
            
            # Analyze by lesson type
            lesson_types = {}
            for progress in progress_data:
                lesson_type = progress.get('lesson_type', 'unknown')
                if lesson_type not in lesson_types:
                    lesson_types[lesson_type] = {'scores': [], 'times': []}
                lesson_types[lesson_type]['scores'].append(progress.get('score', 0))
                lesson_types[lesson_type]['times'].append(progress.get('time_spent', 0))
                
            for lesson_type, data in lesson_types.items():
                avg_type_score = sum(data['scores']) / len(data['scores'])
                if avg_type_score > 80:
                    strengths.append(f"Excels at {lesson_type} content")
                elif avg_type_score < 60:
                    weaknesses.append(f"Struggles with {lesson_type} content")
                    
            # Generate recommendations
            recommendations = []
            if avg_score < 70:
                recommendations.append("Consider reviewing fundamental concepts before proceeding")
            if total_time_spent / max(total_lessons, 1) > 30:
                recommendations.append("Try breaking study sessions into shorter, focused intervals")
            if completed_lessons / max(total_lessons, 1) < 0.5:
                recommendations.append("Set daily learning goals to maintain consistent progress")
                
            return {
                'task_type': 'analyze_progress',
                'user_id': user_id,
                'metrics': {
                    'completion_rate': completed_lessons / max(total_lessons, 1),
                    'average_score': avg_score,
                    'total_time_spent': total_time_spent,
                    'lessons_per_day': total_lessons / 7 if time_period == 'week' else total_lessons / 30
                },
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendations': recommendations,
                'learning_velocity': self.calculate_learning_velocity(progress_data),
                'predicted_completion': self.predict_completion_time(progress_data),
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing progress: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    def generate_milestones(self, courses: List[Dict], level: str) -> List[Dict]:
        """Generate learning milestones"""
        milestones = []
        
        for i, course in enumerate(courses):
            milestones.append({
                'id': f'milestone_{i+1}',
                'title': f'Complete {course["title"]}',
                'description': f'Master the concepts in {course["title"]}',
                'target_date': f'{(i+1)*4} weeks',
                'skills': ['problem_solving', 'critical_thinking'],
                'prerequisites': milestones[-1]['id'] if milestones else None
            })
            
        return milestones
        
    def estimate_timeline(self, courses: List[Dict], level: str) -> Dict[str, Any]:
        """Estimate learning timeline"""
        base_hours_per_course = {'beginner': 20, 'intermediate': 15, 'advanced': 10}
        hours_per_course = base_hours_per_course.get(level, 20)
        
        total_hours = len(courses) * hours_per_course
        weeks = total_hours // 5  # Assuming 5 hours per week
        
        return {
            'total_hours': total_hours,
            'estimated_weeks': weeks,
            'hours_per_week': 5,
            'completion_date': f'{weeks} weeks from start'
        }
        
    def get_adaptation_strategy(self, level: str) -> Dict[str, Any]:
        """Get adaptation strategy based on level"""
        strategies = {
            'beginner': {
                'pace': 'slow',
                'repetition': 'high',
                'examples': 'many',
                'feedback_frequency': 'immediate'
            },
            'intermediate': {
                'pace': 'moderate',
                'repetition': 'medium',
                'examples': 'some',
                'feedback_frequency': 'regular'
            },
            'advanced': {
                'pace': 'fast',
                'repetition': 'low',
                'examples': 'few',
                'feedback_frequency': 'periodic'
            }
        }
        
        return strategies.get(level, strategies['beginner'])
        
    def get_next_lesson_in_course(self, course_id: int, completed_lessons: List[int]) -> Optional[Dict]:
        """Get next lesson in a course"""
        # Mock lesson data - in real implementation, query database
        course_lessons = {
            1: [
                {'id': 1, 'title': 'Welcome and Course Overview', 'order': 1},
                {'id': 2, 'title': 'What is an LLM?', 'order': 2},
                {'id': 3, 'title': 'Prompting Basics', 'order': 3},
                {'id': 4, 'title': 'Hands-on: Talk to the Tutor Agent', 'order': 4},
                {'id': 5, 'title': 'Quiz: Prompting Essentials', 'order': 5}
            ]
        }
        
        lessons = course_lessons.get(course_id, [])
        for lesson in lessons:
            if lesson['id'] not in completed_lessons:
                return lesson
                
        return None
        
    def get_lesson_by_style(self, learning_style: str, completed_lessons: List[int]) -> Dict:
        """Get lesson recommendation based on learning style"""
        style_preferences = {
            'visual': {'type': 'video', 'title': 'Visual Learning: Diagrams and Charts'},
            'auditory': {'type': 'audio', 'title': 'Audio Lesson: Listen and Learn'},
            'kinesthetic': {'type': 'interactive', 'title': 'Hands-on Practice Session'},
            'mixed': {'type': 'text', 'title': 'Comprehensive Text Lesson'}
        }
        
        return style_preferences.get(learning_style, style_preferences['mixed'])
        
    def adjust_timeline(self, performance_data: Dict) -> Dict:
        """Adjust timeline based on performance"""
        base_weeks = 8
        performance_factor = performance_data.get('avg_completion_time', 1.0)
        
        adjusted_weeks = int(base_weeks * performance_factor)
        
        return {
            'original_weeks': base_weeks,
            'adjusted_weeks': adjusted_weeks,
            'adjustment_reason': 'Based on current learning pace'
        }
        
    def get_next_actions(self, adaptations: List[Dict]) -> List[str]:
        """Get next actions based on adaptations"""
        actions = []
        
        for adaptation in adaptations:
            if adaptation['type'] == 'remedial_content':
                actions.append(f"Review {adaptation['area']} concepts")
            elif adaptation['type'] == 'acceleration':
                actions.append("Consider advanced topics")
            elif adaptation['type'] == 'engagement':
                actions.append("Try interactive exercises")
                
        return actions
        
    def calculate_learning_velocity(self, progress_data: List[Dict]) -> float:
        """Calculate learning velocity (lessons per day)"""
        if not progress_data:
            return 0.0
            
        # Simple calculation based on recent progress
        completed_count = len([p for p in progress_data if p.get('completion_status') == 'completed'])
        days = 7  # Assume week period
        
        return completed_count / days
        
    def predict_completion_time(self, progress_data: List[Dict]) -> str:
        """Predict when user will complete current path"""
        velocity = self.calculate_learning_velocity(progress_data)
        remaining_lessons = len([p for p in progress_data if p.get('completion_status') != 'completed'])
        
        if velocity > 0:
            days_remaining = remaining_lessons / velocity
            return f"{int(days_remaining)} days"
        else:
            return "Unable to predict"

# Worker function for running the agent
async def run_learning_path_agent():
    """Run the Learning Path Agent worker"""
    import asyncio
    
    agent = LearningPathAgent()
    await agent.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_learning_path_agent())
