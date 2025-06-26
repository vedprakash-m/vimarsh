"""
Example integration of Vimarsh monitoring system
Demonstrates how to integrate monitoring into spiritual guidance functions.
"""

import asyncio
import time
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring.vimarsh_monitor import (
    VimarshMonitor,
    SpiritualGuidanceMetrics,
    CostMetrics,
    VoiceInteractionMetrics,
    monitor_spiritual_guidance,
    monitor_performance,
    log_expert_review
)

# Initialize monitor
monitor = VimarshMonitor()

@monitor_spiritual_guidance(query_type="text", language="en")
async def provide_spiritual_guidance(query: str, language: str = "en") -> Dict[str, Any]:
    """Example spiritual guidance function with monitoring."""
    
    # Simulate spiritual guidance processing
    await asyncio.sleep(0.5)  # Simulate LLM processing time
    
    # Example response
    response = {
        "guidance": "Dear seeker, Lord Krishna teaches us in the Bhagavad Gita...",
        "citations": [
            {"source": "Bhagavad Gita", "chapter": 2, "verse": 47},
            {"source": "Bhagavad Gita", "chapter": 4, "verse": 7}
        ],
        "quality_score": 0.95,
        "expert_review_required": False
    }
    
    # Log cost metrics for AI operation
    cost_metrics = CostMetrics(
        operation_type="spiritual_guidance",
        token_count=150,
        cost_usd=0.0045,
        model_used="gemini-pro",
        cache_hit=False
    )
    monitor.log_cost_metrics(cost_metrics)
    
    # Check if expert review is needed
    if response["quality_score"] < 0.8:
        log_expert_review(
            content_id=f"query_{int(time.time())}",
            flag_reason="low_quality_score",
            severity="medium"
        )
    
    return response

@monitor_performance("voice_processing")
async def process_voice_input(audio_data: bytes, language: str = "en") -> Dict[str, Any]:
    """Example voice processing function with monitoring."""
    
    start_time = time.time()
    
    # Simulate voice processing
    await asyncio.sleep(0.3)
    
    # Example voice processing results
    result = {
        "transcription": "What is the meaning of dharma?",
        "confidence": 0.92,
        "language_detected": language,
        "sanskrit_terms": ["dharma"],
        "processing_time": time.time() - start_time
    }
    
    # Log voice interaction metrics
    voice_metrics = VoiceInteractionMetrics(
        language=language,
        duration_seconds=result["processing_time"],
        transcription_accuracy=result["confidence"],
        tts_quality_score=0.88,
        sanskrit_terms_detected=len(result["sanskrit_terms"])
    )
    monitor.log_voice_interaction(voice_metrics)
    
    return result

@monitor_performance("expert_validation")
async def validate_spiritual_content(content: str, source: str) -> Dict[str, Any]:
    """Example expert validation function with monitoring."""
    
    # Simulate expert validation
    await asyncio.sleep(0.1)
    
    # Example validation logic
    quality_indicators = {
        "cultural_sensitivity": 0.95,
        "scriptural_accuracy": 0.90,
        "spiritual_depth": 0.88,
        "linguistic_correctness": 0.92
    }
    
    overall_score = sum(quality_indicators.values()) / len(quality_indicators)
    
    # Log validation metrics
    validation_metrics = SpiritualGuidanceMetrics(
        query_type="validation",
        language="en",
        response_time_ms=100,
        quality_score=overall_score,
        source_citations=1,
        expert_reviewed=True
    )
    monitor.log_spiritual_guidance(validation_metrics)
    
    return {
        "validated": overall_score > 0.85,
        "quality_score": overall_score,
        "quality_indicators": quality_indicators,
        "recommendations": []
    }

async def demonstrate_monitoring():
    """Demonstrate the monitoring system in action."""
    
    print("🙏 Vimarsh Monitoring System Demonstration")
    print("=" * 50)
    
    # Example 1: Text-based spiritual guidance
    print("\n1. Text-based Spiritual Guidance:")
    guidance_result = await provide_spiritual_guidance(
        "What is the nature of duty?", 
        language="en"
    )
    print(f"   Quality Score: {guidance_result['quality_score']}")
    print(f"   Citations: {len(guidance_result['citations'])}")
    
    # Example 2: Voice interaction
    print("\n2. Voice Interaction Processing:")
    voice_result = await process_voice_input(
        b"mock_audio_data", 
        language="hi"
    )
    print(f"   Transcription: {voice_result['transcription']}")
    print(f"   Confidence: {voice_result['confidence']}")
    
    # Example 3: Expert validation
    print("\n3. Expert Content Validation:")
    validation_result = await validate_spiritual_content(
        "Lord Krishna teaches us about dharma...",
        "Bhagavad Gita"
    )
    print(f"   Validated: {validation_result['validated']}")
    print(f"   Quality Score: {validation_result['quality_score']:.2f}")
    
    # Example 4: Cost monitoring
    print("\n4. Cost Monitoring:")
    high_cost_operation = CostMetrics(
        operation_type="complex_analysis",
        token_count=2000,
        cost_usd=15.50,  # High cost to trigger alert
        model_used="gemini-pro"
    )
    monitor.log_cost_metrics(high_cost_operation)
    print(f"   High cost operation logged: ${high_cost_operation.cost_usd}")
    
    # Example 5: Expert review trigger
    print("\n5. Expert Review System:")
    log_expert_review(
        content_id="content_12345",
        flag_reason="cultural_sensitivity_concern",
        severity="high"
    )
    print("   Expert review triggered for cultural sensitivity")
    
    print("\n✅ Monitoring demonstration completed")
    print("🕉️ All metrics have been logged to Application Insights")

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_monitoring())
