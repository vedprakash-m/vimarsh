"""
AI Cost Analytics Dashboard with Detailed Breakdown
Task 7.10: Enhanced AI Cost Management & Dynamic Fallbacks

This module provides a comprehensive analytics dashboard for AI cost monitoring,
trend analysis, and cost optimization insights for the Vimarsh spiritual guidance app.

Features:
- Real-time cost monitoring and visualization
- Detailed cost breakdown by user, model, operation type
- Trend analysis and forecasting
- Cost optimization recommendations
- Interactive dashboard with charts and metrics
- Export capabilities for financial reporting
- Integration with existing cost management systems
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import defaultdict, Counter
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of analytics reports"""
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


class CostCategory(Enum):
    """Cost categorization for detailed breakdown"""
    LLM_OPERATIONS = "llm_operations"
    VOICE_PROCESSING = "voice_processing"
    VECTOR_SEARCH = "vector_search"
    INFRASTRUCTURE = "infrastructure"
    STORAGE = "storage"
    MONITORING = "monitoring"


@dataclass
class CostMetrics:
    """Cost metrics for analytics"""
    total_cost: float
    token_cost: float
    operation_count: int
    average_cost_per_operation: float
    cost_by_model: Dict[str, float]
    cost_by_user: Dict[str, float]
    cost_by_category: Dict[str, float]
    peak_usage_hour: int
    efficiency_score: float  # 0-100, higher is better
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    period: str
    growth_rate: float  # percentage
    predicted_next_period: float
    confidence_level: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    seasonal_pattern: bool
    anomalies_detected: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    category: str
    recommendation: str
    potential_savings: float
    implementation_effort: str  # "low", "medium", "high"
    priority: int  # 1-5, 1 being highest priority
    impact_description: str
    implementation_steps: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class CostAnalyticsDashboard:
    """AI Cost Analytics Dashboard with comprehensive reporting"""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize cost analytics dashboard
        
        Args:
            storage_path: Path to store analytics data and reports
        """
        self.storage_path = Path(storage_path) if storage_path else Path("data/cost_analytics")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Analytics data storage
        self.cost_history: List[Dict[str, Any]] = []
        self.cached_reports: Dict[str, Dict[str, Any]] = {}
        
        # Initialize with cost management integration
        self._load_historical_data()
        
        logger.info("Cost Analytics Dashboard initialized")
    
    def _load_historical_data(self):
        """Load historical cost data from storage"""
        try:
            history_file = self.storage_path / "cost_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.cost_history = json.load(f)
                logger.info(f"Loaded {len(self.cost_history)} historical cost records")
        except Exception as e:
            logger.warning(f"Could not load historical data: {e}")
            self.cost_history = []
    
    def _save_historical_data(self):
        """Save cost history to storage"""
        try:
            history_file = self.storage_path / "cost_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.cost_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save historical data: {e}")
    
    async def generate_cost_metrics(self, 
                                  start_date: datetime = None, 
                                  end_date: datetime = None,
                                  user_id: str = None) -> CostMetrics:
        """
        Generate comprehensive cost metrics for specified period
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis  
            user_id: Optional user ID for user-specific metrics
            
        Returns:
            CostMetrics: Comprehensive cost analysis
        """
        try:
            # Default to last 30 days if no dates provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Filter data for the specified period
            filtered_data = [
                record for record in self.cost_history
                if self._parse_timestamp(record.get('timestamp', '')) >= start_date and
                   self._parse_timestamp(record.get('timestamp', '')) <= end_date and
                   (not user_id or record.get('user_id') == user_id)
            ]
            
            if not filtered_data:
                # Return zero metrics if no data
                return CostMetrics(
                    total_cost=0.0,
                    token_cost=0.0,
                    operation_count=0,
                    average_cost_per_operation=0.0,
                    cost_by_model={},
                    cost_by_user={},
                    cost_by_category={},
                    peak_usage_hour=12,  # Default noon
                    efficiency_score=100.0
                )
            
            # Calculate metrics
            total_cost = sum(record.get('cost', 0) for record in filtered_data)
            token_cost = sum(record.get('token_cost', 0) for record in filtered_data)
            operation_count = len(filtered_data)
            average_cost = total_cost / operation_count if operation_count > 0 else 0
            
            # Cost by model
            cost_by_model = defaultdict(float)
            for record in filtered_data:
                model = record.get('model', 'unknown')
                cost_by_model[model] += record.get('cost', 0)
            
            # Cost by user  
            cost_by_user = defaultdict(float)
            for record in filtered_data:
                user = record.get('user_id', 'anonymous')
                cost_by_user[user] += record.get('cost', 0)
            
            # Cost by category
            cost_by_category = defaultdict(float)
            for record in filtered_data:
                category = record.get('category', 'llm_operations')
                cost_by_category[category] += record.get('cost', 0)
            
            # Peak usage hour analysis
            hours = [self._parse_timestamp(record.get('timestamp', '')).hour for record in filtered_data]
            peak_usage_hour = max(set(hours), key=hours.count) if hours else 12
            
            # Efficiency score calculation (higher is better)
            efficiency_score = self._calculate_efficiency_score(filtered_data)
            
            metrics = CostMetrics(
                total_cost=total_cost,
                token_cost=token_cost,
                operation_count=operation_count,
                average_cost_per_operation=average_cost,
                cost_by_model=dict(cost_by_model),
                cost_by_user=dict(cost_by_user),
                cost_by_category=dict(cost_by_category),
                peak_usage_hour=peak_usage_hour,
                efficiency_score=efficiency_score
            )
            
            logger.info(f"Generated cost metrics: ${total_cost:.4f} total, {operation_count} operations")
            return metrics
            
        except Exception as e:
            logger.error(f"Error generating cost metrics: {e}")
            # Return default metrics on error
            return CostMetrics(
                total_cost=0.0, token_cost=0.0, operation_count=0,
                average_cost_per_operation=0.0, cost_by_model={},
                cost_by_user={}, cost_by_category={},
                peak_usage_hour=12, efficiency_score=50.0
            )
    
    async def analyze_trends(self, 
                           period_days: int = 30,
                           user_id: str = None) -> TrendAnalysis:
        """
        Analyze cost trends and predict future usage
        
        Args:
            period_days: Number of days to analyze
            user_id: Optional user ID for user-specific analysis
            
        Returns:
            TrendAnalysis: Trend analysis results
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get daily costs for the period
            daily_costs = self._get_daily_costs(start_date, end_date, user_id)
            
            if len(daily_costs) < 2:
                return TrendAnalysis(
                    period=f"{period_days} days",
                    growth_rate=0.0,
                    predicted_next_period=0.0,
                    confidence_level=0.0,
                    trend_direction="stable",
                    seasonal_pattern=False,
                    anomalies_detected=[]
                )
            
            # Calculate growth rate
            first_week_avg = statistics.mean(daily_costs[:7]) if len(daily_costs) >= 7 else daily_costs[0]
            last_week_avg = statistics.mean(daily_costs[-7:]) if len(daily_costs) >= 7 else daily_costs[-1]
            growth_rate = ((last_week_avg - first_week_avg) / first_week_avg * 100) if first_week_avg > 0 else 0
            
            # Predict next period
            recent_avg = statistics.mean(daily_costs[-7:]) if len(daily_costs) >= 7 else statistics.mean(daily_costs)
            predicted_next_period = recent_avg * period_days
            
            # Determine trend direction
            if abs(growth_rate) < 5:
                trend_direction = "stable"
            elif growth_rate > 0:
                trend_direction = "increasing"  
            else:
                trend_direction = "decreasing"
            
            # Confidence level based on data consistency
            std_dev = statistics.stdev(daily_costs) if len(daily_costs) > 1 else 0
            mean_cost = statistics.mean(daily_costs)
            coefficient_of_variation = std_dev / mean_cost if mean_cost > 0 else 1
            confidence_level = max(0, min(100, (1 - coefficient_of_variation) * 100))
            
            # Detect anomalies (costs > 2 standard deviations from mean)
            anomalies = []
            if std_dev > 0:
                threshold = mean_cost + (2 * std_dev)
                for i, cost in enumerate(daily_costs):
                    if cost > threshold:
                        anomaly_date = start_date + timedelta(days=i)
                        anomalies.append({
                            'date': anomaly_date.isoformat(),
                            'cost': cost,
                            'deviation': (cost - mean_cost) / std_dev
                        })
            
            # Detect seasonal patterns (simple weekly pattern detection)
            seasonal_pattern = len(daily_costs) >= 14 and self._detect_weekly_pattern(daily_costs)
            
            analysis = TrendAnalysis(
                period=f"{period_days} days",
                growth_rate=growth_rate,
                predicted_next_period=predicted_next_period,
                confidence_level=confidence_level,
                trend_direction=trend_direction,
                seasonal_pattern=seasonal_pattern,
                anomalies_detected=anomalies
            )
            
            logger.info(f"Trend analysis: {growth_rate:.1f}% growth, {trend_direction} trend")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return TrendAnalysis(
                period=f"{period_days} days", growth_rate=0.0,
                predicted_next_period=0.0, confidence_level=0.0,
                trend_direction="stable", seasonal_pattern=False,
                anomalies_detected=[]
            )
    
    async def generate_optimization_recommendations(self, 
                                                 metrics: CostMetrics = None) -> List[OptimizationRecommendation]:
        """
        Generate cost optimization recommendations based on usage patterns
        
        Args:
            metrics: Cost metrics to analyze (will generate if not provided)
            
        Returns:
            List[OptimizationRecommendation]: Prioritized optimization recommendations
        """
        try:
            if not metrics:
                metrics = await self.generate_cost_metrics()
            
            recommendations = []
            
            # Model optimization recommendations
            if 'gemini-pro' in metrics.cost_by_model and 'gemini-flash' in metrics.cost_by_model:
                pro_cost = metrics.cost_by_model['gemini-pro']
                flash_cost = metrics.cost_by_model['gemini-flash']
                
                if pro_cost > flash_cost * 2:  # Pro is significantly more expensive
                    potential_savings = pro_cost * 0.6  # Assume 60% of pro queries can use flash
                    recommendations.append(OptimizationRecommendation(
                        category="model_optimization",
                        recommendation="Increase usage of Gemini Flash for simpler spiritual queries",
                        potential_savings=potential_savings,
                        implementation_effort="low",
                        priority=1,
                        impact_description=f"Could save ${potential_savings:.2f} by using Flash for 60% of queries",
                        implementation_steps=[
                            "Implement query complexity scoring",
                            "Route simple queries to Gemini Flash",
                            "Monitor response quality impact"
                        ]
                    ))
            
            # Caching recommendations
            cache_hit_rate = self._estimate_cache_hit_rate()
            if cache_hit_rate < 0.4:  # Less than 40% cache hit rate
                potential_savings = metrics.total_cost * (0.6 - cache_hit_rate)
                recommendations.append(OptimizationRecommendation(
                    category="caching",
                    recommendation="Improve caching strategy for repeated spiritual queries",
                    potential_savings=potential_savings,
                    implementation_effort="medium",
                    priority=2,
                    impact_description=f"Increase cache hit rate from {cache_hit_rate:.1%} to 60%",
                    implementation_steps=[
                        "Analyze query patterns for commonalities",
                        "Implement semantic caching for similar spiritual questions",
                        "Extend cache expiration for stable content"
                    ]
                ))
            
            # Peak usage optimization
            if metrics.efficiency_score < 70:
                recommendations.append(OptimizationRecommendation(
                    category="efficiency",
                    recommendation="Optimize peak usage patterns and request batching",
                    potential_savings=metrics.total_cost * 0.15,
                    implementation_effort="medium",
                    priority=3,
                    impact_description="Reduce costs through better load distribution",
                    implementation_steps=[
                        "Implement request batching during peak hours",
                        "Add user guidance for off-peak usage",
                        "Optimize concurrent request handling"
                    ]
                ))
            
            # User-specific recommendations
            if len(metrics.cost_by_user) > 1:
                # Find high-cost users
                total_users = len(metrics.cost_by_user)
                high_cost_users = [
                    user for user, cost in metrics.cost_by_user.items()
                    if cost > metrics.total_cost / total_users * 3
                ]
                
                if high_cost_users:
                    recommendations.append(OptimizationRecommendation(
                        category="user_limits",
                        recommendation=f"Implement usage limits for {len(high_cost_users)} high-usage users",
                        potential_savings=sum(metrics.cost_by_user[user] for user in high_cost_users) * 0.25,
                        implementation_effort="low",
                        priority=2,
                        impact_description="Reduce costs from heavy users while maintaining quality",
                        implementation_steps=[
                            "Set per-user daily/hourly limits",
                            "Implement graceful degradation for heavy users",
                            "Add usage notifications"
                        ]
                    ))
            
            # Infrastructure recommendations
            if metrics.cost_by_category.get('infrastructure', 0) > metrics.total_cost * 0.3:
                recommendations.append(OptimizationRecommendation(
                    category="infrastructure",
                    recommendation="Optimize infrastructure costs through right-sizing",
                    potential_savings=metrics.cost_by_category.get('infrastructure', 0) * 0.2,
                    implementation_effort="high",
                    priority=4,
                    impact_description="Reduce infrastructure overhead through optimization",
                    implementation_steps=[
                        "Audit current resource utilization",
                        "Implement auto-scaling policies",
                        "Consider serverless alternatives"
                    ]
                ))
            
            # Sort recommendations by priority
            recommendations.sort(key=lambda x: x.priority)
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def generate_dashboard_report(self, 
                                      report_type: ReportType = ReportType.DAILY,
                                      user_id: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard report
        
        Args:
            report_type: Type of report to generate
            user_id: Optional user ID for user-specific report
            
        Returns:
            Dict: Complete dashboard report with metrics, trends, and recommendations
        """
        try:
            # Determine date range based on report type
            end_date = datetime.now()
            if report_type == ReportType.DAILY:
                start_date = end_date - timedelta(days=1)
                period_days = 7  # For trend analysis
            elif report_type == ReportType.WEEKLY:
                start_date = end_date - timedelta(days=7)
                period_days = 30
            elif report_type == ReportType.MONTHLY:
                start_date = end_date - timedelta(days=30)
                period_days = 90
            else:  # REAL_TIME
                start_date = end_date - timedelta(hours=1)
                period_days = 1
            
            # Generate all components
            metrics = await self.generate_cost_metrics(start_date, end_date, user_id)
            trends = await self.analyze_trends(period_days, user_id)
            recommendations = await self.generate_optimization_recommendations(metrics)
            
            # Create comprehensive report
            report = {
                'report_type': report_type.value,
                'generated_at': datetime.now().isoformat(),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'duration_days': (end_date - start_date).days
                },
                'user_filter': user_id,
                'metrics': metrics.to_dict(),
                'trends': trends.to_dict(),
                'recommendations': [rec.to_dict() for rec in recommendations],
                'summary': {
                    'total_cost': metrics.total_cost,
                    'operations': metrics.operation_count,
                    'efficiency_score': metrics.efficiency_score,
                    'growth_rate': trends.growth_rate,
                    'potential_savings': sum(rec.potential_savings for rec in recommendations)
                }
            }
            
            # Cache the report
            cache_key = f"{report_type.value}_{user_id or 'all'}_{end_date.strftime('%Y%m%d')}"
            self.cached_reports[cache_key] = report
            
            # Save report to file
            report_file = self.storage_path / f"dashboard_report_{cache_key}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Generated {report_type.value} dashboard report: ${metrics.total_cost:.4f} total cost")
            return report
            
        except Exception as e:
            logger.error(f"Error generating dashboard report: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.now().isoformat(),
                'report_type': report_type.value
            }
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object"""
        try:
            # Try different timestamp formats
            for fmt in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            # If all formats fail, return epoch start
            return datetime.fromtimestamp(0)
        except:
            return datetime.fromtimestamp(0)
    
    def _calculate_efficiency_score(self, data: List[Dict[str, Any]]) -> float:
        """Calculate efficiency score based on cost patterns"""
        try:
            if not data:
                return 100.0
            
            # Factors for efficiency scoring
            # 1. Model usage efficiency (Flash vs Pro ratio)
            model_counts = Counter(record.get('model', 'unknown') for record in data)
            flash_ratio = model_counts.get('gemini-flash', 0) / len(data)
            model_efficiency = flash_ratio * 30  # Max 30 points for using Flash
            
            # 2. Cache hit rate efficiency
            cache_hits = sum(1 for record in data if record.get('cache_hit', False))
            cache_efficiency = (cache_hits / len(data)) * 25  # Max 25 points for cache hits
            
            # 3. Cost per operation efficiency
            costs = [record.get('cost', 0) for record in data if record.get('cost', 0) > 0]
            if costs:
                avg_cost = statistics.mean(costs)
                # Efficient if average cost is low (under $0.01 per operation)
                cost_efficiency = max(0, min(25, (0.01 - avg_cost) / 0.01 * 25))
            else:
                cost_efficiency = 25
            
            # 4. Time-based efficiency (off-peak usage)
            peak_hours = [9, 10, 11, 14, 15, 16, 17, 18, 19, 20]  # 9 AM - 8 PM
            off_peak_ops = sum(
                1 for record in data 
                if self._parse_timestamp(record.get('timestamp', '')).hour not in peak_hours
            )
            time_efficiency = (off_peak_ops / len(data)) * 20  # Max 20 points for off-peak usage
            
            total_score = model_efficiency + cache_efficiency + cost_efficiency + time_efficiency
            return min(100.0, max(0.0, total_score))
            
        except Exception as e:
            logger.warning(f"Error calculating efficiency score: {e}")
            return 50.0  # Default neutral score
    
    def _get_daily_costs(self, start_date: datetime, end_date: datetime, user_id: str = None) -> List[float]:
        """Get daily cost totals for trend analysis"""
        try:
            daily_costs = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                
                day_cost = sum(
                    record.get('cost', 0) for record in self.cost_history
                    if day_start <= self._parse_timestamp(record.get('timestamp', '')) <= day_end and
                       (not user_id or record.get('user_id') == user_id)
                )
                
                daily_costs.append(day_cost)
                current_date += timedelta(days=1)
            
            return daily_costs
            
        except Exception as e:
            logger.error(f"Error getting daily costs: {e}")
            return [0.0]
    
    def _detect_weekly_pattern(self, daily_costs: List[float]) -> bool:
        """Detect if there's a weekly pattern in daily costs"""
        try:
            if len(daily_costs) < 14:  # Need at least 2 weeks
                return False
            
            # Compare first week with second week pattern
            week1 = daily_costs[:7]
            week2 = daily_costs[7:14]
            
            # Calculate correlation between weeks
            if statistics.stdev(week1) == 0 or statistics.stdev(week2) == 0:
                return False
            
            # Simple correlation check - if patterns are similar
            correlation = sum((w1 - statistics.mean(week1)) * (w2 - statistics.mean(week2)) 
                            for w1, w2 in zip(week1, week2))
            correlation /= (statistics.stdev(week1) * statistics.stdev(week2) * 7)
            
            return abs(correlation) > 0.5  # 50% correlation threshold
            
        except Exception as e:
            logger.warning(f"Error detecting weekly pattern: {e}")
            return False
    
    def _estimate_cache_hit_rate(self) -> float:
        """Estimate cache hit rate from historical data"""
        try:
            cache_hits = sum(1 for record in self.cost_history if record.get('cache_hit', False))
            total_requests = len(self.cost_history)
            return cache_hits / total_requests if total_requests > 0 else 0.0
        except Exception as e:
            logger.warning(f"Error estimating cache hit rate: {e}")
            return 0.3  # Default 30% estimate
    
    async def add_cost_record(self, 
                            user_id: str,
                            model: str, 
                            cost: float,
                            tokens: int = 0,
                            operation_type: str = "spiritual_guidance",
                            category: str = "llm_operations",
                            cache_hit: bool = False):
        """
        Add a cost record to the analytics system
        
        Args:
            user_id: User identifier
            model: Model used (e.g., 'gemini-pro', 'gemini-flash')
            cost: Cost of the operation
            tokens: Number of tokens used
            operation_type: Type of operation performed
            category: Cost category
            cache_hit: Whether this was a cache hit
        """
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'model': model,
                'cost': cost,
                'token_cost': cost,  # Assuming all cost is token-related for now
                'tokens': tokens,
                'operation_type': operation_type,
                'category': category,
                'cache_hit': cache_hit
            }
            
            self.cost_history.append(record)
            
            # Keep only last 10,000 records for performance
            if len(self.cost_history) > 10000:
                self.cost_history = self.cost_history[-10000:]
            
            # Save periodically
            if len(self.cost_history) % 100 == 0:
                self._save_historical_data()
            
        except Exception as e:
            logger.error(f"Error adding cost record: {e}")


# Dashboard decorator for automatic cost tracking
def with_cost_analytics(dashboard: CostAnalyticsDashboard):
    """
    Decorator to automatically track costs in the analytics dashboard
    
    Args:
        dashboard: CostAnalyticsDashboard instance
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            user_id = kwargs.get('user_id', 'anonymous')
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract cost information from result or function metadata
                cost = getattr(result, 'cost', 0.0) if hasattr(result, 'cost') else 0.0
                tokens = getattr(result, 'tokens', 0) if hasattr(result, 'tokens') else 0
                model = getattr(result, 'model', 'unknown') if hasattr(result, 'model') else 'unknown'
                
                # Add cost record
                await dashboard.add_cost_record(
                    user_id=user_id,
                    model=model,
                    cost=cost,
                    tokens=tokens,
                    operation_type=func.__name__,
                    category="llm_operations",
                    cache_hit=getattr(result, 'cache_hit', False) if hasattr(result, 'cache_hit') else False
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Error in cost analytics wrapper: {e}")
                raise
                
        return wrapper
    return decorator


# Global dashboard instance
_global_dashboard = None

def get_dashboard() -> CostAnalyticsDashboard:
    """Get global dashboard instance"""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = CostAnalyticsDashboard()
    return _global_dashboard


# Example usage and integration
if __name__ == "__main__":
    async def demo_analytics_dashboard():
        """Demonstrate the cost analytics dashboard"""
        print("🎯 Vimarsh AI Cost Analytics Dashboard Demo")
        print("=" * 50)
        
        # Initialize dashboard
        dashboard = CostAnalyticsDashboard("data/demo_analytics")
        
        # Add some sample cost records
        print("\n📊 Adding sample cost data...")
        sample_records = [
            ("user1", "gemini-pro", 0.0045, 1500, "spiritual_guidance"),
            ("user2", "gemini-flash", 0.0012, 1200, "voice_response"),
            ("user1", "gemini-flash", 0.0008, 800, "spiritual_guidance"),
            ("user3", "gemini-pro", 0.0055, 1800, "expert_review"),
            ("user2", "gemini-flash", 0.0009, 900, "spiritual_guidance"),
        ]
        
        for user_id, model, cost, tokens, operation in sample_records:
            await dashboard.add_cost_record(
                user_id=user_id,
                model=model,
                cost=cost,
                tokens=tokens,
                operation_type=operation
            )
        
        # Generate cost metrics
        print("\n💰 Generating cost metrics...")
        metrics = await dashboard.generate_cost_metrics()
        print(f"Total Cost: ${metrics.total_cost:.4f}")
        print(f"Operations: {metrics.operation_count}")
        print(f"Average Cost/Op: ${metrics.average_cost_per_operation:.4f}")
        print(f"Efficiency Score: {metrics.efficiency_score:.1f}/100")
        print(f"Cost by Model: {metrics.cost_by_model}")
        
        # Analyze trends
        print("\n📈 Analyzing trends...")
        trends = await dashboard.analyze_trends(period_days=7)
        print(f"Growth Rate: {trends.growth_rate:.1f}%")
        print(f"Trend Direction: {trends.trend_direction}")
        print(f"Confidence: {trends.confidence_level:.1f}%")
        
        # Generate recommendations
        print("\n💡 Generating optimization recommendations...")
        recommendations = await dashboard.generate_optimization_recommendations(metrics)
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec.recommendation}")
            print(f"   Potential Savings: ${rec.potential_savings:.4f}")
            print(f"   Priority: {rec.priority}/5")
        
        # Generate full dashboard report
        print("\n📋 Generating dashboard report...")
        report = await dashboard.generate_dashboard_report(ReportType.DAILY)
        print(f"Report generated with {len(report['recommendations'])} recommendations")
        print(f"Summary: ${report['summary']['total_cost']:.4f} total, {report['summary']['operations']} ops")
        
        print("\n✅ Analytics dashboard demo completed successfully!")
        
    # Run the demo
    asyncio.run(demo_analytics_dashboard())
