"""
Admin Authentication and Role-Based Access Control for Vimarsh
Implements the admin role system as per Tech Spec Section 19.10
"""

import os
import jwt
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List
from functools import wraps
import azure.functions as func
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User role enumeration for RBAC system"""
    USER = "user"                    # Standard spiritual guidance access
    ADMIN = "admin"                  # Cost management and user control access  
    SUPER_ADMIN = "super_admin"      # Emergency controls and role management

@dataclass
class VedUser:
    """User model with role support"""
    user_id: str
    email: str
    name: str
    role: UserRole = UserRole.USER
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    permissions: List[str] = field(default_factory=list)
    cost_limit: Optional[float] = None
    monthly_usage: float = 0.0

class AdminAuthService:
    """Admin authentication and role management service"""
    
    def __init__(self):
        self.admin_emails = self._get_admin_emails()
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-here')
        
    def _get_admin_emails(self) -> List[str]:
        """Get admin email addresses from environment"""
        admin_emails_str = os.getenv('ADMIN_EMAILS', '')
        if not admin_emails_str:
            logger.warning("🚨 No ADMIN_EMAILS configured - admin access disabled")
            return []
        
        emails = [email.strip().lower() for email in admin_emails_str.split(',')]
        logger.info(f"🔐 Admin emails configured: {len(emails)} addresses")
        return emails
    
    def is_admin_email(self, email: str) -> bool:
        """Check if email is in admin list"""
        return email.lower().strip() in self.admin_emails
    
    def create_admin_jwt_token(self, user: VedUser) -> str:
        """Create JWT token with admin role claims"""
        payload = {
            'sub': user.user_id,
            'email': user.email,
            'name': user.name,
            'role': user.role.value,
            'permissions': user.permissions,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'aud': 'vimarsh-api',
            'iss': 'vimarsh-auth'
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        logger.info(f"🔐 Created admin JWT token for {user.email} with role {user.role.value}")
        return token
    
    def validate_admin_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload.get('exp', 0)):
                logger.warning("🚨 Admin token expired")
                return None
            
            # Validate role
            user_role = payload.get('role', 'user')
            if user_role not in [role.value for role in UserRole]:
                logger.warning(f"🚨 Invalid role in token: {user_role}")
                return None
            
            return payload
        except jwt.InvalidTokenError as e:
            logger.warning(f"🚨 Invalid admin token: {str(e)}")
            return None
    
    def setup_initial_admin(self, user_email: str, user_name: str, user_id: str) -> Optional[VedUser]:
        """Setup initial admin during first deployment"""
        if not self.is_admin_email(user_email):
            logger.warning(f"🚨 Email {user_email} not in admin list")
            return None
        
        admin_user = VedUser(
            user_id=user_id,
            email=user_email,
            name=user_name,
            role=UserRole.ADMIN,
            permissions=['cost_management', 'user_management', 'system_monitoring'],
            is_active=True
        )
        
        logger.info(f"🔐 Initial admin setup for {user_email}")
        return admin_user
    
    def promote_user_to_admin(self, promoting_user: VedUser, target_email: str) -> bool:
        """Allow existing admin to promote another user"""
        if promoting_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            logger.warning(f"🚨 User {promoting_user.email} insufficient privileges to promote users")
            return False
        
        if not self.is_admin_email(target_email):
            logger.warning(f"🚨 Target email {target_email} not in admin list")
            return False
        
        logger.info(f"🔐 User {promoting_user.email} promoting {target_email} to admin")
        return True

def extract_bearer_token(req: func.HttpRequest) -> Optional[str]:
    """Extract bearer token from request headers"""
    auth_header = req.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header[7:]  # Remove 'Bearer ' prefix

def require_admin_role(required_role: UserRole = UserRole.ADMIN):
    """Decorator for admin-only endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(req: func.HttpRequest) -> func.HttpResponse:
            try:
                # Extract token
                token = extract_bearer_token(req)
                if not token:
                    logger.warning("🚨 Admin endpoint accessed without token")
                    return func.HttpResponse(
                        "Unauthorized: No token provided", 
                        status_code=401
                    )
                
                # Validate token
                auth_service = AdminAuthService()
                payload = auth_service.validate_admin_token(token)
                if not payload:
                    logger.warning("🚨 Invalid admin token used")
                    return func.HttpResponse(
                        "Unauthorized: Invalid token", 
                        status_code=401
                    )
                
                # Check role permissions
                user_role = UserRole(payload.get('role', 'user'))
                user_email = payload.get('email', 'unknown')
                
                if user_role == UserRole.SUPER_ADMIN:
                    # Super admin has access to everything
                    logger.info(f"🔐 Super admin access granted to {user_email}")
                    pass
                elif user_role == UserRole.ADMIN and required_role == UserRole.ADMIN:
                    # Admin has access to admin functions
                    logger.info(f"🔐 Admin access granted to {user_email}")
                    pass
                else:
                    logger.warning(f"🚨 Insufficient privileges: {user_email} role {user_role.value} required {required_role.value}")
                    return func.HttpResponse(
                        "Forbidden: Insufficient privileges", 
                        status_code=403
                    )
                
                # Add user context to request
                req.user_context = {
                    'user_id': payload.get('sub'),
                    'email': payload.get('email'),
                    'name': payload.get('name'),
                    'role': user_role.value,
                    'permissions': payload.get('permissions', [])
                }
                
                return await func(req)
                
            except Exception as e:
                logger.error(f"🚨 Admin auth error: {str(e)}")
                return func.HttpResponse(
                    "Internal server error", 
                    status_code=500
                )
                
        return wrapper
    return decorator

def require_permission(permission: str):
    """Decorator for permission-based access control"""
    def decorator(func):
        @wraps(func)
        async def wrapper(req: func.HttpRequest) -> func.HttpResponse:
            user_context = getattr(req, 'user_context', {})
            permissions = user_context.get('permissions', [])
            
            if permission not in permissions:
                logger.warning(f"🚨 Permission denied: {permission} required")
                return func.HttpResponse(
                    f"Forbidden: {permission} permission required", 
                    status_code=403
                )
            
            return await func(req)
        return wrapper
    return decorator

def get_user_context(req: func.HttpRequest) -> Dict[str, Any]:
    """Get user context from request (set by admin auth middleware)"""
    return getattr(req, 'user_context', {})

def log_admin_action(action: str, user_context: Dict[str, Any], details: Dict[str, Any] = None):
    """Log admin actions for audit trail"""
    user_email = user_context.get('email', 'unknown')
    user_role = user_context.get('role', 'unknown')
    
    logger.info(f"🔐 ADMIN ACTION: {action} by {user_email} ({user_role}) - {details or {}}")
