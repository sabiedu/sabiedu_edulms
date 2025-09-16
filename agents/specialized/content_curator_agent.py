"""
Content Curator Agent - Handles content discovery, quality assessment, and recommendations
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..communication.tidb_service import TiDBCommunicationService
from ..communication.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

class ContentCuratorAgent:
    def __init__(self, agent_name: str = "ContentCuratorAgent"):
        self.agent_name = agent_name
        self.comm_service = TiDBCommunicationService()
        self.channel = "content_curation"
        self.gemini_client = get_gemini_client()
        
    async def start(self):
        """Start the content curator agent worker loop"""
        logger.info(f"{self.agent_name} starting...")
        
        while True:
            try:
                # Poll for content curation tasks
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
        """Process incoming content curation messages"""
        try:
            message_data = json.loads(message.get('message', '{}'))
            task_type = message_data.get('task_type')
            
            response = None
            
            if task_type == 'search_content':
                response = await self.search_content(message_data)
            elif task_type == 'assess_quality':
                response = await self.assess_content_quality(message_data)
            elif task_type == 'recommend_content':
                response = await self.recommend_content(message_data)
            elif task_type == 'generate_metadata':
                response = await self.generate_content_metadata(message_data)
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
            
    async def search_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for relevant content based on criteria"""
        try:
            query = data.get('query', '')
            content_type = data.get('content_type', 'any')
            difficulty_level = data.get('difficulty_level', 'any')
            learning_style = data.get('learning_style', 'any')
            
            # Mock content search results
            search_results = []
            
            # AI/ML content
            if any(term in query.lower() for term in ['ai', 'artificial intelligence', 'machine learning', 'llm']):
                search_results.extend([
                    {
                        'id': 'content_1',
                        'title': 'Introduction to Large Language Models',
                        'type': 'video',
                        'difficulty': 'beginner',
                        'duration': 15,
                        'quality_score': 4.5,
                        'tags': ['ai', 'llm', 'basics'],
                        'description': 'Comprehensive introduction to LLMs and their applications',
                        'relevance_score': 0.95
                    },
                    {
                        'id': 'content_2',
                        'title': 'Prompt Engineering Best Practices',
                        'type': 'text',
                        'difficulty': 'intermediate',
                        'duration': 20,
                        'quality_score': 4.7,
                        'tags': ['prompting', 'ai', 'best-practices'],
                        'description': 'Advanced techniques for effective prompt engineering',
                        'relevance_score': 0.88
                    }
                ])
                
            # Programming content
            if any(term in query.lower() for term in ['programming', 'coding', 'python', 'javascript']):
                search_results.extend([
                    {
                        'id': 'content_3',
                        'title': 'Python Fundamentals for AI',
                        'type': 'interactive',
                        'difficulty': 'beginner',
                        'duration': 30,
                        'quality_score': 4.3,
                        'tags': ['python', 'programming', 'ai'],
                        'description': 'Learn Python programming with AI applications',
                        'relevance_score': 0.82
                    }
                ])
                
            # Data science content
            if any(term in query.lower() for term in ['data', 'analytics', 'statistics', 'visualization']):
                search_results.extend([
                    {
                        'id': 'content_4',
                        'title': 'Data Visualization with Python',
                        'type': 'video',
                        'difficulty': 'intermediate',
                        'duration': 25,
                        'quality_score': 4.4,
                        'tags': ['data', 'visualization', 'python'],
                        'description': 'Create compelling data visualizations',
                        'relevance_score': 0.79
                    }
                ])
                
            # Filter by criteria
            filtered_results = self.filter_content(search_results, content_type, difficulty_level, learning_style)
            
            # Sort by relevance
            filtered_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return {
                'task_type': 'search_content',
                'query': query,
                'results': filtered_results[:10],  # Top 10 results
                'total_found': len(search_results),
                'filtered_count': len(filtered_results),
                'search_metadata': {
                    'content_type': content_type,
                    'difficulty_level': difficulty_level,
                    'learning_style': learning_style
                },
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def assess_content_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of content"""
        try:
            content_id = data.get('content_id')
            content_text = data.get('content_text', '')
            content_metadata = data.get('metadata', {})
            
            # Quality assessment criteria
            quality_scores = {}
            
            # Content length assessment
            word_count = len(content_text.split())
            if word_count > 500:
                quality_scores['completeness'] = 0.9
            elif word_count > 200:
                quality_scores['completeness'] = 0.7
            else:
                quality_scores['completeness'] = 0.4
                
            # Technical accuracy (keyword-based)
            technical_keywords = ['algorithm', 'data', 'model', 'analysis', 'implementation']
            keyword_count = sum(1 for keyword in technical_keywords if keyword in content_text.lower())
            quality_scores['technical_accuracy'] = min(1.0, keyword_count / 3)
            
            # Clarity and readability
            sentences = content_text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            if avg_sentence_length < 20:
                quality_scores['clarity'] = 0.9
            elif avg_sentence_length < 30:
                quality_scores['clarity'] = 0.7
            else:
                quality_scores['clarity'] = 0.5
                
            # Educational value
            educational_indicators = ['example', 'practice', 'exercise', 'learn', 'understand']
            edu_score = sum(1 for indicator in educational_indicators if indicator in content_text.lower())
            quality_scores['educational_value'] = min(1.0, edu_score / 3)
            
            # Structure and organization
            structure_indicators = ['introduction', 'conclusion', 'step', 'section', 'chapter']
            structure_score = sum(1 for indicator in structure_indicators if indicator in content_text.lower())
            quality_scores['structure'] = min(1.0, structure_score / 2)
            
            # Overall quality score
            overall_score = sum(quality_scores.values()) / len(quality_scores)
            
            # Generate recommendations
            recommendations = []
            if quality_scores['completeness'] < 0.6:
                recommendations.append("Consider expanding content with more detailed explanations")
            if quality_scores['technical_accuracy'] < 0.6:
                recommendations.append("Add more technical details and examples")
            if quality_scores['clarity'] < 0.6:
                recommendations.append("Simplify sentence structure for better readability")
            if quality_scores['educational_value'] < 0.6:
                recommendations.append("Include more practical examples and exercises")
            if quality_scores['structure'] < 0.6:
                recommendations.append("Improve content organization with clear sections")
                
            return {
                'task_type': 'assess_quality',
                'content_id': content_id,
                'overall_score': overall_score,
                'detailed_scores': quality_scores,
                'grade': self.score_to_grade(overall_score),
                'recommendations': recommendations,
                'assessment_criteria': {
                    'completeness': 'Content depth and coverage',
                    'technical_accuracy': 'Technical correctness and precision',
                    'clarity': 'Readability and comprehension',
                    'educational_value': 'Learning effectiveness',
                    'structure': 'Organization and flow'
                },
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def recommend_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend content based on user profile and learning goals"""
        try:
            user_id = data.get('user_id')
            learning_goals = data.get('learning_goals', [])
            current_level = data.get('current_level', 'beginner')
            completed_content = data.get('completed_content', [])
            learning_style = data.get('learning_style', 'mixed')
            
            # Generate recommendations based on goals and level
            recommendations = []
            
            # AI/ML recommendations
            if any('ai' in goal.lower() or 'machine learning' in goal.lower() for goal in learning_goals):
                ai_content = [
                    {
                        'id': 'rec_1',
                        'title': 'Neural Networks Fundamentals',
                        'type': 'video',
                        'difficulty': current_level,
                        'match_score': 0.92,
                        'reason': 'Matches your AI learning goals',
                        'prerequisites': ['basic_math', 'python_basics'],
                        'estimated_time': 45
                    },
                    {
                        'id': 'rec_2',
                        'title': 'Hands-on Machine Learning Projects',
                        'type': 'interactive',
                        'difficulty': current_level,
                        'match_score': 0.88,
                        'reason': 'Practical application of ML concepts',
                        'prerequisites': ['python_intermediate'],
                        'estimated_time': 60
                    }
                ]
                recommendations.extend(ai_content)
                
            # Programming recommendations
            if any('programming' in goal.lower() or 'coding' in goal.lower() for goal in learning_goals):
                prog_content = [
                    {
                        'id': 'rec_3',
                        'title': 'Advanced Python Techniques',
                        'type': 'text',
                        'difficulty': 'intermediate',
                        'match_score': 0.85,
                        'reason': 'Builds on your programming foundation',
                        'prerequisites': ['python_basics'],
                        'estimated_time': 30
                    }
                ]
                recommendations.extend(prog_content)
                
            # Filter out completed content
            recommendations = [rec for rec in recommendations if rec['id'] not in completed_content]
            
            # Adjust for learning style
            recommendations = self.adjust_for_learning_style(recommendations, learning_style)
            
            # Sort by match score
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Generate learning sequence
            learning_sequence = self.generate_learning_sequence(recommendations)
            
            return {
                'task_type': 'recommend_content',
                'user_id': user_id,
                'recommendations': recommendations[:5],  # Top 5 recommendations
                'learning_sequence': learning_sequence,
                'personalization_factors': {
                    'learning_goals': learning_goals,
                    'current_level': current_level,
                    'learning_style': learning_style,
                    'completed_count': len(completed_content)
                },
                'next_steps': self.generate_next_steps(recommendations),
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recommending content: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    async def generate_content_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata for content"""
        try:
            content_text = data.get('content_text', '')
            content_type = data.get('content_type', 'text')
            
            # Extract keywords
            keywords = self.extract_keywords(content_text)
            
            # Determine difficulty level
            difficulty = self.assess_difficulty(content_text)
            
            # Estimate duration
            duration = self.estimate_duration(content_text, content_type)
            
            # Identify learning objectives
            learning_objectives = self.extract_learning_objectives(content_text)
            
            # Determine prerequisites
            prerequisites = self.identify_prerequisites(content_text, keywords)
            
            # Generate tags
            tags = self.generate_tags(keywords, content_type, difficulty)
            
            return {
                'task_type': 'generate_metadata',
                'metadata': {
                    'keywords': keywords,
                    'difficulty_level': difficulty,
                    'estimated_duration': duration,
                    'learning_objectives': learning_objectives,
                    'prerequisites': prerequisites,
                    'tags': tags,
                    'content_type': content_type,
                    'language': 'en',
                    'last_updated': datetime.now().isoformat()
                },
                'confidence_scores': {
                    'difficulty_assessment': 0.8,
                    'duration_estimate': 0.7,
                    'keyword_extraction': 0.9,
                    'objective_identification': 0.6
                },
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating metadata: {e}")
            return {'error': str(e), 'agent': self.agent_name}
            
    def filter_content(self, content_list: List[Dict], content_type: str, difficulty: str, learning_style: str) -> List[Dict]:
        """Filter content based on criteria"""
        filtered = content_list
        
        if content_type != 'any':
            filtered = [c for c in filtered if c.get('type') == content_type]
            
        if difficulty != 'any':
            filtered = [c for c in filtered if c.get('difficulty') == difficulty]
            
        if learning_style != 'any':
            # Prefer content types that match learning style
            style_preferences = {
                'visual': ['video', 'interactive'],
                'auditory': ['audio', 'video'],
                'kinesthetic': ['interactive', 'hands-on'],
                'reading': ['text', 'document']
            }
            preferred_types = style_preferences.get(learning_style, [])
            if preferred_types:
                # Boost relevance for preferred types
                for content in filtered:
                    if content.get('type') in preferred_types:
                        content['relevance_score'] *= 1.2
                        
        return filtered
        
    def score_to_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
            
    def adjust_for_learning_style(self, recommendations: List[Dict], learning_style: str) -> List[Dict]:
        """Adjust recommendations based on learning style"""
        style_multipliers = {
            'visual': {'video': 1.3, 'interactive': 1.2, 'text': 0.9},
            'auditory': {'video': 1.2, 'audio': 1.4, 'text': 0.8},
            'kinesthetic': {'interactive': 1.4, 'hands-on': 1.3, 'text': 0.7},
            'reading': {'text': 1.3, 'document': 1.2, 'video': 0.9}
        }
        
        multipliers = style_multipliers.get(learning_style, {})
        
        for rec in recommendations:
            content_type = rec.get('type', 'text')
            multiplier = multipliers.get(content_type, 1.0)
            rec['match_score'] *= multiplier
            
        return recommendations
        
    def generate_learning_sequence(self, recommendations: List[Dict]) -> List[Dict]:
        """Generate optimal learning sequence"""
        # Simple prerequisite-based ordering
        sequenced = []
        remaining = recommendations.copy()
        
        while remaining:
            # Find items with no unmet prerequisites
            ready_items = []
            for item in remaining:
                prereqs = item.get('prerequisites', [])
                completed_prereqs = [p for p in prereqs if any(p in seq.get('id', '') for seq in sequenced)]
                if len(completed_prereqs) == len(prereqs):
                    ready_items.append(item)
                    
            if ready_items:
                # Add highest scoring ready item
                next_item = max(ready_items, key=lambda x: x['match_score'])
                sequenced.append(next_item)
                remaining.remove(next_item)
            else:
                # Add remaining items (break circular dependencies)
                sequenced.extend(remaining)
                break
                
        return sequenced
        
    def generate_next_steps(self, recommendations: List[Dict]) -> List[str]:
        """Generate next steps for the user"""
        if not recommendations:
            return ["Explore available courses to find content that matches your interests"]
            
        steps = []
        first_rec = recommendations[0]
        
        steps.append(f"Start with '{first_rec['title']}' - it's highly relevant to your goals")
        
        if len(recommendations) > 1:
            steps.append(f"Follow up with '{recommendations[1]['title']}' to build on your knowledge")
            
        steps.append("Complete practice exercises to reinforce your learning")
        steps.append("Ask the AI tutor for clarification on any difficult concepts")
        
        return steps
        
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = text.lower().split()
        keywords = [word.strip('.,!?;:') for word in words if len(word) > 3 and word not in common_words]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
        
    def assess_difficulty(self, text: str) -> str:
        """Assess content difficulty level"""
        # Simple heuristics
        word_count = len(text.split())
        complex_words = ['algorithm', 'implementation', 'optimization', 'architecture', 'methodology']
        complex_count = sum(1 for word in complex_words if word in text.lower())
        
        if word_count > 1000 and complex_count > 3:
            return 'advanced'
        elif word_count > 500 and complex_count > 1:
            return 'intermediate'
        else:
            return 'beginner'
            
    def estimate_duration(self, text: str, content_type: str) -> int:
        """Estimate content duration in minutes"""
        word_count = len(text.split())
        
        # Reading speeds by type
        speeds = {
            'text': 200,  # words per minute
            'video': 150,
            'interactive': 100,
            'audio': 160
        }
        
        speed = speeds.get(content_type, 200)
        return max(5, int(word_count / speed))
        
    def extract_learning_objectives(self, text: str) -> List[str]:
        """Extract learning objectives from content"""
        objectives = []
        
        # Look for common objective patterns
        objective_patterns = [
            'learn to', 'understand', 'master', 'explore', 'discover',
            'develop skills', 'gain knowledge', 'become familiar'
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            for pattern in objective_patterns:
                if pattern in sentence.lower():
                    objectives.append(sentence.strip())
                    break
                    
        return objectives[:5]  # Top 5 objectives
        
    def identify_prerequisites(self, text: str, keywords: List[str]) -> List[str]:
        """Identify prerequisites based on content"""
        prereq_mapping = {
            'python': ['basic_programming'],
            'machine learning': ['python', 'statistics'],
            'neural networks': ['machine learning', 'linear algebra'],
            'data analysis': ['python', 'statistics'],
            'algorithms': ['basic_programming', 'mathematics']
        }
        
        prerequisites = set()
        for keyword in keywords:
            if keyword in prereq_mapping:
                prerequisites.update(prereq_mapping[keyword])
                
        return list(prerequisites)
        
    def generate_tags(self, keywords: List[str], content_type: str, difficulty: str) -> List[str]:
        """Generate tags for content"""
        tags = keywords[:5]  # Top 5 keywords as tags
        tags.append(content_type)
        tags.append(difficulty)
        
        # Add category tags
        if any(word in keywords for word in ['ai', 'machine', 'learning', 'neural']):
            tags.append('artificial-intelligence')
        if any(word in keywords for word in ['python', 'programming', 'code']):
            tags.append('programming')
        if any(word in keywords for word in ['data', 'analysis', 'statistics']):
            tags.append('data-science')
            
        return list(set(tags))  # Remove duplicates

# Worker function for running the agent
async def run_content_curator_agent():
    """Run the Content Curator Agent worker"""
    import asyncio
    
    agent = ContentCuratorAgent()
    await agent.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_content_curator_agent())
