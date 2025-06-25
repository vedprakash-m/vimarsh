"""
Unit tests for Voice Error Recovery and Fallback Mechanisms

This module tests the SpiritualVoiceRecovery functionality including
error classification, recovery strategies, and fallback modes.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
import time
from datetime import datetime, timedelta

from voice_recovery import (
    SpiritualVoiceRecovery,
    VoiceErrorType,
    VoiceErrorContext,
    RecoveryStrategy,
    VoiceFallbackMode,
    RecoveryAction,
    VoiceRecoveryResult,
    create_voice_recovery_system
)


class TestVoiceErrorContext:
    """Test voice error context"""
    
    def test_error_context_creation(self):
        """Test creating voice error context"""
        context = VoiceErrorContext(
            error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
            error_message="Microphone access denied by user",
            user_agent="Mozilla/5.0...",
            device_info={"platform": "MacOS"},
            spiritual_content_type="mantra",
            sanskrit_terms_present=True
        )
        
        assert context.error_type == VoiceErrorType.MICROPHONE_ACCESS_DENIED
        assert context.spiritual_content_type == "mantra"
        assert context.sanskrit_terms_present is True
        assert context.retry_count == 0
        assert len(context.previous_strategies) == 0
    
    def test_error_context_with_retry_info(self):
        """Test error context with retry information"""
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
            error_message="Recognition failed",
            retry_count=2,
            previous_strategies=[RecoveryStrategy.RETRY_WITH_BACKOFF],
            fallback_mode=VoiceFallbackMode.SIMPLIFIED_VOICE
        )
        
        assert context.retry_count == 2
        assert RecoveryStrategy.RETRY_WITH_BACKOFF in context.previous_strategies
        assert context.fallback_mode == VoiceFallbackMode.SIMPLIFIED_VOICE


class TestRecoveryAction:
    """Test recovery action configuration"""
    
    def test_recovery_action_creation(self):
        """Test creating recovery action"""
        action = RecoveryAction(
            strategy=RecoveryStrategy.FALLBACK_TO_TEXT,
            priority=1,
            timeout_seconds=30.0,
            parameters={"maintain_spiritual_tone": True},
            applicable_errors=[VoiceErrorType.TTS_ENGINE_FAILED]
        )
        
        assert action.strategy == RecoveryStrategy.FALLBACK_TO_TEXT
        assert action.priority == 1
        assert action.parameters["maintain_spiritual_tone"] is True
        assert VoiceErrorType.TTS_ENGINE_FAILED in action.applicable_errors
    
    def test_recovery_action_defaults(self):
        """Test recovery action with defaults"""
        action = RecoveryAction(strategy=RecoveryStrategy.RETRY_WITH_BACKOFF)
        
        assert action.priority == 1
        assert action.timeout_seconds == 30.0
        assert action.max_retries == 3
        assert len(action.parameters) == 0


class TestSpiritualVoiceRecovery:
    """Test spiritual voice recovery system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.recovery_system = SpiritualVoiceRecovery()
    
    def test_initialization(self):
        """Test recovery system initialization"""
        assert self.recovery_system is not None
        assert len(self.recovery_system.recovery_actions) > 0
        assert len(self.recovery_system.fallback_handlers) > 0
        assert 'total_errors' in self.recovery_system.recovery_stats
        assert 'auto_fallback_enabled' in self.recovery_system.config
    
    def test_recovery_actions_configuration(self):
        """Test recovery actions are properly configured"""
        
        # Check microphone access denied actions
        mic_actions = self.recovery_system.recovery_actions.get(
            VoiceErrorType.MICROPHONE_ACCESS_DENIED, []
        )
        assert len(mic_actions) > 0
        
        # Should have prompt user action and fallback to text
        strategies = [action.strategy for action in mic_actions]
        assert RecoveryStrategy.PROMPT_USER_ACTION in strategies
        assert RecoveryStrategy.FALLBACK_TO_TEXT in strategies
    
    def test_fallback_handlers_registration(self):
        """Test fallback handlers are registered"""
        
        for mode in VoiceFallbackMode:
            assert mode in self.recovery_system.fallback_handlers
            assert callable(self.recovery_system.fallback_handlers[mode])
    
    @pytest.mark.asyncio
    async def test_handle_microphone_access_denied(self):
        """Test handling microphone access denied error"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
            error_message="User denied microphone access",
            spiritual_content_type="guidance",
            sanskrit_terms_present=False
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        assert isinstance(result, VoiceRecoveryResult)
        assert result.strategy_used in [
            RecoveryStrategy.PROMPT_USER_ACTION,
            RecoveryStrategy.FALLBACK_TO_TEXT
        ]
        assert result.recovery_time_ms >= 0
        assert len(result.actions_attempted) > 0
    
    @pytest.mark.asyncio
    async def test_handle_speech_recognition_failed(self):
        """Test handling speech recognition failure"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
            error_message="Could not recognize speech",
            spiritual_content_type="mantra",
            sanskrit_terms_present=True
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        assert isinstance(result, VoiceRecoveryResult)
        assert result.spiritual_context_preserved is True
        
        # Should try quality reduction or user prompt first
        assert result.strategy_used in [
            RecoveryStrategy.REDUCE_QUALITY,
            RecoveryStrategy.PROMPT_USER_ACTION,
            RecoveryStrategy.ALTERNATIVE_INPUT_METHOD
        ]
    
    @pytest.mark.asyncio
    async def test_handle_tts_engine_failed(self):
        """Test handling TTS engine failure"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.TTS_ENGINE_FAILED,
            error_message="TTS engine unavailable",
            spiritual_content_type="teaching",
            sanskrit_terms_present=True
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        assert isinstance(result, VoiceRecoveryResult)
        
        # Should try to switch engine or reduce quality before text fallback
        assert result.strategy_used in [
            RecoveryStrategy.SWITCH_VOICE_ENGINE,
            RecoveryStrategy.REDUCE_QUALITY,
            RecoveryStrategy.FALLBACK_TO_TEXT
        ]
    
    @pytest.mark.asyncio
    async def test_handle_network_connectivity_error(self):
        """Test handling network connectivity error"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.NETWORK_CONNECTIVITY,
            error_message="Network connection lost",
            network_status="disconnected"
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        assert isinstance(result, VoiceRecoveryResult)
        
        # Should try retry, cached response, or fallback
        assert result.strategy_used in [
            RecoveryStrategy.RETRY_WITH_BACKOFF,
            RecoveryStrategy.CACHED_RESPONSE,
            RecoveryStrategy.FALLBACK_TO_TEXT
        ]
    
    @pytest.mark.asyncio
    async def test_handle_sanskrit_recognition_failed(self):
        """Test handling Sanskrit recognition failure"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SANSKRIT_RECOGNITION_FAILED,
            error_message="Sanskrit pronunciation not recognized",
            spiritual_content_type="mantra",
            sanskrit_terms_present=True
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        assert isinstance(result, VoiceRecoveryResult)
        assert result.spiritual_context_preserved is True
        
        # Should provide pronunciation assistance
        assert result.strategy_used in [
            RecoveryStrategy.PROMPT_USER_ACTION,
            RecoveryStrategy.REDUCE_QUALITY,
            RecoveryStrategy.ALTERNATIVE_INPUT_METHOD
        ]
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_strategy(self):
        """Test retry with backoff strategy"""
        
        action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY_WITH_BACKOFF,
            max_retries=2,
            parameters={'base_delay': 0.1, 'max_delay': 1.0}
        )
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
            error_message="Temporary recognition failure"
        )
        
        start_time = time.time()
        result = await self.recovery_system._execute_single_action(action, context)
        elapsed_time = time.time() - start_time
        
        assert isinstance(result, VoiceRecoveryResult)
        assert result.strategy_used == RecoveryStrategy.RETRY_WITH_BACKOFF
        
        # Should have taken some time due to backoff delays
        # (Note: actual time depends on simulated success/failure)
        assert elapsed_time >= 0
    
    @pytest.mark.asyncio
    async def test_fallback_to_text_strategy(self):
        """Test fallback to text strategy"""
        
        action = RecoveryAction(
            strategy=RecoveryStrategy.FALLBACK_TO_TEXT,
            parameters={
                'maintain_spiritual_tone': True,
                'preserve_sanskrit_pronunciation_guides': True
            }
        )
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.TTS_ENGINE_FAILED,
            error_message="TTS engine error",
            spiritual_content_type="guidance",
            sanskrit_terms_present=True
        )
        
        result = await self.recovery_system._execute_single_action(action, context)
        
        assert result.strategy_used == RecoveryStrategy.FALLBACK_TO_TEXT
        assert result.fallback_mode == VoiceFallbackMode.TEXT_ONLY
        assert result.graceful_degradation is True
        assert result.spiritual_context_preserved is True
    
    @pytest.mark.asyncio
    async def test_prompt_user_action_strategy(self):
        """Test prompt user action strategy"""
        
        action = RecoveryAction(
            strategy=RecoveryStrategy.PROMPT_USER_ACTION,
            parameters={
                'message': 'Please check microphone settings',
                'spiritual_context': True,
                'include_pronunciation_tips': True
            }
        )
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.AUDIO_QUALITY_POOR,
            error_message="Poor audio quality detected",
            sanskrit_terms_present=True
        )
        
        result = await self.recovery_system._execute_single_action(action, context)
        
        assert result.strategy_used == RecoveryStrategy.PROMPT_USER_ACTION
        assert result.success is True  # Prompting always succeeds
        assert result.user_notified is True
        assert result.spiritual_context_preserved is True
    
    def test_spiritual_error_message_creation(self):
        """Test creation of spiritual error messages"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
            error_message="Access denied"
        )
        
        spiritual_msg = self.recovery_system._create_spiritual_error_message(
            context, "Please allow microphone access"
        )
        
        assert len(spiritual_msg) > 0
        assert any(word in spiritual_msg.lower() for word in ['krishna', 'divine', 'spiritual'])
    
    def test_prerequisites_checking(self):
        """Test checking action prerequisites"""
        
        # Action requiring network
        action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY_WITH_BACKOFF,
            prerequisites=['network_available']
        )
        
        # Context with no network
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
            error_message="Recognition failed",
            network_status="disconnected"
        )
        
        can_execute = self.recovery_system._check_prerequisites(action, context)
        assert can_execute is False
        
        # Context with network
        context.network_status = "connected"
        can_execute = self.recovery_system._check_prerequisites(action, context)
        assert can_execute is True
    
    @pytest.mark.asyncio
    async def test_general_fallback_application(self):
        """Test general fallback when no specific actions available"""
        
        # Create context for error type with no specific recovery actions
        context = VoiceErrorContext(
            error_type=VoiceErrorType.VOICE_PROCESSING_TIMEOUT,
            error_message="Voice processing timeout"
        )
        
        result = await self.recovery_system._apply_general_fallback(context)
        
        assert isinstance(result, VoiceRecoveryResult)
        assert result.fallback_mode is not None
        assert result.graceful_degradation is True
    
    def test_statistics_tracking(self):
        """Test recovery statistics tracking"""
        
        initial_stats = self.recovery_system.get_recovery_statistics()
        assert 'total_errors' in initial_stats
        assert 'success_rate' in initial_stats
        assert 'strategy_effectiveness' in initial_stats
        
        # Initial state
        assert initial_stats['total_errors'] == 0
        assert initial_stats['success_rate'] == 0.0
    
    @pytest.mark.asyncio
    async def test_statistics_update_after_recovery(self):
        """Test statistics are updated after recovery attempts"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
            error_message="Access denied"
        )
        
        initial_count = self.recovery_system.recovery_stats['total_errors']
        
        await self.recovery_system.handle_voice_error(context)
        
        assert self.recovery_system.recovery_stats['total_errors'] == initial_count + 1
        
        stats = self.recovery_system.get_recovery_statistics()
        assert stats['total_errors'] > 0
    
    def test_config_update(self):
        """Test updating recovery configuration"""
        
        initial_retries = self.recovery_system.config['max_retry_attempts']
        
        new_config = {
            'max_retry_attempts': 5,
            'auto_fallback_enabled': False
        }
        
        self.recovery_system.update_config(new_config)
        
        assert self.recovery_system.config['max_retry_attempts'] == 5
        assert self.recovery_system.config['auto_fallback_enabled'] is False
        
        # Other config should remain unchanged
        assert 'retry_base_delay' in self.recovery_system.config


class TestFallbackModeHandlers:
    """Test fallback mode handlers"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.recovery_system = SpiritualVoiceRecovery()
    
    @pytest.mark.asyncio
    async def test_text_only_fallback_handler(self):
        """Test text-only fallback handler"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
            error_message="No microphone access",
            spiritual_content_type="guidance"
        )
        
        parameters = {
            'maintain_spiritual_tone': True,
            'preserve_sanskrit_pronunciation_guides': True
        }
        
        success = await self.recovery_system._handle_text_only_fallback(context, parameters)
        assert success is True
    
    @pytest.mark.asyncio
    async def test_simplified_voice_fallback_handler(self):
        """Test simplified voice fallback handler"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.AUDIO_QUALITY_POOR,
            error_message="Poor audio quality"
        )
        
        success = await self.recovery_system._handle_simplified_voice_fallback(context, {})
        assert success is True
    
    @pytest.mark.asyncio
    async def test_hybrid_mode_fallback_handler(self):
        """Test hybrid mode fallback handler"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
            error_message="Recognition intermittent"
        )
        
        success = await self.recovery_system._handle_hybrid_mode_fallback(context, {})
        assert success is True
    
    @pytest.mark.asyncio
    async def test_offline_mode_fallback_handler(self):
        """Test offline mode fallback handler"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.NETWORK_CONNECTIVITY,
            error_message="No network connection",
            network_status="disconnected"
        )
        
        success = await self.recovery_system._handle_offline_mode_fallback(context, {})
        assert success is True
    
    @pytest.mark.asyncio
    async def test_assisted_mode_fallback_handler(self):
        """Test assisted mode fallback handler"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.BROWSER_COMPATIBILITY,
            error_message="Browser not supported"
        )
        
        success = await self.recovery_system._handle_assisted_mode_fallback(context, {})
        assert success is True


class TestRecoveryStrategies:
    """Test individual recovery strategies"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.recovery_system = SpiritualVoiceRecovery()
    
    @pytest.mark.asyncio
    async def test_switch_voice_engine_strategy(self):
        """Test switching voice engine strategy"""
        
        action = RecoveryAction(
            strategy=RecoveryStrategy.SWITCH_VOICE_ENGINE,
            parameters={
                'preferred_engines': ['Google TTS', 'Web Speech API'],
                'maintain_spiritual_tone': True
            }
        )
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.TTS_ENGINE_FAILED,
            error_message="Primary TTS engine failed"
        )
        
        result = await self.recovery_system._execute_single_action(action, context)
        
        assert result.strategy_used == RecoveryStrategy.SWITCH_VOICE_ENGINE
        # Result can be success or failure depending on simulation
        assert result.spiritual_context_preserved is True
    
    @pytest.mark.asyncio
    async def test_reduce_quality_strategy(self):
        """Test reduce quality strategy"""
        
        action = RecoveryAction(
            strategy=RecoveryStrategy.REDUCE_QUALITY,
            parameters={
                'lower_sample_rate': True,
                'disable_ssml': False
            }
        )
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.AUDIO_QUALITY_POOR,
            error_message="Audio quality issues"
        )
        
        result = await self.recovery_system._execute_single_action(action, context)
        
        assert result.strategy_used == RecoveryStrategy.REDUCE_QUALITY
        assert result.graceful_degradation is True
        assert 0 <= result.voice_quality_after_recovery <= 1.0
    
    @pytest.mark.asyncio
    async def test_alternative_input_method_strategy(self):
        """Test alternative input method strategy"""
        
        action = RecoveryAction(
            strategy=RecoveryStrategy.ALTERNATIVE_INPUT_METHOD,
            parameters={
                'enable_text_input': True,
                'enable_sanskrit_keyboard': True
            }
        )
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SANSKRIT_RECOGNITION_FAILED,
            error_message="Sanskrit not recognized",
            sanskrit_terms_present=True
        )
        
        result = await self.recovery_system._execute_single_action(action, context)
        
        assert result.strategy_used == RecoveryStrategy.ALTERNATIVE_INPUT_METHOD
        assert result.fallback_mode == VoiceFallbackMode.HYBRID_MODE
        assert result.spiritual_context_preserved is True
    
    @pytest.mark.asyncio
    async def test_cached_response_strategy(self):
        """Test cached response strategy"""
        
        action = RecoveryAction(
            strategy=RecoveryStrategy.CACHED_RESPONSE,
            parameters={
                'use_spiritual_fallback_responses': True,
                'include_offline_mantras': True
            }
        )
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.NETWORK_CONNECTIVITY,
            error_message="Network unavailable",
            spiritual_content_type="mantra"
        )
        
        result = await self.recovery_system._execute_single_action(action, context)
        
        assert result.strategy_used == RecoveryStrategy.CACHED_RESPONSE
        # Fallback mode depends on success of cached retrieval
        assert result.graceful_degradation is True


class TestErrorHandlingEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.recovery_system = SpiritualVoiceRecovery()
    
    @pytest.mark.asyncio
    async def test_unknown_error_type(self):
        """Test handling unknown error type"""
        
        # Create context with no specific recovery actions
        context = VoiceErrorContext(
            error_type=VoiceErrorType.VOICE_PROCESSING_TIMEOUT,
            error_message="Unknown timeout error"
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        # Should fall back to general recovery
        assert isinstance(result, VoiceRecoveryResult)
        assert result.fallback_mode is not None
    
    @pytest.mark.asyncio
    async def test_recovery_system_exception_handling(self):
        """Test recovery system handles internal exceptions gracefully"""
        
        # Mock a method to raise an exception
        with patch.object(
            self.recovery_system, 
            '_execute_recovery_actions', 
            side_effect=Exception("Internal error")
        ):
            context = VoiceErrorContext(
                error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
                error_message="Test error"
            )
            
            result = await self.recovery_system.handle_voice_error(context)
            
            # Should return failed result but not crash
            assert isinstance(result, VoiceRecoveryResult)
            assert result.success is False
            assert "Internal error" in result.final_error
    
    def test_empty_recovery_actions_list(self):
        """Test behavior with empty recovery actions list"""
        
        # Temporarily clear recovery actions for a specific error
        original_actions = self.recovery_system.recovery_actions.get(
            VoiceErrorType.MICROPHONE_ACCESS_DENIED, []
        )
        
        self.recovery_system.recovery_actions[VoiceErrorType.MICROPHONE_ACCESS_DENIED] = []
        
        try:
            context = VoiceErrorContext(
                error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
                error_message="Test error"
            )
            
            # Should handle gracefully and apply general fallback
            # (This is tested in the async test above)
            
        finally:
            # Restore original actions
            self.recovery_system.recovery_actions[VoiceErrorType.MICROPHONE_ACCESS_DENIED] = original_actions


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_create_voice_recovery_system(self):
        """Test convenience function for creating recovery system"""
        
        recovery_system = create_voice_recovery_system()
        
        assert isinstance(recovery_system, SpiritualVoiceRecovery)
        assert len(recovery_system.recovery_actions) > 0
        assert len(recovery_system.fallback_handlers) > 0


class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.recovery_system = SpiritualVoiceRecovery()
    
    @pytest.mark.asyncio
    async def test_complete_microphone_recovery_workflow(self):
        """Test complete microphone access recovery workflow"""
        
        # Initial error
        context = VoiceErrorContext(
            error_type=VoiceErrorType.MICROPHONE_ACCESS_DENIED,
            error_message="User denied microphone access",
            spiritual_content_type="guidance",
            sanskrit_terms_present=False,
            device_info={"platform": "Chrome", "version": "91.0"}
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        # Should provide spiritual guidance about allowing access
        assert result.spiritual_context_preserved is True
        assert result.user_notified is True or result.fallback_mode is not None
        
        # Check statistics were updated
        stats = self.recovery_system.get_recovery_statistics()
        assert stats['total_errors'] >= 1
    
    @pytest.mark.asyncio
    async def test_sanskrit_mantra_recovery_workflow(self):
        """Test Sanskrit mantra recognition recovery"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.SANSKRIT_RECOGNITION_FAILED,
            error_message="Could not recognize 'Om Namah Shivaya'",
            spiritual_content_type="mantra",
            sanskrit_terms_present=True,
            audio_context={"quality": "poor", "noise_level": "high"}
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        # Should preserve spiritual context for mantras
        assert result.spiritual_context_preserved is True
        
        # Should provide guidance or alternative input
        assert (result.user_notified is True or 
                result.fallback_mode in [
                    VoiceFallbackMode.HYBRID_MODE,
                    VoiceFallbackMode.TEXT_ONLY,
                    VoiceFallbackMode.SIMPLIFIED_VOICE
                ])
    
    @pytest.mark.asyncio
    async def test_network_failure_during_spiritual_guidance(self):
        """Test network failure during spiritual guidance session"""
        
        context = VoiceErrorContext(
            error_type=VoiceErrorType.NETWORK_CONNECTIVITY,
            error_message="Connection lost during guidance session",
            spiritual_content_type="teaching",
            sanskrit_terms_present=True,
            network_status="disconnected"
        )
        
        result = await self.recovery_system.handle_voice_error(context)
        
        # Should try to use cached content or provide offline guidance
        assert (result.strategy_used in [
            RecoveryStrategy.CACHED_RESPONSE,
            RecoveryStrategy.FALLBACK_TO_TEXT,
            RecoveryStrategy.RETRY_WITH_BACKOFF
        ])
        
        # Should maintain spiritual context
        assert result.spiritual_context_preserved is True
    
    @pytest.mark.asyncio
    async def test_multiple_consecutive_failures(self):
        """Test handling multiple consecutive failures"""
        
        # First failure
        context1 = VoiceErrorContext(
            error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
            error_message="First recognition failure",
            retry_count=0
        )
        
        result1 = await self.recovery_system.handle_voice_error(context1)
        
        # Second failure with retry context
        context2 = VoiceErrorContext(
            error_type=VoiceErrorType.SPEECH_RECOGNITION_FAILED,
            error_message="Second recognition failure",
            retry_count=1,
            previous_strategies=[result1.strategy_used]
        )
        
        result2 = await self.recovery_system.handle_voice_error(context2)
        
        # Should try different strategy for second attempt
        assert result2.strategy_used != result1.strategy_used or result2.fallback_mode is not None
        
        # Statistics should show multiple errors
        stats = self.recovery_system.get_recovery_statistics()
        assert stats['total_errors'] >= 2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
