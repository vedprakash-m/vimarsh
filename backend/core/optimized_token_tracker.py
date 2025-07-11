"""
Optimized Token Usage Tracking System with Memory Management
Replaces the original token tracker with LRU cache limits and periodic cleanup
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, OrderedDict
import os
import asyncio
import threading
from functools import lru_cache

# Import database service and transaction manager for persistent storage
try:
    from services.database_service import db_service, UsageRecord, UserStats
    from services.transaction_manager import transaction_manager, atomic_token_operation
    DATABASE_AVAILABLE = True
    TRANSACTION_MANAGER_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    TRANSACTION_MANAGER_AVAILABLE = False

# Import unified configuration
try:
    from config.unified_config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

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


class LRUCache:
    """Lightweight LRU cache implementation for memory management"""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache = OrderedDict()
        
    def get(self, key: str) -> Any:
        """Get item from cache, moving it to end (most recently used)"""
        if key in self.cache:
            # Move to end
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        return None
    
    def put(self, key: str, value: Any):
        """Put item in cache, evicting oldest if necessary"""
        if key in self.cache:
            # Update existing
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Evict oldest
            self.cache.popitem(last=False)
        
        self.cache[key] = value
    
    def remove(self, key: str):
        """Remove item from cache"""
        self.cache.pop(key, None)
    
    def clear(self):
        """Clear all items from cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


class OptimizedTokenTracker:
    """Optimized token usage tracker with memory management and performance enhancements"""
    
    def __init__(self, max_memory_records: int = 1000, max_cache_size: int = 500):
        # Memory management configuration
        self.max_memory_records = max_memory_records
        self.max_cache_size = max_cache_size
        
        # In-memory storage with LRU eviction
        self.usage_records = LRUCache(max_memory_records)
        self.user_stats_cache = LRUCache(max_cache_size)
        self.session_stats = defaultdict(dict)
        
        # Performance optimization
        self._stats_dirty = defaultdict(bool)  # Track which stats need recalculation
        self._last_cleanup = datetime.utcnow()
        self._cleanup_interval = timedelta(hours=1)  # Cleanup every hour
        
        # Thread safety
        self._lock = threading.RLock()
        
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
        
        # Load configuration
        self._load_configuration()
        
        # Start periodic cleanup task
        self._start_cleanup_task()
    
    def _load_configuration(self):
        """Load configuration from unified config system"""
        if CONFIG_AVAILABLE:
            config = get_config()
            self.max_memory_records = config.get_int('TOKEN_TRACKER_MAX_MEMORY_RECORDS', self.max_memory_records)
            self.max_cache_size = config.get_int('TOKEN_TRACKER_MAX_CACHE_SIZE', self.max_cache_size)
            
            # Update cleanup interval from config
            cleanup_hours = config.get_int('TOKEN_TRACKER_CLEANUP_INTERVAL_HOURS', 1)
            self._cleanup_interval = timedelta(hours=cleanup_hours)
            
            logger.info(f"🔧 Token tracker configured: max_memory={self.max_memory_records}, max_cache={self.max_cache_size}")
    
    def _start_cleanup_task(self):
        """Start periodic cleanup task in background"""
        def cleanup_worker():
            while True:
                try:
                    asyncio.create_task(self._periodic_cleanup())
                    # Sleep for cleanup interval
                    import time
                    time.sleep(self._cleanup_interval.total_seconds())
                except Exception as e:
                    logger.error(f"Error in cleanup worker: {e}")
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        
        logger.info("🧹 Started periodic cleanup task")
    
    async def _periodic_cleanup(self):
        """Perform periodic cleanup of old records and stats"""
        try:
            current_time = datetime.utcnow()
            
            # Only cleanup if interval has passed
            if current_time - self._last_cleanup < self._cleanup_interval:
                return
            
            with self._lock:
                # Archive old records to database before cleaning up
                await self._archive_old_records()
                
                # Clean up session stats older than 24 hours
                cutoff_time = current_time - timedelta(hours=24)
                expired_sessions = []
                
                for session_id, stats in self.session_stats.items():
                    if 'last_activity' in stats:
                        last_activity = datetime.fromisoformat(stats['last_activity'])
                        if last_activity < cutoff_time:
                            expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.session_stats[session_id]
                
                # Clear dirty flags for stats that haven't been accessed recently
                self._stats_dirty.clear()
                
                self._last_cleanup = current_time
                
                logger.info(f"🧹 Periodic cleanup completed: removed {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Error during periodic cleanup: {e}")
    
    async def _archive_old_records(self):
        """Archive old records to database and remove from memory"""
        if not DATABASE_AVAILABLE:
            return
        
        try:
            # This would typically archive records older than a certain threshold
            # For now, we'll just log the intent
            logger.debug("📦 Archival process would run here for old records")
            
        except Exception as e:
            logger.error(f"Error during record archival: {e}")
    
    @lru_cache(maxsize=128)
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage with caching"""
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
        """Record a new token usage event with optimized memory management"""
        
        with self._lock:
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
            
            # Store in LRU cache (automatically evicts old records)
            usage_key = f"{user_id}_{session_id}_{usage.timestamp.isoformat()}"
            self.usage_records.put(usage_key, usage)
            
            # Update user stats efficiently
            self._update_user_stats_optimized(usage)
            self._update_session_stats_optimized(usage)
            
            # Mark user stats as dirty for lazy recalculation
            self._stats_dirty[user_id] = True
            
        # Save to database asynchronously (non-blocking)
        if DATABASE_AVAILABLE and TRANSACTION_MANAGER_AVAILABLE:
            asyncio.create_task(self._save_usage_atomic(usage, personality))
        elif DATABASE_AVAILABLE:
            asyncio.create_task(self._save_usage_to_db(usage, personality))
        
        logger.info(f"💰 Token usage recorded - User: {user_email}, Tokens: {total_tokens}, Cost: ${cost_usd:.4f}")
        
        return usage
    
    def _update_user_stats_optimized(self, usage: TokenUsage):
        """Update user statistics with optimized memory usage"""
        user_stats = self.user_stats_cache.get(usage.user_id)
        
        if user_stats is None:
            # Create new stats
            user_stats = UserUsageStats(
                user_id=usage.user_id,
                user_email=usage.user_email,
                total_requests=1,
                total_tokens=usage.total_tokens,
                total_cost_usd=usage.cost_usd,
                current_month_tokens=usage.total_tokens,
                current_month_cost_usd=usage.cost_usd,
                last_request=usage.timestamp,
                avg_tokens_per_request=usage.total_tokens,
                favorite_model=usage.model,
                quality_breakdown={usage.response_quality: 1}
            )
        else:
            # Update existing stats
            user_stats.total_requests += 1
            user_stats.total_tokens += usage.total_tokens
            user_stats.total_cost_usd += usage.cost_usd
            user_stats.last_request = usage.timestamp
            user_stats.avg_tokens_per_request = user_stats.total_tokens / user_stats.total_requests
            
            # Update quality breakdown
            if usage.response_quality in user_stats.quality_breakdown:
                user_stats.quality_breakdown[usage.response_quality] += 1
            else:
                user_stats.quality_breakdown[usage.response_quality] = 1
            
            # Update favorite model (most used)
            # This could be optimized further with a separate counter
            user_stats.favorite_model = usage.model
        
        # Store back in cache
        self.user_stats_cache.put(usage.user_id, user_stats)
    
    def _update_session_stats_optimized(self, usage: TokenUsage):
        """Update session statistics with memory limits"""
        # Keep only essential session data
        if usage.session_id not in self.session_stats:
            self.session_stats[usage.session_id] = {
                'total_tokens': 0,
                'total_cost': 0.0,
                'request_count': 0,
                'first_activity': usage.timestamp.isoformat(),
                'last_activity': usage.timestamp.isoformat()
            }
        
        session_stats = self.session_stats[usage.session_id]
        session_stats['total_tokens'] += usage.total_tokens
        session_stats['total_cost'] += usage.cost_usd
        session_stats['request_count'] += 1
        session_stats['last_activity'] = usage.timestamp.isoformat()
        
        # Clean up sessions if we have too many
        if len(self.session_stats) > self.max_cache_size:
            # Remove oldest session
            oldest_session = min(self.session_stats.keys(), 
                               key=lambda k: self.session_stats[k]['last_activity'])
            del self.session_stats[oldest_session]
    
    async def _save_usage_to_db(self, usage: TokenUsage, personality: str):
        """Save usage record to database"""
        try:
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
        """Save usage record atomically using transaction manager"""
        try:
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
            
            # Use atomic operation from transaction manager
            await atomic_token_operation(usage_record)
            logger.debug(f"💾 Usage record saved atomically: {usage_record.id}")
            
        except Exception as e:
            logger.error(f"Failed to save usage record atomically: {e}")
    
    def get_user_stats(self, user_id: str) -> Optional[UserUsageStats]:
        """Get user statistics with lazy loading from database if needed"""
        with self._lock:
            # Try cache first
            stats = self.user_stats_cache.get(user_id)
            
            if stats is None and DATABASE_AVAILABLE:
                # Load from database asynchronously
                asyncio.create_task(self._load_user_stats_from_db(user_id))
                return None
            
            return stats
    
    async def _load_user_stats_from_db(self, user_id: str):
        """Load user statistics from database"""
        try:
            user_stats = await db_service.get_user_stats(user_id)
            if user_stats:
                # Convert to our format and cache
                stats = UserUsageStats(
                    user_id=user_stats.userId,
                    user_email=user_stats.userEmail,
                    total_requests=user_stats.totalRequests,
                    total_tokens=user_stats.totalTokens,
                    total_cost_usd=user_stats.totalCostUsd,
                    current_month_tokens=user_stats.currentMonthTokens,
                    current_month_cost_usd=user_stats.currentMonthCostUsd,
                    last_request=datetime.fromisoformat(user_stats.lastRequest) if user_stats.lastRequest else None,
                    avg_tokens_per_request=user_stats.avgTokensPerRequest,
                    favorite_model=user_stats.favoriteModel,
                    quality_breakdown=user_stats.qualityBreakdown or {}
                )
                
                self.user_stats_cache.put(user_id, stats)
                logger.debug(f"📊 Loaded user stats from database: {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to load user stats from database: {e}")
    
    def get_memory_usage_info(self) -> Dict[str, Any]:
        """Get information about current memory usage"""
        return {
            "usage_records_count": self.usage_records.size(),
            "max_memory_records": self.max_memory_records,
            "user_stats_cached": self.user_stats_cache.size(),
            "max_cache_size": self.max_cache_size,
            "session_stats_count": len(self.session_stats),
            "last_cleanup": self._last_cleanup.isoformat(),
            "memory_utilization": {
                "usage_records": f"{(self.usage_records.size() / self.max_memory_records) * 100:.1f}%",
                "user_stats": f"{(self.user_stats_cache.size() / self.max_cache_size) * 100:.1f}%"
            }
        }
    
    def force_cleanup(self):
        """Force immediate cleanup (for testing or maintenance)"""
        asyncio.create_task(self._periodic_cleanup())
        logger.info("🧹 Forced cleanup initiated")


# Global optimized tracker instance
_optimized_tracker = None

def get_optimized_token_tracker() -> OptimizedTokenTracker:
    """Get the global optimized token tracker instance"""
    global _optimized_tracker
    if _optimized_tracker is None:
        _optimized_tracker = OptimizedTokenTracker()
    return _optimized_tracker
