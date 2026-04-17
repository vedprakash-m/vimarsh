"""
Azure OpenAI Chat Service for GPT-5-mini and other chat models
Handles chat completion with retry logic and error handling
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """Chat response with metadata"""
    text: str
    model: str
    tokens_used: int
    finish_reason: str
    response_time: float


class AzureOpenAIChatService:
    """Azure OpenAI chat service with retry logic for GPT models"""
    
    def __init__(self, test_mode: bool = False):
        """Initialize Azure OpenAI chat service"""
        self.test_mode = test_mode
        
        # Configuration — prefer the unified AZURE_OPENAI_* vars (used by embedding/RAG)
        # so that chat and embeddings share the same endpoint and API key.
        self.endpoint = (
            os.getenv('AZURE_OPENAI_CHAT_ENDPOINT')
            or os.getenv('AZURE_OPENAI_ENDPOINT')
            or 'https://vimarsh-openai.openai.azure.com'
        )
        self.api_key = (
            os.getenv('AZURE_OPENAI_CHAT_API_KEY')
            or os.getenv('AZURE_OPENAI_API_KEY')
            or ''
        )
        self.deployment_name = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT', 'gpt-5.4-mini')
        self.model_name = os.getenv('AZURE_OPENAI_CHAT_MODEL', 'gpt-5.4-mini')
        self.api_version = os.getenv('AZURE_OPENAI_CHAT_API_VERSION', os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'))
        
        # Retry configuration
        self.max_retries = 5
        self.retry_base_delay = 1.0  # seconds
        self.retry_multiplier = 2.0  # exponential backoff
        
        if not self.test_mode:
            if not self.api_key:
                logger.error("❌ AZURE_OPENAI_CHAT_API_KEY not set")
                raise ValueError("AZURE_OPENAI_CHAT_API_KEY is required")
            
            try:
                # Clean endpoint: AzureOpenAI client expects 'https://{resource}.openai.azure.com/'
                # If the env var has /openai/v1, strip it to prevent 404s with double-pathing
                clean_endpoint = self.endpoint
                if '/openai/v1' in clean_endpoint:
                    clean_endpoint = clean_endpoint.split('/openai/v1')[0]
                
                self.client = AzureOpenAI(
                    azure_endpoint=clean_endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version
                )
                logger.info(f"✅ Azure OpenAI Chat service initialized: {self.deployment_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Azure OpenAI client: {e}")
                raise
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.95
    ) -> ChatResponse:
        """
        Generate chat response with retry logic
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0-2) for response generation
            max_tokens: Maximum output tokens (mapped to max_completion_tokens for GPT-5-mini)
            top_p: Nucleus sampling parameter
            
        Returns:
            ChatResponse with text and metadata
        """
        if self.test_mode:
            return self._generate_test_response(messages)
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # GPT-5-mini: only supports max_completion_tokens, temperature=1, no top_p
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=1  # GPT-5-mini only supports temperature=1
                )
                
                response_time = time.time() - start_time
                
                return ChatResponse(
                    text=response.choices[0].message.content,
                    model=self.model_name,
                    tokens_used=response.usage.total_tokens,
                    finish_reason=response.choices[0].finish_reason,
                    response_time=response_time
                )
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # Check if it's a rate limit error
                if "429" in error_msg or "rate" in error_msg.lower():
                    delay = self.retry_base_delay * (self.retry_multiplier ** attempt)
                    logger.warning(f"⏳ Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                    continue
                
                # For other errors, retry with shorter delay
                if attempt < self.max_retries - 1:
                    delay = self.retry_base_delay
                    logger.warning(f"⚠️ Error: {error_msg}, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"❌ All retries exhausted: {error_msg}")
                    raise
        
        # If we get here, all retries failed
        raise Exception(f"Failed to generate response after {self.max_retries} attempts: {last_error}")

    def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: int = 2000
    ):
        """
        Generate streaming chat response for GPT-5-mini
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (GPT-5-mini expects 1)
            max_tokens: Maximum output tokens
            
        Yields:
            Chunks of text as they are generated
        """
        if self.test_mode:
            yield "This is a test streaming response from Azure OpenAI GPT-5-mini"
            return

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=max_tokens,
                temperature=1,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"❌ Streaming completion error: {e}")
            raise
    
    def _generate_test_response(self, messages: List[Dict[str, str]]) -> ChatResponse:
        """Generate test response for unit testing"""
        return ChatResponse(
            text="This is a test response from Azure OpenAI GPT-5-mini",
            model=self.model_name,
            tokens_used=100,
            finish_reason="stop",
            response_time=0.5
        )
    
    def calculate_cost(self, tokens: int) -> float:
        """
        Calculate cost for GPT-5-mini
        Pricing: $0.69/1M tokens (approximate)
        
        Args:
            tokens: Total tokens used
            
        Returns:
            Cost in USD
        """
        cost_per_million = 0.69
        return (tokens / 1_000_000) * cost_per_million


# Singleton instance
_chat_service_instance: Optional[AzureOpenAIChatService] = None


def get_azure_chat_service(test_mode: bool = False) -> AzureOpenAIChatService:
    """Get singleton Azure OpenAI chat service instance"""
    global _chat_service_instance
    
    if _chat_service_instance is None:
        _chat_service_instance = AzureOpenAIChatService(test_mode=test_mode)
    
    return _chat_service_instance
