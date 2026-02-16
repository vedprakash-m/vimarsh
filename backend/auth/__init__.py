"""
Authentication module for Vimarsh AI Agent

This module provides unified authentication and authorization functionality
with extensible user models and support for multiple authentication modes.

SECURITY POLICY: Fail-closed — if auth dependencies cannot load, all protected
endpoints return HTTP 503 Service Unavailable. Auth decorators NEVER silently
degrade to identity functions (no-ops).
"""

import functools
import logging

_auth_logger = logging.getLogger(__name__)

# Handle missing dependencies with FAIL-CLOSED pattern
try:
    from .unified_auth_service import (
        UnifiedAuthService,
        auth_service,
        require_auth,
        require_admin,
        admin_required,
        super_admin_required,
        auth_required,
        optional_auth,
        get_authenticated_user,
        verify_token,
        get_user_from_token
    )
    UNIFIED_AUTH_AVAILABLE = True
except ImportError as e:
    # FAIL-CLOSED: Log critical error and deny all protected requests
    _auth_logger.critical(
        f"🚨 AUTH MODULE FAILED TO LOAD: {e}. "
        "All protected endpoints will return 503 Service Unavailable. "
        "Install auth dependencies to restore access."
    )
    UNIFIED_AUTH_AVAILABLE = False

    def _make_denied_decorator(decorator_name):
        """Create a decorator that returns 503 for any protected endpoint."""
        def denied_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                import azure.functions as func_module
                _auth_logger.error(
                    f"🚨 Auth decorator '{decorator_name}' denying request — "
                    "auth module not loaded"
                )
                return func_module.HttpResponse(
                    '{"error": "Service temporarily unavailable — authentication service not loaded"}',
                    status_code=503,
                    mimetype="application/json"
                )
            return wrapper
        return denied_decorator

    require_auth = _make_denied_decorator("require_auth")
    require_admin = _make_denied_decorator("require_admin")
    admin_required = _make_denied_decorator("admin_required")
    super_admin_required = _make_denied_decorator("super_admin_required")
    auth_required = _make_denied_decorator("auth_required")

    # optional_auth is a special case — anonymous access is intentionally allowed,
    # so it should still pass through even when auth module is unavailable
    def optional_auth(func): return func

    def get_authenticated_user(): return None
    def verify_token(token): return None
    def get_user_from_token(token): return None
    
    class UnifiedAuthService:
        pass
    
    auth_service = None

try:
    from .models import (
        AuthenticatedUser,
        AuthenticationMode,
        ProfileConfigurations,
        create_authenticated_user
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    
    class AuthenticatedUser:
        def __init__(self, id=None, attributes=None):
            self.id = id or "fallback_user"
            self.attributes = attributes or {}
    
    AuthenticationMode = None
    ProfileConfigurations = None
    def create_authenticated_user(**kwargs): return AuthenticatedUser()

try:
    from .security_validator import (
        SecurityValidator,
        SecurityValidationError,
        secure_admin_endpoint,
        security_validator
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    _auth_logger.warning("⚠️ Security validator not available — admin endpoints will return 503")
    
    class SecurityValidationError(Exception):
        pass
    
    def secure_admin_endpoint(**kwargs):
        """Fail-closed: deny admin access when security validator is unavailable."""
        return _make_denied_decorator("secure_admin_endpoint")
    
    security_validator = None

# Backward compatibility alias
VedUser = AuthenticatedUser

__all__ = [
    'UnifiedAuthService',
    'auth_service',
    'require_auth', 
    'require_admin',
    'admin_required',
    'super_admin_required',
    'auth_required',
    'optional_auth',
    'get_authenticated_user',
    'AuthenticatedUser',
    'AuthenticationMode',
    'ProfileConfigurations',
    'create_authenticated_user',
    'VedUser'  # Backward compatibility
]

__version__ = "1.0.0"
