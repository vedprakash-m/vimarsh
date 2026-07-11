"""
Notification Service
Core service for managing push notification subscriptions and sending notifications
Integrated with PreferencesService for user notification preferences
"""

import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


@dataclass
class NotificationSubscription:
    """Push notification subscription data"""
    user_id: str
    endpoint: str
    keys: Dict[str, str]  # p256dh and auth keys
    created_at: str
    updated_at: str
    is_active: bool = True
    user_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationSubscription':
        """Create from dictionary"""
        return cls(
            user_id=data.get('user_id', ''),
            endpoint=data.get('endpoint', ''),
            keys=data.get('keys', {}),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            is_active=data.get('is_active', True),
            user_agent=data.get('user_agent')
        )


@dataclass
class NotificationPreferences:
    """User notification preferences"""
    user_id: str
    enabled: bool = True
    daily_wisdom_enabled: bool = True
    streak_reminders_enabled: bool = True
    achievement_notifications_enabled: bool = True
    weekly_summary_enabled: bool = True
    
    # Time preferences (in user's timezone)
    preferred_time_hour: int = 9  # 9 AM
    preferred_time_minute: int = 0
    timezone: str = "UTC"
    
    # Frequency controls
    max_notifications_per_day: int = 3
    quiet_hours_start: int = 22  # 10 PM
    quiet_hours_end: int = 7  # 7 AM
    
    # Last notification tracking
    last_daily_wisdom_at: Optional[str] = None
    last_streak_reminder_at: Optional[str] = None
    notifications_sent_today: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationPreferences':
        """Create from dictionary"""
        return cls(
            user_id=data.get('user_id', ''),
            enabled=data.get('enabled', True),
            daily_wisdom_enabled=data.get('daily_wisdom_enabled', True),
            streak_reminders_enabled=data.get('streak_reminders_enabled', True),
            achievement_notifications_enabled=data.get('achievement_notifications_enabled', True),
            weekly_summary_enabled=data.get('weekly_summary_enabled', True),
            preferred_time_hour=data.get('preferred_time_hour', 9),
            preferred_time_minute=data.get('preferred_time_minute', 0),
            timezone=data.get('timezone', 'UTC'),
            max_notifications_per_day=data.get('max_notifications_per_day', 3),
            quiet_hours_start=data.get('quiet_hours_start', 22),
            quiet_hours_end=data.get('quiet_hours_end', 7),
            last_daily_wisdom_at=data.get('last_daily_wisdom_at'),
            last_streak_reminder_at=data.get('last_streak_reminder_at'),
            notifications_sent_today=data.get('notifications_sent_today', 0)
        )


class NotificationService:
    """
    Service for managing push notifications
    
    Features:
    - Push subscription management
    - User preference handling (integrated with PreferencesService)
    - Notification scheduling and sending
    - Rate limiting and quiet hours
    """
    
    def __init__(self, cosmos_client: Optional[Any] = None, preferences_service: Optional[Any] = None):
        """
        Initialize the notification service
        
        Args:
            cosmos_client: Optional Cosmos DB client for persistence
            preferences_service: Optional PreferencesService for user preferences
        """
        self.cosmos_client = cosmos_client
        self._subscriptions_container = None
        self._preferences_container = None  # Legacy, kept for backward compatibility
        self.preferences_service = preferences_service
        
        # VAPID keys would be loaded from environment
        self.vapid_private_key: Optional[str] = None
        self.vapid_public_key: Optional[str] = None
        self.vapid_claims: Dict[str, str] = {
            "sub": "mailto:support@vimarsh.vedmishra.com"
        }
    
    async def initialize(self) -> None:
        """Initialize Cosmos DB containers"""
        if self.cosmos_client:
            try:
                database_name = os.environ.get("AZURE_COSMOS_DATABASE_NAME", "vimarsh-multi-personality")
                database = self.cosmos_client.get_database_client(database_name)
                self._subscriptions_container = database.get_container_client(
                    "notification_subscriptions"
                )
                self._preferences_container = database.get_container_client(
                    "notification_preferences"
                )
                logger.info("✅ NotificationService initialized with Cosmos DB")
            except Exception as e:
                logger.warning(f"⚠️ Cosmos DB initialization failed: {e}")
    
    # =========================================================================
    # SUBSCRIPTION MANAGEMENT
    # =========================================================================
    
    async def subscribe(
        self,
        user_id: str,
        subscription_data: Dict[str, Any],
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a push notification subscription
        
        Args:
            user_id: User identifier
            subscription_data: Web Push subscription object from browser
            user_agent: Browser user agent string
            
        Returns:
            Subscription confirmation
        """
        now = datetime.now(timezone.utc).isoformat()
        
        subscription = NotificationSubscription(
            user_id=user_id,
            endpoint=subscription_data.get('endpoint', ''),
            keys={
                'p256dh': subscription_data.get('keys', {}).get('p256dh', ''),
                'auth': subscription_data.get('keys', {}).get('auth', '')
            },
            created_at=now,
            updated_at=now,
            is_active=True,
            user_agent=user_agent
        )
        
        # Generate subscription ID from endpoint hash
        subscription_id = self._generate_subscription_id(subscription.endpoint)
        
        if self._subscriptions_container:
            try:
                doc = {
                    'id': subscription_id,
                    'user_id': user_id,
                    **subscription.to_dict()
                }
                await self._subscriptions_container.upsert_item(doc)
                logger.info(f"✅ Push subscription saved for user {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save subscription: {e}")
                raise
        
        # Ensure default preferences exist
        await self._ensure_preferences_exist(user_id)
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "message": "Push notifications enabled"
        }
    
    async def unsubscribe(
        self,
        user_id: str,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unsubscribe from push notifications
        
        Args:
            user_id: User identifier
            endpoint: Specific endpoint to unsubscribe (optional, unsubscribes all if not provided)
            
        Returns:
            Unsubscription confirmation
        """
        if self._subscriptions_container:
            try:
                if endpoint:
                    subscription_id = self._generate_subscription_id(endpoint)
                    await self._subscriptions_container.delete_item(
                        item=subscription_id,
                        partition_key=user_id
                    )
                else:
                    # Delete all subscriptions for user
                    query = "SELECT * FROM c WHERE c.user_id = @user_id"
                    params = [{"name": "@user_id", "value": user_id}]
                    items = self._subscriptions_container.query_items(
                        query=query,
                        parameters=params
                    )
                    async for item in items:
                        await self._subscriptions_container.delete_item(
                            item=item['id'],
                            partition_key=user_id
                        )
                
                logger.info(f"✅ Unsubscribed user {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to unsubscribe: {e}")
        
        return {
            "success": True,
            "message": "Push notifications disabled"
        }
    
    async def get_user_subscriptions(
        self, 
        user_id: str
    ) -> List[NotificationSubscription]:
        """Get all active subscriptions for a user"""
        subscriptions = []
        
        if self._subscriptions_container:
            try:
                query = """
                    SELECT * FROM c 
                    WHERE c.user_id = @user_id AND c.is_active = true
                """
                params = [{"name": "@user_id", "value": user_id}]
                items = self._subscriptions_container.query_items(
                    query=query,
                    parameters=params
                )
                async for item in items:
                    subscriptions.append(NotificationSubscription.from_dict(item))
            except Exception as e:
                logger.error(f"❌ Failed to get subscriptions: {e}")
        
        return subscriptions
    
    # =========================================================================
    # PREFERENCE MANAGEMENT
    # =========================================================================
    
    async def get_preferences(self, user_id: str) -> NotificationPreferences:
        """
        Get notification preferences for a user
        Fetches from PreferencesService if available, falls back to legacy storage
        """
        if self.preferences_service:
            try:
                # Get preferences from PreferencesService
                user_prefs = self.preferences_service.get_preferences(user_id)
                notif_prefs = user_prefs.get('notification_preferences', {})
                
                # Convert to NotificationPreferences format
                return self._convert_to_notification_preferences(user_id, notif_prefs)
            except Exception as e:
                logger.warning(f"⚠️ Failed to get preferences from PreferencesService: {e}")
        
        # Fall back to legacy container
        if self._preferences_container:
            try:
                doc = await self._preferences_container.read_item(
                    item=user_id,
                    partition_key=user_id
                )
                return NotificationPreferences.from_dict(doc)
            except Exception:
                pass
        
        # Return defaults
        return NotificationPreferences(user_id=user_id)
    
    async def update_preferences(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> NotificationPreferences:
        """
        Update notification preferences
        
        Args:
            user_id: User identifier
            updates: Dictionary of preference updates
            
        Returns:
            Updated preferences
        """
        prefs = await self.get_preferences(user_id)
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        
        if self._preferences_container:
            try:
                doc = {
                    'id': user_id,
                    'user_id': user_id,
                    **prefs.to_dict()
                }
                await self._preferences_container.upsert_item(doc)
                logger.info(f"✅ Preferences updated for user {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to update preferences: {e}")
        
        return prefs
    
    async def _ensure_preferences_exist(self, user_id: str) -> None:
        """Ensure default preferences exist for a user"""
        if self._preferences_container:
            try:
                await self._preferences_container.read_item(
                    item=user_id,
                    partition_key=user_id
                )
            except Exception:
                # Create defaults
                prefs = NotificationPreferences(user_id=user_id)
                doc = {
                    'id': user_id,
                    'user_id': user_id,
                    **prefs.to_dict()
                }
                await self._preferences_container.upsert_item(doc)
    
    # =========================================================================
    # NOTIFICATION SENDING
    # =========================================================================
    
    async def send_notification(
        self,
        user_id: str,
        notification_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a push notification to a user
        
        Args:
            user_id: User identifier
            notification_payload: Notification data (title, body, icon, etc.)
            
        Returns:
            Send result with success/failure info
        """
        subscriptions = await self.get_user_subscriptions(user_id)
        
        if not subscriptions:
            return {
                "success": False,
                "error": "No active subscriptions",
                "sent": 0
            }
        
        # Check preferences
        prefs = await self.get_preferences(user_id)
        if not prefs.enabled:
            return {
                "success": False,
                "error": "Notifications disabled by user",
                "sent": 0
            }
        
        # Check quiet hours
        if self._is_quiet_hours(prefs):
            return {
                "success": False,
                "error": "Quiet hours active",
                "sent": 0
            }
        
        # Check rate limit
        if prefs.notifications_sent_today >= prefs.max_notifications_per_day:
            return {
                "success": False,
                "error": "Daily notification limit reached",
                "sent": 0
            }
        
        sent_count = 0
        failed_endpoints = []
        
        for subscription in subscriptions:
            try:
                # In production, this would use pywebpush
                # await self._send_webpush(subscription, notification_payload)
                sent_count += 1
                logger.info(f"📤 Notification sent to {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send to endpoint: {e}")
                failed_endpoints.append(subscription.endpoint)
        
        # Update sent count
        prefs.notifications_sent_today += 1
        await self.update_preferences(user_id, {
            'notifications_sent_today': prefs.notifications_sent_today
        })
        
        return {
            "success": sent_count > 0,
            "sent": sent_count,
            "failed": len(failed_endpoints)
        }
    
    async def send_to_users_in_window(
        self,
        notification_type: str,
        content_generator: Any
    ) -> Dict[str, Any]:
        """
        Send notifications to all users whose preferred time matches current time
        
        This is called by the timer trigger function
        
        Args:
            notification_type: Type of notification to send
            content_generator: ContentService for generating content
            
        Returns:
            Summary of send operation
        """
        # This would query users whose preferred notification time is now
        # and send appropriate notifications to them
        
        # Placeholder implementation
        return {
            "processed": 0,
            "sent": 0,
            "errors": 0
        }
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _generate_subscription_id(self, endpoint: str) -> str:
        """Generate a unique ID from the subscription endpoint"""
        return hashlib.sha256(endpoint.encode()).hexdigest()[:32]
    
    def _is_quiet_hours(self, prefs: NotificationPreferences) -> bool:
        """Check if current time is within quiet hours in user's timezone"""
        try:
            # Get current time in user's timezone
            user_tz = ZoneInfo(prefs.timezone)
            now = datetime.now(user_tz)
            current_time = now.time()
            
            # Parse quiet hours times (format: "HH:MM")
            if hasattr(prefs, 'quiet_hours_start') and hasattr(prefs, 'quiet_hours_end'):
                # Legacy format: integer hours
                start_hour = prefs.quiet_hours_start
                end_hour = prefs.quiet_hours_end
                current_hour = now.hour
                
                if start_hour < end_hour:
                    return start_hour <= current_hour < end_hour
                else:
                    # Quiet hours span midnight
                    return current_hour >= start_hour or current_hour < end_hour
            else:
                # New format from PreferencesService: "HH:MM" strings
                # This will be implemented when preferences are properly integrated
                return False
        except Exception as e:
            logger.warning(f"⚠️ Error checking quiet hours: {e}")
            return False
    
    def _should_send_notification(
        self,
        prefs: NotificationPreferences,
        notification_type: str
    ) -> bool:
        """Check if a notification should be sent based on preferences"""
        if not prefs.enabled:
            return False
        
        # Check specific notification type settings
        type_checks = {
            'daily_wisdom': prefs.daily_wisdom_enabled,
            'streak_reminder': prefs.streak_reminders_enabled,
            'streak_reminders': prefs.streak_reminders_enabled,  # Alternative key
            'achievement': prefs.achievement_notifications_enabled,
            'achievements': prefs.achievement_notifications_enabled,  # Alternative key
            'weekly_summary': prefs.weekly_summary_enabled,
        }
        
        return type_checks.get(notification_type, True)
    
    def _convert_to_notification_preferences(
        self,
        user_id: str,
        notif_prefs: Dict[str, Any]
    ) -> NotificationPreferences:
        """
        Convert notification_preferences from PreferencesService to NotificationPreferences
        
        Args:
            user_id: User identifier
            notif_prefs: notification_preferences dict from PreferencesService
            
        Returns:
            NotificationPreferences object
        """
        # Parse preferred_time (format: "HH:MM")
        preferred_time = notif_prefs.get('preferred_time', '09:00')
        hour, minute = 9, 0
        try:
            hour, minute = map(int, preferred_time.split(':'))
        except Exception:
            pass
        
        # Parse quiet hours times
        quiet_start = notif_prefs.get('quiet_start', '22:00')
        quiet_end = notif_prefs.get('quiet_end', '07:00')
        quiet_start_hour, quiet_end_hour = 22, 7
        try:
            quiet_start_hour = int(quiet_start.split(':')[0])
            quiet_end_hour = int(quiet_end.split(':')[0])
        except Exception:
            pass
        
        # Get notification types
        types = notif_prefs.get('types', {})
        
        return NotificationPreferences(
            user_id=user_id,
            enabled=notif_prefs.get('daily_wisdom_enabled', True),
            daily_wisdom_enabled=types.get('daily_wisdom', True),
            streak_reminders_enabled=types.get('streak_reminders', True),
            achievement_notifications_enabled=types.get('achievements', True),
            weekly_summary_enabled=types.get('weekly_summary', True),
            preferred_time_hour=hour,
            preferred_time_minute=minute,
            timezone=notif_prefs.get('timezone', 'UTC'),
            quiet_hours_start=quiet_start_hour,
            quiet_hours_end=quiet_end_hour
        )
