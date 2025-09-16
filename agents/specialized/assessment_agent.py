"""
Assessment Agent - Handles quiz/assignment grading and evaluation
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..communication.tidb_service import TiDBCommunicationService
from ..communication.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

class AssessmentAgent:
    def __init__(self, agent_name: str = "AssessmentAgent"):
        self.agent_name = agent_name
        self.comm_service = TiDBCommunicationService()
        self.channel = "assessment"
        self.gemini_client = get_gemini_client()
        
    async def start(self):
        """Start the assessment agent worker loop"""
        logger.info(f"{self.agent_name} starting...")
        
        while True:
            try:
                # Poll for assessment tasks
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
        """Process incoming assessment messages"""
        try:
            message_data = json.loads(message.get('message', '{}'))
            task_type = message_data.get('task_type')
            
            response = None
            
            if task_type == 'grade_quiz':
                response = await self.grade_quiz(message_data)
            elif task_type == 'grade_assignment':
                response = await self.grade_assignment(message_data)
            elif task_type == 'generate_feedback':
                response = await self.generate_feedback(message_data)
            elif task_type == 'create_quiz':
                response = await self.create_quiz(message_data)
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
            
    async def grade_quiz(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a quiz submission"""
        try:
            assessment_id = data.get('assessment_id')
            user_answers = data.get('answers', {})
            
            # Get assessment details from database
            assessment = await self.get_assessment(assessment_id)
            if not assessment:
                return {'error': 'Assessment not found'}
                
            questions = json.loads(assessment.get('questions', '[]'))
            total_questions = len(questions)
            correct_answers = 0
            detailed_results = []
            
            for question in questions:
                q_id = question.get('id')
                correct_answer = question.get('answer')
                user_answer = user_answers.get(q_id)
                
                is_correct = False
                if question.get('type') == 'mcq':
                    is_correct = user_answer == correct_answer
                elif question.get('type') == 'short':
                    # Simple keyword matching for short answers
                    is_correct = self.evaluate_short_answer(user_answer, correct_answer)
                    
                if is_correct:
                    correct_answers += 1
                    
                detailed_results.append({
                    'question_id': q_id,
                    'question': question.get('prompt'),
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'feedback': self.generate_question_feedback(question, user_answer, is_correct)
                })
            
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            grade = self.calculate_letter_grade(score)
            
            return {
                'task_type': 'grade_quiz',
                'assessment_id': assessment_id,
                'score': score,
                'grade': grade,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'detailed_results': detailed_results,
                'overall_feedback': self.generate_overall_feedback(score, grade),
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error grading quiz: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def grade_assignment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Grade an assignment submission"""
        try:
            assessment_id = data.get('assessment_id')
            submission_text = data.get('submission_text', '')
            
            # Get assessment details
            assessment = await self.get_assessment(assessment_id)
            if not assessment:
                return {'error': 'Assessment not found'}
                
            rubric = json.loads(assessment.get('rubric', '{}'))
            
            # Simple rule-based grading
            score_breakdown = {}
            total_score = 0
            max_score = rubric.get('total', 5)
            
            # Length check
            word_count = len(submission_text.split())
            if word_count >= 50:
                score_breakdown['completeness'] = 2
            elif word_count >= 25:
                score_breakdown['completeness'] = 1
            else:
                score_breakdown['completeness'] = 0
                
            # Keyword relevance check
            keywords = ['AI', 'tutor', 'agent', 'learning', 'study', 'plan']
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in submission_text.lower())
            score_breakdown['relevance'] = min(2, keyword_matches // 2)
            
            # Structure check (bullet points, organization)
            if '•' in submission_text or '-' in submission_text or any(str(i) in submission_text for i in range(1, 6)):
                score_breakdown['structure'] = 1
            else:
                score_breakdown['structure'] = 0
                
            total_score = sum(score_breakdown.values())
            percentage = (total_score / max_score) * 100
            grade = self.calculate_letter_grade(percentage)
            
            return {
                'task_type': 'grade_assignment',
                'assessment_id': assessment_id,
                'score': total_score,
                'max_score': max_score,
                'percentage': percentage,
                'grade': grade,
                'score_breakdown': score_breakdown,
                'feedback': self.generate_assignment_feedback(score_breakdown, submission_text),
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error grading assignment: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def generate_feedback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed feedback for submissions"""
        try:
            feedback_type = data.get('feedback_type', 'general')
            score = data.get('score', 0)
            
            if feedback_type == 'quiz':
                feedback = self.generate_quiz_feedback(score)
            elif feedback_type == 'assignment':
                feedback = self.generate_assignment_feedback_detailed(data)
            else:
                feedback = "Good effort! Keep practicing to improve your understanding."
                
            return {
                'task_type': 'generate_feedback',
                'feedback': feedback,
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def create_quiz(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a quiz based on lesson content using Gemini AI"""
        try:
            lesson_content = data.get('lesson_content', '')
            difficulty = data.get('difficulty', 'beginner')
            num_questions = data.get('num_questions', 3)
            
            # Use Gemini to generate quiz questions
            quiz_prompt = f"""
            Create a quiz with {num_questions} questions based on the following lesson content.
            Difficulty level: {difficulty}
            
            Lesson Content:
            {lesson_content}
            
            Generate questions in this JSON format:
            {{
                "questions": [
                    {{
                        "id": "q1",
                        "type": "mcq",
                        "prompt": "Question text here?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "answer": 0
                    }},
                    {{
                        "id": "q2",
                        "type": "short",
                        "prompt": "Short answer question?",
                        "answer": "expected answer keywords"
                    }}
                ]
            }}
            
            Mix multiple choice and short answer questions. Make questions relevant to the content.
            """
            
            try:
                response = await self.gemini_client.generate_content(
                    prompt=quiz_prompt,
                    system_instruction="You are an expert quiz creator. Generate educational quiz questions based on lesson content.",
                    temperature=0.3,
                    max_tokens=1500
                )
                
                # Parse the JSON response
                quiz_data = json.loads(response)
                questions = quiz_data.get('questions', [])
                
            except Exception as e:
                logger.warning(f"Gemini quiz generation failed, using fallback: {e}")
                # Fallback to simple rule-based generation
                questions = self._generate_fallback_quiz(lesson_content, num_questions)
                
            return {
                'task_type': 'create_quiz',
                'questions': questions[:num_questions],
                'difficulty': difficulty,
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating quiz: {e}")
            return {'error': str(e), 'agent': self.agent_name}
    
    def _generate_fallback_quiz(self, lesson_content: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate fallback quiz questions when Gemini is unavailable"""
        questions = []
        
        if 'LLM' in lesson_content or 'language model' in lesson_content.lower():
            questions.append({
                'id': 'q1',
                'type': 'mcq',
                'prompt': 'What does LLM stand for?',
                'options': [
                    'Large Language Model',
                    'Linear Learning Machine',
                    'Logical Language Method',
                    'Limited Learning Model'
                ],
                'answer': 0
            })
            
        if 'prompt' in lesson_content.lower():
            questions.append({
                'id': 'q2',
                'type': 'mcq',
                'prompt': 'Which of the following makes a good prompt?',
                'options': [
                    'Vague and short',
                    'Clear and specific',
                    'Very long and complex',
                    'Contains no context'
                ],
                'answer': 1
            })
            
        # Fill remaining questions with generic ones if needed
        while len(questions) < num_questions:
            questions.append({
                'id': f'q{len(questions) + 1}',
                'type': 'mcq',
                'prompt': 'What is the main goal of this lesson?',
                'options': [
                    'To learn new concepts',
                    'To waste time',
                    'To confuse students',
                    'To skip content'
                ],
                'answer': 0
            })
            
        return questions
            
    def evaluate_short_answer(self, user_answer: str, expected_keywords: str) -> bool:
        """Simple keyword-based evaluation for short answers"""
        if not user_answer or not expected_keywords:
            return False
            
        user_words = user_answer.lower().split()
        expected_words = expected_keywords.lower().split()
        
        # Check if any expected keywords are present
        return any(word in user_words for word in expected_words)
        
    def calculate_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
            
    def generate_question_feedback(self, question: Dict, user_answer: Any, is_correct: bool) -> str:
        """Generate feedback for individual questions"""
        if is_correct:
            return "Correct! Well done."
        else:
            if question.get('type') == 'mcq':
                return f"Incorrect. The correct answer is: {question.get('options', [])[question.get('answer', 0)]}"
            else:
                return "Incorrect. Please review the lesson content and try to include key concepts."
                
    def generate_overall_feedback(self, score: float, grade: str) -> str:
        """Generate overall feedback for quiz"""
        if score >= 90:
            return "Excellent work! You have a strong understanding of the material."
        elif score >= 80:
            return "Good job! You understand most of the concepts well."
        elif score >= 70:
            return "Fair performance. Consider reviewing the material to strengthen your understanding."
        elif score >= 60:
            return "You're making progress, but there's room for improvement. Review the lesson and try again."
        else:
            return "Please review the lesson material carefully and consider asking the AI tutor for help."
            
    def generate_assignment_feedback(self, score_breakdown: Dict, submission_text: str) -> str:
        """Generate feedback for assignments"""
        feedback_parts = []
        
        if score_breakdown.get('completeness', 0) < 2:
            feedback_parts.append("Consider providing more detailed responses to fully address the assignment requirements.")
            
        if score_breakdown.get('relevance', 0) < 2:
            feedback_parts.append("Try to include more relevant concepts and keywords from the lesson material.")
            
        if score_breakdown.get('structure', 0) < 1:
            feedback_parts.append("Organize your response using bullet points or numbered lists for better clarity.")
            
        if not feedback_parts:
            feedback_parts.append("Great work! Your response demonstrates good understanding and organization.")
            
        return " ".join(feedback_parts)
        
    async def get_assessment(self, assessment_id: str) -> Optional[Dict]:
        """Get assessment details from database"""
        try:
            # This would typically query the database
            # For now, return a mock assessment
            return {
                'id': assessment_id,
                'questions': json.dumps([
                    {
                        'id': 'q1',
                        'type': 'mcq',
                        'prompt': 'Sample question?',
                        'options': ['A', 'B', 'C', 'D'],
                        'answer': 1
                    }
                ]),
                'rubric': json.dumps({'total': 5})
            }
        except Exception as e:
            logger.error(f"Error getting assessment: {e}")
            return None

# Worker function for running the agent
async def run_assessment_agent():
    """Run the Assessment Agent worker"""
    import asyncio
    
    agent = AssessmentAgent()
    await agent.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_assessment_agent())
