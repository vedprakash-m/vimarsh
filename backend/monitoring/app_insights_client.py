"""
Application Insights Client for Vimarsh
Provides centralized Application Insights telemetry for spiritual guidance monitoring
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppInsightsClient:
    """Application Insights client for spiritual guidance monitoring"""
    
    def __init__(self, connection_string: str = None):
        """
        Initialize Application Insights client
        
        Args:
            connection_string: Application Insights connection string
        """
        self.connection_string = connection_string or os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
        self.enabled = bool(self.connection_string)
        
        # Try to import Azure Monitor OpenTelemetry if available
        self.telemetry_client = None
        if self.enabled:
            try:
                # For production deployment, this will use Azure Monitor OpenTelemetry
                # For now, we'll use standard logging with structured data
                logger.info("Application Insights client initialized")
            except ImportError:
                logger.warning("Azure Monitor packages not available - using standard logging")
                self.enabled = False
    
    def track_event(self, name: str, properties: Dict[str, Any] = None, measurements: Dict[str, float] = None):
        """Track custom event"""
        if not self.enabled:
            return
            
        try:
            event_data = {
                'event_name': name,
                'timestamp': datetime.now().isoformat(),
                'properties': properties or {},
                'measurements': measurements or {}
            }
            
            # In production, this would use the actual telemetry client
            # For now, use structured logging
            logger.info(f"APP_INSIGHTS_EVENT: {event_data}")
            
        except Exception as e:
            logger.error(f"Error tracking event {name}: {e}")
    
    def track_dependency(self, name: str, dependency_type: str, data: str, 
                        duration: float, success: bool, properties: Dict[str, Any] = None):
        """Track dependency call"""
        if not self.enabled:
            return
            
        try:
            dependency_data = {
                'dependency_name': name,
                'dependency_type': dependency_type,
                'data': data,
                'duration_ms': duration * 1000,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'properties': properties or {}
            }
            
            logger.info(f"APP_INSIGHTS_DEPENDENCY: {dependency_data}")
            
        except Exception as e:
            logger.error(f"Error tracking dependency {name}: {e}")
    
    def track_metric(self, name: str, value: float, properties: Dict[str, Any] = None):
        """Track custom metric"""
        if not self.enabled:
            return
            
        try:
            metric_data = {
                'metric_name': name,
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'properties': properties or {}
            }
            
            logger.info(f"APP_INSIGHTS_METRIC: {metric_data}")
            
        except Exception as e:
            logger.error(f"Error tracking metric {name}: {e}")
    
    def track_exception(self, exception: Exception, properties: Dict[str, Any] = None):
        """Track exception"""
        if not self.enabled:
            return
            
        try:
            exception_data = {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'timestamp': datetime.now().isoformat(),
                'properties': properties or {}
            }
            
            logger.error(f"APP_INSIGHTS_EXCEPTION: {exception_data}")
            
        except Exception as e:
            logger.error(f"Error tracking exception: {e}")
    
    def track_request(self, name: str, url: str, duration: float, response_code: int, 
                     success: bool, properties: Dict[str, Any] = None):
        """Track HTTP request"""
        if not self.enabled:
            return
            
        try:
            request_data = {
                'request_name': name,
                'url': url,
                'duration_ms': duration * 1000,
                'response_code': response_code,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'properties': properties or {}
            }
            
            logger.info(f"APP_INSIGHTS_REQUEST: {request_data}")
            
        except Exception as e:
            logger.error(f"Error tracking request {name}: {e}")
    
    def flush(self):
        """Flush telemetry data"""
        if self.enabled and self.telemetry_client:
            try:
                # In production, this would flush the telemetry client
                logger.info("Flushing Application Insights telemetry")
            except Exception as e:
                logger.error(f"Error flushing telemetry: {e}")
    
    def track_cost_alert(self, alert_data: Dict[str, Any]):
        """Track cost alert event with spiritual context"""
        if not self.enabled:
            return
            
        try:
            alert_event = {
                'event_name': 'cost_alert',
                'alert_level': alert_data.get('alert_level', 'unknown'),
                'metric_type': alert_data.get('metric_type', 'unknown'),
                'current_value': alert_data.get('current_value', 0),
                'threshold_value': alert_data.get('threshold_value', 0),
                'spiritual_message': alert_data.get('spiritual_message', ''),
                'actions_taken': alert_data.get('actions_taken', []),
                'timestamp': datetime.now().isoformat(),
                'properties': {
                    'alert_id': alert_data.get('alert_id', ''),
                    'context': alert_data.get('context', {}),
                    'dharmic_guidance': True  # Flag for spiritual guidance
                }
            }
            
            logger.warning(f"APP_INSIGHTS_COST_ALERT: {alert_event}")
            
        except Exception as e:
            logger.error(f"Error tracking cost alert: {e}")
    
    def track_budget_metrics(self, cost_data: Dict[str, Any]):
        """Track budget and cost metrics"""
        if not self.enabled:
            return
            
        try:
            # Track multiple cost metrics
            metrics = [
                ('cost_total', cost_data.get('total', 0)),
                ('cost_hourly_rate', cost_data.get('hourly', 0)),
                ('cost_daily_projected', cost_data.get('daily', 0)),
                ('cost_monthly_projected', cost_data.get('monthly', 0))
            ]
            
            for metric_name, value in metrics:
                if value > 0:  # Only track non-zero values
                    self.track_metric(metric_name, value, {
                        'measurement_type': 'cost_monitoring',
                        'spiritual_context': 'dharmic_resource_management'
                    })
            
            # Track user and model cost distribution
            by_user = cost_data.get('by_user', {})
            by_model = cost_data.get('by_model', {})
            
            if by_user:
                max_user_cost = max(by_user.values())
                self.track_metric('cost_max_user', max_user_cost)
            
            if by_model:
                for model, cost in by_model.items():
                    self.track_metric(f'cost_model_{model.replace("-", "_")}', cost)
                    
        except Exception as e:
            logger.error(f"Error tracking budget metrics: {e}")


# Global Application Insights client instance
_app_insights_client = None

def get_app_insights_client() -> AppInsightsClient:
    """Get global Application Insights client instance"""
    global _app_insights_client
    if _app_insights_client is None:
        _app_insights_client = AppInsightsClient()
    return _app_insights_client


def track_spiritual_event(event_name: str):
    """Decorator to track spiritual guidance events"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client = get_app_insights_client()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extract spiritual-specific properties
                properties = {
                    'function_name': func.__name__,
                    'success': True,
                    'user_id': kwargs.get('user_id', 'anonymous'),
                    'language': kwargs.get('language', 'en'),
                }
                
                measurements = {
                    'duration_seconds': duration,
                    'response_length': len(str(result)) if result else 0,
                }
                
                # Add spiritual-specific measurements if available
                if hasattr(result, 'quality_score'):
                    measurements['quality_score'] = result.quality_score
                if hasattr(result, 'spiritual_relevance'):
                    measurements['spiritual_relevance'] = result.spiritual_relevance
                if hasattr(result, 'citation_count'):
                    measurements['citation_count'] = result.citation_count
                
                client.track_event(event_name, properties, measurements)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                properties = {
                    'function_name': func.__name__,
                    'success': False,
                    'error_type': type(e).__name__,
                    'user_id': kwargs.get('user_id', 'anonymous'),
                }
                
                measurements = {
                    'duration_seconds': duration,
                }
                
                client.track_event(f"{event_name}_failed", properties, measurements)
                client.track_exception(e, properties)
                raise
                
        return wrapper
    return decorator


def track_performance(operation_name: str):
    """Decorator to track operation performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client = get_app_insights_client()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track as dependency for performance monitoring
                client.track_dependency(
                    name=operation_name,
                    dependency_type="Internal",
                    data=func.__name__,
                    duration=duration,
                    success=True,
                    properties={
                        'function_name': func.__name__,
                        'module': func.__module__,
                    }
                )
                
                # Track performance metric
                client.track_metric(
                    name=f"{operation_name}_duration",
                    value=duration,
                    properties={'operation': operation_name}
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                client.track_dependency(
                    name=operation_name,
                    dependency_type="Internal",
                    data=func.__name__,
                    duration=duration,
                    success=False,
                    properties={
                        'function_name': func.__name__,
                        'error_type': type(e).__name__,
                    }
                )
                
                raise
                
        return wrapper
    return decorator
