"""
Enhanced Unified Authentication Service with Database Persistence
Extends the existing UnifiedAuthService while adding user persistence and deduplication
Maintains 100% compatibility with existing admin system
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from azure.cosmos import CosmosClient
from auth.unified_auth_service import UnifiedAuthService
from auth.models import AuthenticatedUser, create_authenticated_user
from core.user_roles import admin_role_manager, UserRole, UserPermissions
import azure.functions as func

logger = logging.getLogger(__name__)


class UserPersistenceService:
    """Handles user persistence in Cosmos DB with deduplication"""
    
    def __init__(self):
        # Initialize Cosmos DB client
        cosmos_connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
        if cosmos_connection_string:
            self.cosmos_client = CosmosClient.from_connection_string(cosmos_connection_string)
            self.database = self.cosmos_client.get_database_client("vimarsh-multi-personality")
            self.users_container = self.database.get_container_client("users")
            self.db_available = True
            logger.info("✅ UserPersistenceService connected to Cosmos DB")
        else:
            logger.warning("⚠️ No Cosmos DB connection string found - operating without persistence")
            self.db_available = False
    
    async def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find existing user by email to prevent duplicates"""
        if not self.db_available or not email:
            return None
            
        try:
            query = "SELECT * FROM users u WHERE u.email = @email"
            # Use object type for parameters to satisfy type checker
            parameters: list = [{"name": "@email", "value": email.lower()}]
            
            items = list(self.users_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                logger.info(f"📧 Found existing user by email: {email}")
                return items[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding user by email: {str(e)}")
            return None
    
    async def find_user_by_auth_id(self, auth_id: str) -> Optional[Dict[str, Any]]:
        """Find user by Microsoft auth ID (sub/oid)"""
        if not self.db_available or not auth_id:
            return None
            
        try:
            query = "SELECT * FROM users u WHERE u.microsoft_auth_id = @auth_id"
            parameters: list = [{"name": "@auth_id", "value": auth_id}]
            
            items = list(self.users_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                logger.info(f"🔐 Found existing user by auth ID: {auth_id}")
                return items[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding user by auth ID: {str(e)}")
            return None
    
    async def create_or_update_user(self, authenticated_user: AuthenticatedUser) -> Dict[str, Any]:
        """Create new user or update existing user, maintaining consistent user ID"""
        if not self.db_available:
            logger.warning("⚠️ Database not available - cannot persist user")
            return self._convert_to_dict(authenticated_user)
        
        try:
            # First try to find by Microsoft auth ID
            existing_user = await self.find_user_by_auth_id(authenticated_user.id)
            
            # If not found by auth ID, try by email
            if not existing_user:
                existing_user = await self.find_user_by_email(authenticated_user.email)
            
            if existing_user:
                # Update existing user
                return await self._update_existing_user(existing_user, authenticated_user)
            else:
                # Create new user
                return await self._create_new_user(authenticated_user)
                
        except Exception as e:
            logger.error(f"❌ Error in create_or_update_user: {str(e)}")
            # Fallback to in-memory user object
            return self._convert_to_dict(authenticated_user)
    
    async def _update_existing_user(self, existing_user: Dict[str, Any], authenticated_user: AuthenticatedUser) -> Dict[str, Any]:
        """Update existing user with latest authentication data"""
        try:
            current_time = datetime.utcnow().isoformat()
            
            # Update fields that might have changed
            existing_user.update({
                "name": authenticated_user.name or existing_user.get("name"),
                "given_name": authenticated_user.given_name or existing_user.get("given_name"),
                "family_name": authenticated_user.family_name or existing_user.get("family_name"),
                "job_title": authenticated_user.job_title or existing_user.get("job_title"),
                "company_name": authenticated_user.company_name or existing_user.get("company_name"),
                "tenant_id": authenticated_user.tenant_id or existing_user.get("tenant_id"),
                "last_login": current_time,
                
                # Ensure auth fields are updated
                "microsoft_auth_id": authenticated_user.id,
                "email": authenticated_user.email.lower(),
                
                # Update admin role information
                "role": authenticated_user.role.value if authenticated_user.role else existing_user.get("role", "user"),
                "permissions": [p for p in authenticated_user.permissions] if authenticated_user.permissions else existing_user.get("permissions", [])
            })
            
            # Upsert to database
            self.users_container.upsert_item(existing_user)
            logger.info(f"🔄 Updated existing user: {existing_user['id']} (email: {authenticated_user.email})")
            
            return existing_user
            
        except Exception as e:
            logger.error(f"❌ Error updating existing user: {str(e)}")
            return self._convert_to_dict(authenticated_user)
    
    async def _create_new_user(self, authenticated_user: AuthenticatedUser) -> Dict[str, Any]:
        """Create a completely new user with consistent ID format"""
        try:
            # Generate consistent user ID using email domain and timestamp
            email_prefix = authenticated_user.email.split('@')[0] if authenticated_user.email else "user"
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            auth_suffix = authenticated_user.id[:8] if authenticated_user.id else "unknown"
            
            user_id = f"user_{email_prefix}_{timestamp}_{auth_suffix}"
            current_time = datetime.utcnow().isoformat()
            
            new_user = {
                "id": user_id,
                "email": authenticated_user.email.lower() if authenticated_user.email else "",
                "name": authenticated_user.name or "",
                "given_name": authenticated_user.given_name,
                "family_name": authenticated_user.family_name,
                "job_title": authenticated_user.job_title,
                "company_name": authenticated_user.company_name,
                "tenant_id": authenticated_user.tenant_id,
                "microsoft_auth_id": authenticated_user.id,
                "auth_provider": "microsoft",
                "created_at": current_time,
                "last_login": current_time,
                
                # Admin role information
                "role": authenticated_user.role.value if authenticated_user.role else "user",
                "permissions": [p for p in authenticated_user.permissions] if authenticated_user.permissions else [],
                
                # Vimarsh-specific profile
                "profile": authenticated_user.profile or {},
                "attributes": authenticated_user.attributes or {},
                
                # Initialize conversation tracking
                "conversation_sessions": [],
                "total_sessions": 0,
                "first_login": current_time
            }
            
            # Create in database
            self.users_container.create_item(new_user)
            logger.info(f"🆕 Created new user: {user_id} (email: {authenticated_user.email})")
            
            return new_user
            
        except Exception as e:
            logger.error(f"❌ Error creating new user: {str(e)}")
            return self._convert_to_dict(authenticated_user)
    
    def _convert_to_dict(self, authenticated_user: AuthenticatedUser) -> Dict[str, Any]:
        """Convert AuthenticatedUser to dictionary format for fallback"""
        current_time = datetime.utcnow().isoformat()
        fallback_time = datetime.utcnow().strftime('%H%M%S')
        
        return {
            "id": f"fallback_{authenticated_user.email.split('@')[0]}_{fallback_time}" if authenticated_user.email else "fallback_user",
            "email": authenticated_user.email.lower() if authenticated_user.email else "",
            "name": authenticated_user.name or "",
            "microsoft_auth_id": authenticated_user.id,
            "role": authenticated_user.role.value if authenticated_user.role else "user",
            "permissions": [p for p in authenticated_user.permissions] if authenticated_user.permissions else [],
            "created_at": current_time,
            "last_login": current_time,
            "fallback_mode": True
        }


class EnhancedUnifiedAuthService(UnifiedAuthService):
    """
    Enhanced version of UnifiedAuthService with database persistence
    Maintains 100% compatibility with existing admin authentication
    """
    
    def __init__(self, application: str = "vimarsh"):
        super().__init__()  # Fix constructor call
        self.application = application
        self.user_persistence = UserPersistenceService()
        self._persistent_user_cache: Dict[str, str] = {}  # Cache for persistent user IDs
        logger.info("🔧 EnhancedUnifiedAuthService initialized with database persistence")
    
    async def extract_user_from_request(self, req: func.HttpRequest) -> Optional[AuthenticatedUser]:
        """
        Enhanced user extraction with database persistence
        Maintains exact same interface as original UnifiedAuthService
        """
        try:
            # First get the authenticated user using existing logic
            authenticated_user = await super().extract_user_from_request(req)
            
            if not authenticated_user:
                logger.debug("🚫 No authenticated user from parent service")
                return None
            
            # Ensure admin role is properly set using existing AdminRoleManager
            if authenticated_user.email:
                # Use existing admin role manager (preserves all existing admin logic)
                role = admin_role_manager.get_user_role(authenticated_user.email)
                permissions = admin_role_manager.get_user_permissions(authenticated_user.email)
                
                # Update user object with proper admin roles
                authenticated_user.role = role
                authenticated_user.user_permissions = permissions
                
                logger.debug(f"🔐 Role assignment: {authenticated_user.email} -> {role}")
            
            # Persist user to database (with deduplication)
            try:
                user_record = await self.user_persistence.create_or_update_user(authenticated_user)
                
                # Cache the persistent user ID mapping
                if user_record and not user_record.get("fallback_mode"):
                    cache_key = f"{authenticated_user.email}_{authenticated_user.id}"
                    self._persistent_user_cache[cache_key] = user_record["id"]
                    logger.info(f"💾 User persisted: {user_record['id']} (auth_id: {authenticated_user.id})")
                
            except Exception as persistence_error:
                logger.warning(f"⚠️ User persistence failed, continuing with in-memory user: {persistence_error}")
                # Continue with the authenticated user even if persistence fails
            
            return authenticated_user
            
        except Exception as e:
            logger.error(f"❌ Enhanced authentication error: {str(e)}")
            # Fallback to parent implementation
            return await super().extract_user_from_request(req)
    
    async def get_persistent_user_id(self, authenticated_user: AuthenticatedUser) -> str:
        """
        Get the persistent user ID for memory/conversation storage
        This solves the cross-session memory problem
        """
        # Check cache first
        cache_key = f"{authenticated_user.email}_{authenticated_user.id}"
        if cache_key in self._persistent_user_cache:
            return self._persistent_user_cache[cache_key]
        
        # Try to find existing user in database
        if authenticated_user.email:
            try:
                existing_user = await self.user_persistence.find_user_by_email(authenticated_user.email)
                if existing_user:
                    self._persistent_user_cache[cache_key] = existing_user["id"]
                    return existing_user["id"]
            except Exception as e:
                logger.warning(f"⚠️ Could not find persistent user ID: {e}")
        
        # Fallback to auth ID for backward compatibility
        return authenticated_user.id
    
    def get_health_status(self) -> Dict[str, Any]:
        """Enhanced health status including database connectivity"""
        parent_status = super().get_health_status() if hasattr(super(), 'get_health_status') else {}
        
        return {
            **parent_status,
            "database_persistence": self.user_persistence.db_available,
            "service_type": "enhanced_unified_auth",
            "features": [
                "user_deduplication",
                "cross_session_memory",
                "admin_role_preservation",
                "database_persistence"
            ]
        }


# Backward compatibility - can be imported as UnifiedAuthService
EnhancedAuthService = EnhancedUnifiedAuthService
