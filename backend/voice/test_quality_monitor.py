#!/usr/bin/env python3
"""
Test suite for voice quality monitoring and improvement systems.
Tests quality analysis, performance tracking, and improvement recommendations.
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.quality_monitor import (
    VoiceQualityMonitor,
    VoiceQualityAnalyzer,
    VoiceImprovementEngine,
    VoicePerformanceMetrics,
    VoiceQualityScore,
    QualityMetric,
    QualityLevel,
    ImprovementAction
)
from datetime import datetime, timedelta


class TestVoiceQualityAnalyzer:
    """Test cases for VoiceQualityAnalyzer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = VoiceQualityAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization"""
        assert hasattr(self.analyzer, 'quality_thresholds')
        assert QualityLevel.EXCELLENT in self.analyzer.quality_thresholds
        assert QualityLevel.GOOD in self.analyzer.quality_thresholds
        assert QualityLevel.AVERAGE in self.analyzer.quality_thresholds
        assert QualityLevel.POOR in self.analyzer.quality_thresholds
    
    def test_analyze_voice_output(self):
        """Test voice output analysis"""
        audio_data = b"simulated_audio_data"
        text = "Om Namah Shivaya"
        voice_settings = {
            "voice_name": "en-IN-PrabhatNeural",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 0.8
        }
        context = {
            "language": "en",
            "content_type": "mantra"
        }
        
        scores = self.analyzer.analyze_voice_output(audio_data, text, voice_settings, context)
        
        assert isinstance(scores, list)
        assert len(scores) > 0
        
        # Check that we get scores for main metrics
        metrics_covered = {score.metric for score in scores}
        expected_metrics = {
            QualityMetric.CLARITY,
            QualityMetric.PRONUNCIATION,
            QualityMetric.NATURALNESS,
            QualityMetric.EMOTIONAL_TONE,
            QualityMetric.PACE
        }
        assert expected_metrics.issubset(metrics_covered)
        
        # Check score properties
        for score in scores:
            assert isinstance(score, VoiceQualityScore)
            assert 0.0 <= score.score <= 1.0
            assert isinstance(score.level, QualityLevel)
            assert isinstance(score.timestamp, datetime)
    
    def test_clarity_analysis(self):
        """Test clarity analysis"""
        # Test with good settings
        good_settings = {"speed": 1.0, "volume": 0.8}
        clarity_score = self.analyzer._analyze_clarity(b"audio", "test", good_settings)
        assert 0.0 <= clarity_score <= 1.0
        
        # Test with poor settings (too fast)
        poor_settings = {"speed": 2.5, "volume": 0.3}
        poor_clarity = self.analyzer._analyze_clarity(b"audio", "test", poor_settings)
        assert poor_clarity < clarity_score
    
    def test_pronunciation_analysis(self):
        """Test pronunciation analysis"""
        # Text with Sanskrit terms
        sanskrit_text = "Om dharma karma moksha"
        hindi_context = {"language": "hi"}
        english_context = {"language": "en"}
        
        hindi_settings = {"voice_name": "hi-IN-voice"}
        english_settings = {"voice_name": "en-US-voice"}
        
        # Hindi voice should score better on Sanskrit
        hindi_score = self.analyzer._analyze_pronunciation(sanskrit_text, hindi_settings, hindi_context)
        english_score = self.analyzer._analyze_pronunciation(sanskrit_text, english_settings, english_context)
        
        assert 0.0 <= hindi_score <= 1.0
        assert 0.0 <= english_score <= 1.0
        # Hindi should generally be better for Sanskrit pronunciation
    
    def test_emotional_tone_analysis(self):
        """Test emotional tone analysis"""
        devotional_context = {"content_type": "devotional"}
        teaching_context = {"content_type": "teaching"}
        
        # Different contexts should get different tone analysis
        devotional_score = self.analyzer._analyze_emotional_tone(
            "Om Namah Shivaya", {"pitch": 0.9}, devotional_context
        )
        teaching_score = self.analyzer._analyze_emotional_tone(
            "Let me explain dharma", {"emphasis_strength": 1.2}, teaching_context
        )
        
        assert 0.0 <= devotional_score <= 1.0
        assert 0.0 <= teaching_score <= 1.0
    
    def test_quality_level_conversion(self):
        """Test score to quality level conversion"""
        assert self.analyzer._get_quality_level(0.95) == QualityLevel.EXCELLENT
        assert self.analyzer._get_quality_level(0.8) == QualityLevel.GOOD
        assert self.analyzer._get_quality_level(0.65) == QualityLevel.AVERAGE
        assert self.analyzer._get_quality_level(0.5) == QualityLevel.POOR
        assert self.analyzer._get_quality_level(0.3) == QualityLevel.CRITICAL


class TestVoicePerformanceMetrics:
    """Test cases for VoicePerformanceMetrics"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = VoicePerformanceMetrics("test_session")
        
        assert metrics.session_id == "test_session"
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 0.0
        assert metrics.average_quality_score == 0.0
        assert isinstance(metrics.quality_scores, list)
        assert len(metrics.quality_scores) == 0
    
    def test_metric_average_calculation(self):
        """Test metric average calculation"""
        metrics = VoicePerformanceMetrics("test")
        
        # Add some quality scores
        score1 = VoiceQualityScore(
            QualityMetric.CLARITY, 0.8, QualityLevel.GOOD, datetime.now()
        )
        score2 = VoiceQualityScore(
            QualityMetric.CLARITY, 0.9, QualityLevel.EXCELLENT, datetime.now()
        )
        score3 = VoiceQualityScore(
            QualityMetric.PRONUNCIATION, 0.7, QualityLevel.AVERAGE, datetime.now()
        )
        
        metrics.quality_scores.extend([score1, score2, score3])
        
        # Test clarity average
        clarity_avg = metrics.get_metric_average(QualityMetric.CLARITY)
        assert abs(clarity_avg - 0.85) < 0.001  # Allow for floating point precision
        
        # Test pronunciation average
        pronunciation_avg = metrics.get_metric_average(QualityMetric.PRONUNCIATION)
        assert pronunciation_avg == 0.7
        
        # Test non-existent metric
        volume_avg = metrics.get_metric_average(QualityMetric.VOLUME)
        assert volume_avg == 0.0
    
    def test_quality_trend(self):
        """Test quality trend calculation"""
        metrics = VoicePerformanceMetrics("test")
        
        now = datetime.now()
        old_time = now - timedelta(hours=25)  # Older than 24 hours
        recent_time = now - timedelta(hours=1)  # Recent
        
        # Add scores with different timestamps
        old_score = VoiceQualityScore(
            QualityMetric.CLARITY, 0.5, QualityLevel.POOR, old_time
        )
        recent_score1 = VoiceQualityScore(
            QualityMetric.CLARITY, 0.8, QualityLevel.GOOD, recent_time
        )
        recent_score2 = VoiceQualityScore(
            QualityMetric.CLARITY, 0.9, QualityLevel.EXCELLENT, now
        )
        
        metrics.quality_scores.extend([old_score, recent_score1, recent_score2])
        
        # Get trend for last 24 hours
        trend = metrics.get_quality_trend(QualityMetric.CLARITY, 24)
        
        # Should only include recent scores
        assert len(trend) == 2
        assert 0.8 in trend
        assert 0.9 in trend
        assert 0.5 not in trend


class TestVoiceImprovementEngine:
    """Test cases for VoiceImprovementEngine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = VoiceImprovementEngine()
    
    def test_initialization(self):
        """Test improvement engine initialization"""
        assert hasattr(self.engine, 'improvement_rules')
        assert isinstance(self.engine.improvement_rules, dict)
    
    def test_performance_issue_analysis(self):
        """Test performance issue analysis"""
        # Create metrics with issues
        metrics = VoicePerformanceMetrics("test")
        metrics.total_requests = 100
        metrics.successful_requests = 80  # 20% failure rate
        metrics.failed_requests = 20
        metrics.average_quality_score = 0.5  # Low quality
        metrics.average_response_time = 4.0  # Slow
        
        # Add some poor quality scores
        poor_score = VoiceQualityScore(
            QualityMetric.CLARITY, 0.3, QualityLevel.CRITICAL, datetime.now()
        )
        metrics.quality_scores.append(poor_score)
        
        issues = self.engine.analyze_performance_issues(metrics)
        
        assert isinstance(issues, list)
        assert len(issues) > 0
        
        # Check issue structure
        for issue in issues:
            assert "issue" in issue
            assert "severity" in issue
            assert "metric" in issue
            assert "current_score" in issue
            assert "target_score" in issue
            assert "recommendations" in issue
            assert issue["severity"] in ["low", "medium", "high"]
    
    def test_metric_recommendations(self):
        """Test metric-specific recommendations"""
        # Test clarity recommendations
        clarity_recs = self.engine._get_metric_recommendations(QualityMetric.CLARITY, 0.4)
        assert isinstance(clarity_recs, list)
        assert ImprovementAction.ADJUST_SPEED in clarity_recs
        assert ImprovementAction.ADJUST_VOLUME in clarity_recs
        
        # Test pronunciation recommendations
        pronunciation_recs = self.engine._get_metric_recommendations(QualityMetric.PRONUNCIATION, 0.4)
        assert ImprovementAction.RETRAIN_PRONUNCIATION in pronunciation_recs
        
        # Test naturalness recommendations
        naturalness_recs = self.engine._get_metric_recommendations(QualityMetric.NATURALNESS, 0.4)
        assert ImprovementAction.UPDATE_VOICE_MODEL in naturalness_recs


class TestVoiceQualityMonitor:
    """Test cases for VoiceQualityMonitor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.monitor = VoiceQualityMonitor()
    
    def test_initialization(self):
        """Test monitor initialization"""
        assert isinstance(self.monitor.analyzer, VoiceQualityAnalyzer)
        assert isinstance(self.monitor.improvement_engine, VoiceImprovementEngine)
        assert isinstance(self.monitor.session_metrics, dict)
        assert isinstance(self.monitor.global_metrics, VoicePerformanceMetrics)
        assert self.monitor.monitoring_enabled is True
    
    def test_monitoring_control(self):
        """Test monitoring start/stop"""
        # Test stopping
        self.monitor.stop_monitoring()
        assert self.monitor.monitoring_enabled is False
        
        # Test starting
        self.monitor.start_monitoring()
        assert self.monitor.monitoring_enabled is True
    
    def test_voice_synthesis_recording(self):
        """Test recording voice synthesis events"""
        session_id = "test_session"
        audio_data = b"test_audio"
        text = "Test text"
        voice_settings = {"voice_name": "test_voice", "speed": 1.0}
        response_time = 1.5
        context = {"language": "en"}
        
        # Record successful synthesis
        self.monitor.record_voice_synthesis(
            session_id=session_id,
            audio_data=audio_data,
            text=text,
            voice_settings=voice_settings,
            response_time=response_time,
            success=True,
            context=context
        )
        
        # Check session metrics created
        assert session_id in self.monitor.session_metrics
        session_metrics = self.monitor.session_metrics[session_id]
        
        assert session_metrics.total_requests == 1
        assert session_metrics.successful_requests == 1
        assert session_metrics.failed_requests == 0
        assert session_metrics.average_response_time == response_time
        assert len(session_metrics.quality_scores) > 0
        
        # Check global metrics updated
        assert self.monitor.global_metrics.total_requests == 1
        assert self.monitor.global_metrics.successful_requests == 1
        
        # Record failed synthesis
        self.monitor.record_voice_synthesis(
            session_id=session_id,
            audio_data=b"",
            text=text,
            voice_settings=voice_settings,
            response_time=3.0,
            success=False,
            context=context
        )
        
        assert session_metrics.total_requests == 2
        assert session_metrics.successful_requests == 1
        assert session_metrics.failed_requests == 1
    
    def test_user_feedback_recording(self):
        """Test recording user feedback"""
        session_id = "test_session"
        
        # Record some feedback
        self.monitor.record_user_feedback(
            session_id=session_id,
            metric=QualityMetric.CLARITY,
            score=0.9,
            context={"comment": "Very clear"}
        )
        
        # Check feedback recorded
        assert session_id in self.monitor.session_metrics
        session_metrics = self.monitor.session_metrics[session_id]
        assert session_metrics.user_feedback_count == 1
        assert len(session_metrics.quality_scores) == 1
        
        feedback_score = session_metrics.quality_scores[0]
        assert feedback_score.metric == QualityMetric.CLARITY
        assert feedback_score.score == 0.9
        assert feedback_score.feedback_source == "user"
        
        # Check global metrics updated
        assert self.monitor.global_metrics.user_feedback_count == 1
    
    def test_quality_report_generation(self):
        """Test quality report generation"""
        session_id = "test_session"
        
        # Record some data
        self.monitor.record_voice_synthesis(
            session_id=session_id,
            audio_data=b"test",
            text="test",
            voice_settings={"voice_name": "test"},
            response_time=1.0,
            success=True
        )
        
        self.monitor.record_user_feedback(
            session_id=session_id,
            metric=QualityMetric.PRONUNCIATION,
            score=0.8
        )
        
        # Test session report
        session_report = self.monitor.get_quality_report(session_id)
        
        assert session_report["scope"] == "session"
        assert session_report["session_id"] == session_id
        assert "summary" in session_report
        assert "metric_details" in session_report
        assert "issues" in session_report
        
        summary = session_report["summary"]
        assert summary["total_requests"] == 1
        assert summary["success_rate"] == 1.0
        assert summary["user_feedback_count"] == 1
        
        # Test global report
        global_report = self.monitor.get_quality_report()
        assert global_report["scope"] == "global"
        assert global_report["session_id"] is None
    
    def test_performance_insights(self):
        """Test performance insights generation"""
        # Record some data to generate insights
        self.monitor.record_voice_synthesis(
            session_id="test",
            audio_data=b"test",
            text="test",
            voice_settings={"voice_name": "test"},
            response_time=1.0,
            success=True
        )
        
        insights = self.monitor.get_performance_insights()
        
        assert "overall_health" in insights
        assert "key_strengths" in insights
        assert "areas_for_improvement" in insights
        assert "urgent_actions" in insights
        assert "recommendations" in insights
        
        assert insights["overall_health"] in ["excellent", "good", "fair", "poor"]
        assert isinstance(insights["key_strengths"], list)
        assert isinstance(insights["areas_for_improvement"], list)
        assert isinstance(insights["urgent_actions"], list)
        assert isinstance(insights["recommendations"], list)
    
    def test_monitoring_disabled(self):
        """Test that recording is ignored when monitoring is disabled"""
        # Disable monitoring
        self.monitor.stop_monitoring()
        
        initial_requests = self.monitor.global_metrics.total_requests
        
        # Try to record (should be ignored)
        self.monitor.record_voice_synthesis(
            session_id="test",
            audio_data=b"test",
            text="test",
            voice_settings={},
            response_time=1.0,
            success=True
        )
        
        # Check that nothing was recorded
        assert self.monitor.global_metrics.total_requests == initial_requests
        assert len(self.monitor.session_metrics) == 0


class TestVoiceQualityScore:
    """Test cases for VoiceQualityScore"""
    
    def test_score_creation(self):
        """Test quality score creation"""
        timestamp = datetime.now()
        context = {"language": "en", "content_type": "test"}
        
        score = VoiceQualityScore(
            metric=QualityMetric.CLARITY,
            score=0.85,
            level=QualityLevel.GOOD,
            timestamp=timestamp,
            context=context,
            feedback_source="user"
        )
        
        assert score.metric == QualityMetric.CLARITY
        assert score.score == 0.85
        assert score.level == QualityLevel.GOOD
        assert score.timestamp == timestamp
        assert score.context == context
        assert score.feedback_source == "user"
    
    def test_score_to_dict(self):
        """Test quality score dictionary conversion"""
        timestamp = datetime.now()
        score = VoiceQualityScore(
            metric=QualityMetric.PRONUNCIATION,
            score=0.7,
            level=QualityLevel.AVERAGE,
            timestamp=timestamp
        )
        
        score_dict = score.to_dict()
        
        assert isinstance(score_dict, dict)
        assert score_dict["metric"] == "pronunciation"
        assert score_dict["score"] == 0.7
        assert score_dict["level"] == "average"
        assert score_dict["timestamp"] == timestamp.isoformat()
        assert score_dict["feedback_source"] == "system"


def test_quality_metric_enum():
    """Test QualityMetric enum"""
    assert QualityMetric.CLARITY.value == "clarity"
    assert QualityMetric.PRONUNCIATION.value == "pronunciation"
    assert QualityMetric.NATURALNESS.value == "naturalness"
    assert QualityMetric.USER_SATISFACTION.value == "user_satisfaction"


def test_quality_level_enum():
    """Test QualityLevel enum"""
    assert QualityLevel.EXCELLENT.value == "excellent"
    assert QualityLevel.GOOD.value == "good"
    assert QualityLevel.AVERAGE.value == "average"
    assert QualityLevel.POOR.value == "poor"
    assert QualityLevel.CRITICAL.value == "critical"


def test_improvement_action_enum():
    """Test ImprovementAction enum"""
    assert ImprovementAction.ADJUST_SPEED.value == "adjust_speed"
    assert ImprovementAction.ADJUST_PITCH.value == "adjust_pitch"
    assert ImprovementAction.RETRAIN_PRONUNCIATION.value == "retrain_pronunciation"
    assert ImprovementAction.UPDATE_VOICE_MODEL.value == "update_voice_model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
