#!/usr/bin/env python3
"""
Debug script to analyze MSAL token structure and identify validation issues
"""

import jwt
import json
import sys
from typing import Dict, Any

def decode_token_safely(token: str) -> Dict[str, Any]:
    """Decode token without signature verification to inspect claims"""
    try:
        # Decode without verification to see the claims
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"❌ Error decoding token: {str(e)}")
        return {}

def analyze_token(token: str):
    """Analyze token structure and identify potential validation issues"""
    print("🔍 Analyzing MSAL Token Structure...")
    print("=" * 60)
    
    # Get header
    try:
        header = jwt.get_unverified_header(token)
        print("📋 Token Header:")
        print(json.dumps(header, indent=2))
        print()
    except Exception as e:
        print(f"❌ Error getting header: {str(e)}")
        return
    
    # Get payload
    payload = decode_token_safely(token)
    if not payload:
        return
    
    print("📄 Token Payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    # Analyze key fields for validation
    print("🔑 Key Fields for Validation:")
    print("-" * 30)
    print(f"Issuer (iss): {payload.get('iss', 'NOT FOUND')}")
    print(f"Audience (aud): {payload.get('aud', 'NOT FOUND')}")
    print(f"Tenant ID (tid): {payload.get('tid', 'NOT FOUND')}")
    print(f"Client ID (appid): {payload.get('appid', 'NOT FOUND')}")
    print(f"Subject (sub): {payload.get('sub', 'NOT FOUND')}")
    print(f"Email: {payload.get('email', payload.get('preferred_username', 'NOT FOUND'))}")
    print(f"Name: {payload.get('name', 'NOT FOUND')}")
    print(f"Expiration: {payload.get('exp', 'NOT FOUND')}")
    print()
    
    # Expected values for Vimarsh
    expected_client_id = "e4bd74b8-9a82-40c6-8d52-3e231733095e"
    expected_tenant = "common"
    
    print("🎯 Validation Analysis:")
    print("-" * 30)
    
    # Check audience
    token_aud = payload.get('aud', '')
    if token_aud == expected_client_id:
        print("✅ Audience matches client_id directly")
    elif token_aud == f"api://{expected_client_id}":
        print("✅ Audience matches api://client_id format")
    else:
        print(f"❌ Audience mismatch:")
        print(f"   Token audience: {token_aud}")
        print(f"   Expected: {expected_client_id} or api://{expected_client_id}")
    
    # Check issuer
    token_iss = payload.get('iss', '')
    token_tid = payload.get('tid', '')
    expected_iss = f"https://login.microsoftonline.com/{token_tid}/v2.0"
    
    if token_iss == expected_iss:
        print("✅ Issuer format is correct")
    else:
        print(f"❌ Issuer format issue:")
        print(f"   Token issuer: {token_iss}")
        print(f"   Expected format: {expected_iss}")
    
    # Check if it's v1 vs v2 token
    if 'ver' in payload:
        version = payload['ver']
        print(f"📋 Token version: {version}")
        if version == "1.0":
            print("⚠️  This is a v1.0 token - may need different validation")
        elif version == "2.0":
            print("✅ This is a v2.0 token")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_token.py <jwt_token>")
        print("\nTo test with your browser token:")
        print("1. Go to your browser F12 console")
        print("2. Look for the token in AdminContext.tsx logs")
        print("3. Copy the full token and run: python debug_token.py 'YOUR_TOKEN_HERE'")
        sys.exit(1)
    
    token = sys.argv[1]
    analyze_token(token)
