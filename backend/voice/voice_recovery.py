"""
Voice Error Recovery and Fallback Mechanisms

This module provides comprehensive error recovery and fallback mechanisms
for voice interface operations in the Vimarsh AI Agent, ensuring robust
voice processing even under adverse conditions.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
import traceback

try:
    import numpy as np
except ImportError:
    np = None


class VoiceErrorType(Enum):
    """Types of voice-related errors"""
    MICROPHONE_ACCESS_DENIED = "microphone_access_denied"
    MICROPHONE_NOT_FOUND = "microphone_not_found"
    AUDIO_QUALITY_POOR = "audio_quality_poor"
    SPEECH_RECOGNITION_FAILED = "speech_recognition_failed"
    TTS_ENGINE_FAILED = "tts_engine_failed"
    NETWORK_CONNECTIVITY = "network_connectivity"
    API_RATE_LIMIT = "api_rate_limit"
    BROWSER_COMPATIBILITY = "browser_compatibility"
    AUDIO_PLAYBACK_FAILED = "audio_playback_failed"
    VOICE_PROCESSING_TIMEOUT = "voice_processing_timeout"
    SANSKRIT_RECOGNITION_FAILED = "sanskrit_recognition_failed"
    SPIRITUAL_CONTENT_VALIDATION_FAILED = "spiritual_content_validation_failed"


class RecoveryStrategy(Enum):
    """Voice error recovery strategies"""
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    FALLBACK_TO_TEXT = "fallback_to_text"
    SWITCH_VOICE_ENGINE = "switch_voice_engine"
    REDUCE_QUALITY = "reduce_quality"
    PROMPT_USER_ACTION = "prompt_user_action"
    SILENT_DEGRADATION = "silent_degradation"
    ALTERNATIVE_INPUT_METHOD = "alternative_input_method"
    CACHED_RESPONSE = "cached_response"


class VoiceFallbackMode(Enum):
    """Voice fallback operation modes"""
    TEXT_ONLY = "text_only"                    # Complete fallback to text
    SIMPLIFIED_VOICE = "simplified_voice"      # Basic voice without optimization
    HYBRID_MODE = "hybrid_mode"               # Mix of voice and text
    OFFLINE_MODE = "offline_mode"             # Local processing only
    ASSISTED_MODE = "assisted_mode"           # With user guidance prompts


@dataclass
class VoiceErrorContext:
    """Context information for voice errors"""
    error_type: VoiceErrorType
    error_message: str
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    network_status: Optional[str] = None
    audio_context: Optional[Dict[str, Any]] = None
    
    # Spiritual context
    spiritual_content_type: Optional[str] = None
    sanskrit_terms_present: bool = False
    
    # Recovery context
    retry_count: int = 0
    previous_strategies: List[RecoveryStrategy] = field(default_factory=list)
    fallback_mode: Optional[VoiceFallbackMode] = None
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RecoveryAction:
    """Voice recovery action definition"""
    strategy: RecoveryStrategy
    priority: int = 1  # 1 = highest priority
    timeout_seconds: float = 30.0
    max_retries: int = 3
    
    # Action-specific parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Conditions for applying this action
    applicable_errors: List[VoiceErrorType] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    
    # Success criteria
    success_indicators: List[str] = field(default_factory=list)
    
    # Callback functions
    action_handler: Optional[Callable] = None
    validation_handler: Optional[Callable] = None


@dataclass
class VoiceRecoveryResult:
    """Result of voice error recovery attempt"""
    success: bool
    strategy_used: RecoveryStrategy
    fallback_mode: Optional[VoiceFallbackMode] = None
    
    # Recovery details
    recovery_time_ms: int = 0
    actions_attempted: List[str] = field(default_factory=list)
    final_error: Optional[str] = None
    
    # User experience impact
    user_notified: bool = False
    graceful_degradation: bool = False
    spiritual_context_preserved: bool = True
    
    # Quality metrics
    voice_quality_after_recovery: float = 0.0
    user_satisfaction_estimated: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.now)


class SpiritualVoiceRecovery:
    """
    Comprehensive voice error recovery and fallback system for spiritual guidance
    """
    
    def __init__(self):
        """Initialize voice recovery system"""
        self.logger = logging.getLogger(__name__)
        
        # Recovery strategies and actions
        self.recovery_actions: Dict[VoiceErrorType, List[RecoveryAction]] = {}
        self.fallback_handlers: Dict[VoiceFallbackMode, Callable] = {}
        
        # Recovery statistics
        self.recovery_stats = {
            'total_errors': 0,
            'successful_recoveries': 0,
            'fallback_activations': 0,
            'user_notifications': 0,
            'avg_recovery_time': 0.0,
            'most_common_errors': {},
            'most_effective_strategies': {}
        }
        
        # Recovery configuration
        self.config = {
            'max_retry_attempts': 3,
            'retry_base_delay': 1.0,  # seconds
            'retry_max_delay': 16.0,  # seconds
            'voice_quality_threshold': 0.6,
            'auto_fallback_enabled': True,
            'user_notification_threshold': 2,  # errors before notifying
            'spiritual_context_priority': True,
            'sanskrit_fallback_enabled': True
        }
        
        # Initialize recovery strategies
        self._initialize_recovery_actions()
        self._initialize_fallback_handlers()
    
    def _initialize_recovery_actions(self):
        """Initialize recovery actions for different error types"""
        
        # Microphone access errors
        self.recovery_actions[VoiceErrorType.MICROPHONE_ACCESS_DENIED] = [
            RecoveryAction(
                strategy=RecoveryStrategy.PROMPT_USER_ACTION,
                priority=1,
                parameters={
                    'message': 'Please grant microphone permissions for voice guidance',
                    'spiritual_context': True,
                    'guidance': 'Voice interaction enhances the spiritual experience'
                },
                applicable_errors=[VoiceErrorType.MICROPHONE_ACCESS_DENIED],
                success_indicators=['microphone_permission_granted']
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK_TO_TEXT,
                priority=2,
                parameters={
                    'maintain_spiritual_tone': True,
                    'preserve_sanskrit_pronunciation_guides': True
                },
                applicable_errors=[VoiceErrorType.MICROPHONE_ACCESS_DENIED]
            )
        ]
        
        # Network connectivity errors
        self.recovery_actions[VoiceErrorType.NETWORK_CONNECTIVITY] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY_WITH_BACKOFF,
                priority=1,
                max_retries=3,
                parameters={'base_delay': 2.0, 'max_delay': 10.0},
                applicable_errors=[VoiceErrorType.NETWORK_CONNECTIVITY]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.CACHED_RESPONSE,
                priority=2,
                parameters={
                    'use_spiritual_fallback_responses': True,
                    'include_offline_mantras': True
                },
                applicable_errors=[VoiceErrorType.NETWORK_CONNECTIVITY]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK_TO_TEXT,
                priority=3,
                parameters={'offline_mode': True},
                applicable_errors=[VoiceErrorType.NETWORK_CONNECTIVITY]
            )
        ]
        
        # Speech recognition failures
        self.recovery_actions[VoiceErrorType.SPEECH_RECOGNITION_FAILED] = [
            RecoveryAction(
                strategy=RecoveryStrategy.REDUCE_QUALITY,
                priority=1,
                parameters={
                    'lower_sample_rate': True,
                    'reduce_noise_filtering': True,
                    'extend_timeout': True
                },
                applicable_errors=[VoiceErrorType.SPEECH_RECOGNITION_FAILED]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.PROMPT_USER_ACTION,
                priority=2,
                parameters={
                    'message': 'Please speak more clearly or closer to the microphone',
                    'include_pronunciation_tips': True,
                    'sanskrit_guidance': True
                },
                applicable_errors=[VoiceErrorType.SPEECH_RECOGNITION_FAILED]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.ALTERNATIVE_INPUT_METHOD,
                priority=3,
                parameters={
                    'enable_text_input': True,
                    'provide_voice_to_text_alternative': True
                },
                applicable_errors=[VoiceErrorType.SPEECH_RECOGNITION_FAILED]
            )
        ]
        
        # TTS engine failures
        self.recovery_actions[VoiceErrorType.TTS_ENGINE_FAILED] = [
            RecoveryAction(
                strategy=RecoveryStrategy.SWITCH_VOICE_ENGINE,
                priority=1,
                parameters={
                    'preferred_engines': ['Google TTS', 'Web Speech API', 'Browser TTS'],
                    'maintain_spiritual_tone': True
                },
                applicable_errors=[VoiceErrorType.TTS_ENGINE_FAILED]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.REDUCE_QUALITY,
                priority=2,
                parameters={
                    'disable_ssml': True,
                    'simplify_pronunciation': True,
                    'fallback_voice': True
                },
                applicable_errors=[VoiceErrorType.TTS_ENGINE_FAILED]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK_TO_TEXT,
                priority=3,
                parameters={
                    'include_pronunciation_guides': True,
                    'format_for_reading': True
                },
                applicable_errors=[VoiceErrorType.TTS_ENGINE_FAILED]
            )
        ]
        
        # Sanskrit recognition failures
        self.recovery_actions[VoiceErrorType.SANSKRIT_RECOGNITION_FAILED] = [
            RecoveryAction(
                strategy=RecoveryStrategy.PROMPT_USER_ACTION,
                priority=1,
                parameters={
                    'message': 'Sanskrit pronunciation assistance available',
                    'provide_phonetic_guide': True,
                    'offer_simplified_pronunciation': True
                },
                applicable_errors=[VoiceErrorType.SANSKRIT_RECOGNITION_FAILED]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.REDUCE_QUALITY,
                priority=2,
                parameters={
                    'use_simplified_sanskrit': True,
                    'phonetic_approximation': True,
                    'regional_pronunciation': True
                },
                applicable_errors=[VoiceErrorType.SANSKRIT_RECOGNITION_FAILED]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.ALTERNATIVE_INPUT_METHOD,
                priority=3,
                parameters={
                    'enable_sanskrit_keyboard': True,
                    'transliteration_support': True
                },
                applicable_errors=[VoiceErrorType.SANSKRIT_RECOGNITION_FAILED]
            )
        ]
        
        # Audio quality issues
        self.recovery_actions[VoiceErrorType.AUDIO_QUALITY_POOR] = [
            RecoveryAction(
                strategy=RecoveryStrategy.PROMPT_USER_ACTION,
                priority=1,
                parameters={
                    'message': 'Please check your microphone and reduce background noise',
                    'provide_audio_tips': True
                },
                applicable_errors=[VoiceErrorType.AUDIO_QUALITY_POOR]
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.REDUCE_QUALITY,
                priority=2,
                parameters={
                    'increase_noise_reduction': True,
                    'lower_quality_threshold': True,
                    'extend_recording_time': True
                },
                applicable_errors=[VoiceErrorType.AUDIO_QUALITY_POOR]
            )
        ]
        
        self.logger.info(f"Initialized recovery actions for {len(self.recovery_actions)} error types")
    
    def _initialize_fallback_handlers(self):
        """Initialize fallback mode handlers"""
        
        self.fallback_handlers = {
            VoiceFallbackMode.TEXT_ONLY: self._handle_text_only_fallback,
            VoiceFallbackMode.SIMPLIFIED_VOICE: self._handle_simplified_voice_fallback,
            VoiceFallbackMode.HYBRID_MODE: self._handle_hybrid_mode_fallback,
            VoiceFallbackMode.OFFLINE_MODE: self._handle_offline_mode_fallback,
            VoiceFallbackMode.ASSISTED_MODE: self._handle_assisted_mode_fallback
        }
        
        self.logger.info(f"Initialized {len(self.fallback_handlers)} fallback handlers")
    
    async def handle_voice_error(
        self, 
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """
        Handle voice error with appropriate recovery strategy
        
        Args:
            error_context: Context information about the error
            
        Returns:
            Recovery result with details about the actions taken
        """
        
        start_time = time.time()
        self.recovery_stats['total_errors'] += 1
        
        self.logger.warning(
            f"Voice error detected: {error_context.error_type.value} - {error_context.error_message}"
        )
        
        try:
            # Get applicable recovery actions
            recovery_actions = self.recovery_actions.get(error_context.error_type, [])
            
            if not recovery_actions:
                # No specific recovery actions, try general fallback
                result = await self._apply_general_fallback(error_context)
            else:
                # Try recovery actions in priority order
                result = await self._execute_recovery_actions(error_context, recovery_actions)
            
            # Update statistics
            recovery_time = int((time.time() - start_time) * 1000)
            result.recovery_time_ms = recovery_time
            
            if result.success:
                self.recovery_stats['successful_recoveries'] += 1
            
            if result.fallback_mode:
                self.recovery_stats['fallback_activations'] += 1
            
            if result.user_notified:
                self.recovery_stats['user_notifications'] += 1
            
            # Update average recovery time
            total_errors = self.recovery_stats['total_errors']
            old_avg = self.recovery_stats['avg_recovery_time']
            self.recovery_stats['avg_recovery_time'] = (
                (old_avg * (total_errors - 1) + recovery_time) / total_errors
            )
            
            # Track error frequency
            error_type_str = error_context.error_type.value
            if error_type_str not in self.recovery_stats['most_common_errors']:
                self.recovery_stats['most_common_errors'][error_type_str] = 0
            self.recovery_stats['most_common_errors'][error_type_str] += 1
            
            # Track strategy effectiveness
            strategy_str = result.strategy_used.value
            if strategy_str not in self.recovery_stats['most_effective_strategies']:
                self.recovery_stats['most_effective_strategies'][strategy_str] = {'attempts': 0, 'successes': 0}
            
            self.recovery_stats['most_effective_strategies'][strategy_str]['attempts'] += 1
            if result.success:
                self.recovery_stats['most_effective_strategies'][strategy_str]['successes'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Recovery system error: {e}")
            traceback.print_exc()
            
            # Return failed recovery result
            return VoiceRecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.FALLBACK_TO_TEXT,
                final_error=str(e),
                recovery_time_ms=int((time.time() - start_time) * 1000),
                graceful_degradation=True
            )
    
    async def _execute_recovery_actions(
        self,
        error_context: VoiceErrorContext,
        recovery_actions: List[RecoveryAction]
    ) -> VoiceRecoveryResult:
        """Execute recovery actions in priority order"""
        
        # Sort actions by priority
        sorted_actions = sorted(recovery_actions, key=lambda x: x.priority)
        
        actions_attempted = []
        
        for action in sorted_actions:
            # Skip if already tried this strategy
            if action.strategy in error_context.previous_strategies:
                continue
            
            # Check prerequisites
            if not self._check_prerequisites(action, error_context):
                continue
            
            self.logger.info(f"Attempting recovery strategy: {action.strategy.value}")
            actions_attempted.append(action.strategy.value)
            
            try:
                # Execute the recovery action
                result = await self._execute_single_action(action, error_context)
                
                if result.success:
                    result.actions_attempted = actions_attempted
                    return result
                
            except Exception as e:
                self.logger.error(f"Recovery action failed: {action.strategy.value} - {e}")
                continue
        
        # All recovery actions failed, apply general fallback
        self.logger.warning("All recovery actions failed, applying general fallback")
        result = await self._apply_general_fallback(error_context)
        result.actions_attempted = actions_attempted
        
        return result
    
    def _check_prerequisites(self, action: RecoveryAction, context: VoiceErrorContext) -> bool:
        """Check if action prerequisites are met"""
        
        for prerequisite in action.prerequisites:
            if prerequisite == 'network_available' and context.network_status != 'connected':
                return False
            elif prerequisite == 'microphone_available' and context.audio_context is None:
                return False
            elif prerequisite == 'browser_support' and not self._check_browser_support():
                return False
        
        return True
    
    def _check_browser_support(self) -> bool:
        """Check browser support for voice features"""
        # This would normally check navigator.getUserMedia, webkitSpeechRecognition, etc.
        # For now, assume basic support
        return True
    
    async def _execute_single_action(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Execute a single recovery action"""
        
        if action.strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
            return await self._retry_with_backoff(action, error_context)
        elif action.strategy == RecoveryStrategy.FALLBACK_TO_TEXT:
            return await self._fallback_to_text(action, error_context)
        elif action.strategy == RecoveryStrategy.SWITCH_VOICE_ENGINE:
            return await self._switch_voice_engine(action, error_context)
        elif action.strategy == RecoveryStrategy.REDUCE_QUALITY:
            return await self._reduce_quality(action, error_context)
        elif action.strategy == RecoveryStrategy.PROMPT_USER_ACTION:
            return await self._prompt_user_action(action, error_context)
        elif action.strategy == RecoveryStrategy.ALTERNATIVE_INPUT_METHOD:
            return await self._alternative_input_method(action, error_context)
        elif action.strategy == RecoveryStrategy.CACHED_RESPONSE:
            return await self._use_cached_response(action, error_context)
        else:
            return VoiceRecoveryResult(
                success=False,
                strategy_used=action.strategy,
                final_error=f"Unknown recovery strategy: {action.strategy.value}"
            )
    
    async def _retry_with_backoff(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Implement retry with exponential backoff"""
        
        base_delay = action.parameters.get('base_delay', self.config['retry_base_delay'])
        max_delay = action.parameters.get('max_delay', self.config['retry_max_delay'])
        max_retries = action.max_retries
        
        for attempt in range(max_retries):
            if attempt > 0:
                # Calculate delay with exponential backoff
                delay = min(base_delay * (2 ** attempt), max_delay)
                await asyncio.sleep(delay)
            
            # Simulate retry attempt (would be actual voice operation retry)
            success = await self._simulate_voice_operation_retry(error_context)
            
            if success:
                return VoiceRecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.RETRY_WITH_BACKOFF,
                    graceful_degradation=False,
                    voice_quality_after_recovery=0.8
                )
        
        return VoiceRecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.RETRY_WITH_BACKOFF,
            final_error=f"Retry failed after {max_retries} attempts"
        )
    
    async def _simulate_voice_operation_retry(self, error_context: VoiceErrorContext) -> bool:
        """Simulate voice operation retry (placeholder)"""
        # In real implementation, this would retry the actual voice operation
        # For demo purposes, simulate some chance of success
        import random
        return random.random() > 0.7  # 30% chance of success
    
    async def _fallback_to_text(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Fallback to text-only mode"""
        
        maintain_spiritual_tone = action.parameters.get('maintain_spiritual_tone', True)
        include_pronunciation = action.parameters.get('preserve_sanskrit_pronunciation_guides', True)
        
        # Activate text-only fallback mode
        fallback_mode = VoiceFallbackMode.TEXT_ONLY
        
        success = await self.fallback_handlers[fallback_mode](error_context, action.parameters)
        
        return VoiceRecoveryResult(
            success=success,
            strategy_used=RecoveryStrategy.FALLBACK_TO_TEXT,
            fallback_mode=fallback_mode,
            graceful_degradation=True,
            spiritual_context_preserved=maintain_spiritual_tone,
            user_satisfaction_estimated=0.7 if maintain_spiritual_tone else 0.5
        )
    
    async def _switch_voice_engine(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Switch to alternative voice engine"""
        
        preferred_engines = action.parameters.get('preferred_engines', [])
        maintain_spiritual_tone = action.parameters.get('maintain_spiritual_tone', True)
        
        # Try each engine in order
        for engine in preferred_engines:
            self.logger.info(f"Attempting to switch to voice engine: {engine}")
            
            # Simulate engine switch attempt
            success = await self._simulate_engine_switch(engine, error_context)
            
            if success:
                return VoiceRecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.SWITCH_VOICE_ENGINE,
                    graceful_degradation=False,
                    spiritual_context_preserved=maintain_spiritual_tone,
                    voice_quality_after_recovery=0.75
                )
        
        return VoiceRecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.SWITCH_VOICE_ENGINE,
            final_error="No alternative voice engines available"
        )
    
    async def _simulate_engine_switch(self, engine: str, error_context: VoiceErrorContext) -> bool:
        """Simulate switching to alternative voice engine"""
        # In real implementation, this would actually switch TTS/STT engines
        import random
        return random.random() > 0.5  # 50% chance of success
    
    async def _reduce_quality(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Reduce voice quality for better reliability"""
        
        # Apply quality reduction parameters
        lower_sample_rate = action.parameters.get('lower_sample_rate', False)
        reduce_noise_filtering = action.parameters.get('reduce_noise_filtering', False)
        disable_ssml = action.parameters.get('disable_ssml', False)
        
        self.logger.info("Reducing voice quality for better reliability")
        
        # Simulate quality reduction
        success = await self._simulate_quality_reduction(error_context)
        
        return VoiceRecoveryResult(
            success=success,
            strategy_used=RecoveryStrategy.REDUCE_QUALITY,
            graceful_degradation=True,
            voice_quality_after_recovery=0.6,  # Reduced quality
            spiritual_context_preserved=not disable_ssml,
            user_satisfaction_estimated=0.6
        )
    
    async def _simulate_quality_reduction(self, error_context: VoiceErrorContext) -> bool:
        """Simulate voice quality reduction"""
        # In real implementation, this would adjust audio parameters
        import random
        return random.random() > 0.3  # 70% chance of success with reduced quality
    
    async def _prompt_user_action(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Prompt user for corrective action"""
        
        message = action.parameters.get('message', 'Please check your voice settings')
        spiritual_context = action.parameters.get('spiritual_context', False)
        include_pronunciation_tips = action.parameters.get('include_pronunciation_tips', False)
        
        # Construct spiritual-appropriate user message
        if spiritual_context:
            spiritual_message = self._create_spiritual_error_message(error_context, message)
        else:
            spiritual_message = message
        
        self.logger.info(f"Prompting user: {spiritual_message}")
        
        return VoiceRecoveryResult(
            success=True,  # Prompting is always successful
            strategy_used=RecoveryStrategy.PROMPT_USER_ACTION,
            user_notified=True,
            graceful_degradation=True,
            spiritual_context_preserved=spiritual_context,
            user_satisfaction_estimated=0.8 if spiritual_context else 0.6
        )
    
    def _create_spiritual_error_message(self, error_context: VoiceErrorContext, base_message: str) -> str:
        """Create spiritually-appropriate error message"""
        
        spiritual_messages = {
            VoiceErrorType.MICROPHONE_ACCESS_DENIED: 
                "🙏 To receive Krishna's guidance through voice, please allow microphone access. This enables a more immersive spiritual experience.",
            VoiceErrorType.SPEECH_RECOGNITION_FAILED:
                "🕉️ The divine words were not clear. Please speak slowly and clearly, as if chanting a sacred mantra.",
            VoiceErrorType.SANSKRIT_RECOGNITION_FAILED:
                "📿 Sanskrit pronunciation needs patience. Let us guide you through the sacred sounds step by step.",
            VoiceErrorType.NETWORK_CONNECTIVITY:
                "🌐 The divine connection is momentarily disrupted. Please check your internet for continued spiritual guidance.",
        }
        
        return spiritual_messages.get(error_context.error_type, base_message)
    
    async def _alternative_input_method(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Provide alternative input methods"""
        
        enable_text_input = action.parameters.get('enable_text_input', True)
        enable_sanskrit_keyboard = action.parameters.get('enable_sanskrit_keyboard', False)
        
        fallback_mode = VoiceFallbackMode.HYBRID_MODE
        
        success = await self.fallback_handlers[fallback_mode](error_context, action.parameters)
        
        return VoiceRecoveryResult(
            success=success,
            strategy_used=RecoveryStrategy.ALTERNATIVE_INPUT_METHOD,
            fallback_mode=fallback_mode,
            user_notified=True,
            graceful_degradation=True,
            spiritual_context_preserved=True
        )
    
    async def _use_cached_response(
        self,
        action: RecoveryAction,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Use cached spiritual responses for offline operation"""
        
        use_spiritual_fallbacks = action.parameters.get('use_spiritual_fallback_responses', True)
        include_offline_mantras = action.parameters.get('include_offline_mantras', True)
        
        # Simulate cached response retrieval
        success = await self._simulate_cached_response_retrieval(error_context)
        
        fallback_mode = VoiceFallbackMode.OFFLINE_MODE if success else None
        
        return VoiceRecoveryResult(
            success=success,
            strategy_used=RecoveryStrategy.CACHED_RESPONSE,
            fallback_mode=fallback_mode,
            graceful_degradation=True,
            spiritual_context_preserved=use_spiritual_fallbacks,
            user_satisfaction_estimated=0.7 if use_spiritual_fallbacks else 0.5
        )
    
    async def _simulate_cached_response_retrieval(self, error_context: VoiceErrorContext) -> bool:
        """Simulate cached response retrieval"""
        # In real implementation, this would check local cache for spiritual content
        import random
        return random.random() > 0.2  # 80% chance of having cached content
    
    async def _apply_general_fallback(
        self,
        error_context: VoiceErrorContext
    ) -> VoiceRecoveryResult:
        """Apply general fallback when no specific recovery actions are available"""
        
        if self.config['auto_fallback_enabled']:
            # Choose appropriate fallback mode based on error type
            if error_context.error_type in [
                VoiceErrorType.NETWORK_CONNECTIVITY,
                VoiceErrorType.API_RATE_LIMIT
            ]:
                fallback_mode = VoiceFallbackMode.OFFLINE_MODE
            elif error_context.error_type in [
                VoiceErrorType.MICROPHONE_ACCESS_DENIED,
                VoiceErrorType.MICROPHONE_NOT_FOUND
            ]:
                fallback_mode = VoiceFallbackMode.TEXT_ONLY
            else:
                fallback_mode = VoiceFallbackMode.SIMPLIFIED_VOICE
            
            success = await self.fallback_handlers[fallback_mode](error_context, {})
            
            return VoiceRecoveryResult(
                success=success,
                strategy_used=RecoveryStrategy.SILENT_DEGRADATION,
                fallback_mode=fallback_mode,
                graceful_degradation=True,
                spiritual_context_preserved=True
            )
        else:
            return VoiceRecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.PROMPT_USER_ACTION,
                final_error="Auto-fallback disabled, user intervention required"
            )
    
    # Fallback mode handlers
    
    async def _handle_text_only_fallback(
        self,
        error_context: VoiceErrorContext,
        parameters: Dict[str, Any]
    ) -> bool:
        """Handle complete fallback to text-only mode"""
        
        self.logger.info("Activating text-only fallback mode")
        
        # In real implementation, this would:
        # - Disable all voice features
        # - Enable enhanced text interface
        # - Provide pronunciation guides for Sanskrit terms
        # - Maintain spiritual formatting and tone
        
        return True
    
    async def _handle_simplified_voice_fallback(
        self,
        error_context: VoiceErrorContext,
        parameters: Dict[str, Any]
    ) -> bool:
        """Handle fallback to simplified voice processing"""
        
        self.logger.info("Activating simplified voice fallback mode")
        
        # In real implementation, this would:
        # - Disable advanced voice optimizations
        # - Use basic TTS without SSML
        # - Simplify Sanskrit pronunciation
        # - Reduce audio quality for reliability
        
        return True
    
    async def _handle_hybrid_mode_fallback(
        self,
        error_context: VoiceErrorContext,
        parameters: Dict[str, Any]
    ) -> bool:
        """Handle hybrid voice/text fallback mode"""
        
        self.logger.info("Activating hybrid voice/text fallback mode")
        
        # In real implementation, this would:
        # - Provide both voice and text options
        # - Allow switching between modes
        # - Offer guided voice interaction
        # - Provide visual feedback for voice issues
        
        return True
    
    async def _handle_offline_mode_fallback(
        self,
        error_context: VoiceErrorContext,
        parameters: Dict[str, Any]
    ) -> bool:
        """Handle offline mode fallback"""
        
        self.logger.info("Activating offline mode fallback")
        
        # In real implementation, this would:
        # - Use cached spiritual content
        # - Enable offline mantras and basic guidance
        # - Provide limited voice processing using local browser APIs
        # - Store user queries for later processing
        
        return True
    
    async def _handle_assisted_mode_fallback(
        self,
        error_context: VoiceErrorContext,
        parameters: Dict[str, Any]
    ) -> bool:
        """Handle assisted mode with user guidance"""
        
        self.logger.info("Activating assisted mode fallback")
        
        # In real implementation, this would:
        # - Provide step-by-step voice setup guidance
        # - Offer troubleshooting tips
        # - Enable gradual feature restoration
        # - Provide feedback on voice quality
        
        return True
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive recovery statistics"""
        
        stats = self.recovery_stats.copy()
        
        # Calculate success rate
        if stats['total_errors'] > 0:
            stats['success_rate'] = stats['successful_recoveries'] / stats['total_errors']
            stats['fallback_rate'] = stats['fallback_activations'] / stats['total_errors']
        else:
            stats['success_rate'] = 0.0
            stats['fallback_rate'] = 0.0
        
        # Calculate strategy effectiveness
        strategy_effectiveness = {}
        for strategy, data in stats['most_effective_strategies'].items():
            if data['attempts'] > 0:
                effectiveness = data['successes'] / data['attempts']
                strategy_effectiveness[strategy] = {
                    'attempts': data['attempts'],
                    'successes': data['successes'],
                    'effectiveness': effectiveness
                }
        
        stats['strategy_effectiveness'] = strategy_effectiveness
        
        return stats
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update recovery configuration"""
        self.config.update(new_config)
        self.logger.info("Voice recovery configuration updated")
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle voice errors with appropriate recovery strategies
        
        Args:
            error: The error that occurred
            context: Additional context about the error
            
        Returns:
            Recovery result with actions taken
        """
        try:
            # Create error context
            error_context = VoiceErrorContext(
                error=error,
                timestamp=datetime.now(),
                error_type=self._classify_error(error),
                user_context=context or {},
                audio_context=context.get('audio_context') if context else None,
                network_status=context.get('network_status', 'unknown') if context else 'unknown',
                device_info=context.get('device_info', {}) if context else {}
            )
            
            # Update statistics
            self.recovery_stats['total_errors'] += 1
            
            # Get recovery actions for this error type
            recovery_actions = self.recovery_actions.get(error_context.error_type, [])
            
            if not recovery_actions:
                return {
                    'success': False,
                    'message': 'No recovery actions available for this error type',
                    'error_type': error_context.error_type.value,
                    'fallback_used': False
                }
            
            # Attempt recovery
            for action in recovery_actions:
                if self._check_prerequisites(action, error_context):
                    result = {
                        'success': True,
                        'strategy_used': action.strategy.value,
                        'message': f'Applied {action.strategy.value} recovery strategy',
                        'error_type': error_context.error_type.value,
                        'fallback_used': False
                    }
                    self.recovery_stats['successful_recoveries'] += 1
                    return result
            
            # If no action worked, use fallback
            self.recovery_stats['fallback_activations'] += 1
            return {
                'success': True,
                'strategy_used': 'fallback',
                'message': 'Used fallback strategy',
                'error_type': error_context.error_type.value,
                'fallback_used': True
            }
            
        except Exception as e:
            self.logger.error(f"Error in error handling: {e}")
            return {
                'success': False,
                'message': f'Recovery system error: {str(e)}',
                'error_type': 'unknown',
                'fallback_used': False
            }
    
    def handle_poor_quality(self, quality_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Handle poor voice quality with improvement strategies
        
        Args:
            quality_metrics: Quality metrics (snr, clarity, etc.)
            
        Returns:
            Quality improvement result
        """
        try:
            # Analyze quality metrics
            quality_score = quality_metrics.get('overall', 0.0)
            
            if quality_score >= self.config['voice_quality_threshold']:
                return {
                    'action_needed': False,
                    'quality_score': quality_score,
                    'message': 'Voice quality is acceptable'
                }
            
            # Apply quality improvement strategies
            improvements = []
            
            if quality_metrics.get('snr', 0) < 10:  # Low signal-to-noise ratio
                improvements.append('noise_reduction')
            
            if quality_metrics.get('clarity', 0) < 0.7:  # Low clarity
                improvements.append('speech_enhancement')
            
            if quality_metrics.get('volume', 0) < 0.3:  # Low volume
                improvements.append('volume_normalization')
            
            return {
                'action_needed': True,
                'quality_score': quality_score,
                'improvements_applied': improvements,
                'message': f'Applied {len(improvements)} quality improvements',
                'fallback_recommended': quality_score < 0.3
            }
            
        except Exception as e:
            self.logger.error(f"Quality handling error: {e}")
            return {
                'action_needed': False,
                'quality_score': 0.0,
                'message': f'Quality assessment error: {str(e)}'
            }
    
    def handle_interruption(self, interruption_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle voice interaction interruptions
        
        Args:
            interruption_type: Type of interruption (user, system, network, etc.)
            context: Additional context about the interruption
            
        Returns:
            Interruption handling result
        """
        try:
            # Update statistics
            self.recovery_stats['total_errors'] += 1
            
            handling_strategies = {
                'user_interruption': {
                    'action': 'pause_and_acknowledge',
                    'message': 'How may I assist you further?',
                    'resume_capability': True
                },
                'network_interruption': {
                    'action': 'retry_with_cache',
                    'message': 'Connection restored, continuing...',
                    'resume_capability': True
                },
                'system_interruption': {
                    'action': 'graceful_restart',
                    'message': 'Voice system restarted, please continue',
                    'resume_capability': False
                },
                'audio_device_interruption': {
                    'action': 'switch_to_fallback',
                    'message': 'Switching to alternative audio output',
                    'resume_capability': True
                }
            }
            
            strategy = handling_strategies.get(interruption_type, {
                'action': 'acknowledge_and_continue',
                'message': 'Continuing with voice interaction',
                'resume_capability': True
            })
            
            result = {
                'interruption_handled': True,
                'strategy_applied': strategy['action'],
                'message': strategy['message'],
                'can_resume': strategy['resume_capability'],
                'interruption_type': interruption_type
            }
            
            # Add context-specific handling
            if context:
                if context.get('preserve_context'):
                    result['context_preserved'] = True
                if context.get('spiritual_content'):
                    result['message'] = f"May Krishna's wisdom guide us as we continue. {strategy['message']}"
            
            self.recovery_stats['successful_recoveries'] += 1
            return result
            
        except Exception as e:
            self.logger.error(f"Interruption handling error: {e}")
            return {
                'interruption_handled': False,
                'message': f'Interruption handling error: {str(e)}',
                'can_resume': False,
                'interruption_type': interruption_type
            }
    
    def _classify_error(self, error: Exception) -> VoiceErrorType:
        """Classify error type based on exception"""
        error_str = str(error).lower()
        
        if 'microphone' in error_str or 'permission' in error_str:
            return VoiceErrorType.MICROPHONE_ACCESS_DENIED
        elif 'network' in error_str or 'connection' in error_str:
            return VoiceErrorType.NETWORK_CONNECTIVITY_ISSUES
        elif 'recognition' in error_str or 'speech' in error_str:
            return VoiceErrorType.SPEECH_RECOGNITION_FAILED
        elif 'tts' in error_str or 'synthesis' in error_str:
            return VoiceErrorType.TTS_ENGINE_FAILED
        elif 'sanskrit' in error_str:
            return VoiceErrorType.SANSKRIT_RECOGNITION_FAILED
        else:
            return VoiceErrorType.AUDIO_PLAYBACK_FAILED
