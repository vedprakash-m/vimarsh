"""
Circuit Breakers and Health Monitoring System for Vimarsh AI Agent

This module implements circuit breaker patterns and comprehensive health monitoring
to ensure system reliability and prevent cascading failures in the spiritual
guidance service.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
from contextlib import asynccontextmanager
import statistics

try:
    from .error_classifier import ErrorCategory, ErrorSeverity
    from .llm_fallback import LLMFallbackSystem, FallbackTrigger
except ImportError:
    from error_classifier import ErrorCategory, ErrorSeverity
    from llm_fallback import LLMFallbackSystem, FallbackTrigger


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ServiceType(Enum):
    """Types of services being monitored"""
    LLM_SERVICE = "llm_service"
    VECTOR_SEARCH = "vector_search"
    TEXT_PROCESSING = "text_processing"
    VOICE_PROCESSING = "voice_processing"
    AUTHENTICATION = "authentication"
    EXPERT_REVIEW = "expert_review"
    CONTENT_MODERATION = "content_moderation"
    FALLBACK_SYSTEM = "fallback_system"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5  # Number of failures to open circuit
    success_threshold: int = 3   # Number of successes to close circuit
    timeout_seconds: float = 60.0  # Time before trying half-open
    slow_call_threshold: float = 5.0  # Seconds to consider call slow
    slow_call_rate_threshold: float = 0.5  # Rate of slow calls to open
    minimum_throughput: int = 10  # Minimum calls before evaluating rates


@dataclass
class HealthCheckConfig:
    """Configuration for health checks"""
    check_interval: float = 30.0  # Seconds between health checks
    timeout: float = 10.0  # Timeout for individual health checks
    max_history: int = 100  # Maximum history entries to keep
    degraded_threshold: float = 0.8  # Response time threshold for degraded
    unhealthy_threshold: float = 0.5  # Success rate threshold for unhealthy


@dataclass
class CircuitMetrics:
    """Metrics for circuit breaker performance"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    slow_calls: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    average_response_time: float = 0.0
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=50))


@dataclass
class HealthMetrics:
    """Health monitoring metrics"""
    service_name: str
    status: HealthStatus = HealthStatus.HEALTHY
    last_check_time: Optional[datetime] = None
    response_time: float = 0.0
    success_rate: float = 1.0
    error_count: int = 0
    check_count: int = 0
    uptime_percentage: float = 100.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """
    Circuit breaker implementation for service protection
    """
    
    def __init__(self, 
                 name: str,
                 config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker
        
        Args:
            name: Name of the service being protected
            config: Configuration for circuit breaker behavior
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._lock = threading.Lock()
        self._last_failure_time = 0.0
        
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Execute a function call through the circuit breaker
        
        Args:
            func: Async function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            CircuitBreakerError: When circuit is open
            Original exceptions: When circuit is closed and function fails
        """
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
                else:
                    self.metrics.total_calls += 1
                    raise CircuitBreakerError(f"Circuit breaker {self.name} is OPEN")
        
        # Execute the function call
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            await self._record_success(response_time)
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            await self._record_failure(e, response_time)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset"""
        return (time.time() - self._last_failure_time) >= self.config.timeout_seconds
    
    async def _record_success(self, response_time: float):
        """Record a successful call"""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = datetime.now()
            self.metrics.recent_response_times.append(response_time)
            
            # Update average response time
            if self.metrics.recent_response_times:
                self.metrics.average_response_time = statistics.mean(
                    self.metrics.recent_response_times
                )
            
            # Check for slow calls
            if response_time > self.config.slow_call_threshold:
                self.metrics.slow_calls += 1
            
            # State transitions
            if self.state == CircuitState.HALF_OPEN:
                # Check if we should close the circuit
                recent_successes = self._count_recent_successes()
                if recent_successes >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.metrics.circuit_closes += 1
                    self.logger.info(f"Circuit breaker {self.name} closed after recovery")
            
    async def _record_failure(self, error: Exception, response_time: float):
        """Record a failed call"""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
            self.metrics.last_failure_time = datetime.now()
            self._last_failure_time = time.time()
            self.metrics.recent_response_times.append(response_time)
            
            # Update average response time
            if self.metrics.recent_response_times:
                self.metrics.average_response_time = statistics.mean(
                    self.metrics.recent_response_times
                )
            
            # Check if we should open the circuit
            if self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]:
                should_open = self._should_open_circuit()
                if should_open:
                    self.state = CircuitState.OPEN
                    self.metrics.circuit_opens += 1
                    self.logger.warning(f"Circuit breaker {self.name} opened due to failures")
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        if self.metrics.total_calls < self.config.minimum_throughput:
            return False
        
        # Check failure rate
        failure_rate = self.metrics.failed_calls / self.metrics.total_calls
        if failure_rate >= (self.config.failure_threshold / self.config.minimum_throughput):
            return True
        
        # Check slow call rate
        if self.metrics.total_calls > 0:
            slow_call_rate = self.metrics.slow_calls / self.metrics.total_calls
            if slow_call_rate >= self.config.slow_call_rate_threshold:
                return True
        
        return False
    
    def _count_recent_successes(self) -> int:
        """Count recent successful calls for half-open state"""
        # Simple implementation - in production, would track recent calls more precisely
        recent_calls = min(self.config.success_threshold * 2, self.metrics.total_calls)
        if recent_calls == 0:
            return 0
        
        recent_success_rate = self.metrics.successful_calls / self.metrics.total_calls
        return int(recent_calls * recent_success_rate)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        with self._lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'metrics': {
                    'total_calls': self.metrics.total_calls,
                    'successful_calls': self.metrics.successful_calls,
                    'failed_calls': self.metrics.failed_calls,
                    'slow_calls': self.metrics.slow_calls,
                    'circuit_opens': self.metrics.circuit_opens,
                    'circuit_closes': self.metrics.circuit_closes,
                    'success_rate': (
                        self.metrics.successful_calls / self.metrics.total_calls
                        if self.metrics.total_calls > 0 else 0.0
                    ),
                    'average_response_time': self.metrics.average_response_time,
                    'last_failure_time': (
                        self.metrics.last_failure_time.isoformat()
                        if self.metrics.last_failure_time else None
                    ),
                    'last_success_time': (
                        self.metrics.last_success_time.isoformat()
                        if self.metrics.last_success_time else None
                    )
                },
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'success_threshold': self.config.success_threshold,
                    'timeout_seconds': self.config.timeout_seconds,
                    'slow_call_threshold': self.config.slow_call_threshold
                }
            }
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.metrics = CircuitMetrics()
            self._last_failure_time = 0.0
            self.logger.info(f"Circuit breaker {self.name} reset")


class HealthMonitor:
    """
    Health monitoring system for service components
    """
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        """
        Initialize health monitor
        
        Args:
            config: Configuration for health monitoring
        """
        self.config = config or HealthCheckConfig()
        self.services: Dict[str, HealthMetrics] = {}
        self.health_checks: Dict[str, Callable[[], Awaitable[bool]]] = {}
        self.logger = logging.getLogger(__name__)
        self._monitoring = False
        self._monitor_task = None
        self._lock = threading.Lock()
        
    def register_service(self, 
                        service_name: str,
                        health_check: Callable[[], Awaitable[bool]],
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Register a service for health monitoring
        
        Args:
            service_name: Name of the service
            health_check: Async function that returns True if service is healthy
            metadata: Additional metadata about the service
        """
        with self._lock:
            self.services[service_name] = HealthMetrics(
                service_name=service_name,
                metadata=metadata or {}
            )
            self.health_checks[service_name] = health_check
            self.logger.info(f"Registered service for health monitoring: {service_name}")
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Health monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.config.check_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks for all registered services"""
        check_tasks = []
        
        for service_name in self.services.keys():
            task = asyncio.create_task(
                self._check_service_health(service_name)
            )
            check_tasks.append(task)
        
        if check_tasks:
            await asyncio.gather(*check_tasks, return_exceptions=True)
    
    async def _check_service_health(self, service_name: str):
        """Check health of a specific service"""
        if service_name not in self.health_checks:
            return
        
        start_time = time.time()
        health_check = self.health_checks[service_name]
        
        try:
            # Run health check with timeout
            is_healthy = await asyncio.wait_for(
                health_check(),
                timeout=self.config.timeout
            )
            
            response_time = time.time() - start_time
            await self._record_health_result(service_name, is_healthy, response_time)
            
        except asyncio.TimeoutError:
            response_time = self.config.timeout
            await self._record_health_result(service_name, False, response_time, "timeout")
            
        except Exception as e:
            response_time = time.time() - start_time
            await self._record_health_result(service_name, False, response_time, str(e))
    
    async def _record_health_result(self, 
                                   service_name: str, 
                                   is_healthy: bool,
                                   response_time: float,
                                   error_message: Optional[str] = None):
        """Record the result of a health check"""
        with self._lock:
            if service_name not in self.services:
                return
            
            metrics = self.services[service_name]
            metrics.check_count += 1
            metrics.last_check_time = datetime.now()
            metrics.response_time = response_time
            
            if is_healthy:
                # Update success rate (rolling average)
                metrics.success_rate = (
                    (metrics.success_rate * (metrics.check_count - 1) + 1.0) / 
                    metrics.check_count
                )
            else:
                metrics.error_count += 1
                metrics.success_rate = (
                    (metrics.success_rate * (metrics.check_count - 1) + 0.0) / 
                    metrics.check_count
                )
                
                if error_message:
                    metrics.metadata['last_error'] = error_message
                    metrics.metadata['last_error_time'] = datetime.now().isoformat()
            
            # Update health status
            metrics.status = self._determine_health_status(metrics, response_time)
            
            # Calculate uptime percentage
            if metrics.check_count > 0:
                healthy_checks = metrics.check_count - metrics.error_count
                metrics.uptime_percentage = (healthy_checks / metrics.check_count) * 100
    
    def _determine_health_status(self, 
                                metrics: HealthMetrics,
                                response_time: float) -> HealthStatus:
        """Determine health status based on metrics"""
        
        # Critical if success rate is very low
        if metrics.success_rate < 0.1:
            return HealthStatus.CRITICAL
        
        # Unhealthy if below threshold
        if metrics.success_rate < self.config.unhealthy_threshold:
            return HealthStatus.UNHEALTHY
        
        # Degraded if response time is high or success rate is marginal
        if (response_time > self.config.degraded_threshold * 1000 or  # Convert to ms
            metrics.success_rate < 0.9):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get health status for a specific service"""
        with self._lock:
            if service_name not in self.services:
                return None
            
            metrics = self.services[service_name]
            return {
                'service_name': metrics.service_name,
                'status': metrics.status.value,
                'last_check_time': (
                    metrics.last_check_time.isoformat()
                    if metrics.last_check_time else None
                ),
                'response_time_ms': metrics.response_time * 1000,
                'success_rate': metrics.success_rate,
                'error_count': metrics.error_count,
                'check_count': metrics.check_count,
                'uptime_percentage': metrics.uptime_percentage,
                'metadata': dict(metrics.metadata)
            }
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        with self._lock:
            if not self.services:
                return {
                    'status': HealthStatus.HEALTHY.value,
                    'services': {},
                    'summary': {
                        'total_services': 0,
                        'healthy_services': 0,
                        'degraded_services': 0,
                        'unhealthy_services': 0,
                        'critical_services': 0
                    }
                }
            
            services_health = {}
            status_counts = defaultdict(int)
            
            for service_name, metrics in self.services.items():
                service_health = self.get_service_health(service_name)
                services_health[service_name] = service_health
                status_counts[metrics.status] += 1
            
            # Determine overall status
            if status_counts[HealthStatus.CRITICAL] > 0:
                overall_status = HealthStatus.CRITICAL
            elif status_counts[HealthStatus.UNHEALTHY] > 0:
                overall_status = HealthStatus.UNHEALTHY
            elif status_counts[HealthStatus.DEGRADED] > 0:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY
            
            return {
                'status': overall_status.value,
                'services': services_health,
                'summary': {
                    'total_services': len(self.services),
                    'healthy_services': status_counts[HealthStatus.HEALTHY],
                    'degraded_services': status_counts[HealthStatus.DEGRADED],
                    'unhealthy_services': status_counts[HealthStatus.UNHEALTHY],
                    'critical_services': status_counts[HealthStatus.CRITICAL]
                },
                'last_updated': datetime.now().isoformat()
            }


class CircuitBreakerManager:
    """
    Centralized manager for circuit breakers
    """
    
    def __init__(self):
        """Initialize circuit breaker manager"""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
    
    def get_circuit_breaker(self, 
                          service_name: str,
                          config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """
        Get or create a circuit breaker for a service
        
        Args:
            service_name: Name of the service
            config: Configuration for the circuit breaker
            
        Returns:
            CircuitBreaker instance
        """
        with self._lock:
            if service_name not in self.circuit_breakers:
                self.circuit_breakers[service_name] = CircuitBreaker(
                    service_name, config
                )
                self.logger.info(f"Created circuit breaker for {service_name}")
            
            return self.circuit_breakers[service_name]
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers"""
        with self._lock:
            return {
                name: breaker.get_state()
                for name, breaker in self.circuit_breakers.items()
            }
    
    def reset_circuit_breaker(self, service_name: str) -> bool:
        """
        Reset a specific circuit breaker
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if reset successful, False if circuit breaker not found
        """
        with self._lock:
            if service_name in self.circuit_breakers:
                self.circuit_breakers[service_name].reset()
                return True
            return False
    
    def reset_all_circuit_breakers(self):
        """Reset all circuit breakers"""
        with self._lock:
            for breaker in self.circuit_breakers.values():
                breaker.reset()
            self.logger.info("Reset all circuit breakers")


class HealthAndCircuitMonitor:
    """
    Integrated health monitoring and circuit breaker system
    """
    
    def __init__(self, 
                 health_config: Optional[HealthCheckConfig] = None,
                 circuit_config: Optional[Dict[str, CircuitBreakerConfig]] = None):
        """
        Initialize integrated monitoring system
        
        Args:
            health_config: Configuration for health monitoring
            circuit_config: Configuration for circuit breakers per service
        """
        self.health_monitor = HealthMonitor(health_config)
        self.circuit_manager = CircuitBreakerManager()
        self.circuit_configs = circuit_config or {}
        self.logger = logging.getLogger(__name__)
        
    def register_service(self,
                        service_name: str,
                        health_check: Callable[[], Awaitable[bool]],
                        circuit_config: Optional[CircuitBreakerConfig] = None,
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Register a service for both health monitoring and circuit breaking
        
        Args:
            service_name: Name of the service
            health_check: Health check function
            circuit_config: Circuit breaker configuration
            metadata: Additional service metadata
        """
        # Register for health monitoring
        self.health_monitor.register_service(service_name, health_check, metadata)
        
        # Create circuit breaker
        config = circuit_config or self.circuit_configs.get(service_name)
        self.circuit_manager.get_circuit_breaker(service_name, config)
        
        self.logger.info(f"Registered service {service_name} for monitoring and protection")
    
    @asynccontextmanager
    async def protected_call(self, service_name: str):
        """
        Context manager for protected service calls
        
        Args:
            service_name: Name of the service being called
            
        Example:
            async with monitor.protected_call("llm_service") as call:
                result = await call(llm_function, query)
        """
        circuit_breaker = self.circuit_manager.get_circuit_breaker(service_name)
        
        class ProtectedCaller:
            def __init__(self, breaker):
                self.breaker = breaker
            
            async def __call__(self, func, *args, **kwargs):
                return await self.breaker.call(func, *args, **kwargs)
        
        yield ProtectedCaller(circuit_breaker)
    
    async def start_monitoring(self):
        """Start health monitoring"""
        await self.health_monitor.start_monitoring()
        self.logger.info("Started integrated health and circuit monitoring")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        await self.health_monitor.stop_monitoring()
        self.logger.info("Stopped integrated health and circuit monitoring")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health_status = self.health_monitor.get_overall_health()
        circuit_states = self.circuit_manager.get_all_states()
        
        return {
            'health': health_status,
            'circuit_breakers': circuit_states,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status for a specific service"""
        health = self.health_monitor.get_service_health(service_name)
        circuit = self.circuit_manager.circuit_breakers.get(service_name)
        
        return {
            'service_name': service_name,
            'health': health,
            'circuit_breaker': circuit.get_state() if circuit else None,
            'timestamp': datetime.now().isoformat()
        }


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


# Service-specific health check implementations
class ServiceHealthChecks:
    """
    Collection of health check implementations for different services
    """
    
    @staticmethod
    async def llm_service_health() -> bool:
        """Health check for LLM service"""
        try:
            # Simple health check - could be more comprehensive
            await asyncio.sleep(0.1)  # Simulate API call
            return True
        except Exception:
            return False
    
    @staticmethod
    async def vector_search_health() -> bool:
        """Health check for vector search service"""
        try:
            # Check if vector search is responsive
            await asyncio.sleep(0.05)  # Simulate vector query
            return True
        except Exception:
            return False
    
    @staticmethod
    async def text_processing_health() -> bool:
        """Health check for text processing service"""
        try:
            # Check text processing capabilities
            test_text = "Om Namah Shivaya"
            # Simulate text processing
            await asyncio.sleep(0.02)
            return len(test_text) > 0
        except Exception:
            return False
    
    @staticmethod
    async def expert_review_health() -> bool:
        """Health check for expert review system"""
        try:
            # Check expert review system
            await asyncio.sleep(0.1)  # Simulate review system check
            return True
        except Exception:
            return False
    
    @staticmethod
    async def content_moderation_health() -> bool:
        """Health check for content moderation"""
        try:
            # Check content moderation system
            await asyncio.sleep(0.03)  # Simulate moderation check
            return True
        except Exception:
            return False
    
    @staticmethod
    async def fallback_system_health() -> bool:
        """Health check for fallback system"""
        try:
            # Check fallback system availability
            await asyncio.sleep(0.01)  # Simulate fallback check
            return True
        except Exception:
            return False


# Pre-configured monitoring system for Vimarsh
def create_vimarsh_monitor() -> HealthAndCircuitMonitor:
    """
    Create a pre-configured monitoring system for Vimarsh services
    
    Returns:
        Configured HealthAndCircuitMonitor instance
    """
    # Health monitoring configuration
    health_config = HealthCheckConfig(
        check_interval=30.0,  # Check every 30 seconds
        timeout=10.0,         # 10 second timeout
        degraded_threshold=2.0,  # 2 second response time for degraded
        unhealthy_threshold=0.7  # 70% success rate threshold
    )
    
    # Circuit breaker configurations per service
    circuit_configs = {
        ServiceType.LLM_SERVICE.value: CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=3,
            timeout_seconds=60.0,
            slow_call_threshold=10.0  # LLM calls can be slower
        ),
        ServiceType.VECTOR_SEARCH.value: CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=30.0,
            slow_call_threshold=2.0  # Vector search should be fast
        ),
        ServiceType.TEXT_PROCESSING.value: CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=20.0,
            slow_call_threshold=1.0  # Text processing should be very fast
        ),
        ServiceType.EXPERT_REVIEW.value: CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=120.0,  # Longer timeout for expert system
            slow_call_threshold=30.0
        ),
        ServiceType.CONTENT_MODERATION.value: CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=30.0,
            slow_call_threshold=5.0
        ),
        ServiceType.FALLBACK_SYSTEM.value: CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=1,
            timeout_seconds=10.0,  # Fallback should recover quickly
            slow_call_threshold=3.0
        )
    }
    
    return HealthAndCircuitMonitor(health_config, circuit_configs)


async def initialize_vimarsh_monitoring() -> HealthAndCircuitMonitor:
    """
    Initialize and configure monitoring for all Vimarsh services
    
    Returns:
        Configured and started monitoring system
    """
    monitor = create_vimarsh_monitor()
    
    # Register all services
    services = [
        (ServiceType.LLM_SERVICE.value, ServiceHealthChecks.llm_service_health, 
         {"description": "Gemini Pro LLM service for spiritual guidance"}),
        (ServiceType.VECTOR_SEARCH.value, ServiceHealthChecks.vector_search_health,
         {"description": "Vector search for spiritual text retrieval"}),
        (ServiceType.TEXT_PROCESSING.value, ServiceHealthChecks.text_processing_health,
         {"description": "Text processing and chunking service"}),
        (ServiceType.EXPERT_REVIEW.value, ServiceHealthChecks.expert_review_health,
         {"description": "Expert review system for response validation"}),
        (ServiceType.CONTENT_MODERATION.value, ServiceHealthChecks.content_moderation_health,
         {"description": "Content moderation and safety validation"}),
        (ServiceType.FALLBACK_SYSTEM.value, ServiceHealthChecks.fallback_system_health,
         {"description": "Fallback response system for service failures"})
    ]
    
    for service_name, health_check, metadata in services:
        monitor.register_service(service_name, health_check, metadata=metadata)
    
    # Start monitoring
    await monitor.start_monitoring()
    
    return monitor
