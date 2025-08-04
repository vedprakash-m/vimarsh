"""
Test script for enhanced authentication middleware
Tests development mode and admin token generation
"""

import os
import sys

# Add backend to path
sys.path.insert(0, '/Users/vedprakashmishra/vimarsh/backend')

# Set up test environment
os.environ['ENABLE_AUTH'] = 'true'
os.environ['AUTH_DEVELOPMENT_MODE'] = 'true'
os.environ['ADMIN_EMAILS'] = 'vedprakash.m@outlook.com'
os.environ['SUPER_ADMIN_EMAILS'] = 'vedprakash.m@outlook.com'

from auth.unified_auth_service import auth_service

# Development token generation functions for testing
def get_admin_dev_token() -> str:
    """Get development token for admin user"""
    return "admin-token"  # Use simple dev token

def get_super_admin_dev_token() -> str:
    """Get development token for super admin user"""
    return "super-admin-token"  # Use simple dev token

def test_dev_token_generation():
    """Test development token generation and validation"""
    print("🔐 Testing Enhanced Authentication Middleware")
    
    # Test admin token generation
    admin_token = get_admin_dev_token()
    print(f"Admin Dev Token: {admin_token}")
    
    # Test super admin token generation
    super_admin_token = get_super_admin_dev_token()
    print(f"Super Admin Dev Token: {super_admin_token}")
    
    # Test token validation using unified auth service
    admin_user = auth_service._validate_development_token(admin_token)
    print(f"Admin token validation: {admin_user.email if admin_user else 'Invalid'}")
    
    super_admin_user = auth_service._validate_development_token(super_admin_token)
    print(f"Super admin token validation: {super_admin_user.email if super_admin_user else 'Invalid'}")
    
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
