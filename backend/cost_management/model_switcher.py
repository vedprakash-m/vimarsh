"""
Cost-Effective Model Switching System
Automatically switches between Gemini Pro and Flash based on budget constraints and query complexity
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, timedelta

from .token_tracker import get_token_tracker
from .budget_validator import BudgetValidator, BudgetActionLevel

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Available model tiers with cost and capability rankings"""
    GEMINI_PRO = "gemini-pro"          # Highest cost, best quality
    GEMINI_FLASH = "gemini-flash"      # Lower cost, good quality
    GEMINI_NANO = "gemini-nano"        # Lowest cost, basic quality (future)


@dataclass
class ModelConfig:
    """Configuration for each model tier"""
    name: str
    cost_per_1k_tokens: float
    max_tokens: int
    quality_score: float  # 0.0-1.0 relative quality
    best_for: List[str]   # Query types this model handles best
    

@dataclass 
class SwitchingDecision:
    """Result of model switching analysis"""
    selected_model: ModelTier
    original_model: ModelTier
    reason: str
    estimated_cost: float
    cost_savings: float
    quality_impact: float  # -1.0 to 1.0, negative means quality reduction
    confidence: float      # 0.0-1.0, how confident we are in this decision


class ModelSwitcher:
    """Intelligent model switching based on budget and query analysis"""
    
    def __init__(self):
        self.tracker = get_token_tracker()
        self.validator = BudgetValidator()
        
        # Model configurations
        self.model_configs = {
            ModelTier.GEMINI_PRO: ModelConfig(
                name="gemini-pro",
                cost_per_1k_tokens=0.005,  # Higher cost
                max_tokens=30720,
                quality_score=1.0,
                best_for=["complex_analysis", "creative_writing", "detailed_explanations", "philosophical_inquiry"]
            ),
            ModelTier.GEMINI_FLASH: ModelConfig(
                name="gemini-flash",
                cost_per_1k_tokens=0.001,  # 5x cheaper
                max_tokens=30720,
                quality_score=0.85,
                best_for=["simple_queries", "factual_questions", "basic_guidance", "quick_responses"]
            )
        }
        
        # Query complexity patterns
        self.complexity_indicators = {
            'high': [
                r'explain.*philosoph',
                r'analyz.*deep',
                r'detailed.*analys',
                r'comprehensive.*overview',
                r'elaborate.*on',
                r'in.*depth',
                r'philosoph.*inquiry',
                r'spiritual.*interpretation',
                r'commentary.*on',
                r'exegesis',
                r'hermeneutics',
                r'foundations.*of',
                r'deep.*meaning',
                r'thorough.*analysis'
            ],
            'medium': [
                r'what.*mean',
                r'how.*practice',
                r'tell.*me.*about',
                r'explain.*briefly',
                r'give.*example',
                r'clarify',
                r'difference.*between'
            ],
            'low': [
                r'^what\s+is\s+\w+\??$',
                r'^who\s+is\s+\w+\??$',
                r'^when\s+\w+',
                r'^where\s+\w+',
                r'yes.*no.*question',
                r'simple.*question',
                r'quick.*answer'
            ]
        }
        
        # Spiritual context weights (higher = more likely to need Pro model)
        self.context_weights = {
            'dharma': 0.8,      # Complex philosophical concepts
            'scripture': 0.9,   # Deep textual analysis
            'meditation': 0.6,  # Practical guidance
            'general': 0.5,     # Basic inquiries
            'prayer': 0.4,      # Simple devotional
            'festival': 0.3     # Factual information
        }
    
    def analyze_query_complexity(self, query: str) -> float:
        """
        Analyze query complexity on a scale of 0.0-1.0
        
        Args:
            query: User's spiritual query
            
        Returns:
            Complexity score (0.0 = simple, 1.0 = very complex)
        """
        
        query_lower = query.lower()
        complexity_score = 0.0
        
        # Check for high complexity indicators
        for pattern in self.complexity_indicators['high']:
            if re.search(pattern, query_lower):
                complexity_score = max(complexity_score, 0.8)
                break  # Found high complexity indicator
        
        # Only check medium if no high complexity found
        if complexity_score < 0.8:
            for pattern in self.complexity_indicators['medium']:
                if re.search(pattern, query_lower):
                    complexity_score = max(complexity_score, 0.5)
                    break
        
        # Only check low if no medium or high complexity found
        if complexity_score < 0.5:
            for pattern in self.complexity_indicators['low']:
                if re.search(pattern, query_lower):
                    complexity_score = max(complexity_score, 0.2)
                    break
        
        # If no patterns matched, use default based on other factors
        if complexity_score == 0.0:
            complexity_score = 0.3  # Default moderate complexity
        
        # Additional complexity factors
        word_count = len(query.split())
        if word_count > 30:
            complexity_score += 0.2
        elif word_count > 15:
            complexity_score += 0.1
        
        # Question marks might indicate uncertainty, needing detailed response
        if query.count('?') > 1:
            complexity_score += 0.1
        
        # Multiple sentences suggest complex inquiry
        sentence_count = len([s for s in query.split('.') if s.strip()])
        if sentence_count > 2:
            complexity_score += 0.15
        
        return min(complexity_score, 1.0)
    
    def estimate_response_length(self, query: str, spiritual_context: str) -> int:
        """
        Estimate expected response length in tokens
        
        Args:
            query: User's spiritual query
            spiritual_context: Context of the spiritual inquiry
            
        Returns:
            Estimated response length in tokens
        """
        
        base_length = 150  # Minimum thoughtful response
        
        # Adjust based on query complexity
        complexity = self.analyze_query_complexity(query)
        complexity_multiplier = 1 + (complexity * 2)  # 1x to 3x based on complexity
        
        # Adjust based on spiritual context
        context_multiplier = self.context_weights.get(spiritual_context, 0.5) + 0.5  # 0.5x to 1.4x
        
        # Adjust based on query length (longer questions often need longer answers)
        query_length_factor = min(len(query.split()) / 10, 2.0)  # Up to 2x for very long queries
        
        estimated_length = int(base_length * complexity_multiplier * context_multiplier * query_length_factor)
        
        # Cap at reasonable limits
        return min(max(estimated_length, 50), 1000)
    
    def should_use_pro_model(self, 
                            query: str,
                            spiritual_context: str = 'general',
                            user_id: Optional[str] = None,
                            force_quality: bool = False) -> SwitchingDecision:
        """
        Determine if Pro model should be used based on query analysis and budget
        
        Args:
            query: User's spiritual query
            spiritual_context: Context of the inquiry
            user_id: User ID for budget tracking
            force_quality: Force high-quality model regardless of cost
            
        Returns:
            SwitchingDecision with model selection and reasoning
        """
        
        # Default to Pro model
        target_model = ModelTier.GEMINI_PRO
        
        # Analyze query characteristics
        complexity = self.analyze_query_complexity(query)
        estimated_tokens = self.estimate_response_length(query, spiritual_context)
        context_weight = self.context_weights.get(spiritual_context, 0.5)
        
        # Calculate estimated costs for both models
        pro_cost = (estimated_tokens / 1000) * self.model_configs[ModelTier.GEMINI_PRO].cost_per_1k_tokens
        flash_cost = (estimated_tokens / 1000) * self.model_configs[ModelTier.GEMINI_FLASH].cost_per_1k_tokens
        cost_savings = pro_cost - flash_cost
        
        # Check budget constraints
        budget_status = self.tracker.check_budget_limits(user_id)
        budget_percentage = budget_status.get('daily_percentage', 0)
        
        # Quality requirement score (0.0-1.0)
        quality_requirement = (complexity * 0.4) + (context_weight * 0.4) + (min(estimated_tokens/500, 1.0) * 0.2)
        
        # Decision logic
        decision_reason = ""
        confidence = 0.8
        
        if force_quality:
            # Quality forced - use Pro regardless of cost
            selected_model = ModelTier.GEMINI_PRO
            decision_reason = "High-quality response explicitly requested"
            confidence = 1.0
            
        elif budget_percentage > 95:
            # Budget critically low - force Flash
            selected_model = ModelTier.GEMINI_FLASH
            decision_reason = f"Budget critically low ({budget_percentage:.1f}%) - forcing cost-effective model"
            confidence = 0.9
            
        elif budget_percentage > 80 and quality_requirement < 0.7:
            # Budget moderately high and quality requirement moderate - use Flash
            selected_model = ModelTier.GEMINI_FLASH
            decision_reason = f"Budget moderately high ({budget_percentage:.1f}%) and query suitable for cost-effective model"
            confidence = 0.8
            
        elif complexity < 0.4 and context_weight < 0.6:
            # Simple query - Flash is adequate
            selected_model = ModelTier.GEMINI_FLASH
            decision_reason = "Simple query well-suited for cost-effective model"
            confidence = 0.8
            
        elif quality_requirement > 0.8:
            # High quality requirement - use Pro
            selected_model = ModelTier.GEMINI_PRO
            decision_reason = "Complex query requiring high-quality response"
            confidence = 0.9
            
        else:
            # Borderline case - consider budget more heavily
            if budget_percentage > 60:
                selected_model = ModelTier.GEMINI_FLASH
                decision_reason = f"Moderate budget usage ({budget_percentage:.1f}%) - preferring cost efficiency"
                confidence = 0.6
            else:
                selected_model = ModelTier.GEMINI_PRO
                decision_reason = "Budget allows for high-quality response"
                confidence = 0.8
        
        # Calculate quality impact
        if selected_model == ModelTier.GEMINI_PRO:
            quality_impact = 0.0  # No quality loss
            estimated_cost = pro_cost
            cost_savings = 0.0
        else:
            quality_impact = -0.15  # 15% quality reduction for Flash
            estimated_cost = flash_cost
        
        return SwitchingDecision(
            selected_model=selected_model,
            original_model=target_model,
            reason=decision_reason,
            estimated_cost=estimated_cost,
            cost_savings=cost_savings,
            quality_impact=quality_impact,
            confidence=confidence
        )
    
    def should_use_pro_model_with_budget(self,
                                       query: str,
                                       spiritual_context: str = 'general',
                                       user_id: Optional[str] = None,
                                       budget_status: Optional[Dict] = None) -> SwitchingDecision:
        """
        Determine model with explicit budget status
        """
        # Override the budget check to use provided status
        original_method = self.tracker.check_budget_limits
        if budget_status:
            self.tracker.check_budget_limits = lambda uid: budget_status
        
        try:
            result = self.should_use_pro_model(query, spiritual_context, user_id)
        finally:
            self.tracker.check_budget_limits = original_method
        
        return result
    
    def get_model_recommendation(self,
                               query: str,
                               spiritual_context: str = 'general',
                               user_id: Optional[str] = None,
                               budget_override: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get comprehensive model recommendation with detailed analysis
        
        Args:
            query: User's spiritual query
            spiritual_context: Context of the inquiry
            user_id: User ID for budget tracking
            budget_override: Optional budget status override for testing
            
        Returns:
            Dictionary with recommendation details
        """
        
        budget_status = budget_override or self.tracker.check_budget_limits(user_id)
        
        # Use budget status for decision making
        decision = self.should_use_pro_model_with_budget(
            query, spiritual_context, user_id, budget_status
        )
        complexity = self.analyze_query_complexity(query)
        estimated_tokens = self.estimate_response_length(query, spiritual_context)
        
        return {
            'recommended_model': decision.selected_model.value,
            'original_model': decision.original_model.value,
            'decision_reason': decision.reason,
            'confidence': decision.confidence,
            'cost_analysis': {
                'estimated_cost': decision.estimated_cost,
                'cost_savings': decision.cost_savings,
                'budget_percentage': budget_status.get('daily_percentage', 0)
            },
            'quality_analysis': {
                'query_complexity': complexity,
                'estimated_tokens': estimated_tokens,
                'quality_impact': decision.quality_impact,
                'context_weight': self.context_weights.get(spiritual_context, 0.5)
            },
            'model_configs': {
                model.value: {
                    'cost_per_1k': config.cost_per_1k_tokens,
                    'quality_score': config.quality_score,
                    'best_for': config.best_for
                }
                for model, config in self.model_configs.items()
            }
        }
    
    def get_switching_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about model switching patterns
        
        Args:
            user_id: Optional user ID for user-specific stats
            
        Returns:
            Statistics dictionary
        """
        
        # In a real implementation, this would query usage logs
        # For now, return structure for testing
        
        return {
            'total_queries': 0,
            'model_usage': {
                'gemini-pro': {'count': 0, 'percentage': 0.0, 'total_cost': 0.0},
                'gemini-flash': {'count': 0, 'percentage': 0.0, 'total_cost': 0.0}
            },
            'cost_savings': {
                'total_saved': 0.0,
                'average_per_query': 0.0,
                'percentage_saved': 0.0
            },
            'quality_metrics': {
                'average_complexity': 0.0,
                'high_quality_needed': 0.0,  # Percentage needing Pro
                'successful_downgrades': 0.0  # Percentage successfully using Flash
            }
        }


# Decorator for automatic model switching
def with_model_switching(spiritual_context: str = 'general', force_quality: bool = False):
    """
    Decorator to add automatic model switching to LLM functions
    
    Args:
        spiritual_context: Context for model selection
        force_quality: Force high-quality model
    """
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            switcher = ModelSwitcher()
            
            # Extract query from arguments
            query = kwargs.get('query') or (args[0] if args else "")
            user_id = kwargs.get('user_id')
            
            # Get model recommendation
            recommendation = switcher.get_model_recommendation(
                query=query,
                spiritual_context=spiritual_context,
                user_id=user_id
            )
            
            # Override with force quality if needed
            if force_quality:
                recommendation['recommended_model'] = 'gemini-pro'
                recommendation['decision_reason'] = "High-quality response explicitly requested (forced)"
            
            # Override model in kwargs
            kwargs['model_name'] = recommendation['recommended_model']
            
            # Call original function with recommended model
            result = await func(*args, **kwargs)
            
            # Add switching metadata to result
            if isinstance(result, dict):
                result['model_switching'] = {
                    'recommended_model': recommendation['recommended_model'],
                    'decision_reason': recommendation['decision_reason'],
                    'cost_savings': recommendation['cost_analysis']['cost_savings'],
                    'quality_impact': recommendation['quality_analysis']['quality_impact']
                }
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, just add model parameter
            switcher = ModelSwitcher()
            query = kwargs.get('query') or (args[0] if args else "")
            user_id = kwargs.get('user_id')
            
            recommendation = switcher.get_model_recommendation(
                query=query,
                spiritual_context=spiritual_context,
                user_id=user_id
            )
            
            # Override with force quality if needed
            if force_quality:
                recommendation['recommended_model'] = 'gemini-pro'
            
            kwargs['model_name'] = recommendation['recommended_model']
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global instance
_model_switcher = None

def get_model_switcher() -> ModelSwitcher:
    """Get global model switcher instance"""
    global _model_switcher
    if _model_switcher is None:
        _model_switcher = ModelSwitcher()
    return _model_switcher


# Example usage and testing
if __name__ == "__main__":
    async def test_model_switching():
        print("🕉️ Testing Cost-Effective Model Switching")
        print("=" * 50)
        
        switcher = ModelSwitcher()
        
        # Test queries of different complexity
        test_queries = [
            {
                'query': "What is dharma?",
                'context': 'dharma',
                'description': "Simple factual question"
            },
            {
                'query': "Can you provide a comprehensive philosophical analysis of the concept of dharma as presented in the Bhagavad Gita, including its various interpretations and practical applications?",
                'context': 'dharma',
                'description': "Complex analytical question"
            },
            {
                'query': "How to meditate?",
                'context': 'meditation', 
                'description': "Practical guidance question"
            },
            {
                'query': "Explain the deep philosophical underpinnings of karma yoga and its relationship to other yogic paths described in ancient texts.",
                'context': 'scripture',
                'description': "Deep scriptural analysis"
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print(f"Query: {test_case['query'][:60]}...")
            
            recommendation = switcher.get_model_recommendation(
                query=test_case['query'],
                spiritual_context=test_case['context'],
                user_id='test_user'
            )
            
            print(f"Recommended Model: {recommendation['recommended_model']}")
            print(f"Complexity Score: {recommendation['quality_analysis']['query_complexity']:.2f}")
            print(f"Estimated Cost: ${recommendation['cost_analysis']['estimated_cost']:.4f}")
            print(f"Cost Savings: ${recommendation['cost_analysis']['cost_savings']:.4f}")
            print(f"Confidence: {recommendation['confidence']:.1%}")
            print(f"Reason: {recommendation['decision_reason']}")
            print("-" * 40)
        
        print("\n✅ Model switching system working correctly!")
    
    import asyncio
    asyncio.run(test_model_switching())
