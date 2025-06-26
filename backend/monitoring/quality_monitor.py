"""
Spiritual Quality Monitor with Application Insights Integration
Monitors and tracks spiritual content quality, persona consistency, and cultural sensitivity
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .app_insights_client import get_app_insights_client, track_spiritual_event

logger = logging.getLogger(__name__)


class SpiritualQualityLevel(Enum):
    """Spiritual quality assessment levels"""
    EXCELLENT = "excellent"    # 90-100%
    GOOD = "good"             # 70-89%
    ACCEPTABLE = "acceptable"  # 50-69%
    POOR = "poor"             # 30-49%
    UNACCEPTABLE = "unacceptable"  # 0-29%


@dataclass
class SpiritualQualityMetrics:
    """Spiritual quality assessment metrics"""
    overall_score: float           # 0.0-1.0
    persona_consistency: float     # Lord Krishna persona adherence
    spiritual_relevance: float     # Relevance to spiritual inquiry
    cultural_sensitivity: float    # Cultural and religious sensitivity
    sanskrit_accuracy: float       # Sanskrit term usage accuracy
    citation_quality: float        # Scripture citation accuracy
    reverence_level: float         # Maintaining appropriate reverence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/tracking"""
        return {
            'overall_score': self.overall_score,
            'persona_consistency': self.persona_consistency,
            'spiritual_relevance': self.spiritual_relevance,
            'cultural_sensitivity': self.cultural_sensitivity,
            'sanskrit_accuracy': self.sanskrit_accuracy,
            'citation_quality': self.citation_quality,
            'reverence_level': self.reverence_level,
            'quality_level': self.get_quality_level().value
        }
    
    def get_quality_level(self) -> SpiritualQualityLevel:
        """Get quality level based on overall score"""
        if self.overall_score >= 0.9:
            return SpiritualQualityLevel.EXCELLENT
        elif self.overall_score >= 0.7:
            return SpiritualQualityLevel.GOOD
        elif self.overall_score >= 0.5:
            return SpiritualQualityLevel.ACCEPTABLE
        elif self.overall_score >= 0.3:
            return SpiritualQualityLevel.POOR
        else:
            return SpiritualQualityLevel.UNACCEPTABLE


class SpiritualQualityMonitor:
    """Monitor and track spiritual content quality with Application Insights"""
    
    def __init__(self):
        """Initialize spiritual quality monitor"""
        self.app_insights = get_app_insights_client()
        self.quality_history: List[SpiritualQualityMetrics] = []
        
        # Quality thresholds for alerting
        self.alert_thresholds = {
            'minimum_overall_score': 0.5,
            'minimum_persona_consistency': 0.6,
            'minimum_cultural_sensitivity': 0.8,
            'minimum_reverence_level': 0.7
        }
        
        logger.info("Spiritual Quality Monitor initialized")
    
    @track_spiritual_event("spiritual_content_assessment")
    async def assess_response_quality(self, 
                                    response: str,
                                    query: str,
                                    citations: List[str] = None,
                                    user_id: str = "anonymous") -> SpiritualQualityMetrics:
        """
        Assess the spiritual quality of a response
        
        Args:
            response: The AI-generated response
            query: The original user query
            citations: List of scripture citations
            user_id: User identifier
            
        Returns:
            SpiritualQualityMetrics: Comprehensive quality assessment
        """
        try:
            # Assess different quality dimensions
            persona_score = self._assess_persona_consistency(response)
            relevance_score = self._assess_spiritual_relevance(response, query)
            cultural_score = self._assess_cultural_sensitivity(response)
            sanskrit_score = self._assess_sanskrit_accuracy(response)
            citation_score = self._assess_citation_quality(response, citations or [])
            reverence_score = self._assess_reverence_level(response)
            
            # Calculate overall score (weighted average)
            weights = {
                'persona': 0.2,
                'relevance': 0.2,
                'cultural': 0.2,
                'sanskrit': 0.15,
                'citation': 0.15,
                'reverence': 0.1
            }
            
            overall_score = (
                persona_score * weights['persona'] +
                relevance_score * weights['relevance'] +
                cultural_score * weights['cultural'] +
                sanskrit_score * weights['sanskrit'] +
                citation_score * weights['citation'] +
                reverence_score * weights['reverence']
            )
            
            # Create metrics object
            metrics = SpiritualQualityMetrics(
                overall_score=overall_score,
                persona_consistency=persona_score,
                spiritual_relevance=relevance_score,
                cultural_sensitivity=cultural_score,
                sanskrit_accuracy=sanskrit_score,
                citation_quality=citation_score,
                reverence_level=reverence_score
            )
            
            # Track metrics in Application Insights
            self._track_quality_metrics(metrics, user_id, len(response))
            
            # Check for quality alerts
            self._check_quality_alerts(metrics, user_id)
            
            # Store in history
            self.quality_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error assessing spiritual quality: {e}")
            self.app_insights.track_exception(e, {
                'operation': 'assess_response_quality',
                'user_id': user_id
            })
            
            # Return default metrics on error
            return SpiritualQualityMetrics(
                overall_score=0.5,
                persona_consistency=0.5,
                spiritual_relevance=0.5,
                cultural_sensitivity=0.5,
                sanskrit_accuracy=0.5,
                citation_quality=0.5,
                reverence_level=0.5
            )
    
    def _assess_persona_consistency(self, response: str) -> float:
        """Assess Lord Krishna persona consistency"""
        try:
            # Simple keyword-based assessment for now
            # In production, this would use more sophisticated NLP
            
            krishna_indicators = [
                'dear devotee', 'my child', 'my dear friend',
                'as i have said', 'as mentioned in', 'dharma',
                'path of righteousness', 'eternal truth'
            ]
            
            inappropriate_indicators = [
                'i am an ai', 'as an ai', 'i cannot', 'i don\'t know',
                'according to my training', 'in my database'
            ]
            
            response_lower = response.lower()
            
            # Count positive indicators
            positive_count = sum(1 for indicator in krishna_indicators 
                               if indicator in response_lower)
            
            # Count negative indicators
            negative_count = sum(1 for indicator in inappropriate_indicators 
                               if indicator in response_lower)
            
            # Calculate score
            base_score = 0.7  # Default reasonable score
            positive_boost = min(0.3, positive_count * 0.1)
            negative_penalty = min(0.5, negative_count * 0.2)
            
            score = max(0.0, min(1.0, base_score + positive_boost - negative_penalty))
            return score
            
        except Exception as e:
            logger.warning(f"Error assessing persona consistency: {e}")
            return 0.5
    
    def _assess_spiritual_relevance(self, response: str, query: str) -> float:
        """Assess spiritual relevance of response to query"""
        try:
            spiritual_terms = [
                'dharma', 'karma', 'moksha', 'atman', 'brahman',
                'meditation', 'devotion', 'bhakti', 'yoga', 'spiritual',
                'divine', 'consciousness', 'enlightenment', 'liberation'
            ]
            
            response_lower = response.lower()
            query_lower = query.lower()
            
            # Check if query is spiritual in nature
            query_spiritual = any(term in query_lower for term in spiritual_terms)
            
            # Check spiritual content in response
            response_spiritual_count = sum(1 for term in spiritual_terms 
                                         if term in response_lower)
            
            # Calculate relevance score
            if query_spiritual:
                # Query is spiritual, response should be too
                score = min(1.0, 0.5 + (response_spiritual_count * 0.1))
            else:
                # Non-spiritual query, spiritual response is still good
                score = min(1.0, 0.6 + (response_spiritual_count * 0.05))
            
            return score
            
        except Exception as e:
            logger.warning(f"Error assessing spiritual relevance: {e}")
            return 0.6
    
    def _assess_cultural_sensitivity(self, response: str) -> float:
        """Assess cultural and religious sensitivity"""
        try:
            # Check for respectful language
            respectful_terms = [
                'respectfully', 'humbly', 'with reverence', 'blessed',
                'sacred', 'holy', 'divine grace', 'eternal wisdom'
            ]
            
            # Check for potentially insensitive content
            insensitive_terms = [
                'cult', 'superstition', 'primitive', 'backward',
                'myth', 'fictional', 'made up', 'false belief'
            ]
            
            response_lower = response.lower()
            
            respectful_count = sum(1 for term in respectful_terms 
                                 if term in response_lower)
            insensitive_count = sum(1 for term in insensitive_terms 
                                  if term in response_lower)
            
            # Start with high base score for cultural sensitivity
            base_score = 0.8
            respectful_boost = min(0.2, respectful_count * 0.05)
            insensitive_penalty = min(0.6, insensitive_count * 0.3)
            
            score = max(0.0, min(1.0, base_score + respectful_boost - insensitive_penalty))
            return score
            
        except Exception as e:
            logger.warning(f"Error assessing cultural sensitivity: {e}")
            return 0.8
    
    def _assess_sanskrit_accuracy(self, response: str) -> float:
        """Assess Sanskrit term usage accuracy"""
        try:
            # Common Sanskrit terms and their context
            sanskrit_terms = [
                'dharma', 'karma', 'moksha', 'atman', 'brahman',
                'bhakti', 'yoga', 'samsara', 'nirvana', 'guru',
                'mantra', 'yantra', 'chakra', 'prana', 'ahimsa'
            ]
            
            response_lower = response.lower()
            sanskrit_count = sum(1 for term in sanskrit_terms 
                               if term in response_lower)
            
            if sanskrit_count == 0:
                # No Sanskrit terms used - neutral score
                return 0.7
            
            # For now, assume proper usage (would need NLP context analysis)
            # Score based on appropriate usage frequency
            if sanskrit_count <= 3:
                return 0.9  # Good usage
            elif sanskrit_count <= 6:
                return 0.8  # Acceptable usage
            else:
                return 0.6  # Potentially overused
            
        except Exception as e:
            logger.warning(f"Error assessing Sanskrit accuracy: {e}")
            return 0.7
    
    def _assess_citation_quality(self, response: str, citations: List[str]) -> float:
        """Assess scripture citation quality"""
        try:
            if not citations:
                # No citations provided - check if response needed them
                scripture_references = [
                    'bhagavad gita', 'gita', 'mahabharata', 'upanishads',
                    'vedas', 'srimad bhagavatam', 'ramayana', 'puranas'
                ]
                
                response_lower = response.lower()
                needs_citation = any(ref in response_lower for ref in scripture_references)
                
                if needs_citation:
                    return 0.3  # Should have citations but doesn't
                else:
                    return 0.8  # No citations needed
            
            # Citations provided - assess quality
            citation_score = 0.7  # Base score for having citations
            
            # Check citation format and completeness
            for citation in citations:
                if any(indicator in citation.lower() for indicator in ['chapter', 'verse', 'shloka']):
                    citation_score += 0.1  # Good citation format
                if len(citation) > 20:  # Reasonably detailed
                    citation_score += 0.05
            
            return min(1.0, citation_score)
            
        except Exception as e:
            logger.warning(f"Error assessing citation quality: {e}")
            return 0.6
    
    def _assess_reverence_level(self, response: str) -> float:
        """Assess appropriate reverence level"""
        try:
            reverent_indicators = [
                'blessed', 'divine', 'sacred', 'holy', 'eternal',
                'gracious', 'merciful', 'compassionate', 'wise',
                'all-knowing', 'supreme', 'lord', 'god'
            ]
            
            casual_indicators = [
                'cool', 'awesome', 'great', 'nice', 'ok', 'sure',
                'no problem', 'whatever', 'basically', 'just'
            ]
            
            response_lower = response.lower()
            
            reverent_count = sum(1 for indicator in reverent_indicators 
                               if indicator in response_lower)
            casual_count = sum(1 for indicator in casual_indicators 
                             if indicator in response_lower)
            
            # Calculate reverence score
            base_score = 0.7
            reverent_boost = min(0.3, reverent_count * 0.05)
            casual_penalty = min(0.4, casual_count * 0.1)
            
            score = max(0.0, min(1.0, base_score + reverent_boost - casual_penalty))
            return score
            
        except Exception as e:
            logger.warning(f"Error assessing reverence level: {e}")
            return 0.7
    
    def _track_quality_metrics(self, metrics: SpiritualQualityMetrics, 
                             user_id: str, response_length: int):
        """Track quality metrics in Application Insights"""
        try:
            # Track individual metrics
            metric_data = metrics.to_dict()
            
            for metric_name, value in metric_data.items():
                if isinstance(value, (int, float)):
                    self.app_insights.track_metric(
                        name=f"spiritual_quality_{metric_name}",
                        value=value,
                        properties={
                            'user_id': user_id,
                            'response_length': response_length
                        }
                    )
            
            # Track overall quality event
            self.app_insights.track_event(
                "spiritual_quality_assessment",
                properties={
                    'user_id': user_id,
                    'quality_level': metrics.get_quality_level().value,
                    'response_length': response_length
                },
                measurements=metric_data
            )
            
        except Exception as e:
            logger.error(f"Error tracking quality metrics: {e}")
    
    def _check_quality_alerts(self, metrics: SpiritualQualityMetrics, user_id: str):
        """Check for quality alerts and trigger notifications"""
        try:
            alerts = []
            
            # Check each threshold
            if metrics.overall_score < self.alert_thresholds['minimum_overall_score']:
                alerts.append(f"Overall quality below threshold: {metrics.overall_score:.2f}")
            
            if metrics.persona_consistency < self.alert_thresholds['minimum_persona_consistency']:
                alerts.append(f"Persona consistency below threshold: {metrics.persona_consistency:.2f}")
            
            if metrics.cultural_sensitivity < self.alert_thresholds['minimum_cultural_sensitivity']:
                alerts.append(f"Cultural sensitivity below threshold: {metrics.cultural_sensitivity:.2f}")
            
            if metrics.reverence_level < self.alert_thresholds['minimum_reverence_level']:
                alerts.append(f"Reverence level below threshold: {metrics.reverence_level:.2f}")
            
            # Log alerts
            if alerts:
                for alert in alerts:
                    logger.warning(f"SPIRITUAL_QUALITY_ALERT: {alert} (User: {user_id})")
                    
                    self.app_insights.track_event(
                        "spiritual_quality_alert",
                        properties={
                            'user_id': user_id,
                            'alert_message': alert,
                            'overall_score': metrics.overall_score,
                            'quality_level': metrics.get_quality_level().value
                        }
                    )
            
        except Exception as e:
            logger.error(f"Error checking quality alerts: {e}")
    
    def get_quality_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get quality summary for the specified time period"""
        try:
            if not self.quality_history:
                return {'message': 'No quality data available'}
            
            # For now, return summary of all data (time filtering would be added)
            recent_metrics = self.quality_history[-100:]  # Last 100 assessments
            
            if not recent_metrics:
                return {'message': 'No recent quality data available'}
            
            # Calculate averages
            avg_overall = sum(m.overall_score for m in recent_metrics) / len(recent_metrics)
            avg_persona = sum(m.persona_consistency for m in recent_metrics) / len(recent_metrics)
            avg_cultural = sum(m.cultural_sensitivity for m in recent_metrics) / len(recent_metrics)
            avg_reverence = sum(m.reverence_level for m in recent_metrics) / len(recent_metrics)
            
            # Count quality levels
            quality_counts = {}
            for level in SpiritualQualityLevel:
                quality_counts[level.value] = sum(
                    1 for m in recent_metrics if m.get_quality_level() == level
                )
            
            summary = {
                'period_hours': hours,
                'total_assessments': len(recent_metrics),
                'average_scores': {
                    'overall': avg_overall,
                    'persona_consistency': avg_persona,
                    'cultural_sensitivity': avg_cultural,
                    'reverence_level': avg_reverence
                },
                'quality_distribution': quality_counts,
                'alerts_triggered': sum(1 for m in recent_metrics 
                                      if m.overall_score < self.alert_thresholds['minimum_overall_score'])
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating quality summary: {e}")
            return {'error': str(e)}


# Global quality monitor instance
_quality_monitor = None

def get_quality_monitor() -> SpiritualQualityMonitor:
    """Get global quality monitor instance"""
    global _quality_monitor
    if _quality_monitor is None:
        _quality_monitor = SpiritualQualityMonitor()
    return _quality_monitor
