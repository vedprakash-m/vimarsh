#!/usr/bin/env python3
"""
Debug Einstein LLM Service Issue
"""

import requests
import json

def debug_einstein_llm():
    """Debug why Einstein is using fallback instead of LLM service"""
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    headers = {"Content-Type": "application/json"}
    
    test_data = {
        "query": "What role does imagination play in scientific breakthroughs?",
        "personality_id": "einstein",
        "language": "en"
    }
    
    print("🔍 Debugging Einstein LLM Service Issue")
    print("=" * 60)
    print(f"📤 Request: {json.dumps(test_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=test_data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"💬 Response Text: {result.get('response', '')}")
        print(f"\n🔍 LLM Service Debug Info:")
        
        metadata = result.get('metadata', {})
        print(f"   📊 Response Source: {metadata.get('response_source', 'unknown')}")
        print(f"   🤖 LLM Service Available: {metadata.get('llm_service_available', 'unknown')}")
        print(f"   ⚙️ LLM Service Initialized: {metadata.get('llm_service_initialized', 'unknown')}")
        print(f"   🔧 LLM Service Configured: {metadata.get('llm_service_configured', 'unknown')}")
        print(f"   🔑 API Key Present: {metadata.get('api_key_present', 'unknown')}")
        print(f"   📏 API Key Length: {metadata.get('api_key_length', 'unknown')}")
        
        safety = metadata.get('safety', {})
        print(f"\n🛡️ Safety Validation:")
        print(f"   ✅ Safety Passed: {safety.get('safety_passed', 'unknown')}")
        print(f"   📊 Safety Score: {safety.get('safety_score', 'unknown')}")
        print(f"   ⚠️ Warnings: {safety.get('warnings', [])}")
        print(f"   🚫 Blocked Patterns: {safety.get('blocked_patterns', [])}")
        
        safety_config = metadata.get('safety_config', {})
        print(f"\n⚙️ Safety Configuration:")
        print(f"   📏 Max Response Length: {safety_config.get('max_response_length', 'unknown')}")
        print(f"   🛡️ Safety Level: {safety_config.get('safety_level', 'unknown')}")
        print(f"   📚 Require Citations: {safety_config.get('require_citations', 'unknown')}")
        
        personality = result.get('personality', {})
        print(f"\n👤 Personality Info:")
        print(f"   🆔 ID: {personality.get('id', 'unknown')}")
        print(f"   📛 Name: {personality.get('name', 'unknown')}")
        print(f"   🏷️ Domain: {personality.get('domain', 'unknown')}")
        
    else:
        print(f"❌ Error: Status {response.status_code}")
        print(f"📄 Response: {response.text}")

if __name__ == "__main__":
    debug_einstein_llm()
