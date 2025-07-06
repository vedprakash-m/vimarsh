"""
Admin API endpoints for cost management and user administration
Requires admin privileges for access
"""

import json
import logging
import os
from azure.functions import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from auth.enhanced_auth_middleware import admin_required, super_admin_required
from core.token_tracker import token_tracker
from core.budget_validator import budget_validator
from core.user_roles import admin_role_manager
from core.admin_error_handling import (
    with_admin_error_handling,
    with_graceful_degradation,
    with_retry_logic,
    validate_admin_request,
    COST_DASHBOARD_FALLBACK,
    USER_MANAGEMENT_FALLBACK,
    SYSTEM_HEALTH_FALLBACK,
    BUDGET_MANAGEMENT_FALLBACK,
    ROLE_MANAGEMENT_FALLBACK,
    USER_ROLE_FALLBACK
)

logger = logging.getLogger(__name__)


@admin_required
@with_admin_error_handling
@with_graceful_degradation(fallback_data=COST_DASHBOARD_FALLBACK)
@validate_admin_request()
async def admin_cost_dashboard(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint to view cost dashboard and system usage
    GET /api/admin/cost-dashboard
    """
    # Get query parameters with validation
    days = int(req.params.get('days', 30))
    limit = int(req.params.get('limit', 10))
    
    # Validate parameters
    if days < 1 or days > 365:
        raise ValueError("Days parameter must be between 1 and 365")
    if limit < 1 or limit > 100:
        raise ValueError("Limit parameter must be between 1 and 100")
    
    # Get system data with proper error handling
    system_usage = token_tracker.get_system_usage(days)
    top_users = token_tracker.get_top_users(limit)
    budget_summary = budget_validator.get_budget_summary()
    recent_alerts = [
        alert.to_dict() for alert in budget_validator.budget_alerts
        if alert.timestamp > datetime.utcnow() - timedelta(hours=24)
    ]
    
    response_data = {
        'system_usage': system_usage,
        'top_users': top_users,
        'budget_summary': budget_summary,
        'recent_alerts': recent_alerts,
        'dashboard_generated': datetime.utcnow().isoformat(),
        'period_days': days,
        'mode': 'development' if os.getenv('AZURE_FUNCTIONS_ENVIRONMENT') != 'Production' else 'production'
    }
    
    return HttpResponse(
        json.dumps(response_data),
        mimetype="application/json",
        status_code=200,
        headers={"Access-Control-Allow-Origin": "*"}
    )


@admin_required
@with_admin_error_handling
@with_graceful_degradation(fallback_data=USER_MANAGEMENT_FALLBACK)
@validate_admin_request()
async def admin_user_management(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint for user management operations
    GET /api/admin/users - List users
    POST /api/admin/users/{user_id}/block - Block user
    POST /api/admin/users/{user_id}/unblock - Unblock user
    """
    method = req.method
    url_parts = req.url.split('/')
    
    if method == "GET":
        # List users with usage stats
        limit = int(req.params.get('limit', 100))
        sort_by = req.params.get('sort', 'cost_desc')
        
        # Validate parameters
        if limit < 1 or limit > 1000:
            raise ValueError("Limit parameter must be between 1 and 1000")
        if sort_by not in ['cost_desc', 'cost_asc', 'usage_desc', 'usage_asc', 'email']:
            raise ValueError("Invalid sort parameter")
        
        # Get users with proper error handling
        users = token_tracker.get_top_users(limit)
        
        # Add budget status for each user with error handling
        for user in users:
            try:
                user_id = user.get('user_id', 'unknown')
                budget_status = budget_validator.get_user_budget_status(user_id)
                user['budget_status'] = budget_status
            except Exception as e:
                logger.warning(f"Failed to get budget status for user {user_id}: {e}")
                user['budget_status'] = {'status': 'unknown', 'error': 'Budget status unavailable'}
        
        # Sort users if requested
        if sort_by == 'cost_desc':
            users.sort(key=lambda x: x.get('current_month_cost_usd', 0), reverse=True)
        elif sort_by == 'cost_asc':
            users.sort(key=lambda x: x.get('current_month_cost_usd', 0))
        elif sort_by == 'email':
            users.sort(key=lambda x: x.get('user_email', ''))
        
        return HttpResponse(
            json.dumps({
                'users': users,
                'total_users': len(users),
                'blocked_users': len(budget_validator.blocked_users),
                'sort_applied': sort_by,
                'retrieved_at': datetime.utcnow().isoformat()
            }),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    elif method == "POST":
        # Enhanced POST handling with validation
        if 'users' not in url_parts:
            raise ValueError("Invalid URL format for user management")
        
        user_index = url_parts.index('users')
        if user_index + 1 >= len(url_parts):
            raise ValueError("User ID required in URL")
        
        user_id = url_parts[user_index + 1]
        action = url_parts[user_index + 2] if user_index + 2 < len(url_parts) else None
        
        if not action or action not in ['block', 'unblock']:
            raise ValueError("Valid action (block/unblock) required")
        
        admin_user = getattr(req, 'user', None)
        admin_email = admin_user.email if admin_user else "system"
        
        if action == "block":
            budget_validator.blocked_users.add(user_id)
            logger.info(f"🚫 User {user_id} blocked by admin {admin_email}")
            
            return HttpResponse(
                json.dumps({
                    'message': f'User {user_id} blocked successfully',
                    'action': 'block',
                    'admin': admin_email,
                    'timestamp': datetime.utcnow().isoformat()
                }),
                mimetype="application/json",
                status_code=200,
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        elif action == "unblock":
            try:
                success = budget_validator.unblock_user(user_id, admin_email)
            except AttributeError:
                # Handle case where unblock_user method doesn't exist
                if user_id in budget_validator.blocked_users:
                    budget_validator.blocked_users.remove(user_id)
                    success = True
                else:
                    success = False
            
            return HttpResponse(
                json.dumps({
                    'message': f'User {user_id} unblocked successfully' if success else 'User not found or not blocked',
                    'action': 'unblock',
                    'success': success,
                    'admin': admin_email,
                    'timestamp': datetime.utcnow().isoformat()
                }),
                mimetype="application/json",
                status_code=200 if success else 404,
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    else:
        raise ValueError(f"HTTP method {method} not supported for user management")


@admin_required
@with_admin_error_handling
@with_graceful_degradation(fallback_data=BUDGET_MANAGEMENT_FALLBACK)
@validate_admin_request()
async def admin_budget_management(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint for budget management
    GET /api/admin/budgets - List all budgets
    POST /api/admin/budgets - Create/update budget
    POST /api/admin/budgets/{user_id}/override - Override budget limits
    """
    Admin endpoint for budget management
    GET /api/admin/budgets - List all budgets
    POST /api/admin/budgets - Create/update budget
    POST /api/admin/budgets/{user_id}/override - Override budget limits
    """
    method = req.method
    url_parts = req.url.split('/')
    
    if method == "GET":
        # List all budgets with validation
        limit = int(req.params.get('limit', 100))
        if limit < 1 or limit > 1000:
            raise ValueError("Limit parameter must be between 1 and 1000")
        
        budgets = []
        for user_id, budget in budget_validator.budget_limits.items():
            budget_data = budget.to_dict()
            budget_data['status'] = budget_validator.get_user_budget_status(user_id)
            budgets.append(budget_data)
        
        return HttpResponse(
            json.dumps({
                'budgets': budgets[:limit],
                'total_budgets': len(budgets),
                'default_limits': budget_validator.default_limits
            }),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    elif method == "POST":
        # Create or update budget
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        if 'override' in req.url:
            # Budget override
            user_index = url_parts.index('budgets')
            if user_index + 1 >= len(url_parts):
                raise ValueError("User ID required for budget override")
            
            user_id = url_parts[user_index + 1]
            reason = body.get('reason', 'Admin override')
            
            admin_user = getattr(req, 'user', None)
            admin_email = admin_user.email if admin_user else "system"
            
            success = budget_validator.override_budget(user_id, admin_email, reason)
            
            return HttpResponse(
                json.dumps({
                    'message': f'Budget override {"successful" if success else "failed"}',
                    'user_id': user_id,
                    'reason': reason,
                    'admin': admin_email,
                    'success': success
                }),
                mimetype="application/json",
                status_code=200 if success else 404,
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        else:
            # Create/update budget
            user_id = body.get('user_id')
            user_email = body.get('user_email')
            monthly_limit = float(body.get('monthly_limit', 50.0))
            daily_limit = float(body.get('daily_limit', monthly_limit / 30))
            per_request_limit = float(body.get('per_request_limit', 0.50))
            
            if not user_id or not user_email:
                raise ValueError("user_id and user_email are required")
            
            # Validate budget limits
            if monthly_limit <= 0 or daily_limit <= 0 or per_request_limit <= 0:
                raise ValueError("All budget limits must be positive")
            
            budget = budget_validator.set_user_budget(
                user_id=user_id,
                user_email=user_email,
                monthly_limit=monthly_limit,
                daily_limit=daily_limit,
                per_request_limit=per_request_limit
            )
            
            return HttpResponse(
                json.dumps({
                    'message': 'Budget updated successfully',
                    'budget': budget.to_dict()
                }),
                mimetype="application/json",
                status_code=200,
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    else:
        raise ValueError(f"HTTP method {method} not supported for budget management")


@super_admin_required
@with_admin_error_handling
@with_graceful_degradation(fallback_data=ROLE_MANAGEMENT_FALLBACK)
@validate_admin_request()
async def super_admin_role_management(req: HttpRequest) -> HttpResponse:
    """
    Super admin endpoint for role management
    GET /api/admin/roles - List all admin roles
    POST /api/admin/roles - Add/remove admin roles
    """
    method = req.method
    
    if method == "GET":
        # List all admin roles
        all_admins = admin_role_manager.get_all_admins()
        
        return HttpResponse(
            json.dumps({
                'admins': all_admins,
                'total_admins': len(all_admins['admins']),
                'total_super_admins': len(all_admins['super_admins'])            }),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    elif method == "POST":
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        action = body.get('action')  # 'add' or 'remove'
        email = body.get('email')
        
        if not action or not email:
            raise ValueError("action and email are required")
        
        if action not in ['add', 'remove']:
            raise ValueError("Invalid action. Use 'add' or 'remove'")
        
        super_admin_user = getattr(req, 'user', None)
        super_admin_email = super_admin_user.email if super_admin_user else "system"
        
        if action == 'add':
            success = admin_role_manager.add_admin(email)
            message = f'Admin role {"added" if success else "already exists or invalid"}'
        elif action == 'remove':
            success = admin_role_manager.remove_admin(email)
            message = f'Admin role {"removed" if success else "not found"}'
        
        return HttpResponse(
            json.dumps({
                'message': message,
                'action': action,
                'email': email,
                'success': success,
                'super_admin': super_admin_email
            }),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    else:
        raise ValueError(f"HTTP method {method} not supported for role management")


@admin_required
@with_admin_error_handling
@with_graceful_degradation(fallback_data=SYSTEM_HEALTH_FALLBACK)
@validate_admin_request()
async def admin_system_health(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint for system health monitoring
    GET /api/admin/health
    """
    # Get system statistics
    days = int(req.params.get('days', 7))
    if days < 1 or days > 30:
        raise ValueError("Days parameter must be between 1 and 30")
    
    system_usage = token_tracker.get_system_usage(days)
    budget_summary = budget_validator.get_budget_summary()
    
    # Calculate health metrics
    total_users = system_usage['total_users']
    blocked_users = len(budget_validator.blocked_users)
    alert_count = len(budget_validator.budget_alerts)
    
    # Health score calculation
    health_score = 100
    if blocked_users > 0:
        health_score -= min(blocked_users * 10, 30)
    if alert_count > 10:
        health_score -= min((alert_count - 10) * 2, 20)
    
    health_status = "excellent" if health_score >= 90 else "good" if health_score >= 70 else "warning" if health_score >= 50 else "critical"
    
    return HttpResponse(
        json.dumps({
            'health_score': health_score,
            'health_status': health_status,
            'system_metrics': {
                'total_users': total_users,
                'blocked_users': blocked_users,
                'active_alerts': alert_count,
                f'total_requests_{days}d': system_usage['total_requests'],
                f'total_cost_{days}d': system_usage['total_cost_usd']
            },
            'system_usage': system_usage,
            'budget_summary': budget_summary,
            'timestamp': datetime.utcnow().isoformat()
        }),
        mimetype="application/json",
        status_code=200,
        headers={"Access-Control-Allow-Origin": "*"}
    )


@admin_required
@with_admin_error_handling
@with_graceful_degradation(fallback_data=USER_ROLE_FALLBACK)
@validate_admin_request()
async def admin_get_user_role(req: HttpRequest) -> HttpResponse:
    """
    Get user role and permissions - Zero-trust security implementation
    GET /api/admin/role
    """
    # Get user from enhanced auth middleware
    user = getattr(req, 'user', None)
    if not user:
        raise ValueError("Authentication required - Valid access token must be provided")
    
    user_email = user.email
    logger.info(f"🔍 Getting role for authenticated user {user_email}")
    
    # Get user role and permissions using the admin role manager
    user_role = admin_role_manager.get_user_role(user_email)
    user_permissions = admin_role_manager.get_user_permissions(user_email)
    
    logger.info(f"🔐 User {user_email} has role {user_role} with permissions: {user_permissions}")
    
    return HttpResponse(
        json.dumps({
            "role": str(user_role),
            "permissions": {
                "can_use_spiritual_guidance": user_permissions.can_use_spiritual_guidance,
                "can_view_own_usage": user_permissions.can_view_own_usage,
                "can_view_cost_dashboard": user_permissions.can_view_cost_dashboard,
                "can_manage_users": user_permissions.can_manage_users,
                "can_block_users": user_permissions.can_block_users,
                "can_view_system_costs": user_permissions.can_view_system_costs,
                "can_configure_budgets": user_permissions.can_configure_budgets,
                "can_access_admin_endpoints": user_permissions.can_access_admin_endpoints,
                "can_override_budget_limits": user_permissions.can_override_budget_limits,
                "can_manage_emergency_controls": user_permissions.can_manage_emergency_controls
            },
            "email": user_email,
            "timestamp": datetime.utcnow().isoformat()
        }),
        mimetype="application/json",
        status_code=200,
        headers={"Access-Control-Allow-Origin": "*"}
    )
