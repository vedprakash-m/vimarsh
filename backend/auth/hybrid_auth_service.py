"""
Hybrid Authentication Service for Microsoft + Google Auth
Supports starting with Microsoft multitenant, then adding Google later
"""

import os
import jwt
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import azure.functions as func
from azure.cosmos import CosmosClient
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import httpx

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    pass

class UserService:
    """Manages user data in Cosmos DB with hybrid auth support"""
    
    def __init__(self):
        # Cosmos DB connection
        cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_DB_KEY")
        self.cosmos_client = CosmosClient(cosmos_endpoint, credential=cosmos_key)
        self.database = self.cosmos_client.get_database_client("vimarsh_db")
        self.users_container = self.database.get_container_client("users")
    
    async def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email across all auth providers"""
        try:
            query = "SELECT * FROM users u WHERE u.email = @email"
            parameters = [{"name": "@email", "value": email}]
            
            items = list(self.users_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return items[0] if items else None
            
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            return None
    
    async def find_user_by_provider(self, provider: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """Find user by specific auth provider ID"""
        try:
            query = """
            SELECT * FROM users u 
            JOIN provider IN u.auth_providers 
            WHERE provider.provider = @provider 
            AND provider.provider_id = @provider_id
            """
            parameters = [
                {"name": "@provider", "value": provider},
                {"name": "@provider_id", "value": provider_id}
            ]
            
            items = list(self.users_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return items[0] if items else None
            
        except Exception as e:
            logger.error(f"Error finding user by provider: {str(e)}")
            return None
    
    async def create_or_update_user(self, normalized_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user or update existing user with new auth provider"""
        try:
            provider = normalized_user_data["provider"]
            provider_id = normalized_user_data["provider_id"]
            email = normalized_user_data["email"]
            
            # Check if user exists by provider ID first
            existing_user = await self.find_user_by_provider(provider, provider_id)
            
            if existing_user:
                # Update last login for existing user
                existing_user["last_login"] = datetime.utcnow().isoformat()
                self.users_container.upsert_item(existing_user)
                return existing_user
            
            # Check if user exists by email (for provider linking)
            existing_user = await self.find_user_by_email(email)
            
            if existing_user:
                # Link new auth provider to existing user
                return await self.link_auth_provider(existing_user, normalized_user_data)
            
            # Create new user
            return await self.create_new_user(normalized_user_data)
            
        except Exception as e:
            logger.error(f"Error creating/updating user: {str(e)}")
            raise AuthenticationError("Failed to create or update user")
    
    async def create_new_user(self, normalized_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a completely new user"""
        user_id = f"user_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{normalized_user_data['provider_id'][:8]}"
        
        new_user = {
            "id": user_id,
            "email": normalized_user_data["email"],
            "name": normalized_user_data["name"],
            "given_name": normalized_user_data.get("given_name"),
            "family_name": normalized_user_data.get("family_name"),
            "profile_picture": normalized_user_data.get("profile_picture"),
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat(),
            
            # Auth provider information
            "auth_providers": [
                {
                    "provider": normalized_user_data["provider"],
                    "provider_id": normalized_user_data["provider_id"],
                    "tenant_id": normalized_user_data.get("tenant_id"),
                    "linked_at": datetime.utcnow().isoformat(),
                    "is_primary": True
                }
            ],
            
            # Vimarsh-specific data (initialize empty)
            "spiritual_preferences": {
                "favorite_personalities": [],
                "preferred_language": "english",
                "guidance_style": "compassionate"
            },
            "conversation_history": [],
            "analytics_data": {
                "total_sessions": 0,
                "avg_session_duration": 0,
                "favorite_topics": [],
                "first_login": datetime.utcnow().isoformat()
            },
            
            # Microsoft-specific data (if applicable)
            **({"job_title": normalized_user_data.get("job_title"), 
                "company": normalized_user_data.get("company")} 
               if normalized_user_data["provider"] == "microsoft" else {})
        }
        
        # Store in Cosmos DB
        self.users_container.create_item(new_user)
        logger.info(f"🕉️ Created new user: {user_id} via {normalized_user_data['provider']}")
        return new_user
    
    async def link_auth_provider(self, existing_user: Dict[str, Any], normalized_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Link additional auth provider to existing user"""
        
        # Check if provider already linked
        for provider in existing_user["auth_providers"]:
            if (provider["provider"] == normalized_user_data["provider"] and 
                provider["provider_id"] == normalized_user_data["provider_id"]):
                # Already linked, just update last login
                existing_user["last_login"] = datetime.utcnow().isoformat()
                self.users_container.upsert_item(existing_user)
                return existing_user
        
        # Add new provider
        new_provider = {
            "provider": normalized_user_data["provider"],
            "provider_id": normalized_user_data["provider_id"],
            "tenant_id": normalized_user_data.get("tenant_id"),
            "linked_at": datetime.utcnow().isoformat(),
            "is_primary": False  # Existing primary provider remains
        }
        
        existing_user["auth_providers"].append(new_provider)
        existing_user["last_login"] = datetime.utcnow().isoformat()
        
        # Update profile if new provider has better data
        if normalized_user_data["provider"] == "microsoft" and not existing_user.get("job_title"):
            existing_user["job_title"] = normalized_user_data.get("job_title")
            existing_user["company"] = normalized_user_data.get("company")
        
        self.users_container.upsert_item(existing_user)
        logger.info(f"🔗 Linked {normalized_user_data['provider']} to user: {existing_user['id']}")
        return existing_user

class HybridAuthService:
    """
    Handles authentication for both Microsoft (multitenant) and Google
    """
    
    def __init__(self):
        # Microsoft configuration
        self.ms_tenant_id = "80feb807-105c-4fb9-ab03-c9a818e35848"  # Your actual tenant ID
        self.ms_client_id = "e4bd74b8-9a82-40c6-8d52-3e231733095e"  # Your actual client ID
        self.ms_client_secret = os.getenv("ENTRA_CLIENT_SECRET")
        
        # Google configuration (for future)
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        # User service
        self.user_service = UserService()
    
    async def validate_microsoft_token(self, token: str) -> Dict[str, Any]:
        """
        Validate Microsoft JWT token from any tenant (multitenant)
        """
        try:
            # Decode token without verification to get tenant ID and key ID
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            tenant_id = unverified_payload.get("tid")
            key_id = jwt.get_unverified_header(token).get("kid")
            
            if not tenant_id:
                raise ValueError("Missing tenant ID in token")
            
            # Get Microsoft's public signing keys for this tenant
            jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
                jwks = response.json()
            
            # Find the correct key
            signing_key = None
            for key in jwks["keys"]:
                if key["kid"] == key_id:
                    signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break
            
            if not signing_key:
                raise ValueError("Unable to find signing key")
            
            # Verify token signature and claims
            payload = jwt.decode(
                token,
                key=signing_key,
                algorithms=["RS256"],
                audience=self.ms_client_id,
                issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0"
            )
            
            # Additional validations
            if payload.get("aud") != self.ms_client_id:
                raise ValueError("Invalid audience")
            
            # Token expiry check
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise ValueError("Token expired")
            
            return self.normalize_microsoft_user(payload)
            
        except Exception as e:
            logger.error(f"❌ Microsoft token validation failed: {str(e)}")
            raise AuthenticationError(f"Invalid Microsoft token: {str(e)}")
    
    async def validate_google_token(self, token: str) -> Dict[str, Any]:
        """
        Validate Google ID token (for future implementation)
        """
        try:
            # Google token validation
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                self.google_client_id
            )
            
            # Validate issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')
            
            return self.normalize_google_user(idinfo)
            
        except Exception as e:
            logger.error(f"❌ Google token validation failed: {str(e)}")
            raise AuthenticationError(f"Invalid Google token: {str(e)}")
    
    def normalize_microsoft_user(self, token_data: Dict) -> Dict[str, Any]:
        """Normalize Microsoft user data to common format"""
        return {
            "provider": "microsoft",
            "provider_id": token_data.get("oid"),  # Object ID - unique across all tenants
            "email": token_data.get("email") or token_data.get("preferred_username"),
            "name": token_data.get("name"),
            "given_name": token_data.get("given_name"),
            "family_name": token_data.get("family_name"),
            "tenant_id": token_data.get("tid"),
            "job_title": token_data.get("jobTitle"),
            "company": token_data.get("companyName"),
            "profile_picture": None  # Will be fetched separately via Graph API if needed
        }
    
    def normalize_google_user(self, token_data: Dict) -> Dict[str, Any]:
        """Normalize Google user data to common format"""
        return {
            "provider": "google",
            "provider_id": token_data.get("sub"),  # Subject - unique Google user ID
            "email": token_data.get("email"),
            "name": token_data.get("name"),
            "given_name": token_data.get("given_name"),
            "family_name": token_data.get("family_name"),
            "profile_picture": token_data.get("picture"),
            "email_verified": token_data.get("email_verified", False)
        }
    
    async def authenticate_user(self, token: str, provider: str) -> Dict[str, Any]:
        """
        Main authentication method - validates token and returns user data
        """
        try:
            # Validate token based on provider
            if provider == "microsoft":
                normalized_user = await self.validate_microsoft_token(token)
            elif provider == "google":
                normalized_user = await self.validate_google_token(token)
            else:
                raise AuthenticationError(f"Unsupported auth provider: {provider}")
            
            # Create or update user in database
            user = await self.user_service.create_or_update_user(normalized_user)
            
            logger.info(f"🕉️ User authenticated successfully: {user['id']} via {provider}")
            return {
                "user": user,
                "provider": provider,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")

# Azure Function handlers
auth_service = HybridAuthService()

@func.route(route="auth/microsoft", methods=["POST"])
async def authenticate_microsoft(req: func.HttpRequest) -> func.HttpResponse:
    """Handle Microsoft authentication"""
    try:
        request_data = req.get_json()
        access_token = request_data.get("access_token")
        
        if not access_token:
            return func.HttpResponse(
                "Missing access_token", 
                status_code=400
            )
        
        result = await auth_service.authenticate_user(access_token, "microsoft")
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            mimetype="application/json"
        )
        
    except AuthenticationError as e:
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=401,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"❌ Microsoft auth endpoint error: {str(e)}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )

@func.route(route="auth/google", methods=["POST"])
async def authenticate_google(req: func.HttpRequest) -> func.HttpResponse:
    """Handle Google authentication (future implementation)"""
    try:
        request_data = req.get_json()
        id_token = request_data.get("id_token")
        
        if not id_token:
            return func.HttpResponse(
                "Missing id_token", 
                status_code=400
            )
        
        result = await auth_service.authenticate_user(id_token, "google")
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            mimetype="application/json"
        )
        
    except AuthenticationError as e:
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=401,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"❌ Google auth endpoint error: {str(e)}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )

@func.route(route="auth/validate", methods=["POST"])
async def validate_token(req: func.HttpRequest) -> func.HttpResponse:
    """Generic token validation endpoint"""
    try:
        request_data = req.get_json()
        token = request_data.get("token")
        provider = request_data.get("provider")
        
        if not token or not provider:
            return func.HttpResponse(
                "Missing token or provider", 
                status_code=400
            )
        
        result = await auth_service.authenticate_user(token, provider)
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            mimetype="application/json"
        )
        
    except AuthenticationError as e:
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=401,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"❌ Token validation error: {str(e)}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )
