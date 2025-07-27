#!/usr/bin/env python3
"""
Test Tesla with User's Specific Questions
"""

import requests
import json

def test_tesla_user_questions():
    """Test Tesla with the exact questions from user's screenshot"""
    
    # Questions from the user's screenshot
    test_cases = [
        "How does the theory of relativity change our understanding of time and space?",
        "What is the relationship between energy and matter in the universe?"
    ]
    
    url = "https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance"
    headers = {"Content-Type": "application/json"}
    
    print("⚡ Testing Tesla with User's Exact Questions")
    print("=" * 60)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n🔬 User Test {i}: {question}")
        
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
                
                # Check if it's Tesla personality (should NOT contain spiritual guidance)
                if "beloved devotee" in response_text.lower() or "spiritual" in response_text.lower():
                    print(f"❌ Still getting wrong personality response!")
                elif "fellow inventor" in response_text.lower() or "electricity" in response_text.lower() or "current" in response_text.lower():
                    print(f"✅ Perfect Tesla personality response!")
                else:
                    print(f"✅ Getting appropriate Tesla response!")
                    
            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_tesla_user_questions()
