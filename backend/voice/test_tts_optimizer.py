"""
Unit tests for TTS optimization for spiritual content delivery

This module tests the SpiritualTTSOptimizer functionality including
Sanskrit pronunciation, tone adjustment, and sacred content handling.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
import json
import tempfile
import os

from tts_optimizer import (
    SpiritualTTSOptimizer, 
    TTSConfig, 
    SpiritualTone,
    VoiceCharacteristic,
    SanskritPronunciation,
    TTSProcessingResult,
    create_spiritual_tts_optimizer
)


class TestTTSConfig:
    """Test TTS configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = TTSConfig()
        
        assert config.language == "en-US"
        assert config.voice_gender == "neutral"
        assert config.speaking_rate == 0.85
        assert config.spiritual_tone == SpiritualTone.WISE
        assert config.voice_characteristic == VoiceCharacteristic.WARM
        assert config.emphasize_sanskrit_terms is True
        assert config.reverent_deity_names is True
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = TTSConfig(
            language="en-IN",
            spiritual_tone=SpiritualTone.DEVOTIONAL,
            voice_characteristic=VoiceCharacteristic.GENTLE,
            speaking_rate=0.7,
            emphasize_sanskrit_terms=False
        )
        
        assert config.language == "en-IN"
        assert config.spiritual_tone == SpiritualTone.DEVOTIONAL
        assert config.voice_characteristic == VoiceCharacteristic.GENTLE
        assert config.speaking_rate == 0.7
        assert config.emphasize_sanskrit_terms is False


class TestSpiritualTTSOptimizer:
    """Test spiritual TTS optimizer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.optimizer = SpiritualTTSOptimizer()
    
    def test_initialization(self):
        """Test optimizer initialization"""
        assert self.optimizer.config is not None
        assert len(self.optimizer.spiritual_phrases) > 0
        assert len(self.optimizer.sanskrit_pronunciations) > 0
        assert len(self.optimizer.tone_patterns) > 0
        assert len(self.optimizer.deity_names) > 0
    
    def test_spiritual_content_detection(self):
        """Test spiritual content detection"""
        
        # Test with Sanskrit terms
        text = "Krishna teaches us about dharma and karma in the Bhagavad Gita"
        analysis = self.optimizer.detect_spiritual_content(text)
        
        assert len(analysis['sanskrit_terms']) >= 3  # krishna, dharma, karma
        assert len(analysis['deity_references']) >= 1  # krishna
        assert analysis['dominant_tone'] == SpiritualTone.DEVOTIONAL
        assert analysis['content_type'] == 'devotional'
    
    def test_mantra_detection(self):
        """Test mantra detection"""
        text = "Let us chant Om Namah Shivaya with devotion"
        analysis = self.optimizer.detect_spiritual_content(text)
        
        assert len(analysis['mantras']) >= 1
        assert analysis['dominant_tone'] == SpiritualTone.REVERENT
        assert analysis['content_type'] == 'mantra'
        assert analysis['reverence_level'] >= 0.8
    
    def test_citation_detection(self):
        """Test scriptural citation detection"""
        text = "As Krishna says in the Gita, we should perform our duty without attachment"
        analysis = self.optimizer.detect_spiritual_content(text)
        
        assert len(analysis['citations']) >= 1
        assert analysis['dominant_tone'] == SpiritualTone.WISE
        assert analysis['content_type'] == 'teaching'
    
    def test_ssml_generation(self):
        """Test SSML markup generation"""
        text = "Krishna teaches dharma"
        analysis = self.optimizer.detect_spiritual_content(text)
        ssml = self.optimizer.generate_ssml_markup(text, analysis)
        
        # Should contain SSML tags
        assert '<speak' in ssml
        assert '</speak>' in ssml
        
        # Should emphasize Sanskrit terms
        if self.optimizer.config.emphasize_sanskrit_terms:
            assert '<emphasis' in ssml
    
    def test_deity_name_reverence(self):
        """Test deity name handling with reverence"""
        text = "Lord Krishna is the supreme deity"
        analysis = self.optimizer.detect_spiritual_content(text)
        ssml = self.optimizer.generate_ssml_markup(text, analysis)
        
        if self.optimizer.config.reverent_deity_names:
            # Should contain pauses and emphasis for deity names
            assert '<break' in ssml
            assert '<emphasis' in ssml
    
    def test_mantra_special_handling(self):
        """Test special handling for mantras"""
        text = "Om Namah Shivaya is a powerful mantra"
        analysis = self.optimizer.detect_spiritual_content(text)
        ssml = self.optimizer.generate_ssml_markup(text, analysis)
        
        if self.optimizer.config.slower_for_mantras:
            # Should contain prosody adjustments for slower delivery
            assert 'rate=' in ssml or 'x-slow' in ssml
    
    def test_duration_estimation(self):
        """Test audio duration estimation"""
        text = "This is a test message with spiritual content about Krishna and dharma"
        analysis = self.optimizer.detect_spiritual_content(text)
        duration = self.optimizer.estimate_audio_duration(text, analysis)
        
        assert isinstance(duration, float)
        assert duration > 0
        assert duration < 60  # Should be reasonable for short text
    
    @pytest.mark.asyncio
    async def test_process_spiritual_content(self):
        """Test complete spiritual content processing"""
        text = "Krishna teaches us in the Bhagavad Gita that we should perform our dharma with devotion"
        
        result = await self.optimizer.process_spiritual_content(text)
        
        assert isinstance(result, TTSProcessingResult)
        assert result.original_text == text
        assert len(result.processed_text) > len(text)  # Should have SSML markup
        assert result.audio_duration_estimate > 0
        assert result.sanskrit_terms_count > 0
        assert result.processing_time_ms >= 0
        
        # Quality metrics should be calculated
        assert 0 <= result.readability_score <= 1
        assert 0 <= result.spiritual_appropriateness <= 1
        assert 0 <= result.pronunciation_accuracy <= 1
    
    def test_pronunciation_mapping(self):
        """Test Sanskrit pronunciation mappings"""
        
        # Test key terms
        assert 'krishna' in self.optimizer.sanskrit_pronunciations
        assert 'dharma' in self.optimizer.sanskrit_pronunciations
        assert 'karma' in self.optimizer.sanskrit_pronunciations
        assert 'om' in self.optimizer.sanskrit_pronunciations
        
        # Test pronunciation formats
        krishna_pronunciation = self.optimizer.sanskrit_pronunciations['krishna']
        assert 'KRISH' in krishna_pronunciation
    
    def test_tone_patterns(self):
        """Test spiritual tone patterns"""
        
        # Test all tones have patterns
        for tone in SpiritualTone:
            assert tone in self.optimizer.tone_patterns
            pattern = self.optimizer.tone_patterns[tone]
            
            # Should have required attributes
            assert 'speaking_rate' in pattern
            assert 'pitch_adjust' in pattern
            assert 'pause_multiplier' in pattern
    
    def test_error_handling(self):
        """Test error handling in processing"""
        
        # Test with potentially problematic input
        text = ""
        analysis = self.optimizer.detect_spiritual_content(text)
        
        # Should handle empty text gracefully
        assert isinstance(analysis, dict)
        assert 'sanskrit_terms' in analysis
    
    def test_statistics_tracking(self):
        """Test processing statistics"""
        
        initial_stats = self.optimizer.get_processing_statistics()
        assert 'total_processed' in initial_stats
        assert initial_stats['total_processed'] == 0
        
        # Process some content
        text = "Krishna teaches dharma"
        analysis = self.optimizer.detect_spiritual_content(text)
        
        # Statistics should still be accessible
        stats = self.optimizer.get_processing_statistics()
        assert isinstance(stats, dict)
    
    def test_config_update(self):
        """Test configuration updates"""
        
        new_config = TTSConfig(
            spiritual_tone=SpiritualTone.PEACEFUL,
            emphasize_sanskrit_terms=False
        )
        
        self.optimizer.update_config(new_config)
        assert self.optimizer.config.spiritual_tone == SpiritualTone.PEACEFUL
        assert self.optimizer.config.emphasize_sanskrit_terms is False
    
    def test_supported_options(self):
        """Test getting supported options"""
        
        tones = self.optimizer.get_supported_tones()
        assert len(tones) > 0
        assert 'wise' in tones
        
        characteristics = self.optimizer.get_supported_characteristics()
        assert len(characteristics) > 0
        assert 'warm' in characteristics


class TestToneSpecificProcessing:
    """Test tone-specific processing"""
    
    def test_reverent_tone(self):
        """Test reverent tone processing"""
        config = TTSConfig(spiritual_tone=SpiritualTone.REVERENT)
        optimizer = SpiritualTTSOptimizer(config)
        
        text = "Om Namah Shivaya"
        analysis = optimizer.detect_spiritual_content(text)
        ssml = optimizer.generate_ssml_markup(text, analysis)
        
        # Reverent tone should have slower rate
        tone_pattern = optimizer.tone_patterns[SpiritualTone.REVERENT]
        assert tone_pattern['speaking_rate'] < 0.8
    
    def test_joyful_tone(self):
        """Test joyful tone processing"""
        config = TTSConfig(spiritual_tone=SpiritualTone.JOYFUL)
        optimizer = SpiritualTTSOptimizer(config)
        
        text = "Hare Krishna brings joy"
        analysis = optimizer.detect_spiritual_content(text)
        ssml = optimizer.generate_ssml_markup(text, analysis)
        
        # Joyful tone should have higher pitch
        tone_pattern = optimizer.tone_patterns[SpiritualTone.JOYFUL]
        assert tone_pattern['pitch_adjust'] > 0
    
    def test_peaceful_tone(self):
        """Test peaceful tone processing"""
        config = TTSConfig(spiritual_tone=SpiritualTone.PEACEFUL)
        optimizer = SpiritualTTSOptimizer(config)
        
        text = "Find inner peace through meditation"
        analysis = optimizer.detect_spiritual_content(text)
        ssml = optimizer.generate_ssml_markup(text, analysis)
        
        # Peaceful tone should have longer pauses
        tone_pattern = optimizer.tone_patterns[SpiritualTone.PEACEFUL]
        assert tone_pattern['pause_multiplier'] > 1.3


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_create_spiritual_tts_optimizer(self):
        """Test convenience function for creating optimizer"""
        
        optimizer = create_spiritual_tts_optimizer(
            tone=SpiritualTone.DEVOTIONAL,
            characteristic=VoiceCharacteristic.GENTLE,
            language="en-IN"
        )
        
        assert isinstance(optimizer, SpiritualTTSOptimizer)
        assert optimizer.config.spiritual_tone == SpiritualTone.DEVOTIONAL
        assert optimizer.config.voice_characteristic == VoiceCharacteristic.GENTLE
        assert optimizer.config.language == "en-IN"


class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.optimizer = SpiritualTTSOptimizer()
    
    @pytest.mark.asyncio
    async def test_bhagavad_gita_quote(self):
        """Test processing of Bhagavad Gita quote"""
        
        text = """Krishna says in the Bhagavad Gita: "You have the right to perform 
        your prescribed duty, but you are not entitled to the fruits of your actions. 
        Never consider yourself to be the cause of the results of your activities, 
        nor be attached to inaction." This teaches us about dharma and karma."""
        
        result = await self.optimizer.process_spiritual_content(text)
        
        assert result.sanskrit_terms_count >= 3  # krishna, dharma, karma
        assert result.spiritual_appropriateness > 0.7
        assert '<speak' in result.processed_text
        assert result.audio_duration_estimate > 10  # Longer text
    
    @pytest.mark.asyncio
    async def test_mantra_chanting_guide(self):
        """Test mantra chanting guidance"""
        
        text = """Begin by chanting Om three times slowly. Then repeat the sacred 
        mantra Om Namah Shivaya with devotion. Feel the vibration of each syllable 
        resonating within your being. Om Shanti Shanti Shanti."""
        
        result = await self.optimizer.process_spiritual_content(text)
        
        assert result.sanskrit_terms_count >= 5
        assert 'mantra' in result.processed_text.lower()
        assert result.spiritual_appropriateness > 0.8
        
        # Should detect multiple mantras
        analysis = self.optimizer.detect_spiritual_content(text)
        assert len(analysis['mantras']) >= 2
    
    @pytest.mark.asyncio
    async def test_philosophical_discourse(self):
        """Test philosophical discourse processing"""
        
        text = """The concept of dharma encompasses righteous living and moral duty. 
        When we align our actions with dharma, we create positive karma. This path 
        leads to moksha, the ultimate liberation from the cycle of samsara. 
        Such wisdom comes from understanding our true nature as atman."""
        
        result = await self.optimizer.process_spiritual_content(text)
        
        assert result.sanskrit_terms_count >= 5
        assert result.readability_score > 0.5
        
        # Should be detected as philosophical content
        analysis = self.optimizer.detect_spiritual_content(text)
        assert analysis['content_type'] == 'philosophical'
        assert analysis['dominant_tone'] == SpiritualTone.CONTEMPLATIVE


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
