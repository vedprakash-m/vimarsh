#!/usr/bin/env python3
"""
Test Buddha Personality on Deployed Enhanced Service
"""

import requests
import json

def test_buddha_personality():
    """Test Buddha personality responses"""
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    
    test_data = {
        "query": "How can I find inner peace?",
        "personality_id": "buddha",
        "language": "en"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing Buddha personality...")
        print(f"📤 Request: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Buddha Response:")
            print(f"📝 Response: {result.get('response', 'No response')}")
            print(f"👤 Personality: {result.get('personality', {}).get('name', 'Unknown')}")
            print(f"🔍 Metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_multiple_personalities():
    """Test multiple personalities to verify enhanced service"""
    
    personalities = [
        ("krishna", "What is dharma?"),
        ("buddha", "How can I find inner peace?"),
        ("jesus", "How should I love others?"),
        ("rumi", "What is divine love?"),
        ("einstein", "What is the nature of reality?")
    ]
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    headers = {"Content-Type": "application/json"}
    
    results = {}
    
    for personality_id, query in personalities:
        print(f"\n🧪 Testing {personality_id.title()} personality...")
        
        test_data = {
            "query": query,
            "personality_id": personality_id,  
            "language": "en"
        }
        
        try:
            response = requests.post(url, headers=headers, json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                results[personality_id] = {
                    "success": True,
                    "response": result.get("response", "")[:100] + "...",
                    "length": len(result.get("response", "")),
                    "source": result.get("metadata", {}).get("response_source", "unknown")
                }
                print(f"✅ {personality_id.title()}: {len(result.get('response', ''))} chars, Source: {results[personality_id]['source']}")
            else:
                results[personality_id] = {
                    "success": False,
                    "error": f"Status {response.status_code}: {response.text[:100]}"
                }
                print(f"❌ {personality_id.title()}: {results[personality_id]['error']}")
                
        except Exception as e:
            results[personality_id] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ {personality_id.title()}: {e}")
    
    print(f"\n📋 Summary:")
    successful = sum(1 for r in results.values() if r["success"])
    print(f"✅ Successful: {successful}/{len(personalities)}")
    
    for personality_id, result in results.items():
        if result["success"]:
            print(f"✅ {personality_id.title()}: {result['length']} chars ({result['source']})")
        else:
            print(f"❌ {personality_id.title()}: {result['error']}")
    
    return results

if __name__ == "__main__":
    print("🚀 Testing Enhanced Multi-Personality Service")
    print("=" * 50)
    
    # Test Buddha specifically
    test_buddha_personality()
    
    print("\n" + "=" * 50)
    
    # Test multiple personalities
    test_multiple_personalities()
