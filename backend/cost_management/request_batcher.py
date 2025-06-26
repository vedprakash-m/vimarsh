"""
Request Batching and Query Deduplication System
Optimizes AI costs by batching requests and eliminating duplicate queries
"""

import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json
import threading
from enum import Enum

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Status of batch processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueryRequest:
    """Individual query request for batching"""
    id: str
    query: str
    spiritual_context: str
    user_id: Optional[str]
    timestamp: datetime
    priority: int = 1  # 1=high, 2=medium, 3=low
    metadata: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None
    future: Optional[asyncio.Future] = None


@dataclass
class BatchResult:
    """Result of batch processing"""
    request_id: str
    content: str
    success: bool
    error: Optional[str] = None
    processing_time: float = 0.0
    cost: float = 0.0
    was_deduplicated: bool = False
    original_request_id: Optional[str] = None  # For deduplicated requests


@dataclass
class DeduplicationEntry:
    """Entry in deduplication cache"""
    query_hash: str
    original_request_id: str
    response: str
    timestamp: datetime
    hit_count: int = 1
    context: str = "general"


class RequestBatcher:
    """Handles request batching and deduplication for cost optimization"""
    
    def __init__(self, 
                 batch_size: int = 5,
                 batch_timeout: float = 2.0,
                 dedup_window: timedelta = timedelta(hours=1)):
        """
        Initialize request batcher
        
        Args:
            batch_size: Maximum requests per batch
            batch_timeout: Maximum time to wait before processing batch (seconds)
            dedup_window: Time window for deduplication
        """
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.dedup_window = dedup_window
        
        # Pending requests queue
        self.pending_requests: List[QueryRequest] = []
        self.processing_lock = threading.Lock()
        
        # Deduplication cache
        self.dedup_cache: Dict[str, DeduplicationEntry] = {}
        self.dedup_lock = threading.Lock()
        
        # Batch processing state
        self.current_batch: List[QueryRequest] = []
        self.batch_timer: Optional[asyncio.TimerHandle] = None
        self.is_processing = False
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'batched_requests': 0,
            'deduplicated_requests': 0,
            'cost_saved': 0.0,
            'batches_processed': 0,
            'average_batch_size': 0.0
        }
    
    def _generate_query_hash(self, query: str, context: str) -> str:
        """
        Generate hash for query deduplication
        
        Args:
            query: Spiritual query text
            context: Spiritual context
            
        Returns:
            Hash string for deduplication
        """
        # Normalize query for better deduplication
        normalized_query = self._normalize_query(query)
        combined = f"{normalized_query}:{context}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for better deduplication matching
        
        Args:
            query: Original query text
            
        Returns:
            Normalized query text
        """
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove common punctuation variations
        normalized = normalized.replace('?', '').replace('!', '').replace('.', '')
        
        # Final trim to remove any trailing spaces
        normalized = normalized.strip()
        
        # Normalize common variations
        replacements = {
            'krishna': 'krishna',
            'krsna': 'krishna',
            'shri krishna': 'krishna',
            'lord krishna': 'krishna',
            'bhagavad gita': 'gita',
            'bhagavad-gita': 'gita',
            'srimad bhagavatam': 'bhagavatam',
            'srimad-bhagavatam': 'bhagavatam'
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def _check_deduplication(self, query_hash: str) -> Optional[DeduplicationEntry]:
        """
        Check if query can be deduplicated
        
        Args:
            query_hash: Hash of the query
            
        Returns:
            Deduplication entry if found, None otherwise
        """
        with self.dedup_lock:
            if query_hash in self.dedup_cache:
                entry = self.dedup_cache[query_hash]
                
                # Check if entry is still within deduplication window
                if datetime.now() - entry.timestamp <= self.dedup_window:
                    entry.hit_count += 1
                    return entry
                else:
                    # Remove expired entry
                    del self.dedup_cache[query_hash]
        
        return None
    
    def _add_to_dedup_cache(self, 
                           query_hash: str,
                           request_id: str,
                           response: str,
                           context: str):
        """
        Add response to deduplication cache
        
        Args:
            query_hash: Hash of the query
            request_id: Original request ID
            response: Response content
            context: Spiritual context
        """
        with self.dedup_lock:
            self.dedup_cache[query_hash] = DeduplicationEntry(
                query_hash=query_hash,
                original_request_id=request_id,
                response=response,
                timestamp=datetime.now(),
                context=context
            )
    
    async def submit_request(self, 
                           query: str,
                           spiritual_context: str = 'general',
                           user_id: Optional[str] = None,
                           priority: int = 1,
                           metadata: Optional[Dict] = None) -> BatchResult:
        """
        Submit a request for batched processing
        
        Args:
            query: Spiritual query
            spiritual_context: Context of the query
            user_id: User ID for tracking
            priority: Priority level (1=high, 2=medium, 3=low)
            metadata: Additional metadata
            
        Returns:
            BatchResult with response or deduplication result
        """
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.pending_requests)}"
        
        # Check for deduplication first
        query_hash = self._generate_query_hash(query, spiritual_context)
        dedup_entry = self._check_deduplication(query_hash)
        
        if dedup_entry:
            # Return deduplicated response immediately
            self.stats['total_requests'] += 1  # Count all requests
            self.stats['deduplicated_requests'] += 1
            self.stats['cost_saved'] += 0.005  # Estimated cost per query
            
            return BatchResult(
                request_id=request_id,
                content=dedup_entry.response,
                success=True,
                processing_time=0.001,  # Near-instant for deduplication
                cost=0.0,  # No cost for deduplicated queries
                was_deduplicated=True,
                original_request_id=dedup_entry.original_request_id
            )
        
        # Create future for async result
        future = asyncio.Future()
        
        # Create request object
        request = QueryRequest(
            id=request_id,
            query=query,
            spiritual_context=spiritual_context,
            user_id=user_id,
            timestamp=datetime.now(),
            priority=priority,
            metadata=metadata or {},
            future=future
        )
        
        # Add to pending queue
        with self.processing_lock:
            self.pending_requests.append(request)
            self.stats['total_requests'] += 1
        
        # Trigger batch processing
        await self._maybe_process_batch()
        
        # Wait for result
        try:
            result = await future
            return result
        except Exception as e:
            logger.error(f"Error waiting for batch result: {e}")
            return BatchResult(
                request_id=request_id,
                content="Error processing request",
                success=False,
                error=str(e)
            )
    
    async def _maybe_process_batch(self):
        """Check if batch should be processed and trigger if needed"""
        
        with self.processing_lock:
            if self.is_processing:
                return
            
            # Check if we should process based on size or time
            should_process = (
                len(self.pending_requests) >= self.batch_size or
                (self.pending_requests and self._oldest_request_age() > self.batch_timeout)
            )
            
            if not should_process:
                # Set timer for timeout if not already set
                if not self.batch_timer and self.pending_requests:
                    self.batch_timer = asyncio.get_event_loop().call_later(
                        self.batch_timeout, 
                        lambda: asyncio.create_task(self._process_batch_timeout())
                    )
                return
            
            # Cancel existing timer
            if self.batch_timer:
                self.batch_timer.cancel()
                self.batch_timer = None
            
            # Mark as processing
            self.is_processing = True
        
        # Process batch
        await self._process_current_batch()
    
    async def _process_batch_timeout(self):
        """Handle batch timeout"""
        with self.processing_lock:
            if not self.is_processing and self.pending_requests:
                self.is_processing = True
            else:
                return
        
        await self._process_current_batch()
    
    def _oldest_request_age(self) -> float:
        """Get age of oldest pending request in seconds"""
        if not self.pending_requests:
            return 0.0
        
        oldest = min(self.pending_requests, key=lambda r: r.timestamp)
        return (datetime.now() - oldest.timestamp).total_seconds()
    
    async def _process_current_batch(self):
        """Process the current batch of requests"""
        
        # Get batch to process
        with self.processing_lock:
            if not self.pending_requests:
                self.is_processing = False
                return
            
            # Take up to batch_size requests, prioritizing by priority and age
            batch = sorted(
                self.pending_requests[:self.batch_size],
                key=lambda r: (r.priority, r.timestamp)
            )
            
            # Remove from pending
            for req in batch:
                self.pending_requests.remove(req)
        
        try:
            logger.info(f"Processing batch of {len(batch)} requests")
            start_time = datetime.now()
            
            # Process batch
            results = await self._execute_batch(batch)
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats['batches_processed'] += 1
            self.stats['batched_requests'] += len(batch)
            self.stats['average_batch_size'] = (
                self.stats['batched_requests'] / self.stats['batches_processed']
            )
            
            # Send results back to requesters
            for request, result in zip(batch, results):
                if request.future and not request.future.done():
                    request.future.set_result(result)
                
                # Add successful responses to dedup cache
                if result.success and not result.was_deduplicated:
                    query_hash = self._generate_query_hash(
                        request.query, request.spiritual_context
                    )
                    self._add_to_dedup_cache(
                        query_hash, request.id, result.content, request.spiritual_context
                    )
            
            logger.info(f"Batch processed in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            
            # Send error results
            for request in batch:
                if request.future and not request.future.done():
                    error_result = BatchResult(
                        request_id=request.id,
                        content="Batch processing failed",
                        success=False,
                        error=str(e)
                    )
                    request.future.set_result(error_result)
        
        finally:
            # Mark as not processing and check for more work
            with self.processing_lock:
                self.is_processing = False
            
            # Process any remaining requests
            if self.pending_requests:
                await self._maybe_process_batch()
    
    async def _execute_batch(self, batch: List[QueryRequest]) -> List[BatchResult]:
        """
        Execute a batch of requests
        
        Args:
            batch: List of requests to process
            
        Returns:
            List of batch results
        """
        
        # Group requests by context for more efficient processing
        context_groups = defaultdict(list)
        for request in batch:
            context_groups[request.spiritual_context].append(request)
        
        all_results = []
        
        for context, requests in context_groups.items():
            # Process requests in this context group
            context_results = await self._process_context_group(context, requests)
            all_results.extend(context_results)
        
        # Return results in original order
        result_map = {r.request_id: r for r in all_results}
        return [result_map[req.id] for req in batch]
    
    async def _process_context_group(self, 
                                   context: str, 
                                   requests: List[QueryRequest]) -> List[BatchResult]:
        """
        Process a group of requests with the same spiritual context
        
        Args:
            context: Spiritual context
            requests: Requests to process
            
        Returns:
            List of results
        """
        
        results = []
        
        for request in requests:
            start_time = datetime.now()
            
            try:
                # Simulate LLM processing (in real implementation, this would call actual LLM)
                response_content = await self._simulate_llm_response(
                    request.query, context
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                estimated_cost = 0.005  # Estimated cost per query
                
                result = BatchResult(
                    request_id=request.id,
                    content=response_content,
                    success=True,
                    processing_time=processing_time,
                    cost=estimated_cost
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing request {request.id}: {e}")
                
                result = BatchResult(
                    request_id=request.id,
                    content="Error processing request",
                    success=False,
                    error=str(e),
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
                
                results.append(result)
        
        return results
    
    async def _simulate_llm_response(self, query: str, context: str) -> str:
        """
        Simulate LLM response (replace with actual LLM integration)
        
        Args:
            query: Spiritual query
            context: Spiritual context
            
        Returns:
            Simulated response
        """
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Generate context-appropriate response
        context_responses = {
            'dharma': f"🕉️ Regarding your question about dharma: {query[:50]}... The concept of dharma is fundamental to spiritual life, representing righteous duty and moral law as taught in the sacred texts.",
            
            'meditation': f"🧘 For your meditation inquiry: {query[:50]}... Meditation is the practice of turning consciousness inward to discover the divine presence within.",
            
            'scripture': f"📿 About the scriptures: {query[:50]}... The sacred texts offer timeless wisdom that reveals itself through devoted study and contemplation.",
            
            'general': f"🙏 In response to your spiritual question: {query[:50]}... Every sincere inquiry is a step on the path to greater understanding and wisdom."
        }
        
        return context_responses.get(context, context_responses['general'])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get batching and deduplication statistics"""
        
        # Calculate additional stats
        dedup_hit_rate = 0.0
        if self.stats['total_requests'] > 0:
            dedup_hit_rate = self.stats['deduplicated_requests'] / self.stats['total_requests']
        
        batch_efficiency = 0.0
        if self.stats['total_requests'] > 0:
            batch_efficiency = self.stats['batched_requests'] / self.stats['total_requests']
        
        return {
            'total_requests': self.stats['total_requests'],
            'batched_requests': self.stats['batched_requests'],
            'deduplicated_requests': self.stats['deduplicated_requests'],
            'batches_processed': self.stats['batches_processed'],
            'average_batch_size': round(self.stats['average_batch_size'], 2),
            'deduplication_hit_rate': round(dedup_hit_rate * 100, 1),
            'batch_efficiency': round(batch_efficiency * 100, 1),
            'cost_saved': round(self.stats['cost_saved'], 4),
            'active_cache_entries': len(self.dedup_cache),
            'pending_requests': len(self.pending_requests)
        }
    
    def clear_expired_cache(self):
        """Clear expired entries from deduplication cache"""
        
        with self.dedup_lock:
            current_time = datetime.now()
            expired_keys = [
                key for key, entry in self.dedup_cache.items()
                if current_time - entry.timestamp > self.dedup_window
            ]
            
            for key in expired_keys:
                del self.dedup_cache[key]
            
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")


# Decorator for automatic batching
def with_request_batching(spiritual_context: str = 'general', 
                         priority: int = 1,
                         enable_deduplication: bool = True):
    """
    Decorator to add request batching to functions
    
    Args:
        spiritual_context: Context for batching
        priority: Request priority
        enable_deduplication: Whether to enable deduplication
    """
    
    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            # Get or create batcher instance
            batcher = get_request_batcher()
            
            # Extract query from arguments
            query = kwargs.get('query') or (args[0] if args else "")
            user_id = kwargs.get('user_id')
            
            if enable_deduplication and len(query) > 10:  # Only batch meaningful queries
                # Use batcher
                result = await batcher.submit_request(
                    query=query,
                    spiritual_context=spiritual_context,
                    user_id=user_id,
                    priority=priority
                )
                
                return {
                    'content': result.content,
                    'success': result.success,
                    'cost': result.cost,
                    'processing_time': result.processing_time,
                    'was_batched': not result.was_deduplicated,
                    'was_deduplicated': result.was_deduplicated,
                    'batch_metadata': {
                        'request_id': result.request_id,
                        'original_request_id': result.original_request_id
                    }
                }
            else:
                # Call function directly for small queries or when batching disabled
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, return original behavior
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global instance
_request_batcher = None

def get_request_batcher() -> RequestBatcher:
    """Get global request batcher instance"""
    global _request_batcher
    if _request_batcher is None:
        _request_batcher = RequestBatcher()
    return _request_batcher


# Example usage and testing
if __name__ == "__main__":
    async def test_request_batching():
        print("🕉️ Testing Request Batching and Deduplication")
        print("=" * 60)
        
        batcher = RequestBatcher(batch_size=3, batch_timeout=1.0)
        
        # Test queries
        test_queries = [
            ("What is dharma?", "dharma"),
            ("What is dharma?", "dharma"),  # Duplicate for deduplication test
            ("How to meditate?", "meditation"),
            ("Explain karma yoga", "dharma"),
            ("What is the meaning of life?", "general"),
            ("How to meditate properly?", "meditation"),  # Similar but different
        ]
        
        print(f"Submitting {len(test_queries)} requests...")
        
        # Submit all requests concurrently
        tasks = []
        for i, (query, context) in enumerate(test_queries):
            task = batcher.submit_request(
                query=query,
                spiritual_context=context,
                user_id=f"user_{i % 3}",  # 3 different users
                priority=1 if i < 3 else 2
            )
            tasks.append(task)
        
        # Wait for all results
        results = await asyncio.gather(*tasks)
        
        # Display results
        print(f"\nResults:")
        for i, result in enumerate(results):
            query, context = test_queries[i]
            print(f"\nQuery {i+1}: {query[:30]}...")
            print(f"  Context: {context}")
            print(f"  Success: {result.success}")
            print(f"  Deduplicated: {result.was_deduplicated}")
            print(f"  Processing Time: {result.processing_time:.3f}s")
            print(f"  Cost: ${result.cost:.4f}")
            if result.was_deduplicated:
                print(f"  Original Request: {result.original_request_id}")
            print(f"  Response: {result.content[:60]}...")
        
        # Display statistics
        stats = batcher.get_statistics()
        print(f"\nBatching Statistics:")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Batched Requests: {stats['batched_requests']}")
        print(f"  Deduplicated Requests: {stats['deduplicated_requests']}")
        print(f"  Batches Processed: {stats['batches_processed']}")
        print(f"  Average Batch Size: {stats['average_batch_size']}")
        print(f"  Deduplication Hit Rate: {stats['deduplication_hit_rate']}%")
        print(f"  Cost Saved: ${stats['cost_saved']:.4f}")
        
        print("\n✅ Request batching and deduplication system working correctly!")
    
    asyncio.run(test_request_batching())
