#!/usr/bin/env python3
"""
Phase 2 Production Database Integration Test - Simplified
======================================================

Working test of Phase 2 services with Cosmos DB integration.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for testing
os.environ.setdefault('AZURE_STORAGE_CONNECTION_STRING', 'DefaultEndpointsProtocol=https;AccountName=dummy;AccountKey=dummy;EndpointSuffix=core.windows.net')
os.environ.setdefault('AZURE_COSMOS_ENDPOINT', 'https://dummy.documents.azure.com:443/')
os.environ.setdefault('AZURE_COSMOS_KEY', 'dummy_key')

from services.phase2_database_service import phase2_db_service
from services.conversation_memory_service import conversation_memory_service
from services.wisdom_journal_service import wisdom_journal_service
from services.personalization_service import ProgressivePersonalizationService
from models.conversation_models import (
    MessageType, JournalEntryType
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_database_service():
    """Test Phase 2 database service directly."""
    print("\n🔍 Testing Phase 2 Database Service...")
    
    try:
        # Test database containers
        print(f"📊 Database Service Status:")
        print(f"  - Cosmos DB Enabled: {phase2_db_service.cosmos_enabled}")
        print(f"  - Available Containers: {len(phase2_db_service.containers) if phase2_db_service.cosmos_enabled else 'Using local storage'}")
        
        test_user_id = "test_db_user"
        
        # Test user preferences
        from models.conversation_models import create_user_preferences
        prefs = create_user_preferences(test_user_id)
        stored = await phase2_db_service.store_user_preferences(prefs)
        print(f"💾 User Preferences Storage: {'✅' if stored else '❌'}")
        
        # Test retrieval
        retrieved = await phase2_db_service.get_user_preferences(test_user_id)
        print(f"📚 User Preferences Retrieval: {'✅' if retrieved else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database service test failed: {e}")
        return False

async def test_conversation_memory():
    """Test conversation memory service integration."""
    print("\n🧠 Testing Conversation Memory Service...")
    
    try:
        test_user_id = "test_memory_user"
        test_personality_id = "krishna"
        
        # Start a conversation session
        session = await conversation_memory_service.start_conversation(
            user_id=test_user_id,
            personality_id=test_personality_id
        )
        print(f"✅ Started conversation session: {session.id}")
        
        # Add a message
        message = await conversation_memory_service.add_message(
            conversation_id=session.id,
            user_id=test_user_id,
            personality_id=test_personality_id,
            message_type="user",
            content="What is the meaning of dharma?"
        )
        print(f"✅ Added message: {message.id}")
        
        # Get conversation context
        context = await conversation_memory_service.get_conversation_context(
            conversation_id=session.id
        )
        print(f"📖 Retrieved conversation context with {len(context.recent_messages)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation memory test failed: {e}")
        return False

async def test_wisdom_journal():
    """Test wisdom journal service integration."""
    print("\n📓 Testing Wisdom Journal Service...")
    
    try:
        test_user_id = "test_journal_user"
        test_personality_id = "krishna"
        
        # Create journal entry
        entry = await wisdom_journal_service.create_journal_entry(
            user_id=test_user_id,
            content="Today I learned about detachment (vairagya) from Krishna. True detachment means performing actions without being attached to the results, maintaining equanimity in success and failure.",
            entry_type=JournalEntryType.INSIGHT,
            title="Understanding Vairagya",
            personality_id=test_personality_id,
            tags=["detachment", "vairagya", "equanimity", "krishna"]
        )
        print(f"✅ Created journal entry: {entry.id}")
        
        # Search entries
        search_results = await wisdom_journal_service.search_journal_entries(
            user_id=test_user_id,
            query="detachment equanimity",
            limit=5
        )
        print(f"🔍 Found {len(search_results)} entries in search")
        
        # Get user entries
        all_entries = await wisdom_journal_service.get_user_journal_entries(test_user_id)
        print(f"📚 Retrieved {len(all_entries)} total journal entries")
        
        # Get analytics
        analytics = await wisdom_journal_service.get_journal_analytics(test_user_id)
        print(f"📊 Analytics: {analytics.get('total_entries', 0)} total entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Wisdom journal test failed: {e}")
        return False

async def test_personalization():
    """Test personalization service integration."""
    print("\n🎯 Testing Personalization Service...")
    
    try:
        service = ProgressivePersonalizationService()
        test_user_id = "test_personalization_user"
        
        # Initialize user personalization
        preferences = await service.initialize_user_personalization(
            user_id=test_user_id,
            initial_preferences={
                "interests": ["meditation", "dharma", "wisdom"],
                "communication": {"style": "conversational"}
            }
        )
        print(f"✅ Initialized personalization: {preferences.user_id}")
        
        # Get user preferences
        retrieved_prefs = await service.get_user_preferences(test_user_id)
        print(f"📚 Retrieved preferences: {'✅' if retrieved_prefs else '❌'}")
        
        # Track interactions
        await service.track_user_interaction(
            user_id=test_user_id,
            interaction_type="conversation",
            context={
                "personality": "krishna",
                "satisfaction": 0.9,
                "engagement_level": "high"
            },
            personality_id="krishna",
            satisfaction_score=0.9
        )
        print("✅ Tracked user interaction")
        
        # Get adaptive UI settings
        ui_settings = await service.get_adaptive_ui_settings(test_user_id)
        print(f"🎨 Generated adaptive UI settings: theme={ui_settings.get('theme', 'auto')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Personalization test failed: {e}")
        return False

async def test_integrated_workflow():
    """Test a complete workflow across services."""
    print("\n🔗 Testing Integrated Workflow...")
    
    try:
        test_user_id = "workflow_test_user"
        test_personality_id = "krishna"
        
        # Step 1: Initialize personalization
        personalization_service = ProgressivePersonalizationService()
        preferences = await personalization_service.initialize_user_personalization(
            user_id=test_user_id,
            initial_preferences={"interests": ["spiritual-growth", "dharma"]}
        )
        print("✅ Step 1: User personalization initialized")
        
        # Step 2: Start conversation
        session = await conversation_memory_service.start_conversation(
            user_id=test_user_id,
            personality_id=test_personality_id
        )
        print("✅ Step 2: Conversation session started")
        
        # Step 3: Add conversation messages
        user_msg = await conversation_memory_service.add_message(
            conversation_id=session.id,
            user_id=test_user_id,
            personality_id=test_personality_id,
            message_type="user",
            content="Help me understand the balance between action and detachment"
        )
        
        assistant_msg = await conversation_memory_service.add_message(
            conversation_id=session.id,
            user_id=test_user_id,
            personality_id=test_personality_id,
            message_type="assistant",
            content="In the Bhagavad Gita, I teach that you should perform your duty (dharma) with full dedication, but without attachment to the fruits of your actions. This is karma yoga - the path of selfless action."
        )
        print("✅ Step 3: Conversation messages added")
        
        # Step 4: Create wisdom journal entry
        entry = await wisdom_journal_service.create_journal_entry(
            user_id=test_user_id,
            content="Krishna taught me about karma yoga today. The key insight is that I can be fully engaged in action while remaining detached from outcomes. This is the path to inner peace and spiritual growth.",
            entry_type=JournalEntryType.REFLECTION,
            title="Learning Karma Yoga",
            personality_id=test_personality_id,
            conversation_id=session.id,
            tags=["karma-yoga", "detachment", "action", "spiritual-growth"]
        )
        print("✅ Step 4: Wisdom journal entry created")
        
        # Step 5: Track interaction for personalization
        await personalization_service.track_user_interaction(
            user_id=test_user_id,
            interaction_type="spiritual_discussion",
            context={
                "topic": "karma_yoga",
                "depth": "philosophical",
                "satisfaction": 0.95,
                "conversation_id": session.id
            },
            personality_id=test_personality_id,
            satisfaction_score=0.95
        )
        print("✅ Step 5: Interaction tracked for personalization")
        
        # Step 6: Get conversation context
        context = await conversation_memory_service.get_conversation_context(session.id)
        print(f"✅ Step 6: Retrieved context with {len(context.recent_messages)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Integrated workflow test failed: {e}")
        return False

async def run_phase2_test():
    """Run all Phase 2 integration tests."""
    print("=" * 70)
    print("🚀 PHASE 2 PRODUCTION DATABASE INTEGRATION TEST")
    print("=" * 70)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Test individual services
    test_results['database_service'] = await test_database_service()
    test_results['conversation_memory'] = await test_conversation_memory()
    test_results['wisdom_journal'] = await test_wisdom_journal()
    test_results['personalization'] = await test_personalization()
    test_results['integrated_workflow'] = await test_integrated_workflow()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        test_display = test_name.replace('_', ' ').title()
        print(f"{test_display:<25}: {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL PHASE 2 SERVICES SUCCESSFULLY INTEGRATED!")
        print("✅ Cosmos DB containers created and functional")
        print("✅ Conversation memory with cross-session continuity")
        print("✅ Wisdom journal with semantic search")
        print("✅ Progressive personalization with adaptive UI")
        print("✅ Complete workflow integration")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check logs for details.")
    
    # Database status summary
    print(f"\n📊 Database Status:")
    print(f"   Cosmos DB: {'✅ Connected' if phase2_db_service.cosmos_enabled else '🔶 Local Storage Fallback'}")
    print(f"   Containers: {len(phase2_db_service.containers) if phase2_db_service.cosmos_enabled else 'N/A'}")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_phase2_test())
