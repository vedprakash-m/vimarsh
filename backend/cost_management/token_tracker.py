"""
AI Cost Management System for Vimarsh
Real-time token usage tracking and cost optimization for LLM operations
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from functools import wraps
import logging
from collections import defaultdict
import threading
from pathlib import Path

# Import user limits for integration
from .user_limits import UserLimitManager, LimitType, EnforcementAction

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage tracking for LLM operations"""
    timestamp: datetime
    operation_type: str  # 'spiritual_guidance', 'expert_review', 'voice_response'
    model_name: str  # 'gemini-pro', 'gemini-flash', 'local_fallback'
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    spiritual_context: Optional[str] = None  # 'dharma', 'meditation', 'scripture'


@dataclass
class CostBudget:
    """Cost budget configuration and tracking"""
    daily_limit: float = 10.0  # $10 daily limit for beta
    monthly_limit: float = 200.0  # $200 monthly limit for beta
    per_user_daily_limit: float = 1.0  # $1 per user daily
    current_daily_spend: float = 0.0
    current_monthly_spend: float = 0.0
    alert_threshold: float = 0.8  # Alert at 80% of budget
    emergency_threshold: float = 0.95  # Emergency stop at 95%


class TokenUsageTracker:
    """Real-time token usage tracking and cost management"""
    
    def __init__(self, storage_path: str = "data/cost_tracking"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory tracking for real-time operations
        self.usage_history: List[TokenUsage] = []
        self.user_usage: Dict[str, List[TokenUsage]] = defaultdict(list)
        self.session_usage: Dict[str, List[TokenUsage]] = defaultdict(list)
        
        # Budget tracking
        self.budget = CostBudget()
        
        # User limits integration
        self.user_limit_manager = UserLimitManager(str(self.storage_path / "user_limits"))
        
        # Model pricing (per 1K tokens) - updated rates as of 2025
        self.model_pricing = {
            'gemini-pro': {
                'input': 0.0005,   # $0.0005 per 1K input tokens
                'output': 0.0015   # $0.0015 per 1K output tokens  
            },
            'gemini-flash': {
                'input': 0.000075,  # $0.000075 per 1K input tokens (cheaper)
                'output': 0.0003    # $0.0003 per 1K output tokens (cheaper)
            },
            'local_fallback': {
                'input': 0.0,      # Free local processing
                'output': 0.0
            }
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Load existing data
        self._load_usage_data()
        self._load_budget_data()
    
    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage"""
        if model_name not in self.model_pricing:
            logger.warning(f"Unknown model {model_name}, using gemini-pro pricing")
            model_name = 'gemini-pro'
        
        pricing = self.model_pricing[model_name]
        
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def track_usage(self, 
                   operation_type: str,
                   model_name: str,
                   input_tokens: int,
                   output_tokens: int,
                   user_id: Optional[str] = None,
                   session_id: Optional[str] = None,
                   spiritual_context: Optional[str] = None) -> TokenUsage:
        """Track token usage for an LLM operation"""
        
        total_tokens = input_tokens + output_tokens
        estimated_cost = self.calculate_cost(model_name, input_tokens, output_tokens)
        
        usage = TokenUsage(
            timestamp=datetime.now(),
            operation_type=operation_type,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            user_id=user_id,
            session_id=session_id,
            spiritual_context=spiritual_context
        )
        
        with self._lock:
            # Add to tracking collections
            self.usage_history.append(usage)
            
            if user_id:
                self.user_usage[user_id].append(usage)
            
            if session_id:
                self.session_usage[session_id].append(usage)
            
            # Update budget tracking
            self._update_budget_tracking(usage)
        
        # Persist usage data
        self._save_usage_data(usage)
        
        logger.info(f"Tracked {total_tokens} tokens for {operation_type} "
                   f"(${estimated_cost:.6f}) - Model: {model_name}")
        
        return usage
    
    def _update_budget_tracking(self, usage: TokenUsage):
        """Update current spend tracking"""
        now = datetime.now()
        
        # Update daily spend
        today_usage = [u for u in self.usage_history 
                      if u.timestamp.date() == now.date()]
        self.budget.current_daily_spend = sum(u.estimated_cost for u in today_usage)
        
        # Update monthly spend  
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_usage = [u for u in self.usage_history 
                        if u.timestamp >= month_start]
        self.budget.current_monthly_spend = sum(u.estimated_cost for u in monthly_usage)
    
    def check_budget_limits(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if current usage is within budget limits"""
        
        budget_status = {
            'within_limits': True,
            'alerts': [],
            'daily_usage': self.budget.current_daily_spend,
            'daily_limit': self.budget.daily_limit,
            'monthly_usage': self.budget.current_monthly_spend,
            'monthly_limit': self.budget.monthly_limit,
            'daily_percentage': (self.budget.current_daily_spend / self.budget.daily_limit) * 100,
            'monthly_percentage': (self.budget.current_monthly_spend / self.budget.monthly_limit) * 100
        }
        
        # Check daily limits
        if self.budget.current_daily_spend >= self.budget.daily_limit * self.budget.emergency_threshold:
            budget_status['within_limits'] = False
            budget_status['alerts'].append({
                'level': 'emergency',
                'message': f"Daily budget emergency threshold reached: ${self.budget.current_daily_spend:.2f} / ${self.budget.daily_limit:.2f}"
            })
        elif self.budget.current_daily_spend >= self.budget.daily_limit * self.budget.alert_threshold:
            budget_status['alerts'].append({
                'level': 'warning',
                'message': f"Daily budget alert threshold reached: ${self.budget.current_daily_spend:.2f} / ${self.budget.daily_limit:.2f}"
            })
        
        # Check monthly limits
        if self.budget.current_monthly_spend >= self.budget.monthly_limit * self.budget.emergency_threshold:
            budget_status['within_limits'] = False
            budget_status['alerts'].append({
                'level': 'emergency', 
                'message': f"Monthly budget emergency threshold reached: ${self.budget.current_monthly_spend:.2f} / ${self.budget.monthly_limit:.2f}"
            })
        elif self.budget.current_monthly_spend >= self.budget.monthly_limit * self.budget.alert_threshold:
            budget_status['alerts'].append({
                'level': 'warning',
                'message': f"Monthly budget alert threshold reached: ${self.budget.current_monthly_spend:.2f} / ${self.budget.monthly_limit:.2f}"
            })
        
        # Check per-user limits if user_id provided
        if user_id:
            user_daily_spend = self.get_user_daily_spend(user_id)
            budget_status['user_daily_spend'] = user_daily_spend
            budget_status['user_daily_limit'] = self.budget.per_user_daily_limit
            
            if user_daily_spend >= self.budget.per_user_daily_limit:
                budget_status['within_limits'] = False
                budget_status['alerts'].append({
                    'level': 'user_limit',
                    'message': f"User daily limit exceeded: ${user_daily_spend:.2f} / ${self.budget.per_user_daily_limit:.2f}"
                })
        
        return budget_status
    
    def get_user_daily_spend(self, user_id: str) -> float:
        """Get user's spending for today"""
        today = datetime.now().date()
        user_today_usage = [u for u in self.user_usage[user_id] 
                           if u.timestamp.date() == today]
        return sum(u.estimated_cost for u in user_today_usage)
    
    def get_usage_analytics(self, timeframe: str = '24h') -> Dict[str, Any]:
        """Get usage analytics for specified timeframe"""
        now = datetime.now()
        
        if timeframe == '24h':
            start_time = now - timedelta(hours=24)
        elif timeframe == '7d':
            start_time = now - timedelta(days=7)
        elif timeframe == '30d':
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=24)
        
        period_usage = [u for u in self.usage_history if u.timestamp >= start_time]
        
        if not period_usage:
            return {
                'timeframe': timeframe,
                'total_operations': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'operations_by_type': {},
                'usage_by_model': {},
                'spiritual_contexts': {}
            }
        
        # Aggregate analytics
        operations_by_type = defaultdict(int)
        usage_by_model = defaultdict(lambda: {'operations': 0, 'tokens': 0, 'cost': 0.0})
        spiritual_contexts = defaultdict(int)
        
        total_tokens = 0
        total_cost = 0.0
        
        for usage in period_usage:
            operations_by_type[usage.operation_type] += 1
            
            usage_by_model[usage.model_name]['operations'] += 1
            usage_by_model[usage.model_name]['tokens'] += usage.total_tokens
            usage_by_model[usage.model_name]['cost'] += usage.estimated_cost
            
            if usage.spiritual_context:
                spiritual_contexts[usage.spiritual_context] += 1
            
            total_tokens += usage.total_tokens
            total_cost += usage.estimated_cost
        
        return {
            'timeframe': timeframe,
            'total_operations': len(period_usage),
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'operations_by_type': dict(operations_by_type),
            'usage_by_model': dict(usage_by_model),
            'spiritual_contexts': dict(spiritual_contexts),
            'average_tokens_per_operation': total_tokens / len(period_usage) if period_usage else 0,
            'average_cost_per_operation': total_cost / len(period_usage) if period_usage else 0
        }
    
    def _save_usage_data(self, usage: TokenUsage):
        """Save usage data to persistent storage"""
        try:
            date_str = usage.timestamp.strftime('%Y-%m-%d')
            usage_file = self.storage_path / f"usage_{date_str}.jsonl"
            
            with open(usage_file, 'a') as f:
                f.write(json.dumps(asdict(usage), default=str) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")
    
    def _load_usage_data(self):
        """Load recent usage data from storage"""
        try:
            # Load last 7 days of data for analytics
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                usage_file = self.storage_path / f"usage_{date_str}.jsonl"
                
                if usage_file.exists():
                    with open(usage_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                                usage = TokenUsage(**data)
                                self.usage_history.append(usage)
                                
                                if usage.user_id:
                                    self.user_usage[usage.user_id].append(usage)
                                
                                if usage.session_id:
                                    self.session_usage[usage.session_id].append(usage)
            
            logger.info(f"Loaded {len(self.usage_history)} usage records")
            
        except Exception as e:
            logger.error(f"Failed to load usage data: {e}")
    
    def _save_budget_data(self):
        """Save current budget state"""
        try:
            budget_file = self.storage_path / "budget_state.json"
            with open(budget_file, 'w') as f:
                json.dump(asdict(self.budget), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save budget data: {e}")
    
    def _load_budget_data(self):
        """Load budget state from storage"""
        try:
            budget_file = self.storage_path / "budget_state.json"
            if budget_file.exists():
                with open(budget_file, 'r') as f:
                    data = json.load(f)
                    # Only load configuration, recalculate current spend
                    self.budget.daily_limit = data.get('daily_limit', 10.0)
                    self.budget.monthly_limit = data.get('monthly_limit', 200.0)
                    self.budget.per_user_daily_limit = data.get('per_user_daily_limit', 1.0)
                    self.budget.alert_threshold = data.get('alert_threshold', 0.8)
                    self.budget.emergency_threshold = data.get('emergency_threshold', 0.95)
        except Exception as e:
            logger.error(f"Failed to load budget data: {e}")


def track_llm_usage(operation_type: str, spiritual_context: Optional[str] = None):
    """Decorator to automatically track LLM token usage"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user_id and session_id from kwargs if available
            user_id = kwargs.get('user_id')
            session_id = kwargs.get('session_id')
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Extract token usage from result
            if isinstance(result, dict) and 'usage' in result:
                usage_info = result['usage']
                
                # Get tracker instance (singleton pattern)
                tracker = get_token_tracker()
                
                tracker.track_usage(
                    operation_type=operation_type,
                    model_name=usage_info.get('model_name', 'gemini-pro'),
                    input_tokens=usage_info.get('input_tokens', 0),
                    output_tokens=usage_info.get('output_tokens', 0),
                    user_id=user_id,
                    session_id=session_id,
                    spiritual_context=spiritual_context
                )
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions
            user_id = kwargs.get('user_id')
            session_id = kwargs.get('session_id')
            
            result = func(*args, **kwargs)
            
            if isinstance(result, dict) and 'usage' in result:
                usage_info = result['usage']
                tracker = get_token_tracker()
                
                tracker.track_usage(
                    operation_type=operation_type,
                    model_name=usage_info.get('model_name', 'gemini-pro'),
                    input_tokens=usage_info.get('input_tokens', 0),
                    output_tokens=usage_info.get('output_tokens', 0),
                    user_id=user_id,
                    session_id=session_id,
                    spiritual_context=spiritual_context
                )
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Singleton pattern for token tracker
_token_tracker_instance = None

def get_token_tracker() -> TokenUsageTracker:
    """Get singleton token tracker instance"""
    global _token_tracker_instance
    if _token_tracker_instance is None:
        _token_tracker_instance = TokenUsageTracker()
    return _token_tracker_instance


# Example usage and testing
if __name__ == "__main__":
    # Initialize tracker
    tracker = get_token_tracker()
    
    # Simulate some usage
    print("🕉️ Testing AI Cost Management System")
    print("=" * 50)
    
    # Test various operations
    test_operations = [
        {
            'operation_type': 'spiritual_guidance',
            'model_name': 'gemini-pro',
            'input_tokens': 150,
            'output_tokens': 300,
            'user_id': 'user_123',
            'spiritual_context': 'dharma'
        },
        {
            'operation_type': 'voice_response',
            'model_name': 'gemini-flash',
            'input_tokens': 80,
            'output_tokens': 120,
            'user_id': 'user_456',
            'spiritual_context': 'meditation'
        },
        {
            'operation_type': 'expert_review',
            'model_name': 'local_fallback',
            'input_tokens': 200,
            'output_tokens': 100,
            'spiritual_context': 'scripture'
        }
    ]
    
    for op in test_operations:
        usage = tracker.track_usage(**op)
        print(f"✅ Tracked: {usage.operation_type} - ${usage.estimated_cost:.6f}")
    
    # Check budget status
    budget_status = tracker.check_budget_limits('user_123')
    print(f"\n💰 Budget Status:")
    print(f"Daily: ${budget_status['daily_usage']:.4f} / ${budget_status['daily_limit']:.2f} "
          f"({budget_status['daily_percentage']:.1f}%)")
    print(f"Alerts: {len(budget_status['alerts'])}")
    
    # Get analytics
    analytics = tracker.get_usage_analytics('24h')
    print(f"\n📊 24h Analytics:")
    print(f"Operations: {analytics['total_operations']}")
    print(f"Total Cost: ${analytics['total_cost']:.6f}")
    print(f"Models Used: {list(analytics['usage_by_model'].keys())}")
    
    print("\n🎉 Token tracking system working correctly!")
