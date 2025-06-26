"""
Tests for Dynamic Fallback Mechanisms
Validates all fallback strategies and budget constraint handling
"""

import asyncio
import pytest
import tempfile
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path

# Import the dynamic fallback modules
from backend.cost_management.dynamic_fallback import (
    DynamicFallbackManager, FallbackStrategy, FallbackResponse, with_dynamic_fallback
)
from backend.cost_management.token_tracker import TokenUsageTracker
from backend.cost_management.budget_validator import BudgetValidator
from backend.cost_management.intelligent_cache import SpiritualQueryCache


class TestDynamicFallbackManager:
    """Test suite for dynamic fallback mechanisms"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create isolated instances for testing
        self.tracker = TokenUsageTracker(storage_path=self.temp_dir)
        self.cache = SpiritualQueryCache(cache_dir=self.temp_dir)
        self.validator = BudgetValidator()
        self.validator.tracker = self.tracker
        
        self.fallback_manager = DynamicFallbackManager()
        self.fallback_manager.tracker = self.tracker
        self.fallback_manager.validator = self.validator
        self.fallback_manager.cache = self.cache
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_cache_only_fallback_hit(self):
        """Test cache-only fallback when cache hit is available"""
        
        # Pre-cache a response
        query = "What is dharma in Hinduism?"
        cached_content = "Dharma is righteous duty and moral law..."
        self.cache.cache_response(query, cached_content, "dharma")
        
        # Test cache-only fallback
        budget_status = {'daily_percentage': 95, 'within_limits': False}
        
        fallback_result = await self.fallback_manager._cache_only_fallback(
            query, "dharma", budget_status
        )
        
        assert fallback_result is not None
        assert fallback_result.strategy_used == FallbackStrategy.CACHE_ONLY
        assert fallback_result.content == cached_content
        assert fallback_result.cost_saved > 0
        assert fallback_result.quality_score >= 0.8  # High quality from cache
    
    @pytest.mark.asyncio
    async def test_cache_only_fallback_miss(self):
        """Test cache-only fallback when no cache hit"""
        
        query = "What is the meaning of moksha?"
        budget_status = {'daily_percentage': 95, 'within_limits': False}
        
        fallback_result = await self.fallback_manager._cache_only_fallback(
            query, "general", budget_status
        )
        
        assert fallback_result is None  # No cache hit available
    
    @pytest.mark.asyncio
    async def test_model_downgrade_fallback(self):
        """Test model downgrade fallback strategy"""
        
        query = "Explain the philosophy of karma yoga"
        budget_status = {'daily_percentage': 85, 'within_limits': True}
        
        fallback_result = await self.fallback_manager._model_downgrade_fallback(
            query, "dharma", "test_user", budget_status
        )
        
        assert fallback_result is not None
        assert fallback_result.strategy_used == FallbackStrategy.MODEL_DOWNGRADE
        assert fallback_result.content is not None
        assert fallback_result.cost_saved > 0
        assert 0.7 <= fallback_result.quality_score <= 0.9  # Good but not perfect quality
        assert 'gemini-flash' in fallback_result.metadata['model_used']
    
    @pytest.mark.asyncio
    async def test_local_processing_fallback(self):
        """Test local processing fallback strategy"""
        
        query = "What is dharma according to Krishna?"  # Should match keyword
        budget_status = {'daily_percentage': 98, 'within_limits': False}
        
        fallback_result = await self.fallback_manager._local_processing_fallback(
            query, "dharma", budget_status
        )
        
        assert fallback_result is not None
        assert fallback_result.strategy_used == FallbackStrategy.LOCAL_PROCESSING
        assert "dharma" in fallback_result.content.lower()
        assert fallback_result.cost_saved > 0
        assert fallback_result.quality_score >= 0.5  # Moderate quality
    
    @pytest.mark.asyncio
    async def test_local_processing_no_keywords(self):
        """Test local processing when no keywords match"""
        
        query = "Complex philosophical question with rare terminology"
        budget_status = {'daily_percentage': 98, 'within_limits': False}
        
        fallback_result = await self.fallback_manager._local_processing_fallback(
            query, "general", budget_status
        )
        
        assert fallback_result is None  # No keyword matches
    
    @pytest.mark.asyncio
    async def test_simplified_response_fallback(self):
        """Test simplified response fallback strategy"""
        
        query = "Complex question about advanced spiritual practices"
        budget_status = {'daily_percentage': 95, 'within_limits': False}
        
        fallback_result = await self.fallback_manager._simplified_response_fallback(
            query, "meditation", budget_status
        )
        
        assert fallback_result is not None
        assert fallback_result.strategy_used == FallbackStrategy.SIMPLIFIED_RESPONSE
        assert "meditation" in fallback_result.content.lower() or "🧘" in fallback_result.content
        assert fallback_result.cost_saved > 0
        assert fallback_result.quality_score >= 0.3  # Basic but helpful
    
    @pytest.mark.asyncio
    async def test_deferred_processing_fallback(self):
        """Test deferred processing fallback strategy"""
        
        query = "Deep spiritual inquiry requiring detailed response"
        budget_status = {'daily_percentage': 98, 'within_limits': False}
        
        fallback_result = await self.fallback_manager._deferred_processing_fallback(
            query, "scripture", "test_user", budget_status
        )
        
        assert fallback_result is not None
        assert fallback_result.strategy_used == FallbackStrategy.DEFERRED_PROCESSING
        assert "queued" in fallback_result.content.lower() or "later" in fallback_result.content.lower() or "saved" in fallback_result.content.lower()
        assert fallback_result.cost_saved > 0
        assert fallback_result.quality_score >= 0.2  # Promise of future response
        assert 'queued_at' in fallback_result.metadata
    
    @pytest.mark.asyncio
    async def test_graceful_denial_fallback(self):
        """Test graceful denial fallback strategy"""
        
        query = "Any spiritual question"
        budget_status = {'daily_percentage': 99, 'within_limits': False}
        
        fallback_result = await self.fallback_manager._graceful_denial_fallback(
            query, "general", budget_status
        )
        
        assert fallback_result is not None
        assert fallback_result.strategy_used == FallbackStrategy.GRACEFUL_DENIAL
        assert "namaste" in fallback_result.content.lower()
        assert "99%" in fallback_result.content  # Should mention budget percentage
        assert fallback_result.cost_saved > 0
        assert fallback_result.quality_score >= 0.1  # Honest response
    
    @pytest.mark.asyncio
    async def test_execute_fallback_priority_order(self):
        """Test that fallback strategies are tried in priority order"""
        
        # Test with high budget usage but cache available
        query = "What is dharma?"
        self.cache.cache_response(query, "Cached dharma response", "dharma")
        
        budget_status = {'daily_percentage': 96, 'within_limits': False}
        
        fallback_result = await self.fallback_manager.execute_fallback(
            query, "dharma", "test_user", budget_status
        )
        
        # Should use cache first (highest priority)
        assert fallback_result.strategy_used == FallbackStrategy.CACHE_ONLY
        assert fallback_result.content == "Cached dharma response"
    
    @pytest.mark.asyncio
    async def test_execute_fallback_no_cache_available(self):
        """Test fallback execution when cache is not available"""
        
        query = "What is the purpose of meditation in spiritual practice?"
        budget_status = {'daily_percentage': 85, 'within_limits': True}  # Moderate usage
        
        fallback_result = await self.fallback_manager.execute_fallback(
            query, "meditation", "test_user", budget_status
        )
        
        # Should try model downgrade since budget allows cheaper model
        assert fallback_result.strategy_used == FallbackStrategy.MODEL_DOWNGRADE
        assert fallback_result.content is not None
        assert fallback_result.cost_saved > 0
    
    @pytest.mark.asyncio
    async def test_execute_fallback_extreme_budget_constraint(self):
        """Test fallback execution under extreme budget constraints"""
        
        query = "Complex spiritual inquiry"
        budget_status = {'daily_percentage': 99, 'within_limits': False}
        
        fallback_result = await self.fallback_manager.execute_fallback(
            query, "general", "test_user", budget_status
        )
        
        # Should fall through to graceful denial or simplified response
        assert fallback_result.strategy_used in [
            FallbackStrategy.SIMPLIFIED_RESPONSE,
            FallbackStrategy.DEFERRED_PROCESSING,
            FallbackStrategy.GRACEFUL_DENIAL
        ]
        assert fallback_result.content is not None
        assert fallback_result.cost_saved > 0
    
    @pytest.mark.asyncio
    async def test_keyword_matching_accuracy(self):
        """Test accuracy of local keyword matching"""
        
        test_queries = [
            ("What is dharma?", "dharma"),
            ("Explain karma to me", "karma"),
            ("How to practice meditation?", "meditation"),
            ("Tell me about Lord Krishna", "krishna"),
            ("What does the Gita say?", "gita"),
            ("Explain yoga philosophy", "yoga")
        ]
        
        for query, expected_keyword in test_queries:
            response = await self.fallback_manager._generate_local_response(query, "general")
            assert response is not None
            assert expected_keyword in response.lower()
    
    @pytest.mark.asyncio
    async def test_spiritual_context_handling(self):
        """Test handling of different spiritual contexts"""
        
        contexts = ["dharma", "meditation", "scripture", "general"]
        query = "Spiritual guidance question"
        budget_status = {'daily_percentage': 95, 'within_limits': False}
        
        for context in contexts:
            fallback_result = await self.fallback_manager._simplified_response_fallback(
                query, context, budget_status
            )
            
            assert fallback_result is not None
            assert fallback_result.strategy_used == FallbackStrategy.SIMPLIFIED_RESPONSE
            # Response should be contextually appropriate
            if context == "dharma":
                assert ("dharma" in fallback_result.content.lower() or 
                       "🕉️" in fallback_result.content)
            elif context == "meditation":
                assert ("meditation" in fallback_result.content.lower() or 
                       "🧘" in fallback_result.content)
    
    def test_fallback_response_structure(self):
        """Test FallbackResponse data structure"""
        
        response = FallbackResponse(
            content="Test response",
            strategy_used=FallbackStrategy.CACHE_ONLY,
            original_request="Test query",
            fallback_reason="Test reason",
            cost_saved=0.005,
            quality_score=0.8
        )
        
        assert response.content == "Test response"
        assert response.strategy_used == FallbackStrategy.CACHE_ONLY
        assert response.cost_saved == 0.005
        assert response.quality_score == 0.8
        assert response.citations == []  # Default empty list
        assert response.metadata == {}   # Default empty dict
    
    def test_citation_extraction(self):
        """Test basic citation extraction by context"""
        
        dharma_citations = self.fallback_manager._extract_basic_citations("dharma")
        assert len(dharma_citations) > 0
        assert "Bhagavad Gita" in dharma_citations[0]["source"]
        
        meditation_citations = self.fallback_manager._extract_basic_citations("meditation")
        assert len(meditation_citations) > 0
        assert "Patanjali" in meditation_citations[0]["source"]
        
        general_citations = self.fallback_manager._extract_basic_citations("general")
        assert len(general_citations) > 0
    
    def test_fallback_statistics_structure(self):
        """Test fallback statistics structure"""
        
        stats = self.fallback_manager.get_fallback_statistics()
        
        assert 'total_fallbacks' in stats
        assert 'strategies_used' in stats
        assert 'cost_saved' in stats
        assert 'average_quality_score' in stats
        
        # All strategies should be represented
        for strategy in FallbackStrategy:
            assert strategy.value in stats['strategies_used']


class TestDynamicFallbackDecorator:
    """Test suite for the dynamic fallback decorator"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_decorator_normal_operation(self):
        """Test decorator when function operates normally"""
        
        @with_dynamic_fallback(spiritual_context='dharma')
        async def mock_spiritual_function(query: str, user_id: str = None):
            return {
                'content': f"Normal response to: {query}",
                'citations': [],
                'usage': {'model_name': 'gemini-pro', 'input_tokens': 100, 'output_tokens': 200}
            }
        
        result = await mock_spiritual_function("What is dharma?", user_id="test_user")
        
        assert 'content' in result
        assert result['content'].startswith("Normal response to:")
        assert 'fallback_used' not in result  # No fallback needed
    
    @pytest.mark.asyncio
    async def test_decorator_budget_exceeded(self):
        """Test decorator when budget is exceeded"""
        
        @with_dynamic_fallback(spiritual_context='dharma')
        async def mock_budget_exceeded_function(query: str, user_id: str = None):
            return {
                'error': 'budget_exceeded',
                'budget_status': {'daily_percentage': 98, 'within_limits': False}
            }
        
        result = await mock_budget_exceeded_function("What is dharma?", user_id="test_user")
        
        assert 'fallback_used' in result
        assert result['fallback_used'] is True
        assert 'fallback_strategy' in result
        assert 'content' in result
        assert result['content'] is not None
    
    @pytest.mark.asyncio
    async def test_decorator_exception_handling(self):
        """Test decorator exception handling"""
        
        @with_dynamic_fallback(spiritual_context='general')
        async def mock_failing_function(query: str, user_id: str = None):
            raise Exception("Simulated function failure")
        
        result = await mock_failing_function("Test query", user_id="test_user")
        
        assert 'fallback_used' in result
        assert result['fallback_used'] is True
        assert result['fallback_strategy'] == 'emergency'
        assert 'error' in result
        assert 'content' in result
        assert ("unable to provide a response" in result['content'].lower() or 
                "managing resource usage" in result['content'].lower())
    
    def test_decorator_sync_function(self):
        """Test decorator with synchronous functions"""
        
        @with_dynamic_fallback(spiritual_context='general')
        def mock_sync_function(query: str):
            return {'content': f"Sync response: {query}"}
        
        result = mock_sync_function("Test query")
        
        assert 'content' in result
        assert result['content'] == "Sync response: Test query"
    
    def test_decorator_sync_function_exception(self):
        """Test decorator with failing synchronous function"""
        
        @with_dynamic_fallback(spiritual_context='general')
        def mock_failing_sync_function(query: str):
            raise Exception("Sync function failure")
        
        result = mock_failing_sync_function("Test query")
        
        assert 'fallback_used' in result
        assert result['fallback_used'] is True
        assert result['fallback_strategy'] == 'emergency_sync'
        assert 'error' in result


class TestIntegratedFallbackSystem:
    """Integration tests for the complete fallback system"""
    
    def setup_method(self):
        """Set up integrated test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create data directory for queue files
        Path(self.temp_dir + "/cost_tracking").mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_fallback_workflow(self):
        """Test complete fallback workflow under various conditions"""
        
        fallback_manager = DynamicFallbackManager()
        
        # Scenario 1: Low budget usage - should allow normal operation with downgrade
        result1 = await fallback_manager.execute_fallback(
            query="What is the essence of dharma?",
            spiritual_context="dharma",
            user_id="user1",
            budget_status={'daily_percentage': 75, 'within_limits': True}
        )
        
        assert result1.strategy_used == FallbackStrategy.MODEL_DOWNGRADE
        assert result1.quality_score >= 0.8
        
        # Scenario 2: High budget usage - should use fallback strategies
        result2 = await fallback_manager.execute_fallback(
            query="Explain the philosophy of karma yoga",
            spiritual_context="dharma", 
            user_id="user2",
            budget_status={'daily_percentage': 97, 'within_limits': False}
        )
        
        assert result2.strategy_used in [
            FallbackStrategy.LOCAL_PROCESSING,
            FallbackStrategy.SIMPLIFIED_RESPONSE,
            FallbackStrategy.DEFERRED_PROCESSING,
            FallbackStrategy.GRACEFUL_DENIAL
        ]
        assert result2.cost_saved > 0
    
    @pytest.mark.asyncio 
    async def test_fallback_queue_persistence(self):
        """Test that deferred queries are properly queued"""
        
        # Override data directory for testing
        original_queue_file = "data/cost_tracking/deferred_queries.jsonl"
        test_queue_file = f"{self.temp_dir}/cost_tracking/deferred_queries.jsonl"
        
        fallback_manager = DynamicFallbackManager()
        
        # Patch the queue file path
        import backend.cost_management.dynamic_fallback as fallback_module
        original_method = fallback_manager._queue_for_later_processing
        
        async def test_queue_method(query, context, user_id):
            queue_item = {
                'query': query,
                'spiritual_context': context,
                'user_id': user_id,
                'queued_at': datetime.now().isoformat(),
                'priority': 'normal'
            }
            
            with open(test_queue_file, 'a') as f:
                f.write(json.dumps(queue_item) + '\n')
        
        fallback_manager._queue_for_later_processing = test_queue_method
        
        # Test deferred processing
        result = await fallback_manager._deferred_processing_fallback(
            query="Complex spiritual question",
            spiritual_context="scripture",
            user_id="test_user",
            budget_status={'daily_percentage': 98, 'within_limits': False}
        )
        
        assert result.strategy_used == FallbackStrategy.DEFERRED_PROCESSING
        
        # Verify queue file was created and contains the query
        assert Path(test_queue_file).exists()
        
        with open(test_queue_file, 'r') as f:
            queue_data = json.loads(f.readline())
            assert queue_data['query'] == "Complex spiritual question"
            assert queue_data['spiritual_context'] == "scripture"
            assert queue_data['user_id'] == "test_user"
    
    @pytest.mark.asyncio
    async def test_fallback_with_cache_integration(self):
        """Test fallback system integration with cache"""
        
        fallback_manager = DynamicFallbackManager()
        
        # Pre-populate cache
        cache_query = "What is meditation according to yogic traditions?"
        cache_response = "Meditation is the practice of sustained awareness..."
        fallback_manager.cache.cache_response(cache_query, cache_response, "meditation")
        
        # Test fallback with cache hit
        result = await fallback_manager.execute_fallback(
            query=cache_query,
            spiritual_context="meditation",
            user_id="test_user",
            budget_status={'daily_percentage': 95, 'within_limits': False}
        )
        
        assert result.strategy_used == FallbackStrategy.CACHE_ONLY
        assert result.content == cache_response
        assert result.quality_score >= 0.8  # High quality from cache
        assert result.cost_saved > 0
    
    @pytest.mark.asyncio
    async def test_quality_score_consistency(self):
        """Test that quality scores are consistent across strategies"""
        
        fallback_manager = DynamicFallbackManager()
        query = "Spiritual guidance question"
        budget_status = {'daily_percentage': 90, 'within_limits': False}
        
        # Test different strategies and verify quality scores are reasonable
        strategies_to_test = [
            (fallback_manager._simplified_response_fallback, 0.3, 0.5),
            (fallback_manager._local_processing_fallback, 0.5, 0.7),
            (fallback_manager._graceful_denial_fallback, 0.1, 0.3)
        ]
        
        for strategy_func, min_quality, max_quality in strategies_to_test:
            if strategy_func == fallback_manager._local_processing_fallback:
                # Use a query with keywords for local processing
                test_query = "What is dharma in Hindu philosophy?"
            else:
                test_query = query
            
            if strategy_func == fallback_manager._graceful_denial_fallback:
                result = await strategy_func(test_query, "general", budget_status)
            else:
                result = await strategy_func(test_query, "general", budget_status)
            
            if result:  # Some strategies might return None
                assert min_quality <= result.quality_score <= max_quality
                assert result.cost_saved >= 0


# Run tests if executed directly
if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
