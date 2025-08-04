"""
AI Service - Hybrid AI Integration

Implements the hybrid AI approach outlined in PROJECT_OVERVIEW.md:
- Primary: OpenAI API (GPT-4/GPT-3.5) for complex reasoning
- Local Backup: Smaller local models for basic tasks and privacy
- Model management for RTX 2060 Super (8GB VRAM)
"""

from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime

import openai
from openai.types.chat import ChatCompletionMessageParam
import ollama

from crystal.utils.logging import CrystalLogger
from config.settings import settings

class AIService:
    """
    Hybrid AI service supporting both OpenAI API and local models via Ollama.
    
    Implements the AI strategy from PROJECT_OVERVIEW.md:
    - Use local models first if available and suitable
    - Fall back to OpenAI API for complex tasks
    - Optimize for RTX 2060 Super hardware constraints
    """
    
    def __init__(self):
        self.logger = CrystalLogger("ai_service")
        self.openai_client: Optional[openai.AsyncOpenAI] = None
        self.ollama_client = None
        self.available_local_models: List[str] = []
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize AI service with both OpenAI and Ollama."""
        if self.is_initialized:
            return
        
        self.logger.system_event("ai_service_initialization")
        
        # Initialize OpenAI client if API key is available
        if settings.openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            self.logger.info("openai_client_initialized")
        else:
            self.logger.warning("openai_api_key_not_configured")
        
        # Initialize Ollama client
        try:
            self.ollama_client = ollama.AsyncClient(host=settings.ollama_host)
            
            # Check available local models
            models_response = await self.ollama_client.list()
            self.available_local_models = [model['name'] for model in models_response.get('models', [])]
            
            self.logger.info(
                "ollama_client_initialized", 
                available_models=self.available_local_models
            )
            
        except Exception as e:
            self.logger.warning("ollama_initialization_failed", error=str(e))
            self.ollama_client = None
        
        self.is_initialized = True
        self.logger.system_event("ai_service_ready")
    
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate AI response using hybrid approach.
        
        Args:
            message: User message or prompt
            model: Preferred model (will auto-select if None)
            context: Additional context for the conversation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Auto-select model if not specified
        if not model:
            model = await self._select_optimal_model(message, context)
        
        self.logger.assistant_action(
            assistant="ai_service",
            action="generate_response_started",
            model=model,
            message_length=len(message)
        )
        
        try:
            # Try local model first if available and configured
            if settings.use_local_first and self._is_local_model(model):
                if model in self.available_local_models:
                    response = await self._generate_local_response(message, model, context, max_tokens)
                    if response:
                        return response
                
                # Fall back to API if local fails and fallback is enabled
                if settings.fallback_to_api and self.openai_client:
                    self.logger.info("falling_back_to_openai_api")
                    return await self._generate_openai_response(message, settings.openai_model, context, max_tokens)
            
            # Use OpenAI API directly
            elif self.openai_client and self._is_openai_model(model):
                return await self._generate_openai_response(message, model, context, max_tokens)
            
            # Try local as last resort
            elif self.ollama_client and self.available_local_models:
                local_model = self.available_local_models[0]  # Use first available
                response = await self._generate_local_response(message, local_model, context, max_tokens)
                if response:
                    return response
            
            # No AI service available
            return "I'm sorry, but I'm unable to process your request right now. Please check the AI service configuration."
            
        except Exception as e:
            self.logger.error("ai_response_generation_failed", error=str(e))
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def _generate_local_response(
        self,
        message: str,
        model: str,
        context: Optional[Dict[str, Any]],
        max_tokens: Optional[int]
    ) -> Optional[str]:
        """Generate response using local Ollama model."""
        if not self.ollama_client:
            return None
        
        try:
            # Build prompt with context
            prompt = self._build_prompt(message, context)
            
            response = await self.ollama_client.generate(
                model=model,
                prompt=prompt,
                options={
                    'num_predict': max_tokens or settings.openai_max_tokens,
                    'temperature': 0.7
                }
            )
            
            self.logger.assistant_action(
                assistant="ai_service",
                action="local_response_generated",
                model=model
            )
            
            return response['response']
            
        except Exception as e:
            self.logger.error("local_model_generation_failed", model=model, error=str(e))
            return None
    
    async def _generate_openai_response(
        self,
        message: str,
        model: str,
        context: Optional[Dict[str, Any]],
        max_tokens: Optional[int]
    ) -> str:
        """Generate response using OpenAI API."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        # Build messages for chat completion
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are a helpful personal assistant named Ruby."}
        ]
        
        # Add context if provided
        if context and context.get('conversation_history'):
            for msg in context['conversation_history']:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append({
                        "role": msg['role'],  # type: ignore
                        "content": str(msg['content'])
                    })
        
        messages.append({"role": "user", "content": message})
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens or settings.openai_max_tokens,
            temperature=0.7
        )
        
        self.logger.assistant_action(
            assistant="ai_service",
            action="openai_response_generated",
            model=model
        )
        
        content = response.choices[0].message.content
        return content if content is not None else "I apologize, but I couldn't generate a response."
    
    async def _select_optimal_model(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """Select the optimal model based on message complexity and available resources."""
        
        # Simple heuristics for model selection
        message_length = len(message)
        
        # For complex tasks, prefer OpenAI if available
        if message_length > 500 or any(word in message.lower() for word in ['analyze', 'complex', 'detailed']):
            if self.openai_client:
                return settings.openai_model
        
        # For simple tasks, prefer local model
        if self.available_local_models:
            return settings.default_local_model
        
        # Default to OpenAI
        return settings.openai_model
    
    def _is_local_model(self, model: str) -> bool:
        """Check if model is a local Ollama model."""
        return ':' in model or model in self.available_local_models
    
    def _is_openai_model(self, model: str) -> bool:
        """Check if model is an OpenAI model."""
        return model.startswith('gpt-') or model in ['gpt-3.5-turbo', 'gpt-4']
    
    def _build_prompt(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """Build prompt with context for local models."""
        prompt = ""
        
        if context and context.get('conversation_history'):
            prompt += "Previous conversation:\n"
            for msg in context['conversation_history'][-3:]:  # Last 3 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt += f"{role}: {content}\n"
            prompt += "\n"
        
        prompt += f"User: {message}\nAssistant:"
        return prompt
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models."""
        return {
            "local_models": self.available_local_models,
            "openai_available": self.openai_client is not None,
            "default_local": settings.default_local_model,
            "default_openai": settings.openai_model
        }
    
    async def shutdown(self) -> None:
        """Shutdown AI service."""
        self.logger.system_event("ai_service_shutdown")
        # Cleanup if needed
