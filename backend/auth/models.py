"""
Generic, extensible user authentication models for flexible application integration.
Replaces domain-specific user models with configurable, reusable components.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import json
import logging

# Import the existing role system to maintain compatibility
from core.user_roles import UserRole, UserPermissions

logger = logging.getLogger(__name__)


class AuthenticationMode(Enum):
    """Authentication modes supported by the system"""
    DEVELOPMENT = "development"  # Relaxed auth for development
    PRODUCTION = "production"    # Full Microsoft Entra ID integration
    TESTING = "testing"          # Mock authentication for tests


@dataclass
class AuthenticatedUser:
    """
    Generic, extensible user model suitable for any application domain.
    Replaces domain-specific VedUser with configurable attributes.
    """
    # Core authentication fields (required)
    id: str
    email: str
    name: str
    
    # Optional identity fields  
    given_name: str = ""
    family_name: str = ""
    
    # Authorization system
    permissions: List[str] = field(default_factory=list)
    role: UserRole = UserRole.USER
    user_permissions: Optional[UserPermissions] = None
    
    # Extensible profile system - application-specific data
    profile: Dict[str, Any] = field(default_factory=dict)
    
    # Custom attributes for specific applications
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # System metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize user permissions based on role"""
        if self.user_permissions is None:
            self.user_permissions = UserPermissions.for_role(self.role)
    
    @classmethod
    def from_token_data(cls, token_data: Dict[str, Any], 
                       profile_config: Optional[Dict[str, Any]] = None) -> 'AuthenticatedUser':
        """
        Create AuthenticatedUser from JWT token claims.
        
        Args:
            token_data: JWT token claims
            profile_config: Application-specific profile configuration
        
        Returns:
            AuthenticatedUser instance
        """
        from core.user_roles import admin_role_manager
        
        email = token_data.get("email", "")
        
        # Determine user role and permissions
        role = admin_role_manager.get_user_role(email)
        user_permissions = admin_role_manager.get_user_permissions(email)
        
        # Build extensible profile based on configuration
        profile = cls._build_profile(token_data, profile_config or {})
        
        return cls(
            id=token_data.get("sub", ""),
            email=email,
            name=token_data.get("name", ""),
            given_name=token_data.get("given_name", ""),
            family_name=token_data.get("family_name", ""),
            permissions=token_data.get("roles", []),
            role=role,
            user_permissions=user_permissions,
            profile=profile,
            last_login=datetime.utcnow()
        )
    
    @classmethod
    def _build_profile(cls, token_data: Dict[str, Any], 
                      profile_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build user profile based on configuration.
        
        Args:
            token_data: JWT token claims
            profile_config: Profile configuration for the application
        
        Returns:
            Built profile dictionary
        """
        profile = {
            "profile_id": token_data.get("sub", ""),
            "subscription_tier": "free",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add application-specific fields based on config
        if "required_fields" in profile_config:
            for field in profile_config["required_fields"]:
                if field in token_data:
                    profile[field] = token_data[field]
                else:
                    # Set default values for required fields
                    profile[field] = cls._get_default_value(field)
        
        if "optional_fields" in profile_config:
            for field in profile_config["optional_fields"]:
                if field in token_data:
                    profile[field] = token_data[field]
        
        return profile
    
    @staticmethod
    def _get_default_value(field_name: str) -> Any:
        """Get default value for a profile field"""
        defaults = {
            "spiritual_preferences": [],
            "guidance_history": [],
            "meditation_level": "beginner",
            "text_preferences": "modern",
            "language": "English",
            "communication_style": "reverent",
            "apps_enrolled": []
        }
        return defaults.get(field_name, "")
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return (
            permission in self.permissions or 
            (self.user_permissions and getattr(self.user_permissions, permission, False))
        )
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def update_profile(self, updates: Dict[str, Any]) -> None:
        """Update user profile with new data"""
        self.profile.update(updates)
        logger.info(f"🔄 Updated profile for user {self.email}")
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set a custom attribute for the user"""
        self.attributes[key] = value
        logger.debug(f"📝 Set attribute {key} for user {self.email}")
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get a custom attribute value"""
        return self.attributes.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for serialization"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "permissions": self.permissions,
            "role": self.role.value,
            "profile": self.profile,
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active
        }
    
    def __repr__(self) -> str:
        return f"AuthenticatedUser(id='{self.id}', email='{self.email}', role={self.role})"


# Application-specific profile configurations
class ProfileConfigurations:
    """Pre-defined profile configurations for different applications"""
    
    VIMARSH_CONFIG = {
        "required_fields": ["spiritual_preferences", "guidance_history"],
        "optional_fields": ["meditation_level", "text_preferences", "language", "communication_style"],
        "default_attributes": {
            "apps_enrolled": ["vimarsh"],
            "subscription_tier": "free",
            "spiritual_interests": [],
            "communication_style": "reverent"
        }
    }
    
    GENERIC_CONFIG = {
        "required_fields": ["profile_id"],
        "optional_fields": ["language", "preferences"],
        "default_attributes": {
            "subscription_tier": "free"
        }
    }
    
    @classmethod
    def get_config(cls, application: str) -> Dict[str, Any]:
        """Get configuration for a specific application"""
        configs = {
            "vimarsh": cls.VIMARSH_CONFIG,
            "generic": cls.GENERIC_CONFIG
        }
        return configs.get(application.lower(), cls.GENERIC_CONFIG)


# Factory function for creating users with application-specific profiles
def create_authenticated_user(token_data: Dict[str, Any], 
                            application: str = "generic") -> AuthenticatedUser:
    """
    Factory function to create AuthenticatedUser with application-specific configuration.
    
    Args:
        token_data: JWT token claims
        application: Application name for profile configuration
    
    Returns:
        AuthenticatedUser instance configured for the application
    """
    profile_config = ProfileConfigurations.get_config(application)
    return AuthenticatedUser.from_token_data(token_data, profile_config)
