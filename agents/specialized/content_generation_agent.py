"""
Content Generation Agent for EduLMS v2
Handles automated content creation, lesson planning, and educational material generation
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..communication.gemini_client import get_gemini_client
from ..communication.cache_manager import CacheManager
from ..base import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class ContentRequest:
    """Content generation request structure"""
    content_type: str  # lesson, quiz, assignment, summary, explanation
    topic: str
    difficulty_level: str = "intermediate"
    target_audience: str = "general"
    length: str = "medium"  # short, medium, long
    format: str = "text"  # text, markdown, html
    additional_requirements: Dict[str, Any] = None

@dataclass
class GeneratedContent:
    """Generated content structure"""
    content_type: str
    topic: str
    content: str
    metadata: Dict[str, Any]
    quality_score: float
    timestamp: datetime

class ContentGenerationAgent(BaseAgent):
    """
    Content Generation Agent for automated educational content creation
    
    Capabilities:
    - Lesson content generation
    - Quiz and assessment creation
    - Assignment and project generation
    - Educational summaries and explanations
    - Learning path content creation
    - Adaptive content based on learner profiles
    """
    
    def __init__(self, agent_id: str = "content_generation_agent"):
        super().__init__(agent_id)
        self.gemini_client = get_gemini_client()
        self.cache_manager = CacheManager()
        
        # Content templates and guidelines
        self.content_templates = {
            "lesson": {
                "structure": ["introduction", "main_content", "examples", "summary", "exercises"],
                "min_length": 500,
                "max_length": 2000
            },
            "quiz": {
                "question_types": ["multiple_choice", "true_false", "short_answer", "essay"],
                "min_questions": 3,
                "max_questions": 20
            },
            "assignment": {
                "components": ["objectives", "instructions", "requirements", "rubric"],
                "min_length": 200,
                "max_length": 1000
            },
            "summary": {
                "max_length": 500,
                "key_points": 5
            }
        }
        
        # Quality assessment criteria
        self.quality_criteria = {
            "clarity": "Content is clear and easy to understand",
            "accuracy": "Information is factually correct",
            "engagement": "Content is engaging and interactive",
            "structure": "Content is well-organized and structured",
            "relevance": "Content is relevant to learning objectives"
        }
    
    async def start(self):
        """Start the content generation agent"""
        logger.info(f"Starting Content Generation Agent {self.agent_id}")
        await super().start()
        
        while self.running:
            try:
                # Check for content generation requests
                messages = await self.get_messages("content_request")
                
                for message in messages:
                    await self.process_content_request(message)
                
                # Check for content enhancement requests
                enhancement_messages = await self.get_messages("enhance_content")
                
                for message in enhancement_messages:
                    await self.process_enhancement_request(message)
                
                # Check for bulk content generation requests
                bulk_messages = await self.get_messages("bulk_content_request")
                
                for message in bulk_messages:
                    await self.process_bulk_request(message)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in content generation agent loop: {e}")
                await asyncio.sleep(10)
    
    async def process_content_request(self, message: Dict[str, Any]):
        """Process individual content generation request"""
        try:
            data = message.get('data', {})
            request = ContentRequest(**data)
            
            logger.info(f"Processing content request: {request.content_type} on {request.topic}")
            
            # Check cache first
            cache_key = f"content_{request.content_type}_{hash(request.topic)}_{request.difficulty_level}"
            cached_content = await self.cache_manager.get(cache_key)
            
            if cached_content:
                logger.info("Returning cached content")
                await self.send_response(message, cached_content)
                return
            
            # Generate new content
            generated_content = await self.generate_content(request)
            
            # Cache the result
            await self.cache_manager.set(cache_key, generated_content.__dict__, ttl=3600)  # 1 hour
            
            # Send response
            await self.send_response(message, generated_content.__dict__)
            
            # Log activity
            await self.log_content_generation(request, generated_content)
            
        except Exception as e:
            logger.error(f"Error processing content request: {e}")
            await self.send_error_response(message, str(e))
    
    async def generate_content(self, request: ContentRequest) -> GeneratedContent:
        """Generate content based on request"""
        try:
            if request.content_type == "lesson":
                content = await self.generate_lesson_content(request)
            elif request.content_type == "quiz":
                content = await self.generate_quiz_content(request)
            elif request.content_type == "assignment":
                content = await self.generate_assignment_content(request)
            elif request.content_type == "summary":
                content = await self.generate_summary_content(request)
            elif request.content_type == "explanation":
                content = await self.generate_explanation_content(request)
            else:
                content = await self.generate_generic_content(request)
            
            # Assess content quality
            quality_score = await self.assess_content_quality(content, request)
            
            # Create metadata
            metadata = {
                "word_count": len(content.split()),
                "difficulty_level": request.difficulty_level,
                "target_audience": request.target_audience,
                "generation_method": "gemini_ai",
                "template_used": request.content_type
            }
            
            return GeneratedContent(
                content_type=request.content_type,
                topic=request.topic,
                content=content,
                metadata=metadata,
                quality_score=quality_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
    
    async def generate_lesson_content(self, request: ContentRequest) -> str:
        """Generate comprehensive lesson content"""
        try:
            template = self.content_templates["lesson"]
            
            lesson_prompt = f"""
            Create a comprehensive lesson on the topic: {request.topic}
            
            Requirements:
            - Difficulty level: {request.difficulty_level}
            - Target audience: {request.target_audience}
            - Length: {request.length}
            - Format: {request.format}
            
            Structure the lesson with these sections:
            1. Introduction - Hook the learner and explain why this topic matters
            2. Learning Objectives - Clear, measurable objectives
            3. Main Content - Core concepts with explanations
            4. Examples - Practical examples and use cases
            5. Interactive Elements - Questions or activities for engagement
            6. Summary - Key takeaways and review
            7. Next Steps - What to learn next or how to apply knowledge
            
            Make the content engaging, clear, and educational. Include practical examples.
            Word count should be between {template['min_length']} and {template['max_length']} words.
            """
            
            if request.additional_requirements:
                lesson_prompt += f"\nAdditional requirements: {json.dumps(request.additional_requirements)}"
            
            content = await self.gemini_client.generate_content(
                prompt=lesson_prompt,
                system_instruction="You are an expert educational content creator. Create engaging, well-structured lessons that promote active learning.",
                temperature=0.4,
                max_tokens=3000
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating lesson content: {e}")
            return f"Error generating lesson content for {request.topic}: {str(e)}"
    
    async def generate_quiz_content(self, request: ContentRequest) -> str:
        """Generate quiz content with various question types"""
        try:
            quiz_prompt = f"""
            Create a quiz on the topic: {request.topic}
            
            Requirements:
            - Difficulty level: {request.difficulty_level}
            - Target audience: {request.target_audience}
            - Include 5-10 questions of mixed types
            
            Question types to include:
            1. Multiple choice questions (with 4 options each)
            2. True/False questions
            3. Short answer questions
            4. One essay question (if appropriate)
            
            Format as JSON:
            {{
                "quiz_title": "Quiz title",
                "instructions": "Quiz instructions",
                "questions": [
                    {{
                        "id": 1,
                        "type": "multiple_choice",
                        "question": "Question text",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0,
                        "explanation": "Why this is correct"
                    }},
                    {{
                        "id": 2,
                        "type": "true_false",
                        "question": "Statement to evaluate",
                        "correct_answer": true,
                        "explanation": "Explanation"
                    }},
                    {{
                        "id": 3,
                        "type": "short_answer",
                        "question": "Question requiring brief response",
                        "sample_answer": "Expected answer",
                        "keywords": ["key", "terms"]
                    }}
                ]
            }}
            
            Make questions challenging but fair for the {request.difficulty_level} level.
            """
            
            content = await self.gemini_client.generate_content(
                prompt=quiz_prompt,
                system_instruction="You are an expert assessment creator. Create fair, challenging, and educational quiz questions.",
                temperature=0.3,
                max_tokens=2000
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating quiz content: {e}")
            return f"Error generating quiz for {request.topic}: {str(e)}"
    
    async def generate_assignment_content(self, request: ContentRequest) -> str:
        """Generate assignment content with clear instructions and rubric"""
        try:
            assignment_prompt = f"""
            Create an assignment on the topic: {request.topic}
            
            Requirements:
            - Difficulty level: {request.difficulty_level}
            - Target audience: {request.target_audience}
            - Length expectation: {request.length}
            
            Include these components:
            1. Assignment Title
            2. Learning Objectives
            3. Background/Context
            4. Detailed Instructions
            5. Requirements and Specifications
            6. Submission Guidelines
            7. Grading Rubric
            8. Resources and References
            
            Make the assignment practical and relevant to real-world applications.
            Provide clear evaluation criteria in the rubric.
            """
            
            content = await self.gemini_client.generate_content(
                prompt=assignment_prompt,
                system_instruction="You are an expert educator creating practical assignments that reinforce learning objectives.",
                temperature=0.4,
                max_tokens=2500
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating assignment content: {e}")
            return f"Error generating assignment for {request.topic}: {str(e)}"
    
    async def generate_summary_content(self, request: ContentRequest) -> str:
        """Generate concise summary content"""
        try:
            summary_prompt = f"""
            Create a comprehensive summary of the topic: {request.topic}
            
            Requirements:
            - Difficulty level: {request.difficulty_level}
            - Target audience: {request.target_audience}
            - Maximum 500 words
            
            Include:
            1. Key concepts and definitions
            2. Main points and principles
            3. Important relationships or connections
            4. Practical applications
            5. Key takeaways
            
            Make it concise but comprehensive, suitable for review or quick reference.
            """
            
            content = await self.gemini_client.generate_content(
                prompt=summary_prompt,
                system_instruction="You are an expert at creating clear, concise summaries that capture essential information.",
                temperature=0.3,
                max_tokens=800
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating summary content: {e}")
            return f"Error generating summary for {request.topic}: {str(e)}"
    
    async def generate_explanation_content(self, request: ContentRequest) -> str:
        """Generate detailed explanations of concepts"""
        try:
            explanation_prompt = f"""
            Provide a detailed explanation of: {request.topic}
            
            Requirements:
            - Difficulty level: {request.difficulty_level}
            - Target audience: {request.target_audience}
            - Use analogies and examples to clarify complex concepts
            
            Structure:
            1. Simple definition
            2. Detailed explanation
            3. Real-world examples
            4. Common misconceptions (if any)
            5. Related concepts
            6. Practical applications
            
            Make it accessible and easy to understand while being thorough.
            """
            
            content = await self.gemini_client.generate_content(
                prompt=explanation_prompt,
                system_instruction="You are an expert educator skilled at explaining complex concepts in simple, understandable terms.",
                temperature=0.4,
                max_tokens=2000
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating explanation content: {e}")
            return f"Error generating explanation for {request.topic}: {str(e)}"
    
    async def generate_generic_content(self, request: ContentRequest) -> str:
        """Generate generic educational content"""
        try:
            generic_prompt = f"""
            Create educational content about: {request.topic}
            
            Content type: {request.content_type}
            Difficulty level: {request.difficulty_level}
            Target audience: {request.target_audience}
            Length: {request.length}
            
            Make it educational, engaging, and appropriate for the specified audience and difficulty level.
            """
            
            content = await self.gemini_client.generate_content(
                prompt=generic_prompt,
                system_instruction="You are an educational content creator. Create helpful, accurate, and engaging educational material.",
                temperature=0.4,
                max_tokens=2000
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating generic content: {e}")
            return f"Error generating content for {request.topic}: {str(e)}"
    
    async def assess_content_quality(self, content: str, request: ContentRequest) -> float:
        """Assess the quality of generated content"""
        try:
            quality_prompt = f"""
            Assess the quality of this educational content on a scale of 0.0 to 1.0:
            
            Content: {content[:1000]}...
            
            Evaluate based on:
            1. Clarity and readability
            2. Accuracy and correctness
            3. Engagement and interest
            4. Structure and organization
            5. Relevance to topic: {request.topic}
            6. Appropriateness for {request.difficulty_level} level
            
            Provide a single decimal score between 0.0 and 1.0.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=quality_prompt,
                system_instruction="You are a content quality assessor. Provide objective quality scores.",
                temperature=0.1,
                max_tokens=50
            )
            
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
            except ValueError:
                return 0.7  # Default score if parsing fails
                
        except Exception as e:
            logger.error(f"Error assessing content quality: {e}")
            return 0.7  # Default score
    
    async def process_enhancement_request(self, message: Dict[str, Any]):
        """Process content enhancement request"""
        try:
            data = message.get('data', {})
            existing_content = data.get('content', '')
            enhancement_type = data.get('enhancement_type', 'improve')
            
            enhanced_content = await self.enhance_content(existing_content, enhancement_type)
            
            await self.send_response(message, {
                'original_content': existing_content,
                'enhanced_content': enhanced_content,
                'enhancement_type': enhancement_type,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing enhancement request: {e}")
            await self.send_error_response(message, str(e))
    
    async def enhance_content(self, content: str, enhancement_type: str) -> str:
        """Enhance existing content"""
        try:
            enhancement_prompts = {
                'improve': 'Improve the clarity, structure, and engagement of this content',
                'simplify': 'Simplify this content for easier understanding',
                'expand': 'Expand this content with more details and examples',
                'summarize': 'Create a concise summary of this content'
            }
            
            prompt = f"""
            {enhancement_prompts.get(enhancement_type, 'Improve this content')}:
            
            {content}
            
            Maintain the original meaning while making the requested improvements.
            """
            
            enhanced = await self.gemini_client.generate_content(
                prompt=prompt,
                system_instruction="You are a content editor skilled at improving educational materials.",
                temperature=0.3,
                max_tokens=2000
            )
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing content: {e}")
            return content  # Return original if enhancement fails
    
    async def process_bulk_request(self, message: Dict[str, Any]):
        """Process bulk content generation request"""
        try:
            data = message.get('data', {})
            topics = data.get('topics', [])
            content_type = data.get('content_type', 'lesson')
            
            results = []
            
            for topic in topics:
                request = ContentRequest(
                    content_type=content_type,
                    topic=topic,
                    difficulty_level=data.get('difficulty_level', 'intermediate'),
                    target_audience=data.get('target_audience', 'general')
                )
                
                try:
                    content = await self.generate_content(request)
                    results.append({
                        'topic': topic,
                        'status': 'success',
                        'content': content.__dict__
                    })
                except Exception as e:
                    results.append({
                        'topic': topic,
                        'status': 'error',
                        'error': str(e)
                    })
            
            await self.send_response(message, {
                'bulk_generation_results': results,
                'total_topics': len(topics),
                'successful': len([r for r in results if r['status'] == 'success']),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing bulk request: {e}")
            await self.send_error_response(message, str(e))
    
    async def log_content_generation(self, request: ContentRequest, content: GeneratedContent):
        """Log content generation activity"""
        try:
            activity_data = {
                'agent_id': self.agent_id,
                'activity_type': 'content_generated',
                'content_type': request.content_type,
                'topic': request.topic,
                'difficulty_level': request.difficulty_level,
                'quality_score': content.quality_score,
                'word_count': content.metadata.get('word_count', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.log_activity(activity_data)
            
        except Exception as e:
            logger.error(f"Error logging content generation: {e}")

# Agent factory function
def create_content_generation_agent() -> ContentGenerationAgent:
    """Create and return a Content Generation Agent instance"""
    return ContentGenerationAgent()
