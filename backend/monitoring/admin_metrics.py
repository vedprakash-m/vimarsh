"""
Admin-Specific Metrics and Monitoring System for Vimarsh
Provides comprehensive monitoring for admin operations with real-time alerting
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
from enum import Enum
import json

# Import performance monitoring and cache service
try:
    from monitoring.performance_monitor import get_performance_monitor, MetricType, AlertLevel
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False

try:
    from services.cache_service import get_admin_cache_service
    CACHE_SERVICE_AVAILABLE = True
except ImportError:
    CACHE_SERVICE_AVAILABLE = False

# Import unified configuration
try:
    from config.unified_config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger(__name__)


class AdminOperationType(Enum):
    """Types of admin operations to track"""
    USER_MANAGEMENT = "user_management"
    COST_MONITORING = "cost_monitoring"
    SYSTEM_HEALTH = "system_health"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    CONFIGURATION_CHANGE = "configuration_change"
    DATA_EXPORT = "data_export"
    BACKUP_RESTORE = "backup_restore"


class AdminMetricType(Enum):
    """Admin-specific metric types"""
    OPERATION_SUCCESS_RATE = "operation_success_rate"
    OPERATION_LATENCY = "operation_latency"
    USER_SESSION_COUNT = "user_session_count"
    ADMIN_LOGIN_COUNT = "admin_login_count"
    COST_ALERT_COUNT = "cost_alert_count"
    SECURITY_INCIDENT_COUNT = "security_incident_count"
    DATA_EXPORT_SIZE = "data_export_size"
    CONFIG_CHANGE_COUNT = "config_change_count"


@dataclass
class AdminOperation:
    """Admin operation record for tracking"""
    operation_id: str
    operation_type: AdminOperationType
    admin_user_id: str
    admin_email: str
    timestamp: datetime
    duration_ms: float
    success: bool
    details: Dict[str, Any]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/API"""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "admin_user_id": self.admin_user_id,
            "admin_email": self.admin_email,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "success": self.success,
            "details": self.details,
            "error_message": self.error_message
        }


@dataclass
class AdminAlert:
    """Admin-specific alert for operations"""
    alert_id: str
    alert_type: str
    severity: AlertLevel
    message: str
    operation_type: Optional[AdminOperationType]
    admin_user_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "message": self.message,
            "operation_type": self.operation_type.value if self.operation_type else None,
            "admin_user_id": self.admin_user_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class AdminMetricsCollector:
    """Collects and manages admin-specific metrics"""
    
    def __init__(self, max_operations: int = 10000):
        self.max_operations = max_operations
        
        # Storage for admin operations and metrics
        self.operations: deque[AdminOperation] = deque(maxlen=max_operations)
        self.alerts: deque[AdminAlert] = deque(maxlen=1000)
        self.metrics: Dict[AdminMetricType, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Admin session tracking
        self.active_admin_sessions: Dict[str, datetime] = {}  # admin_id -> last_seen
        self.admin_operation_counts: Dict[str, Dict[AdminOperationType, int]] = defaultdict(lambda: defaultdict(int))
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[AdminAlert], None]] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configuration
        self._load_configuration()
        
        # Start monitoring tasks
        self._start_monitoring_tasks()
        
        logger.info("📊 Admin metrics collector initialized")
    
    def _load_configuration(self):
        """Load configuration for admin monitoring"""
        if CONFIG_AVAILABLE:
            config = get_config()
            self.max_operations = config.get_int('ADMIN_METRICS_MAX_OPERATIONS', self.max_operations)
            
            # Alert thresholds
            self.alert_thresholds = {
                'failed_operation_rate': config.get_float('ADMIN_ALERT_FAILED_OPERATION_RATE', 0.1),  # 10%
                'slow_operation_threshold': config.get_float('ADMIN_ALERT_SLOW_OPERATION_MS', 5000),  # 5 seconds
                'suspicious_login_threshold': config.get_int('ADMIN_ALERT_SUSPICIOUS_LOGIN_COUNT', 5),  # 5 failed logins
                'cost_alert_threshold': config.get_float('ADMIN_ALERT_COST_THRESHOLD', 100.0)  # $100
            }
        else:
            # Default thresholds
            self.alert_thresholds = {
                'failed_operation_rate': 0.1,
                'slow_operation_threshold': 5000,
                'suspicious_login_threshold': 5,
                'cost_alert_threshold': 100.0
            }
    
    def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        def monitoring_worker():
            while True:
                try:
                    self._check_admin_alerts()
                    self._cleanup_old_data()
                    self._update_derived_metrics()
                    # Check every minute
                    import time
                    time.sleep(60)
                except Exception as e:
                    logger.error(f"Error in admin monitoring worker: {e}")
        
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()
    
    def record_admin_operation(self,
                             operation_id: str,
                             operation_type: AdminOperationType,
                             admin_user_id: str,
                             admin_email: str,
                             duration_ms: float,
                             success: bool,
                             details: Optional[Dict[str, Any]] = None,
                             error_message: Optional[str] = None) -> AdminOperation:
        """Record an admin operation"""
        
        if details is None:
            details = {}
        
        operation = AdminOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            admin_user_id=admin_user_id,
            admin_email=admin_email,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
            success=success,
            details=details,
            error_message=error_message
        )
        
        with self._lock:
            self.operations.append(operation)
            
            # Update admin session tracking
            self.active_admin_sessions[admin_user_id] = operation.timestamp
            
            # Update operation counts
            self.admin_operation_counts[admin_user_id][operation_type] += 1
            
            # Record metrics for performance monitoring
            if PERFORMANCE_MONITOR_AVAILABLE:
                perf_monitor = get_performance_monitor()
                perf_monitor.record_metric(
                    MetricType.RESPONSE_TIME,
                    duration_ms,
                    {
                        "operation_type": operation_type.value,
                        "admin_user_id": admin_user_id,
                        "success": success
                    }
                )
        
        # Cache the operation if cache is available
        if CACHE_SERVICE_AVAILABLE:
            cache = get_admin_cache_service()
            cache_key = f"admin_operation:{operation_id}"
            cache.cache.put(cache_key, operation.to_dict(), 3600)  # 1 hour TTL
        
        logger.info(f"📊 Admin operation recorded: {operation_type.value} by {admin_email} ({'✅' if success else '❌'})")
        
        return operation
    
    def record_admin_login(self, admin_user_id: str, admin_email: str, success: bool, ip_address: Optional[str] = None):
        """Record admin login attempt"""
        
        details = {"ip_address": ip_address} if ip_address else {}
        
        self.record_admin_operation(
            operation_id=f"login_{admin_user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            operation_type=AdminOperationType.SECURITY_AUDIT,
            admin_user_id=admin_user_id,
            admin_email=admin_email,
            duration_ms=0,  # Login duration not typically measured
            success=success,
            details=details,
            error_message="Authentication failed" if not success else None
        )
        
        # Record metric
        with self._lock:
            self.metrics[AdminMetricType.ADMIN_LOGIN_COUNT].append({
                "timestamp": datetime.utcnow(),
                "admin_user_id": admin_user_id,
                "success": success
            })
    
    def record_cost_alert(self, alert_type: str, cost_amount: float, threshold: float, user_id: Optional[str] = None):
        """Record cost-related alert"""
        
        alert = AdminAlert(
            alert_id=f"cost_alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            alert_type=alert_type,
            severity=AlertLevel.WARNING if cost_amount < threshold * 1.5 else AlertLevel.CRITICAL,
            message=f"Cost alert: {alert_type} - ${cost_amount:.2f} (threshold: ${threshold:.2f})",
            operation_type=AdminOperationType.COST_MONITORING,
            admin_user_id=None,
            timestamp=datetime.utcnow(),
            metadata={
                "cost_amount": cost_amount,
                "threshold": threshold,
                "user_id": user_id,
                "alert_type": alert_type
            }
        )
        
        with self._lock:
            self.alerts.append(alert)
            self.metrics[AdminMetricType.COST_ALERT_COUNT].append({
                "timestamp": datetime.utcnow(),
                "cost_amount": cost_amount,
                "alert_type": alert_type
            })
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in admin alert callback: {e}")
        
        logger.warning(f"💰 Cost alert: {alert.message}")
    
    def record_security_incident(self, incident_type: str, admin_user_id: str, details: Dict[str, Any]):
        """Record security incident"""
        
        alert = AdminAlert(
            alert_id=f"security_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            alert_type=incident_type,
            severity=AlertLevel.CRITICAL,
            message=f"Security incident: {incident_type}",
            operation_type=AdminOperationType.SECURITY_AUDIT,
            admin_user_id=admin_user_id,
            timestamp=datetime.utcnow(),
            metadata=details
        )
        
        with self._lock:
            self.alerts.append(alert)
            self.metrics[AdminMetricType.SECURITY_INCIDENT_COUNT].append({
                "timestamp": datetime.utcnow(),
                "incident_type": incident_type,
                "admin_user_id": admin_user_id
            })
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in security alert callback: {e}")
        
        logger.critical(f"🚨 Security incident: {alert.message}")
    
    def _check_admin_alerts(self):
        """Check for admin alert conditions"""
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(minutes=15)  # 15-minute window
        
        with self._lock:
            # Check failed operation rate
            recent_ops = [op for op in self.operations if op.timestamp >= window_start]
            if len(recent_ops) >= 5:  # Minimum sample size
                failed_ops = [op for op in recent_ops if not op.success]
                failure_rate = len(failed_ops) / len(recent_ops)
                
                if failure_rate > self.alert_thresholds['failed_operation_rate']:
                    self._create_alert(
                        "high_failure_rate",
                        AlertLevel.WARNING,
                        f"High admin operation failure rate: {failure_rate*100:.1f}%",
                        {"failure_rate": failure_rate, "sample_size": len(recent_ops)}
                    )
            
            # Check for slow operations
            slow_ops = [op for op in recent_ops if op.duration_ms > self.alert_thresholds['slow_operation_threshold']]
            if len(slow_ops) > 0:
                for op in slow_ops:
                    self._create_alert(
                        "slow_operation",
                        AlertLevel.WARNING,
                        f"Slow admin operation: {op.operation_type.value} took {op.duration_ms:.0f}ms",
                        {"operation": op.to_dict()}
                    )
    
    def _create_alert(self, alert_type: str, severity: AlertLevel, message: str, metadata: Dict[str, Any]):
        """Create and store an alert"""
        
        alert = AdminAlert(
            alert_id=f"{alert_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            alert_type=alert_type,
            severity=severity,
            message=message,
            operation_type=None,
            admin_user_id=None,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        
        self.alerts.append(alert)
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        logger.log(
            logging.WARNING if severity in [AlertLevel.WARNING] else logging.CRITICAL,
            f"🚨 Admin alert: {message}"
        )
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent memory growth"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        with self._lock:
            # Clean up old admin sessions
            expired_sessions = [admin_id for admin_id, last_seen in self.active_admin_sessions.items()
                              if last_seen < cutoff_time]
            for admin_id in expired_sessions:
                del self.active_admin_sessions[admin_id]
    
    def _update_derived_metrics(self):
        """Update derived metrics for dashboards"""
        current_time = datetime.utcnow()
        
        with self._lock:
            # Update user session count
            active_sessions = len(self.active_admin_sessions)
            self.metrics[AdminMetricType.USER_SESSION_COUNT].append({
                "timestamp": current_time,
                "count": active_sessions
            })
            
            # Update operation success rates by type
            window_start = current_time - timedelta(hours=1)
            recent_ops = [op for op in self.operations if op.timestamp >= window_start]
            
            for op_type in AdminOperationType:
                type_ops = [op for op in recent_ops if op.operation_type == op_type]
                if type_ops:
                    success_count = sum(1 for op in type_ops if op.success)
                    success_rate = success_count / len(type_ops)
                    
                    self.metrics[AdminMetricType.OPERATION_SUCCESS_RATE].append({
                        "timestamp": current_time,
                        "operation_type": op_type.value,
                        "success_rate": success_rate,
                        "sample_size": len(type_ops)
                    })
    
    def get_admin_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive admin dashboard data"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            recent_ops = [op for op in self.operations if op.timestamp >= cutoff_time]
            recent_alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
            
            # Calculate summary statistics
            total_operations = len(recent_ops)
            successful_operations = sum(1 for op in recent_ops if op.success)
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 100
            
            # Operations by type
            ops_by_type = defaultdict(int)
            for op in recent_ops:
                ops_by_type[op.operation_type.value] += 1
            
            # Active admin users
            active_admins = len(self.active_admin_sessions)
            
            # Alert summary
            alerts_by_severity = defaultdict(int)
            for alert in recent_alerts:
                alerts_by_severity[alert.severity.value] += 1
            
            # Performance metrics
            if recent_ops:
                avg_duration = sum(op.duration_ms for op in recent_ops) / len(recent_ops)
                max_duration = max(op.duration_ms for op in recent_ops)
            else:
                avg_duration = 0
                max_duration = 0
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "window_hours": hours,
                "summary": {
                    "total_operations": total_operations,
                    "success_rate": round(success_rate, 1),
                    "active_admins": active_admins,
                    "total_alerts": len(recent_alerts),
                    "avg_operation_duration_ms": round(avg_duration, 2),
                    "max_operation_duration_ms": round(max_duration, 2)
                },
                "operations_by_type": dict(ops_by_type),
                "alerts_by_severity": dict(alerts_by_severity),
                "recent_operations": [op.to_dict() for op in recent_ops[-10:]],  # Last 10 operations
                "recent_alerts": [alert.to_dict() for alert in recent_alerts[-5:]],  # Last 5 alerts
                "active_admin_sessions": {
                    admin_id: last_seen.isoformat() 
                    for admin_id, last_seen in self.active_admin_sessions.items()
                }
            }
    
    def get_admin_performance_report(self, admin_user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get performance report for a specific admin user"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        with self._lock:
            admin_ops = [op for op in self.operations 
                        if op.admin_user_id == admin_user_id and op.timestamp >= cutoff_time]
            
            if not admin_ops:
                return {
                    "admin_user_id": admin_user_id,
                    "period_days": days,
                    "message": "No operations found for this admin user in the specified period"
                }
            
            # Calculate statistics
            total_ops = len(admin_ops)
            successful_ops = sum(1 for op in admin_ops if op.success)
            success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0
            
            # Operations by type
            ops_by_type = defaultdict(int)
            success_by_type = defaultdict(int)
            
            for op in admin_ops:
                ops_by_type[op.operation_type.value] += 1
                if op.success:
                    success_by_type[op.operation_type.value] += 1
            
            # Performance metrics
            avg_duration = sum(op.duration_ms for op in admin_ops) / len(admin_ops)
            
            return {
                "admin_user_id": admin_user_id,
                "period_days": days,
                "summary": {
                    "total_operations": total_ops,
                    "success_rate": round(success_rate, 1),
                    "avg_duration_ms": round(avg_duration, 2)
                },
                "operations_by_type": dict(ops_by_type),
                "success_rates_by_type": {
                    op_type: round((success_by_type[op_type] / ops_by_type[op_type] * 100), 1)
                    for op_type in ops_by_type.keys()
                }
            }
    
    def add_alert_callback(self, callback: Callable[[AdminAlert], None]):
        """Add callback for admin alerts"""
        self.alert_callbacks.append(callback)
        logger.info("📢 Added admin alert callback")


# Global admin metrics collector instance
_admin_metrics_collector = None

def get_admin_metrics_collector() -> AdminMetricsCollector:
    """Get the global admin metrics collector instance"""
    global _admin_metrics_collector
    if _admin_metrics_collector is None:
        _admin_metrics_collector = AdminMetricsCollector()
    return _admin_metrics_collector


# Decorator for automatic admin operation tracking
def track_admin_operation(operation_type: AdminOperationType, operation_details: Optional[Dict[str, Any]] = None):
    """Decorator to automatically track admin operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            import uuid
            
            # Extract admin user info from function arguments
            admin_user_id = kwargs.get('admin_user_id', 'unknown')
            admin_email = kwargs.get('admin_email', 'unknown@vimarsh.com')
            
            operation_id = str(uuid.uuid4())
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Record successful operation
                collector = get_admin_metrics_collector()
                collector.record_admin_operation(
                    operation_id=operation_id,
                    operation_type=operation_type,
                    admin_user_id=admin_user_id,
                    admin_email=admin_email,
                    duration_ms=duration_ms,
                    success=True,
                    details=operation_details or {}
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Record failed operation
                collector = get_admin_metrics_collector()
                collector.record_admin_operation(
                    operation_id=operation_id,
                    operation_type=operation_type,
                    admin_user_id=admin_user_id,
                    admin_email=admin_email,
                    duration_ms=duration_ms,
                    success=False,
                    details=operation_details or {},
                    error_message=str(e)
                )
                
                raise
        
        return wrapper
    return decorator


# Async version of the decorator
def track_admin_operation_async(operation_type: AdminOperationType, operation_details: Optional[Dict[str, Any]] = None):
    """Async decorator to automatically track admin operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import time
            import uuid
            
            # Extract admin user info from function arguments
            admin_user_id = kwargs.get('admin_user_id', 'unknown')
            admin_email = kwargs.get('admin_email', 'unknown@vimarsh.com')
            
            operation_id = str(uuid.uuid4())
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Record successful operation
                collector = get_admin_metrics_collector()
                collector.record_admin_operation(
                    operation_id=operation_id,
                    operation_type=operation_type,
                    admin_user_id=admin_user_id,
                    admin_email=admin_email,
                    duration_ms=duration_ms,
                    success=True,
                    details=operation_details or {}
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Record failed operation
                collector = get_admin_metrics_collector()
                collector.record_admin_operation(
                    operation_id=operation_id,
                    operation_type=operation_type,
                    admin_user_id=admin_user_id,
                    admin_email=admin_email,
                    duration_ms=duration_ms,
                    success=False,
                    details=operation_details or {},
                    error_message=str(e)
                )
                
                raise
        
        return wrapper
    return decorator
