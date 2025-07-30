#!/usr/bin/env python3
"""
Debug script to test backend authentication configuration and tenant settings
"""

import requests
import json
import sys

def test_backend_url():
    """Test if backend URL is accessible"""
    print("🔍 Testing backend URL accessibility...")
    
    # Try both URLs
    urls = [
        "https://vimarsh-backend-app-flex.azurewebsites.net/api",
        "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api"
    ]
    
    for url in urls:
        try:
            print(f"\n📡 Testing: {url}")
            response = requests.get(f"{url}/health", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Backend accessible at: {url}")
                return url
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection failed: {str(e)}")
    
    return None

def test_auth_config(backend_url):
    """Test authentication configuration"""
    if not backend_url:
        print("❌ No accessible backend URL found")
        return
    
    print(f"\n🔐 Testing authentication configuration...")
    
    # Test with mock token (should fail with 401)
    mock_headers = {"Authorization": "Bearer mock-token"}
    try:
        response = requests.post(
            f"{backend_url}/spiritual_guidance",
            headers=mock_headers,
            json={"query": "test", "context": "general"},
            timeout=10
        )
        print(f"   Mock token response: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Backend properly rejects mock tokens")
        else:
            print("   ⚠️ Backend should return 401 for invalid tokens")
    except Exception as e:
        print(f"   ❌ Auth test failed: {str(e)}")

def check_entra_id_config():
    """Check Entra ID configuration from environment"""
    print(f"\n🔐 Entra ID Configuration Check...")
    
    # The configuration we're using
    config = {
        "client_id": "52747449-829f-4fbe-bb5e-b4c54c9b1fbe",
        "tenant_id": "common",
        "authority": "https://login.microsoftonline.com/common"
    }
    
    print(f"   Client ID: {config['client_id']}")
    print(f"   Tenant ID: {config['tenant_id']}")
    print(f"   Authority: {config['authority']}")
    
    if config['tenant_id'] == 'common':
        print("   ✅ Tenant set to 'common' - should support personal and work accounts")
    else:
        print("   ⚠️ Tenant is restricted - may not support personal accounts")

def main():
    print("🚀 Vimarsh Authentication Debug Tool")
    print("=" * 50)
    
    # Test backend accessibility
    backend_url = test_backend_url()
    
    # Test authentication
    test_auth_config(backend_url)
    
    # Check Entra ID config
    check_entra_id_config()
    
    print("\n" + "=" * 50)
    print("🏁 Debug complete")
    
    if backend_url:
        print(f"✅ Use this backend URL: {backend_url}")
    else:
        print("❌ No accessible backend URL found")

if __name__ == "__main__":
    main()
