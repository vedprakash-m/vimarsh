"""
Vimarsh Monitoring and Analytics Module
Provides comprehensive monitoring for spiritual guidance system with Application Insights integration.
"""

import logging
import time
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone
from functools import wraps
from dataclasses import dataclass, asdict
import os

# Application Insights integration (install with: pip install opencensus-ext-azure)
try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.trace import config_integration
    from opencensus.ext.azure.trace_exporter import AzureExporter
    from opencensus.trace.samplers import ProbabilitySampler
    from opencensus.trace.tracer import Tracer
    from opencensus.trace.span import SpanKind
    AZURE_MONITORING_AVAILABLE = True
except ImportError:
    AZURE_MONITORING_AVAILABLE = False
    logging.warning("Azure monitoring not available. Install opencensus-ext-azure for full monitoring.")

@dataclass
class SpiritualGuidanceMetrics:
    """Metrics for spiritual guidance interactions."""
    query_type: str
    language: str
    response_time_ms: float
    quality_score: float
    source_citations: int
    user_satisfaction: Optional[float] = None
    expert_reviewed: bool = False

@dataclass
class CostMetrics:
    """Metrics for AI cost tracking."""
    operation_type: str
    token_count: int
    cost_usd: float
    model_used: str
    cache_hit: bool = False

@dataclass
class VoiceInteractionMetrics:
    """Metrics for voice interface interactions."""
    language: str
    duration_seconds: float
    transcription_accuracy: float
    tts_quality_score: float
    sanskrit_terms_detected: int

class VimarshMonitor:
    """Comprehensive monitoring system for Vimarsh spiritual guidance platform."""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv('APPINSIGHTS_CONNECTION_STRING')
        self.logger = self._setup_logging()
        self.tracer = self._setup_tracing()
        self.metrics_cache = []
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging with Application Insights integration."""
        logger = logging.getLogger('vimarsh_monitor')
        logger.setLevel(logging.INFO)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Azure Application Insights handler
        if AZURE_MONITORING_AVAILABLE and self.connection_string:
            try:
                azure_handler = AzureLogHandler(connection_string=self.connection_string)
                azure_handler.setLevel(logging.INFO)
                logger.addHandler(azure_handler)
                logger.info("✅ Azure Application Insights logging configured")
            except Exception as e:
                logger.warning(f"Failed to configure Azure logging: {e}")
        
        return logger
    
    def _setup_tracing(self) -> Optional[Any]:
        """Set up distributed tracing with Application Insights."""
        if not AZURE_MONITORING_AVAILABLE or not self.connection_string:
            return None
            
        try:
            # Configure integrations
            config_integration.trace_integrations(['requests', 'logging'])
            
            # Create tracer with Azure exporter
            tracer = Tracer(
                exporter=AzureExporter(connection_string=self.connection_string),
                sampler=ProbabilitySampler(1.0)  # Sample all traces in development
            )
            
            self.logger.info("✅ Azure Application Insights tracing configured")
            return tracer
        except Exception as e:
            self.logger.warning(f"Failed to configure Azure tracing: {e}")
            return None
    
    def log_spiritual_guidance(self, metrics: SpiritualGuidanceMetrics, 
                             additional_properties: Optional[Dict[str, Any]] = None):
        """Log spiritual guidance interaction metrics."""
        properties = asdict(metrics)
        if additional_properties:
            properties.update(additional_properties)
        
        # Log to Application Insights custom events
        self._log_custom_event(
            "SpiritualGuidanceRequested",
            properties,
            {
                'responseTime': metrics.response_time_ms,
                'qualityScore': metrics.quality_score,
                'sourceCitations': metrics.source_citations
            }
        )
        
        # Log to standard logger
        self.logger.info(
            f"🙏 Spiritual guidance provided - Language: {metrics.language}, "
            f"Quality: {metrics.quality_score:.2f}, Time: {metrics.response_time_ms:.0f}ms"
        )
    
    def log_cost_metrics(self, metrics: CostMetrics, 
                        additional_properties: Optional[Dict[str, Any]] = None):
        """Log AI cost metrics for budget tracking."""
        properties = asdict(metrics)
        if additional_properties:
            properties.update(additional_properties)
        
        # Log to Application Insights
        self._log_custom_event(
            "AIOperationCost",
            properties,
            {
                'tokenCount': metrics.token_count,
                'costUsd': metrics.cost_usd
            }
        )
        
        # Check cost thresholds
        self._check_cost_thresholds(metrics.cost_usd)
        
        self.logger.info(
            f"💰 AI Operation - Model: {metrics.model_used}, "
            f"Cost: ${metrics.cost_usd:.4f}, Tokens: {metrics.token_count}"
        )
    
    def log_voice_interaction(self, metrics: VoiceInteractionMetrics,
                            additional_properties: Optional[Dict[str, Any]] = None):
        """Log voice interface interaction metrics."""
        properties = asdict(metrics)
        if additional_properties:
            properties.update(additional_properties)
        
        self._log_custom_event(
            "VoiceInteractionCompleted",
            properties,
            {
                'duration': metrics.duration_seconds,
                'transcriptionAccuracy': metrics.transcription_accuracy,
                'ttsQuality': metrics.tts_quality_score
            }
        )
        
        self.logger.info(
            f"🎙️ Voice interaction - Language: {metrics.language}, "
            f"Duration: {metrics.duration_seconds:.1f}s, "
            f"Sanskrit terms: {metrics.sanskrit_terms_detected}"
        )
    
    def log_expert_review(self, content_id: str, flag_reason: str, severity: str,
                         additional_properties: Optional[Dict[str, Any]] = None):
        """Log expert review trigger event."""
        properties = {
            'contentId': content_id,
            'flagReason': flag_reason,
            'severity': severity,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        if additional_properties:
            properties.update(additional_properties)
        
        self._log_custom_event("ExpertReviewTriggered", properties)
        
        self.logger.warning(
            f"👨‍🏫 Expert review triggered - Content: {content_id}, "
            f"Reason: {flag_reason}, Severity: {severity}"
        )
    
    def log_cost_threshold_reached(self, current_cost: float, threshold: float, 
                                 action_taken: str):
        """Log cost threshold alert."""
        properties = {
            'currentCost': current_cost,
            'threshold': threshold,
            'action': action_taken,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self._log_custom_event(
            "CostThresholdReached", 
            properties,
            {'currentCost': current_cost, 'threshold': threshold}
        )
        
        self.logger.warning(
            f"💸 Cost threshold reached - Current: ${current_cost:.2f}, "
            f"Threshold: ${threshold:.2f}, Action: {action_taken}"
        )
    
    def log_performance_metrics(self, operation: str, duration_ms: float, 
                              success: bool, error_details: Optional[str] = None):
        """Log performance metrics for operations."""
        properties = {
            'operation': operation,
            'duration_ms': duration_ms,
            'success': success,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if error_details:
            properties['errorDetails'] = error_details
        
        self._log_custom_event(
            "PerformanceMetric",
            properties,
            {'duration': duration_ms}
        )
        
        status = "✅" if success else "❌"
        self.logger.info(
            f"{status} {operation} - Duration: {duration_ms:.0f}ms, Success: {success}"
        )
    
    def _log_custom_event(self, event_name: str, properties: Dict[str, Any], 
                         measurements: Optional[Dict[str, float]] = None):
        """Log custom event to Application Insights."""
        if AZURE_MONITORING_AVAILABLE:
            try:
                # Custom events are automatically sent with the logger
                self.logger.info(
                    f"CUSTOM_EVENT: {event_name}",
                    extra={
                        'custom_dimensions': properties,
                        'custom_measurements': measurements or {}
                    }
                )
            except Exception as e:
                self.logger.error(f"Failed to log custom event: {e}")
    
    def _check_cost_thresholds(self, cost: float):
        """Check if cost thresholds are exceeded."""
        # This would integrate with the cost management system
        monthly_budget = float(os.getenv('MONTHLY_BUDGET_USD', '50'))
        threshold = float(os.getenv('COST_ALERT_THRESHOLD', '0.8'))
        
        # Simplified threshold check (would be more sophisticated in production)
        if cost > (monthly_budget * threshold / 100):
            self.log_cost_threshold_reached(cost, monthly_budget * threshold, "alert_sent")
    
    def create_performance_monitor(self, operation_name: str):
        """Create a context manager for monitoring operation performance."""
        return PerformanceMonitor(self, operation_name)
    
    def monitor_spiritual_guidance(self, query_type: str = "text", language: str = "en"):
        """Decorator for monitoring spiritual guidance functions."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                quality_score = 0.0
                citations = 0
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    
                    # Extract quality metrics from result if available
                    if isinstance(result, dict):
                        quality_score = result.get('quality_score', 0.8)
                        citations = len(result.get('citations', []))
                    
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Spiritual guidance error: {e}")
                    raise
                    
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    if success:
                        metrics = SpiritualGuidanceMetrics(
                            query_type=query_type,
                            language=language,
                            response_time_ms=duration_ms,
                            quality_score=quality_score,
                            source_citations=citations
                        )
                        self.log_spiritual_guidance(metrics)
                    
                    self.log_performance_metrics(
                        f"spiritual_guidance_{func.__name__}",
                        duration_ms,
                        success
                    )
            
            return wrapper
        return decorator

class PerformanceMonitor:
    """Context manager for monitoring operation performance."""
    
    def __init__(self, monitor: VimarshMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            success = exc_type is None
            error_details = str(exc_val) if exc_val else None
            
            self.monitor.log_performance_metrics(
                self.operation_name,
                duration_ms,
                success,
                error_details
            )

# Global monitor instance
_monitor_instance = None

def get_monitor() -> VimarshMonitor:
    """Get the global monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = VimarshMonitor()
    return _monitor_instance

# Convenience functions
def log_spiritual_guidance(metrics: SpiritualGuidanceMetrics, **kwargs):
    get_monitor().log_spiritual_guidance(metrics, kwargs)

def log_cost_metrics(metrics: CostMetrics, **kwargs):
    get_monitor().log_cost_metrics(metrics, kwargs)

def log_voice_interaction(metrics: VoiceInteractionMetrics, **kwargs):
    get_monitor().log_voice_interaction(metrics, kwargs)

def log_expert_review(content_id: str, flag_reason: str, severity: str, **kwargs):
    get_monitor().log_expert_review(content_id, flag_reason, severity, kwargs)

def monitor_performance(operation_name: str):
    """Decorator for monitoring function performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with get_monitor().create_performance_monitor(f"{operation_name}_{func.__name__}"):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def monitor_spiritual_guidance(query_type: str = "text", language: str = "en"):
    """Decorator for monitoring spiritual guidance functions."""
    return get_monitor().monitor_spiritual_guidance(query_type, language)
