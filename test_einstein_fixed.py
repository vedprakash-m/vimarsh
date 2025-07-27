#!/usr/bin/env python3
"""
Test Einstein Locally with Fixed Configuration
"""

import requests
import json

def test_einstein_locally():
    """Test Einstein personality with scientific questions locally"""
    
    # Test questions about imagination in scientific breakthroughs
    test_cases = [
        "What role does imagination play in scientific breakthroughs?",
        "How did imagination contribute to your theory of relativity?",
        "What is the relationship between creativity and scientific discovery?",
        "How can we encourage imaginative thinking in science?",
        "What is more important: knowledge or imagination?"
    ]
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    headers = {"Content-Type": "application/json"}
    
    print("🧪 Testing Einstein with Scientific Questions")
    print("=" * 60)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {question}")
        
        test_data = {
            "query": question,
            "personality_id": "einstein",
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
                if "please ask me something related to science" in response_text.lower():
                    print(f"⚠️ Still getting generic fallback response!")
                else:
                    print(f"✅ Getting appropriate scientific response!")
                    
            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 40)

def test_safety_validation():
    """Test Einstein's safety validation directly"""
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/safety/validate"
    headers = {"Content-Type": "application/json"}
    
    print("\n🛡️ Testing Einstein Safety Validation")
    print("=" * 60)
    
    # Test content that should pass
    valid_content = "My friend, imagination is more important than knowledge. It allows us to explore new possibilities and see beyond current limitations. Through imagination, we can visualize complex theories like relativity."
    
    test_data = {
        "content": valid_content,
        "personality_id": "einstein",
        "query": "What role does imagination play in scientific breakthroughs?"
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
    test_einstein_locally()
    test_safety_validation()
