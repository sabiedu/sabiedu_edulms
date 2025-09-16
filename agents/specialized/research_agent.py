"""
Research Agent for EduLMS v2
Handles academic research, literature review, and citation management
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
class ResearchQuery:
    """Research query structure"""
    query: str
    domain: str
    user_id: int
    course_id: Optional[int] = None
    depth: str = "moderate"  # basic, moderate, comprehensive
    sources: List[str] = None

@dataclass
class ResearchResult:
    """Research result structure"""
    query: str
    summary: str
    key_findings: List[str]
    sources: List[Dict[str, Any]]
    citations: List[str]
    related_topics: List[str]
    confidence_score: float
    timestamp: datetime

class ResearchAgent(BaseAgent):
    """
    Research Agent for academic research and literature review
    
    Capabilities:
    - Academic literature search and analysis
    - Citation management and formatting
    - Research trend analysis
    - Knowledge discovery and synthesis
    - Research methodology recommendations
    """
    
    def __init__(self, agent_id: str = "research_agent"):
        super().__init__(agent_id)
        self.gemini_client = get_gemini_client()
        self.cache_manager = CacheManager()
        
        # Research domains and their characteristics
        self.research_domains = {
            "computer_science": {
                "keywords": ["algorithm", "programming", "software", "AI", "machine learning"],
                "sources": ["ACM", "IEEE", "arXiv", "Google Scholar"],
                "citation_style": "ACM"
            },
            "mathematics": {
                "keywords": ["theorem", "proof", "equation", "analysis", "algebra"],
                "sources": ["MathSciNet", "arXiv", "Zentralblatt MATH"],
                "citation_style": "AMS"
            },
            "education": {
                "keywords": ["pedagogy", "learning", "curriculum", "assessment"],
                "sources": ["ERIC", "Education Source", "PsycINFO"],
                "citation_style": "APA"
            },
            "general": {
                "keywords": ["research", "study", "analysis", "methodology"],
                "sources": ["Google Scholar", "JSTOR", "PubMed"],
                "citation_style": "APA"
            }
        }
    
    async def start(self):
        """Start the research agent"""
        logger.info(f"Starting Research Agent {self.agent_id}")
        await super().start()
        
        while self.running:
            try:
                # Check for research requests
                messages = await self.get_messages("research_request")
                
                for message in messages:
                    await self.process_research_request(message)
                
                # Check for citation requests
                citation_messages = await self.get_messages("citation_request")
                
                for message in citation_messages:
                    await self.process_citation_request(message)
                
                # Check for trend analysis requests
                trend_messages = await self.get_messages("trend_analysis")
                
                for message in trend_messages:
                    await self.process_trend_analysis(message)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in research agent loop: {e}")
                await asyncio.sleep(10)
    
    async def process_research_request(self, message: Dict[str, Any]):
        """Process research request from users or other agents"""
        try:
            data = message.get('data', {})
            query = ResearchQuery(**data)
            
            logger.info(f"Processing research request: {query.query}")
            
            # Check cache first
            cache_key = f"research_{hash(query.query)}_{query.domain}_{query.depth}"
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                logger.info("Returning cached research result")
                await self.send_response(message, cached_result)
                return
            
            # Conduct research
            result = await self.conduct_research(query)
            
            # Cache result
            await self.cache_manager.set(cache_key, result.__dict__, ttl=3600)  # 1 hour
            
            # Send response
            await self.send_response(message, result.__dict__)
            
            # Log research activity
            await self.log_research_activity(query, result)
            
        except Exception as e:
            logger.error(f"Error processing research request: {e}")
            await self.send_error_response(message, str(e))
    
    async def conduct_research(self, query: ResearchQuery) -> ResearchResult:
        """Conduct comprehensive research on the given query"""
        try:
            # Determine research domain
            domain_info = self.research_domains.get(query.domain, self.research_domains["general"])
            
            # Generate research prompt
            research_prompt = self._build_research_prompt(query, domain_info)
            
            # Get research insights from Gemini
            research_response = await self.gemini_client.generate_content(
                prompt=research_prompt,
                system_instruction=self._get_research_system_instruction(),
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=3000
            )
            
            # Parse research response
            research_data = await self._parse_research_response(research_response)
            
            # Generate citations
            citations = await self._generate_citations(research_data, domain_info["citation_style"])
            
            # Find related topics
            related_topics = await self._find_related_topics(query.query, query.domain)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(research_data)
            
            return ResearchResult(
                query=query.query,
                summary=research_data.get("summary", ""),
                key_findings=research_data.get("key_findings", []),
                sources=research_data.get("sources", []),
                citations=citations,
                related_topics=related_topics,
                confidence_score=confidence_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error conducting research: {e}")
            raise
    
    def _build_research_prompt(self, query: ResearchQuery, domain_info: Dict) -> str:
        """Build comprehensive research prompt"""
        depth_instructions = {
            "basic": "Provide a concise overview with 3-5 key points",
            "moderate": "Provide a comprehensive analysis with detailed explanations",
            "comprehensive": "Provide an in-depth analysis with multiple perspectives and detailed evidence"
        }
        
        return f"""
        Conduct academic research on: "{query.query}"
        
        Research Parameters:
        - Domain: {query.domain}
        - Depth: {query.depth} ({depth_instructions.get(query.depth, "moderate")})
        - Focus keywords: {', '.join(domain_info['keywords'])}
        - Preferred sources: {', '.join(domain_info['sources'])}
        
        Please provide:
        1. Executive Summary (2-3 paragraphs)
        2. Key Findings (5-10 bullet points)
        3. Relevant Sources (with titles, authors, and brief descriptions)
        4. Methodological Insights
        5. Current Research Gaps
        6. Future Research Directions
        
        Format your response as structured JSON with the following keys:
        - summary: string
        - key_findings: array of strings
        - sources: array of objects with {title, authors, description, relevance_score}
        - methodology: string
        - research_gaps: array of strings
        - future_directions: array of strings
        """
    
    def _get_research_system_instruction(self) -> str:
        """Get system instruction for research tasks"""
        return """
        You are an expert academic researcher with access to comprehensive knowledge across multiple disciplines.
        
        Guidelines:
        - Provide accurate, evidence-based information
        - Cite credible academic sources when possible
        - Acknowledge limitations and uncertainties
        - Use appropriate academic language and terminology
        - Structure information logically and clearly
        - Focus on peer-reviewed and authoritative sources
        - Provide balanced perspectives on controversial topics
        """
    
    async def _parse_research_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini research response"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: parse structured text
                return await self._parse_structured_text(response)
                
        except json.JSONDecodeError:
            return await self._parse_structured_text(response)
    
    async def _parse_structured_text(self, text: str) -> Dict[str, Any]:
        """Parse structured text response when JSON parsing fails"""
        # Use Gemini to convert unstructured response to structured data
        parsing_prompt = f"""
        Convert the following research response into structured JSON format:
        
        {text}
        
        Required JSON structure:
        {{
            "summary": "executive summary text",
            "key_findings": ["finding 1", "finding 2", ...],
            "sources": [{{"title": "title", "authors": "authors", "description": "desc", "relevance_score": 0.8}}],
            "methodology": "methodology description",
            "research_gaps": ["gap 1", "gap 2", ...],
            "future_directions": ["direction 1", "direction 2", ...]
        }}
        """
        
        structured_response = await self.gemini_client.generate_content(
            prompt=parsing_prompt,
            temperature=0.1
        )
        
        try:
            return json.loads(structured_response)
        except:
            # Ultimate fallback
            return {
                "summary": text[:500] + "...",
                "key_findings": ["Research analysis completed"],
                "sources": [],
                "methodology": "Comprehensive literature review",
                "research_gaps": [],
                "future_directions": []
            }
    
    async def _generate_citations(self, research_data: Dict, citation_style: str) -> List[str]:
        """Generate properly formatted citations"""
        citations = []
        
        for source in research_data.get("sources", []):
            citation_prompt = f"""
            Generate a properly formatted {citation_style} citation for:
            Title: {source.get('title', 'Unknown')}
            Authors: {source.get('authors', 'Unknown')}
            Description: {source.get('description', '')}
            
            Provide only the citation text, no additional formatting.
            """
            
            citation = await self.gemini_client.generate_content(
                prompt=citation_prompt,
                temperature=0.1,
                max_tokens=200
            )
            
            citations.append(citation.strip())
        
        return citations
    
    async def _find_related_topics(self, query: str, domain: str) -> List[str]:
        """Find related research topics"""
        related_prompt = f"""
        Given the research query: "{query}" in the domain of {domain},
        suggest 5-7 related topics that would be valuable for further research.
        
        Provide only the topic names, one per line, without numbering or bullets.
        """
        
        response = await self.gemini_client.generate_content(
            prompt=related_prompt,
            temperature=0.4,
            max_tokens=300
        )
        
        return [topic.strip() for topic in response.split('\n') if topic.strip()]
    
    async def _calculate_confidence_score(self, research_data: Dict) -> float:
        """Calculate confidence score based on research quality"""
        score = 0.5  # Base score
        
        # Adjust based on number of sources
        num_sources = len(research_data.get("sources", []))
        if num_sources >= 5:
            score += 0.2
        elif num_sources >= 3:
            score += 0.1
        
        # Adjust based on key findings
        num_findings = len(research_data.get("key_findings", []))
        if num_findings >= 7:
            score += 0.2
        elif num_findings >= 5:
            score += 0.1
        
        # Adjust based on methodology description
        if research_data.get("methodology") and len(research_data["methodology"]) > 100:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def process_citation_request(self, message: Dict[str, Any]):
        """Process citation formatting request"""
        try:
            data = message.get('data', {})
            sources = data.get('sources', [])
            citation_style = data.get('style', 'APA')
            
            citations = []
            for source in sources:
                citation = await self._generate_citations([source], citation_style)
                citations.extend(citation)
            
            await self.send_response(message, {
                'citations': citations,
                'style': citation_style,
                'count': len(citations)
            })
            
        except Exception as e:
            logger.error(f"Error processing citation request: {e}")
            await self.send_error_response(message, str(e))
    
    async def process_trend_analysis(self, message: Dict[str, Any]):
        """Process research trend analysis request"""
        try:
            data = message.get('data', {})
            domain = data.get('domain', 'general')
            timeframe = data.get('timeframe', '5 years')
            
            trend_prompt = f"""
            Analyze current research trends in {domain} over the past {timeframe}.
            
            Provide:
            1. Emerging research areas
            2. Declining research interests
            3. Hot topics and breakthrough areas
            4. Methodological trends
            5. Future predictions
            
            Format as JSON with keys: emerging_areas, declining_areas, hot_topics, methodological_trends, predictions
            """
            
            response = await self.gemini_client.generate_content(
                prompt=trend_prompt,
                system_instruction=self._get_research_system_instruction(),
                temperature=0.4,
                max_tokens=2000
            )
            
            trend_data = await self._parse_research_response(response)
            
            await self.send_response(message, trend_data)
            
        except Exception as e:
            logger.error(f"Error processing trend analysis: {e}")
            await self.send_error_response(message, str(e))
    
    async def log_research_activity(self, query: ResearchQuery, result: ResearchResult):
        """Log research activity for analytics"""
        try:
            activity_data = {
                'agent_id': self.agent_id,
                'activity_type': 'research_conducted',
                'user_id': query.user_id,
                'course_id': query.course_id,
                'query': query.query,
                'domain': query.domain,
                'depth': query.depth,
                'confidence_score': result.confidence_score,
                'sources_found': len(result.sources),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.log_activity(activity_data)
            
        except Exception as e:
            logger.error(f"Error logging research activity: {e}")

# Agent factory function
def create_research_agent() -> ResearchAgent:
    """Create and return a Research Agent instance"""
    return ResearchAgent()
