#!/usr/bin/env python3
"""
Demo Script: AI Cost Forecasting and Budget Planning Tools
Task 7.8: Enhanced AI Cost Management & Dynamic Fallbacks

This demo showcases the comprehensive cost forecasting and budget planning
capabilities for the Vimarsh AI platform, designed for beta testing cost control.

Features demonstrated:
- Usage tracking and analytics
- Cost forecasting with multiple models
- Budget planning and monitoring
- Cost optimization recommendations
- Beta testing scenarios
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random
import json
from pathlib import Path

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from cost_management.cost_forecaster import (
    CostForecaster,
    ForecastModel,
    BudgetPeriod,
    with_cost_tracking,
    get_cost_forecaster
)


class CostForecastingDemo:
    """Demo class for cost forecasting and budget planning"""
    
    def __init__(self):
        """Initialize demo"""
        self.demo_data_path = Path("demo_data/cost_forecasting")
        self.demo_data_path.mkdir(parents=True, exist_ok=True)
        self.forecaster = CostForecaster(storage_path=str(self.demo_data_path))
        
        print("🕉️ Vimarsh AI Cost Forecasting and Budget Planning Demo")
        print("=" * 70)
        print("Namaste! Welcome to the divine wisdom of cost management.")
        print("Like Krishna taught Arjuna about dharma, we shall learn about fiscal discipline.")
        print()
    
    def generate_sample_data(self, days: int = 30):
        """Generate realistic sample usage data"""
        print(f"📊 Generating {days} days of sample usage data...")
        
        models = [
            ('gemini-pro', 0.0005, 0.0015),    # Input cost, output cost per token
            ('gemini-flash', 0.0001, 0.0003)   # Cheaper model
        ]
        
        query_types = [
            ('spiritual_guidance', 0.6),  # 60% spiritual queries
            ('general_question', 0.3),    # 30% general queries
            ('complex_analysis', 0.1)     # 10% complex queries
        ]
        
        # Simulate realistic usage patterns
        for day in range(days):
            # Weekend vs weekday patterns
            is_weekend = (day % 7) in [5, 6]
            base_queries = 20 if is_weekend else 50
            daily_queries = random.randint(base_queries, base_queries + 30)
            
            for query in range(daily_queries):
                # Select model (gradually shift to cheaper model over time)
                if day < 10:
                    model_choice = random.choices(models, weights=[0.8, 0.2])[0]
                else:
                    model_choice = random.choices(models, weights=[0.4, 0.6])[0]
                
                model_name, input_cost, output_cost = model_choice
                
                # Select query type
                query_type = random.choices(
                    [qt[0] for qt in query_types],
                    weights=[qt[1] for qt in query_types]
                )[0]
                
                # Generate realistic token usage
                if query_type == 'spiritual_guidance':
                    input_tokens = random.randint(100, 400)
                    output_tokens = random.randint(200, 600)
                elif query_type == 'complex_analysis':
                    input_tokens = random.randint(300, 800)
                    output_tokens = random.randint(400, 1000)
                else:
                    input_tokens = random.randint(50, 200)
                    output_tokens = random.randint(100, 300)
                
                total_tokens = input_tokens + output_tokens
                cost = (input_tokens * input_cost) + (output_tokens * output_cost)
                
                # Simulate caching (improves over time)
                cache_probability = min(0.4, day * 0.02)  # Increases to 40% over time
                cached = random.random() < cache_probability
                if cached:
                    cost = 0.0  # Cached queries are free
                
                # Quality varies by model and query type
                base_quality = 0.95 if model_name == 'gemini-pro' else 0.90
                if query_type == 'spiritual_guidance':
                    quality_score = base_quality + random.uniform(-0.05, 0.05)
                else:
                    quality_score = base_quality + random.uniform(-0.10, 0.05)
                
                quality_score = max(0.7, min(1.0, quality_score))
                
                # Simulate timestamp
                timestamp = datetime.now() - timedelta(
                    days=days-day-1,
                    hours=random.randint(6, 22),  # Active hours
                    minutes=random.randint(0, 59)
                )
                
                # Record usage
                self.forecaster.record_usage(
                    tokens_used=total_tokens,
                    cost=cost,
                    model_used=model_name,
                    query_type=query_type,
                    response_time=random.uniform(0.5, 3.0),
                    quality_score=quality_score,
                    cached=cached
                )
        
        print(f"   ✅ Generated {len(self.forecaster.usage_history)} usage records")
        print()
    
    def demonstrate_usage_analytics(self):
        """Demonstrate usage analytics"""
        print("📈 Usage Analytics Dashboard")
        print("-" * 40)
        
        stats = self.forecaster.get_usage_stats(30)
        
        print(f"📊 30-Day Usage Summary:")
        print(f"   Total Cost: ${stats['total_cost']:.2f}")
        print(f"   Total Tokens: {stats['total_tokens']:,}")
        print(f"   Total Queries: {stats['total_queries']:,}")
        print(f"   Avg Cost/Query: ${stats['avg_cost_per_query']:.4f}")
        print(f"   Avg Tokens/Query: {stats['avg_tokens_per_query']:.0f}")
        print(f"   Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
        print(f"   Avg Quality Score: {stats['avg_quality_score']:.3f}")
        print()
        
        print("💰 Cost Breakdown by Model:")
        for model, cost in stats['cost_by_model'].items():
            percentage = (cost / stats['total_cost'] * 100) if stats['total_cost'] > 0 else 0
            print(f"   {model}: ${cost:.2f} ({percentage:.1f}%)")
        print()
        
        # Show daily cost trend
        daily_costs = list(stats['cost_by_day'].values())
        if len(daily_costs) >= 7:
            recent_avg = sum(daily_costs[-7:]) / 7
            older_avg = sum(daily_costs[:-7]) / len(daily_costs[:-7]) if len(daily_costs) > 7 else recent_avg
            
            if recent_avg > older_avg * 1.1:
                trend = "📈 Increasing"
            elif recent_avg < older_avg * 0.9:
                trend = "📉 Decreasing"
            else:
                trend = "➡️ Stable"
            
            print(f"📊 Cost Trend: {trend}")
            print(f"   Recent 7-day avg: ${recent_avg:.2f}/day")
            print(f"   Earlier period avg: ${older_avg:.2f}/day")
            print()
    
    def demonstrate_forecasting(self):
        """Demonstrate cost forecasting"""
        print("🔮 Cost Forecasting")
        print("-" * 40)
        
        # Test different forecasting models
        models = [
            ForecastModel.LINEAR_TREND,
            ForecastModel.MOVING_AVERAGE,
            ForecastModel.EXPONENTIAL_SMOOTHING
        ]
        
        forecasts = {}
        
        print("📊 Generating forecasts with different models:")
        for model in models:
            forecast = self.forecaster.generate_forecast(horizon_days=30, model=model)
            if forecast:
                forecasts[model.value] = forecast
                print(f"   {model.value.title()}: ${forecast.predicted_cost:.2f} (accuracy: {forecast.accuracy_score:.2f})")
        
        print()
        
        # Show best forecast
        if forecasts:
            best_model = max(forecasts.keys(), key=lambda k: forecasts[k].accuracy_score)
            best_forecast = forecasts[best_model]
            
            print(f"🎯 Best Forecast ({best_model.title()}):")
            print(f"   Predicted 30-day cost: ${best_forecast.predicted_cost:.2f}")
            print(f"   Confidence interval: ${best_forecast.confidence_interval[0]:.2f} - ${best_forecast.confidence_interval[1]:.2f}")
            print(f"   Accuracy score: {best_forecast.accuracy_score:.2f}")
            print()
            
            print("💡 Key Factors:")
            for factor, value in best_forecast.factors.items():
                if isinstance(value, float):
                    print(f"   {factor.replace('_', ' ').title()}: {value:.3f}")
                else:
                    print(f"   {factor.replace('_', ' ').title()}: {value}")
            print()
            
            print("📋 Recommendations:")
            for i, rec in enumerate(best_forecast.recommendations, 1):
                print(f"   {i}. {rec}")
            print()
    
    def demonstrate_budget_planning(self):
        """Demonstrate budget planning"""
        print("💰 Budget Planning and Monitoring")
        print("-" * 40)
        
        # Create multiple budget scenarios
        scenarios = [
            ("Conservative Beta", 50.0, BudgetPeriod.MONTHLY),
            ("Standard Beta", 100.0, BudgetPeriod.MONTHLY),
            ("Aggressive Beta", 200.0, BudgetPeriod.MONTHLY)
        ]
        
        plan_statuses = []
        
        for name, budget, period in scenarios:
            # Create budget plan
            plan_id = self.forecaster.create_budget_plan(
                name=name,
                period=period,
                total_budget=budget,
                duration_days=30,
                alerts={
                    'early_warning': 0.5,
                    'warning': 0.75,
                    'critical': 0.90,
                    'emergency': 0.95
                }
            )
            
            # Get status
            status = self.forecaster.get_budget_status(plan_id)
            plan_statuses.append((name, status))
            
            print(f"📊 {name} (${budget}/month):")
            print(f"   Current spend: ${status['current_spend']:.2f}")
            print(f"   Utilization: {status['utilization']:.1%}")
            print(f"   Days remaining: {status['days_remaining']}")
            print(f"   Daily burn rate: ${status['daily_burn_rate']:.2f}")
            print(f"   Projected total: ${status['projected_spend']:.2f}")
            
            if status['active_alerts']:
                print(f"   🚨 Active alerts:")
                for alert in status['active_alerts']:
                    print(f"     • {alert['type'].title()}: {alert['message']}")
            else:
                print(f"   ✅ No alerts")
            print()
        
        # Recommend best budget
        print("🎯 Budget Recommendation:")
        for name, status in plan_statuses:
            utilization = status['utilization']
            if 0.6 <= utilization <= 0.8:  # Sweet spot
                print(f"   ✅ {name} appears optimal (utilization: {utilization:.1%})")
            elif utilization < 0.5:
                print(f"   💸 {name} may be too generous (utilization: {utilization:.1%})")
            elif utilization > 0.9:
                print(f"   🚨 {name} is too tight (utilization: {utilization:.1%})")
        print()
    
    def demonstrate_cost_analytics(self):
        """Demonstrate comprehensive cost analytics"""
        print("📊 Comprehensive Cost Analytics")
        print("-" * 40)
        
        analytics = self.forecaster.get_cost_analytics(30)
        
        # Usage stats
        usage = analytics['usage_stats']
        print(f"📈 Usage Overview:")
        print(f"   Total cost: ${usage['total_cost']:.2f}")
        print(f"   Query volume: {usage['total_queries']:,}")
        print(f"   Cache efficiency: {usage['cache_hit_rate']:.1%}")
        print()
        
        # Trend analysis
        trend = analytics['trend_analysis']
        print(f"📊 Trend Analysis:")
        print(f"   Cost direction: {trend['direction'].title()}")
        if trend['peak_cost_day']:
            print(f"   Peak cost day: {trend['peak_cost_day'][0]} (${trend['peak_cost_day'][1]:.2f})")
        if trend['lowest_cost_day']:
            print(f"   Lowest cost day: {trend['lowest_cost_day'][0]} (${trend['lowest_cost_day'][1]:.2f})")
        print()
        
        # Efficiency metrics
        efficiency = analytics['efficiency_metrics']
        print(f"⚡ Efficiency Metrics:")
        print(f"   Cost per token: ${efficiency['cost_per_token']:.6f}")
        print(f"   Cache savings: ${efficiency['cache_savings']:.2f}")
        print(f"   Quality/cost ratio: {efficiency['quality_cost_ratio']:.2f}")
        print()
        
        # Forecast summary
        if analytics['forecast']:
            forecast = analytics['forecast']
            print(f"🔮 Forecast Summary:")
            print(f"   30-day prediction: ${forecast['predicted_cost']:.2f}")
            print(f"   Model used: {forecast['model_used'].title()}")
            print(f"   Confidence: {forecast['accuracy_score']:.1%}")
            print()
    
    def demonstrate_beta_testing_scenario(self):
        """Demonstrate complete beta testing cost management"""
        print("🧪 Beta Testing Cost Management Scenario")
        print("-" * 40)
        
        print("🎯 Scenario: 30-day beta testing with $100 budget")
        print("   Goal: Control costs while maintaining quality spiritual guidance")
        print()
        
        # Create beta budget
        beta_plan_id = self.forecaster.create_budget_plan(
            name="Vimarsh Beta Testing",
            period=BudgetPeriod.MONTHLY,
            total_budget=100.0,
            allocated_budgets={
                'llm_costs': 75.0,      # 75% for AI costs
                'infrastructure': 15.0,  # 15% for Azure services
                'monitoring': 5.0,       # 5% for monitoring
                'contingency': 5.0       # 5% buffer
            },
            alerts={
                'daily_check': 0.5,      # Check at 50%
                'warning': 0.75,         # Warning at 75%
                'urgent': 0.90,          # Urgent at 90%
                'emergency': 0.95        # Emergency at 95%
            }
        )
        
        status = self.forecaster.get_budget_status(beta_plan_id)
        
        print(f"💰 Current Budget Status:")
        print(f"   Allocated budget: ${status['total_budget']}")
        print(f"   Current spend: ${status['current_spend']:.2f}")
        print(f"   Remaining: ${status['remaining_budget']:.2f}")
        print(f"   Utilization: {status['utilization']:.1%}")
        print(f"   Burn rate: ${status['daily_burn_rate']:.2f}/day")
        print()
        
        # Generate forecast for remaining period
        forecast = self.forecaster.generate_forecast(horizon_days=status['days_remaining'])
        if forecast:
            print(f"🔮 Forecast for remaining {status['days_remaining']} days:")
            print(f"   Predicted cost: ${forecast.predicted_cost:.2f}")
            
            total_projected = status['current_spend'] + forecast.predicted_cost
            if total_projected > status['total_budget']:
                overage = total_projected - status['total_budget']
                print(f"   ⚠️ Potential overage: ${overage:.2f}")
                print(f"   🎯 Recommended actions:")
                for rec in forecast.recommendations:
                    print(f"     • {rec}")
            else:
                remaining_after_forecast = status['total_budget'] - total_projected
                print(f"   ✅ Projected to stay within budget")
                print(f"   💰 Expected remaining: ${remaining_after_forecast:.2f}")
            print()
        
        # Cost optimization recommendations
        print("💡 Divine Wisdom for Cost Optimization:")
        print("   🕉️ Like Krishna's teachings on moderation, balance cost and quality")
        print("   📿 Use caching wisely - repetition brings enlightenment at no extra cost")
        print("   ⚡ Choose models mindfully - Gemini Flash for simple, Pro for complex")
        print("   🧘‍♂️ Monitor usage patterns - awareness leads to optimization")
        print("   🌸 Set alerts early - prevention is better than correction")
        print()
    
    def save_demo_results(self):
        """Save demo results for analysis"""
        print("💾 Saving Demo Results")
        print("-" * 40)
        
        # Generate comprehensive report
        analytics = self.forecaster.get_cost_analytics(30)
        forecast = self.forecaster.generate_forecast(30)
        
        report = {
            'demo_date': datetime.now().isoformat(),
            'analytics': analytics,
            'forecast': forecast.to_dict() if forecast else None,
            'usage_summary': {
                'total_records': len(self.forecaster.usage_history),
                'date_range': {
                    'start': min(u.timestamp for u in self.forecaster.usage_history).isoformat() if self.forecaster.usage_history else None,
                    'end': max(u.timestamp for u in self.forecaster.usage_history).isoformat() if self.forecaster.usage_history else None
                }
            },
            'budget_plans': {plan_id: plan.to_dict() for plan_id, plan in self.forecaster.budget_plans.items()}
        }
        
        # Save to file
        report_file = self.demo_data_path / "cost_forecasting_demo_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   📊 Demo report saved to: {report_file}")
        print(f"   📈 Analytics dashboard available")
        print(f"   💰 Budget plans exported")
        print("   ✅ All demo data preserved for analysis")
        print()


async def main():
    """Run the complete cost forecasting demo"""
    demo = CostForecastingDemo()
    
    try:
        # 1. Generate sample data
        demo.generate_sample_data(days=30)
        
        # 2. Demonstrate usage analytics
        demo.demonstrate_usage_analytics()
        
        # 3. Demonstrate forecasting
        demo.demonstrate_forecasting()
        
        # 4. Demonstrate budget planning
        demo.demonstrate_budget_planning()
        
        # 5. Demonstrate cost analytics
        demo.demonstrate_cost_analytics()
        
        # 6. Demonstrate beta testing scenario
        demo.demonstrate_beta_testing_scenario()
        
        # 7. Save results
        demo.save_demo_results()
        
        print("🙏 Demo completed successfully!")
        print("May this cost forecasting wisdom guide Vimarsh to prosperity!")
        print("Om Shanti Shanti Shanti 🕉️")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
