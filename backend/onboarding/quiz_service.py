"""
Personality Quiz Service for Vimarsh Onboarding
Processes quiz responses and calculates personality matches using domain scoring.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PersonalityQuizService:
    """Service for processing quiz responses and matching personalities"""
    
    # Personality-to-domain mapping
    PERSONALITY_DOMAINS = {
        "spiritual": ["krishna", "buddha", "jesus", "rumi", "swami_vivekananda"],
        "scientific": ["einstein", "newton", "tesla", "archimedes", "leonardo"],
        "philosophical": ["marcus_aurelius", "lao_tzu", "confucius", "aristotle", "plato", "socrates"],
        "leadership": ["chanakya", "lincoln", "gandhi", "washington", "mlk", "franklin"],
        "literary": ["tagore", "shakespeare"],
        "psychology": ["freud"]
    }
    
    # Reverse mapping for quick lookup
    DOMAIN_BY_PERSONALITY = {}
    for domain, personalities in PERSONALITY_DOMAINS.items():
        for p in personalities:
            DOMAIN_BY_PERSONALITY[p] = domain
    
    def __init__(self):
        """Initialize quiz service with questions from JSON file"""
        self.questions = []
        self.personality_profiles = {}
        self.domain_descriptions = {}
        self._load_quiz_data()
    
    def _load_quiz_data(self):
        """Load quiz questions and personality profiles from JSON"""
        try:
            quiz_file = Path(__file__).parent / "quiz_questions.json"
            with open(quiz_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = data.get("questions", [])
                self.personality_profiles = data.get("personality_profiles", {})
                self.domain_descriptions = data.get("domain_descriptions", {})
            logger.info(f"✅ Loaded {len(self.questions)} quiz questions")
        except Exception as e:
            logger.error(f"❌ Failed to load quiz questions: {e}")
            self.questions = []
    
    def get_questions(self) -> List[Dict[str, Any]]:
        """Get all quiz questions"""
        return self.questions
    
    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific question by ID"""
        for question in self.questions:
            if question["id"] == question_id:
                return question
        return None
    
    def get_option(self, question: Dict[str, Any], option_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific option from a question"""
        for option in question.get("options", []):
            if option["id"] == option_id:
                return option
        return None
    
    def calculate_domain_scores(self, responses: List[Dict[str, str]]) -> Dict[str, float]:
        """
        Calculate domain scores from quiz responses.
        
        Args:
            responses: List of {question_id: str, selected_option: str}
            
        Returns:
            Dict mapping domain names to normalized scores (0-1)
        """
        domain_scores = defaultdict(int)
        
        for response in responses:
            question_id = response.get("question_id")
            selected_option = response.get("selected_option")
            
            question = self.get_question(question_id)
            if not question:
                logger.warning(f"Question not found: {question_id}")
                continue
                
            option = self.get_option(question, selected_option)
            if not option:
                logger.warning(f"Option not found: {selected_option} for question {question_id}")
                continue
            
            # Add weights from selected option
            weights = option.get("weights", {})
            for domain, weight in weights.items():
                domain_scores[domain] += weight
        
        # Normalize scores
        total = sum(domain_scores.values())
        if total > 0:
            normalized = {domain: score / total for domain, score in domain_scores.items()}
        else:
            # Equal distribution if no valid responses
            all_domains = list(self.PERSONALITY_DOMAINS.keys())
            normalized = {domain: 1.0 / len(all_domains) for domain in all_domains}
        
        return normalized
    
    def _get_personality_hints_from_responses(self, responses: List[Dict[str, str]]) -> Dict[str, int]:
        """Count personality hints from all responses"""
        hint_counts = defaultdict(int)
        
        for response in responses:
            question = self.get_question(response.get("question_id"))
            if not question:
                continue
            option = self.get_option(question, response.get("selected_option"))
            if not option:
                continue
            
            for personality in option.get("personality_hints", []):
                hint_counts[personality] += 1
        
        return dict(hint_counts)
    
    def _select_primary_personality(
        self, 
        top_domain: str, 
        domain_scores: Dict[str, float],
        personality_hints: Dict[str, int]
    ) -> str:
        """
        Select the best personality from the top domain.
        Uses personality hints and domain scores to pick the most suitable match.
        """
        domain_personalities = self.PERSONALITY_DOMAINS.get(top_domain, [])
        
        if not domain_personalities:
            # Fallback to krishna if domain not found
            return "krishna"
        
        # Score each personality in the domain
        personality_scores = {}
        for personality in domain_personalities:
            score = 0
            # Add hint count (weighted heavily)
            score += personality_hints.get(personality, 0) * 2
            # Add domain score as base
            score += domain_scores.get(top_domain, 0)
            personality_scores[personality] = score
        
        # Return personality with highest score
        if personality_scores:
            return max(personality_scores, key=personality_scores.get)
        
        # Fallback to first personality in domain
        return domain_personalities[0]
    
    def _select_secondary_personality(
        self, 
        primary: str, 
        domain_scores: Dict[str, float],
        personality_hints: Dict[str, int]
    ) -> str:
        """Select a secondary personality from a different domain"""
        primary_domain = self.DOMAIN_BY_PERSONALITY.get(primary)
        
        # Get second-highest domain
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        for domain, score in sorted_domains:
            if domain != primary_domain:
                # Pick best personality from this domain
                domain_personalities = self.PERSONALITY_DOMAINS.get(domain, [])
                if domain_personalities:
                    # Use hints to pick best one
                    best = max(
                        domain_personalities,
                        key=lambda p: personality_hints.get(p, 0)
                    )
                    return best
        
        # Fallback
        return "einstein" if primary != "einstein" else "buddha"
    
    def calculate_personality_match(
        self, 
        responses: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Calculate the best personality match from quiz responses.
        
        Args:
            responses: List of {question_id: str, selected_option: str}
            
        Returns:
            PersonalityMatch with primary, secondary, scores, and reasoning
        """
        # Calculate domain scores
        domain_scores = self.calculate_domain_scores(responses)
        
        # Get personality hints from responses
        personality_hints = self._get_personality_hints_from_responses(responses)
        
        # Find top domain
        top_domain = max(domain_scores, key=domain_scores.get)
        
        # Select primary personality
        primary = self._select_primary_personality(
            top_domain, domain_scores, personality_hints
        )
        
        # Select secondary personality from different domain
        secondary = self._select_secondary_personality(
            primary, domain_scores, personality_hints
        )
        
        # Get profile info for primary personality
        profile = self.personality_profiles.get(primary, {})
        
        # Build match result
        match_result = {
            "primary": primary,
            "secondary": secondary,
            "primary_domain": top_domain,
            "match_score": domain_scores.get(top_domain, 0),
            "domain_scores": domain_scores,
            "match_title": profile.get("match_title", "Your Wisdom Guide"),
            "reasoning": profile.get(
                "match_description", 
                f"Based on your responses, {primary} is your ideal wisdom guide."
            ),
            "first_message_suggestion": profile.get(
                "first_message_suggestion",
                f"What wisdom can you share with me today?"
            ),
            "domain_description": self.domain_descriptions.get(top_domain, ""),
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"🎯 Personality match calculated: {primary} (domain: {top_domain})")
        return match_result
    
    def validate_responses(self, responses: List[Dict[str, str]]) -> tuple[bool, str]:
        """
        Validate quiz responses.
        
        Returns:
            (is_valid, error_message)
        """
        if not responses:
            return False, "No responses provided"
        
        if len(responses) < len(self.questions):
            return False, f"Incomplete quiz: {len(responses)}/{len(self.questions)} questions answered"
        
        for response in responses:
            if "question_id" not in response or "selected_option" not in response:
                return False, "Invalid response format"
            
            question = self.get_question(response["question_id"])
            if not question:
                return False, f"Unknown question: {response['question_id']}"
            
            option = self.get_option(question, response["selected_option"])
            if not option:
                return False, f"Invalid option: {response['selected_option']}"
        
        return True, ""


# Singleton instance
_quiz_service = None

def get_quiz_service() -> PersonalityQuizService:
    """Get singleton quiz service instance"""
    global _quiz_service
    if _quiz_service is None:
        _quiz_service = PersonalityQuizService()
    return _quiz_service
