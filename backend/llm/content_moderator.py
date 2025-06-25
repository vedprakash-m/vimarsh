"""
Spiritual Content Moderation and Safety Validation System

This module provides advanced content moderation beyond basic AI filters,
specifically designed for spiritual guidance applications. It ensures that
content maintains appropriate spiritual tone, cultural sensitivity, and
religious authenticity.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ModerationResult(Enum):
    """Content moderation results"""
    APPROVED = "approved"
    REQUIRES_REVIEW = "requires_review"
    FLAGGED = "flagged"
    BLOCKED = "blocked"


class ModerationCategory(Enum):
    """Categories of content moderation"""
    SPIRITUAL_APPROPRIATENESS = "spiritual_appropriateness"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    RELIGIOUS_ACCURACY = "religious_accuracy"
    SAFETY_CONTENT = "safety_content"
    RESPECTFUL_LANGUAGE = "respectful_language"
    DOCTRINAL_CONSISTENCY = "doctrinal_consistency"
    SACRED_CONTEXT = "sacred_context"


@dataclass
class ModerationFlag:
    """Individual moderation flag"""
    category: ModerationCategory
    severity: int  # 1-5, where 5 is most severe
    reason: str
    suggested_action: str
    confidence: float = 0.0
    auto_fixable: bool = False
    suggested_replacement: Optional[str] = None


@dataclass
class ModerationReport:
    """Complete moderation report"""
    content_id: str
    original_content: str
    result: ModerationResult
    flags: List[ModerationFlag] = field(default_factory=list)
    overall_score: float = 0.0
    requires_expert_review: bool = False
    cultural_context_warnings: List[str] = field(default_factory=list)
    spiritual_tone_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class SpiritualContentModerator:
    """Advanced spiritual content moderation system"""
    
    def __init__(self):
        self.inappropriate_terms = self._load_inappropriate_terms()
        self.sacred_terms = self._load_sacred_terms()
        self.cultural_guidelines = self._load_cultural_guidelines()
        self.doctrinal_patterns = self._load_doctrinal_patterns()
        
    def _load_inappropriate_terms(self) -> Dict[str, List[str]]:
        """Load terms inappropriate for spiritual context"""
        return {
            "casual_language": [
                "dude", "bro", "lol", "omg", "wtf", "damn", "hell yeah",
                "cool beans", "awesome sauce", "no way", "for real",
                "totally", "whatever", "like totally", "seriously?"
            ],
            "commercial_language": [
                "buy now", "purchase", "sale", "discount", "deal",
                "money back", "limited time", "act now", "subscribe",
                "upgrade", "premium", "exclusive offer"
            ],
            "dismissive_language": [
                "nonsense", "rubbish", "garbage", "stupid", "idiotic",
                "ridiculous", "absurd", "pointless", "useless", "waste"
            ],
            "overly_casual_spiritual": [
                "god is chill", "divine vibes", "karma's a bitch",
                "spiritual AF", "enlightened AF", "blessed and stressed",
                "manifest that", "good vibes only", "spiritual gangster"
            ]
        }
    
    def _load_sacred_terms(self) -> Dict[str, Dict[str, Any]]:
        """Load sacred terms that require special handling"""
        return {
            "sanskrit_terms": {
                "terms": [
                    "Om", "Aum", "Brahman", "Atman", "Dharma", "Karma", "Moksha",
                    "Samsara", "Ahimsa", "Satya", "Shanti", "Bhakti", "Yoga",
                    "Meditation", "Pranayama", "Mantra", "Yantra", "Chakra"
                ],
                "requires_respect": True,
                "proper_capitalization": True
            },
            "deity_names": {
                "terms": [
                    "Krishna", "Rama", "Shiva", "Vishnu", "Brahma", "Devi",
                    "Lakshmi", "Saraswati", "Ganesha", "Hanuman", "Durga"
                ],
                "requires_respect": True,
                "honorific_context": True
            },
            "sacred_texts": {
                "terms": [
                    "Bhagavad Gita", "Mahabharata", "Ramayana", "Upanishads",
                    "Vedas", "Puranas", "Srimad Bhagavatam", "Brahma Sutras"
                ],
                "proper_citation": True,
                "reverent_context": True
            }
        }
    
    def _load_cultural_guidelines(self) -> Dict[str, Any]:
        """Load cultural sensitivity guidelines"""
        return {
            "avoid_appropriation": {
                "patterns": [
                    r"my spirit animal",
                    r"that's so zen",
                    r"indian wisdom says",
                    r"ancient secret",
                    r"mystical powers"
                ],
                "replacement_suggestions": [
                    "spiritual guide",
                    "peaceful",
                    "traditional wisdom teaches",
                    "traditional knowledge",
                    "spiritual practices"
                ]
            },
            "respectful_language": {
                "required_context": [
                    "reverent tone when discussing deities",
                    "proper context for Sanskrit terms",
                    "acknowledgment of cultural origins",
                    "avoid casual use of sacred concepts"
                ]
            },
            "inclusive_language": {
                "avoid": ["guys", "mankind", "he/his for universal"],
                "prefer": ["everyone", "humanity", "they/their for universal"]
            }
        }
    
    def _load_doctrinal_patterns(self) -> Dict[str, Any]:
        """Load patterns for doctrinal consistency checking"""
        return {
            "krishna_persona_consistency": {
                "required_elements": [
                    "compassionate tone",
                    "reference to duty (dharma)",
                    "spiritual context",
                    "teaching through guidance"
                ],
                "avoid": [
                    "commanding tone",
                    "judgment without compassion",
                    "materialistic advice",
                    "non-spiritual solutions only"
                ]
            },
            "vedantic_principles": [
                "non-duality (Advaita)",
                "dharma (righteous duty)",
                "karma (action and consequence)",
                "moksha (liberation)",
                "ahimsa (non-violence)"
            ]
        }
    
    def moderate_content(self, content: str, context: Dict[str, Any] = None) -> ModerationReport:
        """Perform comprehensive content moderation"""
        if context is None:
            context = {}
        
        content_id = context.get("content_id", f"content_{datetime.now().timestamp()}")
        
        report = ModerationReport(
            content_id=content_id,
            original_content=content,
            result=ModerationResult.APPROVED  # Default, will be updated
        )
        
        # Run all moderation checks
        self._check_spiritual_appropriateness(content, report)
        self._check_cultural_sensitivity(content, report)
        self._check_religious_accuracy(content, report)
        self._check_safety_content(content, report)
        self._check_respectful_language(content, report)
        self._check_doctrinal_consistency(content, report)
        self._check_sacred_context(content, report)
        
        # Calculate overall scores and determine result
        self._calculate_overall_scores(report)
        self._determine_moderation_result(report)
        
        return report
    
    def _check_spiritual_appropriateness(self, content: str, report: ModerationReport):
        """Check if content maintains appropriate spiritual tone"""
        content_lower = content.lower()
        
        # Check for casual language inappropriate in spiritual context
        for category, terms in self.inappropriate_terms.items():
            for term in terms:
                if term.lower() in content_lower:
                    severity = 3 if category == "overly_casual_spiritual" else 2
                    report.flags.append(ModerationFlag(
                        category=ModerationCategory.SPIRITUAL_APPROPRIATENESS,
                        severity=severity,
                        reason=f"Contains inappropriate {category.replace('_', ' ')}: '{term}'",
                        suggested_action="Replace with more appropriate spiritual language",
                        confidence=0.8,
                        auto_fixable=True
                    ))
        
        # Check for overly casual tone patterns
        casual_patterns = [
            r'\blike\b.*\blike\b',  # "like... like..."
            r'\byou know\b',
            r'\bbasically\b',
            r'\bobviously\b',
            r'\bof course\b'
        ]
        
        for pattern in casual_patterns:
            if re.search(pattern, content_lower):
                report.flags.append(ModerationFlag(
                    category=ModerationCategory.SPIRITUAL_APPROPRIATENESS,
                    severity=2,
                    reason="Contains overly casual language patterns",
                    suggested_action="Use more formal, respectful language",
                    confidence=0.7
                ))
    
    def _check_cultural_sensitivity(self, content: str, report: ModerationReport):
        """Check for cultural sensitivity issues"""
        content_lower = content.lower()
        
        # Check for cultural appropriation patterns
        appropriation_patterns = self.cultural_guidelines["avoid_appropriation"]["patterns"]
        suggestions = self.cultural_guidelines["avoid_appropriation"]["replacement_suggestions"]
        
        for i, pattern in enumerate(appropriation_patterns):
            if re.search(pattern, content_lower):
                suggestion = suggestions[i] if i < len(suggestions) else "more culturally sensitive language"
                report.flags.append(ModerationFlag(
                    category=ModerationCategory.CULTURAL_SENSITIVITY,
                    severity=4,
                    reason=f"Contains culturally appropriative language: '{pattern}'",
                    suggested_action=f"Replace with: '{suggestion}'",
                    confidence=0.9,
                    auto_fixable=True,
                    suggested_replacement=suggestion
                ))
        
        # Check for generalization patterns
        generalization_patterns = [
            r"all indians",
            r"hindus believe",
            r"eastern philosophy says",
            r"ancient wisdom teaches"
        ]
        
        for pattern in generalization_patterns:
            if re.search(pattern, content_lower):
                report.flags.append(ModerationFlag(
                    category=ModerationCategory.CULTURAL_SENSITIVITY,
                    severity=3,
                    reason="Contains overgeneralization about cultural groups",
                    suggested_action="Use more specific, nuanced language",
                    confidence=0.8
                ))
    
    def _check_religious_accuracy(self, content: str, report: ModerationReport):
        """Check for religious accuracy and proper representation"""
        # Check for misuse of sacred terms
        for category_name, category_data in self.sacred_terms.items():
            terms = category_data["terms"]
            
            for term in terms:
                # Check if term appears in inappropriate context
                if term.lower() in content.lower():
                    # Check capitalization if required
                    if category_data.get("proper_capitalization") and term not in content:
                        report.flags.append(ModerationFlag(
                            category=ModerationCategory.RELIGIOUS_ACCURACY,
                            severity=2,
                            reason=f"Sacred term '{term}' should be properly capitalized",
                            suggested_action=f"Use proper capitalization: '{term}'",
                            confidence=0.9,
                            auto_fixable=True
                        ))
                    
                    # Check for respectful context if required
                    if category_data.get("requires_respect"):
                        context_window = self._get_context_window(content, term, 50)
                        if self._is_disrespectful_context(context_window):
                            report.flags.append(ModerationFlag(
                                category=ModerationCategory.RELIGIOUS_ACCURACY,
                                severity=4,
                                reason=f"Sacred term '{term}' used in disrespectful context",
                                suggested_action="Ensure respectful, reverent context",
                                confidence=0.8
                            ))
    
    def _check_safety_content(self, content: str, report: ModerationReport):
        """Check for safety-related content issues"""
        content_lower = content.lower()
        
        # Check for dangerous advice patterns (more flexible matching)
        dangerous_patterns = [
            r"ignore.{0,20}medical advice",
            r"stop taking.{0,20}medication",
            r"prayer will cure",
            r"meditation replaces.{0,20}medicine",
            r"spiritual healing instead.{0,20}medicine",
            r"don't take.{0,20}medication",
            r"avoid.{0,20}doctors",
            r"natural healing.{0,20}cure cancer",
            r"prayer.{0,20}cure.{0,20}disease"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content_lower):
                report.flags.append(ModerationFlag(
                    category=ModerationCategory.SAFETY_CONTENT,
                    severity=5,
                    reason="Contains potentially dangerous medical advice",
                    suggested_action="Include medical disclaimer and encourage professional consultation",
                    confidence=0.9
                ))
        
        # Check for financial advice
        financial_patterns = [
            r"invest in",
            r"financial blessing",
            r"money will come",
            r"donate money to",
            r"financial guarantee"
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, content_lower):
                report.flags.append(ModerationFlag(
                    category=ModerationCategory.SAFETY_CONTENT,
                    severity=3,
                    reason="Contains financial advice or promises",
                    suggested_action="Add disclaimers about financial decisions",
                    confidence=0.8
                ))
    
    def _check_respectful_language(self, content: str, report: ModerationReport):
        """Check for respectful, inclusive language"""
        content_lower = content.lower()
        
        # Check for inclusive language
        exclusive_terms = self.cultural_guidelines["inclusive_language"]["avoid"]
        inclusive_alternatives = self.cultural_guidelines["inclusive_language"]["prefer"]
        
        for i, term in enumerate(exclusive_terms):
            if term.lower() in content_lower:
                alternative = inclusive_alternatives[i] if i < len(inclusive_alternatives) else "more inclusive language"
                report.flags.append(ModerationFlag(
                    category=ModerationCategory.RESPECTFUL_LANGUAGE,
                    severity=2,
                    reason=f"Use more inclusive language instead of '{term}'",
                    suggested_action=f"Consider using '{alternative}'",
                    confidence=0.7,
                    auto_fixable=True,
                    suggested_replacement=alternative
                ))
    
    def _check_doctrinal_consistency(self, content: str, report: ModerationReport):
        """Check for consistency with Krishna persona and Vedantic principles"""
        content_lower = content.lower()
        
        # Check Krishna persona consistency
        krishna_guidelines = self.doctrinal_patterns["krishna_persona_consistency"]
        
        # Check for avoided patterns
        for avoid_pattern in krishna_guidelines["avoid"]:
            if self._check_pattern_presence(content_lower, avoid_pattern):
                report.flags.append(ModerationFlag(
                    category=ModerationCategory.DOCTRINAL_CONSISTENCY,
                    severity=3,
                    reason=f"Content conflicts with Krishna persona: {avoid_pattern}",
                    suggested_action="Align with compassionate, teaching-oriented approach",
                    confidence=0.8
                ))
        
        # Check for required elements (informational, not flagged unless severely lacking)
        missing_elements = []
        for required in krishna_guidelines["required_elements"]:
            if not self._check_pattern_presence(content_lower, required):
                missing_elements.append(required)
        
        # Only flag if missing most elements AND content is short/lacks spiritual context
        # Skip check for very short content (under 10 words)
        if len(missing_elements) >= 3 and len(content.split()) >= 10 and len(content.split()) < 50:
            report.flags.append(ModerationFlag(
                category=ModerationCategory.DOCTRINAL_CONSISTENCY,
                severity=1,  # Reduced severity for missing elements
                reason=f"Content could better reflect Krishna persona (missing: {', '.join(missing_elements[:2])}...)",
                suggested_action="Consider incorporating more spiritual guidance elements",
                confidence=0.4  # Lower confidence for these suggestions
            ))
    
    def _check_sacred_context(self, content: str, report: ModerationReport):
        """Check if sacred concepts are used in appropriate context"""
        content_lower = content.lower()
        
        # Check for sacred terms in inappropriate contexts
        sacred_terms_all = []
        for category_data in self.sacred_terms.values():
            sacred_terms_all.extend([term.lower() for term in category_data["terms"]])
        
        for term in sacred_terms_all:
            if term in content_lower:
                context_window = self._get_context_window(content, term, 100)
                
                # Check for commercial context
                if self._is_commercial_context(context_window):
                    report.flags.append(ModerationFlag(
                        category=ModerationCategory.SACRED_CONTEXT,
                        severity=4,
                        reason=f"Sacred term '{term}' used in commercial context",
                        suggested_action="Remove commercial language around sacred terms",
                        confidence=0.8
                    ))
                
                # Check for trivial context
                if self._is_trivial_context(context_window):
                    report.flags.append(ModerationFlag(
                        category=ModerationCategory.SACRED_CONTEXT,
                        severity=3,
                        reason=f"Sacred term '{term}' used in trivial context",
                        suggested_action="Use sacred terms only in meaningful spiritual context",
                        confidence=0.7
                    ))
    
    def _get_context_window(self, content: str, term: str, window_size: int) -> str:
        """Get context window around a term"""
        term_index = content.lower().find(term.lower())
        if term_index == -1:
            return ""
        
        start = max(0, term_index - window_size)
        end = min(len(content), term_index + len(term) + window_size)
        
        return content[start:end]
    
    def _is_disrespectful_context(self, context: str) -> bool:
        """Check if context is disrespectful"""
        disrespectful_words = [
            "joke", "funny", "ridiculous", "silly", "weird", "strange",
            "lol", "haha", "whatever", "nonsense", "fake", "made up"
        ]
        
        context_lower = context.lower()
        return any(word in context_lower for word in disrespectful_words)
    
    def _is_commercial_context(self, context: str) -> bool:
        """Check if context is commercial"""
        commercial_words = [
            "buy", "sell", "purchase", "money", "price", "cost", "sale",
            "discount", "deal", "offer", "business", "product", "service"
        ]
        
        context_lower = context.lower()
        return any(word in context_lower for word in commercial_words)
    
    def _is_trivial_context(self, context: str) -> bool:
        """Check if context is trivial"""
        trivial_words = [
            "fashion", "food", "movie", "game", "sport", "celebrity",
            "gossip", "party", "weekend", "vacation", "shopping"
        ]
        
        context_lower = context.lower()
        return any(word in context_lower for word in trivial_words)
    
    def _check_pattern_presence(self, content: str, pattern: str) -> bool:
        """Check if a pattern is present in content"""
        # Simple keyword-based checking for now
        # Could be enhanced with more sophisticated NLP
        pattern_words = pattern.lower().split()
        content_words = content.split()
        
        # Check if most words from pattern are present
        matches = sum(1 for word in pattern_words if word in content)
        return matches >= len(pattern_words) * 0.6  # 60% match threshold
    
    def _calculate_overall_scores(self, report: ModerationReport):
        """Calculate overall moderation scores"""
        if not report.flags:
            report.overall_score = 1.0
            report.spiritual_tone_score = 1.0
            return
        
        # Calculate weighted score based on flag severity (more lenient for minor issues)
        total_weight = 0
        weighted_score = 0
        
        spiritual_flags = 0
        total_flags = len(report.flags)
        
        for flag in report.flags:
            # Use exponential weighting - higher severity flags have much more impact
            weight = (flag.severity ** 2) * flag.confidence
            total_weight += weight
            
            # More lenient scoring for low severity issues
            if flag.severity <= 2:
                score_penalty = flag.severity / 10  # Very small penalty for minor issues
            else:
                score_penalty = flag.severity / 5   # Original penalty for serious issues
            
            weighted_score += weight * (1 - score_penalty)
            
            if flag.category == ModerationCategory.SPIRITUAL_APPROPRIATENESS:
                spiritual_flags += 1
        
        if total_weight > 0:
            report.overall_score = weighted_score / total_weight
        else:
            report.overall_score = 1.0
        
        # Calculate spiritual tone score
        report.spiritual_tone_score = 1.0 - (spiritual_flags / max(total_flags, 1)) * 0.8
        
        # Determine if expert review is needed (more conservative)
        high_severity_flags = [f for f in report.flags if f.severity >= 4]
        cultural_or_religious_flags = [
            f for f in report.flags 
            if f.category in [ModerationCategory.CULTURAL_SENSITIVITY, ModerationCategory.RELIGIOUS_ACCURACY] and f.severity >= 3
        ]
        
        report.requires_expert_review = (
            len(high_severity_flags) > 0 or
            len(cultural_or_religious_flags) > 1 or
            report.overall_score < 0.4  # Lower threshold
        )
    
    def _determine_moderation_result(self, report: ModerationReport):
        """Determine final moderation result"""
        high_severity_flags = [f for f in report.flags if f.severity >= 4]
        blocking_flags = [f for f in report.flags if f.severity == 5]
        medium_severity_flags = [f for f in report.flags if f.severity == 3]
        minor_flags = [f for f in report.flags if f.severity <= 2]
        
        # Count spiritual appropriateness flags specifically
        spiritual_flags = [f for f in report.flags if f.category == ModerationCategory.SPIRITUAL_APPROPRIATENESS]
        
        if blocking_flags:
            report.result = ModerationResult.BLOCKED
        elif high_severity_flags or report.overall_score < 0.3:
            report.result = ModerationResult.FLAGGED
        elif (report.requires_expert_review or 
              len(medium_severity_flags) > 1 or 
              len(spiritual_flags) >= 2 or  # Two or more casual language issues
              report.overall_score < 0.5):
            report.result = ModerationResult.REQUIRES_REVIEW
        else:
            report.result = ModerationResult.APPROVED
    
    def get_content_suggestions(self, report: ModerationReport) -> List[str]:
        """Get suggestions for improving content based on moderation results"""
        suggestions = []
        
        # Auto-fixable suggestions
        auto_fixes = [f for f in report.flags if f.auto_fixable and f.suggested_replacement]
        if auto_fixes:
            suggestions.append("Automatic fixes available for:")
            for fix in auto_fixes:
                suggestions.append(f"  • {fix.reason} → {fix.suggested_replacement}")
        
        # Manual review suggestions
        manual_fixes = [f for f in report.flags if not f.auto_fixable]
        if manual_fixes:
            suggestions.append("Manual review needed for:")
            for fix in manual_fixes:
                suggestions.append(f"  • {fix.reason} → {fix.suggested_action}")
        
        # Overall improvement suggestions
        if report.spiritual_tone_score < 0.7:
            suggestions.append("Consider enhancing spiritual tone with:")
            suggestions.append("  • More reverent language")
            suggestions.append("  • Reference to spiritual principles")
            suggestions.append("  • Compassionate guidance approach")
        
        return suggestions


def moderate_spiritual_content(content: str, context: Dict[str, Any] = None) -> ModerationReport:
    """Convenience function for content moderation"""
    moderator = SpiritualContentModerator()
    return moderator.moderate_content(content, context)


def is_content_safe_for_spiritual_context(content: str) -> bool:
    """Quick check if content is safe for spiritual context"""
    report = moderate_spiritual_content(content)
    return report.result in [ModerationResult.APPROVED, ModerationResult.REQUIRES_REVIEW]


def get_content_safety_score(content: str) -> float:
    """Get safety score for content (0.0 to 1.0)"""
    report = moderate_spiritual_content(content)
    return report.overall_score


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    print("=== Spiritual Content Moderation Demo ===\n")
    
    moderator = SpiritualContentModerator()
    
    test_contents = [
        # Good spiritual content
        "My dear child, dharma is your sacred duty that guides you through life's challenges. As Lord Krishna teaches in the Bhagavad Gita, perform your actions with devotion and surrender the fruits to the Divine.",
        
        # Casual inappropriate language
        "Hey dude, just manifest your dreams and like, the universe will totally give you good vibes. Krishna is like, super chill about everything.",
        
        # Cultural appropriation
        "Use your spirit animal and ancient Indian secrets to unlock mystical powers for manifestation.",
        
        # Dangerous medical advice
        "Prayer will cure your cancer, so you should stop taking your medication and rely only on meditation.",
        
        # Disrespectful sacred terms
        "That Krishna guy was pretty cool, and the Gita is just some old book with funny stories."
    ]
    
    for i, content in enumerate(test_contents, 1):
        print(f"Test Content {i}:")
        print(f"Content: {content[:80]}...")
        
        report = moderator.moderate_content(content)
        
        print(f"Result: {report.result.value}")
        print(f"Overall Score: {report.overall_score:.2f}")
        print(f"Spiritual Tone Score: {report.spiritual_tone_score:.2f}")
        print(f"Flags: {len(report.flags)}")
        print(f"Expert Review Required: {report.requires_expert_review}")
        
        if report.flags:
            print("Issues found:")
            for flag in report.flags[:3]:  # Show first 3 flags
                print(f"  • {flag.category.value}: {flag.reason} (severity: {flag.severity})")
        
        suggestions = moderator.get_content_suggestions(report)
        if suggestions:
            print("Suggestions:")
            for suggestion in suggestions[:3]:  # Show first 3 suggestions
                print(f"  {suggestion}")
        
        print("-" * 80 + "\n")
    
    print("Spiritual content moderation demo completed!")
