#!/usr/bin/env python3
"""
Demo script for Spiritual TTS Optimization

This script demonstrates the TTS optimization capabilities for spiritual content,
including Sanskrit pronunciation, tone adjustment, and sacred content handling.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add the voice module to Python path
sys.path.append(str(Path(__file__).parent))

from tts_optimizer import (
    SpiritualTTSOptimizer,
    TTSConfig,
    SpiritualTone,
    VoiceCharacteristic,
    SanskritPronunciation,
    create_spiritual_tts_optimizer
)


def print_banner():
    """Print demo banner"""
    print("\n" + "="*70)
    print("🕉️  VIMARSH AI AGENT - SPIRITUAL TTS OPTIMIZATION DEMO  🕉️")
    print("="*70)
    print("Demonstrating advanced TTS optimization for spiritual content")
    print("Including Sanskrit pronunciation, sacred tone adjustment,")
    print("and reverent delivery of spiritual teachings.")
    print("="*70 + "\n")


def print_section(title: str):
    """Print section header"""
    print(f"\n📖 {title}")
    print("-" * (len(title) + 4))


def print_result(result):
    """Print processing result in a formatted way"""
    print(f"✨ Original Text: {result.original_text[:100]}...")
    print(f"🎵 Processed SSML: {len(result.processed_text)} characters")
    print(f"⏱️  Estimated Duration: {result.audio_duration_estimate:.2f} seconds")
    print(f"🔤 Sanskrit Terms: {result.sanskrit_terms_count}")
    print(f"🙏 Spiritual Phrases: {result.spiritual_phrases_count}")
    print(f"🎭 Tone Adjustments: {', '.join(result.tone_adjustments)}")
    print(f"📚 Pronunciation Adjustments: {len(result.pronunciation_adjustments)}")
    
    if result.pronunciation_adjustments:
        print("   " + ", ".join(result.pronunciation_adjustments[:3]))
    
    print(f"📊 Quality Scores:")
    print(f"   Readability: {result.readability_score:.2f}")
    print(f"   Spiritual Appropriateness: {result.spiritual_appropriateness:.2f}")
    print(f"   Pronunciation Accuracy: {result.pronunciation_accuracy:.2f}")
    print(f"⚡ Processing Time: {result.processing_time_ms}ms")


def show_ssml_preview(ssml_text: str, max_length: int = 300):
    """Show a preview of SSML markup"""
    print(f"\n🔧 SSML Preview:")
    if len(ssml_text) > max_length:
        preview = ssml_text[:max_length] + "..."
    else:
        preview = ssml_text
    
    print(f"   {preview}")


async def demo_basic_optimization():
    """Demonstrate basic TTS optimization"""
    print_section("Basic Spiritual Content Optimization")
    
    optimizer = SpiritualTTSOptimizer()
    
    test_texts = [
        "Krishna teaches us about dharma and karma in the Bhagavad Gita.",
        "The practice of yoga leads to moksha through understanding atman.",
        "Om Namah Shivaya is a powerful mantra for spiritual transformation.",
        "Hanuman shows us the path of devotion and service to the divine."
    ]
    
    for text in test_texts:
        print(f"\n🔍 Processing: {text}")
        
        start_time = time.time()
        result = await optimizer.process_spiritual_content(text)
        processing_time = time.time() - start_time
        
        print(f"✅ Completed in {processing_time:.3f}s")
        print_result(result)
        
        # Show SSML preview for first example
        if text == test_texts[0]:
            show_ssml_preview(result.processed_text)


async def demo_tone_variations():
    """Demonstrate different spiritual tones"""
    print_section("Spiritual Tone Variations")
    
    base_text = "May Krishna bless you with peace, wisdom, and devotion on your spiritual journey."
    
    tones = [
        SpiritualTone.REVERENT,
        SpiritualTone.COMPASSIONATE,
        SpiritualTone.WISE,
        SpiritualTone.PEACEFUL,
        SpiritualTone.DEVOTIONAL,
        SpiritualTone.JOYFUL
    ]
    
    for tone in tones:
        print(f"\n🎭 Tone: {tone.value.upper()}")
        
        config = TTSConfig(spiritual_tone=tone)
        optimizer = SpiritualTTSOptimizer(config)
        
        result = await optimizer.process_spiritual_content(base_text)
        
        print(f"   Duration: {result.audio_duration_estimate:.2f}s")
        print(f"   Appropriateness: {result.spiritual_appropriateness:.2f}")
        
        # Show tone-specific characteristics
        tone_pattern = optimizer.tone_patterns[tone]
        print(f"   Rate: {tone_pattern['speaking_rate']}")
        print(f"   Pitch Adjust: {tone_pattern['pitch_adjust']:+.2f}")
        print(f"   Pause Multiplier: {tone_pattern['pause_multiplier']}")


async def demo_mantra_processing():
    """Demonstrate mantra-specific processing"""
    print_section("Sacred Mantra Processing")
    
    mantras = [
        "Om",
        "Om Namah Shivaya", 
        "Hare Krishna Hare Krishna Krishna Krishna Hare Hare",
        "Om Mani Padme Hum",
        "Om Shanti Shanti Shanti"
    ]
    
    # Configure for mantra emphasis
    config = TTSConfig(
        spiritual_tone=SpiritualTone.REVERENT,
        slower_for_mantras=True,
        emphasize_sanskrit_terms=True,
        reverent_deity_names=True,
        breath_pauses=True
    )
    
    optimizer = SpiritualTTSOptimizer(config)
    
    for mantra in mantras:
        print(f"\n🕉️  Mantra: {mantra}")
        
        result = await optimizer.process_spiritual_content(mantra)
        
        # Show mantra-specific analysis
        analysis = optimizer.detect_spiritual_content(mantra)
        
        print(f"   Detected as: {analysis['content_type']}")
        print(f"   Reverence Level: {analysis['reverence_level']:.2f}")
        print(f"   Duration: {result.audio_duration_estimate:.2f}s")
        print(f"   Mantras Detected: {len(analysis['mantras'])}")


async def demo_scriptural_quotes():
    """Demonstrate scriptural quote processing"""
    print_section("Scriptural Quote Processing")
    
    quotes = [
        """Krishna says in the Bhagavad Gita: "You have the right to perform your 
        prescribed duty, but you are not entitled to the fruits of your actions.""",
        
        """As the scriptures tell us, "Tat tvam asi" - That thou art. This profound 
        teaching reveals our true divine nature.""",
        
        """The Upanishads declare: "Sarvam khalvidam brahma" - All this is indeed 
        Brahman. Everything is one universal consciousness."""
    ]
    
    config = TTSConfig(
        spiritual_tone=SpiritualTone.WISE,
        pause_after_quotes=True,
        citation_formatting=True
    )
    
    optimizer = SpiritualTTSOptimizer(config)
    
    for quote in quotes:
        print(f"\n📜 Processing scriptural quote...")
        
        result = await optimizer.process_spiritual_content(quote)
        
        # Analyze citation detection
        analysis = optimizer.detect_spiritual_content(quote)
        
        print(f"   Citations Detected: {len(analysis['citations'])}")
        print(f"   Sanskrit Terms: {result.sanskrit_terms_count}")
        print(f"   Content Type: {analysis['content_type']}")
        print(f"   Duration: {result.audio_duration_estimate:.2f}s")
        print(f"   Spiritual Appropriateness: {result.spiritual_appropriateness:.2f}")


async def demo_pronunciation_optimization():
    """Demonstrate Sanskrit pronunciation optimization"""
    print_section("Sanskrit Pronunciation Optimization")
    
    text = """In yoga philosophy, we learn about chakras, kundalini, pranayama, 
    and asanas. The practice of dharma leads to good karma. Through bhakti and 
    jnana, we can achieve moksha and understand our true atman nature."""
    
    print(f"📝 Text: {text}")
    
    optimizer = SpiritualTTSOptimizer()
    
    # Show pronunciation mappings
    analysis = optimizer.detect_spiritual_content(text)
    
    print(f"\n🔤 Sanskrit Terms Detected: {len(analysis['sanskrit_terms'])}")
    for term_info in analysis['sanskrit_terms']:
        term = term_info['term']
        pronunciation = term_info['pronunciation']
        print(f"   {term} → {pronunciation}")
    
    result = await optimizer.process_spiritual_content(text)
    print(f"\n✨ Processing Results:")
    print(f"   Pronunciation Accuracy: {result.pronunciation_accuracy:.2f}")
    print(f"   Total Adjustments: {len(result.pronunciation_adjustments)}")


async def demo_voice_characteristics():
    """Demonstrate different voice characteristics"""
    print_section("Voice Characteristic Variations")
    
    text = "Let us journey together on the path of spiritual wisdom and divine love."
    
    characteristics = [
        VoiceCharacteristic.WARM,
        VoiceCharacteristic.GENTLE,
        VoiceCharacteristic.WISE,
        VoiceCharacteristic.PEACEFUL
    ]
    
    for char in characteristics:
        print(f"\n🎤 Voice Characteristic: {char.value.upper()}")
        
        optimizer = create_spiritual_tts_optimizer(
            tone=SpiritualTone.COMPASSIONATE,
            characteristic=char
        )
        
        result = await optimizer.process_spiritual_content(text)
        
        print(f"   Spiritual Appropriateness: {result.spiritual_appropriateness:.2f}")
        print(f"   Duration: {result.audio_duration_estimate:.2f}s")


async def demo_comprehensive_spiritual_guidance():
    """Demonstrate comprehensive spiritual guidance processing"""
    print_section("Comprehensive Spiritual Guidance")
    
    guidance = """
    Welcome, dear seeker, to this moment of spiritual reflection. 
    
    Begin by taking three deep breaths and chanting Om three times. Feel the sacred 
    vibration resonate within your being.
    
    As Krishna teaches us in the Bhagavad Gita, we must perform our dharma with 
    dedication while remaining unattached to the results. This is the essence of 
    karma yoga - the path of selfless action.
    
    Remember that your true nature is atman, the eternal soul that is one with 
    Brahman, the universal consciousness. Through the practice of yoga, pranayama, 
    and meditation, we can transcend the illusions of samsara and achieve moksha.
    
    With devotion and surrender, chant with me: Om Namah Shivaya. Let this sacred 
    mantra purify your heart and mind.
    
    May Hanuman give you strength, may Ganesha remove all obstacles, and may the 
    divine Mother Durga protect you on your spiritual journey.
    
    Om Shanti Shanti Shanti. May peace be with you always.
    """
    
    print("🙏 Processing comprehensive spiritual guidance...")
    
    # Use optimal settings for spiritual guidance
    config = TTSConfig(
        spiritual_tone=SpiritualTone.COMPASSIONATE,
        voice_characteristic=VoiceCharacteristic.WARM,
        emphasize_sanskrit_terms=True,
        reverent_deity_names=True,
        slower_for_mantras=True,
        pause_after_quotes=True,
        breath_pauses=True,
        natural_phrasing=True
    )
    
    optimizer = SpiritualTTSOptimizer(config)
    
    start_time = time.time()
    result = await optimizer.process_spiritual_content(guidance)
    processing_time = time.time() - start_time
    
    print(f"\n✨ Comprehensive Processing Results:")
    print(f"   Total Processing Time: {processing_time:.2f}s")
    print(f"   Original Length: {len(guidance)} characters")
    print(f"   Processed Length: {len(result.processed_text)} characters")
    print(f"   Estimated Audio Duration: {result.audio_duration_estimate:.1f}s ({result.audio_duration_estimate/60:.1f} minutes)")
    print(f"   Sanskrit Terms: {result.sanskrit_terms_count}")
    print(f"   Spiritual Phrases: {result.spiritual_phrases_count}")
    print(f"   Quality Scores:")
    print(f"     Readability: {result.readability_score:.2f}")
    print(f"     Spiritual Appropriateness: {result.spiritual_appropriateness:.2f}")
    print(f"     Pronunciation Accuracy: {result.pronunciation_accuracy:.2f}")
    
    # Show content analysis
    analysis = optimizer.detect_spiritual_content(guidance)
    print(f"\n📊 Content Analysis:")
    print(f"   Content Type: {analysis['content_type']}")
    print(f"   Dominant Tone: {analysis['dominant_tone'].value}")
    print(f"   Reverence Level: {analysis['reverence_level']:.2f}")
    print(f"   Deity References: {len(analysis['deity_references'])}")
    print(f"   Mantras: {len(analysis['mantras'])}")
    print(f"   Citations: {len(analysis['citations'])}")


async def demo_processing_statistics():
    """Demonstrate processing statistics tracking"""
    print_section("Processing Statistics")
    
    optimizer = SpiritualTTSOptimizer()
    
    # Process multiple texts to generate statistics
    test_texts = [
        "Krishna is the supreme divine being.",
        "Practice yoga and pranayama daily.",
        "Om Namah Shivaya brings peace.",
        "Dharma guides our righteous actions.",
        "Meditation leads to self-realization."
    ]
    
    print("🔄 Processing multiple texts for statistics...")
    
    for text in test_texts:
        await optimizer.process_spiritual_content(text)
    
    stats = optimizer.get_processing_statistics()
    
    print(f"\n📈 Processing Statistics:")
    print(f"   Total Processed: {stats['total_processed']}")
    print(f"   Total Duration: {stats['total_duration']:.1f}s")
    print(f"   Average Duration: {stats.get('average_duration', 0):.2f}s per text")
    print(f"   Average Processing Time: {stats['average_processing_time']:.1f}ms")
    print(f"   Sanskrit Terms Processed: {stats['sanskrit_terms_processed']}")
    print(f"   Average Sanskrit Terms: {stats.get('average_sanskrit_terms', 0):.1f} per text")
    print(f"   Tone Adjustments Applied: {stats['tone_adjustments_applied']}")
    print(f"   Pronunciation Corrections: {stats['pronunciation_corrections']}")


async def main():
    """Main demo function"""
    print_banner()
    
    try:
        await demo_basic_optimization()
        await demo_tone_variations()
        await demo_mantra_processing()
        await demo_scriptural_quotes()
        await demo_pronunciation_optimization()
        await demo_voice_characteristics()
        await demo_comprehensive_spiritual_guidance()
        await demo_processing_statistics()
        
        print("\n" + "="*70)
        print("🎉 SPIRITUAL TTS OPTIMIZATION DEMO COMPLETED SUCCESSFULLY! 🎉")
        print("="*70)
        print("The TTS optimizer is ready for spiritual content delivery.")
        print("Features demonstrated:")
        print("  ✅ Sanskrit pronunciation optimization")
        print("  ✅ Spiritual tone adjustments")
        print("  ✅ Sacred mantra handling")
        print("  ✅ Scriptural quote processing")
        print("  ✅ Deity name reverence")
        print("  ✅ Voice characteristic variations")
        print("  ✅ Comprehensive spiritual guidance")
        print("  ✅ Processing statistics tracking")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
