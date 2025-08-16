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
    # Gemini Models
    gemini_generation_model: str
    gemini_embedding_model: str
    
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
        # Primary Gemini Models - use environment variables with defaults
        gemini_generation_model=os.getenv('GEMINI_GENERATION_MODEL', 'models/gemini-2.5-flash'),
        gemini_embedding_model=os.getenv('GEMINI_EMBEDDING_MODEL', 'models/text-embedding-004'),
        
        # Model Parameters
        max_tokens=int(os.getenv('GEMINI_MAX_TOKENS', '8192')),
        temperature=float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
        top_p=float(os.getenv('GEMINI_TOP_P', '0.95')),
        
        # Rate Limiting
        requests_per_minute=int(os.getenv('GEMINI_REQUESTS_PER_MINUTE', '60')),
        max_retries=int(os.getenv('GEMINI_MAX_RETRIES', '3')),
        
        # Fallback Models
        fallback_generation_model=os.getenv('GEMINI_FALLBACK_MODEL', 'models/gemini-1.5-flash')
    )

# Global configuration instance
AI_CONFIG = get_ai_model_config()

# Convenience constants for backward compatibility
GEMINI_GENERATION_MODEL = AI_CONFIG.gemini_generation_model
GEMINI_EMBEDDING_MODEL = AI_CONFIG.gemini_embedding_model

def get_model_info() -> Dict[str, Any]:
    """Get current model configuration info for diagnostics"""
    return {
        "generation_model": AI_CONFIG.gemini_generation_model,
        "embedding_model": AI_CONFIG.gemini_embedding_model,
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
