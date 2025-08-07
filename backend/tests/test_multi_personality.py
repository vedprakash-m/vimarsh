#!/usr/bin/env python3
"""
Test multi-personality functionality
"""

import asyncio
import logging
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.llm_service import LLMService as EnhancedSimpleLLMService
from services.personality_service import personality_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_personalities():
    """Test different personalities"""
    
    # Initialize LLM service
    llm_service = EnhancedSimpleLLMService()
    
    # Test query
    query = "What is the meaning of life?"
    
    # Test different personalities
    personalities = ['krishna', 'einstein', 'marcus_aurelius']
    
    for personality_id in personalities:
        logger.info(f"\n🧠 Testing {personality_id}...")
        
        try:
            # Get personality info
            personality = await personality_service.get_personality(personality_id)
            if personality:
                logger.info(f"✅ Found personality: {personality['name']} ({personality['domain']})")
            else:
                logger.warning(f"❌ Personality {personality_id} not found")
                continue
            
            # Generate response
            response = await llm_service.generate_personality_response(
                query=query,
                context="philosophy",
                personality_id=personality_id
            )
            
            logger.info(f"📝 Response from {personality['name']}:")
            logger.info(f"   {response.content[:200]}...")
            logger.info(f"   Confidence: {response.confidence}")
            logger.info(f"   Safety passed: {response.safety_passed}")
            
        except Exception as e:
            logger.error(f"❌ Error testing {personality_id}: {e}")

if __name__ == "__main__":
    asyncio.run(test_personalities())