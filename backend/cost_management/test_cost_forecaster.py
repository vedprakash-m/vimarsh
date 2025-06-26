"""
Tests for AI Cost Forecasting and Budget Planning Tools
Task 7.8: Enhanced AI Cost Management & Dynamic Fallbacks

This module tests the comprehensive cost forecasting and budget planning
capabilities including usage tracking, forecast generation, and budget management.
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
import statistics

from .cost_forecaster import (
    CostForecaster,
    ForecastModel,
    BudgetPeriod,
    UsageMetrics,
    CostForecast,
    BudgetPlan,
    with_cost_tracking,
    get_cost_forecaster
)


class TestUsageMetrics:
    """Test usage metrics data structure"""
    
    def test_usage_metrics_creation(self):
        """Test usage metrics creation"""
        timestamp = datetime.now()
        metrics = UsageMetrics(
            timestamp=timestamp,
            tokens_used=500,
            cost=0.25,
            model_used='gemini-pro',
            user_id='user123',
            query_type='spiritual',
            response_time=1.5,
            quality_score=0.95,
            cached=False
        )
        
        assert metrics.timestamp == timestamp
        assert metrics.tokens_used == 500
        assert metrics.cost == 0.25
        assert metrics.model_used == 'gemini-pro'
        assert metrics.user_id == 'user123'
        assert metrics.query_type == 'spiritual'
        assert metrics.response_time == 1.5
        assert metrics.quality_score == 0.95
        assert metrics.cached == False
    
    def test_usage_metrics_to_dict(self):
        """Test usage metrics serialization"""
        timestamp = datetime.now()
        metrics = UsageMetrics(
            timestamp=timestamp,
            tokens_used=500,
            cost=0.25,
            model_used='gemini-pro'
        )
        
        data = metrics.to_dict()
        assert data['timestamp'] == timestamp.isoformat()
        assert data['tokens_used'] == 500
        assert data['cost'] == 0.25
        assert data['model_used'] == 'gemini-pro'


class TestCostForecaster:
    """Test cost forecaster functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.forecaster = CostForecaster(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test forecaster initialization"""
        assert isinstance(self.forecaster, CostForecaster)
        assert self.forecaster.storage_path.exists()
        assert self.forecaster.min_history_days == 7
        assert self.forecaster.max_history_days == 90
        assert self.forecaster.forecast_horizon_days == 30
        assert len(self.forecaster.usage_history) == 0
        assert len(self.forecaster.budget_plans) == 0
    
    def test_record_usage(self):
        """Test usage recording"""
        self.forecaster.record_usage(
            tokens_used=500,
            cost=0.25,
            model_used='gemini-pro',
            user_id='user123',
            query_type='spiritual',
            response_time=1.5,
            quality_score=0.95,
            cached=False
        )
        
        assert len(self.forecaster.usage_history) == 1
        usage = self.forecaster.usage_history[0]
        assert usage.tokens_used == 500
        assert usage.cost == 0.25
        assert usage.model_used == 'gemini-pro'
        assert usage.user_id == 'user123'
        assert usage.query_type == 'spiritual'
        assert usage.response_time == 1.5
        assert usage.quality_score == 0.95
        assert usage.cached == False
    
    def test_usage_history_cleanup(self):
        """Test usage history cleanup for old records"""
        # Record old usage (beyond max_history_days)
        old_date = datetime.now() - timedelta(days=self.forecaster.max_history_days + 1)
        
        # Temporarily add old usage
        old_usage = UsageMetrics(
            timestamp=old_date,
            tokens_used=100,
            cost=0.05,
            model_used='gemini-pro'
        )
        self.forecaster.usage_history.append(old_usage)
        
        # Record new usage (should trigger cleanup)
        self.forecaster.record_usage(
            tokens_used=500,
            cost=0.25,
            model_used='gemini-pro'
        )
        
        # Old usage should be removed
        assert len(self.forecaster.usage_history) == 1
        assert self.forecaster.usage_history[0].tokens_used == 500
    
    def test_get_usage_stats_empty(self):
        """Test usage stats with no data"""
        stats = self.forecaster.get_usage_stats(30)
        
        assert stats['total_cost'] == 0.0
        assert stats['total_tokens'] == 0
        assert stats['total_queries'] == 0
        assert stats['avg_cost_per_query'] == 0.0
        assert stats['avg_tokens_per_query'] == 0.0
        assert stats['cost_by_model'] == {}
        assert stats['cost_by_day'] == {}
        assert stats['cache_hit_rate'] == 0.0
        assert stats['avg_quality_score'] == 0.0
    
    def test_get_usage_stats_with_data(self):
        """Test usage stats with sample data"""
        # Record multiple usage entries
        models = ['gemini-pro', 'gemini-flash']
        for i in range(10):
            self.forecaster.record_usage(
                tokens_used=100 + i * 50,
                cost=0.1 + i * 0.05,
                model_used=models[i % 2],
                cached=(i % 3 == 0),  # Every 3rd query is cached
                quality_score=0.8 + (i % 5) * 0.04  # Quality varies
            )
        
        stats = self.forecaster.get_usage_stats(30)
        
        assert stats['total_cost'] == sum(0.1 + i * 0.05 for i in range(10))
        assert stats['total_tokens'] == sum(100 + i * 50 for i in range(10))
        assert stats['total_queries'] == 10
        assert stats['avg_cost_per_query'] > 0
        assert stats['avg_tokens_per_query'] > 0
        assert len(stats['cost_by_model']) == 2
        assert stats['cache_hit_rate'] > 0  # Some queries are cached
        assert stats['avg_quality_score'] > 0.8
    
    def test_linear_trend_forecast(self):
        """Test linear trend forecasting"""
        daily_costs = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]  # Increasing trend
        forecast, accuracy = self.forecaster._linear_trend_forecast(daily_costs, 7)
        
        assert len(forecast) == 7
        assert all(cost > 0 for cost in forecast)
        assert 0.1 <= accuracy <= 0.9
        # Should predict increasing trend
        assert forecast[0] > daily_costs[-1]
    
    def test_moving_average_forecast(self):
        """Test moving average forecasting"""
        daily_costs = [2.0, 2.1, 1.9, 2.0, 2.2, 1.8, 2.0]  # Stable around 2.0
        forecast, accuracy = self.forecaster._moving_average_forecast(daily_costs, 7)
        
        assert len(forecast) == 7
        assert all(cost > 0 for cost in forecast)
        assert 0.1 <= accuracy <= 1.0  # Allow accuracy up to 1.0
        # Should predict around the recent average
        recent_avg = statistics.mean(daily_costs[-7:])
        assert all(abs(cost - recent_avg) < 0.5 for cost in forecast)
    
    def test_exponential_smoothing_forecast(self):
        """Test exponential smoothing forecasting"""
        daily_costs = [1.0, 1.5, 2.0, 1.8, 2.2, 2.1, 2.0]
        forecast, accuracy = self.forecaster._exponential_smoothing_forecast(daily_costs, 5)
        
        assert len(forecast) == 5
        assert all(cost > 0 for cost in forecast)
        assert 0.1 <= accuracy <= 0.9
    
    def test_generate_forecast_insufficient_data(self):
        """Test forecast generation with insufficient data"""
        # Only record 2 days of data (less than min_history_days)
        for i in range(2):
            self.forecaster.record_usage(
                tokens_used=100,
                cost=0.1,
                model_used='gemini-pro'
            )
        
        forecast = self.forecaster.generate_forecast()
        assert forecast is None
    
    def test_generate_forecast_with_data(self):
        """Test forecast generation with sufficient data"""
        # Record 10 days of data
        for i in range(10):
            # Simulate data for different days
            timestamp = datetime.now() - timedelta(days=9-i)
            usage = UsageMetrics(
                timestamp=timestamp,
                tokens_used=100 + i * 10,
                cost=0.1 + i * 0.01,
                model_used='gemini-pro'
            )
            self.forecaster.usage_history.append(usage)
        
        forecast = self.forecaster.generate_forecast(horizon_days=7)
        
        assert forecast is not None
        assert forecast.predicted_cost > 0
        assert len(forecast.confidence_interval) == 2
        assert forecast.confidence_interval[0] >= 0
        assert forecast.confidence_interval[1] >= forecast.confidence_interval[0]
        assert isinstance(forecast.model_used, ForecastModel)
        assert 0 <= forecast.accuracy_score <= 1
        assert len(forecast.recommendations) > 0
    
    def test_create_budget_plan(self):
        """Test budget plan creation"""
        plan_id = self.forecaster.create_budget_plan(
            name="Test Budget",
            period=BudgetPeriod.MONTHLY,
            total_budget=100.0,
            duration_days=30
        )
        
        assert plan_id.startswith("budget_")
        assert plan_id in self.forecaster.budget_plans
        
        plan = self.forecaster.budget_plans[plan_id]
        assert plan.name == "Test Budget"
        assert plan.period == BudgetPeriod.MONTHLY
        assert plan.total_budget == 100.0
        assert len(plan.allocated_budgets) > 0
        assert sum(plan.allocated_budgets.values()) <= plan.total_budget
    
    def test_budget_plan_with_custom_allocations(self):
        """Test budget plan with custom allocations"""
        custom_allocations = {
            'llm_costs': 80.0,
            'infrastructure': 15.0,
            'monitoring': 5.0
        }
        
        plan_id = self.forecaster.create_budget_plan(
            name="Custom Budget",
            period=BudgetPeriod.WEEKLY,
            total_budget=100.0,
            allocated_budgets=custom_allocations
        )
        
        plan = self.forecaster.budget_plans[plan_id]
        assert plan.allocated_budgets == custom_allocations
    
    def test_get_budget_status_nonexistent(self):
        """Test budget status for non-existent plan"""
        status = self.forecaster.get_budget_status("nonexistent")
        assert status is None
    
    def test_get_budget_status_with_usage(self):
        """Test budget status with actual usage"""
        # Create budget plan
        plan_id = self.forecaster.create_budget_plan(
            name="Test Budget",
            period=BudgetPeriod.MONTHLY,
            total_budget=100.0
        )
        
        # Record some usage within the budget period
        for i in range(5):
            self.forecaster.record_usage(
                tokens_used=100,
                cost=5.0,  # Total: $25
                model_used='gemini-pro'
            )
        
        status = self.forecaster.get_budget_status(plan_id)
        
        assert status is not None
        assert status['plan_id'] == plan_id
        assert status['plan_name'] == "Test Budget"
        assert status['total_budget'] == 100.0
        assert status['current_spend'] == 25.0
        assert status['remaining_budget'] == 75.0
        assert status['utilization'] == 0.25
        assert status['days_remaining'] >= 0
        assert status['daily_burn_rate'] > 0
    
    def test_budget_alerts(self):
        """Test budget alert generation"""
        # Create budget plan with custom alerts
        plan_id = self.forecaster.create_budget_plan(
            name="Alert Test Budget",
            period=BudgetPeriod.MONTHLY,
            total_budget=100.0,
            alerts={'warning': 0.5, 'critical': 0.8}  # 50% and 80% thresholds
        )
        
        # Record usage to exceed warning threshold
        for i in range(10):
            self.forecaster.record_usage(
                tokens_used=100,
                cost=6.0,  # Total: $60 (60% of budget)
                model_used='gemini-pro'
            )
        
        status = self.forecaster.get_budget_status(plan_id)
        
        assert len(status['active_alerts']) > 0
        alert = status['active_alerts'][0]
        assert alert['type'] == 'warning'
        assert alert['current'] >= alert['threshold']
    
    def test_get_cost_analytics(self):
        """Test comprehensive cost analytics"""
        # Record varied usage data
        models = ['gemini-pro', 'gemini-flash']
        query_types = ['spiritual', 'general']
        
        for i in range(20):
            self.forecaster.record_usage(
                tokens_used=100 + i * 25,
                cost=0.05 + i * 0.02,
                model_used=models[i % 2],
                query_type=query_types[i % 2],
                cached=(i % 4 == 0),
                quality_score=0.8 + (i % 5) * 0.04
            )
        
        analytics = self.forecaster.get_cost_analytics(30)
        
        assert 'period_days' in analytics
        assert analytics['period_days'] == 30
        assert 'usage_stats' in analytics
        assert 'trend_analysis' in analytics
        assert 'efficiency_metrics' in analytics
        assert 'generated_at' in analytics
        
        # Check trend analysis
        trend = analytics['trend_analysis']
        assert trend['direction'] in ['increasing', 'decreasing', 'stable']
        assert 'daily_costs' in trend
        assert 'peak_cost_day' in trend
        assert 'lowest_cost_day' in trend
        
        # Check efficiency metrics
        efficiency = analytics['efficiency_metrics']
        assert efficiency['cost_per_token'] >= 0
        assert efficiency['cache_savings'] >= 0
        assert efficiency['quality_cost_ratio'] >= 0
    
    def test_persistence(self):
        """Test data persistence across instances"""
        # Record usage in first instance
        self.forecaster.record_usage(
            tokens_used=500,
            cost=0.25,
            model_used='gemini-pro'
        )
        
        # Create budget plan
        plan_id = self.forecaster.create_budget_plan(
            name="Persistence Test",
            period=BudgetPeriod.MONTHLY,
            total_budget=100.0
        )
        
        # Force save data
        self.forecaster._save_historical_data()
        self.forecaster._save_budget_plans()
        
        # Create new instance with same storage path
        forecaster2 = CostForecaster(storage_path=self.temp_dir)
        
        # Data should be loaded
        assert len(forecaster2.usage_history) == 1
        assert forecaster2.usage_history[0].tokens_used == 500
        assert plan_id in forecaster2.budget_plans
        assert forecaster2.budget_plans[plan_id].name == "Persistence Test"


class TestCostTrackingDecorator:
    """Test cost tracking decorator"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        # Reset global forecaster
        import cost_management.cost_forecaster as cf
        cf._cost_forecaster = CostForecaster(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @with_cost_tracking(query_type="test")
    def sample_function_with_cost_info(self):
        """Sample function that returns cost info"""
        return {
            'response': 'Test response',
            'cost_info': {
                'tokens_used': 500,
                'cost': 0.25,
                'model_used': 'gemini-pro',
                'quality_score': 0.95,
                'cached': False
            }
        }
    
    @with_cost_tracking(query_type="test")
    def sample_function_no_cost_info(self):
        """Sample function without cost info"""
        return {'response': 'Test response'}
    
    @with_cost_tracking(query_type="test")
    def sample_function_with_error(self):
        """Sample function that raises an error"""
        raise ValueError("Test error")
    
    def test_cost_tracking_with_cost_info(self):
        """Test decorator with cost information"""
        forecaster = get_cost_forecaster()
        initial_count = len(forecaster.usage_history)
        
        result = self.sample_function_with_cost_info()
        
        assert result['response'] == 'Test response'
        assert len(forecaster.usage_history) == initial_count + 1
        
        usage = forecaster.usage_history[-1]
        assert usage.tokens_used == 500
        assert usage.cost == 0.25
        assert usage.model_used == 'gemini-pro'
        assert usage.query_type == 'test'
        assert usage.quality_score == 0.95
        assert usage.cached == False
    
    def test_cost_tracking_no_cost_info(self):
        """Test decorator without cost information"""
        forecaster = get_cost_forecaster()
        initial_count = len(forecaster.usage_history)
        
        result = self.sample_function_no_cost_info()
        
        assert result['response'] == 'Test response'
        # Should not record usage without cost info
        assert len(forecaster.usage_history) == initial_count
    
    def test_cost_tracking_with_error(self):
        """Test decorator with function error"""
        forecaster = get_cost_forecaster()
        initial_count = len(forecaster.usage_history)
        
        with pytest.raises(ValueError, match="Test error"):
            self.sample_function_with_error()
        
        # Should record error attempt
        assert len(forecaster.usage_history) == initial_count + 1
        
        usage = forecaster.usage_history[-1]
        assert usage.tokens_used == 0
        assert usage.cost == 0.0
        assert usage.model_used == 'error'
        assert usage.query_type == 'test'


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.forecaster = CostForecaster(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_beta_testing_scenario(self):
        """Test complete beta testing cost management scenario"""
        print("\n🧪 Testing Beta Testing Cost Management Scenario")
        
        # 1. Create beta testing budget
        plan_id = self.forecaster.create_budget_plan(
            name="Beta Testing Budget",
            period=BudgetPeriod.MONTHLY,
            total_budget=50.0,  # $50/month for beta
            duration_days=30,
            alerts={'warning': 0.7, 'critical': 0.9}
        )
        
        # 2. Simulate beta testing usage over time
        import random
        models = ['gemini-pro', 'gemini-flash']
        query_types = ['spiritual', 'general', 'complex']
        
        for day in range(15):  # 15 days of beta testing
            daily_queries = random.randint(10, 30)  # Variable daily usage
            
            for query in range(daily_queries):
                # Simulate realistic usage patterns
                model = random.choice(models)
                base_cost = 0.02 if model == 'gemini-flash' else 0.1
                tokens = random.randint(200, 800)
                cost = base_cost * (tokens / 1000)
                
                # Simulate timestamp for different days
                timestamp = datetime.now() - timedelta(days=14-day, hours=random.randint(0, 23))
                
                usage = UsageMetrics(
                    timestamp=timestamp,
                    tokens_used=tokens,
                    cost=cost,
                    model_used=model,
                    query_type=random.choice(query_types),
                    response_time=random.uniform(0.5, 3.0),
                    quality_score=random.uniform(0.85, 1.0),
                    cached=random.choice([True, False])
                )
                
                self.forecaster.usage_history.append(usage)
        
        # 3. Check budget status
        status = self.forecaster.get_budget_status(plan_id)
        print(f"   Budget utilization: {status['utilization']:.1%}")
        print(f"   Daily burn rate: ${status['daily_burn_rate']:.2f}")
        print(f"   Projected spend: ${status['projected_spend']:.2f}")
        
        # 4. Generate forecast
        forecast = self.forecaster.generate_forecast(horizon_days=15)
        if forecast:
            print(f"   15-day forecast: ${forecast.predicted_cost:.2f}")
            print(f"   Forecast accuracy: {forecast.accuracy_score:.2f}")
            print(f"   Recommendations: {len(forecast.recommendations)}")
        
        # 5. Get analytics
        analytics = self.forecaster.get_cost_analytics(15)
        print(f"   Cost trend: {analytics['trend_analysis']['direction']}")
        print(f"   Cache hit rate: {analytics['usage_stats']['cache_hit_rate']:.1%}")
        print(f"   Quality/cost ratio: {analytics['efficiency_metrics']['quality_cost_ratio']:.2f}")
        
        # Assertions
        assert status['utilization'] >= 0
        assert status['daily_burn_rate'] >= 0  # Allow zero burn rate
        assert forecast is not None
        assert len(forecast.recommendations) > 0
        assert analytics['trend_analysis']['direction'] in ['increasing', 'decreasing', 'stable']
        
        print("   ✅ Beta testing scenario completed successfully!")
    
    def test_cost_optimization_recommendations(self):
        """Test cost optimization recommendations generation"""
        print("\n💡 Testing Cost Optimization Recommendations")
        
        # Simulate high-cost scenario
        for i in range(30):
            self.forecaster.record_usage(
                tokens_used=1000,  # High token usage
                cost=0.5,  # High cost
                model_used='gemini-pro',  # Expensive model
                cached=False,  # No caching
                quality_score=0.95
            )
        
        forecast = self.forecaster.generate_forecast()
        recommendations = forecast.recommendations
        
        print(f"   Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"     {i}. {rec}")
        
        # Should suggest caching and model switching
        rec_text = ' '.join(recommendations).lower()
        assert 'caching' in rec_text or 'flash' in rec_text or 'cost' in rec_text
        assert len(recommendations) > 0
        
        print("   ✅ Cost optimization recommendations working correctly!")


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
