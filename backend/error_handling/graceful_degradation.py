"""
Graceful Degradation Strategies for Vimarsh AI Agent

This module provides comprehensive fallback mechanisms and graceful degradation
strategies when various services fail, ensuring the system remains functional
and provides meaningful responses even during partial outages.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from .error_classifier import ErrorClassifier, ErrorCategory, ErrorSeverity, RecoveryStrategy

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of services that can fail"""
    LLM_SERVICE = "llm_service"           # Gemini Pro API
    VECTOR_SEARCH = "vector_search"       # Vector/RAG pipeline
    DATABASE = "database"                 # Data storage
    CONTENT_MODERATION = "content_moderation"  # Content safety
    EXPERT_REVIEW = "expert_review"       # Expert validation
    AUTHENTICATION = "authentication"     # User auth
    VOICE_PROCESSING = "voice_processing" # Speech services
    EXTERNAL_API = "external_api"         # General external APIs


class DegradationLevel(Enum):
    """Levels of service degradation"""
    FULL_SERVICE = "full_service"         # All services operational
    MINOR_DEGRADATION = "minor_degradation"  # Non-critical features affected
    MAJOR_DEGRADATION = "major_degradation"  # Significant functionality limited
    MINIMAL_SERVICE = "minimal_service"   # Basic functionality only
    EMERGENCY_MODE = "emergency_mode"     # Fallback to static responses


@dataclass
class ServiceHealth:
    """Health status of a service"""
    service_type: ServiceType
    is_healthy: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    response_time: float = 0.0
    uptime_percentage: float = 100.0
    degradation_level: DegradationLevel = DegradationLevel.FULL_SERVICE
    last_error: Optional[str] = None
    recovery_attempts: int = 0


@dataclass
class FallbackResponse:
    """A fallback response when primary service fails"""
    content: str
    confidence: float
    source: str
    limitations: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DegradationStrategy:
    """Base class for degradation strategies"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def execute(self, context: Dict[str, Any]) -> FallbackResponse:
        """Execute the degradation strategy"""
        raise NotImplementedError
    
    def is_applicable(self, failed_services: List[ServiceType], context: Dict[str, Any]) -> bool:
        """Check if this strategy is applicable for the given failures"""
        raise NotImplementedError


class LLMFallbackStrategy(DegradationStrategy):
    """Fallback strategy when LLM service fails"""
    
    def __init__(self):
        super().__init__(
            "LLM Fallback",
            "Provides responses when primary LLM service is unavailable"
        )
        self.static_responses = {
            "spiritual_question": [
                "I'm currently experiencing technical difficulties accessing my full knowledge base. "
                "However, I can share this fundamental teaching: The Bhagavad Gita teaches us that "
                "the soul is eternal and unchanging. Focus on your dharma (duty) and surrender the "
                "results to the Divine. 'You have the right to perform your actions, but never to "
                "the fruits of action.' (Bhagavad Gita 2.47)",
                
                "While my advanced capabilities are temporarily limited, I can offer this timeless wisdom: "
                "Lord Krishna teaches in the Gita that the mind can be both friend and enemy. Through "
                "regular practice of meditation and devotion, we can transcend temporary difficulties. "
                "'For one who has conquered the mind, the mind is the best of friends.' (Bhagavad Gita 6.6)",
                
                "Though I'm operating with reduced capabilities, this essential truth remains: "
                "All paths of sincere spiritual seeking ultimately lead to the Divine. Whether through "
                "karma yoga (action), bhakti yoga (devotion), or jnana yoga (knowledge), the goal "
                "is self-realization and union with the Supreme."
            ],
            
            "life_guidance": [
                "While my full guidance system is temporarily unavailable, remember this core principle: "
                "Life's challenges are opportunities for spiritual growth. Face them with courage, "
                "compassion, and trust in divine providence. Every difficulty carries within it the "
                "seeds of wisdom and strength.",
                
                "Though my services are limited right now, this wisdom endures: Live in harmony with "
                "your true nature. Perform your duties without attachment to results. Practice kindness, "
                "speak truthfully, and remember that you are not just the body and mind, but the eternal soul.",
                
                "Even with reduced capabilities, I can share this: The purpose of human life is to realize "
                "your divine nature. Use every experience - pleasant or unpleasant - as a stepping stone "
                "toward this ultimate goal. 'The wise see with equal vision a learned brahmin, a cow, "
                "an elephant, a dog, and a dog-eater.' (Bhagavad Gita 5.18)"
            ],
            
            "meditation_guidance": [
                "While my detailed meditation guidance is temporarily limited, here's a simple practice: "
                "Sit comfortably, close your eyes, and focus on your breath. When thoughts arise, gently "
                "return attention to breathing. Start with 5-10 minutes daily. This practice helps calm "
                "the mind and connect with your inner peace.",
                
                "Though my full meditation library is currently inaccessible, try this: Repeat a sacred "
                "mantra like 'Om' or 'So Hum' (I am That) with each breath. Let the sound vibrate through "
                "your being. This ancient practice helps transcend mental chatter and experience deeper states.",
                
                "With limited access to advanced techniques, focus on this fundamental: Meditation is about "
                "witnessing thoughts without attachment. You are the observer, not the thoughts themselves. "
                "This recognition is the foundation of all spiritual practice and self-realization."
            ]
        }
    
    def is_applicable(self, failed_services: List[ServiceType], context: Dict[str, Any]) -> bool:
        return ServiceType.LLM_SERVICE in failed_services
    
    async def execute(self, context: Dict[str, Any]) -> FallbackResponse:
        """Execute LLM fallback strategy"""
        user_query = context.get("user_query", "").lower()
        
        # Determine response category based on query keywords
        if any(word in user_query for word in ["meditat", "practice", "breathe", "mindful"]):
            category = "meditation_guidance"
        elif any(word in user_query for word in ["life", "problem", "decision", "help", "guidance"]):
            category = "life_guidance"
        else:
            category = "spiritual_question"
        
        # Select appropriate response
        import random
        responses = self.static_responses[category]
        selected_response = random.choice(responses)
        
        return FallbackResponse(
            content=selected_response,
            confidence=0.6,  # Lower confidence for static responses
            source="static_knowledge_base",
            limitations=[
                "Advanced AI capabilities temporarily unavailable",
                "Response from static knowledge base",
                "Cannot provide personalized guidance"
            ],
            suggestions=[
                "Try again in a few minutes for full AI capabilities",
                "Consult sacred texts directly for deeper study",
                "Consider speaking with a qualified spiritual teacher"
            ],
            metadata={"fallback_strategy": "llm_static", "category": category}
        )


class VectorSearchFallbackStrategy(DegradationStrategy):
    """Fallback strategy when vector search fails"""
    
    def __init__(self):
        super().__init__(
            "Vector Search Fallback",
            "Provides text-based search when vector search is unavailable"
        )
        # Simplified keyword-based search patterns
        self.keyword_mappings = {
            "karma": "Bhagavad Gita 2.47: 'You have the right to perform your actions, but never to the fruits of action.'",
            "dharma": "Bhagavad Gita 18.47: 'Better is one's own dharma, though performed imperfectly, than the dharma of another performed perfectly.'",
            "devotion": "Bhagavad Gita 9.22: 'Those who worship Me with devotion, meditating on My transcendental form, I provide what they lack and preserve what they have.'",
            "meditation": "Bhagavad Gita 6.19: 'As a lamp in a windless place does not waver, so the transcendentalist, whose mind is controlled, remains always steady in his meditation on the transcendent self.'",
            "suffering": "Bhagavad Gita 2.14: 'O son of Kunti, the nonpermanent appearance of happiness and distress, and their disappearance in due course, are like the appearance and disappearance of winter and summer seasons.'",
            "peace": "Bhagavad Gita 2.71: 'A person who is not disturbed by the incessant flow of desires can alone achieve peace, and not the man who strives to satisfy such desires.'",
            "surrender": "Bhagavad Gita 18.66: 'Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.'",
            "soul": "Bhagavad Gita 2.20: 'For the soul there is neither birth nor death. It is not slain when the body is slain.'",
            "wisdom": "Bhagavad Gita 4.38: 'In this world, there is nothing so sublime and pure as transcendental knowledge. Such knowledge is the mature fruit of all mysticism.'",
            "action": "Bhagavad Gita 3.8: 'Perform your prescribed duty, for doing so is better than not working. One cannot even maintain one's physical body without work.'"
        }
    
    def is_applicable(self, failed_services: List[ServiceType], context: Dict[str, Any]) -> bool:
        return ServiceType.VECTOR_SEARCH in failed_services
    
    async def execute(self, context: Dict[str, Any]) -> FallbackResponse:
        """Execute vector search fallback strategy"""
        user_query = context.get("user_query", "").lower()
        
        # Find relevant verses using keyword matching
        relevant_verses = []
        for keyword, verse in self.keyword_mappings.items():
            if keyword in user_query:
                relevant_verses.append(verse)
        
        if not relevant_verses:
            # Provide a general verse if no specific match
            relevant_verses = [self.keyword_mappings["wisdom"]]
        
        content = "While my advanced text search is temporarily limited, here are relevant teachings:\n\n"
        content += "\n\n".join(relevant_verses[:2])  # Limit to 2 verses
        
        return FallbackResponse(
            content=content,
            confidence=0.4,  # Lower confidence for keyword matching
            source="keyword_based_search",
            limitations=[
                "Advanced semantic search temporarily unavailable",
                "Using simplified keyword matching",
                "May miss contextually relevant texts"
            ],
            suggestions=[
                "Try again later for comprehensive text search",
                "Use specific Sanskrit terms for better matches",
                "Consult complete texts for broader context"
            ],
            metadata={"fallback_strategy": "keyword_search", "matched_keywords": list(self.keyword_mappings.keys())}
        )


class ContentModerationFallbackStrategy(DegradationStrategy):
    """Fallback strategy when content moderation fails"""
    
    def __init__(self):
        super().__init__(
            "Content Moderation Fallback",
            "Provides basic content filtering when advanced moderation is unavailable"
        )
        self.basic_filters = [
            "inappropriate", "offensive", "harmful", "dangerous",
            "violent", "hate", "discriminatory", "explicit"
        ]
    
    def is_applicable(self, failed_services: List[ServiceType], context: Dict[str, Any]) -> bool:
        return ServiceType.CONTENT_MODERATION in failed_services
    
    async def execute(self, context: Dict[str, Any]) -> FallbackResponse:
        """Execute content moderation fallback strategy"""
        content_to_check = context.get("content", "")
        
        # Basic word-based filtering
        flagged_words = [word for word in self.basic_filters if word in content_to_check.lower()]
        
        if flagged_words:
            content = ("I notice your query might contain sensitive content. While my advanced "
                      "content safety systems are temporarily limited, I'll provide guidance with "
                      "extra care for spiritual appropriateness and cultural sensitivity.")
        else:
            content = ("My advanced content moderation is temporarily limited, but I'll proceed "
                      "with heightened attention to spiritual and cultural appropriateness.")
        
        return FallbackResponse(
            content=content,
            confidence=0.3,  # Low confidence for basic filtering
            source="basic_content_filter",
            limitations=[
                "Advanced content moderation temporarily unavailable",
                "Using basic keyword filtering only",
                "May miss subtle content issues"
            ],
            suggestions=[
                "Ensure your questions are respectful and appropriate",
                "Avoid sensitive or controversial topics",
                "Try again later for full content safety features"
            ],
            metadata={"fallback_strategy": "basic_moderation", "flagged_words": flagged_words}
        )


class ExpertReviewFallbackStrategy(DegradationStrategy):
    """Fallback strategy when expert review system fails"""
    
    def __init__(self):
        super().__init__(
            "Expert Review Fallback",
            "Provides validated content when expert review system is unavailable"
        )
    
    def is_applicable(self, failed_services: List[ServiceType], context: Dict[str, Any]) -> bool:
        return ServiceType.EXPERT_REVIEW in failed_services
    
    async def execute(self, context: Dict[str, Any]) -> FallbackResponse:
        """Execute expert review fallback strategy"""
        content = ("While our expert review system is temporarily unavailable, I'll provide "
                  "guidance based on well-established spiritual teachings. Please note that "
                  "this response hasn't been validated by our spiritual scholars.")
        
        return FallbackResponse(
            content=content,
            confidence=0.5,
            source="pre_validated_content",
            limitations=[
                "Expert review system temporarily unavailable",
                "Response not validated by spiritual scholars",
                "Relying on pre-approved content patterns"
            ],
            suggestions=[
                "Cross-reference with authoritative spiritual texts",
                "Consult qualified spiritual teachers for validation",
                "Try again later for expert-reviewed responses"
            ],
            metadata={"fallback_strategy": "no_expert_review"}
        )


class GracefulDegradationManager:
    """Main manager for graceful degradation strategies"""
    
    def __init__(self):
        self.error_classifier = ErrorClassifier()
        self.service_health: Dict[ServiceType, ServiceHealth] = {}
        self.degradation_strategies: List[DegradationStrategy] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize service health tracking
        for service_type in ServiceType:
            self.service_health[service_type] = ServiceHealth(service_type)
        
        # Register degradation strategies
        self._register_strategies()
    
    def _register_strategies(self):
        """Register all degradation strategies"""
        self.degradation_strategies = [
            LLMFallbackStrategy(),
            VectorSearchFallbackStrategy(),
            ContentModerationFallbackStrategy(),
            ExpertReviewFallbackStrategy()
        ]
    
    async def handle_service_failure(self, 
                                   failed_service: ServiceType,
                                   context: Dict[str, Any],
                                   original_error: Optional[Exception] = None) -> FallbackResponse:
        """Handle a specific service failure with appropriate degradation"""
        
        # Update service health
        self._update_service_health(failed_service, is_healthy=False, error=original_error)
        
        # Find applicable strategies
        applicable_strategies = [
            strategy for strategy in self.degradation_strategies
            if strategy.is_applicable([failed_service], context)
        ]
        
        if not applicable_strategies:
            return await self._emergency_fallback(context)
        
        # Execute the first applicable strategy
        strategy = applicable_strategies[0]
        try:
            logger.info(f"Executing degradation strategy: {strategy.name}")
            response = await strategy.execute(context)
            
            # Add degradation notice
            response.content = self._add_degradation_notice(response.content, failed_service)
            
            return response
            
        except Exception as e:
            logger.error(f"Degradation strategy failed: {str(e)}")
            return await self._emergency_fallback(context)
    
    async def handle_multiple_failures(self,
                                     failed_services: List[ServiceType],
                                     context: Dict[str, Any]) -> FallbackResponse:
        """Handle multiple simultaneous service failures"""
        
        # Update health for all failed services
        for service in failed_services:
            self._update_service_health(service, is_healthy=False)
        
        # Determine degradation level
        degradation_level = self._assess_degradation_level(failed_services)
        
        if degradation_level == DegradationLevel.EMERGENCY_MODE:
            return await self._emergency_fallback(context)
        
        # Find strategies that can handle the combination of failures
        applicable_strategies = [
            strategy for strategy in self.degradation_strategies
            if strategy.is_applicable(failed_services, context)
        ]
        
        if not applicable_strategies:
            return await self._emergency_fallback(context)
        
        # Execute strategies in order of priority
        responses = []
        for strategy in applicable_strategies[:2]:  # Limit to top 2 strategies
            try:
                response = await strategy.execute(context)
                responses.append(response)
            except Exception as e:
                logger.error(f"Strategy {strategy.name} failed: {str(e)}")
        
        if responses:
            # Combine responses from multiple strategies
            return self._combine_responses(responses, failed_services)
        else:
            return await self._emergency_fallback(context)
    
    def _update_service_health(self, 
                              service_type: ServiceType,
                              is_healthy: bool,
                              error: Optional[Exception] = None,
                              response_time: Optional[float] = None):
        """Update health status for a service"""
        health = self.service_health[service_type]
        health.is_healthy = is_healthy
        health.last_check = datetime.now()
        
        if not is_healthy:
            health.error_count += 1
            health.last_error = str(error) if error else "Unknown error"
            health.recovery_attempts = 0
        else:
            # Reset error count on successful recovery
            health.error_count = max(0, health.error_count - 1)
        
        if response_time:
            health.response_time = response_time
        
        # Update degradation level based on error frequency
        if health.error_count > 10:
            health.degradation_level = DegradationLevel.EMERGENCY_MODE
        elif health.error_count > 5:
            health.degradation_level = DegradationLevel.MAJOR_DEGRADATION
        elif health.error_count > 2:
            health.degradation_level = DegradationLevel.MINOR_DEGRADATION
        else:
            health.degradation_level = DegradationLevel.FULL_SERVICE
    
    def _assess_degradation_level(self, failed_services: List[ServiceType]) -> DegradationLevel:
        """Assess overall system degradation level"""
        critical_services = [ServiceType.LLM_SERVICE, ServiceType.DATABASE]
        
        if ServiceType.LLM_SERVICE in failed_services and ServiceType.VECTOR_SEARCH in failed_services:
            return DegradationLevel.EMERGENCY_MODE
        
        if any(service in failed_services for service in critical_services):
            return DegradationLevel.MAJOR_DEGRADATION
        
        if len(failed_services) > 2:
            return DegradationLevel.MAJOR_DEGRADATION
        
        if len(failed_services) > 0:
            return DegradationLevel.MINOR_DEGRADATION
        
        return DegradationLevel.FULL_SERVICE
    
    async def _emergency_fallback(self, context: Dict[str, Any]) -> FallbackResponse:
        """Last resort emergency fallback when all strategies fail"""
        content = ("I'm currently experiencing significant technical difficulties and operating "
                  "in emergency mode. While I cannot provide my usual comprehensive guidance, "
                  "I encourage you to:\n\n"
                  "• Consult the Bhagavad Gita directly for timeless wisdom\n"
                  "• Practice meditation and self-reflection\n"
                  "• Seek guidance from qualified spiritual teachers\n"
                  "• Remember that all challenges are opportunities for growth\n\n"
                  "Please try again later when my services are restored.")
        
        return FallbackResponse(
            content=content,
            confidence=0.2,
            source="emergency_static_response",
            limitations=[
                "All advanced services temporarily unavailable",
                "Operating in emergency mode",
                "Limited to static responses only"
            ],
            suggestions=[
                "Try again in 10-15 minutes",
                "Consult primary spiritual texts directly",
                "Seek human spiritual guidance",
                "Practice meditation while waiting"
            ],
            metadata={"fallback_strategy": "emergency_mode"}
        )
    
    def _add_degradation_notice(self, content: str, failed_service: ServiceType) -> str:
        """Add a notice about service degradation to the response"""
        service_notices = {
            ServiceType.LLM_SERVICE: "Note: My advanced AI capabilities are temporarily limited.",
            ServiceType.VECTOR_SEARCH: "Note: Advanced text search is temporarily unavailable.",
            ServiceType.CONTENT_MODERATION: "Note: Enhanced content safety features are temporarily limited.",
            ServiceType.EXPERT_REVIEW: "Note: Expert review validation is temporarily unavailable.",
            ServiceType.VOICE_PROCESSING: "Note: Voice features may be temporarily limited.",
        }
        
        notice = service_notices.get(failed_service, "Note: Some features are temporarily limited.")
        return f"{notice}\n\n{content}"
    
    def _combine_responses(self, 
                          responses: List[FallbackResponse],
                          failed_services: List[ServiceType]) -> FallbackResponse:
        """Combine multiple fallback responses into one"""
        
        # Use the response with highest confidence as base
        best_response = max(responses, key=lambda r: r.confidence)
        
        # Combine limitations and suggestions
        all_limitations = []
        all_suggestions = []
        
        for response in responses:
            all_limitations.extend(response.limitations)
            all_suggestions.extend(response.suggestions)
        
        # Remove duplicates while preserving order
        unique_limitations = list(dict.fromkeys(all_limitations))
        unique_suggestions = list(dict.fromkeys(all_suggestions))
        
        return FallbackResponse(
            content=best_response.content,
            confidence=best_response.confidence * 0.8,  # Slightly reduce confidence for combined response
            source="combined_fallback_strategies",
            limitations=unique_limitations,
            suggestions=unique_suggestions,
            metadata={
                "fallback_strategy": "combined",
                "failed_services": [service.value for service in failed_services],
                "strategies_used": len(responses)
            }
        )
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        status = {
            "overall_health": "healthy",
            "degradation_level": DegradationLevel.FULL_SERVICE.value,
            "services": {},
            "active_degradations": [],
            "recommendations": []
        }
        
        unhealthy_services = []
        for service_type, health in self.service_health.items():
            status["services"][service_type.value] = {
                "healthy": health.is_healthy,
                "error_count": health.error_count,
                "last_check": health.last_check.isoformat(),
                "degradation_level": health.degradation_level.value,
                "uptime_percentage": health.uptime_percentage
            }
            
            if not health.is_healthy:
                unhealthy_services.append(service_type)
                status["active_degradations"].append({
                    "service": service_type.value,
                    "level": health.degradation_level.value,
                    "error_count": health.error_count
                })
        
        # Determine overall health
        if unhealthy_services:
            overall_degradation = self._assess_degradation_level(unhealthy_services)
            status["degradation_level"] = overall_degradation.value
            
            if overall_degradation in [DegradationLevel.MAJOR_DEGRADATION, DegradationLevel.EMERGENCY_MODE]:
                status["overall_health"] = "degraded"
            else:
                status["overall_health"] = "partial"
        
        # Add recommendations
        if unhealthy_services:
            status["recommendations"] = [
                "Monitor failed services for recovery",
                "Check service logs for error patterns",
                "Consider manual intervention if degradation persists",
                "Notify users of potential service limitations"
            ]
        
        return status
    
    async def attempt_service_recovery(self, service_type: ServiceType) -> bool:
        """Attempt to recover a failed service"""
        health = self.service_health[service_type]
        health.recovery_attempts += 1
        
        # Implement service-specific recovery logic here
        # For now, simulate recovery attempt
        await asyncio.sleep(1)  # Simulate recovery time
        
        # For demonstration, mark as recovered after 3 attempts
        if health.recovery_attempts >= 3:
            self._update_service_health(service_type, is_healthy=True)
            logger.info(f"Service {service_type.value} recovered after {health.recovery_attempts} attempts")
            return True
        
        logger.info(f"Recovery attempt {health.recovery_attempts} for {service_type.value} failed")
        return False


# Convenience functions
async def handle_service_failure(service_type: ServiceType, 
                               context: Dict[str, Any],
                               error: Optional[Exception] = None) -> FallbackResponse:
    """Convenience function to handle a single service failure"""
    manager = GracefulDegradationManager()
    return await manager.handle_service_failure(service_type, context, error)


async def handle_multiple_failures(failed_services: List[ServiceType],
                                 context: Dict[str, Any]) -> FallbackResponse:
    """Convenience function to handle multiple service failures"""
    manager = GracefulDegradationManager()
    return await manager.handle_multiple_failures(failed_services, context)


def get_system_health() -> Dict[str, Any]:
    """Convenience function to get system health status"""
    manager = GracefulDegradationManager()
    return manager.get_system_health_status()
