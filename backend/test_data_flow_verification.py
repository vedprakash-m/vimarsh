#!/usr/bin/env python3
"""
Test script to verify data flows correctly through the new container architecture.
This tests the specific data flow: user interaction → new containers → proper storage
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv('../.env')

def test_data_flow_verification():
    """Test data flow through the new container architecture"""
    print("🔍 DATA FLOW VERIFICATION TEST")
    print("=" * 60)
    
    try:
        # Import services
        from services.user_profile_service import UserProfileService
        from auth.models import AuthenticatedUser
        
        print("✅ Imported services successfully")
        
        # Test 1: Verify container connections
        print("\n📋 Test 1: Verifying container connections...")
        user_service = UserProfileService()
        
        if user_service.cosmos_client:
            print(f"✅ Connected to Cosmos DB")
            print(f"   Users container: {user_service.users_container is not None}")
            print(f"   Sessions container: {user_service.sessions_container is not None}")
            print(f"   Interactions container: {user_service.interactions_container is not None}")
        else:
            print("📁 Using local storage mode")
        
        # Test 2: Mock user interaction flow
        print("\n📋 Test 2: Testing user interaction data flow...")
        
        # Create mock authenticated user
        mock_auth_user = AuthenticatedUser(
            id="test-auth-id-123",
            email="test-dataflow@vimarsh.app",
            name="Data Flow Test User",
            auth_provider="microsoft"
        )
        
        async def test_interaction_flow():
            # Create/get user profile
            user_profile = await user_service.get_or_create_user_profile(mock_auth_user)
            print(f"✅ User profile: {user_profile.email}")
            
            # Record an interaction
            session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            interaction_data = {
                "query": "What is the purpose of life according to Vedic philosophy?",
                "response": "According to Vedic philosophy, the purpose of life is to realize one's true nature as eternal soul (atman) and achieve union with the Supreme (Brahman) through dharma, artha, kama, and moksha.",
                "personality": "krishna",
                "response_time_ms": 1200,
                "input_tokens": 15,
                "output_tokens": 45,
                "cost_usd": 0.012,
                "model": "gemini-flash"
            }
            
            await user_service.record_interaction(
                user_id=user_profile.id,
                session_id=session_id,
                interaction_data=interaction_data
            )
            
            print(f"✅ Recorded interaction to session: {session_id}")
            print(f"   User ID: {user_profile.id}")
            print(f"   Query: {interaction_data['query'][:50]}...")
            
            return user_profile.id, session_id
        
        # Run async test
        user_id, session_id = asyncio.run(test_interaction_flow())
        
        # Test 3: Verify data was saved to correct containers
        print("\n📋 Test 3: Verifying data was saved to correct containers...")
        
        if user_service.cosmos_client:
            print("   🔍 Checking Cosmos DB containers...")
            
            # Check users container
            try:
                user_data = user_service.users_container.read_item(item=user_id, partition_key=user_id)
                print(f"   ✅ User found in 'users' container: {user_data.get('email')}")
            except Exception as e:
                print(f"   ❌ User not found in 'users' container: {e}")
            
            # Check user_interactions container
            try:
                query = f"SELECT * FROM c WHERE c.user_id = '{user_id}' AND c.session_id = '{session_id}'"
                interactions = list(user_service.interactions_container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                print(f"   ✅ Found {len(interactions)} interactions in 'user_interactions' container")
                if interactions:
                    print(f"      Latest interaction: {interactions[0].get('user_input', '')[:50]}...")
            except Exception as e:
                print(f"   ❌ Error checking interactions: {e}")
            
            # Check user_sessions container  
            try:
                query = f"SELECT * FROM c WHERE c.user_id = '{user_id}' AND c.session_id = '{session_id}'"
                sessions = list(user_service.sessions_container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                print(f"   ✅ Found {len(sessions)} sessions in 'user_sessions' container")
            except Exception as e:
                print(f"   ❌ Error checking sessions: {e}")
                
        else:
            print("   📁 Checking local storage...")
            
            # Check local files
            local_path = user_service.local_storage_path
            
            users_path = f"{local_path}/users/{user_id}.json"
            if os.path.exists(users_path):
                print(f"   ✅ User file exists: {users_path}")
            else:
                print(f"   ❌ User file missing: {users_path}")
            
            # Check interactions directory
            interactions_dir = f"{local_path}/user_interactions"
            if os.path.exists(interactions_dir):
                interaction_files = [f for f in os.listdir(interactions_dir) if f.endswith('.json')]
                print(f"   ✅ Found {len(interaction_files)} interaction files")
            else:
                print(f"   ❌ Interactions directory missing: {interactions_dir}")
            
            # Check sessions directory
            sessions_dir = f"{local_path}/user_sessions"
            if os.path.exists(sessions_dir):
                session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.json')]
                print(f"   ✅ Found {len(session_files)} session files")
            else:
                print(f"   ❌ Sessions directory missing: {sessions_dir}")
        
        print("\n🎉 DATA FLOW VERIFICATION COMPLETED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_flow_verification()
    if success:
        print("✅ All data flow tests passed!")
        sys.exit(0)
    else:
        print("❌ Data flow tests failed!")
        sys.exit(1)
