"""
Tests for Real-time Cost Monitoring and Budget Alert System
Task 8.6: Enhanced Azure Infrastructure & Production Readiness
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
from unittest.mock import AsyncMock, MagicMock, patch
from collections import defaultdict

from backend.cost_management.real_time_monitor import (
    RealTimeCostMonitor,
    BudgetThreshold,
    CostAlert,
    AlertLevel,
    CostMetricType,
    MonitoringAction,
    get_monitor,
    track_cost
)


class TestRealTimeCostMonitor:
    """Test real-time cost monitoring functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def monitor(self, temp_dir):
        """Create test monitor instance"""
        config_path = Path(temp_dir) / "test_config.json"
        monitor = RealTimeCostMonitor(config_path=str(config_path))
        return monitor
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization"""
        assert monitor is not None
        assert len(monitor.thresholds) > 0
        assert not monitor.is_monitoring
        assert monitor.current_costs['total'] == 0.0
    
    def test_default_config_creation(self, monitor):
        """Test default configuration creation"""
        # Should have default thresholds
        assert len(monitor.thresholds) >= 5
        
        # Check daily budget thresholds
        daily_thresholds = [t for t in monitor.thresholds if t.metric_type == CostMetricType.DAILY_BUDGET]
        assert len(daily_thresholds) >= 3
        
        # Check threshold values
        threshold_values = [t.threshold_value for t in daily_thresholds]
        assert 10.0 in threshold_values  # Warning
        assert 15.0 in threshold_values  # Critical
        assert 20.0 in threshold_values  # Emergency
    
    def test_config_save_and_load(self, temp_dir):
        """Test configuration save and load"""
        config_path = Path(temp_dir) / "test_config.json"
        
        # Create monitor and save config
        monitor1 = RealTimeCostMonitor(config_path=str(config_path))
        original_count = len(monitor1.thresholds)
        
        # Load config in new monitor instance
        monitor2 = RealTimeCostMonitor(config_path=str(config_path))
        assert len(monitor2.thresholds) == original_count
    
    def test_cost_tracking(self, monitor):
        """Test cost tracking functionality"""
        # Update costs
        monitor.update_cost("user1", "gemini-pro", "chat", 0.05)
        monitor.update_cost("user2", "gemini-flash", "voice", 0.02)
        
        # Check totals
        assert monitor.current_costs['total'] == 0.07
        assert monitor.current_costs['by_user']['user1'] == 0.05
        assert monitor.current_costs['by_user']['user2'] == 0.02
        assert monitor.current_costs['by_model']['gemini-pro'] == 0.05
        assert monitor.current_costs['by_operation']['chat'] == 0.05
    
    def test_metric_value_calculation(self, monitor):
        """Test metric value calculation"""
        # Set up test data
        monitor.current_costs['total'] = 10.0
        monitor.current_costs['hourly'] = 2.0
        monitor.current_costs['daily'] = 48.0
        monitor.current_costs['by_user']['user1'] = 5.0
        
        # Test metric retrieval
        assert monitor._get_metric_value(CostMetricType.TOTAL_COST) == 10.0
        assert monitor._get_metric_value(CostMetricType.HOURLY_RATE) == 2.0
        assert monitor._get_metric_value(CostMetricType.DAILY_BUDGET) == 48.0
        assert monitor._get_metric_value(CostMetricType.USER_COST) == 5.0
    
    def test_threshold_management(self, monitor):
        """Test threshold addition and removal"""
        initial_count = len(monitor.thresholds)
        
        # Add new threshold
        new_threshold = BudgetThreshold(
            metric_type=CostMetricType.HOURLY_RATE,
            threshold_value=10.0,
            alert_level=AlertLevel.WARNING,
            actions=[MonitoringAction.LOG_ONLY],
            notification_channels=["test"],
            spiritual_message="Test message"
        )
        
        monitor.add_threshold(new_threshold)
        assert len(monitor.thresholds) == initial_count + 1
        
        # Remove threshold
        monitor.remove_threshold(CostMetricType.HOURLY_RATE, 10.0)
        assert len(monitor.thresholds) == initial_count
    
    @pytest.mark.asyncio
    async def test_alert_creation(self, monitor):
        """Test alert creation"""
        threshold = BudgetThreshold(
            metric_type=CostMetricType.DAILY_BUDGET,
            threshold_value=10.0,
            alert_level=AlertLevel.WARNING,
            actions=[MonitoringAction.LOG_ONLY],
            notification_channels=["test"],
            spiritual_message="Test alert"
        )
        
        alert = await monitor._create_alert(threshold, 15.0)
        
        assert alert.metric_type == CostMetricType.DAILY_BUDGET
        assert alert.current_value == 15.0
        assert alert.threshold_value == 10.0
        assert alert.alert_level == AlertLevel.WARNING
        assert alert.spiritual_message == "Test alert"
    
    def test_cooldown_functionality(self, monitor):
        """Test alert cooldown functionality"""
        alert_key = "test_alert"
        
        # No cooldown initially
        assert not monitor._is_in_cooldown(alert_key, 5)
        
        # Set last alert time
        monitor.last_alert_times[alert_key] = datetime.now()
        
        # Should be in cooldown
        assert monitor._is_in_cooldown(alert_key, 5)
        
        # Set old alert time
        monitor.last_alert_times[alert_key] = datetime.now() - timedelta(minutes=10)
        
        # Should not be in cooldown
        assert not monitor._is_in_cooldown(alert_key, 5)
    
    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, monitor):
        """Test monitoring start/stop lifecycle"""
        assert not monitor.is_monitoring
        
        # Start monitoring
        await monitor.start_monitoring(interval_seconds=0.1)
        assert monitor.is_monitoring
        assert monitor.monitoring_task is not None
        
        # Wait a bit
        await asyncio.sleep(0.2)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert not monitor.is_monitoring
    
    @pytest.mark.asyncio
    async def test_alert_processing(self, monitor):
        """Test alert processing"""
        # Set up callback
        callback_called = False
        alert_received = None
        
        async def test_callback(alert):
            nonlocal callback_called, alert_received
            callback_called = True
            alert_received = alert
        
        monitor.register_alert_callback(test_callback)
        
        # Create and process alert
        threshold = BudgetThreshold(
            metric_type=CostMetricType.DAILY_BUDGET,
            threshold_value=10.0,
            alert_level=AlertLevel.WARNING,
            actions=[MonitoringAction.LOG_ONLY],
            notification_channels=[],
            spiritual_message="Test alert"
        )
        
        alert = await monitor._create_alert(threshold, 15.0)
        await monitor._process_alert(alert)
        
        # Check callback was called
        assert callback_called
        assert alert_received is not None
        assert alert.alert_id in monitor.active_alerts
        assert len(monitor.alert_history) > 0
    
    @pytest.mark.asyncio
    async def test_action_execution(self, monitor):
        """Test monitoring action execution"""
        # Set up action callback
        action_called = False
        
        async def test_action(alert):
            nonlocal action_called
            action_called = True
        
        monitor.register_action_callback(MonitoringAction.NOTIFY_ADMIN, test_action)
        
        # Create alert
        alert = CostAlert(
            alert_id="test",
            timestamp=datetime.now(),
            metric_type=CostMetricType.DAILY_BUDGET,
            current_value=15.0,
            threshold_value=10.0,
            alert_level=AlertLevel.WARNING,
            message="Test alert",
            spiritual_message="Test message",
            actions_taken=[],
            context={}
        )
        
        # Execute action
        await monitor._execute_action(MonitoringAction.NOTIFY_ADMIN, alert)
        
        assert action_called
        assert MonitoringAction.NOTIFY_ADMIN.value in alert.actions_taken
    
    def test_current_metrics_api(self, monitor):
        """Test current metrics API"""
        # Update some costs
        monitor.update_cost("user1", "model1", "op1", 1.0)
        
        metrics = monitor.get_current_metrics()
        
        assert 'timestamp' in metrics
        assert 'costs' in metrics
        assert 'active_alerts' in metrics
        assert 'monitoring_active' in metrics
        assert metrics['costs']['total'] == 1.0
    
    def test_alert_history_api(self, monitor):
        """Test alert history API"""
        # Add some alerts to history
        for i in range(5):
            alert = CostAlert(
                alert_id=f"test_{i}",
                timestamp=datetime.now(),
                metric_type=CostMetricType.DAILY_BUDGET,
                current_value=15.0,
                threshold_value=10.0,
                alert_level=AlertLevel.WARNING,
                message=f"Test alert {i}",
                spiritual_message="Test message",
                actions_taken=[],
                context={}
            )
            monitor.alert_history.append(alert)
        
        history = monitor.get_alert_history(limit=3)
        assert len(history) == 3
        
        # Test all history
        all_history = monitor.get_alert_history(limit=10)
        assert len(all_history) == 5
    
    def test_active_alerts_api(self, monitor):
        """Test active alerts API"""
        # Add active alerts
        alert1 = CostAlert(
            alert_id="active1",
            timestamp=datetime.now(),
            metric_type=CostMetricType.DAILY_BUDGET,
            current_value=15.0,
            threshold_value=10.0,
            alert_level=AlertLevel.WARNING,
            message="Active alert 1",
            spiritual_message="Test message",
            actions_taken=[],
            context={}
        )
        
        monitor.active_alerts["active1"] = alert1
        
        active = monitor.get_active_alerts()
        assert len(active) == 1
        assert active[0]['alert_id'] == 'active1'
    
    def test_global_monitor_instance(self):
        """Test global monitor instance"""
        monitor1 = get_monitor()
        monitor2 = get_monitor()
        
        # Should be the same instance
        assert monitor1 is monitor2


class TestCostTrackingDecorator:
    """Test cost tracking decorator"""
    
    @pytest.mark.asyncio
    async def test_async_function_tracking(self):
        """Test async function cost tracking"""
        monitor = get_monitor()
        initial_cost = monitor.current_costs['total']
        
        @track_cost(user_id="test_user", model="test_model", operation="test_op")
        async def test_async_function():
            await asyncio.sleep(0.01)  # Simulate work
            return "result"
        
        result = await test_async_function()
        
        assert result == "result"
        assert monitor.current_costs['total'] > initial_cost
        assert monitor.current_costs['by_user']['test_user'] > 0
        assert monitor.current_costs['by_model']['test_model'] > 0
        assert monitor.current_costs['by_operation']['test_op'] > 0
    
    def test_sync_function_tracking(self):
        """Test sync function cost tracking"""
        monitor = get_monitor()
        initial_cost = monitor.current_costs['total']
        
        @track_cost(user_id="test_user2", model="test_model2", operation="test_op2")
        def test_sync_function():
            import time
            time.sleep(0.01)  # Simulate work
            return "sync_result"
        
        result = test_sync_function()
        
        assert result == "sync_result"
        assert monitor.current_costs['total'] > initial_cost
        assert monitor.current_costs['by_user']['test_user2'] > 0
    
    @pytest.mark.asyncio
    async def test_error_tracking(self):
        """Test error cost tracking"""
        monitor = get_monitor()
        initial_cost = monitor.current_costs['total']
        
        @track_cost(user_id="error_user", model="error_model", operation="error_op")
        async def error_function():
            await asyncio.sleep(0.01)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await error_function()
        
        # Should still track cost for errors
        assert monitor.current_costs['total'] > initial_cost
        assert monitor.current_costs['by_operation']['error_op_error'] > 0


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_budget_alert_scenario(self):
        """Test complete budget alert scenario"""
        monitor = get_monitor()
        
        # Set up low threshold for testing
        test_threshold = BudgetThreshold(
            metric_type=CostMetricType.TOTAL_COST,
            threshold_value=0.1,  # $0.10
            alert_level=AlertLevel.WARNING,
            actions=[MonitoringAction.LOG_ONLY],
            notification_channels=[],
            spiritual_message="Test budget alert",
            cooldown_minutes=0  # No cooldown for testing
        )
        
        monitor.add_threshold(test_threshold)
        
        # Track callback
        alerts_received = []
        
        async def alert_callback(alert):
            alerts_received.append(alert)
        
        monitor.register_alert_callback(alert_callback)
        
        # Simulate cost that exceeds threshold
        monitor.update_cost("test_user", "test_model", "test_op", 0.15)
        
        # Start monitoring briefly
        await monitor.start_monitoring(interval_seconds=0.1)
        await asyncio.sleep(0.2)  # Let it run one cycle
        await monitor.stop_monitoring()
        
        # Check if alert was triggered
        assert len(alerts_received) > 0
        assert alerts_received[0].current_value >= 0.1
    
    @pytest.mark.asyncio
    async def test_spiritual_messaging(self):
        """Test spiritual messaging in alerts"""
        monitor = get_monitor()
        
        # Check default spiritual messages
        daily_thresholds = [t for t in monitor.thresholds if t.metric_type == CostMetricType.DAILY_BUDGET]
        
        for threshold in daily_thresholds:
            assert len(threshold.spiritual_message) > 0
            # Should contain spiritual/dharmic elements
            spiritual_indicators = ['🙏', '⚠️', '🛑', 'divine', 'wisdom', 'dharma', 'balance']
            has_spiritual_element = any(indicator in threshold.spiritual_message.lower() for indicator in spiritual_indicators)
            assert has_spiritual_element, f"No spiritual element in: {threshold.spiritual_message}"
    
    def test_cost_calculation_accuracy(self):
        """Test cost calculation accuracy"""
        monitor = get_monitor()
        
        # Clear current costs
        monitor.current_costs = {
            'total': 0.0,
            'hourly': 0.0,
            'daily': 0.0,
            'monthly': 0.0,
            'by_user': defaultdict(float),
            'by_model': defaultdict(float),
            'by_operation': defaultdict(float)
        }
        
        # Add specific costs
        monitor.update_cost("user1", "model1", "op1", 1.25)
        monitor.update_cost("user1", "model2", "op2", 2.75)
        monitor.update_cost("user2", "model1", "op1", 1.50)
        
        # Check totals
        assert monitor.current_costs['total'] == 5.50
        assert monitor.current_costs['by_user']['user1'] == 4.00
        assert monitor.current_costs['by_user']['user2'] == 1.50
        assert monitor.current_costs['by_model']['model1'] == 2.75
        assert monitor.current_costs['by_model']['model2'] == 2.75


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
