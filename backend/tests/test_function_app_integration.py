#!/usr/bin/env python3
"""
Test script for function_app integration with multi-personality LLM service
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

async def test_function_app_integration():
    """Test the function_app integration with multi-personality support"""
    
    # Initialize LLM service (same way function_app does)
    llm_service = EnhancedSimpleLLMService()
    
    print("🧪 Testing Function App Integration")
    print("=" * 50)
    
    # Test the get_spiritual_guidance method (used by function_app)
    personalities = ["krishna", "einstein", "lincoln", "marcus_aurelius"]
    test_query = "How can I find inner peace?"
    
    for personality_id in personalities:
        print(f"\n🎭 Testing {personality_id.upper()} via get_spiritual_guidance:")
        print("-" * 40)
        
        try:
            # This is how function_app calls it
            response = await llm_service.generate_personality_response(
                query=test_query,
                context="guidance",
                personality_id=personality_id
            )
            
            print(f"✅ Response: {response.content[:150]}...")
            print(f"📚 Citations: {response.citations}")
            print(f"🎯 Confidence: {response.confidence}")
            
        except Exception as e:
            print(f"❌ Error testing {personality_id}: {e}")
    
    # Test error handling (no personality_id)
    print(f"\n🧪 Testing Error Handling (no personality_id):")
    print("-" * 40)
    
    try:
        response = await llm_service.generate_personality_response(
            query=test_query,
            context="guidance"
            # No personality_id provided
        )
        print(f"❌ Should have failed without personality_id")
    except Exception as e:
        print(f"✅ Correctly rejected missing personality_id: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Function App integration testing complete!")

if __name__ == "__main__":
    asyncio.run(test_function_app_integration())