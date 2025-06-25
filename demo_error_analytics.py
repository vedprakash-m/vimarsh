#!/usr/bin/env python3
"""
Demo script for Error Analytics and Pattern Learning System

This script demonstrates the capabilities of the error analytics system
by simulating various error scenarios and generating analytics reports.
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add the backend directory to the path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

from error_handling.error_analytics import ErrorAnalytics, AnalyticsMetric
from error_handling.error_classifier import ErrorCategory, ErrorSeverity


class ErrorAnalyticsDemo:
    """Demo class for error analytics system"""
    
    def __init__(self):
        self.analytics = ErrorAnalytics(
            storage_path="demo_analytics_data",
            max_events=1000,
            pattern_detection_window=24
        )
        
        # Demo error scenarios
        self.error_scenarios = [
            {
                "error": ValueError("Invalid spiritual query format"),
                "component": "query_validator",
                "context": {
                    "user_input": "not a proper question",
                    "validation_step": "format_check",
                    "user_visible": True
                },
                "frequency": 15,
                "severity_pattern": [ErrorSeverity.MEDIUM] * 12 + [ErrorSeverity.LOW] * 3
            },
            {
                "error": ConnectionError("Gemini API connection timeout"),
                "component": "llm_client",
                "context": {
                    "api_endpoint": "generativelanguage.googleapis.com",
                    "timeout_duration": 30,
                    "retry_count": 3,
                    "user_visible": True,
                    "session_interrupted": True
                },
                "frequency": 8,
                "severity_pattern": [ErrorSeverity.HIGH] * 6 + [ErrorSeverity.CRITICAL] * 2
            },
            {
                "error": KeyError("Missing citation in response"),
                "component": "citation_extractor",
                "context": {
                    "response_length": 500,
                    "expected_citations": 2,
                    "found_citations": 0,
                    "user_visible": False
                },
                "frequency": 12,
                "severity_pattern": [ErrorSeverity.MEDIUM] * 10 + [ErrorSeverity.HIGH] * 2
            },
            {
                "error": TimeoutError("Vector search timeout"),
                "component": "vector_search",
                "context": {
                    "query_embedding_time": 2.1,
                    "search_time": 15.3,
                    "timeout_threshold": 10.0,
                    "collection_size": 50000
                },
                "frequency": 5,
                "severity_pattern": [ErrorSeverity.HIGH] * 4 + [ErrorSeverity.CRITICAL] * 1
            },
            {
                "error": RuntimeError("Content moderation service unavailable"),
                "component": "content_moderator",
                "context": {
                    "moderation_service": "internal",
                    "fallback_attempted": True,
                    "fallback_successful": False,
                    "user_visible": True
                },
                "frequency": 3,
                "severity_pattern": [ErrorSeverity.CRITICAL] * 3
            },
            {
                "error": ValueError("Sanskrit transliteration failed"),
                "component": "text_processor",
                "context": {
                    "input_language": "sanskrit",
                    "transliteration_scheme": "IAST",
                    "character_encoding": "UTF-8",
                    "user_visible": False
                },
                "frequency": 20,
                "severity_pattern": [ErrorSeverity.LOW] * 18 + [ErrorSeverity.MEDIUM] * 2
            },
            {
                "error": PermissionError("Expert review access denied"),
                "component": "expert_review_system",
                "context": {
                    "reviewer_id": "expert_123",
                    "review_level": "theological",
                    "permission_required": "REVIEW_THEOLOGICAL",
                    "user_visible": False
                },
                "frequency": 4,
                "severity_pattern": [ErrorSeverity.MEDIUM] * 3 + [ErrorSeverity.HIGH] * 1
            }
        ]
    
    async def run_demo(self):
        """Run the complete error analytics demo"""
        print("🔍 Error Analytics and Pattern Learning System Demo")
        print("=" * 60)
        
        # Simulate error events over time
        await self.simulate_error_events()
        
        # Demonstrate system health monitoring
        await self.demonstrate_system_health()
        
        # Show pattern detection capabilities
        await self.demonstrate_pattern_detection()
        
        # Generate comprehensive analytics report
        await self.demonstrate_analytics_report()
        
        # Show recovery tracking
        await self.demonstrate_recovery_tracking()
        
        # Demonstrate real-time monitoring
        await self.demonstrate_real_time_monitoring()
        
        print("\n✅ Demo completed successfully!")
        print("Analytics data saved to: demo_analytics_data/")
    
    async def simulate_error_events(self):
        """Simulate various error events over time"""
        print("\n📊 Simulating Error Events")
        print("-" * 30)
        
        total_events = 0
        
        # Simulate errors over the past 6 hours
        base_time = datetime.now() - timedelta(hours=6)
        
        for scenario in self.error_scenarios:
            print(f"Simulating {scenario['frequency']} instances of: {scenario['error']}")
            
            for i in range(scenario['frequency']):
                # Spread events over time with some clustering
                time_offset = random.uniform(0, 6 * 3600)  # 6 hours in seconds
                event_time = base_time + timedelta(seconds=time_offset)
                
                # Vary the context slightly for each event
                context = scenario['context'].copy()
                context['event_id'] = f"{scenario['component']}_{i}"
                context['timestamp_offset'] = time_offset
                
                # Simulate user sessions
                if random.random() < 0.7:  # 70% of errors have user context
                    context['user_id'] = f"user_{random.randint(1, 100)}"
                    context['session_id'] = f"session_{random.randint(1, 50)}"
                
                # Create a modified analytics instance with custom timestamp
                class TimestampedAnalytics(ErrorAnalytics):
                    def __init__(self, base_analytics, custom_time):
                        self.classifier = base_analytics.classifier
                        self.storage_path = base_analytics.storage_path
                        self.max_events = base_analytics.max_events
                        self.pattern_detection_window = base_analytics.pattern_detection_window
                        self.recent_events = base_analytics.recent_events
                        self.detected_patterns = base_analytics.detected_patterns
                        self._metrics_cache = base_analytics._metrics_cache
                        self._cache_timestamp = base_analytics._cache_timestamp
                        self._cache_ttl = base_analytics._cache_ttl
                        self.logger = base_analytics.logger
                        self.custom_time = custom_time
                
                timestamped_analytics = TimestampedAnalytics(self.analytics, event_time)
                
                # Record the error with custom timestamp
                event = await timestamped_analytics.record_error(
                    error=scenario['error'],
                    component=scenario['component'],
                    context=context,
                    user_id=context.get('user_id'),
                    session_id=context.get('session_id')
                )
                
                # Override timestamp to simulate past events
                event.timestamp = event_time
                
                total_events += 1
                
                # Simulate some recovery attempts
                if random.random() < 0.4:  # 40% of errors have recovery attempts
                    recovery_time = random.uniform(0.5, 5.0)
                    recovery_success = random.random() < 0.7  # 70% success rate
                    recovery_method = random.choice([
                        "retry_with_backoff", "fallback_service", 
                        "circuit_breaker", "manual_intervention"
                    ])
                    
                    await self.analytics.record_recovery_attempt(
                        event_id=f"{scenario['component']}_{event.timestamp.timestamp()}",
                        recovery_successful=recovery_success,
                        recovery_time=recovery_time,
                        recovery_method=recovery_method
                    )
                
                # Small delay to simulate real-time
                await asyncio.sleep(0.01)
        
        print(f"✅ Generated {total_events} error events across {len(self.error_scenarios)} scenarios")
    
    async def demonstrate_system_health(self):
        """Demonstrate system health monitoring"""
        print("\n🏥 System Health Monitoring")
        print("-" * 30)
        
        health = await self.analytics.get_system_health()
        
        print(f"Overall Health Score: {health.overall_health_score:.1f}/100")
        print(f"Error Rate: {health.error_rate:.2f} errors/minute")
        print(f"Mean Recovery Time: {health.mean_recovery_time:.2f} seconds")
        print(f"Critical Error Count: {health.critical_error_count}")
        print(f"User Impact Score: {health.user_impact_score:.2f}/10")
        print(f"Reliability Score: {health.reliability_score:.1f}/100")
        
        print("\nTop Error Categories:")
        for category, count in health.top_error_categories[:5]:
            print(f"  • {category.value}: {count} errors")
        
        if health.trending_issues:
            print("\nTrending Issues:")
            for issue in health.trending_issues:
                print(f"  ⚠️  {issue}")
        
        # Health score interpretation
        if health.overall_health_score >= 90:
            print("🟢 System health is EXCELLENT")
        elif health.overall_health_score >= 70:
            print("🟡 System health is GOOD with minor issues")
        elif health.overall_health_score >= 50:
            print("🟠 System health is FAIR - attention needed")
        else:
            print("🔴 System health is POOR - immediate action required")
    
    async def demonstrate_pattern_detection(self):
        """Demonstrate error pattern detection"""
        print("\n🔍 Error Pattern Detection")
        print("-" * 30)
        
        # Trigger pattern detection
        await self.analytics._detect_patterns()
        
        patterns = await self.analytics.get_error_patterns(
            min_frequency=3,
            min_confidence=0.5
        )
        
        if not patterns:
            print("No significant patterns detected yet.")
            return
        
        print(f"Detected {len(patterns)} error patterns:")
        
        for i, pattern in enumerate(patterns[:5], 1):
            print(f"\nPattern {i}: {pattern.description}")
            print(f"  Frequency: {pattern.frequency} occurrences")
            print(f"  Confidence: {pattern.confidence_score:.2f}")
            print(f"  First Seen: {pattern.first_seen.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Last Seen: {pattern.last_seen.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Affected Components: {', '.join(pattern.affected_components)}")
            
            print("  Severity Distribution:")
            for severity, count in pattern.severity_distribution.items():
                print(f"    • {severity.value}: {count}")
            
            if pattern.suggested_actions:
                print("  Suggested Actions:")
                for action in pattern.suggested_actions[:3]:
                    print(f"    → {action}")
            
            if pattern.common_contexts:
                print("  Common Context Patterns:")
                for context in pattern.common_contexts[:2]:
                    print(f"    • {context['key']}: {context['value']} ({context['frequency']} times)")
    
    async def demonstrate_analytics_report(self):
        """Demonstrate comprehensive analytics report"""
        print("\n📈 Comprehensive Analytics Report")
        print("-" * 30)
        
        # Generate report for last 6 hours
        report = await self.analytics.get_analytics_report(
            time_range=timedelta(hours=6)
        )
        
        if 'error' in report:
            print(f"❌ Error generating report: {report['error']}")
            return
        
        # Report summary
        summary = report['summary']
        print(f"Report Period: {report['report_period']['duration_hours']:.1f} hours")
        print(f"Total Errors: {summary['total_errors']}")
        print(f"Unique Error Types: {summary['unique_error_types']}")
        print(f"Affected Components: {summary['affected_components']}")
        print(f"Recovery Rate: {summary['recovery_rate_percent']:.1f}%")
        
        # Distribution analysis
        distributions = report['distributions']
        print("\nError Severity Distribution:")
        for severity, count in distributions['severity'].items():
            print(f"  • {severity}: {count}")
        
        print("\nError Category Distribution:")
        for category, count in distributions['category'].items():
            print(f"  • {category}: {count}")
        
        # Component analysis
        component_analysis = report['component_analysis']
        print("\nMost Problematic Components:")
        for component, error_count in component_analysis['most_problematic'][:3]:
            print(f"  • {component}: {error_count} errors")
        
        # Recommendations
        recommendations = report['recommendations']
        if recommendations:
            print("\nSystem Recommendations:")
            for rec in recommendations:
                print(f"  💡 {rec}")
        
        # Temporal patterns
        if distributions['hourly_pattern']:
            print("\nHourly Error Distribution:")
            for hour in sorted(distributions['hourly_pattern'].keys()):
                count = distributions['hourly_pattern'][hour]
                bar = "█" * min(count, 20)  # Simple bar chart
                print(f"  {hour:2d}:00 │{bar} ({count})")
    
    async def demonstrate_recovery_tracking(self):
        """Demonstrate recovery attempt tracking"""
        print("\n🔄 Recovery Attempt Tracking")
        print("-" * 30)
        
        # Analyze recovery patterns from recent events
        recent_events = [
            e for e in self.analytics.recent_events 
            if e.timestamp > datetime.now() - timedelta(hours=6)
        ]
        
        recovery_events = [e for e in recent_events if e.recovery_attempted]
        successful_recoveries = [e for e in recovery_events if e.recovery_successful]
        failed_recoveries = [e for e in recovery_events if not e.recovery_successful]
        
        print(f"Total Events: {len(recent_events)}")
        print(f"Recovery Attempts: {len(recovery_events)}")
        print(f"Successful Recoveries: {len(successful_recoveries)}")
        print(f"Failed Recoveries: {len(failed_recoveries)}")
        
        if recovery_events:
            success_rate = len(successful_recoveries) / len(recovery_events) * 100
            print(f"Recovery Success Rate: {success_rate:.1f}%")
            
            # Recovery time analysis
            recovery_times = [e.resolution_time for e in recovery_events if e.resolution_time]
            if recovery_times:
                avg_recovery_time = sum(recovery_times) / len(recovery_times)
                min_recovery_time = min(recovery_times)
                max_recovery_time = max(recovery_times)
                
                print(f"Average Recovery Time: {avg_recovery_time:.2f} seconds")
                print(f"Fastest Recovery: {min_recovery_time:.2f} seconds")
                print(f"Slowest Recovery: {max_recovery_time:.2f} seconds")
            
            # Recovery method analysis
            recovery_methods = {}
            for event in recovery_events:
                method = event.context.get('recovery_method', 'unknown')
                recovery_methods[method] = recovery_methods.get(method, 0) + 1
            
            print("\nRecovery Methods Used:")
            for method, count in sorted(recovery_methods.items(), key=lambda x: x[1], reverse=True):
                success_count = sum(1 for e in recovery_events 
                                  if e.context.get('recovery_method') == method and e.recovery_successful)
                success_rate = success_count / count * 100 if count > 0 else 0
                print(f"  • {method}: {count} attempts ({success_rate:.0f}% success)")
    
    async def demonstrate_real_time_monitoring(self):
        """Demonstrate real-time monitoring capabilities"""
        print("\n⚡ Real-time Monitoring Simulation")
        print("-" * 30)
        
        print("Simulating real-time error stream for 10 seconds...")
        
        start_time = time.time()
        real_time_events = 0
        
        while time.time() - start_time < 10:
            # Randomly generate an error event
            scenario = random.choice(self.error_scenarios)
            
            context = scenario['context'].copy()
            context['real_time'] = True
            context['simulation_time'] = time.time() - start_time
            
            await self.analytics.record_error(
                error=scenario['error'],
                component=scenario['component'],
                context=context,
                user_id=f"realtime_user_{random.randint(1, 20)}",
                session_id=f"realtime_session_{random.randint(1, 10)}"
            )
            
            real_time_events += 1
            
            # Show real-time health updates every 2 seconds
            if real_time_events % 3 == 0:
                health = await self.analytics.get_system_health()
                print(f"  [{time.time() - start_time:.1f}s] Health: {health.overall_health_score:.1f}, "
                      f"Error Rate: {health.error_rate:.2f}/min, "
                      f"Critical: {health.critical_error_count}")
            
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        print(f"✅ Processed {real_time_events} real-time events")
        
        # Final health check
        final_health = await self.analytics.get_system_health()
        print(f"Final Health Score: {final_health.overall_health_score:.1f}/100")
    
    def save_demo_results(self):
        """Save demo results for examination"""
        try:
            demo_summary = {
                "demo_timestamp": datetime.now().isoformat(),
                "total_events": len(self.analytics.recent_events),
                "total_patterns": len(self.analytics.detected_patterns),
                "scenarios_simulated": len(self.error_scenarios),
                "demo_data_location": str(self.analytics.storage_path)
            }
            
            with open("demo_analytics_summary.json", "w") as f:
                json.dump(demo_summary, f, indent=2)
            
            print(f"\n💾 Demo summary saved to: demo_analytics_summary.json")
            
        except Exception as e:
            print(f"❌ Failed to save demo results: {e}")


async def main():
    """Run the error analytics demo"""
    demo = ErrorAnalyticsDemo()
    
    try:
        await demo.run_demo()
        demo.save_demo_results()
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Ensure event loop compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
