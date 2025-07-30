"""
Performance Monitoring Service for Vimarsh
Automated daily performance reports and system health monitoring
"""

import logging
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import statistics

try:
    from models.vimarsh_models import (
        DailyPerformanceReport, PerformanceMetric, model_to_dict
    )
    from services.database_service import DatabaseService
    from services.analytics_service import AnalyticsService
    from services.cache_service import CacheService
except ImportError as e:
    logging.warning(f"Import warning in performance_monitoring_service: {e}")
    # Mock classes for testing
    DailyPerformanceReport = None
    PerformanceMetric = None

logger = logging.getLogger(__name__)

class PerformanceMonitoringService:
    """Service for monitoring system performance and generating automated reports"""
    
    def __init__(self):
        """Initialize performance monitoring service"""
        self.db_service = DatabaseService()
        self.analytics_service = AnalyticsService()
        self.cache_service = CacheService()
        
        # Local storage for development
        self.local_storage_path = "data/performance"
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Performance thresholds
        self.thresholds = {
            'response_time_warning': 3000,  # 3 seconds
            'response_time_critical': 5000,  # 5 seconds
            'error_rate_warning': 5,  # 5%
            'error_rate_critical': 10,  # 10%
            'success_rate_warning': 95,  # 95%
            'success_rate_critical': 90   # 90%
        }
        
        logger.info("📈 Performance Monitoring Service initialized")
    
    async def generate_daily_report(self, date: str = None) -> DailyPerformanceReport:
        """Generate comprehensive daily performance report"""
        try:
            if date is None:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            logger.info(f"Generating daily performance report for {date}")
            
            # Get analytics data for the day
            insights = await self.analytics_service.get_performance_insights("1d")
            personality_stats = await self.analytics_service.get_personality_stats("1d")
            
            # Calculate detailed metrics
            performance_metrics = await self._calculate_detailed_metrics(date)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(insights, performance_metrics)
            
            # Create performance report
            report = DailyPerformanceReport(
                id=f"performance_report_{date}",
                report_date=date,
                total_requests=insights.get('total_queries', 0),
                successful_requests=self._calculate_successful_requests(insights),
                failed_requests=self._calculate_failed_requests(insights),
                avg_response_time_ms=insights.get('avg_response_time', 0),
                p95_response_time_ms=performance_metrics.get('p95_response_time', 0),
                p99_response_time_ms=performance_metrics.get('p99_response_time', 0),
                personality_performance=self._format_personality_performance(personality_stats),
                error_breakdown=insights.get('error_breakdown', {}),
                peak_usage_hour=performance_metrics.get('peak_usage_hour', 0),
                recommendations=recommendations,
                health_score=self._calculate_health_score(insights, performance_metrics)
            )
            
            # Save report
            await self._save_report(report)
            
            logger.info(f"Generated daily performance report: Health Score {report.health_score}%")
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily performance report: {e}")
            return DailyPerformanceReport(
                id=f"performance_report_{date or 'unknown'}",
                report_date=date or datetime.utcnow().strftime('%Y-%m-%d')
            )
    
    async def track_performance_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        personality_id: str = None,
        session_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Track a performance metric"""
        try:
            metric = PerformanceMetric(
                id="",  # Will be auto-generated
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
                timestamp=datetime.utcnow().isoformat(),
                personality_id=personality_id,
                session_id=session_id,
                metadata=metadata or {}
            )
            
            # Save to database
            await self._save_metric_to_db(metric)
            
            # Update real-time monitoring cache
            await self._update_realtime_metrics(metric)
            
            logger.debug(f"Tracked performance metric: {metric_name} = {metric_value} {metric_unit}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking performance metric: {e}")
            return False
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        try:
            # Check cache first
            cache_key = "realtime_metrics"
            cached_metrics = self.cache_service.get(cache_key)
            
            if cached_metrics:
                return cached_metrics
            
            # Calculate current metrics
            current_time = datetime.utcnow()
            one_hour_ago = current_time - timedelta(hours=1)
            
            # Get recent metrics
            recent_metrics = await self._get_metrics_by_period(
                one_hour_ago.isoformat(), 
                current_time.isoformat()
            )
            
            # Calculate real-time stats
            realtime_stats = self._calculate_realtime_stats(recent_metrics)
            
            # Cache for 5 minutes
            self.cache_service.put(cache_key, realtime_stats, ttl=300)
            
            return realtime_stats
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    async def get_performance_trends(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get performance trends over time"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get daily reports for the period
            reports = await self._get_reports_by_period(start_date, end_date)
            
            if not reports:
                return {
                    'trends': {},
                    'average_health_score': 0,
                    'trend_direction': 'stable'
                }
            
            # Calculate trends
            trends = self._calculate_trends(reports)
            
            logger.info(f"Calculated performance trends for {days} days")
            return trends
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {}
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        try:
            health_status = {
                'overall_status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {},
                'alerts': [],
                'health_score': 100.0
            }
            
            # Check response times
            response_time_check = await self._check_response_times()
            health_status['checks']['response_times'] = response_time_check
            
            # Check error rates
            error_rate_check = await self._check_error_rates()
            health_status['checks']['error_rates'] = error_rate_check
            
            # Check personality availability
            personality_check = await self._check_personality_availability()
            health_status['checks']['personalities'] = personality_check
            
            # Check database connectivity
            db_check = await self._check_database_health()
            health_status['checks']['database'] = db_check
            
            # Calculate overall health
            health_status = self._calculate_overall_health(health_status)
            
            logger.info(f"System health check completed: {health_status['overall_status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {
                'overall_status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    async def schedule_automated_reports(self):
        """Schedule automated daily performance reports"""
        try:
            logger.info("Starting automated performance report scheduler")
            
            while True:
                # Wait until next report time (e.g., 6 AM)
                now = datetime.utcnow()
                next_report_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
                
                if next_report_time <= now:
                    next_report_time += timedelta(days=1)
                
                sleep_seconds = (next_report_time - now).total_seconds()
                logger.info(f"Next automated report in {sleep_seconds/3600:.1f} hours")
                
                await asyncio.sleep(sleep_seconds)
                
                # Generate yesterday's report
                yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
                report = await self.generate_daily_report(yesterday)
                
                logger.info(f"Automated daily report generated for {yesterday}")
                
                # Send alerts if health score is low
                if report.health_score < 80:
                    await self._send_health_alert(report)
                
        except Exception as e:
            logger.error(f"Error in automated report scheduler: {e}")
    
    # Private helper methods
    
    async def _calculate_detailed_metrics(self, date: str) -> Dict[str, Any]:
        """Calculate detailed performance metrics for a specific date"""
        try:
            # Get all metrics for the date
            start_time = f"{date}T00:00:00"
            end_time = f"{date}T23:59:59"
            
            metrics = await self._get_metrics_by_period(start_time, end_time)
            
            if not metrics:
                return {}
            
            # Calculate percentiles for response times
            response_times = [
                m.metric_value for m in metrics 
                if m.metric_name == 'response_time' and m.metric_unit == 'ms'
            ]
            
            result = {}
            
            if response_times:
                result['p95_response_time'] = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                result['p99_response_time'] = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
            
            # Calculate peak usage hour
            hourly_counts = {}
            for metric in metrics:
                if metric.metric_name == 'query_count':
                    hour = datetime.fromisoformat(metric.timestamp).hour
                    hourly_counts[hour] = hourly_counts.get(hour, 0) + metric.metric_value
            
            if hourly_counts:
                result['peak_usage_hour'] = max(hourly_counts, key=hourly_counts.get)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating detailed metrics: {e}")
            return {}
    
    def _generate_recommendations(
        self,
        insights: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Response time recommendations
        avg_response_time = insights.get('avg_response_time', 0)
        if avg_response_time > self.thresholds['response_time_critical']:
            recommendations.append("CRITICAL: Average response time exceeds 5 seconds - immediate optimization required")
        elif avg_response_time > self.thresholds['response_time_warning']:
            recommendations.append("WARNING: Average response time exceeds 3 seconds - consider optimization")
        
        # Error rate recommendations
        error_rate = insights.get('error_rate', 0)
        if error_rate > self.thresholds['error_rate_critical']:
            recommendations.append("CRITICAL: Error rate exceeds 10% - investigate and fix immediately")
        elif error_rate > self.thresholds['error_rate_warning']:
            recommendations.append("WARNING: Error rate exceeds 5% - monitor closely")
        
        # Personality-specific recommendations
        personality_performance = insights.get('personality_performance', {})
        for personality, perf in personality_performance.items():
            if perf.get('avg_response_time', 0) > self.thresholds['response_time_critical']:
                recommendations.append(f"CRITICAL: {personality} personality has very slow response times")
            
            if perf.get('error_count', 0) > 10:
                recommendations.append(f"WARNING: {personality} personality has high error count")
        
        # P95/P99 recommendations
        p95_time = metrics.get('p95_response_time', 0)
        if p95_time > 8000:  # 8 seconds
            recommendations.append("WARNING: 95th percentile response time is very high - optimize slow queries")
        
        return recommendations
    
    def _calculate_health_score(
        self,
        insights: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall system health score"""
        score = 100.0
        
        # Response time impact
        avg_response_time = insights.get('avg_response_time', 0)
        if avg_response_time > self.thresholds['response_time_critical']:
            score -= 30
        elif avg_response_time > self.thresholds['response_time_warning']:
            score -= 15
        
        # Error rate impact
        error_rate = insights.get('error_rate', 0)
        if error_rate > self.thresholds['error_rate_critical']:
            score -= 40
        elif error_rate > self.thresholds['error_rate_warning']:
            score -= 20
        
        # P95 response time impact
        p95_time = metrics.get('p95_response_time', 0)
        if p95_time > 8000:
            score -= 10
        
        return max(0.0, min(100.0, score))
    
    def _format_personality_performance(
        self,
        personality_stats: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Format personality performance data"""
        formatted = {}
        
        for personality_id, stats in personality_stats.items():
            formatted[personality_id] = {
                'total_queries': float(stats.total_queries),
                'avg_response_time_ms': float(stats.avg_response_time_ms),
                'success_rate': float(stats.success_rate),
                'total_cost_usd': float(stats.total_cost_usd)
            }
        
        return formatted
    
    def _calculate_successful_requests(self, insights: Dict[str, Any]) -> int:
        """Calculate number of successful requests"""
        total_queries = insights.get('total_queries', 0)
        error_rate = insights.get('error_rate', 0)
        
        if total_queries > 0:
            return int(total_queries * (1 - error_rate / 100))
        
        return 0
    
    def _calculate_failed_requests(self, insights: Dict[str, Any]) -> int:
        """Calculate number of failed requests"""
        total_queries = insights.get('total_queries', 0)
        successful_requests = self._calculate_successful_requests(insights)
        
        return max(0, total_queries - successful_requests)
    
    async def _save_report(self, report: DailyPerformanceReport) -> bool:
        """Save performance report to database"""
        try:
            if hasattr(self.db_service, 'save_performance_report'):
                return await self.db_service.save_performance_report(model_to_dict(report))
        except Exception as e:
            logger.warning(f"Database unavailable, using local storage: {e}")
        
        return self._save_report_to_local(report)
    
    def _save_report_to_local(self, report: DailyPerformanceReport) -> bool:
        """Save report to local JSON storage"""
        try:
            report_file = os.path.join(self.local_storage_path, f"{report.report_date}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(model_to_dict(report), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving local performance report: {e}")
            return False

# Global service instance
performance_monitoring_service = PerformanceMonitoringService()
