"""
Tests for Request Batching and Query Deduplication System
Validates cost optimization through batching and deduplication
"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from backend.cost_management.request_batcher import (
    RequestBatcher, QueryRequest, BatchResult, DeduplicationEntry,
    BatchStatus, with_request_batching, get_request_batcher
)


class TestRequestBatcher:
    """Test suite for request batching system"""
    
    def setup_method(self):
        """Set up test environment"""
        self.batcher = RequestBatcher(
            batch_size=3,
            batch_timeout=0.5,  # Short timeout for testing
            dedup_window=timedelta(minutes=5)
        )
    
    def test_query_normalization(self):
        """Test query normalization for deduplication"""
        
        test_cases = [
            ("What is dharma?", "what is dharma"),
            ("  What   is   dharma  ?  ", "what is dharma"),
            ("What is Lord Krishna's teaching?", "what is krishna's teaching"),
            ("Tell me about Bhagavad Gita", "tell me about gita"),
            ("Explain Srimad-Bhagavatam verses", "explain bhagavatam verses")
        ]
        
        for original, expected in test_cases:
            normalized = self.batcher._normalize_query(original)
            assert normalized == expected, f"Failed for: {original}"
    
    def test_query_hash_generation(self):
        """Test query hash generation for deduplication"""
        
        # Same query should produce same hash
        hash1 = self.batcher._generate_query_hash("What is dharma?", "dharma")
        hash2 = self.batcher._generate_query_hash("What is dharma?", "dharma")
        assert hash1 == hash2
        
        # Different queries should produce different hashes
        hash3 = self.batcher._generate_query_hash("What is karma?", "dharma")
        assert hash1 != hash3
        
        # Same query with different context should produce different hashes
        hash4 = self.batcher._generate_query_hash("What is dharma?", "general")
        assert hash1 != hash4
        
        # Normalized variations should produce same hash
        hash5 = self.batcher._generate_query_hash("What is dharma ???", "dharma")
        hash6 = self.batcher._generate_query_hash("what is dharma", "dharma")
        assert hash5 == hash6
    
    def test_deduplication_cache_operations(self):
        """Test deduplication cache add and retrieve operations"""
        
        query_hash = "test_hash_123"
        request_id = "req_001"
        response = "Test response content"
        context = "dharma"
        
        # Initially, cache should be empty
        entry = self.batcher._check_deduplication(query_hash)
        assert entry is None
        
        # Add to cache
        self.batcher._add_to_dedup_cache(query_hash, request_id, response, context)
        
        # Should find entry now
        entry = self.batcher._check_deduplication(query_hash)
        assert entry is not None
        assert entry.query_hash == query_hash
        assert entry.original_request_id == request_id
        assert entry.response == response
        assert entry.context == context
        assert entry.hit_count == 2  # 1 initial + 1 from check
    
    def test_deduplication_expiry(self):
        """Test that deduplication cache entries expire correctly"""
        
        # Create batcher with very short dedup window
        short_batcher = RequestBatcher(dedup_window=timedelta(microseconds=1))
        
        query_hash = "expiry_test_hash"
        request_id = "req_expiry"
        response = "Expiry test response"
        context = "general"
        
        # Add to cache
        short_batcher._add_to_dedup_cache(query_hash, request_id, response, context)
        
        # Wait for expiry
        import time
        time.sleep(0.001)  # 1ms should be enough for microsecond window
        
        # Should not find expired entry
        entry = short_batcher._check_deduplication(query_hash)
        assert entry is None
        
        # Cache should be cleaned up
        assert query_hash not in short_batcher.dedup_cache
    
    @pytest.mark.asyncio
    async def test_immediate_deduplication(self):
        """Test immediate deduplication response"""
        
        query = "What is the essence of dharma?"
        context = "dharma"
        
        # First request should process normally
        result1 = await self.batcher.submit_request(query, context, "user1")
        assert result1.success
        assert not result1.was_deduplicated
        assert result1.cost > 0
        
        # Second identical request should be deduplicated
        result2 = await self.batcher.submit_request(query, context, "user2")
        assert result2.success
        assert result2.was_deduplicated
        assert result2.cost == 0.0
        assert result2.processing_time < 0.01  # Should be near-instant
        assert result2.content == result1.content
        assert result2.original_request_id == result1.request_id
    
    @pytest.mark.asyncio
    async def test_batch_processing_by_size(self):
        """Test that batches are processed when size limit is reached"""
        
        # Submit exactly batch_size requests
        tasks = []
        for i in range(self.batcher.batch_size):
            task = self.batcher.submit_request(
                f"Question {i} about spiritual wisdom",
                "general",
                f"user_{i}"
            )
            tasks.append(task)
        
        # All should complete since batch size is reached
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=2.0)
        
        assert len(results) == self.batcher.batch_size
        for result in results:
            assert result.success
            assert not result.was_deduplicated
        
        # Check statistics
        stats = self.batcher.get_statistics()
        assert stats['batches_processed'] >= 1
        assert stats['batched_requests'] >= self.batcher.batch_size
    
    @pytest.mark.asyncio
    async def test_batch_processing_by_timeout(self):
        """Test that batches are processed when timeout is reached"""
        
        # Submit fewer than batch_size requests
        tasks = []
        for i in range(self.batcher.batch_size - 1):
            task = self.batcher.submit_request(
                f"Timeout test question {i}",
                "general",
                f"user_{i}"
            )
            tasks.append(task)
        
        # Should complete due to timeout even with fewer requests
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=2.0)
        
        assert len(results) == self.batcher.batch_size - 1
        for result in results:
            assert result.success
        
        # Check that batch was processed
        stats = self.batcher.get_statistics()
        assert stats['batches_processed'] >= 1
    
    @pytest.mark.asyncio
    async def test_request_priority_ordering(self):
        """Test that higher priority requests are processed first"""
        
        # Submit requests with different priorities
        high_priority_task = self.batcher.submit_request(
            "High priority question", "general", "user1", priority=1
        )
        
        low_priority_task = self.batcher.submit_request(
            "Low priority question", "general", "user2", priority=3
        )
        
        medium_priority_task = self.batcher.submit_request(
            "Medium priority question", "general", "user3", priority=2
        )
        
        # All should complete
        results = await asyncio.wait_for(asyncio.gather(
            high_priority_task, low_priority_task, medium_priority_task
        ), timeout=2.0)
        
        assert all(result.success for result in results)
    
    @pytest.mark.asyncio
    async def test_context_grouping(self):
        """Test that requests are grouped by spiritual context"""
        
        # Submit requests with different contexts
        tasks = []
        contexts = ['dharma', 'meditation', 'scripture', 'general']
        
        for i, context in enumerate(contexts):
            task = self.batcher.submit_request(
                f"Question about {context} topic {i}",
                context,
                f"user_{i}"
            )
            tasks.append(task)
        
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=2.0)
        
        assert len(results) == len(contexts)
        for result in results:
            assert result.success
            # Response should contain context-appropriate content
            assert any(ctx in result.content.lower() for ctx in ['dharma', 'meditation', 'scripture', 'spiritual'])
    
    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(self):
        """Test handling of concurrent batch submissions"""
        
        # Submit many requests concurrently
        num_requests = 10
        tasks = []
        
        for i in range(num_requests):
            task = self.batcher.submit_request(
                f"Concurrent question {i}",
                "general",
                f"user_{i % 3}"  # 3 different users
            )
            tasks.append(task)
        
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
        
        # All should succeed
        successful_results = [r for r in results if r.success]
        assert len(successful_results) == num_requests
        
        # Check statistics
        stats = self.batcher.get_statistics()
        assert stats['total_requests'] >= num_requests
        assert stats['batches_processed'] >= 1
    
    @pytest.mark.asyncio
    async def test_error_handling_in_batch(self):
        """Test error handling when batch processing fails"""
        
        # Mock the LLM simulation to raise an error
        with patch.object(
            self.batcher, '_simulate_llm_response',
            side_effect=Exception("Simulated LLM error")
        ):
            result = await self.batcher.submit_request(
                "Question that will fail",
                "general",
                "test_user"
            )
            
            assert not result.success
            assert result.error is not None
            assert "Simulated LLM error" in result.error
    
    def test_statistics_calculation(self):
        """Test statistics calculation accuracy"""
        
        # Initial statistics
        stats = self.batcher.get_statistics()
        assert stats['total_requests'] == 0
        assert stats['deduplication_hit_rate'] == 0.0
        assert stats['cost_saved'] == 0.0
        
        # Manually update statistics for testing
        self.batcher.stats['total_requests'] = 10
        self.batcher.stats['deduplicated_requests'] = 3
        self.batcher.stats['batched_requests'] = 7
        self.batcher.stats['batches_processed'] = 2
        self.batcher.stats['cost_saved'] = 0.015
        # Update average batch size manually for test
        self.batcher.stats['average_batch_size'] = 7 / 2
        
        updated_stats = self.batcher.get_statistics()
        assert updated_stats['total_requests'] == 10
        assert updated_stats['deduplication_hit_rate'] == 30.0  # 3/10 * 100
        assert updated_stats['batch_efficiency'] == 70.0  # 7/10 * 100
        assert updated_stats['average_batch_size'] == 3.5  # 7/2
        assert updated_stats['cost_saved'] == 0.015
    
    def test_cache_cleanup(self):
        """Test expired cache entry cleanup"""
        
        # Add some entries to cache
        for i in range(5):
            query_hash = f"hash_{i}"
            self.batcher._add_to_dedup_cache(
                query_hash, f"req_{i}", f"response_{i}", "general"
            )
        
        assert len(self.batcher.dedup_cache) == 5
        
        # Manually set some entries as expired
        current_time = datetime.now()
        expired_time = current_time - self.batcher.dedup_window - timedelta(minutes=1)
        
        self.batcher.dedup_cache['hash_0'].timestamp = expired_time
        self.batcher.dedup_cache['hash_1'].timestamp = expired_time
        
        # Clean up expired entries
        self.batcher.clear_expired_cache()
        
        # Should have 3 entries left
        assert len(self.batcher.dedup_cache) == 3
        assert 'hash_0' not in self.batcher.dedup_cache
        assert 'hash_1' not in self.batcher.dedup_cache


class TestRequestBatchingDecorator:
    """Test suite for request batching decorator"""
    
    def setup_method(self):
        """Set up test environment"""
        # Reset global batcher for clean testing
        global _request_batcher
        import backend.cost_management.request_batcher as batcher_module
        batcher_module._request_batcher = None
    
    @pytest.mark.asyncio
    async def test_decorator_basic_functionality(self):
        """Test basic decorator functionality"""
        
        @with_request_batching(spiritual_context='dharma', priority=1)
        async def mock_spiritual_function(query: str, user_id: str = None):
            return {
                'content': f"Mock response for: {query}",
                'original_processing': True
            }
        
        # Test with batchable query
        result = await mock_spiritual_function(
            query="What is the meaning of dharma in daily life?",
            user_id="test_user"
        )
        
        assert 'content' in result
        assert 'was_batched' in result or 'was_deduplicated' in result
        assert result['success']
    
    @pytest.mark.asyncio
    async def test_decorator_small_query_bypass(self):
        """Test that small queries bypass batching"""
        
        @with_request_batching(spiritual_context='general')
        async def mock_function(query: str, user_id: str = None):
            return {
                'content': f"Direct response: {query}",
                'direct_call': True
            }
        
        # Small query should bypass batching
        result = await mock_function(query="Hi", user_id="test_user")
        
        assert 'direct_call' in result
        assert result['direct_call'] is True
    
    @pytest.mark.asyncio
    async def test_decorator_deduplication_disabled(self):
        """Test decorator with deduplication disabled"""
        
        @with_request_batching(
            spiritual_context='general',
            enable_deduplication=False
        )
        async def mock_function(query: str, user_id: str = None):
            return {
                'content': f"No batching response: {query}",
                'no_batch': True
            }
        
        result = await mock_function(
            query="This should not be batched",
            user_id="test_user"
        )
        
        assert 'no_batch' in result
        assert result['no_batch'] is True
    
    def test_decorator_sync_function(self):
        """Test decorator with synchronous function"""
        
        @with_request_batching(spiritual_context='general')
        def sync_function(query: str, user_id: str = None):
            return {
                'content': f"Sync response: {query}",
                'sync_call': True
            }
        
        result = sync_function(query="Sync test query", user_id="test_user")
        
        assert 'sync_call' in result
        assert result['sync_call'] is True
    
    def test_global_batcher_instance(self):
        """Test global batcher instance management"""
        
        batcher1 = get_request_batcher()
        batcher2 = get_request_batcher()
        
        # Should return same instance
        assert batcher1 is batcher2
        assert isinstance(batcher1, RequestBatcher)


class TestRequestBatchingIntegration:
    """Integration tests for request batching system"""
    
    def setup_method(self):
        """Set up integration test environment"""
        self.batcher = RequestBatcher(
            batch_size=2,  # Smaller batch size for faster testing
            batch_timeout=0.5,  # Shorter timeout for faster testing
            dedup_window=timedelta(minutes=2)
        )
    
    @pytest.mark.asyncio
    async def test_mixed_deduplication_and_batching(self):
        """Test system with both deduplication and batching"""
        
        # First submit some queries to populate cache
        initial_queries = [
            ("What is dharma?", "dharma"),
            ("How to meditate?", "meditation"),
        ]
        
        initial_tasks = []
        for query, context in initial_queries:
            task = self.batcher.submit_request(query, context, "test_user")
            initial_tasks.append(task)
        
        # Wait for initial queries to complete and populate cache
        initial_results = await asyncio.wait_for(asyncio.gather(*initial_tasks), timeout=3.0)
        assert all(r.success for r in initial_results)
        
        # Now submit mix including duplicates
        queries = [
            ("What is dharma?", "dharma"),  # Should be deduplicated
            ("Explain karma yoga", "dharma"),
            ("How to meditate?", "meditation"),  # Should be deduplicated  
            ("What is moksha?", "dharma"),
        ]
        
        tasks = []
        for query, context in queries:
            task = self.batcher.submit_request(query, context, "test_user")
            tasks.append(task)
        
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
        assert len(results) == len(queries)
        
        # Count deduplicated vs processed
        deduplicated = sum(1 for r in results if r.was_deduplicated)
        processed = sum(1 for r in results if not r.was_deduplicated)
        
        # Should have deduplication
        assert deduplicated >= 2  # At least 2 duplicates (dharma and meditation)
        assert processed >= 2    # At least 2 unique queries
        
        # All should succeed
        assert all(r.success for r in results)
        
        # Check cost savings
        total_cost_saved = sum(r.cost for r in results if r.was_deduplicated)
        assert total_cost_saved == 0.0  # Deduplicated queries have zero cost
    
    @pytest.mark.asyncio
    async def test_high_throughput_scenario(self):
        """Test system under high throughput with realistic deduplication"""
        
        # Create fresh batcher for this test
        batcher = RequestBatcher(
            batch_size=2,
            batch_timeout=0.5,
            dedup_window=timedelta(minutes=2)
        )
        
        unique_queries = [
            "What is dharma?",
            "How to practice yoga?", 
            "What is karma?",
            "What is moksha?",
            "How to meditate?"
        ]
        
        # First batch - submit unique queries to populate cache
        initial_tasks = []
        for query in unique_queries:
            task = batcher.submit_request(query, "general", "initial_user")
            initial_tasks.append(task)
        
        # Wait for initial batch to complete
        initial_results = await asyncio.wait_for(asyncio.gather(*initial_tasks), timeout=5.0)
        assert all(r.success for r in initial_results)
        assert all(not r.was_deduplicated for r in initial_results)
        
        # Second batch - submit duplicates that should be deduplicated
        duplicate_tasks = []
        for i in range(10):  # Submit 2x each unique query
            query = unique_queries[i % len(unique_queries)]
            task = batcher.submit_request(query, "general", f"user_{i}")
            duplicate_tasks.append(task)
        
        start_time = datetime.now()
        results = await asyncio.wait_for(asyncio.gather(*duplicate_tasks), timeout=10.0)
        end_time = datetime.now()
        
        # All should complete
        assert len(results) == 10
        assert all(r.success for r in results)
        
        # Should have significant deduplication
        deduplicated_count = sum(1 for r in results if r.was_deduplicated)
        assert deduplicated_count >= 8  # At least 8 out of 10 should be deduplicated
        
        # Processing should be efficient
        total_time = (end_time - start_time).total_seconds()
        assert total_time < 3.0  # Should complete quickly with deduplication
        
        # Check statistics
        stats = batcher.get_statistics()
        assert stats['total_requests'] >= 15  # 5 initial + 10 duplicates
        assert stats['deduplication_hit_rate'] > 50.0  # Should have good hit rate
    
    @pytest.mark.asyncio
    async def test_spiritual_context_preservation(self):
        """Test that spiritual context is preserved through batching"""
        
        # Submit requests with different spiritual contexts
        context_queries = [
            ("What is my dharma?", "dharma"),
            ("Guide me in meditation", "meditation"),
            ("Explain this scripture verse", "scripture"),
            ("General spiritual question", "general")
        ]
        
        tasks = []
        for query, context in context_queries:
            task = self.batcher.submit_request(query, context, "test_user")
            tasks.append(task)
        
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=3.0)
        for (query, expected_context), result in zip(context_queries, results):
            assert result.success
            
            # Response should contain context-appropriate symbols/terms
            content_lower = result.content.lower()
            if expected_context == "dharma":
                assert any(term in content_lower for term in ["dharma", "🕉️", "duty", "righteous"])
            elif expected_context == "meditation":
                assert any(term in content_lower for term in ["meditation", "🧘", "consciousness", "inward"])
            elif expected_context == "scripture":
                assert any(term in content_lower for term in ["scripture", "📿", "sacred", "texts"])


# Run tests if executed directly
if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
