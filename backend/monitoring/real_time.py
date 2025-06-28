"""
Real-time monitoring system for Vimarsh.

This module provides real-time metrics streaming, anomaly detection,
and dashboard data aggregation.
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import deque
import statistics


@dataclass
class MetricPoint:
    """Represents a single metric data point."""
    
    timestamp: datetime
    metric_name: str
    value: float
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric point to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'value': self.value,
            'tags': self.tags
        }


class MetricsBuffer:
    """Thread-safe buffer for real-time metrics."""
    
    def __init__(self, max_size: int = 10000):
        """Initialize metrics buffer."""
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.lock = asyncio.Lock()
    
    async def add_metric(self, metric: MetricPoint) -> None:
        """Add metric to buffer."""
        async with self.lock:
            self.buffer.append(metric)
    
    async def get_metrics(self, since: Optional[datetime] = None) -> List[MetricPoint]:
        """Get metrics from buffer."""
        async with self.lock:
            if since is None:
                return list(self.buffer)
            
            return [
                metric for metric in self.buffer
                if metric.timestamp >= since
            ]
    
    async def clear_old_metrics(self, before: datetime) -> int:
        """Clear metrics older than specified time."""
        async with self.lock:
            original_size = len(self.buffer)
            # Convert to list, filter, and create new deque
            filtered_metrics = [
                metric for metric in self.buffer
                if metric.timestamp >= before
            ]
            self.buffer.clear()
            self.buffer.extend(filtered_metrics)
            return original_size - len(self.buffer)


class RealTimeMonitor:
    """Real-time monitoring system."""
    
    def __init__(self):
        """Initialize real-time monitor."""
        self.logger = logging.getLogger(__name__)
        self.buffer = MetricsBuffer()
        self.subscribers = []
        self.is_running = False
        self.anomaly_detectors = {}
        
        # Metrics aggregation windows
        self.aggregation_windows = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '1h': timedelta(hours=1)
        }
    
    async def start_monitoring(self) -> None:
        """Start real-time monitoring."""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("Real-time monitoring started")
        
        # Start background tasks
        asyncio.create_task(self._metrics_cleanup_task())
        asyncio.create_task(self._anomaly_detection_task())
    
    async def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self.is_running = False
        self.logger.info("Real-time monitoring stopped")
    
    async def record_metric(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a metric point."""
        if tags is None:
            tags = {}
        
        metric = MetricPoint(
            timestamp=datetime.now(),
            metric_name=name,
            value=value,
            tags=tags
        )
        
        await self.buffer.add_metric(metric)
        
        # Notify subscribers
        await self._notify_subscribers(metric)
    
    async def subscribe(self, callback: Callable[[MetricPoint], None]) -> None:
        """Subscribe to real-time metrics."""
        self.subscribers.append(callback)
    
    async def get_metrics_stream(self, since: datetime = None) -> List[Dict[str, Any]]:
        """Get metrics as stream data."""
        if since is None:
            since = datetime.now() - timedelta(minutes=5)
        
        metrics = await self.buffer.get_metrics(since)
        return [metric.to_dict() for metric in metrics]
    
    async def aggregate_metrics(self, window: str = '5m') -> Dict[str, Any]:
        """Aggregate metrics for dashboard."""
        if window not in self.aggregation_windows:
            window = '5m'
        
        since = datetime.now() - self.aggregation_windows[window]
        metrics = await self.buffer.get_metrics(since)
        
        # Group metrics by name
        grouped_metrics = {}
        for metric in metrics:
            if metric.metric_name not in grouped_metrics:
                grouped_metrics[metric.metric_name] = []
            grouped_metrics[metric.metric_name].append(metric.value)
        
        # Calculate aggregations
        aggregated = {}
        for metric_name, values in grouped_metrics.items():
            if values:
                aggregated[metric_name] = {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': values[-1] if values else 0
                }
                
                # Add median and percentiles for larger datasets
                if len(values) >= 5:
                    aggregated[metric_name].update({
                        'median': statistics.median(values),
                        'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                        'p99': statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
                    })
        
        return {
            'window': window,
            'timestamp': datetime.now().isoformat(),
            'metrics': aggregated
        }
    
    async def detect_anomalies(self, metric_name: str) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values."""
        since = datetime.now() - timedelta(minutes=15)
        metrics = await self.buffer.get_metrics(since)
        
        # Filter metrics by name
        metric_values = [
            metric for metric in metrics
            if metric.metric_name == metric_name
        ]
        
        if len(metric_values) < 10:
            return []  # Not enough data for anomaly detection
        
        values = [metric.value for metric in metric_values]
        
        # Simple statistical anomaly detection
        mean_val = statistics.mean(values)
        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        threshold = 2.0  # 2 standard deviations
        
        for metric in metric_values:
            if stdev_val > 0:
                z_score = abs(metric.value - mean_val) / stdev_val
                if z_score > threshold:
                    anomalies.append({
                        'timestamp': metric.timestamp.isoformat(),
                        'value': metric.value,
                        'mean': mean_val,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3.0 else 'medium'
                    })
        
        return anomalies
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        # Get aggregated metrics for different windows
        current_metrics = await self.aggregate_metrics('1m')
        recent_metrics = await self.aggregate_metrics('5m')
        hourly_metrics = await self.aggregate_metrics('1h')
        
        # Get recent metric stream
        recent_stream = await self.get_metrics_stream(
            datetime.now() - timedelta(minutes=5)
        )
        
        # Detect anomalies for key metrics
        key_metrics = ['response_time', 'error_rate', 'spiritual_quality_score']
        anomalies = {}
        for metric_name in key_metrics:
            anomalies[metric_name] = await self.detect_anomalies(metric_name)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'current': current_metrics,
                'recent': recent_metrics,
                'hourly': hourly_metrics
            },
            'stream': recent_stream[-100:],  # Last 100 points
            'anomalies': anomalies,
            'status': 'healthy' if not any(anomalies.values()) else 'warning'
        }
    
    async def emit_metric(self, metric_name: str, value: float, 
                            tags: Optional[Dict[str, str]] = None) -> None:
        """Emit a metric point to the real-time system."""
        if tags is None:
            tags = {}
        
        metric_point = MetricPoint(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            tags=tags
        )
        
        await self.buffer.add_metric(metric_point)
        
        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                await subscriber(metric_point)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
    
    async def detect_anomaly(self, metric_name: str, value: float) -> Optional[Dict[str, Any]]:
        """Detect if a single metric value is anomalous."""
        anomalies = await self.detect_anomalies(metric_name)
        
        # Check if current value would be anomalous
        since = datetime.now() - timedelta(minutes=15)
        metrics = await self.buffer.get_metrics(since)
        
        metric_values = [
            metric.value for metric in metrics
            if metric.metric_name == metric_name
        ]
        
        if len(metric_values) < 5:
            return None
        
        # Simple threshold-based detection
        mean_val = statistics.mean(metric_values)
        std_val = statistics.stdev(metric_values) if len(metric_values) > 1 else 0
        
        if abs(value - mean_val) > 2 * std_val:
            return {
                'metric_name': metric_name,
                'anomalous_value': value,
                'expected_range': [mean_val - 2*std_val, mean_val + 2*std_val],
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    async def aggregate_for_dashboard(self, window: str = '5m') -> Dict[str, Any]:
        """Aggregate metrics for dashboard display."""
        if window not in self.aggregation_windows:
            window = '5m'
        
        since = datetime.now() - self.aggregation_windows[window]
        aggregated = await self.aggregate_metrics(window, since)
        
        # Add additional dashboard-specific data
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'window': window,
            'metrics': aggregated.get('metrics', {}),
            'health_status': self._calculate_health_status(aggregated.get('metrics', {})),
            'alerts_count': len([
                metric for metric in aggregated.get('metrics', {}).values()
                if isinstance(metric, dict) and metric.get('max', 0) > 1000  # Example threshold
            ])
        }
        
        return dashboard_data
    
    def _calculate_health_status(self, metrics: Dict[str, Any]) -> str:
        """Calculate overall system health status."""
        if not metrics:
            return 'unknown'
        
        # Simple health calculation based on response times and error rates
        response_time_metrics = metrics.get('response_time', {})
        error_rate_metrics = metrics.get('error_rate', {})
        
        if response_time_metrics.get('avg', 0) > 5000:  # 5 seconds
            return 'critical'
        elif error_rate_metrics.get('avg', 0) > 0.1:  # 10% error rate
            return 'warning'
        else:
            return 'healthy'

    async def _notify_subscribers(self, metric: MetricPoint) -> None:
        """Notify all subscribers of new metric."""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(metric)
                else:
                    callback(metric)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
    
    async def _metrics_cleanup_task(self) -> None:
        """Background task to clean up old metrics."""
        while self.is_running:
            try:
                # Clean up metrics older than 1 hour
                cutoff = datetime.now() - timedelta(hours=1)
                cleared = await self.buffer.clear_old_metrics(cutoff)
                
                if cleared > 0:
                    self.logger.debug(f"Cleaned up {cleared} old metrics")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in metrics cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _anomaly_detection_task(self) -> None:
        """Background task for anomaly detection."""
        while self.is_running:
            try:
                # Run anomaly detection for key metrics
                key_metrics = ['response_time', 'error_rate', 'spiritual_quality_score']
                
                for metric_name in key_metrics:
                    anomalies = await self.detect_anomalies(metric_name)
                    
                    if anomalies:
                        self.logger.warning(
                            f"Anomalies detected for {metric_name}: {len(anomalies)} points"
                        )
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                self.logger.error(f"Error in anomaly detection: {e}")
                await asyncio.sleep(60)


# Global real-time monitor instance
real_time_monitor = RealTimeMonitor()
