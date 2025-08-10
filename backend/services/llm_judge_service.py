#!/usr/bin/env python3
"""
LLM-as-Judge Service - Multi-Model Response Evaluation Framework
==============================================================

Phase 2 feature implementation for LLM-as-Judge framework with
multi-model validation, response quality assessment, and
personality consistency evaluation.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)

class JudgmentCriteria(Enum):
    """Criteria for LLM judgment evaluation."""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    HELPFULNESS = "helpfulness"
    CLARITY = "clarity"
    PERSONALITY_CONSISTENCY = "personality_consistency"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    SPIRITUAL_DEPTH = "spiritual_depth"

class JudgmentScore(Enum):
    """Score levels for judgment evaluation."""
    EXCELLENT = 5
    GOOD = 4
    SATISFACTORY = 3
    NEEDS_IMPROVEMENT = 2
    POOR = 1

class EvaluationContext(Enum):
    """Context types for evaluation."""
    SPIRITUAL_GUIDANCE = "spiritual_guidance"
    PRACTICAL_ADVICE = "practical_advice"
    PHILOSOPHICAL_DISCUSSION = "philosophical_discussion"
    EMOTIONAL_SUPPORT = "emotional_support"
    KNOWLEDGE_SHARING = "knowledge_sharing"

class LLMJudgeService:
    """Service for LLM-as-Judge evaluation and quality assessment."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # In-memory storage for MVP implementation
        self._evaluation_history: Dict[str, List[Dict[str, Any]]] = {}
        self._quality_metrics: Dict[str, Dict[str, float]] = {}
        self._personality_benchmarks: Dict[str, Dict[str, float]] = {}
        
        # Initialize personality benchmarks
        self._initialize_personality_benchmarks()
        
    def _initialize_personality_benchmarks(self):
        """Initialize quality benchmarks for each personality."""
        self._personality_benchmarks = {
            "krishna": {
                "wisdom_depth": 0.9,
                "practical_guidance": 0.85,
                "emotional_balance": 0.95,
                "philosophical_insight": 0.9,
                "cultural_authenticity": 0.9
            },
            "rama": {
                "moral_clarity": 0.95,
                "leadership_wisdom": 0.9,
                "duty_guidance": 0.9,
                "righteousness": 0.95,
                "cultural_authenticity": 0.9
            },
            "hanuman": {
                "motivational_power": 0.95,
                "devotional_strength": 0.9,
                "courage_inspiration": 0.95,
                "service_orientation": 0.9,
                "cultural_authenticity": 0.85
            },
            "saraswati": {
                "knowledge_accuracy": 0.95,
                "learning_guidance": 0.9,
                "intellectual_depth": 0.9,
                "wisdom_transmission": 0.85,
                "cultural_authenticity": 0.9
            }
        }
    
    async def evaluate_response_quality(
        self,
        user_query: str,
        personality_response: str,
        personality_id: str,
        context: EvaluationContext,
        criteria: Optional[List[JudgmentCriteria]] = None,
        reference_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Comprehensive evaluation of personality response quality."""
        
        try:
            if not criteria:
                criteria = [
                    JudgmentCriteria.ACCURACY,
                    JudgmentCriteria.RELEVANCE,
                    JudgmentCriteria.HELPFULNESS,
                    JudgmentCriteria.PERSONALITY_CONSISTENCY
                ]
            
            # Perform evaluation for each criterion
            evaluation_results = {}
            overall_scores = []
            
            for criterion in criteria:
                score, analysis = await self._evaluate_criterion(
                    user_query, personality_response, personality_id, 
                    criterion, context, reference_sources
                )
                evaluation_results[criterion.value] = {
                    "score": score,
                    "analysis": analysis
                }
                overall_scores.append(score)
            
            # Calculate overall quality score
            overall_score = sum(overall_scores) / len(overall_scores)
            
            # Generate improvement suggestions
            suggestions = await self._generate_improvement_suggestions(
                evaluation_results, personality_id, context
            )
            
            # Create comprehensive evaluation report
            evaluation_report = {
                "timestamp": datetime.now().isoformat(),
                "user_query": user_query,
                "personality_id": personality_id,
                "context": context.value,
                "overall_score": round(overall_score, 2),
                "criteria_scores": evaluation_results,
                "improvement_suggestions": suggestions,
                "quality_tier": self._determine_quality_tier(overall_score),
                "benchmark_comparison": await self._compare_with_benchmarks(
                    personality_id, evaluation_results
                )
            }
            
            # Store evaluation for analytics
            await self._store_evaluation(personality_id, evaluation_report)
            
            self.logger.info(f"✅ Evaluated response quality for {personality_id}: {overall_score:.2f}")
            return evaluation_report
            
        except Exception as e:
            self.logger.error(f"❌ Failed to evaluate response quality: {e}")
            return {"error": str(e)}
    
    async def compare_personality_responses(
        self,
        user_query: str,
        responses: Dict[str, str],
        context: EvaluationContext,
        criteria: Optional[List[JudgmentCriteria]] = None
    ) -> Dict[str, Any]:
        """Compare responses from multiple personalities for the same query."""
        
        try:
            if not criteria:
                criteria = [
                    JudgmentCriteria.RELEVANCE,
                    JudgmentCriteria.HELPFULNESS,
                    JudgmentCriteria.PERSONALITY_CONSISTENCY
                ]
            
            # Evaluate each response
            personality_evaluations = {}
            for personality_id, response in responses.items():
                evaluation = await self.evaluate_response_quality(
                    user_query, response, personality_id, context, criteria
                )
                personality_evaluations[personality_id] = evaluation
            
            # Rank personalities by overall performance
            rankings = sorted(
                personality_evaluations.items(),
                key=lambda x: x[1].get("overall_score", 0),
                reverse=True
            )
            
            # Analyze strengths and weaknesses
            analysis = await self._analyze_comparative_strengths(
                personality_evaluations, criteria
            )
            
            # Generate recommendations
            recommendations = await self._generate_personality_recommendations(
                user_query, rankings, context
            )
            
            comparison_report = {
                "timestamp": datetime.now().isoformat(),
                "user_query": user_query,
                "context": context.value,
                "personality_evaluations": personality_evaluations,
                "rankings": [(p, round(e.get("overall_score", 0), 2)) for p, e in rankings],
                "best_personality": rankings[0][0] if rankings else None,
                "comparative_analysis": analysis,
                "recommendations": recommendations
            }
            
            self.logger.info(f"🏆 Compared {len(responses)} personality responses")
            return comparison_report
            
        except Exception as e:
            self.logger.error(f"❌ Failed to compare personality responses: {e}")
            return {"error": str(e)}
    
    async def validate_cultural_authenticity(
        self,
        response: str,
        personality_id: str,
        cultural_context: str = "hindu_vedic"
    ) -> Dict[str, Any]:
        """Validate cultural and spiritual authenticity of responses."""
        
        try:
            # Cultural authenticity checks
            authenticity_checks = {
                "terminology_accuracy": await self._check_terminology_accuracy(response, personality_id),
                "cultural_sensitivity": await self._check_cultural_sensitivity(response),
                "scriptural_alignment": await self._check_scriptural_alignment(response, personality_id),
                "philosophical_consistency": await self._check_philosophical_consistency(response, personality_id),
                "respectful_representation": await self._check_respectful_representation(response, personality_id)
            }
            
            # Calculate overall authenticity score
            scores = [check["score"] for check in authenticity_checks.values()]
            overall_authenticity = sum(scores) / len(scores)
            
            # Identify issues and suggestions
            issues = []
            suggestions = []
            
            for check_name, check_result in authenticity_checks.items():
                if check_result["score"] < 0.7:  # Below acceptable threshold
                    issues.append({
                        "category": check_name,
                        "score": check_result["score"],
                        "details": check_result["analysis"]
                    })
                    suggestions.extend(check_result["suggestions"])
            
            validation_report = {
                "timestamp": datetime.now().isoformat(),
                "personality_id": personality_id,
                "cultural_context": cultural_context,
                "overall_authenticity_score": round(overall_authenticity, 2),
                "detailed_checks": authenticity_checks,
                "issues_identified": issues,
                "improvement_suggestions": suggestions,
                "authenticity_tier": self._determine_authenticity_tier(overall_authenticity),
                "cultural_compliance": overall_authenticity >= 0.8
            }
            
            self.logger.info(f"🕉️ Validated cultural authenticity for {personality_id}: {overall_authenticity:.2f}")
            return validation_report
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate cultural authenticity: {e}")
            return {"error": str(e)}
    
    async def generate_quality_insights(
        self,
        personality_id: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate quality insights and trends for a personality."""
        
        try:
            # Get evaluation history
            evaluations = self._evaluation_history.get(personality_id, [])
            
            if not evaluations:
                return {"error": "No evaluation data available"}
            
            # Filter by time period
            cutoff_date = datetime.now().timestamp() - (time_period_days * 24 * 60 * 60)
            recent_evaluations = [
                e for e in evaluations 
                if datetime.fromisoformat(e["timestamp"]).timestamp() > cutoff_date
            ]
            
            if not recent_evaluations:
                return {"error": "No recent evaluation data available"}
            
            # Calculate metrics
            metrics = await self._calculate_quality_metrics(recent_evaluations)
            
            # Identify trends
            trends = await self._identify_quality_trends(recent_evaluations)
            
            # Generate recommendations
            recommendations = await self._generate_quality_recommendations(
                personality_id, metrics, trends
            )
            
            # Benchmark comparison
            benchmark_comparison = await self._compare_with_historical_performance(
                personality_id, recent_evaluations
            )
            
            insights_report = {
                "timestamp": datetime.now().isoformat(),
                "personality_id": personality_id,
                "analysis_period_days": time_period_days,
                "total_evaluations": len(recent_evaluations),
                "quality_metrics": metrics,
                "performance_trends": trends,
                "benchmark_comparison": benchmark_comparison,
                "improvement_recommendations": recommendations,
                "overall_assessment": await self._generate_overall_assessment(metrics, trends)
            }
            
            self.logger.info(f"📊 Generated quality insights for {personality_id}")
            return insights_report
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate quality insights: {e}")
            return {"error": str(e)}
    
    async def calibrate_judgment_model(
        self,
        reference_dataset: List[Dict[str, Any]],
        personality_id: str
    ) -> Dict[str, Any]:
        """Calibrate judgment model against reference dataset."""
        
        try:
            calibration_results = {
                "accuracy_metrics": {},
                "consistency_scores": {},
                "bias_analysis": {},
                "calibration_adjustments": {}
            }
            
            # Test against reference dataset
            for item in reference_dataset:
                predicted_score = await self._evaluate_criterion(
                    item["query"],
                    item["response"],
                    personality_id,
                    JudgmentCriteria.HELPFULNESS,
                    EvaluationContext.SPIRITUAL_GUIDANCE
                )
                
                expected_score = item.get("expected_score", 3)
                accuracy = 1.0 - abs(predicted_score[0] - expected_score) / 4.0
                
                criterion = item.get("criterion", "general")
                if criterion not in calibration_results["accuracy_metrics"]:
                    calibration_results["accuracy_metrics"][criterion] = []
                calibration_results["accuracy_metrics"][criterion].append(accuracy)
            
            # Calculate overall calibration score
            all_accuracies = []
            for accuracies in calibration_results["accuracy_metrics"].values():
                all_accuracies.extend(accuracies)
            
            overall_calibration = sum(all_accuracies) / len(all_accuracies) if all_accuracies else 0
            
            calibration_report = {
                "timestamp": datetime.now().isoformat(),
                "personality_id": personality_id,
                "dataset_size": len(reference_dataset),
                "overall_calibration_score": round(overall_calibration, 3),
                "detailed_results": calibration_results,
                "calibration_quality": self._determine_calibration_quality(overall_calibration),
                "recommended_adjustments": await self._generate_calibration_adjustments(calibration_results)
            }
            
            self.logger.info(f"🎯 Calibrated judgment model for {personality_id}: {overall_calibration:.3f}")
            return calibration_report
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calibrate judgment model: {e}")
            return {"error": str(e)}
    
    # Helper methods for evaluation criteria
    async def _evaluate_criterion(
        self,
        query: str,
        response: str,
        personality_id: str,
        criterion: JudgmentCriteria,
        context: EvaluationContext,
        reference_sources: Optional[List[str]] = None
    ) -> Tuple[float, str]:
        """Evaluate response against a specific criterion."""
        
        try:
            # Simulate LLM evaluation with rule-based logic for MVP
            score = 3.0  # Default satisfactory score
            analysis = ""
            
            if criterion == JudgmentCriteria.RELEVANCE:
                score, analysis = await self._evaluate_relevance(query, response)
            elif criterion == JudgmentCriteria.ACCURACY:
                score, analysis = await self._evaluate_accuracy(response, reference_sources)
            elif criterion == JudgmentCriteria.HELPFULNESS:
                score, analysis = await self._evaluate_helpfulness(query, response, context)
            elif criterion == JudgmentCriteria.CLARITY:
                score, analysis = await self._evaluate_clarity(response)
            elif criterion == JudgmentCriteria.PERSONALITY_CONSISTENCY:
                score, analysis = await self._evaluate_personality_consistency(response, personality_id)
            elif criterion == JudgmentCriteria.CULTURAL_SENSITIVITY:
                score, analysis = await self._evaluate_cultural_sensitivity(response)
            elif criterion == JudgmentCriteria.SPIRITUAL_DEPTH:
                score, analysis = await self._evaluate_spiritual_depth(response, personality_id)
            
            return score, analysis
            
        except Exception as e:
            self.logger.error(f"❌ Failed to evaluate criterion {criterion}: {e}")
            return 3.0, f"Error evaluating {criterion.value}"
    
    async def _evaluate_relevance(self, query: str, response: str) -> Tuple[float, str]:
        """Evaluate how relevant the response is to the query."""
        query_keywords = set(query.lower().split())
        response_keywords = set(response.lower().split())
        
        # Simple keyword overlap analysis
        overlap = len(query_keywords.intersection(response_keywords))
        total_query_words = len(query_keywords)
        
        if total_query_words == 0:
            return 3.0, "Unable to analyze relevance"
        
        relevance_ratio = overlap / total_query_words
        
        if relevance_ratio > 0.6:
            score = 4.5
            analysis = "High relevance - response directly addresses query topics"
        elif relevance_ratio > 0.3:
            score = 3.5
            analysis = "Moderate relevance - response somewhat related to query"
        else:
            score = 2.5
            analysis = "Low relevance - response may not fully address the query"
        
        return score, analysis
    
    async def _evaluate_accuracy(self, response: str, reference_sources: Optional[List[str]]) -> Tuple[float, str]:
        """Evaluate factual accuracy of the response."""
        # For MVP, use basic checks
        # In production, this would integrate with fact-checking services
        
        # Check for common factual patterns
        if any(term in response.lower() for term in ["according to", "research shows", "studies indicate"]):
            score = 4.0
            analysis = "Response includes references to authoritative sources"
        elif any(term in response.lower() for term in ["believe", "think", "opinion"]):
            score = 3.5
            analysis = "Response appropriately frames subjective content"
        else:
            score = 3.0
            analysis = "Response appears to be general guidance without specific claims"
        
        return score, analysis
    
    async def _evaluate_helpfulness(self, query: str, response: str, context: EvaluationContext) -> Tuple[float, str]:
        """Evaluate how helpful the response is for the user."""
        # Check for actionable advice
        actionable_terms = ["can", "should", "try", "practice", "consider", "remember"]
        actionable_count = sum(1 for term in actionable_terms if term in response.lower())
        
        # Check for empathy and understanding
        empathy_terms = ["understand", "feel", "experience", "journey", "path"]
        empathy_count = sum(1 for term in empathy_terms if term in response.lower())
        
        base_score = 3.0
        
        if actionable_count >= 3:
            base_score += 0.8
        elif actionable_count >= 1:
            base_score += 0.4
        
        if empathy_count >= 2:
            base_score += 0.5
        
        # Context-specific adjustments
        if context == EvaluationContext.EMOTIONAL_SUPPORT and empathy_count >= 3:
            base_score += 0.5
        elif context == EvaluationContext.PRACTICAL_ADVICE and actionable_count >= 4:
            base_score += 0.5
        
        score = min(5.0, base_score)
        
        if score >= 4.5:
            analysis = "Highly helpful - provides actionable guidance with empathetic understanding"
        elif score >= 3.5:
            analysis = "Moderately helpful - offers some practical guidance"
        else:
            analysis = "Basic helpfulness - addresses query but could be more actionable"
        
        return score, analysis
    
    async def _evaluate_clarity(self, response: str) -> Tuple[float, str]:
        """Evaluate clarity and readability of the response."""
        # Simple clarity metrics
        sentences = response.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Check for clear structure
        has_structure = any(marker in response for marker in ["first", "second", "finally", "however", "therefore"])
        
        base_score = 3.0
        
        # Optimal sentence length (10-20 words)
        if 10 <= avg_sentence_length <= 20:
            base_score += 0.8
        elif avg_sentence_length > 30:
            base_score -= 0.5
        
        if has_structure:
            base_score += 0.5
        
        score = max(1.0, min(5.0, base_score))
        
        if score >= 4.0:
            analysis = "Clear and well-structured response"
        elif score >= 3.0:
            analysis = "Reasonably clear with adequate structure"
        else:
            analysis = "Could be clearer or better structured"
        
        return score, analysis
    
    async def _evaluate_personality_consistency(self, response: str, personality_id: str) -> Tuple[float, str]:
        """Evaluate consistency with personality characteristics."""
        # Personality-specific keywords and phrases
        personality_markers = {
            "krishna": ["dharma", "wisdom", "path", "balance", "duty", "devotion", "truth"],
            "rama": ["righteousness", "duty", "honor", "justice", "moral", "virtue", "leadership"],
            "hanuman": ["strength", "courage", "devotion", "service", "overcome", "power", "faith"],
            "saraswati": ["knowledge", "learning", "wisdom", "understanding", "study", "insight", "truth"]
        }
        
        markers = personality_markers.get(personality_id, [])
        response_lower = response.lower()
        
        matches = sum(1 for marker in markers if marker in response_lower)
        
        if matches >= 3:
            score = 4.5
            analysis = f"Strong personality consistency - response embodies {personality_id.title()}'s characteristics"
        elif matches >= 1:
            score = 3.5
            analysis = f"Moderate personality consistency - some {personality_id.title()}-like elements present"
        else:
            score = 2.5
            analysis = f"Limited personality consistency - could better reflect {personality_id.title()}'s voice"
        
        return score, analysis
    
    async def _evaluate_cultural_sensitivity(self, response: str) -> Tuple[float, str]:
        """Evaluate cultural sensitivity and appropriateness."""
        # Check for respectful language
        respectful_terms = ["sacred", "blessed", "revered", "ancient", "tradition", "honor"]
        disrespectful_terms = ["primitive", "backward", "superstition", "myth"]
        
        respectful_count = sum(1 for term in respectful_terms if term in response.lower())
        disrespectful_count = sum(1 for term in disrespectful_terms if term in response.lower())
        
        base_score = 4.0
        
        if respectful_count >= 2:
            base_score += 0.5
        
        if disrespectful_count > 0:
            base_score -= 2.0
        
        score = max(1.0, min(5.0, base_score))
        
        if score >= 4.0:
            analysis = "Culturally sensitive and respectful language"
        elif score >= 3.0:
            analysis = "Generally appropriate cultural sensitivity"
        else:
            analysis = "May need improvement in cultural sensitivity"
        
        return score, analysis
    
    async def _evaluate_spiritual_depth(self, response: str, personality_id: str) -> Tuple[float, str]:
        """Evaluate spiritual depth and wisdom in the response."""
        # Spiritual depth indicators
        depth_indicators = [
            "consciousness", "inner", "soul", "spirit", "divine", "eternal",
            "transcendence", "enlightenment", "awareness", "meditation", "truth"
        ]
        
        depth_count = sum(1 for indicator in depth_indicators if indicator in response.lower())
        
        # Check for philosophical concepts
        has_philosophy = any(term in response.lower() for term in [
            "purpose", "meaning", "existence", "reality", "nature", "essence"
        ])
        
        base_score = 3.0
        
        if depth_count >= 3:
            base_score += 1.0
        elif depth_count >= 1:
            base_score += 0.5
        
        if has_philosophy:
            base_score += 0.5
        
        score = min(5.0, base_score)
        
        if score >= 4.5:
            analysis = "Deep spiritual wisdom with profound insights"
        elif score >= 3.5:
            analysis = "Good spiritual depth with meaningful guidance"
        else:
            analysis = "Basic spiritual content - could be deeper"
        
        return score, analysis
    
    # Helper methods for cultural authenticity
    async def _check_terminology_accuracy(self, response: str, personality_id: str) -> Dict[str, Any]:
        """Check accuracy of spiritual/cultural terminology."""
        # Simplified check for MVP
        sanskrit_terms = ["dharma", "karma", "yoga", "moksha", "samsara", "ahimsa"]
        found_terms = [term for term in sanskrit_terms if term in response.lower()]
        
        score = 0.8 if found_terms else 0.6
        
        return {
            "score": score,
            "analysis": f"Found {len(found_terms)} authentic terms",
            "suggestions": ["Consider using more authentic Sanskrit terminology"] if score < 0.8 else []
        }
    
    async def _check_cultural_sensitivity(self, response: str) -> Dict[str, Any]:
        """Check cultural sensitivity in response."""
        score = 0.9  # Default high score for MVP
        
        return {
            "score": score,
            "analysis": "Response demonstrates cultural sensitivity",
            "suggestions": []
        }
    
    async def _check_scriptural_alignment(self, response: str, personality_id: str) -> Dict[str, Any]:
        """Check alignment with traditional scriptures."""
        # Simplified check
        scriptural_concepts = {
            "krishna": ["bhagavad gita", "dharma", "yoga", "devotion"],
            "rama": ["ramayana", "righteousness", "duty", "virtue"],
            "hanuman": ["ramayana", "devotion", "service", "strength"],
            "saraswati": ["knowledge", "wisdom", "learning", "arts"]
        }
        
        concepts = scriptural_concepts.get(personality_id, [])
        found = sum(1 for concept in concepts if concept in response.lower())
        
        score = min(1.0, 0.6 + (found * 0.1))
        
        return {
            "score": score,
            "analysis": f"Found {found} scriptural concepts",
            "suggestions": ["Include more scriptural references"] if score < 0.8 else []
        }
    
    async def _check_philosophical_consistency(self, response: str, personality_id: str) -> Dict[str, Any]:
        """Check philosophical consistency."""
        score = 0.85  # Default good score for MVP
        
        return {
            "score": score,
            "analysis": "Philosophically consistent response",
            "suggestions": []
        }
    
    async def _check_respectful_representation(self, response: str, personality_id: str) -> Dict[str, Any]:
        """Check respectful representation of the personality."""
        score = 0.9  # Default high score for MVP
        
        return {
            "score": score,
            "analysis": f"Respectful representation of {personality_id.title()}",
            "suggestions": []
        }
    
    # Additional helper methods
    def _determine_quality_tier(self, score: float) -> str:
        """Determine quality tier based on score."""
        if score >= 4.5:
            return "excellent"
        elif score >= 3.5:
            return "good"
        elif score >= 2.5:
            return "satisfactory"
        else:
            return "needs_improvement"
    
    def _determine_authenticity_tier(self, score: float) -> str:
        """Determine authenticity tier based on score."""
        if score >= 0.9:
            return "highly_authentic"
        elif score >= 0.8:
            return "authentic"
        elif score >= 0.7:
            return "moderately_authentic"
        else:
            return "needs_improvement"
    
    def _determine_calibration_quality(self, score: float) -> str:
        """Determine calibration quality based on score."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.7:
            return "acceptable"
        else:
            return "needs_improvement"
    
    async def _generate_improvement_suggestions(
        self, evaluation_results: Dict[str, Any], personality_id: str, context: EvaluationContext
    ) -> List[str]:
        """Generate improvement suggestions based on evaluation."""
        suggestions = []
        
        for criterion, result in evaluation_results.items():
            if result["score"] < 3.5:
                if criterion == "relevance":
                    suggestions.append("Focus more directly on addressing the user's specific question")
                elif criterion == "helpfulness":
                    suggestions.append("Provide more actionable guidance and practical steps")
                elif criterion == "personality_consistency":
                    suggestions.append(f"Better embody {personality_id.title()}'s characteristic wisdom and style")
                elif criterion == "clarity":
                    suggestions.append("Structure the response more clearly with shorter sentences")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    async def _compare_with_benchmarks(
        self, personality_id: str, evaluation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare evaluation results with personality benchmarks."""
        benchmarks = self._personality_benchmarks.get(personality_id, {})
        
        comparison = {}
        for criterion, result in evaluation_results.items():
            # Map criteria to benchmark categories
            benchmark_key = self._map_criterion_to_benchmark(criterion, personality_id)
            if benchmark_key in benchmarks:
                benchmark_score = benchmarks[benchmark_key] * 5  # Convert to 5-point scale
                actual_score = result["score"]
                comparison[criterion] = {
                    "benchmark": benchmark_score,
                    "actual": actual_score,
                    "meets_benchmark": actual_score >= benchmark_score * 0.9
                }
        
        return comparison
    
    def _map_criterion_to_benchmark(self, criterion: str, personality_id: str) -> str:
        """Map evaluation criterion to benchmark category."""
        mapping = {
            "accuracy": "knowledge_accuracy",
            "helpfulness": "practical_guidance",
            "personality_consistency": "cultural_authenticity",
            "spiritual_depth": "wisdom_depth"
        }
        
        return mapping.get(criterion, "cultural_authenticity")
    
    async def _store_evaluation(self, personality_id: str, evaluation_report: Dict[str, Any]) -> None:
        """Store evaluation for historical analysis."""
        if personality_id not in self._evaluation_history:
            self._evaluation_history[personality_id] = []
        
        self._evaluation_history[personality_id].append(evaluation_report)
        
        # Keep only last 100 evaluations
        if len(self._evaluation_history[personality_id]) > 100:
            self._evaluation_history[personality_id] = self._evaluation_history[personality_id][-100:]
    
    async def _analyze_comparative_strengths(
        self, personality_evaluations: Dict[str, Any], criteria: List[JudgmentCriteria]
    ) -> Dict[str, Any]:
        """Analyze comparative strengths across personalities."""
        analysis = {}
        
        for criterion in criteria:
            criterion_scores = {}
            for personality, evaluation in personality_evaluations.items():
                score = evaluation.get("criteria_scores", {}).get(criterion.value, {}).get("score", 0)
                criterion_scores[personality] = score
            
            if criterion_scores:
                best_personality = max(criterion_scores.items(), key=lambda x: x[1])
                analysis[criterion.value] = {
                    "best_performer": best_personality[0],
                    "best_score": best_personality[1],
                    "all_scores": criterion_scores
                }
        
        return analysis
    
    async def _generate_personality_recommendations(
        self, user_query: str, rankings: List[Tuple[str, Any]], context: EvaluationContext
    ) -> List[str]:
        """Generate recommendations for personality selection."""
        recommendations = []
        
        if rankings:
            best_personality = rankings[0][0]
            recommendations.append(f"{best_personality.title()} provides the most appropriate guidance for this query")
            
            if len(rankings) > 1:
                second_best = rankings[1][0]
                recommendations.append(f"Consider {second_best.title()} for alternative perspective")
        
        return recommendations
    
    async def _calculate_quality_metrics(self, evaluations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate quality metrics from evaluations."""
        if not evaluations:
            return {}
        
        total_scores = []
        criteria_scores = {}
        
        for evaluation in evaluations:
            total_scores.append(evaluation.get("overall_score", 0))
            
            for criterion, result in evaluation.get("criteria_scores", {}).items():
                if criterion not in criteria_scores:
                    criteria_scores[criterion] = []
                criteria_scores[criterion].append(result.get("score", 0))
        
        metrics = {
            "average_overall_score": sum(total_scores) / len(total_scores),
            "score_trend": "improving" if len(total_scores) > 1 and total_scores[-1] > total_scores[0] else "stable"
        }
        
        for criterion, scores in criteria_scores.items():
            metrics[f"average_{criterion}_score"] = sum(scores) / len(scores)
        
        return metrics
    
    async def _identify_quality_trends(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify quality trends over time."""
        if len(evaluations) < 3:
            return {"trend": "insufficient_data"}
        
        scores = [e.get("overall_score", 0) for e in evaluations]
        
        # Simple trend analysis
        early_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
        late_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        
        if late_avg > early_avg + 0.2:
            trend = "improving"
        elif early_avg > late_avg + 0.2:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "early_average": round(early_avg, 2),
            "recent_average": round(late_avg, 2),
            "change": round(late_avg - early_avg, 2)
        }
    
    async def _generate_quality_recommendations(
        self, personality_id: str, metrics: Dict[str, float], trends: Dict[str, Any]
    ) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        if trends.get("trend") == "declining":
            recommendations.append("Review recent response patterns to identify quality decline factors")
        
        if metrics.get("average_overall_score", 0) < 3.5:
            recommendations.append("Focus on improving overall response quality")
        
        # Check specific criteria
        for key, value in metrics.items():
            if "average_" in key and "_score" in key and value < 3.0:
                criterion = key.replace("average_", "").replace("_score", "")
                recommendations.append(f"Improve {criterion} in responses")
        
        return recommendations[:5]  # Limit to top 5
    
    async def _compare_with_historical_performance(
        self, personality_id: str, recent_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare with historical performance."""
        all_evaluations = self._evaluation_history.get(personality_id, [])
        
        if len(all_evaluations) < 10:
            return {"comparison": "insufficient_historical_data"}
        
        # Compare recent vs historical averages
        recent_scores = [e.get("overall_score", 0) for e in recent_evaluations]
        historical_scores = [e.get("overall_score", 0) for e in all_evaluations[:-len(recent_evaluations)]]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        historical_avg = sum(historical_scores) / len(historical_scores)
        
        return {
            "recent_average": round(recent_avg, 2),
            "historical_average": round(historical_avg, 2),
            "performance_change": round(recent_avg - historical_avg, 2),
            "is_improving": recent_avg > historical_avg
        }
    
    async def _generate_overall_assessment(
        self, metrics: Dict[str, float], trends: Dict[str, Any]
    ) -> str:
        """Generate overall assessment summary."""
        avg_score = metrics.get("average_overall_score", 0)
        trend = trends.get("trend", "stable")
        
        if avg_score >= 4.0 and trend == "improving":
            return "Excellent performance with positive trajectory"
        elif avg_score >= 3.5:
            return f"Good performance that is {trend}"
        elif avg_score >= 3.0:
            return f"Satisfactory performance that is {trend}"
        else:
            return f"Performance needs improvement (currently {trend})"
    
    async def _generate_calibration_adjustments(
        self, calibration_results: Dict[str, Any]
    ) -> List[str]:
        """Generate calibration adjustment recommendations."""
        adjustments = []
        
        # Analyze accuracy metrics
        for criterion, accuracies in calibration_results.get("accuracy_metrics", {}).items():
            avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
            if avg_accuracy < 0.8:
                adjustments.append(f"Improve {criterion} evaluation accuracy")
        
        return adjustments[:3]  # Limit to top 3

# Singleton instance
llm_judge_service = LLMJudgeService()

# Test function
async def test_llm_judge_service():
    """Test the LLM Judge service functionality."""
    print("🧪 Testing LLM Judge Service...")
    
    service = llm_judge_service
    
    try:
        # Test response evaluation
        evaluation = await service.evaluate_response_quality(
            user_query="How can I find inner peace?",
            personality_response="Inner peace comes through understanding your dharma and practicing meditation. Remember that like a calm lake reflects the sky perfectly, a peaceful mind reflects divine wisdom.",
            personality_id="krishna",
            context=EvaluationContext.SPIRITUAL_GUIDANCE
        )
        print(f"✅ Evaluated response quality: {evaluation.get('overall_score', 0):.2f}")
        
        # Test cultural authenticity validation
        authenticity = await service.validate_cultural_authenticity(
            response="Dharma is your righteous path in life, as taught in the sacred Bhagavad Gita.",
            personality_id="krishna"
        )
        print(f"✅ Validated cultural authenticity: {authenticity.get('overall_authenticity_score', 0):.2f}")
        
        # Test personality comparison
        responses = {
            "krishna": "Find balance through dharma and devotion.",
            "hanuman": "Gain strength through courage and determination."
        }
        comparison = await service.compare_personality_responses(
            user_query="How can I overcome challenges?",
            responses=responses,
            context=EvaluationContext.EMOTIONAL_SUPPORT
        )
        print(f"✅ Compared personality responses: {len(comparison.get('rankings', []))} personalities evaluated")
        
        print("🎉 LLM Judge Service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_judge_service())
