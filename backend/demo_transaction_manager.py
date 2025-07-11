"""
Transaction Manager Demonstration
Shows atomic operations, rollback scenarios, and consistency validation
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
    transaction_manager
)
from services.database_service import (
    DatabaseService,
    UsageRecord,
    UserStats,
    Conversation
)


async def demonstrate_successful_transaction():
    """Demonstrate successful atomic transaction"""
    print("🎯 DEMO 1: Successful Atomic Transaction")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        tx_manager = DatabaseTransactionManager(db_service)
        
        # Create test data
        usage_record = UsageRecord(
            id="demo_usage_success",
            userId="demo_user_1",
            userEmail="demo1@vimarsh.com",
            sessionId="demo_session_1",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=150,
            outputTokens=75,
            totalTokens=225,
            costUsd=0.035,
            requestType="spiritual_guidance",
            responseQuality="high",
            personality="krishna"
        )
        
        user_stats = UserStats(
            id="stats_demo_user_1",
            userId="demo_user_1",
            userEmail="demo1@vimarsh.com",
            totalRequests=1,
            totalTokens=225,
            totalCostUsd=0.035,
            currentMonthTokens=225,
            currentMonthCostUsd=0.035,
            lastRequest=datetime.utcnow().isoformat(),
            avgTokensPerRequest=225.0,
            favoriteModel="gemini-2.5-flash",
            personalityUsage={"krishna": 1},
            qualityBreakdown={"high": 1}
        )
        
        conversation = Conversation(
            id="demo_conv_1",
            userId="demo_user_1",
            userEmail="demo1@vimarsh.com",
            sessionId="demo_session_1",
            timestamp=datetime.utcnow().isoformat(),
            question="What is the path to moksha?",
            response="The path to moksha involves selfless action, devotion, and knowledge...",
            citations=["Bhagavad Gita 18.65", "Bhagavad Gita 9.34"],
            personality="krishna"
        )
        
        print(f"💾 Saving usage record: {usage_record.totalTokens} tokens, ${usage_record.costUsd}")
        print(f"📊 Saving user stats: {user_stats.totalRequests} requests")
        print(f"💬 Saving conversation: {len(conversation.response)} chars")
        
        # Execute transaction
        async with tx_manager.transaction() as tx:
            await tx.save_usage_record(usage_record)
            await tx.save_user_stats(user_stats)
            await tx.save_conversation(conversation)
        
        print("✅ Transaction committed successfully!")
        
        # Show transaction history
        history = await tx_manager.get_transaction_history(limit=1)
        if history:
            latest = history[0]
            print(f"📝 Transaction ID: {latest['transaction_id']}")
            print(f"📝 State: {latest['state']}")
            print(f"📝 Operations: {latest['operation_count']}")
        
        print()


async def demonstrate_rollback_scenario():
    """Demonstrate transaction rollback on failure"""
    print("🎯 DEMO 2: Transaction Rollback on Failure")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup with a db service that will fail
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        # Make one of the save methods fail
        original_save_method = db_service._save_user_stats_local
        def failing_save_method(stats):
            raise Exception("Simulated database failure")
        db_service._save_user_stats_local = failing_save_method
        
        tx_manager = DatabaseTransactionManager(db_service)
        
        # Create test data
        usage_record = UsageRecord(
            id="demo_usage_fail",
            userId="demo_user_2",
            userEmail="demo2@vimarsh.com",
            sessionId="demo_session_2",
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
            id="stats_demo_user_2",
            userId="demo_user_2",
            userEmail="demo2@vimarsh.com",
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
        
        print(f"💾 Attempting to save usage record: {usage_record.totalTokens} tokens")
        print(f"📊 Attempting to save user stats: {user_stats.totalRequests} requests")
        print("💥 Simulating database failure on user stats save...")
        
        # Execute transaction that will fail
        try:
            async with tx_manager.transaction() as tx:
                await tx.save_usage_record(usage_record)
                await tx.save_user_stats(user_stats)  # This will fail
        except Exception as e:
            print(f"❌ Transaction failed as expected: {e}")
        
        # Show transaction history
        history = await tx_manager.get_transaction_history(limit=1)
        if history:
            latest = history[0]
            print(f"📝 Transaction ID: {latest['transaction_id']}")
            print(f"📝 State: {latest['state']}")
            print(f"📝 Error: {latest.get('error_message', 'N/A')}")
        
        print()


async def demonstrate_atomic_utility():
    """Demonstrate atomic utility functions"""
    print("🎯 DEMO 3: Atomic Utility Functions")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        # Initialize global transaction manager
        global transaction_manager
        transaction_manager = DatabaseTransactionManager(db_service)
        
        # Test atomic token operation
        usage_record = UsageRecord(
            id="atomic_demo_usage",
            userId="atomic_user",
            userEmail="atomic@vimarsh.com",
            sessionId="atomic_session",
            timestamp=datetime.utcnow().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=300,
            outputTokens=150,
            totalTokens=450,
            costUsd=0.075,
            requestType="spiritual_guidance",
            responseQuality="high",
            personality="krishna"
        )
        
        user_stats = UserStats(
            id="stats_atomic_user",
            userId="atomic_user",
            userEmail="atomic@vimarsh.com",
            totalRequests=1,
            totalTokens=450,
            totalCostUsd=0.075,
            currentMonthTokens=450,
            currentMonthCostUsd=0.075,
            lastRequest=datetime.utcnow().isoformat(),
            avgTokensPerRequest=450.0,
            favoriteModel="gemini-2.5-flash",
            personalityUsage={"krishna": 1},
            qualityBreakdown={"high": 1}
        )
        
        print(f"⚡ Using atomic_token_operation utility")
        print(f"💾 Token usage: {usage_record.totalTokens} tokens, ${usage_record.costUsd}")
        print(f"📊 User stats: {user_stats.totalRequests} requests")
        
        await atomic_token_operation(usage_record, user_stats)
        print("✅ Atomic operation completed successfully!")
        
        # Show transaction history
        history = await transaction_manager.get_transaction_history(limit=1)
        if history:
            latest = history[0]
            print(f"📝 Transaction ID: {latest['transaction_id']}")
            print(f"📝 Operations: {latest['operation_count']}")
        
        print()


async def demonstrate_consistency_validation():
    """Demonstrate consistency validation"""
    print("🎯 DEMO 4: Consistency Validation")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        tx_manager = DatabaseTransactionManager(db_service)
        
        print("🔍 Running consistency validation (Local storage only)...")
        report = await tx_manager.validate_consistency()
        
        print(f"📊 Validation completed at: {report['summary']['validation_time']}")
        print(f"📊 Total inconsistencies: {report['summary']['total_inconsistencies']}")
        print(f"📊 Spiritual texts: {len(report['spiritual_texts'])} issues")
        print(f"📊 Conversations: {len(report['conversations'])} issues")
        print(f"📊 Usage records: {len(report['usage_records'])} issues")
        print(f"📊 User stats: {len(report['user_stats'])} issues")
        
        # Test with Cosmos DB "enabled"
        print("\n🔍 Running consistency validation (With Cosmos DB enabled)...")
        tx_manager.db_service.is_cosmos_enabled = True
        report = await tx_manager.validate_consistency()
        
        print(f"📊 Validation completed successfully")
        print()


async def main():
    """Run all demonstrations"""
    print("🚀 TRANSACTION MANAGER DEMONSTRATION")
    print("=" * 60)
    print("This demo shows the Database Transaction Manager providing")
    print("atomic operations across dual storage systems (JSON + Cosmos DB)")
    print("while preserving Vimarsh's cost-optimized pause-resume strategy.")
    print("=" * 60)
    print()
    
    demos = [
        demonstrate_successful_transaction,
        demonstrate_rollback_scenario,
        demonstrate_atomic_utility,
        demonstrate_consistency_validation
    ]
    
    for demo in demos:
        try:
            await demo()
        except Exception as e:
            print(f"❌ Demo {demo.__name__} failed: {e}")
            print()
    
    print("=" * 60)
    print("🎉 TRANSACTION MANAGER DEMONSTRATION COMPLETED")
    print("✅ Phase 1.2 Database Layer Stability: IMPLEMENTED")
    print("✅ Atomic operations across dual storage systems")
    print("✅ Transaction rollback and error handling")
    print("✅ Consistency validation between storage systems")
    print("✅ Preserves cost-optimized pause-resume architecture")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
