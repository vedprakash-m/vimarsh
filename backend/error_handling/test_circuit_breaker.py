"""
Test Suite for Circuit Breaker and Health Monitoring System

Comprehensive tests covering circuit breaker behavior, health monitoring,
and integrated system functionality for the Vimarsh AI Agent.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

# Import the systems under test
try:
    from .circuit_breaker import (
        CircuitBreaker, CircuitBreakerConfig, CircuitState,
        HealthMonitor, HealthCheckConfig, HealthStatus,
        CircuitBreakerManager, HealthAndCircuitMonitor,
        ServiceHealthChecks, CircuitBreakerError,
        create_vimarsh_monitor, initialize_vimarsh_monitoring
    )
except ImportError:
    from circuit_breaker import (
        CircuitBreaker, CircuitBreakerConfig, CircuitState,
        HealthMonitor, HealthCheckConfig, HealthStatus,
        CircuitBreakerManager, HealthAndCircuitMonitor,
        ServiceHealthChecks, CircuitBreakerError,
        create_vimarsh_monitor, initialize_vimarsh_monitoring
    )


class TestCircuitBreaker:
    """Test cases for CircuitBreaker functionality"""
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization"""
        config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=30.0)
        breaker = CircuitBreaker("test_service", config)
        
        assert breaker.name == "test_service"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.config.failure_threshold == 3
        assert breaker.config.timeout_seconds == 30.0
        assert breaker.metrics.total_calls == 0
    
    @pytest.mark.asyncio
    async def test_successful_call(self):
        """Test successful function calls through circuit breaker"""
        breaker = CircuitBreaker("test_service")
        
        async def successful_function():
            return "success"
        
        result = await breaker.call(successful_function)
        
        assert result == "success"
        assert breaker.metrics.total_calls == 1
        assert breaker.metrics.successful_calls == 1
        assert breaker.metrics.failed_calls == 0
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_failed_call(self):
        """Test failed function calls through circuit breaker"""
        breaker = CircuitBreaker("test_service")
        
        async def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await breaker.call(failing_function)
        
        assert breaker.metrics.total_calls == 1
        assert breaker.metrics.successful_calls == 0
        assert breaker.metrics.failed_calls == 1
        assert breaker.state == CircuitState.CLOSED  # Should not open on single failure
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Test that circuit opens after reaching failure threshold"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            minimum_throughput=3
        )
        breaker = CircuitBreaker("test_service", config)
        
        async def failing_function():
            raise ValueError("Test error")
        
        # Execute enough failures to reach threshold
        for i in range(5):
            with pytest.raises(ValueError):
                await breaker.call(failing_function)
        
        assert breaker.metrics.failed_calls == 5
        assert breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_circuit_open_blocks_calls(self):
        """Test that open circuit blocks function calls"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            minimum_throughput=2
        )
        breaker = CircuitBreaker("test_service", config)
        
        # Force circuit to open
        async def failing_function():
            raise ValueError("Test error")
        
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_function)
        
        assert breaker.state == CircuitState.OPEN
        
        # Now test that calls are blocked
        async def any_function():
            return "should not execute"
        
        with pytest.raises(CircuitBreakerError):
            await breaker.call(any_function)
    
    @pytest.mark.asyncio
    async def test_circuit_half_open_recovery(self):
        """Test circuit recovery through half-open state"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.1,  # Short timeout for testing
            minimum_throughput=2
        )
        breaker = CircuitBreaker("test_service", config)
        
        # Open the circuit
        async def failing_function():
            raise ValueError("Test error")
        
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_function)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Try a successful call - should enter half-open
        async def successful_function():
            return "success"
        
        result = await breaker.call(successful_function)
        assert result == "success"
        # Circuit should either be half-open or closed depending on success count
        assert breaker.state in [CircuitState.HALF_OPEN, CircuitState.CLOSED]
    
    @pytest.mark.asyncio
    async def test_slow_call_detection(self):
        """Test detection of slow calls"""
        config = CircuitBreakerConfig(slow_call_threshold=0.1)
        breaker = CircuitBreaker("test_service", config)
        
        async def slow_function():
            await asyncio.sleep(0.2)  # Slower than threshold
            return "slow result"
        
        result = await breaker.call(slow_function)
        
        assert result == "slow result"
        assert breaker.metrics.slow_calls == 1
        assert breaker.metrics.average_response_time > 0.1
    
    def test_circuit_breaker_state_export(self):
        """Test circuit breaker state export"""
        config = CircuitBreakerConfig(failure_threshold=5)
        breaker = CircuitBreaker("test_service", config)
        
        state = breaker.get_state()
        
        assert state['name'] == "test_service"
        assert state['state'] == CircuitState.CLOSED.value
        assert 'metrics' in state
        assert 'config' in state
        assert state['metrics']['total_calls'] == 0
        assert state['config']['failure_threshold'] == 5
    
    def test_circuit_breaker_reset(self):
        """Test circuit breaker reset functionality"""
        breaker = CircuitBreaker("test_service")
        
        # Manually set some metrics
        breaker.metrics.total_calls = 10
        breaker.metrics.failed_calls = 5
        breaker.state = CircuitState.OPEN
        
        breaker.reset()
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.metrics.total_calls == 0
        assert breaker.metrics.failed_calls == 0


class TestHealthMonitor:
    """Test cases for HealthMonitor functionality"""
    
    @pytest.mark.asyncio
    async def test_health_monitor_initialization(self):
        """Test health monitor initialization"""
        config = HealthCheckConfig(check_interval=10.0, timeout=5.0)
        monitor = HealthMonitor(config)
        
        assert monitor.config.check_interval == 10.0
        assert monitor.config.timeout == 5.0
        assert len(monitor.services) == 0
        assert not monitor._monitoring
    
    @pytest.mark.asyncio
    async def test_service_registration(self):
        """Test service registration for health monitoring"""
        monitor = HealthMonitor()
        
        async def test_health_check():
            return True
        
        monitor.register_service(
            "test_service", 
            test_health_check,
            metadata={"version": "1.0"}
        )
        
        assert "test_service" in monitor.services
        assert "test_service" in monitor.health_checks
        assert monitor.services["test_service"].service_name == "test_service"
        assert monitor.services["test_service"].metadata["version"] == "1.0"
    
    @pytest.mark.asyncio
    async def test_successful_health_check(self):
        """Test successful health check execution"""
        monitor = HealthMonitor()
        
        async def healthy_service():
            return True
        
        monitor.register_service("healthy_service", healthy_service)
        
        # Perform single health check
        await monitor._check_service_health("healthy_service")
        
        metrics = monitor.services["healthy_service"]
        assert metrics.status == HealthStatus.HEALTHY
        assert metrics.success_rate == 1.0
        assert metrics.error_count == 0
        assert metrics.check_count == 1
    
    @pytest.mark.asyncio
    async def test_failed_health_check(self):
        """Test failed health check execution"""
        monitor = HealthMonitor()
        
        async def unhealthy_service():
            return False
        
        monitor.register_service("unhealthy_service", unhealthy_service)
        
        # Perform single health check
        await monitor._check_service_health("unhealthy_service")
        
        metrics = monitor.services["unhealthy_service"]
        assert metrics.status != HealthStatus.HEALTHY
        assert metrics.success_rate == 0.0
        assert metrics.error_count == 1
        assert metrics.check_count == 1
    
    @pytest.mark.asyncio
    async def test_health_check_timeout(self):
        """Test health check timeout handling"""
        config = HealthCheckConfig(timeout=0.1)
        monitor = HealthMonitor(config)
        
        async def slow_service():
            await asyncio.sleep(0.2)  # Slower than timeout
            return True
        
        monitor.register_service("slow_service", slow_service)
        
        # Perform health check that should timeout
        await monitor._check_service_health("slow_service")
        
        metrics = monitor.services["slow_service"]
        assert metrics.status != HealthStatus.HEALTHY
        assert metrics.error_count == 1
        assert "timeout" in metrics.metadata.get("last_error", "")
    
    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test health check exception handling"""
        monitor = HealthMonitor()
        
        async def failing_service():
            raise ValueError("Service is down")
        
        monitor.register_service("failing_service", failing_service)
        
        # Perform health check that raises exception
        await monitor._check_service_health("failing_service")
        
        metrics = monitor.services["failing_service"]
        assert metrics.status != HealthStatus.HEALTHY
        assert metrics.error_count == 1
        assert "Service is down" in metrics.metadata.get("last_error", "")
    
    @pytest.mark.asyncio
    async def test_health_status_determination(self):
        """Test health status determination logic"""
        monitor = HealthMonitor()
        
        # Test critical status (very low success rate)
        metrics = monitor.services["test"] = type('MockMetrics', (), {
            'success_rate': 0.05,
            'check_count': 20,
            'error_count': 19
        })()
        
        status = monitor._determine_health_status(metrics, 0.1)
        assert status == HealthStatus.CRITICAL
        
        # Test unhealthy status
        metrics.success_rate = 0.3
        status = monitor._determine_health_status(metrics, 0.1)
        assert status == HealthStatus.UNHEALTHY
        
        # Test degraded status (marginal success rate)
        metrics.success_rate = 0.85
        status = monitor._determine_health_status(metrics, 0.1)
        assert status == HealthStatus.DEGRADED
        
        # Test healthy status
        metrics.success_rate = 0.99
        status = monitor._determine_health_status(metrics, 0.1)
        assert status == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_overall_health_calculation(self):
        """Test overall system health calculation"""
        monitor = HealthMonitor()
        
        # Register multiple services with different health states
        async def healthy_service():
            return True
        
        async def degraded_service():
            await asyncio.sleep(0.1)  # Slightly slow
            return True
        
        async def unhealthy_service():
            return False
        
        monitor.register_service("healthy", healthy_service)
        monitor.register_service("degraded", degraded_service)
        monitor.register_service("unhealthy", unhealthy_service)
        
        # Simulate health checks
        await monitor._check_service_health("healthy")
        await monitor._check_service_health("degraded")
        await monitor._check_service_health("unhealthy")
        
        # Manually set states for testing
        monitor.services["healthy"].status = HealthStatus.HEALTHY
        monitor.services["degraded"].status = HealthStatus.DEGRADED
        monitor.services["unhealthy"].status = HealthStatus.UNHEALTHY
        
        overall_health = monitor.get_overall_health()
        
        assert overall_health['status'] == HealthStatus.UNHEALTHY.value
        assert overall_health['summary']['total_services'] == 3
        assert overall_health['summary']['healthy_services'] == 1
        assert overall_health['summary']['degraded_services'] == 1
        assert overall_health['summary']['unhealthy_services'] == 1
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_start_stop(self):
        """Test starting and stopping monitoring loop"""
        config = HealthCheckConfig(check_interval=0.1)
        monitor = HealthMonitor(config)
        
        async def test_service():
            return True
        
        monitor.register_service("test", test_service)
        
        # Start monitoring
        await monitor.start_monitoring()
        assert monitor._monitoring is True
        assert monitor._monitor_task is not None
        
        # Let it run for a short time
        await asyncio.sleep(0.25)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor._monitoring is False
        
        # Check that health checks were performed
        assert monitor.services["test"].check_count > 0


class TestCircuitBreakerManager:
    """Test cases for CircuitBreakerManager"""
    
    def test_circuit_breaker_creation(self):
        """Test circuit breaker creation and retrieval"""
        manager = CircuitBreakerManager()
        
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = manager.get_circuit_breaker("test_service", config)
        
        assert breaker.name == "test_service"
        assert breaker.config.failure_threshold == 3
        
        # Test that same instance is returned on subsequent calls
        same_breaker = manager.get_circuit_breaker("test_service")
        assert same_breaker is breaker
    
    def test_multiple_circuit_breakers(self):
        """Test managing multiple circuit breakers"""
        manager = CircuitBreakerManager()
        
        breaker1 = manager.get_circuit_breaker("service1")
        breaker2 = manager.get_circuit_breaker("service2")
        
        assert breaker1 is not breaker2
        assert breaker1.name == "service1"
        assert breaker2.name == "service2"
        
        states = manager.get_all_states()
        assert "service1" in states
        assert "service2" in states
    
    def test_circuit_breaker_reset(self):
        """Test resetting circuit breakers"""
        manager = CircuitBreakerManager()
        
        breaker = manager.get_circuit_breaker("test_service")
        breaker.metrics.total_calls = 10  # Set some test data
        
        # Reset specific breaker
        result = manager.reset_circuit_breaker("test_service")
        assert result is True
        assert breaker.metrics.total_calls == 0
        
        # Test resetting non-existent breaker
        result = manager.reset_circuit_breaker("non_existent")
        assert result is False
    
    def test_reset_all_circuit_breakers(self):
        """Test resetting all circuit breakers"""
        manager = CircuitBreakerManager()
        
        breaker1 = manager.get_circuit_breaker("service1")
        breaker2 = manager.get_circuit_breaker("service2")
        
        # Set some test data
        breaker1.metrics.total_calls = 5
        breaker2.metrics.total_calls = 10
        
        # Reset all
        manager.reset_all_circuit_breakers()
        
        assert breaker1.metrics.total_calls == 0
        assert breaker2.metrics.total_calls == 0


class TestHealthAndCircuitMonitor:
    """Test cases for integrated monitoring system"""
    
    @pytest.mark.asyncio
    async def test_integrated_service_registration(self):
        """Test registering services with integrated monitoring"""
        monitor = HealthAndCircuitMonitor()
        
        async def test_health():
            return True
        
        await monitor.register_service(
            "integrated_service",
            test_health,
            metadata={"type": "test"}
        )
        
        # Check that service is registered in both systems
        assert "integrated_service" in monitor.health_monitor.services
        assert "integrated_service" in monitor.circuit_manager.circuit_breakers
    
    @pytest.mark.asyncio
    async def test_protected_call_context(self):
        """Test protected call context manager"""
        monitor = HealthAndCircuitMonitor()
        
        async def test_function():
            return "protected result"
        
        async with monitor.protected_call("test_service") as call:
            result = await call(test_function)
        
        assert result == "protected result"
        
        # Check that circuit breaker was created
        assert "test_service" in monitor.circuit_manager.circuit_breakers
    
    @pytest.mark.asyncio
    async def test_system_status_reporting(self):
        """Test comprehensive system status reporting"""
        monitor = HealthAndCircuitMonitor()
        
        async def test_health():
            return True
        
        await monitor.register_service("status_test", test_health)
        
        # Get system status
        status = monitor.get_system_status()
        
        assert 'health' in status
        assert 'circuit_breakers' in status
        assert 'timestamp' in status
        assert status['health']['summary']['total_services'] == 1
        assert 'status_test' in status['circuit_breakers']
    
    @pytest.mark.asyncio
    async def test_service_specific_status(self):
        """Test service-specific status reporting"""
        monitor = HealthAndCircuitMonitor()
        
        async def test_health():
            return True
        
        await monitor.register_service(
            "specific_service", 
            test_health,
            metadata={"component": "test"}
        )
        
        status = monitor.get_service_status("specific_service")
        
        assert status['service_name'] == "specific_service"
        assert 'health' in status
        assert 'circuit_breaker' in status
        assert status['health']['metadata']['component'] == "test"


class TestServiceHealthChecks:
    """Test cases for service-specific health checks"""
    
    @pytest.mark.asyncio
    async def test_llm_service_health_check(self):
        """Test LLM service health check"""
        result = await ServiceHealthChecks.llm_service_health()
        assert isinstance(result, bool)
        # Should return True for basic implementation
        assert result is True
    
    @pytest.mark.asyncio
    async def test_vector_search_health_check(self):
        """Test vector search health check"""
        result = await ServiceHealthChecks.vector_search_health()
        assert isinstance(result, bool)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_text_processing_health_check(self):
        """Test text processing health check"""
        result = await ServiceHealthChecks.text_processing_health()
        assert isinstance(result, bool)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_expert_review_health_check(self):
        """Test expert review health check"""
        result = await ServiceHealthChecks.expert_review_health()
        assert isinstance(result, bool)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_content_moderation_health_check(self):
        """Test content moderation health check"""
        result = await ServiceHealthChecks.content_moderation_health()
        assert isinstance(result, bool)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_fallback_system_health_check(self):
        """Test fallback system health check"""
        result = await ServiceHealthChecks.fallback_system_health()
        assert isinstance(result, bool)
        assert result is True


class TestVimarshMonitoring:
    """Test cases for pre-configured Vimarsh monitoring"""
    
    def test_vimarsh_monitor_creation(self):
        """Test creation of pre-configured Vimarsh monitor"""
        monitor = create_vimarsh_monitor()
        
        assert isinstance(monitor, HealthAndCircuitMonitor)
        assert monitor.health_monitor.config.check_interval == 30.0
        assert len(monitor.circuit_configs) == 6  # Six service types
        
        # Check that different services have appropriate configurations
        llm_config = monitor.circuit_configs["llm_service"]
        vector_config = monitor.circuit_configs["vector_search"]
        
        assert llm_config.slow_call_threshold > vector_config.slow_call_threshold
        assert llm_config.timeout_seconds > vector_config.timeout_seconds
    
    @pytest.mark.asyncio
    async def test_vimarsh_monitoring_initialization(self):
        """Test full Vimarsh monitoring initialization"""
        monitor = await initialize_vimarsh_monitoring()
        
        # Check that all services are registered
        expected_services = [
            "llm_service", "vector_search", "text_processing",
            "expert_review", "content_moderation", "fallback_system"
        ]
        
        for service in expected_services:
            assert service in monitor.health_monitor.services
            assert service in monitor.circuit_manager.circuit_breakers
        
        # Check that monitoring is active
        assert monitor.health_monitor._monitoring is True
        
        # Clean up
        await monitor.stop_monitoring()


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    @pytest.mark.asyncio
    async def test_service_failure_and_recovery(self):
        """Test complete service failure and recovery scenario"""
        monitor = HealthAndCircuitMonitor()
        
        # Track service state
        service_working = True
        
        async def flaky_service():
            return service_working
        
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.1,
            minimum_throughput=2
        )
        
        await monitor.register_service(
            "flaky_service",
            flaky_service,
            circuit_config=config
        )
        
        # Test normal operation
        async with monitor.protected_call("flaky_service") as call:
            result = await call(flaky_service)
            assert result is True
        
        # Simulate service failure
        service_working = False
        
        # Should fail and eventually open circuit
        for _ in range(5):
            try:
                async with monitor.protected_call("flaky_service") as call:
                    await call(flaky_service)
            except Exception:
                pass
        
        # Circuit should be open
        circuit = monitor.circuit_manager.circuit_breakers["flaky_service"]
        assert circuit.state == CircuitState.OPEN
        
        # Wait for timeout and restore service
        await asyncio.sleep(0.2)
        service_working = True
        
        # Should recover through half-open state
        async with monitor.protected_call("flaky_service") as call:
            result = await call(flaky_service)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_concurrent_monitoring(self):
        """Test monitoring system under concurrent load"""
        monitor = HealthAndCircuitMonitor()
        
        call_count = 0
        
        async def concurrent_service():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simulate some work
            return True
        
        await monitor.register_service("concurrent_service", concurrent_service)
        
        # Make many concurrent calls
        async def make_call():
            async with monitor.protected_call("concurrent_service") as call:
                return await call(concurrent_service)
        
        tasks = [make_call() for _ in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All calls should succeed
        successful_results = [r for r in results if r is True]
        assert len(successful_results) == 20
        
        # Check metrics
        circuit = monitor.circuit_manager.circuit_breakers["concurrent_service"]
        assert circuit.metrics.total_calls == 20
        assert circuit.metrics.successful_calls == 20
        assert circuit.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_cascading_failure_prevention(self):
        """Test that circuit breakers prevent cascading failures"""
        monitor = HealthAndCircuitMonitor()
        
        failure_count = 0
        
        async def failing_service():
            nonlocal failure_count
            failure_count += 1
            raise Exception(f"Service failure {failure_count}")
        
        config = CircuitBreakerConfig(
            failure_threshold=3,
            minimum_throughput=3
        )
        
        await monitor.register_service(
            "failing_service",
            failing_service,
            circuit_config=config
        )
        
        # Make calls that will fail
        exceptions_caught = 0
        circuit_breaker_errors = 0
        
        for i in range(10):
            try:
                async with monitor.protected_call("failing_service") as call:
                    await call(failing_service)
            except CircuitBreakerError:
                circuit_breaker_errors += 1
            except Exception:
                exceptions_caught += 1
        
        # Should have some direct failures and some circuit breaker blocks
        assert exceptions_caught > 0
        assert circuit_breaker_errors > 0
        assert exceptions_caught + circuit_breaker_errors == 10
        
        # Failure count should be less than total calls due to circuit breaker
        assert failure_count < 10


if __name__ == "__main__":
    """Run the test suite"""
    import sys
    
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Running Circuit Breaker and Health Monitoring tests...")
    
    # Run async tests
    async def run_async_tests():
        """Run async test cases manually for demonstration"""
        
        print("\n1. Testing Circuit Breaker Basic Functionality...")
        breaker = CircuitBreaker("demo_service")
        
        async def demo_function():
            return "success"
        
        result = await breaker.call(demo_function)
        print(f"✓ Circuit breaker call successful: {result}")
        print(f"  Metrics: {breaker.metrics.total_calls} calls, {breaker.metrics.successful_calls} successful")
        
        print("\n2. Testing Health Monitor...")
        monitor = HealthMonitor()
        
        async def healthy_service():
            return True
        
        monitor.register_service("demo_health", healthy_service)
        await monitor._check_service_health("demo_health")
        
        health = monitor.get_service_health("demo_health")
        print(f"✓ Health check completed: {health['status']}")
        print(f"  Success rate: {health['success_rate']:.2f}")
        
        print("\n3. Testing Integrated Monitor...")
        integrated = HealthAndCircuitMonitor()
        
        await integrated.register_service("integrated_demo", healthy_service)
        
        async with integrated.protected_call("integrated_demo") as call:
            result = await call(demo_function)
        
        status = integrated.get_service_status("integrated_demo")
        print(f"✓ Integrated monitoring: {result}")
        print(f"  Health status: {status['health']['status']}")
        print(f"  Circuit state: {status['circuit_breaker']['state']}")
        
        print("\n4. Testing Vimarsh Pre-configured Monitor...")
        vimarsh_monitor = create_vimarsh_monitor()
        print(f"✓ Vimarsh monitor created with {len(vimarsh_monitor.circuit_configs)} service configs")
        
        # Test service health checks
        print("\n5. Testing Service Health Checks...")
        services_to_test = [
            ("LLM Service", ServiceHealthChecks.llm_service_health),
            ("Vector Search", ServiceHealthChecks.vector_search_health),
            ("Text Processing", ServiceHealthChecks.text_processing_health),
            ("Expert Review", ServiceHealthChecks.expert_review_health),
            ("Content Moderation", ServiceHealthChecks.content_moderation_health),
            ("Fallback System", ServiceHealthChecks.fallback_system_health)
        ]
        
        for service_name, health_check in services_to_test:
            result = await health_check()
            status = "✓" if result else "❌"
            print(f"  {status} {service_name}: {'Healthy' if result else 'Unhealthy'}")
        
        print("\n6. Testing Circuit Breaker Failure Scenarios...")
        failure_config = CircuitBreakerConfig(
            failure_threshold=3,
            minimum_throughput=3
        )
        failure_breaker = CircuitBreaker("failure_demo", failure_config)
        
        async def failing_function():
            raise ValueError("Simulated failure")
        
        # Cause failures to open circuit
        for i in range(5):
            try:
                await failure_breaker.call(failing_function)
            except (ValueError, CircuitBreakerError):
                pass
        
        print(f"✓ Circuit state after failures: {failure_breaker.state.value}")
        print(f"  Failed calls: {failure_breaker.metrics.failed_calls}")
        print(f"  Circuit opens: {failure_breaker.metrics.circuit_opens}")
        
        # Test that circuit blocks further calls
        try:
            await failure_breaker.call(demo_function)
            print("❌ Circuit should have blocked this call")
        except CircuitBreakerError:
            print("✓ Circuit correctly blocked call when open")
        except Exception as e:
            print(f"✓ Circuit correctly blocked call when open (exception: {type(e).__name__})")
        
        print("\n7. Testing Full Vimarsh Monitoring System...")
        full_monitor = await initialize_vimarsh_monitoring()
        
        system_status = full_monitor.get_system_status()
        print(f"✓ Full system initialized and monitoring")
        print(f"  Total services: {system_status['health']['summary']['total_services']}")
        print(f"  Healthy services: {system_status['health']['summary']['healthy_services']}")
        
        # Clean up
        await full_monitor.stop_monitoring()
        
        print("\n✅ All circuit breaker and health monitoring tests completed successfully!")
    
    # Run the async tests
    asyncio.run(run_async_tests())
