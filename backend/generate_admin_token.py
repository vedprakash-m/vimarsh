#!/usr/bin/env python3
"""
Generate development admin token for testing
"""

import os
import sys
import hashlib
import hmac
from datetime import datetime

def generate_dev_token(email: str) -> str:
    """Generate secure development token"""
    dev_secret = 'dev-secret-change-in-production'  # From local.settings.json
    timestamp = str(int(datetime.utcnow().timestamp()))
    payload = f"{email}:{timestamp}"
    signature = hmac.new(
        dev_secret.encode(), 
        payload.encode(), 
        hashlib.sha256
    ).hexdigest()
    return f"dev:{payload}:{signature}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_admin_token.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    token = generate_dev_token(email)
    print(f"Development admin token for {email}:")
    print(token)
    print("\nUse with curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:7071/api/vimarsh-admin/role')
