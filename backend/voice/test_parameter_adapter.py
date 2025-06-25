"""
Tests for Voice Parameter Adaptation System
"""

import pytest
from voice.parameter_adapter import (
    VoiceParameterAdapter,
    ContentAnalyzer,
    VoiceSettings,
    ContentType,
    ContentAnalysis,
    adapt_voice_for_content,
    analyze_spiritual_content,
    preview_voice_adaptation
)


class TestVoiceSettings:
    """Test VoiceSettings dataclass"""
    
    def test_voice_settings_creation(self):
        """Test creating VoiceSettings"""
        settings = VoiceSettings(
            speed=0.8,
            pitch=1.1,
            volume=0.9,
            pause_duration=1.5,
            emphasis_strength=1.2,
            reverence_level=1.8
        )
        
        assert settings.speed == 0.8
        assert settings.pitch == 1.1
        assert settings.reverence_level == 1.8
    
    def test_voice_settings_to_dict(self):
        """Test converting VoiceSettings to dictionary"""
        settings = VoiceSettings(speed=0.8, pitch=1.1)
        settings_dict = settings.to_dict()
        
        assert isinstance(settings_dict, dict)
        assert settings_dict['speed'] == 0.8
        assert settings_dict['pitch'] == 1.1
        assert 'reverence_level' in settings_dict
    
    def test_voice_settings_copy(self):
        """Test copying VoiceSettings"""
        original = VoiceSettings(speed=0.8, pitch=1.1, reverence_level=1.5)
        copy = original.copy()
        
        assert copy.speed == original.speed
        assert copy.pitch == original.pitch
        assert copy.reverence_level == original.reverence_level
        
        # Ensure it's a different object
        copy.speed = 1.0
        assert original.speed == 0.8  # Original unchanged


class TestContentAnalyzer:
    """Test ContentAnalyzer functionality"""
    
    def setUp(self):
        self.analyzer = ContentAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test ContentAnalyzer initialization"""
        analyzer = ContentAnalyzer()
        assert analyzer.content_patterns is not None
        assert analyzer.sacred_terms is not None
        assert analyzer.emotional_indicators is not None
    
    def test_scripture_quote_detection(self):
        """Test detection of scripture quotes"""
        analyzer = ContentAnalyzer()
        content = 'As Lord Krishna says in Bhagavad Gita 2.47: "You have the right to action, but not to the fruits of action."'
        
        analysis = analyzer.analyze_content(content)
        
        assert analysis.content_type == ContentType.SCRIPTURE_QUOTE
        assert analysis.confidence > 0.0
        assert analysis.contains_citations
        assert "krishna" in analysis.sacred_terms
    
    def test_personal_guidance_detection(self):
        """Test detection of personal guidance"""
        analyzer = ContentAnalyzer()
        content = "My dear child, I understand your struggles. Let me guide you through this difficult time."
        
        analysis = analyzer.analyze_content(content)
        
        assert analysis.content_type == ContentType.PERSONAL_GUIDANCE
        assert analysis.emotional_tone == "compassionate"
    
    def test_meditation_instruction_detection(self):
        """Test detection of meditation instructions"""
        analyzer = ContentAnalyzer()
        content = "Close your eyes, breathe deeply, and focus on the divine presence within. Let Om resonate."
        
        analysis = analyzer.analyze_content(content)
        
        assert analysis.content_type == ContentType.PRAYER_MEDITATION
        assert analysis.contains_sanskrit
        assert "om" in analysis.sacred_terms
    
    def test_philosophical_content_detection(self):
        """Test detection of philosophical content"""
        analyzer = ContentAnalyzer()
        content = "The nature of consciousness and its relationship to ultimate reality is profound."
        
        analysis = analyzer.analyze_content(content)
        
        assert analysis.content_type == ContentType.PHILOSOPHICAL_TEACHING
        assert analysis.complexity_level == "complex"
    
    def test_consolation_detection(self):
        """Test detection of consolation content"""
        analyzer = ContentAnalyzer()
        content = "Do not worry, beloved devotee. This suffering is temporary."
        
        analysis = analyzer.analyze_content(content)
        
        assert analysis.content_type == ContentType.CONSOLATION_COMFORT
        assert analysis.emotional_tone == "consoling"
    
    def test_length_categorization(self):
        """Test content length categorization"""
        analyzer = ContentAnalyzer()
        
        short_content = "Short message"
        medium_content = "This is a medium length message with several words to reach the threshold"
        long_content = "This is a long content message that contains many words and sentences to ensure it gets categorized as long content. " * 5
        
        short_analysis = analyzer.analyze_content(short_content)
        medium_analysis = analyzer.analyze_content(medium_content)
        long_analysis = analyzer.analyze_content(long_content)
        
        assert short_analysis.length_category == "short"
        assert medium_analysis.length_category == "medium"
        assert long_analysis.length_category == "long"
    
    def test_complexity_assessment(self):
        """Test complexity level assessment"""
        analyzer = ContentAnalyzer()
        
        simple_content = "Krishna loves all beings"
        complex_content = "The transcendental consciousness reveals the ultimate metaphysical reality"
        
        simple_analysis = analyzer.analyze_content(simple_content)
        complex_analysis = analyzer.analyze_content(complex_content)
        
        assert simple_analysis.complexity_level in ["simple", "medium"]
        assert complex_analysis.complexity_level == "complex"
    
    def test_sanskrit_detection(self):
        """Test Sanskrit term detection"""
        analyzer = ContentAnalyzer()
        
        content_with_sanskrit = "Dharma and karma guide our spiritual journey"
        content_without_sanskrit = "Love and compassion guide our journey"
        
        sanskrit_analysis = analyzer.analyze_content(content_with_sanskrit)
        no_sanskrit_analysis = analyzer.analyze_content(content_without_sanskrit)
        
        assert sanskrit_analysis.contains_sanskrit
        assert not no_sanskrit_analysis.contains_sanskrit
    
    def test_citation_detection(self):
        """Test citation detection"""
        analyzer = ContentAnalyzer()
        
        content_with_citation = "According to Bhagavad Gita 2.47, we have duties to perform"
        content_without_citation = "We have duties to perform in life"
        
        citation_analysis = analyzer.analyze_content(content_with_citation)
        no_citation_analysis = analyzer.analyze_content(content_without_citation)
        
        assert citation_analysis.contains_citations
        assert not no_citation_analysis.contains_citations


class TestVoiceParameterAdapter:
    """Test VoiceParameterAdapter functionality"""
    
    def test_adapter_initialization(self):
        """Test VoiceParameterAdapter initialization"""
        adapter = VoiceParameterAdapter()
        assert adapter.analyzer is not None
        assert adapter.parameter_templates is not None
        assert len(adapter.parameter_templates) == len(ContentType)
    
    def test_scripture_quote_adaptation(self):
        """Test voice adaptation for scripture quotes"""
        adapter = VoiceParameterAdapter()
        content = 'As Krishna says in Gita 2.47: "You have the right to action."'
        
        settings = adapter.adapt_parameters(content)
        
        # Scripture quotes should be slower and more reverent
        assert settings.speed < 1.0
        assert settings.reverence_level > 1.5
        assert settings.pause_duration > 1.0
        assert settings.pre_pause > 0.0
    
    def test_meditation_adaptation(self):
        """Test voice adaptation for meditation content"""
        adapter = VoiceParameterAdapter()
        content = "Close your eyes and breathe deeply. Focus on Om."
        
        settings = adapter.adapt_parameters(content)
        
        # Meditation should be very slow and peaceful
        assert settings.speed < 0.8
        assert settings.pause_duration > 1.5
        assert settings.reverence_level > 1.5
    
    def test_personal_guidance_adaptation(self):
        """Test voice adaptation for personal guidance"""
        adapter = VoiceParameterAdapter()
        content = "My dear child, I understand your struggles."
        
        settings = adapter.adapt_parameters(content)
        
        # Personal guidance should be warm and gentle
        assert settings.pitch >= 1.0  # Warmer pitch
        assert settings.volume <= 1.0  # Softer volume
        assert settings.emphasis_strength >= 1.0
    
    def test_sanskrit_content_adaptation(self):
        """Test adaptation for content with Sanskrit terms"""
        adapter = VoiceParameterAdapter()
        content_with_sanskrit = "Dharma and karma guide our spiritual journey through samsara to moksha."
        content_without_sanskrit = "Duty and action guide our spiritual journey to liberation."
        
        sanskrit_settings = adapter.adapt_parameters(content_with_sanskrit)
        regular_settings = adapter.adapt_parameters(content_without_sanskrit)
        
        # Sanskrit content should be slower and more emphasized
        assert sanskrit_settings.speed < regular_settings.speed
        assert sanskrit_settings.emphasis_strength > regular_settings.emphasis_strength
    
    def test_user_preferences_application(self):
        """Test application of user preferences"""
        adapter = VoiceParameterAdapter()
        content = "Regular spiritual guidance content"
        
        preferences = {
            "speed_preference": 0.8,
            "volume_preference": 1.2,
            "pause_preference": 1.5
        }
        
        settings = adapter.adapt_parameters(content, preferences)
        
        # User preferences should be applied
        assert settings.speed <= 1.0  # Should be affected by speed preference
        assert settings.volume >= 1.0  # Should be affected by volume preference
    
    def test_accessibility_mode(self):
        """Test accessibility mode adjustments"""
        adapter = VoiceParameterAdapter()
        content = "Spiritual guidance for accessibility"
        
        preferences = {"accessibility_mode": True}
        
        settings = adapter.adapt_parameters(content, preferences)
        
        # Accessibility mode should be slower, louder, with longer pauses
        assert settings.speed <= 1.0
        assert settings.volume >= 1.0
        assert settings.pause_duration >= 1.0
    
    def test_content_analysis_method(self):
        """Test get_content_analysis method"""
        adapter = VoiceParameterAdapter()
        content = "Krishna teaches us about dharma"
        
        analysis = adapter.get_content_analysis(content)
        
        assert isinstance(analysis, ContentAnalysis)
        assert analysis.content_type is not None
        assert isinstance(analysis.confidence, float)
    
    def test_preview_voice_settings(self):
        """Test preview_voice_settings method"""
        adapter = VoiceParameterAdapter()
        content = "My dear child, follow the path of dharma"
        
        preview = adapter.preview_voice_settings(content)
        
        assert "content_analysis" in preview
        assert "voice_settings" in preview
        assert "recommendations" in preview
        
        assert isinstance(preview["content_analysis"], dict)
        assert isinstance(preview["voice_settings"], dict)
        assert isinstance(preview["recommendations"], list)


class TestParameterTemplates:
    """Test parameter templates for different content types"""
    
    def test_all_content_types_have_templates(self):
        """Test that all content types have parameter templates"""
        adapter = VoiceParameterAdapter()
        
        for content_type in ContentType:
            assert content_type in adapter.parameter_templates
    
    def test_scripture_quote_template(self):
        """Test scripture quote template characteristics"""
        adapter = VoiceParameterAdapter()
        template = adapter.parameter_templates[ContentType.SCRIPTURE_QUOTE]
        
        assert template.speed < 1.0  # Should be slower
        assert template.reverence_level > 1.5  # Should be very reverent
        assert template.pause_duration > 1.0  # Should have longer pauses
    
    def test_meditation_template(self):
        """Test meditation template characteristics"""
        adapter = VoiceParameterAdapter()
        template = adapter.parameter_templates[ContentType.PRAYER_MEDITATION]
        
        assert template.speed < 0.8  # Should be very slow
        assert template.pause_duration > 1.5  # Should have long pauses
        assert template.volume < 1.0  # Should be quieter
    
    def test_casual_conversation_template(self):
        """Test casual conversation template (baseline)"""
        adapter = VoiceParameterAdapter()
        template = adapter.parameter_templates[ContentType.CASUAL_CONVERSATION]
        
        # Should be close to normal values
        assert template.speed == 1.0
        assert template.pitch == 1.0
        assert template.volume == 1.0
        assert template.reverence_level == 1.0


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_adapt_voice_for_content_function(self):
        """Test adapt_voice_for_content utility function"""
        content = "Krishna teaches us about dharma"
        settings = adapt_voice_for_content(content)
        
        assert isinstance(settings, VoiceSettings)
        assert settings.speed > 0
        assert settings.pitch > 0
    
    def test_analyze_spiritual_content_function(self):
        """Test analyze_spiritual_content utility function"""
        content = "My dear child, follow the path of righteousness"
        analysis = analyze_spiritual_content(content)
        
        assert isinstance(analysis, ContentAnalysis)
        assert analysis.content_type is not None
    
    def test_preview_voice_adaptation_function(self):
        """Test preview_voice_adaptation utility function"""
        content = "Sacred Om mantra chanting"
        preview = preview_voice_adaptation(content)
        
        assert isinstance(preview, dict)
        assert "content_analysis" in preview
        assert "voice_settings" in preview
        assert "recommendations" in preview


class TestIntegration:
    """Integration tests for voice parameter adaptation"""
    
    def test_complete_adaptation_workflow(self):
        """Test complete adaptation workflow"""
        adapter = VoiceParameterAdapter()
        
        # Test different types of content
        test_cases = [
            ('As Krishna says: "Perform your duty"', ContentType.SCRIPTURE_QUOTE),
            ("My dear child, find peace", ContentType.PERSONAL_GUIDANCE),
            ("Close your eyes and meditate", ContentType.PRAYER_MEDITATION),
            ("The nature of consciousness", ContentType.PHILOSOPHICAL_TEACHING)
        ]
        
        for content, expected_type in test_cases:
            settings = adapter.adapt_parameters(content)
            analysis = adapter.get_content_analysis(content)
            
            assert analysis.content_type == expected_type
            assert isinstance(settings, VoiceSettings)
            assert settings.speed > 0
            assert settings.reverence_level > 0
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        adapter = VoiceParameterAdapter()
        
        # Empty content
        empty_settings = adapter.adapt_parameters("")
        assert isinstance(empty_settings, VoiceSettings)
        
        # Very short content
        short_settings = adapter.adapt_parameters("Om")
        assert isinstance(short_settings, VoiceSettings)
        
        # Very long content
        long_content = "Krishna teaches us about dharma. " * 100
        long_settings = adapter.adapt_parameters(long_content)
        assert isinstance(long_settings, VoiceSettings)
    
    def test_consistency_across_calls(self):
        """Test that adaptation is consistent across multiple calls"""
        adapter = VoiceParameterAdapter()
        content = "Krishna teaches us about dharma and karma"
        
        settings1 = adapter.adapt_parameters(content)
        settings2 = adapter.adapt_parameters(content)
        
        assert settings1.speed == settings2.speed
        assert settings1.pitch == settings2.pitch
        assert settings1.reverence_level == settings2.reverence_level


if __name__ == "__main__":
    pytest.main([__file__])
