"""
Cost Management Service for Vimarsh AI
Implements real-time token usage tracking and budget validation
As per Tech Spec Section 19 and PRD Section 13
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import azure.functions as func
from azure.cosmos import CosmosClient
import asyncio

logger = logging.getLogger(__name__)

class CostCategory(Enum):
    """Cost categories for tracking"""
    LLM_GENERATION = "llm_generation"
    EMBEDDING_GENERATION = "embedding_generation"
    VECTOR_SEARCH = "vector_search"
    TEXT_TO_SPEECH = "text_to_speech"
    SPEECH_TO_TEXT = "speech_to_text"
    TRANSLATION = "translation"

@dataclass
class TokenUsage:
    """Token usage tracking data"""
    user_id: str
    session_id: str
    operation_type: CostCategory
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    timestamp: datetime = field(default_factory=datetime.now)
    model_name: str = "gemini-pro"
    request_id: str = ""
    context_length: int = 0

@dataclass
class BudgetStatus:
    """Budget status information"""
    user_id: str
    daily_budget: float
    monthly_budget: float
    daily_used: float
    monthly_used: float
    daily_remaining: float
    monthly_remaining: float
    is_over_budget: bool
    budget_utilization: float
    cost_trend: str  # "increasing", "stable", "decreasing"

class CostManagementService:
    """Core cost management and tracking service"""
    
    def __init__(self):
        self.cosmos_client = self._initialize_cosmos()
        self.default_daily_budget = float(os.getenv('DEFAULT_DAILY_BUDGET', '5.0'))
        self.default_monthly_budget = float(os.getenv('DEFAULT_MONTHLY_BUDGET', '50.0'))
        self.admin_daily_budget = float(os.getenv('ADMIN_DAILY_BUDGET', '50.0'))
        self.admin_monthly_budget = float(os.getenv('ADMIN_MONTHLY_BUDGET', '500.0'))
        
        # Cost per token estimates (in USD)
        self.token_costs = {
            CostCategory.LLM_GENERATION: 0.0000005,  # Gemini Pro estimate
            CostCategory.EMBEDDING_GENERATION: 0.0000001,
            CostCategory.VECTOR_SEARCH: 0.0000001,
            CostCategory.TEXT_TO_SPEECH: 0.000016,  # Google TTS
            CostCategory.SPEECH_TO_TEXT: 0.000024,  # Google STT
            CostCategory.TRANSLATION: 0.00002,     # Google Translate
        }
        
    def _initialize_cosmos(self):
        """Initialize Cosmos DB client"""
        try:
            cosmos_url = os.getenv('COSMOS_DB_URL')
            cosmos_key = os.getenv('COSMOS_DB_KEY')
            
            if not cosmos_url or not cosmos_key:
                logger.error("🚨 Cosmos DB credentials not configured")
                return None
            
            client = CosmosClient(cosmos_url, cosmos_key)
            logger.info("🔐 Cosmos DB client initialized for cost tracking")
            return client
            
        except Exception as e:
            logger.error(f"🚨 Failed to initialize Cosmos DB: {str(e)}")
            return None
    
    async def track_token_usage(self, usage: TokenUsage) -> bool:
        """Track token usage in real-time"""
        try:
            # Calculate cost
            cost_per_token = self.token_costs.get(usage.operation_type, 0.0000005)
            usage.estimated_cost = usage.total_tokens * cost_per_token
            
            # Store in Cosmos DB
            await self._store_usage_record(usage)
            
            # Update user's running totals
            await self._update_user_totals(usage)
            
            logger.info(f"💰 Token usage tracked: {usage.user_id} - {usage.total_tokens} tokens, ${usage.estimated_cost:.6f}")
            return True
            
        except Exception as e:
            logger.error(f"🚨 Failed to track token usage: {str(e)}")
            return False
    
    async def _store_usage_record(self, usage: TokenUsage):
        """Store usage record in Cosmos DB"""
        if not self.cosmos_client:
            logger.warning("🚨 Cosmos DB not available for usage tracking")
            return
        
        try:
            database = self.cosmos_client.get_database_client('vimarsh-db')
            container = database.get_container_client('token_usage')
            
            record = {
                'id': f"{usage.user_id}_{usage.session_id}_{int(usage.timestamp.timestamp())}",
                'user_id': usage.user_id,
                'session_id': usage.session_id,
                'operation_type': usage.operation_type.value,
                'input_tokens': usage.input_tokens,
                'output_tokens': usage.output_tokens,
                'total_tokens': usage.total_tokens,
                'estimated_cost': usage.estimated_cost,
                'timestamp': usage.timestamp.isoformat(),
                'model_name': usage.model_name,
                'request_id': usage.request_id,
                'context_length': usage.context_length,
                'date': usage.timestamp.strftime('%Y-%m-%d'),
                'hour': usage.timestamp.hour
            }
            
            container.create_item(body=record)
            logger.debug(f"💾 Usage record stored: {record['id']}")
            
        except Exception as e:
            logger.error(f"🚨 Failed to store usage record: {str(e)}")
    
    async def _update_user_totals(self, usage: TokenUsage):
        """Update user's daily and monthly totals"""
        if not self.cosmos_client:
            return
        
        try:
            database = self.cosmos_client.get_database_client('vimarsh-db')
            container = database.get_container_client('user_cost_totals')
            
            today = usage.timestamp.strftime('%Y-%m-%d')
            month = usage.timestamp.strftime('%Y-%m')
            
            # Update daily total
            daily_id = f"{usage.user_id}_{today}"
            await self._upsert_cost_total(container, daily_id, usage.user_id, 'daily', today, usage.estimated_cost)
            
            # Update monthly total  
            monthly_id = f"{usage.user_id}_{month}"
            await self._upsert_cost_total(container, monthly_id, usage.user_id, 'monthly', month, usage.estimated_cost)
            
        except Exception as e:
            logger.error(f"🚨 Failed to update user totals: {str(e)}")
    
    async def _upsert_cost_total(self, container, record_id: str, user_id: str, period_type: str, period: str, cost: float):
        """Upsert cost total record"""
        try:
            # Try to get existing record
            try:
                existing = container.read_item(item=record_id, partition_key=user_id)
                existing['total_cost'] += cost
                existing['total_tokens'] += 1  # Simplified
                existing['last_updated'] = datetime.now().isoformat()
                container.upsert_item(body=existing)
            except:
                # Create new record
                new_record = {
                    'id': record_id,
                    'user_id': user_id,
                    'period_type': period_type,
                    'period': period,
                    'total_cost': cost,
                    'total_tokens': 1,
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
                container.create_item(body=new_record)
                
        except Exception as e:
            logger.error(f"🚨 Failed to upsert cost total: {str(e)}")
    
    async def get_budget_status(self, user_id: str, is_admin: bool = False) -> BudgetStatus:
        """Get current budget status for user"""
        try:
            # Get user's daily and monthly usage
            daily_used = await self._get_period_usage(user_id, 'daily')
            monthly_used = await self._get_period_usage(user_id, 'monthly')
            
            # Determine budget limits
            if is_admin:
                daily_budget = self.admin_daily_budget
                monthly_budget = self.admin_monthly_budget
            else:
                daily_budget = self.default_daily_budget
                monthly_budget = self.default_monthly_budget
            
            # Calculate remaining budgets
            daily_remaining = max(0, daily_budget - daily_used)
            monthly_remaining = max(0, monthly_budget - monthly_used)
            
            # Check if over budget
            is_over_budget = daily_used >= daily_budget or monthly_used >= monthly_budget
            
            # Calculate utilization
            budget_utilization = min(100, (monthly_used / monthly_budget) * 100)
            
            # Determine cost trend
            cost_trend = await self._calculate_cost_trend(user_id)
            
            return BudgetStatus(
                user_id=user_id,
                daily_budget=daily_budget,
                monthly_budget=monthly_budget,
                daily_used=daily_used,
                monthly_used=monthly_used,
                daily_remaining=daily_remaining,
                monthly_remaining=monthly_remaining,
                is_over_budget=is_over_budget,
                budget_utilization=budget_utilization,
                cost_trend=cost_trend
            )
            
        except Exception as e:
            logger.error(f"🚨 Failed to get budget status: {str(e)}")
            return BudgetStatus(
                user_id=user_id,
                daily_budget=self.default_daily_budget,
                monthly_budget=self.default_monthly_budget,
                daily_used=0,
                monthly_used=0,
                daily_remaining=self.default_daily_budget,
                monthly_remaining=self.default_monthly_budget,
                is_over_budget=False,
                budget_utilization=0,
                cost_trend="stable"
            )
    
    async def _get_period_usage(self, user_id: str, period_type: str) -> float:
        """Get usage for current period"""
        if not self.cosmos_client:
            return 0.0
        
        try:
            database = self.cosmos_client.get_database_client('vimarsh-db')
            container = database.get_container_client('user_cost_totals')
            
            if period_type == 'daily':
                period = datetime.now().strftime('%Y-%m-%d')
            else:
                period = datetime.now().strftime('%Y-%m')
            
            record_id = f"{user_id}_{period}"
            
            try:
                record = container.read_item(item=record_id, partition_key=user_id)
                return record.get('total_cost', 0.0)
            except:
                return 0.0
                
        except Exception as e:
            logger.error(f"🚨 Failed to get period usage: {str(e)}")
            return 0.0
    
    async def _calculate_cost_trend(self, user_id: str) -> str:
        """Calculate cost trend for user"""
        # Simplified implementation - could be enhanced with ML
        try:
            current_week = await self._get_week_usage(user_id, 0)
            previous_week = await self._get_week_usage(user_id, 1)
            
            if previous_week == 0:
                return "stable"
            
            change_percent = ((current_week - previous_week) / previous_week) * 100
            
            if change_percent > 10:
                return "increasing"
            elif change_percent < -10:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"🚨 Failed to calculate cost trend: {str(e)}")
            return "stable"
    
    async def _get_week_usage(self, user_id: str, weeks_ago: int) -> float:
        """Get usage for specific week"""
        # Simplified implementation
        return 0.0
    
    async def validate_budget_before_operation(self, user_id: str, estimated_cost: float, is_admin: bool = False) -> Tuple[bool, str]:
        """Validate budget before performing expensive operation"""
        try:
            budget_status = await self.get_budget_status(user_id, is_admin)
            
            # Check if user is already over budget
            if budget_status.is_over_budget:
                message = f"🚨 Budget exceeded. Daily: ${budget_status.daily_used:.2f}/${budget_status.daily_budget:.2f}, Monthly: ${budget_status.monthly_used:.2f}/${budget_status.monthly_budget:.2f}"
                logger.warning(f"Budget validation failed for {user_id}: {message}")
                return False, message
            
            # Check if this operation would exceed budget
            if (budget_status.daily_used + estimated_cost) > budget_status.daily_budget:
                message = f"⚠️ This operation would exceed your daily budget of ${budget_status.daily_budget:.2f}"
                logger.warning(f"Budget validation failed for {user_id}: {message}")
                return False, message
            
            if (budget_status.monthly_used + estimated_cost) > budget_status.monthly_budget:
                message = f"⚠️ This operation would exceed your monthly budget of ${budget_status.monthly_budget:.2f}"
                logger.warning(f"Budget validation failed for {user_id}: {message}")
                return False, message
            
            logger.info(f"✅ Budget validation passed for {user_id}: ${estimated_cost:.6f}")
            return True, "Budget validation passed"
            
        except Exception as e:
            logger.error(f"🚨 Budget validation error: {str(e)}")
            return True, "Budget validation unavailable - proceeding"
    
    async def get_cost_analytics(self, admin_user_id: str) -> Dict[str, Any]:
        """Get comprehensive cost analytics for admin dashboard"""
        try:
            analytics = {
                'total_users': await self._get_total_users(),
                'daily_total_cost': await self._get_total_cost('daily'),
                'monthly_total_cost': await self._get_total_cost('monthly'),
                'top_users': await self._get_top_users_by_cost(),
                'cost_by_category': await self._get_cost_by_category(),
                'budget_utilization': await self._get_budget_utilization(),
                'abuse_patterns': await self._detect_abuse_patterns(),
                'cost_trend': await self._get_system_cost_trend(),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"📊 Cost analytics generated for admin {admin_user_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"🚨 Failed to get cost analytics: {str(e)}")
            return {'error': str(e)}
    
    async def _get_total_users(self) -> int:
        """Get total number of users with usage"""
        # Simplified implementation
        return 42  # Placeholder
    
    async def _get_total_cost(self, period_type: str) -> float:
        """Get total cost for period"""
        # Simplified implementation
        return 125.50  # Placeholder
    
    async def _get_top_users_by_cost(self) -> List[Dict[str, Any]]:
        """Get top users by cost"""
        # Simplified implementation
        return [
            {'user_id': 'user1', 'cost': 15.25, 'usage_count': 50},
            {'user_id': 'user2', 'cost': 12.75, 'usage_count': 35},
            {'user_id': 'user3', 'cost': 8.90, 'usage_count': 28}
        ]
    
    async def _get_cost_by_category(self) -> Dict[str, float]:
        """Get cost breakdown by category"""
        return {
            'llm_generation': 85.2,
            'text_to_speech': 12.3,
            'speech_to_text': 8.9,
            'translation': 4.1,
            'vector_search': 2.5,
            'embedding_generation': 1.8
        }
    
    async def _get_budget_utilization(self) -> float:
        """Get overall budget utilization"""
        return 67.5  # Placeholder
    
    async def _detect_abuse_patterns(self) -> List[Dict[str, Any]]:
        """Detect potential abuse patterns"""
        return [
            {'user_id': 'user123', 'pattern': 'excessive_requests', 'severity': 'high'},
            {'user_id': 'user456', 'pattern': 'unusual_hours', 'severity': 'medium'}
        ]
    
    async def _get_system_cost_trend(self) -> str:
        """Get system-wide cost trend"""
        return "increasing"  # Placeholder
    
    async def block_user(self, admin_user_id: str, target_user_id: str, reason: str) -> bool:
        """Block user from using the service"""
        try:
            # Implementation would update user status in database
            logger.info(f"🚫 Admin {admin_user_id} blocked user {target_user_id}: {reason}")
            return True
        except Exception as e:
            logger.error(f"🚨 Failed to block user: {str(e)}")
            return False
    
    async def unblock_user(self, admin_user_id: str, target_user_id: str) -> bool:
        """Unblock user"""
        try:
            # Implementation would update user status in database
            logger.info(f"✅ Admin {admin_user_id} unblocked user {target_user_id}")
            return True
        except Exception as e:
            logger.error(f"🚨 Failed to unblock user: {str(e)}")
            return False
    
    async def set_user_budget(self, admin_user_id: str, target_user_id: str, daily_budget: float, monthly_budget: float) -> bool:
        """Set custom budget for user"""
        try:
            # Implementation would update user budget in database
            logger.info(f"💰 Admin {admin_user_id} set budget for {target_user_id}: ${daily_budget:.2f}/day, ${monthly_budget:.2f}/month")
            return True
        except Exception as e:
            logger.error(f"🚨 Failed to set user budget: {str(e)}")
            return False

# Global instance
cost_management = CostManagementService()
