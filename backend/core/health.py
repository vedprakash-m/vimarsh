"""
Health Check System for Vimarsh
Provides comprehensive health monitoring for all system components
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

# Import centralized configuration and logging
try:
    from backend.core.config import get_config
    from backend.core.logging import get_logger, LogContext, PerformanceMetrics, EventType, LogLevel
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Import service dependencies
try:
    from backend.services.llm_service import llm_service
    LLM_SERVICE_AVAILABLE = True
except ImportError:
    LLM_SERVICE_AVAILABLE = False

try:
    from backend.services.database_service import db_service
    DB_SERVICE_AVAILABLE = True
except ImportError:
    DB_SERVICE_AVAILABLE = False

logger = get_logger("vimarsh.health") if CONFIG_AVAILABLE else None


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ComponentType(Enum):
    """Types of system components"""
    LLM_SERVICE = "llm_service"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    STORAGE = "storage"
    EXTERNAL_API = "external_api"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    component: ComponentType
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "component": self.component.value,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms
        }


@dataclass
class SystemHealthSummary:
    """Overall system health summary"""
    overall_status: HealthStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    components: List[HealthCheckResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "overall_status": self.overall_status.value,
            "timestamp": self.timestamp.isoformat(),
            "components": [comp.to_dict() for comp in self.components],
            "healthy_components": len([c for c in self.components if c.status == HealthStatus.HEALTHY]),
            "total_components": len(self.components)
        }


class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        """Initialize health checker"""
        self.config = get_config() if CONFIG_AVAILABLE else None
        self.last_check_time = None
        self.cached_results = {}
        self.cache_duration = timedelta(minutes=5)  # Cache health results for 5 minutes
    
    def check_llm_service(self) -> HealthCheckResult:
        """Check LLM service health"""
        start_time = time.time()
        
        try:
            if not LLM_SERVICE_AVAILABLE:
                return HealthCheckResult(
                    component=ComponentType.LLM_SERVICE,
                    status=HealthStatus.CRITICAL,
                    message="LLM service not available",
                    details={"error": "Service not imported"}
                )
            
            # Check if service is configured
            if not llm_service.is_configured:
                return HealthCheckResult(
                    component=ComponentType.LLM_SERVICE,
                    status=HealthStatus.DEGRADED,
                    message="LLM service using fallback responses",
                    details={
                        "api_configured": False,
                        "fallback_mode": True,
                        "model_name": llm_service.get_model_info().get("model_name", "unknown")
                    },
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Test connection
            connection_test = llm_service.test_connection()
            
            if connection_test:
                return HealthCheckResult(
                    component=ComponentType.LLM_SERVICE,
                    status=HealthStatus.HEALTHY,
                    message="LLM service operational",
                    details={
                        "api_configured": True,
                        "connection_test": True,
                        "model_name": llm_service.get_model_info().get("model_name", "unknown")
                    },
                    response_time_ms=(time.time() - start_time) * 1000
                )
            else:
                return HealthCheckResult(
                    component=ComponentType.LLM_SERVICE,
                    status=HealthStatus.UNHEALTHY,
                    message="LLM service connection failed",
                    details={
                        "api_configured": True,
                        "connection_test": False,
                        "model_name": llm_service.get_model_info().get("model_name", "unknown")
                    },
                    response_time_ms=(time.time() - start_time) * 1000
                )
        
        except Exception as e:
            return HealthCheckResult(
                component=ComponentType.LLM_SERVICE,
                status=HealthStatus.CRITICAL,
                message=f"LLM service check failed: {str(e)}",
                details={"error": str(e)},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def check_database(self) -> HealthCheckResult:
        """Check database health"""
        start_time = time.time()
        
        try:
            if not DB_SERVICE_AVAILABLE:
                return HealthCheckResult(
                    component=ComponentType.DATABASE,
                    status=HealthStatus.CRITICAL,
                    message="Database service not available",
                    details={"error": "Service not imported"}
                )
            
            # Check database health
            health_status = db_service.health_check()
            
            if health_status.get("status") == "healthy":
                return HealthCheckResult(
                    component=ComponentType.DATABASE,
                    status=HealthStatus.HEALTHY,
                    message="Database operational",
                    details={
                        "storage_type": health_status.get("storage_type", "unknown"),
                        "record_count": health_status.get("record_count", 0),
                        "last_update": health_status.get("last_update")
                    },
                    response_time_ms=(time.time() - start_time) * 1000
                )
            else:
                return HealthCheckResult(
                    component=ComponentType.DATABASE,
                    status=HealthStatus.UNHEALTHY,
                    message="Database health check failed",
                    details=health_status,
                    response_time_ms=(time.time() - start_time) * 1000
                )
        
        except Exception as e:
            return HealthCheckResult(
                component=ComponentType.DATABASE,
                status=HealthStatus.CRITICAL,
                message=f"Database check failed: {str(e)}",
                details={"error": str(e)},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def check_authentication(self) -> HealthCheckResult:
        """Check authentication system health"""
        start_time = time.time()
        
        try:
            if not CONFIG_AVAILABLE:
                return HealthCheckResult(
                    component=ComponentType.AUTHENTICATION,
                    status=HealthStatus.CRITICAL,
                    message="Configuration not available",
                    details={"error": "Config not imported"}
                )
            
            auth_config = self.config.auth
            
            if not auth_config.enabled:
                return HealthCheckResult(
                    component=ComponentType.AUTHENTICATION,
                    status=HealthStatus.DEGRADED,
                    message="Authentication disabled",
                    details={
                        "enabled": False,
                        "development_mode": True
                    },
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check authentication configuration
            if auth_config.validate():
                return HealthCheckResult(
                    component=ComponentType.AUTHENTICATION,
                    status=HealthStatus.HEALTHY,
                    message="Authentication configured",
                    details={
                        "enabled": True,
                        "tenant_configured": bool(auth_config.tenant_id),
                        "client_configured": bool(auth_config.client_id)
                    },
                    response_time_ms=(time.time() - start_time) * 1000
                )
            else:
                return HealthCheckResult(
                    component=ComponentType.AUTHENTICATION,
                    status=HealthStatus.UNHEALTHY,
                    message="Authentication misconfigured",
                    details={
                        "enabled": True,
                        "validation_failed": True
                    },
                    response_time_ms=(time.time() - start_time) * 1000
                )
        
        except Exception as e:
            return HealthCheckResult(
                component=ComponentType.AUTHENTICATION,
                status=HealthStatus.CRITICAL,
                message=f"Authentication check failed: {str(e)}",
                details={"error": str(e)},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def check_configuration(self) -> HealthCheckResult:
        """Check configuration system health"""
        start_time = time.time()
        
        try:
            if not CONFIG_AVAILABLE:
                return HealthCheckResult(
                    component=ComponentType.CONFIGURATION,
                    status=HealthStatus.CRITICAL,
                    message="Configuration system not available",
                    details={"error": "Config not imported"}
                )
            
            # Check configuration loading
            if not self.config.config_loaded:
                return HealthCheckResult(
                    component=ComponentType.CONFIGURATION,
                    status=HealthStatus.UNHEALTHY,
                    message="Configuration not loaded",
                    details={"config_loaded": False},
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check critical configurations
            validation_results = {
                "azure_valid": self.config.azure.validate(),
                "llm_valid": self.config.llm.validate(),
                "auth_valid": self.config.auth.validate(),
                "monitoring_valid": self.config.monitoring.validate()
            }
            
            valid_configs = sum(validation_results.values())
            total_configs = len(validation_results)
            
            if valid_configs == total_configs:
                status = HealthStatus.HEALTHY
                message = "All configurations valid"
            elif valid_configs >= total_configs * 0.7:
                status = HealthStatus.DEGRADED
                message = "Some configurations invalid"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Multiple configuration failures"
            
            return HealthCheckResult(
                component=ComponentType.CONFIGURATION,
                status=status,
                message=message,
                details={
                    "environment": self.config.environment.value,
                    "valid_configs": valid_configs,
                    "total_configs": total_configs,
                    "validation_results": validation_results
                },
                response_time_ms=(time.time() - start_time) * 1000
            )
        
        except Exception as e:
            return HealthCheckResult(
                component=ComponentType.CONFIGURATION,
                status=HealthStatus.CRITICAL,
                message=f"Configuration check failed: {str(e)}",
                details={"error": str(e)},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def check_external_apis(self) -> HealthCheckResult:
        """Check external API availability"""
        start_time = time.time()
        
        try:
            apis_status = {}
            
            # Check Gemini API
            if LLM_SERVICE_AVAILABLE and llm_service.is_configured:
                try:
                    gemini_test = llm_service.test_connection()
                    apis_status["gemini"] = {"available": gemini_test, "configured": True}
                except Exception as e:
                    apis_status["gemini"] = {"available": False, "configured": True, "error": str(e)}
            else:
                apis_status["gemini"] = {"available": False, "configured": False}
            
            # Determine overall status
            available_apis = sum(1 for api in apis_status.values() if api.get("available", False))
            total_apis = len(apis_status)
            
            if available_apis == total_apis:
                status = HealthStatus.HEALTHY
                message = "All external APIs available"
            elif available_apis > 0:
                status = HealthStatus.DEGRADED
                message = "Some external APIs unavailable"
            else:
                status = HealthStatus.UNHEALTHY
                message = "No external APIs available"
            
            return HealthCheckResult(
                component=ComponentType.EXTERNAL_API,
                status=status,
                message=message,
                details={
                    "apis": apis_status,
                    "available_count": available_apis,
                    "total_count": total_apis
                },
                response_time_ms=(time.time() - start_time) * 1000
            )
        
        except Exception as e:
            return HealthCheckResult(
                component=ComponentType.EXTERNAL_API,
                status=HealthStatus.CRITICAL,
                message=f"External API check failed: {str(e)}",
                details={"error": str(e)},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def perform_full_health_check(self, use_cache: bool = True) -> SystemHealthSummary:
        """Perform comprehensive health check"""
        
        # Check cache
        if use_cache and self.last_check_time:
            if datetime.utcnow() - self.last_check_time < self.cache_duration:
                return self.cached_results
        
        # Perform health checks
        health_checks = [
            self.check_llm_service(),
            self.check_database(),
            self.check_authentication(),
            self.check_configuration(),
            self.check_external_apis()
        ]
        
        # Determine overall status
        statuses = [check.status for check in health_checks]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(status == HealthStatus.CRITICAL for status in statuses):
            overall_status = HealthStatus.CRITICAL
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED
        
        # Create summary
        summary = SystemHealthSummary(
            overall_status=overall_status,
            components=health_checks
        )
        
        # Cache results
        self.cached_results = summary
        self.last_check_time = datetime.utcnow()
        
        # Log health check
        if logger:
            logger.log_event(
                event_type=EventType.HEALTH_CHECK,
                message=f"Health check completed - {overall_status.value}",
                level=LogLevel.INFO,
                extra_data={"overall_status": overall_status.value, "component_count": len(health_checks)}
            )
        
        return summary
    
    def get_quick_health_status(self) -> Dict[str, Any]:
        """Get quick health status without full checks"""
        return {
            "status": "healthy" if CONFIG_AVAILABLE else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_check": True,
            "config_available": CONFIG_AVAILABLE,
            "llm_available": LLM_SERVICE_AVAILABLE,
            "db_available": DB_SERVICE_AVAILABLE
        }


# Global health checker instance
health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance"""
    return health_checker
