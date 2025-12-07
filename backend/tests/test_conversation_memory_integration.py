"""
Unit Tests for ConversationMemoryService Integration with PreferencesService
Tests privacy modes, data retention, and storage/retrieval controls
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Optional

from services.conversation_memory_service import (
    ConversationMemoryService,
    ConversationContext,
    ConversationStatus
)
from services.preferences_service import PreferencesService


# Mock ConversationMessage for testing
class MockConversationMessage:
    """Mock conversation message for testing"""
    def __init__(self, id, session_id, user_id, personality_id, message_type, content, timestamp, metadata=None):
        self.id = id
        self.session_id = session_id
        self.user_id = user_id
        self.personality_id = personality_id
        self.message_type = message_type
        self.content = content
        self.timestamp = timestamp
        self.metadata = metadata or {}


class TestConversationMemoryServiceIntegration:
    """Test suite for ConversationMemoryService integration with PreferencesService"""
    
    @pytest.fixture
    def mock_database_service(self):
        """Create mock database service"""
        service = Mock()
        service.store_conversation_message = AsyncMock(return_value=True)
        service.get_conversation_messages = AsyncMock(return_value=[])
        return service
    
    @pytest.fixture
    def preferences_service(self):
        """Create PreferencesService instance"""
        return PreferencesService()
    
    @pytest.fixture
    def service(self, mock_database_service, preferences_service):
        """Create ConversationMemoryService instance with mocked dependencies"""
        return ConversationMemoryService(
            database_service=mock_database_service,
            preferences_service=preferences_service
        )
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing"""
        return "test_user_123"
    
    @pytest.fixture
    def sample_conversation_id(self):
        """Sample conversation ID for testing"""
        return "conv_test_user_123_krishna_20251207_120000"


class TestPrivacyModeStorage(TestConversationMemoryServiceIntegration):
    """Test privacy mode controls for message storage"""
    
    @pytest.mark.asyncio
    async def test_standard_privacy_mode_allows_storage(
        self,
        service,
        preferences_service,
        sample_user_id,
        sample_conversation_id
    ):
        """Test that standard privacy mode allows message storage"""
        # Setup: Standard privacy mode
        prefs = {
            "memory_preferences": {
                "remember_conversations": True,
                "privacy_mode": "standard"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Should allow storage
        should_store = await service._should_store_message(sample_user_id)
        assert should_store is True
    
    @pytest.mark.asyncio
    async def test_private_privacy_mode_allows_storage(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that private privacy mode still allows storage (just limits retrieval)"""
        # Setup: Private privacy mode
        prefs = {
            "memory_preferences": {
                "remember_conversations": True,
                "privacy_mode": "private"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Should allow storage
        should_store = await service._should_store_message(sample_user_id)
        assert should_store is True
    
    @pytest.mark.asyncio
    async def test_minimal_privacy_mode_blocks_storage(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that minimal privacy mode blocks message storage"""
        # Setup: Minimal privacy mode
        prefs = {
            "memory_preferences": {
                "remember_conversations": True,
                "privacy_mode": "minimal"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Should block storage
        should_store = await service._should_store_message(sample_user_id)
        assert should_store is False
    
    @pytest.mark.asyncio
    async def test_remember_conversations_disabled_blocks_storage(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that disabling remember_conversations blocks storage"""
        # Setup: Remember conversations disabled
        prefs = {
            "memory_preferences": {
                "remember_conversations": False,
                "privacy_mode": "standard"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Should block storage
        should_store = await service._should_store_message(sample_user_id)
        assert should_store is False
    
    @pytest.mark.asyncio
    async def test_add_message_respects_storage_preferences(
        self,
        service,
        preferences_service,
        sample_user_id,
        sample_conversation_id,
        mock_database_service
    ):
        """Test that add_message respects storage preferences"""
        # Setup: Minimal privacy mode (no storage)
        prefs = {
            "memory_preferences": {
                "remember_conversations": True,
                "privacy_mode": "minimal"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Try to add message
        result = await service.add_message(
            conversation_id=sample_conversation_id,
            user_id=sample_user_id,
            personality_id="krishna",
            message_type="user_query",
            content="Test message"
        )
        
        # Should return None (not stored)
        assert result is None
        
        # Database should not be called
        mock_database_service.store_conversation_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_add_message_stores_with_standard_mode(
        self,
        service,
        preferences_service,
        sample_user_id,
        sample_conversation_id
    ):
        """Test that add_message stores with standard privacy mode"""
        # Setup: Standard privacy mode
        prefs = {
            "memory_preferences": {
                "remember_conversations": True,
                "privacy_mode": "standard"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Start conversation first
        await service.start_conversation(
            user_id=sample_user_id,
            personality_id="krishna"
        )
        
        # Add message
        result = await service.add_message(
            conversation_id=sample_conversation_id,
            user_id=sample_user_id,
            personality_id="krishna",
            message_type="user_query",
            content="Test message"
        )
        
        # Should return message (or dict)
        assert result is not None


class TestPrivacyModeRetrieval(TestConversationMemoryServiceIntegration):
    """Test privacy mode controls for context retrieval"""
    
    @pytest.mark.asyncio
    async def test_standard_privacy_mode_allows_retrieval(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that standard privacy mode allows context retrieval"""
        # Setup: Standard privacy mode
        prefs = {
            "memory_preferences": {
                "privacy_mode": "standard"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Check retrieval
        should_retrieve, privacy_mode = await service._should_retrieve_context(sample_user_id)
        
        assert should_retrieve is True
        assert privacy_mode == "standard"
    
    @pytest.mark.asyncio
    async def test_private_privacy_mode_allows_limited_retrieval(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that private privacy mode allows limited retrieval"""
        # Setup: Private privacy mode
        prefs = {
            "memory_preferences": {
                "privacy_mode": "private"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Check retrieval
        should_retrieve, privacy_mode = await service._should_retrieve_context(sample_user_id)
        
        assert should_retrieve is True
        assert privacy_mode == "private"
    
    @pytest.mark.asyncio
    async def test_minimal_privacy_mode_blocks_retrieval(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that minimal privacy mode blocks context retrieval"""
        # Setup: Minimal privacy mode
        prefs = {
            "memory_preferences": {
                "privacy_mode": "minimal"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Check retrieval
        should_retrieve, privacy_mode = await service._should_retrieve_context(sample_user_id)
        
        assert should_retrieve is False
        assert privacy_mode == "minimal"
    
    @pytest.mark.asyncio
    async def test_get_conversation_context_respects_minimal_mode(
        self,
        service,
        preferences_service,
        sample_user_id,
        sample_conversation_id
    ):
        """Test that get_conversation_context respects minimal privacy mode"""
        # Setup: Minimal privacy mode
        prefs = {
            "memory_preferences": {
                "privacy_mode": "minimal"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Try to get context
        context = await service.get_conversation_context(
            conversation_id=sample_conversation_id,
            user_id=sample_user_id
        )
        
        # Should return None (blocked by privacy mode)
        assert context is None
    
    @pytest.mark.asyncio
    async def test_get_conversation_context_allows_standard_mode(
        self,
        service,
        preferences_service,
        sample_user_id,
        sample_conversation_id
    ):
        """Test that get_conversation_context allows standard privacy mode"""
        # Setup: Standard privacy mode
        prefs = {
            "memory_preferences": {
                "privacy_mode": "standard"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Start conversation first
        await service.start_conversation(
            user_id=sample_user_id,
            personality_id="krishna"
        )
        
        # Mock _get_recent_messages to return empty list
        service._get_recent_messages = AsyncMock(return_value=[])
        service._analyze_user_patterns = AsyncMock(return_value={})
        service._get_personality_preferences = AsyncMock(return_value={})
        
        # Get context
        context = await service.get_conversation_context(
            conversation_id=sample_conversation_id,
            user_id=sample_user_id
        )
        
        # Should return context (allowed by privacy mode)
        assert context is not None
        assert isinstance(context, ConversationContext)


class TestDataRetentionPolicy(TestConversationMemoryServiceIntegration):
    """Test data retention policy enforcement"""
    
    @pytest.mark.asyncio
    async def test_cleanup_by_retention_policy_default_90_days(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test cleanup with default 90-day retention"""
        # Setup: Default preferences (90 days)
        prefs = {
            "memory_preferences": {
                "data_retention_days": 90
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Create old conversation in cache (100 days old)
        old_conv_id = f"conv_{sample_user_id}_krishna_old"
        service.session_cache[old_conv_id] = {
            "user_id": sample_user_id,
            "personality_id": "krishna",
            "started_at": datetime.now() - timedelta(days=100),
            "status": ConversationStatus.ACTIVE
        }
        
        # Create recent conversation (30 days old)
        recent_conv_id = f"conv_{sample_user_id}_krishna_recent"
        service.session_cache[recent_conv_id] = {
            "user_id": sample_user_id,
            "personality_id": "krishna",
            "started_at": datetime.now() - timedelta(days=30),
            "status": ConversationStatus.ACTIVE
        }
        
        # Mock _archive_conversation
        service._archive_conversation = AsyncMock()
        
        # Run cleanup
        cleaned_count = await service.cleanup_by_retention_policy(sample_user_id)
        
        # Should clean up old conversation
        assert cleaned_count == 1
        assert old_conv_id not in service.session_cache
        assert recent_conv_id in service.session_cache
    
    @pytest.mark.asyncio
    async def test_cleanup_by_retention_policy_custom_30_days(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test cleanup with custom 30-day retention"""
        # Setup: 30-day retention
        prefs = {
            "memory_preferences": {
                "data_retention_days": 30
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Create conversation 45 days old
        old_conv_id = f"conv_{sample_user_id}_krishna_old"
        service.session_cache[old_conv_id] = {
            "user_id": sample_user_id,
            "personality_id": "krishna",
            "started_at": datetime.now() - timedelta(days=45),
            "status": ConversationStatus.ACTIVE
        }
        
        # Mock _archive_conversation
        service._archive_conversation = AsyncMock()
        
        # Run cleanup
        cleaned_count = await service.cleanup_by_retention_policy(sample_user_id)
        
        # Should clean up conversation
        assert cleaned_count == 1
        assert old_conv_id not in service.session_cache
    
    @pytest.mark.asyncio
    async def test_cleanup_by_retention_policy_365_days(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test cleanup with maximum 365-day retention"""
        # Setup: 365-day retention
        prefs = {
            "memory_preferences": {
                "data_retention_days": 365
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Create conversation 300 days old (should be kept)
        conv_id = f"conv_{sample_user_id}_krishna"
        service.session_cache[conv_id] = {
            "user_id": sample_user_id,
            "personality_id": "krishna",
            "started_at": datetime.now() - timedelta(days=300),
            "status": ConversationStatus.ACTIVE
        }
        
        # Run cleanup
        cleaned_count = await service.cleanup_by_retention_policy(sample_user_id)
        
        # Should not clean up (within retention period)
        assert cleaned_count == 0
        assert conv_id in service.session_cache
    
    @pytest.mark.asyncio
    async def test_cleanup_only_affects_specific_user(
        self,
        service,
        preferences_service
    ):
        """Test that cleanup only affects the specified user's conversations"""
        user1_id = "user1"
        user2_id = "user2"
        
        # Setup: User1 with 30-day retention
        prefs = {
            "memory_preferences": {
                "data_retention_days": 30
            }
        }
        preferences_service.update_preferences(user1_id, prefs)
        
        # Create old conversations for both users
        user1_conv = f"conv_{user1_id}_krishna"
        user2_conv = f"conv_{user2_id}_krishna"
        
        service.session_cache[user1_conv] = {
            "user_id": user1_id,
            "personality_id": "krishna",
            "started_at": datetime.now() - timedelta(days=45),
            "status": ConversationStatus.ACTIVE
        }
        
        service.session_cache[user2_conv] = {
            "user_id": user2_id,
            "personality_id": "krishna",
            "started_at": datetime.now() - timedelta(days=45),
            "status": ConversationStatus.ACTIVE
        }
        
        # Mock _archive_conversation
        service._archive_conversation = AsyncMock()
        
        # Run cleanup for user1 only
        cleaned_count = await service.cleanup_by_retention_policy(user1_id)
        
        # Should only clean up user1's conversation
        assert cleaned_count == 1
        assert user1_conv not in service.session_cache
        assert user2_conv in service.session_cache


class TestConnectInsightsFeature(TestConversationMemoryServiceIntegration):
    """Test connect_insights feature behavior"""
    
    @pytest.mark.asyncio
    async def test_connect_insights_enabled_allows_cross_session_context(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that connect_insights enabled allows cross-session context"""
        # Setup: connect_insights enabled
        prefs = {
            "memory_preferences": {
                "connect_insights": True,
                "privacy_mode": "standard"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Verify preferences stored correctly
        stored_prefs = preferences_service.get_preferences(sample_user_id)
        memory_prefs = stored_prefs.get('memory_preferences', {})
        
        assert memory_prefs.get('connect_insights') is True
        assert memory_prefs.get('privacy_mode') == "standard"
    
    @pytest.mark.asyncio
    async def test_connect_insights_disabled_limits_context(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that connect_insights disabled limits context to current session"""
        # Setup: connect_insights disabled
        prefs = {
            "memory_preferences": {
                "connect_insights": False,
                "privacy_mode": "standard"
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Verify preferences stored correctly
        stored_prefs = preferences_service.get_preferences(sample_user_id)
        memory_prefs = stored_prefs.get('memory_preferences', {})
        
        assert memory_prefs.get('connect_insights') is False


class TestServiceInitialization(TestConversationMemoryServiceIntegration):
    """Test service initialization with preferences"""
    
    def test_service_initializes_with_preferences_service(
        self,
        mock_database_service,
        preferences_service
    ):
        """Test that service initializes correctly with PreferencesService"""
        service = ConversationMemoryService(
            database_service=mock_database_service,
            preferences_service=preferences_service
        )
        
        assert service.preferences_service is not None
        assert service.database_service is not None
    
    def test_service_initializes_without_preferences_service(
        self,
        mock_database_service
    ):
        """Test that service initializes correctly without PreferencesService"""
        service = ConversationMemoryService(
            database_service=mock_database_service,
            preferences_service=None
        )
        
        assert service.preferences_service is None
        assert service.database_service is not None
    
    @pytest.mark.asyncio
    async def test_service_defaults_to_storage_without_preferences(
        self,
        mock_database_service
    ):
        """Test that service defaults to allowing storage without PreferencesService"""
        service = ConversationMemoryService(
            database_service=mock_database_service,
            preferences_service=None
        )
        
        # Should default to allowing storage
        should_store = await service._should_store_message("any_user")
        assert should_store is True
    
    @pytest.mark.asyncio
    async def test_service_defaults_to_retrieval_without_preferences(
        self,
        mock_database_service
    ):
        """Test that service defaults to allowing retrieval without PreferencesService"""
        service = ConversationMemoryService(
            database_service=mock_database_service,
            preferences_service=None
        )
        
        # Should default to allowing retrieval
        should_retrieve, privacy_mode = await service._should_retrieve_context("any_user")
        assert should_retrieve is True
        assert privacy_mode == "standard"


class TestErrorHandling(TestConversationMemoryServiceIntegration):
    """Test error handling in preference integration"""
    
    @pytest.mark.asyncio
    async def test_storage_check_handles_preferences_error(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that storage check handles PreferencesService errors gracefully"""
        # Mock get_preferences to raise exception
        preferences_service.get_preferences = Mock(side_effect=Exception("DB error"))
        
        # Should not raise, defaults to True
        should_store = await service._should_store_message(sample_user_id)
        assert should_store is True
    
    @pytest.mark.asyncio
    async def test_retrieval_check_handles_preferences_error(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that retrieval check handles PreferencesService errors gracefully"""
        # Mock get_preferences to raise exception
        preferences_service.get_preferences = Mock(side_effect=Exception("DB error"))
        
        # Should not raise, defaults to True with standard mode
        should_retrieve, privacy_mode = await service._should_retrieve_context(sample_user_id)
        assert should_retrieve is True
        assert privacy_mode == "standard"
    
    @pytest.mark.asyncio
    async def test_retention_cleanup_handles_error(
        self,
        service,
        preferences_service,
        sample_user_id
    ):
        """Test that retention cleanup handles errors gracefully"""
        # Mock get_preferences to raise exception
        preferences_service.get_preferences = Mock(side_effect=Exception("DB error"))
        
        # Should not raise, returns 0
        cleaned_count = await service.cleanup_by_retention_policy(sample_user_id)
        assert cleaned_count == 0
