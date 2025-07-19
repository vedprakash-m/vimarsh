"""
Authentication module for Vimarsh AI Agent

This module provides unified authentication and authorization functionality
with extensible user models and support for multiple authentication modes.
"""

# Handle missing dependencies gracefully for development/testing
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
        get_authenticated_user
    )
    UNIFIED_AUTH_AVAILABLE = True
except ImportError as e:
    # Provide fallback implementations for development
    UNIFIED_AUTH_AVAILABLE = False
    
    def require_auth(func): return func
    def require_admin(func): return func
    def admin_required(func): return func
    def super_admin_required(func): return func
    def auth_required(func): return func
    def optional_auth(func): return func
    def get_authenticated_user(): return None
    
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
    
    class SecurityValidationError(Exception):
        pass
    
    def secure_admin_endpoint(**kwargs):
        def decorator(func): return func
        return decorator
    
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
