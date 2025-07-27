"""
Test script for enhanced authentication middleware
Tests development mode and admin token generation
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, '/Users/vedprakashmishra/vimarsh/backend')

# Set up test environment
os.environ['ENABLE_AUTH'] = 'true'
os.environ['AUTH_DEVELOPMENT_MODE'] = 'true'
os.environ['ADMIN_EMAILS'] = 'vedprakash.m@outlook.com'
os.environ['SUPER_ADMIN_EMAILS'] = 'vedprakash.m@outlook.com'

from auth.unified_auth_service import (
    auth_service,
    AuthenticatedUser
)
# Note: Some functions like get_admin_dev_token may need to be implemented 
# in the unified auth service or removed if no longer needed

def test_dev_token_generation():
    """Test development token generation and validation"""
    print("🔐 Testing Enhanced Authentication Middleware")
    
    # Test admin token generation
    admin_token = get_admin_dev_token()
    print(f"Admin Dev Token: {admin_token}")
    
    # Test super admin token generation
    super_admin_token = get_super_admin_dev_token()
    print(f"Super Admin Dev Token: {super_admin_token}")
    
    # Test token validation
    auth = SecureDevAuthenticator()
    admin_email = auth.validate_dev_token(admin_token)
    print(f"Admin token validation: {admin_email}")
    
    super_admin_email = auth.validate_dev_token(super_admin_token)
    print(f"Super admin token validation: {super_admin_email}")
    
    # Test middleware
    middleware = AuthenticationMiddleware()
    
    # Test admin token
    admin_claims = middleware.validate_token(admin_token)
    print(f"Admin claims: {admin_claims}")
    
    # Test super admin token
    super_admin_claims = middleware.validate_token(super_admin_token)
    print(f"Super admin claims: {super_admin_claims}")
    
    print("✅ Enhanced authentication tests completed successfully")

def generate_frontend_test_tokens():
    """Generate tokens for frontend testing"""
    print("\n🎯 Frontend Test Tokens:")
    print("="*50)
    
    admin_token = get_admin_dev_token()
    super_admin_token = get_super_admin_dev_token()
    
    print(f"Admin Token (for development):")
    print(f"Authorization: Bearer {admin_token}")
    print()
    print(f"Super Admin Token (for development):")
    print(f"Authorization: Bearer {super_admin_token}")
    print()
    print("Copy these tokens to test admin endpoints in development mode")
    print("="*50)

if __name__ == "__main__":
    test_dev_token_generation()
    generate_frontend_test_tokens()
