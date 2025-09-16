"""
Analytics Agent for EduLMS v2
Handles learning analytics, predictive modeling, and reporting
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from ..communication.gemini_client import get_gemini_client
from ..communication.cache_manager import CacheManager
from ..base import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsQuery:
    """Analytics query structure"""
    query_type: str  # performance, prediction, cohort, engagement
    user_id: Optional[int] = None
    course_id: Optional[int] = None
    timeframe: str = "30d"
    metrics: List[str] = None
    filters: Dict[str, Any] = None

@dataclass
class AnalyticsResult:
    """Analytics result structure"""
    query_type: str
    data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    timestamp: datetime

class AnalyticsAgent(BaseAgent):
    """
    Analytics Agent for learning analytics and predictive modeling
    
    Capabilities:
    - Learning performance analysis
    - Predictive modeling for student outcomes
    - Cohort analysis and comparison
    - Engagement pattern analysis
    - Intervention recommendations
    - Custom reporting and dashboards
    """
    
    def __init__(self, agent_id: str = "analytics_agent"):
        super().__init__(agent_id)
        self.gemini_client = get_gemini_client()
        self.cache_manager = CacheManager()
        
        # Analytics models
        self.performance_model = None
        self.engagement_model = None
        self.scaler = StandardScaler()
        
        # Metrics definitions
        self.metrics_config = {
            "engagement": {
                "time_spent": "Total time spent in courses",
                "login_frequency": "Number of logins per week",
                "resource_access": "Number of resources accessed",
                "discussion_posts": "Number of discussion posts",
                "assignment_submissions": "Assignment submission rate"
            },
            "performance": {
                "quiz_scores": "Average quiz scores",
                "assignment_grades": "Average assignment grades",
                "completion_rate": "Course completion percentage",
                "progress_velocity": "Learning progress speed",
                "skill_mastery": "Skill mastery levels"
            },
            "behavioral": {
                "study_patterns": "Study time patterns",
                "help_seeking": "Frequency of help requests",
                "collaboration": "Collaboration activity",
                "procrastination": "Assignment delay patterns",
                "self_regulation": "Self-directed learning indicators"
            }
        }
    
    async def start(self):
        """Start the analytics agent"""
        logger.info(f"Starting Analytics Agent {self.agent_id}")
        await super().start()
        
        # Initialize ML models
        await self.initialize_models()
        
        while self.running:
            try:
                # Check for analytics requests
                messages = await self.get_messages("analytics_request")
                
                for message in messages:
                    await self.process_analytics_request(message)
                
                # Check for prediction requests
                prediction_messages = await self.get_messages("prediction_request")
                
                for message in prediction_messages:
                    await self.process_prediction_request(message)
                
                # Check for report generation requests
                report_messages = await self.get_messages("report_request")
                
                for message in report_messages:
                    await self.process_report_request(message)
                
                # Periodic model updates
                await self.update_models_if_needed()
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in analytics agent loop: {e}")
                await asyncio.sleep(15)
    
    async def initialize_models(self):
        """Initialize machine learning models"""
        try:
            logger.info("Initializing analytics models")
            
            # Load historical data for model training
            training_data = await self.load_training_data()
            
            if training_data and len(training_data) > 100:  # Minimum data requirement
                await self.train_models(training_data)
            else:
                logger.warning("Insufficient data for model training, using default models")
                self.performance_model = RandomForestClassifier(n_estimators=100, random_state=42)
                self.engagement_model = LinearRegression()
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    async def process_analytics_request(self, message: Dict[str, Any]):
        """Process analytics request from users or other agents"""
        try:
            data = message.get('data', {})
            query = AnalyticsQuery(**data)
            
            logger.info(f"Processing analytics request: {query.query_type}")
            
            # Check cache first
            cache_key = f"analytics_{query.query_type}_{query.user_id}_{query.course_id}_{query.timeframe}"
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                logger.info("Returning cached analytics result")
                await self.send_response(message, cached_result)
                return
            
            # Perform analytics
            result = await self.perform_analytics(query)
            
            # Cache result
            ttl = 1800 if query.query_type in ["performance", "engagement"] else 3600  # 30min or 1hour
            await self.cache_manager.set(cache_key, result.__dict__, ttl=ttl)
            
            # Send response
            await self.send_response(message, result.__dict__)
            
            # Log analytics activity
            await self.log_analytics_activity(query, result)
            
        except Exception as e:
            logger.error(f"Error processing analytics request: {e}")
            await self.send_error_response(message, str(e))
    
    async def perform_analytics(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Perform analytics based on query type"""
        try:
            if query.query_type == "performance":
                return await self.analyze_performance(query)
            elif query.query_type == "engagement":
                return await self.analyze_engagement(query)
            elif query.query_type == "cohort":
                return await self.analyze_cohort(query)
            elif query.query_type == "prediction":
                return await self.generate_predictions(query)
            elif query.query_type == "intervention":
                return await self.recommend_interventions(query)
            else:
                raise ValueError(f"Unknown analytics query type: {query.query_type}")
                
        except Exception as e:
            logger.error(f"Error performing analytics: {e}")
            raise
    
    async def analyze_performance(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Analyze learning performance metrics"""
        try:
            # Fetch performance data
            performance_data = await self.fetch_performance_data(query)
            
            # Calculate key metrics
            metrics = await self.calculate_performance_metrics(performance_data)
            
            # Generate insights using Gemini
            insights = await self.generate_performance_insights(metrics, query)
            
            # Generate recommendations
            recommendations = await self.generate_performance_recommendations(metrics, insights)
            
            # Calculate confidence score
            confidence_score = await self.calculate_confidence_score(performance_data, metrics)
            
            return AnalyticsResult(
                query_type="performance",
                data={
                    "metrics": metrics,
                    "raw_data": performance_data,
                    "trends": await self.identify_trends(performance_data)
                },
                insights=insights,
                recommendations=recommendations,
                confidence_score=confidence_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            raise
    
    async def analyze_engagement(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Analyze student engagement patterns"""
        try:
            # Fetch engagement data
            engagement_data = await self.fetch_engagement_data(query)
            
            # Calculate engagement metrics
            metrics = await self.calculate_engagement_metrics(engagement_data)
            
            # Identify engagement patterns
            patterns = await self.identify_engagement_patterns(engagement_data)
            
            # Generate insights
            insights = await self.generate_engagement_insights(metrics, patterns)
            
            # Generate recommendations
            recommendations = await self.generate_engagement_recommendations(metrics, patterns)
            
            return AnalyticsResult(
                query_type="engagement",
                data={
                    "metrics": metrics,
                    "patterns": patterns,
                    "raw_data": engagement_data
                },
                insights=insights,
                recommendations=recommendations,
                confidence_score=0.85,  # High confidence for engagement analysis
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            raise
    
    async def generate_predictions(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Generate predictive analytics"""
        try:
            # Fetch historical data
            historical_data = await self.fetch_historical_data(query)
            
            # Prepare features for prediction
            features = await self.prepare_prediction_features(historical_data)
            
            # Generate predictions
            predictions = await self.make_predictions(features, query)
            
            # Generate insights about predictions
            insights = await self.generate_prediction_insights(predictions, query)
            
            # Generate actionable recommendations
            recommendations = await self.generate_prediction_recommendations(predictions, insights)
            
            return AnalyticsResult(
                query_type="prediction",
                data={
                    "predictions": predictions,
                    "features_used": list(features.keys()) if features else [],
                    "model_info": await self.get_model_info()
                },
                insights=insights,
                recommendations=recommendations,
                confidence_score=predictions.get("confidence", 0.7) if predictions else 0.5,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            raise
    
    async def fetch_performance_data(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Fetch performance data from database"""
        try:
            # Build SQL query based on parameters
            sql_conditions = []
            params = []
            
            if query.user_id:
                sql_conditions.append("user_id = %s")
                params.append(query.user_id)
            
            if query.course_id:
                sql_conditions.append("course_id = %s")
                params.append(query.course_id)
            
            # Add timeframe condition
            if query.timeframe:
                days = int(query.timeframe.replace('d', ''))
                sql_conditions.append("created_at >= %s")
                params.append(datetime.now() - timedelta(days=days))
            
            where_clause = " AND ".join(sql_conditions) if sql_conditions else "1=1"
            
            # Fetch user progress data
            progress_query = f"""
            SELECT user_id, course_id, lesson_id, progress_percentage, 
                   completed_at, time_spent, metadata, created_at
            FROM user_progress 
            WHERE {where_clause}
            ORDER BY created_at DESC
            """
            
            progress_data = await self.execute_query(progress_query, params)
            
            # Fetch assessment data (if available)
            assessment_query = f"""
            SELECT user_id, course_id, assessment_type, score, 
                   max_score, completed_at, metadata
            FROM assessments 
            WHERE {where_clause}
            ORDER BY completed_at DESC
            """
            
            assessment_data = await self.execute_query(assessment_query, params) or []
            
            return {
                "progress": progress_data or [],
                "assessments": assessment_data,
                "timeframe": query.timeframe,
                "user_count": len(set(row.get('user_id') for row in progress_data)) if progress_data else 0
            }
            
        except Exception as e:
            logger.error(f"Error fetching performance data: {e}")
            return {"progress": [], "assessments": [], "timeframe": query.timeframe, "user_count": 0}
    
    async def calculate_performance_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key performance metrics"""
        try:
            progress_data = data.get("progress", [])
            assessment_data = data.get("assessments", [])
            
            if not progress_data:
                return {"error": "No progress data available"}
            
            # Convert to DataFrame for easier analysis
            df_progress = pd.DataFrame(progress_data)
            df_assessments = pd.DataFrame(assessment_data) if assessment_data else pd.DataFrame()
            
            metrics = {}
            
            # Progress metrics
            if not df_progress.empty:
                metrics["average_progress"] = df_progress["progress_percentage"].mean()
                metrics["completion_rate"] = (df_progress["progress_percentage"] == 100).mean() * 100
                metrics["total_time_spent"] = df_progress["time_spent"].sum() if "time_spent" in df_progress.columns else 0
                metrics["active_users"] = df_progress["user_id"].nunique()
                metrics["lessons_completed"] = (df_progress["progress_percentage"] == 100).sum()
            
            # Assessment metrics
            if not df_assessments.empty:
                metrics["average_score"] = df_assessments["score"].mean()
                metrics["pass_rate"] = (df_assessments["score"] / df_assessments["max_score"] >= 0.7).mean() * 100
                metrics["assessment_completion"] = len(df_assessments)
            
            # Engagement metrics
            if not df_progress.empty:
                # Calculate study velocity (progress per day)
                df_progress["created_at"] = pd.to_datetime(df_progress["created_at"])
                date_range = (df_progress["created_at"].max() - df_progress["created_at"].min()).days
                metrics["study_velocity"] = metrics.get("average_progress", 0) / max(date_range, 1)
                
                # Calculate consistency (standard deviation of progress)
                metrics["consistency_score"] = 100 - min(df_progress["progress_percentage"].std(), 100)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {"error": str(e)}
    
    async def generate_performance_insights(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> List[str]:
        """Generate insights about performance using Gemini"""
        try:
            insights_prompt = f"""
            Analyze the following learning performance metrics and provide key insights:
            
            Metrics:
            {json.dumps(metrics, indent=2)}
            
            Query Context:
            - User ID: {query.user_id or 'All users'}
            - Course ID: {query.course_id or 'All courses'}
            - Timeframe: {query.timeframe}
            
            Provide 3-5 key insights about:
            1. Overall performance trends
            2. Areas of concern or excellence
            3. Patterns in learning behavior
            4. Comparative analysis (if applicable)
            
            Format as a JSON array of insight strings.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=insights_prompt,
                system_instruction="You are an expert learning analytics specialist. Provide actionable insights based on educational data.",
                temperature=0.3,
                max_tokens=1000
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: split by lines and clean
                insights = [line.strip() for line in response.split('\n') if line.strip()]
                return insights[:5]  # Limit to 5 insights
                
        except Exception as e:
            logger.error(f"Error generating performance insights: {e}")
            return ["Performance analysis completed with available data"]
    
    async def generate_performance_recommendations(self, metrics: Dict[str, Any], insights: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        try:
            recommendations_prompt = f"""
            Based on these performance metrics and insights, provide actionable recommendations:
            
            Metrics: {json.dumps(metrics, indent=2)}
            
            Insights: {json.dumps(insights, indent=2)}
            
            Provide 3-5 specific, actionable recommendations for:
            1. Improving learning outcomes
            2. Increasing engagement
            3. Addressing identified issues
            4. Optimizing learning paths
            
            Format as a JSON array of recommendation strings.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=recommendations_prompt,
                system_instruction="You are an educational consultant. Provide specific, actionable recommendations.",
                temperature=0.4,
                max_tokens=1000
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                recommendations = [line.strip() for line in response.split('\n') if line.strip()]
                return recommendations[:5]
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Continue monitoring performance metrics and adjust learning strategies as needed"]
    
    async def fetch_engagement_data(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Fetch engagement data from database"""
        # Similar to fetch_performance_data but focused on engagement metrics
        # This would include login patterns, resource access, interaction data, etc.
        return {
            "logins": [],
            "resource_access": [],
            "interactions": [],
            "session_duration": []
        }
    
    async def calculate_engagement_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        return {
            "daily_active_users": 0,
            "average_session_duration": 0,
            "resource_utilization": 0,
            "interaction_rate": 0
        }
    
    async def identify_engagement_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify engagement patterns"""
        return {
            "peak_hours": [],
            "weekly_patterns": {},
            "seasonal_trends": {}
        }
    
    async def generate_engagement_insights(self, metrics: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate engagement insights"""
        return ["Engagement analysis completed"]
    
    async def generate_engagement_recommendations(self, metrics: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate engagement recommendations"""
        return ["Monitor engagement patterns and adjust content delivery timing"]
    
    async def calculate_confidence_score(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> float:
        """Calculate confidence score for analytics results"""
        score = 0.5  # Base score
        
        # Adjust based on data volume
        data_points = len(data.get("progress", []))
        if data_points >= 100:
            score += 0.3
        elif data_points >= 50:
            score += 0.2
        elif data_points >= 10:
            score += 0.1
        
        # Adjust based on data completeness
        if "time_spent" in str(data):
            score += 0.1
        if "assessments" in data and data["assessments"]:
            score += 0.1
        
        return min(score, 1.0)
    
    async def process_prediction_request(self, message: Dict[str, Any]):
        """Process prediction request"""
        try:
            query = AnalyticsQuery(**message.get('data', {}))
            query.query_type = "prediction"
            
            result = await self.perform_analytics(query)
            await self.send_response(message, result.__dict__)
            
        except Exception as e:
            logger.error(f"Error processing prediction request: {e}")
            await self.send_error_response(message, str(e))
    
    async def process_report_request(self, message: Dict[str, Any]):
        """Process report generation request"""
        try:
            data = message.get('data', {})
            report_type = data.get('report_type', 'summary')
            
            # Generate comprehensive report
            report = await self.generate_comprehensive_report(data)
            
            await self.send_response(message, {
                'report_type': report_type,
                'report_data': report,
                'generated_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing report request: {e}")
            await self.send_error_response(message, str(e))
    
    async def generate_comprehensive_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        return {
            "summary": "Comprehensive analytics report generated",
            "sections": ["Performance", "Engagement", "Predictions"],
            "data_points": 0,
            "insights_count": 0
        }
    
    async def update_models_if_needed(self):
        """Update ML models periodically"""
        # Check if models need updating (e.g., weekly)
        # This would retrain models with new data
        pass
    
    async def log_analytics_activity(self, query: AnalyticsQuery, result: AnalyticsResult):
        """Log analytics activity"""
        try:
            activity_data = {
                'agent_id': self.agent_id,
                'activity_type': 'analytics_performed',
                'query_type': query.query_type,
                'user_id': query.user_id,
                'course_id': query.course_id,
                'confidence_score': result.confidence_score,
                'insights_count': len(result.insights),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.log_activity(activity_data)
            
        except Exception as e:
            logger.error(f"Error logging analytics activity: {e}")

# Agent factory function
def create_analytics_agent() -> AnalyticsAgent:
    """Create and return an Analytics Agent instance"""
    return AnalyticsAgent()
