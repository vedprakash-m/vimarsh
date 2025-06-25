#!/usr/bin/env python3
"""
Demo script for advanced voice features (interruption handling, voice commands).
Tests command recognition, interruption handling, and conversation flow management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.advanced_features import (
    AdvancedVoiceFeatures,
    VoiceCommand,
    InterruptionType,
    ConversationState
)
import asyncio
import time

async def demo_advanced_voice_features():
    """Demonstrate advanced voice features capabilities."""
    print("=== Vimarsh Advanced Voice Features Demo ===\n")
    
    # Initialize the advanced voice features system
    voice_features = AdvancedVoiceFeatures()
    session_id = "demo_session_001"
    
    # Test 1: Session Initialization
    print("1. Session Initialization")
    print("-" * 40)
    
    init_result = voice_features.initialize_session(session_id)
    print(f"Session ID: {init_result['session_id']}")
    print(f"Status: {init_result['status']}")
    print(f"Features Enabled:")
    for feature, enabled in init_result['features'].items():
        print(f"  - {feature.replace('_', ' ').title()}: {'✓' if enabled else '✗'}")
    print(f"Available Commands: {len(init_result['available_commands'])}")
    print()
    
    # Test 2: Voice Command Recognition
    print("2. Voice Command Recognition")
    print("-" * 40)
    
    test_commands = [
        "Please pause for a moment",
        "Can you repeat that?",
        "Stop talking",
        "Make it louder please",
        "Speak slower",
        "Switch to Hindi",
        "Start meditation",
        "Help me understand the commands",
        "Explain more about this topic",
        "Give me an example"
    ]
    
    for command_text in test_commands:
        result = voice_features.process_voice_interaction(
            session_id=session_id,
            audio_data=b"simulated_audio",
            transcribed_text=command_text,
            user_speech_detected=True
        )
        
        print(f"Input: '{command_text}'")
        if result.get("command"):
            cmd_info = result["command"]
            print(f"  Recognized Command: {cmd_info['command']}")
            print(f"  Confidence: {cmd_info['confidence']:.2f}")
            if result.get("response"):
                print(f"  Response: {result['response']}")
        else:
            print("  No command recognized")
        print()
    
    # Test 3: AI Speaking and Interruption Handling
    print("3. AI Speaking and Interruption Handling")
    print("-" * 40)
    
    # Start AI speaking
    long_response = ("धर्म एक अत्यंत महत्वपूर्ण अवधारणा है जो हमारे जीवन के हर पहलू को प्रभावित करती है। "
                    "यह केवल धार्मिक कर्मकांड नहीं है, बल्कि जीवन जीने का एक तरीका है। "
                    "धर्म का अर्थ है वह जो धारण किया जाए, यानी जो हमारे चरित्र और व्यवहार को "
                    "सहारा प्रदान करे।")
    
    speak_result = voice_features.start_ai_speaking(session_id, long_response)
    print(f"AI Started Speaking: {speak_result['started']}")
    print(f"Response Length: {len(speak_result['response_text'])} characters")
    print(f"Interruption Handling: {speak_result['interruption_handling']}")
    print()
    
    # Simulate user interruptions
    interruption_scenarios = [
        {
            "text": "Wait, pause please",
            "description": "User asks to pause"
        },
        {
            "text": "Can you repeat that last part?",
            "description": "User asks for repetition"
        },
        {
            "text": "Stop, I have a question",
            "description": "User interrupts with question"
        },
        {
            "text": "",
            "description": "Background noise interruption",
            "simulate_noise": True
        }
    ]
    
    for scenario in interruption_scenarios:
        print(f"Scenario: {scenario['description']}")
        
        audio_data = b"background_noise_detected" if scenario.get("simulate_noise") else b"user_speech"
        
        result = voice_features.process_voice_interaction(
            session_id=session_id,
            audio_data=audio_data,
            transcribed_text=scenario["text"],
            user_speech_detected=bool(scenario["text"]) or scenario.get("simulate_noise")
        )
        
        if result.get("interruption"):
            int_info = result["interruption"]
            print(f"  Interruption Detected: {int_info['type']}")
            print(f"  State Change: {int_info['previous_state']} → {int_info['new_state']}")
            print(f"  Should Resume: {int_info['should_resume']}")
            if int_info.get("detected_command"):
                print(f"  Command in Interruption: {int_info['detected_command']}")
        
        if result.get("command"):
            print(f"  Command Response: {result.get('response', 'No response')}")
        
        print(f"  Current State: {result['current_state']}")
        print()
    
    # Test 4: Conversation Flow Management
    print("4. Conversation Flow Management")
    print("-" * 40)
    
    # Test conversation context and state management
    conversation_tests = [
        "Resume the explanation",
        "Continue where you left off",
        "Can you simplify that?",
        "Give me an example of dharma",
        "Switch to English please"
    ]
    
    for test_input in conversation_tests:
        result = voice_features.process_voice_interaction(
            session_id=session_id,
            audio_data=b"user_speech",
            transcribed_text=test_input,
            user_speech_detected=True
        )
        
        print(f"User: {test_input}")
        if result.get("command"):
            print(f"Command: {result['command']['command']}")
        if result.get("response"):
            print(f"System: {result['response']}")
        
        session_info = result.get("session_info", {})
        print(f"State: {session_info.get('current_state', 'unknown')}")
        print()
    
    # Test 5: Session Statistics
    print("5. Session Statistics")
    print("-" * 40)
    
    stats = voice_features.get_session_statistics(session_id)
    print(f"Session Duration: {stats['session_duration']:.1f} seconds")
    print(f"Current State: {stats['current_state']}")
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"Interruption Count: {stats['interruption_count']}")
    print(f"Commands Executed: {stats['commands_executed']}")
    
    print(f"Voice Settings:")
    for setting, value in stats['voice_settings'].items():
        print(f"  {setting}: {value}")
    
    print(f"Performance Metrics:")
    for metric, value in stats['performance_metrics'].items():
        print(f"  {metric}: {value}")
    print()
    
    # Test 6: Voice Settings Adjustment Through Commands
    print("6. Voice Settings Adjustment")
    print("-" * 40)
    
    settings_commands = [
        "Make it louder",
        "Speak faster please",
        "Can you speak more quietly?",
        "Slow down a bit"
    ]
    
    for cmd in settings_commands:
        result = voice_features.process_voice_interaction(
            session_id=session_id,
            audio_data=b"user_speech",
            transcribed_text=cmd,
            user_speech_detected=True
        )
        
        print(f"Command: {cmd}")
        if result.get("response"):
            print(f"Response: {result['response']}")
        
        # Show updated settings
        session_info = result.get("session_info", {})
        if session_info.get("voice_settings"):
            print(f"Updated Settings: {session_info['voice_settings']}")
        print()
    
    # Test 7: Meditation and Spiritual Commands
    print("7. Spiritual Practice Commands")
    print("-" * 40)
    
    spiritual_commands = [
        "Start meditation please",
        "Play a mantra",
        "End meditation",
        "Stop the mantra"
    ]
    
    for cmd in spiritual_commands:
        result = voice_features.process_voice_interaction(
            session_id=session_id,
            audio_data=b"user_speech",
            transcribed_text=cmd,
            user_speech_detected=True
        )
        
        print(f"Command: {cmd}")
        if result.get("command"):
            print(f"Recognized: {result['command']['command']}")
        if result.get("response"):
            print(f"Response: {result['response']}")
        print()
    
    # Test 8: System Status and Capabilities
    print("8. System Status and Capabilities")
    print("-" * 40)
    
    system_status = voice_features.get_system_status()
    print(f"Features Enabled: {system_status['features_enabled']}")
    print(f"Active Sessions: {system_status['active_sessions']}")
    print(f"Total Commands: {system_status['total_commands']}")
    print(f"Interruption Types: {system_status['interruption_types']}")
    print(f"Conversation States: {system_status['conversation_states']}")
    
    print(f"System Capabilities:")
    for capability, available in system_status['capabilities'].items():
        print(f"  - {capability.replace('_', ' ').title()}: {'✓' if available else '✗'}")
    print()
    
    # Test 9: Help and Support Commands
    print("9. Help and Support Commands")
    print("-" * 40)
    
    help_result = voice_features.process_voice_interaction(
        session_id=session_id,
        audio_data=b"user_speech",
        transcribed_text="Help, what commands can I use?",
        user_speech_detected=True
    )
    
    print("User: Help, what commands can I use?")
    if help_result.get("response"):
        print(f"System Help: {help_result['response']}")
    print()
    
    # Test 10: Session Cleanup
    print("10. Session Management")
    print("-" * 40)
    
    # Show current active sessions
    print(f"Active Sessions Before Cleanup: {system_status['active_sessions']}")
    
    # Get final session statistics before cleanup
    final_stats = voice_features.get_session_statistics(session_id)
    if final_stats and 'session_duration' in final_stats:
        print(f"Final Session Duration: {final_stats['session_duration']:.1f} seconds")
        print(f"Total Interactions: {final_stats['total_interactions']}")
    
    # Simulate cleanup of inactive sessions (but don't cleanup our demo session)
    # cleanup_count = voice_features.cleanup_inactive_sessions(timeout_minutes=0)
    print(f"Sessions Available for Cleanup: 0 (demo session still active)")
    print()
    
    print("=== Demo Completed Successfully ===")
    print(f"Advanced voice features demonstrated:")
    print("✓ Voice command recognition")
    print("✓ Interruption handling")
    print("✓ Conversation flow management")
    print("✓ Real-time voice settings adjustment")
    print("✓ Spiritual practice integration")
    print("✓ Session management and statistics")

if __name__ == "__main__":
    asyncio.run(demo_advanced_voice_features())
