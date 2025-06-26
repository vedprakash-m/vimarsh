"""
AI Cost Forecasting and Budget Planning Tools
Task 7.8: Enhanced AI Cost Management & Dynamic Fallbacks

This module provides comprehensive cost forecasting and budget planning capabilities
for managing AI costs during beta testing and production operations.

Features:
- Historical usage analysis and trend detection
- Predictive cost forecasting using multiple models
- Budget planning with scenario analysis
- Cost optimization recommendations
- Usage pattern analysis and anomaly detection
- Budget allocation and tracking
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path
from collections import defaultdict, deque
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForecastModel(Enum):
    """Forecasting models available"""
    LINEAR_TREND = "linear_trend"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"


class BudgetPeriod(Enum):
    """Budget period types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class UsageMetrics:
    """Usage metrics for cost analysis"""
    timestamp: datetime
    tokens_used: int
    cost: float
    model_used: str
    user_id: Optional[str] = None
    query_type: str = "general"
    response_time: float = 0.0
    quality_score: float = 1.0
    cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class CostForecast:
    """Cost forecast result"""
    period: str
    predicted_cost: float
    confidence_interval: Tuple[float, float]
    model_used: ForecastModel
    accuracy_score: float
    factors: Dict[str, Any]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['model_used'] = self.model_used.value
        return data


@dataclass
class BudgetPlan:
    """Budget planning configuration"""
    id: str
    name: str
    period: BudgetPeriod
    total_budget: float
    allocated_budgets: Dict[str, float]  # category -> budget
    start_date: datetime
    end_date: datetime
    alerts: Dict[str, float]  # threshold -> percentage
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['period'] = self.period.value
        data['start_date'] = self.start_date.isoformat()
        data['end_date'] = self.end_date.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class CostForecaster:
    """AI cost forecasting and budget planning system"""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize cost forecaster
        
        Args:
            storage_path: Path to store historical data and forecasts
        """
        self.storage_path = Path(storage_path) if storage_path else Path("data/cost_forecasting")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Historical data storage
        self.usage_history: List[UsageMetrics] = []
        self.forecasts_cache: Dict[str, CostForecast] = {}
        self.budget_plans: Dict[str, BudgetPlan] = {}
        
        # Analysis parameters
        self.min_history_days = 7  # Minimum days of history for forecasting
        self.max_history_days = 90  # Maximum days to consider
        self.forecast_horizon_days = 30  # Default forecast horizon
        
        # Threading
        self.lock = threading.Lock()
        
        # Load historical data
        self._load_historical_data()
        self._load_budget_plans()
    
    def _load_historical_data(self):
        """Load historical usage data"""
        try:
            history_file = self.storage_path / "usage_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.usage_history = [
                        UsageMetrics(
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            tokens_used=item['tokens_used'],
                            cost=item['cost'],
                            model_used=item['model_used'],
                            user_id=item.get('user_id'),
                            query_type=item.get('query_type', 'general'),
                            response_time=item.get('response_time', 0.0),
                            quality_score=item.get('quality_score', 1.0),
                            cached=item.get('cached', False)
                        )
                        for item in data
                    ]
                logger.info(f"Loaded {len(self.usage_history)} historical usage records")
        except Exception as e:
            logger.warning(f"Could not load historical data: {e}")
    
    def _load_budget_plans(self):
        """Load budget plans"""
        try:
            plans_file = self.storage_path / "budget_plans.json"
            if plans_file.exists():
                with open(plans_file, 'r') as f:
                    data = json.load(f)
                    for plan_id, plan_data in data.items():
                        self.budget_plans[plan_id] = BudgetPlan(
                            id=plan_data['id'],
                            name=plan_data['name'],
                            period=BudgetPeriod(plan_data['period']),
                            total_budget=plan_data['total_budget'],
                            allocated_budgets=plan_data['allocated_budgets'],
                            start_date=datetime.fromisoformat(plan_data['start_date']),
                            end_date=datetime.fromisoformat(plan_data['end_date']),
                            alerts=plan_data['alerts'],
                            created_at=datetime.fromisoformat(plan_data['created_at']),
                            updated_at=datetime.fromisoformat(plan_data['updated_at'])
                        )
                logger.info(f"Loaded {len(self.budget_plans)} budget plans")
        except Exception as e:
            logger.warning(f"Could not load budget plans: {e}")
    
    def _save_historical_data(self):
        """Save historical usage data"""
        try:
            history_file = self.storage_path / "usage_history.json"
            with open(history_file, 'w') as f:
                json.dump([item.to_dict() for item in self.usage_history], f, indent=2)
        except Exception as e:
            logger.error(f"Could not save historical data: {e}")
    
    def _save_budget_plans(self):
        """Save budget plans"""
        try:
            plans_file = self.storage_path / "budget_plans.json"
            with open(plans_file, 'w') as f:
                json.dump({plan_id: plan.to_dict() for plan_id, plan in self.budget_plans.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save budget plans: {e}")
    
    def record_usage(self, 
                    tokens_used: int,
                    cost: float,
                    model_used: str,
                    user_id: Optional[str] = None,
                    query_type: str = "general",
                    response_time: float = 0.0,
                    quality_score: float = 1.0,
                    cached: bool = False):
        """
        Record usage for cost tracking and forecasting
        
        Args:
            tokens_used: Number of tokens consumed
            cost: Cost incurred
            model_used: Model used (e.g., 'gemini-pro', 'gemini-flash')
            user_id: User identifier (optional)
            query_type: Type of query (spiritual, general, etc.)
            response_time: Response time in seconds
            quality_score: Quality score (0.0-1.0)
            cached: Whether response was cached
        """
        with self.lock:
            usage = UsageMetrics(
                timestamp=datetime.now(),
                tokens_used=tokens_used,
                cost=cost,
                model_used=model_used,
                user_id=user_id,
                query_type=query_type,
                response_time=response_time,
                quality_score=quality_score,
                cached=cached
            )
            
            self.usage_history.append(usage)
            
            # Keep only recent history
            cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
            self.usage_history = [u for u in self.usage_history if u.timestamp >= cutoff_date]
            
            # Save periodically
            if len(self.usage_history) % 10 == 0:
                self._save_historical_data()
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics for the specified period
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with usage statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [u for u in self.usage_history if u.timestamp >= cutoff_date]
        
        if not recent_usage:
            return {
                'total_cost': 0.0,
                'total_tokens': 0,
                'total_queries': 0,
                'avg_cost_per_query': 0.0,
                'avg_tokens_per_query': 0.0,
                'cost_by_model': {},
                'cost_by_day': {},
                'cache_hit_rate': 0.0,
                'avg_quality_score': 0.0
            }
        
        total_cost = sum(u.cost for u in recent_usage)
        total_tokens = sum(u.tokens_used for u in recent_usage)
        total_queries = len(recent_usage)
        cached_queries = sum(1 for u in recent_usage if u.cached)
        
        # Cost by model
        cost_by_model = defaultdict(float)
        for usage in recent_usage:
            cost_by_model[usage.model_used] += usage.cost
        
        # Cost by day
        cost_by_day = defaultdict(float)
        for usage in recent_usage:
            day_key = usage.timestamp.strftime('%Y-%m-%d')
            cost_by_day[day_key] += usage.cost
        
        return {
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'total_queries': total_queries,
            'avg_cost_per_query': total_cost / total_queries if total_queries > 0 else 0.0,
            'avg_tokens_per_query': total_tokens / total_queries if total_queries > 0 else 0.0,
            'cost_by_model': dict(cost_by_model),
            'cost_by_day': dict(cost_by_day),
            'cache_hit_rate': cached_queries / total_queries if total_queries > 0 else 0.0,
            'avg_quality_score': statistics.mean(u.quality_score for u in recent_usage)
        }
    
    def _linear_trend_forecast(self, daily_costs: List[float], horizon_days: int) -> Tuple[List[float], float]:
        """Linear trend forecasting"""
        if len(daily_costs) < 2:
            return [daily_costs[-1] if daily_costs else 0.0] * horizon_days, 0.5
        
        # Simple linear regression
        x_values = list(range(len(daily_costs)))
        y_values = daily_costs
        
        # Calculate slope and intercept using simple statistics
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x_values[i] * y_values[i] for i in range(n))
        sum_x2 = sum(x * x for x in x_values)
        
        # Linear regression formulas
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0
            intercept = statistics.mean(y_values)
        
        # Forecast
        future_x = list(range(len(daily_costs), len(daily_costs) + horizon_days))
        forecast = [max(0, slope * xi + intercept) for xi in future_x]
        
        # Calculate accuracy (R-squared approximation)
        y_pred = [slope * xi + intercept for xi in x_values]
        ss_res = sum((y_values[i] - y_pred[i]) ** 2 for i in range(len(y_values)))
        mean_y = statistics.mean(y_values)
        ss_tot = sum((y_values[i] - mean_y) ** 2 for i in range(len(y_values)))
        accuracy = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.5
        
        return forecast, max(0.1, min(0.9, accuracy))
    
    def _moving_average_forecast(self, daily_costs: List[float], horizon_days: int) -> Tuple[List[float], float]:
        """Moving average forecasting"""
        if not daily_costs:
            return [0.0] * horizon_days, 0.5
        
        window_size = min(7, len(daily_costs))  # 7-day moving average or less
        recent_avg = statistics.mean(daily_costs[-window_size:])
        
        forecast = [recent_avg] * horizon_days
        
        # Calculate accuracy based on recent stability
        if len(daily_costs) >= window_size and window_size > 1:
            recent_std = statistics.stdev(daily_costs[-window_size:])
            recent_mean = statistics.mean(daily_costs[-window_size:])
            accuracy = max(0.1, 1 - (recent_std / recent_mean)) if recent_mean > 0 else 0.5
        else:
            accuracy = 0.5
        
        return forecast, accuracy
    
    def _exponential_smoothing_forecast(self, daily_costs: List[float], horizon_days: int) -> Tuple[List[float], float]:
        """Exponential smoothing forecasting"""
        if not daily_costs:
            return [0.0] * horizon_days, 0.5
        
        alpha = 0.3  # Smoothing factor
        
        # Calculate smoothed values
        smoothed = [daily_costs[0]]
        for i in range(1, len(daily_costs)):
            smoothed.append(alpha * daily_costs[i] + (1 - alpha) * smoothed[-1])
        
        # Forecast using last smoothed value
        forecast = [smoothed[-1]] * horizon_days
        
        # Calculate accuracy
        errors = [abs(daily_costs[i] - smoothed[i]) for i in range(len(daily_costs))]
        mean_error = statistics.mean(errors)
        mean_actual = statistics.mean(daily_costs)
        accuracy = max(0.1, 1 - (mean_error / mean_actual)) if mean_actual > 0 else 0.5
        
        return forecast, accuracy
    
    def generate_forecast(self, 
                         horizon_days: int = 30,
                         model: ForecastModel = ForecastModel.LINEAR_TREND) -> Optional[CostForecast]:
        """
        Generate cost forecast for the specified horizon
        
        Args:
            horizon_days: Number of days to forecast
            model: Forecasting model to use
            
        Returns:
            Cost forecast or None if insufficient data
        """
        # Check if we have sufficient history
        cutoff_date = datetime.now() - timedelta(days=self.min_history_days)
        recent_usage = [u for u in self.usage_history if u.timestamp >= cutoff_date]
        
        if len(recent_usage) < self.min_history_days:
            logger.warning(f"Insufficient data for forecasting. Need at least {self.min_history_days} days of history")
            return None
        
        # Aggregate daily costs
        daily_costs = defaultdict(float)
        for usage in recent_usage:
            day_key = usage.timestamp.strftime('%Y-%m-%d')
            daily_costs[day_key] += usage.cost
        
        # Convert to list, filling missing days with 0
        start_date = min(usage.timestamp for usage in recent_usage).date()
        end_date = datetime.now().date()
        
        cost_series = []
        current_date = start_date
        while current_date <= end_date:
            day_key = current_date.strftime('%Y-%m-%d')
            cost_series.append(daily_costs.get(day_key, 0.0))
            current_date += timedelta(days=1)
        
        # Generate forecast based on model
        if model == ForecastModel.LINEAR_TREND:
            forecast_values, accuracy = self._linear_trend_forecast(cost_series, horizon_days)
        elif model == ForecastModel.MOVING_AVERAGE:
            forecast_values, accuracy = self._moving_average_forecast(cost_series, horizon_days)
        elif model == ForecastModel.EXPONENTIAL_SMOOTHING:
            forecast_values, accuracy = self._exponential_smoothing_forecast(cost_series, horizon_days)
        else:
            # Default to linear trend
            forecast_values, accuracy = self._linear_trend_forecast(cost_series, horizon_days)
        
        # Calculate total predicted cost
        predicted_cost = sum(forecast_values)
        
        # Calculate confidence interval (simple approach)
        if len(cost_series) > 1:
            historical_std = statistics.stdev(cost_series)
            confidence_margin = historical_std * 1.96  # 95% confidence
            lower_bound = max(0, predicted_cost - confidence_margin)
            upper_bound = predicted_cost + confidence_margin
        else:
            lower_bound = predicted_cost * 0.5
            upper_bound = predicted_cost * 1.5
        
        # Generate recommendations
        recommendations = self._generate_recommendations(recent_usage, predicted_cost)
        
        forecast = CostForecast(
            period=f"Next {horizon_days} days",
            predicted_cost=predicted_cost,
            confidence_interval=(lower_bound, upper_bound),
            model_used=model,
            accuracy_score=accuracy,
            factors={
                'historical_avg_daily_cost': statistics.mean(cost_series) if cost_series else 0.0,
                'trend_slope': (cost_series[-1] - cost_series[0]) / len(cost_series) if len(cost_series) > 1 else 0.0,
                'cache_hit_rate': sum(1 for u in recent_usage if u.cached) / len(recent_usage) if recent_usage else 0.0,
                'primary_model': max(set(u.model_used for u in recent_usage), key=lambda x: sum(1 for u in recent_usage if u.model_used == x)) if recent_usage else 'unknown'
            },
            recommendations=recommendations
        )
        
        # Cache forecast
        cache_key = f"{model.value}_{horizon_days}_{datetime.now().strftime('%Y-%m-%d')}"
        self.forecasts_cache[cache_key] = forecast
        
        return forecast
    
    def _generate_recommendations(self, recent_usage: List[UsageMetrics], predicted_cost: float) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        if not recent_usage:
            return ["📊 Start collecting usage data to get personalized recommendations"]
        
        # Analyze cache hit rate
        cache_hit_rate = sum(1 for u in recent_usage if u.cached) / len(recent_usage)
        if cache_hit_rate < 0.3:
            recommendations.append("🔄 Consider implementing more aggressive caching to reduce costs by up to 50%")
        
        # Analyze model usage
        model_costs = defaultdict(float)
        for usage in recent_usage:
            model_costs[usage.model_used] += usage.cost
        
        if model_costs.get('gemini-pro', 0) > model_costs.get('gemini-flash', 0) * 2:
            recommendations.append("⚡ Consider using Gemini Flash for simpler queries to reduce costs by up to 80%")
        
        # Analyze usage patterns
        hourly_usage = defaultdict(int)
        for usage in recent_usage:
            hour = usage.timestamp.hour
            hourly_usage[hour] += 1
        
        peak_hours = sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        if peak_hours and peak_hours[0][1] > len(recent_usage) * 0.3:
            recommendations.append(f"📅 Peak usage detected at {peak_hours[0][0]}:00. Consider implementing request batching during peak hours")
        
        # Budget-based recommendations
        daily_predicted = predicted_cost / 30  # Assuming 30-day forecast
        if daily_predicted > 10:  # $10/day threshold
            recommendations.append("💰 High cost forecast detected. Consider implementing stricter budget controls and user limits")
        
        # Quality vs Cost analysis
        avg_quality = statistics.mean(u.quality_score for u in recent_usage)
        if avg_quality > 0.9 and predicted_cost > 5:  # High quality, moderate cost
            recommendations.append("⚖️ Excellent quality maintained. Consider A/B testing with more cost-effective models for non-critical queries")
        
        if not recommendations:
            recommendations.append("✅ Cost optimization looks good! Continue monitoring usage patterns")
        
        return recommendations
    
    def create_budget_plan(self,
                          name: str,
                          period: BudgetPeriod,
                          total_budget: float,
                          allocated_budgets: Dict[str, float] = None,
                          duration_days: int = 30,
                          alerts: Dict[str, float] = None) -> str:
        """
        Create a new budget plan
        
        Args:
            name: Budget plan name
            period: Budget period (daily, weekly, monthly)
            total_budget: Total budget amount
            allocated_budgets: Budget allocation by category
            duration_days: Duration of the budget plan
            alerts: Alert thresholds (percentage -> threshold)
            
        Returns:
            Budget plan ID
        """
        plan_id = f"budget_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        # Default allocations
        if allocated_budgets is None:
            allocated_budgets = {
                'llm_costs': total_budget * 0.7,
                'infrastructure': total_budget * 0.2,
                'storage': total_budget * 0.05,
                'monitoring': total_budget * 0.05
            }
        
        # Default alerts
        if alerts is None:
            alerts = {
                'warning': 0.75,  # 75% of budget
                'critical': 0.90,  # 90% of budget
                'emergency': 0.95   # 95% of budget
            }
        
        plan = BudgetPlan(
            id=plan_id,
            name=name,
            period=period,
            total_budget=total_budget,
            allocated_budgets=allocated_budgets,
            start_date=start_date,
            end_date=end_date,
            alerts=alerts,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with self.lock:
            self.budget_plans[plan_id] = plan
            self._save_budget_plans()
        
        logger.info(f"Created budget plan '{name}' with ID {plan_id}")
        return plan_id
    
    def get_budget_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get budget status for a plan
        
        Args:
            plan_id: Budget plan ID
            
        Returns:
            Budget status dictionary or None if plan not found
        """
        if plan_id not in self.budget_plans:
            return None
        
        plan = self.budget_plans[plan_id]
        
        # Calculate current spend within plan period
        plan_usage = [
            u for u in self.usage_history 
            if plan.start_date <= u.timestamp <= plan.end_date
        ]
        
        current_spend = sum(u.cost for u in plan_usage)
        remaining_budget = plan.total_budget - current_spend
        utilization = current_spend / plan.total_budget if plan.total_budget > 0 else 0.0
        
        # Calculate spend by category (simplified)
        spend_by_category = {
            'llm_costs': sum(u.cost for u in plan_usage),
            'infrastructure': 0.0,  # Would be calculated from actual infrastructure costs
            'storage': 0.0,         # Would be calculated from storage costs
            'monitoring': 0.0       # Would be calculated from monitoring costs
        }
        
        # Check alert thresholds
        active_alerts = []
        for alert_name, threshold in plan.alerts.items():
            if utilization >= threshold:
                active_alerts.append({
                    'type': alert_name,
                    'threshold': threshold,
                    'current': utilization,
                    'message': f"Budget utilization ({utilization:.1%}) has exceeded {alert_name} threshold ({threshold:.1%})"
                })
        
        return {
            'plan_id': plan_id,
            'plan_name': plan.name,
            'total_budget': plan.total_budget,
            'current_spend': current_spend,
            'remaining_budget': remaining_budget,
            'utilization': utilization,
            'spend_by_category': spend_by_category,
            'active_alerts': active_alerts,
            'days_remaining': (plan.end_date - datetime.now()).days,
            'daily_burn_rate': current_spend / max(1, (datetime.now() - plan.start_date).days),
            'projected_spend': current_spend + (remaining_budget * utilization) if utilization > 0 else current_spend
        }
    
    def get_cost_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive cost analytics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Analytics dictionary
        """
        stats = self.get_usage_stats(days)
        
        # Generate forecast
        forecast = self.generate_forecast(horizon_days=30)
        
        # Analyze trends
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [u for u in self.usage_history if u.timestamp >= cutoff_date]
        
        # Cost trend analysis
        daily_costs = defaultdict(float)
        for usage in recent_usage:
            day_key = usage.timestamp.strftime('%Y-%m-%d')
            daily_costs[day_key] += usage.cost
        
        cost_values = list(daily_costs.values())
        trend_direction = "stable"
        if len(cost_values) >= 2:
            recent_avg = statistics.mean(cost_values[-7:]) if len(cost_values) >= 7 else statistics.mean(cost_values)
            older_avg = statistics.mean(cost_values[:-7]) if len(cost_values) >= 14 else statistics.mean(cost_values[:len(cost_values)//2]) if len(cost_values) >= 2 else recent_avg
            
            if recent_avg > older_avg * 1.1:
                trend_direction = "increasing"
            elif recent_avg < older_avg * 0.9:
                trend_direction = "decreasing"
        
        return {
            'period_days': days,
            'usage_stats': stats,
            'forecast': forecast.to_dict() if forecast else None,
            'trend_analysis': {
                'direction': trend_direction,
                'daily_costs': dict(daily_costs),
                'peak_cost_day': max(daily_costs.items(), key=lambda x: x[1]) if daily_costs else None,
                'lowest_cost_day': min(daily_costs.items(), key=lambda x: x[1]) if daily_costs else None
            },
            'efficiency_metrics': {
                'cost_per_token': stats['total_cost'] / stats['total_tokens'] if stats['total_tokens'] > 0 else 0.0,
                'cache_savings': stats['cache_hit_rate'] * stats['total_cost'],  # Estimated savings from caching
                'quality_cost_ratio': stats['avg_quality_score'] / (stats['avg_cost_per_query'] + 0.001)  # Quality per cost unit
            },
            'generated_at': datetime.now().isoformat()
        }


# Global instance
_cost_forecaster: Optional[CostForecaster] = None

def get_cost_forecaster() -> CostForecaster:
    """Get global cost forecaster instance"""
    global _cost_forecaster
    if _cost_forecaster is None:
        _cost_forecaster = CostForecaster()
    return _cost_forecaster


# Decorator for automatic cost tracking
def with_cost_tracking(query_type: str = "general"):
    """Decorator to automatically track costs for forecasting"""
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            forecaster = get_cost_forecaster()
            start_time = datetime.now()
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract cost information from result (assuming it's included in response)
                if isinstance(result, dict) and 'cost_info' in result:
                    cost_info = result['cost_info']
                    forecaster.record_usage(
                        tokens_used=cost_info.get('tokens_used', 0),
                        cost=cost_info.get('cost', 0.0),
                        model_used=cost_info.get('model_used', 'unknown'),
                        query_type=query_type,
                        response_time=(datetime.now() - start_time).total_seconds(),
                        quality_score=cost_info.get('quality_score', 1.0),
                        cached=cost_info.get('cached', False)
                    )
                
                return result
            except Exception as e:
                # Still record the attempt for cost tracking
                response_time = (datetime.now() - start_time).total_seconds()
                forecaster.record_usage(
                    tokens_used=0,
                    cost=0.0,
                    model_used='error',
                    query_type=query_type,
                    response_time=response_time,
                    quality_score=0.0,
                    cached=False
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            forecaster = get_cost_forecaster()
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                
                # Extract cost information from result
                if isinstance(result, dict) and 'cost_info' in result:
                    cost_info = result['cost_info']
                    forecaster.record_usage(
                        tokens_used=cost_info.get('tokens_used', 0),
                        cost=cost_info.get('cost', 0.0),
                        model_used=cost_info.get('model_used', 'unknown'),
                        query_type=query_type,
                        response_time=(datetime.now() - start_time).total_seconds(),
                        quality_score=cost_info.get('quality_score', 1.0),
                        cached=cost_info.get('cached', False)
                    )
                
                return result
            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds()
                forecaster.record_usage(
                    tokens_used=0,
                    cost=0.0,
                    model_used='error',
                    query_type=query_type,
                    response_time=response_time,
                    quality_score=0.0,
                    cached=False
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Example usage and testing
if __name__ == "__main__":
    async def test_cost_forecasting():
        print("🕉️ Testing AI Cost Forecasting and Budget Planning")
        print("=" * 60)
        
        forecaster = CostForecaster()
        
        print("1. Recording sample usage data...")
        # Simulate usage data
        models = ['gemini-pro', 'gemini-flash']
        query_types = ['spiritual', 'general', 'complex']
        
        for i in range(50):  # 50 sample records
            import random
            forecaster.record_usage(
                tokens_used=random.randint(100, 1000),
                cost=random.uniform(0.01, 0.5),
                model_used=random.choice(models),
                query_type=random.choice(query_types),
                response_time=random.uniform(0.5, 3.0),
                quality_score=random.uniform(0.8, 1.0),
                cached=random.choice([True, False])
            )
        
        print("2. Generating usage statistics...")
        stats = forecaster.get_usage_stats(30)
        print(f"   Total cost: ${stats['total_cost']:.2f}")
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"   Avg quality score: {stats['avg_quality_score']:.2f}")
        
        print("\n3. Generating cost forecast...")
        forecast = forecaster.generate_forecast(horizon_days=30)
        if forecast:
            print(f"   Predicted cost (30 days): ${forecast.predicted_cost:.2f}")
            print(f"   Confidence interval: ${forecast.confidence_interval[0]:.2f} - ${forecast.confidence_interval[1]:.2f}")
            print(f"   Model used: {forecast.model_used.value}")
            print(f"   Accuracy score: {forecast.accuracy_score:.2f}")
            print("   Recommendations:")
            for rec in forecast.recommendations:
                print(f"     • {rec}")
        
        print("\n4. Creating budget plan...")
        plan_id = forecaster.create_budget_plan(
            name="Beta Testing Budget",
            period=BudgetPeriod.MONTHLY,
            total_budget=100.0,
            duration_days=30
        )
        print(f"   Created budget plan: {plan_id}")
        
        print("\n5. Checking budget status...")
        status = forecaster.get_budget_status(plan_id)
        if status:
            print(f"   Current spend: ${status['current_spend']:.2f}")
            print(f"   Budget utilization: {status['utilization']:.1%}")
            print(f"   Remaining budget: ${status['remaining_budget']:.2f}")
            print(f"   Daily burn rate: ${status['daily_burn_rate']:.2f}")
        
        print("\n6. Generating cost analytics...")
        analytics = forecaster.get_cost_analytics(30)
        print(f"   Trend direction: {analytics['trend_analysis']['direction']}")
        print(f"   Cost per token: ${analytics['efficiency_metrics']['cost_per_token']:.4f}")
        print(f"   Quality/cost ratio: {analytics['efficiency_metrics']['quality_cost_ratio']:.2f}")
        
        print("\n✅ Cost forecasting and budget planning testing completed!")
    
    asyncio.run(test_cost_forecasting())
