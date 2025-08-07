#!/usr/bin/env python3
"""
Test script to verify Newton personality timeout fix
This tests the Priority 1 implementation from the plan
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.llm_service import LLMService as EnhancedSimpleLLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_newton_timeout_fix():
    """Test Newton personality with timeout and retry logic"""
    
    service = EnhancedSimpleLLMService()
    
    if not service.is_configured:
        print("❌ Service not configured - check API key")
        return False
    
    print("🧪 Testing Newton Personality Timeout Fix")
    print("=" * 50)
    
    # Get Newton personality configuration
    newton_config = service.personalities.get("newton")
    if newton_config:
        print(f"📊 Newton Configuration:")
        print(f"   Timeout: {newton_config.timeout_seconds}s")
        print(f"   Max Retries: {newton_config.max_retries}")
        print(f"   Max Characters: {newton_config.max_chars}")
        print()
    else:
        print("❌ Newton personality not found!")
        return False
    
    # Test queries that might cause timeouts
    test_queries = [
        "What are Newton's laws of motion?",
        "Explain the law of universal gravitation",
        "How did you develop calculus?",
        "What is the nature of light and optics?",
        "Describe your scientific method"
    ]
    
    success_count = 0
    total_tests = len(test_queries)
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔬 Test {i}/{total_tests}: {query}")
        print("-" * 40)
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Generate response with Newton
            response = await service.generate_personality_response(
                query=query,
                personality_id="newton"
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            print(f"✅ Response received in {response_time:.2f}s")
            print(f"📄 Content: {response.content[:100]}...")
            print(f"📊 Characters: {response.character_count}/{response.max_allowed}")
            print(f"🔧 Source: {response.source}")
            
            if hasattr(response, 'metadata') and response.metadata:
                print(f"⚙️  Metadata:")
                print(f"   Model: {response.metadata.get('model', 'unknown')}")
                print(f"   Response Time: {response.metadata.get('response_time', 'unknown')}s")
                print(f"   Attempt: {response.metadata.get('attempt', 'unknown')}")
                print(f"   Timeout Config: {response.metadata.get('timeout_seconds', 'unknown')}s")
            
            success_count += 1
            print("✅ Test PASSED")
            
        except Exception as e:
            print(f"❌ Test FAILED: {e}")
        
        print()
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Successful: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
    print(f"📈 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All Newton timeout tests PASSED!")
        return True
    else:
        print("⚠️  Some tests failed - check logs for details")
        return False

async def test_timeout_comparison():
    """Compare timeout behavior between different personalities"""
    
    service = EnhancedSimpleLLMService()
    
    if not service.is_configured:
        print("❌ Service not configured")
        return
    
    print("\n🔄 Timeout Comparison Test")
    print("=" * 50)
    
    # Test different personalities with same query
    personalities = ["newton", "einstein", "krishna"]
    query = "What is the nature of scientific discovery?"
    
    for personality_id in personalities:
        config = service.personalities.get(personality_id)
        if not config:
            continue
            
        print(f"\n🎭 Testing {config.name}:")
        print(f"   Timeout: {config.timeout_seconds}s, Retries: {config.max_retries}")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            response = await service.generate_personality_response(
                query=query,
                personality_id=personality_id
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            print(f"   ✅ Response: {response_time:.2f}s ({len(response.content)} chars)")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    async def main():
        success = await test_newton_timeout_fix()
        await test_timeout_comparison()
        return success
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
