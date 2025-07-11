"""
Performance Monitoring and Alerting System for Vimarsh
Provides real-time performance tracking with configurable alerts
"""

import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
from enum import Enum
import statistics

# Import unified configuration and cache service
try:
    from config.unified_config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from services.cache_service import get_cache_service
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    MEMORY_USAGE = "memory_usage"
    TOKEN_USAGE = "token_usage"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_LATENCY = "database_latency"
    API_THROUGHPUT = "api_throughput"


@dataclass
class PerformanceMetric:
    """Single performance metric measurement"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


@dataclass
class AlertRule:
    """Performance alert rule configuration"""
    name: str
    metric_type: MetricType
    condition: str  # "greater_than", "less_than", "equals"
    threshold: float
    level: AlertLevel
    window_minutes: int = 5  # Time window for aggregation
    min_samples: int = 3  # Minimum samples needed in window
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Alert:
    """Performance alert instance"""
    rule_name: str
    metric_type: MetricType
    level: AlertLevel
    message: str
    value: float
    threshold: float
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_name": self.rule_name,
            "metric_type": self.metric_type.value,
            "level": self.level.value,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


class PerformanceMonitor:
    """Performance monitoring and alerting system"""
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        
        # Storage for metrics and alerts
        self.metrics: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        self.alerts: deque[Alert] = deque(maxlen=1000)  # Keep last 1000 alerts
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Performance tracking
        self._active_requests: Dict[str, float] = {}  # request_id -> start_time
        self._request_stats = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Load configuration and setup default rules
        self._load_configuration()
        self._setup_default_alert_rules()
        
        # Start monitoring task
        self._start_monitoring_task()
        
        logger.info("📊 Performance monitor initialized")
    
    def _load_configuration(self):
        """Load configuration from unified config system"""
        if CONFIG_AVAILABLE:
            config = get_config()
            self.max_history_size = config.get_int('PERF_MONITOR_HISTORY_SIZE', self.max_history_size)
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        default_rules = [
            AlertRule(
                name="high_response_time",
                metric_type=MetricType.RESPONSE_TIME,
                condition="greater_than",
                threshold=5000.0,  # 5 seconds
                level=AlertLevel.WARNING,
                window_minutes=5,
                min_samples=3
            ),
            AlertRule(
                name="critical_response_time",
                metric_type=MetricType.RESPONSE_TIME,
                condition="greater_than",
                threshold=10000.0,  # 10 seconds
                level=AlertLevel.CRITICAL,
                window_minutes=2,
                min_samples=2
            ),
            AlertRule(
                name="high_error_rate",
                metric_type=MetricType.ERROR_RATE,
                condition="greater_than",
                threshold=0.05,  # 5% error rate
                level=AlertLevel.ERROR,
                window_minutes=10,
                min_samples=5
            ),
            AlertRule(
                name="low_cache_hit_rate",
                metric_type=MetricType.CACHE_HIT_RATE,
                condition="less_than",
                threshold=0.70,  # 70% hit rate
                level=AlertLevel.WARNING,
                window_minutes=15,
                min_samples=10
            ),
            AlertRule(
                name="high_token_usage",
                metric_type=MetricType.TOKEN_USAGE,
                condition="greater_than",
                threshold=1000000,  # 1M tokens per window
                level=AlertLevel.WARNING,
                window_minutes=60,
                min_samples=1
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def _start_monitoring_task(self):
        """Start background monitoring and alerting task"""
        def monitoring_worker():
            while True:
                try:
                    self._check_alerts()
                    self._cleanup_old_metrics()
                    # Check every 30 seconds
                    time.sleep(30)
                except Exception as e:
                    logger.error(f"Error in monitoring worker: {e}")
        
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()
    
    def record_metric(self, 
                     metric_type: MetricType, 
                     value: float, 
                     context: Optional[Dict[str, Any]] = None):
        """Record a performance metric"""
        
        if context is None:
            context = {}
        
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            context=context
        )
        
        with self._lock:
            self.metrics[metric_type].append(metric)
        
        logger.debug(f"📊 Recorded metric: {metric_type.value}={value}")
        
        # Cache the metric if cache is available
        if CACHE_AVAILABLE:
            cache = get_cache_service()
            cache_key = f"perf_metric:{metric_type.value}:latest"
            cache.put(cache_key, metric.to_dict(), 300)  # 5 minutes TTL
    
    def start_request_tracking(self, request_id: str) -> str:
        """Start tracking a request"""
        start_time = time.time()
        
        with self._lock:
            self._active_requests[request_id] = start_time
        
        return request_id
    
    def end_request_tracking(self, 
                           request_id: str, 
                           success: bool = True,
                           context: Optional[Dict[str, Any]] = None) -> float:
        """End request tracking and record metrics"""
        
        if context is None:
            context = {}
        
        with self._lock:
            if request_id not in self._active_requests:
                logger.warning(f"Request {request_id} not found in active requests")
                return 0.0
            
            start_time = self._active_requests.pop(request_id)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Record response time
        context.update({
            "request_id": request_id,
            "success": success
        })
        
        self.record_metric(MetricType.RESPONSE_TIME, response_time_ms, context)
        
        # Track error rate
        self._request_stats["total"].append(1)
        if not success:
            self._request_stats["errors"].append(1)
        
        return response_time_ms
    
    def record_memory_usage(self, memory_mb: float, context: Optional[Dict[str, Any]] = None):
        """Record memory usage metric"""
        self.record_metric(MetricType.MEMORY_USAGE, memory_mb, context or {})
    
    def record_token_usage(self, tokens: int, context: Optional[Dict[str, Any]] = None):
        """Record token usage metric"""
        self.record_metric(MetricType.TOKEN_USAGE, tokens, context or {})
    
    def record_cache_performance(self, hit_rate: float, context: Optional[Dict[str, Any]] = None):
        """Record cache hit rate metric"""
        self.record_metric(MetricType.CACHE_HIT_RATE, hit_rate, context or {})
    
    def record_database_latency(self, latency_ms: float, context: Optional[Dict[str, Any]] = None):
        """Record database operation latency"""
        self.record_metric(MetricType.DATABASE_LATENCY, latency_ms, context or {})
    
    def add_alert_rule(self, rule: AlertRule):
        """Add or update an alert rule"""
        with self._lock:
            self.alert_rules[rule.name] = rule
        
        logger.info(f"📋 Added alert rule: {rule.name} ({rule.metric_type.value} {rule.condition} {rule.threshold})")
    
    def remove_alert_rule(self, rule_name: str) -> bool:
        """Remove an alert rule"""
        with self._lock:
            if rule_name in self.alert_rules:
                del self.alert_rules[rule_name]
                logger.info(f"🗑️ Removed alert rule: {rule_name}")
                return True
        return False
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback function for alert notifications"""
        self.alert_callbacks.append(callback)
        logger.info("📢 Added alert callback")
    
    def _check_alerts(self):
        """Check metrics against alert rules"""
        current_time = datetime.utcnow()
        
        with self._lock:
            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Get metrics in the time window
                window_start = current_time - timedelta(minutes=rule.window_minutes)
                metrics_in_window = [
                    m for m in self.metrics[rule.metric_type]
                    if m.timestamp >= window_start
                ]
                
                if len(metrics_in_window) < rule.min_samples:
                    continue
                
                # Calculate aggregated value (mean for now)
                values = [m.value for m in metrics_in_window]
                avg_value = statistics.mean(values)
                
                # Check condition
                triggered = False
                if rule.condition == "greater_than" and avg_value > rule.threshold:
                    triggered = True
                elif rule.condition == "less_than" and avg_value < rule.threshold:
                    triggered = True
                elif rule.condition == "equals" and abs(avg_value - rule.threshold) < 0.001:
                    triggered = True
                
                if triggered:
                    self._trigger_alert(rule, avg_value, metrics_in_window)
    
    def _trigger_alert(self, rule: AlertRule, value: float, metrics: List[PerformanceMetric]):
        """Trigger an alert"""
        alert = Alert(
            rule_name=rule.name,
            metric_type=rule.metric_type,
            level=rule.level,
            message=f"{rule.metric_type.value} {rule.condition} {rule.threshold} (current: {value:.2f})",
            value=value,
            threshold=rule.threshold,
            timestamp=datetime.utcnow(),
            context={
                "window_minutes": rule.window_minutes,
                "sample_count": len(metrics),
                "rule": rule.to_dict()
            }
        )
        
        self.alerts.append(alert)
        
        # Log alert
        logger.log(
            logging.WARNING if alert.level in [AlertLevel.WARNING, AlertLevel.ERROR] else logging.CRITICAL,
            f"🚨 ALERT [{alert.level.value.upper()}] {alert.message}"
        )
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory growth"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        with self._lock:
            for metric_type in self.metrics:
                # Remove metrics older than 24 hours
                metrics_deque = self.metrics[metric_type]
                while metrics_deque and metrics_deque[0].timestamp < cutoff_time:
                    metrics_deque.popleft()
    
    def get_metrics_summary(self, 
                          metric_type: MetricType, 
                          minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a metric type"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        with self._lock:
            recent_metrics = [
                m for m in self.metrics[metric_type]
                if m.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {
                "metric_type": metric_type.value,
                "window_minutes": minutes,
                "sample_count": 0,
                "summary": None
            }
        
        values = [m.value for m in recent_metrics]
        
        return {
            "metric_type": metric_type.value,
            "window_minutes": minutes,
            "sample_count": len(values),
            "summary": {
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0
            }
        }
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        with self._lock:
            recent_alerts = [
                alert.to_dict() for alert in self.alerts
                if alert.timestamp >= cutoff_time
            ]
        
        return recent_alerts
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        
        # Get recent metrics for each type
        summaries = {}
        for metric_type in MetricType:
            summaries[metric_type.value] = self.get_metrics_summary(metric_type, 30)
        
        # Calculate error rate
        recent_requests = len(self._request_stats["total"])
        recent_errors = len(self._request_stats["errors"])
        error_rate = (recent_errors / recent_requests) if recent_requests > 0 else 0
        
        # Get recent alerts
        recent_alerts = self.get_recent_alerts(60)
        critical_alerts = [a for a in recent_alerts if a["level"] == "critical"]
        
        # Determine overall health
        health_status = "healthy"
        if critical_alerts:
            health_status = "critical"
        elif len(recent_alerts) > 5:
            health_status = "degraded"
        elif error_rate > 0.1:
            health_status = "warning"
        
        return {
            "health_status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "error_rate": error_rate,
            "active_requests": len(self._active_requests),
            "recent_alerts": len(recent_alerts),
            "critical_alerts": len(critical_alerts),
            "metrics_summary": summaries,
            "alert_rules_count": len(self.alert_rules)
        }
    
    def export_metrics(self, metric_type: MetricType, minutes: int = 60) -> List[Dict[str, Any]]:
        """Export metrics for external analysis"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        with self._lock:
            recent_metrics = [
                m.to_dict() for m in self.metrics[metric_type]
                if m.timestamp >= cutoff_time
            ]
        
        return recent_metrics


# Decorator for automatic performance tracking
def track_performance(metric_context: Optional[Dict[str, Any]] = None):
    """Decorator to automatically track function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            request_id = f"{func.__name__}_{time.time()}"
            
            monitor.start_request_tracking(request_id)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_request_tracking(request_id, True, metric_context)
                return result
            except Exception as e:
                monitor.end_request_tracking(request_id, False, {
                    **(metric_context or {}),
                    "error": str(e)
                })
                raise
        
        return wrapper
    return decorator


# Async version of the decorator
def track_performance_async(metric_context: Optional[Dict[str, Any]] = None):
    """Async decorator to automatically track function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            request_id = f"{func.__name__}_{time.time()}"
            
            monitor.start_request_tracking(request_id)
            
            try:
                result = await func(*args, **kwargs)
                monitor.end_request_tracking(request_id, True, metric_context)
                return result
            except Exception as e:
                monitor.end_request_tracking(request_id, False, {
                    **(metric_context or {}),
                    "error": str(e)
                })
                raise
        
        return wrapper
    return decorator


# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
