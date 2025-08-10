#!/usr/bin/env python3
"""
Debug Memory Storage and Retrieval

Debug the exact storage and retrieval process to see what's going wrong.
"""

import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_memory_storage():
    """Debug conversation memory storage and retrieval"""
    
    print("🐛 Debugging Memory Storage and Retrieval")
    print("=" * 60)
    
    try:
        # Import services
        from services.phase2_database_service import Phase2DatabaseService
        from models.conversation_models import ConversationMessage, MessageType
        
        # Initialize database service
        db_service = Phase2DatabaseService()
        print("✅ Database service initialized")
        
        # Test parameters
        user_id = "debug_user"
        personality_id = "chanakya"
        
        # Create a test message
        test_message = ConversationMessage(
            id="debug_msg_001",
            session_id="debug_conv_001",  # Use session_id instead of conversation_id
            user_id=user_id,
            personality_id=personality_id,
            message_type=MessageType.USER_QUERY,  # Use enum instead of string
            content="This is a debug test message",
            timestamp=datetime.now()
        )
        
        print("\n📝 Step 1: Storing test message...")
        print(f"Message data: {json.dumps(test_message.to_dict(), indent=2, default=str)}")
        
        # Store the message
        success = await db_service.store_conversation_message(test_message)
        print(f"✅ Storage result: {success}")
        
        print("\n📝 Step 2: Retrieving messages...")
        print(f"Querying for user_id='{user_id}', personality_id='{personality_id}'")
        
        # Get recent messages
        messages = await db_service.get_recent_messages(user_id, personality_id, limit=5)
        print(f"Retrieved {len(messages)} messages")
        
        if messages:
            for i, msg in enumerate(messages):
                print(f"Message {i+1}:")
                print(f"  - ID: {msg.id}")
                print(f"  - Type: {msg.message_type}")
                print(f"  - Content: {msg.content[:50]}...")
                print(f"  - User: {msg.user_id}")
                print(f"  - Personality: {msg.personality_id}")
        else:
            print("❌ No messages retrieved!")
            
            # Debug: Check what's actually in storage
            print("\n🔍 Debug: Checking raw storage...")
            with open('/Users/ved/Apps/vimarsh/backend/data/phase2-storage/conversation_messages.json', 'r') as f:
                raw_data = json.load(f)
            
            print(f"Total messages in storage: {len(raw_data)}")
            
            # Filter manually to see what matches
            matching = [
                item for item in raw_data 
                if (item.get('user_id') == user_id and 
                    item.get('personality_id') == personality_id)
            ]
            print(f"Messages matching filter: {len(matching)}")
            
            if matching:
                print("Matching messages:")
                for item in matching:
                    print(f"  - {item.get('id')}: {item.get('message_type')} from {item.get('user_id')}")
            else:
                print("No messages match the filter!")
                print(f"Looking for user_id='{user_id}' and personality_id='{personality_id}'")
                print("Available user_ids:", set(item.get('user_id') for item in raw_data))
                print("Available personality_ids:", set(item.get('personality_id') for item in raw_data))
        
        print("\n🎯 Summary:")
        print(f"✅ Message storage: {'Working' if success else 'Failed'}")
        print(f"{'✅' if messages else '❌'} Message retrieval: {'Working' if messages else 'Failed'}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_memory_storage())
