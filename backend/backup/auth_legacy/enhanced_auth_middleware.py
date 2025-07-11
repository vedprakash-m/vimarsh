"""
Enhanced authentication middleware for admin endpoints
Provides secure development mode and production authentication
"""

import jwt
import os
import hashlib
import hmac
import requests
import json
import logging
from functools import wraps, lru_cache
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from azure.functions import HttpRequest, HttpResponse

# Import admin role system
from core.user_roles import UserRole, UserPermissions, admin_role_manager

logger = logging.getLogger(__name__)

@dataclass
class VedUser:
    """Standardized user object for Vedprakash domain applications"""
    id: str
    email: str
    name: str
    givenName: str
    familyName: str
    permissions: list
    vedProfile: dict
    # Admin role system
    role: UserRole
    user_permissions: UserPermissions

    @classmethod
    def from_token_data(cls, token_data: Dict[str, Any]) -> 'VedUser':
        """Create VedUser from JWT token claims"""
        email = token_data.get("email", "")
        
        # Determine user role and permissions
        role = admin_role_manager.get_user_role(email)
        user_permissions = admin_role_manager.get_user_permissions(email)
        
        return cls(
            id=token_data.get("sub", ""),
            email=email,
            name=token_data.get("name", ""),
            givenName=token_data.get("given_name", ""),
            familyName=token_data.get("family_name", ""),
            permissions=token_data.get("roles", []),
            vedProfile={
                "profileId": token_data.get("sub", ""),
                "subscriptionTier": "free",
                "appsEnrolled": ["vimarsh"],
                "preferences": {
                    "language": "English",
                    "spiritualInterests": [],
                    "communicationStyle": "reverent"
                }
            },
            role=role,
            user_permissions=user_permissions
        )
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def is_super_admin(self) -> bool:
        """Check if user has super admin privileges"""
        return self.role == UserRole.SUPER_ADMIN
    
    def can_access_admin_endpoints(self) -> bool:
        """Check if user can access admin endpoints"""
        return self.user_permissions.can_access_admin_endpoints

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class SecureDevAuthenticator:
    """Secure development mode authenticator"""
    
    def __init__(self):
        self.dev_secret = os.getenv('DEV_AUTH_SECRET', 'dev-secret-change-in-production')
        self.dev_mode = os.getenv('AUTH_DEVELOPMENT_MODE', 'false').lower() == 'true'
    
    def generate_dev_token(self, email: str) -> str:
        """Generate secure development token"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        payload = f"{email}:{timestamp}"
        signature = hmac.new(
            self.dev_secret.encode(), 
            payload.encode(), 
            hashlib.sha256
        ).hexdigest()
        return f"dev:{payload}:{signature}"
    
    def validate_dev_token(self, token: str) -> Optional[str]:
        """Validate development token and return email if valid"""
        try:
            if not token.startswith('dev:'):
                return None
            
            parts = token.split(':')
            if len(parts) != 4:
                return None
            
            email, timestamp, signature = parts[1], parts[2], parts[3]
            
            # Check if token is expired (24 hours)
            token_time = datetime.fromtimestamp(int(timestamp))
            if datetime.utcnow() - token_time > timedelta(hours=24):
                return None
            
            # Verify signature
            payload = f"{email}:{timestamp}"
            expected_signature = hmac.new(
                self.dev_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return email
            
            return None
            
        except Exception as e:
            logger.error(f"Dev token validation error: {e}")
            return None

class AuthenticationMiddleware:
    """Production-ready authentication middleware for Vimarsh."""
    
    def __init__(self):
        self.jwks_cache = {}
        self.tenant_id = os.getenv('AZURE_TENANT_ID', 'vedprakashentraidtenant.onmicrosoft.com')
        self.client_id = os.getenv('AZURE_CLIENT_ID', '')
        self.authority = os.getenv('AZURE_AUTHORITY', 'https://vedprakashentraidtenant.b2clogin.com/vedprakashentraidtenant.onmicrosoft.com/B2C_1_SignUpSignIn')
        self.dev_authenticator = SecureDevAuthenticator()
        
    @lru_cache(maxsize=1)
    def get_jwks_uri(self) -> str:
        """Get JWKS URI from OpenID configuration."""
        try:
            config_url = f"{self.authority}/v2.0/.well-known/openid_configuration"
            response = requests.get(config_url, timeout=10)
            response.raise_for_status()
            config = response.json()
            return config.get('jwks_uri', '')
        except Exception as e:
            logger.error(f"Failed to get JWKS URI: {e}")
            # Fallback to standard format
            return f"{self.authority}/discovery/v2.0/keys"
    
    @lru_cache(maxsize=1)
    def get_jwks(self) -> Dict[str, Any]:
        """Fetch and cache JWKS (JSON Web Key Set)."""
        try:
            jwks_uri = self.get_jwks_uri()
            response = requests.get(jwks_uri, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            return {"keys": []}
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return claims."""
        try:
            # Check if it's a development token
            if self.dev_authenticator.dev_mode and token.startswith('dev:'):
                email = self.dev_authenticator.validate_dev_token(token)
                if email:
                    return {
                        "email": email,
                        "sub": email,
                        "name": email,
                        "given_name": email.split('@')[0],
                        "family_name": "",
                        "roles": []
                    }
                return None
            
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get('kid')
            
            if not key_id:
                raise AuthenticationError("Token missing key ID")
            
            # Get JWKS and find matching key
            jwks = self.get_jwks()
            public_key = None
            
            for key in jwks.get('keys', []):
                if key.get('kid') == key_id:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not public_key:
                raise AuthenticationError("Public key not found for token")
            
            # Validate and decode token
            claims = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=self.authority
            )
            
            return claims
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise AuthenticationError("Token validation failed")
    
    def extract_user_from_request(self, req: HttpRequest) -> Optional[VedUser]:
        """Extract and validate user from request."""
        try:
            # Get authorization header
            auth_header = req.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Validate token and extract claims
            claims = self.validate_token(token)
            
            if claims:
                user = VedUser.from_token_data(claims)
                logger.info(f"🔐 Authenticated user: {user.email}")
                return user
            
            return None
            
        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {e}")
            return None
        except Exception as e:
            logger.error(f"User extraction failed: {e}")
            return None

# Global middleware instance
auth_middleware = AuthenticationMiddleware()

def auth_required(f: Callable) -> Callable:
    """Decorator to require authentication for Azure Functions endpoints."""
    @wraps(f)
    async def decorated_function(req: HttpRequest) -> HttpResponse:
        # Check if authentication is enabled
        if not os.getenv('ENABLE_AUTH', 'false').lower() == 'true':
            # Authentication disabled - proceed without user context
            logger.warning("⚠️ Authentication disabled - Development mode only")
            return await f(req)
        
        try:
            user = auth_middleware.extract_user_from_request(req)
            
            if not user:
                return HttpResponse(
                    json.dumps({
                        "error": "Authentication required",
                        "message": "Valid access token must be provided",
                        "code": "UNAUTHORIZED"
                    }),
                    status_code=401,
                    mimetype="application/json",
                    headers={
                        "WWW-Authenticate": "Bearer",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            
            # Add user to request context
            req.user = user  # type: ignore
            return await f(req)
            
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            return HttpResponse(
                json.dumps({
                    "error": "Authentication error",
                    "message": "Internal authentication error",
                    "code": "AUTH_ERROR"
                }),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    return decorated_function

def admin_required(f: Callable) -> Callable:
    """Decorator to require admin privileges for Azure Functions endpoints."""
    @wraps(f)
    async def decorated_function(req: HttpRequest) -> HttpResponse:
        # Always require authentication for admin endpoints
        if not os.getenv('ENABLE_AUTH', 'false').lower() == 'true':
            logger.error("🚨 Admin endpoints require authentication - ENABLE_AUTH must be true")
            return HttpResponse(
                json.dumps({
                    "error": "Authentication required",
                    "message": "Admin endpoints require authentication to be enabled",
                    "code": "AUTH_REQUIRED"
                }),
                status_code=401,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        try:
            user = auth_middleware.extract_user_from_request(req)
            
            if not user:
                return HttpResponse(
                    json.dumps({
                        "error": "Authentication required",
                        "message": "Valid access token must be provided for admin access",
                        "code": "UNAUTHORIZED"
                    }),
                    status_code=401,
                    mimetype="application/json",
                    headers={
                        "WWW-Authenticate": "Bearer",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            
            # Check admin privileges
            if not user.is_admin():
                return HttpResponse(
                    json.dumps({
                        "error": "Admin access required",
                        "message": f"User {user.email} does not have admin privileges",
                        "code": "FORBIDDEN",
                        "userRole": str(user.role)
                    }),
                    status_code=403,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Add user to request context
            req.user = user  # type: ignore
            logger.info(f"🔐 Admin access granted to: {user.email}")
            return await f(req)
            
        except Exception as e:
            logger.error(f"Admin authentication error: {e}")
            return HttpResponse(
                json.dumps({
                    "error": "Authentication error",
                    "message": "Internal authentication error",
                    "code": "AUTH_ERROR"
                }),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    return decorated_function

def super_admin_required(f: Callable) -> Callable:
    """Decorator to require super admin privileges for Azure Functions endpoints."""
    @wraps(f)
    async def decorated_function(req: HttpRequest) -> HttpResponse:
        # Always require authentication for super admin endpoints
        if not os.getenv('ENABLE_AUTH', 'false').lower() == 'true':
            logger.error("🚨 Super admin endpoints require authentication - ENABLE_AUTH must be true")
            return HttpResponse(
                json.dumps({
                    "error": "Authentication required",
                    "message": "Super admin endpoints require authentication to be enabled",
                    "code": "AUTH_REQUIRED"
                }),
                status_code=401,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        try:
            user = auth_middleware.extract_user_from_request(req)
            
            if not user:
                return HttpResponse(
                    json.dumps({
                        "error": "Authentication required",
                        "message": "Valid access token must be provided for super admin access",
                        "code": "UNAUTHORIZED"
                    }),
                    status_code=401,
                    mimetype="application/json",
                    headers={
                        "WWW-Authenticate": "Bearer",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            
            # Check super admin privileges
            if not user.is_super_admin():
                return HttpResponse(
                    json.dumps({
                        "error": "Super admin access required",
                        "message": f"User {user.email} does not have super admin privileges",
                        "code": "FORBIDDEN",
                        "userRole": str(user.role)
                    }),
                    status_code=403,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Add user to request context
            req.user = user  # type: ignore
            logger.info(f"🔐 Super admin access granted to: {user.email}")
            return await f(req)
            
        except Exception as e:
            logger.error(f"Super admin authentication error: {e}")
            return HttpResponse(
                json.dumps({
                    "error": "Authentication error",
                    "message": "Internal authentication error",
                    "code": "AUTH_ERROR"
                }),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    return decorated_function

# Development utility functions
def generate_dev_token(email: str) -> str:
    """Generate development token for testing admin endpoints"""
    return auth_middleware.dev_authenticator.generate_dev_token(email)

def get_admin_dev_token() -> str:
    """Get development token for admin user"""
    admin_email = os.getenv('ADMIN_EMAILS', 'vedprakash.m@outlook.com').split(',')[0]
    return generate_dev_token(admin_email)

def get_super_admin_dev_token() -> str:
    """Get development token for super admin user"""
    super_admin_email = os.getenv('SUPER_ADMIN_EMAILS', 'vedprakash.m@outlook.com').split(',')[0]
    return generate_dev_token(super_admin_email)

# Optional middleware for endpoints that can work with or without auth
def optional_auth(f: Callable) -> Callable:
    """Decorator for optional authentication - user context available if authenticated."""
    @wraps(f)
    async def decorated_function(req: HttpRequest) -> HttpResponse:
        # Check if authentication is enabled
        if not os.getenv('ENABLE_AUTH', 'false').lower() == 'true':
            # Authentication disabled - proceed without user context
            return await f(req)
        
        try:
            user = auth_middleware.extract_user_from_request(req)
            
            if user:
                # Add user to request context if authenticated
                req.user = user  # type: ignore
                logger.info(f"🔐 Optional auth - authenticated user: {user.email}")
            else:
                logger.info("🔐 Optional auth - no authentication provided")
            
            return await f(req)
            
        except Exception as e:
            logger.error(f"Optional auth error: {e}")
            # Continue without authentication on error
            return await f(req)
    
    return decorated_function
