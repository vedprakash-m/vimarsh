#!/usr/bin/env python3
"""
Quick test script for error handling system
"""

import sys
import os
import asyncio

# Add the backend directory to the path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

async def test_error_handling():
    """Test the error handling system initialization"""
    print("🧪 Testing Error Handling System...")
    
    try:
        # Test 1: Import the error recovery tester
        print("  1. Testing imports...")
        from error_handling.error_recovery_testing import ErrorRecoveryTester
        print("     ✅ ErrorRecoveryTester imported successfully")
        
        # Test 2: Initialize the tester
        print("  2. Testing initialization...")
        tester = ErrorRecoveryTester()
        print("     ✅ ErrorRecoveryTester created successfully")
        
        # Test 3: Initialize systems
        print("  3. Testing system initialization...")
        await tester.initialize_systems()
        print("     ✅ Systems initialized successfully")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"     ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_error_handling())
    exit(0 if success else 1)
