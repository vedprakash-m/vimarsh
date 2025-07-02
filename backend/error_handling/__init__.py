"""
Error Handling System for Vimarsh AI Agent

This package provides comprehensive error handling, recovery, and monitoring
capabilities for the spiritual guidance system.

Key Components:
- Error Classification and Analysis
- Graceful Degradation Management
- Intelligent Retry Mechanisms
- LLM Fallback System
- Circuit Breaker Pattern
- Error Analytics and Monitoring
"""

from typing import Optional, Dict, Any

# Core error handling components
from .error_classifier import (
    ErrorCategory,
    ErrorSeverity, 
    ErrorSource,
    ErrorContext,
    ClassifiedError,
    ErrorClassifier
)

from .graceful_degradation import (
    DegradationLevel,
    ServiceType,
    DegradationStrategy,
    GracefulDegradationManager
)

from .intelligent_retry import (
    BackoffStrategy,
    RetryConfig,
    RetryAttempt,
    IntelligentRetryManager
)

from .llm_fallback import (
    FallbackTrigger,
    FallbackResponse,
    TemplatePattern,
    SpiritualQuery,
    LLMFallbackSystem
)

from .circuit_breaker import (
    CircuitState,
    CircuitBreakerConfig,
    HealthCheckConfig,
    CircuitBreakerError,
    HealthAndCircuitMonitor
)

from .error_analytics import (
    ErrorEvent,
    ErrorPattern,
    SystemHealthMetrics,
    ErrorAnalytics
)

from .error_recovery_testing import (
    TestScenario,
    TestResult,
    TestConfiguration,
    TestMetrics,
    TestReport,
    ErrorRecoveryTester
)

# Version information
__version__ = "1.0.0"
__author__ = "Vimarsh AI Team"

# Default configuration
DEFAULT_ERROR_CONFIG = {
    "retry": {
        "max_attempts": 3,
        "base_delay": 1.0,
        "max_delay": 60.0,
        "backoff_strategy": "exponential"
    },
    "circuit_breaker": {
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "half_open_max_calls": 3
    },
    "fallback": {
        "enable_external_llm": True,
        "cache_responses": True,
        "template_confidence_threshold": 0.7
    },
    "analytics": {
        "max_events": 10000,
        "pattern_detection_window": 3600
    }
}

def create_error_handling_system(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Factory function to create a complete error handling system.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing all error handling components
    """
    if config is None:
        config = DEFAULT_ERROR_CONFIG.copy()
    
    # Initialize components
    error_classifier = ErrorClassifier()
    degradation_manager = GracefulDegradationManager()
    retry_manager = IntelligentRetryManager()  # Fixed: IntelligentRetryManager doesn't take config in __init__
    fallback_system = LLMFallbackSystem(
        enable_external_llm=config.get("fallback", {}).get("enable_external_llm", True)
    )
    
    analytics_config = config.get("analytics", {})
    analytics_system = ErrorAnalytics(
        max_events=analytics_config.get("max_events", 10000),
        pattern_detection_window=analytics_config.get("pattern_detection_window", 3600)
    )
    
    return {
        "classifier": error_classifier,
        "degradation_manager": degradation_manager,
        "retry_manager": retry_manager,
        "fallback_system": fallback_system,
        "analytics": analytics_system,
        "config": config
    }

# Utility functions for error handling
def get_service_status(service_name: str) -> Dict[str, Any]:
    """Get the current status of a service."""
    # This will be implemented to check actual service health
    return {
        "name": service_name,
        "status": "unknown",
        "last_check": None,
        "error_count": 0
    }

# Export all public components
__all__ = [
    # Error Classification
    "ErrorCategory",
    "ErrorSeverity", 
    "ErrorSource",
    "ErrorContext",
    "ClassifiedError",
    "ErrorClassifier",
    
    # Graceful Degradation
    "DegradationLevel",
    "ServiceType",
    "DegradationStrategy",
    "GracefulDegradationManager",
    
    # Intelligent Retry
    "BackoffStrategy",
    "RetryConfig",
    "RetryAttempt",
    "IntelligentRetryManager",
    
    # LLM Fallback
    "FallbackTrigger",
    "FallbackResponse", 
    "TemplatePattern",
    "SpiritualQuery",
    "LLMFallbackSystem",
    
    # Circuit Breaker
    "CircuitState",
    "CircuitBreakerConfig",
    "HealthCheckConfig",
    "CircuitBreakerError",
    "HealthAndCircuitMonitor",
    
    # Analytics
    "ErrorEvent",
    "ErrorPattern",
    "SystemHealthMetrics",
    "ErrorAnalytics",
    
    # Testing
    "TestScenario",
    "TestResult",
    "TestConfiguration",
    "TestMetrics",
    "TestReport",
    "ErrorRecoveryTester",
    
    # Factory and utilities
    "create_error_handling_system",
    "get_service_status",
    "DEFAULT_ERROR_CONFIG"
]
