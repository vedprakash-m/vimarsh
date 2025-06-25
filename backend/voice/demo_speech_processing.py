"""
Demo Script for Speech Processing Components

This script demonstrates the speech processing functionality of the Vimarsh AI Agent,
including Web Speech API integration and spiritual content optimization.
"""

import asyncio
import logging
import time
from datetime import datetime

from speech_processor import (
    SpeechProcessor,
    VoiceConfig,
    VoiceLanguage,
    SpeechQuality,
    create_spiritual_speech_processor
)
from web_speech_integration import (
    WebSpeechIntegration,
    WebSpeechConfig,
    WebSpeechEvent,
    create_web_speech_integration,
    get_supported_languages
)


async def demo_speech_processor():
    """Demonstrate speech processor functionality"""
    
    print("🎤 Speech Processor Demo")
    print("=" * 50)
    
    # Create spiritual speech processor
    processor = create_spiritual_speech_processor(
        language=VoiceLanguage.ENGLISH,
        quality=SpeechQuality.HIGH
    )
    
    print(f"✅ Created speech processor with config:")
    print(f"   Language: {processor.config.language.value}")
    print(f"   Quality: {processor.config.quality.value}")
    print(f"   Sanskrit Support: {processor.config.sanskrit_support}")
    print(f"   Spiritual Vocabulary Boost: {processor.config.spiritual_vocabulary_boost}")
    
    # Demonstrate vocabulary loading
    print(f"\n📚 Loaded Spiritual Vocabulary:")
    print(f"   Sanskrit Terms: {len(processor.sanskrit_terms)}")
    print(f"   Deity Names: {len(processor.deity_names)}")
    print(f"   Mantras: {len(processor.mantras)}")
    print(f"   Spiritual Vocabulary: {len(processor.spiritual_vocabulary)}")
    
    # Show some examples
    print(f"\n📖 Example Sanskrit Terms:")
    for term, variations in list(processor.sanskrit_terms.items())[:5]:
        print(f"   {term}: {', '.join(variations[:3])}")
    
    print(f"\n🕉️  Example Deity Names:")
    for deity, variations in list(processor.deity_names.items())[:3]:
        print(f"   {deity}: {', '.join(variations[:3])}")
    
    # Demonstrate recognition workflow
    print(f"\n🎯 Recognition Workflow Demo:")
    
    # Start recognition session
    session_id = await processor.start_recognition("demo_session")
    print(f"   ✅ Started recognition session: {session_id}")
    
    # Simulate processing multiple audio samples
    print(f"   🔄 Processing audio samples...")
    
    for i in range(3):
        # Create dummy audio data
        audio_data = b'\x00' * (1000 + i * 500)
        
        print(f"      Sample {i+1}: {len(audio_data)} bytes")
        result = await processor.process_audio_data(audio_data, 16000)
        
        print(f"         Transcript: '{result.transcript}'")
        print(f"         Confidence: {result.confidence:.2f}")
        print(f"         Processing Time: {result.processing_time_ms}ms")
        
        if result.spiritual_terms:
            print(f"         Spiritual Terms: {', '.join(result.spiritual_terms)}")
        if result.deity_references:
            print(f"         Deity References: {', '.join(result.deity_references)}")
        if result.detected_mantras:
            print(f"         Detected Mantras: {', '.join(result.detected_mantras)}")
        
        print()
        await asyncio.sleep(0.5)
    
    # Stop recognition
    final_result = await processor.stop_recognition()
    print(f"   ✅ Stopped recognition session")
    
    # Show statistics
    stats = processor.get_recognition_stats()
    print(f"\n📊 Recognition Statistics:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Successful: {stats['successful_recognitions']}")
    print(f"   Failed: {stats['failed_recognitions']}")
    print(f"   Success Rate: {stats['success_rate']:.2%}")
    print(f"   Average Confidence: {stats['average_confidence']:.2f}")
    print(f"   Average Processing Time: {stats['average_processing_time']:.1f}ms")
    
    # Demonstrate optimization
    print(f"\n⚡ Spiritual Content Optimization:")
    optimization = await processor.optimize_for_spiritual_content()
    print(f"   Spiritual Content Ratio: {optimization['spiritual_content_ratio']:.2%}")
    print(f"   Sanskrit Content Ratio: {optimization['sanskrit_content_ratio']:.2%}")
    print(f"   Average Confidence: {optimization['average_confidence']:.2f}")
    
    if optimization['recommendations']:
        print(f"   Recommendations:")
        for rec in optimization['recommendations']:
            print(f"     • {rec}")
    
    return processor


async def demo_web_speech_integration():
    """Demonstrate Web Speech API integration"""
    
    print("\n🌐 Web Speech API Integration Demo")
    print("=" * 50)
    
    # Show supported languages
    languages = get_supported_languages()
    print(f"📢 Supported Languages ({len(languages)}):")
    for code, name in list(languages.items())[:5]:
        print(f"   {code}: {name}")
    
    # Create Web Speech integration
    integration = await create_web_speech_integration(
        language="en-US",
        spiritual_optimization=True
    )
    
    print(f"\n✅ Created Web Speech integration:")
    status = integration.get_integration_status()
    print(f"   Initialized: {status['initialized']}")
    print(f"   Language: {status['current_config']['language']}")
    print(f"   Spiritual Grammar: {status['current_config']['spiritual_grammar_enabled']}")
    
    # Show spiritual grammar
    print(f"\n📝 Spiritual Grammar Rules:")
    sample_terms = ['dharma', 'krishna', 'bhagavad_gita', 'om']
    for term in sample_terms:
        variations = integration.get_term_variations(term)
        if variations:
            print(f"   {term}: {', '.join(variations[:4])}")
    
    # Show pronunciation guide
    print(f"\n🗣️  Pronunciation Guide:")
    sample_pronunciations = ['dharma', 'krishna', 'yoga', 'namaste']
    for term in sample_pronunciations:
        pronunciation = integration.get_pronunciation_guide(term)
        if pronunciation:
            print(f"   {term}: {pronunciation}")
    
    # Set up event handlers
    print(f"\n🎧 Setting up event handlers...")
    
    recognition_results = []
    
    async def on_result(event, data):
        recognition_results.append(data)
        print(f"   📝 Recognition result: '{data.transcript}' (confidence: {data.confidence:.2f})")
        if data.spiritual_terms:
            print(f"      🕉️  Spiritual terms: {', '.join(data.spiritual_terms)}")
    
    async def on_start(event, data):
        print(f"   🎬 Recognition started")
    
    async def on_end(event, data):
        print(f"   🛑 Recognition ended")
    
    async def on_error(event, data):
        print(f"   ❌ Recognition error: {data}")
    
    # Add event handlers
    integration.add_event_handler(WebSpeechEvent.RESULT, on_result)
    integration.add_event_handler(WebSpeechEvent.START, on_start)
    integration.add_event_handler(WebSpeechEvent.END, on_end)
    integration.add_event_handler(WebSpeechEvent.ERROR, on_error)
    
    # Demonstrate recognition
    print(f"\n🎤 Starting recognition demo...")
    success = await integration.start_recognition()
    
    if success:
        print(f"   ✅ Recognition started successfully")
        
        # Let it run for a few seconds
        await asyncio.sleep(3)
        
        # Stop recognition
        final_result = await integration.stop_recognition()
        print(f"   ✅ Recognition stopped")
        
        if final_result:
            print(f"   📋 Final result: '{final_result.transcript}'")
    
    # Show integration statistics
    final_status = integration.get_integration_status()
    print(f"\n📊 Integration Statistics:")
    print(f"   Total Results: {final_status['total_results']}")
    print(f"   Spiritual Results: {final_status['spiritual_results']}")
    print(f"   Spiritual Ratio: {final_status['spiritual_ratio']:.2%}")
    
    return integration


async def demo_spiritual_content_analysis():
    """Demonstrate spiritual content analysis"""
    
    print("\n🕉️  Spiritual Content Analysis Demo")
    print("=" * 50)
    
    processor = create_spiritual_speech_processor()
    
    # Test spiritual queries
    test_queries = [
        "What is the meaning of dharma in the Bhagavad Gita?",
        "How can I develop devotion to Lord Krishna?",
        "Please explain karma yoga and selfless action",
        "What does Om Namah Shivaya mean?",
        "How do I practice meditation according to Patanjali?",
        "Tell me about the path to moksha or liberation",
        "What is the nature of the eternal soul or atman?",
        "How can I serve humanity through spiritual practice?",
        "What does surrender mean in bhakti yoga?",
        "Please guide me on the spiritual path to enlightenment"
    ]
    
    print(f"🧪 Analyzing {len(test_queries)} spiritual queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: '{query}'")
        
        # Create mock recognition result
        from speech_processor import RecognitionResult
        result = RecognitionResult(
            transcript=query,
            confidence=0.85,
            language=VoiceLanguage.ENGLISH
        )
        
        # Enhance with spiritual analysis
        await processor._enhance_spiritual_recognition(result)
        
        print(f"   Analysis Results:")
        print(f"     Contains Sanskrit: {result.contains_sanskrit}")
        print(f"     Confidence Boost: {result.confidence:.2f} (was 0.85)")
        
        if result.spiritual_terms:
            print(f"     Spiritual Terms: {', '.join(result.spiritual_terms)}")
        
        if result.deity_references:
            print(f"     Deity References: {', '.join(result.deity_references)}")
        
        if result.detected_mantras:
            print(f"     Detected Mantras: {', '.join(result.detected_mantras)}")
        
        # Brief pause for readability
        await asyncio.sleep(0.2)
    
    print(f"\n✅ Spiritual content analysis complete!")


async def demo_error_handling():
    """Demonstrate error handling capabilities"""
    
    print("\n🛡️  Error Handling Demo")
    print("=" * 50)
    
    processor = SpeechProcessor()
    
    # Test error scenarios
    error_scenarios = [
        ("Empty audio data", b''),
        ("Invalid audio format", b'invalid'),
        ("Very short audio", b'\x00' * 10),
    ]
    
    print(f"🧪 Testing {len(error_scenarios)} error scenarios...")
    
    for scenario_name, audio_data in error_scenarios:
        print(f"\n🔍 Testing: {scenario_name}")
        
        try:
            result = await processor.process_audio_data(audio_data)
            
            print(f"   Status: {result.status.value}")
            print(f"   Confidence: {result.confidence}")
            
            if result.error_message:
                print(f"   Error: {result.error_message}")
            else:
                print(f"   Transcript: '{result.transcript}'")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Show error statistics
    stats = processor.get_recognition_stats()
    print(f"\n📊 Error Statistics:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Failed Requests: {stats['failed_recognitions']}")
    print(f"   Failure Rate: {stats['failure_rate']:.2%}")


async def main():
    """Main demo function"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Vimarsh AI Agent - Voice Interface Demo")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run speech processor demo
        processor = await demo_speech_processor()
        
        # Run Web Speech integration demo
        integration = await demo_web_speech_integration()
        
        # Run spiritual content analysis demo
        await demo_spiritual_content_analysis()
        
        # Run error handling demo
        await demo_error_handling()
        
        print("\n🎉 All demos completed successfully!")
        print("=" * 60)
        
        # Final summary
        final_stats = processor.get_recognition_stats()
        integration_status = integration.get_integration_status()
        
        print(f"📈 Final Statistics:")
        print(f"   Speech Processor:")
        print(f"     Total Requests: {final_stats['total_requests']}")
        print(f"     Success Rate: {final_stats['success_rate']:.2%}")
        print(f"     Avg Confidence: {final_stats['average_confidence']:.2f}")
        print(f"   Web Speech Integration:")
        print(f"     Total Results: {integration_status['total_results']}")
        print(f"     Spiritual Ratio: {integration_status['spiritual_ratio']:.2%}")
        
        print(f"\n✅ Voice interface system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
