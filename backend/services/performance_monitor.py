"""
Performance Monitoring Service for Vimarsh Multi-Personality Platform

This service provides comprehensive performance monitoring, metrics collection,
and optimization recommendations for personality-specific operations.
"""

import logging
import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import json

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    personality_id: str
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    timestamp: datetime
    user_id: Optional[str] = None
    cache_hit: bool = False
    error_message: Optional[str] = None

@dataclass
class PersonalityPerformance:
    personality_id: str
    total_requests: int = 0
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    active_users: int = 0
    requests_per_minute: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    last_updated: datetime = None

@dataclass
class SystemPerformance:
    total_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_errors: int = 0
    global_error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    active_personalities: int = 0
    concurrent_users: int = 0
    cache_hit_rate: float = 0.0
    uptime_seconds: int = 0
    last_updated: datetime = None

@dataclass
class PerformanceAlert:
    alert_id: str
    personality_id: Optional[str]
    alert_type: str  # 'high_response_time', 'high_error_rate', 'memory_usage', etc.
    severity: str    # 'low', 'medium', 'high', 'critical'
    message: str
    threshold_value: float
    current_value: float
    created_at: datetime
    resolved_at: Optional[datetime] = None

class PerformanceMonitor:
    """Comprehensive performance monitoring for multi-personality system"""
    
    def __init__(self):
        # Metrics storage
        self.request_history: deque = deque(maxlen=10000)  # Last 10k requests
        self.personality_metrics: Dict[str, PersonalityPerformance] = defaultdict(
            lambda: PersonalityPerformance(personality_id="")
        )
        self.system_metrics = SystemPerformance()
        
        # Real-time metrics (sliding window)
        self.sliding_window_minutes = 5
        self.request_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=300))  # 5 min window
        
        # Performance alerts
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_thresholds = {
            'response_time_ms': 5000,      # 5 seconds
            'error_rate_percent': 5.0,     # 5%
            'memory_usage_mb': 1024,       # 1GB
            'cpu_usage_percent': 80.0,     # 80%
            'cache_hit_rate_percent': 50.0 # Below 50%
        }
        
        # Monitoring configuration
        self.monitoring_enabled = True
        self.collection_interval_seconds = 30
        self.cleanup_interval_hours = 24
        
        # System startup time
        self.startup_time = datetime.now()
        
        # Background tasks
        self.monitoring_task = None
        self.cleanup_task = None
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Start monitoring
        self._start_monitoring()
    
    def record_request(
        self,
        personality_id: str,
        endpoint: str,
        method: str,
        response_time_ms: float,
        status_code: int,
        user_id: Optional[str] = None,
        cache_hit: bool = False,
        error_message: Optional[str] = None
    ) -> None:
        """Record a request for performance tracking"""
        
        try:
            with self.lock:
                # Create request metrics
                request_metrics = RequestMetrics(
                    personality_id=personality_id,
                    endpoint=endpoint,
                    method=method,
                    response_time_ms=response_time_ms,
                    status_code=status_code,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    cache_hit=cache_hit,
                    error_message=error_message
                )
                
                # Add to history
                self.request_history.append(request_metrics)
                
                # Add to sliding window
                self.request_windows[personality_id].append(request_metrics)
                
                # Update personality metrics
                self._update_personality_metrics(personality_id, request_metrics)
                
                # Check for alerts
                self._check_performance_alerts(personality_id)
                
        except Exception as e:
            logger.error(f"Failed to record request metrics: {str(e)}")
    
    def get_personality_metrics(self, personality_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific personality"""
        
        with self.lock:
            metrics = self.personality_metrics.get(personality_id)
            if not metrics:
                return {}
            
            # Add real-time metrics
            real_time_metrics = self._calculate_real_time_metrics(personality_id)
            
            result = asdict(metrics)
            result.update(real_time_metrics)
            
            return result
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        
        with self.lock:
            # Update system metrics
            self._update_system_metrics()
            
            return {
                "system": asdict(self.system_metrics),
                "personalities": {
                    pid: asdict(metrics) for pid, metrics in self.personality_metrics.items()
                },
                "alerts": {
                    aid: asdict(alert) for aid, alert in self.active_alerts.items()
                }
            }
    
    def get_performance_report(
        self,
        personality_id: Optional[str] = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        try:
            with self.lock:
                cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
                
                # Filter requests by time range
                filtered_requests = [
                    req for req in self.request_history
                    if req.timestamp >= cutoff_time and
                    (not personality_id or req.personality_id == personality_id)
                ]
                
                if not filtered_requests:
                    return {"message": "No data available for the specified time range"}
                
                # Calculate report metrics
                report = self._generate_performance_report(filtered_requests, personality_id)
                
                return report
                
        except Exception as e:
            logger.error(f"Failed to generate performance report: {str(e)}")
            return {"error": str(e)}
    
    def get_active_alerts(self, personality_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active performance alerts"""
        
        with self.lock:
            alerts = []
            for alert in self.active_alerts.values():
                if not personality_id or alert.personality_id == personality_id:
                    alerts.append(asdict(alert))
            
            return sorted(alerts, key=lambda x: x['created_at'], reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a performance alert"""
        
        try:
            with self.lock:
                if alert_id in self.active_alerts:
                    self.active_alerts[alert_id].resolved_at = datetime.now()
                    del self.active_alerts[alert_id]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {str(e)}")
            return False
    
    def get_optimization_recommendations(
        self,
        personality_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get performance optimization recommendations"""
        
        recommendations = []
        
        try:
            with self.lock:
                if personality_id:
                    recommendations.extend(self._get_personality_recommendations(personality_id))
                else:
                    # System-wide recommendations
                    recommendations.extend(self._get_system_recommendations())
                    
                    # Per-personality recommendations
                    for pid in self.personality_metrics.keys():
                        recommendations.extend(self._get_personality_recommendations(pid))
                
                return recommendations
                
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return []
    
    # Private methods
    
    def _start_monitoring(self) -> None:
        """Start background monitoring tasks"""
        
        if self.monitoring_enabled:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        
        while self.monitoring_enabled:
            try:
                await asyncio.sleep(self.collection_interval_seconds)
                
                # Update system metrics
                self._update_system_metrics()
                
                # Check for system-wide alerts
                self._check_system_alerts()
                
                # Log performance summary
                self._log_performance_summary()
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        
        while self.monitoring_enabled:
            try:
                await asyncio.sleep(self.cleanup_interval_hours * 3600)
                
                # Clean up old metrics
                self._cleanup_old_metrics()
                
                # Resolve old alerts
                self._cleanup_old_alerts()
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {str(e)}")
    
    def _update_personality_metrics(
        self,
        personality_id: str,
        request_metrics: RequestMetrics
    ) -> None:
        """Update metrics for a specific personality"""
        
        metrics = self.personality_metrics[personality_id]
        metrics.personality_id = personality_id
        
        # Update request count
        metrics.total_requests += 1
        
        # Update response time metrics
        response_time = request_metrics.response_time_ms
        if metrics.avg_response_time_ms == 0:
            metrics.avg_response_time_ms = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            metrics.avg_response_time_ms = (
                alpha * response_time + (1 - alpha) * metrics.avg_response_time_ms
            )
        
        metrics.min_response_time_ms = min(metrics.min_response_time_ms, response_time)
        metrics.max_response_time_ms = max(metrics.max_response_time_ms, response_time)
        
        # Update error metrics
        if request_metrics.status_code >= 400:
            metrics.error_count += 1
        
        metrics.error_rate = (metrics.error_count / metrics.total_requests) * 100
        
        # Update cache hit rate
        recent_requests = list(self.request_windows[personality_id])
        if recent_requests:
            cache_hits = sum(1 for req in recent_requests if req.cache_hit)
            metrics.cache_hit_rate = (cache_hits / len(recent_requests)) * 100
        
        metrics.last_updated = datetime.now()
    
    def _update_system_metrics(self) -> None:
        """Update system-wide performance metrics"""
        
        try:
            # System resource usage
            self.system_metrics.memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
            self.system_metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
            self.system_metrics.disk_usage_percent = psutil.disk_usage('/').percent
            
            # Aggregate personality metrics
            total_requests = sum(m.total_requests for m in self.personality_metrics.values())
            total_errors = sum(m.error_count for m in self.personality_metrics.values())
            
            self.system_metrics.total_requests = total_requests
            self.system_metrics.total_errors = total_errors
            self.system_metrics.global_error_rate = (
                (total_errors / total_requests * 100) if total_requests > 0 else 0
            )
            
            # Calculate average response time
            if self.personality_metrics:
                avg_response_times = [
                    m.avg_response_time_ms for m in self.personality_metrics.values()
                    if m.avg_response_time_ms > 0
                ]
                if avg_response_times:
                    self.system_metrics.avg_response_time_ms = sum(avg_response_times) / len(avg_response_times)
            
            # Active personalities
            self.system_metrics.active_personalities = len(self.personality_metrics)
            
            # Uptime
            self.system_metrics.uptime_seconds = int(
                (datetime.now() - self.startup_time).total_seconds()
            )
            
            self.system_metrics.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to update system metrics: {str(e)}")
    
    def _calculate_real_time_metrics(self, personality_id: str) -> Dict[str, Any]:
        """Calculate real-time metrics for personality"""
        
        recent_requests = list(self.request_windows[personality_id])
        if not recent_requests:
            return {}
        
        # Calculate requests per minute
        now = datetime.now()
        recent_minute = now - timedelta(minutes=1)
        recent_requests_count = sum(
            1 for req in recent_requests if req.timestamp >= recent_minute
        )
        
        # Calculate active users (unique users in last 5 minutes)
        recent_users = set(
            req.user_id for req in recent_requests
            if req.user_id and req.timestamp >= now - timedelta(minutes=5)
        )
        
        return {
            "requests_per_minute": recent_requests_count,
            "active_users": len(recent_users),
            "recent_requests_count": len(recent_requests)
        }
    
    def _check_performance_alerts(self, personality_id: str) -> None:
        """Check for performance alerts for a personality"""
        
        metrics = self.personality_metrics[personality_id]
        
        # Check response time
        if metrics.avg_response_time_ms > self.alert_thresholds['response_time_ms']:
            self._create_alert(
                personality_id,
                'high_response_time',
                'high',
                f"High response time for {personality_id}",
                self.alert_thresholds['response_time_ms'],
                metrics.avg_response_time_ms
            )
        
        # Check error rate
        if metrics.error_rate > self.alert_thresholds['error_rate_percent']:
            self._create_alert(
                personality_id,
                'high_error_rate',
                'high',
                f"High error rate for {personality_id}",
                self.alert_thresholds['error_rate_percent'],
                metrics.error_rate
            )
        
        # Check cache hit rate
        if metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate_percent']:
            self._create_alert(
                personality_id,
                'low_cache_hit_rate',
                'medium',
                f"Low cache hit rate for {personality_id}",
                self.alert_thresholds['cache_hit_rate_percent'],
                metrics.cache_hit_rate
            )
    
    def _check_system_alerts(self) -> None:
        """Check for system-wide performance alerts"""
        
        # Check memory usage
        if self.system_metrics.memory_usage_mb > self.alert_thresholds['memory_usage_mb']:
            self._create_alert(
                None,
                'high_memory_usage',
                'critical',
                "High system memory usage",
                self.alert_thresholds['memory_usage_mb'],
                self.system_metrics.memory_usage_mb
            )
        
        # Check CPU usage
        if self.system_metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage_percent']:
            self._create_alert(
                None,
                'high_cpu_usage',
                'high',
                "High system CPU usage",
                self.alert_thresholds['cpu_usage_percent'],
                self.system_metrics.cpu_usage_percent
            )
    
    def _create_alert(
        self,
        personality_id: Optional[str],
        alert_type: str,
        severity: str,
        message: str,
        threshold_value: float,
        current_value: float
    ) -> None:
        """Create a performance alert"""
        
        alert_key = f"{personality_id or 'system'}_{alert_type}"
        
        # Don't create duplicate alerts
        if alert_key in self.active_alerts:
            return
        
        alert_id = f"alert_{int(time.time())}_{alert_key}"
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            personality_id=personality_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            threshold_value=threshold_value,
            current_value=current_value,
            created_at=datetime.now()
        )
        
        self.active_alerts[alert_key] = alert
        logger.warning(f"Performance alert created: {message}")
    
    def _generate_performance_report(
        self,
        requests: List[RequestMetrics],
        personality_id: Optional[str]
    ) -> Dict[str, Any]:
        """Generate detailed performance report"""
        
        if not requests:
            return {}
        
        # Basic statistics
        total_requests = len(requests)
        response_times = [req.response_time_ms for req in requests]
        error_count = sum(1 for req in requests if req.status_code >= 400)
        cache_hits = sum(1 for req in requests if req.cache_hit)
        
        # Calculate percentiles
        response_times.sort()
        p50 = response_times[int(0.5 * len(response_times))]
        p95 = response_times[int(0.95 * len(response_times))]
        p99 = response_times[int(0.99 * len(response_times))]
        
        # Endpoint analysis
        endpoint_stats = defaultdict(lambda: {'count': 0, 'avg_time': 0, 'errors': 0})
        for req in requests:
            endpoint_stats[req.endpoint]['count'] += 1
            endpoint_stats[req.endpoint]['avg_time'] += req.response_time_ms
            if req.status_code >= 400:
                endpoint_stats[req.endpoint]['errors'] += 1
        
        # Finalize endpoint stats
        for endpoint, stats in endpoint_stats.items():
            stats['avg_time'] /= stats['count']
            stats['error_rate'] = (stats['errors'] / stats['count']) * 100
        
        return {
            "summary": {
                "total_requests": total_requests,
                "error_count": error_count,
                "error_rate": (error_count / total_requests) * 100,
                "cache_hit_rate": (cache_hits / total_requests) * 100,
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times)
            },
            "percentiles": {
                "p50_ms": p50,
                "p95_ms": p95,
                "p99_ms": p99
            },
            "endpoints": dict(endpoint_stats),
            "time_range": {
                "start": min(req.timestamp for req in requests).isoformat(),
                "end": max(req.timestamp for req in requests).isoformat()
            }
        }
    
    def _get_personality_recommendations(self, personality_id: str) -> List[Dict[str, Any]]:
        """Get optimization recommendations for a personality"""
        
        recommendations = []
        metrics = self.personality_metrics.get(personality_id)
        
        if not metrics:
            return recommendations
        
        # High response time recommendation
        if metrics.avg_response_time_ms > 3000:
            recommendations.append({
                "type": "performance",
                "personality_id": personality_id,
                "priority": "high",
                "title": "High Response Time",
                "description": f"Average response time is {metrics.avg_response_time_ms:.1f}ms",
                "recommendations": [
                    "Enable response caching for common queries",
                    "Optimize knowledge base retrieval",
                    "Consider pre-computing frequent responses"
                ]
            })
        
        # Low cache hit rate recommendation
        if metrics.cache_hit_rate < 60:
            recommendations.append({
                "type": "caching",
                "personality_id": personality_id,
                "priority": "medium",
                "title": "Low Cache Hit Rate",
                "description": f"Cache hit rate is {metrics.cache_hit_rate:.1f}%",
                "recommendations": [
                    "Increase cache TTL for stable responses",
                    "Implement cache warming for popular queries",
                    "Review cache invalidation strategy"
                ]
            })
        
        # High error rate recommendation
        if metrics.error_rate > 2:
            recommendations.append({
                "type": "reliability",
                "personality_id": personality_id,
                "priority": "high",
                "title": "High Error Rate",
                "description": f"Error rate is {metrics.error_rate:.1f}%",
                "recommendations": [
                    "Review error logs for common issues",
                    "Implement better error handling",
                    "Add input validation and sanitization"
                ]
            })
        
        return recommendations
    
    def _get_system_recommendations(self) -> List[Dict[str, Any]]:
        """Get system-wide optimization recommendations"""
        
        recommendations = []
        
        # High memory usage
        if self.system_metrics.memory_usage_mb > 512:
            recommendations.append({
                "type": "resource",
                "personality_id": None,
                "priority": "medium",
                "title": "High Memory Usage",
                "description": f"System memory usage is {self.system_metrics.memory_usage_mb:.1f}MB",
                "recommendations": [
                    "Implement memory-efficient caching",
                    "Review cache size limits",
                    "Consider memory optimization techniques"
                ]
            })
        
        # High CPU usage
        if self.system_metrics.cpu_usage_percent > 70:
            recommendations.append({
                "type": "resource",
                "personality_id": None,
                "priority": "high",
                "title": "High CPU Usage",
                "description": f"System CPU usage is {self.system_metrics.cpu_usage_percent:.1f}%",
                "recommendations": [
                    "Optimize expensive operations",
                    "Implement request queuing",
                    "Consider horizontal scaling"
                ]
            })
        
        return recommendations
    
    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics data"""
        
        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_interval_hours)
        
        # Clean up request history
        self.request_history = deque(
            [req for req in self.request_history if req.timestamp >= cutoff_time],
            maxlen=self.request_history.maxlen
        )
        
        # Clean up sliding windows
        for personality_id, window in self.request_windows.items():
            self.request_windows[personality_id] = deque(
                [req for req in window if req.timestamp >= cutoff_time],
                maxlen=window.maxlen
            )
    
    def _cleanup_old_alerts(self) -> None:
        """Clean up resolved alerts older than 24 hours"""
        
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        alerts_to_remove = []
        for alert_key, alert in self.active_alerts.items():
            if alert.resolved_at and alert.resolved_at < cutoff_time:
                alerts_to_remove.append(alert_key)
        
        for alert_key in alerts_to_remove:
            del self.active_alerts[alert_key]
    
    def _log_performance_summary(self) -> None:
        """Log performance summary"""
        
        try:
            summary = {
                "active_personalities": len(self.personality_metrics),
                "total_requests": self.system_metrics.total_requests,
                "avg_response_time_ms": self.system_metrics.avg_response_time_ms,
                "error_rate": self.system_metrics.global_error_rate,
                "memory_usage_mb": self.system_metrics.memory_usage_mb,
                "cpu_usage_percent": self.system_metrics.cpu_usage_percent,
                "active_alerts": len(self.active_alerts)
            }
            
            logger.info(f"Performance Summary: {json.dumps(summary, default=str)}")
            
        except Exception as e:
            logger.error(f"Failed to log performance summary: {str(e)}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()