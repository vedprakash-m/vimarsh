#!/usr/bin/env python3
"""
AI Model Configuration
Centralized configuration for AI models to avoid fragmentation
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class AIModelConfig:
    """Configuration for AI models"""
    # Gemini Models (Generation only)
    gemini_generation_model: str
    
    # Azure OpenAI Embedding Configuration
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_embedding_deployment: str
    azure_openai_api_version: str
    embedding_output_dimensionality: int  # 768 dimensions for Cosmos DB compatibility
    
    # Model Parameters
    max_tokens: int
    temperature: float
    top_p: float
    
    # Rate Limiting
    requests_per_minute: int
    max_retries: int
    
    # Fallback Models
    fallback_generation_model: str

def get_ai_model_config() -> AIModelConfig:
    """Get AI model configuration from environment variables with sensible defaults"""
    
    return AIModelConfig(
        # Primary Gemini Model for generation
        gemini_generation_model=os.getenv('GEMINI_GENERATION_MODEL', 'models/gemini-2.5-flash'),
        
        # Azure OpenAI Embedding Configuration
        azure_openai_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT', ''),
        azure_openai_api_key=os.getenv('AZURE_OPENAI_API_KEY', ''),
        azure_openai_embedding_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'vimarsh-embedding-large'),
        azure_openai_api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'),
        embedding_output_dimensionality=int(os.getenv('EMBEDDING_OUTPUT_DIMENSIONALITY', '768')),
        
        # Model Parameters
        max_tokens=int(os.getenv('GEMINI_MAX_TOKENS', '8192')),
        temperature=float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
        top_p=float(os.getenv('GEMINI_TOP_P', '0.95')),
        
        # Rate Limiting
        requests_per_minute=int(os.getenv('AZURE_OPENAI_REQUESTS_PER_MINUTE', '100')),
        max_retries=int(os.getenv('AZURE_OPENAI_MAX_RETRIES', '3')),
        
        # Fallback Models
        fallback_generation_model=os.getenv('GEMINI_FALLBACK_MODEL', 'models/gemini-1.5-flash')
    )

# Global configuration instance
AI_CONFIG = get_ai_model_config()

# Convenience constants for backward compatibility
GEMINI_GENERATION_MODEL = AI_CONFIG.gemini_generation_model
AZURE_OPENAI_ENDPOINT = AI_CONFIG.azure_openai_endpoint
AZURE_OPENAI_API_KEY = AI_CONFIG.azure_openai_api_key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = AI_CONFIG.azure_openai_embedding_deployment
AZURE_OPENAI_API_VERSION = AI_CONFIG.azure_openai_api_version
EMBEDDING_OUTPUT_DIMENSIONALITY = AI_CONFIG.embedding_output_dimensionality

def get_model_info() -> Dict[str, Any]:
    """Get current model configuration info for diagnostics"""
    return {
        "generation_model": AI_CONFIG.gemini_generation_model,
        "embedding_model": AI_CONFIG.gemini_embedding_model,
        "embedding_dimensionality": AI_CONFIG.embedding_output_dimensionality,
        "fallback_model": AI_CONFIG.fallback_generation_model,
        "parameters": {
            "max_tokens": AI_CONFIG.max_tokens,
            "temperature": AI_CONFIG.temperature,
            "top_p": AI_CONFIG.top_p
        },
        "rate_limits": {
            "requests_per_minute": AI_CONFIG.requests_per_minute,
            "max_retries": AI_CONFIG.max_retries
        }
    }

def update_model_config(**kwargs) -> None:
    """Update model configuration at runtime (for testing/admin purposes)"""
    global AI_CONFIG
    for key, value in kwargs.items():
        if hasattr(AI_CONFIG, key):
            setattr(AI_CONFIG, key, value)
        else:
            raise ValueError(f"Invalid configuration key: {key}")
