#!/usr/bin/env python3
"""
Test the deployed Azure function with detailed debugging
"""

import os
import sys
import requests
import json
import asyncio

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from services.simple_llm_service import SimpleLLMService

async def test_local_service():
    """Test the local simple service"""
    print("🔍 Testing Local Simple Service...")
    
    service = SimpleLLMService()
    
    print(f"API Key Present: {bool(service.api_key)}")
    print(f"API Key Length: {len(service.api_key) if service.api_key else 0}")
    print(f"Service Configured: {service.is_configured}")
    
    if service.is_configured:
        result = await service.get_krishna_response("How can I find inner peace?")
        print(f"\n🕉️ Local Service Result:")
        print(f"Source: {result.get('source')}")
        print(f"Response: {result.get('response')}")
        print(f"Error: {result.get('error', 'None')}")
    else:
        print("❌ Local service not configured")

def test_deployed_service():
    """Test the deployed Azure function"""
    print("\n🌐 Testing Deployed Azure Function...")
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    data = {
        "query": "How can I find inner peace?",
        "personality": "Krishna"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received!")
            print(f"Response: {result.get('response')}")
            print(f"Metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE SERVICE TEST")
    print("=" * 60)
    
    # Test local service
    await test_local_service()
    
    # Test deployed service
    test_deployed_service()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
