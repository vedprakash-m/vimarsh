"""
Text-to-Speech Optimization for Spiritual Content Delivery

This module provides specialized TTS optimization for spiritual guidance content,
including Sanskrit pronunciation, emotional tone adjustment, and sacred content
delivery optimization for the Vimarsh AI Agent.
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
import unicodedata

try:
    import numpy as np
except ImportError:
    np = None

# Mock texttospeech for testing
try:
    from google.cloud import texttospeech
except ImportError:
    class texttospeech:
        """Mock texttospeech module for testing."""
        class TextToSpeechClient:
            def __init__(self):
                pass


class SpiritualTone(Enum):
    """Spiritual tone types for TTS"""
    REVERENT = "reverent"           # Deep respect and devotion
    COMPASSIONATE = "compassionate" # Warm and caring
    WISE = "wise"                  # Authoritative but gentle
    PEACEFUL = "peaceful"          # Calm and serene
    DEVOTIONAL = "devotional"      # Loving and surrendered
    INSTRUCTIONAL = "instructional" # Clear and guiding
    CONTEMPLATIVE = "contemplative" # Reflective and thoughtful
    JOYFUL = "joyful"             # Uplifting and celebratory


class VoiceCharacteristic(Enum):
    """Voice characteristics for spiritual content"""
    DEEP = "deep"           # Lower pitch, authoritative
    GENTLE = "gentle"       # Soft and soothing
    MELODIC = "melodic"     # Musical and flowing
    STEADY = "steady"       # Consistent and reliable
    WARM = "warm"          # Inviting and comforting
    CLEAR = "clear"        # Crisp and articulate


class SanskritPronunciation(Enum):
    """Sanskrit pronunciation styles"""
    CLASSICAL = "classical"     # Traditional Sanskrit pronunciation
    MODERN = "modern"          # Contemporary adapted pronunciation
    REGIONAL = "regional"      # Regional variations (Indian English)
    SIMPLIFIED = "simplified"  # Simplified for global audiences


@dataclass
class TTSConfig:
    """Configuration for spiritual TTS optimization"""
    
    # Basic TTS settings
    language: str = "en-US"
    voice_gender: str = "neutral"
    speaking_rate: float = 0.85  # Slightly slower for contemplation
    pitch: float = 0.0          # Neutral pitch
    volume: float = 0.8         # Slightly reduced for gentleness
    
    # Spiritual content settings
    spiritual_tone: SpiritualTone = SpiritualTone.WISE
    voice_characteristic: VoiceCharacteristic = VoiceCharacteristic.WARM
    sanskrit_pronunciation: SanskritPronunciation = SanskritPronunciation.MODERN
    
    # Content-specific adjustments
    emphasize_sanskrit_terms: bool = True
    pause_after_quotes: bool = True
    slower_for_mantras: bool = True
    reverent_deity_names: bool = True
    
    # Advanced settings
    emotion_intensity: float = 0.6  # 0.0 to 1.0
    breath_pauses: bool = True
    natural_phrasing: bool = True
    citation_formatting: bool = True


@dataclass
class SpiritualPhrase:
    """Spiritual phrase with TTS metadata"""
    text: str
    category: str  # mantra, quote, teaching, etc.
    tone: SpiritualTone
    emphasis_level: float = 0.5  # 0.0 to 1.0
    pause_before: float = 0.0    # seconds
    pause_after: float = 0.0     # seconds
    pronunciation_guide: Optional[str] = None
    cultural_context: Optional[str] = None


@dataclass
class TTSProcessingResult:
    """Result from TTS processing"""
    original_text: str
    processed_text: str  # With SSML markup
    audio_duration_estimate: float  # seconds
    
    # Processing metadata
    sanskrit_terms_count: int = 0
    spiritual_phrases_count: int = 0
    tone_adjustments: List[str] = field(default_factory=list)
    pronunciation_adjustments: List[str] = field(default_factory=list)
    
    # Quality metrics
    readability_score: float = 0.0
    spiritual_appropriateness: float = 0.0
    pronunciation_accuracy: float = 0.0
    
    processing_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class SpiritualTTSOptimizer:
    """
    Advanced TTS optimization system for spiritual content delivery
    """
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """Initialize spiritual TTS optimizer"""
        self.config = config or TTSConfig()
        self.logger = logging.getLogger(__name__)
        
        # Spiritual content mappings
        self.spiritual_phrases: Dict[str, SpiritualPhrase] = {}
        self.sanskrit_pronunciations: Dict[str, str] = {}
        self.tone_patterns: Dict[SpiritualTone, Dict[str, Any]] = {}
        self.deity_names: Dict[str, Dict[str, Any]] = {}
        
        # TTS processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'total_duration': 0.0,
            'average_processing_time': 0.0,
            'sanskrit_terms_processed': 0,
            'tone_adjustments_applied': 0,
            'pronunciation_corrections': 0
        }
        
        # Initialize spiritual content data
        self._initialize_spiritual_phrases()
        self._initialize_sanskrit_pronunciations()
        self._initialize_tone_patterns()
        self._initialize_deity_names()
    
    def _initialize_spiritual_phrases(self):
        """Initialize common spiritual phrases with TTS metadata"""
        
        phrases = [
            # Mantras
            SpiritualPhrase(
                text="Om",
                category="mantra",
                tone=SpiritualTone.REVERENT,
                emphasis_level=0.8,
                pause_before=0.5,
                pause_after=0.8,
                pronunciation_guide="AUM (long, resonant)",
                cultural_context="Sacred sound, primordial vibration"
            ),
            SpiritualPhrase(
                text="Om Namah Shivaya",
                category="mantra",
                tone=SpiritualTone.DEVOTIONAL,
                emphasis_level=0.9,
                pause_before=0.3,
                pause_after=1.0,
                pronunciation_guide="AUM NA-mah SHEE-va-ya",
                cultural_context="Invocation to Lord Shiva"
            ),
            SpiritualPhrase(
                text="Hare Krishna",
                category="mantra",
                tone=SpiritualTone.JOYFUL,
                emphasis_level=0.8,
                pause_before=0.2,
                pause_after=0.5,
                pronunciation_guide="HA-re KRISH-na",
                cultural_context="Devotional chant to Krishna"
            ),
            
            # Scriptural quotes markers
            SpiritualPhrase(
                text="As Krishna says in the Bhagavad Gita",
                category="citation",
                tone=SpiritualTone.REVERENT,
                emphasis_level=0.7,
                pause_after=0.3,
                cultural_context="Introducing sacred teaching"
            ),
            SpiritualPhrase(
                text="The scriptures tell us",
                category="citation",
                tone=SpiritualTone.WISE,
                emphasis_level=0.6,
                pause_after=0.2,
                cultural_context="Referencing ancient wisdom"
            ),
            
            # Philosophical concepts
            SpiritualPhrase(
                text="dharma",
                category="concept",
                tone=SpiritualTone.CONTEMPLATIVE,
                emphasis_level=0.7,
                pronunciation_guide="DHAR-ma",
                cultural_context="Righteous duty, natural law"
            ),
            SpiritualPhrase(
                text="karma",
                category="concept",
                tone=SpiritualTone.INSTRUCTIONAL,
                emphasis_level=0.6,
                pronunciation_guide="KAR-ma",
                cultural_context="Action, law of cause and effect"
            ),
            SpiritualPhrase(
                text="moksha",
                category="concept",
                tone=SpiritualTone.PEACEFUL,
                emphasis_level=0.8,
                pronunciation_guide="MOKE-sha",
                cultural_context="Liberation, spiritual freedom"
            ),
            
            # Devotional expressions
            SpiritualPhrase(
                text="with devotion",
                category="devotional",
                tone=SpiritualTone.COMPASSIONATE,
                emphasis_level=0.5,
                cultural_context="Expressing bhakti"
            ),
            SpiritualPhrase(
                text="in surrender",
                category="devotional",
                tone=SpiritualTone.PEACEFUL,
                emphasis_level=0.6,
                cultural_context="Act of spiritual surrender"
            ),
            
            # Blessings and conclusions
            SpiritualPhrase(
                text="May you find peace",
                category="blessing",
                tone=SpiritualTone.COMPASSIONATE,
                emphasis_level=0.7,
                pause_before=0.3,
                cultural_context="Spiritual blessing"
            ),
            SpiritualPhrase(
                text="Om Shanti Shanti Shanti",
                category="blessing",
                tone=SpiritualTone.PEACEFUL,
                emphasis_level=0.8,
                pause_before=0.5,
                pause_after=1.0,
                pronunciation_guide="AUM SHAN-ti SHAN-ti SHAN-ti",
                cultural_context="Peace invocation"
            )
        ]
        
        # Index phrases
        for phrase in phrases:
            self.spiritual_phrases[phrase.text.lower()] = phrase
        
        self.logger.info(f"Initialized {len(self.spiritual_phrases)} spiritual phrases")
    
    def _initialize_sanskrit_pronunciations(self):
        """Initialize Sanskrit pronunciation mappings"""
        
        self.sanskrit_pronunciations = {
            # Deities
            'krishna': 'KRISH-na',
            'rama': 'RA-ma',
            'shiva': 'SHEE-va',
            'vishnu': 'VISH-nu',
            'brahma': 'BRAH-ma',
            'ganesha': 'ga-NE-sha',
            'hanuman': 'HA-nu-man',
            'durga': 'DUR-ga',
            'lakshmi': 'LAKH-shmi',
            'saraswati': 'sa-ras-VA-ti',
            
            # Philosophical terms
            'dharma': 'DHAR-ma',
            'karma': 'KAR-ma',
            'yoga': 'YO-ga',
            'moksha': 'MOKE-sha',
            'nirvana': 'nir-VA-na',
            'samadhi': 'sa-MA-dhee',
            'atman': 'AAT-man',
            'brahman': 'BRAH-man',
            'samsara': 'sam-SA-ra',
            'ahimsa': 'a-HIM-sa',
            
            # Yoga terms
            'pranayama': 'pra-na-YA-ma',
            'asana': 'AA-sa-na',
            'vinyasa': 'vi-NYA-sa',
            'ujjayi': 'oo-JAH-yee',
            'bandha': 'BAN-da',
            'mudra': 'MU-dra',
            'chakra': 'CHAK-ra',
            'kundalini': 'kun-da-LEE-nee',
            
            # Mantras and sounds
            'om': 'AUM',
            'aum': 'AUM',
            'namaste': 'na-mas-TE',
            'namah': 'NA-mah',
            'shanti': 'SHAN-ti',
            'guru': 'GU-ru',
            'mantra': 'MAN-tra',
            
            # Scriptures
            'vedas': 'VE-das',
            'upanishads': 'u-pa-ni-SHADS',
            'bhagavad': 'BHA-ga-vad',
            'gita': 'GEE-ta',
            'ramayana': 'ra-MA-ya-na',
            'mahabharata': 'ma-ha-BHA-ra-ta',
            'puranas': 'pu-RA-nas',
            
            # Places and concepts
            'ayurveda': 'AY-ur-ve-da',
            'ashram': 'AASH-ram',
            'satsang': 'SAT-sang',
            'darshan': 'DAR-shan',
            'puja': 'PU-ja',
            'yajna': 'YAG-nya',
            'tapas': 'TA-pas',
            'seva': 'SE-va',
            'bhakti': 'BHAK-ti',
            'jnana': 'GYAA-na'
        }
        
        self.logger.info(f"Initialized {len(self.sanskrit_pronunciations)} pronunciation mappings")
    
    def _initialize_tone_patterns(self):
        """Initialize tone patterns for different spiritual contexts"""
        
        self.tone_patterns = {
            SpiritualTone.REVERENT: {
                'speaking_rate': 0.75,  # Slower
                'pitch_adjust': -0.1,   # Slightly lower
                'pause_multiplier': 1.3,
                'emphasis_style': 'strong',
                'breath_pauses': True
            },
            SpiritualTone.COMPASSIONATE: {
                'speaking_rate': 0.8,
                'pitch_adjust': 0.05,   # Slightly higher, warmer
                'pause_multiplier': 1.2,
                'emphasis_style': 'moderate',
                'breath_pauses': True
            },
            SpiritualTone.WISE: {
                'speaking_rate': 0.85,
                'pitch_adjust': 0.0,    # Neutral
                'pause_multiplier': 1.1,
                'emphasis_style': 'moderate',
                'breath_pauses': False
            },
            SpiritualTone.PEACEFUL: {
                'speaking_rate': 0.7,   # Very slow
                'pitch_adjust': -0.05,  # Slightly lower
                'pause_multiplier': 1.5,
                'emphasis_style': 'reduced',
                'breath_pauses': True
            },
            SpiritualTone.DEVOTIONAL: {
                'speaking_rate': 0.9,
                'pitch_adjust': 0.1,    # Higher, more emotional
                'pause_multiplier': 1.1,
                'emphasis_style': 'strong',
                'breath_pauses': False
            },
            SpiritualTone.INSTRUCTIONAL: {
                'speaking_rate': 0.9,
                'pitch_adjust': 0.0,
                'pause_multiplier': 1.0,
                'emphasis_style': 'clear',
                'breath_pauses': False
            },
            SpiritualTone.CONTEMPLATIVE: {
                'speaking_rate': 0.75,
                'pitch_adjust': -0.05,
                'pause_multiplier': 1.4,
                'emphasis_style': 'thoughtful',
                'breath_pauses': True
            },
            SpiritualTone.JOYFUL: {
                'speaking_rate': 1.0,
                'pitch_adjust': 0.15,   # Higher, more energetic
                'pause_multiplier': 0.9,
                'emphasis_style': 'enthusiastic',
                'breath_pauses': False
            }
        }
        
        self.logger.info(f"Initialized tone patterns for {len(self.tone_patterns)} tones")
    
    def _initialize_deity_names(self):
        """Initialize deity name handling with special reverence"""
        
        self.deity_names = {
            'krishna': {
                'pronunciation': 'KRISH-na',
                'pause_before': 0.2,
                'pause_after': 0.3,
                'emphasis': 0.8,
                'tone': SpiritualTone.REVERENT,
                'honorifics': ['Lord Krishna', 'Bhagavan Krishna', 'Sri Krishna']
            },
            'rama': {
                'pronunciation': 'RA-ma',
                'pause_before': 0.2,
                'pause_after': 0.3,
                'emphasis': 0.8,
                'tone': SpiritualTone.REVERENT,
                'honorifics': ['Lord Rama', 'Sri Rama', 'Bhagavan Rama']
            },
            'shiva': {
                'pronunciation': 'SHEE-va',
                'pause_before': 0.2,
                'pause_after': 0.3,
                'emphasis': 0.8,
                'tone': SpiritualTone.REVERENT,
                'honorifics': ['Lord Shiva', 'Mahadev', 'Bhagavan Shiva']
            },
            'vishnu': {
                'pronunciation': 'VISH-nu',
                'pause_before': 0.2,
                'pause_after': 0.3,
                'emphasis': 0.8,
                'tone': SpiritualTone.REVERENT,
                'honorifics': ['Lord Vishnu', 'Bhagavan Vishnu', 'Narayana']
            },
            'ganesha': {
                'pronunciation': 'ga-NE-sha',
                'pause_before': 0.15,
                'pause_after': 0.25,
                'emphasis': 0.7,
                'tone': SpiritualTone.JOYFUL,
                'honorifics': ['Lord Ganesha', 'Ganapati', 'Vinayaka']
            },
            'hanuman': {
                'pronunciation': 'HA-nu-man',
                'pause_before': 0.15,
                'pause_after': 0.25,
                'emphasis': 0.7,
                'tone': SpiritualTone.DEVOTIONAL,
                'honorifics': ['Lord Hanuman', 'Hanuman ji', 'Bajrangbali']
            }
        }
        
        self.logger.info(f"Initialized handling for {len(self.deity_names)} deity names")
    
    def detect_spiritual_content(self, text: str) -> Dict[str, Any]:
        """
        Detect spiritual content in text for TTS optimization
        
        Args:
            text: Input text to analyze
            
        Returns:
            Analysis results with detected spiritual elements
        """
        
        analysis = {
            'sanskrit_terms': [],
            'spiritual_phrases': [],
            'deity_references': [],
            'mantras': [],
            'citations': [],
            'dominant_tone': SpiritualTone.WISE,
            'content_type': 'general',
            'reverence_level': 0.5
        }
        
        text_lower = text.lower()
        
        # Detect Sanskrit terms
        for term, pronunciation in self.sanskrit_pronunciations.items():
            if term in text_lower:
                analysis['sanskrit_terms'].append({
                    'term': term,
                    'pronunciation': pronunciation,
                    'positions': [m.start() for m in re.finditer(re.escape(term), text_lower)]
                })
        
        # Detect spiritual phrases
        for phrase_text, phrase_obj in self.spiritual_phrases.items():
            if phrase_text in text_lower:
                analysis['spiritual_phrases'].append({
                    'text': phrase_text,
                    'phrase_obj': phrase_obj,
                    'positions': [m.start() for m in re.finditer(re.escape(phrase_text), text_lower)]
                })
        
        # Detect deity references
        for deity, deity_info in self.deity_names.items():
            if deity in text_lower:
                analysis['deity_references'].append({
                    'deity': deity,
                    'info': deity_info,
                    'positions': [m.start() for m in re.finditer(re.escape(deity), text_lower)]
                })
        
        # Detect mantras (longer sacred phrases)
        mantra_patterns = [
            r'om\s+namah?\s+shivaya',
            r'hare\s+krishna',
            r'om\s+mani\s+padme\s+hum',
            r'gayatri\s+mantra',
            r'om\s+shanti\s+shanti\s+shanti'
        ]
        
        for pattern in mantra_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                analysis['mantras'].append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Detect citations
        citation_patterns = [
            r'(krishna|lord krishna)\s+(says?|teaches?|explains?)',
            r'(bhagavad\s+)?gita\s+(says?|teaches?|tells us)',
            r'(the\s+)?(scriptures?|vedas?|upanishads?)\s+(say|tell|teach)',
            r'according\s+to\s+(krishna|the\s+gita|vedas?)',
            r'as\s+(krishna|the\s+gita|scriptures?)\s+(says?|teaches?)'
        ]
        
        for pattern in citation_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                analysis['citations'].append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Determine dominant tone and content type
        if analysis['mantras']:
            analysis['dominant_tone'] = SpiritualTone.REVERENT
            analysis['content_type'] = 'mantra'
            analysis['reverence_level'] = 0.9
        elif analysis['deity_references']:
            analysis['dominant_tone'] = SpiritualTone.DEVOTIONAL
            analysis['content_type'] = 'devotional'
            analysis['reverence_level'] = 0.8
        elif analysis['citations']:
            analysis['dominant_tone'] = SpiritualTone.WISE
            analysis['content_type'] = 'teaching'
            analysis['reverence_level'] = 0.7
        elif len(analysis['sanskrit_terms']) >= 3:
            analysis['dominant_tone'] = SpiritualTone.CONTEMPLATIVE
            analysis['content_type'] = 'philosophical'
            analysis['reverence_level'] = 0.6
        
        return analysis
    
    def generate_ssml_markup(self, text: str, analysis: Dict[str, Any]) -> str:
        """
        Generate SSML markup for spiritual content
        
        Args:
            text: Original text
            analysis: Spiritual content analysis
            
        Returns:
            Text with SSML markup
        """
        
        # Start with clean text
        ssml_text = text
        
        # Apply tone adjustments based on analysis
        tone = analysis['dominant_tone']
        tone_pattern = self.tone_patterns.get(tone, {})
        
        # Wrap in speak tag with prosody adjustments
        prosody_attrs = []
        
        if 'speaking_rate' in tone_pattern:
            rate_value = tone_pattern['speaking_rate']
            if rate_value < 0.8:
                prosody_attrs.append('rate="slow"')
            elif rate_value > 1.1:
                prosody_attrs.append('rate="fast"')
            else:
                prosody_attrs.append(f'rate="{rate_value}"')
        
        if 'pitch_adjust' in tone_pattern:
            pitch_adjust = tone_pattern['pitch_adjust']
            if abs(pitch_adjust) > 0.05:
                sign = '+' if pitch_adjust > 0 else ''
                prosody_attrs.append(f'pitch="{sign}{pitch_adjust * 100:.0f}%"')
        
        # Apply Sanskrit pronunciations
        for term_info in analysis['sanskrit_terms']:
            term = term_info['term']
            pronunciation = term_info['pronunciation']
            
            if self.config.emphasize_sanskrit_terms:
                # Use phoneme or substitute pronunciation
                phoneme_markup = f'<phoneme alphabet="ipa" ph="{pronunciation}">{term}</phoneme>'
                # Fallback to emphasis if phoneme not supported
                emphasis_markup = f'<emphasis level="moderate">{term}</emphasis>'
                
                # Replace with phoneme markup (use emphasis as fallback)
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                ssml_text = pattern.sub(emphasis_markup, ssml_text)
        
        # Apply deity name reverence
        for deity_info in analysis['deity_references']:
            deity = deity_info['deity']
            deity_data = deity_info['info']
            
            if self.config.reverent_deity_names:
                # Add pauses and emphasis for deity names
                pause_before = f'<break time="{deity_data["pause_before"]}s"/>'
                pause_after = f'<break time="{deity_data["pause_after"]}s"/>'
                emphasis = f'<emphasis level="strong">{deity}</emphasis>'
                
                full_markup = f'{pause_before}{emphasis}{pause_after}'
                
                pattern = re.compile(re.escape(deity), re.IGNORECASE)
                ssml_text = pattern.sub(full_markup, ssml_text)
        
        # Apply mantra special handling
        for mantra_info in analysis['mantras']:
            mantra_text = mantra_info['text']
            
            if self.config.slower_for_mantras:
                # Slow down mantras significantly
                mantra_markup = f'<prosody rate="x-slow">{mantra_text}</prosody>'
                ssml_text = ssml_text.replace(mantra_text, mantra_markup)
        
        # Add pauses after quotes/citations
        if self.config.pause_after_quotes:
            for citation_info in analysis['citations']:
                citation_text = citation_info['text']
                # Add pause after citation
                with_pause = f'{citation_text}<break time="0.5s"/>'
                ssml_text = ssml_text.replace(citation_text, with_pause)
        
        # Apply spiritual phrase handling
        for phrase_info in analysis['spiritual_phrases']:
            phrase_obj = phrase_info['phrase_obj']
            phrase_text = phrase_info['text']
            
            markup_parts = []
            
            # Add pause before if specified
            if phrase_obj.pause_before > 0:
                markup_parts.append(f'<break time="{phrase_obj.pause_before}s"/>')
            
            # Add emphasis based on level
            if phrase_obj.emphasis_level > 0.7:
                markup_parts.append(f'<emphasis level="strong">{phrase_text}</emphasis>')
            elif phrase_obj.emphasis_level > 0.4:
                markup_parts.append(f'<emphasis level="moderate">{phrase_text}</emphasis>')
            else:
                markup_parts.append(phrase_text)
            
            # Add pause after if specified
            if phrase_obj.pause_after > 0:
                markup_parts.append(f'<break time="{phrase_obj.pause_after}s"/>')
            
            full_markup = ''.join(markup_parts)
            ssml_text = ssml_text.replace(phrase_text, full_markup)
        
        # Add breath pauses for natural flow
        if self.config.breath_pauses and tone_pattern.get('breath_pauses', False):
            # Add subtle breath pauses at sentence boundaries
            ssml_text = re.sub(r'\.(\s+)', r'.<break time="0.3s"/>\1', ssml_text)
            ssml_text = re.sub(r'\?(\s+)', r'?<break time="0.4s"/>\1', ssml_text)
            ssml_text = re.sub(r'!(\s+)', r'!<break time="0.4s"/>\1', ssml_text)
        
        # Wrap in prosody tags if needed
        if prosody_attrs:
            prosody_tag = f'<prosody {" ".join(prosody_attrs)}>'
            ssml_text = f'{prosody_tag}{ssml_text}</prosody>'
        
        # Wrap in speak tag
        ssml_text = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">{ssml_text}</speak>'
        
        return ssml_text
    
    def estimate_audio_duration(self, text: str, analysis: Dict[str, Any]) -> float:
        """
        Estimate audio duration for processed text
        
        Args:
            text: Processed text
            analysis: Content analysis
            
        Returns:
            Estimated duration in seconds
        """
        
        # Base calculation: assume ~150 words per minute for normal speech
        words = len(text.split())
        base_duration = words / (150 / 60)  # Convert to seconds
        
        # Apply tone adjustments
        tone = analysis['dominant_tone']
        tone_pattern = self.tone_patterns.get(tone, {})
        
        if 'speaking_rate' in tone_pattern:
            rate_multiplier = 1.0 / tone_pattern['speaking_rate']
            base_duration *= rate_multiplier
        
        # Add time for pauses
        pause_time = 0.0
        
        # Pauses for Sanskrit terms
        if self.config.emphasize_sanskrit_terms:
            pause_time += len(analysis['sanskrit_terms']) * 0.1
        
        # Pauses for deity names
        if self.config.reverent_deity_names:
            for deity_info in analysis['deity_references']:
                deity_data = deity_info['info']
                pause_time += deity_data['pause_before'] + deity_data['pause_after']
        
        # Pauses for mantras
        if self.config.slower_for_mantras:
            mantra_words = sum(len(m['text'].split()) for m in analysis['mantras'])
            pause_time += mantra_words * 0.5  # Extra time for slow mantra delivery
        
        # Pauses for citations
        if self.config.pause_after_quotes:
            pause_time += len(analysis['citations']) * 0.5
        
        # Natural breath pauses
        if self.config.breath_pauses:
            sentence_count = text.count('.') + text.count('?') + text.count('!')
            pause_time += sentence_count * 0.3
        
        return base_duration + pause_time
    
    async def process_spiritual_content(self, text: str) -> TTSProcessingResult:
        """
        Process spiritual content for optimal TTS delivery
        
        Args:
            text: Input text to process
            
        Returns:
            Processing result with SSML and metadata
        """
        
        start_time = time.time()
        
        try:
            # Analyze spiritual content
            analysis = self.detect_spiritual_content(text)
            
            # Generate SSML markup
            processed_text = self.generate_ssml_markup(text, analysis)
            
            # Estimate duration
            duration = self.estimate_audio_duration(text, analysis)
            
            # Calculate quality metrics
            readability = self._calculate_readability_score(text)
            spiritual_appropriateness = self._calculate_spiritual_appropriateness(analysis)
            pronunciation_accuracy = self._calculate_pronunciation_accuracy(analysis)
            
            # Create result
            processing_time = int((time.time() - start_time) * 1000)
            
            result = TTSProcessingResult(
                original_text=text,
                processed_text=processed_text,
                audio_duration_estimate=duration,
                sanskrit_terms_count=len(analysis['sanskrit_terms']),
                spiritual_phrases_count=len(analysis['spiritual_phrases']),
                tone_adjustments=[analysis['dominant_tone'].value],
                pronunciation_adjustments=[
                    f"{term['term']} → {term['pronunciation']}"
                    for term in analysis['sanskrit_terms']
                ],
                readability_score=readability,
                spiritual_appropriateness=spiritual_appropriateness,
                pronunciation_accuracy=pronunciation_accuracy,
                processing_time_ms=processing_time
            )
            
            # Update statistics
            self._update_processing_stats(result, analysis)
            
            return result
            
        except Exception as e:
            self.logger.error(f"TTS processing error: {e}")
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Return basic result on error
            return TTSProcessingResult(
                original_text=text,
                processed_text=text,  # Fallback to original
                audio_duration_estimate=len(text.split()) / 2.5,  # Basic estimate
                processing_time_ms=processing_time
            )
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score for TTS"""
        
        # Simple readability calculation
        words = text.split()
        sentences = text.count('.') + text.count('?') + text.count('!')
        
        if sentences == 0:
            return 0.8  # Default for single sentence
        
        avg_words_per_sentence = len(words) / sentences
        
        # Ideal for TTS is 10-15 words per sentence
        if 10 <= avg_words_per_sentence <= 15:
            return 1.0
        elif avg_words_per_sentence < 10:
            return 0.9  # Short sentences are still good
        else:
            # Penalty for very long sentences
            return max(0.3, 1.0 - ((avg_words_per_sentence - 15) * 0.05))
    
    def _calculate_spiritual_appropriateness(self, analysis: Dict[str, Any]) -> float:
        """Calculate spiritual appropriateness score"""
        
        score = 0.5  # Base score
        
        # Bonus for spiritual content
        if analysis['sanskrit_terms']:
            score += 0.1
        
        if analysis['deity_references']:
            score += 0.15
        
        if analysis['mantras']:
            score += 0.2
        
        if analysis['citations']:
            score += 0.1
        
        # Bonus for appropriate reverence level
        if 0.6 <= analysis['reverence_level'] <= 0.9:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_pronunciation_accuracy(self, analysis: Dict[str, Any]) -> float:
        """Calculate pronunciation accuracy score"""
        
        total_terms = len(analysis['sanskrit_terms'])
        
        if total_terms == 0:
            return 1.0  # Perfect if no Sanskrit terms
        
        # Assume all terms have pronunciation guides (high accuracy)
        covered_terms = sum(
            1 for term in analysis['sanskrit_terms']
            if term['pronunciation']
        )
        
        return covered_terms / total_terms
    
    def _update_processing_stats(self, result: TTSProcessingResult, analysis: Dict[str, Any]):
        """Update processing statistics"""
        
        self.processing_stats['total_processed'] += 1
        self.processing_stats['total_duration'] += result.audio_duration_estimate
        
        # Update average processing time
        old_avg = self.processing_stats['average_processing_time']
        total = self.processing_stats['total_processed']
        self.processing_stats['average_processing_time'] = (
            (old_avg * (total - 1) + result.processing_time_ms) / total
        )
        
        self.processing_stats['sanskrit_terms_processed'] += result.sanskrit_terms_count
        self.processing_stats['tone_adjustments_applied'] += len(result.tone_adjustments)
        self.processing_stats['pronunciation_corrections'] += len(result.pronunciation_adjustments)
    
    def update_config(self, new_config: TTSConfig):
        """Update TTS configuration"""
        self.config = new_config
        self.logger.info("TTS configuration updated")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        
        stats = self.processing_stats.copy()
        
        if stats['total_processed'] > 0:
            stats['average_duration'] = stats['total_duration'] / stats['total_processed']
            stats['average_sanskrit_terms'] = stats['sanskrit_terms_processed'] / stats['total_processed']
        else:
            stats['average_duration'] = 0.0
            stats['average_sanskrit_terms'] = 0.0
        
        return stats
    
    def get_supported_tones(self) -> List[str]:
        """Get list of supported spiritual tones"""
        return [tone.value for tone in SpiritualTone]
    
    def get_supported_characteristics(self) -> List[str]:
        """Get list of supported voice characteristics"""
        return [char.value for char in VoiceCharacteristic]
    
    def preprocess_for_tts(self, text: str) -> str:
        """Preprocess spiritual text for optimal TTS delivery."""
        processed_text = text
        
        # Add pronunciation guides for Sanskrit terms
        for sanskrit_term, pronunciation in self.sanskrit_pronunciations.items():
            pattern = r'\b' + re.escape(sanskrit_term) + r'\b'
            replacement = f'<phoneme alphabet="ipa" ph="{pronunciation}">{sanskrit_term}</phoneme>'
            processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE)
        
        # Add pauses for spiritual phrases
        for phrase_text, phrase_obj in self.spiritual_phrases.items():
            if phrase_text in processed_text:
                pause_before = f'<break time="{phrase_obj.pause_before}s"/>' if phrase_obj.pause_before > 0 else ''
                pause_after = f'<break time="{phrase_obj.pause_after}s"/>' if phrase_obj.pause_after > 0 else ''
                processed_text = processed_text.replace(phrase_text, f'{pause_before}{phrase_text}{pause_after}')
        
        return processed_text
    
    def get_pronunciation_guide(self, text: str) -> Dict[str, str]:
        """Get pronunciation guide for Sanskrit terms in text."""
        pronunciation_guide = {}
        
        for sanskrit_term, pronunciation in self.sanskrit_pronunciations.items():
            if sanskrit_term in text:
                pronunciation_guide[sanskrit_term] = pronunciation
        
        return pronunciation_guide
    
    def select_optimal_voice(self, content_type: str, language: str = "en") -> Dict[str, Any]:
        """Select optimal voice parameters for content type."""
        voice_config = {
            'language': language,
            'voice_name': 'default',
            'pitch': 0.0,
            'speed': 1.0,
            'tone': SpiritualTone.WISE.value
        }
        
        # Adjust based on content type
        if content_type == 'mantra':
            voice_config.update({
                'tone': SpiritualTone.DEVOTIONAL.value,
                'pitch': -0.2,
                'speed': 0.8
            })
        elif content_type == 'teaching':
            voice_config.update({
                'tone': SpiritualTone.WISE.value,
                'pitch': 0.0,
                'speed': 0.9
            })
        elif content_type == 'meditation':
            voice_config.update({
                'tone': SpiritualTone.PEACEFUL.value,
                'pitch': -0.1,
                'speed': 0.7
            })
        
        return voice_config
    
    def adjust_emotional_tone(self, text: str, target_tone: SpiritualTone) -> str:
        """Adjust emotional tone of text for TTS."""
        # Add SSML markup for emotional tone
        tone_markup = f'<amazon:domain name="{target_tone.value}">'
        
        # Apply tone-specific adjustments
        if target_tone == SpiritualTone.REVERENT:
            tone_markup += '<prosody rate="slow" pitch="-10%">'
        elif target_tone == SpiritualTone.PEACEFUL:
            tone_markup += '<prosody rate="x-slow" pitch="-5%">'
        elif target_tone == SpiritualTone.JOYFUL:
            tone_markup += '<prosody rate="medium" pitch="+10%">'
        else:
            tone_markup += '<prosody rate="medium">'
        
        processed_text = f'{tone_markup}{text}</prosody></amazon:domain>'
        return processed_text
    
    def optimize_pauses_and_emphasis(self, text: str) -> Any:
        """Optimize pauses and emphasis for spiritual content."""
        optimized_text = text
        
        # Track markers for analysis
        markers = []
        
        # Add pauses after sentences
        optimized_text = re.sub(r'\.(\s+)', r'.<break time="0.5s"/>\1', optimized_text)
        
        # Track citation pauses
        if 'Chapter' in text or 'Verse' in text or '"' in text:
            markers.append(type('Marker', (), {
                'type': 'pause',
                'duration': 1.2,
                'position': text.find('Chapter') if 'Chapter' in text else text.find('"'),
                'reason': 'citation'
            })())
        
        # Add emphasis to important spiritual terms
        spiritual_keywords = ['dharma', 'karma', 'moksha', 'atman', 'brahman', 'yoga']
        for keyword in spiritual_keywords:
            if keyword.lower() in text.lower():
                pattern = r'\b' + re.escape(keyword) + r'\b'
                replacement = f'<emphasis level="moderate">{keyword}</emphasis>'
                optimized_text = re.sub(pattern, replacement, optimized_text, flags=re.IGNORECASE)
                
                markers.append(type('Marker', (), {
                    'type': 'emphasis',
                    'duration': 0.3,
                    'position': text.lower().find(keyword.lower()),
                    'term': keyword
                })())
        
        # Add emphasis for quoted text
        if '"' in text:
            markers.append(type('Marker', (), {
                'type': 'emphasis',
                'duration': 0.5,
                'position': text.find('"'),
                'reason': 'quote'
            })())
        
        # Create result object with markers
        result = type('OptimizedResult', (), {
            'text': optimized_text,
            'markers': markers,
            'marker_count': len(markers)
        })()
        
        return result
    
    async def generate_speech(self, text: str, voice_config: Optional[Dict[str, Any]] = None, language: str = "en-US") -> Any:
        """Generate speech with spiritual optimizations."""
        if voice_config is None:
            voice_config = self.select_optimal_voice('teaching')
        
        # Process text
        processed_text = self.preprocess_for_tts(text)
        
        # Mock TTS generation with async simulation
        await asyncio.sleep(0.01)  # Simulate async processing
        
        # Create mock audio response object
        audio_response = type('AudioResponse', (), {
            'audio_data': f"generated_audio_for_{text[:20]}".encode(),
            'duration': len(text) * 0.1,  # Rough estimate
            'language': language,
            'processed_text': processed_text,
            'voice_config': voice_config,
            'success': True
        })()
        
        return audio_response
