"""
Notification API Endpoints
REST API for push notification management
"""

import logging
import azure.functions as func
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def register_notification_routes(app: func.FunctionApp) -> None:
    """
    Register all notification-related routes
    
    Endpoints:
    - POST /api/notifications/subscribe - Subscribe to push notifications
    - DELETE /api/notifications/unsubscribe - Unsubscribe from push notifications
    - GET /api/notifications/preferences - Get notification preferences
    - PUT /api/notifications/preferences - Update notification preferences
    - GET /api/notifications/status - Get subscription status
    - POST /api/notifications/test - Send a test notification (dev only)
    """
    
    # =========================================================================
    # POST /api/notifications/subscribe
    # =========================================================================
    @app.route(
        route="notifications/subscribe",
        methods=["POST"],
        auth_level=func.AuthLevel.ANONYMOUS
    )
    async def subscribe_to_notifications(req: func.HttpRequest) -> func.HttpResponse:
        """
        Subscribe to push notifications
        
        Request body:
        {
            "subscription": {
                "endpoint": "https://...",
                "keys": {
                    "p256dh": "...",
                    "auth": "..."
                }
            }
        }
        """
        try:
            # Get user ID from auth header
            user_id = _get_user_id(req)
            if not user_id:
                return func.HttpResponse(
                    '{"error": "Authentication required"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            # Parse request body
            try:
                body = req.get_json()
            except Exception:
                return func.HttpResponse(
                    '{"error": "Invalid JSON body"}',
                    status_code=400,
                    mimetype="application/json"
                )
            
            subscription_data = body.get('subscription', {})
            if not subscription_data.get('endpoint'):
                return func.HttpResponse(
                    '{"error": "Missing subscription endpoint"}',
                    status_code=400,
                    mimetype="application/json"
                )
            
            # Get user agent for device tracking
            user_agent = req.headers.get('User-Agent')
            
            # Import services here to avoid circular imports
            from .notification_service import NotificationService
            from services.preferences_service import PreferencesService
            
            preferences_service = PreferencesService()
            service = NotificationService(preferences_service=preferences_service)
            
            result = await service.subscribe(
                user_id=user_id,
                subscription_data=subscription_data,
                user_agent=user_agent
            )
            
            import json
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"❌ Subscribe error: {e}")
            return func.HttpResponse(
                f'{{"error": "Failed to subscribe: {str(e)}"}}',
                status_code=500,
                mimetype="application/json"
            )
    
    # =========================================================================
    # DELETE /api/notifications/unsubscribe
    # =========================================================================
    @app.route(
        route="notifications/unsubscribe",
        methods=["DELETE", "POST"],
        auth_level=func.AuthLevel.ANONYMOUS
    )
    async def unsubscribe_from_notifications(req: func.HttpRequest) -> func.HttpResponse:
        """
        Unsubscribe from push notifications
        
        Optional body:
        {
            "endpoint": "https://..." // Optional, unsubscribes specific endpoint
        }
        """
        try:
            user_id = _get_user_id(req)
            if not user_id:
                return func.HttpResponse(
                    '{"error": "Authentication required"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            # Optional endpoint in body
            endpoint = None
            try:
                body = req.get_json()
                endpoint = body.get('endpoint')
            except Exception:
                pass
            
            from .notification_service import NotificationService
            from services.preferences_service import PreferencesService
            
            preferences_service = PreferencesService()
            service = NotificationService(preferences_service=preferences_service)
            
            result = await service.unsubscribe(
                user_id=user_id,
                endpoint=endpoint
            )
            
            import json
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"❌ Unsubscribe error: {e}")
            return func.HttpResponse(
                f'{{"error": "Failed to unsubscribe: {str(e)}"}}',
                status_code=500,
                mimetype="application/json"
            )
    
    # =========================================================================
    # GET /api/notifications/preferences
    # =========================================================================
    @app.route(
        route="notifications/preferences",
        methods=["GET"],
        auth_level=func.AuthLevel.ANONYMOUS
    )
    async def get_notification_preferences(req: func.HttpRequest) -> func.HttpResponse:
        """
        Get notification preferences for the current user
        """
        try:
            user_id = _get_user_id(req)
            if not user_id:
                return func.HttpResponse(
                    '{"error": "Authentication required"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            from .notification_service import NotificationService
            from services.preferences_service import PreferencesService
            
            preferences_service = PreferencesService()
            service = NotificationService(preferences_service=preferences_service)
            
            prefs = await service.get_preferences(user_id)
            
            import json
            return func.HttpResponse(
                json.dumps(prefs.to_dict()),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"❌ Get preferences error: {e}")
            return func.HttpResponse(
                f'{{"error": "Failed to get preferences: {str(e)}"}}',
                status_code=500,
                mimetype="application/json"
            )
    
    # =========================================================================
    # PUT /api/notifications/preferences
    # =========================================================================
    @app.route(
        route="notifications/preferences",
        methods=["PUT", "PATCH"],
        auth_level=func.AuthLevel.ANONYMOUS
    )
    async def update_notification_preferences(req: func.HttpRequest) -> func.HttpResponse:
        """
        Update notification preferences
        
        Request body:
        {
            "enabled": true,
            "daily_wisdom_enabled": true,
            "streak_reminders_enabled": true,
            "achievement_notifications_enabled": true,
            "weekly_summary_enabled": true,
            "preferred_time_hour": 9,
            "preferred_time_minute": 0,
            "timezone": "America/New_York",
            "quiet_hours_start": 22,
            "quiet_hours_end": 7
        }
        """
        try:
            user_id = _get_user_id(req)
            if not user_id:
                return func.HttpResponse(
                    '{"error": "Authentication required"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            try:
                body = req.get_json()
            except Exception:
                return func.HttpResponse(
                    '{"error": "Invalid JSON body"}',
                    status_code=400,
                    mimetype="application/json"
                )
            
            # Validate allowed fields
            allowed_fields = {
                'enabled', 'daily_wisdom_enabled', 'streak_reminders_enabled',
                'achievement_notifications_enabled', 'weekly_summary_enabled',
                'preferred_time_hour', 'preferred_time_minute', 'timezone',
                'quiet_hours_start', 'quiet_hours_end', 'max_notifications_per_day'
            }
            
            updates = {k: v for k, v in body.items() if k in allowed_fields}
            
            from .notification_service import NotificationService
            from services.preferences_service import PreferencesService
            
            preferences_service = PreferencesService()
            service = NotificationService(preferences_service=preferences_service)
            
            prefs = await service.update_preferences(user_id, updates)
            
            import json
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "preferences": prefs.to_dict()
                }),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"❌ Update preferences error: {e}")
            return func.HttpResponse(
                f'{{"error": "Failed to update preferences: {str(e)}"}}',
                status_code=500,
                mimetype="application/json"
            )
    
    # =========================================================================
    # GET /api/notifications/status
    # =========================================================================
    @app.route(
        route="notifications/status",
        methods=["GET"],
        auth_level=func.AuthLevel.ANONYMOUS
    )
    async def get_notification_status(req: func.HttpRequest) -> func.HttpResponse:
        """
        Get notification status including subscription count and preferences summary
        """
        try:
            user_id = _get_user_id(req)
            if not user_id:
                return func.HttpResponse(
                    '{"error": "Authentication required"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            from .notification_service import NotificationService
            from services.preferences_service import PreferencesService
            
            preferences_service = PreferencesService()
            service = NotificationService(preferences_service=preferences_service)
            
            subscriptions = await service.get_user_subscriptions(user_id)
            prefs = await service.get_preferences(user_id)
            
            import json
            return func.HttpResponse(
                json.dumps({
                    "is_subscribed": len(subscriptions) > 0,
                    "subscription_count": len(subscriptions),
                    "notifications_enabled": prefs.enabled,
                    "daily_wisdom_enabled": prefs.daily_wisdom_enabled,
                    "streak_reminders_enabled": prefs.streak_reminders_enabled,
                    "preferred_time": f"{prefs.preferred_time_hour:02d}:{prefs.preferred_time_minute:02d}",
                    "timezone": prefs.timezone,
                    "notifications_sent_today": prefs.notifications_sent_today
                }),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"❌ Get status error: {e}")
            return func.HttpResponse(
                f'{{"error": "Failed to get status: {str(e)}"}}',
                status_code=500,
                mimetype="application/json"
            )
    
    # =========================================================================
    # POST /api/notifications/test (Development only)
    # =========================================================================
    @app.route(
        route="notifications/test",
        methods=["POST"],
        auth_level=func.AuthLevel.ANONYMOUS
    )
    async def send_test_notification(req: func.HttpRequest) -> func.HttpResponse:
        """
        Send a test notification (for development/testing)
        """
        try:
            user_id = _get_user_id(req)
            if not user_id:
                return func.HttpResponse(
                    '{"error": "Authentication required"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            from .notification_service import NotificationService\n            from .content_service import ContentService\n            from .notification_templates import NotificationType, render_notification\n            from services.preferences_service import PreferencesService\n            \n            preferences_service = PreferencesService()\n            service = NotificationService(preferences_service=preferences_service)\n            content_service = ContentService()            # Generate test content
            content = content_service.get_daily_wisdom_content(user_id)
            notification = render_notification(NotificationType.DAILY_WISDOM, content)
            
            # Send notification
            result = await service.send_notification(user_id, notification)
            
            import json
            return func.HttpResponse(
                json.dumps({
                    "success": result.get("success", False),
                    "message": "Test notification sent" if result.get("success") else "Failed to send",
                    "details": result
                }),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"❌ Test notification error: {e}")
            return func.HttpResponse(
                f'{{"error": "Failed to send test: {str(e)}"}}',
                status_code=500,
                mimetype="application/json"
            )


def _get_user_id(req: func.HttpRequest) -> Optional[str]:
    """
    Extract user ID from request headers or authentication
    
    Checks:
    1. X-User-ID header (for development)
    2. Authorization header (JWT token)
    3. X-MS-CLIENT-PRINCIPAL-ID (Azure Static Web Apps auth)
    """
    # Check for direct user ID header (dev mode)
    user_id = req.headers.get('X-User-ID')
    if user_id:
        return user_id
    
    # Check Azure SWA auth
    principal_id = req.headers.get('X-MS-CLIENT-PRINCIPAL-ID')
    if principal_id:
        return principal_id
    
    # Check for Bearer token and extract user
    auth_header = req.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        # In production, decode JWT and extract user ID
        # For now, return None to indicate auth required
        pass
    
    return None
