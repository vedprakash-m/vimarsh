"""
Unit Tests for NotificationService Integration with PreferencesService
Tests preference integration, quiet hours, timezone handling, and notification types
"""

import pytest
from datetime import datetime, time, timezone
from unittest.mock import Mock, AsyncMock, patch
from zoneinfo import ZoneInfo

from notifications.notification_service import (
    NotificationService,
    NotificationPreferences,
    NotificationSubscription
)
from services.preferences_service import PreferencesService


class TestNotificationServiceIntegration:
    """Test suite for NotificationService integration with PreferencesService"""
    
    @pytest.fixture
    def mock_cosmos_client(self):
        """Create mock Cosmos DB client"""
        client = Mock()
        database = Mock()
        subscriptions_container = Mock()
        preferences_container = Mock()
        
        client.get_database_client.return_value = database
        database.get_container_client.side_effect = [
            subscriptions_container,
            preferences_container
        ]
        
        return client
    
    @pytest.fixture
    def preferences_service(self):
        """Create PreferencesService instance"""
        return PreferencesService()
    
    @pytest.fixture
    async def service(self, mock_cosmos_client, preferences_service):
        """Create NotificationService instance with mocked dependencies"""
        service = NotificationService(
            cosmos_client=mock_cosmos_client,
            preferences_service=preferences_service
        )
        await service.initialize()
        return service
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing"""
        return "test_user_123"
    
    @pytest.fixture
    def sample_subscription_data(self):
        """Sample push notification subscription data"""
        return {
            "endpoint": "https://fcm.googleapis.com/fcm/send/abc123",
            "keys": {
                "p256dh": "test_p256dh_key",
                "auth": "test_auth_key"
            }
        }


class TestPreferencesIntegration(TestNotificationServiceIntegration):
    """Test PreferencesService integration"""
    
    @pytest.mark.asyncio
    async def test_get_preferences_from_preferences_service(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test getting preferences from PreferencesService"""
        # Setup: Create preferences via PreferencesService
        test_prefs = {
            "notification_preferences": {
                "daily_wisdom_enabled": True,
                "preferred_time": "10:30",
                "timezone": "America/New_York",
                "quiet_hours_enabled": True,
                "quiet_start": "23:00",
                "quiet_end": "08:00",
                "types": {
                    "daily_wisdom": True,
                    "streak_reminders": False,
                    "achievements": True,
                    "weekly_summary": False
                }
            }
        }
        preferences_service.update_preferences(sample_user_id, test_prefs)
        
        # Get preferences through NotificationService
        prefs = await service.get_preferences(sample_user_id)
        
        # Verify conversion
        assert isinstance(prefs, NotificationPreferences)
        assert prefs.user_id == sample_user_id
        assert prefs.preferred_time_hour == 10
        assert prefs.preferred_time_minute == 30
        assert prefs.timezone == "America/New_York"
        assert prefs.quiet_hours_start == 23
        assert prefs.quiet_hours_end == 8
        assert prefs.daily_wisdom_enabled is True
        assert prefs.streak_reminders_enabled is False
        assert prefs.achievement_notifications_enabled is True
        assert prefs.weekly_summary_enabled is False
    
    @pytest.mark.asyncio
    async def test_get_preferences_with_default_values(
        self,
        service,
        sample_user_id
    ):
        """Test getting preferences with default values for new user"""
        prefs = await service.get_preferences(sample_user_id)
        
        # Verify defaults
        assert prefs.user_id == sample_user_id
        assert prefs.enabled is True
        assert prefs.daily_wisdom_enabled is True
        assert prefs.preferred_time_hour == 9
        assert prefs.preferred_time_minute == 0
        assert prefs.timezone == "UTC"
        assert prefs.quiet_hours_start == 22
        assert prefs.quiet_hours_end == 7
    
    @pytest.mark.asyncio
    async def test_preference_conversion_handles_invalid_time_format(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test handling of invalid time format in preferences"""
        # Setup: Create preferences with invalid time format
        test_prefs = {
            "notification_preferences": {
                "preferred_time": "invalid_time",
                "quiet_start": "bad_format",
                "quiet_end": "also_bad"
            }
        }
        preferences_service.update_preferences(sample_user_id, test_prefs)
        
        # Should fall back to defaults
        prefs = await service.get_preferences(sample_user_id)
        
        assert prefs.preferred_time_hour == 9  # Default
        assert prefs.preferred_time_minute == 0  # Default
        assert prefs.quiet_hours_start == 22  # Default
        assert prefs.quiet_hours_end == 7  # Default


class TestQuietHoursHandling(TestNotificationServiceIntegration):
    """Test quiet hours functionality"""
    
    @pytest.mark.asyncio
    async def test_quiet_hours_simple_range(self, service):
        """Test quiet hours within same day (22:00 - 07:00)"""
        prefs = NotificationPreferences(
            user_id="test",
            timezone="UTC",
            quiet_hours_start=22,
            quiet_hours_end=7
        )
        
        # Test times within quiet hours
        with patch('notifications.notification_service.datetime') as mock_datetime:
            # 23:00 UTC - should be quiet
            mock_datetime.now.return_value = datetime(2025, 12, 7, 23, 0, 0, tzinfo=ZoneInfo('UTC'))
            assert service._is_quiet_hours(prefs) is True
            
            # 02:00 UTC - should be quiet
            mock_datetime.now.return_value = datetime(2025, 12, 7, 2, 0, 0, tzinfo=ZoneInfo('UTC'))
            assert service._is_quiet_hours(prefs) is True
            
            # 10:00 UTC - should not be quiet
            mock_datetime.now.return_value = datetime(2025, 12, 7, 10, 0, 0, tzinfo=ZoneInfo('UTC'))
            assert service._is_quiet_hours(prefs) is False
    
    @pytest.mark.asyncio
    async def test_quiet_hours_spanning_midnight(self, service):
        """Test quiet hours that span midnight"""
        prefs = NotificationPreferences(
            user_id="test",
            timezone="America/Los_Angeles",
            quiet_hours_start=22,
            quiet_hours_end=7
        )
        
        with patch('notifications.notification_service.datetime') as mock_datetime:
            # 01:00 PST (after midnight) - should be quiet
            mock_datetime.now.return_value = datetime(
                2025, 12, 7, 1, 0, 0,
                tzinfo=ZoneInfo('America/Los_Angeles')
            )
            assert service._is_quiet_hours(prefs) is True
    
    @pytest.mark.asyncio
    async def test_quiet_hours_different_timezones(self, service):
        """Test quiet hours respect user's timezone"""
        # User in Tokyo with quiet hours 22:00 - 07:00 JST
        prefs = NotificationPreferences(
            user_id="test",
            timezone="Asia/Tokyo",
            quiet_hours_start=22,
            quiet_hours_end=7
        )
        
        with patch('notifications.notification_service.datetime') as mock_datetime:
            # 23:00 JST - should be quiet
            mock_datetime.now.return_value = datetime(
                2025, 12, 7, 23, 0, 0,
                tzinfo=ZoneInfo('Asia/Tokyo')
            )
            assert service._is_quiet_hours(prefs) is True
    
    @pytest.mark.asyncio
    async def test_quiet_hours_edge_cases(self, service):
        """Test quiet hours edge cases"""
        prefs = NotificationPreferences(
            user_id="test",
            timezone="UTC",
            quiet_hours_start=22,
            quiet_hours_end=7
        )
        
        with patch('notifications.notification_service.datetime') as mock_datetime:
            # Exactly at start time - should be quiet
            mock_datetime.now.return_value = datetime(2025, 12, 7, 22, 0, 0, tzinfo=ZoneInfo('UTC'))
            assert service._is_quiet_hours(prefs) is True
            
            # Exactly at end time - should not be quiet
            mock_datetime.now.return_value = datetime(2025, 12, 7, 7, 0, 0, tzinfo=ZoneInfo('UTC'))
            assert service._is_quiet_hours(prefs) is False
    
    @pytest.mark.asyncio
    async def test_quiet_hours_invalid_timezone(self, service):
        """Test handling of invalid timezone"""
        prefs = NotificationPreferences(
            user_id="test",
            timezone="Invalid/Timezone",
            quiet_hours_start=22,
            quiet_hours_end=7
        )
        
        # Should not raise exception, returns False
        result = service._is_quiet_hours(prefs)
        assert result is False


class TestNotificationTypeFiltering(TestNotificationServiceIntegration):
    """Test notification type filtering"""
    
    @pytest.mark.asyncio
    async def test_should_send_notification_all_enabled(self, service):
        """Test notification sending when all types are enabled"""
        prefs = NotificationPreferences(
            user_id="test",
            enabled=True,
            daily_wisdom_enabled=True,
            streak_reminders_enabled=True,
            achievement_notifications_enabled=True,
            weekly_summary_enabled=True
        )
        
        assert service._should_send_notification(prefs, 'daily_wisdom') is True
        assert service._should_send_notification(prefs, 'streak_reminder') is True
        assert service._should_send_notification(prefs, 'achievement') is True
        assert service._should_send_notification(prefs, 'weekly_summary') is True
    
    @pytest.mark.asyncio
    async def test_should_send_notification_selective_disabled(self, service):
        """Test notification sending with some types disabled"""
        prefs = NotificationPreferences(
            user_id="test",
            enabled=True,
            daily_wisdom_enabled=True,
            streak_reminders_enabled=False,
            achievement_notifications_enabled=True,
            weekly_summary_enabled=False
        )
        
        assert service._should_send_notification(prefs, 'daily_wisdom') is True
        assert service._should_send_notification(prefs, 'streak_reminder') is False
        assert service._should_send_notification(prefs, 'streak_reminders') is False  # Alternative key
        assert service._should_send_notification(prefs, 'achievement') is True
        assert service._should_send_notification(prefs, 'achievements') is True  # Alternative key
        assert service._should_send_notification(prefs, 'weekly_summary') is False
    
    @pytest.mark.asyncio
    async def test_should_send_notification_all_disabled(self, service):
        """Test notification sending when notifications are globally disabled"""
        prefs = NotificationPreferences(
            user_id="test",
            enabled=False,
            daily_wisdom_enabled=True,
            streak_reminders_enabled=True
        )
        
        # All types should be blocked when globally disabled
        assert service._should_send_notification(prefs, 'daily_wisdom') is False
        assert service._should_send_notification(prefs, 'streak_reminder') is False
    
    @pytest.mark.asyncio
    async def test_should_send_notification_unknown_type(self, service):
        """Test notification sending with unknown notification type"""
        prefs = NotificationPreferences(
            user_id="test",
            enabled=True
        )
        
        # Unknown types default to True (sent)
        assert service._should_send_notification(prefs, 'unknown_type') is True


class TestSendNotification(TestNotificationServiceIntegration):
    """Test notification sending logic"""
    
    @pytest.mark.asyncio
    async def test_send_notification_respects_quiet_hours(
        self,
        service,
        sample_user_id,
        preferences_service
    ):
        """Test that notifications are blocked during quiet hours"""
        # Setup preferences with quiet hours
        test_prefs = {
            "notification_preferences": {
                "daily_wisdom_enabled": True,
                "quiet_hours_enabled": True,
                "quiet_start": "22:00",
                "quiet_end": "07:00",
                "timezone": "UTC"
            }
        }
        preferences_service.update_preferences(sample_user_id, test_prefs)
        
        # Mock subscriptions
        service.get_user_subscriptions = AsyncMock(return_value=[
            NotificationSubscription(
                user_id=sample_user_id,
                endpoint="https://test.com/push",
                keys={"p256dh": "key1", "auth": "key2"},
                created_at="2025-12-07T00:00:00Z",
                updated_at="2025-12-07T00:00:00Z"
            )
        ])
        
        # Mock time to be in quiet hours
        with patch('notifications.notification_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 12, 7, 23, 0, 0, tzinfo=ZoneInfo('UTC'))
            
            result = await service.send_notification(
                sample_user_id,
                {"title": "Test", "body": "Test notification"}
            )
            
            assert result['success'] is False
            assert result['error'] == "Quiet hours active"
            assert result['sent'] == 0
    
    @pytest.mark.asyncio
    async def test_send_notification_respects_rate_limit(
        self,
        service,
        sample_user_id
    ):
        """Test that notifications respect daily rate limits"""
        # Create preferences with rate limit reached
        prefs = NotificationPreferences(
            user_id=sample_user_id,
            enabled=True,
            max_notifications_per_day=3,
            notifications_sent_today=3
        )
        
        # Mock methods
        service.get_user_subscriptions = AsyncMock(return_value=[
            NotificationSubscription(
                user_id=sample_user_id,
                endpoint="https://test.com/push",
                keys={"p256dh": "key1", "auth": "key2"},
                created_at="2025-12-07T00:00:00Z",
                updated_at="2025-12-07T00:00:00Z"
            )
        ])
        service.get_preferences = AsyncMock(return_value=prefs)
        
        result = await service.send_notification(
            sample_user_id,
            {"title": "Test", "body": "Test notification"}
        )
        
        assert result['success'] is False
        assert result['error'] == "Daily notification limit reached"
        assert result['sent'] == 0
    
    @pytest.mark.asyncio
    async def test_send_notification_no_subscriptions(
        self,
        service,
        sample_user_id
    ):
        """Test sending notification when user has no subscriptions"""
        service.get_user_subscriptions = AsyncMock(return_value=[])
        
        result = await service.send_notification(
            sample_user_id,
            {"title": "Test", "body": "Test notification"}
        )
        
        assert result['success'] is False
        assert result['error'] == "No active subscriptions"
        assert result['sent'] == 0
    
    @pytest.mark.asyncio
    async def test_send_notification_notifications_disabled(
        self,
        service,
        sample_user_id
    ):
        """Test sending notification when notifications are disabled"""
        prefs = NotificationPreferences(
            user_id=sample_user_id,
            enabled=False
        )
        
        service.get_user_subscriptions = AsyncMock(return_value=[
            NotificationSubscription(
                user_id=sample_user_id,
                endpoint="https://test.com/push",
                keys={"p256dh": "key1", "auth": "key2"},
                created_at="2025-12-07T00:00:00Z",
                updated_at="2025-12-07T00:00:00Z"
            )
        ])
        service.get_preferences = AsyncMock(return_value=prefs)
        
        result = await service.send_notification(
            sample_user_id,
            {"title": "Test", "body": "Test notification"}
        )
        
        assert result['success'] is False
        assert result['error'] == "Notifications disabled by user"
        assert result['sent'] == 0


class TestSubscriptionManagement(TestNotificationServiceIntegration):
    """Test subscription management"""
    
    @pytest.mark.asyncio
    async def test_subscribe_creates_subscription(
        self,
        service,
        sample_user_id,
        sample_subscription_data
    ):
        """Test creating a new push subscription"""
        result = await service.subscribe(
            sample_user_id,
            sample_subscription_data,
            user_agent="Mozilla/5.0"
        )
        
        assert result['success'] is True
        assert 'subscription_id' in result
        assert result['message'] == "Push notifications enabled"
    
    @pytest.mark.asyncio
    async def test_subscribe_generates_consistent_id(
        self,
        service,
        sample_user_id,
        sample_subscription_data
    ):
        """Test that same endpoint generates same subscription ID"""
        result1 = await service.subscribe(sample_user_id, sample_subscription_data)
        result2 = await service.subscribe(sample_user_id, sample_subscription_data)
        
        assert result1['subscription_id'] == result2['subscription_id']
    
    @pytest.mark.asyncio
    async def test_unsubscribe_removes_subscription(
        self,
        service,
        sample_user_id,
        sample_subscription_data
    ):
        """Test removing a subscription"""
        # First subscribe
        await service.subscribe(sample_user_id, sample_subscription_data)
        
        # Then unsubscribe
        result = await service.unsubscribe(
            sample_user_id,
            endpoint=sample_subscription_data['endpoint']
        )
        
        assert result['success'] is True
        assert result['message'] == "Push notifications disabled"


class TestConversionHelpers(TestNotificationServiceIntegration):
    """Test preference conversion helpers"""
    
    @pytest.mark.asyncio
    async def test_convert_to_notification_preferences(self, service):
        """Test converting PreferencesService format to NotificationPreferences"""
        notif_prefs = {
            "daily_wisdom_enabled": True,
            "preferred_time": "14:30",
            "timezone": "Europe/London",
            "quiet_hours_enabled": True,
            "quiet_start": "21:00",
            "quiet_end": "06:00",
            "types": {
                "daily_wisdom": False,
                "streak_reminders": True,
                "achievements": False,
                "weekly_summary": True
            }
        }
        
        result = service._convert_to_notification_preferences("test_user", notif_prefs)
        
        assert result.user_id == "test_user"
        assert result.preferred_time_hour == 14
        assert result.preferred_time_minute == 30
        assert result.timezone == "Europe/London"
        assert result.quiet_hours_start == 21
        assert result.quiet_hours_end == 6
        assert result.daily_wisdom_enabled is False
        assert result.streak_reminders_enabled is True
        assert result.achievement_notifications_enabled is False
        assert result.weekly_summary_enabled is True
    
    @pytest.mark.asyncio
    async def test_convert_handles_missing_fields(self, service):
        """Test conversion handles missing optional fields"""
        notif_prefs = {}
        
        result = service._convert_to_notification_preferences("test_user", notif_prefs)
        
        # Should use defaults
        assert result.user_id == "test_user"
        assert result.preferred_time_hour == 9
        assert result.preferred_time_minute == 0
        assert result.timezone == "UTC"
        assert result.daily_wisdom_enabled is True
