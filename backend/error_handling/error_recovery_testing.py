"""
Error Recovery Testing and Validation System for Vimarsh AI Agent

This module provides comprehensive testing and validation procedures for error
recovery mechanisms, ensuring the spiritual guidance system can gracefully
handle and recover from various failure scenarios.
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

# Import error handling components with proper fallback handling
try:
    # Try relative imports first (when used as package)
    from .error_classifier import ErrorCategory, ErrorSeverity, ErrorContext, ErrorClassifier
    from .graceful_degradation import GracefulDegradationManager, DegradationLevel
    from .intelligent_retry import IntelligentRetryManager
    from .llm_fallback import LLMFallbackSystem, FallbackTrigger, SpiritualQuery
    from .circuit_breaker import HealthAndCircuitMonitor, CircuitBreakerError
    from .error_analytics import ErrorAnalytics as ErrorAnalyticsSystem
except ImportError:
    # Fallback to absolute imports (when run directly)
    try:
        from error_handling.error_classifier import ErrorCategory, ErrorSeverity, ErrorContext, ErrorClassifier
        from error_handling.graceful_degradation import GracefulDegradationManager, DegradationLevel
        from error_handling.intelligent_retry import IntelligentRetryManager
        from error_handling.llm_fallback import LLMFallbackSystem, FallbackTrigger, SpiritualQuery
        from error_handling.circuit_breaker import HealthAndCircuitMonitor, CircuitBreakerError
        from error_handling.error_analytics import ErrorAnalytics as ErrorAnalyticsSystem
    except ImportError:
        # Final fallback for development/testing
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from error_classifier import ErrorCategory, ErrorSeverity, ErrorContext, ErrorClassifier
        from graceful_degradation import GracefulDegradationManager, DegradationLevel
        from intelligent_retry import IntelligentRetryManager
        from llm_fallback import LLMFallbackSystem, FallbackTrigger, SpiritualQuery
        from circuit_breaker import HealthAndCircuitMonitor, CircuitBreakerError
        from error_analytics import ErrorAnalytics as ErrorAnalyticsSystem


class TestScenario(Enum):
    """Types of error recovery test scenarios"""
    TRANSIENT_NETWORK_FAILURE = "transient_network_failure"
    PERSISTENT_SERVICE_OUTAGE = "persistent_service_outage"
    PARTIAL_SYSTEM_DEGRADATION = "partial_system_degradation"
    CASCADING_FAILURES = "cascading_failures"
    HIGH_LOAD_STRESS_TEST = "high_load_stress_test"
    GRADUAL_RECOVERY_TEST = "gradual_recovery_test"
    SPIRITUAL_CONTENT_VALIDATION = "spiritual_content_validation"
    MULTILINGUAL_ERROR_HANDLING = "multilingual_error_handling"


class TestResult(Enum):
    """Test result outcomes"""
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class TestConfiguration:
    """Configuration for error recovery tests"""
    scenario: TestScenario
    duration_seconds: float = 60.0
    failure_rate: float = 0.3  # 30% failure rate
    recovery_time: float = 10.0  # Time to recovery in seconds
    concurrent_requests: int = 10
    timeout_seconds: float = 30.0
    expected_success_rate: float = 0.8  # 80% success rate expected
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestMetrics:
    """Metrics collected during error recovery testing"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    average_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = float('inf')
    error_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    recovery_time: Optional[float] = None
    degradation_events: int = 0
    fallback_activations: int = 0
    circuit_breaker_trips: int = 0
    response_times: List[float] = field(default_factory=list)


@dataclass
class TestReport:
    """Comprehensive test report for error recovery validation"""
    scenario: TestScenario
    result: TestResult
    metrics: TestMetrics
    start_time: datetime
    end_time: datetime
    duration: float
    success_rate: float
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    detailed_logs: List[str] = field(default_factory=list)


class ErrorRecoveryTester:
    """
    Comprehensive error recovery testing and validation system
    """
    
    def __init__(self):
        """Initialize the error recovery testing system"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize all error handling components
        self.error_classifier = None
        self.degradation_manager = None
        self.retry_manager = None
        self.fallback_system = None
        self.circuit_monitor = None
        self.analytics_system = None
        
        # Test state
        self.test_reports: List[TestReport] = []
        self.current_test: Optional[TestConfiguration] = None
        
        # Failure simulation
        self._failure_probability = 0.0
        self._service_outages = set()
        self._degraded_services = set()
    
    async def initialize_systems(self):
        """Initialize all error handling systems for testing"""
        try:
            # Initialize error classification with safe fallback
            try:
                self.error_classifier = ErrorClassifier()
            except Exception as e:
                self.logger.warning(f"Could not initialize ErrorClassifier: {e}")
                self.error_classifier = None
            
            # Initialize degradation management with safe fallback
            try:
                self.degradation_manager = GracefulDegradationManager()
            except Exception as e:
                self.logger.warning(f"Could not initialize GracefulDegradationManager: {e}")
                self.degradation_manager = None
            
            # Initialize retry management with safe fallback
            try:
                self.retry_manager = IntelligentRetryManager()
            except Exception as e:
                self.logger.warning(f"Could not initialize IntelligentRetryManager: {e}")
                self.retry_manager = None
            
            # Initialize fallback system with safe fallback
            try:
                self.fallback_system = LLMFallbackSystem(
                    enable_external_llm=False  # Disable for testing
                )
            except Exception as e:
                self.logger.warning(f"Could not initialize LLMFallbackSystem: {e}")
                self.fallback_system = None
            
            # Initialize circuit breaker and health monitoring with safe fallback
            try:
                # Import circuit breaker initializer
                try:
                    from .circuit_breaker import initialize_vimarsh_monitoring
                except ImportError:
                    try:
                        from error_handling.circuit_breaker import initialize_vimarsh_monitoring
                    except ImportError:
                        from .circuit_breaker import initialize_vimarsh_monitoring
                
                self.circuit_monitor = await initialize_vimarsh_monitoring()
            except Exception as e:
                self.logger.warning(f"Could not initialize circuit breaker monitoring: {e}")
                self.circuit_monitor = None
            
            # Initialize analytics with safe fallback
            try:
                self.analytics_system = ErrorAnalyticsSystem()
            except Exception as e:
                self.logger.warning(f"Could not initialize ErrorAnalyticsSystem: {e}")
                self.analytics_system = None
            
            # Count successfully initialized systems
            initialized_count = sum(1 for system in [
                self.error_classifier,
                self.degradation_manager,
                self.retry_manager,
                self.fallback_system,
                self.circuit_monitor,
                self.analytics_system
            ] if system is not None)
            
            self.logger.info(f"Initialized {initialized_count}/6 error handling systems for testing")
            
            if initialized_count == 0:
                self.logger.error("No error handling systems could be initialized")
                # Continue anyway for testing purposes
            
        except Exception as e:
            self.logger.error(f"Critical failure in system initialization: {e}")
            # Initialize minimal systems for testing
            self.error_classifier = None
            self.degradation_manager = None
            self.retry_manager = None
            self.fallback_system = None
            self.circuit_monitor = None
            self.analytics_system = None
    
    async def run_test_scenario(self, config: TestConfiguration) -> TestReport:
        """
        Run a specific error recovery test scenario
        
        Args:
            config: Test configuration
            
        Returns:
            Test report with results and metrics
        """
        self.current_test = config
        start_time = datetime.now()
        
        self.logger.info(f"Starting test scenario: {config.scenario.value}")
        
        # Initialize test metrics
        metrics = TestMetrics()
        
        try:
            # Configure failure simulation
            await self._setup_failure_simulation(config)
            
            # Run the test scenario
            if config.scenario == TestScenario.TRANSIENT_NETWORK_FAILURE:
                await self._test_transient_failures(config, metrics)
            elif config.scenario == TestScenario.PERSISTENT_SERVICE_OUTAGE:
                await self._test_persistent_outage(config, metrics)
            elif config.scenario == TestScenario.PARTIAL_SYSTEM_DEGRADATION:
                await self._test_partial_degradation(config, metrics)
            elif config.scenario == TestScenario.CASCADING_FAILURES:
                await self._test_cascading_failures(config, metrics)
            elif config.scenario == TestScenario.HIGH_LOAD_STRESS_TEST:
                await self._test_high_load_stress(config, metrics)
            elif config.scenario == TestScenario.GRADUAL_RECOVERY_TEST:
                await self._test_gradual_recovery(config, metrics)
            elif config.scenario == TestScenario.SPIRITUAL_CONTENT_VALIDATION:
                await self._test_spiritual_content_validation(config, metrics)
            elif config.scenario == TestScenario.MULTILINGUAL_ERROR_HANDLING:
                await self._test_multilingual_error_handling(config, metrics)
            else:
                raise ValueError(f"Unknown test scenario: {config.scenario}")
            
            # Clean up failure simulation
            await self._cleanup_failure_simulation()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Calculate success rate
            success_rate = (
                metrics.successful_requests / metrics.total_requests
                if metrics.total_requests > 0 else 0.0
            )
            
            # Determine test result
            result = self._evaluate_test_result(config, metrics, success_rate)
            
            # Generate report
            report = TestReport(
                scenario=config.scenario,
                result=result,
                metrics=metrics,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success_rate=success_rate
            )
            
            # Add issues and recommendations
            self._analyze_test_results(report, config)
            
            self.test_reports.append(report)
            
            self.logger.info(f"Completed test scenario: {config.scenario.value} - Result: {result.value}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Test scenario failed: {e}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            report = TestReport(
                scenario=config.scenario,
                result=TestResult.ERROR,
                metrics=metrics,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success_rate=0.0,
                issues_found=[f"Test execution error: {str(e)}"]
            )
            
            self.test_reports.append(report)
            return report
    
    async def _setup_failure_simulation(self, config: TestConfiguration):
        """Setup failure simulation based on test configuration"""
        self._failure_probability = config.failure_rate
        
        # Configure specific failures based on scenario
        if config.scenario == TestScenario.PERSISTENT_SERVICE_OUTAGE:
            self._service_outages.add("llm_service")
        elif config.scenario == TestScenario.PARTIAL_SYSTEM_DEGRADATION:
            self._degraded_services.add("vector_search")
            self._degraded_services.add("text_processing")
        elif config.scenario == TestScenario.CASCADING_FAILURES:
            # Will simulate progressive failures
            pass
    
    async def _cleanup_failure_simulation(self):
        """Clean up failure simulation"""
        self._failure_probability = 0.0
        self._service_outages.clear()
        self._degraded_services.clear()
    
    async def _simulate_service_call(self, service_name: str, query: str) -> Tuple[bool, str, float]:
        """
        Simulate a service call with potential failures
        
        Returns:
            (success, response, response_time)
        """
        start_time = time.time()
        
        # Simulate network latency
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Check for configured failures
        if service_name in self._service_outages:
            response_time = time.time() - start_time
            return False, "Service outage", response_time
        
        if service_name in self._degraded_services:
            # Degraded service - slower and higher failure rate
            await asyncio.sleep(random.uniform(1.0, 3.0))
            if random.random() < 0.6:  # 60% failure rate when degraded
                response_time = time.time() - start_time
                return False, "Service degraded", response_time
        
        # Random failures based on failure probability
        if random.random() < self._failure_probability:
            response_time = time.time() - start_time
            error_types = ["timeout", "network_error", "invalid_response", "rate_limit"]
            error_type = random.choice(error_types)
            return False, f"Simulated {error_type}", response_time
        
        # Successful response
        response_time = time.time() - start_time
        spiritual_responses = [
            "Krishna teaches us about dharma and righteous action.",
            "The soul is eternal and beyond physical limitations.",
            "Devotion and surrender lead to spiritual liberation.",
            "Karma yoga is the path of selfless action.",
            "Meditation brings peace and inner realization."
        ]
        
        response = random.choice(spiritual_responses)
        return True, response, response_time
    
    async def _test_transient_failures(self, config: TestConfiguration, metrics: TestMetrics):
        """Test recovery from transient network failures"""
        
        async def make_request():
            query = SpiritualQuery(
                text="What is the path to spiritual enlightenment?",
                language="en"
            )
            
            try:
                # Simulate service call with potential transient failures
                success, response, response_time = await self._simulate_service_call(
                    "llm_service", query.text
                )
                
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                if success:
                    metrics.successful_requests += 1
                    # Test fallback system integration
                    if self.fallback_system and random.random() < 0.1:  # 10% fallback tests
                        fallback_response = await self.fallback_system.get_fallback_response(
                            query, FallbackTrigger.LLM_TIMEOUT
                        )
                        metrics.fallback_activations += 1
                else:
                    metrics.failed_requests += 1
                    metrics.error_types[response] += 1
                    
                    # Test retry mechanism
                    if self.retry_manager:
                        retry_count = 0
                        while retry_count < 3 and not success:
                            await asyncio.sleep(0.5)  # Brief delay
                            success, response, retry_time = await self._simulate_service_call(
                                "llm_service", query.text
                            )
                            retry_count += 1
                            metrics.total_requests += 1
                            response_time += retry_time
                            
                            if success:
                                metrics.successful_requests += 1
                                break
                            else:
                                metrics.failed_requests += 1
                
                return success, response_time
                
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.error_types[str(e)] += 1
                return False, 0.0
        
        # Run concurrent requests for the test duration
        end_time = time.time() + config.duration_seconds
        tasks = []
        
        while time.time() < end_time:
            # Create batch of concurrent requests
            batch_size = min(config.concurrent_requests, 5)
            batch_tasks = [make_request() for _ in range(batch_size)]
            
            try:
                results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        metrics.total_requests += 1
                        metrics.failed_requests += 1
                        metrics.error_types[str(result)] += 1
            
            except Exception as e:
                self.logger.error(f"Batch execution error: {e}")
            
            # Brief pause between batches
            await asyncio.sleep(1.0)
        
        # Calculate response time statistics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    async def _test_persistent_outage(self, config: TestConfiguration, metrics: TestMetrics):
        """Test recovery from persistent service outages"""
        
        # Simulate persistent LLM service outage
        self._service_outages.add("llm_service")
        
        query = SpiritualQuery(
            text="How can I find peace in difficult times?",
            language="en"
        )
        
        # Test fallback system under persistent failure
        for i in range(20):  # 20 test requests
            try:
                start_time = time.time()
                
                # Primary service should fail
                success, response, response_time = await self._simulate_service_call(
                    "llm_service", query.text
                )
                
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                if not success:
                    metrics.failed_requests += 1
                    metrics.error_types[response] += 1
                    
                    # Test fallback activation
                    if self.fallback_system:
                        fallback_response = await self.fallback_system.get_fallback_response(
                            query, FallbackTrigger.SERVICE_UNAVAILABLE
                        )
                        
                        if fallback_response and fallback_response.confidence > 0.3:
                            metrics.successful_requests += 1
                            metrics.fallback_activations += 1
                        else:
                            metrics.failed_requests += 1
                else:
                    metrics.successful_requests += 1
                
                # Test circuit breaker behavior
                if self.circuit_monitor:
                    try:
                        async with self.circuit_monitor.protected_call("llm_service") as call:
                            await call(self._simulate_service_call, "llm_service", query.text)
                    except CircuitBreakerError:
                        metrics.circuit_breaker_trips += 1
                
                await asyncio.sleep(0.5)  # Pace the requests
                
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.error_types[str(e)] += 1
        
        # Calculate metrics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    async def _test_partial_degradation(self, config: TestConfiguration, metrics: TestMetrics):
        """Test recovery from partial system degradation"""
        
        # Test with multiple degraded services
        queries = [
            "What is my dharma in life?",
            "How should I practice meditation?",
            "What does Krishna teach about devotion?",
            "How can I overcome suffering?",
            "What is the nature of the soul?"
        ]
        
        for i in range(15):  # 15 test cycles
            query_text = random.choice(queries)
            query = SpiritualQuery(text=query_text, language="en")
            
            # Test vector search (degraded)
            success, response, response_time = await self._simulate_service_call(
                "vector_search", query_text
            )
            
            metrics.total_requests += 1
            metrics.response_times.append(response_time)
            
            if not success:
                metrics.failed_requests += 1
                metrics.error_types[response] += 1
                metrics.degradation_events += 1
                
                # Test degradation management
                if self.degradation_manager:
                    degraded_response = await self.degradation_manager.handle_service_degradation(
                        "vector_search", ErrorSeverity.MEDIUM, {"query": query_text}
                    )
                    if degraded_response:
                        metrics.successful_requests += 1
            else:
                metrics.successful_requests += 1
            
            await asyncio.sleep(0.3)
        
        # Calculate metrics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    async def _test_cascading_failures(self, config: TestConfiguration, metrics: TestMetrics):
        """Test recovery from cascading failures"""
        
        # Simulate progressive service failures
        services = ["text_processing", "vector_search", "llm_service", "expert_review"]
        failure_progression = []
        
        for i, service in enumerate(services):
            # Add service to outage list progressively
            self._service_outages.add(service)
            failure_progression.append(service)
            
            # Test system behavior as failures cascade
            for j in range(5):  # 5 requests per failure stage
                query = SpiritualQuery(
                    text=f"Test query {i}-{j} about spiritual guidance",
                    language="en"
                )
                
                try:
                    # Test each affected service
                    for failed_service in failure_progression:
                        success, response, response_time = await self._simulate_service_call(
                            failed_service, query.text
                        )
                        
                        metrics.total_requests += 1
                        metrics.response_times.append(response_time)
                        
                        if not success:
                            metrics.failed_requests += 1
                            metrics.error_types[response] += 1
                        else:
                            metrics.successful_requests += 1
                    
                    # Test fallback system under cascading failures
                    if self.fallback_system and len(failure_progression) >= 2:
                        fallback_response = await self.fallback_system.get_fallback_response(
                            query, FallbackTrigger.SERVICE_UNAVAILABLE
                        )
                        metrics.fallback_activations += 1
                        
                        if fallback_response and fallback_response.confidence > 0.5:
                            metrics.successful_requests += 1
                        else:
                            metrics.failed_requests += 1
                
                except Exception as e:
                    metrics.total_requests += 1
                    metrics.failed_requests += 1
                    metrics.error_types[str(e)] += 1
                
                await asyncio.sleep(0.2)
            
            # Brief pause between failure stages
            await asyncio.sleep(1.0)
        
        # Calculate metrics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    async def _test_high_load_stress(self, config: TestConfiguration, metrics: TestMetrics):
        """Test system behavior under high load stress"""
        
        async def stress_request():
            query = SpiritualQuery(
                text=f"High load test query at {time.time()}",
                language="en"
            )
            
            start_time = time.time()
            try:
                success, response, response_time = await self._simulate_service_call(
                    "llm_service", query.text
                )
                
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                if success:
                    metrics.successful_requests += 1
                else:
                    metrics.failed_requests += 1
                    metrics.error_types[response] += 1
                
                return success
                
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.error_types[str(e)] += 1
                return False
        
        # Create high concurrent load
        concurrent_load = config.concurrent_requests * 2  # Double the normal load
        
        # Run stress test for specified duration
        end_time = time.time() + config.duration_seconds
        
        while time.time() < end_time:
            # Create large batch of concurrent requests
            tasks = [stress_request() for _ in range(concurrent_load)]
            
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                self.logger.error(f"Stress test batch error: {e}")
            
            # Brief pause to prevent overwhelming
            await asyncio.sleep(0.5)
        
        # Calculate metrics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    async def _test_gradual_recovery(self, config: TestConfiguration, metrics: TestMetrics):
        """Test gradual system recovery after failures"""
        
        # Start with full outage
        self._service_outages.add("llm_service")
        recovery_start_time = time.time()
        
        # Test during outage
        for i in range(5):
            query = SpiritualQuery(text=f"Recovery test query {i}", language="en")
            success, response, response_time = await self._simulate_service_call("llm_service", query.text)
            
            metrics.total_requests += 1
            metrics.response_times.append(response_time)
            
            if success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
                metrics.error_types[response] += 1
        
        # Simulate gradual recovery
        await asyncio.sleep(2.0)
        self._service_outages.remove("llm_service")
        self._failure_probability = 0.7  # High failure rate initially
        
        # Test during recovery phase
        for i in range(10):
            query = SpiritualQuery(text=f"Recovery phase query {i}", language="en")
            success, response, response_time = await self._simulate_service_call("llm_service", query.text)
            
            metrics.total_requests += 1
            metrics.response_times.append(response_time)
            
            if success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
                metrics.error_types[response] += 1
            
            # Gradually improve failure rate
            self._failure_probability *= 0.9  # Reduce by 10% each iteration
            await asyncio.sleep(0.5)
        
        metrics.recovery_time = time.time() - recovery_start_time
        
        # Calculate metrics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    async def _test_spiritual_content_validation(self, config: TestConfiguration, metrics: TestMetrics):
        """Test error recovery for spiritual content validation"""
        
        spiritual_queries = [
            "What does the Bhagavad Gita say about dharma?",
            "How does Krishna guide us in difficult times?",
            "What is the path to moksha according to Vedic wisdom?",
            "How should I practice bhakti yoga?",
            "What is the significance of Om in meditation?"
        ]
        
        for query_text in spiritual_queries:
            query = SpiritualQuery(text=query_text, language="en")
            
            # Test with potential content validation failures
            try:
                success, response, response_time = await self._simulate_service_call(
                    "content_moderation", query_text
                )
                
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                if success:
                    metrics.successful_requests += 1
                    
                    # Test expert review fallback
                    if random.random() < 0.3:  # 30% require expert review
                        expert_success, expert_response, expert_time = await self._simulate_service_call(
                            "expert_review", query_text
                        )
                        
                        metrics.total_requests += 1
                        metrics.response_times.append(expert_time)
                        
                        if expert_success:
                            metrics.successful_requests += 1
                        else:
                            metrics.failed_requests += 1
                            metrics.error_types[expert_response] += 1
                else:
                    metrics.failed_requests += 1
                    metrics.error_types[response] += 1
                    
                    # Test fallback for content validation failures
                    if self.fallback_system:
                        fallback_response = await self.fallback_system.get_fallback_response(
                            query, FallbackTrigger.SAFETY_VIOLATION
                        )
                        metrics.fallback_activations += 1
                        
                        if fallback_response and fallback_response.confidence > 0.7:
                            metrics.successful_requests += 1
                        else:
                            metrics.failed_requests += 1
            
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.error_types[str(e)] += 1
            
            await asyncio.sleep(0.5)
        
        # Calculate metrics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    async def _test_multilingual_error_handling(self, config: TestConfiguration, metrics: TestMetrics):
        """Test error recovery for multilingual scenarios"""
        
        test_queries = [
            ("What is dharma?", "en"),
            ("धर्म क्या है?", "hi"),
            ("How to find inner peace?", "en"),
            ("आंतरिक शांति कैसे पाएं?", "hi"),
            ("Krishna's teachings on devotion", "en"),
            ("भक्ति पर कृष्ण की शिक्षा", "hi")
        ]
        
        for query_text, language in test_queries:
            query = SpiritualQuery(text=query_text, language=language)
            
            try:
                # Test language-specific processing
                success, response, response_time = await self._simulate_service_call(
                    "text_processing", query_text
                )
                
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                if success:
                    metrics.successful_requests += 1
                else:
                    metrics.failed_requests += 1
                    metrics.error_types[f"{language}_{response}"] += 1
                    
                    # Test language-specific fallback
                    if self.fallback_system:
                        fallback_response = await self.fallback_system.get_fallback_response(
                            query, FallbackTrigger.INVALID_RESPONSE
                        )
                        metrics.fallback_activations += 1
                        
                        if fallback_response and fallback_response.confidence > 0.6:
                            metrics.successful_requests += 1
                        else:
                            metrics.failed_requests += 1
            
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.error_types[f"{language}_{str(e)}"] += 1
            
            await asyncio.sleep(0.3)
        
        # Calculate metrics
        if metrics.response_times:
            metrics.average_response_time = statistics.mean(metrics.response_times)
            metrics.max_response_time = max(metrics.response_times)
            metrics.min_response_time = min(metrics.response_times)
    
    def _evaluate_test_result(self, config: TestConfiguration, metrics: TestMetrics, success_rate: float) -> TestResult:
        """Evaluate overall test result based on metrics"""
        
        # Check if success rate meets expectations
        if success_rate >= config.expected_success_rate:
            result = TestResult.PASS
        elif success_rate >= config.expected_success_rate * 0.7:  # 70% of expected
            result = TestResult.PARTIAL
        else:
            result = TestResult.FAIL
        
        # Additional checks for specific scenarios
        if config.scenario == TestScenario.PERSISTENT_SERVICE_OUTAGE:
            if metrics.fallback_activations == 0:
                result = TestResult.FAIL
        elif config.scenario == TestScenario.CASCADING_FAILURES:
            if metrics.failed_requests > metrics.successful_requests:
                result = TestResult.FAIL
        elif config.scenario == TestScenario.HIGH_LOAD_STRESS_TEST:
            if metrics.average_response_time > 5.0:  # 5 second threshold
                result = TestResult.PARTIAL if result == TestResult.PASS else result
        
        return result
    
    def _analyze_test_results(self, report: TestReport, config: TestConfiguration):
        """Analyze test results and generate issues and recommendations"""
        
        # Check for common issues
        if report.success_rate < 0.8:
            report.issues_found.append(f"Low success rate: {report.success_rate:.2%}")
            report.recommendations.append("Review error handling thresholds and fallback strategies")
        
        if report.metrics.average_response_time > 3.0:
            report.issues_found.append(f"High average response time: {report.metrics.average_response_time:.2f}s")
            report.recommendations.append("Optimize service timeouts and implement response caching")
        
        if report.metrics.fallback_activations == 0 and config.scenario in [
            TestScenario.PERSISTENT_SERVICE_OUTAGE,
            TestScenario.CASCADING_FAILURES
        ]:
            report.issues_found.append("Fallback system not activated during failures")
            report.recommendations.append("Review fallback trigger conditions and configuration")
        
        if report.metrics.circuit_breaker_trips == 0 and config.scenario == TestScenario.HIGH_LOAD_STRESS_TEST:
            report.issues_found.append("Circuit breakers not triggered under high load")
            report.recommendations.append("Review circuit breaker thresholds and load limits")
        
        # Scenario-specific analysis
        if config.scenario == TestScenario.GRADUAL_RECOVERY_TEST:
            if report.metrics.recovery_time and report.metrics.recovery_time > 30.0:
                report.issues_found.append(f"Slow recovery time: {report.metrics.recovery_time:.1f}s")
                report.recommendations.append("Implement faster recovery detection and healing")
        
        if config.scenario == TestScenario.SPIRITUAL_CONTENT_VALIDATION:
            content_errors = sum(1 for error in report.metrics.error_types.keys() if "content" in error.lower())
            if content_errors > report.metrics.total_requests * 0.1:
                report.issues_found.append("High content validation error rate")
                report.recommendations.append("Review spiritual content validation rules and expert review process")
    
    async def run_comprehensive_test_suite(self) -> List[TestReport]:
        """Run comprehensive error recovery test suite"""
        
        self.logger.info("Starting comprehensive error recovery test suite")
        
        # Initialize all systems
        await self.initialize_systems()
        
        # Define test configurations
        test_configs = [
            TestConfiguration(
                scenario=TestScenario.TRANSIENT_NETWORK_FAILURE,
                duration_seconds=30.0,
                failure_rate=0.3,
                concurrent_requests=5,
                expected_success_rate=0.8
            ),
            TestConfiguration(
                scenario=TestScenario.PERSISTENT_SERVICE_OUTAGE,
                duration_seconds=20.0,
                failure_rate=1.0,  # 100% failure for outage test
                concurrent_requests=3,
                expected_success_rate=0.7  # Lower due to fallback reliance
            ),
            TestConfiguration(
                scenario=TestScenario.PARTIAL_SYSTEM_DEGRADATION,
                duration_seconds=25.0,
                failure_rate=0.5,
                concurrent_requests=4,
                expected_success_rate=0.75
            ),
            TestConfiguration(
                scenario=TestScenario.CASCADING_FAILURES,
                duration_seconds=30.0,
                failure_rate=0.8,
                concurrent_requests=3,
                expected_success_rate=0.6
            ),
            TestConfiguration(
                scenario=TestScenario.HIGH_LOAD_STRESS_TEST,
                duration_seconds=20.0,
                failure_rate=0.2,
                concurrent_requests=15,
                expected_success_rate=0.85
            ),
            TestConfiguration(
                scenario=TestScenario.GRADUAL_RECOVERY_TEST,
                duration_seconds=15.0,
                failure_rate=0.7,
                concurrent_requests=3,
                expected_success_rate=0.7
            ),
            TestConfiguration(
                scenario=TestScenario.SPIRITUAL_CONTENT_VALIDATION,
                duration_seconds=15.0,
                failure_rate=0.2,
                concurrent_requests=2,
                expected_success_rate=0.9
            ),
            TestConfiguration(
                scenario=TestScenario.MULTILINGUAL_ERROR_HANDLING,
                duration_seconds=10.0,
                failure_rate=0.3,
                concurrent_requests=2,
                expected_success_rate=0.8
            )
        ]
        
        # Run all test scenarios
        all_reports = []
        
        for config in test_configs:
            try:
                report = await self.run_test_scenario(config)
                all_reports.append(report)
                
                # Brief pause between tests
                await asyncio.sleep(2.0)
                
            except Exception as e:
                self.logger.error(f"Failed to run test {config.scenario.value}: {e}")
        
        # Generate summary report
        self._generate_summary_report(all_reports)
        
        self.logger.info("Completed comprehensive error recovery test suite")
        
        return all_reports
    
    def _generate_summary_report(self, reports: List[TestReport]):
        """Generate summary report for all tests"""
        
        total_tests = len(reports)
        passed_tests = sum(1 for r in reports if r.result == TestResult.PASS)
        partial_tests = sum(1 for r in reports if r.result == TestResult.PARTIAL)
        failed_tests = sum(1 for r in reports if r.result == TestResult.FAIL)
        error_tests = sum(1 for r in reports if r.result == TestResult.ERROR)
        
        overall_success_rate = sum(r.success_rate for r in reports) / total_tests if total_tests > 0 else 0.0
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'partial_tests': partial_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'overall_success_rate': overall_success_rate,
            'test_results': [
                {
                    'scenario': r.scenario.value,
                    'result': r.result.value,
                    'success_rate': r.success_rate,
                    'duration': r.duration,
                    'issues_count': len(r.issues_found)
                }
                for r in reports
            ]
        }
        
        self.logger.info(f"Test Suite Summary: {passed_tests}/{total_tests} passed, overall success rate: {overall_success_rate:.2%}")
        
        return summary
    
    def get_test_reports(self) -> List[TestReport]:
        """Get all test reports"""
        return self.test_reports.copy()
    
    def export_test_results(self, filepath: str):
        """Export test results to JSON file"""
        
        export_data = {
            'test_run_timestamp': datetime.now().isoformat(),
            'total_tests': len(self.test_reports),
            'reports': []
        }
        
        for report in self.test_reports:
            report_data = {
                'scenario': report.scenario.value,
                'result': report.result.value,
                'start_time': report.start_time.isoformat(),
                'end_time': report.end_time.isoformat(),
                'duration': report.duration,
                'success_rate': report.success_rate,
                'metrics': {
                    'total_requests': report.metrics.total_requests,
                    'successful_requests': report.metrics.successful_requests,
                    'failed_requests': report.metrics.failed_requests,
                    'average_response_time': report.metrics.average_response_time,
                    'max_response_time': report.metrics.max_response_time,
                    'min_response_time': report.metrics.min_response_time,
                    'error_types': dict(report.metrics.error_types),
                    'recovery_time': report.metrics.recovery_time,
                    'degradation_events': report.metrics.degradation_events,
                    'fallback_activations': report.metrics.fallback_activations,
                    'circuit_breaker_trips': report.metrics.circuit_breaker_trips
                },
                'issues_found': report.issues_found,
                'recommendations': report.recommendations
            }
            export_data['reports'].append(report_data)
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Test results exported to {filepath}")


# Convenience function for running error recovery validation
async def validate_error_recovery_system() -> List[TestReport]:
    """
    Convenience function to run complete error recovery validation
    
    Returns:
        List of test reports
    """
    tester = ErrorRecoveryTester()
    return await tester.run_comprehensive_test_suite()


# Example usage and test runner
if __name__ == "__main__":
    """Run error recovery validation"""
    
    async def main():
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Run comprehensive test suite
        tester = ErrorRecoveryTester()
        reports = await tester.run_comprehensive_test_suite()
        
        # Export results
        tester.export_test_results("error_recovery_test_results.json")
        
        # Print summary
        print("\n" + "="*70)
        print("ERROR RECOVERY VALIDATION COMPLETED")
        print("="*70)
        
        for report in reports:
            print(f"\n{report.scenario.value}: {report.result.value}")
            print(f"  Success Rate: {report.success_rate:.2%}")
            print(f"  Duration: {report.duration:.1f}s")
            print(f"  Requests: {report.metrics.total_requests}")
            print(f"  Avg Response Time: {report.metrics.average_response_time:.2f}s")
            
            if report.issues_found:
                print(f"  Issues: {', '.join(report.issues_found[:2])}")
        
        # Overall assessment
        passed_tests = sum(1 for r in reports if r.result == TestResult.PASS)
        total_tests = len(reports)
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ Error recovery system validation PASSED")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  Error recovery system validation PARTIAL")
        else:
            print("❌ Error recovery system validation FAILED")
    
    asyncio.run(main())
