"""
Unified Authentication Service - Consolidates all authentication middleware
Supports both development and production modes with extensible user model
"""

import jwt
import os
import requests
import json
import logging
from functools import wraps, lru_cache
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from azure.functions import HttpRequest, HttpResponse

# Import our new generic user model
from auth.models import AuthenticatedUser, AuthenticationMode, create_authenticated_user
from core.user_roles import UserRole, UserPermissions

logger = logging.getLogger(__name__)


class UnifiedAuthService:
    """
    Unified authentication service supporting multiple modes and providers.
    Replaces duplicate middleware with single, configurable service.
    """
    
    def __init__(self, mode: AuthenticationMode = None, application: str = "vimarsh"):
        """
        Initialize unified auth service.
        
        Args:
            mode: Authentication mode (defaults to environment setting)
            application: Application name for profile configuration
        """
        self.mode = mode or self._get_auth_mode()
        self.application = application
        self.is_enabled = self._get_auth_enabled()
        
        # Cache for validated tokens
        self._token_cache = {}
        self._cache_expiry = {}
        
        logger.info(f"🔐 UnifiedAuthService initialized - Mode: {self.mode}, Enabled: {self.is_enabled}")
    
    def _get_auth_mode(self) -> AuthenticationMode:
        """Determine authentication mode from environment"""
        mode_str = os.getenv("AUTH_MODE", "development").lower()
        try:
            return AuthenticationMode(mode_str)
        except ValueError:
            logger.warning(f"⚠️ Invalid AUTH_MODE '{mode_str}', defaulting to development")
            return AuthenticationMode.DEVELOPMENT
    
    def _get_auth_enabled(self) -> bool:
        """Check if authentication is enabled"""
        enabled = os.getenv("ENABLE_AUTH", "false").lower() == "true"
        return enabled or self.mode == AuthenticationMode.PRODUCTION
    
    def authenticate_request(self, req: HttpRequest) -> Optional[AuthenticatedUser]:
        """
        Authenticate incoming request and return user or None.
        
        Args:
            req: Azure Functions HTTP request
            
        Returns:
            AuthenticatedUser if authenticated, None otherwise
        """
        try:
            if not self.is_enabled:
                return self._create_development_user()
            
            # Extract token from request
            token = self._extract_token(req)
            if not token:
                logger.warning("🚫 No authentication token found")
                return None
            
            # Validate token based on mode
            if self.mode == AuthenticationMode.DEVELOPMENT:
                return self._validate_development_token(token)
            elif self.mode == AuthenticationMode.PRODUCTION:
                return self._validate_production_token(token)
            else:
                logger.error(f"❌ Unsupported authentication mode: {self.mode}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return None
    
    async def extract_user_from_request(self, req: HttpRequest) -> Optional[AuthenticatedUser]:
        """
        Extract authenticated user from request (async version for the plan implementation).
        This is an alias for authenticate_request to match the implementation plan naming.
        
        Args:
            req: Azure Functions HTTP request
            
        Returns:
            AuthenticatedUser if authenticated, None otherwise
        """
        return self.authenticate_request(req)
    
    def _extract_token(self, req: HttpRequest) -> Optional[str]:
        """Extract JWT token from request headers"""
        auth_header = req.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None
    
    def _create_development_user(self) -> AuthenticatedUser:
        """Create a development user when auth is disabled"""
        dev_token_data = {
            "sub": "dev-user-123",
            "email": "dev@vimarsh.local",
            "name": "Development User",
            "given_name": "Development",
            "family_name": "User",
            "roles": ["admin"]  # Dev user gets admin rights
        }
        
        user = create_authenticated_user(dev_token_data, self.application)
        user.role = UserRole.ADMIN  # Ensure dev user has admin access
        user.user_permissions = UserPermissions.for_role(UserRole.ADMIN)
        
        logger.debug("🔧 Created development user with admin privileges")
        return user
    
    def _validate_development_token(self, token: str) -> Optional[AuthenticatedUser]:
        """Validate token in development mode (relaxed validation)"""
        try:
            # Check cache first
            if token in self._token_cache:
                if datetime.utcnow() < self._cache_expiry[token]:
                    return self._token_cache[token]
            
            # Simple development token validation
            if self._is_development_token_valid(token):
                # Create mock user data from token
                token_data = self._decode_development_token(token)
                user = create_authenticated_user(token_data, self.application)
                
                # Cache the result
                self._token_cache[token] = user
                self._cache_expiry[token] = datetime.utcnow() + timedelta(hours=1)
                
                logger.info(f"✅ Development token validated for {user.email}")
                return user
            else:
                logger.warning("⚠️ Invalid development token")
                return None
                
        except Exception as e:
            logger.error(f"❌ Development token validation error: {str(e)}")
            return None
    
    def _validate_production_token(self, token: str) -> Optional[AuthenticatedUser]:
        """Validate token against Microsoft Entra ID"""
        try:
            # Check cache first
            if token in self._token_cache:
                if datetime.utcnow() < self._cache_expiry[token]:
                    return self._token_cache[token]
            
            # Get Entra ID configuration
            tenant_id = os.getenv("ENTRA_TENANT_ID") or os.getenv("AZURE_TENANT_ID")
            client_id = os.getenv("ENTRA_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID")
            
            if not tenant_id or not client_id:
                logger.error("❌ Missing Azure configuration for production auth")
                return None
            
            # Validate against Microsoft Entra ID
            token_data = self._validate_entra_token(token, tenant_id, client_id)
            if token_data:
                user = create_authenticated_user(token_data, self.application)
                
                # Cache the result
                self._token_cache[token] = user
                self._cache_expiry[token] = datetime.utcnow() + timedelta(minutes=55)  # Refresh before expiry
                
                logger.info(f"✅ Production token validated for {user.email}")
                return user
            else:
                logger.warning("⚠️ Invalid production token")
                return None
                
        except Exception as e:
            logger.error(f"❌ Production token validation error: {str(e)}")
            return None
    
    def _is_development_token_valid(self, token: str) -> bool:
        """Simple development token validation"""
        # For development, accept specific test tokens or any valid JWT structure
        test_tokens = ["dev-token", "admin-token", "test-token"]
        
        if token in test_tokens:
            return True
        
        # Try to decode as JWT (even if signature is invalid)
        try:
            jwt.decode(token, options={"verify_signature": False})
            return True
        except Exception:
            return False
    
    def _decode_development_token(self, token: str) -> Dict[str, Any]:
        """Decode development token to extract user data"""
        # Handle simple test tokens
        test_token_data = {
            "dev-token": {
                "sub": "dev-user-123",
                "email": "dev@vimarsh.local",
                "name": "Development User",
                "given_name": "Development",
                "family_name": "User",
                "roles": ["user"]
            },
            "admin-token": {
                "sub": "admin-user-456",
                "email": "admin@vimarsh.local", 
                "name": "Admin User",
                "given_name": "Admin",
                "family_name": "User",
                "roles": ["admin"]
            },
            "test-token": {
                "sub": "test-user-789",
                "email": "test@vimarsh.local",
                "name": "Test User", 
                "given_name": "Test",
                "family_name": "User",
                "roles": ["user"]
            }
        }
        
        if token in test_token_data:
            return test_token_data[token]
        
        # Try to decode as actual JWT
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception:
            # Fallback to default dev user
            return test_token_data["dev-token"]
    
    @lru_cache(maxsize=100)
    def _validate_entra_token(self, token: str, tenant_id: str, client_id: str) -> Optional[Dict[str, Any]]:
        """Validate token against Microsoft Entra ID with multi-tenant support"""
        try:
            # First decode token to get actual tenant if using "common"
            unverified = jwt.decode(token, options={"verify_signature": False})
            actual_tenant = unverified.get("tid", tenant_id)
            
            # For multi-tenant, use common endpoint or specific tenant
            if tenant_id == "common":
                # Use common endpoint but validate against actual tenant from token
                jwks_url = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
                expected_issuer = f"https://login.microsoftonline.com/{actual_tenant}/v2.0"
            else:
                # Single tenant validation
                jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
                expected_issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
            
            # Get JWKS from Microsoft
            jwks_response = requests.get(jwks_url, timeout=10)
            jwks_response.raise_for_status()
            jwks = jwks_response.json()
            
            # Decode and validate JWT
            header = jwt.get_unverified_header(token)
            key = None
            
            for jwk in jwks["keys"]:
                if jwk["kid"] == header["kid"]:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                logger.error("❌ No matching key found in JWKS")
                return None
            
            # Validate token with multi-tenant support
            decoded_token = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=client_id,
                issuer=expected_issuer
            )
            
            logger.info(f"✅ Successfully validated Entra ID token for {decoded_token.get('email', 'unknown')} from tenant {actual_tenant}")
            return decoded_token
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Token validation error: {str(e)}")
            return None
    
    def create_auth_decorator(self, require_admin: bool = False) -> Callable:
        """
        Create authentication decorator for Azure Functions.
        
        Args:
            require_admin: Whether admin privileges are required
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(req: HttpRequest) -> HttpResponse:
                try:
                    # Authenticate user
                    user = self.authenticate_request(req)
                    
                    if not user:
                        return HttpResponse(
                            json.dumps({"error": "Authentication required"}),
                            status_code=401,
                            mimetype="application/json",
                            headers={
                                "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                                "Access-Control-Allow-Credentials": "true",
                                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                                "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id"
                            }
                        )
                    
                    # Check admin requirement
                    if require_admin and not user.is_admin():
                        return HttpResponse(
                            json.dumps({"error": "Admin privileges required"}),
                            status_code=403, 
                            mimetype="application/json",
                            headers={
                                "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                                "Access-Control-Allow-Credentials": "true",
                                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                                "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id"
                            }
                        )
                    
                    # Add user to request context
                    req.user = user
                    
                    # Call the original function
                    return func(req)
                    
                except Exception as e:
                    logger.error(f"❌ Auth decorator error: {str(e)}")
                    return HttpResponse(
                        json.dumps({"error": "Authentication error"}),
                        status_code=500,
                        mimetype="application/json"
                    )
            
            return wrapper
        return decorator
    
    def clear_cache(self) -> None:
        """Clear the token cache"""
        self._token_cache.clear()
        self._cache_expiry.clear()
        logger.info("🗑️ Cleared authentication cache")


# Global instance for the application
auth_service = UnifiedAuthService()

# Convenience decorators
def require_auth(func: Callable) -> Callable:
    """Decorator requiring authentication"""
    return auth_service.create_auth_decorator(require_admin=False)(func)

def require_admin(func: Callable) -> Callable:
    """Decorator requiring admin authentication"""
    return auth_service.create_auth_decorator(require_admin=True)(func)

# Backward compatibility function
def get_authenticated_user(req: HttpRequest) -> Optional[AuthenticatedUser]:
    """Get authenticated user from request (backward compatibility)"""
    return auth_service.authenticate_request(req)

# Backward compatibility decorators for existing code
def admin_required(func: Callable) -> Callable:
    """Backward compatibility decorator for admin_required"""
    return auth_service.create_auth_decorator(require_admin=True)(func)

def super_admin_required(func: Callable) -> Callable:
    """Backward compatibility decorator for super_admin_required (same as admin for now)"""
    return auth_service.create_auth_decorator(require_admin=True)(func)

def auth_required(func: Callable) -> Callable:
    """Backward compatibility decorator for auth_required"""
    return auth_service.create_auth_decorator(require_admin=False)(func)

def optional_auth(func: Callable) -> Callable:
    """Backward compatibility decorator for optional_auth (no-op since we handle this in the service)"""
    return func

# Backward compatibility aliases
VedUser = AuthenticatedUser  # For existing code that imports VedUser
