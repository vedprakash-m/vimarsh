"""
Personality-Specific Caching Service for Vimarsh Multi-Personality Platform

This service provides multi-level caching strategies optimized for personality-specific
data, responses, and performance monitoring. It implements cache warming, invalidation,
and performance metrics collection per personality.
"""

import logging
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
from collections import defaultdict, OrderedDict
import threading

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    L1_MEMORY = "l1_memory"      # In-memory cache (fastest)
    L2_REDIS = "l2_redis"        # Redis cache (fast, distributed)
    L3_DATABASE = "l3_database"  # Database cache (persistent)

class CacheType(Enum):
    PERSONALITY_DATA = "personality_data"
    RESPONSE_CACHE = "response_cache"
    KNOWLEDGE_BASE = "knowledge_base"
    USER_PREFERENCES = "user_preferences"
    ANALYTICS_DATA = "analytics_data"

@dataclass
class CacheEntry:
    key: str
    value: Any
    personality_id: str
    cache_type: CacheType
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None
    size_bytes: int = 0

@dataclass
class CacheMetrics:
    personality_id: str
    cache_type: CacheType
    cache_level: CacheLevel
    hit_count: int = 0
    miss_count: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    cache_size_bytes: int = 0
    entry_count: int = 0
    last_updated: datetime = None

@dataclass
class PerformanceMetrics:
    personality_id: str
    request_count: int = 0
    avg_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    error_rate: float = 0.0
    last_updated: datetime = None

class LRUCache:
    """Thread-safe LRU Cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                entry = self.cache.pop(key)
                self.cache[key] = entry
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                return entry
            return None
    
    def put(self, key: str, entry: CacheEntry) -> None:
        with self.lock:
            if key in self.cache:
                # Update existing entry
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)
            
            self.cache[key] = entry
    
    def remove(self, key: str) -> bool:
        with self.lock:
            return self.cache.pop(key, None) is not None
    
    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        with self.lock:
            return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            total_size = sum(entry.size_bytes for entry in self.cache.values())
            total_accesses = sum(entry.access_count for entry in self.cache.values())
            return {
                "entry_count": len(self.cache),
                "total_size_bytes": total_size,
                "total_accesses": total_accesses,
                "avg_accesses_per_entry": total_accesses / len(self.cache) if self.cache else 0
            }

class PersonalityCacheService:
    """Multi-level caching service optimized for personality-specific data"""
    
    def __init__(self):
        # L1 Cache - In-memory LRU caches per personality
        self.l1_caches: Dict[str, Dict[CacheType, LRUCache]] = defaultdict(
            lambda: {cache_type: LRUCache(max_size=500) for cache_type in CacheType}
        )
        
        # Cache metrics per personality and cache type
        self.cache_metrics: Dict[str, Dict[CacheType, Dict[CacheLevel, CacheMetrics]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: CacheMetrics(
                personality_id="", cache_type=CacheType.PERSONALITY_DATA, cache_level=CacheLevel.L1_MEMORY
            )))
        )
        
        # Performance metrics per personality
        self.performance_metrics: Dict[str, PerformanceMetrics] = defaultdict(
            lambda: PerformanceMetrics(personality_id="")
        )
        
        # Cache warming configuration
        self.cache_warming_config = {
            "enabled": True,
            "warm_on_startup": True,
            "warm_popular_personalities": ["krishna", "einstein", "lincoln", "marcus_aurelius"],
            "warm_interval_minutes": 30,
            "preload_responses": 50  # Number of common responses to preload
        }
        
        # Performance monitoring
        self.monitoring_enabled = True
        self.metrics_collection_interval = 60  # seconds
        
        # Initialize cache warming
        if self.cache_warming_config["warm_on_startup"]:
            asyncio.create_task(self._initialize_cache_warming())
    
    async def get(
        self,
        key: str,
        personality_id: str,
        cache_type: CacheType,
        cache_levels: List[CacheLevel] = None
    ) -> Optional[Any]:
        """Get value from cache with multi-level fallback"""
        
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_DATABASE]
        
        start_time = time.time()
        
        for cache_level in cache_levels:
            try:
                value = await self._get_from_level(key, personality_id, cache_type, cache_level)
                if value is not None:
                    # Record cache hit
                    self._record_cache_hit(personality_id, cache_type, cache_level, start_time)
                    
                    # Promote to higher cache levels
                    await self._promote_to_higher_levels(key, value, personality_id, cache_type, cache_level)
                    
                    return value
                    
            except Exception as e:
                logger.warning(f"Cache level {cache_level.value} failed for {key}: {str(e)}")
                continue
        
        # Record cache miss
        self._record_cache_miss(personality_id, cache_type, start_time)
        return None
    
    async def put(
        self,
        key: str,
        value: Any,
        personality_id: str,
        cache_type: CacheType,
        ttl_seconds: int = 3600,
        cache_levels: List[CacheLevel] = None
    ) -> bool:
        """Put value into cache at specified levels"""
        
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY]
        
        success = True
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        for cache_level in cache_levels:
            try:
                await self._put_to_level(key, value, personality_id, cache_type, expires_at, cache_level)
            except Exception as e:
                logger.error(f"Failed to put to cache level {cache_level.value}: {str(e)}")
                success = False
        
        return success
    
    async def invalidate(
        self,
        key: str = None,
        personality_id: str = None,
        cache_type: CacheType = None
    ) -> bool:
        """Invalidate cache entries based on criteria"""
        
        try:
            if key:
                # Invalidate specific key
                for personality_id_key, caches in self.l1_caches.items():
                    if personality_id and personality_id_key != personality_id:
                        continue
                    for cache_type_key, cache in caches.items():
                        if cache_type and cache_type_key != cache_type:
                            continue
                        cache.remove(key)
            
            elif personality_id:
                # Invalidate all entries for a personality
                if personality_id in self.l1_caches:
                    if cache_type:
                        self.l1_caches[personality_id][cache_type].clear()
                    else:
                        for cache in self.l1_caches[personality_id].values():
                            cache.clear()
            
            elif cache_type:
                # Invalidate all entries of a specific type
                for caches in self.l1_caches.values():
                    caches[cache_type].clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache invalidation failed: {str(e)}")
            return False
    
    async def warm_cache(self, personality_id: str) -> bool:
        """Warm cache for a specific personality"""
        
        try:
            logger.info(f"Warming cache for personality: {personality_id}")
            
            # Warm personality data
            await self._warm_personality_data(personality_id)
            
            # Warm common responses
            await self._warm_common_responses(personality_id)
            
            # Warm knowledge base
            await self._warm_knowledge_base(personality_id)
            
            logger.info(f"Cache warming completed for personality: {personality_id}")
            return True
            
        except Exception as e:
            logger.error(f"Cache warming failed for {personality_id}: {str(e)}")
            return False
    
    def get_cache_metrics(self, personality_id: str = None) -> Dict[str, Any]:
        """Get cache performance metrics"""
        
        if personality_id:
            return self._get_personality_metrics(personality_id)
        else:
            return self._get_global_metrics()
    
    def get_performance_metrics(self, personality_id: str = None) -> Dict[str, Any]:
        """Get performance metrics"""
        
        if personality_id:
            metrics = self.performance_metrics.get(personality_id)
            return asdict(metrics) if metrics else {}
        else:
            return {
                pid: asdict(metrics) for pid, metrics in self.performance_metrics.items()
            }
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance and cleanup"""
        
        optimization_results = {
            "cleaned_entries": 0,
            "memory_freed_mb": 0,
            "personalities_optimized": 0
        }
        
        try:
            for personality_id, caches in self.l1_caches.items():
                for cache_type, cache in caches.items():
                    # Remove expired entries
                    expired_count = await self._cleanup_expired_entries(cache)
                    optimization_results["cleaned_entries"] += expired_count
                
                optimization_results["personalities_optimized"] += 1
            
            # Update metrics
            await self._update_performance_metrics()
            
            logger.info(f"Cache optimization completed: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {str(e)}")
            return optimization_results
    
    # Private methods
    
    async def _get_from_level(
        self,
        key: str,
        personality_id: str,
        cache_type: CacheType,
        cache_level: CacheLevel
    ) -> Optional[Any]:
        """Get value from specific cache level"""
        
        if cache_level == CacheLevel.L1_MEMORY:
            cache = self.l1_caches[personality_id][cache_type]
            entry = cache.get(key)
            if entry and entry.expires_at > datetime.now():
                return entry.value
            elif entry:
                # Remove expired entry
                cache.remove(key)
        
        elif cache_level == CacheLevel.L2_REDIS:
            # Redis implementation would go here
            # For now, return None as Redis is not implemented
            return None
        
        elif cache_level == CacheLevel.L3_DATABASE:
            # Database cache implementation would go here
            # For now, return None as database cache is not implemented
            return None
        
        return None
    
    async def _put_to_level(
        self,
        key: str,
        value: Any,
        personality_id: str,
        cache_type: CacheType,
        expires_at: datetime,
        cache_level: CacheLevel
    ) -> None:
        """Put value to specific cache level"""
        
        if cache_level == CacheLevel.L1_MEMORY:
            cache = self.l1_caches[personality_id][cache_type]
            
            # Calculate size (rough estimate)
            size_bytes = len(str(value).encode('utf-8'))
            
            entry = CacheEntry(
                key=key,
                value=value,
                personality_id=personality_id,
                cache_type=cache_type,
                created_at=datetime.now(),
                expires_at=expires_at,
                size_bytes=size_bytes
            )
            
            cache.put(key, entry)
        
        elif cache_level == CacheLevel.L2_REDIS:
            # Redis implementation would go here
            pass
        
        elif cache_level == CacheLevel.L3_DATABASE:
            # Database cache implementation would go here
            pass
    
    async def _promote_to_higher_levels(
        self,
        key: str,
        value: Any,
        personality_id: str,
        cache_type: CacheType,
        current_level: CacheLevel
    ) -> None:
        """Promote cache entry to higher levels"""
        
        if current_level == CacheLevel.L2_REDIS:
            # Promote to L1
            await self._put_to_level(
                key, value, personality_id, cache_type,
                datetime.now() + timedelta(hours=1),
                CacheLevel.L1_MEMORY
            )
        elif current_level == CacheLevel.L3_DATABASE:
            # Promote to L1 and L2
            expires_at = datetime.now() + timedelta(hours=1)
            await self._put_to_level(key, value, personality_id, cache_type, expires_at, CacheLevel.L1_MEMORY)
            # await self._put_to_level(key, value, personality_id, cache_type, expires_at, CacheLevel.L2_REDIS)
    
    def _record_cache_hit(
        self,
        personality_id: str,
        cache_type: CacheType,
        cache_level: CacheLevel,
        start_time: float
    ) -> None:
        """Record cache hit metrics"""
        
        metrics = self.cache_metrics[personality_id][cache_type][cache_level]
        metrics.hit_count += 1
        metrics.total_requests += 1
        metrics.hit_rate = metrics.hit_count / metrics.total_requests
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        if metrics.avg_response_time_ms == 0:
            metrics.avg_response_time_ms = response_time
        else:
            metrics.avg_response_time_ms = (metrics.avg_response_time_ms + response_time) / 2
        
        metrics.last_updated = datetime.now()
    
    def _record_cache_miss(
        self,
        personality_id: str,
        cache_type: CacheType,
        start_time: float
    ) -> None:
        """Record cache miss metrics"""
        
        for cache_level in CacheLevel:
            metrics = self.cache_metrics[personality_id][cache_type][cache_level]
            metrics.miss_count += 1
            metrics.total_requests += 1
            metrics.hit_rate = metrics.hit_count / metrics.total_requests if metrics.total_requests > 0 else 0
            metrics.last_updated = datetime.now()
    
    async def _warm_personality_data(self, personality_id: str) -> None:
        """Warm personality-specific data"""
        
        # Mock personality data warming
        personality_data = {
            "id": personality_id,
            "name": f"Personality {personality_id}",
            "domain": "spiritual",
            "voice_settings": {},
            "knowledge_base_ids": []
        }
        
        await self.put(
            f"personality:{personality_id}",
            personality_data,
            personality_id,
            CacheType.PERSONALITY_DATA,
            ttl_seconds=7200  # 2 hours
        )
    
    async def _warm_common_responses(self, personality_id: str) -> None:
        """Warm common responses for personality"""
        
        common_queries = [
            "What is the meaning of life?",
            "How can I find happiness?",
            "What is wisdom?",
            "How should I live?",
            "What is truth?"
        ]
        
        for i, query in enumerate(common_queries):
            query_hash = hashlib.md5(query.encode()).hexdigest()
            mock_response = f"This is a {personality_id} response to: {query}"
            
            await self.put(
                f"response:{query_hash}",
                mock_response,
                personality_id,
                CacheType.RESPONSE_CACHE,
                ttl_seconds=3600  # 1 hour
            )
    
    async def _warm_knowledge_base(self, personality_id: str) -> None:
        """Warm knowledge base data for personality"""
        
        # Mock knowledge base warming
        knowledge_data = {
            "chunks": [f"Knowledge chunk {i} for {personality_id}" for i in range(10)],
            "embeddings": [f"embedding_{i}" for i in range(10)]
        }
        
        await self.put(
            f"knowledge:{personality_id}",
            knowledge_data,
            personality_id,
            CacheType.KNOWLEDGE_BASE,
            ttl_seconds=14400  # 4 hours
        )
    
    async def _cleanup_expired_entries(self, cache: LRUCache) -> int:
        """Clean up expired entries from cache"""
        
        expired_keys = []
        current_time = datetime.now()
        
        with cache.lock:
            for key, entry in cache.cache.items():
                if entry.expires_at < current_time:
                    expired_keys.append(key)
        
        for key in expired_keys:
            cache.remove(key)
        
        return len(expired_keys)
    
    async def _update_performance_metrics(self) -> None:
        """Update performance metrics for all personalities"""
        
        for personality_id in self.l1_caches.keys():
            metrics = self.performance_metrics[personality_id]
            metrics.personality_id = personality_id
            
            # Calculate cache hit rate across all cache types
            total_hits = 0
            total_requests = 0
            
            for cache_type_metrics in self.cache_metrics[personality_id].values():
                for level_metrics in cache_type_metrics.values():
                    total_hits += level_metrics.hit_count
                    total_requests += level_metrics.total_requests
            
            metrics.cache_hit_rate = total_hits / total_requests if total_requests > 0 else 0
            
            # Calculate memory usage (rough estimate)
            total_memory = 0
            for cache_type, cache in self.l1_caches[personality_id].items():
                stats = cache.get_stats()
                total_memory += stats["total_size_bytes"]
            
            metrics.memory_usage_mb = total_memory / (1024 * 1024)  # Convert to MB
            metrics.last_updated = datetime.now()
    
    def _get_personality_metrics(self, personality_id: str) -> Dict[str, Any]:
        """Get metrics for specific personality"""
        
        cache_metrics = {}
        for cache_type, level_metrics in self.cache_metrics[personality_id].items():
            cache_metrics[cache_type.value] = {
                level.value: asdict(metrics) for level, metrics in level_metrics.items()
            }
        
        performance_metrics = asdict(self.performance_metrics[personality_id])
        
        # Add cache statistics
        cache_stats = {}
        for cache_type, cache in self.l1_caches[personality_id].items():
            cache_stats[cache_type.value] = cache.get_stats()
        
        return {
            "personality_id": personality_id,
            "cache_metrics": cache_metrics,
            "performance_metrics": performance_metrics,
            "cache_statistics": cache_stats
        }
    
    def _get_global_metrics(self) -> Dict[str, Any]:
        """Get global cache metrics"""
        
        global_stats = {
            "total_personalities": len(self.l1_caches),
            "total_cache_entries": 0,
            "total_memory_usage_mb": 0,
            "avg_hit_rate": 0,
            "personalities": {}
        }
        
        total_hit_rate = 0
        personality_count = 0
        
        for personality_id in self.l1_caches.keys():
            personality_metrics = self._get_personality_metrics(personality_id)
            global_stats["personalities"][personality_id] = personality_metrics
            
            # Aggregate statistics
            for cache_type, cache in self.l1_caches[personality_id].items():
                stats = cache.get_stats()
                global_stats["total_cache_entries"] += stats["entry_count"]
                global_stats["total_memory_usage_mb"] += stats["total_size_bytes"] / (1024 * 1024)
            
            # Add to average hit rate calculation
            perf_metrics = self.performance_metrics[personality_id]
            total_hit_rate += perf_metrics.cache_hit_rate
            personality_count += 1
        
        if personality_count > 0:
            global_stats["avg_hit_rate"] = total_hit_rate / personality_count
        
        return global_stats
    
    async def _initialize_cache_warming(self) -> None:
        """Initialize cache warming for popular personalities"""
        
        try:
            await asyncio.sleep(5)  # Wait for system initialization
            
            for personality_id in self.cache_warming_config["warm_popular_personalities"]:
                await self.warm_cache(personality_id)
            
            # Schedule periodic cache warming
            if self.cache_warming_config["enabled"]:
                asyncio.create_task(self._periodic_cache_warming())
                
        except Exception as e:
            logger.error(f"Cache warming initialization failed: {str(e)}")
    
    async def _periodic_cache_warming(self) -> None:
        """Periodic cache warming task"""
        
        while self.cache_warming_config["enabled"]:
            try:
                await asyncio.sleep(self.cache_warming_config["warm_interval_minutes"] * 60)
                
                for personality_id in self.cache_warming_config["warm_popular_personalities"]:
                    await self.warm_cache(personality_id)
                
                # Optimize cache
                await self.optimize_cache()
                
            except Exception as e:
                logger.error(f"Periodic cache warming failed: {str(e)}")

# Global cache service instance
personality_cache_service = PersonalityCacheService()