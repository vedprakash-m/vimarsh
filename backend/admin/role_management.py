"""
Admin role management endpoint
"""
import json
import logging
from azure.functions import HttpRequest, HttpResponse
from ..auth.unified_auth_service import admin_required
from ..core.user_roles import admin_role_manager

logger = logging.getLogger(__name__)

@admin_required
async def get_user_role(req: HttpRequest) -> HttpResponse:
    """Get current user's role and permissions"""
    try:
        # Get user from request context (set by admin_required decorator)
        user = getattr(req, 'user', None)
        if not user:
            return HttpResponse(
                json.dumps({"error": "User not found in request context"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logger.info(f"🔐 Role check for user: {user.email}")
        
        response_data = {
            "role": user.role.value,
            "permissions": {
                "can_view_cost_dashboard": user.user_permissions.can_view_cost_dashboard,
                "can_manage_users": user.user_permissions.can_manage_users,
                "can_block_users": user.user_permissions.can_block_users,
                "can_view_system_costs": user.user_permissions.can_view_system_costs,
                "can_configure_budgets": user.user_permissions.can_configure_budgets,
                "can_access_admin_endpoints": user.user_permissions.can_access_admin_endpoints,
                "can_override_budget_limits": user.user_permissions.can_override_budget_limits,
                "can_manage_emergency_controls": user.user_permissions.can_manage_emergency_controls
            },
            "user_info": {
                "email": user.email,
                "name": user.name,
                "is_admin": user.is_admin(),
                "is_super_admin": user.is_super_admin()
            }
        }
        
        logger.info(f"✅ Role response for {user.email}: {user.role.value}")
        
        return HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logger.error(f"❌ Role check failed: {str(e)}")
        return HttpResponse(
            json.dumps({"error": "Failed to get user role", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
