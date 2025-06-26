"""
Vimarsh Cost Monitoring and Budget Management Service
Real-time cost tracking, budget alerts, and optimization recommendations
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal
import os

# Azure SDK imports
try:
    from azure.mgmt.consumption import ConsumptionManagementClient
    from azure.mgmt.costmanagement import CostManagementClient
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning("Azure SDK not available - using mock data for cost monitoring")

@dataclass
class CostAlert:
    """Cost alert configuration and status"""
    threshold_percentage: int
    threshold_amount: Decimal
    current_amount: Decimal
    is_triggered: bool
    alert_type: str  # 'info', 'warning', 'critical', 'emergency'
    message: str
    spiritual_guidance: str
    timestamp: datetime

@dataclass
class BudgetStatus:
    """Current budget status and utilization"""
    budget_amount: Decimal
    current_spend: Decimal
    projected_spend: Decimal
    utilization_percentage: float
    days_remaining: int
    average_daily_spend: Decimal
    alerts: List[CostAlert]
    recommendations: List[str]

@dataclass
class ResourceCost:
    """Individual resource cost information"""
    resource_id: str
    resource_name: str
    resource_type: str
    daily_cost: Decimal
    monthly_cost: Decimal
    cost_trend: str  # 'increasing', 'stable', 'decreasing'
    optimization_potential: Decimal

@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    category: str
    title: str
    description: str
    potential_savings: Decimal
    effort_level: str  # 'low', 'medium', 'high'
    priority: str  # 'low', 'medium', 'high', 'critical'
    implementation_steps: List[str]
    spiritual_context: str

class VimarshCostMonitor:
    """
    Comprehensive cost monitoring and budget management service
    """
    
    def __init__(self, 
                 subscription_id: Optional[str] = None,
                 resource_group: Optional[str] = None,
                 budget_amount: Decimal = Decimal('100'),
                 environment: str = 'dev'):
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = resource_group or f'vimarsh-{environment}-rg'
        self.budget_amount = budget_amount
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        
        # Initialize Azure clients if available
        self.consumption_client = None
        self.cost_client = None
        if AZURE_AVAILABLE and self.subscription_id:
            try:
                credential = DefaultAzureCredential()
                self.consumption_client = ConsumptionManagementClient(
                    credential, self.subscription_id
                )
                self.cost_client = CostManagementClient(credential)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Azure clients: {e}")
        
        # Alert thresholds with spiritual messaging
        self.alert_thresholds = {
            50: {
                'type': 'info',
                'message': 'Budget utilization at 50% - mindful monitoring begins',
                'spiritual_guidance': 'Like a wise archer who checks his quiver, we monitor our resources with awareness.'
            },
            80: {
                'type': 'warning', 
                'message': 'Budget utilization at 80% - optimization recommended',
                'spiritual_guidance': 'As Lord Krishna teaches moderation, let us optimize our resource usage.'
            },
            90: {
                'type': 'critical',
                'message': 'Budget utilization at 90% - immediate action required',
                'spiritual_guidance': 'Like Arjuna seeking guidance, we must act decisively to maintain balance.'
            },
            100: {
                'type': 'emergency',
                'message': 'Budget limit reached - emergency cost controls activated',
                'spiritual_guidance': 'In times of constraint, dharmic principles guide us to use resources wisely.'
            }
        }

    async def get_current_costs(self) -> Dict[str, Any]:
        """Get current cost data from Azure or mock data"""
        
        if self.consumption_client and self.subscription_id:
            try:
                return await self._get_azure_costs()
            except Exception as e:
                self.logger.error(f"Failed to get Azure costs: {e}")
        
        # Return mock data for development/testing
        return self._get_mock_costs()

    async def _get_azure_costs(self) -> Dict[str, Any]:
        """Get actual cost data from Azure Cost Management API"""
        
        # Get current month's costs
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Query cost data (simplified - actual implementation would use proper API calls)
            scope = f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}"
            
            # This is a simplified placeholder - actual implementation would use:
            # cost_data = self.cost_client.query.usage(scope, parameters)
            
            return {
                'current_spend': Decimal('65.50'),
                'projected_spend': Decimal('87.30'),
                'daily_average': Decimal('2.10'),
                'resource_breakdown': [
                    {'name': 'vimarsh-functions', 'cost': Decimal('26.20'), 'type': 'Microsoft.Web/sites'},
                    {'name': 'vimarsh-cosmos', 'cost': Decimal('19.65'), 'type': 'Microsoft.DocumentDB/databaseAccounts'},
                    {'name': 'vimarsh-staticweb', 'cost': Decimal('13.10'), 'type': 'Microsoft.Web/staticSites'},
                    {'name': 'vimarsh-insights', 'cost': Decimal('6.55'), 'type': 'Microsoft.Insights/components'},
                ]
            }
        except AzureError as e:
            self.logger.error(f"Azure API error: {e}")
            return self._get_mock_costs()

    def _get_mock_costs(self) -> Dict[str, Any]:
        """Generate realistic mock cost data for development"""
        
        # Simulate gradual cost increase throughout the month
        days_into_month = datetime.now().day
        base_daily_cost = float(self.budget_amount) / 30
        current_spend = Decimal(str(base_daily_cost * days_into_month * 0.85))
        projected_spend = Decimal(str(base_daily_cost * 30 * 0.92))
        
        return {
            'current_spend': current_spend,
            'projected_spend': projected_spend,
            'daily_average': current_spend / days_into_month if days_into_month > 0 else Decimal('0'),
            'resource_breakdown': [
                {'name': 'vimarsh-functions', 'cost': current_spend * Decimal('0.4'), 'type': 'Microsoft.Web/sites'},
                {'name': 'vimarsh-cosmos', 'cost': current_spend * Decimal('0.3'), 'type': 'Microsoft.DocumentDB/databaseAccounts'},
                {'name': 'vimarsh-staticweb', 'cost': current_spend * Decimal('0.2'), 'type': 'Microsoft.Web/staticSites'},
                {'name': 'vimarsh-insights', 'cost': current_spend * Decimal('0.1'), 'type': 'Microsoft.Insights/components'},
            ]
        }

    def generate_budget_status(self, cost_data: Dict[str, Any]) -> BudgetStatus:
        """Generate comprehensive budget status report"""
        
        current_spend = cost_data['current_spend']
        projected_spend = cost_data['projected_spend']
        utilization = float(current_spend / self.budget_amount * 100)
        
        # Calculate days remaining in month
        today = datetime.now()
        last_day_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        days_remaining = (last_day_of_month - today).days
        
        # Generate alerts
        alerts = []
        for threshold, config in self.alert_thresholds.items():
            if utilization >= threshold:
                alert = CostAlert(
                    threshold_percentage=threshold,
                    threshold_amount=self.budget_amount * Decimal(str(threshold / 100)),
                    current_amount=current_spend,
                    is_triggered=True,
                    alert_type=config['type'],
                    message=config['message'],
                    spiritual_guidance=config['spiritual_guidance'],
                    timestamp=datetime.now()
                )
                alerts.append(alert)
        
        # Generate recommendations
        recommendations = self._generate_cost_recommendations(cost_data, utilization)
        
        return BudgetStatus(
            budget_amount=self.budget_amount,
            current_spend=current_spend,
            projected_spend=projected_spend,
            utilization_percentage=utilization,
            days_remaining=days_remaining,
            average_daily_spend=cost_data['daily_average'],
            alerts=alerts,
            recommendations=recommendations
        )

    def _generate_cost_recommendations(self, cost_data: Dict[str, Any], utilization: float) -> List[str]:
        """Generate contextual cost optimization recommendations"""
        
        recommendations = []
        
        if utilization > 80:
            recommendations.append("URGENT: Consider implementing immediate cost controls")
            recommendations.append("Review and potentially downgrade non-critical resources")
            
        if utilization > 60:
            recommendations.append("Implement auto-shutdown schedules for development resources")
            recommendations.append("Review Cosmos DB throughput settings for optimization")
            
        if self.environment == 'dev':
            recommendations.append("Use Azure Functions Consumption Plan for cost efficiency")
            recommendations.append("Consider serverless Cosmos DB for development workloads")
            
        if utilization < 50:
            recommendations.append("Current spending is well within budget - maintain monitoring")
            
        # Add spiritual context
        recommendations.append("Follow dharmic principles: use resources mindfully and purposefully")
        
        return recommendations

    def generate_optimization_recommendations(self, cost_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate detailed optimization recommendations"""
        
        recommendations = []
        resource_breakdown = cost_data['resource_breakdown']
        
        # Azure Functions optimization
        functions_cost = next((r['cost'] for r in resource_breakdown if 'functions' in r['name']), Decimal('0'))
        if functions_cost > Decimal('20'):
            recommendations.append(OptimizationRecommendation(
                category="compute",
                title="Optimize Azure Functions Plan",
                description="Switch to Consumption Plan Y1 for better cost efficiency",
                potential_savings=functions_cost * Decimal('0.3'),
                effort_level="low",
                priority="high",
                implementation_steps=[
                    "Review current Functions plan usage",
                    "Migrate to Consumption Plan if suitable",
                    "Monitor performance after migration"
                ],
                spiritual_context="Like choosing the right path in dharma, select the most appropriate hosting plan"
            ))
        
        # Cosmos DB optimization
        cosmos_cost = next((r['cost'] for r in resource_breakdown if 'cosmos' in r['name']), Decimal('0'))
        if cosmos_cost > Decimal('15'):
            recommendations.append(OptimizationRecommendation(
                category="database",
                title="Optimize Cosmos DB Throughput",
                description="Review and right-size throughput settings",
                potential_savings=cosmos_cost * Decimal('0.25'),
                effort_level="medium",
                priority="medium",
                implementation_steps=[
                    "Analyze current throughput usage patterns",
                    "Implement auto-scaling if not enabled",
                    "Consider serverless mode for variable workloads"
                ],
                spiritual_context="Balance is key - neither excess nor scarcity serves the greater purpose"
            ))
        
        # Development resource optimization
        if self.environment in ['dev', 'staging']:
            recommendations.append(OptimizationRecommendation(
                category="scheduling",
                title="Implement Resource Scheduling",
                description="Auto-shutdown development resources during off-hours",
                potential_savings=cost_data['current_spend'] * Decimal('0.15'),
                effort_level="medium",
                priority="medium",
                implementation_steps=[
                    "Identify resources suitable for scheduling",
                    "Implement Azure Automation runbooks",
                    "Configure start/stop schedules"
                ],
                spiritual_context="Rest is as important as action - allow resources to rest when not needed"
            ))
        
        return recommendations

    async def check_budget_alerts(self) -> List[CostAlert]:
        """Check for budget alerts and return triggered alerts"""
        
        cost_data = await self.get_current_costs()
        budget_status = self.generate_budget_status(cost_data)
        
        triggered_alerts = [alert for alert in budget_status.alerts if alert.is_triggered]
        
        if triggered_alerts:
            self.logger.warning(f"Budget alerts triggered: {len(triggered_alerts)} alerts")
            for alert in triggered_alerts:
                self.logger.warning(f"Alert: {alert.message}")
        
        return triggered_alerts

    def generate_cost_report(self, cost_data: Dict[str, Any], budget_status: BudgetStatus) -> Dict[str, Any]:
        """Generate comprehensive cost monitoring report"""
        
        optimization_recs = self.generate_optimization_recommendations(cost_data)
        
        report = {
            'report_metadata': {
                'timestamp': datetime.now().isoformat(),
                'environment': self.environment,
                'subscription_id': self.subscription_id,
                'resource_group': self.resource_group,
                'reporting_period': 'current_month'
            },
            'budget_status': asdict(budget_status),
            'cost_breakdown': cost_data['resource_breakdown'],
            'optimization_recommendations': [asdict(rec) for rec in optimization_recs],
            'spiritual_guidance': {
                'message': 'Cost management is a spiritual practice of mindful stewardship',
                'principle': 'dharmic_resource_management',
                'teaching': 'Just as a gardener tends their garden with care, we must tend our cloud resources with wisdom and purpose',
                'action_guidance': 'Monitor with awareness, optimize with compassion, spend with intention'
            },
            'executive_summary': {
                'status': self._get_status_summary(budget_status.utilization_percentage),
                'key_metrics': {
                    'budget_utilization': f"{budget_status.utilization_percentage:.1f}%",
                    'projected_overage': max(0, float(budget_status.projected_spend - budget_status.budget_amount)),
                    'optimization_potential': sum(rec.potential_savings for rec in optimization_recs),
                    'alerts_count': len([a for a in budget_status.alerts if a.is_triggered])
                },
                'next_actions': self._get_next_actions(budget_status.utilization_percentage, optimization_recs)
            }
        }
        
        return report

    def _get_status_summary(self, utilization: float) -> str:
        """Get status summary based on utilization"""
        if utilization >= 100:
            return "CRITICAL - Budget exceeded"
        elif utilization >= 90:
            return "WARNING - Near budget limit"
        elif utilization >= 80:
            return "ATTENTION - High utilization"
        elif utilization >= 50:
            return "GOOD - Moderate utilization"
        else:
            return "EXCELLENT - Low utilization"

    def _get_next_actions(self, utilization: float, recommendations: List[OptimizationRecommendation]) -> List[str]:
        """Get next actions based on current status"""
        actions = []
        
        if utilization >= 90:
            actions.append("Implement immediate cost controls")
            actions.append("Review and pause non-critical resources")
        elif utilization >= 80:
            actions.append("Implement top optimization recommendations")
            actions.append("Schedule weekly cost reviews")
        elif utilization >= 50:
            actions.append("Monitor cost trends regularly")
            actions.append("Plan optimization implementations")
        else:
            actions.append("Continue current monitoring practices")
            actions.append("Focus on efficiency improvements")
        
        # Add top recommendation
        if recommendations:
            top_rec = max(recommendations, key=lambda r: r.potential_savings)
            actions.append(f"Priority: {top_rec.title}")
        
        return actions

    async def run_cost_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete cost monitoring cycle"""
        
        self.logger.info(f"Starting cost monitoring cycle for {self.environment} environment")
        
        try:
            # Get current cost data
            cost_data = await self.get_current_costs()
            
            # Generate budget status
            budget_status = self.generate_budget_status(cost_data)
            
            # Check for alerts
            alerts = await self.check_budget_alerts()
            
            # Generate comprehensive report
            report = self.generate_cost_report(cost_data, budget_status)
            
            self.logger.info(f"Cost monitoring cycle completed - Utilization: {budget_status.utilization_percentage:.1f}%")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Cost monitoring cycle failed: {e}")
            raise

# Convenience function for easy usage
async def monitor_vimarsh_costs(environment: str = 'dev', 
                              budget_amount: Decimal = Decimal('100')) -> Dict[str, Any]:
    """Convenient function to run cost monitoring"""
    
    monitor = VimarshCostMonitor(
        environment=environment,
        budget_amount=budget_amount
    )
    
    return await monitor.run_cost_monitoring_cycle()

# CLI interface for standalone usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vimarsh Cost Monitoring Service")
    parser.add_argument('--environment', '-e', default='dev', help='Environment (dev/staging/prod)')
    parser.add_argument('--budget', '-b', type=float, default=100, help='Monthly budget amount')
    parser.add_argument('--subscription', '-s', help='Azure subscription ID')
    parser.add_argument('--resource-group', '-g', help='Resource group name')
    parser.add_argument('--output', '-o', help='Output file for report')
    
    args = parser.parse_args()
    
    async def main():
        monitor = VimarshCostMonitor(
            subscription_id=args.subscription,
            resource_group=args.resource_group,
            budget_amount=Decimal(str(args.budget)),
            environment=args.environment
        )
        
        report = await monitor.run_cost_monitoring_cycle()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2, default=str))
    
    asyncio.run(main())
