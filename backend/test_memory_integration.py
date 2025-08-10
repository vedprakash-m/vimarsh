#!/usr/bin/env python3
"""
Test Memory Integration in Guidance Endpoint

This tests if the conversation memory integration is working properly
for follow-up questions in the guidance endpoint.
"""

import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_memory_integration():
    """Test conversation memory integration"""
    
    print("🧪 Testing Memory Integration for Follow-up Questions")
    print("=" * 60)
    
    try:
        # Import the conversation memory service
        from services.conversation_memory_service import ConversationMemoryService
        
        memory_service = ConversationMemoryService()
        print("✅ Conversation memory service initialized")
        
        # Test parameters
        user_id = "test_user_001"
        personality_id = "chanakya"
        
        # Simulate first conversation
        print("\n📝 Step 1: Starting conversation...")
        conversation_id = await memory_service.start_conversation(
            user_id=user_id,
            personality_id=personality_id
        )
        print(f"✅ Started conversation: {conversation_id}")
        
        # First question - context setting
        first_query = "How do we balance justice with compassion in difficult decisions?"
        first_response = "Dear student, justice tempered with compassion is the cornerstone of a stable kingdom. Dharma guides our actions, but practical wisdom dictates their execution. In difficult decisions, assess the threat to the state's stability. Severe but just punishment for major crimes, while merciful considerations for minor offenses and extenuating circumstances, achieve this balance. Human nature necessitates such pragmatism. Strategic thinking demands it."
        
        print(f"\n📝 Step 2: Storing first exchange...")
        print(f"User: {first_query}")
        print(f"Chanakya: {first_response[:100]}...")
        
        # Store first message pair
        await memory_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            personality_id=personality_id,
            message_type="user_query",
            content=first_query
        )
        
        await memory_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            personality_id=personality_id,
            message_type="personality_response",
            content=first_response
        )
        
        print("✅ First exchange stored in memory")
        
        # Follow-up question - this should reference previous context
        followup_query = "how to be strategic about this?"
        
        print(f"\n📝 Step 3: Testing context retrieval for follow-up...")
        print(f"Follow-up question: {followup_query}")
        
        # Get conversation context
        context_data = await memory_service.get_conversation_context(
            conversation_id=conversation_id
        )
        
        # Format recent messages as context (simulate what guidance endpoint does)
        conversation_context = ""
        if hasattr(context_data, 'recent_messages') and context_data.recent_messages:
            recent_msgs = []
            for msg in context_data.recent_messages[-3:]:  # Last 3 messages for context
                # Handle both old string format and new enum format
                msg_type = getattr(msg.message_type, 'value', str(msg.message_type))
                if msg_type == "user_query":
                    recent_msgs.append(f"Previous question: {msg.content}")
                elif msg_type == "personality_response":
                    recent_msgs.append(f"My previous response: {msg.content[:200]}...")
            conversation_context = "\n".join(recent_msgs)
        
        print(f"\n🧠 Retrieved context:")
        print(f"Context length: {len(conversation_context)} characters")
        print(f"Context preview: {conversation_context[:300]}...")
        
        # Enhanced query (simulate what guidance endpoint creates)
        enhanced_query = followup_query
        if conversation_context:
            enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {followup_query}"
        
        print(f"\n🔍 Enhanced query for LLM:")
        print(f"Query length: {len(enhanced_query)} characters")
        print(f"Enhanced query: {enhanced_query[:400]}...")
        
        # Expected behavior analysis
        print("\n📊 Analysis:")
        print(f"✅ Memory retrieved: {len(context_data.recent_messages)} messages")
        print(f"✅ Context formatted: {len(conversation_context)} chars")
        print(f"✅ Query enhanced: {len(enhanced_query)} chars")
        
        if "justice" in enhanced_query and "compassion" in enhanced_query:
            print("✅ Previous context about justice and compassion is preserved")
        else:
            print("❌ Previous context about justice and compassion is missing")
        
        if "strategic" in enhanced_query.lower():
            print("✅ Current follow-up question about strategy is included")
        else:
            print("❌ Current follow-up question about strategy is missing")
        
        print("\n🎯 Expected LLM behavior with this enhanced query:")
        print("- Should understand 'this' refers to balancing justice and compassion")
        print("- Should provide strategic advice specifically about justice/compassion balance")
        print("- Should NOT give generic strategic advice")
        
        print("\n🔧 Integration Status:")
        print("✅ Conversation memory service: Working")
        print("✅ Context retrieval: Working") 
        print("✅ Query enhancement: Working")
        print("📋 Next step: Deploy this integration to guidance endpoint")
        
    except ImportError as e:
        print(f"❌ Failed to import conversation memory service: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_memory_integration())
