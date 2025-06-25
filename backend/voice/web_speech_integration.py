"""
Web Speech API Integration for Vimarsh AI Agent

This module provides seamless integration with the Web Speech API for
browser-based speech recognition, optimized for spiritual guidance applications.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum

from .speech_processor import VoiceConfig, RecognitionResult, VoiceLanguage, RecognitionStatus


class SpeechRecognitionError(Exception):
    """Custom exception for speech recognition errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class WebSpeechEvent(Enum):
    """Web Speech API event types"""
    START = "start"
    END = "end"
    RESULT = "result"
    ERROR = "error"
    NO_MATCH = "nomatch"
    AUDIO_START = "audiostart"
    AUDIO_END = "audioend"
    SOUND_START = "soundstart"
    SOUND_END = "soundend"
    SPEECH_START = "speechstart"
    SPEECH_END = "speechend"


@dataclass
class WebSpeechConfig:
    """Configuration for Web Speech API integration"""
    
    # Basic recognition settings
    continuous: bool = True
    interim_results: bool = True
    max_alternatives: int = 3
    service_uri: Optional[str] = None
    
    # Language and grammar
    lang: str = "en-US"
    grammars: List[str] = None
    
    # Spiritual content optimization
    spiritual_grammar_enabled: bool = True
    sanskrit_pronunciation_guide: bool = True
    deity_name_variants: bool = True
    
    # Error handling
    auto_restart: bool = True
    max_restart_attempts: int = 3
    restart_delay_seconds: float = 1.0


class WebSpeechIntegration:
    """
    Web Speech API integration with spiritual content optimization
    """
    
    def __init__(self, config: Optional[WebSpeechConfig] = None):
        """Initialize Web Speech API integration"""
        self.config = config or WebSpeechConfig()
        self.logger = logging.getLogger(__name__)
        
        # Integration state
        self.is_initialized = False
        self.is_listening = False
        self.current_recognition = None
        self.restart_attempts = 0
        
        # Event handlers
        self.event_handlers: Dict[WebSpeechEvent, List[Callable]] = {
            event: [] for event in WebSpeechEvent
        }
        
        # Recognition results
        self.current_result: Optional[RecognitionResult] = None
        self.result_history: List[RecognitionResult] = []
        
        # Spiritual content enhancement
        self.spiritual_grammar = self._create_spiritual_grammar()
        self.pronunciation_guide = self._create_pronunciation_guide()
    
    def _create_spiritual_grammar(self) -> Dict[str, List[str]]:
        """Create grammar rules for spiritual content recognition"""
        return {
            # Sanskrit terms with common mispronunciations
            'dharma': ['dharma', 'dhamma', 'darma', 'dharama'],
            'karma': ['karma', 'karm', 'karam', 'karama'],
            'yoga': ['yoga', 'yog', 'yoge'],
            'bhakti': ['bhakti', 'bhakthi', 'bakti', 'bhakathi'],
            'moksha': ['moksha', 'moksh', 'moksa', 'mokshya'],
            'samadhi': ['samadhi', 'samadh', 'samadi'],
            'pranayama': ['pranayama', 'pranayam', 'pranyama'],
            
            # Deity names with variations
            'krishna': [
                'krishna', 'krsna', 'krish', 'krishn', 'krishnaa',
                'govinda', 'gopal', 'gopala', 'madhava', 'vasudeva'
            ],
            'rama': ['rama', 'ram', 'raghava', 'raghuram', 'sita-rama'],
            'shiva': [
                'shiva', 'shiv', 'shankar', 'shankara', 'mahadev',
                'nataraja', 'rudra', 'bholenath'
            ],
            'vishnu': [
                'vishnu', 'visnu', 'narayana', 'hari', 'vasudeva'
            ],
            
            # Scripture names
            'bhagavad_gita': [
                'bhagavad gita', 'gita', 'geeta', 'bhagavat gita',
                'bhagwad gita', 'bhagwat geeta'
            ],
            'mahabharata': [
                'mahabharata', 'mahabharat', 'maha bharata', 'mahabharatam'
            ],
            'ramayana': [
                'ramayana', 'ramayan', 'ramayanam'
            ],
            
            # Mantras and sacred phrases
            'om': ['om', 'aum', 'ohm'],
            'namaste': ['namaste', 'namasthe', 'namaskar'],
            'hari_om': ['hari om', 'hari aum', 'hariom'],
            'om_namah_shivaya': [
                'om namah shivaya', 'om nama shivaya', 'om namaha shivaya'
            ]
        }
    
    def _create_pronunciation_guide(self) -> Dict[str, str]:
        """Create pronunciation guide for spiritual terms"""
        return {
            'dharma': 'DHAR-ma',
            'karma': 'KAR-ma', 
            'yoga': 'YO-ga',
            'bhakti': 'BHAK-ti',
            'moksha': 'MOKE-sha',
            'samadhi': 'sa-MA-dhee',
            'pranayama': 'pra-na-YA-ma',
            'krishna': 'KRISH-na',
            'rama': 'RA-ma',
            'shiva': 'SHEE-va',
            'vishnu': 'VISH-nu',
            'ganesha': 'ga-NE-sha',
            'hanuman': 'HA-nu-man',
            'namaste': 'na-mas-TE',
            'guru': 'GU-ru',
            'ashram': 'ASH-ram',
            'mantra': 'MAN-tra',
            'mudra': 'MU-dra',
            'chakra': 'CHAK-ra'
        }
    
    async def initialize(self) -> bool:
        """
        Initialize Web Speech API integration
        
        Returns:
            True if initialization successful
        """
        try:
            # In a real implementation, this would:
            # 1. Check for Web Speech API support
            # 2. Initialize SpeechRecognition object
            # 3. Set up event listeners
            # 4. Configure spiritual grammar rules
            
            self.logger.info("Initializing Web Speech API integration")
            
            # Simulate initialization
            await asyncio.sleep(0.1)
            
            # Set up spiritual grammar if enabled
            if self.config.spiritual_grammar_enabled:
                await self._setup_spiritual_grammar()
            
            self.is_initialized = True
            self.logger.info("Web Speech API integration initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Web Speech API: {e}")
            raise SpeechRecognitionError(
                "Failed to initialize Web Speech API",
                error_code="INIT_FAILED",
                details={'error': str(e)}
            )
    
    async def _setup_spiritual_grammar(self):
        """Set up spiritual grammar rules for enhanced recognition"""
        
        # In a real implementation, this would create SpeechGrammarList
        # and add grammar rules for spiritual content
        
        grammar_rules = []
        
        for term, variations in self.spiritual_grammar.items():
            # Create grammar rule for each spiritual term
            rule = f"#{term} = {' | '.join(variations)};"
            grammar_rules.append(rule)
        
        self.logger.info(f"Set up {len(grammar_rules)} spiritual grammar rules")
    
    def add_event_handler(self, event: WebSpeechEvent, handler: Callable):
        """Add event handler for Web Speech API events"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        
        self.event_handlers[event].append(handler)
        self.logger.debug(f"Added event handler for {event.value}")
    
    def remove_event_handler(self, event: WebSpeechEvent, handler: Callable):
        """Remove event handler"""
        if event in self.event_handlers and handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
            self.logger.debug(f"Removed event handler for {event.value}")
    
    async def _trigger_event(self, event: WebSpeechEvent, data: Any = None):
        """Trigger event handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event, data)
                    else:
                        handler(event, data)
                except Exception as e:
                    self.logger.error(f"Event handler error for {event.value}: {e}")
    
    async def start_recognition(self) -> bool:
        """
        Start speech recognition
        
        Returns:
            True if recognition started successfully
        """
        if not self.is_initialized:
            raise SpeechRecognitionError(
                "Web Speech API not initialized",
                error_code="NOT_INITIALIZED"
            )
        
        if self.is_listening:
            self.logger.warning("Speech recognition already in progress")
            return True
        
        try:
            self.logger.info("Starting Web Speech API recognition")
            
            # Reset state
            self.current_result = None
            self.restart_attempts = 0
            
            # In real implementation, would call recognition.start()
            self.is_listening = True
            
            # Trigger start event
            await self._trigger_event(WebSpeechEvent.START)
            
            # Simulate recognition process
            asyncio.create_task(self._simulate_recognition_process())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recognition: {e}")
            await self._trigger_event(WebSpeechEvent.ERROR, {
                'error': str(e),
                'error_code': 'START_FAILED'
            })
            return False
    
    async def stop_recognition(self) -> Optional[RecognitionResult]:
        """
        Stop speech recognition
        
        Returns:
            Final recognition result
        """
        if not self.is_listening:
            return self.current_result
        
        self.logger.info("Stopping Web Speech API recognition")
        
        # In real implementation, would call recognition.stop()
        self.is_listening = False
        
        # Trigger end event
        await self._trigger_event(WebSpeechEvent.END)
        
        return self.current_result
    
    async def _simulate_recognition_process(self):
        """Simulate the recognition process for development"""
        
        try:
            # Simulate audio start
            await asyncio.sleep(0.1)
            await self._trigger_event(WebSpeechEvent.AUDIO_START)
            
            # Simulate speech detection
            await asyncio.sleep(0.5)
            await self._trigger_event(WebSpeechEvent.SPEECH_START)
            
            # Simulate recognition results
            await asyncio.sleep(1.0)
            
            # Create simulated result
            result = await self._create_simulated_result()
            self.current_result = result
            self.result_history.append(result)
            
            # Trigger result event
            await self._trigger_event(WebSpeechEvent.RESULT, result)
            
            # Simulate speech end
            await asyncio.sleep(0.2)
            await self._trigger_event(WebSpeechEvent.SPEECH_END)
            
            # Simulate audio end
            await asyncio.sleep(0.1)
            await self._trigger_event(WebSpeechEvent.AUDIO_END)
            
        except Exception as e:
            self.logger.error(f"Recognition simulation error: {e}")
            await self._trigger_event(WebSpeechEvent.ERROR, {
                'error': str(e),
                'error_code': 'SIMULATION_ERROR'
            })
    
    async def _create_simulated_result(self) -> RecognitionResult:
        """Create simulated recognition result for testing"""
        
        import random
        
        spiritual_queries = [
            "Please explain the concept of dharma in the Bhagavad Gita",
            "How can I develop devotion to Krishna?",
            "What is the meaning of Om Namah Shivaya?",
            "Tell me about karma yoga and selfless action",
            "How do I practice meditation according to the scriptures?",
            "What is the path to moksha or liberation?",
            "Explain the nature of the eternal soul",
            "How can I overcome suffering through spiritual practice?",
            "What does surrender to God mean in bhakti yoga?",
            "Please guide me on the spiritual path"
        ]
        
        transcript = random.choice(spiritual_queries)
        confidence = random.uniform(0.8, 0.95)
        
        # Create result with spiritual content analysis
        result = RecognitionResult(
            transcript=transcript,
            confidence=confidence,
            language=VoiceLanguage.ENGLISH,
            status=RecognitionStatus.COMPLETED,
            timestamp=datetime.now()
        )
        
        # Enhance with spiritual content detection
        await self._enhance_with_spiritual_content(result)
        
        return result
    
    async def _enhance_with_spiritual_content(self, result: RecognitionResult):
        """Enhance result with spiritual content analysis"""
        
        transcript_lower = result.transcript.lower()
        
        # Check for spiritual grammar matches
        for term, variations in self.spiritual_grammar.items():
            for variation in variations:
                if variation in transcript_lower:
                    if term not in result.spiritual_terms:
                        result.spiritual_terms.append(term)
                    
                    # Check if it's a Sanskrit term
                    if any(sanskrit in variation for sanskrit in ['dharma', 'karma', 'yoga', 'moksha']):
                        result.contains_sanskrit = True
                    
                    # Check if it's a deity reference
                    if term in ['krishna', 'rama', 'shiva', 'vishnu']:
                        if term not in result.deity_references:
                            result.deity_references.append(term)
                    
                    # Check for mantras
                    if term in ['om', 'om_namah_shivaya', 'hari_om']:
                        if variation not in result.detected_mantras:
                            result.detected_mantras.append(variation)
        
        # Boost confidence for spiritual content
        if result.spiritual_terms or result.deity_references:
            boost = min(0.05, len(result.spiritual_terms) * 0.01)
            result.confidence = min(1.0, result.confidence + boost)
    
    async def restart_recognition(self) -> bool:
        """
        Restart recognition after error
        
        Returns:
            True if restart successful
        """
        if self.restart_attempts >= self.config.max_restart_attempts:
            self.logger.error("Maximum restart attempts reached")
            return False
        
        self.restart_attempts += 1
        self.logger.info(f"Restarting recognition (attempt {self.restart_attempts})")
        
        # Stop current recognition
        await self.stop_recognition()
        
        # Wait before restart
        await asyncio.sleep(self.config.restart_delay_seconds)
        
        # Start new recognition
        return await self.start_recognition()
    
    def get_pronunciation_guide(self, term: str) -> Optional[str]:
        """Get pronunciation guide for spiritual term"""
        return self.pronunciation_guide.get(term.lower())
    
    def get_term_variations(self, term: str) -> List[str]:
        """Get recognized variations for spiritual term"""
        return self.spiritual_grammar.get(term.lower(), [])
    
    def get_result_history(self, limit: int = 10) -> List[RecognitionResult]:
        """Get recent recognition results"""
        return self.result_history[-limit:] if limit else self.result_history.copy()
    
    def clear_history(self):
        """Clear recognition history"""
        self.result_history.clear()
        self.logger.info("Recognition history cleared")
    
    async def update_spiritual_vocabulary(self, new_terms: Dict[str, List[str]]):
        """Update spiritual vocabulary with new terms"""
        
        self.spiritual_grammar.update(new_terms)
        
        # Re-setup grammar if recognition is active
        if self.is_initialized and self.config.spiritual_grammar_enabled:
            await self._setup_spiritual_grammar()
        
        self.logger.info(f"Updated spiritual vocabulary with {len(new_terms)} new terms")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and statistics"""
        
        total_results = len(self.result_history)
        spiritual_results = sum(
            1 for r in self.result_history 
            if r.spiritual_terms or r.deity_references
        )
        
        return {
            'initialized': self.is_initialized,
            'listening': self.is_listening,
            'total_results': total_results,
            'spiritual_results': spiritual_results,
            'spiritual_ratio': spiritual_results / total_results if total_results > 0 else 0.0,
            'restart_attempts': self.restart_attempts,
            'current_config': {
                'language': self.config.lang,
                'continuous': self.config.continuous,
                'interim_results': self.config.interim_results,
                'spiritual_grammar_enabled': self.config.spiritual_grammar_enabled
            }
        }


# Convenience functions
async def create_web_speech_integration(
    language: str = "en-US",
    spiritual_optimization: bool = True
) -> WebSpeechIntegration:
    """
    Create and initialize Web Speech API integration
    
    Args:
        language: Target language code
        spiritual_optimization: Enable spiritual content optimization
        
    Returns:
        Initialized WebSpeechIntegration instance
    """
    
    config = WebSpeechConfig(
        lang=language,
        spiritual_grammar_enabled=spiritual_optimization,
        sanskrit_pronunciation_guide=spiritual_optimization,
        deity_name_variants=spiritual_optimization
    )
    
    integration = WebSpeechIntegration(config)
    await integration.initialize()
    
    return integration


def get_supported_languages() -> Dict[str, str]:
    """Get supported languages for spiritual guidance"""
    return {
        'en-US': 'English (United States)',
        'en-GB': 'English (United Kingdom)', 
        'hi-IN': 'Hindi (India)',
        'sa-IN': 'Sanskrit (India)',
        'en-IN': 'English (India)',
        'en-AU': 'English (Australia)',
        'en-CA': 'English (Canada)'
    }
