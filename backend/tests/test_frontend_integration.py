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

from services.personality_service import PersonalityService
from models.personality_models import get_personality_list, get_personalities_by_domain
from services.llm_service import LLMService as EnhancedSimpleLLMService

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
        filters = {}
        personalities = get_personality_list()
        
        print(f"✅ Found {len(personalities)} active personalities:")
        for personality in personalities:
            print(f"   - {personality['name']} ({personality['domain']}) - Score: {personality}")
        
        # Convert to API format (like function_app.py does)
        personality_data = []
        for personality in personalities:
            personality_data.append({
                "id": personality['id'],
                "name": personality.name,
                "display_name": personality['name'],
                "domain": personality['domain'],
                "time_period": personality.time_period,
                "description": personality['description'],
                "expertise_areas": personality.expertise_areas,
                "cultural_context": personality.cultural_context,
                "quality_score": personality,
                "usage_count": personality,
                "is_active": personality,
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
            filters = {}
            personalities = get_personality_list()
            print(f"   {domain.capitalize()}: {len(personalities)} personalities")
        except Exception as e:
            print(f"   {domain.capitalize()}: Error - {e}")

async def test_chat_integration():
    """Test the chat integration with different personalities"""
    
    print("\n🧪 Testing Chat Integration")
    print("=" * 60)
    
    llm_service = EnhancedSimpleLLMService()
    test_query = "What is the meaning of life?"
    
    # Get available personalities
    filters = {}
    personalities = get_personality_list()
    
    for personality in personalities[:4]:  # Test first 4
        print(f"\n🎭 Testing chat with {personality['name']}:")
        print("-" * 40)
        
        try:
            # This simulates what the frontend does
            response = await llm_service.generate_personality_response(
                query=test_query,
                context="general",
                personality_id=personality['id']
            )
            
            print(f"✅ Response: {response.content[:100]}...")
            print(f"📚 Citations: {response.citations}")
            print(f"🎯 Confidence: {response.confidence}")
            
        except Exception as e:
            print(f"❌ Error with {personality['name']}: {e}")

async def test_personality_switching():
    """Test personality switching scenario"""
    
    print("\n🔄 Testing Personality Switching")
    print("=" * 60)
    
    llm_service = EnhancedSimpleLLMService()
    test_query = "How should I handle difficult situations?"
    
    # Get different personalities
    filters = {}
    personalities = get_personality_list()
    
    print("Simulating user switching between personalities in same session:")
    
    for i, personality in enumerate(personalities[:3]):
        print(f"\n🔄 Switch {i+1}: User selects {personality['name']}")
        print("-" * 30)
        
        try:
            response = await llm_service.generate_personality_response(
                query=test_query,
                context="guidance",
                personality_id=personality['id']
            )
            
            print(f"Response: {response.content[:150]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_personalities_api())
    asyncio.run(test_chat_integration())
    asyncio.run(test_personality_switching())