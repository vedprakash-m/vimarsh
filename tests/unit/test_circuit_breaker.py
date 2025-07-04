import asyncio
from datetime import timedelta

import pytest

from backend.error_handling.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _successful_action() -> str:
    """Dummy coroutine that succeeds quickly."""
    await asyncio.sleep(0)  # allow event-loop context switch
    return "ok"


async def _failing_action() -> None:
    """Dummy coroutine that always fails."""
    await asyncio.sleep(0)
    raise ValueError("simulated failure")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions():
    """CircuitBreaker should move CLOSED → OPEN → HALF_OPEN → CLOSED.

    We use a very small `failure_threshold` and `timeout_seconds` so the test
    completes in milliseconds and stays deterministic.
    """

    config = CircuitBreakerConfig(
        failure_threshold=2,  # open after two failures
        success_threshold=1,  # close after one success in half-open
        timeout_seconds=0.05,  # 50 ms before attempting reset
        minimum_throughput=2,  # evaluate immediately
    )

    breaker = CircuitBreaker("unit-test-service", config=config)

    # First failure — breaker still CLOSED and raises original error.
    with pytest.raises(ValueError):
        await breaker.call(_failing_action)
    assert breaker.state == CircuitState.CLOSED

    # Second failure — breaker should OPEN and raise CircuitBreakerError.
    with pytest.raises(CircuitBreakerError):
        await breaker.call(_failing_action)
    assert breaker.state == CircuitState.OPEN

    # Wait a bit longer than the timeout, so HALF_OPEN attempt is allowed.
    await asyncio.sleep(config.timeout_seconds + 0.01)

    # Next successful call should transition HALF_OPEN → CLOSED.
    result = await breaker.call(_successful_action)
    assert result == "ok"
    assert breaker.state == CircuitState.CLOSED

    # Sanity-check metrics updated as expected.
    metrics = breaker.get_state()["metrics"]
    assert metrics["failed_calls"] == 2
    assert metrics["successful_calls"] >= 1


@pytest.mark.asyncio
async def test_circuit_breaker_resets_after_timeout_and_success():
    """Breaker should move OPEN → HALF_OPEN after timeout, and back to CLOSED after a success."""

    config = CircuitBreakerConfig(
        failure_threshold=1,
        success_threshold=1,
        timeout_seconds=0.05,
        minimum_throughput=1,
    )
    breaker = CircuitBreaker("reset-test", config=config)

    async def _fail():
        raise RuntimeError("boom")

    # Trigger open state.
    with pytest.raises(RuntimeError):
        await breaker.call(_fail)
    with pytest.raises(CircuitBreakerError):
        await breaker.call(_fail)
    assert breaker.state == CircuitState.OPEN

    # wait and then succeed
    await asyncio.sleep(config.timeout_seconds + 0.02)

    async def _succeed():
        return "ok"

    result = await breaker.call(_succeed)
    assert result == "ok"
    assert breaker.state == CircuitState.CLOSED 