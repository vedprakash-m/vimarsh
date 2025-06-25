"""
Test Suite for LLM Fallback System in Vimarsh AI Agent

Comprehensive tests covering all fallback strategies, error scenarios,
and system robustness for spiritual guidance delivery.
"""

import asyncio
import json
import pytest
import pytest_asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import the system under test
try:
    from .llm_fallback import (
        LLMFallbackSystem, SpiritualQuery, FallbackResponse,
        FallbackStrategy, FallbackTrigger, TemplatePattern
    )
    from .error_classifier import ErrorCategory, ErrorSeverity
except ImportError:
    from llm_fallback import (
        LLMFallbackSystem, SpiritualQuery, FallbackResponse,
        FallbackStrategy, FallbackTrigger, TemplatePattern
    )
    from error_classifier import ErrorCategory, ErrorSeverity


class TestLLMFallbackSystem:
    """Test cases for the LLM Fallback System"""
    
    @pytest_asyncio.fixture
    async def fallback_system(self):
        """Create a fallback system for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = LLMFallbackSystem(
                templates_path=f"{temp_dir}/templates",
                cache_path=f"{temp_dir}/cache",
                enable_external_llm=True
            )
            yield system
    
    @pytest.fixture
    def sample_query(self):
        """Create a sample spiritual query"""
        return SpiritualQuery(
            text="I am struggling with my dharma. How should I act in this difficult situation?",
            language="en",
            context={"topic": "dharma", "difficulty": "high"},
            user_id="test_user_123",
            session_id="session_456"
        )
    
    @pytest.fixture
    def hindi_query(self):
        """Create a Hindi spiritual query"""
        return SpiritualQuery(
            text="मैं अपने धर्म को लेकर संघर्ष कर रहा हूं। मुझे क्या करना चाहिए?",
            language="hi",
            user_id="test_user_456"
        )
    
    # Core System Tests
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, fallback_system):
        """Test that the fallback system initializes properly"""
        assert fallback_system is not None
        assert len(fallback_system.template_patterns) > 0
        assert len(fallback_system.spiritual_content) > 0
        assert fallback_system.templates_path.exists()
        assert fallback_system.cache_path.exists()
    
    @pytest.mark.asyncio
    async def test_fallback_strategies_determination(self, fallback_system, sample_query):
        """Test strategy determination for different failure types"""
        
        # Test LLM timeout
        strategies = fallback_system._determine_fallback_strategies(
            FallbackTrigger.LLM_TIMEOUT, sample_query
        )
        assert FallbackStrategy.CACHED_RESPONSES in strategies
        assert FallbackStrategy.TEMPLATE_RESPONSES in strategies
        
        # Test safety violation
        strategies = fallback_system._determine_fallback_strategies(
            FallbackTrigger.SAFETY_VIOLATION, sample_query
        )
        assert FallbackStrategy.TEMPLATE_RESPONSES in strategies
        assert FallbackStrategy.HUMAN_ESCALATION in strategies
        
        # Test rate limit
        strategies = fallback_system._determine_fallback_strategies(
            FallbackTrigger.RATE_LIMIT, sample_query
        )
        assert FallbackStrategy.CACHED_RESPONSES in strategies
        assert FallbackStrategy.EXTERNAL_LLM in strategies
    
    @pytest.mark.asyncio
    async def test_strategy_availability_checks(self, fallback_system):
        """Test strategy availability checks"""
        
        # These should always be available
        assert fallback_system._is_strategy_available(FallbackStrategy.SIMPLIFIED_REASONING)
        assert fallback_system._is_strategy_available(FallbackStrategy.HUMAN_ESCALATION)
        assert fallback_system._is_strategy_available(FallbackStrategy.MEDITATION_GUIDANCE)
        
        # These depend on data/config
        assert fallback_system._is_strategy_available(FallbackStrategy.TEMPLATE_RESPONSES)
        assert fallback_system._is_strategy_available(FallbackStrategy.EDUCATIONAL_CONTENT)
        
        # External LLM depends on configuration
        assert fallback_system._is_strategy_available(FallbackStrategy.EXTERNAL_LLM) == fallback_system.enable_external_llm
    
    # Template Response Tests
    
    @pytest.mark.asyncio
    async def test_template_response_dharma_query(self, fallback_system, sample_query):
        """Test template response for dharma-related queries"""
        response = await fallback_system._handle_template_responses(
            sample_query, FallbackTrigger.LLM_ERROR
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.TEMPLATE_RESPONSES
        assert response.confidence > 0.5
        assert "dharma" in response.content.lower()
        assert len(response.citations) > 0
        assert "template_id" in response.metadata
    
    @pytest.mark.asyncio
    async def test_template_response_suffering_query(self, fallback_system):
        """Test template response for suffering/comfort queries"""
        suffering_query = SpiritualQuery(
            text="I am going through so much pain and suffering. Please help me.",
            language="en"
        )
        
        response = await fallback_system._handle_template_responses(
            suffering_query, FallbackTrigger.LLM_TIMEOUT
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.TEMPLATE_RESPONSES
        assert "suffering" in response.content.lower() or "pain" in response.content.lower()
        assert response.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_template_response_no_match(self, fallback_system):
        """Test template response when no patterns match"""
        random_query = SpiritualQuery(
            text="What is the weather like today?",
            language="en"
        )
        
        response = await fallback_system._handle_template_responses(
            random_query, FallbackTrigger.LLM_ERROR
        )
        
        # Should return None when no templates match
        assert response is None
    
    # Cached Response Tests
    
    @pytest.mark.asyncio
    async def test_cache_and_retrieve_response(self, fallback_system, sample_query):
        """Test caching and retrieving responses"""
        
        # Cache a response
        test_response = "This is a test response about dharma and spiritual duty."
        await fallback_system.cache_successful_response(
            query=sample_query.text,
            response=test_response,
            language=sample_query.language,
            confidence=0.9,
            citations=["Bhagavad Gita 3.8"]
        )
        
        # Retrieve cached response
        response = await fallback_system._handle_cached_responses(
            sample_query, FallbackTrigger.LLM_TIMEOUT
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.CACHED_RESPONSES
        assert response.content == test_response
        assert response.confidence == 0.9
        assert "Bhagavad Gita 3.8" in response.citations
        assert response.metadata['cache_hit'] == 'exact'
    
    @pytest.mark.asyncio
    async def test_cache_similar_response(self, fallback_system):
        """Test retrieving similar cached responses"""
        
        # Cache a response about dharma
        await fallback_system.cache_successful_response(
            query="What is my dharma in life?",
            response="Your dharma is your righteous path in life...",
            language="en",
            confidence=0.8
        )
        
        # Query with similar but different wording
        similar_query = SpiritualQuery(
            text="How do I find my dharma and duty?",
            language="en"
        )
        
        response = await fallback_system._handle_cached_responses(
            similar_query, FallbackTrigger.RATE_LIMIT
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.CACHED_RESPONSES
        assert response.metadata['cache_hit'] == 'similar'
        assert 'similarity_score' in response.metadata
        assert response.confidence < 0.8  # Reduced confidence for similar match
    
    @pytest.mark.asyncio
    async def test_cache_no_match(self, fallback_system):
        """Test cache when no matching responses exist"""
        unrelated_query = SpiritualQuery(
            text="What should I eat for breakfast?",
            language="en"
        )
        
        response = await fallback_system._handle_cached_responses(
            unrelated_query, FallbackTrigger.LLM_ERROR
        )
        
        assert response is None
    
    # Simplified Reasoning Tests
    
    @pytest.mark.asyncio
    async def test_simplified_reasoning_soul_concept(self, fallback_system):
        """Test simplified reasoning for soul-related queries"""
        soul_query = SpiritualQuery(
            text="What is the nature of the soul and its eternal existence?",
            language="en"
        )
        
        response = await fallback_system._handle_simplified_reasoning(
            soul_query, FallbackTrigger.INVALID_RESPONSE
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.SIMPLIFIED_REASONING
        assert "soul" in response.content.lower()
        assert "eternal" in response.content.lower()
        assert response.confidence == 0.6
        assert 'concepts_identified' in response.metadata
        assert "soul" in response.metadata['concepts_identified']
    
    @pytest.mark.asyncio
    async def test_simplified_reasoning_karma_concept(self, fallback_system):
        """Test simplified reasoning for karma-related queries"""
        karma_query = SpiritualQuery(
            text="How does karma affect my actions and their consequences?",
            language="en"
        )
        
        response = await fallback_system._handle_simplified_reasoning(
            karma_query, FallbackTrigger.LLM_ERROR
        )
        
        assert response is not None
        assert "karma" in response.content.lower()
        assert "action" in response.content.lower()
        assert "karma" in response.metadata['concepts_identified']
    
    @pytest.mark.asyncio
    async def test_simplified_reasoning_no_concepts(self, fallback_system):
        """Test simplified reasoning when no spiritual concepts are identified"""
        random_query = SpiritualQuery(
            text="What is the best programming language?",
            language="en"
        )
        
        response = await fallback_system._handle_simplified_reasoning(
            random_query, FallbackTrigger.LLM_TIMEOUT
        )
        
        assert response is None
    
    # Educational Content Tests
    
    @pytest.mark.asyncio
    async def test_educational_content_wisdom(self, fallback_system):
        """Test educational content for wisdom queries"""
        wisdom_query = SpiritualQuery(
            text="I seek wisdom and understanding about life's meaning.",
            language="en"
        )
        
        response = await fallback_system._handle_educational_content(
            wisdom_query, FallbackTrigger.SERVICE_UNAVAILABLE
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.EDUCATIONAL_CONTENT
        assert response.confidence == 0.7
        assert len(response.citations) > 0
        assert response.metadata['content_category'] == 'wisdom'
        assert "wisdom" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_educational_content_dharma(self, fallback_system, sample_query):
        """Test educational content for dharma queries"""
        response = await fallback_system._handle_educational_content(
            sample_query, FallbackTrigger.NETWORK_ERROR
        )
        
        assert response is not None
        assert response.metadata['content_category'] == 'dharma'
        assert "dharma" in response.content.lower()
    
    # Meditation Guidance Tests
    
    @pytest.mark.asyncio
    async def test_meditation_guidance_calming(self, fallback_system):
        """Test calming meditation guidance"""
        anxiety_query = SpiritualQuery(
            text="I am feeling very anxious and stressed. Please help me find peace.",
            language="en"
        )
        
        response = await fallback_system._handle_meditation_guidance(
            anxiety_query, FallbackTrigger.LLM_TIMEOUT
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.MEDITATION_GUIDANCE
        assert response.confidence == 0.8
        assert response.metadata['guidance_type'] == 'calming'
        assert "peace" in response.content.lower() or "calm" in response.content.lower()
        assert "Om Shanti" in response.content
    
    @pytest.mark.asyncio
    async def test_meditation_guidance_devotional(self, fallback_system):
        """Test devotional meditation guidance"""
        devotion_query = SpiritualQuery(
            text="I want to deepen my love and devotion to Krishna.",
            language="en"
        )
        
        response = await fallback_system._handle_meditation_guidance(
            devotion_query, FallbackTrigger.RATE_LIMIT
        )
        
        assert response is not None
        assert response.metadata['guidance_type'] == 'devotional'
        assert "Krishna" in response.content
        assert "devotion" in response.content.lower() or "love" in response.content.lower()
        assert "Hare Krishna" in response.content
    
    @pytest.mark.asyncio
    async def test_meditation_guidance_concentration(self, fallback_system):
        """Test concentration meditation guidance"""
        focus_query = SpiritualQuery(
            text="I have trouble concentrating during meditation. Help me focus better.",
            language="en"
        )
        
        response = await fallback_system._handle_meditation_guidance(
            focus_query, FallbackTrigger.INVALID_RESPONSE
        )
        
        assert response is not None
        assert response.metadata['guidance_type'] == 'concentration'
        assert "focus" in response.content.lower() or "concentration" in response.content.lower()
        assert "breath" in response.content.lower()
    
    # Human Escalation Tests
    
    @pytest.mark.asyncio
    async def test_human_escalation_english(self, fallback_system, sample_query):
        """Test human escalation for English queries"""
        response = await fallback_system._handle_human_escalation(
            sample_query, FallbackTrigger.SAFETY_VIOLATION
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.HUMAN_ESCALATION
        assert response.confidence == 0.9
        assert response.escalation_required is True
        assert 'escalation_id' in response.metadata
        assert response.metadata['escalation_id'].startswith('ESC-')
        assert "24-48 hours" in response.content
        assert "🙏" in response.content
    
    @pytest.mark.asyncio
    async def test_human_escalation_hindi(self, fallback_system, hindi_query):
        """Test human escalation for Hindi queries"""
        response = await fallback_system._handle_human_escalation(
            hindi_query, FallbackTrigger.LLM_ERROR
        )
        
        assert response is not None
        assert response.escalation_required is True
        assert "विद्वानों" in response.content  # "scholars" in Hindi
        assert "24-48" in response.content
    
    # External LLM Tests
    
    @pytest.mark.asyncio
    async def test_external_llm_enabled(self, fallback_system, sample_query):
        """Test external LLM fallback when enabled"""
        response = await fallback_system._handle_external_llm(
            sample_query, FallbackTrigger.LLM_ERROR
        )
        
        assert response is not None
        assert response.strategy == FallbackStrategy.EXTERNAL_LLM
        assert response.confidence == 0.7
        assert "Krishna" in response.content
        assert "Bhagavad Gita" in response.citations
        assert response.metadata['simulated'] is True
    
    @pytest.mark.asyncio
    async def test_external_llm_disabled(self):
        """Test external LLM fallback when disabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = LLMFallbackSystem(
                templates_path=f"{temp_dir}/templates",
                cache_path=f"{temp_dir}/cache",
                enable_external_llm=False
            )
            
            query = SpiritualQuery(text="Test query", language="en")
            response = await system._handle_external_llm(
                query, FallbackTrigger.LLM_ERROR
            )
            
            assert response is None
    
    # Integration Tests
    
    @pytest.mark.asyncio
    async def test_full_fallback_workflow_success(self, fallback_system, sample_query):
        """Test complete fallback workflow with successful strategy"""
        response = await fallback_system.get_fallback_response(
            sample_query, FallbackTrigger.LLM_TIMEOUT
        )
        
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert response.strategy in [s for s in FallbackStrategy]
        assert response.confidence > 0.0
        assert response.fallback_reason == "LLM failure: llm_timeout"
    
    @pytest.mark.asyncio
    async def test_full_fallback_workflow_all_strategies_fail(self, fallback_system):
        """Test fallback workflow when all strategies fail"""
        # Create a system with minimal resources to force failures
        with tempfile.TemporaryDirectory() as temp_dir:
            minimal_system = LLMFallbackSystem(
                templates_path=f"{temp_dir}/templates",
                cache_path=f"{temp_dir}/cache",
                enable_external_llm=False
            )
            # Clear all templates and content to force failures
            minimal_system.template_patterns.clear()
            minimal_system.spiritual_content.clear()
            
            query = SpiritualQuery(text="Random question", language="en")
            
            # Mock all strategy handlers to fail
            with patch.object(minimal_system, '_handle_cached_responses', return_value=None), \
                 patch.object(minimal_system, '_handle_template_responses', return_value=None), \
                 patch.object(minimal_system, '_handle_simplified_reasoning', return_value=None), \
                 patch.object(minimal_system, '_handle_educational_content', return_value=None), \
                 patch.object(minimal_system, '_handle_meditation_guidance', return_value=None):
                
                response = await minimal_system.get_fallback_response(
                    query, FallbackTrigger.LLM_ERROR
                )
                
                # Should fall back to generic response
                assert response is not None
                assert "temporary difficulty" in response.content.lower()
                assert response.confidence == 0.5
                assert response.metadata['response_type'] == 'generic'
    
    @pytest.mark.asyncio
    async def test_emergency_response(self, fallback_system, sample_query):
        """Test emergency response when everything fails"""
        response = fallback_system._emergency_response(sample_query)
        
        assert response is not None
        assert response.strategy == FallbackStrategy.TEMPLATE_RESPONSES
        assert response.confidence == 0.3
        assert response.escalation_required is True
        assert response.metadata['response_type'] == 'emergency'
        assert "technical difficulties" in response.content.lower()
        assert "🙏" in response.content
    
    # Statistics and Monitoring Tests
    
    @pytest.mark.asyncio
    async def test_fallback_statistics_tracking(self, fallback_system, sample_query):
        """Test fallback statistics tracking"""
        # Generate some fallback responses to create statistics
        await fallback_system.get_fallback_response(sample_query, FallbackTrigger.LLM_TIMEOUT)
        await fallback_system.get_fallback_response(sample_query, FallbackTrigger.RATE_LIMIT)
        await fallback_system.get_fallback_response(sample_query, FallbackTrigger.LLM_TIMEOUT)
        
        stats = await fallback_system.get_fallback_statistics()
        
        assert 'total_fallbacks' in stats
        assert stats['total_fallbacks'] >= 3
        assert 'fallback_reasons' in stats
        assert 'llm_timeout' in stats['fallback_reasons']
        assert stats['fallback_reasons']['llm_timeout'] >= 2
        assert 'rate_limit' in stats['fallback_reasons']
        assert stats['fallback_reasons']['rate_limit'] >= 1
        assert 'cached_responses' in stats
        assert 'template_patterns' in stats
        assert 'strategies_available' in stats
    
    # Cache Management Tests
    
    @pytest.mark.asyncio
    async def test_cache_persistence(self, fallback_system, sample_query):
        """Test cache persistence to disk"""
        # Cache multiple responses
        for i in range(5):
            await fallback_system.cache_successful_response(
                query=f"Test query {i}",
                response=f"Test response {i}",
                language="en",
                confidence=0.8
            )
        
        # Force save
        await fallback_system._save_cache()
        
        # Verify cache file exists and contains data
        cache_file = fallback_system.cache_path / "responses.json"
        assert cache_file.exists()
        
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)
            assert len(cached_data) >= 5
    
    @pytest.mark.asyncio
    async def test_cache_cleanup(self, fallback_system):
        """Test cleanup of old cached responses"""
        # Add some old cached responses
        old_time = (datetime.now() - timedelta(days=35)).isoformat()
        recent_time = datetime.now().isoformat()
        
        fallback_system.cached_responses.update({
            'old_key_1': {'content': 'Old response 1', 'timestamp': old_time},
            'old_key_2': {'content': 'Old response 2', 'timestamp': old_time},
            'recent_key': {'content': 'Recent response', 'timestamp': recent_time}
        })
        
        initial_count = len(fallback_system.cached_responses)
        
        # Cleanup cache older than 30 days
        await fallback_system.cleanup_old_cache(max_age_days=30)
        
        # Should have removed old entries but kept recent ones
        assert len(fallback_system.cached_responses) < initial_count
        assert 'recent_key' in fallback_system.cached_responses
        assert 'old_key_1' not in fallback_system.cached_responses
        assert 'old_key_2' not in fallback_system.cached_responses
    
    # Edge Cases and Error Handling
    
    @pytest.mark.asyncio
    async def test_invalid_language_handling(self, fallback_system):
        """Test handling of invalid language codes"""
        invalid_query = SpiritualQuery(
            text="Test query",
            language="xyz"  # Invalid language code
        )
        
        response = await fallback_system.get_fallback_response(
            invalid_query, FallbackTrigger.LLM_ERROR
        )
        
        # Should still provide a response (likely in English)
        assert response is not None
        assert len(response.content) > 0
    
    @pytest.mark.asyncio
    async def test_empty_query_handling(self, fallback_system):
        """Test handling of empty queries"""
        empty_query = SpiritualQuery(text="", language="en")
        
        response = await fallback_system.get_fallback_response(
            empty_query, FallbackTrigger.INVALID_RESPONSE
        )
        
        assert response is not None
        assert len(response.content) > 0
    
    @pytest.mark.asyncio
    async def test_very_long_query_handling(self, fallback_system):
        """Test handling of very long queries"""
        long_text = "This is a very long spiritual question about dharma and karma. " * 100
        long_query = SpiritualQuery(text=long_text, language="en")
        
        response = await fallback_system.get_fallback_response(
            long_query, FallbackTrigger.LLM_TIMEOUT
        )
        
        assert response is not None
        assert len(response.content) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_fallback_requests(self, fallback_system):
        """Test handling of concurrent fallback requests"""
        queries = [
            SpiritualQuery(text=f"Question {i} about spiritual guidance", language="en")
            for i in range(10)
        ]
        
        # Make concurrent requests
        tasks = [
            fallback_system.get_fallback_response(query, FallbackTrigger.LLM_ERROR)
            for query in queries
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert len(responses) == 10
        for response in responses:
            assert response is not None
            assert len(response.content) > 0
    
    # Utility Function Tests
    
    def test_cache_key_generation(self, fallback_system):
        """Test cache key generation consistency"""
        query1 = "What is my dharma?"
        query2 = "what   is  my   dharma?   "  # Different spacing
        query3 = "What is my karma?"  # Different content
        
        key1 = fallback_system._generate_cache_key(query1, "en")
        key2 = fallback_system._generate_cache_key(query2, "en")
        key3 = fallback_system._generate_cache_key(query3, "en")
        
        # Similar queries should have same key
        assert key1 == key2
        # Different queries should have different keys
        assert key1 != key3
        
        # Different languages should have different keys
        key_en = fallback_system._generate_cache_key(query1, "en")
        key_hi = fallback_system._generate_cache_key(query1, "hi")
        assert key_en != key_hi
    
    def test_spiritual_concept_extraction(self, fallback_system):
        """Test extraction of spiritual concepts from queries"""
        
        # Test dharma concept
        dharma_query = "I need guidance about my dharma and duty in life"
        concepts = fallback_system._extract_spiritual_concepts(dharma_query)
        assert "dharma" in concepts
        
        # Test karma concept
        karma_query = "How does karma affect my actions?"
        concepts = fallback_system._extract_spiritual_concepts(karma_query)
        assert "karma" in concepts
        
        # Test soul concept
        soul_query = "What is the nature of the eternal soul?"
        concepts = fallback_system._extract_spiritual_concepts(soul_query)
        assert "soul" in concepts
        
        # Test devotion concept
        devotion_query = "I want to develop bhakti and devotion"
        concepts = fallback_system._extract_spiritual_concepts(devotion_query)
        assert "devotion" in concepts
        
        # Test multiple concepts
        complex_query = "How does my dharma relate to karma and the soul's journey?"
        concepts = fallback_system._extract_spiritual_concepts(complex_query)
        assert "dharma" in concepts
        assert "karma" in concepts
        assert "soul" in concepts
    
    def test_template_pattern_matching(self, fallback_system):
        """Test template pattern matching logic"""
        
        # Test dharma pattern matching
        dharma_query = "I have questions about my moral duty and righteousness"
        matches = fallback_system._find_matching_templates(dharma_query, "en")
        dharma_matches = [m for m in matches if m.pattern_id == "dharma_questions"]
        assert len(dharma_matches) > 0
        
        # Test suffering pattern matching
        suffering_query = "I am experiencing great pain and difficulty"
        matches = fallback_system._find_matching_templates(suffering_query, "en")
        comfort_matches = [m for m in matches if m.pattern_id == "suffering_comfort"]
        assert len(comfort_matches) > 0
        
        # Test no match scenario
        random_query = "What is the weather forecast?"
        matches = fallback_system._find_matching_templates(random_query, "en")
        assert len(matches) == 0


if __name__ == "__main__":
    """Run the test suite"""
    import sys
    
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    print("Running LLM Fallback System tests...")
    
    # Run async tests
    async def run_async_tests():
        """Run async test cases manually for demonstration"""
        
        print("\n1. Testing system initialization...")
        with tempfile.TemporaryDirectory() as temp_dir:
            system = LLMFallbackSystem(
                templates_path=f"{temp_dir}/templates",
                cache_path=f"{temp_dir}/cache",
                enable_external_llm=True
            )
            print(f"✓ System initialized with {len(system.template_patterns)} templates")
            print(f"✓ Spiritual content loaded: {list(system.spiritual_content.keys())}")
        
        print("\n2. Testing template response generation...")
        query = SpiritualQuery(
            text="I am struggling with my dharma. How should I act?",
            language="en"
        )
        
        response = await system._handle_template_responses(query, FallbackTrigger.LLM_ERROR)
        if response:
            print(f"✓ Template response generated:")
            print(f"   Strategy: {response.strategy.value}")
            print(f"   Confidence: {response.confidence}")
            print(f"   Content preview: {response.content[:100]}...")
            print(f"   Citations: {response.citations}")
        
        print("\n3. Testing meditation guidance...")
        anxiety_query = SpiritualQuery(
            text="I am feeling very anxious and stressed. Please help me find peace.",
            language="en"
        )
        
        meditation_response = await system._handle_meditation_guidance(
            anxiety_query, FallbackTrigger.LLM_TIMEOUT
        )
        if meditation_response:
            print(f"✓ Meditation guidance generated:")
            print(f"   Type: {meditation_response.metadata.get('guidance_type')}")
            print(f"   Content preview: {meditation_response.content[:150]}...")
        
        print("\n4. Testing full fallback workflow...")
        full_response = await system.get_fallback_response(
            query, FallbackTrigger.RATE_LIMIT
        )
        
        print(f"✓ Full fallback response:")
        print(f"   Strategy: {full_response.strategy.value}")
        print(f"   Confidence: {full_response.confidence}")
        print(f"   Fallback reason: {full_response.fallback_reason}")
        print(f"   Content length: {len(full_response.content)} characters")
        
        print("\n5. Testing statistics...")
        stats = await system.get_fallback_statistics()
        print(f"✓ Fallback statistics:")
        print(f"   Total fallbacks: {stats['total_fallbacks']}")
        print(f"   Cached responses: {stats['cached_responses']}")
        print(f"   Template patterns: {stats['template_patterns']}")
        print(f"   Available strategies: {sum(stats['strategies_available'].values())}")
        
        print("\n6. Testing cache functionality...")
        await system.cache_successful_response(
            query="What is the purpose of life?",
            response="The purpose of life is to realize your true divine nature...",
            language="en",
            confidence=0.9
        )
        
        cached_query = SpiritualQuery(text="What is the purpose of life?", language="en")
        cached_response = await system._handle_cached_responses(
            cached_query, FallbackTrigger.LLM_TIMEOUT
        )
        
        if cached_response:
            print(f"✓ Cache functionality working:")
            print(f"   Cache hit type: {cached_response.metadata['cache_hit']}")
            print(f"   Response confidence: {cached_response.confidence}")
        
        print("\n✅ All fallback system tests completed successfully!")
    
    # Run the async tests
    asyncio.run(run_async_tests())
