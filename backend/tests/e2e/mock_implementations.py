"""
Mock implementations for testing without full infrastructure.

This module provides lightweight mocks for E2E testing
when the full system infrastructure is not available.
"""

from typing import Dict, List, Any, Optional
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class MockSpiritualGuidanceAPI:
    """Mock implementation of the spiritual guidance API for testing."""
    
    def __init__(self):
        self.responses = {
            "What is dharma?": {
                "response": "O Arjuna, dharma is the eternal law that sustains all creation. It is the righteous path that leads to liberation and inner peace, as taught in the sacred Bhagavad Gita.",
                "citations": [
                    {
                        "source": "Bhagavad Gita",
                        "chapter": 4,
                        "verse": 7,
                        "text": "Whenever dharma declines and adharma increases, I manifest Myself."
                    }
                ],
                "authenticity_score": 0.95,
                "confidence": 0.93,
                "language": "English"
            },
            "What is dharma in modern life?": {
                "response": "O Arjuna, dharma is the eternal law that sustains all creation. In your modern life, it manifests as righteous action performed without attachment to results, as I have taught in the Bhagavad Gita.",
                "citations": [
                    {
                        "source": "Bhagavad Gita",
                        "chapter": 2,
                        "verse": 47,
                        "text": "You have a right to perform your prescribed duty, but not to the fruits of action."
                    }
                ],
                "authenticity_score": 0.95,
                "confidence": 0.95,
                "language": "English"
            },
            "आधुनिक जीवन में धर्म क्या है?": {
                "response": "हे अर्जुन, धर्म वह शाश्वत नियम है जो सभी सृष्टि को धारण करता है। आपके आधुनिक जीवन में, यह बिना फल की आसक्ति के किए गए धर्मयुक्त कार्य के रूप में प्रकट होता है।",
                "citations": [
                    {
                        "source": "भगवद् गीता",
                        "chapter": 2,
                        "verse": 47,
                        "text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"
                    }
                ],
                "authenticity_score": 0.94,
                "confidence": 0.94,
                "language": "Hindi"
            }
        }
        self.conversations = {}
    
    async def process_spiritual_query(
        self, 
        query: str, 
        language: str = "English", 
        user_id: str = "test_user",
        conversation_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Mock spiritual query processing."""
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Get response or provide default
        response = self.responses.get(query, {
            "response": "I understand your spiritual inquiry, dear seeker. Let me reflect on the wisdom of the sacred texts to provide you with proper guidance.",
            "citations": [
                {
                    "source": "Bhagavad Gita",
                    "chapter": 18,
                    "verse": 66,
                    "text": "Surrender unto Me all varieties of religion and I will deliver you from all sinful reactions."
                }
            ],
            "authenticity_score": 0.90,
            "confidence": 0.85,
            "language": language
        })
        
        # Add conversation tracking
        conversation_id = f"conv_{user_id}_{len(self.conversations)}"
        if conversation_context:
            conversation_id = conversation_context.get("conversation_id", conversation_id)
        
        response["conversation_id"] = conversation_id
        response["user_id"] = user_id
        response["timestamp"] = "2025-06-24T19:47:00Z"
        
        # Store conversation
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append({
            "query": query,
            "response": response,
            "timestamp": response["timestamp"]
        })
        
        return response

class MockVoiceInterfaceAPI:
    """Mock implementation of the voice interface API for testing."""
    
    async def process_voice_query(
        self,
        audio_data: bytes,
        language: str = "English",
        user_id: str = "test_user"
    ) -> Dict[str, Any]:
        """Mock voice query processing."""
        
        # Simulate voice processing delay
        await asyncio.sleep(0.2)
        
        # Mock STT result
        if language == "English":
            transcribed_text = "What is dharma in modern life?"
        else:
            transcribed_text = "आधुनिक जीवन में धर्म क्या है?"
        
        # Get text response using mock API
        api = MockSpiritualGuidanceAPI()
        text_response = await api.process_spiritual_query(
            transcribed_text, language, user_id
        )
        
        # Mock TTS result
        return {
            "text_response": text_response["response"],
            "audio_response": {
                "audio_data": b"mock_audio_data_" + audio_data,
                "duration": 15.5,
                "format": "mp3"
            },
            "citations": text_response["citations"],
            "stt_result": {
                "text": transcribed_text,
                "confidence": 0.95
            },
            "authenticity_score": text_response["authenticity_score"]
        }

class MockSpiritualValidator:
    """Mock implementation of spiritual content validator."""
    
    def validate_response(self, response: str, citations: List[Dict]) -> Dict[str, Any]:
        """Mock response validation."""
        
        # Check for basic spiritual authenticity indicators
        divine_terms = ["O Arjuna", "beloved", "dear", "divine", "sacred", "eternal"]
        has_divine_address = any(term.lower() in response.lower() for term in divine_terms)
        
        inappropriate_terms = [" dude", " hey", " yo ", " whatever", " yolo"]
        has_inappropriate = any(term.lower() in response.lower() for term in inappropriate_terms)
        
        has_citations = len(citations) > 0
        
        authenticity_score = 0.95 if has_divine_address and not has_inappropriate else 0.3
        tone_score = 0.95 if has_divine_address and not has_inappropriate else 0.2
        
        # Generate appropriate issues based on the response content
        issues = []
        if authenticity_score < 0.5:
            issues.append("low_authenticity")
        if has_inappropriate:
            issues.extend(["inappropriate_tone", "lack_of_reverence"])
        if not has_citations:
            issues.append("missing_citations")
        if "yolo" in response.lower():
            issues.append("colloquial_language")
        if "money" in response.lower() and "success" in response.lower():
            issues.extend(["materialistic_focus", "dismissive_of_tradition"])
        if "don't know" in response.lower():
            issues.extend(["unhelpful", "breaking_character", "lack_of_wisdom"])
        
        return {
            "is_valid": authenticity_score > 0.8 and has_citations,
            "authenticity_score": authenticity_score,
            "tone_score": tone_score,
            "citations_valid": has_citations,
            "issues": issues
        }
    
    def validate_sanskrit_usage(self, response: str) -> Dict[str, Any]:
        """Mock Sanskrit usage validation."""
        return {
            "respectful_usage": True,
            "proper_context": True,
            "issues": []
        }
    
    def validate_cultural_sensitivity(self, query: str, response: str) -> Dict[str, Any]:
        """Mock cultural sensitivity validation."""
        return {
            "culturally_sensitive": True,
            "avoids_stereotypes": True,
            "respectful_approach": True,
            "issues": []
        }
    
    def check_cross_textual_consistency(self, responses: List[Dict]) -> Dict[str, Any]:
        """Mock cross-textual consistency check."""
        return {
            "consistent": True,
            "complementary": True,
            "issues": []
        }

class MockFallbackSystem:
    """Mock implementation of fallback system."""
    
    def get_fallback_response(self, error_type: str = "general") -> Dict[str, Any]:
        """Mock fallback response generation."""
        
        fallback_responses = {
            "llm_failure": {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try your question again in a moment. The wisdom you seek remains eternal and unchanging.",
                "is_fallback": True,
                "error_type": "llm_failure"
            },
            "content_validation_failed": {
                "response": "I must reflect more deeply on your question to provide wisdom worthy of the sacred texts. Please allow me a moment to consider the eternal teachings that address your inquiry.",
                "is_fallback": True,
                "reason": "content_validation_failed"
            },
            "general": {
                "response": "I seek to provide you with the most authentic spiritual guidance. Please rephrase your question so I may better serve your spiritual journey.",
                "is_fallback": True,
                "error_type": "general"
            }
        }
        
        return fallback_responses.get(error_type, fallback_responses["general"])

class MockExpertReviewValidator:
    """Mock implementation of expert review validator."""
    
    def aggregate_expert_reviews(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Mock expert review aggregation."""
        
        if not reviews:
            return {
                "overall_score": 0.0,
                "consensus_level": 0.0,
                "approval_status": "pending"
            }
        
        # Calculate averages
        auth_scores = [r["authenticity_score"] for r in reviews]
        cultural_scores = [r["cultural_accuracy"] for r in reviews]
        spiritual_scores = [r["spiritual_depth"] for r in reviews]
        
        overall_score = (sum(auth_scores) + sum(cultural_scores) + sum(spiritual_scores)) / (3 * len(reviews))
        
        # Calculate consensus (how close the scores are)
        score_variance = sum((s - overall_score) ** 2 for s in auth_scores) / len(auth_scores)
        consensus_level = max(0, 1 - score_variance)
        
        approval_status = "approved" if overall_score >= 0.9 and consensus_level >= 0.8 else "needs_review"
        
        return {
            "overall_score": overall_score,
            "consensus_level": consensus_level,
            "approval_status": approval_status
        }

class MockFeedbackProcessor:
    """Mock implementation of feedback processor."""
    
    def generate_system_improvements(self, feedback_data: List[Dict]) -> Dict[str, Any]:
        """Mock system improvement generation based on feedback."""
        
        improvements = {
            "citation_requirements": False,
            "tone_calibration": False,
            "priority_order": []
        }
        
        for feedback in feedback_data:
            if "citation" in feedback["issue"]:
                improvements["citation_requirements"] = True
            if "tone" in feedback["issue"]:
                improvements["tone_calibration"] = True
        
        # Sort by priority
        improvements["priority_order"] = sorted(feedback_data, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
        
        return improvements
