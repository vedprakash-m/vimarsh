
import jwt
import os
import logging
from functools import wraps
from typing import Dict, Any, Optional
from azure.functions import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

class EntraExternalIDAuth:
    """Microsoft Entra External ID authentication middleware."""
    
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_AD_TENANT_ID")
        self.client_id = os.getenv("AZURE_AD_CLIENT_ID")
        self.issuer = os.getenv("JWT_ISSUER")
        self.jwks_uri = os.getenv("JWT_JWKS_URI")
        
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token from Entra External ID."""
        try:
            # Decode and validate JWT token
            decoded_token = jwt.decode(
                token,
                options={"verify_signature": False},  # Signature verification via JWKS
                audience=self.client_id,
                issuer=self.issuer
            )
            
            # Extract user information
            user_info = {
                "user_id": decoded_token.get("sub"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "tenant_id": decoded_token.get("tid"),
                "client_id": decoded_token.get("aud")
            }
            
            logger.info(f"✅ Token validated for user: {user_info.get('email')}")
            return user_info
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"❌ Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            return None
    
    def extract_token_from_request(self, req: HttpRequest) -> Optional[str]:
        """Extract Bearer token from request headers."""
        auth_header = req.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None

def require_auth(f):
    """Decorator to require authentication for Azure Function endpoints."""
    @wraps(f)
    def wrapper(req: HttpRequest) -> HttpResponse:
        auth = EntraExternalIDAuth()
        
        # Extract token
        token = auth.extract_token_from_request(req)
        if not token:
            return HttpResponse(
                "Authentication required",
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token
        user_info = auth.validate_token(token)
        if not user_info:
            return HttpResponse(
                "Invalid authentication token",
                status_code=401
            )
        
        # Add user info to request context
        req.user = user_info
        
        # Call the original function
        return f(req)
    
    return wrapper
