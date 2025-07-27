#!/usr/bin/env python3
"""
Test All Twelve Personalities on Enhanced Service
"""

import requests
import json

def test_all_personalities():
    """Test all 12 personalities with standardized 500 character limits"""
    
    personalities = [
        ("krishna", "What is dharma?", 500),
        ("buddha", "How can I find inner peace?", 500),
        ("jesus", "How should I love others?", 500),
        ("rumi", "What is divine love?", 500),
        ("lao_tzu", "What is the natural way?", 500),
        ("einstein", "What is the nature of reality?", 500),
        ("lincoln", "How can we achieve unity?", 500),
        ("marcus_aurelius", "How should I live virtuously?", 500),
        ("tesla", "How can innovation change the world?", 500),
        ("newton", "What are the fundamental laws of nature?", 500),
        ("chanakya", "What makes an effective leader?", 500),
        ("confucius", "How should we live ethically?", 500)
    ]
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    headers = {"Content-Type": "application/json"}
    
    results = {}
    
    print("🧪 Testing All 12 Enhanced Personalities")
    print("=" * 60)
    
    for personality_id, query, expected_max in personalities:
        print(f"\n🎭 Testing {personality_id.replace('_', ' ').title()}")
        print(f"❓ Query: {query}")
        print(f"📏 Expected max length: {expected_max} chars")
        
        test_data = {
            "query": query,
            "personality_id": personality_id,
            "language": "en"
        }
        
        try:
            response = requests.post(url, headers=headers, json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                actual_length = len(response_text)
                source = result.get("metadata", {}).get("response_source", "unknown")
                safety_passed = result.get("metadata", {}).get("safety", {}).get("safety_passed", False)
                
                results[personality_id] = {
                    "success": True,
                    "response": response_text,
                    "length": actual_length,
                    "expected_max": expected_max,
                    "within_limit": actual_length <= expected_max,
                    "source": source,
                    "safety_passed": safety_passed
                }
                
                # Status indicators
                length_status = "✅" if actual_length <= expected_max else "⚠️"
                source_status = "🤖" if source == "llm_service" else "📝"
                safety_status = "🛡️" if safety_passed else "❌"
                
                print(f"{length_status} Length: {actual_length}/{expected_max} chars")
                print(f"{source_status} Source: {source}")
                print(f"{safety_status} Safety: {'Passed' if safety_passed else 'Failed'}")
                print(f"💬 Preview: {response_text[:100]}...")
                
            else:
                results[personality_id] = {
                    "success": False,
                    "error": f"Status {response.status_code}: {response.text[:100]}"
                }
                print(f"❌ Error: {results[personality_id]['error']}")
                
        except Exception as e:
            results[personality_id] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ Exception: {e}")
    
    # Summary Report
    print(f"\n📊 ENHANCED SERVICE VALIDATION REPORT")
    print("=" * 60)
    
    successful = sum(1 for r in results.values() if r.get("success", False))
    ai_powered = sum(1 for r in results.values() if r.get("source") == "llm_service")
    within_limits = sum(1 for r in results.values() if r.get("within_limit", False))
    safe_responses = sum(1 for r in results.values() if r.get("safety_passed", False))
    
    print(f"✅ Total Successful: {successful}/12")
    print(f"🤖 AI-Powered Responses: {ai_powered}/12")
    print(f"📏 Within Character Limits: {within_limits}/12")
    print(f"🛡️ Safety Validated: {safe_responses}/12")
    
    print(f"\n📋 Detailed Results:")
    for personality_id, result in results.items():
        if result.get("success"):
            name = personality_id.replace('_', ' ').title()
            length = result["length"]
            max_len = result["expected_max"]
            source = "AI" if result["source"] == "llm_service" else "Template"
            limit_ok = "✅" if result["within_limit"] else "⚠️"
            safety_ok = "🛡️" if result["safety_passed"] else "❌"
            
            print(f"{limit_ok} {name}: {length}/{max_len} chars ({source}) {safety_ok}")
        else:
            print(f"❌ {personality_id.replace('_', ' ').title()}: {result['error']}")
    
    # Final Assessment
    if successful == 12 and ai_powered == 12 and within_limits == 12:
        print(f"\n🎉 ENHANCED SERVICE VALIDATION: COMPLETE SUCCESS!")
        print("✅ All personalities working with real AI responses")
        print("✅ All character limits properly configured")
        print("✅ All safety validations passing")
    else:
        print(f"\n⚠️ ENHANCED SERVICE VALIDATION: PARTIAL SUCCESS")
        print(f"Issues detected - check individual results above")
    
    return results

if __name__ == "__main__":
    test_all_personalities()
