#!/usr/bin/env python3
"""
Demo script for multilingual voice support in Vimarsh platform.
Tests English/Hindi language switching and cultural context adaptation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.multilingual import MultilingualVoiceManager, Language, VoiceProfile, Accent, VoiceGender
from voice.parameter_adapter import VoiceSettings
import asyncio

async def demo_multilingual_voice():
    """Demonstrate multilingual voice capabilities."""
    print("=== Vimarsh Multilingual Voice Support Demo ===\n")
    
    # Initialize the multilingual voice manager
    voice_manager = MultilingualVoiceManager()
    
    # Test 1: Language Detection and Preference
    print("1. Language Detection Test")
    print("-" * 30)
    
    test_texts = [
        "What is the meaning of dharma?",
        "धर्म का अर्थ क्या है?",
        "ॐ शान्ति शान्ति शान्तिः",
        "Please explain the concept of moksha and karma",
        "कृपया मोक्ष की अवधारणा समझाएं"
    ]
    
    for text in test_texts:
        detected = voice_manager.detect_language_preference(text)
        print(f"Text: {text}")
        print(f"Preferred Language: {detected.value}")
        print()
    
    # Test 2: Voice Initialization for Different Languages
    print("2. Voice Initialization")
    print("-" * 30)
    
    # Initialize English voice
    en_profile = voice_manager.initialize_voice(Language.ENGLISH)
    print(f"English Voice Profile:")
    print(f"  Voice: {en_profile.voice_name}")
    print(f"  Language: {en_profile.language.value}")
    print(f"  Accent: {en_profile.accent.value}")
    print(f"  Gender: {en_profile.gender.value}")
    print(f"  Sanskrit Support: {en_profile.supports_sanskrit}")
    print()
    
    # Initialize Hindi voice
    hi_profile = voice_manager.initialize_voice(Language.HINDI)
    print(f"Hindi Voice Profile:")
    print(f"  Voice: {hi_profile.voice_name}")
    print(f"  Language: {hi_profile.language.value}")
    print(f"  Accent: {hi_profile.accent.value}")
    print(f"  Gender: {hi_profile.gender.value}")
    print(f"  Sanskrit Support: {hi_profile.supports_sanskrit}")
    print()
    
    # Test 3: Speech Synthesis Preparation
    print("3. Speech Synthesis Preparation")
    print("-" * 30)
    
    sample_texts = [
        ("Hello, let's learn about dharma and karma", Language.ENGLISH),
        ("नमस्ते, आइए धर्म और कर्म के बारे में सीखते हैं", Language.HINDI),
        ("Om Namah Shivaya is a powerful mantra", Language.ENGLISH),
        ("ॐ नमः शिवाय एक शक्तिशाली मंत्र है", Language.HINDI)
    ]
    
    for text, lang in sample_texts:
        synthesis_data = voice_manager.prepare_speech_synthesis(text, lang)
        print(f"Original: {text}")
        print(f"Language: {lang.value}")
        print(f"Processed: {synthesis_data['processed_text']}")
        print(f"Voice: {synthesis_data['voice_profile']['voice_name']}")
        print()
    
    # Test 4: Sanskrit Pronunciation Guide
    print("4. Sanskrit Pronunciation Guide")
    print("-" * 30)
    
    sanskrit_terms = ["om", "krishna", "dharma", "karma", "moksha", "yoga"]
    
    for term in sanskrit_terms:
        en_guide = voice_manager.get_sanskrit_pronunciation_guide(term, Language.ENGLISH)
        hi_guide = voice_manager.get_sanskrit_pronunciation_guide(term, Language.HINDI)
        
        print(f"Term: {term}")
        if en_guide:
            print(f"  English Guide: {en_guide}")
        if hi_guide:
            print(f"  Hindi Guide: {hi_guide}")
        print()
    
    # Test 5: Language Capabilities
    print("5. Language Capabilities")
    print("-" * 30)
    
    capabilities = voice_manager.get_language_capabilities()
    for lang, caps in capabilities.items():
        print(f"{lang.upper()} Language:")
        print(f"  Supported: {caps['supported']}")
        print(f"  Voice Count: {caps['voice_count']}")
        print(f"  Sanskrit Support: {caps['sanskrit_support']}")
        print(f"  Available Accents: {caps['available_accents']}")
        print(f"  Available Genders: {caps['available_genders']}")
        print()
    
    # Test 6: Language Switching
    print("6. Language Switching Test")
    print("-" * 30)
    
    # Start with English
    voice_manager.initialize_voice(Language.ENGLISH)
    print(f"Current Language: {voice_manager.current_language.value}")
    
    # Switch to Hindi
    success = voice_manager.switch_language(Language.HINDI)
    print(f"Switch to Hindi: {'Success' if success else 'Failed'}")
    print(f"Current Language: {voice_manager.current_language.value}")
    
    # Switch back to English
    success = voice_manager.switch_language(Language.ENGLISH)
    print(f"Switch to English: {'Success' if success else 'Failed'}")
    print(f"Current Language: {voice_manager.current_language.value}")
    print()
    
    # Test 7: Content-Based Language Selection
    print("7. Content-Based Language Selection")
    print("-" * 30)
    
    mixed_content = [
        "The ancient concept of dharma",
        "प्राचीन धर्म की अवधारणा",
        "Krishna teaches us about righteousness",
        "कृष्ण हमें धार्मिकता के बारे में सिखाते हैं",
        "Om meditation brings peace",
        "ॐ ध्यान शांति लाता है"
    ]
    
    for content in mixed_content:
        preferred_lang = voice_manager.detect_language_preference(content)
        synthesis_data = voice_manager.prepare_speech_synthesis(content, preferred_lang)
        
        print(f"Content: {content}")
        print(f"Auto-detected Language: {preferred_lang.value}")
        print(f"Selected Voice: {synthesis_data['voice_profile']['voice_name']}")
        print()
    
    print("=== Demo Completed Successfully ===")

if __name__ == "__main__":
    asyncio.run(demo_multilingual_voice())
