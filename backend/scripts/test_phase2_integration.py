#!/usr/bin/env python3
"""
Phase 2 Production Database Integration Test
==========================================

Comprehensive testing of all Phase 2 services with Cosmos DB integration.
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
    MessageType, JournalEntryType, create_conversation_message,
    create_wisdom_journal_entry
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_database_service():
    """Test Phase 2 database service directly."""
    print("\n🔍 Testing Phase 2 Database Service...")
    
    try:
        # Test database health
        health = await phase2_db_service.check_database_health()
        print(f"📊 Database Health: {health}")
        
        # Test conversation storage
        test_user_id = "integration_test_user"
        test_personality_id = "krishna"
        
        message = create_conversation_message(
            user_id=test_user_id,
            personality_id=test_personality_id,
            content="Testing database integration",
            message_type=MessageType.USER_MESSAGE
        )
        
        stored = await phase2_db_service.store_conversation_message(message)
        print(f"💾 Message Storage: {'✅' if stored else '❌'}")
        
        # Test message retrieval
        messages = await phase2_db_service.get_recent_messages(test_user_id, test_personality_id, limit=5)
        print(f"📚 Retrieved {len(messages)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Database service test failed: {e}")
        return False

async def test_conversation_memory():
    """Test conversation memory service integration."""
    print("\n🧠 Testing Conversation Memory Service...")
    
    try:
        test_user_id = "memory_test_user"
        test_personality_id = "krishna"
        
        # Store a message
        await conversation_memory_service.store_message(
            user_id=test_user_id,
            personality_id=test_personality_id,
            content="This is a test message for memory integration",
            message_type=MessageType.USER_MESSAGE
        )
        print("✅ Stored message in conversation memory")
        
        # Retrieve context
        context = await conversation_memory_service.get_conversation_context(
            user_id=test_user_id,
            personality_id=test_personality_id
        )
        print(f"📖 Retrieved conversation context: {len(context.get('recent_messages', []))} messages")
        
        # Get cross-session insights
        insights = await conversation_memory_service.get_cross_session_insights(
            user_id=test_user_id,
            personality_id=test_personality_id
        )
        print(f"💡 Generated {len(insights.get('recurring_themes', []))} cross-session insights")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation memory test failed: {e}")
        return False

async def test_wisdom_journal():
    """Test wisdom journal service integration."""
    print("\n📓 Testing Wisdom Journal Service...")
    
    try:
        test_user_id = "journal_test_user"
        test_personality_id = "krishna"
        
        # Create journal entry
        entry = await wisdom_journal_service.create_journal_entry(
            user_id=test_user_id,
            content="Today I learned about detachment and non-attachment in spiritual practice. Krishna's teachings in the Bhagavad Gita emphasize performing one's duty without attachment to results.",
            entry_type=JournalEntryType.INSIGHT,
            title="Understanding Detachment",
            personality_id=test_personality_id,
            tags=["detachment", "bhagavad-gita", "krishna", "duty"]
        )
        print(f"✅ Created journal entry: {entry.id}")
        
        # Search entries
        search_results = await wisdom_journal_service.search_journal_entries(
            user_id=test_user_id,
            query="detachment spiritual practice",
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
        test_user_id = "personalization_test_user"
        
        # Initialize user personalization
        preferences = await service.initialize_user_personalization(
            user_id=test_user_id,
            initial_preferences={
                "interests": ["meditation", "dharma", "wisdom"],
                "communication": {"style": "conversational"}
            }
        )
        print(f"✅ Initialized personalization: {preferences.user_id}")
        
        # Track interactions
        await service.track_user_interaction(
            user_id=test_user_id,
            interaction_type="conversation",
            context={
                "personality": "krishna",
                "satisfaction": 0.9,
                "engagement_level": "high",
                "response_time": 2.5
            },
            personality_id="krishna",
            satisfaction_score=0.9
        )
        print("✅ Tracked user interaction")
        
        # Get recommendations
        recommendations = await service.get_personalized_recommendations(
            user_id=test_user_id,
            context="spiritual_guidance",
            limit=5
        )
        print(f"🎯 Generated {len(recommendations)} personalized recommendations")
        
        # Get adaptive UI settings
        ui_settings = await service.get_adaptive_ui_settings(test_user_id)
        print(f"🎨 Generated adaptive UI settings: theme={ui_settings.get('theme', 'auto')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Personalization test failed: {e}")
        return False

async def test_cross_service_integration():
    """Test integration between different Phase 2 services."""
    print("\n🔗 Testing Cross-Service Integration...")
    
    try:
        test_user_id = "integration_user"
        test_personality_id = "krishna"
        
        # Step 1: Initialize personalization
        personalization_service = ProgressivePersonalizationService()
        preferences = await personalization_service.initialize_user_personalization(
            user_id=test_user_id,
            initial_preferences={"interests": ["wisdom", "dharma"]}
        )
        print("✅ Step 1: User personalization initialized")
        
        # Step 2: Store conversation messages
        await conversation_memory_service.store_message(
            user_id=test_user_id,
            personality_id=test_personality_id,
            content="I want to understand the concept of dharma better",
            message_type=MessageType.USER_MESSAGE
        )
        
        await conversation_memory_service.store_message(
            user_id=test_user_id,
            personality_id=test_personality_id,
            content="Dharma is your righteous duty, the path of moral and ethical living. It varies according to your stage of life, your role in society, and your personal circumstances.",
            message_type=MessageType.ASSISTANT_MESSAGE
        )
        print("✅ Step 2: Conversation messages stored")
        
        # Step 3: Create wisdom journal entry based on conversation
        entry = await wisdom_journal_service.create_journal_entry(
            user_id=test_user_id,
            content="Learning about dharma from Krishna. Dharma is not just duty, but righteous action aligned with cosmic order. It's personal yet universal.",
            entry_type=JournalEntryType.REFLECTION,
            personality_id=test_personality_id,
            tags=["dharma", "righteousness", "cosmic-order"]
        )
        print("✅ Step 3: Wisdom journal entry created")
        
        # Step 4: Track interaction for personalization
        await personalization_service.track_user_interaction(
            user_id=test_user_id,
            interaction_type="spiritual_discussion",
            context={
                "topic": "dharma",
                "depth": "philosophical",
                "satisfaction": 0.95
            },
            personality_id=test_personality_id,
            satisfaction_score=0.95
        )
        print("✅ Step 4: Interaction tracked for personalization")
        
        # Step 5: Get integrated recommendations
        recommendations = await personalization_service.get_personalized_recommendations(
            user_id=test_user_id,
            context="dharma_exploration",
            limit=3
        )
        print(f"✅ Step 5: Generated {len(recommendations)} integrated recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ Cross-service integration test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all Phase 2 integration tests."""
    print("=" * 60)
    print("🚀 PHASE 2 PRODUCTION DATABASE INTEGRATION TEST")
    print("=" * 60)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Test individual services
    test_results['database_service'] = await test_database_service()
    test_results['conversation_memory'] = await test_conversation_memory()
    test_results['wisdom_journal'] = await test_wisdom_journal()
    test_results['personalization'] = await test_personalization()
    test_results['cross_service_integration'] = await test_cross_service_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL PHASE 2 SERVICES SUCCESSFULLY INTEGRATED WITH PRODUCTION DATABASE!")
    else:
        print("⚠️ Some tests failed. Check logs for details.")
    
    print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
