#!/usr/bin/env python3
"""
Test script for frontend integration with multi-personality backend
"""

import asyncio
import logging
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from services.personality_service import personality_service, PersonalitySearchFilter
from services.llm_service import EnhancedLLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_personalities_api():
    """Test the personalities API that frontend uses"""
    
    print("🧪 Testing Personalities API for Frontend Integration")
    print("=" * 60)
    
    # Test 1: Get all active personalities
    print("\n📋 Test 1: Get Active Personalities")
    print("-" * 40)
    
    try:
        filters = PersonalitySearchFilter(is_active=True)
        personalities = await personality_service.search_personalities(filters, limit=50)
        
        print(f"✅ Found {len(personalities)} active personalities:")
        for personality in personalities:
            print(f"   - {personality.display_name} ({personality.domain.value}) - Score: {personality.quality_score}")
        
        # Convert to API format (like function_app.py does)
        personality_data = []
        for personality in personalities:
            personality_data.append({
                "id": personality.id,
                "name": personality.name,
                "display_name": personality.display_name,
                "domain": personality.domain.value,
                "time_period": personality.time_period,
                "description": personality.description,
                "expertise_areas": personality.expertise_areas,
                "cultural_context": personality.cultural_context,
                "quality_score": personality.quality_score,
                "usage_count": personality.usage_count,
                "is_active": personality.is_active,
                "tags": personality.tags
            })
        
        print(f"\n📄 API Response Format Sample:")
        if personality_data:
            sample = personality_data[0]
            print(json.dumps(sample, indent=2))
            
    except Exception as e:
        print(f"❌ Error getting personalities: {e}")
    
    # Test 2: Test domain filtering
    print("\n🔍 Test 2: Domain Filtering")
    print("-" * 40)
    
    domains = ['spiritual', 'scientific', 'historical', 'philosophical']
    for domain in domains:
        try:
            from services.personality_service import PersonalityDomain
            domain_enum = PersonalityDomain(domain)
            filters = PersonalitySearchFilter(domain=domain_enum, is_active=True)
            personalities = await personality_service.search_personalities(filters)
            print(f"   {domain.capitalize()}: {len(personalities)} personalities")
        except Exception as e:
            print(f"   {domain.capitalize()}: Error - {e}")

async def test_chat_integration():
    """Test the chat integration with different personalities"""
    
    print("\n🧪 Testing Chat Integration")
    print("=" * 60)
    
    llm_service = EnhancedLLMService()
    test_query = "What is the meaning of life?"
    
    # Get available personalities
    filters = PersonalitySearchFilter(is_active=True)
    personalities = await personality_service.search_personalities(filters, limit=4)
    
    for personality in personalities[:4]:  # Test first 4
        print(f"\n🎭 Testing chat with {personality.display_name}:")
        print("-" * 40)
        
        try:
            # This simulates what the frontend does
            response = await llm_service.get_spiritual_guidance(
                query=test_query,
                context="general",
                personality_id=personality.id
            )
            
            print(f"✅ Response: {response.content[:100]}...")
            print(f"📚 Citations: {response.citations}")
            print(f"🎯 Confidence: {response.confidence}")
            
        except Exception as e:
            print(f"❌ Error with {personality.display_name}: {e}")

async def test_personality_switching():
    """Test personality switching scenario"""
    
    print("\n🔄 Testing Personality Switching")
    print("=" * 60)
    
    llm_service = EnhancedLLMService()
    test_query = "How should I handle difficult situations?"
    
    # Get different personalities
    filters = PersonalitySearchFilter(is_active=True)
    personalities = await personality_service.search_personalities(filters, limit=4)
    
    print("Simulating user switching between personalities in same session:")
    
    for i, personality in enumerate(personalities[:3]):
        print(f"\n🔄 Switch {i+1}: User selects {personality.display_name}")
        print("-" * 30)
        
        try:
            response = await llm_service.get_spiritual_guidance(
                query=test_query,
                context="guidance",
                personality_id=personality.id
            )
            
            print(f"Response: {response.content[:150]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_personalities_api())
    asyncio.run(test_chat_integration())
    asyncio.run(test_personality_switching())