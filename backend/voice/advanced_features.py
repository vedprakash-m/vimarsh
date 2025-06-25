"""
Advanced Voice Features (Interruption Handling, Voice Commands)

This module provides advanced voice interface features including interruption
handling, voice commands recognition, and intelligent conversation flow
management for the Vimarsh platform.
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class VoiceCommand(Enum):
    """Supported voice commands"""
    # Navigation commands
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    REPEAT = "repeat"
    SKIP = "skip"
    
    # Spiritual practice commands
    START_MEDITATION = "start_meditation"
    END_MEDITATION = "end_meditation"
    PLAY_MANTRA = "play_mantra"
    STOP_MANTRA = "stop_mantra"
    
    # Learning commands
    EXPLAIN_MORE = "explain_more"
    SIMPLIFY = "simplify"
    GIVE_EXAMPLE = "give_example"
    NEXT_TOPIC = "next_topic"
    PREVIOUS_TOPIC = "previous_topic"
    
    # Language commands
    SWITCH_TO_HINDI = "switch_to_hindi"
    SWITCH_TO_ENGLISH = "switch_to_english"
    TRANSLATE = "translate"
    
    # Volume and speed commands
    LOUDER = "louder"
    QUIETER = "quieter"
    FASTER = "faster"
    SLOWER = "slower"
    
    # Help and system commands
    HELP = "help"
    SETTINGS = "settings"
    FEEDBACK = "feedback"


class InterruptionType(Enum):
    """Types of voice interruptions"""
    USER_SPEECH = "user_speech"          # User starts speaking
    BACKGROUND_NOISE = "background_noise" # Loud background noise
    DEVICE_NOTIFICATION = "device_notification"  # Device notification sound
    EMERGENCY = "emergency"              # Emergency interruption
    COMMAND = "command"                  # Voice command interruption
    SILENCE_TIMEOUT = "silence_timeout"   # Long silence detected


class ConversationState(Enum):
    """States of voice conversation"""
    IDLE = "idle"                        # Not speaking or listening
    LISTENING = "listening"              # Listening for user input
    PROCESSING = "processing"            # Processing user request
    SPEAKING = "speaking"                # AI is speaking
    PAUSED = "paused"                   # Conversation paused
    INTERRUPTED = "interrupted"          # Conversation interrupted
    WAITING_FOR_COMMAND = "waiting_for_command"  # Waiting for voice command


@dataclass
class VoiceCommandPattern:
    """Pattern for recognizing voice commands"""
    command: VoiceCommand
    patterns: List[str]  # Regular expression patterns
    keywords: List[str]  # Keywords that might indicate this command
    confidence_threshold: float = 0.7
    languages: List[str] = field(default_factory=lambda: ["en", "hi"])
    
    def matches(self, text: str, language: str = "en") -> Tuple[bool, float]:
        """Check if text matches this command pattern"""
        if language not in self.languages:
            return False, 0.0
        
        text_lower = text.lower().strip()
        confidence = 0.0
        
        # Check exact pattern matches
        for pattern in self.patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                confidence = max(confidence, 0.9)
        
        # Check keyword matches
        keyword_matches = 0
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                keyword_matches += 1
        
        if keyword_matches > 0:
            keyword_confidence = min(0.8, keyword_matches / len(self.keywords))
            confidence = max(confidence, keyword_confidence)
        
        return confidence >= self.confidence_threshold, confidence


@dataclass
class InterruptionEvent:
    """Voice interruption event"""
    interruption_type: InterruptionType
    timestamp: datetime
    confidence: float
    context: Dict[str, Any] = field(default_factory=dict)
    user_text: Optional[str] = None
    detected_command: Optional[VoiceCommand] = None
    should_resume: bool = True
    resume_from_position: Optional[float] = None  # Position in seconds


@dataclass
class ConversationContext:
    """Context for ongoing conversation"""
    session_id: str
    current_state: ConversationState = ConversationState.IDLE
    current_response: Optional[str] = None
    response_position: float = 0.0  # Current position in response (seconds)
    response_start_time: Optional[datetime] = None
    last_user_input: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    interruption_count: int = 0
    last_interruption: Optional[InterruptionEvent] = None
    voice_settings: Dict[str, Any] = field(default_factory=dict)


class VoiceCommandRecognizer:
    """Recognizes voice commands from user speech"""
    
    def __init__(self):
        self.command_patterns = self._load_command_patterns()
        self.recognition_enabled = True
    
    def _load_command_patterns(self) -> List[VoiceCommandPattern]:
        """Load voice command patterns"""
        patterns = [
            # Pause/Resume commands
            VoiceCommandPattern(
                command=VoiceCommand.PAUSE,
                patterns=[r"\b(pause|wait|hold on|stop for a moment)\b"],
                keywords=["pause", "wait", "hold", "stop"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.RESUME,
                patterns=[r"\b(resume|continue|go on|carry on)\b"],
                keywords=["resume", "continue", "go", "carry"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.STOP,
                patterns=[r"\b(stop|end|finish|quit|enough)\b"],
                keywords=["stop", "end", "finish", "quit", "enough"]
            ),
            
            # Repetition commands
            VoiceCommandPattern(
                command=VoiceCommand.REPEAT,
                patterns=[r"\b(repeat|say again|once more|again)\b"],
                keywords=["repeat", "again", "once more"]
            ),
            
            # Spiritual practice commands
            VoiceCommandPattern(
                command=VoiceCommand.START_MEDITATION,
                patterns=[r"\b(start meditation|begin meditation|meditate)\b"],
                keywords=["meditation", "meditate", "start", "begin"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.PLAY_MANTRA,
                patterns=[r"\b(play mantra|chant mantra|start chanting)\b"],
                keywords=["mantra", "chant", "play", "start"]
            ),
            
            # Learning commands
            VoiceCommandPattern(
                command=VoiceCommand.EXPLAIN_MORE,
                patterns=[r"\b(explain more|tell me more|elaborate|details)\b"],
                keywords=["explain", "more", "elaborate", "details"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.SIMPLIFY,
                patterns=[r"\b(simplify|make it simple|easier|simpler)\b"],
                keywords=["simplify", "simple", "easier", "basic"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.GIVE_EXAMPLE,
                patterns=[r"\b(give example|for example|show example)\b"],
                keywords=["example", "show", "instance"]
            ),
            
            # Language commands
            VoiceCommandPattern(
                command=VoiceCommand.SWITCH_TO_HINDI,
                patterns=[r"\b(switch to hindi|speak hindi|hindi me|हिंदी में)\b"],
                keywords=["hindi", "हिंदी", "switch"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.SWITCH_TO_ENGLISH,
                patterns=[r"\b(switch to english|speak english|english me)\b"],
                keywords=["english", "switch"]
            ),
            
            # Volume commands
            VoiceCommandPattern(
                command=VoiceCommand.LOUDER,
                patterns=[r"\b(louder|increase volume|speak up|more volume)\b"],
                keywords=["louder", "volume", "speak up"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.QUIETER,
                patterns=[r"\b(quieter|lower volume|speak softly|less volume)\b"],
                keywords=["quieter", "lower", "softly", "quiet"]
            ),
            
            # Speed commands
            VoiceCommandPattern(
                command=VoiceCommand.FASTER,
                patterns=[r"\b(faster|speed up|quickly|quick)\b"],
                keywords=["faster", "speed", "quick"]
            ),
            VoiceCommandPattern(
                command=VoiceCommand.SLOWER,
                patterns=[r"\b(slower|slow down|slowly)\b"],
                keywords=["slower", "slow"]
            ),
            
            # Help command
            VoiceCommandPattern(
                command=VoiceCommand.HELP,
                patterns=[r"\b(help|what can you do|commands|options)\b"],
                keywords=["help", "commands", "options"]
            )
        ]
        
        return patterns
    
    def recognize_command(self, 
                         text: str, 
                         language: str = "en",
                         context: Optional[ConversationContext] = None) -> Optional[Tuple[VoiceCommand, float]]:
        """
        Recognize voice command from text
        
        Args:
            text: User speech text
            language: Language of the text
            context: Current conversation context
            
        Returns:
            Tuple of (command, confidence) or None if no command recognized
        """
        if not self.recognition_enabled or not text.strip():
            return None
        
        best_command = None
        best_confidence = 0.0
        
        for pattern in self.command_patterns:
            matches, confidence = pattern.matches(text, language)
            if matches and confidence > best_confidence:
                best_command = pattern.command
                best_confidence = confidence
        
        # Context-based adjustments
        if context and best_command:
            best_confidence = self._adjust_confidence_for_context(
                best_command, best_confidence, context
            )
        
        if best_command and best_confidence >= 0.7:
            return best_command, best_confidence
        
        return None
    
    def _adjust_confidence_for_context(self, 
                                     command: VoiceCommand, 
                                     confidence: float,
                                     context: ConversationContext) -> float:
        """Adjust confidence based on conversation context"""
        # Increase confidence for contextually appropriate commands
        if context.current_state == ConversationState.SPEAKING:
            if command in [VoiceCommand.PAUSE, VoiceCommand.STOP, VoiceCommand.REPEAT]:
                confidence = min(1.0, confidence + 0.1)
        
        elif context.current_state == ConversationState.PAUSED:
            if command in [VoiceCommand.RESUME, VoiceCommand.STOP]:
                confidence = min(1.0, confidence + 0.1)
        
        # Decrease confidence for inappropriate commands
        if context.current_state == ConversationState.IDLE:
            if command in [VoiceCommand.PAUSE, VoiceCommand.RESUME]:
                confidence = max(0.0, confidence - 0.2)
        
        return confidence


class InterruptionHandler:
    """Handles voice interruptions intelligently"""
    
    def __init__(self):
        self.interruption_threshold = 0.7
        self.silence_timeout = 10.0  # seconds
        self.noise_threshold = 0.6
        self.handler_enabled = True
    
    def detect_interruption(self, 
                          audio_data: bytes,
                          context: ConversationContext,
                          user_speech_detected: bool = False,
                          user_text: str = "") -> Optional[InterruptionEvent]:
        """
        Detect voice interruption from audio or other signals
        
        Args:
            audio_data: Current audio data
            context: Conversation context
            user_speech_detected: Whether user speech was detected
            user_text: Transcribed user speech if available
            
        Returns:
            InterruptionEvent if interruption detected, None otherwise
        """
        if not self.handler_enabled:
            return None
        
        now = datetime.now()
        
        # Check for user speech interruption
        if user_speech_detected and context.current_state == ConversationState.SPEAKING:
            # Calculate current position in response
            position = 0.0
            if context.response_start_time:
                position = (now - context.response_start_time).total_seconds()
            
            return InterruptionEvent(
                interruption_type=InterruptionType.USER_SPEECH,
                timestamp=now,
                confidence=0.9,
                user_text=user_text,
                should_resume=self._should_resume_after_user_speech(user_text, context),
                resume_from_position=position,
                context={"original_state": context.current_state.value}
            )
        
        # Check for silence timeout
        if (context.current_state == ConversationState.LISTENING and 
            context.response_start_time and
            (now - context.response_start_time).total_seconds() > self.silence_timeout):
            
            return InterruptionEvent(
                interruption_type=InterruptionType.SILENCE_TIMEOUT,
                timestamp=now,
                confidence=0.8,
                should_resume=False,
                context={"timeout_duration": self.silence_timeout}
            )
        
        # Check for background noise (simulated)
        if self._detect_background_noise(audio_data):
            return InterruptionEvent(
                interruption_type=InterruptionType.BACKGROUND_NOISE,
                timestamp=now,
                confidence=0.6,
                should_resume=True,
                context={"noise_level": "high"}
            )
        
        return None
    
    def _should_resume_after_user_speech(self, user_text: str, context: ConversationContext) -> bool:
        """Determine if conversation should resume after user speech"""
        if not user_text:
            return True  # Unknown speech, assume interruption
        
        # Check if user text contains stop/end commands
        stop_words = ["stop", "enough", "end", "finish", "quit", "no more"]
        if any(word in user_text.lower() for word in stop_words):
            return False
        
        # Check if it's a question or command
        if user_text.strip().endswith('?'):
            return False  # User has a question
        
        # If user is asking for clarification, don't resume
        clarification_words = ["what", "how", "why", "explain", "clarify"]
        if any(word in user_text.lower() for word in clarification_words):
            return False
        
        return True  # Default: resume after interruption
    
    def _detect_background_noise(self, audio_data: bytes) -> bool:
        """Detect if there's significant background noise (simulated)"""
        # In a real implementation, this would analyze audio for noise levels
        # For now, we'll simulate based on audio data length
        return len(audio_data) > 1000 and b"noise" in audio_data


class ConversationFlowManager:
    """Manages conversation flow with interruption handling"""
    
    def __init__(self):
        self.command_recognizer = VoiceCommandRecognizer()
        self.interruption_handler = InterruptionHandler()
        self.active_contexts: Dict[str, ConversationContext] = {}
        self.flow_enabled = True
    
    def start_conversation(self, session_id: str, initial_response: str = "") -> ConversationContext:
        """Start a new conversation session"""
        context = ConversationContext(
            session_id=session_id,
            current_state=ConversationState.IDLE,
            current_response=initial_response
        )
        
        self.active_contexts[session_id] = context
        logger.info(f"Started conversation session: {session_id}")
        
        return context
    
    def process_voice_input(self, 
                          session_id: str,
                          audio_data: bytes,
                          transcribed_text: str = "",
                          user_speech_detected: bool = False) -> Dict[str, Any]:
        """
        Process voice input and manage conversation flow
        
        Args:
            session_id: Session identifier
            audio_data: Audio data from microphone
            transcribed_text: Transcribed speech text
            user_speech_detected: Whether user speech was detected
            
        Returns:
            Dictionary with processing results and actions
        """
        if not self.flow_enabled or session_id not in self.active_contexts:
            return {"error": "Session not found or flow disabled"}
        
        context = self.active_contexts[session_id]
        result = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "state_change": None,
            "response": None,
            "interruption": None,
            "command": None
        }
        
        # Check for interruptions
        interruption = self.interruption_handler.detect_interruption(
            audio_data, context, user_speech_detected, transcribed_text
        )
        
        if interruption:
            result["interruption"] = self._handle_interruption(context, interruption)
            result["actions"].append("interruption_handled")
        
        # Check for voice commands
        if transcribed_text:
            command_result = self.command_recognizer.recognize_command(
                transcribed_text, "en", context
            )
            
            if command_result:
                command, confidence = command_result
                result["command"] = {
                    "command": command.value,
                    "confidence": confidence,
                    "text": transcribed_text
                }
                
                command_response = self._handle_command(context, command, transcribed_text)
                result["actions"].append("command_executed")
                result["response"] = command_response
        
        # Update conversation history
        if transcribed_text or interruption:
            context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": transcribed_text,
                "interruption": interruption.interruption_type.value if interruption else None,
                "state": context.current_state.value
            })
        
        result["current_state"] = context.current_state.value
        return result
    
    def start_ai_response(self, session_id: str, response_text: str) -> bool:
        """Start AI speaking response"""
        if session_id not in self.active_contexts:
            return False
        
        context = self.active_contexts[session_id]
        context.current_state = ConversationState.SPEAKING
        context.current_response = response_text
        context.response_position = 0.0
        context.response_start_time = datetime.now()
        
        logger.info(f"Started AI response for session {session_id}")
        return True
    
    def _handle_interruption(self, 
                           context: ConversationContext, 
                           interruption: InterruptionEvent) -> Dict[str, Any]:
        """Handle interruption event"""
        previous_state = context.current_state
        context.last_interruption = interruption
        context.interruption_count += 1
        
        if interruption.interruption_type == InterruptionType.USER_SPEECH:
            if context.current_state == ConversationState.SPEAKING:
                context.current_state = ConversationState.INTERRUPTED
                
                # Check if user speech contains a command
                if interruption.user_text:
                    command_result = self.command_recognizer.recognize_command(
                        interruption.user_text, "en", context
                    )
                    if command_result:
                        interruption.detected_command = command_result[0]
        
        elif interruption.interruption_type == InterruptionType.SILENCE_TIMEOUT:
            context.current_state = ConversationState.IDLE
        
        elif interruption.interruption_type == InterruptionType.BACKGROUND_NOISE:
            # Pause briefly for noise, then resume
            context.current_state = ConversationState.PAUSED
        
        return {
            "type": interruption.interruption_type.value,
            "previous_state": previous_state.value,
            "new_state": context.current_state.value,
            "should_resume": interruption.should_resume,
            "resume_position": interruption.resume_from_position,
            "detected_command": interruption.detected_command.value if interruption.detected_command else None
        }
    
    def _handle_command(self, 
                       context: ConversationContext, 
                       command: VoiceCommand,
                       original_text: str) -> str:
        """Handle recognized voice command"""
        logger.info(f"Handling command: {command.value} in session {context.session_id}")
        
        if command == VoiceCommand.PAUSE:
            if context.current_state == ConversationState.SPEAKING:
                context.current_state = ConversationState.PAUSED
                return "पॉज़ किया गया। Resume करने के लिए 'continue' कहें।"
            return "कुछ भी चल नहीं रहा pause करने के लिए।"
        
        elif command == VoiceCommand.RESUME:
            if context.current_state == ConversationState.PAUSED:
                context.current_state = ConversationState.SPEAKING
                return "जारी रखते हैं..."
            return "Resume करने के लिए कुछ भी paused नहीं है।"
        
        elif command == VoiceCommand.STOP:
            context.current_state = ConversationState.IDLE
            context.current_response = None
            return "रोक दिया गया। कुछ और पूछना चाहते हैं?"
        
        elif command == VoiceCommand.REPEAT:
            if context.current_response:
                context.response_position = 0.0
                context.response_start_time = datetime.now()
                return context.current_response
            return "दोहराने के लिए कुछ भी नहीं है।"
        
        elif command == VoiceCommand.EXPLAIN_MORE:
            return "मैं इस विषय के बारे में और विस्तार से बताता हूं..."
        
        elif command == VoiceCommand.SIMPLIFY:
            return "मैं इसे और सरल शब्दों में समझाता हूं..."
        
        elif command == VoiceCommand.GIVE_EXAMPLE:
            return "एक उदाहरण देता हूं..."
        
        elif command == VoiceCommand.SWITCH_TO_HINDI:
            context.voice_settings["language"] = "hi"
            return "अब मैं हिंदी में बात करूंगा।"
        
        elif command == VoiceCommand.SWITCH_TO_ENGLISH:
            context.voice_settings["language"] = "en"
            return "I will now speak in English."
        
        elif command == VoiceCommand.LOUDER:
            current_volume = context.voice_settings.get("volume", 1.0)
            context.voice_settings["volume"] = min(1.5, current_volume + 0.2)
            return "आवाज़ तेज़ कर दी।"
        
        elif command == VoiceCommand.QUIETER:
            current_volume = context.voice_settings.get("volume", 1.0)
            context.voice_settings["volume"] = max(0.5, current_volume - 0.2)
            return "आवाज़ धीमी कर दी।"
        
        elif command == VoiceCommand.FASTER:
            current_speed = context.voice_settings.get("speed", 1.0)
            context.voice_settings["speed"] = min(1.5, current_speed + 0.2)
            return "तेज़ी से बोल रहा हूं।"
        
        elif command == VoiceCommand.SLOWER:
            current_speed = context.voice_settings.get("speed", 1.0)
            context.voice_settings["speed"] = max(0.7, current_speed - 0.2)
            return "धीरे-धीरे बोल रहा हूं।"
        
        elif command == VoiceCommand.START_MEDITATION:
            context.current_state = ConversationState.SPEAKING
            return "ॐ... आइए ध्यान शुरू करते हैं। आंखें बंद करें और गहरी सांस लें..."
        
        elif command == VoiceCommand.PLAY_MANTRA:
            context.current_state = ConversationState.SPEAKING
            return "ॐ नमः शिवाय... ॐ नमः शिवाय... ॐ नमः शिवाय..."
        
        elif command == VoiceCommand.HELP:
            return ("आप ये commands कह सकते हैं: pause, resume, stop, repeat, explain more, "
                   "simplify, louder, quieter, faster, slower, Hindi में switch करें, "
                   "meditation start करें। और भी जानना चाहते हैं?")
        
        else:
            return f"'{command.value}' command को handle करने का तरीका अभी implement नहीं हुआ है।"
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a conversation session"""
        if session_id not in self.active_contexts:
            return None
        
        context = self.active_contexts[session_id]
        
        return {
            "session_id": session_id,
            "current_state": context.current_state.value,
            "interruption_count": context.interruption_count,
            "last_interruption": (
                context.last_interruption.interruption_type.value 
                if context.last_interruption else None
            ),
            "conversation_length": len(context.conversation_history),
            "voice_settings": context.voice_settings,
            "response_position": context.response_position,
            "is_speaking": context.current_state == ConversationState.SPEAKING
        }
    
    def end_conversation(self, session_id: str) -> bool:
        """End a conversation session"""
        if session_id in self.active_contexts:
            del self.active_contexts[session_id]
            logger.info(f"Ended conversation session: {session_id}")
            return True
        return False


class AdvancedVoiceFeatures:
    """Main class for advanced voice features"""
    
    def __init__(self):
        self.flow_manager = ConversationFlowManager()
        self.features_enabled = True
        self.active_sessions: Dict[str, datetime] = {}
    
    def initialize_session(self, session_id: str) -> Dict[str, Any]:
        """Initialize a new voice session with advanced features"""
        if not self.features_enabled:
            return {"error": "Advanced voice features are disabled"}
        
        context = self.flow_manager.start_conversation(session_id)
        self.active_sessions[session_id] = datetime.now()
        
        return {
            "session_id": session_id,
            "status": "initialized",
            "features": {
                "interruption_handling": True,
                "voice_commands": True,
                "conversation_flow": True
            },
            "available_commands": [cmd.value for cmd in VoiceCommand],
            "context": {
                "state": context.current_state.value,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def process_voice_interaction(self, 
                                session_id: str,
                                audio_data: bytes,
                                transcribed_text: str = "",
                                user_speech_detected: bool = False) -> Dict[str, Any]:
        """Process voice interaction with advanced features"""
        if not self.features_enabled:
            return {"error": "Advanced voice features are disabled"}
        
        if session_id not in self.active_sessions:
            return {"error": "Session not initialized"}
        
        # Update session timestamp
        self.active_sessions[session_id] = datetime.now()
        
        # Process with flow manager
        result = self.flow_manager.process_voice_input(
            session_id, audio_data, transcribed_text, user_speech_detected
        )
        
        # Add session info
        result["session_info"] = self.flow_manager.get_session_status(session_id)
        
        return result
    
    def start_ai_speaking(self, session_id: str, response_text: str) -> Dict[str, Any]:
        """Start AI speaking with interruption handling"""
        if session_id not in self.active_sessions:
            return {"error": "Session not initialized"}
        
        success = self.flow_manager.start_ai_response(session_id, response_text)
        
        return {
            "session_id": session_id,
            "started": success,
            "response_text": response_text,
            "timestamp": datetime.now().isoformat(),
            "interruption_handling": "enabled"
        }
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        status = self.flow_manager.get_session_status(session_id)
        if not status:
            return {"error": "Session not found"}
        
        context = self.flow_manager.active_contexts[session_id]
        
        return {
            "session_id": session_id,
            "session_duration": (
                datetime.now() - self.active_sessions[session_id]
            ).total_seconds(),
            "current_state": status["current_state"],
            "total_interactions": len(context.conversation_history),
            "interruption_count": status["interruption_count"],
            "commands_executed": sum(
                1 for entry in context.conversation_history 
                if "command" in str(entry)
            ),
            "voice_settings": status["voice_settings"],
            "performance_metrics": {
                "avg_response_time": 1.2,  # Simulated
                "interruption_recovery_rate": 0.95 if status["interruption_count"] > 0 else 1.0
            }
        }
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = 30) -> int:
        """Clean up inactive sessions"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        inactive_sessions = [
            sid for sid, last_activity in self.active_sessions.items()
            if last_activity < cutoff_time
        ]
        
        for session_id in inactive_sessions:
            self.flow_manager.end_conversation(session_id)
            del self.active_sessions[session_id]
        
        logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")
        return len(inactive_sessions)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "features_enabled": self.features_enabled,
            "active_sessions": len(self.active_sessions),
            "total_commands": len(VoiceCommand),
            "interruption_types": len(InterruptionType),
            "conversation_states": len(ConversationState),
            "uptime": "operational",
            "capabilities": {
                "real_time_interruption": True,
                "voice_command_recognition": True,
                "multilingual_commands": True,
                "conversation_context": True,
                "adaptive_responses": True
            }
        }
