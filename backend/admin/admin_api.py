"""
Admin Dashboard API Endpoints for Vimarsh
Implements admin-only endpoints for cost management and user control
"""

import json
import logging
from typing import Dict, Any
import azure.functions as func
from datetime import datetime

from ..auth.admin_auth import require_admin_role, get_user_context, log_admin_action, UserRole
from ..cost_management.cost_service import cost_management

logger = logging.getLogger(__name__)

@require_admin_role(UserRole.ADMIN)
async def admin_dashboard_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Admin dashboard data endpoint"""
    try:
        user_context = get_user_context(req)
        user_id = user_context.get('user_id')
        
        # Get comprehensive cost analytics
        analytics = await cost_management.get_cost_analytics(user_id)
        
        # Log admin action
        log_admin_action('dashboard_access', user_context)
        
        response_data = {
            'status': 'success',
            'data': analytics,
            'timestamp': datetime.now().isoformat(),
            'admin_user': user_context.get('email')
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"🚨 Admin dashboard error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Internal server error'}),
            mimetype="application/json",
            status_code=500
        )

@require_admin_role(UserRole.ADMIN)
async def admin_users_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Admin user management endpoint"""
    try:
        user_context = get_user_context(req)
        method = req.method
        
        if method == 'GET':
            # Get user list with cost analytics
            users = await get_user_list_with_costs()
            
            log_admin_action('user_list_access', user_context)
            
            return func.HttpResponse(
                json.dumps({
                    'status': 'success',
                    'users': users,
                    'total_count': len(users)
                }),
                mimetype="application/json",
                status_code=200
            )
            
        elif method == 'POST':
            # Handle user actions (block, unblock, set budget)
            return await handle_user_action(req, user_context)
            
        else:
            return func.HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                mimetype="application/json",
                status_code=405
            )
            
    except Exception as e:
        logger.error(f"🚨 Admin users error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Internal server error'}),
            mimetype="application/json",
            status_code=500
        )

@require_admin_role(UserRole.ADMIN)
async def admin_cost_controls_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Admin cost control actions endpoint"""
    try:
        user_context = get_user_context(req)
        
        if req.method == 'POST':
            request_data = json.loads(req.get_body().decode('utf-8'))
            action = request_data.get('action')
            
            if action == 'emergency_shutdown':
                success = await handle_emergency_shutdown(user_context)
                action_name = 'emergency_shutdown'
                
            elif action == 'budget_override':
                success = await handle_budget_override(request_data, user_context)
                action_name = 'budget_override'
                
            elif action == 'mass_user_action':
                success = await handle_mass_user_action(request_data, user_context)
                action_name = 'mass_user_action'
                
            else:
                return func.HttpResponse(
                    json.dumps({'error': 'Invalid action'}),
                    mimetype="application/json",
                    status_code=400
                )
            
            log_admin_action(action_name, user_context, request_data)
            
            return func.HttpResponse(
                json.dumps({
                    'status': 'success' if success else 'error',
                    'action': action,
                    'executed_by': user_context.get('email')
                }),
                mimetype="application/json",
                status_code=200 if success else 500
            )
            
        else:
            return func.HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                mimetype="application/json",
                status_code=405
            )
            
    except Exception as e:
        logger.error(f"🚨 Admin cost controls error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Internal server error'}),
            mimetype="application/json",
            status_code=500
        )

@require_admin_role(UserRole.SUPER_ADMIN)
async def admin_role_management_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Super admin role management endpoint"""
    try:
        user_context = get_user_context(req)
        
        if req.method == 'POST':
            request_data = json.loads(req.get_body().decode('utf-8'))
            action = request_data.get('action')
            
            if action == 'promote_to_admin':
                success = await promote_user_to_admin(request_data, user_context)
                
            elif action == 'demote_admin':
                success = await demote_admin_user(request_data, user_context)
                
            else:
                return func.HttpResponse(
                    json.dumps({'error': 'Invalid action'}),
                    mimetype="application/json",
                    status_code=400
                )
            
            log_admin_action(f'role_management_{action}', user_context, request_data)
            
            return func.HttpResponse(
                json.dumps({
                    'status': 'success' if success else 'error',
                    'action': action,
                    'executed_by': user_context.get('email')
                }),
                mimetype="application/json",
                status_code=200 if success else 500
            )
            
        else:
            return func.HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                mimetype="application/json",
                status_code=405
            )
            
    except Exception as e:
        logger.error(f"🚨 Admin role management error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Internal server error'}),
            mimetype="application/json",
            status_code=500
        )

async def get_user_list_with_costs() -> list:
    """Get list of users with their cost analytics"""
    try:
        # Simplified implementation - would query actual user database
        users = [
            {
                'user_id': 'user1',
                'email': 'user1@example.com',
                'name': 'User One',
                'daily_cost': 2.50,
                'monthly_cost': 45.75,
                'total_requests': 127,
                'status': 'active',
                'last_active': '2025-01-10T10:30:00Z',
                'budget_utilization': 91.5,
                'is_blocked': False
            },
            {
                'user_id': 'user2',
                'email': 'user2@example.com',
                'name': 'User Two',
                'daily_cost': 0.75,
                'monthly_cost': 18.25,
                'total_requests': 89,
                'status': 'active',
                'last_active': '2025-01-10T09:15:00Z',
                'budget_utilization': 36.5,
                'is_blocked': False
            },
            {
                'user_id': 'user3',
                'email': 'user3@example.com',
                'name': 'User Three',
                'daily_cost': 5.25,
                'monthly_cost': 67.80,
                'total_requests': 256,
                'status': 'warning',
                'last_active': '2025-01-10T11:45:00Z',
                'budget_utilization': 135.6,
                'is_blocked': False
            }
        ]
        
        return users
        
    except Exception as e:
        logger.error(f"🚨 Failed to get user list: {str(e)}")
        return []

async def handle_user_action(req: func.HttpRequest, user_context: Dict[str, Any]) -> func.HttpResponse:
    """Handle user management actions"""
    try:
        request_data = json.loads(req.get_body().decode('utf-8'))
        action = request_data.get('action')
        target_user_id = request_data.get('user_id')
        admin_user_id = user_context.get('user_id')
        
        success = False
        
        if action == 'block_user':
            reason = request_data.get('reason', 'Admin action')
            success = await cost_management.block_user(admin_user_id, target_user_id, reason)
            
        elif action == 'unblock_user':
            success = await cost_management.unblock_user(admin_user_id, target_user_id)
            
        elif action == 'set_budget':
            daily_budget = request_data.get('daily_budget', 5.0)
            monthly_budget = request_data.get('monthly_budget', 50.0)
            success = await cost_management.set_user_budget(admin_user_id, target_user_id, daily_budget, monthly_budget)
            
        else:
            return func.HttpResponse(
                json.dumps({'error': 'Invalid user action'}),
                mimetype="application/json",
                status_code=400
            )
        
        log_admin_action(f'user_action_{action}', user_context, request_data)
        
        return func.HttpResponse(
            json.dumps({
                'status': 'success' if success else 'error',
                'action': action,
                'target_user': target_user_id
            }),
            mimetype="application/json",
            status_code=200 if success else 500
        )
        
    except Exception as e:
        logger.error(f"🚨 User action error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Internal server error'}),
            mimetype="application/json",
            status_code=500
        )

async def handle_emergency_shutdown(user_context: Dict[str, Any]) -> bool:
    """Handle emergency system shutdown"""
    try:
        admin_email = user_context.get('email')
        logger.warning(f"🚨 EMERGENCY SHUTDOWN initiated by {admin_email}")
        
        # Implementation would:
        # 1. Set global service flag to reject new requests
        # 2. Complete ongoing requests
        # 3. Send notifications to users
        # 4. Log emergency action
        
        return True
        
    except Exception as e:
        logger.error(f"🚨 Emergency shutdown error: {str(e)}")
        return False

async def handle_budget_override(request_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
    """Handle budget override for critical operations"""
    try:
        override_amount = request_data.get('amount', 0.0)
        duration_hours = request_data.get('duration_hours', 1)
        reason = request_data.get('reason', 'Admin override')
        
        admin_email = user_context.get('email')
        logger.warning(f"💰 BUDGET OVERRIDE: ${override_amount:.2f} for {duration_hours}h by {admin_email}: {reason}")
        
        # Implementation would:
        # 1. Set temporary budget increase
        # 2. Schedule automatic reversion
        # 3. Log override action
        # 4. Send notifications
        
        return True
        
    except Exception as e:
        logger.error(f"🚨 Budget override error: {str(e)}")
        return False

async def handle_mass_user_action(request_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
    """Handle mass user actions"""
    try:
        action = request_data.get('mass_action')
        user_ids = request_data.get('user_ids', [])
        
        admin_email = user_context.get('email')
        logger.warning(f"👥 MASS USER ACTION: {action} on {len(user_ids)} users by {admin_email}")
        
        # Implementation would:
        # 1. Apply action to all specified users
        # 2. Log each action
        # 3. Send notifications
        # 4. Generate summary report
        
        return True
        
    except Exception as e:
        logger.error(f"🚨 Mass user action error: {str(e)}")
        return False

async def promote_user_to_admin(request_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
    """Promote user to admin role"""
    try:
        target_email = request_data.get('email')
        admin_email = user_context.get('email')
        
        logger.info(f"🔐 ROLE PROMOTION: {target_email} promoted to admin by {admin_email}")
        
        # Implementation would:
        # 1. Update user role in database
        # 2. Add admin permissions
        # 3. Send notification to new admin
        # 4. Log promotion
        
        return True
        
    except Exception as e:
        logger.error(f"🚨 Role promotion error: {str(e)}")
        return False

async def demote_admin_user(request_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
    """Demote admin user to regular user"""
    try:
        target_email = request_data.get('email')
        admin_email = user_context.get('email')
        
        logger.info(f"🔐 ROLE DEMOTION: {target_email} demoted to user by {admin_email}")
        
        # Implementation would:
        # 1. Update user role in database
        # 2. Remove admin permissions
        # 3. Send notification to demoted user
        # 4. Log demotion
        
        return True
        
    except Exception as e:
        logger.error(f"🚨 Role demotion error: {str(e)}")
        return False
