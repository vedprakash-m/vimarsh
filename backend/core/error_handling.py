"""
Minimal Error Handling for Vimarsh

This module provides basic error handling for the spiritual guidance system,
replacing the over-engineered error handling system that was archived.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Basic error categories"""
    USER_INPUT = "user_input"
    LLM_ERROR = "llm_error" 
    NETWORK_ERROR = "network_error"
    SYSTEM_ERROR = "system_error"


@dataclass
class ErrorInfo:
    """Basic error information"""
    category: ErrorCategory
    message: str
    details: Optional[Dict[str, Any]] = None


class BasicErrorHandler:
    """Simple error handler for the spiritual guidance system"""
    
    def __init__(self):
        self.error_count = 0
        
    def handle_error(self, error: Exception, category: ErrorCategory = ErrorCategory.SYSTEM_ERROR) -> ErrorInfo:
        """Handle an error with basic logging and categorization"""
        self.error_count += 1
        
        error_info = ErrorInfo(
            category=category,
            message=str(error),
            details={
                "type": type(error).__name__,
                "error_count": self.error_count
            }
        )
        
        logger.error(f"Error handled - {category.value}: {error_info.message}")
        return error_info
    
    def get_simple_fallback_response(self, error_category: ErrorCategory) -> str:
        """Get a simple fallback response for errors"""
        fallback_responses = {
            ErrorCategory.LLM_ERROR: "🙏 I'm experiencing technical difficulties accessing spiritual wisdom right now. Please try again in a moment. (Backend Core Error)",
            ErrorCategory.NETWORK_ERROR: "🙏 There seems to be a connection issue. Please check your network and try again.",
            ErrorCategory.USER_INPUT: "🙏 I couldn't understand your question. Could you please rephrase it?",
            ErrorCategory.SYSTEM_ERROR: "🙏 I'm experiencing technical difficulties. Please try again later."
        }
        return fallback_responses.get(error_category, fallback_responses[ErrorCategory.SYSTEM_ERROR])


# Global error handler instance
error_handler = BasicErrorHandler()


def handle_api_error(func):
    """Simple decorator for API error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = error_handler.handle_error(e)
            return {
                "error": True,
                "message": error_handler.get_simple_fallback_response(error_info.category),
                "details": error_info.details
            }
    return wrapper


async def handle_async_api_error(func):
    """Simple decorator for async API error handling"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_info = error_handler.handle_error(e)
            return {
                "error": True, 
                "message": error_handler.get_simple_fallback_response(error_info.category),
                "details": error_info.details
            }
    return wrapper
