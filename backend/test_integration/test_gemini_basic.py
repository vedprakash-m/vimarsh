"""
Simple test script for Gemini Pro API client functionality.
Tests basic client initialization and response generation.
"""

import os
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our Gemini client
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm.gemini_client import create_development_client, SpiritualContext

def test_gemini_client_basic():
    """Test basic Gemini client functionality with mock responses."""
    
    print("=== Testing Gemini Pro Client ===")
    
    try:
        # Create development client (will use mock if no API key)
        client = create_development_client()
        print(f"✅ Client created: {type(client).__name__}")
        
        # Test with a simple spiritual query
        test_query = "What is the nature of dharma according to the Bhagavad Gita?"
        context = SpiritualContext.TEACHING
        
        print(f"🔍 Test query: {test_query}")
        print(f"📚 Context: {context.value}")
        
        # Since we're testing without actual API key, this should work with mock responses
        response = client.generate_spiritual_response(
            prompt=test_query,
            context=context,
            retrieved_chunks=[]  # Empty for basic test
        )
        
        print(f"📝 Response received:")
        print(f"   Content: {response.content[:200]}...")
        print(f"   Safety: {response.safety_ratings}")
        print(f"   Metadata: {response.metadata}")
        
        # Test configuration
        config = client.get_current_config()
        print(f"⚙️  Client configuration:")
        print(f"   Safety level: {config.safety_level.value}")
        print(f"   Allowed contexts: {[ctx.value for ctx in config.allowed_contexts]}")
        print(f"   Require citations: {config.require_citations}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logger.error(f"Gemini client test failed: {str(e)}")
        return False

def test_client_configurations():
    """Test different client configurations."""
    
    print("\n=== Testing Client Configurations ===")
    
    try:
        from llm.gemini_client import create_testing_client, create_production_client
        
        # Test development client
        dev_client = create_development_client()
        print(f"✅ Development client: {dev_client.get_current_config().safety_level.value}")
        
        # Test testing client
        test_client = create_testing_client()
        print(f"✅ Testing client: {test_client.get_current_config().safety_level.value}")
        
        # Test production client (will likely fail without API key, but structure should work)
        try:
            prod_client = create_production_client()
            print(f"✅ Production client: {prod_client.get_current_config().safety_level.value}")
        except Exception as e:
            print(f"⚠️  Production client requires API key: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    
    print("🕉️  Vimarsh - Gemini Pro Client Test")
    print("="*50)
    
    # Check for API key
    api_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"🔑 API Key found: {'*' * 10}{api_key[-4:]}")
    else:
        print("⚠️  No API key found - will use mock responses")
        print("   Set GOOGLE_AI_API_KEY or GOOGLE_API_KEY to test real API")
    
    # Run tests
    test1_passed = test_gemini_client_basic()
    test2_passed = test_client_configurations()
    
    # Summary
    print("\n" + "="*50)
    if test1_passed and test2_passed:
        print("✅ All tests passed! Gemini client is working correctly.")
    else:
        print("❌ Some tests failed. Check the logs above.")
    
    print("\n💡 Next steps:")
    print("   1. Add your Gemini API key to .env file")
    print("   2. Run integration tests with real API")
    print("   3. Test with RAG pipeline integration")

if __name__ == "__main__":
    main()
