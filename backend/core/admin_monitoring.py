"""
Admin Operations Monitoring & Metrics
Comprehensive monitoring for all admin activities with performance tracking
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
from enum import Enum
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AdminOperationType(Enum):
    """Types of admin operations for monitoring"""
    USER_MANAGEMENT = "user_management"
    BUDGET_MANAGEMENT = "budget_management"
    ROLE_MANAGEMENT = "role_management"
    COST_DASHBOARD = "cost_dashboard"
    SYSTEM_HEALTH = "system_health"
    USER_ROLE_QUERY = "user_role_query"


class AdminMetricType(Enum):
    """Types of metrics to track"""
    OPERATION_COUNT = "operation_count"
    OPERATION_DURATION = "operation_duration"
    ERROR_COUNT = "error_count"
    SUCCESS_RATE = "success_rate"
    CONCURRENT_USERS = "concurrent_users"
    RESPONSE_SIZE = "response_size"


@dataclass
class AdminOperationMetric:
    """Single admin operation metric record"""
    operation_type: AdminOperationType
    metric_type: AdminMetricType
    value: float
    admin_email: str
    timestamp: datetime
    additional_data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['operation_type'] = self.operation_type.value
        result['metric_type'] = self.metric_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class AdminAlert:
    """Admin system alert"""
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    operation_type: Optional[AdminOperationType]
    admin_email: Optional[str]
    timestamp: datetime
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        if self.operation_type:
            result['operation_type'] = self.operation_type.value
        return result


class AdminMetricsCollector:
    """Collects and manages admin operation metrics"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.alerts: List[AdminAlert] = []
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.operation_counts: Dict[AdminOperationType, int] = defaultdict(int)
        self.error_counts: Dict[AdminOperationType, int] = defaultdict(int)
        self.response_times: Dict[AdminOperationType, deque] = defaultdict(lambda: deque(maxlen=100))
        self.concurrent_admins: set = set()
        self.lock = threading.RLock()
        
        # Performance thresholds
        self.performance_thresholds = {
            AdminOperationType.COST_DASHBOARD: 2.0,  # seconds
            AdminOperationType.USER_MANAGEMENT: 1.5,
            AdminOperationType.BUDGET_MANAGEMENT: 1.0,
            AdminOperationType.ROLE_MANAGEMENT: 0.5,
            AdminOperationType.SYSTEM_HEALTH: 1.0,
            AdminOperationType.USER_ROLE_QUERY: 0.3
        }
    
    def record_operation_start(self, operation_type: AdminOperationType, admin_email: str, request_data: Dict[str, Any] = None) -> str:
        """Record the start of an admin operation"""
        operation_id = f"{operation_type.value}_{admin_email}_{int(time.time() * 1000)}"
        
        with self.lock:
            self.active_operations[operation_id] = {
                'operation_type': operation_type,
                'admin_email': admin_email,
                'start_time': time.time(),
                'request_data': request_data or {}
            }
            self.concurrent_admins.add(admin_email)
            
            # Record concurrent users metric
            self._add_metric(
                operation_type,
                AdminMetricType.CONCURRENT_USERS,
                len(self.concurrent_admins),
                admin_email
            )
        
        logger.info(f"🎯 Admin operation started: {operation_type.value} by {admin_email}")
        return operation_id
    
    def record_operation_end(self, operation_id: str, success: bool = True, response_data: Dict[str, Any] = None, error_message: str = None) -> None:
        """Record the end of an admin operation"""
        with self.lock:
            if operation_id not in self.active_operations:
                logger.warning(f"⚠️ Unknown operation ID: {operation_id}")
                return
            
            operation = self.active_operations.pop(operation_id)
            operation_type = operation['operation_type']
            admin_email = operation['admin_email']
            duration = time.time() - operation['start_time']
            
            # Record operation count
            self.operation_counts[operation_type] += 1
            self._add_metric(operation_type, AdminMetricType.OPERATION_COUNT, 1, admin_email)
            
            # Record duration
            self.response_times[operation_type].append(duration)
            self._add_metric(operation_type, AdminMetricType.OPERATION_DURATION, duration, admin_email)
            
            # Record response size if available
            if response_data:
                response_size = len(json.dumps(response_data))
                self._add_metric(operation_type, AdminMetricType.RESPONSE_SIZE, response_size, admin_email)
            
            # Record errors
            if not success:
                self.error_counts[operation_type] += 1
                self._add_metric(operation_type, AdminMetricType.ERROR_COUNT, 1, admin_email)
                
                # Create alert for errors
                self._create_alert(
                    alert_type="operation_error",
                    severity="medium",
                    message=f"Admin operation failed: {operation_type.value} - {error_message}",
                    operation_type=operation_type,
                    admin_email=admin_email
                )
            
            # Check performance thresholds
            threshold = self.performance_thresholds.get(operation_type, 2.0)
            if duration > threshold:
                self._create_alert(
                    alert_type="performance_warning",
                    severity="low" if duration < threshold * 2 else "medium",
                    message=f"Slow admin operation: {operation_type.value} took {duration:.2f}s (threshold: {threshold}s)",
                    operation_type=operation_type,
                    admin_email=admin_email
                )
            
            # Calculate success rate
            total_ops = self.operation_counts[operation_type]
            error_ops = self.error_counts[operation_type]
            success_rate = ((total_ops - error_ops) / total_ops) * 100 if total_ops > 0 else 100
            self._add_metric(operation_type, AdminMetricType.SUCCESS_RATE, success_rate, admin_email)
            
            logger.info(f"✅ Admin operation completed: {operation_type.value} by {admin_email} in {duration:.3f}s (success: {success})")
    
    def _add_metric(self, operation_type: AdminOperationType, metric_type: AdminMetricType, value: float, admin_email: str, additional_data: Dict[str, Any] = None) -> None:
        """Add a metric to the collection"""
        metric = AdminOperationMetric(
            operation_type=operation_type,
            metric_type=metric_type,
            value=value,
            admin_email=admin_email,
            timestamp=datetime.utcnow(),
            additional_data=additional_data
        )
        self.metrics.append(metric)
    
    def _create_alert(self, alert_type: str, severity: str, message: str, operation_type: AdminOperationType = None, admin_email: str = None) -> None:
        """Create a new alert"""
        alert = AdminAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            operation_type=operation_type,
            admin_email=admin_email,
            timestamp=datetime.utcnow()
        )
        self.alerts.append(alert)
        
        # Log based on severity
        if severity == "critical":
            logger.critical(f"🚨 CRITICAL ALERT: {message}")
        elif severity == "high":
            logger.error(f"🔴 HIGH ALERT: {message}")
        elif severity == "medium":
            logger.warning(f"🟡 MEDIUM ALERT: {message}")
        else:
            logger.info(f"🔵 LOW ALERT: {message}")
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of metrics for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
            
            summary = {
                'time_period_hours': hours,
                'total_operations': len([m for m in recent_metrics if m.metric_type == AdminMetricType.OPERATION_COUNT]),
                'unique_admins': len(set(m.admin_email for m in recent_metrics)),
                'operation_breakdown': {},
                'performance_stats': {},
                'error_summary': {},
                'current_alerts': len([a for a in self.alerts if not a.resolved]),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Operation breakdown
            for op_type in AdminOperationType:
                op_metrics = [m for m in recent_metrics if m.operation_type == op_type]
                count_metrics = [m for m in op_metrics if m.metric_type == AdminMetricType.OPERATION_COUNT]
                duration_metrics = [m for m in op_metrics if m.metric_type == AdminMetricType.OPERATION_DURATION]
                error_metrics = [m for m in op_metrics if m.metric_type == AdminMetricType.ERROR_COUNT]
                
                total_count = sum(m.value for m in count_metrics)
                avg_duration = sum(m.value for m in duration_metrics) / len(duration_metrics) if duration_metrics else 0
                total_errors = sum(m.value for m in error_metrics)
                success_rate = ((total_count - total_errors) / total_count) * 100 if total_count > 0 else 100
                
                summary['operation_breakdown'][op_type.value] = {
                    'total_operations': total_count,
                    'average_duration': round(avg_duration, 3),
                    'total_errors': total_errors,
                    'success_rate': round(success_rate, 2)
                }
            
            # Performance stats
            for op_type in AdminOperationType:
                durations = [m.value for m in recent_metrics if m.operation_type == op_type and m.metric_type == AdminMetricType.OPERATION_DURATION]
                if durations:
                    summary['performance_stats'][op_type.value] = {
                        'min_duration': round(min(durations), 3),
                        'max_duration': round(max(durations), 3),
                        'avg_duration': round(sum(durations) / len(durations), 3),
                        'threshold': self.performance_thresholds.get(op_type, 2.0),
                        'violations': len([d for d in durations if d > self.performance_thresholds.get(op_type, 2.0)])
                    }
            
            return summary
    
    def get_alerts(self, severity: str = None, resolved: bool = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering"""
        filtered_alerts = self.alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if resolved is not None:
            filtered_alerts = [a for a in filtered_alerts if a.resolved == resolved]
        
        # Sort by timestamp descending and limit
        filtered_alerts = sorted(filtered_alerts, key=lambda a: a.timestamp, reverse=True)[:limit]
        
        return [alert.to_dict() for alert in filtered_alerts]
    
    def resolve_alert(self, alert_index: int, resolution_notes: str, admin_email: str) -> bool:
        """Resolve an alert"""
        try:
            if 0 <= alert_index < len(self.alerts):
                self.alerts[alert_index].resolved = True
                self.alerts[alert_index].resolution_notes = resolution_notes
                logger.info(f"🔄 Alert resolved by {admin_email}: {resolution_notes}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to resolve alert: {e}")
            return False
    
    def cleanup_old_data(self, days: int = 7) -> None:
        """Clean up old metrics and resolved alerts"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        with self.lock:
            # Remove old metrics (deque handles this automatically, but we can log)
            old_count = len([m for m in self.metrics if m.timestamp < cutoff_time])
            
            # Remove old resolved alerts
            old_alerts = [a for a in self.alerts if a.resolved and a.timestamp < cutoff_time]
            for alert in old_alerts:
                self.alerts.remove(alert)
            
            logger.info(f"🧹 Cleaned up {old_count} old metrics and {len(old_alerts)} old resolved alerts")


# Global metrics collector instance
admin_metrics_collector = AdminMetricsCollector()


def monitor_admin_operation(operation_type: AdminOperationType):
    """Decorator to monitor admin operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(req, *args, **kwargs):
            # Extract admin email from request
            admin_user = getattr(req, 'user', None)
            admin_email = admin_user.email if admin_user else 'unknown'
            
            # Start monitoring
            operation_id = admin_metrics_collector.record_operation_start(
                operation_type=operation_type,
                admin_email=admin_email,
                request_data={
                    'method': req.method,
                    'url': req.url,
                    'params': dict(req.params) if hasattr(req, 'params') else {}
                }
            )
            
            try:
                # Execute the function
                result = await func(req, *args, **kwargs)
                
                # Extract response data for metrics
                response_data = {}
                if hasattr(result, 'get_body'):
                    try:
                        response_data = json.loads(result.get_body().decode())
                    except:
                        pass
                
                # Record successful completion
                admin_metrics_collector.record_operation_end(
                    operation_id=operation_id,
                    success=True,
                    response_data=response_data
                )
                
                return result
                
            except Exception as e:
                # Record failure
                admin_metrics_collector.record_operation_end(
                    operation_id=operation_id,
                    success=False,
                    error_message=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(req, *args, **kwargs):
            # Extract admin email from request
            admin_user = getattr(req, 'user', None)
            admin_email = admin_user.email if admin_user else 'unknown'
            
            # Start monitoring
            operation_id = admin_metrics_collector.record_operation_start(
                operation_type=operation_type,
                admin_email=admin_email,
                request_data={
                    'method': req.method,
                    'url': req.url,
                    'params': dict(req.params) if hasattr(req, 'params') else {}
                }
            )
            
            try:
                # Execute the function
                result = func(req, *args, **kwargs)
                
                # Extract response data for metrics
                response_data = {}
                if hasattr(result, 'get_body'):
                    try:
                        response_data = json.loads(result.get_body().decode())
                    except:
                        pass
                
                # Record successful completion
                admin_metrics_collector.record_operation_end(
                    operation_id=operation_id,
                    success=True,
                    response_data=response_data
                )
                
                return result
                
            except Exception as e:
                # Record failure
                admin_metrics_collector.record_operation_end(
                    operation_id=operation_id,
                    success=False,
                    error_message=str(e)
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
