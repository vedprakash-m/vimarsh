"""
Core module for Vimarsh backend services
Provides centralized configuration, error handling, logging, health checks, and common utilities
"""

from .config import (
    ConfigManager,
    Environment,
    LogLevel,
    AzureConfig,
    LLMConfig,
    AuthConfig,
    MonitoringConfig,
    SecurityConfig,
    ApplicationConfig,
    config,
    get_config,
    reload_config
)

from .logging import (
    StructuredLogger,
    LogContext,
    PerformanceMetrics,
    EventType,
    get_logger,
    spiritual_logger,
    auth_logger,
    db_logger,
    api_logger,
    health_logger,
    security_logger
)

from .health import (
    HealthChecker,
    HealthStatus,
    ComponentType,
    HealthCheckResult,
    SystemHealthSummary,
    health_checker,
    get_health_checker
)

__all__ = [
    # Configuration
    "ConfigManager",
    "Environment", 
    "LogLevel",
    "AzureConfig",
    "LLMConfig", 
    "AuthConfig",
    "MonitoringConfig",
    "SecurityConfig",
    "ApplicationConfig",
    "config",
    "get_config",
    "reload_config",
    
    # Logging
    "StructuredLogger",
    "LogContext",
    "PerformanceMetrics",
    "EventType",
    "get_logger",
    "spiritual_logger",
    "auth_logger",
    "db_logger",
    "api_logger",
    "health_logger",
    "security_logger",
    
    # Health Checks
    "HealthChecker",
    "HealthStatus",
    "ComponentType",
    "HealthCheckResult",
    "SystemHealthSummary",
    "health_checker",
    "get_health_checker"
]
