#!/usr/bin/env python3
"""
Test suite for advanced voice features (interruption handling, voice commands).
Tests command recognition, interruption handling, and conversation flow management.
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.advanced_features import (
    AdvancedVoiceFeatures,
    VoiceCommandRecognizer,
    InterruptionHandler,
    ConversationFlowManager,
    VoiceCommand,
    InterruptionType,
    ConversationState,
    VoiceCommandPattern,
    InterruptionEvent,
    ConversationContext
)
from datetime import datetime, timedelta


class TestVoiceCommandPattern:
    """Test cases for VoiceCommandPattern"""
    
    def test_pattern_creation(self):
        """Test command pattern creation"""
        pattern = VoiceCommandPattern(
            command=VoiceCommand.PAUSE,
            patterns=[r"\bpause\b"],
            keywords=["pause", "wait"],
            confidence_threshold=0.8
        )
        
        assert pattern.command == VoiceCommand.PAUSE
        assert len(pattern.patterns) == 1
        assert len(pattern.keywords) == 2
        assert pattern.confidence_threshold == 0.8
    
    def test_pattern_matching(self):
        """Test pattern matching functionality"""
        pattern = VoiceCommandPattern(
            command=VoiceCommand.PAUSE,
            patterns=[r"\b(pause|wait|hold)\b"],
            keywords=["pause", "wait", "hold"],
            confidence_threshold=0.7
        )
        
        # Test exact pattern match
        matches, confidence = pattern.matches("Please pause for a moment")
        assert matches is True
        assert confidence >= 0.7
        
        # Test keyword match
        matches, confidence = pattern.matches("Can you wait a second")
        assert matches is True
        assert confidence >= 0.7
        
        # Test no match
        matches, confidence = pattern.matches("Continue speaking")
        assert matches is False
        assert confidence < 0.7
    
    def test_language_support(self):
        """Test language-specific pattern matching"""
        pattern = VoiceCommandPattern(
            command=VoiceCommand.PAUSE,
            patterns=[r"\bpause\b"],
            keywords=["pause"],
            languages=["en"]
        )
        
        # Should match supported language
        matches, confidence = pattern.matches("pause", "en")
        assert matches is True
        
        # Should not match unsupported language
        matches, confidence = pattern.matches("pause", "fr")
        assert matches is False


class TestVoiceCommandRecognizer:
    """Test cases for VoiceCommandRecognizer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.recognizer = VoiceCommandRecognizer()
    
    def test_initialization(self):
        """Test recognizer initialization"""
        assert isinstance(self.recognizer.command_patterns, list)
        assert len(self.recognizer.command_patterns) > 0
        assert self.recognizer.recognition_enabled is True
    
    def test_basic_command_recognition(self):
        """Test basic command recognition"""
        # Test pause command
        result = self.recognizer.recognize_command("Please pause")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.PAUSE
        assert confidence >= 0.7
        
        # Test stop command
        result = self.recognizer.recognize_command("Stop talking")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.STOP
        
        # Test help command
        result = self.recognizer.recognize_command("Help me")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.HELP
    
    def test_volume_commands(self):
        """Test volume adjustment commands"""
        # Test louder
        result = self.recognizer.recognize_command("Make it louder")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.LOUDER
        
        # Test quieter
        result = self.recognizer.recognize_command("Please speak quieter")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.QUIETER
    
    def test_speed_commands(self):
        """Test speed adjustment commands"""
        # Test faster
        result = self.recognizer.recognize_command("Speak faster")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.FASTER
        
        # Test slower
        result = self.recognizer.recognize_command("Slow down")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.SLOWER
    
    def test_spiritual_commands(self):
        """Test spiritual practice commands"""
        # Test meditation
        result = self.recognizer.recognize_command("Start meditation")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.START_MEDITATION
        
        # Test mantra
        result = self.recognizer.recognize_command("Play mantra")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.PLAY_MANTRA
    
    def test_language_commands(self):
        """Test language switching commands"""
        # Test Hindi switch
        result = self.recognizer.recognize_command("Switch to Hindi")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.SWITCH_TO_HINDI
        
        # Test English switch
        result = self.recognizer.recognize_command("Switch to English")
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.SWITCH_TO_ENGLISH
    
    def test_no_command_recognition(self):
        """Test when no command should be recognized"""
        # Random text without commands
        result = self.recognizer.recognize_command("The weather is nice today")
        assert result is None
        
        # Empty text
        result = self.recognizer.recognize_command("")
        assert result is None
    
    def test_recognition_disabled(self):
        """Test command recognition when disabled"""
        self.recognizer.recognition_enabled = False
        
        result = self.recognizer.recognize_command("pause")
        assert result is None
        
        # Re-enable for other tests
        self.recognizer.recognition_enabled = True
    
    def test_context_adjustment(self):
        """Test confidence adjustment based on context"""
        context = ConversationContext("test")
        context.current_state = ConversationState.SPEAKING
        
        # Pause should have higher confidence when AI is speaking
        result = self.recognizer.recognize_command("pause", "en", context)
        assert result is not None
        command, confidence = result
        assert command == VoiceCommand.PAUSE
        
        # Test with different state
        context.current_state = ConversationState.IDLE
        result = self.recognizer.recognize_command("pause", "en", context)
        # Should still work but might have different confidence


class TestInterruptionHandler:
    """Test cases for InterruptionHandler"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.handler = InterruptionHandler()
    
    def test_initialization(self):
        """Test handler initialization"""
        assert self.handler.interruption_threshold == 0.7
        assert self.handler.silence_timeout == 10.0
        assert self.handler.handler_enabled is True
    
    def test_user_speech_interruption(self):
        """Test user speech interruption detection"""
        context = ConversationContext("test")
        context.current_state = ConversationState.SPEAKING
        context.response_start_time = datetime.now()
        
        interruption = self.handler.detect_interruption(
            audio_data=b"test_audio",
            context=context,
            user_speech_detected=True,
            user_text="Wait, pause please"
        )
        
        assert interruption is not None
        assert interruption.interruption_type == InterruptionType.USER_SPEECH
        assert interruption.user_text == "Wait, pause please"
        assert interruption.confidence >= 0.8
    
    def test_silence_timeout(self):
        """Test silence timeout detection"""
        context = ConversationContext("test")
        context.current_state = ConversationState.LISTENING
        context.response_start_time = datetime.now() - timedelta(seconds=15)  # 15 seconds ago
        
        interruption = self.handler.detect_interruption(
            audio_data=b"test_audio",
            context=context,
            user_speech_detected=False
        )
        
        assert interruption is not None
        assert interruption.interruption_type == InterruptionType.SILENCE_TIMEOUT
        assert interruption.should_resume is False
    
    def test_background_noise(self):
        """Test background noise detection"""
        context = ConversationContext("test")
        context.current_state = ConversationState.SPEAKING
        
        # Simulate noisy audio data
        noisy_audio = b"noise" * 500  # Create long audio with "noise" pattern
        
        interruption = self.handler.detect_interruption(
            audio_data=noisy_audio,
            context=context,
            user_speech_detected=False
        )
        
        assert interruption is not None
        assert interruption.interruption_type == InterruptionType.BACKGROUND_NOISE
        assert interruption.should_resume is True
    
    def test_no_interruption(self):
        """Test when no interruption should be detected"""
        context = ConversationContext("test")
        context.current_state = ConversationState.IDLE
        
        interruption = self.handler.detect_interruption(
            audio_data=b"quiet_audio",
            context=context,
            user_speech_detected=False
        )
        
        assert interruption is None
    
    def test_handler_disabled(self):
        """Test interruption detection when handler is disabled"""
        self.handler.handler_enabled = False
        
        context = ConversationContext("test")
        context.current_state = ConversationState.SPEAKING
        
        interruption = self.handler.detect_interruption(
            audio_data=b"test",
            context=context,
            user_speech_detected=True,
            user_text="pause"
        )
        
        assert interruption is None
        
        # Re-enable for other tests
        self.handler.handler_enabled = True
    
    def test_resume_decision(self):
        """Test decision making for resume after user speech"""
        # Test with stop words
        should_resume = self.handler._should_resume_after_user_speech(
            "stop talking", ConversationContext("test")
        )
        assert should_resume is False
        
        # Test with questions
        should_resume = self.handler._should_resume_after_user_speech(
            "What does that mean?", ConversationContext("test")
        )
        assert should_resume is False
        
        # Test with random interruption
        should_resume = self.handler._should_resume_after_user_speech(
            "um, wait", ConversationContext("test")
        )
        assert should_resume is True


class TestConversationFlowManager:
    """Test cases for ConversationFlowManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.flow_manager = ConversationFlowManager()
        self.session_id = "test_session_123"
    
    def test_initialization(self):
        """Test flow manager initialization"""
        assert isinstance(self.flow_manager.command_recognizer, VoiceCommandRecognizer)
        assert isinstance(self.flow_manager.interruption_handler, InterruptionHandler)
        assert isinstance(self.flow_manager.active_contexts, dict)
        assert self.flow_manager.flow_enabled is True
    
    def test_conversation_start(self):
        """Test starting a conversation"""
        context = self.flow_manager.start_conversation(self.session_id)
        
        assert context.session_id == self.session_id
        assert context.current_state == ConversationState.IDLE
        assert self.session_id in self.flow_manager.active_contexts
    
    def test_voice_input_processing(self):
        """Test voice input processing"""
        # Start conversation
        self.flow_manager.start_conversation(self.session_id)
        
        # Process voice input with command
        result = self.flow_manager.process_voice_input(
            session_id=self.session_id,
            audio_data=b"test_audio",
            transcribed_text="pause please",
            user_speech_detected=True
        )
        
        assert "session_id" in result
        assert "actions" in result
        assert "current_state" in result
        assert result["session_id"] == self.session_id
    
    def test_ai_response_start(self):
        """Test starting AI response"""
        # Start conversation
        self.flow_manager.start_conversation(self.session_id)
        
        # Start AI response
        success = self.flow_manager.start_ai_response(
            self.session_id, "Test response from AI"
        )
        
        assert success is True
        
        context = self.flow_manager.active_contexts[self.session_id]
        assert context.current_state == ConversationState.SPEAKING
        assert context.current_response == "Test response from AI"
        assert context.response_start_time is not None
    
    def test_command_handling(self):
        """Test voice command handling"""
        # Start conversation
        context = self.flow_manager.start_conversation(self.session_id)
        
        # Test pause command
        response = self.flow_manager._handle_command(
            context, VoiceCommand.PAUSE, "pause"
        )
        assert isinstance(response, str)
        
        # Test stop command
        response = self.flow_manager._handle_command(
            context, VoiceCommand.STOP, "stop"
        )
        assert isinstance(response, str)
        assert context.current_state == ConversationState.IDLE
        
        # Test volume command
        response = self.flow_manager._handle_command(
            context, VoiceCommand.LOUDER, "louder"
        )
        assert isinstance(response, str)
        assert context.voice_settings.get("volume", 1.0) > 1.0
    
    def test_interruption_handling(self):
        """Test interruption handling"""
        # Start conversation and AI response
        context = self.flow_manager.start_conversation(self.session_id)
        context.current_state = ConversationState.SPEAKING
        
        # Create interruption event
        interruption = InterruptionEvent(
            interruption_type=InterruptionType.USER_SPEECH,
            timestamp=datetime.now(),
            confidence=0.9,
            user_text="pause",
            should_resume=True
        )
        
        # Handle interruption
        result = self.flow_manager._handle_interruption(context, interruption)
        
        assert isinstance(result, dict)
        assert "type" in result
        assert "previous_state" in result
        assert "new_state" in result
        assert result["type"] == "user_speech"
    
    def test_session_status(self):
        """Test getting session status"""
        # Test non-existent session
        status = self.flow_manager.get_session_status("non_existent")
        assert status is None
        
        # Test existing session
        self.flow_manager.start_conversation(self.session_id)
        status = self.flow_manager.get_session_status(self.session_id)
        
        assert status is not None
        assert "session_id" in status
        assert "current_state" in status
        assert "interruption_count" in status
        assert status["session_id"] == self.session_id
    
    def test_conversation_end(self):
        """Test ending a conversation"""
        # Start conversation
        self.flow_manager.start_conversation(self.session_id)
        assert self.session_id in self.flow_manager.active_contexts
        
        # End conversation
        success = self.flow_manager.end_conversation(self.session_id)
        assert success is True
        assert self.session_id not in self.flow_manager.active_contexts
        
        # Try to end non-existent conversation
        success = self.flow_manager.end_conversation("non_existent")
        assert success is False


class TestAdvancedVoiceFeatures:
    """Test cases for AdvancedVoiceFeatures"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.voice_features = AdvancedVoiceFeatures()
        self.session_id = "test_advanced_session"
    
    def test_initialization(self):
        """Test advanced voice features initialization"""
        assert isinstance(self.voice_features.flow_manager, ConversationFlowManager)
        assert self.voice_features.features_enabled is True
        assert isinstance(self.voice_features.active_sessions, dict)
    
    def test_session_initialization(self):
        """Test session initialization"""
        result = self.voice_features.initialize_session(self.session_id)
        
        assert "session_id" in result
        assert "status" in result
        assert "features" in result
        assert "available_commands" in result
        assert result["session_id"] == self.session_id
        assert result["status"] == "initialized"
        assert self.session_id in self.voice_features.active_sessions
    
    def test_voice_interaction_processing(self):
        """Test voice interaction processing"""
        # Initialize session first
        self.voice_features.initialize_session(self.session_id)
        
        # Process voice interaction
        result = self.voice_features.process_voice_interaction(
            session_id=self.session_id,
            audio_data=b"test_audio",
            transcribed_text="help",
            user_speech_detected=True
        )
        
        assert "session_id" in result
        assert "session_info" in result
        assert result["session_id"] == self.session_id
    
    def test_ai_speaking_start(self):
        """Test starting AI speaking"""
        # Initialize session first
        self.voice_features.initialize_session(self.session_id)
        
        # Start AI speaking
        result = self.voice_features.start_ai_speaking(
            self.session_id, "This is a test response"
        )
        
        assert "session_id" in result
        assert "started" in result
        assert "response_text" in result
        assert result["started"] is True
        assert result["response_text"] == "This is a test response"
    
    def test_session_statistics(self):
        """Test getting session statistics"""
        # Initialize session
        self.voice_features.initialize_session(self.session_id)
        
        # Process some interactions
        self.voice_features.process_voice_interaction(
            session_id=self.session_id,
            audio_data=b"test",
            transcribed_text="help",
            user_speech_detected=True
        )
        
        # Get statistics
        stats = self.voice_features.get_session_statistics(self.session_id)
        
        assert "session_id" in stats
        assert "session_duration" in stats
        assert "current_state" in stats
        assert "total_interactions" in stats
        assert stats["session_id"] == self.session_id
    
    def test_system_status(self):
        """Test getting system status"""
        status = self.voice_features.get_system_status()
        
        assert "features_enabled" in status
        assert "active_sessions" in status
        assert "total_commands" in status
        assert "capabilities" in status
        assert isinstance(status["capabilities"], dict)
    
    def test_features_disabled(self):
        """Test behavior when features are disabled"""
        # Disable features
        self.voice_features.features_enabled = False
        
        # Try to initialize session
        result = self.voice_features.initialize_session(self.session_id)
        assert "error" in result
        
        # Try to process interaction
        result = self.voice_features.process_voice_interaction(
            self.session_id, b"test", "test", True
        )
        assert "error" in result
        
        # Re-enable for other tests
        self.voice_features.features_enabled = True
    
    def test_session_cleanup(self):
        """Test session cleanup functionality"""
        # Initialize session
        self.voice_features.initialize_session(self.session_id)
        
        # Verify session exists
        assert self.session_id in self.voice_features.active_sessions
        
        # Clean up with very short timeout (should clean up active session)
        cleanup_count = self.voice_features.cleanup_inactive_sessions(timeout_minutes=0)
        
        # Check that session was cleaned up
        assert self.session_id not in self.voice_features.active_sessions


def test_voice_command_enum():
    """Test VoiceCommand enum"""
    assert VoiceCommand.PAUSE.value == "pause"
    assert VoiceCommand.RESUME.value == "resume"
    assert VoiceCommand.STOP.value == "stop"
    assert VoiceCommand.HELP.value == "help"


def test_interruption_type_enum():
    """Test InterruptionType enum"""
    assert InterruptionType.USER_SPEECH.value == "user_speech"
    assert InterruptionType.BACKGROUND_NOISE.value == "background_noise"
    assert InterruptionType.SILENCE_TIMEOUT.value == "silence_timeout"


def test_conversation_state_enum():
    """Test ConversationState enum"""
    assert ConversationState.IDLE.value == "idle"
    assert ConversationState.LISTENING.value == "listening"
    assert ConversationState.SPEAKING.value == "speaking"
    assert ConversationState.PAUSED.value == "paused"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
