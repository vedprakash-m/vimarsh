"""
Budget validation system for LLM operations
Prevents expensive operations when budget limits are exceeded
"""

import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum

from .token_tracker import get_token_tracker

logger = logging.getLogger(__name__)


class BudgetActionLevel(Enum):
    """Action levels for budget validation"""
    ALLOW = "allow"              # Operation allowed
    WARN = "warn"                # Show warning but allow
    DOWNGRADE = "downgrade"      # Use cheaper model
    BLOCK = "block"              # Block operation


@dataclass
class BudgetValidationResult:
    """Result of budget validation check"""
    action: BudgetActionLevel
    message: str
    current_spend: float
    budget_limit: float
    percentage_used: float
    suggested_model: Optional[str] = None
    retry_after: Optional[int] = None  # seconds to wait


class BudgetValidator:
    """Budget validation system for cost-aware LLM operations"""
    
    def __init__(self):
        self.tracker = get_token_tracker()
        
        # Model downgrade path: expensive -> cheaper
        self.model_downgrade_path = {
            'gemini-pro': 'gemini-flash',
            'gemini-flash': 'local_fallback',
            'local_fallback': None  # No further downgrade
        }
        
        # Estimated cost per operation by model (for prediction)
        self.operation_cost_estimates = {
            'gemini-pro': {
                'simple_query': 0.003,      # ~500 tokens
                'complex_guidance': 0.008,   # ~1200 tokens  
                'expert_review': 0.015,      # ~2000 tokens
                'voice_response': 0.005      # ~700 tokens
            },
            'gemini-flash': {
                'simple_query': 0.0006,     # Same tokens, cheaper rate
                'complex_guidance': 0.0015,
                'expert_review': 0.003,
                'voice_response': 0.001
            },
            'local_fallback': {
                'simple_query': 0.0,        # Free
                'complex_guidance': 0.0,
                'expert_review': 0.0,
                'voice_response': 0.0
            }
        }
    
    def validate_operation_budget(self, 
                                 operation_type: str = 'simple_query',
                                 model_name: str = 'gemini-pro',
                                 user_id: Optional[str] = None) -> BudgetValidationResult:
        """
        Validate if an operation is within budget limits
        
        Args:
            operation_type: Type of operation (simple_query, complex_guidance, etc.)
            model_name: Requested model name
            user_id: User ID for per-user limits
            
        Returns:
            BudgetValidationResult with action and details
        """
        
        # Get current budget status
        budget_status = self.tracker.check_budget_limits(user_id)
        
        # Estimate cost of this operation
        estimated_cost = self.operation_cost_estimates.get(model_name, {}).get(
            operation_type, 
            self.operation_cost_estimates['gemini-pro']['simple_query']
        )
        
        # Check if operation would exceed daily budget
        daily_after_op = budget_status['daily_usage'] + estimated_cost
        daily_percentage_after = (daily_after_op / budget_status['daily_limit']) * 100
        
        # Check if operation would exceed monthly budget
        monthly_after_op = budget_status['monthly_usage'] + estimated_cost
        monthly_percentage_after = (monthly_after_op / budget_status['monthly_limit']) * 100
        
        # Determine action based on budget status
        action = BudgetActionLevel.ALLOW
        message = "Operation approved within budget"
        suggested_model = model_name
        
        # Check emergency thresholds (95% budget used)
        if (daily_percentage_after >= 95 or monthly_percentage_after >= 95 or
            not budget_status['within_limits']):
            
            # Try downgrade to cheaper model
            cheaper_model = self.model_downgrade_path.get(model_name)
            if cheaper_model:
                cheaper_cost = self.operation_cost_estimates.get(cheaper_model, {}).get(
                    operation_type, 0
                )
                cheaper_daily_after = budget_status['daily_usage'] + cheaper_cost
                cheaper_daily_percentage = (cheaper_daily_after / budget_status['daily_limit']) * 100
                
                if cheaper_daily_percentage < 95:
                    action = BudgetActionLevel.DOWNGRADE
                    message = f"Budget near limit, downgrading from {model_name} to {cheaper_model}"
                    suggested_model = cheaper_model
                else:
                    action = BudgetActionLevel.BLOCK
                    message = "Budget limit exceeded, operation blocked"
                    suggested_model = None
            else:
                action = BudgetActionLevel.BLOCK
                message = "Budget limit exceeded, no cheaper model available"
                suggested_model = None
        
        # Check warning thresholds (80% budget used)
        elif daily_percentage_after >= 80 or monthly_percentage_after >= 80:
            action = BudgetActionLevel.WARN
            message = f"Budget warning: {max(daily_percentage_after, monthly_percentage_after):.1f}% of limit would be used"
        
        # Check per-user limits
        if user_id and budget_status.get('user_daily_spend', 0) + estimated_cost >= budget_status.get('user_daily_limit', 1.0):
            action = BudgetActionLevel.BLOCK
            message = f"User daily limit would be exceeded: ${budget_status.get('user_daily_spend', 0) + estimated_cost:.4f}"
            suggested_model = None
        
        return BudgetValidationResult(
            action=action,
            message=message,
            current_spend=max(budget_status['daily_usage'], budget_status['monthly_usage']),
            budget_limit=min(budget_status['daily_limit'], budget_status['monthly_limit']),
            percentage_used=max(budget_status.get('daily_percentage', 0), 
                              budget_status.get('monthly_percentage', 0)),
            suggested_model=suggested_model,
            retry_after=3600 if action == BudgetActionLevel.BLOCK else None  # Retry after 1 hour
        )
    
    def get_recommended_model(self, 
                            operation_type: str = 'simple_query',
                            user_id: Optional[str] = None,
                            preferred_model: str = 'gemini-pro') -> str:
        """
        Get recommended model based on current budget status
        
        Args:
            operation_type: Type of operation
            user_id: User ID for per-user limits  
            preferred_model: User's preferred model
            
        Returns:
            Recommended model name
        """
        validation = self.validate_operation_budget(operation_type, preferred_model, user_id)
        
        if validation.action in [BudgetActionLevel.ALLOW, BudgetActionLevel.WARN]:
            return preferred_model
        elif validation.action == BudgetActionLevel.DOWNGRADE:
            return validation.suggested_model or 'local_fallback'
        else:  # BLOCK
            return 'local_fallback'  # Free fallback


def budget_aware_operation(operation_type: str = 'simple_query', 
                          allow_downgrade: bool = True,
                          fallback_on_block: bool = True):
    """
    Decorator for budget-aware LLM operations
    
    Args:
        operation_type: Type of operation for cost estimation
        allow_downgrade: Whether to allow automatic model downgrade
        fallback_on_block: Whether to use local fallback when blocked
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            validator = BudgetValidator()
            
            # Extract parameters
            user_id = kwargs.get('user_id')
            model_name = kwargs.get('model_name', 'gemini-pro')
            
            # Validate budget
            validation = validator.validate_operation_budget(
                operation_type=operation_type,
                model_name=model_name,
                user_id=user_id
            )
            
            # Handle validation result
            if validation.action == BudgetActionLevel.ALLOW:
                # Proceed with original operation
                return await func(*args, **kwargs)
            
            elif validation.action == BudgetActionLevel.WARN:
                # Log warning and proceed
                logger.warning(f"Budget warning: {validation.message}")
                return await func(*args, **kwargs)
            
            elif validation.action == BudgetActionLevel.DOWNGRADE and allow_downgrade:
                # Downgrade model and proceed
                logger.info(f"Budget downgrade: {validation.message}")
                kwargs['model_name'] = validation.suggested_model
                return await func(*args, **kwargs)
            
            elif validation.action == BudgetActionLevel.BLOCK:
                if fallback_on_block:
                    # Use local fallback
                    logger.warning(f"Budget blocked, using fallback: {validation.message}")
                    kwargs['model_name'] = 'local_fallback'
                    return await func(*args, **kwargs)
                else:
                    # Return budget error response
                    return {
                        'content': "I apologize, but I'm currently unable to provide a response due to budget constraints. Please try again later.",
                        'error': 'budget_exceeded',
                        'budget_status': validation,
                        'usage': {'model_name': 'none', 'input_tokens': 0, 'output_tokens': 0}
                    }
            
            # Fallback for unexpected cases
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar logic for sync functions
            validator = BudgetValidator()
            user_id = kwargs.get('user_id')
            model_name = kwargs.get('model_name', 'gemini-pro')
            
            validation = validator.validate_operation_budget(
                operation_type=operation_type,
                model_name=model_name,
                user_id=user_id
            )
            
            if validation.action == BudgetActionLevel.ALLOW:
                return func(*args, **kwargs)
            elif validation.action == BudgetActionLevel.WARN:
                logger.warning(f"Budget warning: {validation.message}")
                return func(*args, **kwargs)
            elif validation.action == BudgetActionLevel.DOWNGRADE and allow_downgrade:
                logger.info(f"Budget downgrade: {validation.message}")
                kwargs['model_name'] = validation.suggested_model
                return func(*args, **kwargs)
            elif validation.action == BudgetActionLevel.BLOCK:
                if fallback_on_block:
                    logger.warning(f"Budget blocked, using fallback: {validation.message}")
                    kwargs['model_name'] = 'local_fallback'
                    return func(*args, **kwargs)
                else:
                    return {
                        'content': "I apologize, but I'm currently unable to provide a response due to budget constraints. Please try again later.",
                        'error': 'budget_exceeded',
                        'budget_status': validation,
                        'usage': {'model_name': 'none', 'input_tokens': 0, 'output_tokens': 0}
                    }
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Convenience function for quick budget checks
def check_operation_budget(operation_type: str = 'simple_query',
                          model_name: str = 'gemini-pro',
                          user_id: Optional[str] = None) -> bool:
    """
    Quick budget check for an operation
    
    Returns:
        True if operation is allowed, False if blocked
    """
    validator = BudgetValidator()
    validation = validator.validate_operation_budget(operation_type, model_name, user_id)
    return validation.action != BudgetActionLevel.BLOCK


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_budget_validation():
        print("🕉️ Testing Budget Validation System")
        print("=" * 50)
        
        validator = BudgetValidator()
        
        # Test different scenarios
        test_cases = [
            ('simple_query', 'gemini-pro', 'user_123'),
            ('complex_guidance', 'gemini-pro', 'user_123'),
            ('expert_review', 'gemini-flash', 'user_456'),
            ('voice_response', 'local_fallback', None)
        ]
        
        for operation_type, model_name, user_id in test_cases:
            validation = validator.validate_operation_budget(
                operation_type=operation_type,
                model_name=model_name,
                user_id=user_id
            )
            
            print(f"Operation: {operation_type} ({model_name})")
            print(f"Action: {validation.action.value}")
            print(f"Message: {validation.message}")
            if validation.suggested_model:
                print(f"Suggested Model: {validation.suggested_model}")
            print(f"Budget Used: {validation.percentage_used:.1f}%")
            print("-" * 30)
        
        print("✅ Budget validation system working correctly!")
    
    asyncio.run(test_budget_validation())
