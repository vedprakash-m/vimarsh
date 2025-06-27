"""
Application Insights integration for Vimarsh AI Agent

Provides comprehensive monitoring and telemetry collection
for spiritual guidance applications.
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SpiritualMetrics:
    """Metrics for spiritual guidance operations."""
    query_id: str = ""
    response_time: float = 0.0
    token_count: int = 0
    retrieval_count: int = 0
    success: bool = True
    timestamp: Optional[datetime] = None
    authenticity_score: float = 0.0
    overall_quality: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
            
    def passes_quality_threshold(self, threshold: float) -> bool:
        """Check if metrics pass quality threshold."""
        return self.overall_quality >= threshold


class AppInsightsClient:
    """Application Insights client for Vimarsh monitoring."""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "test_connection"
        self.is_enabled = True
        self.logger = logging.getLogger(__name__)
        
    def track_event(self, event_name: str, properties: Dict[str, Any] = None, 
                   measurements: Dict[str, float] = None):
        """Track custom event."""
        self.logger.info(f"Event: {event_name}, Properties: {properties}, Measurements: {measurements}")
        
    def track_spiritual_guidance_request(self, query: str, response_time: float, 
                                       language: str, success: bool):
        """Track spiritual guidance request."""
        self.track_event(
            event_name='SpiritualGuidanceRequest',
            properties={
                'query': query[:100],  # Truncate for privacy
                'language': language,
                'success': success
            },
            measurements={
                'response_time': response_time
            }
        )
        
    def track_exception(self, error: Exception, properties: Dict[str, Any] = None):
        """Track exception with context."""
        self.logger.error(f"Exception: {error}, Properties: {properties}")
        
    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        """Track error with spiritual context."""
        self.track_exception(error, context)
        
    def track_user_session(self, session_data: Dict[str, Any]):
        """Track user session data."""
        self.track_event(
            event_name='UserSession',
            properties={
                'session_id': session_data.get('session_id'),
                'languages_used': session_data.get('languages_used', [])
            },
            measurements={
                'duration': session_data.get('duration', 0),
                'queries_count': session_data.get('queries_count', 0)
            }
        )
        
    def track_metric(self, name: str, value: float, properties: Dict[str, Any] = None):
        """Track custom metric."""
        self.logger.info(f"Metric: {name} = {value}, Properties: {properties}")
        
    def track_performance_metric(self, metric_name: str, value: float):
        """Track performance metric."""
        self.track_metric(metric_name, value)


class MetricsCollector:
    """Metrics collection system for spiritual guidance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def collect_spiritual_guidance_metrics(self, query: str, response_time: float,
                                         token_count: int, retrieval_count: int,
                                         success: bool) -> SpiritualMetrics:
        """Collect metrics for spiritual guidance operation."""
        return SpiritualMetrics(
            query_id=f"query_{int(time.time())}",
            response_time=response_time,
            token_count=token_count,
            retrieval_count=retrieval_count,
            success=success
        )
        
    def aggregate_session_metrics(self, session_metrics: List[SpiritualMetrics]) -> Dict[str, Any]:
        """Aggregate metrics for a user session."""
        if not session_metrics:
            return {}
            
        total_queries = len(session_metrics)
        avg_response_time = sum(m.response_time for m in session_metrics) / total_queries
        total_tokens = sum(m.token_count for m in session_metrics)
        success_rate = sum(1 for m in session_metrics if m.success) / total_queries
        
        return {
            'total_queries': total_queries,
            'avg_response_time': avg_response_time,
            'total_tokens': total_tokens,
            'success_rate': success_rate
        }
        
    def check_performance_thresholds(self, metrics: Dict[str, float], 
                                   thresholds: Dict[str, float]) -> List[str]:
        """Check if metrics exceed performance thresholds."""
        alerts = []
        for metric_name, value in metrics.items():
            threshold = thresholds.get(metric_name)
            if threshold and value > threshold:
                alerts.append(f"{metric_name} exceeded threshold: {value} > {threshold}")
        return alerts
        
    def collect_quality_metrics(self, query_id: str, 
                               quality_scores: Dict[str, float]) -> SpiritualMetrics:
        """Collect quality metrics for spiritual content."""
        overall_quality = sum(quality_scores.values()) / len(quality_scores)
        
        return SpiritualMetrics(
            query_id=query_id,
            authenticity_score=quality_scores.get('authenticity', 0.0),
            overall_quality=overall_quality
        )
