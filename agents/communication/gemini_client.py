"""
Google Gemini client for EduLMS v2 AI agents
Provides unified interface for Gemini API calls across all agents
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """Unified Gemini client for all EduLMS agents"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model = os.getenv('GOOGLE_GEMINI_MODEL', 'gemini-2.0-flash-001')
        self.embedding_model = os.getenv('GOOGLE_GEMINI_EMBEDDING_MODEL', 'text-embedding-004')
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize client
        self.client = genai.Client(api_key=self.api_key)
        
        # Default generation config
        self.default_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                )
            ]
        )
    
    async def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate content using Gemini model"""
        try:
            # Prepare config
            config = self.default_config
            if temperature is not None:
                config.temperature = temperature
            if max_tokens is not None:
                config.max_output_tokens = max_tokens
            
            # Prepare contents
            contents = [prompt]
            
            # Add system instruction if provided
            if system_instruction:
                config.system_instruction = system_instruction
            
            # Generate content
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=contents,
                config=config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
    
    async def generate_content_stream(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        **kwargs
    ):
        """Generate streaming content using Gemini model"""
        try:
            config = self.default_config
            if system_instruction:
                config.system_instruction = system_instruction
            
            contents = [prompt]
            
            # Generate streaming content
            stream = await asyncio.to_thread(
                self.client.models.generate_content_stream,
                model=self.model,
                contents=contents,
                config=config
            )
            
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error generating streaming content: {e}")
            raise
    
    async def generate_embeddings(
        self, 
        texts: Union[str, List[str]],
        task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> List[List[float]]:
        """Generate embeddings using Gemini embedding model"""
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = []
            for text in texts:
                response = await asyncio.to_thread(
                    self.client.models.embed_content,
                    model=self.embedding_model,
                    contents=[text],
                    task_type=task_type
                )
                embeddings.append(response.embeddings[0].values)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> str:
        """Chat completion interface compatible with existing agent code"""
        try:
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                if msg['role'] == 'user':
                    contents.append(msg['content'])
                elif msg['role'] == 'assistant':
                    # For conversation history, we might need to handle this differently
                    # For now, we'll include it as context
                    contents.append(f"Assistant: {msg['content']}")
            
            # Use the last user message as the main prompt
            prompt = contents[-1] if contents else ""
            
            return await self.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    async def function_calling(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Function calling with Gemini"""
        try:
            # Convert functions to Gemini format
            tools = []
            for func in functions:
                tool = types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=func['name'],
                            description=func['description'],
                            parameters=func.get('parameters', {})
                        )
                    ]
                )
                tools.append(tool)
            
            config = self.default_config
            config.tools = tools
            if system_instruction:
                config.system_instruction = system_instruction
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=[prompt],
                config=config
            )
            
            # Parse function calls from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call'):
                        return {
                            'function_call': {
                                'name': part.function_call.name,
                                'arguments': dict(part.function_call.args)
                            }
                        }
            
            return {'text': response.text}
            
        except Exception as e:
            logger.error(f"Error in function calling: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model': self.model,
            'embedding_model': self.embedding_model,
            'provider': 'Google Gemini',
            'api_version': 'v1'
        }

# Global client instance
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create global Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

# Compatibility functions for existing agent code
async def create_chat_completion(messages, **kwargs):
    """Compatibility function for existing OpenAI-style calls"""
    client = get_gemini_client()
    return await client.chat_completion(messages, **kwargs)

async def create_embedding(text, **kwargs):
    """Compatibility function for existing OpenAI-style embedding calls"""
    client = get_gemini_client()
    embeddings = await client.generate_embeddings(text, **kwargs)
    return embeddings[0] if embeddings else []
