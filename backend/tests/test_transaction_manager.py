"""
Comprehensive test suite for DatabaseTransactionManager
Tests atomic operations, rollback mechanisms, and consistency validation
"""

import asyncio
import json
import os
import pytest
import tempfile
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from typing import List

# Import the modules under test
from services.transaction_manager import (
    DatabaseTransactionManager,
    DatabaseTransaction,
    TransactionOperation,
    TransactionState,
    TransactionContext,
    atomic_token_operation,
    atomic_conversation_save
)
from services.database_service import (
    DatabaseService,
    UsageRecord,
    UserStats,
    Conversation,
    SpiritualText
)
from core.token_tracker import TokenUsageTracker


class TestDatabaseTransactionManager:
    """Test suite for DatabaseTransactionManager"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup is handled by tempfile
    
    @pytest.fixture
    def mock_db_service(self, temp_storage):
        """Create a mock database service for testing"""
        db_service = Mock(spec=DatabaseService)
        db_service.storage_path = temp_storage
        db_service.is_cosmos_enabled = False
        
        # Mock local storage methods
        db_service._add_to_local = Mock(return_value=True)
        db_service._save_conversation_local = Mock(return_value=True)
        db_service._save_usage_record_local = Mock(return_value=True)
        db_service._save_user_stats_local = Mock(return_value=True)
        
        # Mock Cosmos DB methods
        db_service._save_to_cosmos = AsyncMock(return_value=True)
        
        # Mock Cosmos DB containers
        db_service.usage_records_container = Mock()
        db_service.conversations_container = Mock()
        db_service.user_stats_container = Mock()
        db_service.spiritual_texts_container = Mock()
        
        return db_service
    
    @pytest.fixture
    def transaction_manager(self, mock_db_service):
        """Create transaction manager for testing"""
        return DatabaseTransactionManager(db_service=mock_db_service)
    
    @pytest.mark.asyncio
    async def test_successful_transaction(self, transaction_manager):
        """Test successful transaction with multiple operations"""
        # Create test data
        usage_record = UsageRecord(
            id="test_usage_1",
            userId="user123",
            userEmail="test@example.com",
            sessionId="session123",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=100,
            outputTokens=50,
            totalTokens=150,
            costUsd=0.025,
            requestType="spiritual_guidance",
            responseQuality="high"
        )
        
        user_stats = UserStats(
            id="stats_user123",
            userId="user123",
            userEmail="test@example.com",
            totalRequests=1,
            totalTokens=150,
            totalCostUsd=0.025,
            currentMonthTokens=150,
            currentMonthCostUsd=0.025,
            lastRequest=datetime.utcnow().isoformat(),
            avgTokensPerRequest=150.0,
            favoriteModel="gemini-2.5-flash",
            personalityUsage={"krishna": 1},
            qualityBreakdown={"high": 1}
        )
        
        # Execute transaction
        async with transaction_manager.transaction() as tx:
            await tx.save_usage_record(usage_record)
            await tx.save_user_stats(user_stats)
        
        # Verify transaction was committed
        assert len(transaction_manager.active_transactions) == 0
        
        # Verify local storage was called
        transaction_manager.db_service._save_usage_record_local.assert_called_once()
        transaction_manager.db_service._save_user_stats_local.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_exception(self, transaction_manager):
        """Test transaction rollback when exception occurs"""
        # Mock a failure in local storage
        transaction_manager.db_service._save_usage_record_local.return_value = False
        
        usage_record = UsageRecord(
            id="test_usage_fail",
            userId="user123",
            userEmail="test@example.com",
            sessionId="session123",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=100,
            outputTokens=50,
            totalTokens=150,
            costUsd=0.025,
            requestType="spiritual_guidance",
            responseQuality="high"
        )
        
        # Execute transaction that should fail
        with pytest.raises(Exception):
            async with transaction_manager.transaction() as tx:
                await tx.save_usage_record(usage_record)
        
        # Verify transaction was cleaned up
        assert len(transaction_manager.active_transactions) == 0
    
    @pytest.mark.asyncio
    async def test_atomic_token_operation(self, transaction_manager):
        """Test the atomic token operation utility function"""
        usage_record = UsageRecord(
            id="test_atomic_usage",
            userId="user456",
            userEmail="atomic@example.com",
            sessionId="session456",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=200,
            outputTokens=100,
            totalTokens=300,
            costUsd=0.05,
            requestType="spiritual_guidance",
            responseQuality="high"
        )
        
        user_stats = UserStats(
            id="stats_user456",
            userId="user456",
            userEmail="atomic@example.com",
            totalRequests=1,
            totalTokens=300,
            totalCostUsd=0.05,
            currentMonthTokens=300,
            currentMonthCostUsd=0.05,
            lastRequest=datetime.utcnow().isoformat(),
            avgTokensPerRequest=300.0,
            favoriteModel="gemini-2.5-flash",
            personalityUsage={"krishna": 1},
            qualityBreakdown={"high": 1}
        )
        
        # Execute atomic operation
        with patch('services.transaction_manager.transaction_manager', transaction_manager):
            await atomic_token_operation(usage_record, user_stats)
        
        # Verify both records were saved
        transaction_manager.db_service._save_usage_record_local.assert_called()
        transaction_manager.db_service._save_user_stats_local.assert_called()
    
    @pytest.mark.asyncio
    async def test_conversation_save_with_usage(self, transaction_manager):
        """Test atomic conversation save with usage tracking"""
        conversation = Conversation(
            id="conv_123",
            userId="user789",
            userEmail="conv@example.com",
            sessionId="session789",
            timestamp=datetime.utcnow().isoformat(),
            question="What is dharma?",
            response="Dharma is your righteous duty...",
            citations=["Bhagavad Gita 2.47"],
            personality="krishna"
        )
        
        usage_record = UsageRecord(
            id="usage_conv_123",
            userId="user789",
            userEmail="conv@example.com",
            sessionId="session789",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=50,
            outputTokens=25,
            totalTokens=75,
            costUsd=0.0125,
            requestType="spiritual_guidance",
            responseQuality="high"
        )
        
        # Execute atomic conversation save
        with patch('services.transaction_manager.transaction_manager', transaction_manager):
            await atomic_conversation_save(conversation, usage_record)
        
        # Verify both records were saved
        transaction_manager.db_service._save_conversation_local.assert_called()
        transaction_manager.db_service._save_usage_record_local.assert_called()
    
    @pytest.mark.asyncio
    async def test_cosmos_db_enabled_operations(self, transaction_manager):
        """Test operations when Cosmos DB is enabled"""
        # Enable Cosmos DB for this test
        transaction_manager.db_service.is_cosmos_enabled = True
        
        usage_record = UsageRecord(
            id="cosmos_test_usage",
            userId="cosmos_user",
            userEmail="cosmos@example.com",
            sessionId="cosmos_session",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=75,
            outputTokens=25,
            totalTokens=100,
            costUsd=0.015,
            requestType="spiritual_guidance",
            responseQuality="high"
        )
        
        # Execute transaction
        async with transaction_manager.transaction() as tx:
            await tx.save_usage_record(usage_record)
        
        # Verify both local and Cosmos DB were called
        transaction_manager.db_service._save_usage_record_local.assert_called()
        transaction_manager.db_service._save_to_cosmos.assert_called()
    
    @pytest.mark.asyncio
    async def test_consistency_validation(self, transaction_manager):
        """Test consistency validation between storage systems"""
        # Test with Cosmos DB disabled
        report = await transaction_manager.validate_consistency()
        assert 'validation_time' in report['summary']
        assert report['summary']['total_inconsistencies'] == 0
        
        # Test with Cosmos DB enabled
        transaction_manager.db_service.is_cosmos_enabled = True
        report = await transaction_manager.validate_consistency()
        assert 'validation_time' in report['summary']
    
    def test_transaction_log_initialization(self, transaction_manager):
        """Test transaction log file initialization"""
        log_path = transaction_manager.transaction_log_path
        assert os.path.exists(log_path)
        
        # Verify log file contains empty array
        with open(log_path, 'r') as f:
            log_data = json.load(f)
        assert log_data == []
    
    @pytest.mark.asyncio
    async def test_transaction_history(self, transaction_manager):
        """Test transaction history retrieval"""
        # Execute a transaction to create history
        usage_record = UsageRecord(
            id="history_test",
            userId="history_user",
            userEmail="history@example.com",
            sessionId="history_session",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=50,
            outputTokens=25,
            totalTokens=75,
            costUsd=0.01,
            requestType="spiritual_guidance",
            responseQuality="high"
        )
        
        async with transaction_manager.transaction() as tx:
            await tx.save_usage_record(usage_record)
        
        # Get transaction history
        history = await transaction_manager.get_transaction_history()
        assert len(history) >= 1
        assert history[0]['state'] == 'committed'
        assert 'transaction_id' in history[0]


class TestTokenUsageTrackerIntegration:
    """Test integration between TokenUsageTracker and TransactionManager"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
    
    @pytest.fixture
    def mock_db_service(self, temp_storage):
        """Create mock database service"""
        db_service = Mock(spec=DatabaseService)
        db_service.storage_path = temp_storage
        db_service.is_cosmos_enabled = False
        db_service._save_usage_record_local = Mock(return_value=True)
        db_service._save_user_stats_local = Mock(return_value=True)
        db_service.get_user_stats = AsyncMock(return_value=None)
        return db_service
    
    @pytest.fixture
    def token_tracker(self, mock_db_service):
        """Create token usage tracker for testing"""
        with patch('core.token_tracker.db_service', mock_db_service):
            with patch('core.token_tracker.DATABASE_AVAILABLE', True):
                with patch('core.token_tracker.TRANSACTION_MANAGER_AVAILABLE', True):
                    return TokenUsageTracker()
    
    @pytest.mark.asyncio
    async def test_token_tracker_atomic_save(self, token_tracker):
        """Test token tracker uses atomic operations"""
        # Record usage which should trigger atomic save
        usage = token_tracker.record_usage(
            user_id="tracker_user",
            user_email="tracker@example.com",
            session_id="tracker_session",
            model="gemini-2.5-flash",
            input_tokens=100,
            output_tokens=50,
            request_type="spiritual_guidance",
            response_quality="high",
            personality="krishna"
        )
        
        # Verify usage was recorded
        assert usage.user_id == "tracker_user"
        assert usage.total_tokens == 150
        assert len(token_tracker.usage_records) == 1
        
        # Allow async task to complete
        await asyncio.sleep(0.1)
    
    @pytest.mark.asyncio
    async def test_token_tracker_fallback_save(self, token_tracker):
        """Test token tracker falls back to non-atomic save when transaction manager unavailable"""
        with patch('core.token_tracker.TRANSACTION_MANAGER_AVAILABLE', False):
            usage = token_tracker.record_usage(
                user_id="fallback_user",
                user_email="fallback@example.com",
                session_id="fallback_session",
                model="gemini-2.5-flash",
                input_tokens=75,
                output_tokens=25,
                request_type="spiritual_guidance",
                response_quality="high",
                personality="krishna"
            )
            
            # Verify usage was recorded
            assert usage.user_id == "fallback_user"
            assert usage.total_tokens == 100
            
            # Allow async task to complete
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
