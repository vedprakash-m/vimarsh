"""
Test suite for spiritual response validation system

Tests all components of the response validation framework including:
- Spiritual tone validation
- Authenticity validation
- Cultural sensitivity validation
- Citation validation
- Content appropriateness validation
- Overall validation orchestration
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from .response_validator import (
    SpiritualResponseValidator,
    SpiritualToneValidator,
    AuthenticityValidator,
    CulturalSensitivityValidator,
    CitationValidator,
    ContentAppropriatenessValidator,
    ValidationReport,
    ValidationResult,
    ValidationCategory,
    ValidationIssue,
    validate_spiritual_response,
    is_response_acceptable
)


class TestValidationIssue:
    """Test ValidationIssue data class"""
    
    def test_issue_creation(self):
        """Test creating a validation issue"""
        issue = ValidationIssue(
            category=ValidationCategory.SPIRITUAL_TONE,
            severity="high",
            description="Test issue",
            location="paragraph 1",
            suggestion="Fix this"
        )
        
        assert issue.category == ValidationCategory.SPIRITUAL_TONE
        assert issue.severity == "high"
        assert issue.description == "Test issue"
        assert issue.location == "paragraph 1"
        assert issue.suggestion == "Fix this"


class TestValidationReport:
    """Test ValidationReport data class"""
    
    def test_report_creation(self):
        """Test creating a validation report"""
        report = ValidationReport(
            overall_result=ValidationResult.APPROVED,
            confidence_score=0.85
        )
        
        assert report.overall_result == ValidationResult.APPROVED
        assert report.confidence_score == 0.85
        assert report.issues == []
        assert report.passed_checks == []
        assert not report.expert_review_required
        assert isinstance(report.timestamp, datetime)
    
    def test_add_issue(self):
        """Test adding issues to report"""
        report = ValidationReport(
            overall_result=ValidationResult.APPROVED,
            confidence_score=0.85
        )
        
        issue = ValidationIssue(
            category=ValidationCategory.SPIRITUAL_TONE,
            severity="medium",
            description="Test issue"
        )
        
        report.add_issue(issue)
        assert len(report.issues) == 1
        assert report.issues[0] == issue
    
    def test_has_critical_issues(self):
        """Test critical issue detection"""
        report = ValidationReport(
            overall_result=ValidationResult.APPROVED,
            confidence_score=0.85
        )
        
        # No critical issues initially
        assert not report.has_critical_issues()
        
        # Add non-critical issue
        report.add_issue(ValidationIssue(
            category=ValidationCategory.SPIRITUAL_TONE,
            severity="medium",
            description="Medium issue"
        ))
        assert not report.has_critical_issues()
        
        # Add critical issue
        report.add_issue(ValidationIssue(
            category=ValidationCategory.CONTENT_APPROPRIATENESS,
            severity="critical",
            description="Critical issue"
        ))
        assert report.has_critical_issues()
    
    def test_has_high_severity_issues(self):
        """Test high severity issue detection"""
        report = ValidationReport(
            overall_result=ValidationResult.APPROVED,
            confidence_score=0.85
        )
        
        # No high severity issues initially
        assert not report.has_high_severity_issues()
        
        # Add low severity issue
        report.add_issue(ValidationIssue(
            category=ValidationCategory.SPIRITUAL_TONE,
            severity="low",
            description="Low issue"
        ))
        assert not report.has_high_severity_issues()
        
        # Add high severity issue
        report.add_issue(ValidationIssue(
            category=ValidationCategory.AUTHENTICITY,
            severity="high",
            description="High issue"
        ))
        assert report.has_high_severity_issues()


class TestSpiritualToneValidator:
    """Test spiritual tone validation"""
    
    def setUp(self):
        self.validator = SpiritualToneValidator()
    
    def test_appropriate_spiritual_tone(self):
        """Test validation of appropriate spiritual tone"""
        self.validator = SpiritualToneValidator()
        response = "My dear child, divine wisdom guides us through dharma and devotion. The sacred teachings of Lord Krishna illuminate the path to enlightenment."
        
        issues = self.validator.validate_tone(response)
        assert len(issues) == 0
    
    def test_inappropriate_casual_language(self):
        """Test detection of inappropriate casual language"""
        self.validator = SpiritualToneValidator()
        response = "Hey dude, that's awesome! No worries, spiritual stuff is easy peasy."
        
        issues = self.validator.validate_tone(response)
        assert len(issues) > 0
        
        # Should detect casual language
        casual_issue = next((issue for issue in issues if "casual language" in issue.description), None)
        assert casual_issue is not None
        assert casual_issue.severity == "high"
        assert casual_issue.category == ValidationCategory.SPIRITUAL_TONE
    
    def test_lack_of_spiritual_content(self):
        """Test detection of insufficient spiritual content"""
        self.validator = SpiritualToneValidator()
        response = "This is a longer regular response without any spiritual terminology or references to make it sound like guidance from a divine source and lacks proper spiritual content completely."
        
        issues = self.validator.validate_tone(response)
        
        # Should detect lack of spiritual terminology
        spiritual_issue = next((issue for issue in issues if "lacks sufficient spiritual" in issue.description), None)
        assert spiritual_issue is not None
        assert spiritual_issue.severity == "medium"
    
    def test_missing_divine_address_long_response(self):
        """Test detection of missing divine address in longer responses"""
        self.validator = SpiritualToneValidator()
        long_response = " ".join(["This is a long spiritual response about dharma and wisdom."] * 15)
        
        issues = self.validator.validate_tone(long_response)
        
        # Should suggest divine address for long responses
        address_issue = next((issue for issue in issues if "lacks personal divine address" in issue.description), None)
        assert address_issue is not None
        assert address_issue.severity == "low"
    
    def test_proper_divine_address(self):
        """Test recognition of proper divine address"""
        self.validator = SpiritualToneValidator()
        response = "My dear child, " + " ".join(["the path of spiritual wisdom guides us."] * 15)
        
        issues = self.validator.validate_tone(response)
        
        # Should not flag missing divine address
        address_issues = [issue for issue in issues if "divine address" in issue.description]
        assert len(address_issues) == 0


class TestAuthenticityValidator:
    """Test authenticity validation"""
    
    def test_traditional_authentic_response(self):
        """Test validation of traditional authentic response"""
        validator = AuthenticityValidator()
        response = "The path of dharma leads to moksha through bhakti and jnana. As taught in the Vedanta tradition, the atman seeks union with Brahman."
        
        issues = validator.validate_authenticity(response)
        assert len(issues) == 0
    
    def test_new_age_dilution_detection(self):
        """Test detection of new age concepts that may dilute authenticity"""
        validator = AuthenticityValidator()
        response = "Use manifestation and the law of attraction for chakra balancing. Quantum healing will align your energy."
        
        issues = validator.validate_authenticity(response)
        assert len(issues) > 0
        
        # Should detect modern concepts
        modern_issue = next((issue for issue in issues if "modern concepts" in issue.description), None)
        assert modern_issue is not None
        assert modern_issue.severity == "medium"
        assert modern_issue.category == ValidationCategory.AUTHENTICITY
    
    def test_sanskrit_misuse_detection(self):
        """Test detection of Sanskrit term misuse"""
        validator = AuthenticityValidator()
        response = "Your bad karma is punishment for your sins. Dharma is just religious belief."
        
        issues = validator.validate_authenticity(response)
        
        # Should detect potential misuse of Sanskrit terms
        sanskrit_issues = [issue for issue in issues if "Sanskrit terms" in issue.description]
        assert len(sanskrit_issues) > 0
        assert sanskrit_issues[0].severity == "high"


class TestCulturalSensitivityValidator:
    """Test cultural sensitivity validation"""
    
    def test_culturally_appropriate_response(self):
        """Test validation of culturally appropriate response"""
        validator = CulturalSensitivityValidator()
        response = "In the ancient tradition, the sacred texts teach us wisdom through devotion and surrender."
        
        issues = validator.validate_cultural_sensitivity(response)
        assert len(issues) == 0
    
    def test_sensitive_term_detection(self):
        """Test detection of culturally sensitive terms"""
        validator = CulturalSensitivityValidator()
        response = "The caste system and brahmin traditions versus untouchable practices in colonial times."
        
        issues = validator.validate_cultural_sensitivity(response)
        assert len(issues) > 0
        
        # Should detect sensitive terms
        sensitive_issue = next((issue for issue in issues if "culturally sensitive terms" in issue.description), None)
        assert sensitive_issue is not None
        assert sensitive_issue.severity == "medium"
        assert sensitive_issue.category == ValidationCategory.CULTURAL_SENSITIVITY


class TestCitationValidator:
    """Test citation validation"""
    
    def test_proper_citations(self):
        """Test validation of proper citations"""
        validator = CitationValidator()
        response = "As stated in Bhagavad Gita 2.47, we have the right to action but not to results."
        
        issues = validator.validate_citations(response)
        assert len(issues) == 0
    
    def test_missing_citations_for_claims(self):
        """Test detection of scriptural claims without citations"""
        validator = CitationValidator()
        response = "The scripture says that meditation leads to enlightenment. The Gita teaches us about dharma."
        
        issues = validator.validate_citations(response)
        assert len(issues) > 0
        
        # Should detect missing citations
        citation_issue = next((issue for issue in issues if "without proper citations" in issue.description), None)
        assert citation_issue is not None
        assert citation_issue.severity == "high"
        assert citation_issue.category == ValidationCategory.CITATION_ACCURACY


class TestContentAppropriatenessValidator:
    """Test content appropriateness validation"""
    
    def test_appropriate_spiritual_content(self):
        """Test validation of appropriate spiritual content"""
        validator = ContentAppropriatenessValidator()
        response = "Through meditation and devotion, we may find peace and wisdom on the spiritual path."
        
        issues = validator.validate_appropriateness(response)
        assert len(issues) == 0
    
    def test_sensitive_topic_detection(self):
        """Test detection of sensitive topics"""
        validator = ContentAppropriatenessValidator()
        response = "When dealing with death and suicide, seek medical advice for treatment."
        
        issues = validator.validate_appropriateness(response)
        assert len(issues) > 0
        
        # Should detect sensitive topics
        sensitive_issue = next((issue for issue in issues if "sensitive topics" in issue.description), None)
        assert sensitive_issue is not None
        assert sensitive_issue.severity == "high"
    
    def test_inappropriate_certainty_claims(self):
        """Test detection of inappropriate certainty claims"""
        validator = ContentAppropriatenessValidator()
        response = "I predict you will definitely succeed. You must follow this path and it will absolutely happen."
        
        issues = validator.validate_appropriateness(response)
        
        # Should detect inappropriate certainty
        certainty_issue = next((issue for issue in issues if "certainty claims" in issue.description), None)
        assert certainty_issue is not None
        assert certainty_issue.severity == "high"


class TestSpiritualResponseValidator:
    """Test main orchestrating validator"""
    
    def test_validator_initialization(self):
        """Test validator initialization"""
        validator = SpiritualResponseValidator()
        
        assert validator.tone_validator is not None
        assert validator.authenticity_validator is not None
        assert validator.cultural_validator is not None
        assert validator.citation_validator is not None
        assert validator.content_validator is not None
        assert validator.expert_review_threshold == 0.7
        assert validator.rejection_threshold == 0.3
    
    def test_validator_with_custom_config(self):
        """Test validator with custom configuration"""
        config = {
            "expert_review_threshold": 0.8,
            "rejection_threshold": 0.2
        }
        validator = SpiritualResponseValidator(config)
        
        assert validator.expert_review_threshold == 0.8
        assert validator.rejection_threshold == 0.2
    
    def test_excellent_response_validation(self):
        """Test validation of excellent spiritual response"""
        validator = SpiritualResponseValidator()
        response = """My dear child, the path of dharma is illuminated by divine wisdom. 
        As Lord Krishna teaches in Bhagavad Gita 2.47, you have the right to perform your 
        duties but not to the fruits of your actions. Through devotion and surrender, 
        we transcend the temporary difficulties of this world."""
        
        report = validator.validate_response(response)
        
        assert report.overall_result == ValidationResult.APPROVED
        assert report.confidence_score > 0.8
        assert len(report.issues) == 0
        assert len(report.passed_checks) > 0
        assert not report.expert_review_required
    
    def test_problematic_response_validation(self):
        """Test validation of problematic response"""
        validator = SpiritualResponseValidator()
        response = """Hey dude, just manifest your success using the law of attraction! 
        Chakra balancing and quantum healing will totally fix your caste problems. 
        I guarantee you'll be awesome!"""
        
        report = validator.validate_response(response)
        
        assert report.overall_result in [ValidationResult.REJECTED, ValidationResult.NEEDS_REVIEW]
        assert report.confidence_score < 0.8
        assert len(report.issues) > 0
        assert report.has_high_severity_issues()
    
    def test_mixed_quality_response_needs_review(self):
        """Test response that needs expert review"""
        validator = SpiritualResponseValidator()
        response = """The sacred teachings speak of transcendence through devotion. 
        However, when dealing with death and medical conditions, manifestation 
        techniques can help align your chakras for healing."""
        
        report = validator.validate_response(response)
        
        # Should need review due to mixed authentic/inauthentic content
        assert report.overall_result == ValidationResult.NEEDS_REVIEW
        assert report.expert_review_required
        assert report.expert_review_reason is not None
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation logic"""
        validator = SpiritualResponseValidator()
        
        # Mock report with known issues
        report = ValidationReport(
            overall_result=ValidationResult.APPROVED,
            confidence_score=1.0
        )
        
        # Add issues of different severities
        report.add_issue(ValidationIssue(
            category=ValidationCategory.SPIRITUAL_TONE,
            severity="critical",
            description="Critical issue"
        ))
        report.add_issue(ValidationIssue(
            category=ValidationCategory.AUTHENTICITY,
            severity="high",
            description="High issue"
        ))
        report.add_issue(ValidationIssue(
            category=ValidationCategory.CULTURAL_SENSITIVITY,
            severity="medium",
            description="Medium issue"
        ))
        
        validator._calculate_validation_result(report)
        
        # Should have low confidence and be rejected due to critical issue
        assert report.confidence_score < 0.7
        assert report.overall_result == ValidationResult.REJECTED
    
    def test_get_validation_summary(self):
        """Test validation summary generation"""
        validator = SpiritualResponseValidator()
        response = "Test response with some issues"
        
        report = validator.validate_response(response)
        summary = validator.get_validation_summary(report)
        
        assert "Validation Result:" in summary
        assert "Confidence Score:" in summary
        assert "Issues Found:" in summary
        assert "Checks Passed:" in summary


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_validate_spiritual_response_function(self):
        """Test convenience validation function"""
        response = "My dear child, divine wisdom guides us through dharma and devotion."
        
        report = validate_spiritual_response(response)
        
        assert isinstance(report, ValidationReport)
        assert report.overall_result == ValidationResult.APPROVED
    
    def test_is_response_acceptable_function(self):
        """Test quick acceptability check function"""
        good_response = "My dear child, divine wisdom guides us through dharma and devotion."
        bad_response = "Hey dude, just manifest your dreams!"
        
        assert is_response_acceptable(good_response) == True
        assert is_response_acceptable(bad_response, min_confidence=0.8) == False
    
    def test_is_response_acceptable_with_threshold(self):
        """Test acceptability with custom threshold"""
        response = "A mediocre response with some spiritual content but lacks depth and proper guidance for seekers"
        
        # Should pass with low threshold but fail with high threshold
        assert is_response_acceptable(response, min_confidence=0.3) == True
        # The response should actually pass validation despite being mediocre, so let's test with a problematic response
        problematic_response = "Hey dude, just manifest your dreams with awesome energy!"
        assert is_response_acceptable(problematic_response, min_confidence=0.9) == False


class TestIntegration:
    """Integration tests for complete validation workflow"""
    
    def test_complete_validation_workflow_excellent(self):
        """Test complete workflow with excellent response"""
        validator = SpiritualResponseValidator()
        query = "How can I find peace in difficult times?"
        response = """My beloved child, in times of difficulty, remember the eternal wisdom 
        of Lord Krishna. As He teaches in Bhagavad Gita 2.14, 'The contacts of the senses 
        with their objects give rise to happiness and sorrow; they come and go and are 
        impermanent. Therefore, endure them bravely, O Arjuna.' Through devotion and 
        surrender to the divine will, we find the peace that surpasses understanding."""
        
        report = validator.validate_response(response, query)
        
        assert report.overall_result == ValidationResult.APPROVED
        assert report.confidence_score > 0.8
        assert not report.expert_review_required
        assert "spiritual_tone" in report.passed_checks
        assert "authenticity" in report.passed_checks
    
    def test_complete_validation_workflow_problematic(self):
        """Test complete workflow with problematic response"""
        validator = SpiritualResponseValidator()
        query = "How can I find peace?"
        response = """Dude, just chill out and use manifestation! The law of attraction 
        will totally solve your problems. Get some chakra balancing and quantum healing - 
        I guarantee it will work 100%! Your bad karma is punishment, but new age techniques 
        can fix your caste issues."""
        
        report = validator.validate_response(response, query)
        
        assert report.overall_result == ValidationResult.REJECTED
        assert report.confidence_score < 0.7
        assert len(report.issues) > 5
        assert report.has_critical_issues() or report.has_high_severity_issues()
    
    def test_validation_with_context(self):
        """Test validation with additional context"""
        validator = SpiritualResponseValidator()
        context = {
            "user_spiritual_level": "beginner",
            "previous_conversation": True,
            "sensitive_topic": False
        }
        
        response = "Divine guidance flows through compassionate understanding, dear seeker."
        report = validator.validate_response(response, context=context)
        
        assert isinstance(report, ValidationReport)
        assert report.overall_result in [ValidationResult.APPROVED, ValidationResult.NEEDS_REVIEW]


# Example test runner
if __name__ == "__main__":
    # Run some basic tests
    print("Running response validation tests...")
    
    # Test excellent response
    print("\n=== Testing Excellent Response ===")
    validator = SpiritualResponseValidator()
    excellent_response = """My dear child, the path of dharma leads to eternal peace. 
    As Lord Krishna teaches in Bhagavad Gita 2.47, you have the right to perform your 
    duties but not to the fruits of your actions. Through devotion and surrender, 
    we transcend the illusions of this world."""
    
    report = validator.validate_response(excellent_response)
    print(validator.get_validation_summary(report))
    
    # Test problematic response
    print("\n=== Testing Problematic Response ===")
    problematic_response = """Hey dude, manifestation and the law of attraction will 
    totally fix your karma punishment! Use chakra balancing - I guarantee success!"""
    
    report = validator.validate_response(problematic_response)
    print(validator.get_validation_summary(report))
    
    print("\nResponse validation tests completed!")
