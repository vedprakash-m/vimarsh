#!/usr/bin/env python3
"""
Generate development admin token for Vimarsh
This creates a properly formatted dev token for admin access
"""

import os
import sys
import hashlib
import hmac
from datetime import datetime

# Load environment variables from local.settings.json
sys.path.append('/Users/vedprakashmishra/vimarsh/backend')

def generate_dev_token(email: str, dev_secret: str) -> str:
    """Generate secure development token"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    payload = f"{email}:{timestamp}"
    signature = hmac.new(
        dev_secret.encode(), 
        payload.encode(), 
        hashlib.sha256
    ).hexdigest()
    return f"dev:{payload}:{signature}"

def main():
    # Configuration from local.settings.json
    admin_email = "vedprakash.m@outlook.com"
    dev_secret = "dev-secret-change-in-production"
    
    # Generate admin token
    admin_token = generate_dev_token(admin_email, dev_secret)
    
    print("🔐 VIMARSH ADMIN DEVELOPMENT TOKENS")
    print("=" * 50)
    print(f"Admin Email: {admin_email}")
    print(f"Admin Token: {admin_token}")
    print()
    print("📝 USAGE:")
    print("1. Copy the admin token above")
    print("2. Update frontend/.env.local with:")
    print(f"   REACT_APP_DEV_ADMIN_TOKEN={admin_token}")
    print("3. Restart frontend (npm start)")
    print("4. You will have admin access for 24 hours")
    print()
    print("🔄 TOKEN EXPIRY: 24 hours from now")
    print("🔒 ADMIN ROLE: Permanent (configured in backend/local.settings.json)")

if __name__ == "__main__":
    main()
