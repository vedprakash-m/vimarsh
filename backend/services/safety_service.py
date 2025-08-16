"""
Safety service for content validation and filtering.
Implements basic safety checks while remaining lightweight.
"""

import logging
import re
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety validation levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    MINIMAL = "minimal"


class SafetyService:
    """Lightweight safety validation service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._safety_patterns = self._load_safety_patterns()
    
    def _load_safety_patterns(self) -> Dict[str, List[str]]:
        """Load basic safety patterns to check for"""
        return {
            "inappropriate_content": [
                r"explicit sexual content",
                r"violence",
                r"hate speech",
                r"illegal activities"
            ],
            "medical_advice": [
                r"medical diagnosis",
                r"medical treatment",
                r"cure guarantee",
                r"drug recommendation"
            ],
            "financial_advice": [
                r"investment advice",
                r"stock tips",
                r"guaranteed returns",
                r"financial predictions"
            ],
            "legal_advice": [
                r"legal advice",
                r"legal recommendation",
                r"lawsuit guidance"
            ]
        }
    
    def validate_content(
        self, 
        content: str, 
        personality_id: str = "general",
        safety_level: SafetyLevel = SafetyLevel.MODERATE
    ) -> Dict[str, Any]:
        """
        Validate content for safety concerns.
        
        Args:
            content: Content to validate
            personality_id: ID of personality (for context)
            safety_level: Level of safety validation to apply
            
        Returns:
            Dict with validation results
        """
        try:
            warnings = []
            blocked_patterns = []
            
            # Check for blocked patterns
            for category, patterns in self._safety_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content.lower()):
                        blocked_patterns.append(pattern)
                        warnings.append(f"Content contains {category}: {pattern}")
            
            # Calculate safety score
            safety_score = max(0.0, 1.0 - (len(blocked_patterns) * 0.2))
            
            # Determine if content passes safety check
            safety_passed = len(blocked_patterns) == 0 and safety_score >= 0.7
            
            # Length validation
            max_length = 1000  # Default max length
            length_valid = len(content) <= max_length
            
            if not length_valid:
                warnings.append(f"Content too long: {len(content)} > {max_length}")
            
            result = {
                "safety_passed": safety_passed and length_valid,
                "safety_score": safety_score,
                "warnings": warnings,
                "blocked_patterns": blocked_patterns,
                "length_valid": length_valid,
                "content_length": len(content),
                "safety_level": safety_level.value,
                "personality_id": personality_id,
                "service_version": "safety_v1.0"
            }
            
            if not safety_passed:
                self.logger.warning(f"Safety validation failed for {personality_id}: {warnings}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Safety validation error: {e}")
            return {
                "safety_passed": False,
                "safety_score": 0.0,
                "warnings": [f"Safety validation error: {str(e)}"],
                "blocked_patterns": [],
                "length_valid": False,
                "error": str(e)
            }
    
    def get_safe_fallback_response(self, personality_id: str) -> str:
        """Get a safe fallback response when content is blocked"""
        fallback_responses = {
            "krishna": "Beloved devotee, please ask me something more appropriate for spiritual guidance. I am here to help you on your dharmic path with wisdom from the scriptures.",
            "buddha": "Dear friend, perhaps you could rephrase your question in a way that seeks wisdom and reduces suffering. I am here to guide you toward peace and enlightenment.",
            "jesus_christ": "Beloved child, please ask me something that aligns with love and compassion. I am here to share God's love and wisdom with you.",
            "rumi": "Beloved, let us speak of love and divine mysteries instead. I am here to guide you on the path of spiritual union.",
            "albert_einstein": "My friend, please ask me something related to science, curiosity, or the wonders of the universe. I'm here to explore knowledge with you.",
            "abraham_lincoln": "My fellow citizen, please ask me something about leadership, unity, or democratic principles. I'm here to share wisdom about governance and human dignity.",
            "marcus_aurelius": "My friend, let us focus on virtue, wisdom, and what we can control. I am here to share Stoic principles for better living.",
            "lao_tzu": "Dear seeker, let us speak of the natural way and harmony with the Tao. I am here to guide you toward effortless wisdom.",
            "isaac_newton": "My colleague, please ask me about scientific principles, mathematics, or natural laws. I am here to explore the workings of the universe.",
            "chanakya": "My student, let us discuss strategy, governance, or practical wisdom. I am here to share insights about effective leadership.",
            "confucius": "My friend, please ask me about virtue, ethics, or proper conduct. I am here to guide you toward moral excellence.",
            "nikola_tesla": "My fellow inventor, let us discuss innovation, electricity, or future possibilities. I am here to explore technological advancement.",
            "leonardo_da_vinci": "My friend, please ask me about art, science, or human potential. I am here to explore the Renaissance spirit of discovery.",
            "archimedes": "My colleague, let us discuss mathematics, physics, or engineering principles. I am here to share insights about natural laws.",
            "socrates": "My friend, let us engage in meaningful dialogue and questioning. I am here to help you examine life and seek truth.",
            "plato": "My student, please ask me about philosophy, justice, or the nature of reality. I am here to guide you toward wisdom.",
            "aristotle": "My pupil, let us discuss logic, ethics, or systematic thinking. I am here to share practical wisdom.",
            "sigmund_freud": "My patient, please ask me about psychology, human behavior, or the mind. I am here to explore the depths of consciousness.",
            "benjamin_franklin": "My friend, let us discuss practical wisdom, diplomacy, or innovation. I am here to share insights about effective living.",
            "martin_luther_king_jr": "My brother or sister, please ask me about justice, equality, or peaceful change. I am here to share wisdom about civil rights.",
            "george_washington": "My fellow citizen, let us discuss leadership, integrity, or nation-building. I am here to share wisdom about principled governance.",
            "mahatma_gandhi": "My friend, please ask me about non-violence, truth, or social transformation. I am here to guide you toward peaceful change.",
            "swami_vivekananda": "My friend, let us discuss spiritual wisdom, Eastern philosophy, or universal truth. I am here to bridge spiritual traditions.",
            "william_shakespeare": "My friend, please ask me about human nature, literature, or the human condition. I am here to explore the depths of existence.",
            "rabindranath_tagore": "My friend, let us discuss poetry, education, or universal humanity. I am here to share wisdom about art and life."
        }
        
        return fallback_responses.get(
            personality_id, 
            "Please ask me something more appropriate. I'm here to provide helpful and constructive guidance."
        )
    
    def is_query_appropriate(self, query: str, personality_id: str = "general") -> bool:
        """Quick check if a query is appropriate"""
        validation = self.validate_content(query, personality_id)
        return validation["safety_passed"]
