"""
Test token tracker integration with transaction manager
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

# Mock the database availability before importing
os.environ['MOCK_DATABASE_AVAILABLE'] = 'true'

from core.token_tracker import TokenUsageTracker
from services.database_service import DatabaseService


async def test_token_tracker_atomic_operations():
    """Test token tracker with atomic operations"""
    print("🔄 Testing TokenUsageTracker with atomic operations...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize database service
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.spiritual_texts_path = os.path.join(temp_dir, 'spiritual-texts.json')
        db_service.conversations_path = os.path.join(temp_dir, 'conversations.json')
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        # Initialize token tracker
        tracker = TokenUsageTracker()
        
        try:
            # Record multiple usage events
            usage1 = tracker.record_usage(
                user_id="test_user_1",
                user_email="test1@vimarsh.com",
                session_id="session_001",
                model="gemini-2.5-flash",
                input_tokens=100,
                output_tokens=50,
                request_type="spiritual_guidance",
                response_quality="high",
                personality="krishna"
            )
            
            usage2 = tracker.record_usage(
                user_id="test_user_1",
                user_email="test1@vimarsh.com",
                session_id="session_001",
                model="gemini-2.5-flash",
                input_tokens=75,
                output_tokens=35,
                request_type="rag_query",
                response_quality="medium",
                personality="krishna"
            )
            
            usage3 = tracker.record_usage(
                user_id="test_user_2",
                user_email="test2@vimarsh.com",
                session_id="session_002",
                model="gemini-1.5-pro",
                input_tokens=200,
                output_tokens=100,
                request_type="spiritual_guidance",
                response_quality="high",
                personality="buddha"
            )
            
            print(f"✅ Recorded {len(tracker.usage_records)} usage events")
            
            # Allow async saves to complete
            await asyncio.sleep(0.5)
            
            # Verify in-memory statistics
            assert len(tracker.usage_records) == 3
            assert len(tracker.user_stats) == 2  # Two different users
            
            # Check user stats
            user1_stats = tracker.user_stats.get("test_user_1")
            assert user1_stats is not None
            assert user1_stats.total_requests == 2
            assert user1_stats.total_tokens == 260  # 150 + 110
            
            user2_stats = tracker.user_stats.get("test_user_2")
            assert user2_stats is not None
            assert user2_stats.total_requests == 1
            assert user2_stats.total_tokens == 300
            
            print(f"✅ User statistics computed correctly")
            print(f"   User 1: {user1_stats.total_requests} requests, {user1_stats.total_tokens} tokens")
            print(f"   User 2: {user2_stats.total_requests} requests, {user2_stats.total_tokens} tokens")
            
            return True
            
        except Exception as e:
            print(f"❌ Token tracker test failed: {e}")
            return False


async def test_concurrent_token_operations():
    """Test concurrent token operations for race conditions"""
    print("\n🔄 Testing concurrent token operations...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize components
        db_service = DatabaseService()
        db_service.storage_path = temp_dir
        db_service.is_cosmos_enabled = False
        db_service._init_local_storage()
        
        tracker = TokenUsageTracker()
        
        async def record_usage_batch(user_id: str, session_id: str, batch_size: int):
            """Record a batch of usage events"""
            for i in range(batch_size):
                tracker.record_usage(
                    user_id=user_id,
                    user_email=f"{user_id}@vimarsh.com",
                    session_id=session_id,
                    model="gemini-2.5-flash",
                    input_tokens=50 + i,
                    output_tokens=25 + i,
                    request_type="spiritual_guidance",
                    response_quality="high",
                    personality="krishna"
                )
        
        try:
            # Run concurrent operations
            await asyncio.gather(
                record_usage_batch("concurrent_user_1", "session_1", 5),
                record_usage_batch("concurrent_user_2", "session_2", 5),
                record_usage_batch("concurrent_user_3", "session_3", 5)
            )
            
            print(f"✅ Recorded {len(tracker.usage_records)} concurrent usage events")
            
            # Allow async saves to complete
            await asyncio.sleep(1.0)
            
            # Verify no data corruption
            assert len(tracker.usage_records) == 15  # 3 users × 5 events each
            assert len(tracker.user_stats) == 3     # 3 different users
            
            # Verify each user has correct stats
            for user_id in ["concurrent_user_1", "concurrent_user_2", "concurrent_user_3"]:
                user_stats = tracker.user_stats.get(user_id)
                assert user_stats is not None
                assert user_stats.total_requests == 5
                print(f"   {user_id}: {user_stats.total_requests} requests, {user_stats.total_tokens} tokens")
            
            print("✅ Concurrent operations completed without data corruption")
            return True
            
        except Exception as e:
            print(f"❌ Concurrent operations test failed: {e}")
            return False


async def main():
    """Run all token tracker integration tests"""
    print("🚀 Starting Token Tracker Integration Tests")
    print("=" * 60)
    
    tests = [
        test_token_tracker_atomic_operations,
        test_concurrent_token_operations
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
        print("🎉 All token tracker integration tests PASSED!")
        return 0
    else:
        print("❌ Some token tracker integration tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
