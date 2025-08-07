#!/usr/bin/env python3
"""
Test script for multi-personality LLM service refactoring
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from services.llm_service import LLMService as EnhancedSimpleLLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_multi_personality_responses():
    """Test responses from different personalities"""
    
    # Initialize LLM service
    llm_service = EnhancedSimpleLLMService()
    
    # Test query
    test_query = "What is the meaning of life?"
    
    # Test personalities
    personalities = ["krishna", "einstein", "lincoln", "marcus_aurelius"]
    
    print("🧪 Testing Multi-Personality LLM Service")
    print("=" * 50)
    
    for personality_id in personalities:
        print(f"\n🎭 Testing {personality_id.upper()} personality:")
        print("-" * 30)
        
        try:
            # Generate response
            response = await llm_service.generate_personality_response(
                query=test_query,
                context="general",
                personality_id=personality_id
            )
            
            print(f"✅ Response: {response.content[:200]}...")
            print(f"📚 Citations: {response.citations}")
            print(f"🎯 Confidence: {response.confidence}")
            print(f"⚡ Response Time: {response.response_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Error testing {personality_id}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Multi-personality testing complete!")

async def test_error_handling():
    """Test error handling with different personalities"""
    
    llm_service = EnhancedSimpleLLMService()
    
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    # Test with invalid personality
    try:
        response = await llm_service.generate_personality_response(
            query="Test query",
            context="general",
            personality_id="invalid_personality"
        )
        print(f"✅ Invalid personality handled: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ Error with invalid personality: {e}")
    
    # Test without personality_id
    try:
        response = await llm_service.generate_personality_response(
            query="Test query",
            context="general",
            personality_id=None
        )
        print(f"❌ Should have failed without personality_id")
    except Exception as e:
        print(f"✅ Correctly rejected missing personality_id: {e}")

if __name__ == "__main__":
    asyncio.run(test_multi_personality_responses())
    asyncio.run(test_error_handling())