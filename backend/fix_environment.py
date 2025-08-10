#!/usr/bin/env python3
'''
Environment Fix Script for Vimarsh Phase 1
==========================================

This script ensures proper environment variable loading
before running any Phase 1 services.
'''

import os
from pathlib import Path

def load_environment():
    '''Load environment variables from correct .env file'''
    
    # Primary .env file with real credentials
    primary_env = "/Users/ved/Apps/vimarsh/.env"
    
    if os.path.exists(primary_env):
        print(f"Loading environment from: {primary_env}")
        
        with open(primary_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    
        print("✅ Environment variables loaded successfully")
        return True
    else:
        print(f"❌ Primary .env file not found: {primary_env}")
        return False

def verify_environment():
    '''Verify critical environment variables'''
    
    required_vars = [
        'GEMINI_API_KEY',
        'AZURE_COSMOS_CONNECTION_STRING', 
        'AZURE_COSMOS_DATABASE_NAME',
        'AZURE_COSMOS_CONTAINER_NAME'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    else:
        print("✅ All required environment variables present")
        return True

if __name__ == "__main__":
    load_environment()
    verify_environment()
