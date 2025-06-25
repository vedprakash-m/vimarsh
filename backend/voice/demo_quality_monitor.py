#!/usr/bin/env python3
"""
Demo script for voice quality monitoring and improvement systems.
Tests quality analysis, performance tracking, and improvement recommendations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.quality_monitor import (
    VoiceQualityMonitor,
    QualityMetric,
    QualityLevel,
    ImprovementAction
)
import asyncio
import time
import random

async def demo_voice_quality_monitoring():
    """Demonstrate voice quality monitoring capabilities."""
    print("=== Vimarsh Voice Quality Monitoring Demo ===\n")
    
    # Initialize the quality monitor
    quality_monitor = VoiceQualityMonitor()
    quality_monitor.start_monitoring()
    
    # Test 1: Recording Voice Synthesis Events
    print("1. Recording Voice Synthesis Events")
    print("-" * 40)
    
    # Simulate various voice synthesis scenarios
    test_scenarios = [
        {
            "session_id": "user_123",
            "text": "ॐ शान्ति शान्ति शान्तिः",
            "voice_settings": {
                "voice_name": "en-IN-PrabhatNeural",
                "speed": 0.8,
                "pitch": 1.0,
                "volume": 0.9
            },
            "response_time": 1.2,
            "success": True,
            "context": {
                "language": "hi",
                "content_type": "mantra",
                "cultural_context": "devotional"
            }
        },
        {
            "session_id": "user_123",
            "text": "The concept of dharma is central to Hindu philosophy",
            "voice_settings": {
                "voice_name": "en-US-AriaNeural",
                "speed": 1.0,
                "pitch": 1.1,
                "volume": 1.0
            },
            "response_time": 0.9,
            "success": True,
            "context": {
                "language": "en",
                "content_type": "teaching",
                "cultural_context": "educational"
            }
        },
        {
            "session_id": "user_456",
            "text": "कृष्ण भगवान की शिक्षाएं अत्यंत गहरी हैं",
            "voice_settings": {
                "voice_name": "hi-IN-MadhurNeural",
                "speed": 0.9,
                "pitch": 0.9,
                "volume": 0.8
            },
            "response_time": 1.8,
            "success": True,
            "context": {
                "language": "hi",
                "content_type": "devotional",
                "cultural_context": "spiritual"
            }
        },
        {
            "session_id": "user_789",
            "text": "Failed synthesis attempt",
            "voice_settings": {
                "voice_name": "invalid-voice",
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            },
            "response_time": 5.0,
            "success": False,
            "context": {
                "language": "en",
                "content_type": "general"
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Recording synthesis event {i}:")
        print(f"  Session: {scenario['session_id']}")
        print(f"  Text: {scenario['text']}")
        print(f"  Success: {scenario['success']}")
        print(f"  Response Time: {scenario['response_time']}s")
        
        # Simulate audio data
        audio_data = b"simulated_audio_data" if scenario['success'] else b""
        
        quality_monitor.record_voice_synthesis(
            session_id=scenario['session_id'],
            audio_data=audio_data,
            text=scenario['text'],
            voice_settings=scenario['voice_settings'],
            response_time=scenario['response_time'],
            success=scenario['success'],
            context=scenario['context']
        )
        print(f"  ✓ Recorded\n")
    
    # Test 2: Recording User Feedback
    print("2. Recording User Feedback")
    print("-" * 40)
    
    feedback_scenarios = [
        {
            "session_id": "user_123",
            "metric": QualityMetric.PRONUNCIATION,
            "score": 0.9,
            "context": {"comment": "Excellent Sanskrit pronunciation"}
        },
        {
            "session_id": "user_123",
            "metric": QualityMetric.NATURALNESS,
            "score": 0.7,
            "context": {"comment": "Sounds a bit robotic"}
        },
        {
            "session_id": "user_456",
            "metric": QualityMetric.EMOTIONAL_TONE,
            "score": 0.95,
            "context": {"comment": "Perfect devotional tone"}
        },
        {
            "session_id": "user_456",
            "metric": QualityMetric.PACE,
            "score": 0.6,
            "context": {"comment": "Too slow for my preference"}
        }
    ]
    
    for feedback in feedback_scenarios:
        print(f"Recording user feedback:")
        print(f"  Session: {feedback['session_id']}")
        print(f"  Metric: {feedback['metric'].value}")
        print(f"  Score: {feedback['score']}")
        print(f"  Comment: {feedback['context'].get('comment', 'N/A')}")
        
        quality_monitor.record_user_feedback(
            session_id=feedback['session_id'],
            metric=feedback['metric'],
            score=feedback['score'],
            context=feedback['context']
        )
        print(f"  ✓ Recorded\n")
    
    # Test 3: Session Quality Report
    print("3. Session Quality Report")
    print("-" * 40)
    
    session_report = quality_monitor.get_quality_report("user_123")
    print(f"Quality Report for Session: user_123")
    print(f"Total Requests: {session_report['summary']['total_requests']}")
    print(f"Success Rate: {session_report['summary']['success_rate']:.1%}")
    print(f"Average Response Time: {session_report['summary']['average_response_time']:.2f}s")
    print(f"Average Quality Score: {session_report['summary']['average_quality_score']:.2f}")
    print(f"User Feedback Count: {session_report['summary']['user_feedback_count']}")
    print()
    
    # Show metric details
    print("Metric Performance:")
    for metric, data in session_report['metric_details'].items():
        if data['average'] > 0:  # Only show metrics with data
            print(f"  {metric.title()}: {data['average']:.2f} ({data['level']})")
    print()
    
    # Show issues and recommendations
    if session_report['issues']:
        print("Identified Issues:")
        for issue in session_report['issues']:
            print(f"  - {issue['issue']} (Severity: {issue['severity']})")
            print(f"    Current: {issue['current_score']:.2f}, Target: {issue['target_score']:.2f}")
        print()
    
    # Test 4: Global Quality Report
    print("4. Global Quality Report")
    print("-" * 40)
    
    global_report = quality_monitor.get_quality_report()
    print(f"Global Quality Report:")
    print(f"Total Requests: {global_report['summary']['total_requests']}")
    print(f"Success Rate: {global_report['summary']['success_rate']:.1%}")
    print(f"Average Response Time: {global_report['summary']['average_response_time']:.2f}s")
    print(f"Average Quality Score: {global_report['summary']['average_quality_score']:.2f}")
    print()
    
    # Test 5: Performance Insights
    print("5. Performance Insights")
    print("-" * 40)
    
    insights = quality_monitor.get_performance_insights()
    print(f"Overall System Health: {insights['overall_health'].upper()}")
    
    if insights['key_strengths']:
        print(f"Key Strengths:")
        for strength in insights['key_strengths']:
            print(f"  ✓ {strength.replace('_', ' ').title()}")
    
    if insights['areas_for_improvement']:
        print(f"Areas for Improvement:")
        for area in insights['areas_for_improvement']:
            print(f"  ⚠ {area.replace('_', ' ').title()}")
    
    if insights['urgent_actions']:
        print(f"Urgent Actions Required:")
        for action in insights['urgent_actions']:
            print(f"  ⚡ {action}")
    
    if insights['recommendations']:
        print(f"Recommendations:")
        for rec in insights['recommendations']:
            print(f"  💡 {rec}")
    print()
    
    # Test 6: Simulate Real-time Monitoring
    print("6. Real-time Monitoring Simulation")
    print("-" * 40)
    
    print("Simulating continuous voice synthesis events...")
    
    # Simulate multiple sessions with varying quality
    sessions = ["user_001", "user_002", "user_003"]
    texts = [
        "Welcome to spiritual guidance",
        "ॐ गं गणपतये नमः",
        "Let us meditate together",
        "धर्म एव हतो हन्ति धर्मो रक्षति रक्षितः",
        "Find peace in your heart"
    ]
    
    for i in range(10):
        session_id = random.choice(sessions)
        text = random.choice(texts)
        
        # Simulate varying quality based on different factors
        success = random.random() > 0.05  # 95% success rate
        response_time = random.uniform(0.5, 3.0)
        
        voice_settings = {
            "voice_name": random.choice(["en-IN-PrabhatNeural", "hi-IN-MadhurNeural"]),
            "speed": random.uniform(0.7, 1.3),
            "pitch": random.uniform(0.8, 1.2),
            "volume": random.uniform(0.7, 1.0)
        }
        
        context = {
            "language": random.choice(["en", "hi"]),
            "content_type": random.choice(["teaching", "devotional", "general"]),
            "timestamp": time.time()
        }
        
        audio_data = b"simulated_audio" if success else b""
        
        quality_monitor.record_voice_synthesis(
            session_id=session_id,
            audio_data=audio_data,
            text=text,
            voice_settings=voice_settings,
            response_time=response_time,
            success=success,
            context=context
        )
        
        if i % 3 == 0:  # Show progress
            print(f"  Processed {i+1} events...")
    
    print("✓ Simulation completed")
    print()
    
    # Test 7: Updated Performance Analysis
    print("7. Updated Performance Analysis")
    print("-" * 40)
    
    final_report = quality_monitor.get_quality_report()
    print(f"Final System Stats:")
    print(f"  Total Requests: {final_report['summary']['total_requests']}")
    print(f"  Success Rate: {final_report['summary']['success_rate']:.1%}")
    print(f"  Avg Response Time: {final_report['summary']['average_response_time']:.2f}s")
    print(f"  Avg Quality Score: {final_report['summary']['average_quality_score']:.2f}")
    print()
    
    # Show quality levels distribution
    quality_levels = {}
    for metric, data in final_report['metric_details'].items():
        if data['average'] > 0:
            level = data['level']
            quality_levels[level] = quality_levels.get(level, 0) + 1
    
    print("Quality Distribution:")
    for level, count in quality_levels.items():
        print(f"  {level.title()}: {count} metrics")
    print()
    
    # Test 8: Stop Monitoring
    print("8. Monitoring Control")
    print("-" * 40)
    
    print("Stopping voice quality monitoring...")
    quality_monitor.stop_monitoring()
    
    # Try to record an event (should be ignored)
    quality_monitor.record_voice_synthesis(
        session_id="test",
        audio_data=b"test",
        text="test",
        voice_settings={},
        response_time=1.0,
        success=True
    )
    
    print("✓ Monitoring stopped - new events ignored")
    print()
    
    print("=== Demo Completed Successfully ===")

if __name__ == "__main__":
    asyncio.run(demo_voice_quality_monitoring())
