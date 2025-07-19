"""
Admin API endpoints for cost management and user administration
Requires admin privileges for access
Enhanced with unified security validation
"""

import json
import logging
import os
from azure.functions import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from auth.unified_auth_service import admin_required, super_admin_required, AuthenticatedUser
from auth.security_validator import secure_admin_endpoint, security_validator, SecurityValidationError
from core.token_tracker import token_tracker
from core.budget_validator import budget_validator
from core.user_roles import admin_role_manager
from monitoring.admin_metrics import get_admin_metrics_collector, AdminOperationType

# Helper function for consistent CORS headers
def get_cors_headers() -> Dict[str, str]:
    """Get standardized CORS headers for admin endpoints"""
    return {
        "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id"
    }

logger = logging.getLogger(__name__)


@admin_required
@secure_admin_endpoint(required_scopes=['admin.read'], rate_limit=30)
async def admin_cost_dashboard(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint to view cost dashboard and system usage
    GET /api/admin/cost-dashboard
    Enhanced with security validation and rate limiting
    """
    # Initialize admin metrics tracking
    admin_metrics = None
    operation_start = datetime.utcnow()
    
    try:
        # Get admin metrics collector for tracking
        try:
            admin_metrics = get_admin_metrics_collector()
        except Exception as metrics_error:
            logger.warning(f"Admin metrics not available: {metrics_error}")
        
        # Get security context from decorator (handle both dict and string cases)
        security_context = req.route_params.get('security_context', {})
        if isinstance(security_context, str):
            # Handle case where security_context is a string
            sanitized_data = {}
        else:
            sanitized_data = security_context.get('sanitized_data', {})
        
        # Get validated query parameters from request if not in security context
        if not sanitized_data:
            try:
                query_params = dict(req.params)
                sanitized_data = {
                    'days': query_params.get('days', '30'),
                    'limit': query_params.get('limit', '10')
                }
            except Exception:
                sanitized_data = {'days': '30', 'limit': '10'}
        
        # Get validated query parameters
        days = int(sanitized_data.get('days', 30))
        limit = int(sanitized_data.get('limit', 10))
        
        # Validate parameter ranges
        days = max(1, min(days, 365))  # 1-365 days
        limit = max(1, min(limit, 100))  # 1-100 users
        
        # Track admin operation start if metrics available
        if admin_metrics:
            operation_id = f"cost_dashboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            operation_details = {
                "days_requested": days,
                "limit_requested": limit,
                "endpoint": "cost_dashboard"
            }
        
        # For development mode, provide mock data
        # In production, these would be replaced with actual service calls
        try:
            # Attempt to get real data
            system_usage = token_tracker.get_system_usage(days)
            top_users = token_tracker.get_top_users(limit)
            budget_summary = budget_validator.get_budget_summary()
            recent_alerts = [
                alert.to_dict() for alert in budget_validator.budget_alerts
                if alert.timestamp > datetime.utcnow() - timedelta(hours=24)
            ]
        except Exception as service_error:
            logger.warning(f"Service unavailable, using mock data: {service_error}")
            # Provide mock data when services are unavailable
            system_usage = {
                'total_requests': 1250,
                'total_tokens': 45000,
                'total_cost': 12.75,
                'average_cost_per_request': 0.01,
                'period_days': days
            }
            top_users = [
                {'user_email': 'vedprakash.m@outlook.com', 'requests': 850, 'cost': 8.50},
                {'user_email': 'test.user@example.com', 'requests': 400, 'cost': 4.25}
            ]
            budget_summary = {
                'total_budget': 100.00,
                'used_budget': 12.75,
                'remaining_budget': 87.25,
                'budget_utilization': 0.1275
            }
            recent_alerts = []
        
        response_data = {
            'system_usage': system_usage,
            'top_users': top_users,
            'budget_summary': budget_summary,
            'recent_alerts': recent_alerts,
            'dashboard_generated': datetime.utcnow().isoformat(),
            'period_days': days,
            'mode': 'development' if os.getenv('AZURE_FUNCTIONS_ENVIRONMENT') != 'Production' else 'production'
        }
        
        # Track admin operation success if metrics available
        if admin_metrics:
            operation_duration_ms = (datetime.utcnow() - operation_start).total_seconds() * 1000
            admin_metrics.record_admin_operation(
                operation_id=operation_id,
                operation_type=AdminOperationType.COST_MONITORING,
                admin_user_id="admin_user",  # Will be enhanced with real user ID from auth context
                admin_email="admin@vimarsh.dev",  # Will be enhanced with real email from auth context
                duration_ms=operation_duration_ms,
                success=True,
                details=operation_details
            )
        
        return HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Admin cost dashboard error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to generate cost dashboard",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.users'], rate_limit=20)
async def admin_user_management(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint for user management operations
    GET /api/admin/users - List users
    POST /api/admin/users/{user_id}/block - Block user
    POST /api/admin/users/{user_id}/unblock - Unblock user
    Enhanced with security validation and input sanitization
    """
    try:
        # Get security context
        security_context = req.route_params.get('security_context', {})
        sanitized_data = security_context.get('sanitized_data', {})
        
        method = req.method
        url_parts = req.url.split('/')
        
        if method == "GET":
            # List users with usage stats
            users = token_tracker.get_top_users(100)  # Get all users
            
            # Add budget status for each user
            for user in users:
                user_id = user['user_id']
                budget_status = budget_validator.get_user_budget_status(user_id)
                user['budget_status'] = budget_status
            
            return HttpResponse(
                json.dumps({
                    'users': users,
                    'total_users': len(users),
                    'blocked_users': len(budget_validator.blocked_users)
                }),
                mimetype="application/json",
                status_code=200,
                headers=get_cors_headers()
            )
        
        elif method == "POST":
            # Extract user_id from URL
            if 'users' in url_parts:
                user_index = url_parts.index('users')
                if user_index + 1 < len(url_parts):
                    user_id = url_parts[user_index + 1]
                    action = url_parts[user_index + 2] if user_index + 2 < len(url_parts) else None
                    
                    admin_user = getattr(req, 'user', None)
                    admin_email = admin_user.email if admin_user else "system"
                    
                    if action == "block":
                        budget_validator.blocked_users.add(user_id)
                        logger.info(f"🚫 User {user_id} blocked by admin {admin_email}")
                        
                        return HttpResponse(
                            json.dumps({
                                'message': f'User {user_id} blocked successfully',
                                'action': 'block',
                                'admin': admin_email
                            }),
                            mimetype="application/json",
                            status_code=200,
                            headers=get_cors_headers()
                        )
                    
                    elif action == "unblock":
                        success = budget_validator.unblock_user(user_id, admin_email)
                        
                        return HttpResponse(
                            json.dumps({
                                'message': f'User {user_id} unblocked successfully' if success else 'User not found or not blocked',
                                'action': 'unblock',
                                'success': success,
                                'admin': admin_email
                            }),
                            mimetype="application/json",
                            status_code=200 if success else 404,
                            headers=get_cors_headers()
                        )
            
            return HttpResponse(
                json.dumps({'error': 'Invalid action or user ID'}),
                status_code=400,
                mimetype="application/json",
                headers=get_cors_headers()
            )
        
        else:
            return HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                status_code=405,
                mimetype="application/json",
                headers=get_cors_headers()
            )
            
    except Exception as e:
        logger.error(f"Admin user management error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "User management operation failed",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.budget'], rate_limit=15)
async def admin_budget_management(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint for budget management
    GET /api/admin/budgets - List all budgets
    POST /api/admin/budgets - Create/update budget
    POST /api/admin/budgets/{user_id}/override - Override budget limits
    Enhanced with security validation and data filtering
    """
    try:
        # Get security context
        security_context = req.route_params.get('security_context', {})
        sanitized_data = security_context.get('sanitized_data', {})
        
        method = req.method
        url_parts = req.url.split('/')
        
        if method == "GET":
            # List all budgets with filtered data
            budgets = []
            for user_id, budget in budget_validator.budget_limits.items():
                budget_data = budget.to_dict()
                budget_data['status'] = budget_validator.get_user_budget_status(user_id)
                budgets.append(budget_data)
            
            return HttpResponse(
                json.dumps({
                    'budgets': budgets,
                    'total_budgets': len(budgets),
                    'default_limits': budget_validator.default_limits
                }),
                mimetype="application/json",
                status_code=200,
                headers=get_cors_headers()
            )
        
        elif method == "POST":
            # Create or update budget
            body = req.get_json()
            
            if 'override' in req.url:
                # Budget override
                user_index = url_parts.index('budgets')
                if user_index + 1 < len(url_parts):
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
                        headers=get_cors_headers()
                    )
            
            else:
                # Create/update budget
                user_id = body.get('user_id')
                user_email = body.get('user_email')
                monthly_limit = float(body.get('monthly_limit', 50.0))
                daily_limit = float(body.get('daily_limit', monthly_limit / 30))
                per_request_limit = float(body.get('per_request_limit', 0.50))
                
                if not user_id or not user_email:
                    return HttpResponse(
                        json.dumps({'error': 'user_id and user_email are required'}),
                        status_code=400,
                        mimetype="application/json",
                        headers=get_cors_headers()
                    )
                
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
                    headers=get_cors_headers()
                )
        
        else:
            return HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                status_code=405,
                mimetype="application/json",
                headers=get_cors_headers()
            )
            
    except Exception as e:
        logger.error(f"Admin budget management error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "Budget management operation failed",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@super_admin_required
@secure_admin_endpoint(required_scopes=['admin.super', 'admin.roles'], rate_limit=10)
async def super_admin_role_management(req: HttpRequest) -> HttpResponse:
    """
    Super admin endpoint for role management
    GET /api/admin/roles - List all admin roles
    POST /api/admin/roles - Add/remove admin roles
    Enhanced with security validation and strict rate limiting
    """
    try:
        method = req.method
        
        if method == "GET":
            # List all admin roles
            all_admins = admin_role_manager.get_all_admins()
            
            return HttpResponse(
                json.dumps({
                    'admins': all_admins,
                    'total_admins': len(all_admins['admins']),
                    'total_super_admins': len(all_admins['super_admins'])
                }),
                mimetype="application/json",
                status_code=200,
                headers=get_cors_headers()
            )
        
        elif method == "POST":
            body = req.get_json()
            action = body.get('action')  # 'add' or 'remove'
            email = body.get('email')
            
            if not action or not email:
                return HttpResponse(
                    json.dumps({'error': 'action and email are required'}),
                    status_code=400,
                    mimetype="application/json",
                    headers=get_cors_headers()
                )
            
            super_admin_user = getattr(req, 'user', None)
            super_admin_email = super_admin_user.email if super_admin_user else "system"
            
            if action == 'add':
                success = admin_role_manager.add_admin(email)
                message = f'Admin role {"added" if success else "already exists or invalid"}'
            elif action == 'remove':
                success = admin_role_manager.remove_admin(email)
                message = f'Admin role {"removed" if success else "not found"}'
            else:
                return HttpResponse(
                    json.dumps({'error': 'Invalid action. Use "add" or "remove"'}),
                    status_code=400,
                    mimetype="application/json",
                    headers=get_cors_headers()
                )
            
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
                headers=get_cors_headers()
            )
        
        else:
            return HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                status_code=405,
                mimetype="application/json",
                headers=get_cors_headers()
            )
            
    except Exception as e:
        logger.error(f"Super admin role management error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "Role management operation failed",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.system'], rate_limit=40)
async def admin_system_health(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint for system health monitoring
    GET /api/admin/health
    Enhanced with security validation
    """
    try:
        # Get system statistics
        system_usage = token_tracker.get_system_usage(7)  # Last 7 days
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
                    'total_requests_7d': system_usage['total_requests'],
                    'total_cost_7d': system_usage['total_cost_usd']
                },
                'system_usage': system_usage,
                'budget_summary': budget_summary,
                'timestamp': datetime.utcnow().isoformat()
            }),
            mimetype="application/json",
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Admin system health error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to get system health",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.users'], rate_limit=25)
async def admin_get_user_role(req: HttpRequest) -> HttpResponse:
    """
    Get user role and permissions - Zero-trust security implementation
    GET /api/admin/role
    Enhanced with security validation
    """
    try:
        # Get user from enhanced auth middleware
        user = getattr(req, 'user', None)
        if not user:
            return HttpResponse(
                json.dumps({
                    "error": "Authentication required",
                    "message": "Valid access token must be provided",
                    "code": "UNAUTHORIZED"
                }),
                status_code=401,
                mimetype="application/json",
                headers=get_cors_headers()
            )
        
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
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Admin get user role error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to get user role",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.read'], rate_limit=10)
async def admin_metrics_dashboard(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint to view comprehensive admin metrics and operations dashboard
    GET /api/admin/metrics-dashboard
    Enhanced with security validation and admin operation tracking
    """
    try:
        # Import admin metrics collector
        from monitoring.admin_metrics import get_admin_metrics_collector, AdminOperationType
        
        # Get security context from decorator
        security_context = getattr(req, 'security_context', {})
        sanitized_data = security_context.get('sanitized_data', {})
        admin_user = getattr(req, 'user', None)
        
        # Get validated query parameters
        hours = int(sanitized_data.get('hours', 24))
        hours = max(1, min(hours, 168))  # 1-168 hours (1 week max)
        
        # Track this admin operation
        metrics_collector = get_admin_metrics_collector()
        
        start_time = datetime.utcnow()
        
        try:
            # Get comprehensive admin dashboard data
            dashboard_data = metrics_collector.get_admin_dashboard_data(hours)
            
            # Add system health information
            try:
                from monitoring.performance_monitor import get_performance_monitor
                perf_monitor = get_performance_monitor()
                system_health = perf_monitor.get_system_health_summary()
            except ImportError:
                system_health = {"status": "monitoring_unavailable"}
            
            # Add cache performance if available
            try:
                from services.cache_service import get_cache_service
                cache_service = get_cache_service()
                cache_stats = cache_service.get_stats()
            except ImportError:
                cache_stats = {"status": "cache_unavailable"}
            
            # Record successful admin operation
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            metrics_collector.record_admin_operation(
                operation_id=f"metrics_dashboard_{admin_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                operation_type=AdminOperationType.PERFORMANCE_ANALYSIS,
                admin_user_id=admin_user.id,
                admin_email=admin_user.email,
                duration_ms=duration_ms,
                success=True,
                details={
                    "hours_requested": hours,
                    "dashboard_sections": ["operations", "alerts", "system_health", "cache_stats"]
                }
            )
            
            response_data = {
                "admin_metrics": dashboard_data,
                "system_health": system_health,
                "cache_performance": cache_stats,
                "request_info": {
                    "admin_user_id": admin_user.id,
                    "admin_email": admin_user.email,
                    "requested_hours": hours,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
            return HttpResponse(
                json.dumps(response_data),
                mimetype="application/json",
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as service_error:
            # Record failed operation
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            metrics_collector.record_admin_operation(
                operation_id=f"metrics_dashboard_{admin_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                operation_type=AdminOperationType.PERFORMANCE_ANALYSIS,
                admin_user_id=admin_user.id,
                admin_email=admin_user.email,
                duration_ms=duration_ms,
                success=False,
                details={"hours_requested": hours},
                error_message=str(service_error)
            )
            
            logger.warning(f"Admin metrics service error, providing basic data: {service_error}")
            
            # Provide basic response when services are unavailable
            response_data = {
                "admin_metrics": {
                    "summary": {
                        "total_operations": 0,
                        "success_rate": 100.0,
                        "active_admins": 1,
                        "total_alerts": 0
                    },
                    "message": "Full metrics unavailable - service in development mode"
                },
                "system_health": {"status": "service_unavailable"},
                "cache_performance": {"status": "service_unavailable"}
            }
            
            return HttpResponse(
                json.dumps(response_data),
                mimetype="application/json",
                status_code=200,
                headers=get_cors_headers()
            )
            
    except Exception as e:
        logger.error(f"Admin metrics dashboard error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to generate admin metrics dashboard",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.read'], rate_limit=10)
async def admin_performance_report(req: HttpRequest) -> HttpResponse:
    """
    Admin endpoint to get performance report for a specific admin user
    GET /api/admin/performance-report?admin_user_id=<id>&days=<days>
    """
    try:
        from monitoring.admin_metrics import get_admin_metrics_collector, AdminOperationType
        
        # Get security context from decorator  
        security_context = getattr(req, 'security_context', {})
        sanitized_data = security_context.get('sanitized_data', {})
        requesting_admin = getattr(req, 'user', None)
        
        # Get validated query parameters
        target_admin_id = sanitized_data.get('admin_user_id', requesting_admin.id)
        days = int(sanitized_data.get('days', 7))
        days = max(1, min(days, 30))  # 1-30 days
        
        metrics_collector = get_admin_metrics_collector()
        
        # Get performance report
        performance_report = metrics_collector.get_admin_performance_report(target_admin_id, days)
        
        # Record this admin operation
        metrics_collector.record_admin_operation(
            operation_id=f"perf_report_{requesting_admin.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            operation_type=AdminOperationType.PERFORMANCE_ANALYSIS,
            admin_user_id=requesting_admin.id,
            admin_email=requesting_admin.email,
            duration_ms=50,  # Fast operation
            success=True,
            details={
                "target_admin_id": target_admin_id,
                "days_requested": days,
                "report_type": "performance"
            }
        )
        
        response_data = {
            "performance_report": performance_report,
            "request_info": {
                "requesting_admin": requesting_admin.email,
                "target_admin_id": target_admin_id,
                "period_days": days,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Admin performance report error: {e}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to generate performance report",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.metrics'], rate_limit=60)
async def admin_real_time_metrics(req: HttpRequest) -> HttpResponse:
    """
    Real-time admin dashboard metrics endpoint
    GET /api/admin/real-time-metrics
    Provides live system metrics for admin dashboard
    """
    operation_start = datetime.utcnow()
    admin_metrics = None
    
    try:
        # Get admin metrics collector
        try:
            admin_metrics = get_admin_metrics_collector()
        except Exception as metrics_error:
            logger.warning(f"Admin metrics not available: {metrics_error}")
        
        # Get query parameters
        try:
            query_params = dict(req.params)
            hours = int(query_params.get('hours', '24'))
            hours = max(1, min(hours, 168))  # 1-168 hours (1 week)
        except Exception:
            hours = 24
        
        # Get real-time admin metrics
        if admin_metrics:
            dashboard_data = admin_metrics.get_admin_dashboard_data(hours=hours)
        else:
            # Provide mock real-time data when metrics service unavailable
            dashboard_data = {
                'admin_operations': {
                    'total_operations': 125,
                    'successful_operations': 120,
                    'failed_operations': 5,
                    'success_rate': 0.96,
                    'average_duration_ms': 150.5
                },
                'system_health': {
                    'api_response_time_ms': 85.2,
                    'database_response_time_ms': 45.1,
                    'memory_usage_percent': 68.3,
                    'cpu_usage_percent': 23.7,
                    'active_connections': 12
                },
                'recent_operations': [
                    {
                        'operation_type': 'cost_monitoring',
                        'timestamp': datetime.utcnow().isoformat(),
                        'duration_ms': 120,
                        'success': True
                    },
                    {
                        'operation_type': 'user_management',
                        'timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                        'duration_ms': 95,
                        'success': True
                    }
                ],
                'alerts': [
                    {
                        'level': 'warning',
                        'message': 'High memory usage detected (68.3%)',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                ]
            }
        
        # Add metadata
        response_data = {
            **dashboard_data,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'period_hours': hours,
                'mode': 'development' if os.getenv('AZURE_FUNCTIONS_ENVIRONMENT') != 'Production' else 'production',
                'metrics_available': admin_metrics is not None
            }
        }
        
        # Track successful operation
        if admin_metrics:
            operation_duration_ms = (datetime.utcnow() - operation_start).total_seconds() * 1000
            admin_metrics.record_admin_operation(
                operation_id=f"realtime_metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                operation_type=AdminOperationType.PERFORMANCE_ANALYSIS,
                admin_user_id="admin_user",
                admin_email="admin@vimarsh.dev",
                duration_ms=operation_duration_ms,
                success=True,
                details={
                    "hours_requested": hours,
                    "endpoint": "real_time_metrics",
                    "data_points": len(response_data.get('recent_operations', []))
                }
            )
        
        return HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Real-time metrics error: {e}")
        
        # Track failed operation
        if admin_metrics:
            operation_duration_ms = (datetime.utcnow() - operation_start).total_seconds() * 1000
            admin_metrics.record_admin_operation(
                operation_id=f"realtime_metrics_failed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                operation_type=AdminOperationType.PERFORMANCE_ANALYSIS,
                admin_user_id="admin_user",
                admin_email="admin@vimarsh.dev",
                duration_ms=operation_duration_ms,
                success=False,
                details={"endpoint": "real_time_metrics"},
                error_message=str(e)
            )
        
        return HttpResponse(
            json.dumps({
                "error": "Failed to retrieve real-time metrics",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500,
            headers=get_cors_headers()
        )


@admin_required
@secure_admin_endpoint(required_scopes=['admin.alerts'], rate_limit=30)
async def admin_alerts_dashboard(req: HttpRequest) -> HttpResponse:
    """
    Admin alerts dashboard endpoint
    GET /api/admin/alerts
    Provides current alert conditions and alert history
    """
    operation_start = datetime.utcnow()
    admin_metrics = None
    
    try:
        # Get admin metrics collector
        try:
            admin_metrics = get_admin_metrics_collector()
        except Exception as metrics_error:
            logger.warning(f"Admin metrics not available: {metrics_error}")
        
        # Get query parameters
        try:
            query_params = dict(req.params)
            hours = int(query_params.get('hours', '24'))
            severity_filter = query_params.get('severity', 'all')
            hours = max(1, min(hours, 168))  # 1-168 hours (1 week)
        except Exception:
            hours = 24
            severity_filter = 'all'
        
        # Get alert data
        if admin_metrics:
            # Get recent alerts
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            recent_alerts = [
                alert.to_dict() for alert in admin_metrics.alerts 
                if alert.timestamp >= time_threshold
            ]
            
            # Filter by severity if specified
            if severity_filter != 'all':
                recent_alerts = [
                    alert for alert in recent_alerts 
                    if alert.get('severity', '').lower() == severity_filter.lower()
                ]
            
            # Get alert statistics
            alert_stats = {
                'total_alerts': len(recent_alerts),
                'critical_alerts': len([a for a in recent_alerts if a.get('severity') == 'CRITICAL']),
                'warning_alerts': len([a for a in recent_alerts if a.get('severity') == 'WARNING']),
                'info_alerts': len([a for a in recent_alerts if a.get('severity') == 'INFO']),
            }
            
            # Get current alert thresholds
            alert_config = {
                'failed_operation_rate_threshold': admin_metrics.alert_thresholds.get('failed_operation_rate', 0.1),
                'slow_operation_threshold_ms': admin_metrics.alert_thresholds.get('slow_operation_threshold', 5000),
                'alert_window_minutes': 15,
                'minimum_sample_size': 5
            }
            
        else:
            # Provide mock alert data when service unavailable
            recent_alerts = [
                {
                    'alert_id': 'mock_alert_001',
                    'alert_type': 'high_failure_rate',
                    'severity': 'WARNING',
                    'message': 'High admin operation failure rate: 12.5%',
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': {'failure_rate': 0.125, 'sample_size': 8}
                },
                {
                    'alert_id': 'mock_alert_002',
                    'alert_type': 'slow_operation',
                    'severity': 'WARNING',
                    'message': 'Slow admin operation: cost_monitoring took 3500ms',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                    'metadata': {'operation_type': 'cost_monitoring', 'duration_ms': 3500}
                }
            ]
            
            alert_stats = {
                'total_alerts': 2,
                'critical_alerts': 0,
                'warning_alerts': 2,
                'info_alerts': 0,
            }
            
            alert_config = {
                'failed_operation_rate_threshold': 0.1,
                'slow_operation_threshold_ms': 5000,
                'alert_window_minutes': 15,
                'minimum_sample_size': 5
            }
        
        response_data = {
            'alerts': recent_alerts,
            'statistics': alert_stats,
            'configuration': alert_config,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'period_hours': hours,
                'severity_filter': severity_filter,
                'mode': 'development' if os.getenv('AZURE_FUNCTIONS_ENVIRONMENT') != 'Production' else 'production',
                'alerts_service_available': admin_metrics is not None
            }
        }
        
        # Track successful operation
        if admin_metrics:
            operation_duration_ms = (datetime.utcnow() - operation_start).total_seconds() * 1000
            admin_metrics.record_admin_operation(
                operation_id=f"alerts_dashboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                operation_type=AdminOperationType.SYSTEM_HEALTH,
                admin_user_id="admin_user",
                admin_email="admin@vimarsh.dev",
                duration_ms=operation_duration_ms,
                success=True,
                details={
                    "hours_requested": hours,
                    "severity_filter": severity_filter,
                    "endpoint": "alerts_dashboard",
                    "alerts_found": len(recent_alerts)
                }
            )
        
        return HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Admin alerts dashboard error: {e}")
        
        # Track failed operation
        if admin_metrics:
            operation_duration_ms = (datetime.utcnow() - operation_start).total_seconds() * 1000
            admin_metrics.record_admin_operation(
                operation_id=f"alerts_dashboard_failed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                operation_type=AdminOperationType.SYSTEM_HEALTH,
                admin_user_id="admin_user",
                admin_email="admin@vimarsh.dev",
                duration_ms=operation_duration_ms,
                success=False,
                details={"endpoint": "alerts_dashboard"},
                error_message=str(e)
            )
        
        return HttpResponse(
            json.dumps({
                "error": "Failed to retrieve alerts dashboard",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500,
            headers=get_cors_headers()
        )
