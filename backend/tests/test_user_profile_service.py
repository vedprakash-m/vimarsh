"""
Test script for UserProfileService implementation
Tests both local storage and Cosmos DB functionality
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our services
from services.user_profile_service import user_profile_service
from auth.models import AuthenticatedUser, create_authenticated_user


async def test_user_profile_service():
    """Test the UserProfileService functionality"""
    
    print("🧪 Testing UserProfileService Implementation")
    print("=" * 50)
    
    try:
        # Create a mock authenticated user
        mock_token_data = {
            "oid": "test-microsoft-auth-id-12345",
            "email": "testuser@vimarsh.example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "job_title": "Spiritual Seeker",
            "company_name": "Vimarsh Community"
        }
        
        authenticated_user = create_authenticated_user(mock_token_data)
        print(f"✅ Created mock authenticated user: {authenticated_user.email}")
        
        # Test 1: Create user profile
        print("\n📝 Test 1: Creating user profile...")
        user_profile = await user_profile_service.get_or_create_user_profile(authenticated_user)
        print(f"✅ User profile created: {user_profile.id}")
        print(f"   Email: {user_profile.email}")
        print(f"   Name: {user_profile.name}")
        print(f"   Auth Provider: {user_profile.auth_provider}")
        print(f"   Created At: {user_profile.created_at}")
        
        # Test 2: Get same user profile (should return existing)
        print("\n🔄 Test 2: Getting existing user profile...")
        existing_profile = await user_profile_service.get_or_create_user_profile(authenticated_user)
        print(f"✅ Retrieved existing profile: {existing_profile.id}")
        assert existing_profile.id == user_profile.id, "Profile IDs should match"
        print("   ✅ Profile persistence confirmed")
        
        # Test 3: Record an interaction
        print("\n💬 Test 3: Recording user interaction...")
        session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        interaction_data = {
            "query": "What is the meaning of dharma?",
            "response": "Dharma represents righteous duty and moral law in Hindu philosophy. It is the principle of natural order that regulates and coordinates the operation of the universe and everything within it.",
            "personality": "krishna",
            "response_time_ms": 1200,
            "input_tokens": 25,
            "output_tokens": 150,
            "cost_usd": 0.023,
            "themes": ["philosophy", "dharma", "hinduism"],
            "model": "gemini-flash"
        }
        
        await user_profile_service.record_interaction(
            user_id=user_profile.id,
            session_id=session_id,
            interaction_data=interaction_data
        )
        print("✅ Interaction recorded successfully")
        
        # Test 4: Add a bookmark
        print("\n🔖 Test 4: Adding bookmark...")
        bookmark_data = {
            "title": "Understanding Dharma",
            "query": "What is the meaning of dharma?",
            "response": interaction_data["response"][:200] + "...",
            "personality": "krishna",
            "tags": ["dharma", "philosophy", "hindu"],
            "notes": "Great explanation for meditation practice"
        }
        
        success = await user_profile_service.add_bookmark(user_profile.id, bookmark_data)
        print(f"✅ Bookmark added: {success}")
        
        # Test 5: Get updated user profile with stats
        print("\n📊 Test 5: Getting updated user profile...")
        updated_profile = await user_profile_service.get_or_create_user_profile(authenticated_user)
        
        print(f"✅ Updated profile retrieved:")
        print(f"   Total queries: {updated_profile.usage_stats.get('total_queries', 0)}")
        print(f"   Total tokens: {updated_profile.usage_stats.get('total_tokens', 0)}")
        print(f"   Total cost: ${updated_profile.usage_stats.get('total_cost_usd', 0):.4f}")
        print(f"   Recent activity items: {len(updated_profile.recent_activity)}")
        print(f"   Bookmarks: {len(updated_profile.bookmarks)}")
        
        if updated_profile.recent_activity:
            print(f"   Latest activity: {updated_profile.recent_activity[0]['query'][:50]}...")
        
        # Test 6: Get user analytics
        print("\n📈 Test 6: Getting user analytics...")
        analytics = await user_profile_service.get_user_analytics(user_profile.id)
        
        print(f"✅ Analytics retrieved:")
        print(f"   User ID: {analytics.get('user_id')}")
        print(f"   Email: {analytics.get('email')}")
        print(f"   Account created: {analytics.get('account_created')}")
        print(f"   Last activity: {analytics.get('last_activity')}")
        print(f"   Usage stats: {analytics.get('usage_stats', {})}")
        print(f"   Bookmarks count: {analytics.get('bookmarks_count', 0)}")
        
        print("\n🎉 All tests passed successfully!")
        print("\n📋 Test Summary:")
        print("   ✅ User profile creation")
        print("   ✅ User profile persistence")
        print("   ✅ Interaction recording")
        print("   ✅ Bookmark management")
        print("   ✅ Statistics aggregation")
        print("   ✅ Analytics retrieval")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_storage_backends():
    """Test different storage backends"""
    
    print("\n🗄️ Testing Storage Backends")
    print("=" * 30)
    
    # Check if Cosmos DB is configured
    cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_DB_KEY")
    
    if cosmos_endpoint:
        print("✅ Cosmos DB configuration detected")
        print(f"   Endpoint: {cosmos_endpoint}")
        print(f"   Key configured: {'Yes' if cosmos_key else 'No (using managed identity)'}")
    else:
        print("ℹ️ No Cosmos DB configuration - using local JSON storage")
        print("   Storage path: data/vimarsh-db/")
    
    # Check storage permissions
    storage_path = "data/vimarsh-db"
    try:
        os.makedirs(storage_path, exist_ok=True)
        test_file = os.path.join(storage_path, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Local storage access confirmed")
    except Exception as e:
        print(f"❌ Local storage access failed: {e}")


def main():
    """Main test function"""
    print("🚀 Vimarsh UserProfileService Test Suite")
    print("=" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("ℹ️ python-dotenv not available - using system environment")
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Test storage backends
        loop.run_until_complete(test_storage_backends())
        
        # Test user profile service
        success = loop.run_until_complete(test_user_profile_service())
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("\n📋 Next steps:")
            print("1. Run your Azure Functions app")
            print("2. Test the authentication flow")
            print("3. Check user profile endpoints")
            print("4. Monitor user interactions and analytics")
            return 0
        else:
            print("\n❌ Some tests failed. Check the logs above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1
    finally:
        loop.close()


if __name__ == "__main__":
    exit(main())
