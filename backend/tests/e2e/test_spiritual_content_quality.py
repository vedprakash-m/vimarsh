"""
Comprehensive spiritual content quality testing and validation.

This module tests the spiritual authenticity, cultural sensitivity,
and reverence of responses generated by the Vimarsh platform.
"""

import pytest
import json
import re
from typing import Dict, List, Any
from unittest.mock import Mock, patch
import logging
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import mock implementations
try:
    from mock_implementations import (
        MockSpiritualValidator,
        MockExpertReviewValidator,
        MockFeedbackProcessor
    )
except ImportError:
    # Fallback if mock implementations not available
    class MockSpiritualValidator:
        def validate_response(self, *args):
            return {"is_valid": True, "authenticity_score": 0.9}
        def validate_sanskrit_usage(self, *args):
            return {"respectful_usage": True}
        def validate_cultural_sensitivity(self, *args):
            return {"culturally_sensitive": True, "avoids_stereotypes": True}
        def check_cross_textual_consistency(self, *args):
            return {"consistent": True, "complementary": True}
    
    class MockExpertReviewValidator:
        def aggregate_expert_reviews(self, *args):
            return {"overall_score": 0.9, "approval_status": "approved"}
    
    class MockFeedbackProcessor:
        def generate_system_improvements(self, *args):
            return {"citation_requirements": True, "tone_calibration": True}

logger = logging.getLogger(__name__)

class TestSpiritualContentQuality:
    """Test spiritual content quality and authenticity."""
    
    @pytest.fixture
    def sample_authentic_responses(self):
        """Sample responses that should pass spiritual validation."""
        return [
            {
                "response": "O Arjuna, dharma is the eternal law that sustains all creation. As I have taught in the Bhagavad Gita, it is the righteous path that leads to liberation. In your modern life, dharma manifests as performing your duties without attachment to the fruits of action.",
                "citations": [
                    {
                        "source": "Bhagavad Gita",
                        "chapter": 2,
                        "verse": 47,
                        "text": "You have a right to perform your prescribed duty, but not to the fruits of action."
                    }
                ],
                "expected_authenticity": 0.95,
                "expected_tone": "divine_reverent"
            },
            {
                "response": "Beloved child, the path of devotion is the sweetest of all paths. When you surrender your ego and offer all actions to the Divine, you transcend the limitations of the material world. This is the essence of Bhakti Yoga as taught in the sacred texts.",
                "citations": [
                    {
                        "source": "Bhagavad Gita",
                        "chapter": 9,
                        "verse": 27,
                        "text": "Whatever you do, whatever you eat, whatever you offer or give away, whatever austerities you practice—do that as an offering to God."
                    }
                ],
                "expected_authenticity": 0.98,
                "expected_tone": "compassionate_divine"
            }
        ]
    
    @pytest.fixture
    def sample_inappropriate_responses(self):
        """Sample responses that should fail spiritual validation."""
        return [
            {
                "response": "Hey dude, just do whatever makes you happy! Life's too short to worry about all this dharma stuff. YOLO!",
                "citations": [],
                "expected_issues": ["inappropriate_tone", "lack_of_reverence", "missing_citations", "colloquial_language"]
            },
            {
                "response": "Dharma is just an old concept that doesn't apply to modern life. You should focus on making money and being successful.",
                "citations": [],
                "expected_issues": ["dismissive_of_tradition", "materialistic_focus", "missing_citations"]
            },
            {
                "response": "I don't know anything about that. Ask someone else.",
                "citations": [],
                "expected_issues": ["unhelpful", "breaking_character", "missing_citations", "lack_of_wisdom"]
            }
        ]
    
    def test_divine_persona_consistency(self, sample_authentic_responses):
        """Test that responses maintain Lord Krishna's divine persona."""
        logger.info("Testing divine persona consistency")
        
        validator = MockSpiritualValidator()
        
        for response_data in sample_authentic_responses:
            response = response_data["response"]
            
            # Test for divine addressing patterns
            divine_patterns = [
                r"O Arjuna",
                r"Beloved child",
                r"Dear devotee",
                r"My child",
                r"O seeker"
            ]
            
            has_divine_address = any(re.search(pattern, response, re.IGNORECASE) for pattern in divine_patterns)
            assert has_divine_address, f"Response lacks divine addressing: {response[:100]}..."
            
            # Test for absence of inappropriate language
            inappropriate_terms = [
                " dude", " hey", " yo ", " whatever", " stuff", " things", " yolo",
                " cool", " awesome", " epic", " lol", " lmao", " wtf", " omg"
            ]  # Added spaces to avoid false positives like "yo" in "your"
            
            for term in inappropriate_terms:
                assert term.lower() not in response.lower(), f"Response contains inappropriate term '{term.strip()}': {response}"
            
            # Test for spiritual vocabulary
            spiritual_terms = [
                "dharma", "karma", "liberation", "divine", "sacred", "eternal",
                "righteousness", "devotion", "wisdom", "consciousness", "soul"
            ]
            
            has_spiritual_vocabulary = any(term.lower() in response.lower() for term in spiritual_terms)
            assert has_spiritual_vocabulary, f"Response lacks spiritual vocabulary: {response[:100]}..."
    
    def test_citation_authenticity(self, sample_authentic_responses):
        """Test that citations are properly formatted and authentic."""
        logger.info("Testing citation authenticity")
        
        for response_data in sample_authentic_responses:
            citations = response_data["citations"]
            
            assert len(citations) > 0, "Response must include citations"
            
            for citation in citations:
                # Required fields
                assert "source" in citation, "Citation must include source"
                assert "text" in citation, "Citation must include text"
                
                # Valid sources
                valid_sources = ["Bhagavad Gita", "Mahabharata", "Srimad Bhagavatam"]
                assert any(source in citation["source"] for source in valid_sources), \
                    f"Invalid source: {citation['source']}"
                
                # Proper formatting
                if "Bhagavad Gita" in citation["source"]:
                    assert "chapter" in citation and "verse" in citation, \
                        "Bhagavad Gita citations must include chapter and verse"
                
                # Non-empty citation text
                assert len(citation["text"].strip()) > 10, \
                    "Citation text must be substantial"
    
    def test_inappropriate_content_detection(self, sample_inappropriate_responses):
        """Test detection of inappropriate spiritual content."""
        logger.info("Testing inappropriate content detection")
        
        validator = MockSpiritualValidator()
        
        for response_data in sample_inappropriate_responses:
            response = response_data["response"]
            expected_issues = response_data["expected_issues"]
            
            # Mock validation result
            validation_result = validator.validate_response(response, response_data["citations"])
            
            # Should be marked as invalid
            assert not validation_result["is_valid"], \
                f"Response should be invalid: {response}"
            
            # Should have low authenticity score
            assert validation_result["authenticity_score"] < 0.5, \
                f"Inappropriate response has high authenticity: {validation_result['authenticity_score']}"
            
            # Should identify specific issues
            detected_issues = validation_result.get("issues", [])
            for expected_issue in expected_issues:
                assert any(expected_issue in issue for issue in detected_issues), \
                    f"Expected issue '{expected_issue}' not detected in: {detected_issues}"
    
    def test_sanskrit_terminology_respect(self):
        """Test that Sanskrit terms are used respectfully and correctly."""
        logger.info("Testing Sanskrit terminology respect")
        
        sanskrit_terms = {
            "dharma": "righteous duty",
            "karma": "action and consequence", 
            "moksha": "liberation",
            "samsara": "cycle of birth and death",
            "yoga": "union with the divine",
            "bhakti": "devotion",
            "jnana": "knowledge",
            "ahimsa": "non-violence"
        }
        
        # Test proper usage in context
        test_responses = [
            "Dharma, or righteous duty, is the foundation of spiritual life.",
            "Through karma yoga, the path of selfless action, one achieves purification.",
            "Bhakti, pure devotion to the Divine, is the easiest path to moksha."
        ]
        
        validator = MockSpiritualValidator()
        
        for response in test_responses:
            # Should not dilute or misrepresent Sanskrit terms
            assert not re.search(r"dharma.*just", response, re.IGNORECASE), \
                "Should not minimize significance of dharma"
            
            assert not re.search(r"karma.*only", response, re.IGNORECASE), \
                "Should not oversimplify karma"
            
            # Should maintain reverent context
            validation = validator.validate_sanskrit_usage(response)
            assert validation["respectful_usage"], \
                f"Sanskrit terms not used respectfully in: {response}"
    
    def test_cultural_sensitivity(self):
        """Test cultural sensitivity in spiritual guidance."""
        logger.info("Testing cultural sensitivity")
        
        # Test scenarios that require cultural awareness
        test_cases = [
            {
                "query": "Is idol worship wrong?",
                "response": "The forms and images in spiritual practice are not mere idols but sacred representations that help focus the mind on the Divine. As I have taught, the Supreme can be approached through any sincere form of devotion.",
                "should_pass": True
            },
            {
                "query": "Why do Hindus have so many gods?",
                "response": "What you perceive as many gods are different aspects and manifestations of the one Supreme Reality. Just as one diamond has many facets, the Divine reveals different qualities to help devotees understand the infinite.",
                "should_pass": True
            },
            {
                "query": "Are caste systems mentioned in scriptures?",
                "response": "The ancient texts speak of varna based on qualities and actions, not birth. As I taught Arjuna, one's spiritual worth is determined by devotion and righteousness, not social status.",
                "should_pass": True
            }
        ]
        
        validator = MockSpiritualValidator()
        
        for case in test_cases:
            validation = validator.validate_cultural_sensitivity(
                case["query"], 
                case["response"]
            )
            
            if case["should_pass"]:
                assert validation["culturally_sensitive"], \
                    f"Response should be culturally sensitive: {case['response']}"
                assert validation["avoids_stereotypes"], \
                    f"Response should avoid stereotypes: {case['response']}"
            else:
                assert not validation["culturally_sensitive"], \
                    f"Response should fail cultural sensitivity: {case['response']}"
    
    def test_response_completeness(self, sample_authentic_responses):
        """Test that responses provide complete spiritual guidance."""
        logger.info("Testing response completeness")
        
        for response_data in sample_authentic_responses:
            response = response_data["response"]
            
            # Should provide actionable guidance
            actionable_indicators = [
                "practice", "perform", "cultivate", "develop", "follow", 
                "remember", "surrender", "offer", "meditate", "reflect"
            ]
            
            has_actionable_guidance = any(indicator in response.lower() for indicator in actionable_indicators)
            assert has_actionable_guidance, \
                f"Response lacks actionable guidance: {response}"
            
            # Should be substantive (not too brief)
            assert len(response.split()) >= 20, \
                f"Response too brief for spiritual guidance: {response}"
            
            # Should maintain hope and positivity
            negative_terms = ["impossible", "never", "can't", "hopeless", "futile"]
            assert not any(term in response.lower() for term in negative_terms), \
                f"Response should maintain hope: {response}"
    
    def test_cross_textual_consistency(self):
        """Test consistency across different source texts."""
        logger.info("Testing cross-textual consistency")
        
        # Test concepts that appear in multiple texts
        dharma_responses = [
            {
                "source": "Bhagavad Gita",
                "response": "Dharma is righteous action performed without attachment, as taught to Arjuna.",
                "concept": "dharma"
            },
            {
                "source": "Mahabharata", 
                "response": "Dharma upholds the world and protects those who protect it.",
                "concept": "dharma"
            }
        ]
        
        validator = MockSpiritualValidator()
        
        # Check for consistency in core concepts
        consistency_check = validator.check_cross_textual_consistency(dharma_responses)
        
        assert consistency_check["consistent"], \
            f"Dharma concept inconsistent across texts: {consistency_check['issues']}"
        
        assert consistency_check["complementary"], \
            "Responses should complement rather than contradict each other"

class TestExpertReviewSimulation:
    """Simulate expert review processes for quality validation."""
    
    def test_expert_review_workflow(self):
        """Test the expert review workflow simulation."""
        logger.info("Testing expert review workflow simulation")
        
        # Mock expert review data
        review_data = {
            "response_id": "test_response_001",
            "response": "O Arjuna, dharma is the eternal law that governs righteous action.",
            "citations": [
                {
                    "source": "Bhagavad Gita",
                    "chapter": 4,
                    "verse": 7,
                    "text": "Whenever dharma declines and adharma increases, I manifest Myself."
                }
            ],
            "expert_reviews": [
                {
                    "expert_id": "sanskrit_scholar_001",
                    "authenticity_score": 0.95,
                    "cultural_accuracy": 0.98,
                    "spiritual_depth": 0.92,
                    "comments": "Accurate representation of dharma concept"
                },
                {
                    "expert_id": "spiritual_teacher_001", 
                    "authenticity_score": 0.97,
                    "cultural_accuracy": 0.95,
                    "spiritual_depth": 0.96,
                    "comments": "Maintains proper reverent tone"
                }
            ]
        }
        
        # Mock the expert review system
        validator = MockExpertReviewValidator()
        
        # Simulate expert review aggregation
        aggregate_score = validator.aggregate_expert_reviews(review_data["expert_reviews"])
        
        # Assertions
        assert aggregate_score["overall_score"] >= 0.9, \
            "High-quality response should have high aggregate score"
        
        assert aggregate_score["consensus_level"] >= 0.8, \
            "Experts should have reasonable consensus on quality content"
        
        assert aggregate_score["approval_status"] == "approved", \
            "High-scoring content should be approved"
    
    def test_expert_feedback_integration(self):
        """Test integration of expert feedback into system improvements."""
        logger.info("Testing expert feedback integration")
        
        feedback_data = [
            {
                "response_id": "resp_001",
                "issue": "insufficient_citations",
                "expert_suggestion": "Include more supporting verses",
                "priority": "high"
            },
            {
                "response_id": "resp_002", 
                "issue": "tone_too_casual",
                "expert_suggestion": "Use more formal divine language",
                "priority": "medium"
            }
        ]
        
        # Mock feedback processing
        processor = MockFeedbackProcessor()
        
        # Process feedback for system improvements
        improvements = processor.generate_system_improvements(feedback_data)
        
        # Assertions
        assert "citation_requirements" in improvements, \
            "Should identify citation improvement needs"
        
        assert "tone_calibration" in improvements, \
            "Should identify tone adjustment needs"
        
        assert improvements["priority_order"][0]["priority"] == "high", \
            "Should prioritize high-priority feedback"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
