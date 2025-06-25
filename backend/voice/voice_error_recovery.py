"""
Voice Error Recovery and Fallback Mechanisms

This module provides comprehensive error recovery and fallback systems for voice 
interface functionality, ensuring reliable spiritual guidance delivery even when 
voice services experience issues.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field


class VoiceErrorType(Enum):
    """Types of voice-related errors"""
    # Speech Recognition Errors
    NO_SPEECH_DETECTED = "no_speech_detected"
    SPEECH_UNCLEAR = "speech_unclear"
    AUDIO_INPUT_FAILED = "audio_input_failed"
    RECOGNITION_TIMEOUT = "recognition_timeout"
    LANGUAGE_NOT_SUPPORTED = "language_not_supported"
    
    # Text-to-Speech Errors
    TTS_SERVICE_UNAVAILABLE = "tts_service_unavailable"
    VOICE_SYNTHESIS_FAILED = "voice_synthesis_failed"
    AUDIO_OUTPUT_FAILED = "audio_output_failed"
    VOICE_NOT_AVAILABLE = "voice_not_available"
    
    # Network and Service Errors
    NETWORK_TIMEOUT = "network_timeout"
    SERVICE_QUOTA_EXCEEDED = "service_quota_exceeded"
    API_KEY_INVALID = "api_key_invalid"
    SERVICE_MAINTENANCE = "service_maintenance"
    
    # Browser/Device Errors
    MICROPHONE_PERMISSION_DENIED = "microphone_permission_denied"
    MICROPHONE_NOT_AVAILABLE = "microphone_not_available"
    SPEAKER_NOT_AVAILABLE = "speaker_not_available"
    BROWSER_NOT_SUPPORTED = "browser_not_supported"
    
    # Sanskrit/Spiritual Content Errors
    SANSKRIT_PRONUNCIATION_FAILED = "sanskrit_pronunciation_failed"
    SPIRITUAL_CONTENT_VALIDATION_FAILED = "spiritual_content_validation_failed"
    MANTRA_PROCESSING_ERROR = "mantra_processing_error"


class FallbackStrategy(Enum):
    """Voice fallback strategies"""
    TEXT_DISPLAY = "text_display"              # Show text instead of speech
    SIMPLIFIED_VOICE = "simplified_voice"      # Use basic TTS without optimization
    OFFLINE_VOICE = "offline_voice"           # Use offline/browser-based voice
    PHONETIC_GUIDE = "phonetic_guide"         # Show pronunciation guides
    AUDIO_ALTERNATIVES = "audio_alternatives" # Pre-recorded audio clips
    VISUAL_CUES = "visual_cues"              # Visual indicators and animations
    GESTURE_INPUT = "gesture_input"           # Alternative input methods


class RecoveryAction(Enum):
    """Recovery actions for voice errors"""
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    SWITCH_TO_FALLBACK = "switch_to_fallback"
    REQUEST_USER_ACTION = "request_user_action"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    SERVICE_RESTART = "service_restart"
    ERROR_REPORTING = "error_reporting"


@dataclass
class VoiceError:
    """Voice error information"""
    error_type: VoiceErrorType
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    is_recoverable: bool = True
    severity: str = "medium"  # low, medium, high, critical
    spiritual_context: Optional[str] = None


@dataclass
class RecoveryRule:
    """Rule for handling specific voice errors"""
    error_type: VoiceErrorType
    max_retries: int
    retry_delay: float  # seconds
    fallback_strategy: FallbackStrategy
    recovery_action: RecoveryAction
    timeout: float = 30.0
    requires_user_action: bool = False
    custom_handler: Optional[Callable] = None


@dataclass
class VoiceFallbackResult:
    """Result from voice fallback operation"""
    success: bool
    fallback_used: FallbackStrategy
    original_error: VoiceError
    fallback_data: Dict[str, Any] = field(default_factory=dict)
    user_message: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class VoiceErrorRecovery:
    """
    Comprehensive voice error recovery and fallback system
    """
    
    def __init__(self):
        """Initialize voice error recovery system"""
        self.logger = logging.getLogger(__name__)
        
        # Error tracking
        self.error_history: List[VoiceError] = []
        self.recovery_stats = {
            'total_errors': 0,
            'successful_recoveries': 0,
            'fallback_activations': 0,
            'retry_attempts': 0,
            'user_interventions': 0
        }
        
        # Recovery rules
        self.recovery_rules: Dict[VoiceErrorType, RecoveryRule] = {}
        self._initialize_recovery_rules()
        
        # Fallback handlers
        self.fallback_handlers: Dict[FallbackStrategy, Callable] = {}
        self._initialize_fallback_handlers()
        
        # Service health tracking
        self.service_health = {
            'speech_recognition': {'status': 'healthy', 'last_check': datetime.now()},
            'text_to_speech': {'status': 'healthy', 'last_check': datetime.now()},
            'audio_input': {'status': 'healthy', 'last_check': datetime.now()},
            'audio_output': {'status': 'healthy', 'last_check': datetime.now()}
        }
        
        # Pre-recorded spiritual content for fallbacks
        self.spiritual_fallback_content = {
            'welcome_message': "Welcome to your spiritual guidance session.",
            'connection_error': "Please check your connection and try again.",
            'voice_unavailable': "Voice is currently unavailable. Please read the guidance below.",
            'technical_difficulty': "We're experiencing technical difficulties. Your spiritual journey continues with text guidance.",
            'retry_prompt': "Would you like to try speaking again?",
            'fallback_active': "Using alternative guidance method for your spiritual session."
        }
    
    def _initialize_recovery_rules(self):
        """Initialize recovery rules for different error types"""
        
        self.recovery_rules = {
            # Speech Recognition Errors
            VoiceErrorType.NO_SPEECH_DETECTED: RecoveryRule(
                error_type=VoiceErrorType.NO_SPEECH_DETECTED,
                max_retries=3,
                retry_delay=2.0,
                fallback_strategy=FallbackStrategy.TEXT_DISPLAY,
                recovery_action=RecoveryAction.REQUEST_USER_ACTION,
                requires_user_action=True
            ),
            
            VoiceErrorType.SPEECH_UNCLEAR: RecoveryRule(
                error_type=VoiceErrorType.SPEECH_UNCLEAR,
                max_retries=2,
                retry_delay=1.0,
                fallback_strategy=FallbackStrategy.PHONETIC_GUIDE,
                recovery_action=RecoveryAction.RETRY_WITH_BACKOFF
            ),
            
            VoiceErrorType.RECOGNITION_TIMEOUT: RecoveryRule(
                error_type=VoiceErrorType.RECOGNITION_TIMEOUT,
                max_retries=2,
                retry_delay=3.0,
                fallback_strategy=FallbackStrategy.TEXT_DISPLAY,
                recovery_action=RecoveryAction.SWITCH_TO_FALLBACK,
                timeout=15.0
            ),
            
            # TTS Errors
            VoiceErrorType.TTS_SERVICE_UNAVAILABLE: RecoveryRule(
                error_type=VoiceErrorType.TTS_SERVICE_UNAVAILABLE,
                max_retries=3,
                retry_delay=5.0,
                fallback_strategy=FallbackStrategy.OFFLINE_VOICE,
                recovery_action=RecoveryAction.GRACEFUL_DEGRADATION
            ),
            
            VoiceErrorType.VOICE_SYNTHESIS_FAILED: RecoveryRule(
                error_type=VoiceErrorType.VOICE_SYNTHESIS_FAILED,
                max_retries=2,
                retry_delay=2.0,
                fallback_strategy=FallbackStrategy.SIMPLIFIED_VOICE,
                recovery_action=RecoveryAction.RETRY_WITH_BACKOFF
            ),
            
            # Permission Errors
            VoiceErrorType.MICROPHONE_PERMISSION_DENIED: RecoveryRule(
                error_type=VoiceErrorType.MICROPHONE_PERMISSION_DENIED,
                max_retries=0,  # No retry for permission issues
                retry_delay=0.0,
                fallback_strategy=FallbackStrategy.TEXT_DISPLAY,
                recovery_action=RecoveryAction.REQUEST_USER_ACTION,
                requires_user_action=True
            ),
            
            # Network Errors
            VoiceErrorType.NETWORK_TIMEOUT: RecoveryRule(
                error_type=VoiceErrorType.NETWORK_TIMEOUT,
                max_retries=3,
                retry_delay=5.0,
                fallback_strategy=FallbackStrategy.OFFLINE_VOICE,
                recovery_action=RecoveryAction.RETRY_WITH_BACKOFF
            ),
            
            # Sanskrit/Spiritual Content Errors
            VoiceErrorType.SANSKRIT_PRONUNCIATION_FAILED: RecoveryRule(
                error_type=VoiceErrorType.SANSKRIT_PRONUNCIATION_FAILED,
                max_retries=1,
                retry_delay=1.0,
                fallback_strategy=FallbackStrategy.PHONETIC_GUIDE,
                recovery_action=RecoveryAction.GRACEFUL_DEGRADATION
            ),
            
            VoiceErrorType.MANTRA_PROCESSING_ERROR: RecoveryRule(
                error_type=VoiceErrorType.MANTRA_PROCESSING_ERROR,
                max_retries=2,
                retry_delay=2.0,
                fallback_strategy=FallbackStrategy.AUDIO_ALTERNATIVES,
                recovery_action=RecoveryAction.SWITCH_TO_FALLBACK
            )
        }
        
        self.logger.info(f"Initialized {len(self.recovery_rules)} recovery rules")
    
    def _initialize_fallback_handlers(self):
        """Initialize fallback handlers"""
        
        self.fallback_handlers = {
            FallbackStrategy.TEXT_DISPLAY: self._handle_text_display_fallback,
            FallbackStrategy.SIMPLIFIED_VOICE: self._handle_simplified_voice_fallback,
            FallbackStrategy.OFFLINE_VOICE: self._handle_offline_voice_fallback,
            FallbackStrategy.PHONETIC_GUIDE: self._handle_phonetic_guide_fallback,
            FallbackStrategy.AUDIO_ALTERNATIVES: self._handle_audio_alternatives_fallback,
            FallbackStrategy.VISUAL_CUES: self._handle_visual_cues_fallback
        }
        
        self.logger.info(f"Initialized {len(self.fallback_handlers)} fallback handlers")
    
    async def handle_voice_error(self, error: VoiceError) -> VoiceFallbackResult:
        """
        Handle voice error with recovery and fallback
        
        Args:
            error: Voice error to handle
            
        Returns:
            Fallback result with recovery information
        """
        
        try:
            self.logger.warning(f"Handling voice error: {error.error_type.value} - {error.message}")
            
            # Add to error history
            self.error_history.append(error)
            self.recovery_stats['total_errors'] += 1
            
            # Get recovery rule
            rule = self.recovery_rules.get(error.error_type)
            if not rule:
                # Default rule for unknown errors
                rule = RecoveryRule(
                    error_type=error.error_type,
                    max_retries=1,
                    retry_delay=2.0,
                    fallback_strategy=FallbackStrategy.TEXT_DISPLAY,
                    recovery_action=RecoveryAction.GRACEFUL_DEGRADATION
                )
            
            # Attempt recovery
            recovery_result = await self._attempt_recovery(error, rule)
            
            if recovery_result.success:
                self.recovery_stats['successful_recoveries'] += 1
                self.logger.info(f"Successfully recovered from {error.error_type.value}")
            else:
                self.logger.warning(f"Recovery failed for {error.error_type.value}, using fallback")
            
            return recovery_result
            
        except Exception as e:
            self.logger.error(f"Error handling voice error: {e}")
            
            # Return basic fallback result
            return VoiceFallbackResult(
                success=False,
                fallback_used=FallbackStrategy.TEXT_DISPLAY,
                original_error=error,
                user_message="Technical difficulties. Please use text interface.",
                recovery_suggestions=["Refresh the page", "Check your internet connection"]
            )
    
    async def _attempt_recovery(self, error: VoiceError, rule: RecoveryRule) -> VoiceFallbackResult:
        """Attempt to recover from voice error"""
        
        # Check if we should retry
        if error.retry_count < rule.max_retries and error.is_recoverable:
            
            # Increment retry count
            error.retry_count += 1
            self.recovery_stats['retry_attempts'] += 1
            
            # Wait before retry
            if rule.retry_delay > 0:
                await asyncio.sleep(rule.retry_delay)
            
            # For now, simulate retry success/failure
            # In real implementation, this would call the original voice function
            retry_success = await self._simulate_retry(error, rule)
            
            if retry_success:
                return VoiceFallbackResult(
                    success=True,
                    fallback_used=FallbackStrategy.TEXT_DISPLAY,  # No fallback needed
                    original_error=error,
                    user_message="Voice service restored.",
                    recovery_suggestions=[]
                )
        
        # Recovery failed or max retries reached, use fallback
        self.recovery_stats['fallback_activations'] += 1
        
        fallback_result = await self._execute_fallback(error, rule)
        
        return fallback_result
    
    async def _simulate_retry(self, error: VoiceError, rule: RecoveryRule) -> bool:
        """
        Simulate retry attempt (placeholder for actual retry logic)
        In real implementation, this would retry the original voice operation
        """
        
        # Simulate different success rates based on error type
        success_rates = {
            VoiceErrorType.NETWORK_TIMEOUT: 0.7,
            VoiceErrorType.TTS_SERVICE_UNAVAILABLE: 0.5,
            VoiceErrorType.SPEECH_UNCLEAR: 0.8,
            VoiceErrorType.RECOGNITION_TIMEOUT: 0.6,
            VoiceErrorType.VOICE_SYNTHESIS_FAILED: 0.4
        }
        
        success_rate = success_rates.get(error.error_type, 0.3)
        
        # Simulate async operation
        await asyncio.sleep(0.1)
        
        # Return success based on probability
        import random
        return random.random() < success_rate
    
    async def _execute_fallback(self, error: VoiceError, rule: RecoveryRule) -> VoiceFallbackResult:
        """Execute fallback strategy"""
        
        handler = self.fallback_handlers.get(rule.fallback_strategy)
        
        if handler:
            fallback_data = await handler(error, rule)
        else:
            # Default fallback
            fallback_data = await self._handle_text_display_fallback(error, rule)
        
        # Generate user-friendly message
        user_message = self._generate_user_message(error, rule)
        recovery_suggestions = self._generate_recovery_suggestions(error, rule)
        
        return VoiceFallbackResult(
            success=True,  # Fallback is considered successful
            fallback_used=rule.fallback_strategy,
            original_error=error,
            fallback_data=fallback_data,
            user_message=user_message,
            recovery_suggestions=recovery_suggestions
        )
    
    async def _handle_text_display_fallback(self, error: VoiceError, rule: RecoveryRule) -> Dict[str, Any]:
        """Handle text display fallback"""
        
        return {
            'display_type': 'text',
            'content': {
                'message': self.spiritual_fallback_content.get(
                    'voice_unavailable', 
                    "Voice guidance is temporarily unavailable. Please read the spiritual guidance below."
                ),
                'show_text_interface': True,
                'enable_typing': True,
                'spiritual_context': error.spiritual_context
            },
            'accessibility': {
                'screen_reader_friendly': True,
                'high_contrast': True,
                'large_text_option': True
            }
        }
    
    async def _handle_simplified_voice_fallback(self, error: VoiceError, rule: RecoveryRule) -> Dict[str, Any]:
        """Handle simplified voice fallback"""
        
        return {
            'voice_type': 'browser_default',
            'optimization_disabled': True,
            'settings': {
                'rate': 0.9,
                'pitch': 1.0,
                'volume': 0.8,
                'voice': 'default'
            },
            'features_disabled': [
                'sanskrit_optimization',
                'spiritual_tone_adjustment',
                'advanced_pronunciation'
            ],
            'fallback_message': "Using simplified voice synthesis for spiritual guidance."
        }
    
    async def _handle_offline_voice_fallback(self, error: VoiceError, rule: RecoveryRule) -> Dict[str, Any]:
        """Handle offline voice fallback"""
        
        return {
            'voice_type': 'browser_native',
            'offline_mode': True,
            'available_voices': ['default', 'male', 'female'],
            'limitations': [
                'No Sanskrit optimization',
                'Basic pronunciation only',
                'Limited emotional expression'
            ],
            'instructions': "Using your browser's built-in voice capabilities."
        }
    
    async def _handle_phonetic_guide_fallback(self, error: VoiceError, rule: RecoveryRule) -> Dict[str, Any]:
        """Handle phonetic guide fallback"""
        
        return {
            'display_type': 'phonetic_text',
            'features': {
                'show_pronunciation': True,
                'sanskrit_transliteration': True,
                'audio_symbols': True,
                'syllable_breakdown': True
            },
            'content': {
                'phonetic_guides': True,
                'pronunciation_tips': True,
                'mantra_guides': True
            },
            'instructions': "Pronunciation guides are shown to help with Sanskrit terms."
        }
    
    async def _handle_audio_alternatives_fallback(self, error: VoiceError, rule: RecoveryRule) -> Dict[str, Any]:
        """Handle audio alternatives fallback"""
        
        return {
            'audio_type': 'prerecorded',
            'available_content': {
                'mantras': ['om', 'om_namah_shivaya', 'hare_krishna'],
                'blessings': ['peace_blessing', 'wisdom_blessing'],
                'guidance': ['basic_meditation', 'breathing_exercise']
            },
            'format': 'mp3',
            'fallback_message': "Using pre-recorded spiritual audio content."
        }
    
    async def _handle_visual_cues_fallback(self, error: VoiceError, rule: RecoveryRule) -> Dict[str, Any]:
        """Handle visual cues fallback"""
        
        return {
            'visual_type': 'enhanced_ui',
            'features': {
                'animated_text': True,
                'breathing_animations': True,
                'sacred_symbols': True,
                'progress_indicators': True
            },
            'accessibility': {
                'color_coding': True,
                'size_adjustments': True,
                'motion_options': True
            },
            'instructions': "Enhanced visual guidance for your spiritual session."
        }
    
    def _generate_user_message(self, error: VoiceError, rule: RecoveryRule) -> str:
        """Generate user-friendly error message"""
        
        # Map error types to user-friendly messages
        user_messages = {
            VoiceErrorType.NO_SPEECH_DETECTED: "I didn't hear anything. Please try speaking again.",
            VoiceErrorType.SPEECH_UNCLEAR: "I couldn't understand that clearly. Please speak a bit more clearly.",
            VoiceErrorType.MICROPHONE_PERMISSION_DENIED: "Microphone access is needed for voice interaction. Please enable it in your browser settings.",
            VoiceErrorType.TTS_SERVICE_UNAVAILABLE: "Voice synthesis is temporarily unavailable. I'll show you the guidance in text.",
            VoiceErrorType.NETWORK_TIMEOUT: "Connection seems slow. Let me try a different approach for your spiritual guidance.",
            VoiceErrorType.SANSKRIT_PRONUNCIATION_FAILED: "Having trouble with Sanskrit pronunciation. I'll show you pronunciation guides.",
            VoiceErrorType.MANTRA_PROCESSING_ERROR: "Let me help you with that mantra using a different method."
        }
        
        base_message = user_messages.get(
            error.error_type, 
            "We're experiencing a technical issue, but your spiritual journey continues."
        )
        
        # Add spiritual context if available
        if error.spiritual_context:
            base_message += f" We're still here to guide you on your {error.spiritual_context} practice."
        
        return base_message
    
    def _generate_recovery_suggestions(self, error: VoiceError, rule: RecoveryRule) -> List[str]:
        """Generate recovery suggestions for user"""
        
        suggestions_map = {
            VoiceErrorType.NO_SPEECH_DETECTED: [
                "Check that your microphone is working",
                "Speak clearly and a bit louder",
                "Try moving closer to your microphone"
            ],
            VoiceErrorType.MICROPHONE_PERMISSION_DENIED: [
                "Click the microphone icon in your browser address bar",
                "Allow microphone access in browser settings",
                "Refresh the page and try again"
            ],
            VoiceErrorType.NETWORK_TIMEOUT: [
                "Check your internet connection",
                "Try refreshing the page",
                "Use text input if voice continues to have issues"
            ],
            VoiceErrorType.TTS_SERVICE_UNAVAILABLE: [
                "Try using text-based guidance",
                "Check back in a few minutes",
                "Read the guidance aloud to yourself"
            ],
            VoiceErrorType.SPEECH_UNCLEAR: [
                "Speak more slowly and clearly",
                "Reduce background noise",
                "Try using simpler phrases"
            ]
        }
        
        return suggestions_map.get(error.error_type, [
            "Try refreshing the page",
            "Check your internet connection",
            "Contact support if the issue persists"
        ])
    
    def create_voice_error(
        self, 
        error_type: VoiceErrorType, 
        message: str,
        context: Optional[Dict[str, Any]] = None,
        spiritual_context: Optional[str] = None,
        severity: str = "medium"
    ) -> VoiceError:
        """Create a voice error object"""
        
        return VoiceError(
            error_type=error_type,
            message=message,
            context=context or {},
            spiritual_context=spiritual_context,
            severity=severity,
            is_recoverable=self._is_error_recoverable(error_type)
        )
    
    def _is_error_recoverable(self, error_type: VoiceErrorType) -> bool:
        """Determine if an error type is recoverable"""
        
        non_recoverable_errors = {
            VoiceErrorType.MICROPHONE_PERMISSION_DENIED,
            VoiceErrorType.BROWSER_NOT_SUPPORTED,
            VoiceErrorType.API_KEY_INVALID
        }
        
        return error_type not in non_recoverable_errors
    
    def update_service_health(self, service: str, status: str):
        """Update service health status"""
        
        if service in self.service_health:
            self.service_health[service] = {
                'status': status,
                'last_check': datetime.now()
            }
            
            self.logger.info(f"Updated {service} health status to {status}")
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get current service health status"""
        return self.service_health.copy()
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error and recovery statistics"""
        
        stats = self.recovery_stats.copy()
        
        # Calculate derived statistics
        if stats['total_errors'] > 0:
            stats['recovery_success_rate'] = stats['successful_recoveries'] / stats['total_errors']
            stats['fallback_rate'] = stats['fallback_activations'] / stats['total_errors']
        else:
            stats['recovery_success_rate'] = 1.0
            stats['fallback_rate'] = 0.0
        
        # Recent error trends
        recent_errors = [
            error for error in self.error_history 
            if error.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        stats['recent_errors_count'] = len(recent_errors)
        stats['error_types_recent'] = {}
        
        for error in recent_errors:
            error_type = error.error_type.value
            stats['error_types_recent'][error_type] = stats['error_types_recent'].get(error_type, 0) + 1
        
        return stats
    
    def clear_error_history(self, older_than_hours: int = 24):
        """Clear old error history"""
        
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        self.error_history = [
            error for error in self.error_history 
            if error.timestamp > cutoff_time
        ]
        
        self.logger.info(f"Cleared error history older than {older_than_hours} hours")


# Convenience functions
def create_voice_error_recovery() -> VoiceErrorRecovery:
    """Create voice error recovery system"""
    return VoiceErrorRecovery()


async def handle_speech_recognition_error(
    error_message: str, 
    context: Dict[str, Any] = None,
    recovery_system: VoiceErrorRecovery = None
) -> VoiceFallbackResult:
    """Handle speech recognition error"""
    
    if not recovery_system:
        recovery_system = VoiceErrorRecovery()
    
    # Determine error type based on message
    error_type = VoiceErrorType.SPEECH_UNCLEAR
    if "no speech" in error_message.lower():
        error_type = VoiceErrorType.NO_SPEECH_DETECTED
    elif "timeout" in error_message.lower():
        error_type = VoiceErrorType.RECOGNITION_TIMEOUT
    elif "permission" in error_message.lower():
        error_type = VoiceErrorType.MICROPHONE_PERMISSION_DENIED
    
    error = recovery_system.create_voice_error(
        error_type=error_type,
        message=error_message,
        context=context,
        spiritual_context="meditation session"
    )
    
    return await recovery_system.handle_voice_error(error)


async def handle_tts_error(
    error_message: str,
    context: Dict[str, Any] = None,
    recovery_system: VoiceErrorRecovery = None
) -> VoiceFallbackResult:
    """Handle text-to-speech error"""
    
    if not recovery_system:
        recovery_system = VoiceErrorRecovery()
    
    # Determine error type
    error_type = VoiceErrorType.VOICE_SYNTHESIS_FAILED
    if "service unavailable" in error_message.lower():
        error_type = VoiceErrorType.TTS_SERVICE_UNAVAILABLE
    elif "network" in error_message.lower():
        error_type = VoiceErrorType.NETWORK_TIMEOUT
    elif "sanskrit" in error_message.lower():
        error_type = VoiceErrorType.SANSKRIT_PRONUNCIATION_FAILED
    
    error = recovery_system.create_voice_error(
        error_type=error_type,
        message=error_message,
        context=context,
        spiritual_context="spiritual guidance"
    )
    
    return await recovery_system.handle_voice_error(error)
