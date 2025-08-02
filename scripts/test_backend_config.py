#!/usr/bin/env python3
"""
Simple test to check what the backend is receiving
"""

import requests

def test_backend_auth_config():
    """Test what the backend knows about its auth configuration"""
    backend_url = "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api"
    
    print("🔍 Testing Backend Authentication Configuration")
    print("=" * 60)
    
    # Test 1: Check if backend is accessible
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"✅ Health Check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test 2: Check unauthenticated request
    try:
        payload = {"query": "test", "personality_id": "krishna"}
        response = requests.post(f"{backend_url}/spiritual_guidance", json=payload, timeout=10)
        print(f"🔒 Unauthenticated Request: {response.status_code}")
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"   📋 Error Response: {error_data}")
            except:
                print(f"   📋 Raw Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Auth Test Failed: {e}")
    
    # Test 3: Check with mock bearer token
    try:
        headers = {"Authorization": "Bearer mock_token_test"}
        payload = {"query": "test", "personality_id": "krishna"}
        response = requests.post(f"{backend_url}/spiritual_guidance", json=payload, headers=headers, timeout=10)
        print(f"🎭 Mock Token Request: {response.status_code}")
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"   📋 Error Response: {error_data}")
            except:
                print(f"   📋 Raw Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Mock Token Test Failed: {e}")

if __name__ == "__main__":
    test_backend_auth_config()
