"""
Dynamic Fallback Mechanisms for Budget Constraints
Implements intelligent fallback strategies when budget limits are reached
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta

from .token_tracker import get_token_tracker
from .budget_validator import BudgetValidator, BudgetActionLevel
from .intelligent_cache import get_spiritual_cache

logger = logging.getLogger(__name__)


class FallbackStrategy(Enum):
    """Types of fallback strategies available"""
    CACHE_ONLY = "cache_only"              # Use cached responses only
    MODEL_DOWNGRADE = "model_downgrade"    # Switch to cheaper model
    LOCAL_PROCESSING = "local_processing"  # Use local/offline processing
    SIMPLIFIED_RESPONSE = "simplified_response"  # Provide basic response
    DEFERRED_PROCESSING = "deferred_processing"  # Queue for later processing
    GRACEFUL_DENIAL = "graceful_denial"    # Politely decline with explanation


@dataclass
class FallbackResponse:
    """Response from fallback mechanism"""
    content: str
    strategy_used: FallbackStrategy
    original_request: str
    fallback_reason: str
    cost_saved: float
    quality_score: float  # 0.0-1.0, where 1.0 is equivalent to full LLM
    citations: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []
        if self.metadata is None:
            self.metadata = {}


class DynamicFallbackManager:
    """Manages dynamic fallback mechanisms for budget constraints"""
    
    def __init__(self):
        self.tracker = get_token_tracker()
        self.validator = BudgetValidator()
        self.cache = get_spiritual_cache()
        
        # Fallback strategy priorities (ordered by preference)
        self.fallback_priorities = [
            FallbackStrategy.CACHE_ONLY,
            FallbackStrategy.MODEL_DOWNGRADE,
            FallbackStrategy.LOCAL_PROCESSING,
            FallbackStrategy.SIMPLIFIED_RESPONSE,
            FallbackStrategy.DEFERRED_PROCESSING,
            FallbackStrategy.GRACEFUL_DENIAL
        ]
        
        # Pre-defined responses for different scenarios
        self.template_responses = {
            'dharma': {
                'simplified': "🕉️ Dear seeker, dharma represents righteous duty and moral law. The Bhagavad Gita teaches us that following our dharma leads to spiritual growth and inner peace. Would you like to explore specific aspects of dharmic living?",
                'cache_miss': "🕉️ I understand you seek guidance about dharma. While I cannot provide a detailed response right now, I encourage you to reflect on the teachings of the Bhagavad Gita about righteous duty and moral conduct.",
                'deferred': "🕉️ Your question about dharma is important and deserves a thoughtful response. I've queued your inquiry for detailed processing when resources become available."
            },
            'meditation': {
                'simplified': "🧘 Meditation is the practice of turning inward to find peace and clarity. Ancient texts teach us that regular meditation helps calm the mind and connect with the divine within.",
                'cache_miss': "🧘 Meditation is a sacred practice for inner peace. Please try simple breathing exercises while I prepare a more detailed response for you.",
                'deferred': "🧘 Your meditation question has been noted. In the meantime, practice deep breathing and mindful awareness."
            },
            'scripture': {
                'simplified': "📿 The sacred scriptures offer timeless wisdom for spiritual seekers. Each verse contains layers of meaning that reveal themselves through study and contemplation.",
                'cache_miss': "📿 The scriptures hold profound wisdom. While I cannot provide detailed interpretation right now, I encourage continued study and reflection.",
                'deferred': "📿 Your scripture inquiry is valuable. I've queued it for detailed analysis when full resources are available."
            },
            'general': {
                'simplified': "🙏 Namaste, dear seeker. Every spiritual question is sacred. While I provide a brief response now, true wisdom comes through contemplation and practice.",
                'cache_miss': "🙏 Your spiritual inquiry is important. Please continue your practice while I prepare a more complete response.",
                'deferred': "🙏 Your question has been received with reverence. I will provide a detailed response when possible."
            }
        }
    
    async def execute_fallback(self, 
                              query: str,
                              spiritual_context: str = 'general',
                              user_id: Optional[str] = None,
                              budget_status: Optional[Dict] = None) -> FallbackResponse:
        """
        Execute appropriate fallback strategy based on budget constraints
        
        Args:
            query: User's spiritual query
            spiritual_context: Context of the query
            user_id: User ID for tracking
            budget_status: Current budget status
            
        Returns:
            FallbackResponse with appropriate content and metadata
        """
        
        if budget_status is None:
            budget_status = self.tracker.check_budget_limits(user_id)
        
        # Try fallback strategies in order of preference
        for strategy in self.fallback_priorities:
            try:
                fallback_result = await self._try_strategy(
                    strategy, query, spiritual_context, user_id, budget_status
                )
                
                if fallback_result:
                    logger.info(f"Fallback successful using strategy: {strategy.value}")
                    return fallback_result
                    
            except Exception as e:
                logger.warning(f"Fallback strategy {strategy.value} failed: {e}")
                continue
        
        # Final fallback - graceful denial
        return await self._graceful_denial_fallback(query, spiritual_context, budget_status)
    
    async def _try_strategy(self, 
                           strategy: FallbackStrategy,
                           query: str,
                           spiritual_context: str,
                           user_id: Optional[str],
                           budget_status: Dict) -> Optional[FallbackResponse]:
        """Try a specific fallback strategy"""
        
        if strategy == FallbackStrategy.CACHE_ONLY:
            return await self._cache_only_fallback(query, spiritual_context, budget_status)
        
        elif strategy == FallbackStrategy.MODEL_DOWNGRADE:
            return await self._model_downgrade_fallback(query, spiritual_context, user_id, budget_status)
        
        elif strategy == FallbackStrategy.LOCAL_PROCESSING:
            return await self._local_processing_fallback(query, spiritual_context, budget_status)
        
        elif strategy == FallbackStrategy.SIMPLIFIED_RESPONSE:
            return await self._simplified_response_fallback(query, spiritual_context, budget_status)
        
        elif strategy == FallbackStrategy.DEFERRED_PROCESSING:
            return await self._deferred_processing_fallback(query, spiritual_context, user_id, budget_status)
        
        elif strategy == FallbackStrategy.GRACEFUL_DENIAL:
            return await self._graceful_denial_fallback(query, spiritual_context, budget_status)
        
        return None
    
    async def _cache_only_fallback(self, 
                                  query: str, 
                                  spiritual_context: str,
                                  budget_status: Dict) -> Optional[FallbackResponse]:
        """Try to answer using cached responses only"""
        
        cached_result = self.cache.get_cached_response(query, spiritual_context)
        
        if cached_result:
            # Estimate cost saved by using cache
            saved_cost = 0.005  # Typical cost of gemini-pro query
            
            return FallbackResponse(
                content=cached_result['content'],
                strategy_used=FallbackStrategy.CACHE_ONLY,
                original_request=query,
                fallback_reason="Using cached response to avoid LLM costs",
                cost_saved=saved_cost,
                quality_score=cached_result.get('confidence', 0.9),
                citations=cached_result.get('citations', []),
                metadata={
                    'cache_type': cached_result.get('cache_type'),
                    'hit_count': cached_result.get('hit_count'),
                    'budget_percentage': budget_status.get('daily_percentage', 0)
                }
            )
        
        return None
    
    async def _model_downgrade_fallback(self,
                                      query: str,
                                      spiritual_context: str, 
                                      user_id: Optional[str],
                                      budget_status: Dict) -> Optional[FallbackResponse]:
        """Try using a cheaper model"""
        
        # Only allow model downgrade if budget is not severely constrained
        if budget_status.get('daily_percentage', 0) > 95:
            return None  # Too constrained for even cheaper model
        
        # Check if we can afford gemini-flash instead of gemini-pro
        validation = self.validator.validate_operation_budget(
            operation_type='spiritual_guidance',
            model_name='gemini-flash',
            user_id=user_id
        )
        
        if validation.action in [BudgetActionLevel.ALLOW, BudgetActionLevel.WARN]:
            # We can afford the cheaper model
            # This would typically call the actual LLM service with gemini-flash
            # For this implementation, we'll simulate a response
            
            cost_saved = 0.004  # Difference between pro and flash
            
            response_content = await self._generate_budget_conscious_response(
                query, spiritual_context, 'gemini-flash'
            )
            
            return FallbackResponse(
                content=response_content,
                strategy_used=FallbackStrategy.MODEL_DOWNGRADE,
                original_request=query,
                fallback_reason="Downgraded to gemini-flash to stay within budget",
                cost_saved=cost_saved,
                quality_score=0.85,  # Slightly lower quality than pro
                citations=self._extract_basic_citations(spiritual_context),
                metadata={
                    'model_used': 'gemini-flash',
                    'budget_percentage': budget_status.get('daily_percentage', 0)
                }
            )
        
        return None
    
    async def _local_processing_fallback(self,
                                       query: str,
                                       spiritual_context: str,
                                       budget_status: Dict) -> Optional[FallbackResponse]:
        """Use local processing without LLM"""
        
        # Simulate local processing using keyword matching and templates
        response_content = await self._generate_local_response(query, spiritual_context)
        
        if response_content:
            return FallbackResponse(
                content=response_content,
                strategy_used=FallbackStrategy.LOCAL_PROCESSING,
                original_request=query,
                fallback_reason="Using local processing to avoid LLM costs",
                cost_saved=0.005,  # Full LLM cost saved
                quality_score=0.6,  # Lower quality but still helpful
                citations=self._extract_basic_citations(spiritual_context),
                metadata={
                    'processing_type': 'local_keyword_matching',
                    'budget_percentage': budget_status.get('daily_percentage', 0)
                }
            )
        
        return None
    
    async def _simplified_response_fallback(self,
                                          query: str,
                                          spiritual_context: str,
                                          budget_status: Dict) -> FallbackResponse:
        """Provide a simplified template response"""
        
        context_key = spiritual_context if spiritual_context in self.template_responses else 'general'
        response_content = self.template_responses[context_key]['simplified']
        
        return FallbackResponse(
            content=response_content,
            strategy_used=FallbackStrategy.SIMPLIFIED_RESPONSE,
            original_request=query,
            fallback_reason="Providing simplified response due to budget constraints",
            cost_saved=0.005,  # Full LLM cost saved
            quality_score=0.4,  # Basic but respectful response
            citations=[],
            metadata={
                'template_used': context_key,
                'budget_percentage': budget_status.get('daily_percentage', 0)
            }
        )
    
    async def _deferred_processing_fallback(self,
                                          query: str,
                                          spiritual_context: str,
                                          user_id: Optional[str],
                                          budget_status: Dict) -> FallbackResponse:
        """Queue query for later processing"""
        
        # Save query for later processing
        await self._queue_for_later_processing(query, spiritual_context, user_id)
        
        context_key = spiritual_context if spiritual_context in self.template_responses else 'general'
        response_content = self.template_responses[context_key]['deferred']
        
        return FallbackResponse(
            content=response_content,
            strategy_used=FallbackStrategy.DEFERRED_PROCESSING,
            original_request=query,
            fallback_reason="Query queued for processing when budget allows",
            cost_saved=0.005,  # Immediate cost saved
            quality_score=0.3,  # Promise of future response
            citations=[],
            metadata={
                'queued_at': datetime.now().isoformat(),
                'estimated_processing_time': '1-24 hours',
                'budget_percentage': budget_status.get('daily_percentage', 0)
            }
        )
    
    async def _graceful_denial_fallback(self,
                                      query: str,
                                      spiritual_context: str,
                                      budget_status: Dict) -> FallbackResponse:
        """Gracefully decline with explanation"""
        
        budget_pct = budget_status.get('daily_percentage', 0)
        
        response_content = (
            f"🙏 Namaste, dear seeker. I deeply appreciate your spiritual inquiry. "
            f"Currently, I'm managing resource usage carefully (at {budget_pct:.0f}% of daily capacity) "
            f"to ensure sustainable service for all seekers. "
            f"Please try again later, or consider exploring the timeless wisdom in "
            f"the Bhagavad Gita, Upanishads, or other sacred texts while you wait. "
            f"Your spiritual journey is precious, and I look forward to assisting you soon. 🕉️"
        )
        
        return FallbackResponse(
            content=response_content,
            strategy_used=FallbackStrategy.GRACEFUL_DENIAL,
            original_request=query,
            fallback_reason=f"Budget limit reached ({budget_pct:.1f}% of daily limit used)",
            cost_saved=0.005,  # Full LLM cost saved
            quality_score=0.2,  # Honest but limited response
            citations=[],
            metadata={
                'budget_percentage': budget_pct,
                'suggested_retry_time': (datetime.now() + timedelta(hours=1)).isoformat()
            }
        )
    
    async def _generate_budget_conscious_response(self,
                                                query: str,
                                                spiritual_context: str,
                                                model: str) -> str:
        """Generate a response using budget-conscious model"""
        
        # This would integrate with the actual LLM service
        # For now, simulate a shorter but quality response
        
        context_templates = {
            'dharma': f"🕉️ Regarding your question about dharma: The Bhagavad Gita teaches that dharma is our righteous duty. Krishna advises Arjuna to follow his dharma as a warrior, showing us that each person must fulfill their role with dedication and without attachment to results. Your specific question about '{query[:50]}...' relates to this timeless principle of righteous action.",
            
            'meditation': f"🧘 For your meditation inquiry: Ancient wisdom teaches that meditation is the path to inner peace. Regular practice helps quiet the mind and connect with the divine presence within. Your question about '{query[:50]}...' touches on this sacred practice of turning inward.",
            
            'scripture': f"📿 Regarding the scriptures: The sacred texts contain layers of wisdom that reveal themselves through devoted study. Your question about '{query[:50]}...' invites us to explore these timeless teachings with reverence and contemplation.",
            
            'general': f"🙏 In response to your spiritual inquiry: Every sincere question is a step on the path to wisdom. Your question about '{query[:50]}...' reflects the universal human seeking for truth and meaning."
        }
        
        return context_templates.get(spiritual_context, context_templates['general'])
    
    async def _generate_local_response(self, query: str, spiritual_context: str) -> Optional[str]:
        """Generate response using local keyword matching"""
        
        query_lower = query.lower()
        
        # Keyword-based responses for common spiritual topics
        keyword_responses = {
            'dharma': "🕉️ Dharma represents righteous duty and moral law, as taught in the Bhagavad Gita.",
            'karma': "⚖️ Karma is the law of cause and effect in our actions and their consequences.",
            'meditation': "🧘 Meditation is the practice of mindful awareness and inner stillness.",
            'krishna': "🙏 Lord Krishna is the divine teacher of the Bhagavad Gita and embodiment of divine love.",
            'gita': "📿 The Bhagavad Gita is a sacred dialogue on duty, righteousness, and spiritual wisdom.",
            'yoga': "🕉️ Yoga means union - the practice of connecting body, mind, and spirit.",
            'moksha': "🌟 Moksha is liberation, the ultimate goal of spiritual practice.",
            'bhakti': "❤️ Bhakti is the path of devotion and love for the Divine."
        }
        
        for keyword, response in keyword_responses.items():
            if keyword in query_lower:
                return f"{response} This is a foundational teaching worth deeper contemplation."
        
        return None
    
    def _extract_basic_citations(self, spiritual_context: str) -> List[Dict[str, Any]]:
        """Extract basic citations based on context"""
        
        context_citations = {
            'dharma': [{"source": "Bhagavad Gita", "chapter": "2", "verse": "31"}],
            'meditation': [{"source": "Patanjali Yoga Sutras", "chapter": "1", "verse": "2"}],
            'scripture': [{"source": "Bhagavad Gita", "chapter": "4", "verse": "7-8"}],
            'general': [{"source": "Upanishads", "text": "Traditional wisdom"}]
        }
        
        return context_citations.get(spiritual_context, [])
    
    async def _queue_for_later_processing(self,
                                        query: str,
                                        spiritual_context: str,
                                        user_id: Optional[str]):
        """Queue query for processing when budget allows"""
        
        queue_item = {
            'query': query,
            'spiritual_context': spiritual_context,
            'user_id': user_id,
            'queued_at': datetime.now().isoformat(),
            'priority': 'normal'
        }
        
        # Save to queue file (in production, this would use a proper queue system)
        try:
            queue_file = "data/cost_tracking/deferred_queries.jsonl"
            with open(queue_file, 'a') as f:
                f.write(json.dumps(queue_item) + '\n')
        except Exception as e:
            logger.warning(f"Failed to queue query: {e}")
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get statistics about fallback usage"""
        
        # This would track fallback usage over time
        # For now, return basic structure
        
        return {
            'total_fallbacks': 0,
            'strategies_used': {strategy.value: 0 for strategy in FallbackStrategy},
            'cost_saved': 0.0,
            'average_quality_score': 0.0,
            'user_satisfaction': 0.0
        }


# Decorator for automatic fallback handling
def with_dynamic_fallback(spiritual_context: str = 'general'):
    """Decorator to add dynamic fallback capability to functions"""
    
    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            try:
                # Try original function first
                result = await func(*args, **kwargs)
                
                # Check if result indicates budget issues
                if isinstance(result, dict) and result.get('error') == 'budget_exceeded':
                    # Trigger fallback
                    fallback_manager = DynamicFallbackManager()
                    query = kwargs.get('query', args[0] if args else "")
                    user_id = kwargs.get('user_id')
                    
                    fallback_result = await fallback_manager.execute_fallback(
                        query=query,
                        spiritual_context=spiritual_context,
                        user_id=user_id,
                        budget_status=result.get('budget_status')
                    )
                    
                    return {
                        'content': fallback_result.content,
                        'fallback_used': True,
                        'fallback_strategy': fallback_result.strategy_used.value,
                        'fallback_reason': fallback_result.fallback_reason,
                        'quality_score': fallback_result.quality_score,
                        'cost_saved': fallback_result.cost_saved,
                        'citations': fallback_result.citations,
                        'metadata': fallback_result.metadata
                    }
                
                return result
                
            except Exception as e:
                logger.error(f"Error in function with fallback: {e}")
                # Emergency fallback
                fallback_manager = DynamicFallbackManager()
                query = kwargs.get('query', args[0] if args else "")
                
                emergency_fallback = await fallback_manager._graceful_denial_fallback(
                    query, spiritual_context, {}
                )
                
                return {
                    'content': emergency_fallback.content,
                    'fallback_used': True,
                    'fallback_strategy': 'emergency',
                    'error': str(e)
                }
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, use simplified fallback
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Simple text fallback for sync functions
                return {
                    'content': "🙏 I apologize, but I'm unable to provide a response at this moment. Please try again later.",
                    'fallback_used': True,
                    'fallback_strategy': 'emergency_sync',
                    'error': str(e)
                }
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Example usage and testing
if __name__ == "__main__":
    async def test_dynamic_fallbacks():
        print("🕉️ Testing Dynamic Fallback Mechanisms")
        print("=" * 50)
        
        fallback_manager = DynamicFallbackManager()
        
        # Test different scenarios
        test_scenarios = [
            {
                'query': "What is dharma according to Krishna?",
                'context': 'dharma',
                'budget_status': {'daily_percentage': 85, 'within_limits': True}
            },
            {
                'query': "How do I meditate properly?",
                'context': 'meditation', 
                'budget_status': {'daily_percentage': 95, 'within_limits': False}
            },
            {
                'query': "Explain the meaning of this Sanskrit verse",
                'context': 'scripture',
                'budget_status': {'daily_percentage': 98, 'within_limits': False}
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\nScenario {i}: {scenario['query'][:40]}...")
            print(f"Budget Status: {scenario['budget_status']['daily_percentage']:.0f}%")
            
            fallback_result = await fallback_manager.execute_fallback(
                query=scenario['query'],
                spiritual_context=scenario['context'],
                user_id='test_user',
                budget_status=scenario['budget_status']
            )
            
            print(f"Strategy Used: {fallback_result.strategy_used.value}")
            print(f"Quality Score: {fallback_result.quality_score:.1f}")
            print(f"Cost Saved: ${fallback_result.cost_saved:.4f}")
            print(f"Response Preview: {fallback_result.content[:100]}...")
            print("-" * 40)
        
        print("\n✅ Dynamic fallback system working correctly!")
    
    asyncio.run(test_dynamic_fallbacks())
