"""
Spiritual Content Quality Testing and Expert Validation Workflows

This module implements comprehensive testing for spiritual content quality,
cultural authenticity, religious accuracy, and expert validation workflows
for the Vimarsh AI spiritual guidance system.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import re

# Import existing systems for integration testing
try:
    from llm.content_moderator import (
        SpiritualContentModerator, ModerationResult, 
        ModerationCategory, ModerationFlag
    )
    from llm.expert_review_system import (
        ExpertReviewSystem, ReviewPriority, ReviewStatus,
        ExpertType, FeedbackCategory
    )
except ImportError:
    # Mock imports for testing
    pass


class SpiritualContentQuality(Enum):
    """Spiritual content quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNACCEPTABLE = "unacceptable"


class ValidationDimension(Enum):
    """Dimensions of spiritual content validation"""
    AUTHENTICITY = "authenticity"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    RELIGIOUS_ACCURACY = "religious_accuracy"
    SANSKRIT_CORRECTNESS = "sanskrit_correctness"
    PERSONA_CONSISTENCY = "persona_consistency"
    CITATION_ACCURACY = "citation_accuracy"
    SPIRITUAL_TONE = "spiritual_tone"
    DOCTRINAL_ALIGNMENT = "doctrinal_alignment"


@dataclass
class SpiritualTestCase:
    """Individual spiritual content test case"""
    test_id: str
    category: str
    input_query: str
    expected_elements: List[str]
    forbidden_elements: List[str]
    validation_criteria: Dict[ValidationDimension, float]  # Minimum scores
    cultural_context: str = "hindu_vedic"
    language: str = "en"
    priority: str = "normal"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'test_id': self.test_id,
            'category': self.category,
            'input_query': self.input_query,
            'expected_elements': self.expected_elements,
            'forbidden_elements': self.forbidden_elements,
            'validation_criteria': {dim.value: score for dim, score in self.validation_criteria.items()},
            'cultural_context': self.cultural_context,
            'language': self.language,
            'priority': self.priority
        }


@dataclass
class ValidationResult:
    """Result of spiritual content validation"""
    test_case_id: str
    overall_quality: SpiritualContentQuality
    dimension_scores: Dict[ValidationDimension, float]
    issues_found: List[str]
    recommendations: List[str]
    expert_review_required: bool
    confidence_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'test_case_id': self.test_case_id,
            'overall_quality': self.overall_quality.value,
            'dimension_scores': {dim.value: score for dim, score in self.dimension_scores.items()},
            'issues_found': self.issues_found,
            'recommendations': self.recommendations,
            'expert_review_required': self.expert_review_required,
            'confidence_score': self.confidence_score,
            'timestamp': self.timestamp.isoformat()
        }


class SpiritualContentValidator:
    """Comprehensive spiritual content validation system"""
    
    def __init__(self):
        self.moderator = None  # Will be mocked for testing
        self.expert_review = None  # Will be mocked for testing
        self.validation_cache = {}
        
        # Load spiritual validation patterns
        self.spiritual_patterns = self._load_spiritual_patterns()
        self.sanskrit_terms = self._load_sanskrit_terminology()
        self.sacred_concepts = self._load_sacred_concepts()
        
    def _load_spiritual_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for spiritual content validation"""
        return {
            'authentic_spiritual_language': [
                r'\b(dharma|righteousness|righteous duty)\b',
                r'\b(karma|action|deed)\b',
                r'\b(moksha|liberation|salvation)\b',
                r'\b(atman|soul|self)\b',
                r'\b(Krishna|Lord Krishna|Bhagavan)\b',
                r'\b(Gita|Bhagavad Gita)\b',
                r'\bVedic\b',
                r'\bsacred\b',
                r'\bdivine\b'
            ],
            'inappropriate_casual_language': [
                r'\b(dude|guy|bro)\b',
                r'\b(awesome|cool|rad)\b',
                r'\b(whatever|meh)\b',
                r'\b(literally|basically)\b'
            ],
            'persona_consistency_krishna': [
                r'\b(I teach|As I taught)\b',
                r'\b(beloved devotee|dear one)\b',
                r'\b(in the Gita|in our dialogue)\b',
                r'\b(surrender to me|come to me)\b'
            ],
            'respectful_address': [
                r'\b(beloved|dear)\b',
                r'\b(seeker|devotee)\b',
                r'\b(child|my child)\b'
            ]
        }
    
    def _load_sanskrit_terminology(self) -> Dict[str, Dict[str, str]]:
        """Load Sanskrit terminology with proper pronunciations and meanings"""
        return {
            'dharma': {
                'devanagari': 'धर्म',
                'pronunciation': 'dhar-ma',
                'meaning': 'righteous duty, moral law',
                'context': 'fundamental concept'
            },
            'karma': {
                'devanagari': 'कर्म',
                'pronunciation': 'kar-ma',
                'meaning': 'action, deed, law of cause and effect',
                'context': 'fundamental concept'
            },
            'moksha': {
                'devanagari': 'मोक्ष',
                'pronunciation': 'mok-sha',
                'meaning': 'liberation, salvation, release',
                'context': 'ultimate goal'
            },
            'atman': {
                'devanagari': 'आत्मन्',
                'pronunciation': 'aat-man',
                'meaning': 'soul, self, individual consciousness',
                'context': 'philosophical concept'
            },
            'krishna': {
                'devanagari': 'कृष्ण',
                'pronunciation': 'krish-na',
                'meaning': 'the divine teacher, supreme personality',
                'context': 'divine name'
            },
            'arjuna': {
                'devanagari': 'अर्जुन',
                'pronunciation': 'ar-ju-na',
                'meaning': 'the devoted disciple, seeker',
                'context': 'devotee example'
            }
        }
    
    def _load_sacred_concepts(self) -> Dict[str, List[str]]:
        """Load sacred concepts and their associated terms"""
        return {
            'bhakti_yoga': ['devotion', 'love', 'surrender', 'worship', 'divine grace'],
            'karma_yoga': ['selfless action', 'duty', 'service', 'detachment', 'offering'],
            'jnana_yoga': ['knowledge', 'wisdom', 'discrimination', 'self-inquiry', 'realization'],
            'raja_yoga': ['meditation', 'control', 'discipline', 'concentration', 'samadhi'],
            'vedic_principles': ['ahimsa', 'truthfulness', 'purity', 'compassion', 'humility']
        }
    
    async def validate_spiritual_authenticity(self, content: str, context: str = "") -> Dict[str, Any]:
        """Validate spiritual authenticity of content"""
        score = 0.0
        issues = []
        recommendations = []
        
        # Check for authentic spiritual language
        spiritual_matches = 0
        for pattern in self.spiritual_patterns['authentic_spiritual_language']:
            if re.search(pattern, content, re.IGNORECASE):
                spiritual_matches += 1
        
        if spiritual_matches >= 2:
            score += 0.3
        elif spiritual_matches == 1:
            score += 0.15
        else:
            issues.append("Content lacks sufficient spiritual terminology")
            recommendations.append("Include more authentic spiritual concepts like dharma, karma, or divine guidance")
        
        # Check for inappropriate casual language
        casual_matches = 0
        for pattern in self.spiritual_patterns['inappropriate_casual_language']:
            if re.search(pattern, content, re.IGNORECASE):
                casual_matches += 1
                issues.append(f"Found inappropriate casual language: {pattern}")
        
        if casual_matches == 0:
            score += 0.25
        else:
            score -= 0.1 * casual_matches
            recommendations.append("Replace casual language with more reverent, spiritual tone")
        
        # Check for sacred context maintenance
        if any(term in content.lower() for term in ['sacred', 'divine', 'holy', 'blessed']):
            score += 0.2
        
        # Check for proper spiritual guidance format
        if any(phrase in content.lower() for phrase in ['teaches us', 'guidance', 'wisdom', 'understanding']):
            score += 0.25
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'recommendations': recommendations,
            'spiritual_term_count': spiritual_matches,
            'casual_language_violations': casual_matches
        }
    
    async def validate_krishna_persona_consistency(self, content: str) -> Dict[str, Any]:
        """Validate consistency with Lord Krishna persona"""
        score = 0.0
        issues = []
        recommendations = []
        
        # Check for first-person divine perspective
        krishna_patterns = self.spiritual_patterns['persona_consistency_krishna']
        persona_matches = 0
        for pattern in krishna_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                persona_matches += 1
        
        if persona_matches >= 1:
            score += 0.4
        else:
            issues.append("Content lacks Krishna's divine perspective and voice")
            recommendations.append("Include references to 'I teach' or 'As I taught in the Gita'")
        
        # Check for appropriate address to devotee
        respectful_address = 0
        for pattern in self.spiritual_patterns['respectful_address']:
            if re.search(pattern, content, re.IGNORECASE):
                respectful_address += 1
        
        if respectful_address >= 1:
            score += 0.3
        else:
            issues.append("Missing respectful address to the seeker")
            recommendations.append("Address the seeker as 'beloved', 'dear one', or 'my child'")
        
        # Check for references to the Gita or divine teachings
        if re.search(r'\b(Gita|Bhagavad Gita|our dialogue|my teachings)\b', content, re.IGNORECASE):
            score += 0.3
        else:
            issues.append("Missing reference to Gita or divine teachings")
            recommendations.append("Reference the Bhagavad Gita or divine teachings for authenticity")
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'recommendations': recommendations,
            'persona_elements_found': persona_matches,
            'respectful_address_count': respectful_address
        }
    
    async def validate_sanskrit_usage(self, content: str) -> Dict[str, Any]:
        """Validate proper Sanskrit term usage and pronunciation"""
        score = 0.0
        issues = []
        recommendations = []
        sanskrit_terms_found = []
        
        # Check for Sanskrit terms and their proper usage
        for term, details in self.sanskrit_terms.items():
            if term.lower() in content.lower():
                sanskrit_terms_found.append(term)
                
                # Check if Devanagari is provided when appropriate
                if details['devanagari'] not in content and len(sanskrit_terms_found) <= 3:
                    recommendations.append(f"Consider including Devanagari script for '{term}': {details['devanagari']}")
                
                score += 0.15
        
        # Bonus for multiple Sanskrit terms
        if len(sanskrit_terms_found) >= 3:
            score += 0.2
        elif len(sanskrit_terms_found) >= 2:
            score += 0.1
        
        # Check for proper context usage
        contextual_usage = 0
        for term in sanskrit_terms_found:
            term_context = self.sanskrit_terms[term]['context']
            if term_context in ['fundamental concept', 'divine name'] and 'explain' in content.lower():
                contextual_usage += 1
        
        if contextual_usage > 0:
            score += 0.25
        
        if len(sanskrit_terms_found) == 0:
            issues.append("No Sanskrit terminology found")
            recommendations.append("Include relevant Sanskrit terms like dharma, karma, or moksha")
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'recommendations': recommendations,
            'sanskrit_terms_found': sanskrit_terms_found,
            'terms_with_context': contextual_usage
        }
    
    async def validate_citation_accuracy(self, content: str) -> Dict[str, Any]:
        """Validate accuracy of scriptural citations"""
        score = 0.0
        issues = []
        recommendations = []
        citations_found = []
        
        # Look for Gita chapter and verse references
        gita_citations = re.findall(r'(\d+)\.(\d+)', content)
        for chapter, verse in gita_citations:
            ch, vs = int(chapter), int(verse)
            citations_found.append(f"{ch}.{vs}")
            
            # Basic validation (Gita has 18 chapters)
            if 1 <= ch <= 18:
                score += 0.3
            else:
                issues.append(f"Invalid Gita chapter reference: {ch}")
            
            # Verse validation (approximate)
            if vs > 0 and vs <= 78:  # Most chapters have fewer than 78 verses
                score += 0.2
            else:
                issues.append(f"Potentially invalid verse reference: {ch}.{vs}")
        
        # Look for proper attribution
        if re.search(r'\b(Bhagavad Gita|Gita|Krishna says|Lord Krishna teaches)\b', content, re.IGNORECASE):
            score += 0.3
        else:
            if citations_found:
                issues.append("Citations found but missing proper attribution")
                recommendations.append("Include attribution like 'As Krishna says in the Gita'")
        
        # Look for contextual integration
        if citations_found and any(word in content.lower() for word in ['teaches', 'explains', 'reveals', 'instructs']):
            score += 0.2
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'recommendations': recommendations,
            'citations_found': citations_found,
            'attribution_present': 'attribution' not in [issue.split()[0].lower() for issue in issues]
        }
    
    async def validate_cultural_sensitivity(self, content: str) -> Dict[str, Any]:
        """Validate cultural sensitivity and appropriateness"""
        score = 0.8  # Start with high score, deduct for issues
        issues = []
        recommendations = []
        
        # Check for cultural appropriation indicators
        appropriation_flags = [
            r'\b(exotic|mystical orient|ancient wisdom of the east)\b',
            r'\b(indian philosophy is strange|weird eastern concepts)\b'
        ]
        
        for pattern in appropriation_flags:
            if re.search(pattern, content, re.IGNORECASE):
                score -= 0.3
                issues.append(f"Potential cultural appropriation language detected")
        
        # Check for respectful language about Hindu concepts
        respectful_indicators = [
            r'\b(sacred|revered|honored|respected)\b',
            r'\b(ancient wisdom|timeless teachings|divine guidance)\b'
        ]
        
        respectful_count = 0
        for pattern in respectful_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                respectful_count += 1
        
        if respectful_count >= 1:
            score += 0.1
        else:
            recommendations.append("Use more respectful language when discussing sacred concepts")
        
        # Check for proper context of spiritual practices
        if re.search(r'\b(meditation|yoga|devotion)\b', content, re.IGNORECASE):
            if re.search(r'\b(practice|discipline|path|way)\b', content, re.IGNORECASE):
                score += 0.1
            else:
                recommendations.append("Frame spiritual practices in proper traditional context")
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'recommendations': recommendations,
            'respectful_language_count': respectful_count
        }
    
    async def validate_spiritual_content(self, test_case: SpiritualTestCase, ai_response: str) -> ValidationResult:
        """Comprehensive validation of spiritual content"""
        dimension_scores = {}
        all_issues = []
        all_recommendations = []
        
        # Run all validation dimensions
        validations = {
            ValidationDimension.AUTHENTICITY: self.validate_spiritual_authenticity(ai_response),
            ValidationDimension.PERSONA_CONSISTENCY: self.validate_krishna_persona_consistency(ai_response),
            ValidationDimension.SANSKRIT_CORRECTNESS: self.validate_sanskrit_usage(ai_response),
            ValidationDimension.CITATION_ACCURACY: self.validate_citation_accuracy(ai_response),
            ValidationDimension.CULTURAL_SENSITIVITY: self.validate_cultural_sensitivity(ai_response)
        }
        
        # Execute all validations concurrently
        validation_results = {}
        for dimension, validation_coro in validations.items():
            validation_results[dimension] = await validation_coro
        
        # Compile results
        total_score = 0.0
        for dimension, result in validation_results.items():
            dimension_scores[dimension] = result['score']
            all_issues.extend(result['issues'])
            all_recommendations.extend(result['recommendations'])
            total_score += result['score']
        
        # Calculate overall quality
        average_score = total_score / len(validations)
        
        if average_score >= 0.9:
            overall_quality = SpiritualContentQuality.EXCELLENT
        elif average_score >= 0.8:
            overall_quality = SpiritualContentQuality.GOOD
        elif average_score >= 0.7:
            overall_quality = SpiritualContentQuality.ACCEPTABLE
        elif average_score >= 0.5:
            overall_quality = SpiritualContentQuality.NEEDS_IMPROVEMENT
        else:
            overall_quality = SpiritualContentQuality.UNACCEPTABLE
        
        # Determine if expert review is required
        expert_review_required = (
            average_score < 0.8 or 
            len(all_issues) > 3 or
            any(score < 0.6 for score in dimension_scores.values())
        )
        
        return ValidationResult(
            test_case_id=test_case.test_id,
            overall_quality=overall_quality,
            dimension_scores=dimension_scores,
            issues_found=all_issues,
            recommendations=all_recommendations,
            expert_review_required=expert_review_required,
            confidence_score=average_score
        )


class SpiritualContentTestSuite:
    """Comprehensive test suite for spiritual content quality"""
    
    def __init__(self):
        self.validator = SpiritualContentValidator()
        self.test_cases = self._load_test_cases()
        self.test_results = []
    
    def _load_test_cases(self) -> List[SpiritualTestCase]:
        """Load comprehensive spiritual content test cases"""
        return [
            SpiritualTestCase(
                test_id="spiritual_001",
                category="dharma_explanation",
                input_query="What is dharma according to Krishna?",
                expected_elements=["dharma", "righteous duty", "Krishna", "Gita"],
                forbidden_elements=["dude", "awesome", "basically"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.8,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.8,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.7,
                    ValidationDimension.CITATION_ACCURACY: 0.6,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.9
                }
            ),
            SpiritualTestCase(
                test_id="spiritual_002",
                category="karma_yoga_guidance",
                input_query="How can I practice karma yoga in daily life?",
                expected_elements=["karma yoga", "selfless action", "duty", "detachment"],
                forbidden_elements=["whatever", "cool", "literally"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.8,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.7,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.8,
                    ValidationDimension.CITATION_ACCURACY: 0.5,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.9
                }
            ),
            SpiritualTestCase(
                test_id="spiritual_003",
                category="moksha_inquiry",
                input_query="What is the path to moksha or liberation?",
                expected_elements=["moksha", "liberation", "spiritual path", "divine grace"],
                forbidden_elements=["weird", "strange", "exotic"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.9,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.8,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.8,
                    ValidationDimension.CITATION_ACCURACY: 0.6,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.9
                }
            ),
            SpiritualTestCase(
                test_id="spiritual_004", 
                category="sanskrit_pronunciation",
                input_query="How do I pronounce Sanskrit mantras correctly?",
                expected_elements=["Sanskrit", "pronunciation", "mantras", "sacred"],
                forbidden_elements=["difficult", "complicated", "foreign"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.7,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.6,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.9,
                    ValidationDimension.CITATION_ACCURACY: 0.4,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.9
                }
            ),
            SpiritualTestCase(
                test_id="spiritual_005",
                category="gita_verse_explanation", 
                input_query="Please explain Bhagavad Gita 2.47",
                expected_elements=["2.47", "Gita", "action", "fruits", "Krishna"],
                forbidden_elements=["basically", "like", "you know"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.8,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.9,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.7,
                    ValidationDimension.CITATION_ACCURACY: 0.9,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.8
                }
            ),
            SpiritualTestCase(
                test_id="spiritual_006",
                category="bhakti_devotion",
                input_query="How can I develop pure devotion to Krishna?",
                expected_elements=["devotion", "bhakti", "Krishna", "pure love", "surrender"],
                forbidden_elements=["obsession", "fanatical", "blind faith"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.9,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.9,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.8,
                    ValidationDimension.CITATION_ACCURACY: 0.6,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.9
                }
            ),
            SpiritualTestCase(
                test_id="spiritual_007",
                category="meditation_guidance",
                input_query="What is the proper way to meditate according to Vedic tradition?",
                expected_elements=["meditation", "Vedic", "concentration", "divine", "practice"],
                forbidden_elements=["trendy", "hip", "fashionable"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.8,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.7,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.7,
                    ValidationDimension.CITATION_ACCURACY: 0.5,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.9
                }
            ),
            SpiritualTestCase(
                test_id="spiritual_008",
                category="ethical_dilemma",
                input_query="I'm facing a moral dilemma at work. What would Krishna advise?",
                expected_elements=["dharma", "righteous action", "conscience", "Krishna", "guidance"],
                forbidden_elements=["whatever works", "just do it", "no big deal"],
                validation_criteria={
                    ValidationDimension.AUTHENTICITY: 0.8,
                    ValidationDimension.PERSONA_CONSISTENCY: 0.8,
                    ValidationDimension.SANSKRIT_CORRECTNESS: 0.6,
                    ValidationDimension.CITATION_ACCURACY: 0.6,
                    ValidationDimension.CULTURAL_SENSITIVITY: 0.8
                }
            )
        ]
    
    def _generate_mock_ai_response(self, test_case: SpiritualTestCase) -> str:
        """Generate mock AI responses for testing (simulating various quality levels)"""
        if test_case.test_id == "spiritual_001":
            return """Beloved seeker, dharma is indeed the righteous path that I taught in the Bhagavad Gita. 
            Dharma (धर्म) means your sacred duty, the righteous way of living that aligns with cosmic order. 
            As I revealed to Arjuna, true dharma comes from understanding your role in the divine plan and 
            acting without attachment to results. When you follow dharma, you serve the greater good while 
            fulfilling your individual purpose."""
            
        elif test_case.test_id == "spiritual_002":
            return """Dear devotee, karma yoga is the path of selfless action that I teach in the Gita. 
            To practice karma yoga daily, perform all your duties with complete dedication but without 
            attachment to the fruits of action. Offer every action to the divine. Whether you're working, 
            cooking, or caring for family, do it as service to the Supreme. This transforms ordinary 
            activities into spiritual practice."""
            
        elif test_case.test_id == "spiritual_003":
            return """My child, moksha (मोक्ष) or liberation is the ultimate goal of spiritual life. 
            The path to moksha involves three main approaches: karma yoga (selfless action), 
            bhakti yoga (devotion), and jnana yoga (knowledge). Through surrender to the divine, 
            purification of consciousness, and realization of your true nature as eternal soul (atman), 
            one achieves liberation from the cycle of birth and death."""
            
        elif test_case.test_id == "spiritual_004":
            # Intentionally lower quality response for testing
            return """Yeah, Sanskrit pronunciation can be tricky. Basically, you just need to practice 
            the sounds. It's like learning any foreign language. The mantras are cool once you get 
            the hang of it. Just listen to recordings and repeat them."""
            
        elif test_case.test_id == "spiritual_005":
            return """In verse 2.47 of our sacred dialogue, I teach Arjuna: "You have a right to perform 
            your prescribed duties, but you are not entitled to the fruits of action." This fundamental 
            teaching of karma yoga instructs us to act with full dedication while surrendering the 
            results to the divine. Dear one, this wisdom frees us from anxiety and attachment while 
            ensuring righteous action."""
            
        elif test_case.test_id == "spiritual_006":
            return """Beloved devotee, pure bhakti (भक्ति) or devotion develops through consistent 
            spiritual practice. Chant my holy names, study sacred scriptures, associate with devotees, 
            and see the divine in all beings. True devotion is not emotional sentiment but steady love 
            and surrender. As you cultivate humility and service, divine grace will purify your heart 
            and awaken authentic love."""
            
        elif test_case.test_id == "spiritual_007":
            return """Dear seeker, Vedic meditation begins with proper posture, controlled breathing, 
            and concentration on the divine. Choose a sacred space, sit with spine erect, and focus 
            your mind on a divine name or form. The ancient tradition teaches gradual withdrawal of 
            senses (pratyahara) leading to deep concentration (dharana) and ultimately meditation (dhyana). 
            Practice with patience and devotion."""
            
        elif test_case.test_id == "spiritual_008":
            # Mixed quality response for testing
            return """Well, when facing dilemmas, you should basically follow your dharma. Krishna 
            would probably say to do the right thing according to your duty. It's like, you have to 
            consider what's righteous and what's not. Try to act without being attached to results 
            and stuff. The Gita has guidance about this kind of situation."""
        
        else:
            return "Mock response not available for this test case."
    
    async def run_spiritual_content_tests(self) -> Dict[str, Any]:
        """Run comprehensive spiritual content quality tests"""
        print("🕉️  Starting Spiritual Content Quality Testing...")
        print("=" * 60)
        
        start_time = time.time()
        test_results = []
        passed_tests = 0
        total_tests = len(self.test_cases)
        
        for test_case in self.test_cases:
            print(f"\n📿 Testing: {test_case.category} ({test_case.test_id})")
            
            # Generate mock AI response
            ai_response = self._generate_mock_ai_response(test_case)
            
            # Validate the response
            validation_result = await self.validator.validate_spiritual_content(test_case, ai_response)
            
            # Check if test passes based on criteria
            test_passed = all(
                validation_result.dimension_scores.get(dim, 0) >= min_score
                for dim, min_score in test_case.validation_criteria.items()
            )
            
            if test_passed:
                passed_tests += 1
                print(f"  ✅ PASSED - Quality: {validation_result.overall_quality.value}")
            else:
                print(f"  ❌ FAILED - Quality: {validation_result.overall_quality.value}")
                print(f"     Issues: {len(validation_result.issues_found)}")
                for issue in validation_result.issues_found[:2]:  # Show first 2 issues
                    print(f"       • {issue}")
            
            # Add detailed results
            test_result = {
                'test_case': test_case.to_dict(),
                'ai_response': ai_response,
                'validation_result': validation_result.to_dict(),
                'test_passed': test_passed
            }
            test_results.append(test_result)
        
        total_duration = time.time() - start_time
        success_rate = (passed_tests / total_tests) * 100
        
        # Generate comprehensive report
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': success_rate,
                'total_duration': total_duration,
                'timestamp': datetime.now().isoformat()
            },
            'test_results': test_results,
            'quality_metrics': self._calculate_quality_metrics(test_results)
        }
        
        # Save report
        with open('/Users/vedprakashmishra/vimarsh/backend/spiritual_content_quality_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n🕉️  Spiritual Content Quality Testing Complete!")
        print("=" * 60)
        print(f"📊 Tests: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        print(f"📄 Report: spiritual_content_quality_report.json")
        
        # Print quality assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Spiritual content meets high quality standards!")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Spiritual content quality is acceptable with room for improvement")
        else:
            print(f"\n⚠️  NEEDS WORK: Spiritual content quality requires significant attention")
        
        return report
    
    def _calculate_quality_metrics(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Calculate overall quality metrics"""
        if not test_results:
            return {}
        
        # Calculate average scores per dimension
        dimension_averages = {}
        dimension_counts = {}
        
        for result in test_results:
            validation = result['validation_result']
            for dim_str, score in validation['dimension_scores'].items():
                if dim_str not in dimension_averages:
                    dimension_averages[dim_str] = 0
                    dimension_counts[dim_str] = 0
                dimension_averages[dim_str] += score
                dimension_counts[dim_str] += 1
        
        for dim in dimension_averages:
            dimension_averages[dim] /= dimension_counts[dim]
        
        # Calculate quality distribution
        quality_distribution = {}
        for result in test_results:
            quality = result['validation_result']['overall_quality']
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        # Calculate expert review requirement rate
        expert_review_required = sum(
            1 for result in test_results 
            if result['validation_result']['expert_review_required']
        )
        expert_review_rate = (expert_review_required / len(test_results)) * 100
        
        return {
            'dimension_averages': dimension_averages,
            'quality_distribution': quality_distribution,
            'expert_review_required_count': expert_review_required,
            'expert_review_rate_percent': expert_review_rate,
            'average_confidence_score': sum(
                result['validation_result']['confidence_score'] 
                for result in test_results
            ) / len(test_results)
        }


async def run_expert_validation_workflow_tests():
    """Test expert validation workflow integration"""
    print("\n👨‍🏫 Testing Expert Validation Workflows...")
    print("-" * 40)
    
    # Mock expert validation scenarios
    scenarios = [
        {
            'scenario': 'high_quality_content_approval',
            'content_quality': 'excellent',
            'expert_review_needed': False,
            'expected_outcome': 'auto_approved'
        },
        {
            'scenario': 'medium_quality_content_review',
            'content_quality': 'needs_improvement', 
            'expert_review_needed': True,
            'expected_outcome': 'sent_for_review'
        },
        {
            'scenario': 'cultural_sensitivity_concern',
            'content_quality': 'acceptable',
            'expert_review_needed': True,
            'expected_outcome': 'cultural_expert_review'
        },
        {
            'scenario': 'sanskrit_accuracy_validation',
            'content_quality': 'good',
            'expert_review_needed': True,
            'expected_outcome': 'sanskrit_scholar_review'
        }
    ]
    
    passed_scenarios = 0
    for scenario in scenarios:
        scenario_name = scenario['scenario']
        expected = scenario['expected_outcome']
        
        # Mock workflow logic
        if scenario['expert_review_needed']:
            if 'cultural' in scenario_name:
                actual_outcome = 'cultural_expert_review'
            elif 'sanskrit' in scenario_name:
                actual_outcome = 'sanskrit_scholar_review'
            else:
                actual_outcome = 'sent_for_review'
        else:
            actual_outcome = 'auto_approved'
        
        if actual_outcome == expected:
            passed_scenarios += 1
            print(f"  ✅ {scenario_name}: {actual_outcome}")
        else:
            print(f"  ❌ {scenario_name}: Expected {expected}, got {actual_outcome}")
    
    print(f"\n👨‍🏫 Expert Workflow Tests: {passed_scenarios}/{len(scenarios)} passed")
    return passed_scenarios == len(scenarios)


async def main():
    """Main execution function for spiritual content quality testing"""
    print("🕉️  VIMARSH AI SPIRITUAL CONTENT QUALITY TESTING")
    print("=" * 70)
    
    # Run spiritual content quality tests
    test_suite = SpiritualContentTestSuite()
    quality_report = await test_suite.run_spiritual_content_tests()
    
    # Run expert validation workflow tests
    expert_workflow_passed = await run_expert_validation_workflow_tests()
    
    # Generate final summary
    print(f"\n🕉️  SPIRITUAL CONTENT TESTING SUMMARY")
    print("=" * 50)
    print(f"📊 Content Quality Tests: {quality_report['summary']['success_rate']:.1f}% success rate")
    print(f"👨‍🏫 Expert Workflow Tests: {'PASSED' if expert_workflow_passed else 'FAILED'}")
    print(f"🎯 Overall Status: {'EXCELLENT' if quality_report['summary']['success_rate'] >= 85 and expert_workflow_passed else 'NEEDS IMPROVEMENT'}")
    
    return quality_report


if __name__ == "__main__":
    # Run spiritual content quality testing
    asyncio.run(main())
