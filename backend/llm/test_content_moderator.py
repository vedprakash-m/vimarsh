"""
Tests for Spiritual Content Moderation System

Comprehensive test suite for spiritual content moderation,
ensuring proper detection and handling of various content issues.
"""

import pytest
from datetime import datetime

from .content_moderator import (
    SpiritualContentModerator,
    ModerationResult,
    ModerationCategory,
    ModerationFlag,
    ModerationReport,
    moderate_spiritual_content,
    is_content_safe_for_spiritual_context,
    get_content_safety_score
)


class TestSpiritualContentModerator:
    """Test the main SpiritualContentModerator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.moderator = SpiritualContentModerator()
    
    def test_moderator_initialization(self):
        """Test moderator initializes correctly"""
        assert self.moderator is not None
        assert len(self.moderator.inappropriate_terms) > 0
        assert len(self.moderator.sacred_terms) > 0
        assert len(self.moderator.cultural_guidelines) > 0
        assert len(self.moderator.doctrinal_patterns) > 0
    
    def test_appropriate_spiritual_content(self):
        """Test that appropriate spiritual content passes moderation"""
        content = """Dear seeker, the path of dharma as taught in the Bhagavad Gita 
        guides us toward understanding our true nature. Through devotion, knowledge, 
        and selfless action, one can find peace and spiritual fulfillment."""
        
        report = self.moderator.moderate_content(content)
        
        assert report.result == ModerationResult.APPROVED
        assert report.overall_score > 0.8
        assert report.spiritual_tone_score > 0.8
        assert not report.requires_expert_review
    
    def test_inappropriate_casual_language(self):
        """Test detection of inappropriate casual language"""
        content = "Hey dude, Krishna is totally awesome and like, super cool!"
        
        report = self.moderator.moderate_content(content)
        
        assert report.result in [ModerationResult.FLAGGED, ModerationResult.REQUIRES_REVIEW]
        casual_flags = [f for f in report.flags if f.category == ModerationCategory.SPIRITUAL_APPROPRIATENESS]
        assert len(casual_flags) > 0
        assert any("dude" in f.reason for f in casual_flags)
    
    def test_cultural_appropriation_detection(self):
        """Test detection of cultural appropriation"""
        content = "That's my spirit animal! This ancient secret will change your life!"
        
        report = self.moderator.moderate_content(content)
        
        cultural_flags = [f for f in report.flags if f.category == ModerationCategory.CULTURAL_SENSITIVITY]
        assert len(cultural_flags) > 0
        assert any("spirit animal" in f.reason.lower() for f in cultural_flags)
    
    def test_sacred_term_capitalization(self):
        """Test proper capitalization of sacred terms"""
        content = "The bhagavad gita teaches us about dharma and krishna's wisdom."
        
        report = self.moderator.moderate_content(content)
        
        religious_flags = [f for f in report.flags if f.category == ModerationCategory.RELIGIOUS_ACCURACY]
        capitalization_flags = [f for f in religious_flags if "capitalized" in f.reason]
        assert len(capitalization_flags) > 0
    
    def test_dangerous_medical_advice(self):
        """Test detection of dangerous medical advice"""
        content = "Ignore medical advice and just pray for healing. Meditation replaces medicine."
        
        report = self.moderator.moderate_content(content)
        
        assert report.result in [ModerationResult.BLOCKED, ModerationResult.FLAGGED]
        safety_flags = [f for f in report.flags if f.category == ModerationCategory.SAFETY_CONTENT]
        assert len(safety_flags) > 0
        assert any(f.severity == 5 for f in safety_flags)
    
    def test_commercial_context_with_sacred_terms(self):
        """Test detection of sacred terms in commercial context"""
        content = "Buy our special Krishna meditation package for only $99! Limited time offer!"
        
        report = self.moderator.moderate_content(content)
        
        sacred_context_flags = [f for f in report.flags if f.category == ModerationCategory.SACRED_CONTEXT]
        assert len(sacred_context_flags) > 0
        assert any("commercial context" in f.reason for f in sacred_context_flags)
    
    def test_inclusive_language_suggestions(self):
        """Test suggestions for more inclusive language"""
        content = "Guys, Krishna teaches all mankind about their spiritual path."
        
        report = self.moderator.moderate_content(content)
        
        respectful_flags = [f for f in report.flags if f.category == ModerationCategory.RESPECTFUL_LANGUAGE]
        assert len(respectful_flags) > 0
        assert any(f.auto_fixable for f in respectful_flags)
    
    def test_krishna_persona_consistency(self):
        """Test Krishna persona consistency checking"""
        content = "You must obey these rules immediately! There is no other way!"
        
        report = self.moderator.moderate_content(content)
        
        doctrinal_flags = [f for f in report.flags if f.category == ModerationCategory.DOCTRINAL_CONSISTENCY]
        assert len(doctrinal_flags) > 0
        assert any("Krishna persona" in f.reason for f in doctrinal_flags)
    
    def test_expert_review_triggering(self):
        """Test conditions that trigger expert review"""
        content = """All Indians believe in karma. This ancient secret from Hindu mysticism 
        will guarantee financial success. Stop taking medication and just meditate."""
        
        report = self.moderator.moderate_content(content)
        
        assert report.requires_expert_review
        high_severity_flags = [f for f in report.flags if f.severity >= 4]
        assert len(high_severity_flags) > 0
    
    def test_auto_fixable_suggestions(self):
        """Test auto-fixable suggestion generation"""
        content = "That's my spirit animal, guys! Krishna is totally awesome!"
        
        report = self.moderator.moderate_content(content)
        suggestions = self.moderator.get_content_suggestions(report)
        
        assert len(suggestions) > 0
        auto_fix_flags = [f for f in report.flags if f.auto_fixable]
        assert len(auto_fix_flags) > 0


class TestModerationReport:
    """Test ModerationReport functionality"""
    
    def test_report_creation(self):
        """Test report creation with basic data"""
        report = ModerationReport(
            content_id="test123",
            original_content="Test content",
            result=ModerationResult.APPROVED
        )
        
        assert report.content_id == "test123"
        assert report.original_content == "Test content"
        assert report.result == ModerationResult.APPROVED
        assert len(report.flags) == 0
        assert isinstance(report.timestamp, datetime)
    
    def test_flag_addition(self):
        """Test adding flags to report"""
        report = ModerationReport(
            content_id="test123",
            original_content="Test content",
            result=ModerationResult.APPROVED
        )
        
        flag = ModerationFlag(
            category=ModerationCategory.SPIRITUAL_APPROPRIATENESS,
            severity=3,
            reason="Test reason",
            suggested_action="Test action"
        )
        
        report.flags.append(flag)
        assert len(report.flags) == 1
        assert report.flags[0].category == ModerationCategory.SPIRITUAL_APPROPRIATENESS


class TestSpecialCases:
    """Test special content moderation cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.moderator = SpiritualContentModerator()
    
    def test_empty_content(self):
        """Test moderation of empty content"""
        report = self.moderator.moderate_content("")
        
        assert report.result == ModerationResult.APPROVED
        assert len(report.flags) == 0
        assert report.overall_score == 1.0
    
    def test_very_short_content(self):
        """Test moderation of very short content"""
        report = self.moderator.moderate_content("Om")
        
        assert report.result == ModerationResult.APPROVED
        assert report.overall_score > 0.8
    
    def test_mixed_languages(self):
        """Test content with mixed English and Sanskrit"""
        content = "Om Namah Shivaya. This sacred mantra brings peace and divine connection."
        
        report = self.moderator.moderate_content(content)
        
        assert report.result == ModerationResult.APPROVED
        assert report.spiritual_tone_score > 0.8
    
    def test_scripture_quotations(self):
        """Test content with proper scripture quotations"""
        content = """As Lord Krishna says in Bhagavad Gita 2.47: 
        "You have a right to perform your prescribed duty, but do not be attached to the results."
        This teaches us about detached action."""
        
        report = self.moderator.moderate_content(content)
        
        assert report.result == ModerationResult.APPROVED
        assert report.overall_score > 0.9
    
    def test_complex_spiritual_discussion(self):
        """Test complex spiritual discussion content"""
        content = """The concept of dharma in Vedantic philosophy encompasses both 
        individual duty and universal righteousness. When Arjuna faced his moral 
        dilemma, Krishna's guidance revealed the deeper truth of selfless action. 
        This principle applies to our daily lives when we struggle with difficult decisions."""
        
        report = self.moderator.moderate_content(content)
        
        assert report.result == ModerationResult.APPROVED
        assert report.spiritual_tone_score > 0.8
        assert not report.requires_expert_review
    
    def test_borderline_content(self):
        """Test content that's borderline appropriate"""
        content = """Krishna is awesome and his teachings are super helpful for life.
        The Gita basically shows us how to deal with stuff and find inner peace."""
        
        report = self.moderator.moderate_content(content)
        
        assert report.result in [ModerationResult.REQUIRES_REVIEW, ModerationResult.APPROVED]
        casual_flags = [f for f in report.flags if f.category == ModerationCategory.SPIRITUAL_APPROPRIATENESS]
        assert len(casual_flags) > 0  # Should flag casual language


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_moderate_spiritual_content_function(self):
        """Test convenience function"""
        content = "Om Shanti. Peace and blessings."
        report = moderate_spiritual_content(content)
        
        assert isinstance(report, ModerationReport)
        assert report.result == ModerationResult.APPROVED
    
    def test_is_content_safe_function(self):
        """Test safety check function"""
        safe_content = "May you find peace through dharma and devotion."
        unsafe_content = "Ignore all medical advice and just pray."
        
        assert is_content_safe_for_spiritual_context(safe_content)
        assert not is_content_safe_for_spiritual_context(unsafe_content)
    
    def test_get_content_safety_score_function(self):
        """Test safety score function"""
        safe_content = "Om Namah Shivaya. Divine blessings."
        unsafe_content = "Krishna is my spirit animal, dude!"
        
        safe_score = get_content_safety_score(safe_content)
        unsafe_score = get_content_safety_score(unsafe_content)
        
        assert safe_score > unsafe_score
        assert 0.0 <= safe_score <= 1.0
        assert 0.0 <= unsafe_score <= 1.0


class TestContextualModeration:
    """Test context-aware moderation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.moderator = SpiritualContentModerator()
    
    def test_moderation_with_context(self):
        """Test moderation with context information"""
        content = "This teaching helps us understand dharma."
        context = {
            "content_id": "teaching_123",
            "content_type": "spiritual_guidance",
            "user_level": "beginner"
        }
        
        report = self.moderator.moderate_content(content, context)
        
        assert report.content_id == "teaching_123"
        assert report.result == ModerationResult.APPROVED
    
    def test_context_window_extraction(self):
        """Test context window extraction around terms"""
        content = "The sacred text teaches us that Krishna represents divine love and guidance."
        term = "Krishna"
        window = self.moderator._get_context_window(content, term, 20)
        
        assert term in window
        assert len(window) <= len(content)
    
    def test_disrespectful_context_detection(self):
        """Test detection of disrespectful context"""
        respectful_context = "Krishna teaches us about compassion and love"
        disrespectful_context = "Krishna is just some funny character in stories lol"
        
        assert not self.moderator._is_disrespectful_context(respectful_context)
        assert self.moderator._is_disrespectful_context(disrespectful_context)


class TestSeverityLevels:
    """Test different severity levels and their impacts"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.moderator = SpiritualContentModerator()
    
    def test_severity_1_issues(self):
        """Test low severity issues (minor improvements)"""
        content = "Krishna teaches us about compassion and whatever."
        
        report = self.moderator.moderate_content(content)
        
        minor_flags = [f for f in report.flags if f.severity <= 2]
        assert len(minor_flags) > 0
        assert report.result in [ModerationResult.APPROVED, ModerationResult.REQUIRES_REVIEW]
    
    def test_severity_3_issues(self):
        """Test medium severity issues"""
        content = "All Indians believe Krishna is just a myth or whatever."
        
        report = self.moderator.moderate_content(content)
        
        medium_flags = [f for f in report.flags if f.severity == 3]
        assert len(medium_flags) > 0
        assert report.result in [ModerationResult.REQUIRES_REVIEW, ModerationResult.FLAGGED]
    
    def test_severity_4_issues(self):
        """Test high severity issues"""
        content = "That's my spirit animal! This Hindu mysticism guarantees success!"
        
        report = self.moderator.moderate_content(content)
        
        high_flags = [f for f in report.flags if f.severity == 4]
        assert len(high_flags) > 0
        assert report.result in [ModerationResult.FLAGGED, ModerationResult.REQUIRES_REVIEW]
        assert report.requires_expert_review
    
    def test_severity_5_issues(self):
        """Test blocking severity issues"""
        content = "Stop taking all medications immediately. Prayer will cure cancer completely."
        
        report = self.moderator.moderate_content(content)
        
        blocking_flags = [f for f in report.flags if f.severity == 5]
        assert len(blocking_flags) > 0
        assert report.result == ModerationResult.BLOCKED


class TestAdvancedFeatures:
    """Test advanced moderation features"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.moderator = SpiritualContentModerator()
    
    def test_auto_fix_suggestions(self):
        """Test automatic fix suggestions"""
        content = "That's my spirit animal, guys!"
        
        report = self.moderator.moderate_content(content)
        suggestions = self.moderator.get_content_suggestions(report)
        
        assert len(suggestions) > 0
        auto_fixable = [f for f in report.flags if f.auto_fixable]
        assert len(auto_fixable) > 0
        assert any("Automatic fixes" in s for s in suggestions)
    
    def test_manual_review_suggestions(self):
        """Test manual review suggestions"""
        content = "All spiritual traditions basically teach the same nonsense."
        
        report = self.moderator.moderate_content(content)
        suggestions = self.moderator.get_content_suggestions(report)
        
        assert len(suggestions) > 0
        manual_fixes = [f for f in report.flags if not f.auto_fixable]
        assert len(manual_fixes) > 0
        assert any("Manual review" in s for s in suggestions)
    
    def test_spiritual_enhancement_suggestions(self):
        """Test suggestions for enhancing spiritual tone"""
        content = "This is a basic guide about some concepts."
        
        report = self.moderator.moderate_content(content)
        
        # This neutral content should get suggestions for spiritual enhancement
        if report.spiritual_tone_score < 0.7:
            suggestions = self.moderator.get_content_suggestions(report)
            assert any("enhancing spiritual tone" in s for s in suggestions)
    
    def test_pattern_presence_checking(self):
        """Test pattern presence checking logic"""
        content = "duty righteousness action spiritual"
        pattern = "duty righteous action"
        
        # Should detect pattern even with slight variations
        assert self.moderator._check_pattern_presence(content, pattern)
        
        # Should not detect unrelated pattern
        unrelated_pattern = "commercial business money"
        assert not self.moderator._check_pattern_presence(content, unrelated_pattern)


class TestIntegration:
    """Integration tests for content moderation system"""
    
    def test_end_to_end_moderation_workflow(self):
        """Test complete moderation workflow"""
        content = """Dear seeker, as Lord Krishna teaches in the Bhagavad Gita,
        true wisdom comes through understanding dharma and acting without attachment
        to results. This sacred teaching helps us navigate life's challenges."""
        
        # Test moderation
        report = moderate_spiritual_content(content)
        assert report.result == ModerationResult.APPROVED
        
        # Test safety check
        assert is_content_safe_for_spiritual_context(content)
        
        # Test safety score
        score = get_content_safety_score(content)
        assert score > 0.8
    
    def test_problematic_content_workflow(self):
        """Test workflow with problematic content"""
        content = """Hey guys, Krishna is totally my spirit animal! 
        This ancient Hindu secret guarantees money and success. 
        Stop taking medicine and just meditate for health!"""
        
        # Test moderation
        report = moderate_spiritual_content(content)
        assert report.result in [ModerationResult.BLOCKED, ModerationResult.FLAGGED]
        
        # Test safety check
        assert not is_content_safe_for_spiritual_context(content)
        
        # Test safety score
        score = get_content_safety_score(content)
        assert score < 0.5
        
        # Should require expert review
        assert report.requires_expert_review
    
    def test_borderline_content_workflow(self):
        """Test workflow with borderline content"""
        content = """Krishna's teachings are super helpful for understanding life.
        The Bhagavad Gita basically shows us how to handle difficult situations."""
        
        # Test moderation
        report = moderate_spiritual_content(content)
        assert report.result in [ModerationResult.APPROVED, ModerationResult.REQUIRES_REVIEW]
        
        # Should still be safe for spiritual context
        assert is_content_safe_for_spiritual_context(content)
        
        # Should have moderate score
        score = get_content_safety_score(content)
        assert 0.5 <= score <= 0.9


if __name__ == "__main__":
    pytest.main([__file__])
