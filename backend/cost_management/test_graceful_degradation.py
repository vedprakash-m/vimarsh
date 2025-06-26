"""
Tests for Graceful Degradation with User Notification System
Task 7.7: Enhanced AI Cost Management & Dynamic Fallbacks

This module tests the comprehensive graceful degradation capabilities
including user notifications, service health monitoring, and recovery.
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from .graceful_degradation import (
    GracefulDegradationManager,
    DegradationLevel,
    ServiceComponent,
    NotificationType,
    DegradationStatus,
    UserNotification,
    SpiritualMessageGenerator,
    with_degradation_monitoring,
    get_degradation_manager
)


class TestSpiritualMessageGenerator:
    """Test spiritual message generation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.generator = SpiritualMessageGenerator()
    
    def test_message_generation_for_all_levels(self):
        """Test that messages are generated for all degradation levels"""
        for level in DegradationLevel:
            if level != DegradationLevel.NORMAL:
                message = self.generator.get_message(level)
                assert isinstance(message, str)
                assert len(message) > 0
                assert any(char in message for char in "🕉️🙏📿🧘‍♂️🌸⚡🛡️🔥💫🌟⭐")  # Contains spiritual emojis
    
    def test_message_content_appropriateness(self):
        """Test that messages are culturally appropriate"""
        for level in [DegradationLevel.MINOR, DegradationLevel.MODERATE, DegradationLevel.SEVERE]:
            message = self.generator.get_message(level)
            # Should contain spiritual/cultural references
            spiritual_terms = ["Krishna", "dharma", "Gita", "devotion", "lotus", "Hanuman", "divine", "soul", "Arjuna"]
            assert any(term in message for term in spiritual_terms)
    
    def test_message_randomness(self):
        """Test that different messages are returned for variety"""
        messages = set()
        for _ in range(20):
            message = self.generator.get_message(DegradationLevel.MODERATE)
            messages.add(message)
        
        # Should have some variety (not always the same message)
        assert len(messages) > 1


class TestDegradationStatus:
    """Test degradation status data structure"""
    
    def test_status_creation(self):
        """Test creating degradation status"""
        status = DegradationStatus(
            level=DegradationLevel.MODERATE,
            affected_components=[ServiceComponent.LLM_SERVICE],
            timestamp=datetime.now(),
            reason="Test degradation"
        )
        
        assert status.level == DegradationLevel.MODERATE
        assert ServiceComponent.LLM_SERVICE in status.affected_components
        assert status.reason == "Test degradation"
    
    def test_status_serialization(self):
        """Test status serialization to dictionary"""
        timestamp = datetime.now()
        status = DegradationStatus(
            level=DegradationLevel.SEVERE,
            affected_components=[ServiceComponent.LLM_SERVICE, ServiceComponent.VECTOR_SEARCH],
            timestamp=timestamp,
            reason="Multiple failures",
            estimated_recovery=timestamp + timedelta(hours=2)
        )
        
        data = status.to_dict()
        assert data['level'] == 'severe'
        assert 'llm_service' in data['affected_components']
        assert 'vector_search' in data['affected_components']
        assert data['reason'] == "Multiple failures"
        assert 'estimated_recovery' in data


class TestUserNotification:
    """Test user notification system"""
    
    def test_notification_creation(self):
        """Test creating user notifications"""
        notification = UserNotification(
            id="test_001",
            type=NotificationType.WARNING,
            title="Test Notification",
            message="This is a test notification",
            spiritual_message="🕉️ Test spiritual message"
        )
        
        assert notification.id == "test_001"
        assert notification.type == NotificationType.WARNING
        assert notification.title == "Test Notification"
        assert notification.spiritual_message == "🕉️ Test spiritual message"
        assert notification.dismissible is True
        assert isinstance(notification.timestamp, datetime)
    
    def test_notification_serialization(self):
        """Test notification serialization"""
        notification = UserNotification(
            id="test_002",
            type=NotificationType.ERROR,
            title="Error Notification",
            message="An error occurred",
            actions=[{"label": "Retry", "action": "retry"}],
            auto_dismiss_after=30
        )
        
        data = notification.to_dict()
        assert data['id'] == "test_002"
        assert data['type'] == 'error'
        assert data['title'] == "Error Notification"
        assert len(data['actions']) == 1
        assert data['auto_dismiss_after'] == 30


class TestGracefulDegradationManager:
    """Test graceful degradation manager"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GracefulDegradationManager(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        # Handle async shutdown properly
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.manager.shutdown())
        except RuntimeError:
            # No running loop, create a new one for shutdown
            asyncio.run(self.manager.shutdown())
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manager_initialization(self):
        """Test manager initialization"""
        assert self.manager.current_status.level == DegradationLevel.NORMAL
        assert len(self.manager.current_status.affected_components) == 0
        assert len(self.manager.component_health) == len(ServiceComponent)
        assert len(self.manager.degradation_rules) == len(ServiceComponent)
    
    def test_component_health_initialization(self):
        """Test component health initialization"""
        for component in ServiceComponent:
            health = self.manager.component_health[component]
            assert health['status'] == 'healthy'
            assert health['error_count'] == 0
            assert health['success_rate'] == 100.0
            assert isinstance(health['last_check'], datetime)
    
    def test_component_health_update_success(self):
        """Test updating component health with success"""
        component = ServiceComponent.LLM_SERVICE
        initial_rate = self.manager.component_health[component]['success_rate']
        
        self.manager.update_component_health(component, False, 0.1, True)
        
        health = self.manager.component_health[component]
        assert health['error_count'] == 0
        assert health['response_time'] == 0.1
        assert health['success_rate'] >= initial_rate  # Should maintain or improve
    
    def test_component_health_update_failure(self):
        """Test updating component health with failure"""
        component = ServiceComponent.LLM_SERVICE
        
        self.manager.update_component_health(component, True, 2.0, False)
        
        health = self.manager.component_health[component]
        assert health['error_count'] == 1
        assert health['response_time'] == 2.0
        assert health['success_rate'] < 100.0
    
    def test_degradation_threshold_minor(self):
        """Test minor degradation threshold"""
        component = ServiceComponent.LLM_SERVICE
        
        # Trigger minor degradation by error count
        for _ in range(5):
            self.manager.update_component_health(component, True, 0.5, False)
        
        # Should trigger degradation evaluation
        assert self.manager.current_status.level in [DegradationLevel.MINOR, DegradationLevel.MODERATE, DegradationLevel.SEVERE]
    
    def test_degradation_threshold_response_time(self):
        """Test degradation based on response time"""
        component = ServiceComponent.VECTOR_SEARCH
        
        # Trigger degradation with slow response time
        self.manager.update_component_health(component, False, 10.0, True)
        
        # Check if component is flagged for degradation
        health = self.manager.component_health[component]
        assert health['response_time'] == 10.0
    
    @pytest.mark.asyncio
    async def test_manual_degradation(self):
        """Test manual degradation forcing"""
        await self.manager.force_degradation(
            DegradationLevel.MODERATE,
            [ServiceComponent.LLM_SERVICE],
            "Manual test degradation"
        )
        
        assert self.manager.current_status.level == DegradationLevel.MODERATE
        assert ServiceComponent.LLM_SERVICE in self.manager.current_status.affected_components
        assert "Manual test degradation" in self.manager.current_status.reason
    
    @pytest.mark.asyncio
    async def test_notification_creation_on_degradation(self):
        """Test that notifications are created when degradation occurs"""
        initial_count = len(self.manager.active_notifications)
        
        await self.manager.force_degradation(
            DegradationLevel.SEVERE,
            [ServiceComponent.LLM_SERVICE, ServiceComponent.VECTOR_SEARCH],
            "Test notification creation"
        )
        
        # Give time for notification to be added
        await asyncio.sleep(0.1)
        
        assert len(self.manager.active_notifications) > initial_count
        
        # Check notification content
        notifications = self.manager.get_active_notifications()
        notification = notifications[-1]  # Most recent
        assert notification['type'] == 'error'  # Severe degradation should be error type
        assert 'Service Disruption' in notification['title']
    
    @pytest.mark.asyncio
    async def test_recovery_notification(self):
        """Test recovery notification"""
        # First degrade
        await self.manager.force_degradation(
            DegradationLevel.MODERATE,
            [ServiceComponent.LLM_SERVICE],
            "Test recovery"
        )
        
        await asyncio.sleep(0.1)
        
        # Then recover
        await self.manager.force_degradation(
            DegradationLevel.NORMAL,
            [],
            "Service recovered"
        )
        
        await asyncio.sleep(0.1)
        
        # Check for recovery notification
        notifications = self.manager.get_active_notifications()
        recovery_notification = None
        for notification in notifications:
            if 'Restored' in notification['title']:
                recovery_notification = notification
                break
        
        assert recovery_notification is not None
        assert recovery_notification['type'] == 'success'
    
    @pytest.mark.asyncio
    async def test_notification_dismissal(self):
        """Test notification dismissal"""
        notification = UserNotification(
            id="dismiss_test",
            type=NotificationType.INFO,
            title="Test Dismissal",
            message="This notification will be dismissed"
        )
        
        await self.manager.add_notification(notification)
        assert "dismiss_test" in self.manager.active_notifications
        
        success = await self.manager.dismiss_notification("dismiss_test")
        assert success is True
        assert "dismiss_test" not in self.manager.active_notifications
    
    @pytest.mark.asyncio
    async def test_auto_dismiss_notification(self):
        """Test auto-dismissing notifications"""
        notification = UserNotification(
            id="auto_dismiss_test",
            type=NotificationType.INFO,
            title="Auto Dismiss Test",
            message="This notification will auto-dismiss",
            auto_dismiss_after=1  # 1 second
        )
        
        # Start the auto-dismiss task
        asyncio.create_task(self.manager.add_notification(notification))
        
        # Should be active initially
        await asyncio.sleep(0.1)
        assert "auto_dismiss_test" in self.manager.active_notifications
        
        # Should be dismissed after timeout
        await asyncio.sleep(1.5)
        assert "auto_dismiss_test" not in self.manager.active_notifications
    
    def test_persistent_state_save_load(self):
        """Test saving and loading persistent state"""
        # Modify state
        test_status = DegradationStatus(
            level=DegradationLevel.MODERATE,
            affected_components=[ServiceComponent.LLM_SERVICE],
            timestamp=datetime.now(),
            reason="Persistence test"
        )
        self.manager.current_status = test_status
        
        # Save state
        self.manager._save_persistent_state()
        
        # Create new manager and check if state is loaded
        new_manager = GracefulDegradationManager(storage_path=self.temp_dir)
        assert new_manager.current_status.level == DegradationLevel.MODERATE
        assert ServiceComponent.LLM_SERVICE in new_manager.current_status.affected_components
        assert new_manager.current_status.reason == "Persistence test"
    
    def test_component_health_reset(self):
        """Test resetting component health"""
        component = ServiceComponent.VOICE_INTERFACE
        
        # Degrade component health
        for _ in range(10):
            self.manager.update_component_health(component, True, 5.0, False)
        
        health_before = self.manager.component_health[component].copy()
        assert health_before['error_count'] > 0
        assert health_before['success_rate'] < 100.0
        
        # Reset health
        self.manager.reset_component_health(component)
        
        health_after = self.manager.component_health[component]
        assert health_after['error_count'] == 0
        assert health_after['success_rate'] == 100.0
        assert health_after['status'] == 'healthy'
    
    def test_get_current_status(self):
        """Test getting current status"""
        status = self.manager.get_current_status()
        
        assert 'level' in status
        assert 'affected_components' in status
        assert 'timestamp' in status
        assert 'reason' in status
        assert status['level'] == 'normal'
    
    def test_get_component_health(self):
        """Test getting component health status"""
        health = self.manager.get_component_health()
        
        assert len(health) == len(ServiceComponent)
        for component_name, component_health in health.items():
            assert 'status' in component_health
            assert 'error_count' in component_health
            assert 'success_rate' in component_health
            assert 'response_time' in component_health
            assert 'last_check' in component_health
    
    @pytest.mark.asyncio
    async def test_notification_history_limit(self):
        """Test that notification history is limited"""
        # Add many notifications
        for i in range(150):
            notification = UserNotification(
                id=f"history_test_{i}",
                type=NotificationType.INFO,
                title=f"Test {i}",
                message=f"Test notification {i}"
            )
            await self.manager.add_notification(notification)
        
        # Should limit history to 50 most recent
        assert len(self.manager.notification_history) <= 100
    
    @pytest.mark.asyncio
    async def test_timed_recovery(self):
        """Test timed automatic recovery"""
        # Force degradation with 1-minute auto-recovery
        await self.manager.force_degradation(
            DegradationLevel.MINOR,
            [ServiceComponent.AUTHENTICATION],
            "Timed recovery test",
            duration_minutes=0.01  # Very short for testing (0.6 seconds)
        )
        
        assert self.manager.current_status.level == DegradationLevel.MINOR
        
        # Wait for auto-recovery
        await asyncio.sleep(1)
        
        # Should be recovered
        assert self.manager.current_status.level == DegradationLevel.NORMAL


class TestDegradationMonitoringDecorator:
    """Test degradation monitoring decorator"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GracefulDegradationManager(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        # Handle async shutdown properly
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.manager.shutdown())
        except RuntimeError:
            # No running loop, create a new one for shutdown
            asyncio.run(self.manager.shutdown())
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_async_function_monitoring_success(self):
        """Test monitoring async function success"""
        @with_degradation_monitoring(ServiceComponent.LLM_SERVICE, self.manager)
        async def test_async_function():
            await asyncio.sleep(0.1)
            return "success"
        
        initial_health = self.manager.component_health[ServiceComponent.LLM_SERVICE].copy()
        
        result = await test_async_function()
        
        assert result == "success"
        health = self.manager.component_health[ServiceComponent.LLM_SERVICE]
        assert health['error_count'] == initial_health['error_count']  # No new errors
        assert health['response_time'] > 0  # Response time recorded
    
    @pytest.mark.asyncio
    async def test_async_function_monitoring_failure(self):
        """Test monitoring async function failure"""
        @with_degradation_monitoring(ServiceComponent.VECTOR_SEARCH, self.manager)
        async def test_failing_function():
            await asyncio.sleep(0.05)
            raise ValueError("Test error")
        
        initial_error_count = self.manager.component_health[ServiceComponent.VECTOR_SEARCH]['error_count']
        
        with pytest.raises(ValueError):
            await test_failing_function()
        
        health = self.manager.component_health[ServiceComponent.VECTOR_SEARCH]
        assert health['error_count'] == initial_error_count + 1
        assert health['response_time'] > 0
    
    def test_sync_function_monitoring_success(self):
        """Test monitoring sync function success"""
        @with_degradation_monitoring(ServiceComponent.COST_MANAGEMENT, self.manager)
        def test_sync_function():
            import time
            time.sleep(0.1)
            return "sync_success"
        
        initial_health = self.manager.component_health[ServiceComponent.COST_MANAGEMENT].copy()
        
        result = test_sync_function()
        
        assert result == "sync_success"
        health = self.manager.component_health[ServiceComponent.COST_MANAGEMENT]
        assert health['error_count'] == initial_health['error_count']
        assert health['response_time'] > 0
    
    def test_sync_function_monitoring_failure(self):
        """Test monitoring sync function failure"""
        @with_degradation_monitoring(ServiceComponent.CITATION_SYSTEM, self.manager)
        def test_failing_sync_function():
            import time
            time.sleep(0.05)
            raise RuntimeError("Sync test error")
        
        initial_error_count = self.manager.component_health[ServiceComponent.CITATION_SYSTEM]['error_count']
        
        with pytest.raises(RuntimeError):
            test_failing_sync_function()
        
        health = self.manager.component_health[ServiceComponent.CITATION_SYSTEM]
        assert health['error_count'] == initial_error_count + 1


class TestIntegrationScenarios:
    """Test integration scenarios with multiple components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GracefulDegradationManager(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        # Handle async shutdown properly
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.manager.shutdown())
        except RuntimeError:
            # No running loop, create a new one for shutdown
            asyncio.run(self.manager.shutdown())
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_cascading_failure_scenario(self):
        """Test cascading failure across multiple components"""
        # Simulate LLM service failure
        for _ in range(10):
            self.manager.update_component_health(ServiceComponent.LLM_SERVICE, True, 3.0, False)
        
        # Simulate vector search degradation
        for _ in range(5):
            self.manager.update_component_health(ServiceComponent.VECTOR_SEARCH, True, 2.0, False)
        
        # Should trigger degradation
        await asyncio.sleep(0.1)  # Allow evaluation to complete
        
        assert self.manager.current_status.level != DegradationLevel.NORMAL
        assert len(self.manager.current_status.affected_components) >= 1
    
    @pytest.mark.asyncio
    async def test_partial_recovery_scenario(self):
        """Test partial recovery with some components still degraded"""
        # Degrade multiple components
        await self.manager.force_degradation(
            DegradationLevel.SEVERE,
            [ServiceComponent.LLM_SERVICE, ServiceComponent.VOICE_INTERFACE, ServiceComponent.VECTOR_SEARCH],
            "Multi-component failure"
        )
        
        # Recover some components
        self.manager.reset_component_health(ServiceComponent.VOICE_INTERFACE)
        self.manager.reset_component_health(ServiceComponent.VECTOR_SEARCH)
        
        # LLM still degraded
        for _ in range(20):
            self.manager.update_component_health(ServiceComponent.LLM_SERVICE, True, 4.0, False)
        
        # Should maintain some degradation level
        await asyncio.sleep(0.1)
        assert self.manager.current_status.level != DegradationLevel.NORMAL
    
    @pytest.mark.asyncio
    async def test_spiritual_messaging_consistency(self):
        """Test that spiritual messages are consistent with degradation levels"""
        levels_to_test = [DegradationLevel.MINOR, DegradationLevel.MODERATE, DegradationLevel.SEVERE]
        
        for level in levels_to_test:
            await self.manager.force_degradation(
                level,
                [ServiceComponent.LLM_SERVICE],
                f"Testing {level.value} messaging"
            )
            
            await asyncio.sleep(0.1)
            
            # Check that appropriate spiritual message was generated
            assert len(self.manager.current_status.user_message) > 0
            assert any(char in self.manager.current_status.user_message for char in "🕉️🙏📿🧘‍♂️🌸⚡🛡️🔥💫🌟⭐")
            
            # Check notification has spiritual content
            notifications = self.manager.get_active_notifications()
            if notifications:
                recent_notification = notifications[-1]
                assert recent_notification.get('spiritual_message') is not None
    
    @pytest.mark.asyncio
    async def test_high_frequency_updates(self):
        """Test system stability under high frequency updates"""
        # Simulate rapid health updates
        for i in range(100):
            component = list(ServiceComponent)[i % len(ServiceComponent)]
            success = i % 3 != 0  # 2/3 success rate
            error = not success
            response_time = 0.1 + (i % 10) * 0.1
            
            self.manager.update_component_health(component, error, response_time, success)
        
        # System should remain stable
        status = self.manager.get_current_status()
        assert 'level' in status
        assert isinstance(status['level'], str)
        
        # Should have some health data
        health = self.manager.get_component_health()
        assert len(health) == len(ServiceComponent)
    
    @pytest.mark.asyncio
    async def test_notification_flood_protection(self):
        """Test protection against notification flooding"""
        initial_count = len(self.manager.active_notifications)
        
        # Rapidly trigger degradations
        for i in range(10):
            await self.manager.force_degradation(
                DegradationLevel.MINOR,
                [ServiceComponent.LLM_SERVICE],
                f"Flood test {i}"
            )
            await asyncio.sleep(0.01)
        
        # Should not create excessive notifications
        final_count = len(self.manager.active_notifications)
        assert final_count - initial_count < 10  # Less than one per degradation


if __name__ == "__main__":
    # Run basic test
    pytest.main([__file__, "-v"])
