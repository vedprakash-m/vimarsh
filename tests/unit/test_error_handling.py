import asyncio
import time
from typing import Callable

import pytest

from backend.error_handling.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception_factory",
    [
        lambda: ValueError("bad payload"),
        lambda: TimeoutError("upstream timeout"),
        lambda: RuntimeError("quota exhausted"),
    ],
)
async def test_circuit_breaker_opens_on_repeated_failures(exception_factory: Callable[[], Exception]):
    """After N consecutive failures, breaker should open and raise CircuitBreakerError."""

    config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=1,
        timeout_seconds=0.1,
        minimum_throughput=3,
    )
    breaker = CircuitBreaker("failure-test", config=config)

    async def _failing_action():
        await asyncio.sleep(0)
        raise exception_factory()

    # Trigger failures.
    for _ in range(config.failure_threshold):
        with pytest.raises(type(exception_factory())):
            await breaker.call(_failing_action)

    # One more call should raise CircuitBreakerError (breaker is OPEN).
    with pytest.raises(CircuitBreakerError):
        await breaker.call(_failing_action)

    assert breaker.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_circuit_breaker_slow_call_counts_towards_open():
    """A high proportion of slow calls should open the circuit breaker."""

    config = CircuitBreakerConfig(
        failure_threshold=100,  # large so slow-call rate triggers first
        slow_call_threshold=0.01,  # 10 ms
        slow_call_rate_threshold=0.6,  # 60 % slow calls
        minimum_throughput=5,
    )
    breaker = CircuitBreaker("slow-call-test", config=config)

    async def _slow_action():
        # deliberately exceed slow_call_threshold
        await asyncio.sleep(config.slow_call_threshold + 0.02)
        return "done"

    # Make several slow calls – this should eventually open the breaker
    for _ in range(6):
        try:
            await breaker.call(_slow_action)
        except CircuitBreakerError:
            break

    assert breaker.state == CircuitState.OPEN 