"""
Performance Tracker with Application Insights Integration
Tracks application performance, response times, and resource usage
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import wraps
from collections import deque, defaultdict

# Try to import psutil, fall back to basic metrics if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - using basic performance metrics")

from .app_insights_client import get_app_insights_client, track_performance

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    cpu_usage_percent: float
    memory_usage_mb: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/tracking"""
        return {
            'operation_name': self.operation_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': self.duration_seconds,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
            'success': self.success,
            'error_message': self.error_message
        }


class PerformanceTracker:
    """Track application performance with Application Insights integration"""
    
    def __init__(self, max_history_size: int = 1000):
        """
        Initialize performance tracker
        
        Args:
            max_history_size: Maximum number of performance records to keep in memory
        """
        self.app_insights = get_app_insights_client()
        self.performance_history: deque = deque(maxlen=max_history_size)
        self.operation_stats: Dict[str, List[float]] = defaultdict(list)
        
        # Performance thresholds for alerting
        self.alert_thresholds = {
            'max_response_time': 5.0,      # 5 seconds
            'max_cpu_usage': 80.0,         # 80%
            'max_memory_usage': 512.0,     # 512 MB
            'min_success_rate': 0.95       # 95%
        }
        
        logger.info("Performance Tracker initialized")
    
    def start_tracking(self, operation_name: str) -> str:
        """
        Start tracking a performance operation
        
        Args:
            operation_name: Name of the operation to track
            
        Returns:
            str: Tracking ID for this operation
        """
        tracking_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        # Store start metrics
        start_metrics = {
            'tracking_id': tracking_id,
            'operation_name': operation_name,
            'start_time': datetime.now(),
            'start_cpu': self._get_cpu_usage(),
            'start_memory': self._get_memory_usage()
        }
        
        # Store in a temporary tracking dict (you might want to use a proper cache)
        if not hasattr(self, '_active_operations'):
            self._active_operations = {}
        
        self._active_operations[tracking_id] = start_metrics
        
        return tracking_id
    
    def end_tracking(self, tracking_id: str, success: bool = True, 
                    error_message: str = None) -> PerformanceMetrics:
        """
        End tracking a performance operation
        
        Args:
            tracking_id: Tracking ID from start_tracking
            success: Whether the operation succeeded
            error_message: Error message if operation failed
            
        Returns:
            PerformanceMetrics: Performance metrics for the operation
        """
        end_time = datetime.now()
        end_cpu = self._get_cpu_usage()
        end_memory = self._get_memory_usage()
        
        # Get start metrics
        if not hasattr(self, '_active_operations'):
            self._active_operations = {}
        
        start_data = self._active_operations.pop(tracking_id, None)
        if not start_data:
            # Fallback metrics if start tracking wasn't called
            logger.warning(f"No start data found for tracking_id: {tracking_id}")
            return PerformanceMetrics(
                operation_name="unknown",
                start_time=end_time,
                end_time=end_time,
                duration_seconds=0.0,
                cpu_usage_percent=end_cpu,
                memory_usage_mb=end_memory,
                success=success,
                error_message=error_message
            )
        
        # Calculate metrics
        duration = (end_time - start_data['start_time']).total_seconds()
        
        metrics = PerformanceMetrics(
            operation_name=start_data['operation_name'],
            start_time=start_data['start_time'],
            end_time=end_time,
            duration_seconds=duration,
            cpu_usage_percent=max(start_data['start_cpu'], end_cpu),
            memory_usage_mb=max(start_data['start_memory'], end_memory),
            success=success,
            error_message=error_message
        )
        
        # Store metrics
        self.performance_history.append(metrics)
        self.operation_stats[metrics.operation_name].append(duration)
        
        # Track in Application Insights
        self._track_performance_metrics(metrics)
        
        # Check for performance alerts
        self._check_performance_alerts(metrics)
        
        return metrics
    
    @track_performance("spiritual_guidance_operation")
    async def track_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Track a complete operation with automatic performance monitoring
        
        Args:
            operation_name: Name of the operation
            operation_func: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of the operation function
        """
        tracking_id = self.start_tracking(operation_name)
        
        try:
            if asyncio.iscoroutinefunction(operation_func):
                result = await operation_func(*args, **kwargs)
            else:
                result = operation_func(*args, **kwargs)
            
            self.end_tracking(tracking_id, success=True)
            return result
            
        except Exception as e:
            self.end_tracking(tracking_id, success=False, error_message=str(e))
            raise
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            if PSUTIL_AVAILABLE:
                return psutil.cpu_percent(interval=0.1)
            else:
                return 0.0  # Fallback when psutil not available
        except Exception as e:
            logger.warning(f"Error getting CPU usage: {e}")
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                memory_info = process.memory_info()
                return memory_info.rss / 1024 / 1024  # Convert to MB
            else:
                return 0.0  # Fallback when psutil not available
        except Exception as e:
            logger.warning(f"Error getting memory usage: {e}")
            return 0.0
    
    def _track_performance_metrics(self, metrics: PerformanceMetrics):
        """Track performance metrics in Application Insights"""
        try:
            # Track individual metrics
            self.app_insights.track_metric(
                name=f"performance_duration_{metrics.operation_name}",
                value=metrics.duration_seconds,
                properties={
                    'operation': metrics.operation_name,
                    'success': metrics.success
                }
            )
            
            self.app_insights.track_metric(
                name=f"performance_cpu_{metrics.operation_name}",
                value=metrics.cpu_usage_percent,
                properties={'operation': metrics.operation_name}
            )
            
            self.app_insights.track_metric(
                name=f"performance_memory_{metrics.operation_name}",
                value=metrics.memory_usage_mb,
                properties={'operation': metrics.operation_name}
            )
            
            # Track performance event
            self.app_insights.track_event(
                "performance_measurement",
                properties={
                    'operation_name': metrics.operation_name,
                    'success': metrics.success,
                    'error_message': metrics.error_message
                },
                measurements={
                    'duration_seconds': metrics.duration_seconds,
                    'cpu_usage_percent': metrics.cpu_usage_percent,
                    'memory_usage_mb': metrics.memory_usage_mb
                }
            )
            
        except Exception as e:
            logger.error(f"Error tracking performance metrics: {e}")
    
    def _check_performance_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts and trigger notifications"""
        try:
            alerts = []
            
            # Check response time
            if metrics.duration_seconds > self.alert_thresholds['max_response_time']:
                alerts.append(f"Response time exceeded threshold: {metrics.duration_seconds:.2f}s")
            
            # Check CPU usage
            if metrics.cpu_usage_percent > self.alert_thresholds['max_cpu_usage']:
                alerts.append(f"CPU usage exceeded threshold: {metrics.cpu_usage_percent:.1f}%")
            
            # Check memory usage
            if metrics.memory_usage_mb > self.alert_thresholds['max_memory_usage']:
                alerts.append(f"Memory usage exceeded threshold: {metrics.memory_usage_mb:.1f}MB")
            
            # Log alerts
            if alerts:
                for alert in alerts:
                    logger.warning(f"PERFORMANCE_ALERT: {alert} (Operation: {metrics.operation_name})")
                    
                    self.app_insights.track_event(
                        "performance_alert",
                        properties={
                            'operation_name': metrics.operation_name,
                            'alert_message': alert,
                            'duration_seconds': metrics.duration_seconds,
                            'cpu_usage_percent': metrics.cpu_usage_percent,
                            'memory_usage_mb': metrics.memory_usage_mb
                        }
                    )
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
    
    def get_performance_summary(self, operation_name: str = None, 
                              hours: int = 24) -> Dict[str, Any]:
        """
        Get performance summary for specified operation and time period
        
        Args:
            operation_name: Specific operation to analyze (None for all)
            hours: Time period in hours
            
        Returns:
            Dict: Performance summary
        """
        try:
            # Filter metrics by time and operation
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_metrics = [
                m for m in self.performance_history
                if m.start_time >= cutoff_time and 
                   (operation_name is None or m.operation_name == operation_name)
            ]
            
            if not filtered_metrics:
                return {'message': 'No performance data available'}
            
            # Calculate statistics
            durations = [m.duration_seconds for m in filtered_metrics]
            cpu_usages = [m.cpu_usage_percent for m in filtered_metrics]
            memory_usages = [m.memory_usage_mb for m in filtered_metrics]
            success_count = sum(1 for m in filtered_metrics if m.success)
            
            summary = {
                'period_hours': hours,
                'operation_name': operation_name or 'all',
                'total_operations': len(filtered_metrics),
                'success_rate': success_count / len(filtered_metrics),
                'response_times': {
                    'average': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'p95': sorted(durations)[int(len(durations) * 0.95)] if durations else 0
                },
                'resource_usage': {
                    'avg_cpu_percent': sum(cpu_usages) / len(cpu_usages),
                    'max_cpu_percent': max(cpu_usages),
                    'avg_memory_mb': sum(memory_usages) / len(memory_usages),
                    'max_memory_mb': max(memory_usages)
                },
                'alerts_triggered': sum(
                    1 for m in filtered_metrics
                    if (m.duration_seconds > self.alert_thresholds['max_response_time'] or
                        m.cpu_usage_percent > self.alert_thresholds['max_cpu_usage'] or
                        m.memory_usage_mb > self.alert_thresholds['max_memory_usage'])
                )
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {'error': str(e)}
    
    def get_operation_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all tracked operations"""
        try:
            stats = {}
            
            for operation_name, durations in self.operation_stats.items():
                if durations:
                    stats[operation_name] = {
                        'count': len(durations),
                        'average_duration': sum(durations) / len(durations),
                        'min_duration': min(durations),
                        'max_duration': max(durations)
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating operation statistics: {e}")
            return {}


# Global performance tracker instance
_performance_tracker = None

def get_performance_tracker() -> PerformanceTracker:
    """Get global performance tracker instance"""
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    return _performance_tracker


# Convenience decorator for tracking function performance
def track_function_performance(operation_name: str = None):
    """Decorator to automatically track function performance"""
    def decorator(func):
        nonlocal operation_name
        if operation_name is None:
            operation_name = f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracker = get_performance_tracker()
            return await tracker.track_operation(operation_name, func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracker = get_performance_tracker()
            tracking_id = tracker.start_tracking(operation_name)
            try:
                result = func(*args, **kwargs)
                tracker.end_tracking(tracking_id, success=True)
                return result
            except Exception as e:
                tracker.end_tracking(tracking_id, success=False, error_message=str(e))
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
