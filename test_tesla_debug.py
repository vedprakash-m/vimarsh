#!/usr/bin/env python3
"""
Test Tesla Personality Debug
"""

import requests
import json

def test_tesla_debug():
    """Test Tesla personality with scientific questions"""
    
    # Test questions about Tesla's scientific work
    test_cases = [
        "How does the theory of relativity change our understanding of time and space?",
        "What is the relationship between energy and matter in the universe?",
        "Tell me about alternating current and its advantages over direct current",
        "What innovations in electrical engineering do you foresee for the future?",
        "How can wireless transmission of electricity work?"
    ]
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    headers = {"Content-Type": "application/json"}
    
    print("⚡ Testing Tesla with Scientific Questions")
    print("=" * 60)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {question}")
        
        test_data = {
            "query": question,
            "personality_id": "tesla",
            "language": "en"
        }
        
        try:
            response = requests.post(url, headers=headers, json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                source = result.get("metadata", {}).get("response_source", "unknown")
                safety_passed = result.get("metadata", {}).get("safety", {}).get("safety_passed", False)
                response_length = len(response_text)
                
                print(f"✅ Status: Success")
                print(f"📊 Length: {response_length} chars")
                print(f"🤖 Source: {source}")
                print(f"🛡️ Safety: {'Passed' if safety_passed else 'Failed'}")
                print(f"💬 Response: {response_text}")
                
                # Check if it's the generic fallback (indicates problem)
                if "please ask me something" in response_text.lower() and "spiritual" in response_text.lower():
                    print(f"⚠️ Getting generic spiritual fallback response!")
                else:
                    print(f"✅ Getting appropriate scientific response!")
                    
            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 40)

def test_tesla_safety():
    """Test Tesla's safety validation directly"""
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/safety/validate"
    headers = {"Content-Type": "application/json"}
    
    print("\n🛡️ Testing Tesla Safety Validation")
    print("=" * 60)
    
    # Test content that should pass for Tesla
    valid_content = "Fellow inventor, my theory of alternating current revolutionized electrical transmission. Through innovation and experimentation, we can harness electricity's power to illuminate the world and create wireless energy transmission systems."
    
    test_data = {
        "content": valid_content,
        "personality_id": "tesla",
        "query": "Tell me about alternating current and its advantages"
    }
    
    try:
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            safety_passed = result.get("validation_result", {}).get("safety_passed", False)
            safety_score = result.get("validation_result", {}).get("safety_score", 0)
            warnings = result.get("validation_result", {}).get("warnings", [])
            
            print(f"✅ Safety Validation Test:")
            print(f"🛡️ Safety Passed: {safety_passed}")
            print(f"📊 Safety Score: {safety_score}")
            print(f"⚠️ Warnings: {warnings}")
            print(f"📏 Content Length: {result.get('content_length', 0)}")
            
            config = result.get("safety_config", {})
            print(f"⚙️ Max Length: {config.get('max_response_length', 'unknown')}")
            print(f"⚙️ Safety Level: {config.get('safety_level', 'unknown')}")
            
        else:
            print(f"❌ Safety validation failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception in safety validation: {e}")

if __name__ == "__main__":
    test_tesla_debug()
    test_tesla_safety()
