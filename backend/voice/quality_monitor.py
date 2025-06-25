"""
Voice Quality Monitoring and Improvement Systems

This module provides comprehensive voice quality monitoring, performance tracking,
and improvement systems for the Vimarsh platform's voice interface. It tracks
metrics like clarity, pronunciation accuracy, user satisfaction, and provides
recommendations for voice parameter optimization.
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import numpy as np

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Voice quality metrics to monitor"""
    CLARITY = "clarity"                      # How clear and understandable the voice is
    PRONUNCIATION = "pronunciation"          # Accuracy of Sanskrit/Hindi pronunciation
    NATURALNESS = "naturalness"             # How natural the speech sounds
    EMOTIONAL_TONE = "emotional_tone"       # Appropriateness of emotional delivery
    PACE = "pace"                          # Speech speed appropriateness
    VOLUME = "volume"                      # Volume level appropriateness
    INTERRUPTION_HANDLING = "interruption_handling"  # How well interruptions are handled
    USER_SATISFACTION = "user_satisfaction"  # Overall user satisfaction
    ERROR_RATE = "error_rate"              # Rate of voice processing errors
    RESPONSE_TIME = "response_time"        # Time to generate voice response


class QualityLevel(Enum):
    """Quality level categories"""
    EXCELLENT = "excellent"    # 90-100%
    GOOD = "good"             # 75-89%
    AVERAGE = "average"       # 60-74%
    POOR = "poor"            # 40-59%
    CRITICAL = "critical"     # Below 40%


class ImprovementAction(Enum):
    """Types of improvement actions"""
    ADJUST_SPEED = "adjust_speed"
    ADJUST_PITCH = "adjust_pitch"
    ADJUST_VOLUME = "adjust_volume"
    RETRAIN_PRONUNCIATION = "retrain_pronunciation"
    UPDATE_VOICE_MODEL = "update_voice_model"
    OPTIMIZE_PROCESSING = "optimize_processing"
    COLLECT_MORE_FEEDBACK = "collect_more_feedback"
    SWITCH_VOICE = "switch_voice"


@dataclass
class VoiceQualityScore:
    """Voice quality score for a specific metric"""
    metric: QualityMetric
    score: float  # 0.0 to 1.0
    level: QualityLevel
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    feedback_source: str = "system"  # "system", "user", "expert"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "metric": self.metric.value,
            "score": self.score,
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "feedback_source": self.feedback_source
        }


@dataclass
class VoicePerformanceMetrics:
    """Comprehensive voice performance metrics"""
    session_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    average_quality_score: float = 0.0
    quality_scores: List[VoiceQualityScore] = field(default_factory=list)
    user_feedback_count: int = 0
    expert_feedback_count: int = 0
    improvement_actions_taken: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_metric_average(self, metric: QualityMetric) -> float:
        """Get average score for a specific metric"""
        metric_scores = [s.score for s in self.quality_scores if s.metric == metric]
        return statistics.mean(metric_scores) if metric_scores else 0.0
    
    def get_quality_trend(self, metric: QualityMetric, hours: int = 24) -> List[float]:
        """Get quality trend for a metric over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_scores = [
            s.score for s in self.quality_scores 
            if s.metric == metric and s.timestamp > cutoff_time
        ]
        return recent_scores


class VoiceQualityAnalyzer:
    """Analyzes voice quality based on various factors"""
    
    def __init__(self):
        self.quality_thresholds = {
            QualityLevel.EXCELLENT: 0.9,
            QualityLevel.GOOD: 0.75,
            QualityLevel.AVERAGE: 0.6,
            QualityLevel.POOR: 0.4
        }
    
    def analyze_voice_output(self, 
                           audio_data: bytes, 
                           text: str, 
                           voice_settings: Dict[str, Any],
                           context: Dict[str, Any] = None) -> List[VoiceQualityScore]:
        """
        Analyze voice output quality across multiple metrics
        
        Args:
            audio_data: Generated audio data
            text: Original text that was synthesized
            voice_settings: Voice synthesis settings used
            context: Additional context (language, content type, etc.)
            
        Returns:
            List of quality scores for different metrics
        """
        scores = []
        timestamp = datetime.now()
        context = context or {}
        
        # Analyze clarity
        clarity_score = self._analyze_clarity(audio_data, text, voice_settings)
        scores.append(VoiceQualityScore(
            metric=QualityMetric.CLARITY,
            score=clarity_score,
            level=self._get_quality_level(clarity_score),
            timestamp=timestamp,
            context=context
        ))
        
        # Analyze pronunciation (especially for Sanskrit terms)
        pronunciation_score = self._analyze_pronunciation(text, voice_settings, context)
        scores.append(VoiceQualityScore(
            metric=QualityMetric.PRONUNCIATION,
            score=pronunciation_score,
            level=self._get_quality_level(pronunciation_score),
            timestamp=timestamp,
            context=context
        ))
        
        # Analyze naturalness
        naturalness_score = self._analyze_naturalness(audio_data, text, voice_settings)
        scores.append(VoiceQualityScore(
            metric=QualityMetric.NATURALNESS,
            score=naturalness_score,
            level=self._get_quality_level(naturalness_score),
            timestamp=timestamp,
            context=context
        ))
        
        # Analyze emotional tone appropriateness
        emotional_tone_score = self._analyze_emotional_tone(text, voice_settings, context)
        scores.append(VoiceQualityScore(
            metric=QualityMetric.EMOTIONAL_TONE,
            score=emotional_tone_score,
            level=self._get_quality_level(emotional_tone_score),
            timestamp=timestamp,
            context=context
        ))
        
        # Analyze pace appropriateness
        pace_score = self._analyze_pace(audio_data, text, voice_settings)
        scores.append(VoiceQualityScore(
            metric=QualityMetric.PACE,
            score=pace_score,
            level=self._get_quality_level(pace_score),
            timestamp=timestamp,
            context=context
        ))
        
        return scores
    
    def _analyze_clarity(self, audio_data: bytes, text: str, voice_settings: Dict) -> float:
        """Analyze voice clarity (simulated for now)"""
        # In a real implementation, this would use audio processing to:
        # - Measure signal-to-noise ratio
        # - Detect distortions or artifacts
        # - Analyze frequency distribution
        
        # Simulated analysis based on voice settings
        base_score = 0.8
        
        # Adjust based on speed (too fast/slow reduces clarity)
        speed = voice_settings.get("speed", 1.0)
        if 0.8 <= speed <= 1.2:
            speed_bonus = 0.1
        elif 0.6 <= speed <= 1.4:
            speed_bonus = 0.05
        else:
            speed_bonus = -0.1
        
        # Adjust based on volume
        volume = voice_settings.get("volume", 1.0)
        if 0.7 <= volume <= 1.0:
            volume_bonus = 0.05
        else:
            volume_bonus = -0.05
        
        return max(0.0, min(1.0, base_score + speed_bonus + volume_bonus))
    
    def _analyze_pronunciation(self, text: str, voice_settings: Dict, context: Dict) -> float:
        """Analyze pronunciation accuracy, especially for Sanskrit terms"""
        base_score = 0.75
        
        # Check for Sanskrit terms
        sanskrit_terms = ["om", "dharma", "karma", "moksha", "yoga", "krishna", "namaste"]
        has_sanskrit = any(term in text.lower() for term in sanskrit_terms)
        
        if has_sanskrit:
            # Sanskrit pronunciation depends on voice and language settings
            language = context.get("language", "en")
            voice_name = voice_settings.get("voice_name", "")
            
            if language == "hi" or "IN" in voice_name:
                # Indian voices should be better at Sanskrit
                base_score += 0.15
            else:
                # Non-Indian voices might struggle with Sanskrit
                base_score -= 0.1
        
        # Adjust based on content type
        content_type = context.get("content_type", "general")
        if content_type in ["scripture", "mantra", "prayer"]:
            # Religious content needs higher pronunciation accuracy
            if has_sanskrit:
                base_score += 0.05
        
        return max(0.0, min(1.0, base_score))
    
    def _analyze_naturalness(self, audio_data: bytes, text: str, voice_settings: Dict) -> float:
        """Analyze how natural the speech sounds"""
        # Simulated analysis
        base_score = 0.7
        
        # Modern TTS voices are generally more natural
        voice_name = voice_settings.get("voice_name", "")
        if "neural" in voice_name.lower() or "wavenet" in voice_name.lower():
            base_score += 0.15
        
        # Check for appropriate pauses and intonation
        text_length = len(text)
        if text_length > 100:
            # Longer texts need good pacing
            pause_duration = voice_settings.get("pause_duration", 1.0)
            if 0.8 <= pause_duration <= 1.5:
                base_score += 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _analyze_emotional_tone(self, text: str, voice_settings: Dict, context: Dict) -> float:
        """Analyze appropriateness of emotional tone"""
        base_score = 0.8
        
        content_type = context.get("content_type", "general")
        
        # Different content types need different emotional tones
        if content_type in ["prayer", "meditation", "devotional"]:
            # Should be reverent and calm
            pitch = voice_settings.get("pitch", 1.0)
            if 0.8 <= pitch <= 1.0:
                base_score += 0.1
            else:
                base_score -= 0.1
        
        elif content_type in ["teaching", "explanation"]:
            # Should be clear and authoritative
            emphasis = voice_settings.get("emphasis_strength", 1.0)
            if emphasis >= 1.0:
                base_score += 0.05
        
        elif content_type in ["comfort", "consolation"]:
            # Should be gentle and soothing
            pitch = voice_settings.get("pitch", 1.0)
            if pitch <= 1.0:
                base_score += 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _analyze_pace(self, audio_data: bytes, text: str, voice_settings: Dict) -> float:
        """Analyze speech pace appropriateness"""
        base_score = 0.75
        
        speed = voice_settings.get("speed", 1.0)
        text_length = len(text)
        
        # Adjust expectations based on text length
        if text_length < 50:
            # Short texts can be a bit faster
            if 0.9 <= speed <= 1.3:
                base_score += 0.15
        elif text_length > 200:
            # Long texts should be slower for comprehension
            if 0.7 <= speed <= 1.0:
                base_score += 0.15
        else:
            # Medium texts - normal speed
            if 0.8 <= speed <= 1.1:
                base_score += 0.15
        
        return max(0.0, min(1.0, base_score))
    
    def _get_quality_level(self, score: float) -> QualityLevel:
        """Convert score to quality level"""
        if score >= self.quality_thresholds[QualityLevel.EXCELLENT]:
            return QualityLevel.EXCELLENT
        elif score >= self.quality_thresholds[QualityLevel.GOOD]:
            return QualityLevel.GOOD
        elif score >= self.quality_thresholds[QualityLevel.AVERAGE]:
            return QualityLevel.AVERAGE
        elif score >= self.quality_thresholds[QualityLevel.POOR]:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL


class VoiceImprovementEngine:
    """Engine for generating voice improvement recommendations"""
    
    def __init__(self):
        self.improvement_rules = self._load_improvement_rules()
    
    def analyze_performance_issues(self, metrics: VoicePerformanceMetrics) -> List[Dict[str, Any]]:
        """
        Analyze performance metrics and identify issues
        
        Args:
            metrics: Voice performance metrics
            
        Returns:
            List of identified issues with recommendations
        """
        issues = []
        
        # Check overall quality
        if metrics.average_quality_score < 0.7:
            issues.append({
                "issue": "Low overall quality",
                "severity": "high",
                "metric": "overall",
                "current_score": metrics.average_quality_score,
                "target_score": 0.8,
                "recommendations": [
                    ImprovementAction.UPDATE_VOICE_MODEL,
                    ImprovementAction.OPTIMIZE_PROCESSING
                ]
            })
        
        # Check specific metrics
        for metric in QualityMetric:
            avg_score = metrics.get_metric_average(metric)
            if avg_score < 0.6:
                issues.append({
                    "issue": f"Poor {metric.value} performance",
                    "severity": "medium" if avg_score > 0.4 else "high",
                    "metric": metric.value,
                    "current_score": avg_score,
                    "target_score": 0.75,
                    "recommendations": self._get_metric_recommendations(metric, avg_score)
                })
        
        # Check error rate
        error_rate = metrics.failed_requests / max(1, metrics.total_requests)
        if error_rate > 0.05:  # More than 5% error rate
            issues.append({
                "issue": "High error rate",
                "severity": "high",
                "metric": "error_rate",
                "current_score": 1 - error_rate,
                "target_score": 0.98,
                "recommendations": [
                    ImprovementAction.OPTIMIZE_PROCESSING,
                    ImprovementAction.UPDATE_VOICE_MODEL
                ]
            })
        
        # Check response time
        if metrics.average_response_time > 3.0:  # More than 3 seconds
            issues.append({
                "issue": "Slow response time",
                "severity": "medium",
                "metric": "response_time",
                "current_score": max(0, 1 - (metrics.average_response_time - 1) / 5),
                "target_score": 0.9,
                "recommendations": [
                    ImprovementAction.OPTIMIZE_PROCESSING
                ]
            })
        
        return issues
    
    def _get_metric_recommendations(self, metric: QualityMetric, score: float) -> List[ImprovementAction]:
        """Get recommendations for improving a specific metric"""
        recommendations = []
        
        if metric == QualityMetric.CLARITY:
            recommendations.extend([
                ImprovementAction.ADJUST_SPEED,
                ImprovementAction.ADJUST_VOLUME,
                ImprovementAction.UPDATE_VOICE_MODEL
            ])
        
        elif metric == QualityMetric.PRONUNCIATION:
            recommendations.extend([
                ImprovementAction.RETRAIN_PRONUNCIATION,
                ImprovementAction.SWITCH_VOICE,
                ImprovementAction.UPDATE_VOICE_MODEL
            ])
        
        elif metric == QualityMetric.NATURALNESS:
            recommendations.extend([
                ImprovementAction.UPDATE_VOICE_MODEL,
                ImprovementAction.SWITCH_VOICE
            ])
        
        elif metric == QualityMetric.EMOTIONAL_TONE:
            recommendations.extend([
                ImprovementAction.ADJUST_PITCH,
                ImprovementAction.ADJUST_SPEED
            ])
        
        elif metric == QualityMetric.PACE:
            recommendations.extend([
                ImprovementAction.ADJUST_SPEED
            ])
        
        elif metric == QualityMetric.USER_SATISFACTION:
            recommendations.extend([
                ImprovementAction.COLLECT_MORE_FEEDBACK,
                ImprovementAction.UPDATE_VOICE_MODEL
            ])
        
        return recommendations
    
    def _load_improvement_rules(self) -> Dict[str, Any]:
        """Load improvement rules and thresholds"""
        return {
            "quality_thresholds": {
                "critical": 0.4,
                "poor": 0.6,
                "average": 0.75,
                "good": 0.9
            },
            "response_time_targets": {
                "excellent": 1.0,
                "good": 2.0,
                "acceptable": 3.0
            },
            "error_rate_targets": {
                "excellent": 0.01,
                "good": 0.03,
                "acceptable": 0.05
            }
        }


class VoiceQualityMonitor:
    """Main voice quality monitoring system"""
    
    def __init__(self):
        self.analyzer = VoiceQualityAnalyzer()
        self.improvement_engine = VoiceImprovementEngine()
        self.session_metrics: Dict[str, VoicePerformanceMetrics] = {}
        self.global_metrics = VoicePerformanceMetrics("global")
        self.monitoring_enabled = True
        
    def start_monitoring(self) -> None:
        """Start voice quality monitoring"""
        self.monitoring_enabled = True
        logger.info("Voice quality monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop voice quality monitoring"""
        self.monitoring_enabled = False
        logger.info("Voice quality monitoring stopped")
    
    def record_voice_synthesis(self,
                             session_id: str,
                             audio_data: bytes,
                             text: str,
                             voice_settings: Dict[str, Any],
                             response_time: float,
                             success: bool,
                             context: Dict[str, Any] = None) -> None:
        """
        Record a voice synthesis event for quality monitoring
        
        Args:
            session_id: User session ID
            audio_data: Generated audio data
            text: Original text
            voice_settings: Voice synthesis settings
            response_time: Time taken to generate audio
            success: Whether synthesis was successful
            context: Additional context
        """
        if not self.monitoring_enabled:
            return
        
        # Get or create session metrics
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = VoicePerformanceMetrics(session_id)
        
        session_metrics = self.session_metrics[session_id]
        
        # Update basic metrics
        session_metrics.total_requests += 1
        self.global_metrics.total_requests += 1
        
        if success:
            session_metrics.successful_requests += 1
            self.global_metrics.successful_requests += 1
            
            # Analyze quality if synthesis was successful
            quality_scores = self.analyzer.analyze_voice_output(
                audio_data, text, voice_settings, context
            )
            
            session_metrics.quality_scores.extend(quality_scores)
            self.global_metrics.quality_scores.extend(quality_scores)
            
            # Update average quality score
            all_scores = [s.score for s in session_metrics.quality_scores]
            session_metrics.average_quality_score = statistics.mean(all_scores)
            
            all_global_scores = [s.score for s in self.global_metrics.quality_scores]
            self.global_metrics.average_quality_score = statistics.mean(all_global_scores)
        
        else:
            session_metrics.failed_requests += 1
            self.global_metrics.failed_requests += 1
        
        # Update response time
        session_total_time = (session_metrics.average_response_time * 
                            (session_metrics.total_requests - 1) + response_time)
        session_metrics.average_response_time = session_total_time / session_metrics.total_requests
        
        global_total_time = (self.global_metrics.average_response_time * 
                           (self.global_metrics.total_requests - 1) + response_time)
        self.global_metrics.average_response_time = global_total_time / self.global_metrics.total_requests
        
        # Update timestamps
        session_metrics.last_updated = datetime.now()
        self.global_metrics.last_updated = datetime.now()
    
    def record_user_feedback(self,
                           session_id: str,
                           metric: QualityMetric,
                           score: float,
                           context: Dict[str, Any] = None) -> None:
        """Record user feedback about voice quality"""
        if not self.monitoring_enabled:
            return
        
        feedback_score = VoiceQualityScore(
            metric=metric,
            score=score,
            level=self.analyzer._get_quality_level(score),
            timestamp=datetime.now(),
            context=context or {},
            feedback_source="user"
        )
        
        # Add to session metrics
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = VoicePerformanceMetrics(session_id)
        
        self.session_metrics[session_id].quality_scores.append(feedback_score)
        self.session_metrics[session_id].user_feedback_count += 1
        
        # Add to global metrics
        self.global_metrics.quality_scores.append(feedback_score)
        self.global_metrics.user_feedback_count += 1
        
        logger.info(f"User feedback recorded: {metric.value} = {score}")
    
    def get_quality_report(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive quality report
        
        Args:
            session_id: Specific session ID, or None for global report
            
        Returns:
            Quality report dictionary
        """
        if session_id and session_id in self.session_metrics:
            metrics = self.session_metrics[session_id]
            scope = "session"
        else:
            metrics = self.global_metrics
            scope = "global"
        
        # Calculate metric averages
        metric_averages = {}
        for metric in QualityMetric:
            avg = metrics.get_metric_average(metric)
            metric_averages[metric.value] = {
                "average": avg,
                "level": self.analyzer._get_quality_level(avg).value,
                "trend": metrics.get_quality_trend(metric)
            }
        
        # Identify issues and recommendations
        issues = self.improvement_engine.analyze_performance_issues(metrics)
        
        return {
            "scope": scope,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_requests": metrics.total_requests,
                "success_rate": metrics.successful_requests / max(1, metrics.total_requests),
                "average_response_time": metrics.average_response_time,
                "average_quality_score": metrics.average_quality_score,
                "user_feedback_count": metrics.user_feedback_count,
                "expert_feedback_count": metrics.expert_feedback_count
            },
            "metric_details": metric_averages,
            "issues": issues,
            "improvement_actions_taken": metrics.improvement_actions_taken,
            "last_updated": metrics.last_updated.isoformat()
        }
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights and recommendations"""
        report = self.get_quality_report()
        
        insights = {
            "overall_health": "good",
            "key_strengths": [],
            "areas_for_improvement": [],
            "urgent_actions": [],
            "trends": {},
            "recommendations": []
        }
        
        # Determine overall health
        avg_quality = report["summary"]["average_quality_score"]
        success_rate = report["summary"]["success_rate"]
        
        if avg_quality >= 0.8 and success_rate >= 0.95:
            insights["overall_health"] = "excellent"
        elif avg_quality >= 0.7 and success_rate >= 0.9:
            insights["overall_health"] = "good"
        elif avg_quality >= 0.6 and success_rate >= 0.8:
            insights["overall_health"] = "fair"
        else:
            insights["overall_health"] = "poor"
        
        # Identify strengths and weaknesses
        for metric, data in report["metric_details"].items():
            if data["average"] >= 0.8:
                insights["key_strengths"].append(metric)
            elif data["average"] < 0.6:
                insights["areas_for_improvement"].append(metric)
        
        # Urgent actions from high-severity issues
        for issue in report["issues"]:
            if issue["severity"] == "high":
                insights["urgent_actions"].append(issue["issue"])
        
        # Generate recommendations
        if not insights["key_strengths"]:
            insights["recommendations"].append("Consider upgrading voice models")
        
        if len(insights["areas_for_improvement"]) > 3:
            insights["recommendations"].append("Focus on systematic quality improvement")
        
        if report["summary"]["user_feedback_count"] < 10:
            insights["recommendations"].append("Collect more user feedback for better insights")
        
        return insights
