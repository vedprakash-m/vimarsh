#!/usr/bin/env python3
"""
Debug script to test authentication locally
"""

import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.append('/Users/ved/Apps/vimarsh/backend')

# Set environment variables for testing
os.environ['ENVIRONMENT'] = 'production'
os.environ['AZURE_FUNCTIONS_ENVIRONMENT'] = 'Production'
os.environ['ENABLE_AUTH'] = 'true'
os.environ['ENTRA_TENANT_ID'] = 'common'
os.environ['ENTRA_CLIENT_ID'] = 'e4bd74b8-9a82-40c6-8d52-3e231733095e'

def test_authentication():
    print("🔍 Debug Authentication Test")
    print("=" * 50)
    
    try:
        from auth.unified_auth_service import UnifiedAuthService
        print("✅ Successfully imported UnifiedAuthService")
        
        # Test initialization
        auth_service = UnifiedAuthService()
        print(f"✅ Auth service initialized:")
        print(f"   Mode: {auth_service.mode}")
        print(f"   Enabled: {auth_service.is_enabled}")
        print()
        
        # Test with a sample Microsoft Graph token (this will fail validation but should show the process)
        sample_token = "EwBYBMl6BAAUBKgm8k1UswUNwklmy2v7U/S+1fEA"  # Partial token for testing
        print(f"🔍 Testing token validation process...")
        
        # Test token extraction
        class MockRequest:
            def __init__(self, token):
                self.headers = {"Authorization": f"Bearer {token}"}
        
        mock_req = MockRequest(sample_token)
        extracted_token = auth_service._extract_token(mock_req)
        print(f"✅ Token extraction: {extracted_token[:20]}...")
        
        # Test environment detection
        environment = os.getenv("ENVIRONMENT", "").lower()
        azure_env = os.getenv("AZURE_FUNCTIONS_ENVIRONMENT", "").lower()
        print(f"✅ Environment detection:")
        print(f"   ENVIRONMENT: {environment}")
        print(f"   AZURE_FUNCTIONS_ENVIRONMENT: {azure_env}")
        print(f"   Should use production: {environment == 'production' or azure_env == 'production'}")
        
        print("\n✅ Authentication system appears to be working correctly!")
        print("🎯 Issue is likely with token validation in production environment")
        
    except Exception as e:
        print(f"❌ Error testing authentication: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_authentication()
