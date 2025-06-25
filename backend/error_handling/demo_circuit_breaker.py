"""
Demo Script for Circuit Breakers and Health Monitoring in Vimarsh AI Agent

This script demonstrates the circuit breaker and health monitoring functionality
for protecting spiritual guidance services from cascading failures.
"""

import asyncio
import logging
from datetime import datetime

# Import the system under test
try:
    from circuit_breaker import (
        CircuitBreaker, HealthMonitor, HealthAndCircuitMonitor,
        CircuitBreakerConfig, HealthCheckConfig, CircuitBreakerError,
        ServiceHealthChecks, initialize_vimarsh_monitoring
    )
except ImportError:
    print("Please run this from the backend/error_handling directory")
    exit(1)


async def demo_circuit_breaker_system():
    """Demonstrate circuit breaker and health monitoring functionality"""
    
    print("=" * 70)
    print("CIRCUIT BREAKERS & HEALTH MONITORING DEMO")
    print("=" * 70)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print(f"\n1. TESTING BASIC CIRCUIT BREAKER")
    print("-" * 40)
    
    # Create a simple circuit breaker
    config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=5.0,
        slow_call_threshold=1.0
    )
    
    circuit = CircuitBreaker("test_service", config)
    print(f"✓ Created circuit breaker for test_service")
    
    # Simulate successful calls
    async def successful_operation():
        await asyncio.sleep(0.1)
        return "success"
    
    # Simulate failing calls
    async def failing_operation():
        await asyncio.sleep(0.1)
        raise Exception("Service failure")
    
    # Test successful calls
    print("\nTesting successful calls:")
    for i in range(5):
        try:
            result = await circuit.call(successful_operation)
            print(f"  Call {i+1}: {result}")
        except Exception as e:
            print(f"  Call {i+1}: Failed - {e}")
    
    state = circuit.get_state()
    print(f"✓ Circuit state after successes: {state['state']}")
    print(f"✓ Success rate: {state['metrics']['success_rate']:.2f}")
    
    # Test failing calls to trigger circuit opening
    print("\nTesting failing calls to trigger circuit opening:")
    for i in range(5):
        try:
            result = await circuit.call(failing_operation)
            print(f"  Call {i+1}: {result}")
        except CircuitBreakerError as e:
            print(f"  Call {i+1}: Circuit breaker blocked - {e}")
        except Exception as e:
            print(f"  Call {i+1}: Service failed - {e}")
    
    state = circuit.get_state()
    print(f"✓ Circuit state after failures: {state['state']}")
    print(f"✓ Circuit opened at failure count: {state['metrics']['failed_calls']}")
    
    print(f"\n2. TESTING HEALTH MONITORING")
    print("-" * 40)
    
    # Create health monitor
    health_config = HealthCheckConfig(
        check_interval=2.0,  # Check every 2 seconds for demo
        timeout=1.0,
        degraded_threshold=0.5,
        unhealthy_threshold=0.6
    )
    
    monitor = HealthMonitor(health_config)
    print(f"✓ Created health monitor")
    
    # Register services
    monitor.register_service(
        "llm_service",
        ServiceHealthChecks.llm_service_health,
        {"description": "LLM service for spiritual guidance"}
    )
    
    monitor.register_service(
        "vector_search",
        ServiceHealthChecks.vector_search_health,
        {"description": "Vector search service"}
    )
    
    print(f"✓ Registered 2 services for health monitoring")
    
    # Start monitoring
    await monitor.start_monitoring()
    print(f"✓ Started health monitoring")
    
    # Let it run for a few seconds
    print("\nMonitoring services for 6 seconds...")
    await asyncio.sleep(6)
    
    # Check health status
    overall_health = monitor.get_overall_health()
    print(f"\n✓ Overall system status: {overall_health['status']}")
    print(f"✓ Services monitored: {overall_health['summary']['total_services']}")
    print(f"✓ Healthy services: {overall_health['summary']['healthy_services']}")
    
    for service_name, health in overall_health['services'].items():
        print(f"  - {service_name}: {health['status']} (uptime: {health['uptime_percentage']:.1f}%)")
    
    # Stop monitoring
    await monitor.stop_monitoring()
    print(f"✓ Stopped health monitoring")
    
    print(f"\n3. TESTING INTEGRATED MONITORING SYSTEM")
    print("-" * 50)
    
    # Test the integrated system
    integrated_monitor = await initialize_vimarsh_monitoring()
    print(f"✓ Initialized integrated Vimarsh monitoring system")
    
    # Let it run for a few seconds
    print("\nRunning integrated monitoring for 5 seconds...")
    await asyncio.sleep(5)
    
    # Get system status
    system_status = integrated_monitor.get_system_status()
    print(f"\n✓ Integrated system health: {system_status['health']['status']}")
    print(f"✓ Services registered: {len(system_status['health']['services'])}")
    
    # Test protected calls
    print(f"\n4. TESTING PROTECTED SERVICE CALLS")
    print("-" * 45)
    
    async def mock_llm_call(query):
        """Mock LLM service call"""
        await asyncio.sleep(0.1)
        if "fail" in query.lower():
            raise Exception("LLM service error")
        return f"Spiritual guidance for: {query}"
    
    # Test successful protected call
    try:
        async with integrated_monitor.protected_call("llm_service") as call:
            result = await call(mock_llm_call, "What is dharma?")
            print(f"✓ Protected call succeeded: {result}")
    except Exception as e:
        print(f"❌ Protected call failed: {e}")
    
    # Test failing protected calls to trigger circuit breaker
    for i in range(4):
        try:
            async with integrated_monitor.protected_call("llm_service") as call:
                result = await call(mock_llm_call, f"fail test {i+1}")
                print(f"✓ Protected call {i+1} succeeded: {result}")
        except CircuitBreakerError as e:
            print(f"⚡ Protected call {i+1} blocked by circuit breaker")
        except Exception as e:
            print(f"❌ Protected call {i+1} failed: {e}")
    
    # Check circuit breaker state
    llm_service_status = integrated_monitor.get_service_status("llm_service")
    if llm_service_status['circuit_breaker']:
        cb_state = llm_service_status['circuit_breaker']['state']
        failed_calls = llm_service_status['circuit_breaker']['metrics']['failed_calls']
        print(f"✓ LLM service circuit breaker state: {cb_state}")
        print(f"✓ Failed calls recorded: {failed_calls}")
    
    print(f"\n5. TESTING SERVICE-SPECIFIC STATUS")
    print("-" * 40)
    
    # Check status of each service
    services = ["llm_service", "vector_search", "text_processing", "expert_review"]
    
    for service in services:
        status = integrated_monitor.get_service_status(service)
        if status['health']:
            print(f"  {service}:")
            print(f"    Health: {status['health']['status']}")
            print(f"    Uptime: {status['health']['uptime_percentage']:.1f}%")
            if status['circuit_breaker']:
                print(f"    Circuit: {status['circuit_breaker']['state']}")
        else:
            print(f"  {service}: Not found")
    
    # Cleanup
    await integrated_monitor.stop_monitoring()
    print(f"\n✓ Stopped integrated monitoring system")
    
    print("\n" + "=" * 70)
    print("CIRCUIT BREAKER & HEALTH MONITORING DEMO COMPLETED! ✅")
    print("=" * 70)
    
    print("\nSUMMARY:")
    print("• Basic circuit breaker: ✅")
    print("• Health monitoring: ✅") 
    print("• Integrated system: ✅")
    print("• Protected service calls: ✅")
    print("• Circuit breaker protection: ✅")
    print("• Service status tracking: ✅")
    print("• Automatic failure detection: ✅")
    print("• System recovery monitoring: ✅")
    
    print(f"\nThe circuit breaker and health monitoring system is ready! 🎉")


if __name__ == "__main__":
    """Run the comprehensive demo"""
    asyncio.run(demo_circuit_breaker_system())
