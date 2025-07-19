"""
Enhanced Error Handling for Admin Features
Provides graceful degradation, retry logic, and proper error logging
"""

import logging
import json
import time
from typing import Any, Dict, Optional, Callable, TypeVar, Tuple
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta
from azure.functions import HttpResponse
from enum import Enum

logger = logging.getLogger(__name__)

# Type variable for generic decorator
T = TypeVar('T')


class ErrorSeverity(Enum):
    """Error severity levels for proper categorization"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AdminErrorType(Enum):
    """Specific error types for admin operations"""
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    DATABASE_ERROR = "database_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    CONFIG_ERROR = "config_error"
    INTERNAL_ERROR = "internal_error"


@dataclass
class AdminError:
    """Structured error information for admin operations"""
    error_type: AdminErrorType
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    timestamp: datetime = None
    user_friendly_message: Optional[str] = None
    retry_after: Optional[int] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        result = {
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "error_code": f"ADMIN_{self.error_type.value.upper()}"
        }
        
        if self.details:
            result["details"] = self.details
        if self.user_friendly_message:
            result["user_message"] = self.user_friendly_message
        if self.retry_after:
            result["retry_after"] = self.retry_after
            
        return result


class AdminErrorHandler:
    """Centralized error handling for admin operations"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_error_times = {}
    
    def create_error_response(self, admin_error: AdminError, status_code: int = 500) -> HttpResponse:
        """Create standardized error response"""
        
        # Log error with appropriate level
        if admin_error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"🚨 CRITICAL ADMIN ERROR: {admin_error.message}")
        elif admin_error.severity == ErrorSeverity.HIGH:
            logger.error(f"❌ HIGH ADMIN ERROR: {admin_error.message}")
        elif admin_error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"⚠️ MEDIUM ADMIN ERROR: {admin_error.message}")
        else:
            logger.info(f"ℹ️ LOW ADMIN ERROR: {admin_error.message}")
        
        # Create response
        response_data = admin_error.to_dict()
        
        # Add Krishna-inspired spiritual messaging for user-facing errors
        if admin_error.error_type in [AdminErrorType.SERVICE_UNAVAILABLE, AdminErrorType.DATABASE_ERROR]:
            response_data["spiritual_message"] = "🕉️ Even in moments of challenge, divine patience guides us. Please try again shortly."
        elif admin_error.error_type == AdminErrorType.AUTHORIZATION_ERROR:
            response_data["spiritual_message"] = "🙏 With proper guidance comes proper access. Please ensure you have the necessary permissions."
        
        return HttpResponse(
            json.dumps(response_data),
            status_code=status_code,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    def handle_database_error(self, e: Exception, operation: str) -> AdminError:
        """Handle database-related errors with specific recovery guidance"""
        return AdminError(
            error_type=AdminErrorType.DATABASE_ERROR,
            severity=ErrorSeverity.HIGH,
            message=f"Database error during {operation}",
            details=str(e),
            user_friendly_message="Database service temporarily unavailable. Admins can try again in a few moments.",
            retry_after=30
        )
    
    def handle_service_unavailable(self, service_name: str, e: Exception) -> AdminError:
        """Handle service unavailability with fallback guidance"""
        return AdminError(
            error_type=AdminErrorType.SERVICE_UNAVAILABLE,
            severity=ErrorSeverity.MEDIUM,
            message=f"{service_name} service unavailable",
            details=str(e),
            user_friendly_message=f"{service_name} is temporarily unavailable. Using cached data where possible.",
            retry_after=60
        )
    
    def handle_authentication_error(self, details: str) -> AdminError:
        """Handle authentication errors"""
        return AdminError(
            error_type=AdminErrorType.AUTHENTICATION_ERROR,
            severity=ErrorSeverity.HIGH,
            message="Authentication failed for admin access",
            details=details,
            user_friendly_message="Authentication required. Please log in with admin credentials."
        )
    
    def handle_authorization_error(self, user_email: str, required_role: str) -> AdminError:
        """Handle authorization errors"""
        return AdminError(
            error_type=AdminErrorType.AUTHORIZATION_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message=f"User {user_email} lacks required role: {required_role}",
            user_friendly_message=f"Admin privileges required. Contact super admin for role assignment."
        )
    
    def handle_validation_error(self, validation_details: str) -> AdminError:
        """Handle request validation errors"""
        return AdminError(
            error_type=AdminErrorType.VALIDATION_ERROR,
            severity=ErrorSeverity.LOW,
            message="Request validation failed",
            details=validation_details,
            user_friendly_message="Invalid request format. Please check your input and try again."
        )


# Global error handler instance
admin_error_handler = AdminErrorHandler()


def with_graceful_degradation(fallback_data: Dict[str, Any] = None):
    """Decorator for graceful degradation with fallback data"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"🔄 Graceful degradation for {func.__name__}: {e}")
                
                # Return fallback data if available
                if fallback_data:
                    admin_error = AdminError(
                        error_type=AdminErrorType.SERVICE_UNAVAILABLE,
                        severity=ErrorSeverity.LOW,
                        message=f"Service degraded, using fallback data",
                        details=str(e),
                        user_friendly_message="Service temporarily using cached data"
                    )
                    
                    response_data = fallback_data.copy()
                    response_data["_degraded"] = True
                    response_data["_fallback_reason"] = admin_error.message
                    
                    return HttpResponse(
                        json.dumps(response_data),
                        status_code=200,  # Still return 200 for partial success
                        mimetype="application/json",
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
                else:
                    # No fallback data, return error
                    admin_error = admin_error_handler.handle_service_unavailable(func.__name__, e)
                    return admin_error_handler.create_error_response(admin_error)
        
        return wrapper
    return decorator


def with_retry_logic(max_attempts: int = 3, backoff_seconds: float = 1.0):
    """Decorator for automatic retry logic with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:  # Don't wait on last attempt
                        wait_time = backoff_seconds * (2 ** attempt)
                        logger.info(f"🔄 Retry {attempt + 1}/{max_attempts} for {func.__name__} in {wait_time}s")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ All {max_attempts} attempts failed for {func.__name__}")
            
            # All attempts failed, handle the error
            admin_error = admin_error_handler.handle_service_unavailable(func.__name__, last_exception)
            return admin_error_handler.create_error_response(admin_error)
        
        return wrapper
    return decorator


def with_admin_error_handling(func: Callable) -> Callable:
    """Comprehensive error handling decorator for admin endpoints"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Categorize the error and create appropriate response
            error_message = str(e).lower()
            
            if "authentication" in error_message or "unauthorized" in error_message:
                admin_error = admin_error_handler.handle_authentication_error(str(e))
                return admin_error_handler.create_error_response(admin_error, 401)
            elif "permission" in error_message or "forbidden" in error_message:
                admin_error = admin_error_handler.handle_authorization_error("unknown", "admin")
                return admin_error_handler.create_error_response(admin_error, 403)
            elif "database" in error_message or "connection" in error_message:
                admin_error = admin_error_handler.handle_database_error(e, func.__name__)
                return admin_error_handler.create_error_response(admin_error, 503)
            elif "validation" in error_message or "invalid" in error_message:
                admin_error = admin_error_handler.handle_validation_error(str(e))
                return admin_error_handler.create_error_response(admin_error, 400)
            else:
                # Generic internal error
                admin_error = AdminError(
                    error_type=AdminErrorType.INTERNAL_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message=f"Internal error in {func.__name__}",
                    details=str(e),
                    user_friendly_message="An unexpected error occurred. Please try again or contact support."
                )
                return admin_error_handler.create_error_response(admin_error, 500)
    
    return wrapper


def validate_admin_request(required_params: list = None, required_body_fields: list = None):
    """Decorator for validating admin requests"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(req, *args, **kwargs):
            # Validate required parameters
            if required_params:
                missing_params = [param for param in required_params if not req.params.get(param)]
                if missing_params:
                    admin_error = admin_error_handler.handle_validation_error(
                        f"Missing required parameters: {', '.join(missing_params)}"
                    )
                    return admin_error_handler.create_error_response(admin_error, 400)
            
            # Validate required body fields for POST/PUT requests
            if required_body_fields and req.method in ["POST", "PUT"]:
                try:
                    body_data = json.loads(req.get_body().decode())
                    missing_fields = [field for field in required_body_fields if field not in body_data]
                    if missing_fields:
                        admin_error = admin_error_handler.handle_validation_error(
                            f"Missing required body fields: {', '.join(missing_fields)}"
                        )
                        return admin_error_handler.create_error_response(admin_error, 400)
                except json.JSONDecodeError:
                    admin_error = admin_error_handler.handle_validation_error("Invalid JSON in request body")
                    return admin_error_handler.create_error_response(admin_error, 400)
            
            return await func(req, *args, **kwargs)
        
        return wrapper
    return decorator


# Pre-configured fallback data for common admin operations
COST_DASHBOARD_FALLBACK = {
    "system_usage": {
        "total_requests": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "average_cost_per_request": 0.0,
        "period_days": 7
    },
    "top_users": [],
    "budget_summary": {
        "total_budget": 100.0,
        "used_budget": 0.0,
        "remaining_budget": 100.0,
        "budget_utilization": 0.0
    },
    "recent_alerts": [],
    "status": "Service temporarily unavailable - showing cached data"
}

USER_MANAGEMENT_FALLBACK = {
    "users": [],
    "total_users": 0,
    "blocked_users": 0,
    "status": "User data temporarily unavailable"
}

SYSTEM_HEALTH_FALLBACK = {
    "health_status": "unknown",
    "health_score": 0,
    "system_metrics": {
        "total_requests_7d": 0,
        "active_alerts": 0,
        "blocked_users": 0,
        "total_cost_7d": 0.0
    },
    "components": {
        "database": "unknown",
        "auth_system": "unknown",
        "token_tracker": "unknown",
        "budget_validator": "unknown"
    },
    "status": "Health monitoring temporarily unavailable"
}

BUDGET_MANAGEMENT_FALLBACK = {
    "budgets": [],
    "total_budgets": 0,
    "default_limits": {
        "monthly_limit": 50.0,
        "daily_limit": 5.0,
        "per_request_limit": 0.50
    },
    "status": "Budget management temporarily unavailable"
}

ROLE_MANAGEMENT_FALLBACK = {
    "admins": {
        "admins": [],
        "super_admins": []
    },
    "total_admins": 0,
    "total_super_admins": 0,
    "status": "Role management temporarily unavailable"
}

USER_ROLE_FALLBACK = {
    "role": "USER",
    "permissions": {
        "can_use_spiritual_guidance": True,
        "can_view_own_usage": False,
        "can_view_cost_dashboard": False,
        "can_manage_users": False,
        "can_block_users": False,
        "can_view_system_costs": False,
        "can_configure_budgets": False,
        "can_access_admin_endpoints": False,
        "can_override_budget_limits": False,
        "can_manage_emergency_controls": False
    },
    "email": "unknown",
    "status": "Role information temporarily unavailable"
}

ADMIN_METRICS_FALLBACK = {
    "time_period_hours": 24,
    "total_operations": 0,
    "unique_admins": 0,
    "operation_breakdown": {},
    "performance_stats": {},
    "error_summary": {},
    "current_alerts": 0,
    "status": "Metrics temporarily unavailable"
}

ADMIN_ALERTS_FALLBACK = {
    "alerts": [],
    "total_alerts": 0,
    "unresolved_alerts": 0,
    "status": "Alerts temporarily unavailable"
}

BUDGET_MANAGEMENT_FALLBACK = {
    "budgets": [],
    "total_budgets": 0,
    "default_limits": {
        "monthly_limit": 50.0,
        "daily_limit": 1.67,
        "per_request_limit": 0.50
    },
    "status": "Budget management temporarily unavailable"
}

ROLE_MANAGEMENT_FALLBACK = {
    "admins": [],
    "super_admins": [],
    "total_admins": 0,
    "total_super_admins": 0,
    "status": "Role management temporarily unavailable"
}

USER_ROLE_FALLBACK = {
    "role": "user",
    "permissions": {
        "can_use_spiritual_guidance": True,
        "can_view_own_usage": True,
        "can_view_cost_dashboard": False,
        "can_manage_users": False,
        "can_block_users": False,
        "can_view_system_costs": False,
        "can_configure_budgets": False,
        "can_access_admin_endpoints": False,
        "can_override_budget_limits": False,
        "can_manage_emergency_controls": False
    },
    "email": "unknown",
    "status": "Role information temporarily unavailable"
}
