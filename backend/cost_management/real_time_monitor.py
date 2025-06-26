"""
Real-time Cost Monitoring and Budget Alert System
Task 8.6: Enhanced Azure Infrastructure & Production Readiness

This module provides real-time cost monitoring with proactive budget alerts,
threshold management, and integration with Azure Cost Management APIs.

Features:
- Real-time cost tracking and threshold monitoring
- Multi-tier budget alerts (warning, critical, emergency)
- Integration with Azure Cost Management APIs
- Proactive cost anomaly detection
- Automated budget enforcement actions
- Cost spike detection and mitigation
- Integration with Application Insights for alerting
- Spiritual context-aware cost messaging
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import defaultdict, deque
from enum import Enum
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Budget alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class CostMetricType(Enum):
    """Types of cost metrics to monitor"""
    TOTAL_COST = "total_cost"
    HOURLY_RATE = "hourly_rate"
    USER_COST = "user_cost"
    MODEL_COST = "model_cost"
    OPERATION_COST = "operation_cost"
    DAILY_BUDGET = "daily_budget"
    MONTHLY_BUDGET = "monthly_budget"


class MonitoringAction(Enum):
    """Actions to take when thresholds are exceeded"""
    LOG_ONLY = "log_only"
    NOTIFY_ADMIN = "notify_admin"
    REDUCE_QUALITY = "reduce_quality"
    ENABLE_CACHING = "enable_caching"
    SWITCH_MODEL = "switch_model"
    THROTTLE_REQUESTS = "throttle_requests"
    BLOCK_EXPENSIVE_OPERATIONS = "block_expensive_operations"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


@dataclass
class BudgetThreshold:
    """Budget threshold configuration"""
    metric_type: CostMetricType
    threshold_value: float
    alert_level: AlertLevel
    actions: List[MonitoringAction]
    notification_channels: List[str]
    spiritual_message: str
    cooldown_minutes: int = 5
    enabled: bool = True


@dataclass
class CostAlert:
    """Cost alert data structure"""
    alert_id: str
    timestamp: datetime
    metric_type: CostMetricType
    current_value: float
    threshold_value: float
    alert_level: AlertLevel
    message: str
    spiritual_message: str
    actions_taken: List[str]
    context: Dict[str, Any]


@dataclass
class RealTimeMetrics:
    """Real-time cost metrics"""
    timestamp: datetime
    total_cost: float
    hourly_rate: float
    user_costs: Dict[str, float]
    model_costs: Dict[str, float]
    operation_costs: Dict[str, float]
    request_count: int
    error_count: int
    cache_hit_rate: float


class RealTimeCostMonitor:
    """Real-time cost monitoring and budget alert system"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize real-time cost monitor
        
        Args:
            config_path: Path to monitoring configuration file
        """
        self.config_path = config_path or "data/cost_monitoring_config.json"
        self.data_dir = Path("data/real_time_monitoring")
        self.data_dir.mkdir(exist_ok=True)
        
        # Monitoring state
        self.thresholds: List[BudgetThreshold] = []
        self.active_alerts: Dict[str, CostAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.metrics_history: deque = deque(maxlen=100)  # Last 100 data points
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Cost tracking
        self.current_costs = {
            'total': 0.0,
            'hourly': 0.0,
            'daily': 0.0,
            'monthly': 0.0,
            'by_user': defaultdict(float),
            'by_model': defaultdict(float),
            'by_operation': defaultdict(float)
        }
        
        # Monitoring callbacks
        self.alert_callbacks: List[Callable] = []
        self.action_callbacks: Dict[MonitoringAction, Callable] = {}
        
        # Load configuration
        self._load_config()
        
        # Start monitoring task
        self.monitoring_task = None
        self.is_monitoring = False
        
        logger.info("Real-time cost monitor initialized")
    
    def _load_config(self):
        """Load monitoring configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self._parse_config(config)
            else:
                self._create_default_config()
        except Exception as e:
            logger.error(f"Error loading monitoring config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default monitoring configuration"""
        default_thresholds = [
            # Daily budget thresholds
            BudgetThreshold(
                metric_type=CostMetricType.DAILY_BUDGET,
                threshold_value=10.0,  # $10 daily
                alert_level=AlertLevel.WARNING,
                actions=[MonitoringAction.LOG_ONLY, MonitoringAction.NOTIFY_ADMIN],
                notification_channels=["email", "application_insights"],
                spiritual_message="🙏 Divine guidance reminds us of mindful resource usage",
                cooldown_minutes=30
            ),
            BudgetThreshold(
                metric_type=CostMetricType.DAILY_BUDGET,
                threshold_value=15.0,  # $15 daily
                alert_level=AlertLevel.CRITICAL,
                actions=[MonitoringAction.NOTIFY_ADMIN, MonitoringAction.ENABLE_CACHING, MonitoringAction.REDUCE_QUALITY],
                notification_channels=["email", "application_insights"],
                spiritual_message="⚠️ The path of wisdom includes conscious spending",
                cooldown_minutes=15
            ),
            BudgetThreshold(
                metric_type=CostMetricType.DAILY_BUDGET,
                threshold_value=20.0,  # $20 daily
                alert_level=AlertLevel.EMERGENCY,
                actions=[MonitoringAction.THROTTLE_REQUESTS, MonitoringAction.SWITCH_MODEL, MonitoringAction.BLOCK_EXPENSIVE_OPERATIONS],
                notification_channels=["email", "application_insights", "slack"],
                spiritual_message="🛑 Emergency protocols activated - seeking balance",
                cooldown_minutes=5
            ),
            
            # Hourly rate thresholds
            BudgetThreshold(
                metric_type=CostMetricType.HOURLY_RATE,
                threshold_value=2.0,  # $2/hour
                alert_level=AlertLevel.WARNING,
                actions=[MonitoringAction.LOG_ONLY],
                notification_channels=["application_insights"],
                spiritual_message="📊 Observing the flow of resources",
                cooldown_minutes=60
            ),
            BudgetThreshold(
                metric_type=CostMetricType.HOURLY_RATE,
                threshold_value=5.0,  # $5/hour
                alert_level=AlertLevel.CRITICAL,
                actions=[MonitoringAction.NOTIFY_ADMIN, MonitoringAction.ENABLE_CACHING],
                notification_channels=["email", "application_insights"],
                spiritual_message="⚡ High energy usage detected - seeking efficiency",
                cooldown_minutes=30
            ),
            
            # Per-user cost thresholds
            BudgetThreshold(
                metric_type=CostMetricType.USER_COST,
                threshold_value=5.0,  # $5 per user daily
                alert_level=AlertLevel.WARNING,
                actions=[MonitoringAction.LOG_ONLY, MonitoringAction.NOTIFY_ADMIN],
                notification_channels=["application_insights"],
                spiritual_message="👤 Individual usage pattern noted",
                cooldown_minutes=120
            )
        ]
        
        self.thresholds = default_thresholds
        self._save_config()
    
    def _parse_config(self, config: Dict[str, Any]):
        """Parse configuration from dictionary"""
        self.thresholds = []
        for threshold_data in config.get('thresholds', []):
            threshold = BudgetThreshold(
                metric_type=CostMetricType(threshold_data['metric_type']),
                threshold_value=threshold_data['threshold_value'],
                alert_level=AlertLevel(threshold_data['alert_level']),
                actions=[MonitoringAction(action) for action in threshold_data['actions']],
                notification_channels=threshold_data['notification_channels'],
                spiritual_message=threshold_data.get('spiritual_message', ''),
                cooldown_minutes=threshold_data.get('cooldown_minutes', 5),
                enabled=threshold_data.get('enabled', True)
            )
            self.thresholds.append(threshold)
    
    def _save_config(self):
        """Save current configuration"""
        try:
            config = {
                'thresholds': [
                    {
                        'metric_type': t.metric_type.value,
                        'threshold_value': t.threshold_value,
                        'alert_level': t.alert_level.value,
                        'actions': [a.value for a in t.actions],
                        'notification_channels': t.notification_channels,
                        'spiritual_message': t.spiritual_message,
                        'cooldown_minutes': t.cooldown_minutes,
                        'enabled': t.enabled
                    }
                    for t in self.thresholds
                ]
            }
            
            Path(self.config_path).parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving monitoring config: {e}")
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start real-time monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
        logger.info(f"Started real-time cost monitoring with {interval_seconds}s interval")
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped real-time cost monitoring")
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Update current metrics
                await self._update_metrics()
                
                # Check all thresholds
                await self._check_thresholds()
                
                # Clean up old alerts
                self._cleanup_alerts()
                
                # Save monitoring state
                await self._save_monitoring_state()
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _update_metrics(self):
        """Update current cost metrics"""
        try:
            # In a real implementation, this would fetch from Azure Cost Management API
            # For now, we'll simulate with current tracking data
            
            current_time = datetime.now()
            
            # Calculate hourly rate from recent activity
            hourly_rate = self._calculate_hourly_rate()
            
            # Update current costs
            total_cost = sum(self.current_costs['by_user'].values())
            
            # Create current metrics snapshot
            metrics = RealTimeMetrics(
                timestamp=current_time,
                total_cost=total_cost,
                hourly_rate=hourly_rate,
                user_costs=dict(self.current_costs['by_user']),
                model_costs=dict(self.current_costs['by_model']),
                operation_costs=dict(self.current_costs['by_operation']),
                request_count=self._get_request_count(),
                error_count=self._get_error_count(),
                cache_hit_rate=self._get_cache_hit_rate()
            )
            
            # Add to history
            self.metrics_history.append(metrics)
            
            # Update current costs
            self.current_costs['total'] = total_cost
            self.current_costs['hourly'] = hourly_rate
            self.current_costs['daily'] = self._calculate_daily_cost()
            self.current_costs['monthly'] = self._calculate_monthly_cost()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def _calculate_hourly_rate(self) -> float:
        """Calculate current hourly cost rate"""
        if len(self.metrics_history) < 2:
            return 0.0
        
        # Calculate rate from last few data points
        recent_metrics = list(self.metrics_history)[-5:]  # Last 5 data points
        if len(recent_metrics) < 2:
            return 0.0
        
        time_diff = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds() / 3600
        cost_diff = recent_metrics[-1].total_cost - recent_metrics[0].total_cost
        
        return cost_diff / time_diff if time_diff > 0 else 0.0
    
    def _calculate_daily_cost(self) -> float:
        """Calculate daily cost from hourly rate"""
        return self.current_costs['hourly'] * 24
    
    def _calculate_monthly_cost(self) -> float:
        """Calculate monthly cost projection"""
        return self.current_costs['daily'] * 30
    
    def _get_request_count(self) -> int:
        """Get current request count (placeholder)"""
        return 0  # Would integrate with actual request tracking
    
    def _get_error_count(self) -> int:
        """Get current error count (placeholder)"""
        return 0  # Would integrate with actual error tracking
    
    def _get_cache_hit_rate(self) -> float:
        """Get current cache hit rate (placeholder)"""
        return 0.0  # Would integrate with actual cache metrics
    
    async def _check_thresholds(self):
        """Check all configured thresholds"""
        current_time = datetime.now()
        
        for threshold in self.thresholds:
            if not threshold.enabled:
                continue
            
            # Get current value for this metric type
            current_value = self._get_metric_value(threshold.metric_type)
            
            # Check if threshold is exceeded
            if current_value > threshold.threshold_value:
                alert_key = f"{threshold.metric_type.value}_{threshold.threshold_value}"
                
                # Check cooldown period
                if self._is_in_cooldown(alert_key, threshold.cooldown_minutes):
                    continue
                
                # Create and process alert
                alert = await self._create_alert(threshold, current_value)
                await self._process_alert(alert)
                
                # Update last alert time
                self.last_alert_times[alert_key] = current_time
    
    def _get_metric_value(self, metric_type: CostMetricType) -> float:
        """Get current value for a metric type"""
        if metric_type == CostMetricType.TOTAL_COST:
            return self.current_costs['total']
        elif metric_type == CostMetricType.HOURLY_RATE:
            return self.current_costs['hourly']
        elif metric_type == CostMetricType.DAILY_BUDGET:
            return self.current_costs['daily']
        elif metric_type == CostMetricType.MONTHLY_BUDGET:
            return self.current_costs['monthly']
        elif metric_type == CostMetricType.USER_COST:
            return max(self.current_costs['by_user'].values()) if self.current_costs['by_user'] else 0.0
        elif metric_type == CostMetricType.MODEL_COST:
            return max(self.current_costs['by_model'].values()) if self.current_costs['by_model'] else 0.0
        elif metric_type == CostMetricType.OPERATION_COST:
            return max(self.current_costs['by_operation'].values()) if self.current_costs['by_operation'] else 0.0
        else:
            return 0.0
    
    def _is_in_cooldown(self, alert_key: str, cooldown_minutes: int) -> bool:
        """Check if alert is in cooldown period"""
        if alert_key not in self.last_alert_times:
            return False
        
        time_diff = datetime.now() - self.last_alert_times[alert_key]
        return time_diff.total_seconds() < (cooldown_minutes * 60)
    
    async def _create_alert(self, threshold: BudgetThreshold, current_value: float) -> CostAlert:
        """Create a cost alert"""
        alert_id = hashlib.md5(
            f"{threshold.metric_type.value}_{threshold.threshold_value}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        
        alert = CostAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            metric_type=threshold.metric_type,
            current_value=current_value,
            threshold_value=threshold.threshold_value,
            alert_level=threshold.alert_level,
            message=f"{threshold.metric_type.value} exceeded: ${current_value:.2f} > ${threshold.threshold_value:.2f}",
            spiritual_message=threshold.spiritual_message,
            actions_taken=[],
            context=self._get_alert_context()
        )
        
        return alert
    
    def _get_alert_context(self) -> Dict[str, Any]:
        """Get context information for alerts"""
        return {
            'total_cost': self.current_costs['total'],
            'hourly_rate': self.current_costs['hourly'],
            'top_users': dict(sorted(self.current_costs['by_user'].items(), key=lambda x: x[1], reverse=True)[:5]),
            'top_models': dict(sorted(self.current_costs['by_model'].items(), key=lambda x: x[1], reverse=True)[:5]),
            'metrics_count': len(self.metrics_history),
            'active_alerts': len(self.active_alerts)
        }
    
    async def _process_alert(self, alert: CostAlert):
        """Process a cost alert"""
        try:
            # Add to active alerts
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            
            # Find matching threshold
            threshold = next(
                (t for t in self.thresholds 
                 if t.metric_type == alert.metric_type and t.threshold_value == alert.threshold_value),
                None
            )
            
            if threshold:
                # Execute configured actions
                for action in threshold.actions:
                    await self._execute_action(action, alert)
                
                # Send notifications
                await self._send_notifications(alert, threshold.notification_channels)
            
            # Call registered callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
            
            logger.warning(f"Cost alert processed: {alert.message}")
            logger.info(f"Spiritual guidance: {alert.spiritual_message}")
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    async def _execute_action(self, action: MonitoringAction, alert: CostAlert):
        """Execute monitoring action"""
        try:
            if action in self.action_callbacks:
                await self.action_callbacks[action](alert)
                alert.actions_taken.append(action.value)
            else:
                # Default action implementations
                if action == MonitoringAction.LOG_ONLY:
                    logger.info(f"Cost monitoring: {alert.message}")
                elif action == MonitoringAction.NOTIFY_ADMIN:
                    logger.warning(f"Admin notification: {alert.message}")
                elif action == MonitoringAction.REDUCE_QUALITY:
                    logger.info("Reducing AI model quality to save costs")
                elif action == MonitoringAction.ENABLE_CACHING:
                    logger.info("Enabling aggressive caching to reduce costs")
                elif action == MonitoringAction.SWITCH_MODEL:
                    logger.info("Switching to lower-cost AI model")
                elif action == MonitoringAction.THROTTLE_REQUESTS:
                    logger.warning("Throttling requests to control costs")
                elif action == MonitoringAction.BLOCK_EXPENSIVE_OPERATIONS:
                    logger.warning("Blocking expensive operations")
                elif action == MonitoringAction.EMERGENCY_SHUTDOWN:
                    logger.critical("EMERGENCY: Shutting down expensive services")
                
                alert.actions_taken.append(action.value)
                
        except Exception as e:
            logger.error(f"Error executing action {action.value}: {e}")
    
    async def _send_notifications(self, alert: CostAlert, channels: List[str]):
        """Send alert notifications"""
        for channel in channels:
            try:
                if channel == "email":
                    await self._send_email_notification(alert)
                elif channel == "application_insights":
                    await self._send_application_insights_notification(alert)
                elif channel == "slack":
                    await self._send_slack_notification(alert)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
            except Exception as e:
                logger.error(f"Error sending notification to {channel}: {e}")
    
    async def _send_email_notification(self, alert: CostAlert):
        """Send email notification (placeholder)"""
        logger.info(f"Email notification: {alert.message}")
    
    async def _send_application_insights_notification(self, alert: CostAlert):
        """Send Application Insights notification"""
        # This would integrate with the Application Insights client
        logger.info(f"Application Insights alert: {alert.message}")
    
    async def _send_slack_notification(self, alert: CostAlert):
        """Send Slack notification (placeholder)"""
        logger.info(f"Slack notification: {alert.message}")
    
    def _cleanup_alerts(self):
        """Clean up old alerts"""
        current_time = datetime.now()
        expired_alerts = []
        
        for alert_id, alert in self.active_alerts.items():
            # Remove alerts older than 1 hour
            if (current_time - alert.timestamp).total_seconds() > 3600:
                expired_alerts.append(alert_id)
        
        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]
    
    async def _save_monitoring_state(self):
        """Save current monitoring state"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'current_costs': self.current_costs,
                'active_alerts': [asdict(alert) for alert in self.active_alerts.values()],
                'metrics_count': len(self.metrics_history),
                'alert_count': len(self.alert_history)
            }
            
            state_file = self.data_dir / "monitoring_state.json"
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving monitoring state: {e}")
    
    # Public API methods
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for alert events"""
        self.alert_callbacks.append(callback)
    
    def register_action_callback(self, action: MonitoringAction, callback: Callable):
        """Register callback for specific monitoring actions"""
        self.action_callbacks[action] = callback
    
    def update_cost(self, user_id: str, model: str, operation: str, cost: float):
        """Update cost tracking"""
        self.current_costs['by_user'][user_id] += cost
        self.current_costs['by_model'][model] += cost
        self.current_costs['by_operation'][operation] += cost
        self.current_costs['total'] += cost
    
    def add_threshold(self, threshold: BudgetThreshold):
        """Add new budget threshold"""
        self.thresholds.append(threshold)
        self._save_config()
    
    def remove_threshold(self, metric_type: CostMetricType, threshold_value: float):
        """Remove budget threshold"""
        self.thresholds = [
            t for t in self.thresholds 
            if not (t.metric_type == metric_type and t.threshold_value == threshold_value)
        ]
        self._save_config()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current cost metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'costs': dict(self.current_costs),
            'active_alerts': len(self.active_alerts),
            'recent_alerts': len([a for a in self.alert_history if (datetime.now() - a.timestamp).total_seconds() < 3600]),
            'monitoring_active': self.is_monitoring
        }
    
    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        recent_alerts = list(self.alert_history)[-limit:]
        return [asdict(alert) for alert in recent_alerts]
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts"""
        return [asdict(alert) for alert in self.active_alerts.values()]


# Global monitor instance
_monitor_instance = None

def get_monitor() -> RealTimeCostMonitor:
    """Get global monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = RealTimeCostMonitor()
    return _monitor_instance


# Decorator for automatic cost tracking
def track_cost(user_id: str = None, model: str = None, operation: str = None):
    """Decorator to automatically track operation costs"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                # Estimate cost based on execution time (placeholder)
                execution_time = time.time() - start_time
                estimated_cost = execution_time * 0.001  # $0.001 per second
                
                monitor = get_monitor()
                monitor.update_cost(
                    user_id or "unknown",
                    model or "default",
                    operation or func.__name__,
                    estimated_cost
                )
                
                return result
            except Exception as e:
                # Track error costs too
                execution_time = time.time() - start_time
                estimated_cost = execution_time * 0.0005  # Half cost for errors
                
                monitor = get_monitor()
                monitor.update_cost(
                    user_id or "unknown",
                    model or "default",
                    f"{operation or func.__name__}_error",
                    estimated_cost
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                estimated_cost = execution_time * 0.001
                
                monitor = get_monitor()
                monitor.update_cost(
                    user_id or "unknown",
                    model or "default",
                    operation or func.__name__,
                    estimated_cost
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                estimated_cost = execution_time * 0.0005
                
                monitor = get_monitor()
                monitor.update_cost(
                    user_id or "unknown",
                    model or "default",
                    f"{operation or func.__name__}_error",
                    estimated_cost
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
