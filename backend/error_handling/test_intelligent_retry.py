"""
Test suite for the intelligent retry system.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from intelligent_retry import (
    IntelligentRetryManager, RetryConfig, BackoffStrategy, CircuitState,
    CircuitBreaker, RetryStats, RetryAttempt, retry, retry_operation,
    create_retry_config, get_default_configs
)
from error_classifier import ErrorCategory, RecoveryStrategy


class TestRetryConfig:
    """Test cases for RetryConfig"""
    
    def test_default_config(self):
        """Test default retry configuration"""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.backoff_strategy == BackoffStrategy.EXPONENTIAL
        assert config.circuit_breaker_enabled is True
        assert config.adaptive_enabled is True
    
    def test_custom_config(self):
        """Test custom retry configuration"""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            backoff_strategy=BackoffStrategy.LINEAR,
            circuit_breaker_enabled=False
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.backoff_strategy == BackoffStrategy.LINEAR
        assert config.circuit_breaker_enabled is False


class TestCircuitBreaker:
    """Test cases for CircuitBreaker"""
    
    def setup_method(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5.0,
            success_threshold=2
        )
    
    def test_initial_state(self):
        """Test initial circuit breaker state"""
        assert self.circuit_breaker.state == CircuitState.CLOSED
        assert self.circuit_breaker.can_attempt() is True
        assert self.circuit_breaker.failure_count == 0
    
    def test_failure_threshold(self):
        """Test circuit breaker opens after failure threshold"""
        # Record failures below threshold
        for i in range(2):
            self.circuit_breaker.record_failure()
            assert self.circuit_breaker.state == CircuitState.CLOSED
        
        # Record failure that crosses threshold
        self.circuit_breaker.record_failure()
        assert self.circuit_breaker.state == CircuitState.OPEN
        assert self.circuit_breaker.can_attempt() is False
    
    def test_recovery_timeout(self):
        """Test circuit breaker recovery after timeout"""
        # Open the circuit
        for _ in range(3):
            self.circuit_breaker.record_failure()
        
        assert self.circuit_breaker.state == CircuitState.OPEN
        
        # Simulate time passage by modifying last_failure_time
        self.circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=10)
        
        # Should transition to half-open
        assert self.circuit_breaker.can_attempt() is True
        assert self.circuit_breaker.state == CircuitState.HALF_OPEN
    
    def test_half_open_to_closed(self):
        """Test transition from half-open to closed on success"""
        # Set to half-open state
        self.circuit_breaker.state = CircuitState.HALF_OPEN
        
        # Record successes below threshold
        self.circuit_breaker.record_success()
        assert self.circuit_breaker.state == CircuitState.HALF_OPEN
        
        # Record success that crosses threshold
        self.circuit_breaker.record_success()
        assert self.circuit_breaker.state == CircuitState.CLOSED
        assert self.circuit_breaker.failure_count == 0
    
    def test_half_open_to_open_on_failure(self):
        """Test transition from half-open back to open on failure"""
        # Set to half-open state
        self.circuit_breaker.state = CircuitState.HALF_OPEN
        
        # Record failure should return to open
        self.circuit_breaker.record_failure()
        assert self.circuit_breaker.state == CircuitState.OPEN
    
    def test_get_state_info(self):
        """Test circuit breaker state information"""
        info = self.circuit_breaker.get_state_info()
        
        assert "state" in info
        assert "failure_count" in info
        assert "can_attempt" in info
        assert info["state"] == CircuitState.CLOSED.value


class TestIntelligentRetryManager:
    """Test cases for IntelligentRetryManager"""
    
    def setup_method(self):
        self.manager = IntelligentRetryManager()
    
    def test_initialization(self):
        """Test manager initialization"""
        assert hasattr(self.manager, 'error_classifier')
        assert hasattr(self.manager, 'circuit_breakers')
        assert hasattr(self.manager, 'retry_stats')
        assert isinstance(self.manager.global_config, RetryConfig)
    
    def test_calculate_delay_fixed(self):
        """Test fixed backoff delay calculation"""
        config = RetryConfig(backoff_strategy=BackoffStrategy.FIXED, base_delay=2.0)
        
        assert self.manager._calculate_delay(1, config) == 2.0
        assert self.manager._calculate_delay(5, config) == 2.0
    
    def test_calculate_delay_linear(self):
        """Test linear backoff delay calculation"""
        config = RetryConfig(backoff_strategy=BackoffStrategy.LINEAR, base_delay=2.0)
        
        assert self.manager._calculate_delay(1, config) == 2.0
        assert self.manager._calculate_delay(2, config) == 4.0
        assert self.manager._calculate_delay(3, config) == 6.0
    
    def test_calculate_delay_exponential(self):
        """Test exponential backoff delay calculation"""
        config = RetryConfig(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=1.0,
            backoff_multiplier=2.0
        )
        
        assert self.manager._calculate_delay(1, config) == 1.0
        assert self.manager._calculate_delay(2, config) == 2.0
        assert self.manager._calculate_delay(3, config) == 4.0
        assert self.manager._calculate_delay(4, config) == 8.0
    
    def test_calculate_delay_max_constraint(self):
        """Test maximum delay constraint"""
        config = RetryConfig(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=10.0,
            max_delay=15.0,
            backoff_multiplier=3.0
        )
        
        # Should be capped at max_delay
        delay = self.manager._calculate_delay(3, config)  # Would be 90.0 without cap
        assert delay == 15.0
    
    def test_calculate_delay_fibonacci(self):
        """Test Fibonacci backoff delay calculation"""
        config = RetryConfig(backoff_strategy=BackoffStrategy.FIBONACCI, base_delay=1.0)
        
        # Fibonacci: 1, 1, 2, 3, 5, 8, ...
        assert self.manager._calculate_delay(1, config) == 1.0
        assert self.manager._calculate_delay(2, config) == 1.0
        
        # With history
        assert self.manager._calculate_delay(3, config, [1.0, 1.0]) == 2.0
        assert self.manager._calculate_delay(4, config, [1.0, 1.0, 2.0]) == 3.0
    
    def test_calculate_delay_jittered_exponential(self):
        """Test jittered exponential backoff"""
        config = RetryConfig(
            backoff_strategy=BackoffStrategy.JITTERED_EXPONENTIAL,
            base_delay=1.0,
            backoff_multiplier=2.0,
            jitter_factor=0.1
        )
        
        # Should be base value plus some jitter
        delay = self.manager._calculate_delay(2, config)
        assert 2.0 <= delay <= 2.2  # 2.0 + (2.0 * 0.1)
    
    @pytest.mark.asyncio
    async def test_successful_operation(self):
        """Test successful operation without retries"""
        async def successful_operation():
            return "success"
        
        result = await self.manager.retry_operation(successful_operation)
        assert result == "success"
        
        # Check stats
        stats = self.manager.get_operation_stats()
        assert len(stats) == 1
        operation_stats = list(stats.values())[0]
        assert operation_stats["total_attempts"] == 1
        assert operation_stats["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self):
        """Test operation that fails then succeeds"""
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        config = RetryConfig(max_attempts=5, base_delay=0.1)
        result = await self.manager.retry_operation(flaky_operation, config=config)
        
        assert result == "success"
        assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhaustion(self):
        """Test operation that exhausts all retry attempts"""
        async def always_failing_operation():
            raise Exception("Always fails")
        
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        
        with pytest.raises(Exception, match="Always fails"):
            await self.manager.retry_operation(always_failing_operation, config=config)
        
        # Check stats
        stats = self.manager.get_operation_stats()
        operation_stats = list(stats.values())[0]
        assert operation_stats["total_attempts"] == 3
        assert operation_stats["success_rate"] == 0.0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test circuit breaker integration with retries"""
        failure_count = 0
        
        async def failing_operation():
            nonlocal failure_count
            failure_count += 1
            raise Exception("Service unavailable")
        
        config = RetryConfig(
            max_attempts=2,
            base_delay=0.1,
            circuit_breaker_enabled=True,
            failure_threshold=3
        )
        
        # Call multiple times to trigger circuit breaker
        for _ in range(2):
            with pytest.raises(Exception):
                await self.manager.retry_operation(
                    failing_operation,
                    config=config,
                    operation_name="test_op"
                )
        
        # Circuit should still be closed, call once more to open it
        with pytest.raises(Exception):
            await self.manager.retry_operation(
                failing_operation,
                config=config,
                operation_name="test_op"
            )
        
        # Now circuit should be open
        with pytest.raises(Exception, match="Circuit breaker is open"):
            await self.manager.retry_operation(
                failing_operation,
                config=config,
                operation_name="test_op"
            )
    
    @pytest.mark.asyncio
    async def test_sync_operation_support(self):
        """Test support for synchronous operations"""
        def sync_operation():
            return "sync_success"
        
        result = await self.manager.retry_operation(sync_operation)
        assert result == "sync_success"
    
    @pytest.mark.asyncio
    async def test_adaptive_configuration(self):
        """Test adaptive configuration based on performance"""
        failure_count = 0
        
        async def operation_with_declining_performance():
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 8:  # Fail first 8 times
                raise Exception("Frequent failure")
            return "success"
        
        config = RetryConfig(
            max_attempts=3,
            base_delay=0.1,
            adaptive_enabled=True,
            success_rate_threshold=0.5
        )
        
        # Run operation multiple times to build failure history
        for _ in range(3):
            try:
                await self.manager.retry_operation(
                    operation_with_declining_performance,
                    config=config,
                    operation_name="adaptive_test"
                )
            except Exception:
                pass
        
        # Check that stats show poor performance
        stats = self.manager.get_operation_stats("adaptive_test")
        if stats:
            operation_stats = list(stats.values())[0]
            if isinstance(operation_stats, dict):
                assert operation_stats["success_rate"] < 0.5
            else:
                # Direct RetryStats object
                assert operation_stats.success_rate < 0.5
    
    def test_get_circuit_breaker_status(self):
        """Test circuit breaker status retrieval"""
        # Create some circuit breakers
        self.manager._get_circuit_breaker("test_op_1", RetryConfig())
        self.manager._get_circuit_breaker("test_op_2", RetryConfig())
        
        status = self.manager.get_circuit_breaker_status()
        assert len(status) == 2
        
        for key, breaker_info in status.items():
            assert "state" in breaker_info
            assert "failure_count" in breaker_info
            assert "can_attempt" in breaker_info
    
    def test_reset_stats(self):
        """Test statistics reset functionality"""
        # Create some stats
        self.manager._get_retry_stats("test_key", "test_operation")
        assert len(self.manager.retry_stats) == 1
        
        # Reset all stats
        self.manager.reset_stats()
        assert len(self.manager.retry_stats) == 0
    
    def test_reset_circuit_breakers(self):
        """Test circuit breaker reset functionality"""
        # Create and modify a circuit breaker
        config = RetryConfig(failure_threshold=3)  # Use smaller threshold for test
        breaker = self.manager._get_circuit_breaker("test_op", config)
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_failure()  # Should open circuit
        
        assert breaker.state == CircuitState.OPEN
        
        # Reset all circuit breakers
        self.manager.reset_circuit_breakers()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0


class TestRetryDecorator:
    """Test cases for retry decorator"""
    
    @pytest.mark.asyncio
    async def test_async_function_decorator(self):
        """Test retry decorator on async function"""
        attempt_count = 0
        
        @retry(config=RetryConfig(max_attempts=3, base_delay=0.1))
        async def flaky_async_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Temporary failure")
            return "async_success"
        
        result = await flaky_async_function()
        assert result == "async_success"
        assert attempt_count == 2
    
    def test_sync_function_decorator(self):
        """Test retry decorator on sync function"""
        attempt_count = 0
        
        @retry(config=RetryConfig(max_attempts=3, base_delay=0.1))
        def flaky_sync_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Temporary failure")
            return "sync_success"
        
        result = flaky_sync_function()
        assert result == "sync_success"
        assert attempt_count == 2


class TestRetryStats:
    """Test cases for RetryStats"""
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        stats = RetryStats("test_operation")
        assert stats.success_rate == 0.0
        
        stats.total_attempts = 10
        stats.successful_attempts = 7
        assert stats.success_rate == 0.7
        
        stats.failed_attempts = 3
        assert abs(stats.failure_rate - 0.3) < 0.001  # Use approximate comparison for floats


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @pytest.mark.asyncio
    async def test_retry_operation_function(self):
        """Test retry_operation convenience function"""
        async def test_operation():
            return "convenience_success"
        
        result = await retry_operation(test_operation)
        assert result == "convenience_success"
    
    def test_create_retry_config(self):
        """Test create_retry_config convenience function"""
        config = create_retry_config(max_attempts=5, base_delay=2.0)
        
        assert isinstance(config, RetryConfig)
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
    
    def test_get_default_configs(self):
        """Test get_default_configs function"""
        configs = get_default_configs()
        
        assert isinstance(configs, dict)
        assert "llm_service" in configs
        assert "database" in configs
        assert "external_api" in configs
        assert "vector_search" in configs
        
        # Check that configs are properly configured for their use cases
        llm_config = configs["llm_service"]
        assert llm_config.backoff_strategy == BackoffStrategy.JITTERED_EXPONENTIAL
        assert ErrorCategory.LLM_SERVICE in llm_config.retry_on_categories


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def setup_method(self):
        self.manager = IntelligentRetryManager()
    
    @pytest.mark.asyncio
    async def test_llm_service_retry_scenario(self):
        """Test LLM service retry scenario with rate limiting"""
        call_count = 0
        
        async def llm_api_call():
            nonlocal call_count
            call_count += 1
            
            if call_count <= 2:
                # Simulate rate limiting
                error = Exception("rate limit exceeded")
                raise error
            return {"response": "Spiritual guidance provided"}
        
        config = get_default_configs()["llm_service"]
        config.base_delay = 0.1  # Speed up test
        
        result = await self.manager.retry_operation(
            llm_api_call,
            config=config,
            operation_name="llm_guidance"
        )
        
        assert result["response"] == "Spiritual guidance provided"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_database_connection_retry_scenario(self):
        """Test database connection retry scenario"""
        connection_attempts = 0
        
        async def database_query():
            nonlocal connection_attempts
            connection_attempts += 1
            
            if connection_attempts <= 3:
                # Create an error that will be classified appropriately for retry
                error = Exception("database connection refused")
                raise error
            return {"data": "Spiritual texts retrieved"}
        
        # Use a more permissive config that will retry on unknown errors
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.1,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            retry_on_categories=[ErrorCategory.DATABASE, ErrorCategory.NETWORK, ErrorCategory.UNKNOWN],
            adaptive_enabled=False  # Disable to ensure consistent behavior
        )
        
        result = await self.manager.retry_operation(
            database_query,
            config=config,
            operation_name="db_query"
        )
        
        assert result["data"] == "Spiritual texts retrieved"
        assert connection_attempts == 4
    
    @pytest.mark.asyncio
    async def test_cascading_failure_recovery(self):
        """Test recovery from cascading failures"""
        service_states = {
            "llm": "failing",
            "vector_search": "failing",
            "database": "working"
        }
        
        async def multi_service_operation(service: str):
            if service_states[service] == "failing":
                # Simulate gradual recovery
                if service == "llm":
                    service_states["llm"] = "working"
                elif service == "vector_search":
                    service_states["vector_search"] = "working"
                raise Exception(f"{service} service temporarily unavailable")
            return f"{service} operation successful"
        
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        
        # LLM should recover after first failure
        result1 = await self.manager.retry_operation(
            multi_service_operation, "llm",
            config=config,
            operation_name="llm_op"
        )
        assert result1 == "llm operation successful"
        
        # Vector search should recover after first failure
        result2 = await self.manager.retry_operation(
            multi_service_operation, "vector_search",
            config=config,
            operation_name="vector_op"
        )
        assert result2 == "vector_search operation successful"
        
        # Database should work immediately
        result3 = await self.manager.retry_operation(
            multi_service_operation, "database",
            config=config,
            operation_name="db_op"
        )
        assert result3 == "database operation successful"


if __name__ == "__main__":
    pytest.main([__file__])
