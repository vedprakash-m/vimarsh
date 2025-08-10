#!/usr/bin/env python3
"""
Service Reliability Module - Circuit Breaker and Retry Logic

This module implements reliability patterns to reduce template fallback rates
and improve service stability for the Vimarsh application.
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, Callable, TypeVar, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests due to failures
    HALF_OPEN = "half_open" # Testing if service has recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 60  # Seconds to wait before trying half-open
    success_threshold: int = 3  # Successes needed in half-open to close
    
class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.logger = logger
        
    def is_open(self) -> bool:
        """Check if circuit breaker is open (blocking requests)"""
        if self.state == CircuitBreakerState.OPEN:
            # Check if we should transition to half-open
            if (self.last_failure_time and 
                datetime.now(timezone.utc) - self.last_failure_time > 
                timedelta(seconds=self.config.recovery_timeout)):
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                self.logger.info("🔄 Circuit breaker transitioning to HALF_OPEN")
                return False
            return True
        return False
    
    def record_success(self):
        """Record a successful operation"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.logger.info("✅ Circuit breaker CLOSED - service recovered")
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self.logger.warning(f"⚠️ Circuit breaker OPEN - {self.failure_count} failures")
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Failed during testing, go back to open
            self.state = CircuitBreakerState.OPEN
            self.logger.warning("⚠️ Circuit breaker back to OPEN - half-open test failed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "is_blocking": self.is_open()
        }

class ExponentialBackoffRetry:
    """Exponential backoff retry pattern"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.logger = logger
    
    async def execute(self, func: Callable[[], T]) -> T:
        """Execute function with exponential backoff retry"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                result = await func() if asyncio.iscoroutinefunction(func) else func()
                if attempt > 0:
                    self.logger.info(f"✅ Retry successful on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:  # Not the last attempt
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    self.logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"❌ All {self.max_attempts} attempts failed. Last error: {e}")
        
        # Re-raise the last exception if all attempts failed
        if last_exception:
            raise last_exception
        
        raise RuntimeError("All retry attempts failed with no exception recorded")

class FallbackTracker:
    """Track fallback usage for monitoring and alerting"""
    
    def __init__(self):
        self.fallback_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}
        self.response_times: Dict[str, list] = {}
        self.fallback_reasons: Dict[str, list] = {}
        self.logger = logger
        
    def record_success(self, service: str = "default"):
        """Record successful service call"""
        if service not in self.success_counts:
            self.success_counts[service] = 0
        self.success_counts[service] += 1
    
    def record_fallback(self, reason: str, service: str = "default"):
        """Record fallback usage with reason"""
        if service not in self.fallback_counts:
            self.fallback_counts[service] = 0
            self.fallback_reasons[service] = []
        
        self.fallback_counts[service] += 1
        self.fallback_reasons[service].append({
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Keep only last 100 reasons
        if len(self.fallback_reasons[service]) > 100:
            self.fallback_reasons[service] = self.fallback_reasons[service][-100:]
    
    def record_response_time(self, response_time: float, service: str = "default"):
        """Record response time"""
        if service not in self.response_times:
            self.response_times[service] = []
        
        self.response_times[service].append(response_time)
        
        # Keep only last 100 response times
        if len(self.response_times[service]) > 100:
            self.response_times[service] = self.response_times[service][-100:]
    
    def get_fallback_rate(self, service: str = "default") -> float:
        """Get current fallback rate (0.0 to 1.0)"""
        fallbacks = self.fallback_counts.get(service, 0)
        successes = self.success_counts.get(service, 0)
        total = fallbacks + successes
        
        if total == 0:
            return 0.0
        
        return fallbacks / total
    
    def get_avg_response_time(self, service: str = "default") -> float:
        """Get average response time"""
        times = self.response_times.get(service, [])
        if not times:
            return 0.0
        return sum(times) / len(times)
    
    def get_stats(self, service: str = "default") -> Dict[str, Any]:
        """Get comprehensive stats for service"""
        fallback_rate = self.get_fallback_rate(service)
        avg_response_time = self.get_avg_response_time(service)
        recent_reasons = self.fallback_reasons.get(service, [])[-10:]  # Last 10 reasons
        
        return {
            "fallback_rate": fallback_rate,
            "fallback_percentage": f"{fallback_rate:.1%}",
            "total_fallbacks": self.fallback_counts.get(service, 0),
            "total_successes": self.success_counts.get(service, 0),
            "avg_response_time_ms": avg_response_time,
            "recent_fallback_reasons": recent_reasons,
            "health_status": self._determine_health_status(fallback_rate)
        }
    
    def _determine_health_status(self, fallback_rate: float) -> str:
        """Determine health status based on fallback rate"""
        if fallback_rate < 0.1:  # < 10%
            return "excellent"
        elif fallback_rate < 0.2:  # < 20%
            return "good"
        elif fallback_rate < 0.5:  # < 50%
            return "degraded"
        else:
            return "poor"

class ServiceRecoveryManager:
    """Manages service recovery attempts"""
    
    def __init__(self):
        self.recovery_attempts: Dict[str, int] = {}
        self.last_recovery_time: Dict[str, datetime] = {}
        self.recovery_interval = timedelta(minutes=5)  # Try recovery every 5 minutes
        self.logger = logger
    
    def should_attempt_recovery(self, service_name: str) -> bool:
        """Check if we should attempt recovery for a service"""
        last_attempt = self.last_recovery_time.get(service_name)
        
        if not last_attempt:
            return True
        
        return datetime.now(timezone.utc) - last_attempt > self.recovery_interval
    
    async def attempt_recovery(self, service_name: str, recovery_func: Callable) -> bool:
        """Attempt to recover a failed service"""
        if not self.should_attempt_recovery(service_name):
            return False
        
        self.recovery_attempts[service_name] = self.recovery_attempts.get(service_name, 0) + 1
        self.last_recovery_time[service_name] = datetime.now(timezone.utc)
        
        try:
            self.logger.info(f"🔄 Attempting recovery for {service_name} (attempt #{self.recovery_attempts[service_name]})")
            
            result = await recovery_func() if asyncio.iscoroutinefunction(recovery_func) else recovery_func()
            
            if result:
                self.logger.info(f"✅ Successfully recovered {service_name}")
                # Reset recovery count on success
                self.recovery_attempts[service_name] = 0
                return True
            else:
                self.logger.warning(f"⚠️ Recovery attempt failed for {service_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Recovery attempt failed for {service_name}: {e}")
            return False
    
    def get_recovery_status(self, service_name: str) -> Dict[str, Any]:
        """Get recovery status for a service"""
        return {
            "attempts": self.recovery_attempts.get(service_name, 0),
            "last_attempt": self.last_recovery_time.get(service_name),
            "next_attempt_allowed": self.should_attempt_recovery(service_name)
        }

# Global instances for use across the application
circuit_breaker = CircuitBreaker()
fallback_tracker = FallbackTracker()
recovery_manager = ServiceRecoveryManager()

def get_reliability_status() -> Dict[str, Any]:
    """Get overall reliability status"""
    return {
        "circuit_breaker": circuit_breaker.get_status(),
        "fallback_stats": fallback_tracker.get_stats(),
        "recovery_status": {
            service: recovery_manager.get_recovery_status(service)
            for service in recovery_manager.recovery_attempts.keys()
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
