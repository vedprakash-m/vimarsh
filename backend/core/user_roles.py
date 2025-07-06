"""
User Role Management System for Vimarsh
Implements role-based access control (RBAC) with admin capabilities
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os
import logging

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles in the Vimarsh system"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"UserRole.{self.name}"


@dataclass
class UserPermissions:
    """Permissions associated with user roles"""
    can_use_spiritual_guidance: bool = True
    can_view_own_usage: bool = True
    can_view_cost_dashboard: bool = False
    can_manage_users: bool = False
    can_block_users: bool = False
    can_view_system_costs: bool = False
    can_configure_budgets: bool = False
    can_access_admin_endpoints: bool = False
    can_override_budget_limits: bool = False
    can_manage_emergency_controls: bool = False
    
    @classmethod
    def for_role(cls, role: UserRole) -> 'UserPermissions':
        """Get permissions for a specific role"""
        if role == UserRole.USER:
            return cls()
        elif role == UserRole.ADMIN:
            return cls(
                can_view_cost_dashboard=True,
                can_manage_users=True,
                can_block_users=True,
                can_view_system_costs=True,
                can_configure_budgets=True,
                can_access_admin_endpoints=True
            )
        elif role == UserRole.SUPER_ADMIN:
            return cls(
                can_view_cost_dashboard=True,
                can_manage_users=True,
                can_block_users=True,
                can_view_system_costs=True,
                can_configure_budgets=True,
                can_access_admin_endpoints=True,
                can_override_budget_limits=True,
                can_manage_emergency_controls=True
            )
        else:
            logger.warning(f"Unknown role: {role}, defaulting to USER permissions")
            return cls()


class AdminRoleManager:
    """Manages admin role assignments and permissions"""
    
    def __init__(self):
        self.admin_emails = self._load_admin_emails()
        self.super_admin_emails = self._load_super_admin_emails()
        
    def _load_admin_emails(self) -> List[str]:
        """Load admin emails from environment variable"""
        admin_emails_str = os.getenv('ADMIN_EMAILS', '')
        if not admin_emails_str:
            return []
        
        emails = [email.strip().lower() for email in admin_emails_str.split(',') if email.strip()]
        logger.info(f"🔐 Loaded {len(emails)} admin emails")
        return emails
    
    def _load_super_admin_emails(self) -> List[str]:
        """Load super admin emails from environment variable"""
        super_admin_emails_str = os.getenv('SUPER_ADMIN_EMAILS', '')
        if not super_admin_emails_str:
            return []
        
        emails = [email.strip().lower() for email in super_admin_emails_str.split(',') if email.strip()]
        logger.info(f"🔐 Loaded {len(emails)} super admin emails")
        return emails
    
    def get_user_role(self, email: str) -> UserRole:
        """Determine user role based on email"""
        if not email:
            return UserRole.USER
        
        email_lower = email.lower()
        
        if email_lower in self.super_admin_emails:
            return UserRole.SUPER_ADMIN
        elif email_lower in self.admin_emails:
            return UserRole.ADMIN
        else:
            return UserRole.USER
    
    def get_user_permissions(self, email: str) -> UserPermissions:
        """Get permissions for a user based on their role"""
        role = self.get_user_role(email)
        return UserPermissions.for_role(role)
    
    def is_admin(self, email: str) -> bool:
        """Check if user has admin privileges"""
        role = self.get_user_role(email)
        return role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def is_super_admin(self, email: str) -> bool:
        """Check if user has super admin privileges"""
        role = self.get_user_role(email)
        return role == UserRole.SUPER_ADMIN
    
    def add_admin(self, email: str) -> bool:
        """Add a new admin (can only be done by super admin)"""
        if not email or email.lower() in self.admin_emails:
            return False
        
        self.admin_emails.append(email.lower())
        logger.info(f"🔐 Added new admin: {email}")
        return True
    
    def remove_admin(self, email: str) -> bool:
        """Remove an admin (can only be done by super admin)"""
        if not email or email.lower() not in self.admin_emails:
            return False
        
        self.admin_emails.remove(email.lower())
        logger.info(f"🔐 Removed admin: {email}")
        return True
    
    def get_all_admins(self) -> Dict[str, List[str]]:
        """Get all admin users (for super admin view)"""
        return {
            "admins": self.admin_emails,
            "super_admins": self.super_admin_emails
        }


# Global admin role manager instance
admin_role_manager = AdminRoleManager()
