#!/usr/bin/env python3
"""
Generate dev token for admin access in development mode.
This token will be valid for 24 hours.
"""

import os
import sys
import hmac
import hashlib
from datetime import datetime

def generate_dev_token(email: str, dev_secret: str) -> str:
    """Generate secure development token (valid for 24 hours)"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    payload = f"{email}:{timestamp}"
    signature = hmac.new(
        dev_secret.encode(), 
        payload.encode(), 
        hashlib.sha256
    ).hexdigest()
    return f"dev:{payload}:{signature}"

if __name__ == "__main__":
    # Get dev secret from local.settings.json environment
    dev_secret = "dev-secret-change-in-production"  # From your local.settings.json
    admin_email = "vedprakash.m@outlook.com"
    
    # Generate the token
    token = generate_dev_token(admin_email, dev_secret)
    
    print("=" * 60)
    print("🔑 Development Admin Token Generated")
    print("=" * 60)
    print(f"Email: {admin_email}")
    print(f"Token: {token}")
    print(f"Valid for: 24 hours from now")
    print(f"Expires: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC + 24h")
    print("=" * 60)
    print("\n📋 Usage:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:7071/api/vimarsh-admin/role')
    print(f"\n🌐 For frontend, add to .env.local:")
    print(f"REACT_APP_DEV_ADMIN_TOKEN={token}")
    print("=" * 60)
