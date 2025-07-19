"""
Cache Service for Vimarsh Admin Features
Provides caching layer for frequently accessed admin data with automatic invalidation
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
import threading
import asyncio
from collections import OrderedDict
from enum import Enum

# Import unified configuration
try:
    from config.unified_config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"  # Time to live
    LRU = "lru"  # Least recently used
    LFU = "lfu"  # Least frequently used
    MANUAL = "manual"  # Manual invalidation only


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry has expired based on TTL"""
        if self.ttl_seconds is None:
            return False
        
        age = (datetime.utcnow() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "ttl_seconds": self.ttl_seconds
        }


class CacheService:
    """High-performance cache service for admin data"""
    
    def __init__(self, 
                 max_size: int = 1000,
                 default_ttl: int = 3600,  # 1 hour
                 strategy: CacheStrategy = CacheStrategy.LRU):
        
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        # Thread-safe storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Performance metrics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        # Load configuration
        self._load_configuration()
        
        # Start cleanup task
        self._start_cleanup_task()
        
        logger.info(f"🚀 Cache service initialized: strategy={strategy.value}, max_size={max_size}, default_ttl={default_ttl}s")
    
    def _load_configuration(self):
        """Load configuration from unified config system"""
        if CONFIG_AVAILABLE:
            config = get_config()
            self.max_size = config.get_int('CACHE_MAX_SIZE', self.max_size)
            self.default_ttl = config.get_int('CACHE_DEFAULT_TTL', self.default_ttl)
            
            strategy_name = config.get('CACHE_STRATEGY', 'lru').lower()
            try:
                self.strategy = CacheStrategy(strategy_name)
            except ValueError:
                logger.warning(f"Invalid cache strategy '{strategy_name}', using LRU")
                self.strategy = CacheStrategy.LRU
    
    def _start_cleanup_task(self):
        """Start periodic cleanup task"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired()
                    # Cleanup every 5 minutes
                    import time
                    time.sleep(300)
                except Exception as e:
                    logger.error(f"Error in cache cleanup worker: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired(self):
        """Clean up expired entries"""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._evictions += 1
            
            if expired_keys:
                logger.debug(f"🧹 Cache cleanup: removed {len(expired_keys)} expired entries")
    
    def _evict_if_needed(self):
        """Evict entries if cache is full"""
        if len(self._cache) < self.max_size:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used (first in OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            lfu_key = min(self._cache.keys(), 
                         key=lambda k: self._cache[k].access_count)
            del self._cache[lfu_key]
        
        self._evictions += 1
    
    def put(self, 
            key: str, 
            value: Any, 
            ttl_seconds: Optional[int] = None) -> bool:
        """Store value in cache"""
        
        with self._lock:
            # Use default TTL if not specified
            if ttl_seconds is None:
                ttl_seconds = self.default_ttl
            
            # Remove existing entry if present
            if key in self._cache:
                del self._cache[key]
            
            # Evict if needed
            self._evict_if_needed()
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=0,
                ttl_seconds=ttl_seconds
            )
            
            # Add to cache (at end for LRU)
            self._cache[key] = entry
            
            logger.debug(f"📦 Cache PUT: {key} (TTL: {ttl_seconds}s)")
            return True
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                logger.debug(f"🔍 Cache MISS: {key}")
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                self._evictions += 1
                logger.debug(f"⏰ Cache EXPIRED: {key}")
                return None
            
            # Update access info
            entry.touch()
            
            # Move to end for LRU (most recently used)
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)
            
            self._hits += 1
            logger.debug(f"✅ Cache HIT: {key}")
            return entry.value
    
    def get_or_compute(self, 
                      key: str, 
                      compute_func: Callable[[], Any],
                      ttl_seconds: Optional[int] = None) -> Any:
        """Get value from cache or compute if not present"""
        
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        try:
            computed_value = compute_func()
            self.put(key, computed_value, ttl_seconds)
            return computed_value
        except Exception as e:
            logger.error(f"Error computing cache value for key '{key}': {e}")
            raise
    
    async def get_or_compute_async(self,
                                  key: str,
                                  compute_func: Callable[[], Any],
                                  ttl_seconds: Optional[int] = None) -> Any:
        """Async version of get_or_compute"""
        
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value asynchronously
        try:
            if asyncio.iscoroutinefunction(compute_func):
                computed_value = await compute_func()
            else:
                computed_value = compute_func()
            
            self.put(key, computed_value, ttl_seconds)
            return computed_value
        except Exception as e:
            logger.error(f"Error computing async cache value for key '{key}': {e}")
            raise
    
    def delete(self, key: str) -> bool:
        """Remove entry from cache"""
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"🗑️ Cache DELETE: {key}")
                return True
            return False
    
    def clear(self) -> int:
        """Clear all cache entries"""
        
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"🧹 Cache CLEAR: removed {count} entries")
            return count
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern (supports wildcards)"""
        
        import fnmatch
        
        with self._lock:
            matching_keys = [key for key in self._cache.keys() 
                           if fnmatch.fnmatch(key, pattern)]
            
            for key in matching_keys:
                del self._cache[key]
            
            if matching_keys:
                logger.info(f"🧹 Cache INVALIDATE: pattern '{pattern}' removed {len(matching_keys)} entries")
            
            return len(matching_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "utilization": f"{(len(self._cache) / self.max_size) * 100:.1f}%",
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": f"{hit_rate:.1f}%",
                "strategy": self.strategy.value,
                "default_ttl": self.default_ttl
            }
    
    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all cache keys, optionally filtered by pattern"""
        
        with self._lock:
            if pattern is None:
                return list(self._cache.keys())
            
            import fnmatch
            return [key for key in self._cache.keys() 
                   if fnmatch.fnmatch(key, pattern)]
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a cache entry"""
        
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            return entry.to_dict()


# Admin-specific cache helpers
class AdminCacheService:
    """Specialized cache service for admin data with predefined patterns"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        
        # Predefined cache patterns for admin data
        self.cache_patterns = {
            "user_stats": "admin:user_stats:{user_id}",
            "system_metrics": "admin:system_metrics:{metric_type}",
            "cost_analytics": "admin:cost_analytics:{period}:{user_id}",
            "usage_reports": "admin:usage_reports:{report_type}:{date}",
            "security_events": "admin:security_events:{event_type}:{date}",
            "token_analytics": "admin:token_analytics:{period}",
            "performance_metrics": "admin:performance:{metric}:{timeframe}"
        }
        
        # Default TTL for different data types (in seconds)
        self.ttl_config = {
            "user_stats": 1800,      # 30 minutes
            "system_metrics": 300,    # 5 minutes
            "cost_analytics": 3600,   # 1 hour
            "usage_reports": 7200,    # 2 hours
            "security_events": 600,   # 10 minutes
            "token_analytics": 1800,  # 30 minutes
            "performance_metrics": 300 # 5 minutes
        }
    
    def _make_key(self, pattern_name: str, **kwargs) -> str:
        """Create cache key from pattern"""
        pattern = self.cache_patterns.get(pattern_name)
        if not pattern:
            raise ValueError(f"Unknown cache pattern: {pattern_name}")
        
        return pattern.format(**kwargs)
    
    def get_user_stats(self, user_id: str) -> Optional[Any]:
        """Get cached user statistics"""
        key = self._make_key("user_stats", user_id=user_id)
        return self.cache.get(key)
    
    def cache_user_stats(self, user_id: str, stats: Any) -> bool:
        """Cache user statistics"""
        key = self._make_key("user_stats", user_id=user_id)
        ttl = self.ttl_config["user_stats"]
        return self.cache.put(key, stats, ttl)
    
    def get_system_metrics(self, metric_type: str) -> Optional[Any]:
        """Get cached system metrics"""
        key = self._make_key("system_metrics", metric_type=metric_type)
        return self.cache.get(key)
    
    def cache_system_metrics(self, metric_type: str, metrics: Any) -> bool:
        """Cache system metrics"""
        key = self._make_key("system_metrics", metric_type=metric_type)
        ttl = self.ttl_config["system_metrics"]
        return self.cache.put(key, metrics, ttl)
    
    def get_cost_analytics(self, period: str, user_id: str = "all") -> Optional[Any]:
        """Get cached cost analytics"""
        key = self._make_key("cost_analytics", period=period, user_id=user_id)
        return self.cache.get(key)
    
    def cache_cost_analytics(self, period: str, analytics: Any, user_id: str = "all") -> bool:
        """Cache cost analytics"""
        key = self._make_key("cost_analytics", period=period, user_id=user_id)
        ttl = self.ttl_config["cost_analytics"]
        return self.cache.put(key, analytics, ttl)
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a specific user"""
        patterns = [
            f"admin:user_stats:{user_id}",
            f"admin:cost_analytics:*:{user_id}"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.cache.invalidate_pattern(pattern)
        
        logger.info(f"🧹 Invalidated {total_invalidated} cache entries for user {user_id}")
        return total_invalidated
    
    def invalidate_admin_cache(self):
        """Invalidate all admin cache entries"""
        return self.cache.invalidate_pattern("admin:*")


# Global cache service instances
_cache_service = None
_admin_cache_service = None

def get_cache_service() -> CacheService:
    """Get the global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

def get_admin_cache_service() -> AdminCacheService:
    """Get the admin-specific cache service instance"""
    global _admin_cache_service
    if _admin_cache_service is None:
        _admin_cache_service = AdminCacheService(get_cache_service())
    return _admin_cache_service
