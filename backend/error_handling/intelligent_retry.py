"""
Intelligent Retry Mechanisms with Exponential Backoff for Vimarsh AI Agent

This module provides sophisticated retry mechanisms that intelligently handle
transient failures with configurable backoff strategies, circuit breakers,
and adaptive retry logic based on error types and service characteristics.
"""

import logging
import asyncio
import time
import random
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import functools
import inspect

from .error_classifier import ErrorClassifier, ErrorCategory, RecoveryStrategy, ClassifiedError

logger = logging.getLogger(__name__)


class BackoffStrategy(Enum):
    """Types of backoff strategies"""
    FIXED = "fixed"                    # Fixed delay between retries
    LINEAR = "linear"                  # Linear increase in delay
    EXPONENTIAL = "exponential"        # Exponential backoff
    FIBONACCI = "fibonacci"            # Fibonacci sequence backoff
    JITTERED_EXPONENTIAL = "jittered_exponential"  # Exponential with random jitter


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Circuit is open, rejecting requests
    HALF_OPEN = "half_open" # Testing if service has recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay between retries
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1  # Random jitter (0.0 to 1.0)
    
    # Conditional retry settings
    retry_on_exceptions: List[str] = field(default_factory=lambda: ["Exception"])
    retry_on_status_codes: List[int] = field(default_factory=lambda: [500, 502, 503, 504, 429])
    retry_on_categories: List[ErrorCategory] = field(default_factory=lambda: [
        ErrorCategory.NETWORK, ErrorCategory.EXTERNAL_API, ErrorCategory.LLM_SERVICE
    ])
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: float = 60.0  # Seconds before attempting recovery
    success_threshold: int = 3  # Successes needed to close circuit
    
    # Adaptive settings
    adaptive_enabled: bool = True
    success_rate_threshold: float = 0.5  # Minimum success rate to continue retrying


@dataclass
class RetryAttempt:
    """Information about a retry attempt"""
    attempt_number: int
    delay: float
    timestamp: datetime
    error: Optional[Exception] = None
    success: bool = False
    response_time: float = 0.0


@dataclass
class RetryStats:
    """Statistics for retry operations"""
    operation_name: str
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    total_delay: float = 0.0
    average_response_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    attempts_history: List[RetryAttempt] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_attempts / self.total_attempts
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate"""
        return 1.0 - self.success_rate


class CircuitBreaker:
    """Circuit breaker implementation for retry mechanisms"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state_change_time = datetime.now()
    
    def can_attempt(self) -> bool:
        """Check if an attempt is allowed based on circuit state"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker transitioning to HALF_OPEN state")
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Record a successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED - service recovered")
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.state_change_time = datetime.now()
                logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
        elif self.state == CircuitState.HALF_OPEN:
            # Return to open state if failure occurs during testing
            self.state = CircuitState.OPEN
            self.state_change_time = datetime.now()
            logger.warning("Circuit breaker returned to OPEN state after test failure")
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get circuit breaker state information"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "state_change_time": self.state_change_time.isoformat(),
            "can_attempt": self.can_attempt()
        }


class IntelligentRetryManager:
    """Main manager for intelligent retry mechanisms"""
    
    def __init__(self):
        self.error_classifier = ErrorClassifier()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_stats: Dict[str, RetryStats] = {}
        self.global_config = RetryConfig()
    
    def _get_operation_key(self, operation_name: str, *args, **kwargs) -> str:
        """Generate a unique key for operation tracking"""
        # Create a simple hash of operation and parameters
        import hashlib
        key_data = f"{operation_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()[:12]
    
    def _get_circuit_breaker(self, operation_key: str, config: RetryConfig) -> CircuitBreaker:
        """Get or create circuit breaker for operation"""
        if operation_key not in self.circuit_breakers:
            self.circuit_breakers[operation_key] = CircuitBreaker(
                failure_threshold=config.failure_threshold,
                recovery_timeout=config.recovery_timeout,
                success_threshold=config.success_threshold
            )
        return self.circuit_breakers[operation_key]
    
    def _get_retry_stats(self, operation_key: str, operation_name: str) -> RetryStats:
        """Get or create retry statistics for operation"""
        if operation_key not in self.retry_stats:
            self.retry_stats[operation_key] = RetryStats(operation_name=operation_name)
        return self.retry_stats[operation_key]
    
    def _calculate_delay(self, 
                        attempt: int, 
                        config: RetryConfig,
                        previous_delays: List[float] = None) -> float:
        """Calculate delay for retry attempt based on backoff strategy"""
        
        if config.backoff_strategy == BackoffStrategy.FIXED:
            delay = config.base_delay
        
        elif config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = config.base_delay * attempt
        
        elif config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        
        elif config.backoff_strategy == BackoffStrategy.FIBONACCI:
            # Fibonacci sequence for delays
            if attempt <= 2:
                delay = config.base_delay
            else:
                if previous_delays and len(previous_delays) >= 2:
                    delay = previous_delays[-1] + previous_delays[-2]
                else:
                    # Fallback to exponential if no history
                    delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        
        elif config.backoff_strategy == BackoffStrategy.JITTERED_EXPONENTIAL:
            # Exponential with random jitter
            base_delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
            jitter = base_delay * config.jitter_factor * random.random()
            delay = base_delay + jitter
        
        else:
            delay = config.base_delay
        
        # Apply maximum delay constraint
        return min(delay, config.max_delay)
    
    def _should_retry(self, 
                     error: Exception, 
                     classified_error: ClassifiedError,
                     config: RetryConfig,
                     attempt: int) -> bool:
        """Determine if operation should be retried"""
        
        # Check max attempts
        if attempt >= config.max_attempts:
            return False
        
        # Check if recovery strategy allows retry (be more permissive for general exceptions)
        if (classified_error.recovery_strategy == RecoveryStrategy.FAIL_FAST and 
            classified_error.category not in [ErrorCategory.UNKNOWN]):
            return False
        
        # Check exception type - be more permissive for general exceptions
        exception_type = type(error).__name__
        if (config.retry_on_exceptions and 
            config.retry_on_exceptions != ["Exception"] and  # If not default, check specifically
            not any(exc_type in exception_type for exc_type in config.retry_on_exceptions)):
            return False
        
        # For unknown errors or general exceptions, allow retry unless explicitly prohibited
        if classified_error.category == ErrorCategory.UNKNOWN:
            return True
        
        # Check error category
        if config.retry_on_categories and classified_error.category not in config.retry_on_categories:
            return False
        
        return True
    
    def _adapt_config(self, 
                     config: RetryConfig, 
                     stats: RetryStats,
                     classified_error: ClassifiedError) -> RetryConfig:
        """Adapt retry configuration based on historical performance"""
        
        if not config.adaptive_enabled:
            return config
        
        adapted_config = config
        
        # Reduce max attempts if success rate is low
        if stats.total_attempts > 10 and stats.success_rate < config.success_rate_threshold:
            adapted_config.max_attempts = max(1, config.max_attempts - 1)
            logger.info(f"Adapted max_attempts to {adapted_config.max_attempts} due to low success rate")
        
        # Increase delay for frequently failing operations
        if stats.failure_rate > 0.7 and stats.total_attempts > 5:
            adapted_config.base_delay = min(config.base_delay * 1.5, config.max_delay / 4)
            logger.info(f"Adapted base_delay to {adapted_config.base_delay} due to high failure rate")
        
        # Use exponential backoff for rate limit errors
        if classified_error.category == ErrorCategory.RATE_LIMITING:
            adapted_config.backoff_strategy = BackoffStrategy.JITTERED_EXPONENTIAL
            adapted_config.base_delay = max(adapted_config.base_delay, 5.0)
        
        return adapted_config
    
    async def retry_operation(self,
                            operation: Callable,
                            *args,
                            operation_name: Optional[str] = None,
                            config: Optional[RetryConfig] = None,
                            **kwargs) -> Any:
        """
        Execute operation with intelligent retry logic
        
        Args:
            operation: The operation to execute (can be sync or async)
            *args: Arguments to pass to operation
            operation_name: Name for tracking/logging
            config: Retry configuration (uses global config if None)
            **kwargs: Keyword arguments to pass to operation
            
        Returns:
            Result of successful operation execution
            
        Raises:
            Exception: The last exception if all retries failed
        """
        
        if config is None:
            config = self.global_config
        
        if operation_name is None:
            operation_name = getattr(operation, '__name__', 'unnamed_operation')
        
        operation_key = self._get_operation_key(operation_name, *args, **kwargs)
        circuit_breaker = self._get_circuit_breaker(operation_key, config)
        stats = self._get_retry_stats(operation_key, operation_name)
        
        # Check circuit breaker
        if config.circuit_breaker_enabled and not circuit_breaker.can_attempt():
            logger.warning(f"Circuit breaker OPEN for operation {operation_name}")
            raise Exception(f"Circuit breaker is open for {operation_name}")
        
        attempt = 0
        last_error = None
        previous_delays = []
        
        while attempt < config.max_attempts:
            attempt += 1
            start_time = time.time()
            
            try:
                # Execute operation (handle both sync and async)
                if inspect.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)
                
                # Success!
                response_time = time.time() - start_time
                
                # Record success
                retry_attempt = RetryAttempt(
                    attempt_number=attempt,
                    delay=0.0,
                    timestamp=datetime.now(),
                    success=True,
                    response_time=response_time
                )
                
                stats.total_attempts += 1
                stats.successful_attempts += 1
                stats.last_success = datetime.now()
                stats.attempts_history.append(retry_attempt)
                
                # Update circuit breaker
                if config.circuit_breaker_enabled:
                    circuit_breaker.record_success()
                
                logger.info(f"Operation {operation_name} succeeded on attempt {attempt}")
                return result
                
            except Exception as error:
                response_time = time.time() - start_time
                last_error = error
                
                # Classify the error
                classified_error = self.error_classifier.classify_error(error)
                
                # Adapt configuration based on history
                adapted_config = self._adapt_config(config, stats, classified_error)
                
                # Check if we should retry
                should_retry = self._should_retry(error, classified_error, adapted_config, attempt)
                
                if not should_retry or attempt >= adapted_config.max_attempts:
                    # Record final failure
                    stats.total_attempts += 1
                    stats.failed_attempts += 1
                    stats.last_failure = datetime.now()
                    
                    retry_attempt = RetryAttempt(
                        attempt_number=attempt,
                        delay=0.0,
                        timestamp=datetime.now(),
                        error=error,
                        success=False,
                        response_time=response_time
                    )
                    stats.attempts_history.append(retry_attempt)
                    
                    # Update circuit breaker
                    if config.circuit_breaker_enabled:
                        circuit_breaker.record_failure()
                    
                    logger.error(f"Operation {operation_name} failed after {attempt} attempts: {str(error)}")
                    raise error
                
                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt, adapted_config, previous_delays)
                previous_delays.append(delay)
                
                # Record retry attempt
                retry_attempt = RetryAttempt(
                    attempt_number=attempt,
                    delay=delay,
                    timestamp=datetime.now(),
                    error=error,
                    success=False,
                    response_time=response_time
                )
                
                stats.total_attempts += 1
                stats.failed_attempts += 1
                stats.total_delay += delay
                stats.attempts_history.append(retry_attempt)
                
                logger.warning(f"Operation {operation_name} failed on attempt {attempt}: {str(error)}. "
                              f"Retrying in {delay:.2f} seconds...")
                
                # Wait before retry
                await asyncio.sleep(delay)
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        else:
            raise Exception(f"Operation {operation_name} failed after {config.max_attempts} attempts")
    
    def get_operation_stats(self, operation_name: str = None) -> Dict[str, Any]:
        """Get retry statistics for operations"""
        if operation_name:
            # Find stats for specific operation
            matching_stats = {
                key: stats for key, stats in self.retry_stats.items()
                if stats.operation_name == operation_name
            }
            return matching_stats
        else:
            # Return all stats
            return {
                key: {
                    "operation_name": stats.operation_name,
                    "total_attempts": stats.total_attempts,
                    "success_rate": stats.success_rate,
                    "failure_rate": stats.failure_rate,
                    "average_response_time": stats.average_response_time,
                    "last_success": stats.last_success.isoformat() if stats.last_success else None,
                    "last_failure": stats.last_failure.isoformat() if stats.last_failure else None
                }
                for key, stats in self.retry_stats.items()
            }
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            key: breaker.get_state_info()
            for key, breaker in self.circuit_breakers.items()
        }
    
    def reset_stats(self, operation_name: str = None):
        """Reset retry statistics"""
        if operation_name:
            # Reset stats for specific operation
            keys_to_reset = [
                key for key, stats in self.retry_stats.items()
                if stats.operation_name == operation_name
            ]
            for key in keys_to_reset:
                del self.retry_stats[key]
        else:
            # Reset all stats
            self.retry_stats.clear()
    
    def reset_circuit_breakers(self):
        """Reset all circuit breakers to closed state"""
        for breaker in self.circuit_breakers.values():
            breaker.state = CircuitState.CLOSED
            breaker.failure_count = 0
            breaker.success_count = 0
            breaker.last_failure_time = None


# Decorator for automatic retry
def retry(config: Optional[RetryConfig] = None, 
          operation_name: Optional[str] = None):
    """
    Decorator to automatically add retry logic to functions
    
    Args:
        config: Retry configuration
        operation_name: Name for tracking (uses function name if None)
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            manager = IntelligentRetryManager()
            return await manager.retry_operation(
                func, *args, 
                operation_name=operation_name or func.__name__,
                config=config,
                **kwargs
            )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            manager = IntelligentRetryManager()
            return asyncio.run(manager.retry_operation(
                func, *args,
                operation_name=operation_name or func.__name__,
                config=config,
                **kwargs
            ))
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Convenience functions
async def retry_operation(operation: Callable,
                         *args,
                         config: Optional[RetryConfig] = None,
                         operation_name: Optional[str] = None,
                         **kwargs) -> Any:
    """Convenience function to retry an operation"""
    manager = IntelligentRetryManager()
    return await manager.retry_operation(
        operation, *args,
        operation_name=operation_name,
        config=config,
        **kwargs
    )


def create_retry_config(**kwargs) -> RetryConfig:
    """Convenience function to create retry configuration"""
    return RetryConfig(**kwargs)


def get_default_configs() -> Dict[str, RetryConfig]:
    """Get default retry configurations for different operation types"""
    return {
        "llm_service": RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=30.0,
            backoff_strategy=BackoffStrategy.JITTERED_EXPONENTIAL,
            retry_on_categories=[ErrorCategory.LLM_SERVICE, ErrorCategory.NETWORK],
            failure_threshold=3,
            recovery_timeout=60.0
        ),
        
        "database": RetryConfig(
            max_attempts=5,
            base_delay=1.0,
            max_delay=20.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            retry_on_categories=[ErrorCategory.DATABASE, ErrorCategory.NETWORK],
            failure_threshold=5,
            recovery_timeout=30.0
        ),
        
        "external_api": RetryConfig(
            max_attempts=4,
            base_delay=1.5,
            max_delay=60.0,
            backoff_strategy=BackoffStrategy.JITTERED_EXPONENTIAL,
            retry_on_categories=[ErrorCategory.EXTERNAL_API, ErrorCategory.NETWORK, ErrorCategory.RATE_LIMITING],
            failure_threshold=4,
            recovery_timeout=120.0
        ),
        
        "vector_search": RetryConfig(
            max_attempts=3,
            base_delay=0.5,
            max_delay=10.0,
            backoff_strategy=BackoffStrategy.LINEAR,
            retry_on_categories=[ErrorCategory.VECTOR_SEARCH, ErrorCategory.DATABASE],
            failure_threshold=3,
            recovery_timeout=30.0
        )
    }
