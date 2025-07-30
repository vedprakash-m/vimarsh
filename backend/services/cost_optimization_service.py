"""
Cost Optimization Service for Vimarsh
Monitor Gemini API usage, optimize embedding calls, and track costs
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

try:
    from models.vimarsh_models import CostOptimizationMetric, model_to_dict, dict_to_model
    from services.database_service import DatabaseService
    from services.cache_service import CacheService
except ImportError as e:
    logging.warning(f"Import warning in cost_optimization_service: {e}")
    # Mock classes for testing
    CostOptimizationMetric = None

logger = logging.getLogger(__name__)

class CostOptimizationService:
    """Service for monitoring and optimizing API costs"""
    
    def __init__(self):
        """Initialize cost optimization service"""
        self.db_service = DatabaseService()
        self.cache_service = CacheService()
        
        # Local storage for development
        self.local_storage_path = "data/cost_optimization"
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Cost tracking
        self.daily_costs = {}
        self.api_call_counts = {}
        
        # Gemini API pricing (as of 2024)
        self.gemini_pricing = {
            'input_token_cost': 0.000125,   # $0.125 per 1K tokens
            'output_token_cost': 0.000375,  # $0.375 per 1K tokens
            'embedding_cost': 0.0001        # $0.1 per 1K tokens
        }
        
        # Cost thresholds
        self.cost_thresholds = {
            'daily_warning': 5.0,    # $5 per day
            'daily_critical': 10.0,  # $10 per day
            'monthly_warning': 100.0, # $100 per month
            'monthly_critical': 200.0 # $200 per month
        }
        
        logger.info("💰 Cost Optimization Service initialized")
    
    async def track_gemini_api_call(
        self,
        input_tokens: int,
        output_tokens: int,
        call_type: str = "generation"  # "generation" or "embedding"
    ) -> float:
        """Track a Gemini API call and calculate cost"""
        try:
            # Calculate cost based on token usage
            if call_type == "generation":
                cost = (
                    (input_tokens * self.gemini_pricing['input_token_cost'] / 1000) +
                    (output_tokens * self.gemini_pricing['output_token_cost'] / 1000)
                )
            else:  # embedding
                total_tokens = input_tokens + output_tokens
                cost = total_tokens * self.gemini_pricing['embedding_cost'] / 1000
            
            # Track daily costs
            today = datetime.utcnow().strftime('%Y-%m-%d')
            await self._update_daily_cost_tracking(today, call_type, input_tokens, output_tokens, cost)
            
            # Update cache for real-time monitoring
            await self._update_cost_cache(call_type, cost, input_tokens + output_tokens)
            
            logger.debug(f"Tracked Gemini API call: {call_type}, cost: ${cost:.4f}")
            return cost
            
        except Exception as e:
            logger.error(f"Error tracking Gemini API call: {e}")
            return 0.0
    
    async def get_daily_cost_summary(self, date: str = None) -> Dict[str, Any]:
        """Get daily cost summary"""
        try:
            if date is None:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            # Check cache first
            cache_key = f"daily_cost:{date}"
            cached_summary = self.cache_service.get(cache_key)
            
            if cached_summary:
                return cached_summary
            
            # Get cost metric from database or calculate
            cost_metric = await self._get_cost_metric_for_date(date)
            
            if not cost_metric:
                return {
                    'date': date,
                    'total_cost': 0.0,
                    'gemini_cost': 0.0,
                    'embedding_cost': 0.0,
                    'api_calls': 0,
                    'total_tokens': 0,
                    'cost_breakdown': {}
                }
            
            summary = {
                'date': date,
                'total_cost': cost_metric.total_cost_usd,
                'gemini_cost': cost_metric.gemini_cost_usd,
                'embedding_cost': cost_metric.embedding_cost_usd,
                'api_calls': cost_metric.gemini_api_calls + cost_metric.embedding_calls,
                'total_tokens': cost_metric.gemini_input_tokens + cost_metric.gemini_output_tokens + cost_metric.embedding_tokens,
                'cost_breakdown': {
                    'gemini_generation': cost_metric.gemini_cost_usd,
                    'embeddings': cost_metric.embedding_cost_usd
                },
                'cache_efficiency': cost_metric.cache_efficiency,
                'projected_monthly_cost': cost_metric.projected_monthly_cost
            }
            
            # Cache for 1 hour
            self.cache_service.put(cache_key, summary, ttl=3600)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting daily cost summary: {e}")
            return {}
    
    async def get_monthly_cost_projection(self) -> Dict[str, Any]:
        """Get monthly cost projection based on current usage"""
        try:
            # Get last 7 days of cost data
            costs = []
            for i in range(7):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_summary = await self.get_daily_cost_summary(date)
                if daily_summary.get('total_cost', 0) > 0:
                    costs.append(daily_summary['total_cost'])
            
            if not costs:
                return {
                    'projected_monthly_cost': 0.0,
                    'current_daily_average': 0.0,
                    'trend': 'stable',
                    'status': 'within_budget'
                }
            
            # Calculate averages and projections
            daily_average = sum(costs) / len(costs)
            monthly_projection = daily_average * 30
            
            # Determine trend
            if len(costs) >= 3:
                recent_avg = sum(costs[:3]) / 3
                older_avg = sum(costs[3:]) / len(costs[3:]) if len(costs) > 3 else recent_avg
                
                if recent_avg > older_avg * 1.1:
                    trend = 'increasing'
                elif recent_avg < older_avg * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Determine budget status
            if monthly_projection > self.cost_thresholds['monthly_critical']:
                status = 'over_budget'
            elif monthly_projection > self.cost_thresholds['monthly_warning']:
                status = 'approaching_limit'
            else:
                status = 'within_budget'
            
            projection = {
                'projected_monthly_cost': round(monthly_projection, 2),
                'current_daily_average': round(daily_average, 2),
                'trend': trend,
                'status': status,
                'days_analyzed': len(costs),
                'recommendations': self._generate_cost_recommendations(monthly_projection, trend)
            }
            
            logger.info(f"Monthly cost projection: ${monthly_projection:.2f} ({status})")
            return projection
            
        except Exception as e:
            logger.error(f"Error getting monthly cost projection: {e}")
            return {}
    
    async def optimize_embedding_cache(self) -> Dict[str, Any]:
        """Analyze and optimize embedding cache usage"""
        try:
            # Get cache statistics
            cache_stats = await self._get_embedding_cache_stats()
            
            optimization_results = {
                'current_cache_hit_rate': cache_stats.get('hit_rate', 0),
                'potential_savings': 0.0,
                'recommendations': [],
                'cache_efficiency': cache_stats.get('efficiency', 0)
            }
            
            # Calculate potential savings from better caching
            daily_embedding_cost = cache_stats.get('daily_embedding_cost', 0)
            current_hit_rate = cache_stats.get('hit_rate', 0)
            
            # If we could achieve 80% cache hit rate
            target_hit_rate = 0.8
            if current_hit_rate < target_hit_rate:
                potential_savings = daily_embedding_cost * (target_hit_rate - current_hit_rate)
                optimization_results['potential_savings'] = potential_savings * 30  # Monthly
                
                optimization_results['recommendations'].append(
                    f"Improve cache hit rate from {current_hit_rate*100:.1f}% to {target_hit_rate*100}% "
                    f"to save ~${potential_savings*30:.2f}/month"
                )
            
            # Check for cache optimization opportunities
            if cache_stats.get('cache_misses', 0) > cache_stats.get('cache_hits', 0):
                optimization_results['recommendations'].append(
                    "High cache miss rate detected - consider increasing cache TTL or size"
                )
            
            if cache_stats.get('duplicate_queries', 0) > 0:
                optimization_results['recommendations'].append(
                    f"Found {cache_stats['duplicate_queries']} duplicate queries - implement query deduplication"
                )
            
            logger.info(f"Embedding cache optimization completed: {len(optimization_results['recommendations'])} recommendations")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing embedding cache: {e}")
            return {}
    
    async def get_cost_alerts(self) -> List[Dict[str, Any]]:
        """Get cost-related alerts and warnings"""
        try:
            alerts = []
            
            # Check daily cost threshold
            today_summary = await self.get_daily_cost_summary()
            daily_cost = today_summary.get('total_cost', 0)
            
            if daily_cost > self.cost_thresholds['daily_critical']:
                alerts.append({
                    'type': 'critical',
                    'category': 'daily_cost',
                    'message': f"Daily cost ${daily_cost:.2f} exceeds critical threshold ${self.cost_thresholds['daily_critical']}",
                    'recommended_action': 'Immediate cost reduction required'
                })
            elif daily_cost > self.cost_thresholds['daily_warning']:
                alerts.append({
                    'type': 'warning',
                    'category': 'daily_cost',
                    'message': f"Daily cost ${daily_cost:.2f} exceeds warning threshold ${self.cost_thresholds['daily_warning']}",
                    'recommended_action': 'Monitor usage closely'
                })
            
            # Check monthly projection
            monthly_projection = await self.get_monthly_cost_projection()
            projected_cost = monthly_projection.get('projected_monthly_cost', 0)
            
            if projected_cost > self.cost_thresholds['monthly_critical']:
                alerts.append({
                    'type': 'critical',
                    'category': 'monthly_projection',
                    'message': f"Projected monthly cost ${projected_cost:.2f} exceeds budget",
                    'recommended_action': 'Implement cost optimization strategies'
                })
            elif projected_cost > self.cost_thresholds['monthly_warning']:
                alerts.append({
                    'type': 'warning',
                    'category': 'monthly_projection',
                    'message': f"Projected monthly cost ${projected_cost:.2f} approaching limit",
                    'recommended_action': 'Review usage patterns'
                })
            
            # Check for unusual cost spikes
            cost_spike_alert = await self._check_cost_spikes()
            if cost_spike_alert:
                alerts.append(cost_spike_alert)
            
            logger.info(f"Generated {len(alerts)} cost alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting cost alerts: {e}")
            return []
    
    async def generate_cost_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive cost optimization report"""
        try:
            # Get current cost data
            daily_summary = await self.get_daily_cost_summary()
            monthly_projection = await self.get_monthly_cost_projection()
            cache_optimization = await self.optimize_embedding_cache()
            alerts = await self.get_cost_alerts()
            
            # Calculate cost efficiency metrics
            efficiency_metrics = await self._calculate_cost_efficiency()
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'current_costs': {
                    'daily': daily_summary,
                    'monthly_projection': monthly_projection
                },
                'optimization_opportunities': cache_optimization,
                'efficiency_metrics': efficiency_metrics,
                'alerts': alerts,
                'recommendations': self._generate_comprehensive_recommendations(
                    daily_summary, monthly_projection, cache_optimization
                ),
                'cost_breakdown': await self._get_detailed_cost_breakdown()
            }
            
            logger.info("Generated comprehensive cost optimization report")
            return report
            
        except Exception as e:
            logger.error(f"Error generating cost optimization report: {e}")
            return {}
    
    # Private helper methods
    
    async def _update_daily_cost_tracking(
        self,
        date: str,
        call_type: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ):
        """Update daily cost tracking"""
        try:
            # Get or create daily cost metric
            cost_metric = await self._get_cost_metric_for_date(date)
            
            if not cost_metric:
                cost_metric = CostOptimizationMetric(
                    id=f"cost_{date}",
                    date=date
                )
            
            # Update metrics based on call type
            if call_type == "generation":
                cost_metric.gemini_api_calls += 1
                cost_metric.gemini_input_tokens += input_tokens
                cost_metric.gemini_output_tokens += output_tokens
                cost_metric.gemini_cost_usd += cost
            else:  # embedding
                cost_metric.embedding_calls += 1
                cost_metric.embedding_tokens += input_tokens + output_tokens
                cost_metric.embedding_cost_usd += cost
            
            # Update totals and projections
            cost_metric.total_cost_usd = cost_metric.gemini_cost_usd + cost_metric.embedding_cost_usd
            cost_metric.projected_monthly_cost = cost_metric.total_cost_usd * 30
            
            # Save updated metric
            await self._save_cost_metric(cost_metric)
            
        except Exception as e:
            logger.error(f"Error updating daily cost tracking: {e}")
    
    async def _get_cost_metric_for_date(self, date: str):
        """Get cost metric for a specific date"""
        try:
            if hasattr(self.db_service, 'get_cost_metric'):
                cost_data = await self.db_service.get_cost_metric(date)
                if cost_data:
                    return dict_to_model(cost_data, CostOptimizationMetric)
        except Exception as e:
            logger.warning(f"Database unavailable: {e}")
        
        return self._get_cost_metric_local(date)
    
    def _get_cost_metric_local(self, date: str):
        """Get cost metric from local storage"""
        try:
            metric_file = os.path.join(self.local_storage_path, f"{date}.json")
            if os.path.exists(metric_file):
                with open(metric_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return dict_to_model(data, CostOptimizationMetric)
        except Exception as e:
            logger.warning(f"Error reading local cost metric: {e}")
        
        return None
    
    def _generate_cost_recommendations(self, monthly_projection: float, trend: str) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        if monthly_projection > self.cost_thresholds['monthly_critical']:
            recommendations.extend([
                "URGENT: Implement API call throttling",
                "Enable aggressive response caching",
                "Consider reducing response length limits",
                "Review and optimize embedding generation frequency"
            ])
        elif monthly_projection > self.cost_thresholds['monthly_warning']:
            recommendations.extend([
                "Implement smart caching for frequently asked questions",
                "Optimize prompt engineering to reduce token usage",
                "Consider implementing rate limiting for users"
            ])
        
        if trend == 'increasing':
            recommendations.append("Cost trend is increasing - monitor usage patterns closely")
        
        return recommendations

# Global service instance
cost_optimization_service = CostOptimizationService()
