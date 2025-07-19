"""
Integration test for transaction manager with real database operations
Tests actual atomic operations without mocking core database functionality
"""

import asyncio
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.transaction_manager import (
    DatabaseTransactionManager,
    atomic_token_operation,
    atomic_conversation_save
)
from services.database_service import (
    DatabaseService,
    UsageRecord,
    UserStats,
    Conversation
)
from core.token_tracker import TokenUsageTracker


async def test_basic_transaction_manager():
    """Test basic transaction manager functionality"""
    print("🔄 Testing DatabaseTransactionManager...")
    
    # Create temporary storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize database service with temp storage
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.spiritual_texts_path = os.path.join(temp_dir, 'spiritual-texts.json')
        db_service.conversations_path = os.path.join(temp_dir, 'conversations.json')
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        # Initialize transaction manager
        transaction_manager = DatabaseTransactionManager(db_service)
        
        # Test successful transaction
        usage_record = UsageRecord(
            id="test_integration_usage",
            userId="integration_user",
            userEmail="integration@vimarsh.com",
            sessionId="integration_session",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=100,
            outputTokens=50,
            totalTokens=150,
            costUsd=0.025,
            requestType="spiritual_guidance",
            responseQuality="high",
            personality="krishna"
        )
        
        user_stats = UserStats(
            id="stats_integration_user",
            userId="integration_user",
            userEmail="integration@vimarsh.com",
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
        
        try:
            # Execute atomic operation
            async with transaction_manager.transaction() as tx:
                await tx.save_usage_record(usage_record)
                await tx.save_user_stats(user_stats)
            
            print("✅ Transaction completed successfully")
            
            # Verify transaction history
            history = await transaction_manager.get_transaction_history()
            print(f"📊 Transaction history: {len(history)} transactions")
            
            if history:
                latest = history[0]
                print(f"   Latest transaction: {latest['state']} with {latest['operation_count']} operations")
            
            return True
            
        except Exception as e:
            print(f"❌ Transaction failed: {e}")
            return False


async def test_atomic_utility_functions():
    """Test atomic utility functions"""
    print("\n🔄 Testing atomic utility functions...")
    
    # Create temporary storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize database service
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.spiritual_texts_path = os.path.join(temp_dir, 'spiritual-texts.json')
        db_service.conversations_path = os.path.join(temp_dir, 'conversations.json')
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        # Test atomic token operation
        usage_record = UsageRecord(
            id="atomic_test_usage",
            userId="atomic_user",
            userEmail="atomic@vimarsh.com",
            sessionId="atomic_session",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=200,
            outputTokens=100,
            totalTokens=300,
            costUsd=0.05,
            requestType="spiritual_guidance",
            responseQuality="high",
            personality="krishna"
        )
        
        user_stats = UserStats(
            id="stats_atomic_user",
            userId="atomic_user",
            userEmail="atomic@vimarsh.com",
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
        
        try:
            await atomic_token_operation(usage_record, user_stats)
            print("✅ Atomic token operation completed successfully")
            
            # Test atomic conversation save
            conversation = Conversation(
                id="atomic_conv_123",
                userId="atomic_user",
                userEmail="atomic@vimarsh.com",
                sessionId="atomic_session",
                timestamp=datetime.utcnow().isoformat(),
                question="What is the meaning of dharma?",
                response="Dharma refers to righteous duty and moral law...",
                citations=["Bhagavad Gita 2.47", "Mahabharata 12.109.10"],
                personality="krishna"
            )
            
            await atomic_conversation_save(conversation)
            print("✅ Atomic conversation save completed successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Atomic operations failed: {e}")
            return False


async def test_consistency_validation():
    """Test consistency validation functionality"""
    print("\n🔄 Testing consistency validation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize components
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        transaction_manager = DatabaseTransactionManager(db_service)
        
        try:
            # Run consistency validation
            report = await transaction_manager.validate_consistency()
            
            print(f"✅ Consistency validation completed")
            print(f"   Total inconsistencies: {report['summary']['total_inconsistencies']}")
            print(f"   Validation time: {report['summary']['validation_time']}")
            
            # Test with Cosmos DB "enabled" (mocked)
            transaction_manager.db_service.is_cosmos_enabled = True
            report = await transaction_manager.validate_consistency()
            
            print(f"✅ Cosmos DB consistency validation completed")
            
            return True
            
        except Exception as e:
            print(f"❌ Consistency validation failed: {e}")
            return False


async def main():
    """Run all integration tests"""
    print("🚀 Starting Transaction Manager Integration Tests")
    print("=" * 60)
    
    tests = [
        test_basic_transaction_manager,
        test_atomic_utility_functions,
        test_consistency_validation
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All transaction manager integration tests PASSED!")
        return 0
    else:
        print("❌ Some transaction manager integration tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
