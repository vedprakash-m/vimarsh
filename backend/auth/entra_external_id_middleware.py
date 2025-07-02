
import jwt
import os
import requests
import json
import logging
from functools import wraps, lru_cache
from typing import Dict, Any, Optional
from dataclasses import dataclass
from azure.functions import HttpRequest, HttpResponse

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

    @classmethod
    def from_token_data(cls, token_data: Dict[str, Any]) -> 'VedUser':
        """Create VedUser from JWT token claims"""
        return cls(
            id=token_data.get("sub", ""),
            email=token_data.get("email", ""),
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
            }
        )

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class EntraIDJWTValidator:
    """Microsoft Entra ID JWT token validator with proper signature verification."""
    
    def __init__(self):
        self.tenant_id = os.getenv("ENTRA_TENANT_ID", "vedid.onmicrosoft.com")
        self.client_id = os.getenv("ENTRA_CLIENT_ID")
        self.issuer = f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"
        self.jwks_uri = f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"
        
        if not self.client_id:
            raise ValueError("ENTRA_CLIENT_ID environment variable is required")
    
    @lru_cache(maxsize=1)
    def get_jwks_keys(self) -> Dict[str, Any]:
        """Cache JWKS keys for 1 hour to avoid repeated requests."""
        try:
            logger.info(f"Fetching JWKS from: {self.jwks_uri}")
            response = requests.get(self.jwks_uri, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            logger.info(f"✅ Successfully fetched {len(jwks.get('keys', []))} JWKS keys")
            return jwks
        except Exception as e:
            logger.error(f"❌ Failed to fetch JWKS keys: {e}")
            raise
    
    def get_signing_key(self, kid: str) -> Any:
        """Get the signing key for token validation."""
        try:
            jwks = self.get_jwks_keys()
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    logger.info(f"✅ Found signing key for kid: {kid}")
                    return jwt.algorithms.RSAAlgorithm.from_jwk(key)
            
            logger.error(f"❌ Signing key not found for kid: {kid}")
            raise ValueError(f"Unable to find signing key: {kid}")
            
        except Exception as e:
            logger.error(f"❌ Error getting signing key: {e}")
            raise
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token with proper signature verification.
        
        CRITICAL: This method enables signature verification for security.
        """
        try:
            # Decode header to get key ID without verification
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            
            if not kid:
                raise ValueError("No key ID (kid) found in token header")
            
            # Get the signing key for verification
            signing_key = self.get_signing_key(kid)
            
            # Decode and validate token with signature verification
            decoded_token = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],  # Entra ID uses RS256
                audience=self.client_id,
                issuer=self.issuer,
                options={
                    "verify_signature": True,   # ✅ CRITICAL: Enable signature verification
                    "verify_exp": True,         # ✅ Verify expiration
                    "verify_nbf": True,         # ✅ Verify not before
                    "verify_iat": True,         # ✅ Verify issued at
                    "verify_aud": True,         # ✅ Verify audience
                    "verify_iss": True          # ✅ Verify issuer
                }
            )
            
            logger.info(f"✅ Token validated successfully for user: {decoded_token.get('email', 'unknown')}")
            return decoded_token
            
        except jwt.ExpiredSignatureError:
            logger.warning("❌ Token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidAudienceError:
            logger.warning("❌ Invalid token audience")
            raise ValueError("Invalid token audience")
        except jwt.InvalidIssuerError:
            logger.warning("❌ Invalid token issuer")
            raise ValueError("Invalid token issuer")
        except jwt.InvalidSignatureError:
            logger.warning("❌ Invalid token signature")
            raise ValueError("Invalid token signature")
        except jwt.InvalidTokenError as e:
            logger.warning(f"❌ Invalid token: {e}")
            raise ValueError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            raise ValueError("Token validation failed")
    
    def extract_ved_user(self, token_data: Dict[str, Any]) -> VedUser:
        """Extract standardized VedUser from token claims."""
        return VedUser.from_token_data(token_data)
    
    def extract_token_from_request(self, req: HttpRequest) -> Optional[str]:
        """Extract Bearer token from request headers."""
        auth_header = req.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None

def add_security_headers(response: HttpResponse) -> HttpResponse:
    """Add comprehensive security headers to response."""
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "connect-src 'self' https://login.microsoftonline.com https://vedid.b2clogin.com; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com"
        ),
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    })
    return response

def require_auth(func):
    """
    Decorator to require authentication for Azure Function endpoints.
    
    This implements secure JWT validation with signature verification.
    """
    @wraps(func)
    def wrapper(req: HttpRequest) -> HttpResponse:
        try:
            validator = EntraIDJWTValidator()
            
            # Extract token from request
            token = validator.extract_token_from_request(req)
            if not token:
                logger.warning("❌ No authentication token provided")
                response = HttpResponse(
                    json.dumps({"error": "Authentication required", "code": "NO_TOKEN"}),
                    status_code=401,
                    headers={
                        "Content-Type": "application/json",
                        "WWW-Authenticate": "Bearer"
                    }
                )
                return add_security_headers(response)
            
            # Validate token with signature verification
            token_data = validator.validate_token(token)
            user = validator.extract_ved_user(token_data)
            
            # Add user to request context
            req.ved_user = user
            
            logger.info(f"✅ User authenticated: {user.get('email')}")
            
            # Call the protected function
            response = func(req)
            
            # Add security headers to response
            return add_security_headers(response)
            
        except ValueError as e:
            # Token validation error
            logger.warning(f"❌ Authentication failed: {e}")
            response = HttpResponse(
                json.dumps({"error": str(e), "code": "INVALID_TOKEN"}),
                status_code=401,
                headers={"Content-Type": "application/json"}
            )
            return add_security_headers(response)
            
        except Exception as e:
            # Unexpected error
            logger.error(f"❌ Unexpected authentication error: {e}")
            response = HttpResponse(
                json.dumps({"error": "Authentication failed", "code": "AUTH_ERROR"}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
            return add_security_headers(response)
    
    return wrapper

def optional_auth(func):
    """
    Decorator for endpoints that support optional authentication.
    
    Sets req.ved_user if authenticated, None if not.
    Allows anonymous access for basic spiritual guidance.
    """
    @wraps(func)
    def wrapper(req: HttpRequest) -> HttpResponse:
        try:
            validator = EntraIDJWTValidator()
            
            # Extract token from request
            token = validator.extract_token_from_request(req)
            
            if token:
                try:
                    # Validate token if present
                    token_data = validator.validate_token(token)
                    user = validator.extract_ved_user(token_data)
                    req.ved_user = user
                    logger.info(f"✅ Optional auth: User authenticated: {user.get('email')}")
                except Exception as e:
                    # If token is invalid, continue as anonymous
                    logger.warning(f"⚠️ Optional auth: Invalid token, continuing as anonymous: {e}")
                    req.ved_user = None
            else:
                # No token provided, continue as anonymous
                req.ved_user = None
                logger.info("ℹ️ Optional auth: Anonymous access")
            
            # Call the function
            response = func(req)
            
            # Add security headers to response
            return add_security_headers(response)
            
        except Exception as e:
            # Unexpected error - continue as anonymous
            logger.error(f"❌ Unexpected error in optional auth: {e}")
            req.ved_user = None
            response = func(req)
            return add_security_headers(response)
    
    return wrapper

# Environment validation
def validate_auth_config():
    """Validate authentication configuration on startup."""
    required_vars = ["ENTRA_CLIENT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    logger.info("✅ Authentication configuration validated")

def validate_jwt_token(token: str) -> Dict[str, Any]:
    """Validate JWT token and return claims"""
    validator = EntraIDJWTValidator()
    return validator.validate_token(token)

# Create module-level middleware instance for convenience
EntraExternalIDMiddleware = EntraIDJWTValidator

# Call validation on import
try:
    validate_auth_config()
except ValueError as e:
    logger.warning(f"⚠️ Authentication configuration incomplete: {e}")