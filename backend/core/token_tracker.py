"""
Token Usage Tracking System for AI Cost Management
Tracks and monitors LLM token usage with user-specific analytics
Now integrated with database service for persistent storage
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict
import os
import asyncio

# Import database service and transaction manager for persistent storage
try:
    from services.database_service import db_service, UsageRecord, UserStats
    from services.transaction_manager import transaction_manager, atomic_token_operation
    DATABASE_AVAILABLE = True
    TRANSACTION_MANAGER_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    TRANSACTION_MANAGER_AVAILABLE = False
    
    # Fallback UserStats class for when database service is not available
    class UserStats:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage record for a single request"""
    user_id: str
    user_email: str
    session_id: str
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    request_type: str  # 'spiritual_guidance', 'rag_query', etc.
    response_quality: str  # 'high', 'medium', 'low', 'fallback'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenUsage':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class UserUsageStats:
    """Aggregated usage statistics for a user"""
    user_id: str
    user_email: str
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    current_month_tokens: int
    current_month_cost_usd: float
    last_request: Optional[datetime]
    avg_tokens_per_request: float
    favorite_model: str
    quality_breakdown: Dict[str, int]  # quality -> count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        data = asdict(self)
        data['last_request'] = self.last_request.isoformat() if self.last_request else None
        return data


class TokenUsageTracker:
    """Manages token usage tracking and analytics"""
    
    def __init__(self):
        self.usage_records: List[TokenUsage] = []
        self.user_stats: Dict[str, UserUsageStats] = {}
        self.session_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Cost rates per model (USD per 1K tokens)
        self.cost_rates = {
            'gemini-2.5-flash': {
                'input': 0.00015,  # $0.15 per 1M tokens
                'output': 0.0006   # $0.60 per 1M tokens
            },
            'gemini-1.5-pro': {
                'input': 0.00125,  # $1.25 per 1M tokens
                'output': 0.005    # $5.00 per 1M tokens
            }
        }
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage"""
        if model not in self.cost_rates:
            # Default to Gemini Flash rates
            model = 'gemini-2.5-flash'
        
        rates = self.cost_rates[model]
        input_cost = (input_tokens / 1000) * rates['input']
        output_cost = (output_tokens / 1000) * rates['output']
        
        return input_cost + output_cost
    
    def record_usage(self, 
                    user_id: str, 
                    user_email: str, 
                    session_id: str,
                    model: str,
                    input_tokens: int,
                    output_tokens: int,
                    request_type: str = 'spiritual_guidance',
                    response_quality: str = 'high',
                    personality: str = 'krishna') -> TokenUsage:
        """Record a new token usage event with atomic database persistence"""
        
        total_tokens = input_tokens + output_tokens
        cost_usd = self.calculate_cost(model, input_tokens, output_tokens)
        
        usage = TokenUsage(
            user_id=user_id,
            user_email=user_email,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            request_type=request_type,
            response_quality=response_quality
        )
        
        # Keep in memory for backward compatibility
        self.usage_records.append(usage)
        self._update_user_stats(usage)
        self._update_session_stats(usage)
        
        # Save to database with atomic transaction
        if DATABASE_AVAILABLE and TRANSACTION_MANAGER_AVAILABLE:
            asyncio.create_task(self._save_usage_atomic(usage, personality))
        elif DATABASE_AVAILABLE:
            # Fallback to non-atomic save
            asyncio.create_task(self._save_usage_to_db(usage, personality))
        
        logger.info(f"💰 Token usage recorded - User: {user_email}, Tokens: {total_tokens}, Cost: ${cost_usd:.4f}")
        
        return usage
    
    async def _save_usage_to_db(self, usage: TokenUsage, personality: str):
        """Save usage record to database"""
        try:
            # Convert to database format
            usage_record = UsageRecord(
                id=f"usage_{usage.user_id}_{usage.timestamp.strftime('%Y%m%d_%H%M%S')}",
                userId=usage.user_id,
                userEmail=usage.user_email,
                sessionId=usage.session_id,
                timestamp=usage.timestamp.isoformat(),
                model=usage.model,
                inputTokens=usage.input_tokens,
                outputTokens=usage.output_tokens,
                totalTokens=usage.total_tokens,
                costUsd=usage.cost_usd,
                requestType=usage.request_type,
                responseQuality=usage.response_quality,
                personality=personality
            )
            
            await db_service.save_usage_record(usage_record)
            logger.debug(f"📊 Usage record saved to database: {usage_record.id}")
            
        except Exception as e:
            logger.error(f"Failed to save usage record to database: {e}")
    
    async def _save_usage_atomic(self, usage: TokenUsage, personality: str):
        """Save usage record and user stats atomically using transaction manager"""
        try:
            # Convert to database format
            usage_record = UsageRecord(
                id=f"usage_{usage.user_id}_{usage.timestamp.strftime('%Y%m%d_%H%M%S')}",
                userId=usage.user_id,
                userEmail=usage.user_email,
                sessionId=usage.session_id,
                timestamp=usage.timestamp.isoformat(),
                model=usage.model,
                inputTokens=usage.input_tokens,
                outputTokens=usage.output_tokens,
                totalTokens=usage.total_tokens,
                costUsd=usage.cost_usd,
                requestType=usage.request_type,
                responseQuality=usage.response_quality,
                personality=personality
            )
            
            # Generate updated user stats
            user_stats = await self._generate_user_stats(usage.user_id, usage.user_email, personality)
            
            # Save both records atomically
            await atomic_token_operation(usage_record, user_stats)
            logger.debug(f"🔄 Atomic save completed for user: {usage.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Atomic save failed for usage record: {e}")
            # Fallback to non-atomic save
            await self._save_usage_to_db(usage, personality)
    
    async def _generate_user_stats(self, user_id: str, user_email: str, personality: str) -> UserStats:
        """Generate user statistics for atomic save"""
        try:
            # Get current stats from database
            current_stats = await db_service.get_user_stats(user_id)
            
            # Calculate new stats from in-memory data
            user_usage = [u for u in self.usage_records if u.user_id == user_id]
            
            if not user_usage:
                raise ValueError(f"No usage data found for user: {user_id}")
            
            total_tokens = sum(u.total_tokens for u in user_usage)
            total_cost = sum(u.cost_usd for u in user_usage)
            
            # Current month calculations
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_month_usage = [u for u in user_usage if u.timestamp >= current_month_start]
            
            current_month_tokens = sum(u.total_tokens for u in current_month_usage)
            current_month_cost = sum(u.cost_usd for u in current_month_usage)
            
            # Calculate personality usage
            personality_counts = {}
            for u in user_usage:
                # Use the personality from current request or default
                p = getattr(u, 'personality', personality)
                personality_counts[p] = personality_counts.get(p, 0) + 1
            
            # Calculate quality breakdown
            quality_counts = {}
            for u in user_usage:
                quality_counts[u.response_quality] = quality_counts.get(u.response_quality, 0) + 1
            
            if current_stats:
                # Update existing stats
                current_stats.totalRequests = len(user_usage)
                current_stats.totalTokens = total_tokens
                current_stats.totalCostUsd = total_cost
                current_stats.currentMonthTokens = current_month_tokens
                current_stats.currentMonthCostUsd = current_month_cost
                current_stats.lastRequest = max(u.timestamp for u in user_usage).isoformat()
                current_stats.avgTokensPerRequest = total_tokens / len(user_usage)
                current_stats.updatedAt = datetime.utcnow().isoformat()
                current_stats.personalityUsage = personality_counts
                current_stats.qualityBreakdown = quality_counts
                
                return current_stats
            else:
                # Create new stats
                return UserStats(
                    id=f"stats_{user_id}",
                    userId=user_id,
                    userEmail=user_email,
                    totalRequests=len(user_usage),
                    totalTokens=total_tokens,
                    totalCostUsd=total_cost,
                    currentMonthTokens=current_month_tokens,
                    currentMonthCostUsd=current_month_cost,
                    lastRequest=max(u.timestamp for u in user_usage).isoformat(),
                    avgTokensPerRequest=total_tokens / len(user_usage),
                    favoriteModel=max(set(u.model for u in user_usage), key=lambda x: [u.model for u in user_usage].count(x)),
                    personalityUsage=personality_counts,
                    qualityBreakdown=quality_counts,
                    riskScore=0.0,
                    isBlocked=False,
                    blockReason=None
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to generate user stats: {e}")
            raise

    async def _update_user_stats_in_db(self, user_id: str, user_email: str):
        """Update user statistics in database"""
        try:
            # Get current stats from database
            current_stats = await db_service.get_user_stats(user_id)
            
            # Calculate new stats from in-memory data
            user_usage = [u for u in self.usage_records if u.user_id == user_id]
            
            if not user_usage:
                return
            
            total_tokens = sum(u.total_tokens for u in user_usage)
            total_cost = sum(u.cost_usd for u in user_usage)
            
            # Current month calculations
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_month_usage = [u for u in user_usage if u.timestamp >= current_month_start]
            
            current_month_tokens = sum(u.total_tokens for u in current_month_usage)
            current_month_cost = sum(u.cost_usd for u in current_month_usage)
            
            # Create or update user stats
            if current_stats:
                # Update existing stats
                current_stats.totalRequests = len(user_usage)
                current_stats.totalTokens = total_tokens
                current_stats.totalCostUsd = total_cost
                current_stats.currentMonthTokens = current_month_tokens
                current_stats.currentMonthCostUsd = current_month_cost
                current_stats.lastRequest = max(u.timestamp for u in user_usage).isoformat()
                current_stats.avgTokensPerRequest = total_tokens / len(user_usage)
                current_stats.updatedAt = datetime.utcnow().isoformat()
                
                # Update personality usage
                personality_counts = {}
                for u in user_usage:
                    # Try to get personality from request metadata or default to krishna
                    personality = getattr(u, 'personality', 'krishna')
                    personality_counts[personality] = personality_counts.get(personality, 0) + 1
                current_stats.personalityUsage = personality_counts
                
                # Update quality breakdown
                quality_counts = {}
                for u in user_usage:
                    quality_counts[u.response_quality] = quality_counts.get(u.response_quality, 0) + 1
                current_stats.qualityBreakdown = quality_counts
                
                stats_to_save = current_stats
            else:
                # Create new stats
                stats_to_save = UserStats(
                    id=f"stats_{user_id}",
                    userId=user_id,
                    userEmail=user_email,
                    totalRequests=len(user_usage),
                    totalTokens=total_tokens,
                    totalCostUsd=total_cost,
                    currentMonthTokens=current_month_tokens,
                    currentMonthCostUsd=current_month_cost,
                    lastRequest=max(u.timestamp for u in user_usage).isoformat(),
                    avgTokensPerRequest=total_tokens / len(user_usage),
                    favoriteModel=max(set(u.model for u in user_usage), key=lambda x: [u.model for u in user_usage].count(x)),
                    personalityUsage={"krishna": len(user_usage)},  # Default to Krishna
                    qualityBreakdown={u.response_quality: [u.response_quality for u in user_usage].count(u.response_quality) for u in user_usage},
                    riskScore=0.0,
                    isBlocked=False,
                    blockReason=None
                )
            
            await db_service.save_user_stats(stats_to_save)
            logger.debug(f"📊 User stats updated in database: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update user stats in database: {e}")
        
        return usage
    
    def _update_user_stats(self, usage: TokenUsage):
        """Update user statistics with new usage"""
        user_id = usage.user_id
        
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserUsageStats(
                user_id=user_id,
                user_email=usage.user_email,
                total_requests=0,
                total_tokens=0,
                total_cost_usd=0.0,
                current_month_tokens=0,
                current_month_cost_usd=0.0,
                last_request=None,
                avg_tokens_per_request=0.0,
                favorite_model="",
                quality_breakdown={}
            )
        
        stats = self.user_stats[user_id]
        stats.total_requests += 1
        stats.total_tokens += usage.total_tokens
        stats.total_cost_usd += usage.cost_usd
        stats.last_request = usage.timestamp
        stats.avg_tokens_per_request = stats.total_tokens / stats.total_requests
        
        # Update current month stats
        now = datetime.utcnow()
        if usage.timestamp.month == now.month and usage.timestamp.year == now.year:
            stats.current_month_tokens += usage.total_tokens
            stats.current_month_cost_usd += usage.cost_usd
        
        # Update quality breakdown
        if usage.response_quality not in stats.quality_breakdown:
            stats.quality_breakdown[usage.response_quality] = 0
        stats.quality_breakdown[usage.response_quality] += 1
        
        # Update favorite model (most used)
        model_counts = defaultdict(int)
        for record in self.usage_records:
            if record.user_id == user_id:
                model_counts[record.model] += 1
        
        stats.favorite_model = max(model_counts.items(), key=lambda x: x[1])[0] if model_counts else ""
    
    def _update_session_stats(self, usage: TokenUsage):
        """Update session statistics"""
        session_id = usage.session_id
        
        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                'total_tokens': 0,
                'total_cost': 0.0,
                'request_count': 0,
                'start_time': usage.timestamp,
                'last_activity': usage.timestamp
            }
        
        session = self.session_stats[session_id]
        session['total_tokens'] += usage.total_tokens
        session['total_cost'] += usage.cost_usd
        session['request_count'] += 1
        session['last_activity'] = usage.timestamp
    
    def get_user_usage(self, user_id: str) -> Optional[UserUsageStats]:
        """Get usage statistics for a specific user"""
        return self.user_stats.get(user_id)
    
    def get_session_usage(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get usage statistics for a specific session"""
        return self.session_stats.get(session_id)
    
    def get_system_usage(self, days: int = 30) -> Dict[str, Any]:
        """Get system-wide usage statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_records = [r for r in self.usage_records if r.timestamp > cutoff_date]
        
        if not recent_records:
            return {
                'total_users': 0,
                'total_requests': 0,
                'total_tokens': 0,
                'total_cost_usd': 0.0,
                'avg_tokens_per_request': 0.0,
                'cost_per_user': 0.0,
                'model_breakdown': {},
                'quality_breakdown': {},
                'daily_usage': []
            }
        
        total_tokens = sum(r.total_tokens for r in recent_records)
        total_cost = sum(r.cost_usd for r in recent_records)
        unique_users = len(set(r.user_id for r in recent_records))
        
        # Model breakdown
        model_breakdown = defaultdict(int)
        for record in recent_records:
            model_breakdown[record.model] += record.total_tokens
        
        # Quality breakdown
        quality_breakdown = defaultdict(int)
        for record in recent_records:
            quality_breakdown[record.response_quality] += 1
        
        # Daily usage
        daily_usage = defaultdict(lambda: {'tokens': 0, 'cost': 0.0, 'requests': 0})
        for record in recent_records:
            day_key = record.timestamp.strftime('%Y-%m-%d')
            daily_usage[day_key]['tokens'] += record.total_tokens
            daily_usage[day_key]['cost'] += record.cost_usd
            daily_usage[day_key]['requests'] += 1
        
        return {
            'total_users': unique_users,
            'total_requests': len(recent_records),
            'total_tokens': total_tokens,
            'total_cost_usd': total_cost,
            'avg_tokens_per_request': total_tokens / len(recent_records),
            'cost_per_user': total_cost / unique_users if unique_users > 0 else 0.0,
            'model_breakdown': dict(model_breakdown),
            'quality_breakdown': dict(quality_breakdown),
            'daily_usage': [
                {'date': k, **v} for k, v in sorted(daily_usage.items())
            ]
        }
    
    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by token usage"""
        sorted_users = sorted(
            self.user_stats.values(),
            key=lambda u: u.total_tokens,
            reverse=True
        )
        
        return [user.to_dict() for user in sorted_users[:limit]]
    
    def is_user_over_budget(self, user_id: str, budget_usd: float) -> bool:
        """Check if user is over monthly budget"""
        user_stats = self.get_user_usage(user_id)
        if not user_stats:
            return False
        
        return user_stats.current_month_cost_usd > budget_usd
    
    def get_cost_forecast(self, user_id: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Forecast future costs for a user"""
        user_stats = self.get_user_usage(user_id)
        if not user_stats:
            return {'forecast_cost': 0.0, 'confidence': 'low'}
        
        # Simple linear forecast based on current month usage
        now = datetime.utcnow()
        days_in_month = (now.replace(month=now.month + 1, day=1) - now.replace(day=1)).days
        days_elapsed = now.day
        
        if days_elapsed < 3:
            return {'forecast_cost': 0.0, 'confidence': 'low'}
        
        daily_avg = user_stats.current_month_cost_usd / days_elapsed
        forecast_cost = daily_avg * days_ahead
        
        confidence = 'high' if days_elapsed > 7 else 'medium' if days_elapsed > 3 else 'low'
        
        return {
            'forecast_cost': forecast_cost,
            'daily_average': daily_avg,
            'confidence': confidence,
            'days_ahead': days_ahead
        }


# Global token usage tracker
token_tracker = TokenUsageTracker()
