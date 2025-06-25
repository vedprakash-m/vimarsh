#!/usr/bin/env python3
"""
Simple test script for TTS optimizer
"""

import asyncio
import sys
from pathlib import Path

# Add the voice module to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test if all imports work"""
    try:
        from tts_optimizer import (
            SpiritualTTSOptimizer,
            TTSConfig,
            SpiritualTone,
            VoiceCharacteristic,
            create_spiritual_tts_optimizer
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        from tts_optimizer import SpiritualTTSOptimizer, SpiritualTone
        
        # Create optimizer
        optimizer = SpiritualTTSOptimizer()
        print("✅ Optimizer created successfully")
        
        # Test content detection
        text = "Krishna teaches dharma"
        analysis = optimizer.detect_spiritual_content(text)
        print(f"✅ Content analysis successful: {len(analysis['sanskrit_terms'])} Sanskrit terms detected")
        
        # Test SSML generation
        ssml = optimizer.generate_ssml_markup(text, analysis)
        print(f"✅ SSML generation successful: {len(ssml)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_async_processing():
    """Test async processing"""
    try:
        from tts_optimizer import SpiritualTTSOptimizer
        
        optimizer = SpiritualTTSOptimizer()
        text = "Om Namah Shivaya is a sacred mantra"
        
        result = await optimizer.process_spiritual_content(text)
        print(f"✅ Async processing successful: {result.sanskrit_terms_count} Sanskrit terms")
        print(f"   Duration estimate: {result.audio_duration_estimate:.2f}s")
        print(f"   Spiritual appropriateness: {result.spiritual_appropriateness:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Async processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Running TTS Optimizer Tests")
    print("=" * 40)
    
    success = True
    
    # Test imports
    print("\n1. Testing imports...")
    success &= test_imports()
    
    # Test basic functionality
    print("\n2. Testing basic functionality...")
    success &= test_basic_functionality()
    
    # Test async processing
    print("\n3. Testing async processing...")
    success &= asyncio.run(test_async_processing())
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! TTS optimizer is working correctly.")
    else:
        print("❌ Some tests failed. Check the implementation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
