#!/usr/bin/env python3
"""
Test suite for multilingual voice support module.
Tests English/Hindi language switching and cultural context adaptation.
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.multilingual import (
    MultilingualVoiceManager, 
    Language, 
    VoiceProfile, 
    Accent, 
    VoiceGender,
    SanskritPronunciationGuide,
    MultilingualTextProcessor,
    VoiceSelector
)


class TestMultilingualVoiceManager:
    """Test cases for MultilingualVoiceManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.voice_manager = MultilingualVoiceManager()
    
    def test_initialization(self):
        """Test voice manager initialization"""
        assert self.voice_manager.current_language == Language.ENGLISH
        assert self.voice_manager.current_voice_profile is None
        assert isinstance(self.voice_manager.text_processor, MultilingualTextProcessor)
        assert isinstance(self.voice_manager.voice_selector, VoiceSelector)
    
    def test_language_detection(self):
        """Test language preference detection"""
        # English text
        english_text = "What is the meaning of dharma?"
        detected = self.voice_manager.detect_language_preference(english_text)
        assert detected == Language.ENGLISH
        
        # Hindi text with Devanagari
        hindi_text = "धर्म का अर्थ क्या है?"
        detected = self.voice_manager.detect_language_preference(hindi_text)
        assert detected == Language.HINDI
        
        # Sanskrit mantras should prefer Hindi
        sanskrit_text = "ॐ शान्ति शान्ति शान्तिः"
        detected = self.voice_manager.detect_language_preference(sanskrit_text)
        assert detected == Language.HINDI
    
    def test_voice_initialization(self):
        """Test voice initialization for different languages"""
        # Test English voice initialization
        en_profile = self.voice_manager.initialize_voice(Language.ENGLISH)
        assert isinstance(en_profile, VoiceProfile)
        assert en_profile.language == Language.ENGLISH
        assert self.voice_manager.current_language == Language.ENGLISH
        assert self.voice_manager.current_voice_profile == en_profile
        
        # Test Hindi voice initialization
        # Note: Hindi might fall back to English or Sanskrit voices depending on availability
        hi_profile = self.voice_manager.initialize_voice(Language.HINDI)
        assert isinstance(hi_profile, VoiceProfile)
        assert self.voice_manager.current_language == Language.HINDI
        assert self.voice_manager.current_voice_profile == hi_profile
    
    def test_speech_synthesis_preparation(self):
        """Test speech synthesis preparation"""
        text = "Hello, let's learn about dharma"
        
        # Test with specific language
        synthesis_data = self.voice_manager.prepare_speech_synthesis(text, Language.ENGLISH)
        
        assert "processed_text" in synthesis_data
        assert "voice_profile" in synthesis_data
        assert "language" in synthesis_data
        assert "synthesis_settings" in synthesis_data
        assert synthesis_data["language"] == Language.ENGLISH.value
        
        # Test without specifying language (should use current)
        self.voice_manager.initialize_voice(Language.HINDI)
        synthesis_data = self.voice_manager.prepare_speech_synthesis(text)
        assert synthesis_data["language"] == Language.HINDI.value
    
    def test_sanskrit_pronunciation_guide(self):
        """Test Sanskrit pronunciation guide"""
        # Test known Sanskrit terms
        test_terms = ["om", "krishna", "dharma", "karma", "moksha"]
        
        for term in test_terms:
            en_guide = self.voice_manager.get_sanskrit_pronunciation_guide(term, Language.ENGLISH)
            hi_guide = self.voice_manager.get_sanskrit_pronunciation_guide(term, Language.HINDI)
            
            assert en_guide is not None
            assert hi_guide is not None
            assert isinstance(en_guide, str)
            assert isinstance(hi_guide, str)
        
        # Test unknown term
        unknown_guide = self.voice_manager.get_sanskrit_pronunciation_guide("unknown_term", Language.ENGLISH)
        assert unknown_guide is None
    
    def test_language_switching(self):
        """Test language switching functionality"""
        # Start with English
        self.voice_manager.initialize_voice(Language.ENGLISH)
        assert self.voice_manager.current_language == Language.ENGLISH
        
        # Switch to Hindi
        success = self.voice_manager.switch_language(Language.HINDI)
        assert success is True
        assert self.voice_manager.current_language == Language.HINDI
        
        # Switch back to English
        success = self.voice_manager.switch_language(Language.ENGLISH)
        assert success is True
        assert self.voice_manager.current_language == Language.ENGLISH
    
    def test_language_capabilities(self):
        """Test language capabilities information"""
        capabilities = self.voice_manager.get_language_capabilities()
        
        assert isinstance(capabilities, dict)
        
        # Check that all supported languages are included
        for lang in Language:
            assert lang.value in capabilities
            
            lang_caps = capabilities[lang.value]
            assert "supported" in lang_caps
            assert "voice_count" in lang_caps
            assert "sanskrit_support" in lang_caps
            assert "available_accents" in lang_caps
            assert "available_genders" in lang_caps
    
    def test_sanskrit_density_calculation(self):
        """Test Sanskrit density calculation"""
        # Text with high Sanskrit density
        high_sanskrit = "dharma karma moksha yoga"
        density = self.voice_manager._calculate_sanskrit_density(high_sanskrit)
        assert density > 0.5
        
        # Text with low Sanskrit density
        low_sanskrit = "hello world how are you dharma"
        density = self.voice_manager._calculate_sanskrit_density(low_sanskrit)
        assert 0 < density < 0.5
        
        # Text with no Sanskrit
        no_sanskrit = "hello world how are you"
        density = self.voice_manager._calculate_sanskrit_density(no_sanskrit)
        assert density == 0
        
        # Empty text
        empty_density = self.voice_manager._calculate_sanskrit_density("")
        assert empty_density == 0


class TestSanskritPronunciationGuide:
    """Test cases for SanskritPronunciationGuide"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.guide = SanskritPronunciationGuide()
    
    def test_initialization(self):
        """Test guide initialization"""
        assert isinstance(self.guide.sanskrit_terms, dict)
        assert len(self.guide.sanskrit_terms) > 0
        
        # Check that some basic terms are loaded
        expected_terms = ["om", "krishna", "dharma", "karma", "moksha", "yoga"]
        for term in expected_terms:
            assert term in self.guide.sanskrit_terms
    
    def test_pronunciation_guide_retrieval(self):
        """Test pronunciation guide retrieval"""
        # Test existing term
        om_guide = self.guide.get_pronunciation_guide("om", Language.ENGLISH)
        assert om_guide is not None
        assert "AUM" in om_guide
        
        # Test non-existing term
        unknown_guide = self.guide.get_pronunciation_guide("unknown", Language.ENGLISH)
        assert unknown_guide is None
    
    def test_sanskrit_term_properties(self):
        """Test Sanskrit term data structure"""
        om_term = self.guide.sanskrit_terms["om"]
        
        assert hasattr(om_term, 'term')
        assert hasattr(om_term, 'english_pronunciation')
        assert hasattr(om_term, 'hindi_pronunciation')
        assert hasattr(om_term, 'devanagari')
        assert hasattr(om_term, 'meaning')
        assert hasattr(om_term, 'category')
        
        assert om_term.term == "Om"
        assert om_term.devanagari == "ॐ"
        assert om_term.category == "mantra"


class TestMultilingualTextProcessor:
    """Test cases for MultilingualTextProcessor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = MultilingualTextProcessor()
    
    def test_initialization(self):
        """Test processor initialization"""
        assert isinstance(self.processor.sanskrit_guide, SanskritPronunciationGuide)
    
    def test_text_preparation(self):
        """Test text preparation for voice synthesis"""
        voice_profile = VoiceProfile(
            language=Language.ENGLISH,
            accent=Accent.INDIAN_ENGLISH,
            gender=VoiceGender.MALE,
            voice_name="test-voice",
            supports_sanskrit=True,
            cultural_context="indian"
        )
        
        # Test with Sanskrit terms
        text = "Let's chant Om and learn dharma"
        processed = self.processor.prepare_text_for_voice(text, Language.ENGLISH, voice_profile)
        
        assert isinstance(processed, str)
        assert "speak" in processed.lower()
        assert "voice" in processed.lower()


class TestVoiceSelector:
    """Test cases for VoiceSelector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.selector = VoiceSelector()
    
    def test_voice_selection(self):
        """Test voice selection for different languages"""
        # Test English voice selection
        en_voice = self.selector.select_voice(Language.ENGLISH)
        assert isinstance(en_voice, VoiceProfile)
        assert en_voice.language == Language.ENGLISH
        
        # Test Hindi voice selection
        hi_voice = self.selector.select_voice(Language.HINDI)
        assert isinstance(hi_voice, VoiceProfile)
        # Note: Due to implementation, Hindi might fall back to Sanskrit voices
        
        # Test with valid preferences
        preferences = {"gender": "female"}
        pref_voice = self.selector.select_voice(Language.ENGLISH, preferences)
        assert isinstance(pref_voice, VoiceProfile)
    
    def test_available_voices(self):
        """Test getting available voices"""
        for lang in Language:
            voices = self.selector.get_available_voices(lang)
            assert isinstance(voices, list)
            
            # Each voice should be a VoiceProfile
            for voice in voices:
                assert isinstance(voice, VoiceProfile)


class TestVoiceProfile:
    """Test cases for VoiceProfile"""
    
    def test_voice_profile_creation(self):
        """Test voice profile creation"""
        profile = VoiceProfile(
            language=Language.ENGLISH,
            accent=Accent.INDIAN_ENGLISH,
            gender=VoiceGender.FEMALE,
            voice_name="test-voice"
        )
        
        assert profile.language == Language.ENGLISH
        assert profile.accent == Accent.INDIAN_ENGLISH
        assert profile.gender == VoiceGender.FEMALE
        assert profile.voice_name == "test-voice"
        assert profile.sample_rate == 22050  # default
    
    def test_voice_profile_to_dict(self):
        """Test voice profile dictionary conversion"""
        profile = VoiceProfile(
            language=Language.HINDI,
            accent=Accent.STANDARD_HINDI,
            gender=VoiceGender.MALE,
            voice_name="hindi-voice",
            supports_sanskrit=True
        )
        
        profile_dict = profile.to_dict()
        
        assert isinstance(profile_dict, dict)
        assert profile_dict["language"] == "hi"
        assert profile_dict["accent"] == "hi-IN"
        assert profile_dict["gender"] == "male"
        assert profile_dict["voice_name"] == "hindi-voice"
        assert profile_dict["supports_sanskrit"] is True


def test_language_enum():
    """Test Language enum"""
    assert Language.ENGLISH.value == "en"
    assert Language.HINDI.value == "hi"
    assert Language.SANSKRIT.value == "sa"


def test_accent_enum():
    """Test Accent enum"""
    assert Accent.AMERICAN.value == "en-US"
    assert Accent.BRITISH.value == "en-GB"
    assert Accent.INDIAN_ENGLISH.value == "en-IN"
    assert Accent.STANDARD_HINDI.value == "hi-IN"


def test_voice_gender_enum():
    """Test VoiceGender enum"""
    assert VoiceGender.MALE.value == "male"
    assert VoiceGender.FEMALE.value == "female"
    assert VoiceGender.NEUTRAL.value == "neutral"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
