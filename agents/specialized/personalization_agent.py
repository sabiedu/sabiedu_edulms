"""
Personalization Agent for EduLMS v2
Handles adaptive learning, user profiling, and personalized content recommendations
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from ..communication.gemini_client import get_gemini_client
from ..communication.cache_manager import CacheManager
from ..base import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class LearnerProfile:
    """Learner profile structure"""
    user_id: int
    learning_style: str  # visual, auditory, kinesthetic, reading
    difficulty_preference: str  # beginner, intermediate, advanced
    pace: str  # slow, normal, fast
    interests: List[str]
    strengths: List[str]
    weaknesses: List[str]
    goals: List[str]
    engagement_patterns: Dict[str, Any]
    performance_history: Dict[str, Any]
    last_updated: datetime

@dataclass
class PersonalizationRecommendation:
    """Personalization recommendation structure"""
    user_id: int
    recommendation_type: str  # content, path, activity, intervention
    recommendations: List[Dict[str, Any]]
    reasoning: str
    confidence_score: float
    timestamp: datetime

class PersonalizationAgent(BaseAgent):
    """
    Personalization Agent for adaptive learning and user customization
    
    Capabilities:
    - Learner profiling and analysis
    - Adaptive content recommendations
    - Learning path personalization
    - Intervention recommendations
    - Learning style detection
    - Performance prediction and optimization
    """
    
    def __init__(self, agent_id: str = "personalization_agent"):
        super().__init__(agent_id)
        self.gemini_client = get_gemini_client()
        self.cache_manager = CacheManager()
        
        # ML models for personalization
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        
        # Learning style indicators
        self.learning_style_indicators = {
            "visual": ["prefers_images", "uses_diagrams", "color_coding", "spatial_tasks"],
            "auditory": ["prefers_audio", "discussions", "verbal_explanations", "music_background"],
            "kinesthetic": ["hands_on_activities", "movement", "physical_manipulation", "experiments"],
            "reading": ["text_heavy_content", "note_taking", "written_instructions", "research"]
        }
        
        # Engagement patterns
        self.engagement_metrics = [
            "session_duration", "click_through_rate", "completion_rate",
            "interaction_frequency", "help_seeking_behavior", "social_participation"
        ]
        
        # Difficulty adaptation rules
        self.difficulty_rules = {
            "increase": {"min_score": 0.8, "consistency": 3},
            "decrease": {"max_score": 0.6, "struggles": 2},
            "maintain": {"score_range": (0.6, 0.8)}
        }
    
    async def start(self):
        """Start the personalization agent"""
        logger.info(f"Starting Personalization Agent {self.agent_id}")
        await super().start()
        
        while self.running:
            try:
                # Check for profile update requests
                messages = await self.get_messages("profile_update")
                
                for message in messages:
                    await self.process_profile_update(message)
                
                # Check for recommendation requests
                rec_messages = await self.get_messages("recommendation_request")
                
                for message in rec_messages:
                    await self.process_recommendation_request(message)
                
                # Check for learning path adaptation requests
                path_messages = await self.get_messages("adapt_path")
                
                for message in path_messages:
                    await self.process_path_adaptation(message)
                
                # Periodic profile analysis and updates
                await self.periodic_profile_analysis()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in personalization agent loop: {e}")
                await asyncio.sleep(60)
    
    async def process_profile_update(self, message: Dict[str, Any]):
        """Process learner profile update request"""
        try:
            data = message.get('data', {})
            user_id = data.get('user_id')
            
            if not user_id:
                await self.send_error_response(message, "User ID is required")
                return
            
            logger.info(f"Updating profile for user {user_id}")
            
            # Get current profile or create new one
            profile = await self.get_learner_profile(user_id)
            
            # Update profile with new data
            updated_profile = await self.update_profile(profile, data)
            
            # Save updated profile
            await self.save_learner_profile(updated_profile)
            
            # Generate recommendations based on updated profile
            recommendations = await self.generate_recommendations(updated_profile)
            
            await self.send_response(message, {
                'user_id': user_id,
                'profile_updated': True,
                'profile': updated_profile.__dict__,
                'recommendations': recommendations.__dict__,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing profile update: {e}")
            await self.send_error_response(message, str(e))
    
    async def get_learner_profile(self, user_id: int) -> LearnerProfile:
        """Get or create learner profile"""
        try:
            # Check cache first
            cache_key = f"profile_{user_id}"
            cached_profile = await self.cache_manager.get(cache_key)
            
            if cached_profile:
                return LearnerProfile(**cached_profile)
            
            # Fetch from database
            profile_data = await self.fetch_profile_from_db(user_id)
            
            if profile_data:
                profile = LearnerProfile(**profile_data)
            else:
                # Create new profile
                profile = await self.create_new_profile(user_id)
            
            # Cache the profile
            await self.cache_manager.set(cache_key, profile.__dict__, ttl=1800)  # 30 minutes
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting learner profile: {e}")
            return await self.create_new_profile(user_id)
    
    async def create_new_profile(self, user_id: int) -> LearnerProfile:
        """Create a new learner profile with defaults"""
        return LearnerProfile(
            user_id=user_id,
            learning_style="visual",  # Default
            difficulty_preference="intermediate",
            pace="normal",
            interests=[],
            strengths=[],
            weaknesses=[],
            goals=[],
            engagement_patterns={},
            performance_history={},
            last_updated=datetime.now()
        )
    
    async def update_profile(self, profile: LearnerProfile, data: Dict[str, Any]) -> LearnerProfile:
        """Update learner profile with new data"""
        try:
            # Update learning style if provided
            if 'learning_activities' in data:
                profile.learning_style = await self.detect_learning_style(data['learning_activities'])
            
            # Update difficulty preference based on performance
            if 'performance_data' in data:
                profile.difficulty_preference = await self.adapt_difficulty(data['performance_data'])
            
            # Update pace based on completion times
            if 'completion_times' in data:
                profile.pace = await self.detect_pace(data['completion_times'])
            
            # Update interests based on engagement
            if 'engagement_data' in data:
                profile.interests = await self.extract_interests(data['engagement_data'])
            
            # Update strengths and weaknesses
            if 'assessment_results' in data:
                strengths, weaknesses = await self.analyze_performance_patterns(data['assessment_results'])
                profile.strengths = strengths
                profile.weaknesses = weaknesses
            
            # Update goals if provided
            if 'goals' in data:
                profile.goals = data['goals']
            
            # Update engagement patterns
            if 'engagement_metrics' in data:
                profile.engagement_patterns = await self.analyze_engagement_patterns(data['engagement_metrics'])
            
            # Update performance history
            if 'recent_performance' in data:
                profile.performance_history = data['recent_performance']
            
            profile.last_updated = datetime.now()
            
            return profile
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return profile
    
    async def detect_learning_style(self, activities: List[Dict[str, Any]]) -> str:
        """Detect learning style based on activity preferences"""
        try:
            style_scores = {style: 0 for style in self.learning_style_indicators.keys()}
            
            for activity in activities:
                activity_type = activity.get('type', '')
                engagement_score = activity.get('engagement_score', 0)
                
                # Score each learning style based on activity preferences
                for style, indicators in self.learning_style_indicators.items():
                    if any(indicator in activity_type.lower() for indicator in indicators):
                        style_scores[style] += engagement_score
            
            # Return the style with highest score
            return max(style_scores, key=style_scores.get) if any(style_scores.values()) else "visual"
            
        except Exception as e:
            logger.error(f"Error detecting learning style: {e}")
            return "visual"
    
    async def adapt_difficulty(self, performance_data: List[Dict[str, Any]]) -> str:
        """Adapt difficulty level based on performance"""
        try:
            if not performance_data:
                return "intermediate"
            
            recent_scores = [p.get('score', 0) for p in performance_data[-5:]]  # Last 5 performances
            avg_score = np.mean(recent_scores)
            consistency = len(set(recent_scores)) <= 2  # Low variance indicates consistency
            
            if avg_score >= self.difficulty_rules["increase"]["min_score"] and consistency:
                return "advanced"
            elif avg_score <= self.difficulty_rules["decrease"]["max_score"]:
                return "beginner"
            else:
                return "intermediate"
                
        except Exception as e:
            logger.error(f"Error adapting difficulty: {e}")
            return "intermediate"
    
    async def detect_pace(self, completion_times: List[Dict[str, Any]]) -> str:
        """Detect learning pace based on completion times"""
        try:
            if not completion_times:
                return "normal"
            
            times = [ct.get('time_spent', 0) for ct in completion_times]
            avg_time = np.mean(times)
            
            # Compare with expected times (if available)
            expected_times = [ct.get('expected_time', avg_time) for ct in completion_times]
            avg_expected = np.mean(expected_times)
            
            ratio = avg_time / avg_expected if avg_expected > 0 else 1
            
            if ratio < 0.7:
                return "fast"
            elif ratio > 1.3:
                return "slow"
            else:
                return "normal"
                
        except Exception as e:
            logger.error(f"Error detecting pace: {e}")
            return "normal"
    
    async def extract_interests(self, engagement_data: Dict[str, Any]) -> List[str]:
        """Extract interests based on engagement patterns"""
        try:
            interests = []
            
            # Analyze topic engagement
            topic_engagement = engagement_data.get('topic_engagement', {})
            
            # Sort topics by engagement score
            sorted_topics = sorted(topic_engagement.items(), key=lambda x: x[1], reverse=True)
            
            # Take top engaged topics as interests
            interests = [topic for topic, score in sorted_topics[:5] if score > 0.7]
            
            return interests
            
        except Exception as e:
            logger.error(f"Error extracting interests: {e}")
            return []
    
    async def analyze_performance_patterns(self, assessment_results: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Analyze performance to identify strengths and weaknesses"""
        try:
            topic_scores = {}
            
            for result in assessment_results:
                topic = result.get('topic', 'general')
                score = result.get('score', 0)
                
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(score)
            
            # Calculate average scores per topic
            topic_averages = {topic: np.mean(scores) for topic, scores in topic_scores.items()}
            
            # Identify strengths (high performance) and weaknesses (low performance)
            strengths = [topic for topic, avg in topic_averages.items() if avg >= 0.8]
            weaknesses = [topic for topic, avg in topic_averages.items() if avg <= 0.6]
            
            return strengths, weaknesses
            
        except Exception as e:
            logger.error(f"Error analyzing performance patterns: {e}")
            return [], []
    
    async def analyze_engagement_patterns(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        try:
            patterns = {}
            
            # Time-based patterns
            if 'session_times' in metrics:
                patterns['preferred_study_times'] = await self.identify_peak_hours(metrics['session_times'])
            
            # Content type preferences
            if 'content_engagement' in metrics:
                patterns['preferred_content_types'] = await self.identify_content_preferences(metrics['content_engagement'])
            
            # Social learning patterns
            if 'social_interactions' in metrics:
                patterns['social_learning_preference'] = metrics['social_interactions'].get('frequency', 0) > 0.5
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing engagement patterns: {e}")
            return {}
    
    async def process_recommendation_request(self, message: Dict[str, Any]):
        """Process recommendation request"""
        try:
            data = message.get('data', {})
            user_id = data.get('user_id')
            recommendation_type = data.get('type', 'content')
            
            profile = await self.get_learner_profile(user_id)
            recommendations = await self.generate_recommendations(profile, recommendation_type)
            
            await self.send_response(message, recommendations.__dict__)
            
        except Exception as e:
            logger.error(f"Error processing recommendation request: {e}")
            await self.send_error_response(message, str(e))
    
    async def generate_recommendations(self, profile: LearnerProfile, rec_type: str = "content") -> PersonalizationRecommendation:
        """Generate personalized recommendations"""
        try:
            if rec_type == "content":
                recommendations = await self.recommend_content(profile)
            elif rec_type == "path":
                recommendations = await self.recommend_learning_path(profile)
            elif rec_type == "activity":
                recommendations = await self.recommend_activities(profile)
            elif rec_type == "intervention":
                recommendations = await self.recommend_interventions(profile)
            else:
                recommendations = await self.recommend_general(profile)
            
            # Generate reasoning using Gemini
            reasoning = await self.generate_recommendation_reasoning(profile, recommendations, rec_type)
            
            return PersonalizationRecommendation(
                user_id=profile.user_id,
                recommendation_type=rec_type,
                recommendations=recommendations,
                reasoning=reasoning,
                confidence_score=0.8,  # Default confidence
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return PersonalizationRecommendation(
                user_id=profile.user_id,
                recommendation_type=rec_type,
                recommendations=[],
                reasoning="Error generating recommendations",
                confidence_score=0.0,
                timestamp=datetime.now()
            )
    
    async def recommend_content(self, profile: LearnerProfile) -> List[Dict[str, Any]]:
        """Recommend personalized content"""
        recommendations = []
        
        # Content based on learning style
        if profile.learning_style == "visual":
            recommendations.append({
                "type": "visual_content",
                "title": "Interactive Diagrams and Infographics",
                "reason": "Matches your visual learning preference"
            })
        elif profile.learning_style == "auditory":
            recommendations.append({
                "type": "audio_content",
                "title": "Podcast Lectures and Audio Explanations",
                "reason": "Matches your auditory learning preference"
            })
        
        # Content based on interests
        for interest in profile.interests[:3]:
            recommendations.append({
                "type": "interest_content",
                "title": f"Advanced topics in {interest}",
                "reason": f"Based on your interest in {interest}"
            })
        
        # Content to address weaknesses
        for weakness in profile.weaknesses[:2]:
            recommendations.append({
                "type": "remedial_content",
                "title": f"Foundational concepts in {weakness}",
                "reason": f"To strengthen understanding of {weakness}"
            })
        
        return recommendations
    
    async def recommend_learning_path(self, profile: LearnerProfile) -> List[Dict[str, Any]]:
        """Recommend personalized learning path"""
        recommendations = []
        
        # Path based on difficulty preference
        recommendations.append({
            "type": "difficulty_path",
            "title": f"{profile.difficulty_preference.title()} Learning Track",
            "reason": f"Matches your {profile.difficulty_preference} skill level"
        })
        
        # Path based on pace
        if profile.pace == "fast":
            recommendations.append({
                "type": "accelerated_path",
                "title": "Accelerated Learning Program",
                "reason": "Optimized for your fast learning pace"
            })
        elif profile.pace == "slow":
            recommendations.append({
                "type": "extended_path",
                "title": "Extended Learning Program",
                "reason": "Allows more time for concept mastery"
            })
        
        return recommendations
    
    async def recommend_activities(self, profile: LearnerProfile) -> List[Dict[str, Any]]:
        """Recommend personalized activities"""
        recommendations = []
        
        # Activities based on learning style
        style_activities = {
            "visual": ["Mind mapping", "Diagram creation", "Video analysis"],
            "auditory": ["Discussion forums", "Audio recordings", "Verbal presentations"],
            "kinesthetic": ["Hands-on projects", "Simulations", "Interactive labs"],
            "reading": ["Research assignments", "Note-taking exercises", "Written reflections"]
        }
        
        activities = style_activities.get(profile.learning_style, [])
        for activity in activities:
            recommendations.append({
                "type": "learning_activity",
                "title": activity,
                "reason": f"Suits your {profile.learning_style} learning style"
            })
        
        return recommendations
    
    async def recommend_interventions(self, profile: LearnerProfile) -> List[Dict[str, Any]]:
        """Recommend interventions for struggling learners"""
        recommendations = []
        
        # Check if intervention is needed
        if profile.weaknesses:
            recommendations.append({
                "type": "tutoring",
                "title": "One-on-one tutoring sessions",
                "reason": "To address identified knowledge gaps"
            })
        
        # Check engagement patterns
        if profile.engagement_patterns.get('low_engagement', False):
            recommendations.append({
                "type": "engagement_boost",
                "title": "Gamified learning activities",
                "reason": "To increase engagement and motivation"
            })
        
        return recommendations
    
    async def recommend_general(self, profile: LearnerProfile) -> List[Dict[str, Any]]:
        """Generate general recommendations"""
        return [
            {
                "type": "general",
                "title": "Continue current learning path",
                "reason": "Based on your progress and preferences"
            }
        ]
    
    async def generate_recommendation_reasoning(self, profile: LearnerProfile, recommendations: List[Dict[str, Any]], rec_type: str) -> str:
        """Generate reasoning for recommendations using Gemini"""
        try:
            reasoning_prompt = f"""
            Explain why these recommendations are suitable for this learner:
            
            Learner Profile:
            - Learning Style: {profile.learning_style}
            - Difficulty Preference: {profile.difficulty_preference}
            - Pace: {profile.pace}
            - Interests: {', '.join(profile.interests)}
            - Strengths: {', '.join(profile.strengths)}
            - Weaknesses: {', '.join(profile.weaknesses)}
            
            Recommendations:
            {json.dumps(recommendations, indent=2)}
            
            Provide a clear, concise explanation of why these recommendations match the learner's profile.
            """
            
            reasoning = await self.gemini_client.generate_content(
                prompt=reasoning_prompt,
                system_instruction="You are an educational advisor explaining personalized recommendations.",
                temperature=0.3,
                max_tokens=500
            )
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return "Recommendations based on learner profile analysis"
    
    async def process_path_adaptation(self, message: Dict[str, Any]):
        """Process learning path adaptation request"""
        try:
            data = message.get('data', {})
            user_id = data.get('user_id')
            current_path = data.get('current_path', [])
            
            profile = await self.get_learner_profile(user_id)
            adapted_path = await self.adapt_learning_path(profile, current_path)
            
            await self.send_response(message, {
                'user_id': user_id,
                'original_path': current_path,
                'adapted_path': adapted_path,
                'adaptations_made': await self.explain_adaptations(current_path, adapted_path),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing path adaptation: {e}")
            await self.send_error_response(message, str(e))
    
    async def adapt_learning_path(self, profile: LearnerProfile, current_path: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adapt learning path based on learner profile"""
        adapted_path = current_path.copy()
        
        # Adjust difficulty levels
        for item in adapted_path:
            if item.get('difficulty') != profile.difficulty_preference:
                item['difficulty'] = profile.difficulty_preference
                item['adapted'] = True
        
        # Adjust content types based on learning style
        for item in adapted_path:
            if profile.learning_style == "visual" and item.get('type') == 'text':
                item['type'] = 'visual'
                item['adapted'] = True
        
        # Add content for weaknesses
        for weakness in profile.weaknesses:
            adapted_path.append({
                'type': 'remedial',
                'topic': weakness,
                'difficulty': 'beginner',
                'reason': f'Added to address weakness in {weakness}',
                'adapted': True
            })
        
        return adapted_path
    
    async def explain_adaptations(self, original: List[Dict[str, Any]], adapted: List[Dict[str, Any]]) -> List[str]:
        """Explain what adaptations were made"""
        explanations = []
        
        # Compare paths and identify changes
        if len(adapted) > len(original):
            explanations.append(f"Added {len(adapted) - len(original)} additional learning modules")
        
        adapted_items = [item for item in adapted if item.get('adapted', False)]
        if adapted_items:
            explanations.append(f"Modified {len(adapted_items)} existing modules for personalization")
        
        return explanations
    
    async def periodic_profile_analysis(self):
        """Perform periodic analysis and updates of learner profiles"""
        try:
            # This would run periodically to update profiles based on new data
            # Implementation would depend on specific requirements
            pass
        except Exception as e:
            logger.error(f"Error in periodic profile analysis: {e}")
    
    async def save_learner_profile(self, profile: LearnerProfile):
        """Save learner profile to database"""
        try:
            # Save to database
            await self.execute_query(
                "INSERT OR REPLACE INTO learner_profiles (user_id, profile_data, updated_at) VALUES (?, ?, ?)",
                [profile.user_id, json.dumps(profile.__dict__, default=str), datetime.now()]
            )
            
            # Update cache
            cache_key = f"profile_{profile.user_id}"
            await self.cache_manager.set(cache_key, profile.__dict__, ttl=1800)
            
        except Exception as e:
            logger.error(f"Error saving learner profile: {e}")
    
    async def fetch_profile_from_db(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch learner profile from database"""
        try:
            result = await self.execute_query(
                "SELECT profile_data FROM learner_profiles WHERE user_id = ?",
                [user_id]
            )
            
            if result:
                return json.loads(result[0]['profile_data'])
            return None
            
        except Exception as e:
            logger.error(f"Error fetching profile from database: {e}")
            return None

# Agent factory function
def create_personalization_agent() -> PersonalizationAgent:
    """Create and return a Personalization Agent instance"""
    return PersonalizationAgent()
