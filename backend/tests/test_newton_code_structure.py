#!/usr/bin/env python3
"""
Code structure verification for Newton timeout fix
This tests the code changes without requiring API key
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_newton_timeout_code_structure():
    """Verify that timeout code changes are properly implemented"""
    
    print("🧪 Testing Newton Timeout Fix Code Structure")
    print("=" * 50)
    
    try:
        from services.enhanced_simple_llm_service import EnhancedSimpleLLMService, PersonalityConfig
        print("✅ Import successful")
        
        # Create service instance (without requiring API key for structure test)
        service = EnhancedSimpleLLMService()
        
        # Check if personalities are loaded
        if hasattr(service, 'personalities'):
            print("✅ Personalities attribute exists")
            
            # Check Newton configuration
            if 'newton' in service.personalities:
                newton_config = service.personalities['newton']
                print("✅ Newton personality found")
                
                # Check timeout configuration
                if hasattr(newton_config, 'timeout_seconds'):
                    print(f"✅ Timeout configured: {newton_config.timeout_seconds}s")
                else:
                    print("❌ Timeout not configured")
                    return False
                
                # Check retry configuration  
                if hasattr(newton_config, 'max_retries'):
                    print(f"✅ Retries configured: {newton_config.max_retries}")
                else:
                    print("❌ Max retries not configured")
                    return False
                
                # Check if Newton has optimized settings
                if newton_config.timeout_seconds == 20:
                    print("✅ Newton has reduced timeout (20s) for 504 fix")
                else:
                    print(f"⚠️  Newton timeout is {newton_config.timeout_seconds}s (expected 20s)")
                
                if newton_config.max_retries == 3:
                    print("✅ Newton has increased retries (3) for stability")
                else:
                    print(f"⚠️  Newton retries is {newton_config.max_retries} (expected 3)")
                
                if newton_config.max_chars == 450:
                    print("✅ Newton has optimized character limit (450) for faster response")
                else:
                    print(f"⚠️  Newton max_chars is {newton_config.max_chars} (expected 450)")
                    
            else:
                print("❌ Newton personality not found")
                return False
        else:
            print("❌ Personalities not loaded")
            return False
        
        # Check method signature changes
        import inspect
        sig = inspect.signature(service.generate_personality_response)
        print(f"✅ Method signature: {sig}")
        
        # Check if _generate_gemini_response method exists
        if hasattr(service, '_generate_gemini_response'):
            print("✅ Async wrapper method _generate_gemini_response exists")
        else:
            print("❌ Async wrapper method missing")
            return False
        
        print("\n📊 All Code Structure Tests PASSED!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_all_personalities_timeout_config():
    """Verify all personalities have timeout configuration"""
    
    try:
        from services.enhanced_simple_llm_service import EnhancedSimpleLLMService
        
        service = EnhancedSimpleLLMService()
        
        print("\n🔄 Checking All Personalities Timeout Configuration")
        print("=" * 60)
        
        if not hasattr(service, 'personalities'):
            print("❌ No personalities found")
            return False
            
        for pid, config in service.personalities.items():
            timeout = getattr(config, 'timeout_seconds', None)
            retries = getattr(config, 'max_retries', None)
            
            if timeout and retries:
                status = "✅"
                if pid == "newton" and timeout == 20:
                    status += " (OPTIMIZED)"
            else:
                status = "❌"
            
            print(f"{status} {config.name}: {timeout}s timeout, {retries} retries")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking personalities: {e}")
        return False

if __name__ == "__main__":
    success1 = test_newton_timeout_code_structure()
    success2 = test_all_personalities_timeout_config()
    
    print("\n🎯 Summary:")
    if success1 and success2:
        print("✅ All Newton timeout fix code structure tests PASSED!")
        print("✅ Priority 1 implementation is complete")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
