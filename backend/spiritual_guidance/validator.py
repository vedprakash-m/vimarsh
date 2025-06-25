"""
Spiritual response validation system for maintaining authenticity and appropriateness.

This module provides comprehensive validation of spiritual guidance responses to ensure
they maintain divine dignity, cultural sensitivity, and scriptural accuracy.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation checks."""
    SPIRITUAL_AUTHENTICITY = "spiritual_authenticity"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    DIVINE_DIGNITY = "divine_dignity"
    SCRIPTURAL_ACCURACY = "scriptural_accuracy"
    LANGUAGE_APPROPRIATENESS = "language_appropriateness"
    SAFETY_CONTENT = "safety_content"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    category: ValidationCategory
    level: ValidationLevel
    message: str
    suggestion: Optional[str] = None
    score_impact: float = 0.0


class SpiritualResponseValidator:
    """
    Comprehensive validator for spiritual guidance responses.
    
    Ensures all responses maintain appropriate spiritual tone, cultural sensitivity,
    divine dignity, and factual accuracy according to sacred texts.
    """
    
    def __init__(self):
        """Initialize the spiritual response validator."""
        self.validation_rules = self._load_validation_rules()
        self.cultural_guidelines = self._load_cultural_guidelines()
        self.safety_patterns = self._load_safety_patterns()
        
        logger.info("SpiritualResponseValidator initialized")
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """
        Load validation rules for spiritual response checking.
        
        Returns:
            Dictionary of validation rules organized by category
        """
        return {
            ValidationCategory.SPIRITUAL_AUTHENTICITY: {
                "required_elements": [
                    "dharma_reference",
                    "scriptural_grounding",
                    "divine_compassion",
                    "practical_guidance"
                ],
                "prohibited_elements": [
                    "material_promises",
                    "exclusive_claims",
                    "oversimplification",
                    "human_ego_attribution"
                ],
                "tone_requirements": [
                    "compassionate",
                    "wise",
                    "humble",
                    "encouraging"
                ]
            },
            
            ValidationCategory.CULTURAL_SENSITIVITY: {
                "respectful_terms": [
                    "dharma", "karma", "moksha", "bhakti",
                    "देव", "भगवान", "प्रभु", "गुरु"
                ],
                "avoid_terms": [
                    "cult", "mythology", "primitive",
                    "superstition", "backward"
                ],
                "pronunciation_guidance": {
                    "sanskrit_terms": True,
                    "proper_transliteration": True
                }
            },
            
            ValidationCategory.DIVINE_DIGNITY: {
                "appropriate_references": [
                    "Lord Krishna", "भगवान श्रीकृष्ण",
                    "Supreme Divine", "परम पुरुष"
                ],
                "inappropriate_references": [
                    "god", "deity", "character",
                    "myth", "legend", "story"
                ],
                "tone_maintenance": [
                    "reverent", "dignified", "appropriate",
                    "never_casual", "never_dismissive"
                ]
            },
            
            ValidationCategory.SCRIPTURAL_ACCURACY: {
                "verified_sources": [
                    "Bhagavad Gita", "Srimad Bhagavatam",
                    "Mahabharata", "Upanishads"
                ],
                "citation_requirements": [
                    "chapter_verse_reference",
                    "context_appropriate",
                    "translation_accurate"
                ],
                "interpretation_guidelines": [
                    "traditional_understanding",
                    "scholarly_consensus",
                    "expert_validated"
                ]
            }
        }
    
    def _load_cultural_guidelines(self) -> Dict[str, Any]:
        """
        Load cultural sensitivity guidelines for different contexts.
        
        Returns:
            Cultural guidelines for respectful spiritual communication
        """
        return {
            "sanskrit_terms": {
                "use_original": True,
                "provide_translation": True,
                "correct_pronunciation": True,
                "context_explanation": True
            },
            
            "religious_diversity": {
                "respect_all_paths": True,
                "avoid_exclusivity": True,
                "universal_principles": True,
                "interfaith_harmony": True
            },
            
            "cultural_context": {
                "indian_traditions": "respect_and_honor",
                "western_audience": "explain_cultural_context",
                "global_perspective": "universal_spiritual_truths"
            }
        }
    
    def _load_safety_patterns(self) -> Dict[str, List[str]]:
        """
        Load safety patterns to detect inappropriate content.
        
        Returns:
            Dictionary of safety patterns for content filtering
        """
        return {
            "harmful_advice": [
                r"abandon.{0,20}family",
                r"leave.{0,20}responsibilities",
                r"ignore.{0,20}health",
                r"avoid.{0,20}medical"
            ],
            
            "financial_exploitation": [
                r"donate.{0,20}money",
                r"pay.{0,20}fee",
                r"purchase.{0,20}blessing",
                r"financial.{0,20}offering"
            ],
            
            "medical_claims": [
                r"cure.{0,20}disease",
                r"heal.{0,20}illness",
                r"replace.{0,20}medicine",
                r"spiritual.{0,20}treatment"
            ],
            
            "inappropriate_predictions": [
                r"will.{0,20}happen",
                r"future.{0,20}events",
                r"specific.{0,20}outcome",
                r"guarantee.{0,20}result"
            ]
        }
    
    async def validate_response(
        self,
        response: str,
        language: str,
        query_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of spiritual guidance response.
        
        Args:
            response: Generated spiritual response to validate
            language: Language of the response
            query_context: Optional context from the original query
            
        Returns:
            Comprehensive validation results with score and recommendations
        """
        try:
            validation_results = {
                "overall_score": 0.0,
                "is_approved": False,
                "validation_checks": [],
                "recommendations": [],
                "category_scores": {},
                "critical_issues": [],
                "language": language,
                "timestamp": None  # Will be set by caller
            }
            
            # Run all validation checks
            checks = [
                await self._check_spiritual_authenticity(response, language),
                await self._check_cultural_sensitivity(response, language),
                await self._check_divine_dignity(response, language),
                await self._check_scriptural_accuracy(response, language),
                await self._check_language_appropriateness(response, language),
                await self._check_safety_content(response, language)
            ]
            
            # Flatten results and categorize
            all_checks = []
            for check_list in checks:
                all_checks.extend(check_list)
            
            validation_results["validation_checks"] = all_checks
            
            # Calculate category scores
            for category in ValidationCategory:
                category_checks = [c for c in all_checks if c.category == category]
                if category_checks:
                    category_score = self._calculate_category_score(category_checks)
                    validation_results["category_scores"][category.value] = category_score
            
            # Identify critical issues
            critical_issues = [c for c in all_checks if c.level == ValidationLevel.CRITICAL]
            validation_results["critical_issues"] = [c.message for c in critical_issues]
            
            # Calculate overall score
            validation_results["overall_score"] = self._calculate_overall_score(
                validation_results["category_scores"]
            )
            
            # Determine approval status
            validation_results["is_approved"] = (
                validation_results["overall_score"] >= 0.7 and
                len(critical_issues) == 0
            )
            
            # Generate recommendations
            validation_results["recommendations"] = self._generate_recommendations(
                all_checks, validation_results["overall_score"]
            )
            
            logger.info(f"Response validation completed: score={validation_results['overall_score']:.2f}, "
                       f"approved={validation_results['is_approved']}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "overall_score": 0.0,
                "is_approved": False,
                "error": str(e),
                "validation_checks": [],
                "recommendations": ["Review response manually due to validation error"]
            }
    
    async def _check_spiritual_authenticity(self, response: str, language: str) -> List[ValidationResult]:
        """Check spiritual authenticity of the response."""
        results = []
        
        # Check for dharma reference
        if language == "Hindi":
            dharma_terms = ["धर्म", "कर्तव्य", "नैतिकता"]
        else:
            dharma_terms = ["dharma", "duty", "righteousness", "ethics"]
        
        if not any(term.lower() in response.lower() for term in dharma_terms):
            results.append(ValidationResult(
                category=ValidationCategory.SPIRITUAL_AUTHENTICITY,
                level=ValidationLevel.WARNING,
                message="Response lacks clear dharmic guidance",
                suggestion="Include reference to dharma or righteous conduct",
                score_impact=-0.1
            ))
        
        # Check for compassionate tone
        compassion_indicators = ["dear", "beloved", "child", "प्रिय", "स्नेह"] if language == "Hindi" else ["dear", "beloved", "child"]
        if any(indicator in response.lower() for indicator in compassion_indicators):
            results.append(ValidationResult(
                category=ValidationCategory.SPIRITUAL_AUTHENTICITY,
                level=ValidationLevel.INFO,
                message="Response demonstrates appropriate compassionate tone",
                score_impact=0.05
            ))
        
        return results
    
    async def _check_cultural_sensitivity(self, response: str, language: str) -> List[ValidationResult]:
        """Check cultural sensitivity of the response."""
        results = []
        
        # Check for respectful terminology
        avoid_terms = self.validation_rules[ValidationCategory.CULTURAL_SENSITIVITY]["avoid_terms"]
        for term in avoid_terms:
            if term.lower() in response.lower():
                results.append(ValidationResult(
                    category=ValidationCategory.CULTURAL_SENSITIVITY,
                    level=ValidationLevel.ERROR,
                    message=f"Response contains culturally insensitive term: {term}",
                    suggestion=f"Replace '{term}' with more respectful terminology",
                    score_impact=-0.3
                ))
        
        return results
    
    async def _check_divine_dignity(self, response: str, language: str) -> List[ValidationResult]:
        """Check if response maintains divine dignity."""
        results = []
        
        # Check for appropriate divine references
        inappropriate_refs = self.validation_rules[ValidationCategory.DIVINE_DIGNITY]["inappropriate_references"]
        for ref in inappropriate_refs:
            if ref.lower() in response.lower():
                results.append(ValidationResult(
                    category=ValidationCategory.DIVINE_DIGNITY,
                    level=ValidationLevel.CRITICAL,
                    message=f"Response uses inappropriate divine reference: {ref}",
                    suggestion="Use reverent terms like 'Lord Krishna' or 'Supreme Divine'",
                    score_impact=-0.5
                ))
        
        return results
    
    async def _check_scriptural_accuracy(self, response: str, language: str) -> List[ValidationResult]:
        """Check scriptural accuracy and proper citations."""
        results = []
        
        # Basic check for scriptural references
        scriptural_sources = ["Gita", "Bhagavad", "Mahabharata", "Bhagavatam", "गीता"]
        has_scriptural_ref = any(source.lower() in response.lower() for source in scriptural_sources)
        
        if has_scriptural_ref:
            results.append(ValidationResult(
                category=ValidationCategory.SCRIPTURAL_ACCURACY,
                level=ValidationLevel.INFO,
                message="Response includes scriptural reference",
                score_impact=0.1
            ))
        else:
            results.append(ValidationResult(
                category=ValidationCategory.SCRIPTURAL_ACCURACY,
                level=ValidationLevel.WARNING,
                message="Response lacks scriptural grounding",
                suggestion="Include reference to sacred texts for authenticity",
                score_impact=-0.05
            ))
        
        return results
    
    async def _check_language_appropriateness(self, response: str, language: str) -> List[ValidationResult]:
        """Check language appropriateness and quality."""
        results = []
        
        # Basic language quality checks
        if len(response.strip()) < 50:
            results.append(ValidationResult(
                category=ValidationCategory.LANGUAGE_APPROPRIATENESS,
                level=ValidationLevel.WARNING,
                message="Response may be too brief for meaningful guidance",
                suggestion="Provide more comprehensive spiritual guidance",
                score_impact=-0.1
            ))
        
        if len(response) > 2000:
            results.append(ValidationResult(
                category=ValidationCategory.LANGUAGE_APPROPRIATENESS,
                level=ValidationLevel.INFO,
                message="Response is quite lengthy",
                suggestion="Consider condensing while maintaining spiritual depth"
            ))
        
        return results
    
    async def _check_safety_content(self, response: str, language: str) -> List[ValidationResult]:
        """Check for potentially harmful content."""
        results = []
        
        # Check against safety patterns
        for category, patterns in self.safety_patterns.items():
            for pattern in patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    results.append(ValidationResult(
                        category=ValidationCategory.SAFETY_CONTENT,
                        level=ValidationLevel.CRITICAL,
                        message=f"Response contains potentially harmful content: {category}",
                        suggestion="Remove harmful advice and focus on safe spiritual guidance",
                        score_impact=-0.8
                    ))
        
        return results
    
    def _calculate_category_score(self, checks: List[ValidationResult]) -> float:
        """Calculate score for a validation category."""
        if not checks:
            return 0.8  # Default score for categories with no checks
        
        base_score = 0.8
        total_impact = sum(check.score_impact for check in checks)
        
        return max(0.0, min(1.0, base_score + total_impact))
    
    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate overall validation score."""
        if not category_scores:
            return 0.0
        
        # Weight categories by importance
        weights = {
            ValidationCategory.SPIRITUAL_AUTHENTICITY.value: 0.25,
            ValidationCategory.CULTURAL_SENSITIVITY.value: 0.20,
            ValidationCategory.DIVINE_DIGNITY.value: 0.25,
            ValidationCategory.SCRIPTURAL_ACCURACY.value: 0.15,
            ValidationCategory.LANGUAGE_APPROPRIATENESS.value: 0.10,
            ValidationCategory.SAFETY_CONTENT.value: 0.05
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = weights.get(category, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, checks: List[ValidationResult], overall_score: float) -> List[str]:
        """Generate improvement recommendations based on validation results."""
        recommendations = []
        
        # Collect all suggestions from validation checks
        for check in checks:
            if check.suggestion and check.level in [ValidationLevel.WARNING, ValidationLevel.ERROR, ValidationLevel.CRITICAL]:
                recommendations.append(check.suggestion)
        
        # Add general recommendations based on overall score
        if overall_score < 0.5:
            recommendations.append("Response needs significant improvement in spiritual authenticity")
        elif overall_score < 0.7:
            recommendations.append("Response needs minor improvements to meet quality standards")
        elif overall_score >= 0.9:
            recommendations.append("Excellent spiritual response quality")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]  # Limit to top 5 recommendations
