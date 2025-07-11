"""
Tests for Admin Monitoring & Metrics
Tests the comprehensive monitoring system for admin operations
"""

import os
# Set up test environment with authentication enabled
os.environ['ENABLE_AUTH'] = 'true'

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from core.admin_monitoring import (
    AdminMetricsCollector,
    AdminOperationType,
    AdminMetricType,
    AdminOperationMetric,
    AdminAlert,
    monitor_admin_operation,
    admin_metrics_collector
)
from admin.admin_endpoints import (
    admin_cost_dashboard,
    admin_system_health,
    admin_user_management
)
from auth.unified_auth_service import AuthenticatedUser
from core.user_roles import UserRole, UserPermissions
from azure.functions import HttpRequest


class TestAdminMetricsCollector:
    """Test the admin metrics collector"""
    
    def setup_method(self):
        """Set up test environment"""
        self.collector = AdminMetricsCollector(max_metrics=100)
    
    def test_metrics_collector_initialization(self):
        """Test metrics collector initializes correctly"""
        assert self.collector.max_metrics == 100
        assert len(self.collector.metrics) == 0
        assert len(self.collector.alerts) == 0
        assert len(self.collector.active_operations) == 0
        assert len(self.collector.operation_counts) == 0
        assert len(self.collector.error_counts) == 0
    
    def test_record_operation_lifecycle(self):
        """Test complete operation recording lifecycle"""
        # Start operation
        operation_id = self.collector.record_operation_start(
            operation_type=AdminOperationType.COST_DASHBOARD,
            admin_email="test@example.com",
            request_data={"method": "GET", "params": {}}
        )
        
        assert operation_id in self.collector.active_operations
        assert "test@example.com" in self.collector.concurrent_admins
        assert len(self.collector.metrics) > 0  # Concurrent users metric
        
        # End operation successfully
        self.collector.record_operation_end(
            operation_id=operation_id,
            success=True,
            response_data={"status": "ok"}
        )
        
        assert operation_id not in self.collector.active_operations
        assert self.collector.operation_counts[AdminOperationType.COST_DASHBOARD] == 1
        assert self.collector.error_counts[AdminOperationType.COST_DASHBOARD] == 0
    
    def test_record_operation_failure(self):
        """Test operation failure recording"""
        operation_id = self.collector.record_operation_start(
            operation_type=AdminOperationType.USER_MANAGEMENT,
            admin_email="admin@example.com"
        )
        
        self.collector.record_operation_end(
            operation_id=operation_id,
            success=False,
            error_message="Database connection failed"
        )
        
        assert self.collector.error_counts[AdminOperationType.USER_MANAGEMENT] == 1
        assert len(self.collector.alerts) > 0
        
        # Check alert was created
        error_alerts = [a for a in self.collector.alerts if a.alert_type == "operation_error"]
        assert len(error_alerts) == 1
        assert "Database connection failed" in error_alerts[0].message
    
    def test_performance_threshold_alerts(self):
        """Test performance threshold violation alerts"""
        # Set a very low threshold for testing
        self.collector.performance_thresholds[AdminOperationType.COST_DASHBOARD] = 0.001
        
        operation_id = self.collector.record_operation_start(
            operation_type=AdminOperationType.COST_DASHBOARD,
            admin_email="slow@example.com"
        )
        
        # Simulate slow operation
        import time
        time.sleep(0.01)  # 10ms should exceed 1ms threshold
        
        self.collector.record_operation_end(operation_id=operation_id, success=True)
        
        # Check performance alert was created
        perf_alerts = [a for a in self.collector.alerts if a.alert_type == "performance_warning"]
        assert len(perf_alerts) == 1
        assert "Slow admin operation" in perf_alerts[0].message
    
    def test_metrics_summary(self):
        """Test metrics summary generation"""
        # Record some operations
        for i in range(3):
            op_id = self.collector.record_operation_start(
                operation_type=AdminOperationType.BUDGET_MANAGEMENT,
                admin_email=f"admin{i}@example.com"
            )
            self.collector.record_operation_end(op_id, success=True)
        
        summary = self.collector.get_metrics_summary(hours=1)
        
        assert summary['total_operations'] == 3
        assert summary['unique_admins'] == 3
        assert 'operation_breakdown' in summary
        assert 'performance_stats' in summary
        assert AdminOperationType.BUDGET_MANAGEMENT.value in summary['operation_breakdown']
    
    def test_alert_management(self):
        """Test alert creation and resolution"""
        # Create an alert manually
        self.collector._create_alert(
            alert_type="test_alert",
            severity="medium",
            message="Test alert message",
            operation_type=AdminOperationType.ROLE_MANAGEMENT,
            admin_email="test@example.com"
        )
        
        alerts = self.collector.get_alerts()
        assert len(alerts) == 1
        assert alerts[0]['alert_type'] == "test_alert"
        assert alerts[0]['severity'] == "medium"
        assert not alerts[0]['resolved']
        
        # Resolve the alert
        success = self.collector.resolve_alert(
            alert_index=0,
            resolution_notes="Fixed the issue",
            admin_email="admin@example.com"
        )
        
        assert success
        assert self.collector.alerts[0].resolved
        assert self.collector.alerts[0].resolution_notes == "Fixed the issue"
    
    def test_cleanup_old_data(self):
        """Test cleanup of old metrics and alerts"""
        # Create old alert
        old_alert = AdminAlert(
            alert_type="old_alert",
            severity="low",
            message="Old alert",
            operation_type=None,
            admin_email="test@example.com",
            timestamp=datetime.utcnow() - timedelta(days=10),
            resolved=True
        )
        self.collector.alerts.append(old_alert)
        
        # Create new alert
        new_alert = AdminAlert(
            alert_type="new_alert",
            severity="medium",
            message="New alert",
            operation_type=None,
            admin_email="test@example.com",
            timestamp=datetime.utcnow(),
            resolved=True
        )
        self.collector.alerts.append(new_alert)
        
        assert len(self.collector.alerts) == 2
        
        # Cleanup old data
        self.collector.cleanup_old_data(days=5)
        
        # Only new alert should remain
        assert len(self.collector.alerts) == 1
        assert self.collector.alerts[0].alert_type == "new_alert"


class TestAdminMonitoringDecorator:
    """Test the monitoring decorator functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Clear global collector for clean tests
        admin_metrics_collector.metrics.clear()
        admin_metrics_collector.alerts.clear()
        admin_metrics_collector.active_operations.clear()
        admin_metrics_collector.operation_counts.clear()
        admin_metrics_collector.error_counts.clear()
    
    @pytest.mark.asyncio
    async def test_async_function_monitoring(self):
        """Test monitoring decorator with async functions"""
        
        @monitor_admin_operation(AdminOperationType.SYSTEM_HEALTH)
        async def test_async_function(req):
            # Simulate some work
            await asyncio.sleep(0.01)
            return Mock(get_body=lambda: b'{"status": "ok"}')
        
        # Create mock request with user
        mock_request = Mock()
        mock_request.user = AuthenticatedUser(
            id="test-user",
            email="admin@example.com",
            name="Test Admin",
            given_name="Test",
            family_name="Admin",
            permissions=[],
            role=UserRole.ADMIN,
            user_permissions=UserPermissions.for_role(UserRole.ADMIN)
        )
        mock_request.method = "GET"
        mock_request.url = "https://example.com/api/admin/health"
        mock_request.params = {}
        
        result = await test_async_function(mock_request)
        
        # Check metrics were recorded
        assert admin_metrics_collector.operation_counts[AdminOperationType.SYSTEM_HEALTH] == 1
        assert len(admin_metrics_collector.metrics) > 0
        
        # Check metrics contain expected data
        duration_metrics = [m for m in admin_metrics_collector.metrics if m.metric_type == AdminMetricType.OPERATION_DURATION]
        assert len(duration_metrics) > 0
        assert duration_metrics[0].admin_email == "admin@example.com"
    
    @pytest.mark.asyncio
    async def test_async_function_error_monitoring(self):
        """Test monitoring decorator with async function errors"""
        
        @monitor_admin_operation(AdminOperationType.USER_MANAGEMENT)
        async def test_failing_function(req):
            raise ValueError("Test error message")
        
        mock_request = Mock()
        mock_request.user = AuthenticatedUser(
            id="test-user",
            email="error@example.com",
            name="Error Admin",
            given_name="Error",
            family_name="Admin",
            permissions=[],
            role=UserRole.ADMIN,
            user_permissions=UserPermissions.for_role(UserRole.ADMIN)
        )
        mock_request.method = "POST"
        mock_request.url = "https://example.com/api/admin/users"
        mock_request.params = {}
        
        with pytest.raises(ValueError, match="Test error message"):
            await test_failing_function(mock_request)
        
        # Check error was recorded
        assert admin_metrics_collector.error_counts[AdminOperationType.USER_MANAGEMENT] == 1
        error_alerts = [a for a in admin_metrics_collector.alerts if a.alert_type == "operation_error"]
        assert len(error_alerts) == 1
        assert "Test error message" in error_alerts[0].message


class TestMonitoringEndpoints:
    """Test the monitoring API endpoints"""
    
    def setup_method(self):
        """Set up test environment"""
        # Clear metrics for clean tests
        admin_metrics_collector.metrics.clear()
        admin_metrics_collector.alerts.clear()
        admin_metrics_collector.active_operations.clear()
    
    @pytest.mark.asyncio
    async def test_admin_metrics_dashboard(self):
        """Test metrics dashboard endpoint"""
        # Add some test metrics
        admin_metrics_collector._add_metric(
            AdminOperationType.COST_DASHBOARD,
            AdminMetricType.OPERATION_COUNT,
            1,
            "admin@example.com"
        )
        
        # Create mock request
        mock_request = Mock()
        mock_request.user = AuthenticatedUser(
            id="admin-user",
            email="admin@example.com",
            name="Admin User",
            given_name="Admin",
            family_name="User",
            permissions=[],
            role=UserRole.ADMIN,
            user_permissions=UserPermissions.for_role(UserRole.ADMIN)
        )
        mock_request.method = "GET"
        mock_request.params = {"hours": "24"}
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1"}
        mock_request.url = "/admin/cost-dashboard"
        mock_request.route_params = {}
        mock_request.get_json = Mock(return_value={})
        
        # Mock authentication
        with patch('auth.unified_auth_service.auth_service.authenticate_request', 
                  return_value=mock_request.user):
            response = await admin_cost_dashboard(mock_request)
        
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert 'time_period_hours' in body
        assert 'total_operations' in body
        assert 'operation_breakdown' in body
        assert 'monitoring_status' in body
    
    @pytest.mark.asyncio
    async def test_admin_alerts_management_get(self):
        """Test alerts management GET endpoint"""
        # Add test alert
        admin_metrics_collector._create_alert(
            alert_type="test_alert",
            severity="medium",
            message="Test alert for endpoint",
            operation_type=AdminOperationType.BUDGET_MANAGEMENT,
            admin_email="test@example.com"
        )
        
        mock_request = Mock()
        mock_request.user = AuthenticatedUser(
            id="admin-user",
            email="admin@example.com",
            name="Admin User",
            given_name="Admin",
            family_name="User",
            permissions=[],
            role=UserRole.ADMIN,
            user_permissions=UserPermissions.for_role(UserRole.ADMIN)
        )
        mock_request.method = "GET"
        mock_request.params = {"limit": "10"}
        
        # Mock authentication
        with patch('auth.unified_auth_service.auth_service.authenticate_request', 
                  return_value=mock_request.user):
            response = await admin_system_health(mock_request)
        
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert 'alerts' in body
        assert 'summary' in body
        assert len(body['alerts']) == 1
        assert body['alerts'][0]['alert_type'] == "test_alert"
    
    @pytest.mark.asyncio
    async def test_admin_system_maintenance(self):
        """Test system maintenance endpoint"""
        mock_request = Mock()
        mock_request.user = AuthenticatedUser(
            id="admin-user",
            email="admin@example.com",
            name="Admin User",
            given_name="Admin",
            family_name="User",
            permissions=[],
            role=UserRole.ADMIN,
            user_permissions=UserPermissions.for_role(UserRole.ADMIN)
        )
        mock_request.method = "POST"
        mock_request.get_json.return_value = {
            "action": "reset_performance_thresholds"
        }
        
        # Mock authentication
        with patch('auth.unified_auth_service.auth_service.authenticate_request', 
                  return_value=mock_request.user):
            response = await admin_user_management(mock_request)
        
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert body['action'] == "reset_performance_thresholds"
        assert 'results' in body
        assert len(body['results']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
