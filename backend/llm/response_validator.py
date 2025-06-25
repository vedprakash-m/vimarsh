"""
Response Validation System for Spiritual Tone and Authenticity

This module implements comprehensive validation of AI-generated spiritual responses
to ensure they maintain appropriate tone, authenticity, and spiritual quality.
"""

import re
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Validation result types"""
    APPROVED = "approved"
    NEEDS_REVIEW = "needs_review" 
    REJECTED = "rejected"


class ValidationCategory(Enum):
    """Categories of validation checks"""
    SPIRITUAL_TONE = "spiritual_tone"
    AUTHENTICITY = "authenticity"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    CONTENT_APPROPRIATENESS = "content_appropriateness"
    CITATION_ACCURACY = "citation_accuracy"
    LANGUAGE_QUALITY = "language_quality"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a response"""
    category: ValidationCategory
    severity: str  # "low", "medium", "high", "critical"
    description: str
    location: Optional[str] = None  # Where in the response the issue was found
    suggestion: Optional[str] = None  # How to fix the issue


@dataclass
class ValidationReport:
    """Complete validation report for a spiritual response"""
    overall_result: ValidationResult
    confidence_score: float  # 0.0 to 1.0
    issues: List[ValidationIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    expert_review_required: bool = False
    expert_review_reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_issue(self, issue: ValidationIssue):
        """Add a validation issue to the report"""
        self.issues.append(issue)
        
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues"""
        return any(issue.severity == "critical" for issue in self.issues)
    
    def has_high_severity_issues(self) -> bool:
        """Check if there are any high severity issues"""
        return any(issue.severity in ["high", "critical"] for issue in self.issues)


class SpiritualToneValidator:
    """Validates spiritual tone and reverence in responses"""
    
    def __init__(self):
        # Words and phrases that indicate appropriate spiritual tone
        self.positive_spiritual_indicators = [
            "divine", "sacred", "blessed", "wisdom", "enlightenment", 
            "devotion", "surrender", "grace", "compassion", "dharma",
            "according to the scriptures", "in the bhagavad gita",
            "lord krishna teaches", "the vedas speak of", "spiritual journey"
        ]
        
        # Words that may indicate inappropriate casual tone
        self.tone_concerns = [
            "dude", "guy", "awesome", "cool", "whatever", "anyways",
            "no big deal", "piece of cake", "easy peasy", "no worries"
        ]
        
        # Divine address patterns that should be present
        self.divine_address_patterns = [
            r"my (dear )?child",
            r"beloved (seeker|devotee)",
            r"o (noble|dear) soul",
            r"arjuna", # Historical precedent from Gita
        ]
    
    def validate_tone(self, response: str) -> List[ValidationIssue]:
        """Validate the spiritual tone of a response"""
        issues = []
        response_lower = response.lower()
        
        # Check for inappropriate casual language
        casual_words_found = [word for word in self.tone_concerns if word in response_lower]
        if casual_words_found:
            issues.append(ValidationIssue(
                category=ValidationCategory.SPIRITUAL_TONE,
                severity="high",
                description=f"Inappropriate casual language detected: {', '.join(casual_words_found)}",
                suggestion="Replace with more reverent, spiritual language"
            ))
        
        # Check for presence of spiritual indicators
        spiritual_words_found = [word for word in self.positive_spiritual_indicators if word in response_lower]
        word_count = len(response.split())
        spiritual_score = len(spiritual_words_found) / max(word_count, 1)
        
        if word_count > 10 and spiritual_score < 0.05:  # Less than 5% spiritual content for longer responses
            issues.append(ValidationIssue(
                category=ValidationCategory.SPIRITUAL_TONE,
                severity="medium",
                description="Response lacks sufficient spiritual terminology and tone",
                suggestion="Incorporate more spiritual concepts and reverent language"
            ))
        
        # Check for appropriate divine address
        has_divine_address = any(re.search(pattern, response_lower) for pattern in self.divine_address_patterns)
        if len(response.split()) > 50 and not has_divine_address:  # For longer responses
            issues.append(ValidationIssue(
                category=ValidationCategory.SPIRITUAL_TONE,
                severity="low",
                description="Response lacks personal divine address",
                suggestion="Consider adding compassionate address like 'my dear child' or 'beloved seeker'"
            ))
        
        return issues


class AuthenticityValidator:
    """Validates authenticity against spiritual traditions and scriptures"""
    
    def __init__(self):
        # Core spiritual concepts that should be treated with reverence
        self.core_concepts = {
            "dharma": "righteous duty, cosmic law",
            "karma": "action and consequence, cosmic justice",
            "moksha": "liberation, spiritual freedom",
            "bhakti": "devotion, loving surrender",
            "jnana": "wisdom, spiritual knowledge",
            "yoga": "union, spiritual practice",
            "atman": "soul, inner self",
            "brahman": "ultimate reality, divine consciousness"
        }
        
        # Philosophical traditions to respect
        self.valid_traditions = [
            "advaita", "vedanta", "bhakti", "karma yoga", "jnana yoga",
            "raja yoga", "bhagavad gita", "upanishads", "vedas"
        ]
        
        # Modern concepts that might dilute authenticity
        self.authenticity_concerns = [
            "manifestation", "law of attraction", "quantum healing",
            "chakra balancing", "energy healing", "new age"
        ]
    
    def validate_authenticity(self, response: str) -> List[ValidationIssue]:
        """Validate authenticity against traditional spiritual teachings"""
        issues = []
        response_lower = response.lower()
        
        # Check for modern/new-age concepts that might dilute traditional teachings
        modern_concepts = [concept for concept in self.authenticity_concerns if concept in response_lower]
        if modern_concepts:
            issues.append(ValidationIssue(
                category=ValidationCategory.AUTHENTICITY,
                severity="medium",
                description=f"Response contains modern concepts that may dilute traditional authenticity: {', '.join(modern_concepts)}",
                suggestion="Focus on traditional scriptural teachings and avoid modern interpretations"
            ))
        
        # Validate proper use of Sanskrit terms
        sanskrit_misuse = self._check_sanskrit_usage(response)
        if sanskrit_misuse:
            issues.append(ValidationIssue(
                category=ValidationCategory.AUTHENTICITY,
                severity="high",
                description=f"Potential misuse of Sanskrit terms: {sanskrit_misuse}",
                suggestion="Verify Sanskrit term usage against authentic sources"
            ))
        
        return issues
    
    def _check_sanskrit_usage(self, response: str) -> Optional[str]:
        """Check for potential misuse of Sanskrit terms"""
        # This is a simplified check - in production, this would be more sophisticated
        response_lower = response.lower()
        
        # Look for common misuses (simplified examples)
        if "karma" in response_lower and "punishment" in response_lower:
            return "Karma is often misunderstood as punishment rather than action-consequence principle"
        
        if "dharma" in response_lower and ("religion" in response_lower or "belief" in response_lower):
            return "Dharma is cosmic duty/law, not just religious belief"
        
        return None


class CulturalSensitivityValidator:
    """Validates cultural sensitivity and appropriateness"""
    
    def __init__(self):
        # Terms that require careful handling
        self.sensitive_terms = [
            "caste", "brahmin", "untouchable", "dalit", 
            "hindu", "hinduism", "muslim", "christian",
            "colonial", "british", "western"
        ]
        
        # Respectful ways to address cultural concepts
        self.respectful_patterns = [
            r"in the ancient tradition",
            r"according to the sacred texts",
            r"the wise sages taught",
            r"in reverence to"
        ]
    
    def validate_cultural_sensitivity(self, response: str) -> List[ValidationIssue]:
        """Validate cultural sensitivity and appropriateness"""
        issues = []
        response_lower = response.lower()
        
        # Check for potentially sensitive terms
        sensitive_found = [term for term in self.sensitive_terms if term in response_lower]
        if sensitive_found:
            # This would trigger expert review rather than automatic rejection
            issues.append(ValidationIssue(
                category=ValidationCategory.CULTURAL_SENSITIVITY,
                severity="medium",
                description=f"Response contains culturally sensitive terms: {', '.join(sensitive_found)}",
                suggestion="Ensure culturally sensitive terms are handled with appropriate reverence and context"
            ))
        
        return issues


class CitationValidator:
    """Validates citation accuracy and appropriateness"""
    
    def __init__(self):
        # Common scriptural sources
        self.valid_sources = [
            "bhagavad gita", "mahabharata", "ramayana", 
            "upanishads", "vedas", "puranas", "brahma sutras"
        ]
        
        # Citation patterns to look for
        self.citation_patterns = [
            r"bhagavad gita \d+\.\d+",  # Gita chapter.verse
            r"chapter \d+ verse \d+",   # Generic chapter verse
            r"mahabharata \w+ parva",   # Mahabharata book
            r"(rig|sama|yajur|atharva) veda"  # Veda types
        ]
    
    def validate_citations(self, response: str) -> List[ValidationIssue]:
        """Validate citation accuracy and format"""
        issues = []
        response_lower = response.lower()
        
        # Check for citation patterns
        citations_found = []
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, response_lower)
            citations_found.extend(matches)
        
        # If response makes scriptural claims but has no citations
        if any(phrase in response_lower for phrase in ["scripture says", "gita teaches", "vedas state"]):
            if not citations_found:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CITATION_ACCURACY,
                    severity="high",
                    description="Response makes scriptural claims without proper citations",
                    suggestion="Add specific verse or text references for all scriptural claims"
                ))
        
        return issues


class ContentAppropriatenessValidator:
    """Validates overall content appropriateness for spiritual guidance"""
    
    def __init__(self):
        # Topics that require expert review
        self.sensitive_topics = [
            "death", "suicide", "violence", "sexual", "political",
            "medical", "legal", "financial advice", "predictions"
        ]
        
        # Inappropriate response types
        self.inappropriate_patterns = [
            r"i (predict|guarantee|promise)",
            r"you (will|must|have to)",
            r"(definitely|certainly|absolutely) will happen",
            r"medical (advice|diagnosis|treatment)",
            r"legal (advice|opinion)"
        ]
    
    def validate_appropriateness(self, response: str) -> List[ValidationIssue]:
        """Validate content appropriateness for spiritual guidance"""
        issues = []
        response_lower = response.lower()
        
        # Check for sensitive topics
        sensitive_found = [topic for topic in self.sensitive_topics if topic in response_lower]
        if sensitive_found:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_APPROPRIATENESS,
                severity="high",
                description=f"Response addresses sensitive topics: {', '.join(sensitive_found)}",
                suggestion="Sensitive topics require expert review and careful handling"
            ))
        
        # Check for inappropriate certainty claims
        inappropriate_matches = []
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, response_lower):
                inappropriate_matches.append(pattern)
        
        if inappropriate_matches:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_APPROPRIATENESS,
                severity="high",
                description="Response makes inappropriate certainty claims or advice",
                suggestion="Spiritual guidance should be humble and avoid absolute predictions or professional advice"
            ))
        
        return issues


class SpiritualResponseValidator:
    """Main validator that orchestrates all validation checks"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the response validator
        
        Args:
            config: Optional configuration for validation thresholds and settings
        """
        self.config = config or {}
        
        # Initialize sub-validators
        self.tone_validator = SpiritualToneValidator()
        self.authenticity_validator = AuthenticityValidator()
        self.cultural_validator = CulturalSensitivityValidator()
        self.citation_validator = CitationValidator()
        self.content_validator = ContentAppropriatenessValidator()
        
        # Validation thresholds
        self.expert_review_threshold = self.config.get("expert_review_threshold", 0.7)
        self.rejection_threshold = self.config.get("rejection_threshold", 0.3)
    
    def validate_response(self, response: str, query: str = "", context: Optional[Dict] = None) -> ValidationReport:
        """
        Perform comprehensive validation of a spiritual response
        
        Args:
            response: The AI-generated response to validate
            query: The original user query (for context)
            context: Additional context information
            
        Returns:
            ValidationReport with comprehensive validation results
        """
        logger.info(f"Validating response of length {len(response)}")
        
        # Initialize report
        report = ValidationReport(
            overall_result=ValidationResult.APPROVED,
            confidence_score=1.0
        )
        
        # Run all validation checks
        all_issues = []
        
        # Spiritual tone validation
        tone_issues = self.tone_validator.validate_tone(response)
        all_issues.extend(tone_issues)
        if not tone_issues:
            report.passed_checks.append("spiritual_tone")
        
        # Authenticity validation
        auth_issues = self.authenticity_validator.validate_authenticity(response)
        all_issues.extend(auth_issues)
        if not auth_issues:
            report.passed_checks.append("authenticity")
        
        # Cultural sensitivity validation
        cultural_issues = self.cultural_validator.validate_cultural_sensitivity(response)
        all_issues.extend(cultural_issues)
        if not cultural_issues:
            report.passed_checks.append("cultural_sensitivity")
        
        # Citation validation
        citation_issues = self.citation_validator.validate_citations(response)
        all_issues.extend(citation_issues)
        if not citation_issues:
            report.passed_checks.append("citation_accuracy")
        
        # Content appropriateness validation
        content_issues = self.content_validator.validate_appropriateness(response)
        all_issues.extend(content_issues)
        if not content_issues:
            report.passed_checks.append("content_appropriateness")
        
        # Add all issues to report
        report.issues = all_issues
        
        # Calculate confidence score and determine result
        self._calculate_validation_result(report)
        
        logger.info(f"Validation complete: {report.overall_result.value}, confidence: {report.confidence_score:.2f}")
        
        return report
    
    def _calculate_validation_result(self, report: ValidationReport):
        """Calculate overall validation result and confidence score"""
        
        # Count issues by severity
        critical_count = sum(1 for issue in report.issues if issue.severity == "critical")
        high_count = sum(1 for issue in report.issues if issue.severity == "high")
        medium_count = sum(1 for issue in report.issues if issue.severity == "medium")
        low_count = sum(1 for issue in report.issues if issue.severity == "low")
        
        # Calculate confidence score (inverse of issue severity)
        severity_weights = {"critical": 0.4, "high": 0.25, "medium": 0.15, "low": 0.05}
        total_deduction = sum(severity_weights[issue.severity] for issue in report.issues)
        report.confidence_score = max(0.0, 1.0 - total_deduction)
        
        # Determine overall result
        if critical_count > 0:
            report.overall_result = ValidationResult.REJECTED
        elif high_count > 2 or report.confidence_score < self.rejection_threshold:
            report.overall_result = ValidationResult.REJECTED
        elif high_count > 0 or medium_count > 3 or report.confidence_score < self.expert_review_threshold:
            report.overall_result = ValidationResult.NEEDS_REVIEW
            report.expert_review_required = True
            report.expert_review_reason = f"Found {high_count} high and {medium_count} medium severity issues"
        else:
            report.overall_result = ValidationResult.APPROVED
    
    def get_validation_summary(self, report: ValidationReport) -> str:
        """Generate a human-readable validation summary"""
        summary_lines = [
            f"Validation Result: {report.overall_result.value.upper()}",
            f"Confidence Score: {report.confidence_score:.2f}",
            f"Issues Found: {len(report.issues)}",
            f"Checks Passed: {len(report.passed_checks)}"
        ]
        
        if report.issues:
            summary_lines.append("\nIssues by Category:")
            for category in ValidationCategory:
                category_issues = [i for i in report.issues if i.category == category]
                if category_issues:
                    severity_counts = {}
                    for issue in category_issues:
                        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                    summary_lines.append(f"  {category.value}: {severity_counts}")
        
        if report.expert_review_required:
            summary_lines.append(f"\nExpert Review Required: {report.expert_review_reason}")
        
        return "\n".join(summary_lines)


# Utility functions for integration

def validate_spiritual_response(response: str, query: str = "", config: Optional[Dict] = None) -> ValidationReport:
    """
    Convenience function for validating a single spiritual response
    
    Args:
        response: The response to validate
        query: The original query (optional)
        config: Validation configuration (optional)
    
    Returns:
        ValidationReport with results
    """
    validator = SpiritualResponseValidator(config)
    return validator.validate_response(response, query)


def is_response_acceptable(response: str, query: str = "", min_confidence: float = 0.7) -> bool:
    """
    Quick check if a response is acceptable for use
    
    Args:
        response: The response to check
        query: The original query (optional)
        min_confidence: Minimum confidence threshold
    
    Returns:
        True if response is acceptable, False otherwise
    """
    report = validate_spiritual_response(response, query)
    return (report.overall_result == ValidationResult.APPROVED and 
            report.confidence_score >= min_confidence)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    validator = SpiritualResponseValidator()
    
    test_responses = [
        "My dear child, the path of dharma is not always easy, but it leads to eternal peace. As Lord Krishna teaches in the Bhagavad Gita 2.47, you have the right to perform your duties, but not to the fruits of your actions.",
        
        "Hey dude, just manifest your dreams and use the law of attraction! Chakra balancing will totally fix your problems.",
        
        "The scriptures teach us that suffering is part of the human experience. Through devotion and surrender, we can transcend these temporary difficulties."
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n=== Test Response {i} ===")
        report = validator.validate_response(response)
        print(validator.get_validation_summary(report))
