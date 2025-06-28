"""
Intelligent caching system for RAG responses
Reduces LLM costs by caching similar queries and responses
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from functools import lru_cache, wraps
from pathlib import Path
import threading
import pickle
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Cached RAG response with metadata"""
    query_hash: str
    original_query: str
    response_content: str
    spiritual_context: str
    citations: List[Dict[str, Any]]
    timestamp: datetime
    hit_count: int = 1
    last_accessed: datetime = None
    confidence_score: float = 1.0
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp


@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cost_saved: float = 0.0
    hit_rate: float = 0.0
    
    def update_hit(self, saved_cost: float = 0.0):
        self.cache_hits += 1
        self.total_queries += 1
        self.cost_saved += saved_cost
        self.hit_rate = self.cache_hits / self.total_queries
    
    def update_miss(self):
        self.cache_misses += 1
        self.total_queries += 1
        self.hit_rate = self.cache_hits / self.total_queries


class SpiritualQueryCache:
    """Intelligent caching system for spiritual guidance responses"""
    
    def __init__(self, 
                 cache_dir: str = "data/cache",
                 max_cache_size: int = 1000,
                 similarity_threshold: float = 0.85,
                 max_age_days: int = 30):
        """
        Initialize the cache system
        
        Args:
            cache_dir: Directory to store cache files
            max_cache_size: Maximum number of cached responses
            similarity_threshold: Minimum similarity for cache hits (0.0-1.0)
            max_age_days: Maximum age of cached responses in days
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_cache_size = max_cache_size
        self.similarity_threshold = similarity_threshold
        self.max_age_days = max_age_days
        
        # In-memory cache for fast access
        self.memory_cache: Dict[str, CachedResponse] = {}
        
        # Cache performance tracking
        self.stats = CacheStats()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Load existing cache
        self._load_cache()
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent caching"""
        # Remove extra whitespace and convert to lowercase
        normalized = ' '.join(query.lower().strip().split())
        
        # Remove common variations that don't affect meaning
        replacements = {
            'lord krishna': 'krishna',
            'bhagavan': 'krishna',
            'shri krishna': 'krishna',
            'please tell me': '',
            'can you explain': '',
            'what is': '',
            'what does': '',
            'help me understand': ''
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove extra spaces again
        return ' '.join(normalized.split())
    
    def _compute_query_hash(self, query: str, spiritual_context: str) -> str:
        """Compute hash for normalized query with context"""
        normalized_query = self._normalize_query(query)
        content = f"{normalized_query}|{spiritual_context}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _compute_similarity(self, query1: str, query2: str) -> float:
        """Compute similarity between two queries"""
        norm1 = self._normalize_query(query1)
        norm2 = self._normalize_query(query2)
        
        # Use SequenceMatcher for semantic similarity
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _find_similar_responses(self, query: str, spiritual_context: str) -> Optional[CachedResponse]:
        """Find cached responses similar to the query"""
        best_match = None
        best_similarity = 0.0
        
        for cached_response in self.memory_cache.values():
            # Skip if context doesn't match
            if cached_response.spiritual_context != spiritual_context:
                continue
            
            # Skip if too old
            age = datetime.now() - cached_response.timestamp
            if age.days > self.max_age_days:
                continue
            
            # Calculate similarity
            similarity = self._compute_similarity(query, cached_response.original_query)
            
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = cached_response
        
        return best_match
    
    def get_cached_response(self, 
                           query: str, 
                           spiritual_context: str = 'general') -> Optional[Dict[str, Any]]:
        """
        Get cached response for a query
        
        Args:
            query: User's spiritual query
            spiritual_context: Context of the query
            
        Returns:
            Cached response if found, None otherwise
        """
        with self._lock:
            # First try exact hash match
            query_hash = self._compute_query_hash(query, spiritual_context)
            
            if query_hash in self.memory_cache:
                cached = self.memory_cache[query_hash]
                
                # Check if not too old
                age = datetime.now() - cached.timestamp
                if age.days <= self.max_age_days:
                    # Update access statistics
                    cached.hit_count += 1
                    cached.last_accessed = datetime.now()
                    
                    # Estimate cost saved (typical gemini-pro query cost)
                    saved_cost = 0.005
                    self.stats.update_hit(saved_cost)
                    
                    logger.info(f"Cache hit (exact) for query hash {query_hash} "
                              f"(hit #{cached.hit_count})")
                    
                    return {
                        'content': cached.response_content,
                        'citations': cached.citations,
                        'cached': True,
                        'cache_type': 'exact',
                        'hit_count': cached.hit_count,
                        'original_timestamp': cached.timestamp.isoformat(),
                        'confidence': cached.confidence_score
                    }
            
            # Try similarity-based matching
            similar_response = self._find_similar_responses(query, spiritual_context)
            
            if similar_response:
                # Update access statistics
                similar_response.hit_count += 1
                similar_response.last_accessed = datetime.now()
                
                # Lower confidence for similarity matches
                confidence = 0.8
                
                saved_cost = 0.005
                self.stats.update_hit(saved_cost)
                
                logger.info(f"Cache hit (similar) for query: '{query[:50]}...' "
                          f"matched with: '{similar_response.original_query[:50]}...'")
                
                return {
                    'content': similar_response.response_content,
                    'citations': similar_response.citations,
                    'cached': True,
                    'cache_type': 'similar',
                    'hit_count': similar_response.hit_count,
                    'original_query': similar_response.original_query,
                    'original_timestamp': similar_response.timestamp.isoformat(),
                    'confidence': confidence
                }
            
            # No cache hit
            self.stats.update_miss()
            logger.debug(f"Cache miss for query: '{query[:50]}...'")
            return None
    
    def cache_response(self, 
                      query: str,
                      response_content: str,
                      spiritual_context: str = 'general',
                      citations: List[Dict[str, Any]] = None) -> str:
        """
        Cache a spiritual guidance response
        
        Args:
            query: Original user query
            response_content: LLM response content
            spiritual_context: Context of the query
            citations: Source citations
            
        Returns:
            Query hash for the cached response
        """
        if citations is None:
            citations = []
        
        with self._lock:
            query_hash = self._compute_query_hash(query, spiritual_context)
            
            cached_response = CachedResponse(
                query_hash=query_hash,
                original_query=query,
                response_content=response_content,
                spiritual_context=spiritual_context,
                citations=citations,
                timestamp=datetime.now(),
                confidence_score=1.0
            )
            
            # Add to memory cache
            self.memory_cache[query_hash] = cached_response
            
            # Maintain cache size limit
            if len(self.memory_cache) > self.max_cache_size:
                self._evict_old_entries()
            
            # Persist to disk
            self._save_cache_entry(cached_response)
            
            logger.info(f"Cached response for query hash {query_hash}")
            return query_hash
    
    def _evict_old_entries(self):
        """Evict old cache entries to maintain size limit"""
        # Sort by last accessed time and remove oldest
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        entries_to_remove = len(self.memory_cache) - self.max_cache_size + 100  # Remove extra
        
        for i in range(min(entries_to_remove, len(sorted_entries))):
            hash_to_remove = sorted_entries[i][0]
            del self.memory_cache[hash_to_remove]
            
            # Also remove from disk
            cache_file = self.cache_dir / f"{hash_to_remove}.cache"
            if cache_file.exists():
                cache_file.unlink()
        
        logger.info(f"Evicted {entries_to_remove} old cache entries")
    
    def _save_cache_entry(self, cached_response: CachedResponse):
        """Save cache entry to disk"""
        try:
            cache_file = self.cache_dir / f"{cached_response.query_hash}.cache"
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_response, f)
        except Exception as e:
            logger.error(f"Failed to save cache entry: {e}")
    
    def _load_cache(self):
        """Load cache entries from disk"""
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            loaded_count = 0
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'rb') as f:
                        cached_response = pickle.load(f)
                    
                    # Check if not too old
                    age = datetime.now() - cached_response.timestamp
                    if age.days <= self.max_age_days:
                        self.memory_cache[cached_response.query_hash] = cached_response
                        loaded_count += 1
                    else:
                        # Remove old cache file
                        cache_file.unlink()
                
                except Exception as e:
                    logger.warning(f"Failed to load cache file {cache_file}: {e}")
                    # Remove corrupted file
                    cache_file.unlink()
            
            logger.info(f"Loaded {loaded_count} cache entries from disk")
            
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            'total_queries': self.stats.total_queries,
            'cache_hits': self.stats.cache_hits,
            'cache_misses': self.stats.cache_misses,
            'hit_rate': self.stats.hit_rate,
            'cost_saved': self.stats.cost_saved,
            'cache_size': len(self.memory_cache),
            'max_cache_size': self.max_cache_size,
            'similarity_threshold': self.similarity_threshold
        }
    
    def clear_cache(self):
        """Clear all cached entries"""
        with self._lock:
            self.memory_cache.clear()
            
            # Remove cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            # Reset stats
            self.stats = CacheStats()
            
            logger.info("Cache cleared")


class IntelligentRAGCache:
    """
    Intelligent caching system for RAG responses to reduce LLM costs
    """
    
    def __init__(self, 
                 cache_dir: str = "cache_directory",
                 max_cache_size: int = 1000,
                 similarity_threshold: float = 0.85,
                 max_age_days: int = 30):
        """
        Initialize intelligent cache system
        
        Args:
            cache_dir: Directory to store cache files
            max_cache_size: Maximum number of cached responses
            similarity_threshold: Threshold for query similarity matching
            max_age_days: Maximum age of cached responses in days
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_cache_size = max_cache_size
        self.similarity_threshold = similarity_threshold
        self.max_age_days = max_age_days
        
        # In-memory cache for fast access
        self.memory_cache: Dict[str, CachedResponse] = {}
        
        # Cache statistics
        self.stats = CacheStats()
        
        # Thread lock for cache operations
        self._lock = threading.Lock()
        
        # Load existing cache
        self._load_cache()
        
        logger.info(f"Initialized intelligent cache with {len(self.memory_cache)} entries")
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent matching"""
        # Convert to lowercase and strip whitespace
        normalized = ' '.join(query.lower().strip().split())
        
        # Remove common variations that don't affect meaning
        replacements = {
            'lord krishna': 'krishna',
            'bhagavan': 'krishna',
            'shri krishna': 'krishna',
            'please tell me': '',
            'can you explain': '',
            'what is': '',
            'what does': '',
            'help me understand': ''
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove extra spaces again
        return ' '.join(normalized.split())


# Global cache instance
_cache_instance = None

def get_spiritual_cache() -> SpiritualQueryCache:
    """Get singleton cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SpiritualQueryCache()
    return _cache_instance


def cached_spiritual_response(spiritual_context: str = 'general',
                            cache_enabled: bool = True):
    """
    Decorator for caching spiritual guidance responses
    
    Args:
        spiritual_context: Context for cache grouping
        cache_enabled: Whether caching is enabled
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not cache_enabled:
                return await func(*args, **kwargs)
            
            cache = get_spiritual_cache()
            
            # Extract query from arguments
            query = kwargs.get('query') or (args[0] if args else "")
            
            # Try to get cached response
            cached_result = cache.get_cached_response(query, spiritual_context)
            
            if cached_result:
                logger.info(f"Returning cached response for query: '{query[:50]}...'")
                return cached_result
            
            # Generate new response
            result = await func(*args, **kwargs)
            
            # Cache the result if successful
            if isinstance(result, dict) and 'content' in result and not result.get('error'):
                cache.cache_response(
                    query=query,
                    response_content=result['content'],
                    spiritual_context=spiritual_context,
                    citations=result.get('citations', [])
                )
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not cache_enabled:
                return func(*args, **kwargs)
            
            cache = get_spiritual_cache()
            query = kwargs.get('query') or (args[0] if args else "")
            
            cached_result = cache.get_cached_response(query, spiritual_context)
            if cached_result:
                return cached_result
            
            result = func(*args, **kwargs)
            
            if isinstance(result, dict) and 'content' in result and not result.get('error'):
                cache.cache_response(
                    query=query,
                    response_content=result['content'],
                    spiritual_context=spiritual_context,
                    citations=result.get('citations', [])
                )
            
            return result
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_caching_system():
        print("🕉️ Testing Intelligent Caching System")
        print("=" * 50)
        
        cache = get_spiritual_cache()
        
        # Test caching
        test_query = "What does the Bhagavad Gita say about dharma?"
        context = "dharma"
        
        # First query (cache miss)
        print(f"First query: {test_query}")
        result1 = cache.get_cached_response(test_query, context)
        print(f"Cache result: {result1}")
        
        # Cache a response
        sample_response = "The Bhagavad Gita teaches that dharma is one's righteous duty..."
        sample_citations = [{"source": "Bhagavad Gita", "chapter": "2", "verse": "31"}]
        
        cache.cache_response(
            query=test_query,
            response_content=sample_response,
            spiritual_context=context,
            citations=sample_citations
        )
        
        # Second query (cache hit)
        print(f"\nSecond query (exact): {test_query}")
        result2 = cache.get_cached_response(test_query, context)
        print(f"Cache hit: {result2 is not None}")
        if result2:
            print(f"Content preview: {result2['content'][:50]}...")
        
        # Similar query (cache hit)
        similar_query = "What does Bhagavad Gita teach about dharma?"
        print(f"\nSimilar query: {similar_query}")
        result3 = cache.get_cached_response(similar_query, context)
        print(f"Similar match: {result3 is not None}")
        if result3:
            print(f"Cache type: {result3.get('cache_type')}")
        
        # Get cache statistics
        stats = cache.get_cache_stats()
        print(f"\nCache Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Intelligent caching system working correctly!")
    
    asyncio.run(test_caching_system())
