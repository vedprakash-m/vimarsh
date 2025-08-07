"""
Services module for Vimarsh backend
Provides database, LLM, and transaction management services
"""

# Import key services for easier access
from .database_service import DatabaseService, db_service
from .llm_service import LLMService
from .personality_service import PersonalityService
from .admin_service import AdminService
from .safety_service import SafetyService
from .transaction_manager import DatabaseTransactionManager

# Backward compatibility aliases
EnhancedSimpleLLMService = LLMService
OptimizedPersonalityService = PersonalityService

__all__ = [
    'DatabaseService',
    'db_service', 
    'LLMService',
    'PersonalityService', 
    'AdminService',
    'SafetyService',
    'DatabaseTransactionManager',
    # Aliases for backward compatibility
    'EnhancedSimpleLLMService',
    'OptimizedPersonalityService'
]
