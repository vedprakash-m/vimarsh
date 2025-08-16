#!/usr/bin/env python3
"""
Diagnostic script to test Gemini API configuration
"""
import os
import sys

# Import centralized AI model configuration
try:
    from config.ai_models import AI_CONFIG
    GEMINI_MODEL = AI_CONFIG.gemini_generation_model
except ImportError:
    # Fallback if config not available  
    GEMINI_MODEL = "models/gemini-2.5-flash"

def test_environment_variables():
    """Test environment variable configuration"""
    print("=== ENVIRONMENT VARIABLES ===")
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    google_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    
    print(f"GEMINI_API_KEY: {'SET' if gemini_key else 'NOT SET'}")
    print(f"GOOGLE_GEMINI_API_KEY: {'SET' if google_key else 'NOT SET'}")
    
    if gemini_key:
        print(f"GEMINI_API_KEY length: {len(gemini_key)}")
        print(f"GEMINI_API_KEY starts with: {gemini_key[:10]}...")
    
    if google_key:
        print(f"GOOGLE_GEMINI_API_KEY length: {len(google_key)}")
        print(f"GOOGLE_GEMINI_API_KEY starts with: {google_key[:10]}...")
    
    return gemini_key or google_key

def test_gemini_import():
    """Test Google Generative AI import"""
    print("\n=== GOOGLE GENERATIVE AI IMPORT ===")
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
        return genai
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        return None

def test_gemini_configuration(genai, api_key):
    """Test Gemini API configuration"""
    print("\n=== GEMINI CONFIGURATION ===")
    
    if not genai:
        print("❌ Genai not available")
        return False
    
    if not api_key:
        print("❌ No API key available")
        return False
    
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
        return True
    except Exception as e:
        print(f"❌ Gemini configuration failed: {e}")
        return False

def test_simple_generation(genai, api_key):
    """Test simple content generation"""
    print("\n=== SIMPLE GENERATION TEST ===")
    
    if not genai or not api_key:
        print("❌ Prerequisites not met")
        return False
    
    try:
        # Configure first
        genai.configure(api_key=api_key)
        
        # Try simple generation
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content("Hello, world!")
        
        if response and response.text:
            print(f"✅ Generation successful: {response.text[:100]}...")
            return True
        else:
            print("❌ Generation returned no content")
            return False
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("GEMINI API DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Test 1: Environment Variables
    api_key = test_environment_variables()
    
    # Test 2: Import
    genai = test_gemini_import()
    
    # Test 3: Configuration
    config_success = test_gemini_configuration(genai, api_key)
    
    # Test 4: Simple Generation
    if config_success:
        generation_success = test_simple_generation(genai, api_key)
    else:
        generation_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Environment Variables: {'✅' if api_key else '❌'}")
    print(f"Import: {'✅' if genai else '❌'}")
    print(f"Configuration: {'✅' if config_success else '❌'}")
    print(f"Generation: {'✅' if generation_success else '❌'}")
    
    if generation_success:
        print("\n🎉 Gemini API is working correctly!")
    else:
        print("\n💥 Gemini API has issues that need to be resolved.")

if __name__ == "__main__":
    main()
