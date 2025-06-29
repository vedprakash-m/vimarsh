"""
Multilingual Voice Support (English/Hindi)

This module provides comprehensive multilingual voice support for English and Hindi,
including proper pronunciation of Sanskrit terms, regional accents, and
cultural context awareness for spiritual content delivery.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    HINDI = "hi"
    SANSKRIT = "sa"  # For Sanskrit terms and mantras


class Accent(Enum):
    """Regional accents for better localization"""
    # English accents
    AMERICAN = "en-US"
    BRITISH = "en-GB"
    INDIAN_ENGLISH = "en-IN"
    
    # Hindi accents
    STANDARD_HINDI = "hi-IN"
    DELHI_HINDI = "hi-IN-Delhi"
    MUMBAI_HINDI = "hi-IN-Mumbai"


class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


@dataclass
class VoiceProfile:
    """Voice profile for multilingual support"""
    language: Language
    accent: Accent
    gender: VoiceGender
    voice_name: str
    sample_rate: int = 22050
    pitch_range: Tuple[float, float] = (0.8, 1.2)
    speed_range: Tuple[float, float] = (0.7, 1.3)
    supports_sanskrit: bool = False
    cultural_context: str = "neutral"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API usage"""
        return {
            "language": self.language.value,
            "accent": self.accent.value,
            "gender": self.gender.value,
            "voice_name": self.voice_name,
            "sample_rate": self.sample_rate,
            "pitch_range": self.pitch_range,
            "speed_range": self.speed_range,
            "supports_sanskrit": self.supports_sanskrit,
            "cultural_context": self.cultural_context
        }


@dataclass
class TranslationRequest:
    """Request for text translation"""
    source_text: str
    source_language: Language
    target_language: Language
    preserve_sanskrit: bool = True
    maintain_reverence: bool = True
    cultural_adaptation: bool = True


@dataclass
class SanskritTerm:
    """Sanskrit term with pronunciation guides"""
    term: str
    english_pronunciation: str
    hindi_pronunciation: str
    devanagari: str
    meaning: str
    category: str  # "deity", "concept", "practice", etc.


class SanskritPronunciationGuide:
    """Manages Sanskrit pronunciation in different languages"""
    
    def __init__(self):
        self.sanskrit_terms = self._load_sanskrit_terms()
        self.pronunciation_rules = self._load_pronunciation_rules()
    
    def _load_sanskrit_terms(self) -> Dict[str, SanskritTerm]:
        """Load Sanskrit terms with pronunciation guides"""
        return {
            "om": SanskritTerm(
                term="Om",
                english_pronunciation="AUM (with prolonged 'a', 'u', 'm')",
                hindi_pronunciation="ॐ (ओऽम्)",
                devanagari="ॐ",
                meaning="Sacred sound, cosmic vibration",
                category="mantra"
            ),
            "krishna": SanskritTerm(
                term="Krishna",
                english_pronunciation="KRISH-na (with slight roll on 'r')",
                hindi_pronunciation="कृष्ण (कृष्ण)",
                devanagari="कृष्ण",
                meaning="The dark one, divine avatar",
                category="deity"
            ),
            "dharma": SanskritTerm(
                term="Dharma",
                english_pronunciation="DHAR-ma (with soft 'a')",
                hindi_pronunciation="धर्म (धर्म)",
                devanagari="धर्म",
                meaning="Righteous duty, cosmic law",
                category="concept"
            ),
            "karma": SanskritTerm(
                term="Karma",
                english_pronunciation="KAR-ma (with soft 'a')",
                hindi_pronunciation="कर्म (कर्म)",
                devanagari="कर्म",
                meaning="Action and consequence",
                category="concept"
            ),
            "moksha": SanskritTerm(
                term="Moksha",
                english_pronunciation="MOHK-sha",
                hindi_pronunciation="मोक्ष (मोक्ष)",
                devanagari="मोक्ष",
                meaning="Liberation, spiritual freedom",
                category="concept"
            ),
            "yoga": SanskritTerm(
                term="Yoga",
                english_pronunciation="YO-ga (with long 'o')",
                hindi_pronunciation="योग (योग)",
                devanagari="योग",
                meaning="Union, spiritual practice",
                category="practice"
            ),
            "bhakti": SanskritTerm(
                term="Bhakti",
                english_pronunciation="BHAK-ti",
                hindi_pronunciation="भक्ति (भक्ति)",
                devanagari="भक्ति",
                meaning="Devotion, loving surrender",
                category="practice"
            ),
            "gita": SanskritTerm(
                term="Gita",
                english_pronunciation="GEE-ta",
                hindi_pronunciation="गीता (गीता)",
                devanagari="गीता",
                meaning="Song, referring to Bhagavad Gita",
                category="text"
            ),
            "mantra": SanskritTerm(
                term="Mantra",
                english_pronunciation="MAN-tra",
                hindi_pronunciation="मन्त्र (मन्त्र)",
                devanagari="मन्त्र",
                meaning="Sacred sound or phrase",
                category="practice"
            ),
            "atman": SanskritTerm(
                term="Atman",
                english_pronunciation="AHT-man",
                hindi_pronunciation="आत्मन् (आत्मन्)",
                devanagari="आत्मन्",
                meaning="Soul, inner self",
                category="concept"
            )
        }
    
    def _load_pronunciation_rules(self) -> Dict[str, Dict[str, str]]:
        """Load general pronunciation rules for Sanskrit in different languages"""
        return {
            "english": {
                "a": "ah (as in 'father')",
                "i": "ee (as in 'see')",
                "u": "oo (as in 'moon')",
                "e": "ay (as in 'day')",
                "o": "oh (as in 'go')",
                "r": "slight roll",
                "ch": "ch (as in 'church')",
                "bh": "b + h (aspirated b)",
                "dh": "d + h (aspirated d)",
                "gh": "g + h (aspirated g)",
                "kh": "k + h (aspirated k)",
                "ph": "p + h (aspirated p)",
                "th": "t + h (aspirated t)"
            },
            "hindi": {
                "general": "Follow Devanagari pronunciation",
                "emphasis": "Stress usually on first syllable",
                "vowels": "Pure vowel sounds as in Hindi",
                "consonants": "Use retroflex sounds where appropriate"
            }
        }
    
    def get_pronunciation_guide(self, term: str, language: Language) -> Optional[str]:
        """Get pronunciation guide for a Sanskrit term in the specified language"""
        term_lower = term.lower()
        
        if term_lower in self.sanskrit_terms:
            sanskrit_term = self.sanskrit_terms[term_lower]
            
            if language == Language.ENGLISH:
                return sanskrit_term.english_pronunciation
            elif language == Language.HINDI:
                return sanskrit_term.hindi_pronunciation
            elif language == Language.SANSKRIT:
                return sanskrit_term.devanagari
        
        return None
    
    def get_term_info(self, term: str) -> Optional[SanskritTerm]:
        """Get complete information about a Sanskrit term"""
        return self.sanskrit_terms.get(term.lower())


class MultilingualTextProcessor:
    """Processes text for multilingual voice synthesis"""
    
    def __init__(self):
        self.sanskrit_guide = SanskritPronunciationGuide()
        self.translation_cache = {}
        
    def prepare_text_for_voice(self, text: str, target_language: Language, 
                              voice_profile: VoiceProfile) -> str:
        """
        Prepare text for voice synthesis in the target language
        
        Args:
            text: Original text to process
            target_language: Target language for voice synthesis
            voice_profile: Voice profile to use
            
        Returns:
            Processed text optimized for voice synthesis
        """
        processed_text = text
        
        # Handle Sanskrit terms
        processed_text = self._process_sanskrit_terms(processed_text, target_language)
        
        # Add pronunciation markers
        processed_text = self._add_pronunciation_markers(processed_text, target_language)
        
        # Adjust for cultural context
        processed_text = self._adjust_cultural_context(processed_text, voice_profile)
        
        # Add SSML markup if needed
        if self._should_use_ssml(voice_profile):
            processed_text = self._add_ssml_markup(processed_text, voice_profile)
        
        return processed_text
    
    def _process_sanskrit_terms(self, text: str, language: Language) -> str:
        """Process Sanskrit terms for proper pronunciation"""
        processed_text = text
        
        for term, sanskrit_obj in self.sanskrit_guide.sanskrit_terms.items():
            # Find occurrences of the term (case-insensitive)
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                original = match.group()
                
                if language == Language.ENGLISH:
                    # Add pronunciation guide as a comment or SSML
                    pronunciation = sanskrit_obj.english_pronunciation
                    replacement = f"{original}"  # Keep original, add SSML later
                elif language == Language.HINDI:
                    # Use Devanagari script if appropriate
                    replacement = sanskrit_obj.devanagari if sanskrit_obj.devanagari else original
                else:
                    replacement = original
                
                processed_text = processed_text.replace(original, replacement, 1)
        
        return processed_text
    
    def _add_pronunciation_markers(self, text: str, language: Language) -> str:
        """Add pronunciation markers for better voice synthesis"""
        if language == Language.ENGLISH:
            # Add stress markers for important spiritual terms
            spiritual_terms = ["dharma", "karma", "moksha", "krishna", "yoga"]
            for term in spiritual_terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                replacement = f"<emphasis level='moderate'>{term}</emphasis>"
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _adjust_cultural_context(self, text: str, voice_profile: VoiceProfile) -> str:
        """Adjust text based on cultural context"""
        if voice_profile.cultural_context == "indian":
            # Use more traditional greetings and phrases
            text = text.replace("Hello", "Namaste")
            text = text.replace("Goodbye", "Om Shanti")
        
        return text
    
    def _should_use_ssml(self, voice_profile: VoiceProfile) -> bool:
        """Determine if SSML markup should be used"""
        return voice_profile.supports_sanskrit or voice_profile.language == Language.HINDI
    
    def _add_ssml_markup(self, text: str, voice_profile: VoiceProfile) -> str:
        """Add SSML markup for enhanced voice synthesis"""
        # Wrap in SSML speak tag
        ssml_text = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{voice_profile.language.value}">'
        
        # Add voice selection
        ssml_text += f'<voice name="{voice_profile.voice_name}">'
        
        # Process the text content
        ssml_text += text
        
        # Close tags
        ssml_text += '</voice></speak>'
        
        return ssml_text


class VoiceSelector:
    """Selects appropriate voice profiles for different languages and contexts"""
    
    def __init__(self):
        self.voice_profiles = self._initialize_voice_profiles()
    
    def _initialize_voice_profiles(self) -> Dict[str, List[VoiceProfile]]:
        """Initialize voice profiles for different languages"""
        return {
            "english": [
                VoiceProfile(
                    language=Language.ENGLISH,
                    accent=Accent.INDIAN_ENGLISH,
                    gender=VoiceGender.MALE,
                    voice_name="en-IN-PrabhatNeural",
                    supports_sanskrit=True,
                    cultural_context="indian"
                ),
                VoiceProfile(
                    language=Language.ENGLISH,
                    accent=Accent.INDIAN_ENGLISH,
                    gender=VoiceGender.FEMALE,
                    voice_name="en-IN-NeerjaNeural",
                    supports_sanskrit=True,
                    cultural_context="indian"
                ),
                VoiceProfile(
                    language=Language.ENGLISH,
                    accent=Accent.AMERICAN,
                    gender=VoiceGender.MALE,
                    voice_name="en-US-DavisNeural",
                    supports_sanskrit=False,
                    cultural_context="neutral"
                ),
                VoiceProfile(
                    language=Language.ENGLISH,
                    accent=Accent.BRITISH,
                    gender=VoiceGender.FEMALE,
                    voice_name="en-GB-SoniaNeural",
                    supports_sanskrit=False,
                    cultural_context="neutral"
                )
            ],
            "hindi": [
                VoiceProfile(
                    language=Language.HINDI,
                    accent=Accent.STANDARD_HINDI,
                    gender=VoiceGender.MALE,
                    voice_name="hi-IN-MadhurNeural",
                    supports_sanskrit=True,
                    cultural_context="indian"
                ),
                VoiceProfile(
                    language=Language.HINDI,
                    accent=Accent.STANDARD_HINDI,
                    gender=VoiceGender.FEMALE,
                    voice_name="hi-IN-SwaraNeural",
                    supports_sanskrit=True,
                    cultural_context="indian"
                )
            ]
        }
    
    def select_voice(self, language: Language, preferences: Optional[Dict] = None) -> VoiceProfile:
        """
        Select appropriate voice profile based on language and preferences
        
        Args:
            language: Target language
            preferences: User preferences (gender, accent, etc.)
            
        Returns:
            Selected VoiceProfile
        """
        language_key = language.value if language != Language.SANSKRIT else "hindi"
        available_voices = self.voice_profiles.get(language_key, [])
        
        if not available_voices:
            # Fallback to English
            available_voices = self.voice_profiles["english"]
        
        # Apply preferences if provided
        if preferences:
            filtered_voices = self._filter_by_preferences(available_voices, preferences)
            if filtered_voices:
                available_voices = filtered_voices
        
        # For spiritual content, prefer Indian context voices
        spiritual_voices = [v for v in available_voices if v.cultural_context == "indian"]
        if spiritual_voices:
            return spiritual_voices[0]
        
        return available_voices[0]
    
    def _filter_by_preferences(self, voices: List[VoiceProfile], preferences: Dict) -> List[VoiceProfile]:
        """Filter voices based on user preferences"""
        filtered = voices
        
        if "gender" in preferences:
            gender_pref = VoiceGender(preferences["gender"])
            filtered = [v for v in filtered if v.gender == gender_pref]
        
        if "accent" in preferences:
            accent_pref = Accent(preferences["accent"])
            filtered = [v for v in filtered if v.accent == accent_pref]
        
        if "sanskrit_support" in preferences and preferences["sanskrit_support"]:
            filtered = [v for v in filtered if v.supports_sanskrit]
        
        return filtered
    
    def get_available_voices(self, language: Language) -> List[VoiceProfile]:
        """Get all available voices for a language"""
        language_key = language.value if language != Language.SANSKRIT else "hindi"
        return self.voice_profiles.get(language_key, [])


class MultilingualVoiceManager:
    """Main manager for multilingual voice support"""
    
    def __init__(self):
        self.text_processor = MultilingualTextProcessor()
        self.voice_selector = VoiceSelector()
        self.current_language = Language.ENGLISH
        self.current_voice_profile = None
        self.supported_languages = ['en', 'hi', 'sa']  # English, Hindi, Sanskrit
        
    def initialize_voice(self, language: Language, preferences: Optional[Dict] = None) -> VoiceProfile:
        """
        Initialize voice for the specified language
        
        Args:
            language: Target language
            preferences: User voice preferences
            
        Returns:
            Selected VoiceProfile
        """
        self.current_language = language
        self.current_voice_profile = self.voice_selector.select_voice(language, preferences)
        
        logger.info(f"Initialized voice: {self.current_voice_profile.voice_name} for {language.value}")
        
        return self.current_voice_profile
    
    def prepare_speech_synthesis(self, text: str, language: Optional[Language] = None) -> Dict[str, Any]:
        """
        Prepare text for speech synthesis in the specified language
        
        Args:
            text: Text to synthesize
            language: Target language (uses current if not specified)
            
        Returns:
            Dictionary with processed text and voice settings
        """
        target_language = language or self.current_language
        
        # Select voice if not already set for this language
        if not self.current_voice_profile or self.current_voice_profile.language != target_language:
            self.initialize_voice(target_language)
        
        # Process text for voice synthesis
        processed_text = self.text_processor.prepare_text_for_voice(
            text, target_language, self.current_voice_profile
        )
        
        return {
            "processed_text": processed_text,
            "voice_profile": self.current_voice_profile.to_dict(),
            "language": target_language.value,
            "synthesis_settings": {
                "rate": "medium",
                "pitch": "medium",
                "volume": "medium"
            }
        }
    
    def get_sanskrit_pronunciation_guide(self, term: str, language: Language) -> Optional[str]:
        """Get pronunciation guide for Sanskrit terms"""
        return self.text_processor.sanskrit_guide.get_pronunciation_guide(term, language)
    
    def detect_language_preference(self, text: str) -> Language:
        """
        Detect preferred language based on text content
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected preferred language
        """
        # Simple heuristics for language detection
        hindi_indicators = ['देव', 'भगवान', 'गुरु', 'प्रभु', 'श्री', 'है', 'का', 'में', 'से', 'को', 'की', 'के']
        sanskrit_indicators = ['स्य', 'अर्थः', 'किम्', 'त्वम्', 'अहम्', 'तत्', 'इति', 'यत्', 'सः', 'तस्य']
        sanskrit_density = self._calculate_sanskrit_density(text)
        
        # Check for Devanagari script
        devanagari_pattern = r'[\u0900-\u097F]'
        if re.search(devanagari_pattern, text):
            # Check if it's Sanskrit based on specific indicators
            if any(indicator in text for indicator in sanskrit_indicators):
                return Language.SANSKRIT
            # Check for classical Sanskrit patterns
            if 'स्य' in text or 'ः' in text or 'अर्थः' in text:
                return Language.SANSKRIT
            # Otherwise, assume Hindi
            return Language.HINDI
        
        # Check for Hindi indicators in romanized text
        if any(indicator in text for indicator in hindi_indicators):
            return Language.HINDI
        
        # High Sanskrit content might prefer Sanskrit
        if sanskrit_density > 0.5:
            return Language.SANSKRIT
        elif sanskrit_density > 0.3:
            return Language.HINDI
        
        return Language.ENGLISH
    
    def _calculate_sanskrit_density(self, text: str) -> float:
        """Calculate the density of Sanskrit terms in text"""
        words = text.lower().split()
        if not words:
            return 0.0
        
        sanskrit_words = 0
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.text_processor.sanskrit_guide.sanskrit_terms:
                sanskrit_words += 1
        
        return sanskrit_words / len(words)
    
    def switch_language(self, new_language: Language, preferences: Optional[Dict] = None) -> bool:
        """
        Switch to a different language
        
        Args:
            new_language: New language to switch to
            preferences: Voice preferences for new language
            
        Returns:
            True if switch was successful
        """
        try:
            self.initialize_voice(new_language, preferences)
            logger.info(f"Switched to {new_language.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to {new_language.value}: {e}")
            return False
    
    def get_language_capabilities(self) -> Dict[str, Any]:
        """Get information about supported languages and capabilities"""
        capabilities = {}
        
        for lang in Language:
            available_voices = self.voice_selector.get_available_voices(lang)
            capabilities[lang.value] = {
                "supported": len(available_voices) > 0,
                "voice_count": len(available_voices),
                "sanskrit_support": any(v.supports_sanskrit for v in available_voices),
                "available_accents": list(set(v.accent.value for v in available_voices)),
                "available_genders": list(set(v.gender.value for v in available_voices))
            }
        
        return capabilities
    
    def create_voice_sample(self, text: str, language: Language) -> Dict[str, Any]:
        """Create a voice sample for testing purposes"""
        synthesis_data = self.prepare_speech_synthesis(text, language)
        
        # Add sample metadata
        synthesis_data["sample_metadata"] = {
            "text_length": len(text),
            "sanskrit_terms": self._extract_sanskrit_terms(text),
            "estimated_duration": len(text.split()) * 0.5,  # Rough estimate
            "complexity": "simple" if len(text.split()) < 20 else "complex"
        }
        
        return synthesis_data
    
    def _extract_sanskrit_terms(self, text: str) -> List[str]:
        """Extract Sanskrit terms from text"""
        terms = []
        for term in self.text_processor.sanskrit_guide.sanskrit_terms.keys():
            if term in text.lower():
                terms.append(term)
        return terms
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the primary language of the input text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detection results
        """
        # Simulate async language detection
        import asyncio
        await asyncio.sleep(0.01)  # Simulate processing time
        
        # Detect language preference
        lang = self.detect_language_preference(text)
        
        # Check for code-switching (mixed languages)
        is_code_switching = False
        languages = [lang.value]
        
        # Simple heuristic for code-switching detection
        has_devanagari = any(char in text for char in 'नमस्ते जी हैं का धर्म कर्म योग मोक्ष आत्मा ब्रह्म')
        has_ascii_words = len([word for word in text.split() if word.isascii() and word.isalpha()]) > 0
        
        # More specific code-switching detection
        if has_devanagari and has_ascii_words and len(text.split()) > 1:
            # Check if it's actually mixed (not just Sanskrit transliteration)
            mixed_indicators = ['hello', 'hi', 'bye', 'thanks', 'namaste']
            if any(indicator in text.lower() for indicator in mixed_indicators) and has_devanagari:
                is_code_switching = True
                languages = ['en', 'hi']
        
        # Calculate confidence based on text analysis
        confidence = 0.9
        if is_code_switching:
            confidence = 0.7
        elif lang == Language.SANSKRIT:
            confidence = 0.85  # Sanskrit might be less certain due to transliteration
        
        return {
            'primary_language': lang.value,
            'confidence': confidence,
            'is_code_switching': is_code_switching,
            'languages': languages,
            'detected_segments': []
        }
    
    def process_mixed_language(self, text: str) -> Dict[str, Any]:
        """
        Process text that contains multiple languages (code-switching)
        
        Args:
            text: Mixed language text
            
        Returns:
            Processing result with language segments
        """
        try:
            # Analyze text for language segments
            segments = []
            words = text.split()
            current_segment = []
            current_language = self.detect_language(text)
            
            for word in words:
                # Simple heuristic for language detection
                if self._is_sanskrit_term(word):
                    if current_language != Language.SANSKRIT:
                        if current_segment:
                            segments.append({
                                'text': ' '.join(current_segment),
                                'language': current_language,
                                'start_pos': len(' '.join(segments)) if segments else 0
                            })
                            current_segment = []
                        current_language = Language.SANSKRIT
                    current_segment.append(word)
                else:
                    # Continue with current language or detect
                    current_segment.append(word)
            
            # Add final segment
            if current_segment:
                segments.append({
                    'text': ' '.join(current_segment),
                    'language': current_language,
                    'start_pos': len(' '.join(segments)) if segments else 0
                })
            
            return {
                'segments': segments,
                'primary_language': self.detect_language(text),
                'has_code_switching': len(set(s['language'] for s in segments)) > 1
            }
            
        except Exception as e:
            logger.error(f"Mixed language processing error: {e}")
            return {
                'segments': [{'text': text, 'language': self.current_language, 'start_pos': 0}],
                'primary_language': self.current_language,
                'has_code_switching': False
            }
    
    def synthesize_multilingual(self, text: str, preserve_accents: bool = True) -> Dict[str, Any]:
        """
        Synthesize speech for multilingual text
        
        Args:
            text: Text to synthesize (may contain multiple languages)
            preserve_accents: Whether to preserve language-specific accents
            
        Returns:
            Synthesis result with audio data and metadata
        """
        try:
            # Process mixed language content
            processing_result = self.process_mixed_language(text)
            
            # Prepare synthesis for each segment
            synthesis_segments = []
            for segment in processing_result['segments']:
                voice_profile = self.voice_selector.select_voice(
                    segment['language'], 
                    {'preserve_accent': preserve_accents}
                )
                
                synthesis_segments.append({
                    'text': segment['text'],
                    'language': segment['language'],
                    'voice_profile': voice_profile,
                    'start_pos': segment['start_pos']
                })
            
            return {
                'segments': synthesis_segments,
                'total_segments': len(synthesis_segments),
                'primary_language': processing_result['primary_language'],
                'multilingual': processing_result['has_code_switching']
            }
            
        except Exception as e:
            logger.error(f"Multilingual synthesis error: {e}")
            return {
                'segments': [{'text': text, 'language': self.current_language, 'voice_profile': self.current_voice_profile}],
                'total_segments': 1,
                'primary_language': self.current_language,
                'multilingual': False
            }
    
    def _is_sanskrit_term(self, word: str) -> bool:
        """Check if a word is a Sanskrit term"""
        clean_word = re.sub(r'[^\w]', '', word.lower())
        return clean_word in self.text_processor.sanskrit_guide.sanskrit_terms


# Convenience functions for integration

def initialize_multilingual_voice(language: str = "en", preferences: Optional[Dict] = None) -> MultilingualVoiceManager:
    """
    Initialize multilingual voice manager
    
    Args:
        language: Language code ("en", "hi", "sa")
        preferences: Voice preferences
        
    Returns:
        Configured MultilingualVoiceManager
    """
    manager = MultilingualVoiceManager()
    lang_enum = Language(language)
    manager.initialize_voice(lang_enum, preferences)
    return manager


def prepare_multilingual_speech(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Prepare text for multilingual speech synthesis
    
    Args:
        text: Text to synthesize
        language: Target language code
        
    Returns:
        Speech synthesis data
    """
    manager = MultilingualVoiceManager()
    lang_enum = Language(language)
    return manager.prepare_speech_synthesis(text, lang_enum)


def get_sanskrit_pronunciation(term: str, language: str = "en") -> Optional[str]:
    """
    Get Sanskrit pronunciation guide
    
    Args:
        term: Sanskrit term
        language: Target language for pronunciation guide
        
    Returns:
        Pronunciation guide or None
    """
    manager = MultilingualVoiceManager()
    lang_enum = Language(language)
    return manager.get_sanskrit_pronunciation_guide(term, lang_enum)


# Example usage and testing
if __name__ == "__main__":
    print("=== Multilingual Voice Support Demo ===\n")
    
    manager = MultilingualVoiceManager()
    
    # Test texts in different contexts
    test_cases = [
        {
            "text": "My dear child, dharma is your sacred duty. As Krishna teaches in the Bhagavad Gita, perform your actions with devotion.",
            "language": "en",
            "description": "English spiritual guidance"
        },
        {
            "text": "ॐ शान्ति शान्ति शान्तिः। प्रभु कृष्ण की जय।",
            "language": "hi", 
            "description": "Hindi/Sanskrit mantra"
        },
        {
            "text": "Let us chant the sacred mantra Om together in meditation.",
            "language": "en",
            "description": "English meditation instruction"
        },
        {
            "text": "योग और भक्ति के माध्यम से मोक्ष की प्राप्ति होती है।",
            "language": "hi",
            "description": "Hindi philosophical teaching"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test Case {i}: {case['description']}")
        print(f"Text: {case['text'][:60]}...")
        
        # Detect language preference
        detected_lang = manager.detect_language_preference(case['text'])
        print(f"Detected Language: {detected_lang.value}")
        
        # Prepare speech synthesis
        synthesis_data = manager.prepare_speech_synthesis(case['text'], Language(case['language']))
        
        print(f"Target Language: {synthesis_data['language']}")
        print(f"Voice: {synthesis_data['voice_profile']['voice_name']}")
        print(f"Sanskrit Support: {synthesis_data['voice_profile']['supports_sanskrit']}")
        print(f"Cultural Context: {synthesis_data['voice_profile']['cultural_context']}")
        
        # Show processed text if different
        if synthesis_data['processed_text'] != case['text']:
            print(f"Processed Text: {synthesis_data['processed_text'][:60]}...")
        
        print("-" * 80 + "\n")
    
    # Test Sanskrit pronunciation guides
    print("Sanskrit Pronunciation Guides:")
    sanskrit_terms = ["om", "krishna", "dharma", "karma", "yoga"]
    
    for term in sanskrit_terms:
        en_pronunciation = manager.get_sanskrit_pronunciation_guide(term, Language.ENGLISH)
        hi_pronunciation = manager.get_sanskrit_pronunciation_guide(term, Language.HINDI)
        
        print(f"{term.title()}:")
        print(f"  English: {en_pronunciation}")
        print(f"  Hindi: {hi_pronunciation}")
    
    # Show language capabilities
    print(f"\nLanguage Capabilities:")
    capabilities = manager.get_language_capabilities()
    for lang, caps in capabilities.items():
        print(f"{lang.upper()}: {caps['voice_count']} voices, Sanskrit: {caps['sanskrit_support']}")
    
    print("\nMultilingual voice support demo completed!")
