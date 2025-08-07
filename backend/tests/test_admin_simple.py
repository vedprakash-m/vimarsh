#!/usr/bin/env python3
"""
Simple Admin Dashboard Integration Test

This script tests the admin dashboard integration without complex imports.
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from services.personality_service import PersonalityService
from models.personality_models import get_personality_list, get_personalities_by_domain

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

async def test_admin_integration():
    """Test admin dashboard integration capabilities"""
    
    print_section("ADMIN DASHBOARD INTEGRATION TEST")
    
    try:
        # Test personality listing
        print("� Testing personality discovery...")
        filters = {}
        personalities = get_personality_list()
        
        print(f"✅ Found {len(personalities)} active personalities")
        
        # Test domain breakdown
        print("\n📊 Domain Distribution:")
        domain_counts = {}
        for personality in personalities:
            domain = personality['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in domain_counts.items():
            print(f"   • {domain.capitalize()}: {count} personalities")
        
        # Show sample personality details
        if personalities:
            sample_personality = personalities[0]
            print(f"\n🎭 Sample Personality Details:")
            print(f"   • ID: {sample_personality['id']}")
            print(f"   • Name: {sample_personality['name']}")
            print(f"   • Domain: {sample_personality['domain']}")
            print(f"   • Description: {sample_personality['description']}")
        
        # Test domain filtering
        print("\n🔎 Testing domain-specific filtering...")
        spiritual_personalities = get_personalities_by_domain("spiritual")
        scientific_personalities = get_personalities_by_domain("scientific")
        scientific_personalities = get_personalities_by_domain("scientific")
        
        print(f"   • Spiritual personalities: {len(spiritual_personalities)}")
        print(f"   • Scientific personalities: {len(scientific_personalities)}")
        
        print("\n✅ All admin integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Admin integration test failed: {e}")
        return False