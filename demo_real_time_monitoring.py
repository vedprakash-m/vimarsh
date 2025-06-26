"""
Demo Script for Real-time Cost Monitoring and Budget Alert System
Task 8.6: Enhanced Azure Infrastructure & Production Readiness

This script demonstrates the real-time cost monitoring system with:
- Real-time cost tracking and threshold monitoring
- Budget alert scenarios with spiritual messaging
- Integration with existing cost management systems
- Automated budget enforcement actions
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import random
import time

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from backend.cost_management.real_time_monitor import (
        RealTimeCostMonitor,
        BudgetThreshold,
        AlertLevel,
        CostMetricType,
        MonitoringAction,
        track_cost
    )
except ImportError:
    logger.error("Could not import real-time monitor. Running from project root?")
    exit(1)


class RealTimeMonitoringDemo:
    """Demo class for real-time cost monitoring"""
    
    def __init__(self):
        """Initialize demo"""
        self.demo_dir = Path("data/real_time_demo")
        self.demo_dir.mkdir(exist_ok=True)
        
        # Initialize monitor with demo config
        config_path = self.demo_dir / "demo_config.json"
        self.monitor = RealTimeCostMonitor(config_path=str(config_path))
        
        # Demo state
        self.demo_users = ["beta_user_1", "beta_user_2", "beta_user_3", "vip_user"]
        self.demo_models = ["gemini-pro", "gemini-flash"]
        self.demo_operations = ["spiritual_chat", "voice_guidance", "text_analysis", "citation_search"]
        
        self.alerts_received = []
        self.actions_taken = []
        
        # Register callbacks
        self.monitor.register_alert_callback(self._demo_alert_callback)
        self.monitor.register_action_callback(MonitoringAction.NOTIFY_ADMIN, self._demo_admin_action)
        self.monitor.register_action_callback(MonitoringAction.ENABLE_CACHING, self._demo_caching_action)
        self.monitor.register_action_callback(MonitoringAction.SWITCH_MODEL, self._demo_model_switch_action)
        
        logger.info("🕉️ Real-time Cost Monitoring Demo initialized")
    
    async def _demo_alert_callback(self, alert):
        """Demo alert callback"""
        self.alerts_received.append(alert)
        print(f"\n🚨 ALERT RECEIVED:")
        print(f"   Type: {alert.metric_type.value}")
        print(f"   Level: {alert.alert_level.value}")
        print(f"   Current: ${alert.current_value:.2f}")
        print(f"   Threshold: ${alert.threshold_value:.2f}")
        print(f"   Message: {alert.message}")
        print(f"   🙏 Spiritual Guidance: {alert.spiritual_message}")
        print(f"   Actions: {', '.join(alert.actions_taken)}")
    
    async def _demo_admin_action(self, alert):
        """Demo admin notification action"""
        self.actions_taken.append("admin_notified")
        print(f"📧 Admin notified about {alert.alert_level.value} alert")
    
    async def _demo_caching_action(self, alert):
        """Demo caching action"""
        self.actions_taken.append("caching_enabled")
        print(f"⚡ Aggressive caching enabled to reduce costs")
    
    async def _demo_model_switch_action(self, alert):
        """Demo model switching action"""
        self.actions_taken.append("model_switched")
        print(f"🔄 Switched to lower-cost model (Gemini Flash)")
    
    def create_demo_thresholds(self):
        """Create demo-specific thresholds"""
        print("\n🔧 Setting up demo budget thresholds...")
        
        # Low thresholds for demo purposes
        demo_thresholds = [
            BudgetThreshold(
                metric_type=CostMetricType.TOTAL_COST,
                threshold_value=0.50,  # $0.50 total
                alert_level=AlertLevel.INFO,
                actions=[MonitoringAction.LOG_ONLY],
                notification_channels=["console"],
                spiritual_message="🌱 Resources are being used - awareness is the first step to wisdom",
                cooldown_minutes=1
            ),
            BudgetThreshold(
                metric_type=CostMetricType.TOTAL_COST,
                threshold_value=1.00,  # $1.00 total
                alert_level=AlertLevel.WARNING,
                actions=[MonitoringAction.NOTIFY_ADMIN, MonitoringAction.ENABLE_CACHING],
                notification_channels=["console", "application_insights"],
                spiritual_message="⚠️ The wise sage monitors resources like a caring gardener",
                cooldown_minutes=2
            ),
            BudgetThreshold(
                metric_type=CostMetricType.TOTAL_COST,
                threshold_value=2.00,  # $2.00 total
                alert_level=AlertLevel.CRITICAL,
                actions=[MonitoringAction.NOTIFY_ADMIN, MonitoringAction.SWITCH_MODEL, MonitoringAction.THROTTLE_REQUESTS],
                notification_channels=["console", "application_insights", "email"],
                spiritual_message="🔥 Even Lord Krishna teaches balance - moderation in all things",
                cooldown_minutes=1
            ),
            BudgetThreshold(
                metric_type=CostMetricType.HOURLY_RATE,
                threshold_value=0.25,  # $0.25/hour
                alert_level=AlertLevel.WARNING,
                actions=[MonitoringAction.LOG_ONLY, MonitoringAction.NOTIFY_ADMIN],
                notification_channels=["console"],
                spiritual_message="⏰ Time flows like the Ganges - observe its passage mindfully",
                cooldown_minutes=5
            ),
            BudgetThreshold(
                metric_type=CostMetricType.USER_COST,
                threshold_value=0.75,  # $0.75 per user
                alert_level=AlertLevel.WARNING,
                actions=[MonitoringAction.LOG_ONLY],
                notification_channels=["console"],
                spiritual_message="👤 Each soul's journey has its own pace - monitor with compassion",
                cooldown_minutes=3
            )
        ]
        
        # Clear existing thresholds and add demo ones
        self.monitor.thresholds = demo_thresholds
        self.monitor._save_config()
        
        print(f"✅ Created {len(demo_thresholds)} demo thresholds")
        for threshold in demo_thresholds:
            print(f"   - {threshold.metric_type.value}: ${threshold.threshold_value:.2f} ({threshold.alert_level.value})")
    
    async def simulate_usage_patterns(self):
        """Simulate realistic usage patterns"""
        print("\n📊 Simulating realistic usage patterns...")
        
        # Simulate different cost scenarios
        scenarios = [
            ("Light usage", 0.05, 0.15),
            ("Normal usage", 0.15, 0.35),
            ("Heavy usage", 0.35, 0.65),
            ("Cost spike", 0.65, 1.25)
        ]
        
        for scenario_name, min_cost, max_cost in scenarios:
            print(f"\n🎭 Scenario: {scenario_name}")
            
            # Generate random operations
            for _ in range(random.randint(3, 8)):
                user = random.choice(self.demo_users)
                model = random.choice(self.demo_models)
                operation = random.choice(self.demo_operations)
                
                # Cost varies by model and operation
                base_cost = random.uniform(min_cost, max_cost)
                if model == "gemini-pro":
                    base_cost *= 1.5  # Pro model costs more
                if operation == "voice_guidance":
                    base_cost *= 1.3  # Voice processing costs more
                
                self.monitor.update_cost(user, model, operation, base_cost)
                
                print(f"   💰 {user} used {model} for {operation}: ${base_cost:.3f}")
                
                # Small delay to spread out costs
                await asyncio.sleep(0.1)
            
            # Show current status
            metrics = self.monitor.get_current_metrics()
            print(f"   📈 Total cost so far: ${metrics['costs']['total']:.2f}")
            print(f"   🔔 Active alerts: {metrics['active_alerts']}")
            
            await asyncio.sleep(0.5)
    
    @track_cost(user_id="demo_user", model="gemini-pro", operation="demo_operation")
    async def demo_tracked_function(self, work_duration: float = 0.1):
        """Demo function with cost tracking decorator"""
        print(f"🔧 Executing tracked function (duration: {work_duration:.1f}s)")
        await asyncio.sleep(work_duration)
        return f"Work completed in {work_duration:.1f}s"
    
    async def demonstrate_decorator_usage(self):
        """Demonstrate cost tracking decorator"""
        print("\n🎯 Demonstrating automatic cost tracking with decorators...")
        
        # Execute functions with different work loads
        work_loads = [0.05, 0.15, 0.25, 0.35]
        
        for duration in work_loads:
            result = await self.demo_tracked_function(duration)
            print(f"   ✅ {result}")
            await asyncio.sleep(0.2)
    
    async def demonstrate_real_time_monitoring(self):
        """Demonstrate real-time monitoring"""
        print("\n🚀 Starting real-time monitoring demonstration...")
        
        # Start monitoring with short interval for demo
        await self.monitor.start_monitoring(interval_seconds=2)
        print("   ⚡ Real-time monitoring started (2-second intervals)")
        
        # Let it run for a bit
        print("   ⏳ Monitoring for 10 seconds...")
        await asyncio.sleep(10)
        
        # Show monitoring activity
        metrics = self.monitor.get_current_metrics()
        print(f"   📊 Current metrics: {json.dumps(metrics, indent=2, default=str)}")
        
        # Stop monitoring
        await self.monitor.stop_monitoring()
        print("   🛑 Real-time monitoring stopped")
    
    def demonstrate_alert_history(self):
        """Demonstrate alert history and analytics"""
        print("\n📚 Alert History and Analytics:")
        
        # Show recent alerts
        recent_alerts = self.monitor.get_alert_history(limit=5)
        print(f"   📋 Recent alerts ({len(recent_alerts)}):")
        
        for i, alert in enumerate(recent_alerts[-3:], 1):  # Last 3 alerts
            print(f"      {i}. {alert['alert_level']} - {alert['message']}")
            print(f"         🙏 {alert['spiritual_message']}")
        
        # Show active alerts
        active_alerts = self.monitor.get_active_alerts()
        print(f"   🔴 Active alerts: {len(active_alerts)}")
        
        # Show callback statistics
        print(f"   📈 Demo Statistics:")
        print(f"      - Alerts received: {len(self.alerts_received)}")
        print(f"      - Actions taken: {len(self.actions_taken)}")
        print(f"      - Action types: {set(self.actions_taken)}")
    
    def demonstrate_threshold_management(self):
        """Demonstrate threshold management"""
        print("\n🎛️ Threshold Management:")
        
        current_thresholds = len(self.monitor.thresholds)
        print(f"   📊 Current thresholds: {current_thresholds}")
        
        # Add a new threshold
        new_threshold = BudgetThreshold(
            metric_type=CostMetricType.MONTHLY_BUDGET,
            threshold_value=25.0,
            alert_level=AlertLevel.CRITICAL,
            actions=[MonitoringAction.NOTIFY_ADMIN, MonitoringAction.BLOCK_EXPENSIVE_OPERATIONS],
            notification_channels=["email"],
            spiritual_message="🌙 The monthly cycle completes - reflection brings wisdom",
            cooldown_minutes=60
        )
        
        self.monitor.add_threshold(new_threshold)
        print(f"   ✅ Added monthly budget threshold: ${new_threshold.threshold_value}")
        print(f"   📊 Total thresholds now: {len(self.monitor.thresholds)}")
        
        # Remove the threshold
        self.monitor.remove_threshold(CostMetricType.MONTHLY_BUDGET, 25.0)
        print(f"   🗑️ Removed monthly threshold")
        print(f"   📊 Back to {len(self.monitor.thresholds)} thresholds")
    
    async def run_complete_demo(self):
        """Run complete demo sequence"""
        print("🕉️" + "="*60)
        print("   VIMARSH REAL-TIME COST MONITORING DEMO")
        print("   Task 8.6: Enhanced Azure Infrastructure & Production Readiness")
        print("="*62)
        
        try:
            # Setup
            self.create_demo_thresholds()
            
            # Demonstrate features
            await self.simulate_usage_patterns()
            await self.demonstrate_decorator_usage()
            await self.demonstrate_real_time_monitoring()
            
            self.demonstrate_alert_history()
            self.demonstrate_threshold_management()
            
            # Final summary
            print("\n🎉 Demo Summary:")
            final_metrics = self.monitor.get_current_metrics()
            print(f"   💰 Total cost accumulated: ${final_metrics['costs']['total']:.2f}")
            print(f"   🔔 Total alerts triggered: {len(self.alerts_received)}")
            print(f"   ⚡ Actions executed: {len(self.actions_taken)}")
            print(f"   📊 Monitoring active: {final_metrics['monitoring_active']}")
            
            # Show spiritual messages from alerts
            if self.alerts_received:
                print(f"\n🙏 Spiritual Guidance Received:")
                for alert in self.alerts_received[-3:]:  # Last 3 alerts
                    print(f"   - {alert.spiritual_message}")
            
            print("\n✅ Real-time Cost Monitoring Demo completed successfully!")
            print("🌟 System ready for production deployment with comprehensive cost control")
            
        except Exception as e:
            logger.error(f"Demo error: {e}")
            raise
        
        finally:
            # Cleanup
            if self.monitor.is_monitoring:
                await self.monitor.stop_monitoring()


async def main():
    """Main demo function"""
    demo = RealTimeMonitoringDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
