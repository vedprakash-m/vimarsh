"""
Admin service for administrative functions and monitoring.
Lightweight implementation focused on core admin needs with proper security.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class AdminService:
    """Lightweight admin service for core administrative functions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.admin_emails = self._get_admin_emails()
        self.super_admin_emails = self._get_super_admin_emails()
    
    def _get_admin_emails(self) -> List[str]:
        """Get admin email addresses from environment"""
        admin_emails_str = os.getenv('ADMIN_EMAILS', '')
        if not admin_emails_str:
            self.logger.warning("🚨 No ADMIN_EMAILS configured - admin access disabled")
            return []
        
        emails = [email.strip().lower() for email in admin_emails_str.split(',')]
        self.logger.info(f"🔐 Admin emails configured: {len(emails)} addresses")
        return emails
    
    def _get_super_admin_emails(self) -> List[str]:
        """Get super admin email addresses from environment"""
        super_admin_emails_str = os.getenv('SUPER_ADMIN_EMAILS', '')
        if not super_admin_emails_str:
            return []
        
        emails = [email.strip().lower() for email in super_admin_emails_str.split(',')]
        self.logger.info(f"🔐 Super admin emails configured: {len(emails)} addresses")
        return emails
    
    def _is_admin_email(self, email: str) -> bool:
        """Check if email is in admin list"""
        if not email:
            return False
        return email.lower().strip() in self.admin_emails
    
    def _is_super_admin_email(self, email: str) -> bool:
        """Check if email is in super admin list"""
        if not email:
            return False
        return email.lower().strip() in self.super_admin_emails
    
    def get_user_role(self, user_email: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user role information based on email authentication.
        
        Args:
            user_email: User's email address for role validation
            user_id: User identifier (optional)
            
        Returns:
            Dict with role information
        """
        try:
            # Default to non-admin user
            role = "user"
            permissions = ["read"]
            
            if user_email:
                # Check for super admin first
                if self._is_super_admin_email(user_email):
                    role = "super_admin"
                    permissions = ["read", "write", "admin", "super_admin"]
                    self.logger.info(f"🔐 Super admin access granted to: {user_email}")
                
                # Check for regular admin
                elif self._is_admin_email(user_email):
                    role = "admin"
                    permissions = ["read", "write", "admin"]
                    self.logger.info(f"🔐 Admin access granted to: {user_email}")
                
                # Regular user (or non-admin email)
                else:
                    self.logger.info(f"👤 Regular user access for: {user_email}")
            else:
                self.logger.warning("⚠️ No user email provided - defaulting to user role")
            
            role_data: Dict[str, Any] = {
                "role": role,
                "permissions": permissions,
                "user_id": user_id or "anonymous",
                "user_email": user_email or "anonymous",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "admin_v1.0"
            }
            
            return role_data
            
        except Exception as e:
            self.logger.error(f"❌ Error getting user role: {e}")
            return {
                "role": "user",
                "permissions": ["read"],
                "error": str(e),
                "user_email": user_email or "anonymous",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get basic system health information"""
        try:
            health_info: Dict[str, Any] = {
                "status": "healthy",
                "admin_service": "active",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime": "active",
                "version": "admin_v1.0"
            }
            
            return health_info
            
        except Exception as e:
            self.logger.error(f"❌ Error getting system health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def log_admin_action(self, action: str, user_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log administrative actions for audit trail"""
        try:
            log_entry: Dict[str, Any] = {
                "action": action,
                "user_id": user_id or "anonymous",
                "details": details or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "admin_v1.0"
            }
            
            self.logger.info(f"Admin action: {action} by {user_id or 'anonymous'}")
            # Future: Store in proper audit log
            # For now, just log the action
            self.logger.debug(f"Audit entry: {log_entry}")
            
        except Exception as e:
            self.logger.error(f"❌ Error logging admin action: {e}")
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic system statistics"""
        try:
            stats: Dict[str, Any] = {
                "total_personalities": 12,  # Static for now
                "system_status": "operational",
                "admin_features": [
                    "role_management",
                    "health_monitoring",
                    "audit_logging"
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "admin_v1.0"
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Error getting basic stats: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
