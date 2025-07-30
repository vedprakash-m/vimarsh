#!/usr/bin/env python3
"""
Comprehensive test to debug the authentication flow
"""

import requests
import time
import json

def test_complete_auth_flow():
    """Test the complete authentication flow step by step"""
    backend_url = "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api"
    
    print("🔍 Comprehensive Authentication Flow Test")
    print("=" * 60)
    
    # Test 1: Basic connectivity
    print("1️⃣ Testing Basic Connectivity...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=30)
        print(f"   ✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            try:
                health_data = response.json()
                print(f"   📋 Health Response: {health_data}")
            except Exception:
                print(f"   📋 Health Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print("   ⏰ Health check timed out - Function App might be cold starting")
        print("   🔄 Waiting 30 seconds for warm-up...")
        time.sleep(30)
        try:
            response = requests.get(f"{backend_url}/health", timeout=30)
            print(f"   ✅ Health Check (retry): {response.status_code}")
        except Exception as e:
            print(f"   ❌ Health Check Failed (retry): {e}")
            return
    except Exception as e:
        print(f"   ❌ Health Check Failed: {e}")
        return
    
    # Test 2: Unauthenticated request
    print("\n2️⃣ Testing Unauthenticated Request...")
    try:
        payload = {"query": "test spiritual guidance", "personality_id": "krishna"}
        response = requests.post(f"{backend_url}/spiritual_guidance", json=payload, timeout=30)
        print(f"   🔒 Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejecting unauthenticated requests")
        elif response.status_code == 200:
            print("   ⚠️  WARNING: Authentication might be disabled")
        
        try:
            error_data = response.json()
            print(f"   📋 Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   📋 Raw Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Unauthenticated test failed: {e}")
    
    # Test 3: Check CORS headers
    print("\n3️⃣ Testing CORS Configuration...")
    try:
        headers = {
            'Origin': 'https://vimarsh.vedprakash.net',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        response = requests.options(f"{backend_url}/spiritual_guidance", headers=headers, timeout=30)
        print(f"   🌐 CORS Preflight: {response.status_code}")
        
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        if cors_headers:
            print(f"   📋 CORS Headers: {json.dumps(cors_headers, indent=2)}")
        else:
            print("   ⚠️  No CORS headers found")
            
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    # Test 4: Invalid token test
    print("\n4️⃣ Testing Invalid Token...")
    try:
        headers = {"Authorization": "Bearer invalid_token_test"}
        payload = {"query": "test", "personality_id": "krishna"}
        response = requests.post(f"{backend_url}/spiritual_guidance", json=payload, headers=headers, timeout=30)
        print(f"   🎭 Invalid Token Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejecting invalid tokens")
        
        try:
            error_data = response.json()
            print(f"   📋 Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   📋 Raw Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Invalid token test failed: {e}")
    
    print("\n" + "="*60)
    print("🔍 Test Summary:")
    print("- If health check passes: Backend is running")
    print("- If unauthenticated requests return 401: Auth is enabled")
    print("- If CORS headers are present: Frontend can connect")
    print("- Check browser F12 → Network tab for detailed error messages")
    print("\n📝 Next Steps:")
    print("1. Test with real Microsoft token from frontend")
    print("2. Check Azure Function App logs for detailed errors")
    print("3. Verify JWT token validation is working")

if __name__ == "__main__":
    test_complete_auth_flow()
