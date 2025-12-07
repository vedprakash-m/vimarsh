"""
Unit Tests for PreferencesService
Tests preference management, validation, and deep merge functionality
"""

import pytest
from datetime import datetime
from services.preferences_service import PreferencesService


class TestPreferencesService:
    """Test suite for PreferencesService"""
    
    @pytest.fixture
    def service(self):
        """Create a PreferencesService instance for testing"""
        return PreferencesService()
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing"""
        return "test_user_123"
    
    @pytest.fixture
    def sample_preferences(self):
        """Sample valid preferences"""
        return {
            "experience_preferences": {
                "conversation_style": "balanced",
                "language": "en",
                "formality": "respectful",
                "favorite_personalities": ["krishna", "einstein"],
                "theme": "auto",
                "text_size": "medium",
                "reduce_animations": False
            },
            "notification_preferences": {
                "daily_wisdom_enabled": True,
                "preferred_time": "09:00",
                "timezone": "America/Los_Angeles",
                "quiet_hours_enabled": True,
                "quiet_start": "22:00",
                "quiet_end": "07:00",
                "types": {
                    "daily_wisdom": True,
                    "streak_reminders": True,
                    "achievements": True,
                    "weekly_summary": True
                }
            },
            "memory_preferences": {
                "remember_conversations": True,
                "connect_insights": True,
                "track_emotions": True,
                "suggest_topics": True,
                "privacy_mode": "standard",
                "data_retention_days": 90,
                "analytics_consent": True,
                "research_consent": False
            }
        }
    
    # =========================================================================
    # Test: Get Default Preferences
    # =========================================================================
    
    def test_get_default_preferences(self, service):
        """Test that default preferences are returned correctly"""
        defaults = service.get_default_preferences()
        
        # Check structure
        assert "experience_preferences" in defaults
        assert "notification_preferences" in defaults
        assert "memory_preferences" in defaults
        
        # Check experience defaults
        exp_prefs = defaults["experience_preferences"]
        assert exp_prefs["conversation_style"] == "balanced"
        assert exp_prefs["language"] == "en"
        assert exp_prefs["formality"] == "respectful"
        assert exp_prefs["favorite_personalities"] == []
        assert exp_prefs["theme"] == "auto"
        assert exp_prefs["text_size"] == "medium"
        assert exp_prefs["reduce_animations"] is False
        
        # Check notification defaults
        notif_prefs = defaults["notification_preferences"]
        assert notif_prefs["daily_wisdom_enabled"] is True
        assert notif_prefs["preferred_time"] == "08:00"
        assert notif_prefs["timezone"] == "America/Los_Angeles"
        assert notif_prefs["quiet_hours_enabled"] is False
        
        # Check memory defaults
        mem_prefs = defaults["memory_preferences"]
        assert mem_prefs["remember_conversations"] is True
        assert mem_prefs["privacy_mode"] == "standard"
        assert mem_prefs["data_retention_days"] == 90
        assert mem_prefs["analytics_consent"] is True
    
    # =========================================================================
    # Test: Get Preferences (New User)
    # =========================================================================
    
    def test_get_preferences_new_user(self, service, sample_user_id):
        """Test getting preferences for a new user returns defaults"""
        prefs = service.get_preferences(sample_user_id)
        
        # Should return defaults with user_id and timestamps
        assert prefs["user_id"] == sample_user_id
        assert "created_at" in prefs
        assert "updated_at" in prefs
        assert "experience_preferences" in prefs
        assert "notification_preferences" in prefs
        assert "memory_preferences" in prefs
    
    # =========================================================================
    # Test: Update Preferences
    # =========================================================================
    
    def test_update_preferences_full(self, service, sample_user_id, sample_preferences):
        """Test updating all preferences at once"""
        updated = service.update_preferences(sample_user_id, sample_preferences)
        
        # Check that updates were applied
        assert updated["user_id"] == sample_user_id
        assert updated["experience_preferences"]["conversation_style"] == "balanced"
        assert updated["notification_preferences"]["daily_wisdom_enabled"] is True
        assert updated["memory_preferences"]["privacy_mode"] == "standard"
        
        # Verify timestamps exist
        assert "updated_at" in updated
    
    def test_update_preferences_partial(self, service, sample_user_id):
        """Test partial preference updates (deep merge)"""
        # First, set initial preferences
        initial = {
            "experience_preferences": {
                "conversation_style": "brief",
                "favorite_personalities": ["krishna"]
            }
        }
        service.update_preferences(sample_user_id, initial)
        
        # Update only conversation_style
        partial_update = {
            "experience_preferences": {
                "conversation_style": "detailed"
            }
        }
        updated = service.update_preferences(sample_user_id, partial_update)
        
        # Conversation style should be updated
        assert updated["experience_preferences"]["conversation_style"] == "detailed"
        
        # Favorite personalities should still be there (deep merge)
        assert "krishna" in updated["experience_preferences"]["favorite_personalities"]
        
        # Other defaults should still exist
        assert updated["experience_preferences"]["language"] == "en"
    
    def test_update_preferences_nested_deep_merge(self, service, sample_user_id):
        """Test deep merge for nested notification types"""
        # Set initial notification types
        initial = {
            "notification_preferences": {
                "types": {
                    "daily_wisdom": False,
                    "streak_reminders": True,
                    "achievements": True,
                    "weekly_summary": True
                }
            }
        }
        service.update_preferences(sample_user_id, initial)
        
        # Update only daily_wisdom
        partial = {
            "notification_preferences": {
                "types": {
                    "daily_wisdom": True
                }
            }
        }
        updated = service.update_preferences(sample_user_id, partial)
        
        # All notification types should be preserved
        types = updated["notification_preferences"]["types"]
        assert types["daily_wisdom"] is True
        assert types["streak_reminders"] is True
        assert types["achievements"] is True
        assert types["weekly_summary"] is True
    
    # =========================================================================
    # Test: Validation - Conversation Style
    # =========================================================================
    
    def test_validation_invalid_conversation_style(self, service, sample_user_id):
        """Test that invalid conversation style is rejected"""
        invalid_prefs = {
            "experience_preferences": {
                "conversation_style": "super_verbose"  # Invalid
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "conversation_style" in str(exc_info.value).lower()
    
    def test_validation_valid_conversation_styles(self, service, sample_user_id):
        """Test that all valid conversation styles are accepted"""
        valid_styles = ["brief", "balanced", "detailed"]
        
        for style in valid_styles:
            prefs = {
                "experience_preferences": {
                    "conversation_style": style
                }
            }
            updated = service.update_preferences(sample_user_id, prefs)
            assert updated["experience_preferences"]["conversation_style"] == style
    
    # =========================================================================
    # Test: Validation - Language
    # =========================================================================
    
    def test_validation_invalid_language(self, service, sample_user_id):
        """Test that invalid language is rejected"""
        invalid_prefs = {
            "experience_preferences": {
                "language": "fr"  # Invalid (only en, hi supported)
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "language" in str(exc_info.value).lower()
    
    # =========================================================================
    # Test: Validation - Formality
    # =========================================================================
    
    def test_validation_invalid_formality(self, service, sample_user_id):
        """Test that invalid formality level is rejected"""
        invalid_prefs = {
            "experience_preferences": {
                "formality": "super_casual"  # Invalid
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "formality" in str(exc_info.value).lower()
    
    # =========================================================================
    # Test: Validation - Favorite Personalities (Max 5)
    # =========================================================================
    
    def test_validation_max_favorite_personalities(self, service, sample_user_id):
        """Test that more than 5 favorite personalities is rejected"""
        invalid_prefs = {
            "experience_preferences": {
                "favorite_personalities": [
                    "krishna", "einstein", "buddha", 
                    "aristotle", "lincoln", "tesla"  # 6 personalities
                ]
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "favorite_personalities" in str(exc_info.value).lower()
        assert "5" in str(exc_info.value)
    
    def test_validation_exactly_5_favorite_personalities(self, service, sample_user_id):
        """Test that exactly 5 favorite personalities is accepted"""
        valid_prefs = {
            "experience_preferences": {
                "favorite_personalities": [
                    "krishna", "einstein", "buddha", "aristotle", "lincoln"
                ]
            }
        }
        
        updated = service.update_preferences(sample_user_id, valid_prefs)
        assert len(updated["experience_preferences"]["favorite_personalities"]) == 5
    
    # =========================================================================
    # Test: Validation - Privacy Mode
    # =========================================================================
    
    def test_validation_invalid_privacy_mode(self, service, sample_user_id):
        """Test that invalid privacy mode is rejected"""
        invalid_prefs = {
            "memory_preferences": {
                "privacy_mode": "super_private"  # Invalid
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "privacy_mode" in str(exc_info.value).lower()
    
    def test_validation_all_privacy_modes(self, service, sample_user_id):
        """Test that all valid privacy modes are accepted"""
        valid_modes = ["standard", "private", "minimal"]
        
        for mode in valid_modes:
            prefs = {
                "memory_preferences": {
                    "privacy_mode": mode
                }
            }
            updated = service.update_preferences(sample_user_id, prefs)
            assert updated["memory_preferences"]["privacy_mode"] == mode
    
    # =========================================================================
    # Test: Validation - Data Retention Days
    # =========================================================================
    
    def test_validation_data_retention_too_low(self, service, sample_user_id):
        """Test that data retention below 30 days is rejected"""
        invalid_prefs = {
            "memory_preferences": {
                "data_retention_days": 15  # Too low
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "data_retention_days" in str(exc_info.value).lower()
        assert "30" in str(exc_info.value)
    
    def test_validation_data_retention_too_high(self, service, sample_user_id):
        """Test that data retention above 365 days is rejected"""
        invalid_prefs = {
            "memory_preferences": {
                "data_retention_days": 400  # Too high
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "data_retention_days" in str(exc_info.value).lower()
        assert "365" in str(exc_info.value)
    
    def test_validation_data_retention_valid_range(self, service, sample_user_id):
        """Test that valid data retention values are accepted"""
        valid_days = [30, 90, 180, 365]
        
        for days in valid_days:
            prefs = {
                "memory_preferences": {
                    "data_retention_days": days
                }
            }
            updated = service.update_preferences(sample_user_id, prefs)
            assert updated["memory_preferences"]["data_retention_days"] == days
    
    # =========================================================================
    # Test: Validation - Timezone
    # =========================================================================
    
    def test_validation_invalid_timezone(self, service, sample_user_id):
        """Test that invalid timezone is rejected"""
        invalid_prefs = {
            "notification_preferences": {
                "timezone": "Invalid/Timezone"
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.update_preferences(sample_user_id, invalid_prefs)
        
        assert "timezone" in str(exc_info.value).lower()
    
    def test_validation_valid_timezones(self, service, sample_user_id):
        """Test that all valid timezones are accepted"""
        valid_timezones = [
            "America/Los_Angeles", "America/New_York", "Europe/London",
            "Asia/Kolkata", "Asia/Tokyo"
        ]
        
        for tz in valid_timezones:
            prefs = {
                "notification_preferences": {
                    "timezone": tz
                }
            }
            updated = service.update_preferences(sample_user_id, prefs)
            assert updated["notification_preferences"]["timezone"] == tz
    
    # =========================================================================
    # Test: Delete Preferences
    # =========================================================================
    
    def test_delete_preferences(self, service, sample_user_id, sample_preferences):
        """Test deleting user preferences"""
        # First create preferences
        service.update_preferences(sample_user_id, sample_preferences)
        
        # Delete them
        result = service.delete_preferences(sample_user_id)
        assert result is True
        
        # Get preferences should return defaults again
        prefs = service.get_preferences(sample_user_id)
        assert prefs["experience_preferences"]["conversation_style"] == "balanced"  # Default
        assert prefs["experience_preferences"]["favorite_personalities"] == []  # Default
    
    # =========================================================================
    # Test: Timestamps
    # =========================================================================
    
    def test_created_at_timestamp(self, service, sample_user_id):
        """Test that created_at timestamp is set correctly"""
        prefs = service.get_preferences(sample_user_id)
        
        assert "created_at" in prefs
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(prefs["created_at"].replace('Z', '+00:00'))
    
    def test_updated_at_timestamp(self, service, sample_user_id):
        """Test that updated_at timestamp is updated on changes"""
        # Get initial preferences
        initial = service.get_preferences(sample_user_id)
        initial_updated_at = initial["updated_at"]
        
        # Update preferences
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp difference
        
        update = {
            "experience_preferences": {
                "conversation_style": "detailed"
            }
        }
        updated = service.update_preferences(sample_user_id, update)
        
        # Updated timestamp should be different
        assert updated["updated_at"] != initial_updated_at
    
    # =========================================================================
    # Test: Edge Cases
    # =========================================================================
    
    def test_empty_update(self, service, sample_user_id):
        """Test updating with empty dictionary"""
        result = service.update_preferences(sample_user_id, {})
        
        # Should return current preferences (with defaults)
        assert "experience_preferences" in result
        assert "notification_preferences" in result
        assert "memory_preferences" in result
    
    def test_invalid_preference_key(self, service, sample_user_id):
        """Test that invalid top-level keys are ignored"""
        invalid_prefs = {
            "invalid_section": {
                "some_key": "some_value"
            },
            "experience_preferences": {
                "conversation_style": "brief"
            }
        }
        
        updated = service.update_preferences(sample_user_id, invalid_prefs)
        
        # Valid preference should be updated
        assert updated["experience_preferences"]["conversation_style"] == "brief"
        
        # Invalid key should not be in result
        assert "invalid_section" not in updated
    
    def test_concurrent_updates(self, service, sample_user_id):
        """Test that multiple updates work correctly"""
        # Simulate multiple updates in sequence
        updates = [
            {"experience_preferences": {"conversation_style": "brief"}},
            {"experience_preferences": {"language": "hi"}},
            {"notification_preferences": {"daily_wisdom_enabled": False}},
            {"memory_preferences": {"privacy_mode": "minimal"}}
        ]
        
        for update in updates:
            service.update_preferences(sample_user_id, update)
        
        # Get final state
        final = service.get_preferences(sample_user_id)
        
        # All updates should be applied (due to deep merge)
        assert final["experience_preferences"]["conversation_style"] == "brief"
        assert final["experience_preferences"]["language"] == "hi"
        assert final["notification_preferences"]["daily_wisdom_enabled"] is False
        assert final["memory_preferences"]["privacy_mode"] == "minimal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
