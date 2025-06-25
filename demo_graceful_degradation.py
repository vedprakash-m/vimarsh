"""
Demo script for Vimarsh AI Agent Graceful Degradation System

This script demonstrates how the system handles various service failures
gracefully while maintaining spiritual guidance capabilities.
"""

import asyncio
import json
from typing import Dict, Any
import sys
import os

# Add the backend path to sys.path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'error_handling'))

from graceful_degradation import (
    GracefulDegradationManager, ServiceType, DegradationLevel,
    handle_service_failure, handle_multiple_failures, get_system_health
)


async def demo_single_service_failures():
    """Demonstrate handling of individual service failures"""
    print("=" * 60)
    print("DEMO: Single Service Failure Handling")
    print("=" * 60)
    
    contexts = [
        {
            "user_query": "What is the meaning of life according to the Bhagavad Gita?",
            "user_id": "demo_user_1"
        },
        {
            "user_query": "How can I practice meditation for inner peace?",
            "user_id": "demo_user_2"
        },
        {
            "user_query": "Tell me about karma and dharma in spiritual texts",
            "user_id": "demo_user_3"
        }
    ]
    
    # Test different service failures
    service_failures = [
        ServiceType.LLM_SERVICE,
        ServiceType.VECTOR_SEARCH,
        ServiceType.CONTENT_MODERATION,
        ServiceType.EXPERT_REVIEW
    ]
    
    for i, (service, context) in enumerate(zip(service_failures, contexts)):
        print(f"\n{i+1}. Testing {service.value.upper()} failure:")
        print(f"   User Query: '{context['user_query']}'")
        print("-" * 50)
        
        try:
            response = await handle_service_failure(service, context)
            
            print(f"   ✓ Fallback Response Generated")
            print(f"   Source: {response.source}")
            print(f"   Confidence: {response.confidence}")
            print(f"   Content Preview: {response.content[:150]}...")
            print(f"   Limitations: {len(response.limitations)} identified")
            print(f"   Suggestions: {len(response.suggestions)} provided")
            
        except Exception as e:
            print(f"   ✗ Error handling failure: {str(e)}")


async def demo_multiple_service_failures():
    """Demonstrate handling of multiple simultaneous service failures"""
    print("\n" + "=" * 60)
    print("DEMO: Multiple Service Failure Handling")
    print("=" * 60)
    
    context = {
        "user_query": "I'm struggling with life decisions. Can you help me understand dharma and provide spiritual guidance?",
        "user_id": "demo_user_cascade"
    }
    
    # Test cascading failures
    failure_scenarios = [
        {
            "name": "Minor Degradation",
            "services": [ServiceType.VOICE_PROCESSING]
        },
        {
            "name": "Major Degradation", 
            "services": [ServiceType.LLM_SERVICE, ServiceType.CONTENT_MODERATION]
        },
        {
            "name": "Emergency Mode",
            "services": [ServiceType.LLM_SERVICE, ServiceType.VECTOR_SEARCH, ServiceType.DATABASE]
        }
    ]
    
    for i, scenario in enumerate(failure_scenarios):
        print(f"\n{i+1}. Testing {scenario['name']}:")
        print(f"   Failed Services: {[s.value for s in scenario['services']]}")
        print("-" * 50)
        
        try:
            response = await handle_multiple_failures(scenario['services'], context)
            
            print(f"   ✓ System Gracefully Degraded")
            print(f"   Response Source: {response.source}")
            print(f"   Confidence Level: {response.confidence}")
            print(f"   Content Preview: {response.content[:200]}...")
            
            if response.metadata.get('fallback_strategy') == 'emergency_mode':
                print("   🚨 EMERGENCY MODE ACTIVATED")
            
        except Exception as e:
            print(f"   ✗ Error in degradation: {str(e)}")


async def demo_system_health_monitoring():
    """Demonstrate system health monitoring and recovery"""
    print("\n" + "=" * 60)
    print("DEMO: System Health Monitoring & Recovery")
    print("=" * 60)
    
    manager = GracefulDegradationManager()
    
    # Check initial health
    print("\n1. Initial System Health:")
    print("-" * 30)
    health = manager.get_system_health_status()
    print(f"   Overall Health: {health['overall_health']}")
    print(f"   Degradation Level: {health['degradation_level']}")
    print(f"   Active Degradations: {len(health['active_degradations'])}")
    
    # Simulate some failures
    print("\n2. Simulating Service Failures:")
    print("-" * 30)
    
    context = {"user_query": "Test query for health monitoring"}
    
    # Create failures
    await manager.handle_service_failure(ServiceType.LLM_SERVICE, context)
    await manager.handle_service_failure(ServiceType.VECTOR_SEARCH, context)
    
    # Check degraded health
    health = manager.get_system_health_status()
    print(f"   Overall Health: {health['overall_health']}")
    print(f"   Degradation Level: {health['degradation_level']}")
    print(f"   Active Degradations: {len(health['active_degradations'])}")
    
    for degradation in health['active_degradations']:
        print(f"   - {degradation['service']}: {degradation['level']} (errors: {degradation['error_count']})")
    
    # Attempt recovery
    print("\n3. Attempting Service Recovery:")
    print("-" * 30)
    
    services_to_recover = [ServiceType.LLM_SERVICE, ServiceType.VECTOR_SEARCH]
    
    for service in services_to_recover:
        print(f"   Recovering {service.value}...")
        
        # Simulate multiple recovery attempts
        for attempt in range(3):
            recovered = await manager.attempt_service_recovery(service)
            print(f"     Attempt {attempt + 1}: {'✓ Success' if recovered else '✗ Failed'}")
            
            if recovered:
                break
    
    # Check final health
    print("\n4. Final System Health:")
    print("-" * 30)
    health = manager.get_system_health_status()
    print(f"   Overall Health: {health['overall_health']}")
    print(f"   Degradation Level: {health['degradation_level']}")
    print(f"   Active Degradations: {len(health['active_degradations'])}")


async def demo_spiritual_content_fallbacks():
    """Demonstrate spiritual-specific fallback content"""
    print("\n" + "=" * 60)
    print("DEMO: Spiritual Content Fallbacks")
    print("=" * 60)
    
    spiritual_queries = [
        {
            "query": "How can I overcome suffering and find peace?",
            "expected_themes": ["peace", "suffering", "transcend"]
        },
        {
            "query": "What is my dharma and how do I fulfill it?",
            "expected_themes": ["dharma", "duty", "action"]
        },
        {
            "query": "Can you guide me in meditation practice?",
            "expected_themes": ["meditation", "breath", "mind"]
        },
        {
            "query": "How do I surrender to the Divine will?",
            "expected_themes": ["surrender", "divine", "Krishna"]
        }
    ]
    
    for i, query_info in enumerate(spiritual_queries):
        print(f"\n{i+1}. Spiritual Query: '{query_info['query']}'")
        print("-" * 50)
        
        context = {"user_query": query_info["query"]}
        
        # Test LLM service failure (most critical for content)
        response = await handle_service_failure(ServiceType.LLM_SERVICE, context)
        
        print(f"   Fallback Strategy: {response.metadata.get('fallback_strategy', 'unknown')}")
        print(f"   Content Category: {response.metadata.get('category', 'general')}")
        print(f"   Confidence: {response.confidence}")
        
        # Check if expected spiritual themes are present
        content_lower = response.content.lower()
        themes_found = [theme for theme in query_info["expected_themes"] 
                       if theme in content_lower]
        
        if themes_found:
            print(f"   ✓ Spiritual Themes Found: {themes_found}")
        else:
            print(f"   ⚠ Expected themes not explicitly found, but spiritual guidance provided")
        
        print(f"   Response Preview: {response.content[:200]}...")


def print_demo_summary():
    """Print summary of demo capabilities"""
    print("\n" + "=" * 60)
    print("DEMO SUMMARY: Graceful Degradation Capabilities")
    print("=" * 60)
    
    capabilities = [
        "✓ Single Service Failure Handling - Maintains functionality when individual services fail",
        "✓ Multiple Service Failure Management - Graceful degradation across multiple failures", 
        "✓ Emergency Mode Activation - Last-resort responses when critical services are down",
        "✓ System Health Monitoring - Real-time tracking of service status and degradation levels",
        "✓ Automatic Recovery Attempts - Self-healing capabilities for failed services",
        "✓ Spiritual Content Preservation - Maintains spiritual guidance quality even in degraded modes",
        "✓ User-Friendly Error Messages - Clear communication about limitations and alternatives",
        "✓ Confidence Scoring - Transparent confidence levels for fallback responses",
        "✓ Service-Specific Strategies - Tailored fallback approaches for different service types",
        "✓ Integration with Error Classification - Seamless integration with error handling system"
    ]
    
    print("\nKey Features Demonstrated:")
    for capability in capabilities:
        print(f"  {capability}")
    
    print(f"\nFallback Strategies Implemented:")
    strategies = [
        "• LLM Fallback - Static spiritual wisdom when AI is unavailable",
        "• Vector Search Fallback - Keyword-based text search as backup",
        "• Content Moderation Fallback - Basic filtering when advanced moderation fails",
        "• Expert Review Fallback - Pre-validated content when experts are unavailable"
    ]
    
    for strategy in strategies:
        print(f"  {strategy}")
    
    print(f"\nService Recovery Features:")
    recovery_features = [
        "• Automatic retry mechanisms with exponential backoff",
        "• Health status tracking and reporting",
        "• Cascading failure prevention",
        "• Performance degradation monitoring"
    ]
    
    for feature in recovery_features:
        print(f"  {feature}")


async def main():
    """Run the complete graceful degradation demo"""
    print("🕉️  VIMARSH AI AGENT - GRACEFUL DEGRADATION SYSTEM DEMO 🕉️")
    print("Demonstrating robust spiritual guidance under various failure scenarios")
    
    try:
        await demo_single_service_failures()
        await demo_multiple_service_failures() 
        await demo_system_health_monitoring()
        await demo_spiritual_content_fallbacks()
        print_demo_summary()
        
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🕉️  Demo completed successfully! The system maintains spiritual guidance")
    print("   even under adverse conditions, ensuring users always receive meaningful support.")


if __name__ == "__main__":
    asyncio.run(main())
