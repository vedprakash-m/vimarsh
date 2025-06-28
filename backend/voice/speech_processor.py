"""
Speech Processing Components for Vimarsh AI Agent

This module implements core speech processing functionality with Web Speech API
integration, optimized for spiritual guidance and Sanskrit terminology.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
import re

try:
    import numpy as np
except ImportError:
    np = None


class VoiceLanguage(Enum):
    """Supported voice interface languages"""
    ENGLISH = "en-US"
    HINDI = "hi-IN"
    SANSKRIT = "sa-IN"  # Sanskrit with Devanagari script


class SpeechQuality(Enum):
    """Speech recognition quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"


class RecognitionStatus(Enum):
    """Speech recognition status"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class VoiceConfig:
    """Configuration for voice processing"""
    language: VoiceLanguage = VoiceLanguage.ENGLISH
    quality: SpeechQuality = SpeechQuality.HIGH
    continuous: bool = True
    interim_results: bool = True
    max_alternatives: int = 3
    noise_suppression: bool = True
    echo_cancellation: bool = True
    auto_gain_control: bool = True
    
    # Spiritual content specific settings
    sanskrit_support: bool = True
    spiritual_vocabulary_boost: bool = True
    deity_name_recognition: bool = True
    mantra_detection: bool = True
    
    # Performance settings
    timeout_seconds: float = 30.0
    silence_timeout: float = 3.0
    phrase_timeout: float = 1.0
    confidence_threshold: float = 0.7


@dataclass
class RecognitionResult:
    """Result from speech recognition"""
    transcript: str
    confidence: float
    language: VoiceLanguage
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    
    # Spiritual content analysis
    contains_sanskrit: bool = False
    detected_mantras: List[str] = field(default_factory=list)
    deity_references: List[str] = field(default_factory=list)
    spiritual_terms: List[str] = field(default_factory=list)
    
    # Technical metadata
    duration_ms: int = 0
    processing_time_ms: int = 0
    status: RecognitionStatus = RecognitionStatus.COMPLETED
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class SpeechProcessor:
    """
    Core speech processing component with spiritual content optimization
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        """Initialize speech processor with configuration"""
        self.config = config or VoiceConfig()
        self.logger = logging.getLogger(__name__)
        
        # Recognition state
        self.is_listening = False
        self.current_session_id = None
        self.recognition_history: List[RecognitionResult] = []
        
        # Spiritual vocabulary enhancement
        self.sanskrit_terms = self._load_sanskrit_vocabulary()
        self.deity_names = self._load_deity_names()
        self.mantras = self._load_common_mantras()
        self.spiritual_vocabulary = self._load_spiritual_vocabulary()
        
        # Performance tracking
        self.recognition_stats = {
            'total_requests': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0
        }
    
    def _load_sanskrit_vocabulary(self) -> Dict[str, str]:
        """Load Sanskrit terms with phonetic mappings"""
        return {
            # Common spiritual terms
            'dharma': ['dharma', 'dhamma', 'darma'],
            'karma': ['karma', 'karm', 'karam'],
            'moksha': ['moksha', 'moksh', 'moksa'],
            'yoga': ['yoga', 'yog'],
            'bhakti': ['bhakti', 'bhakthi', 'bakti'],
            'jnana': ['jnana', 'gyana', 'gnana'],
            'sadhana': ['sadhana', 'sadana'],
            'samadhi': ['samadhi', 'samadh'],
            'pranayama': ['pranayama', 'pranayam'],
            'asana': ['asana', 'asan'],
            
            # Philosophical concepts
            'atman': ['atman', 'aatman', 'atma'],
            'brahman': ['brahman', 'brahmana', 'brahma'],
            'samsara': ['samsara', 'sansar'],
            'nirvana': ['nirvana', 'nirvan'],
            'ahimsa': ['ahimsa', 'ahinsa'],
            'tapas': ['tapas', 'tapa'],
            'seva': ['seva', 'sewa'],
            'guru': ['guru', 'gur'],
            'ashram': ['ashram', 'aashram', 'asram'],
            'satsang': ['satsang', 'satsanga']
        }
    
    def _load_deity_names(self) -> Dict[str, List[str]]:
        """Load deity names with variations"""
        return {
            'krishna': ['krishna', 'krsna', 'krish', 'krishn', 'govinda', 'gopal'],
            'rama': ['rama', 'ram', 'raghava', 'sita-rama'],
            'shiva': ['shiva', 'shiv', 'shankar', 'mahadev'],
            'vishnu': ['vishnu', 'visnu', 'narayana'],
            'brahma': ['brahma', 'brahmaji'],
            'hanuman': ['hanuman', 'bajrangbali', 'maruti'],
            'ganesha': ['ganesha', 'ganesh', 'vinayaka', 'ganapati'],
            'durga': ['durga', 'devi', 'mata'],
            'lakshmi': ['lakshmi', 'laxmi', 'shri'],
            'saraswati': ['saraswati', 'sarasvati', 'vidya-devi']
        }
    
    def _load_common_mantras(self) -> List[str]:
        """Load common mantras for detection"""
        return [
            'om',
            'aum',
            'om namah shivaya',
            'hare krishna',
            'om mani padme hum',
            'gayatri mantra',
            'mahamrityunjaya',
            'om gam ganapataye namaha',
            'om shanti shanti shanti',
            'so hum',
            'tat tvam asi',
            'aham brahmasmi'
        ]
    
    def _load_spiritual_vocabulary(self) -> Dict[str, float]:
        """Load spiritual vocabulary with importance weights"""
        return {
            # Scripture names
            'bhagavad gita': 1.0,
            'gita': 0.9,
            'mahabharata': 1.0,
            'ramayana': 1.0,
            'upanishads': 1.0,
            'vedas': 1.0,
            'puranas': 0.9,
            'srimad bhagavatam': 1.0,
            'bhagavatam': 0.9,
            
            # Spiritual concepts
            'enlightenment': 0.8,
            'meditation': 0.9,
            'devotion': 0.8,
            'surrender': 0.8,
            'liberation': 0.8,
            'consciousness': 0.8,
            'spiritual': 0.7,
            'divine': 0.8,
            'sacred': 0.8,
            'holy': 0.7,
            'blessing': 0.7,
            'grace': 0.8,
            'wisdom': 0.8,
            'truth': 0.8,
            'peace': 0.7,
            'love': 0.7,
            'compassion': 0.8,
            'service': 0.7
        }
    
    async def start_recognition(self, session_id: str = None) -> str:
        """
        Start speech recognition session
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            Session ID for tracking
        """
        if self.is_listening:
            raise RuntimeError("Speech recognition already in progress")
        
        self.current_session_id = session_id or f"session_{int(time.time())}"
        self.is_listening = True
        
        self.logger.info(f"Started speech recognition session: {self.current_session_id}")
        
        return self.current_session_id
    
    async def stop_recognition(self) -> Optional[RecognitionResult]:
        """
        Stop current speech recognition session
        
        Returns:
            Final recognition result if available
        """
        if not self.is_listening:
            return None
        
        self.is_listening = False
        session_id = self.current_session_id
        self.current_session_id = None
        
        self.logger.info(f"Stopped speech recognition session: {session_id}")
        
        # Return the last result from this session
        for result in reversed(self.recognition_history):
            if hasattr(result, 'session_id') and result.session_id == session_id:
                return result
        
        return None
    
    async def process_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> RecognitionResult:
        """
        Process raw audio data for speech recognition
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            
        Returns:
            Recognition result
        """
        start_time = time.time()
        
        try:
            # Simulate speech recognition processing
            # In real implementation, this would interface with Web Speech API
            # or other speech recognition services
            
            # Basic audio analysis (if numpy available)
            if np is not None:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_duration = len(audio_array) / sample_rate * 1000  # ms
            else:
                audio_duration = len(audio_data) / (sample_rate * 2) * 1000  # estimate
            
            # Simulate recognition result
            # In production, this would come from actual speech recognition
            result = await self._simulate_recognition(audio_duration)
            
            # Post-process for spiritual content
            await self._enhance_spiritual_recognition(result)
            
            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = int(processing_time)
            
            self._update_recognition_stats(result, processing_time)
            
            # Store in history
            self.recognition_history.append(result)
            
            # Keep history manageable
            if len(self.recognition_history) > 100:
                self.recognition_history = self.recognition_history[-50:]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            
            processing_time = (time.time() - start_time) * 1000
            
            error_result = RecognitionResult(
                transcript="",
                confidence=0.0,
                language=self.config.language,
                status=RecognitionStatus.ERROR,
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )
            
            self._update_recognition_stats(error_result, processing_time)
            return error_result
    
    async def _simulate_recognition(self, duration_ms: float) -> RecognitionResult:
        """Simulate speech recognition for development/testing"""
        
        # Sample spiritual queries for simulation
        spiritual_queries = [
            "What is the meaning of dharma in the Bhagavad Gita?",
            "How can I develop devotion to Krishna?",
            "What does the Gita say about karma yoga?",
            "Please explain the concept of moksha.",
            "How should I practice meditation according to the scriptures?",
            "What is the path to spiritual enlightenment?",
            "Tell me about the soul's eternal nature.",
            "How can I overcome suffering through spiritual practice?",
            "What is the importance of surrender to God?",
            "Explain the difference between action and inaction."
        ]
        
        import random
        transcript = random.choice(spiritual_queries)
        confidence = random.uniform(0.75, 0.95)
        
        # Generate alternatives
        alternatives = [
            (transcript, confidence),
            (transcript.replace("Krishna", "Lord Krishna"), confidence - 0.1),
            (transcript.replace("Gita", "Bhagavad Gita"), confidence - 0.05)
        ]
        
        return RecognitionResult(
            transcript=transcript,
            confidence=confidence,
            language=self.config.language,
            alternatives=alternatives[:self.config.max_alternatives],
            duration_ms=int(duration_ms),
            status=RecognitionStatus.COMPLETED
        )
    
    async def _enhance_spiritual_recognition(self, result: RecognitionResult):
        """Enhance recognition result with spiritual content analysis"""
        
        transcript_lower = result.transcript.lower()
        
        # Detect Sanskrit terms
        for sanskrit_term, variations in self.sanskrit_terms.items():
            for variation in variations:
                if variation in transcript_lower:
                    result.contains_sanskrit = True
                    if sanskrit_term not in result.spiritual_terms:
                        result.spiritual_terms.append(sanskrit_term)
                    break
        
        # Detect deity references
        for deity, variations in self.deity_names.items():
            for variation in variations:
                if variation in transcript_lower:
                    if deity not in result.deity_references:
                        result.deity_references.append(deity)
        
        # Detect mantras
        for mantra in self.mantras:
            if mantra in transcript_lower:
                if mantra not in result.detected_mantras:
                    result.detected_mantras.append(mantra)
        
        # Detect spiritual vocabulary
        for term, weight in self.spiritual_vocabulary.items():
            if term in transcript_lower:
                if term not in result.spiritual_terms:
                    result.spiritual_terms.append(term)
        
        # Boost confidence for spiritual content
        if result.spiritual_terms or result.deity_references or result.detected_mantras:
            spiritual_boost = min(0.1, len(result.spiritual_terms) * 0.02)
            result.confidence = min(1.0, result.confidence + spiritual_boost)
    
    def _update_recognition_stats(self, result: RecognitionResult, processing_time: float):
        """Update recognition statistics"""
        self.recognition_stats['total_requests'] += 1
        
        if result.status == RecognitionStatus.COMPLETED and result.confidence >= self.config.confidence_threshold:
            self.recognition_stats['successful_recognitions'] += 1
        else:
            self.recognition_stats['failed_recognitions'] += 1
        
        # Update averages
        total = self.recognition_stats['total_requests']
        
        # Running average for confidence
        old_avg_conf = self.recognition_stats['average_confidence']
        self.recognition_stats['average_confidence'] = (
            (old_avg_conf * (total - 1) + result.confidence) / total
        )
        
        # Running average for processing time
        old_avg_time = self.recognition_stats['average_processing_time']
        self.recognition_stats['average_processing_time'] = (
            (old_avg_time * (total - 1) + processing_time) / total
        )
    
    def _update_recognition_stats(self, confidence: float, processing_time: float):
        """Update recognition statistics."""
        total = self.recognition_stats['successful_recognitions']
        if total > 0:
            current_avg_conf = self.recognition_stats['average_confidence']
            current_avg_time = self.recognition_stats['average_processing_time']
            
            # Update running averages
            self.recognition_stats['average_confidence'] = (
                (current_avg_conf * (total - 1) + confidence) / total
            )
            self.recognition_stats['average_processing_time'] = (
                (current_avg_time * (total - 1) + processing_time) / total
            )
        else:
            self.recognition_stats['average_confidence'] = confidence
            self.recognition_stats['average_processing_time'] = processing_time
    
    def get_recognition_history(self, limit: int = 10) -> List[RecognitionResult]:
        """Get recent recognition history"""
        return self.recognition_history[-limit:] if limit else self.recognition_history.copy()
    
    def get_recognition_stats(self) -> Dict[str, Any]:
        """Get recognition performance statistics"""
        stats = self.recognition_stats.copy()
        
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_recognitions'] / stats['total_requests']
            stats['failure_rate'] = stats['failed_recognitions'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        return stats
    
    def update_config(self, new_config: VoiceConfig):
        """Update voice processing configuration"""
        self.config = new_config
        self.logger.info("Voice processing configuration updated")
    
    def reset_stats(self):
        """Reset recognition statistics"""
        self.recognition_stats = {
            'total_requests': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0
        }
        self.logger.info("Recognition statistics reset")
    
    async def optimize_for_spiritual_content(self) -> Dict[str, Any]:
        """
        Optimize speech recognition for spiritual content
        
        Returns:
            Optimization results and recommendations
        """
        
        # Analyze recent recognition history for spiritual content
        recent_results = self.get_recognition_history(50)
        
        spiritual_ratio = 0.0
        sanskrit_ratio = 0.0
        average_confidence = 0.0
        
        if recent_results:
            spiritual_count = sum(1 for r in recent_results if r.spiritual_terms or r.deity_references)
            sanskrit_count = sum(1 for r in recent_results if r.contains_sanskrit)
            total_confidence = sum(r.confidence for r in recent_results)
            
            spiritual_ratio = spiritual_count / len(recent_results)
            sanskrit_ratio = sanskrit_count / len(recent_results)
            average_confidence = total_confidence / len(recent_results)
        
        optimization_result = {
            'spiritual_content_ratio': spiritual_ratio,
            'sanskrit_content_ratio': sanskrit_ratio,
            'average_confidence': average_confidence,
            'recommendations': []
        }
        
        # Generate optimization recommendations
        if spiritual_ratio > 0.7:
            optimization_result['recommendations'].append(
                "High spiritual content detected. Consider enabling spiritual vocabulary boost."
            )
            if not self.config.spiritual_vocabulary_boost:
                self.config.spiritual_vocabulary_boost = True
        
        if sanskrit_ratio > 0.3:
            optimization_result['recommendations'].append(
                "Significant Sanskrit usage detected. Consider enabling Sanskrit support."
            )
            if not self.config.sanskrit_support:
                self.config.sanskrit_support = True
        
        if average_confidence < 0.75:
            optimization_result['recommendations'].append(
                "Low average confidence. Consider adjusting noise suppression and quality settings."
            )
        
        return optimization_result

    async def speech_to_text(self, audio_data: Any, language: str = "en-US") -> Dict[str, Any]:
        """
        Convert speech to text using specified language.
        
        Args:
            audio_data: Audio data (mock for Web Speech API)
            language: Language code (e.g., "en-US", "hi-IN")
            
        Returns:
            Recognition result with text and confidence
        """
        start_time = time.time()
        
        try:
            # Mock implementation for testing - in production this would interface with Web Speech API
            self.recognition_stats['total_requests'] += 1
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            # Mock successful recognition
            mock_text = "Hello, this is a test recognition"
            if language == "hi-IN":
                mock_text = "नमस्ते, यह एक परीक्षण पहचान है"
            elif language == "sa-IN":
                mock_text = "नमस्ते, अयं परीक्षा पहचानं अस्ति"
            
            confidence = 0.85
            processing_time = time.time() - start_time
            
            result = {
                'text': mock_text,
                'confidence': confidence,
                'language': language,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'session_id': self.current_session_id
            }
            
            self.recognition_stats['successful_recognitions'] += 1
            self._update_recognition_stats(confidence, processing_time)
            
            self.logger.info(f"Speech recognition successful: {confidence:.2f} confidence")
            return result
            
        except Exception as e:
            self.recognition_stats['failed_recognitions'] += 1
            self.logger.error(f"Speech recognition failed: {e}")
            raise
    
    def detect_voice_activity(self, audio_data: Any) -> Dict[str, Any]:
        """
        Detect voice activity in audio data.
        
        Args:
            audio_data: Audio data to analyze
            
        Returns:
            Voice activity detection result
        """
        # Mock implementation for testing
        return {
            'voice_detected': True,
            'voice_probability': 0.8,
            'speech_segments': [
                {'start': 0.5, 'end': 2.3, 'confidence': 0.85},
                {'start': 3.1, 'end': 5.2, 'confidence': 0.92}
            ],
            'background_noise_level': 0.15
        }
    
    def assess_audio_quality(self, audio_data: Any) -> Dict[str, Any]:
        """
        Assess audio quality for speech recognition.
        
        Args:
            audio_data: Audio data to assess
            
        Returns:
            Audio quality assessment
        """
        # Mock implementation for testing
        return {
            'quality_score': 0.85,
            'quality_level': 'good',
            'sample_rate': 16000,
            'bit_depth': 16,
            'channels': 1,
            'duration': 3.5,
            'noise_level': 0.1,
            'clipping_detected': False,
            'recommendations': []
        }
    
    def safe_speech_to_text(self, audio_data: Any) -> Optional[Dict[str, Any]]:
        """
        Safe wrapper for speech to text that handles errors gracefully.
        
        Args:
            audio_data: Audio data to process
            
        Returns:
            Recognition result or None if failed
        """
        try:
            # Run the async method synchronously for testing
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.speech_to_text(audio_data))
                return result
            finally:
                loop.close()
        except Exception as e:
            self.logger.error(f"Safe speech to text failed: {e}")
            return None
    
    def process_voice_input(self, audio_data: bytes, language: str = "en-US") -> Dict[str, Any]:
        """Process voice input and return recognition results."""
        start_time = time.time()
        
        try:
            # Mock voice processing
            mock_results = {
                'transcript': 'What is the meaning of dharma?',
                'confidence': 0.85,
                'alternatives': [
                    ('What is the meaning of dharma?', 0.85),
                    ('What is the meaning of drama?', 0.75)
                ],
                'contains_sanskrit': True,
                'spiritual_terms': ['dharma'],
                'language': language,
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
            
            # Update stats
            self.recognition_stats['total_requests'] += 1
            self.recognition_stats['successful_recognitions'] += 1
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"Voice processing failed: {e}")
            self.recognition_stats['failed_recognitions'] += 1
            return {
                'error': str(e),
                'transcript': '',
                'confidence': 0.0
            }
    
    def recognize_speech(self, audio_data: Optional[bytes] = None, timeout: Optional[float] = None) -> RecognitionResult:
        """
        Recognize speech from audio data or microphone input
        
        Args:
            audio_data: Optional audio data bytes
            timeout: Optional timeout override
            
        Returns:
            Recognition result with transcript and metadata
        """
        try:
            start_time = time.time()
            
            # Use provided timeout or default
            actual_timeout = timeout or self.config.timeout_seconds
            
            # Simulate speech recognition for testing
            if audio_data:
                # Process provided audio data
                transcript = "What is the meaning of dharma?"
                confidence = 0.85
            else:
                # Simulate microphone input
                transcript = "How can I follow Krishna's teachings?"
                confidence = 0.90
            
            # Analyze spiritual content
            contains_sanskrit = self._contains_sanskrit_terms(transcript)
            detected_mantras = self._detect_mantras(transcript)
            deity_references = self._detect_deity_references(transcript)
            spiritual_terms = self._extract_spiritual_terms(transcript)
            
            # Create result
            result = RecognitionResult(
                transcript=transcript,
                confidence=confidence,
                language=self.config.language,
                alternatives=[
                    (transcript, confidence),
                    ("Alternative transcript", confidence - 0.1)
                ],
                contains_sanskrit=contains_sanskrit,
                detected_mantras=detected_mantras,
                deity_references=deity_references,
                spiritual_terms=spiritual_terms,
                duration_ms=int((time.time() - start_time) * 1000),
                processing_time_ms=int((time.time() - start_time) * 1000),
                status=RecognitionStatus.COMPLETED,
                timestamp=datetime.now()
            )
            
            # Update statistics
            self._update_recognition_stats(result, time.time() - start_time)
            self.recognition_history.append(result)
            
            # Limit history size
            if len(self.recognition_history) > 100:
                self.recognition_history = self.recognition_history[-50:]
            
            return result
            
        except Exception as e:
            error_result = RecognitionResult(
                transcript="",
                confidence=0.0,
                language=self.config.language,
                status=RecognitionStatus.ERROR,
                error_message=str(e),
                timestamp=datetime.now()
            )
            self.recognition_history.append(error_result)
            return error_result
    
    def _contains_sanskrit_terms(self, text: str) -> bool:
        """Check if text contains Sanskrit terms"""
        text_lower = text.lower()
        return any(term in text_lower for term in self.sanskrit_vocabulary.keys())
    
    def _detect_mantras(self, text: str) -> List[str]:
        """Detect mantras in text"""
        text_lower = text.lower()
        detected = []
        for mantra in self.common_mantras:
            if mantra in text_lower:
                detected.append(mantra)
        return detected
    
    def _detect_deity_references(self, text: str) -> List[str]:
        """Detect deity name references"""
        text_lower = text.lower()
        detected = []
        for deity, variations in self.deity_names.items():
            if any(var in text_lower for var in variations):
                detected.append(deity)
        return detected
    
    def _extract_spiritual_terms(self, text: str) -> List[str]:
        """Extract spiritual terminology"""
        text_lower = text.lower()
        detected = []
        for term, weight in self.spiritual_vocabulary.items():
            if term in text_lower:
                detected.append(term)
        return detected
