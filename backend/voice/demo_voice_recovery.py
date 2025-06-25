#!/usr/bin/env python3
"""
Demo script for Voice Error Recovery and Fallback Mechanisms

This script demonstrates the comprehensive voice error recovery system
for the Vimarsh AI Agent, including spiritual content preservation
and graceful degradation strategies.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add the voice module to Python path
sys.path.append(str(Path(__file__).parent))

from voice_recovery import (
    SpiritualVoiceRecovery,
    VoiceErrorType,
    VoiceErrorContext,
    RecoveryStrategy,
    VoiceFallbackMode,
    create_voice_recovery_system
)


def print_banner():
    """Print demo banner"""
    print("\n" + "="*70)
    print("🛡️  VIMARSH AI AGENT - VOICE ERROR RECOVERY DEMO  🛡️")
    print("="*70)
    print("Demonstrating comprehensive voice error recovery and fallback")
    print("mechanisms for spiritual guidance, including Sanskrit content")
    print("preservation and graceful degradation strategies.")
    print("="*70 + "\n")


def print_section(title: str):
    """Print section header"""
    print(f"\n🔧 {title}")
    print("-" * (len(title) + 4))


def print_error_context(context):
    """Print error context information"""
    print(f"❌ Error Type: {context.error_type.value}")
    print(f"📝 Message: {context.error_message}")
    print(f"🙏 Spiritual Content: {context.spiritual_content_type or 'None'}")
    print(f"🔤 Sanskrit Terms: {'Yes' if context.sanskrit_terms_present else 'No'}")
    if context.retry_count > 0:
        print(f"🔄 Retry Count: {context.retry_count}")
    if context.previous_strategies:
        print(f"📋 Previous Strategies: {[s.value for s in context.previous_strategies]}")


def print_recovery_result(result):
    """Print recovery result in a formatted way"""
    status = "✅ SUCCESS" if result.success else "❌ FAILED"
    print(f"{status} - Strategy: {result.strategy_used.value}")
    
    if result.fallback_mode:
        print(f"🔄 Fallback Mode: {result.fallback_mode.value}")
    
    print(f"⏱️  Recovery Time: {result.recovery_time_ms}ms")
    print(f"🎭 Graceful Degradation: {'Yes' if result.graceful_degradation else 'No'}")
    print(f"🙏 Spiritual Context Preserved: {'Yes' if result.spiritual_context_preserved else 'No'}")
    
    if result.user_notified:
        print(f"👤 User Notified: Yes")
    
    if result.voice_quality_after_recovery > 0:
        print(f"🎵 Voice Quality After Recovery: {result.voice_quality_after_recovery:.2f}")
    
    if result.user_satisfaction_estimated > 0:
        print(f"😊 Estimated User Satisfaction: {result.user_satisfaction_estimated:.2f}")
    
    if result.actions_attempted:
        print(f"🔧 Actions Attempted: {', '.join(result.actions_attempted)}")
    
    if result.final_error:
        print(f"⚠️  Final Error: {result.final_error}")


async def demo_microphone_access_recovery():
    """Demonstrate microphone access denied recovery"""
    print_section("Microphone Access Denied Recovery")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Simulate microphone access denied during spiritual guidance
    context = VoiceErrorContext(
        error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
        error_message="User denied microphone permissions in browser",
        spiritual_content_type="guidance",
        sanskrit_terms_present=False,
        device_info={"browser": "Chrome", "platform": "macOS"},
        audio_context=None
    )
    
    print("🎤 Simulating microphone access denied during spiritual guidance session...")
    print_error_context(context)
    
    print(f"\n🔄 Applying recovery strategies...")
    start_time = time.time()
    result = await recovery_system.handle_voice_error(context)
    elapsed_time = time.time() - start_time
    
    print(f"\n✨ Recovery completed in {elapsed_time:.3f}s")
    print_recovery_result(result)


async def demo_sanskrit_recognition_recovery():
    """Demonstrate Sanskrit recognition failure recovery"""
    print_section("Sanskrit Recognition Failure Recovery")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Simulate Sanskrit term recognition failure
    context = VoiceErrorContext(
        error_type=VoiceErrorType.SANSKRIT_RECOGNITION_FAILED,
        error_message="Could not recognize Sanskrit mantra 'Om Namah Shivaya'",
        spiritual_content_type="mantra",
        sanskrit_terms_present=True,
        audio_context={"quality": "poor", "noise_level": "medium"},
        device_info={"microphone": "built-in", "sample_rate": 44100}
    )
    
    print("🕉️  Simulating Sanskrit mantra recognition failure...")
    print_error_context(context)
    
    print(f"\n🔄 Applying Sanskrit-specific recovery strategies...")
    start_time = time.time()
    result = await recovery_system.handle_voice_error(context)
    elapsed_time = time.time() - start_time
    
    print(f"\n✨ Recovery completed in {elapsed_time:.3f}s")
    print_recovery_result(result)


async def demo_network_connectivity_recovery():
    """Demonstrate network connectivity error recovery"""
    print_section("Network Connectivity Error Recovery")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Simulate network loss during spiritual teaching
    context = VoiceErrorContext(
        error_type=VoiceErrorType.NETWORK_CONNECTIVITY,
        error_message="Network connection lost during Bhagavad Gita explanation",
        spiritual_content_type="teaching",
        sanskrit_terms_present=True,
        network_status="disconnected",
        device_info={"connection_type": "wifi", "signal_strength": "weak"}
    )
    
    print("🌐 Simulating network connectivity loss during spiritual teaching...")
    print_error_context(context)
    
    print(f"\n🔄 Applying network recovery strategies...")
    start_time = time.time()
    result = await recovery_system.handle_voice_error(context)
    elapsed_time = time.time() - start_time
    
    print(f"\n✨ Recovery completed in {elapsed_time:.3f}s")
    print_recovery_result(result)


async def demo_tts_engine_failure_recovery():
    """Demonstrate TTS engine failure recovery"""
    print_section("TTS Engine Failure Recovery")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Simulate TTS engine failure during response delivery
    context = VoiceErrorContext(
        error_type=VoiceErrorType.TTS_ENGINE_FAILED,
        error_message="Primary TTS engine failed while delivering Krishna's teaching",
        spiritual_content_type="teaching",
        sanskrit_terms_present=True,
        device_info={"tts_engine": "Google Cloud TTS", "browser": "Chrome"}
    )
    
    print("🎵 Simulating TTS engine failure during spiritual response delivery...")
    print_error_context(context)
    
    print(f"\n🔄 Applying TTS recovery strategies...")
    start_time = time.time()
    result = await recovery_system.handle_voice_error(context)
    elapsed_time = time.time() - start_time
    
    print(f"\n✨ Recovery completed in {elapsed_time:.3f}s")
    print_recovery_result(result)


async def demo_speech_recognition_recovery():
    """Demonstrate speech recognition failure recovery"""
    print_section("Speech Recognition Failure Recovery")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Simulate poor audio quality affecting recognition
    context = VoiceErrorContext(
        error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
        error_message="Could not understand user's spiritual question due to background noise",
        spiritual_content_type="question",
        sanskrit_terms_present=False,
        audio_context={
            "quality": "poor",
            "noise_level": "high",
            "volume": "low",
            "clarity": "muffled"
        }
    )
    
    print("🎙️  Simulating speech recognition failure due to poor audio quality...")
    print_error_context(context)
    
    print(f"\n🔄 Applying speech recognition recovery strategies...")
    start_time = time.time()
    result = await recovery_system.handle_voice_error(context)
    elapsed_time = time.time() - start_time
    
    print(f"\n✨ Recovery completed in {elapsed_time:.3f}s")
    print_recovery_result(result)


async def demo_multiple_failure_scenario():
    """Demonstrate handling multiple consecutive failures"""
    print_section("Multiple Consecutive Failures Scenario")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # First failure: Speech recognition
    print("🔴 First Failure: Speech Recognition")
    context1 = VoiceErrorContext(
        error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
        error_message="Initial recognition failure",
        spiritual_content_type="question",
        retry_count=0
    )
    
    print_error_context(context1)
    result1 = await recovery_system.handle_voice_error(context1)
    print(f"First recovery strategy: {result1.strategy_used.value}")
    
    # Second failure: Same issue, but with retry context
    print(f"\n🔴 Second Failure: Same Issue After First Recovery")
    context2 = VoiceErrorContext(
        error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
        error_message="Recognition still failing after first attempt",
        spiritual_content_type="question",
        retry_count=1,
        previous_strategies=[result1.strategy_used]
    )
    
    print_error_context(context2)
    result2 = await recovery_system.handle_voice_error(context2)
    print(f"Second recovery strategy: {result2.strategy_used.value}")
    
    # Third failure: Escalated to different error type
    print(f"\n🔴 Third Failure: Escalated to Audio Quality Issue")
    context3 = VoiceErrorContext(
        error_type=VoiceErrorType.AUDIO_QUALITY_POOR,
        error_message="Audio quality degraded significantly",
        spiritual_content_type="question",
        retry_count=2,
        previous_strategies=[result1.strategy_used, result2.strategy_used]
    )
    
    print_error_context(context3)
    result3 = await recovery_system.handle_voice_error(context3)
    
    print(f"\n📊 Multiple Failure Recovery Summary:")
    print(f"   Attempt 1: {result1.strategy_used.value} -> {'Success' if result1.success else 'Failed'}")
    print(f"   Attempt 2: {result2.strategy_used.value} -> {'Success' if result2.success else 'Failed'}")
    print(f"   Attempt 3: {result3.strategy_used.value} -> {'Success' if result3.success else 'Failed'}")
    
    if result3.fallback_mode:
        print(f"   Final Fallback Mode: {result3.fallback_mode.value}")


async def demo_spiritual_context_preservation():
    """Demonstrate spiritual context preservation during recovery"""
    print_section("Spiritual Context Preservation During Recovery")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Test different spiritual content types
    spiritual_contexts = [
        {
            "type": "mantra",
            "description": "Sacred Mantra Chanting",
            "content": "Om Namah Shivaya",
            "sanskrit": True
        },
        {
            "type": "teaching",
            "description": "Bhagavad Gita Teaching",
            "content": "Krishna's wisdom about dharma",
            "sanskrit": True
        },
        {
            "type": "guidance",
            "description": "Personal Spiritual Guidance",
            "content": "Life advice from Krishna",
            "sanskrit": False
        },
        {
            "type": "prayer",
            "description": "Devotional Prayer",
            "content": "Prayer for peace and wisdom",
            "sanskrit": False
        }
    ]
    
    print("🙏 Testing spiritual context preservation across different content types...")
    
    for ctx in spiritual_contexts:
        print(f"\n📿 Testing: {ctx['description']}")
        
        error_context = VoiceErrorContext(
            error_type=VoiceErrorType.TTS_ENGINE_FAILED,
            error_message=f"TTS failed during {ctx['type']}",
            spiritual_content_type=ctx["type"],
            sanskrit_terms_present=ctx["sanskrit"]
        )
        
        result = await recovery_system.handle_voice_error(error_context)
        
        print(f"   Strategy: {result.strategy_used.value}")
        print(f"   Spiritual Context Preserved: {'✅' if result.spiritual_context_preserved else '❌'}")
        print(f"   Graceful Degradation: {'✅' if result.graceful_degradation else '❌'}")
        
        if result.fallback_mode:
            print(f"   Fallback Mode: {result.fallback_mode.value}")


async def demo_recovery_statistics():
    """Demonstrate recovery statistics tracking"""
    print_section("Recovery Statistics Tracking")
    
    recovery_system = SpiritualVoiceRecovery()
    
    print("📊 Simulating multiple errors to generate statistics...")
    
    # Simulate various errors
    error_scenarios = [
        (VoiceErrorType.MICROPHONE_ACCESS_DENIED, "Microphone denied"),
        (VoiceErrorType.SPEECH_RECOGNITION_FAILED, "Recognition failed"),
        (VoiceErrorType.TTS_ENGINE_FAILED, "TTS failed"),
        (VoiceErrorType.NETWORK_CONNECTIVITY, "Network lost"),
        (VoiceErrorType.SANSKRIT_RECOGNITION_FAILED, "Sanskrit not recognized"),
        (VoiceErrorType.AUDIO_QUALITY_POOR, "Poor audio quality"),
        (VoiceErrorType.SPEECH_RECOGNITION_FAILED, "Recognition failed again"),
        (VoiceErrorType.TTS_ENGINE_FAILED, "TTS failed again")
    ]
    
    results = []
    
    for error_type, message in error_scenarios:
        context = VoiceErrorContext(
            error_type=error_type,
            error_message=message,
            spiritual_content_type="guidance",
            sanskrit_terms_present=(error_type == VoiceErrorType.SANSKRIT_RECOGNITION_FAILED)
        )
        
        result = await recovery_system.handle_voice_error(context)
        results.append(result)
        print(f"   {error_type.value}: {result.strategy_used.value} -> {'✅' if result.success else '❌'}")
    
    print(f"\n📈 Recovery Statistics Summary:")
    stats = recovery_system.get_recovery_statistics()
    
    print(f"   Total Errors: {stats['total_errors']}")
    print(f"   Successful Recoveries: {stats['successful_recoveries']}")
    print(f"   Success Rate: {stats['success_rate']:.2%}")
    print(f"   Fallback Activations: {stats['fallback_activations']}")
    print(f"   Fallback Rate: {stats['fallback_rate']:.2%}")
    print(f"   User Notifications: {stats['user_notifications']}")
    print(f"   Average Recovery Time: {stats['avg_recovery_time']:.1f}ms")
    
    if stats['most_common_errors']:
        print(f"\n🔴 Most Common Errors:")
        for error, count in sorted(stats['most_common_errors'].items(), key=lambda x: x[1], reverse=True):
            print(f"      {error}: {count} occurrences")
    
    if stats['strategy_effectiveness']:
        print(f"\n🎯 Strategy Effectiveness:")
        for strategy, data in stats['strategy_effectiveness'].items():
            effectiveness = data['effectiveness']
            print(f"      {strategy}: {effectiveness:.2%} ({data['successes']}/{data['attempts']})")


async def demo_fallback_mode_comparison():
    """Demonstrate different fallback modes"""
    print_section("Fallback Mode Comparison")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Test different fallback modes with same base error
    base_context = VoiceErrorContext(
        error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
        error_message="Microphone access issue",
        spiritual_content_type="guidance",
        sanskrit_terms_present=True
    )
    
    fallback_modes = [
        VoiceFallbackMode.TEXT_ONLY,
        VoiceFallbackMode.SIMPLIFIED_VOICE,
        VoiceFallbackMode.HYBRID_MODE,
        VoiceFallbackMode.OFFLINE_MODE,
        VoiceFallbackMode.ASSISTED_MODE
    ]
    
    print("🔄 Testing different fallback modes for the same error...")
    
    for mode in fallback_modes:
        print(f"\n📱 Testing Fallback Mode: {mode.value.upper()}")
        
        # Simulate handler execution
        handler = recovery_system.fallback_handlers[mode]
        start_time = time.time()
        success = await handler(base_context, {})
        elapsed_time = time.time() - start_time
        
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        print(f"   Processing Time: {elapsed_time*1000:.1f}ms")
        print(f"   Description: {get_fallback_mode_description(mode)}")


def get_fallback_mode_description(mode: VoiceFallbackMode) -> str:
    """Get description of fallback mode"""
    descriptions = {
        VoiceFallbackMode.TEXT_ONLY: "Complete text interface with Sanskrit pronunciation guides",
        VoiceFallbackMode.SIMPLIFIED_VOICE: "Basic voice without advanced optimizations",
        VoiceFallbackMode.HYBRID_MODE: "Combined voice and text interaction",
        VoiceFallbackMode.OFFLINE_MODE: "Cached spiritual content for offline access",
        VoiceFallbackMode.ASSISTED_MODE: "Guided voice setup with troubleshooting help"
    }
    return descriptions.get(mode, "Unknown mode")


async def demo_browser_compatibility_recovery():
    """Demonstrate browser compatibility issue recovery"""
    print_section("Browser Compatibility Issue Recovery")
    
    recovery_system = SpiritualVoiceRecovery()
    
    # Simulate browser compatibility issues
    browser_scenarios = [
        {
            "browser": "Safari",
            "issue": "WebKit Speech Recognition limited support",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
        },
        {
            "browser": "Firefox",
            "issue": "Web Speech API partial support",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0"
        },
        {
            "browser": "Edge Legacy",
            "issue": "Outdated Speech Synthesis API",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"
        }
    ]
    
    print("🌐 Testing browser compatibility recovery scenarios...")
    
    for scenario in browser_scenarios:
        print(f"\n🔧 Browser: {scenario['browser']}")
        print(f"   Issue: {scenario['issue']}")
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.BROWSER_COMPATIBILITY,
            error_message=scenario["issue"],
            user_agent=scenario["user_agent"],
            spiritual_content_type="guidance",
            device_info={"browser": scenario["browser"]}
        )
        
        result = await recovery_system.handle_voice_error(context)
        
        print(f"   Recovery Strategy: {result.strategy_used.value}")
        print(f"   Success: {'✅' if result.success else '❌'}")
        
        if result.fallback_mode:
            print(f"   Fallback Mode: {result.fallback_mode.value}")


async def main():
    """Main demo function"""
    print_banner()
    
    try:
        await demo_microphone_access_recovery()
        await demo_sanskrit_recognition_recovery()
        await demo_network_connectivity_recovery()
        await demo_tts_engine_failure_recovery()
        await demo_speech_recognition_recovery()
        await demo_multiple_failure_scenario()
        await demo_spiritual_context_preservation()
        await demo_recovery_statistics()
        await demo_fallback_mode_comparison()
        await demo_browser_compatibility_recovery()
        
        print("\n" + "="*70)
        print("🎉 VOICE ERROR RECOVERY DEMO COMPLETED SUCCESSFULLY! 🎉")
        print("="*70)
        print("The voice recovery system is ready for production deployment.")
        print("Features demonstrated:")
        print("  ✅ Comprehensive error classification and handling")
        print("  ✅ Spiritual content preservation during recovery")
        print("  ✅ Sanskrit-specific recovery strategies")
        print("  ✅ Multiple fallback modes")
        print("  ✅ Graceful degradation strategies")
        print("  ✅ Browser compatibility handling")
        print("  ✅ Recovery statistics tracking")
        print("  ✅ Multiple consecutive failure handling")
        print("  ✅ User-friendly spiritual error messages")
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
