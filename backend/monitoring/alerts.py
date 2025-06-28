"""
Alert system for Vimarsh monitoring.

This module provides alerting capabilities for performance, error rate,
and spiritual quality metrics.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class Alert:
    """Represents a monitoring alert."""
    
    alert_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    threshold: float
    current_value: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metrics': self.metrics,
            'threshold': self.threshold,
            'current_value': self.current_value
        }


class AlertManager:
    """Manages alerts for monitoring system."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.logger = logging.getLogger(__name__)
        self.active_alerts = {}
        self.alert_history = []
        
        # Default thresholds
        self.thresholds = {
            'response_time': 5.0,  # seconds
            'error_rate': 0.05,    # 5%
            'spiritual_quality': 0.7  # 70%
        }
    
    def create_performance_alert(self, metrics: Dict[str, Any]) -> Optional[Alert]:
        """Create performance alert if threshold exceeded."""
        response_time = metrics.get('avg_response_time', 0)
        threshold = self.thresholds['response_time']
        
        if response_time > threshold:
            alert = Alert(
                alert_id=f"perf_{datetime.now().timestamp()}",
                alert_type="performance",
                severity="warning" if response_time < threshold * 1.5 else "critical",
                message=f"High response time detected: {response_time:.2f}s",
                timestamp=datetime.now(),
                metrics=metrics,
                threshold=threshold,
                current_value=response_time
            )
            
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            self.logger.warning(f"Performance alert created: {alert.message}")
            return alert
        
        return None
    
    def create_error_rate_alert(self, metrics: Dict[str, Any]) -> Optional[Alert]:
        """Create error rate alert if threshold exceeded."""
        error_rate = metrics.get('error_rate', 0)
        threshold = self.thresholds['error_rate']
        
        if error_rate > threshold:
            alert = Alert(
                alert_id=f"error_{datetime.now().timestamp()}",
                alert_type="error_rate",
                severity="warning" if error_rate < threshold * 2 else "critical",
                message=f"High error rate detected: {error_rate:.2%}",
                timestamp=datetime.now(),
                metrics=metrics,
                threshold=threshold,
                current_value=error_rate
            )
            
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            self.logger.error(f"Error rate alert created: {alert.message}")
            return alert
        
        return None
    
    def create_spiritual_quality_alert(self, metrics: Dict[str, Any]) -> Optional[Alert]:
        """Create spiritual quality alert if threshold not met."""
        quality_score = metrics.get('spiritual_quality_score', 1.0)
        threshold = self.thresholds['spiritual_quality']
        
        if quality_score < threshold:
            alert = Alert(
                alert_id=f"quality_{datetime.now().timestamp()}",
                alert_type="spiritual_quality",
                severity="warning",
                message=f"Low spiritual quality score: {quality_score:.2%}",
                timestamp=datetime.now(),
                metrics=metrics,
                threshold=threshold,
                current_value=quality_score
            )
            
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            self.logger.warning(f"Spiritual quality alert created: {alert.message}")
            return alert
        
        return None
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts.pop(alert_id)
            self.logger.info(f"Alert resolved: {alert.message}")
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return self.alert_history[-limit:]
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """Update alert thresholds."""
        self.thresholds.update(new_thresholds)
        self.logger.info(f"Alert thresholds updated: {new_thresholds}")


class NotificationService:
    """Service for sending alert notifications."""
    
    def __init__(self):
        """Initialize notification service."""
        self.logger = logging.getLogger(__name__)
        self.notification_channels = {
            'email': True,
            'slack': False,
            'webhook': True
        }
    
    def send_alert_notification(self, alert: Alert) -> bool:
        """Send alert notification through configured channels."""
        try:
            self.logger.info(f"Sending notification for alert: {alert.alert_id}")
            
            # Email notification (simulated)
            if self.notification_channels['email']:
                self._send_email_notification(alert)
            
            # Webhook notification (simulated)
            if self.notification_channels['webhook']:
                self._send_webhook_notification(alert)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send alert notification: {e}")
            return False
    
    def _send_email_notification(self, alert: Alert) -> None:
        """Send email notification (simulated)."""
        self.logger.info(f"Email notification sent for alert: {alert.alert_type}")
    
    def _send_webhook_notification(self, alert: Alert) -> None:
        """Send webhook notification (simulated)."""
        self.logger.info(f"Webhook notification sent for alert: {alert.alert_type}")


# Global alert manager instance
alert_manager = AlertManager()
notification_service = NotificationService()
