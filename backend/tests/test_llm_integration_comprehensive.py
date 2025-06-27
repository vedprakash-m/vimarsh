"""
Comprehensive LLM Integration Tests for Vimarsh AI Agent

This module provides comprehensive testing for the LLM integration layer,
focusing on the Gemini Pro client, error handling, and spiritual content generation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any

from llm.gemini_client import (
    GeminiProClient, SafetyLevel, SpiritualContext,
    SpiritualGuidanceRequest, SpiritualGuidanceResponse
)
from tests.fixtures import SAMPLE_KRISHNA_RESPONSES, SAMPLE_USER_QUERIES


class TestGeminiProClient:
    """Test the Gemini Pro LLM client implementation."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.client = GeminiProClient(api_key="test_key")
        self.mock_responses = SAMPLE_KRISHNA_RESPONSES
        
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initializes correctly."""
        assert self.client.api_key == "test_key"
        assert self.client.safety_level == SafetyLevel.STRICT
        assert self.client.model_name == "gemini-pro"
        
    @pytest.mark.asyncio
    async def test_spiritual_guidance_generation(self):
        """Test basic spiritual guidance generation."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "O Arjuna, perform your duty without attachment to results..."
            mock_response.candidates = [Mock(safety_ratings=[])]
            mock_generate.return_value = mock_response
            
            request = SpiritualGuidanceRequest(
                query="What is dharma?",
                context="Personal guidance",
                language="English"
            )
            
            response = await self.client.generate_spiritual_guidance(request)
            
            assert isinstance(response, SpiritualGuidanceResponse)
            assert "Arjuna" in response.response
            assert response.language == "English"
            
    @pytest.mark.asyncio
    async def test_error_handling_api_failure(self):
        """Test error handling for API failures."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            request = SpiritualGuidanceRequest(
                query="Test query",
                context="Test context",
                language="English"
            )
            
            response = await self.client.generate_spiritual_guidance(request)
            
            assert response.error is not None
            assert "error" in response.response.lower()
            
    @pytest.mark.asyncio
    async def test_safety_filtering(self):
        """Test safety filtering functionality."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = None  # Blocked content
            mock_response.candidates = [Mock(safety_ratings=[
                Mock(category="HARM_CATEGORY_HARASSMENT", probability="HIGH")
            ])]
            mock_generate.return_value = mock_response
            
            request = SpiritualGuidanceRequest(
                query="Inappropriate query",
                context="Test context",
                language="English"
            )
            
            response = await self.client.generate_spiritual_guidance(request)
            
            assert response.safety_blocked is True
            assert "appropriate" in response.response.lower()
            
    @pytest.mark.asyncio
    async def test_multilingual_support(self):
        """Test multilingual response generation."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "हे अर्जुन, अपने धर्म का पालन करो..."
            mock_response.candidates = [Mock(safety_ratings=[])]
            mock_generate.return_value = mock_response
            
            request = SpiritualGuidanceRequest(
                query="धर्म क्या है?",
                context="व्यक्तिगत मार्गदर्शन",
                language="Hindi"
            )
            
            response = await self.client.generate_spiritual_guidance(request)
            
            assert response.language == "Hindi"
            assert "अर्जुन" in response.response
            
    @pytest.mark.asyncio
    async def test_token_usage_tracking(self):
        """Test token usage tracking."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            with patch('llm.gemini_client.track_llm_usage') as mock_track:
                mock_response = Mock()
                mock_response.text = "Test response"
                mock_response.candidates = [Mock(safety_ratings=[])]
                mock_response.usage_metadata = Mock(
                    prompt_token_count=100,
                    candidates_token_count=50,
                    total_token_count=150
                )
                mock_generate.return_value = mock_response
                
                request = SpiritualGuidanceRequest(
                    query="Test query",
                    context="Test context",
                    language="English"
                )
                
                await self.client.generate_spiritual_guidance(request)
                
                mock_track.assert_called_once()
                args = mock_track.call_args[1]
                assert args['input_tokens'] == 100
                assert args['output_tokens'] == 50
                
    def test_safety_level_configuration(self):
        """Test safety level configuration."""
        # Test strict safety
        strict_client = GeminiProClient(api_key="test", safety_level=SafetyLevel.STRICT)
        assert strict_client.safety_level == SafetyLevel.STRICT
        
        # Test moderate safety
        moderate_client = GeminiProClient(api_key="test", safety_level=SafetyLevel.MODERATE)
        assert moderate_client.safety_level == SafetyLevel.MODERATE
        
    def test_spiritual_context_handling(self):
        """Test spiritual context enum handling."""
        contexts = [
            SpiritualContext.GUIDANCE,
            SpiritualContext.TEACHING,
            SpiritualContext.MEDITATION,
            SpiritualContext.PERSONAL_GROWTH
        ]
        
        for context in contexts:
            assert isinstance(context.value, str)
            assert len(context.value) > 0


class TestLLMIntegrationWorkflow:
    """Test end-to-end LLM integration workflows."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.client = GeminiProClient(api_key="test_key")
        
    @pytest.mark.asyncio
    async def test_complete_guidance_workflow(self):
        """Test complete spiritual guidance workflow."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = SAMPLE_KRISHNA_RESPONSES["dharma_modern"]["response"]
            mock_response.candidates = [Mock(safety_ratings=[])]
            mock_response.usage_metadata = Mock(
                prompt_token_count=200,
                candidates_token_count=100,
                total_token_count=300
            )
            mock_generate.return_value = mock_response
            
            # Test the complete workflow
            request = SpiritualGuidanceRequest(
                query=SAMPLE_USER_QUERIES["dharma_modern"]["query"],
                context="Personal guidance seeking",
                language="English",
                retrieved_chunks=["Sample Bhagavad Gita verse..."]
            )
            
            response = await self.client.generate_spiritual_guidance(request)
            
            assert response.success is True
            assert len(response.response) > 100
            assert response.token_usage.total > 0
            assert response.processing_time > 0
            
    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test batch processing of multiple requests."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Spiritual guidance response"
            mock_response.candidates = [Mock(safety_ratings=[])]
            mock_response.usage_metadata = Mock(
                prompt_token_count=50,
                candidates_token_count=25,
                total_token_count=75
            )
            mock_generate.return_value = mock_response
            
            requests = [
                SpiritualGuidanceRequest(
                    query=f"Query {i}",
                    context="Test context",
                    language="English"
                ) for i in range(3)
            ]
            
            responses = []
            for request in requests:
                response = await self.client.generate_spiritual_guidance(request)
                responses.append(response)
                
            assert len(responses) == 3
            assert all(r.success for r in responses)
            
    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self):
        """Test rate limiting error handling."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            # Simulate rate limiting error
            mock_generate.side_effect = Exception("Rate limit exceeded")
            
            request = SpiritualGuidanceRequest(
                query="Test query",
                context="Test context",
                language="English"
            )
            
            response = await self.client.generate_spiritual_guidance(request)
            
            assert response.success is False
            assert "rate limit" in response.response.lower() or "try again" in response.response.lower()


class TestLLMPerformance:
    """Test LLM performance and optimization."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.client = GeminiProClient(api_key="test_key")
        
    @pytest.mark.asyncio
    async def test_response_time_performance(self):
        """Test response time performance."""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Quick response"
            mock_response.candidates = [Mock(safety_ratings=[])]
            mock_generate.return_value = mock_response
            
            request = SpiritualGuidanceRequest(
                query="Quick question",
                context="Test",
                language="English"
            )
            
            import time
            start_time = time.time()
            response = await self.client.generate_spiritual_guidance(request)
            end_time = time.time()
            
            # Response should be processed quickly (mock should be fast)
            assert end_time - start_time < 1.0
            assert response.processing_time > 0
            
    def test_prompt_optimization(self):
        """Test prompt optimization for different contexts."""
        # Test different prompt configurations
        contexts = [
            SpiritualContext.GUIDANCE,
            SpiritualContext.TEACHING,
            SpiritualContext.MEDITATION
        ]
        
        for context in contexts:
            prompt = self.client._build_spiritual_prompt(
                query="Test query",
                context=context.value,
                language="English"
            )
            
            assert "Krishna" in prompt
            assert "Bhagavad Gita" in prompt
            assert context.value.lower() in prompt.lower()
            
    def test_token_estimation(self):
        """Test token estimation accuracy."""
        test_texts = [
            "Short text",
            "Medium length text with more words and concepts to test estimation",
            "Very long text with extensive spiritual content discussing dharma, karma, moksha, and various philosophical concepts from the Bhagavad Gita and other sacred texts"
        ]
        
        for text in test_texts:
            estimated = self.client._estimate_tokens(text)
            assert estimated > 0
            assert isinstance(estimated, int)
            # Basic sanity check - longer text should have more tokens
            if len(text) > 100:
                assert estimated > 10
