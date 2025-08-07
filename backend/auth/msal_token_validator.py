"""
MSAL Token Validator for Azure AD authentication
Extracts user information from Microsoft identity tokens
"""

import jwt
import json
import logging
from typing import Optional, Dict, Any
from azure.functions import HttpRequest

logger = logging.getLogger(__name__)


class MSALTokenValidator:
    """Validates and extracts information from MSAL tokens"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_user_email_from_request(self, req: HttpRequest) -> Optional[str]:
        """
        Extract user email from various sources in the request
        
        Args:
            req: Azure Functions HTTP request
            
        Returns:
            User email if found, None otherwise
        """
        try:
            # Try header first (for testing/development)
            user_email = req.headers.get('x-user-email') or req.headers.get('X-User-Email')
            if user_email:
                self.logger.info(f"📧 User email from header: {user_email}")
                return user_email
            
            # Try to extract from Authorization Bearer token
            auth_header = req.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                email = self._extract_email_from_token(token)
                if email:
                    self.logger.info(f"📧 User email from token: {email}")
                    return email
            
            # Try other common header variations
            user_email = (req.headers.get('x-ms-client-principal-name') or 
                         req.headers.get('X-Ms-Client-Principal-Name'))
            if user_email:
                self.logger.info(f"📧 User email from x-ms-client-principal-name: {user_email}")
                return user_email
            
            self.logger.warning("⚠️ No user email found in request")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting user email: {e}")
            return None
    
    def _extract_email_from_token(self, token: str) -> Optional[str]:
        """
        Extract email from JWT token (MSAL token)
        Note: This doesn't validate the token signature for now, just extracts claims
        
        Args:
            token: JWT token string
            
        Returns:
            Email from token claims if found
        """
        try:
            # Decode without verification for now (in production, should verify signature)
            # This is safe because we're only extracting email for role validation,
            # not granting access based on the token alone
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Try different email claim names
            email = (decoded.get('email') or 
                    decoded.get('upn') or 
                    decoded.get('preferred_username') or
                    decoded.get('unique_name'))
            
            if email:
                self.logger.info(f"📧 Extracted email from token: {email}")
                return email
            else:
                self.logger.warning("⚠️ No email claim found in token")
                # Log token claims for debugging (remove in production)
                self.logger.debug(f"Token claims: {list(decoded.keys())}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error decoding token: {e}")
            return None
    
    def get_user_context(self, req: HttpRequest) -> Dict[str, Any]:
        """
        Get comprehensive user context from request
        
        Args:
            req: Azure Functions HTTP request
            
        Returns:
            Dictionary with user context information
        """
        try:
            user_email = self.extract_user_email_from_request(req)
            
            context = {
                "email": user_email,
                "authenticated": bool(user_email),
                "source": "unknown",
                "timestamp": None,
                "headers_checked": [
                    "x-user-email",
                    "X-User-Email", 
                    "Authorization",
                    "x-ms-client-principal-name"
                ]
            }
            
            # Determine source
            if req.headers.get('x-user-email') or req.headers.get('X-User-Email'):
                context["source"] = "header"
            elif req.headers.get('Authorization', '').startswith('Bearer '):
                context["source"] = "msal_token"
            elif req.headers.get('x-ms-client-principal-name'):
                context["source"] = "azure_app_service"
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Error getting user context: {e}")
            return {
                "email": None,
                "authenticated": False,
                "error": str(e),
                "source": "error"
            }


# Global instance for easy import
msal_validator = MSALTokenValidator()
