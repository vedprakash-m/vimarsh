"""
Comprehensive unit tests for LLM integration components.

Tests the Gemini Pro client, prompt engineering, response validation,
and safety filtering systems.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
import time

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm.gemini_client import GeminiProClient
from llm.prompt_engineer import LordKrishnaPersona
from llm.response_validator import SpiritualResponseValidator
from llm.content_moderator import SpiritualContentModerator
from tests.fixtures import (
    SAMPLE_USER_QUERIES, SAMPLE_KRISHNA_RESPONSES, ERROR_TEST_SCENARIOS,
    PERFORMANCE_BENCHMARKS, AUTHENTICITY_MARKERS, SAMPLE_BHAGAVAD_GITA_VERSES
)


class TestGeminiProClient:
    """Test suite for GeminiProClient class."""
    
    @pytest.fixture
    def gemini_client(self):
        """Create GeminiProClient instance for testing."""
        return GeminiProClient(api_key="test_api_key")
    
    @pytest.fixture
    def mock_genai(self):
        """Mock the Google GenAI library."""
        with patch('llm.gemini_client.genai') as mock:
            yield mock
    
    def test_client_initialization(self, gemini_client):
        """Test client initialization."""
        assert gemini_client is not None
        assert hasattr(gemini_client, 'api_key')
        assert hasattr(gemini_client, 'model_name')
        assert hasattr(gemini_client, 'safety_settings')
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, gemini_client, mock_genai):
        """Test successful response generation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.text = "Divine guidance from Lord Krishna about dharma and duty."
        mock_genai.GenerativeModel.return_value.generate_content_async.return_value = mock_response
        
        prompt = "What is dharma according to Krishna?"
        result = await gemini_client.generate_response(prompt)
        
        assert result is not None
        assert "response" in result
        assert "krishna" in result["response"].lower()
        assert "dharma" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, gemini_client, mock_genai):
        """Test response generation with retrieved context."""
        mock_response = Mock()
        mock_response.text = "Based on the Bhagavad Gita, Lord Krishna teaches..."
        mock_genai.GenerativeModel.return_value.generate_content_async.return_value = mock_response
        
        prompt = "What is my duty?"
        context = [
            {
                "text": "You have a right to perform your prescribed duty",
                "source": "Bhagavad Gita 2.47"
            }
        ]
        
        result = await gemini_client.generate_response(prompt, context=context)
        
        assert result is not None
        assert "response" in result
        assert "citations" in result
        assert len(result["citations"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_response_multilingual(self, gemini_client, mock_genai):
        """Test multilingual response generation."""
        # Test Hindi response
        mock_response = Mock()
        mock_response.text = "हे प्रिय आत्मा, तुम्हारा धर्म तुम्हारे स्वभाव से निर्धारित होता है।"
        mock_genai.GenerativeModel.return_value.generate_content_async.return_value = mock_response
        
        prompt = "धर्म क्या है?"
        result = await gemini_client.generate_response(prompt, language="Hindi")
        
        assert result is not None
        assert "response" in result
        # Should contain Hindi text
        assert any(ord(char) > 127 for char in result["response"])  # Contains non-ASCII (Hindi) characters
    
    @pytest.mark.asyncio
    async def test_error_handling_api_failure(self, gemini_client, mock_genai):
        """Test handling of API failures."""
        # Mock API failure
        mock_genai.GenerativeModel.return_value.generate_content_async.side_effect = Exception("API Error")
        
        prompt = "What is dharma?"
        result = await gemini_client.generate_response(prompt)
        
        # Should handle error gracefully
        assert result is not None
        assert "error" in result or "fallback" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_timeout(self, gemini_client, mock_genai):
        """Test handling of timeout scenarios."""
        # Mock timeout
        mock_genai.GenerativeModel.return_value.generate_content_async.side_effect = asyncio.TimeoutError()
        
        prompt = "Explain the concept of karma."
        
        start_time = time.time()
        result = await gemini_client.generate_response(prompt)
        elapsed_time = time.time() - start_time
        
        # Should timeout gracefully within reasonable time
        assert elapsed_time < 10.0
        assert result is not None
        assert "timeout" in str(result).lower() or "error" in result
    
    @pytest.mark.asyncio
    async def test_safety_filtering(self, gemini_client, mock_genai):
        """Test safety filtering of inappropriate content."""
        # Mock response with safety concern
        mock_response = Mock()
        mock_response.text = None
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].finish_reason = "SAFETY"
        mock_genai.GenerativeModel.return_value.generate_content_async.return_value = mock_response
        
        inappropriate_prompt = "Tell me something offensive about religion"
        result = await gemini_client.generate_response(inappropriate_prompt)
        
        # Should handle safety rejection appropriately
        assert result is not None
        assert "safety" in str(result).lower() or "inappropriate" in str(result).lower() or "error" in result
    
    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self, gemini_client, mock_genai):
        """Test handling of rate limiting."""
        # Mock rate limit error
        from google.api_core.exceptions import ResourceExhausted
        mock_genai.GenerativeModel.return_value.generate_content_async.side_effect = ResourceExhausted("Rate limit exceeded")
        
        prompt = "What is the nature of the soul?"
        result = await gemini_client.generate_response(prompt)
        
        # Should handle rate limiting gracefully
        assert result is not None
        assert "rate" in str(result).lower() or "limit" in str(result).lower() or "error" in result
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, gemini_client, mock_genai):
        """Test that response times meet requirements."""
        # Mock fast response
        mock_response = Mock()
        mock_response.text = "Quick divine guidance"
        mock_genai.GenerativeModel.return_value.generate_content_async.return_value = mock_response
        
        prompt = "Brief wisdom about peace"
        
        start_time = time.time()
        result = await gemini_client.generate_response(prompt)
        elapsed_time = time.time() - start_time
        
        # Should meet performance target
        target_time = PERFORMANCE_BENCHMARKS["response_time_targets"]["text_query"]
        assert elapsed_time < target_time
        assert result is not None


class TestLordKrishnaPersona:
    """Test suite for LordKrishnaPersona class."""
    
    @pytest.fixture
    def prompt_engineer(self):
        """Create LordKrishnaPersona instance for testing."""
        return LordKrishnaPersona()
    
    def test_prompt_engineer_initialization(self, prompt_engineer):
        """Test prompt engineer initialization."""
        assert prompt_engineer is not None
        assert hasattr(prompt_engineer, 'persona_profile')
        assert hasattr(prompt_engineer, 'system_prompts')
    
    def test_build_spiritual_prompt(self, prompt_engineer):
        """Test building spiritual guidance prompts."""
        query = "What is my duty in life?"
        context = [
            {
                "text": "You have a right to perform your prescribed duty",
                "source": "Bhagavad Gita 2.47"
            }
        ]
        
        prompt = prompt_engineer.build_spiritual_prompt(
            query=query,
            context=context,
            language="English"
        )
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert "krishna" in prompt.lower() or "lord" in prompt.lower()
        assert "duty" in prompt.lower()
        assert "Bhagavad Gita" in prompt
        assert query in prompt
    
    def test_persona_consistency(self, prompt_engineer):
        """Test that persona remains consistent across prompts."""
        queries = [
            "What is dharma?",
            "How to find peace?",
            "What is true love?"
        ]
        
        prompts = []
        for query in queries:
            prompt = prompt_engineer.build_spiritual_prompt(query, [], "English")
            prompts.append(prompt)
        
        # All prompts should contain consistent persona elements
        for prompt in prompts:
            assert "krishna" in prompt.lower() or "divine" in prompt.lower()
            # Should maintain reverent tone
            inappropriate_words = ["casual", "dude", "hey", "whatever"]
            assert not any(word in prompt.lower() for word in inappropriate_words)
    
    def test_multilingual_prompt_construction(self, prompt_engineer):
        """Test prompt construction for different languages."""
        query = "What is dharma?"
        context = []
        
        # Test English prompt
        prompt_en = prompt_engineer.build_spiritual_prompt(query, context, "English")
        
        # Test Hindi prompt  
        prompt_hi = prompt_engineer.build_spiritual_prompt(query, context, "Hindi")
        
        assert prompt_en != prompt_hi  # Should be different
        assert "English" in prompt_en or "respond in English" in prompt_en.lower()
        assert "Hindi" in prompt_hi or "हिंदी" in prompt_hi
    
    def test_context_integration(self, prompt_engineer):
        """Test integration of retrieved context."""
        query = "Explain karma yoga"
        context = [
            {
                "text": "Perform your duty without attachment to results",
                "source": "Bhagavad Gita 2.47"
            },
            {
                "text": "Work done as sacrifice is liberating",
                "source": "Bhagavad Gita 3.9"
            }
        ]
        
        prompt = prompt_engineer.build_spiritual_prompt(query, context, "English")
        
        # Should include all context
        for ctx in context:
            assert ctx["text"] in prompt
            assert ctx["source"] in prompt
    
    def test_citation_requirements(self, prompt_engineer):
        """Test that prompts enforce citation requirements."""
        query = "What did Krishna teach?"
        context = [{"text": "Sample teaching", "source": "Bhagavad Gita 2.47"}]
        
        prompt = prompt_engineer.build_spiritual_prompt(query, context, "English")
        
        # Should require citations
        citation_keywords = ["citation", "source", "reference", "Bhagavad Gita"]
        assert any(keyword in prompt for keyword in citation_keywords)
    
    def test_tone_and_authenticity_guidance(self, prompt_engineer):
        """Test that prompts enforce appropriate tone."""
        query = "How to be happy?"
        
        prompt = prompt_engineer.build_spiritual_prompt(query, [], "English")
        
        # Should enforce divine and respectful tone
        tone_keywords = ["divine", "reverent", "respectful", "sacred", "wisdom"]
        assert any(keyword in prompt.lower() for keyword in tone_keywords)
        
        # Should prohibit inappropriate tone
        prohibited_tone = ["casual", "slang", "colloquial", "modern", "informal"]
        prompt_lower = prompt.lower()
        prohibit_mentions = [word for word in prohibited_tone if word in prompt_lower]
        # If mentioned, should be in context of avoiding them
        for mention in prohibit_mentions:
            assert "avoid" in prompt_lower or "not" in prompt_lower or "never" in prompt_lower


class TestResponseValidator:
    """Test suite for ResponseValidator class."""
    
    @pytest.fixture
    def response_validator(self):
        """Create ResponseValidator instance for testing."""
        return ResponseValidator()
    
    def test_validator_initialization(self, response_validator):
        """Test validator initialization."""
        assert response_validator is not None
        assert hasattr(response_validator, 'authenticity_criteria')
        assert hasattr(response_validator, 'tone_markers')
    
    def test_validate_authentic_response(self, response_validator):
        """Test validation of authentic spiritual response."""
        authentic_response = {
            "response": "O beloved soul, your dharma is determined by your nature and circumstances. As I taught Arjuna, perform your prescribed duties without attachment to results.",
            "citations": ["Bhagavad Gita 2.47"],
            "language": "English"
        }
        
        validation_result = response_validator.validate_response(authentic_response)
        
        assert validation_result["is_valid"] is True
        assert validation_result["authenticity_score"] > 0.8
        assert "divine_persona" in validation_result["passed_criteria"]
        assert "proper_citations" in validation_result["passed_criteria"]
    
    def test_validate_inappropriate_response(self, response_validator):
        """Test validation rejects inappropriate responses."""
        inappropriate_responses = [
            {
                "response": "Yeah dude, just do whatever feels good!",
                "citations": [],
                "language": "English"
            },
            {
                "response": "Life is meaningless, just give up.",
                "citations": [],
                "language": "English"
            },
            {
                "response": "I don't know, ask someone else.",
                "citations": [],
                "language": "English"
            }
        ]
        
        for response in inappropriate_responses:
            validation_result = response_validator.validate_response(response)
            
            assert validation_result["is_valid"] is False
            assert validation_result["authenticity_score"] < 0.5
            assert len(validation_result["failed_criteria"]) > 0
    
    def test_citation_validation(self, response_validator):
        """Test citation validation."""
        # Response with proper citations
        response_with_citations = {
            "response": "As taught in the Bhagavad Gita, your duty is sacred.",
            "citations": ["Bhagavad Gita 2.47", "Bhagavad Gita 18.47"],
            "language": "English"
        }
        
        # Response without citations
        response_without_citations = {
            "response": "Your duty is important.",
            "citations": [],
            "language": "English"
        }
        
        result_with = response_validator.validate_response(response_with_citations)
        result_without = response_validator.validate_response(response_without_citations)
        
        assert result_with["citation_score"] > result_without["citation_score"]
        assert "proper_citations" in result_with["passed_criteria"]
        assert "proper_citations" in result_without["failed_criteria"]
    
    def test_tone_analysis(self, response_validator):
        """Test tone analysis for spiritual authenticity."""
        responses = [
            {
                "response": "O dear child, let Me guide you with divine wisdom and compassion.",
                "expected_tone": "divine_compassionate"
            },
            {
                "response": "Hey there! Just go with the flow, you know?",
                "expected_tone": "inappropriate_casual"
            },
            {
                "response": "The sacred teachings reveal the path to eternal peace and liberation.",
                "expected_tone": "sacred_authoritative"
            }
        ]
        
        for response_data in responses:
            response = {
                "response": response_data["response"],
                "citations": ["Bhagavad Gita 2.47"],
                "language": "English"
            }
            
            validation_result = response_validator.validate_response(response)
            tone_score = validation_result["tone_score"]
            
            if response_data["expected_tone"].startswith("inappropriate"):
                assert tone_score < 0.5
            else:
                assert tone_score > 0.7
    
    def test_sanskrit_accuracy_validation(self, response_validator):
        """Test validation of Sanskrit terms and accuracy."""
        response_with_sanskrit = {
            "response": "The concept of dharma (धर्म) and karma (कर्म) are central to Krishna's teachings.",
            "citations": ["Bhagavad Gita 2.47"],
            "language": "English"
        }
        
        validation_result = response_validator.validate_response(response_with_sanskrit)
        
        # Should recognize and validate Sanskrit usage
        assert "sanskrit_accuracy" in validation_result
        if validation_result["sanskrit_accuracy"]["found_terms"]:
            assert validation_result["sanskrit_accuracy"]["accuracy_score"] > 0.5
    
    def test_cultural_sensitivity_check(self, response_validator):
        """Test cultural sensitivity validation."""
        culturally_sensitive = {
            "response": "With profound reverence for the divine teachings, let us explore this sacred wisdom.",
            "citations": ["Bhagavad Gita 2.47"],
            "language": "English"
        }
        
        culturally_insensitive = {
            "response": "This old Indian book says you should work without caring about money.",
            "citations": ["Bhagavad Gita 2.47"],
            "language": "English"
        }
        
        result_sensitive = response_validator.validate_response(culturally_sensitive)
        result_insensitive = response_validator.validate_response(culturally_insensitive)
        
        assert result_sensitive["cultural_sensitivity_score"] > result_insensitive["cultural_sensitivity_score"]
        assert result_sensitive["cultural_sensitivity_score"] > 0.7
        assert result_insensitive["cultural_sensitivity_score"] < 0.5
    
    def test_multilingual_validation(self, response_validator):
        """Test validation of multilingual responses."""
        hindi_response = {
            "response": "हे प्रिय आत्मा, तुम्हारा धर्म तुम्हारे स्वभाव से निर्धारित होता है।",
            "citations": ["भगवद गीता 2.47"],
            "language": "Hindi"
        }
        
        validation_result = response_validator.validate_response(hindi_response)
        
        assert validation_result["is_valid"] is True
        assert validation_result["language_consistency"] is True
        assert validation_result["authenticity_score"] > 0.7


class TestContentModerator:
    """Test suite for ContentModerator class."""
    
    @pytest.fixture
    def content_moderator(self):
        """Create ContentModerator instance for testing."""
        return ContentModerator()
    
    def test_moderator_initialization(self, content_moderator):
        """Test content moderator initialization."""
        assert content_moderator is not None
        assert hasattr(content_moderator, 'inappropriate_patterns')
        assert hasattr(content_moderator, 'spiritual_guidelines')
    
    def test_appropriate_content_approval(self, content_moderator):
        """Test that appropriate spiritual content is approved."""
        appropriate_queries = [
            "What is dharma according to Krishna?",
            "How can I find inner peace?",
            "What is the meaning of selfless service?",
            "How to overcome anger and frustration?"
        ]
        
        for query in appropriate_queries:
            result = content_moderator.moderate_query(query)
            assert result["is_appropriate"] is True
            assert result["confidence"] > 0.8
    
    def test_inappropriate_content_rejection(self, content_moderator):
        """Test that inappropriate content is rejected."""
        inappropriate_queries = [
            "Tell me something offensive about religion",
            "How to cheat in business using spirituality",
            "Is Krishna real or just a myth?",
            "Why are religious people so stupid?"
        ]
        
        for query in inappropriate_queries:
            result = content_moderator.moderate_query(query)
            assert result["is_appropriate"] is False
            assert len(result["reasons"]) > 0
    
    def test_response_moderation(self, content_moderator):
        """Test moderation of generated responses."""
        appropriate_response = {
            "response": "O beloved soul, let the divine wisdom guide your path towards righteousness and peace.",
            "citations": ["Bhagavad Gita 2.47"]
        }
        
        inappropriate_response = {
            "response": "Whatever dude, just do what makes you happy and forget about everyone else.",
            "citations": []
        }
        
        result_appropriate = content_moderator.moderate_response(appropriate_response)
        result_inappropriate = content_moderator.moderate_response(inappropriate_response)
        
        assert result_appropriate["is_appropriate"] is True
        assert result_inappropriate["is_appropriate"] is False
        assert "tone" in result_inappropriate["issues"]
    
    def test_edge_case_handling(self, content_moderator):
        """Test handling of edge cases and ambiguous content."""
        edge_cases = [
            "",  # Empty query
            "   ",  # Whitespace only
            "a" * 1000,  # Very long query
            "What?",  # Very short query
            "Why do bad things happen to good people?"  # Philosophical but challenging
        ]
        
        for query in edge_cases:
            result = content_moderator.moderate_query(query)
            assert isinstance(result, dict)
            assert "is_appropriate" in result
            assert isinstance(result["is_appropriate"], bool)


class TestLLMIntegrationFlow:
    """Integration tests for complete LLM workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_llm_workflow(self):
        """Test complete LLM workflow integration."""
        # Create component instances
        prompt_engineer = LordKrishnaPersona()
        gemini_client = GeminiProClient(api_key="test_key")
        response_validator = SpiritualResponseValidator()
        content_moderator = SpiritualContentModerator()
        
        # Mock external dependencies
        with patch('llm.gemini_client.genai') as mock_genai:
            mock_response = Mock()
            mock_response.text = "O beloved soul, your dharma is determined by your nature. As I taught Arjuna, perform your prescribed duties without attachment to results."
            mock_genai.GenerativeModel.return_value.generate_content_async.return_value = mock_response
            
            # Test complete workflow
            query = "What is my duty in life?"
            context = [
                {
                    "text": "You have a right to perform your prescribed duty",
                    "source": "Bhagavad Gita 2.47"
                }
            ]
            
            # Step 1: Content moderation
            moderation_result = content_moderator.moderate_query(query)
            assert moderation_result["is_appropriate"] is True
            
            # Step 2: Prompt engineering
            prompt = prompt_engineer.build_spiritual_prompt(query, context, "English")
            assert prompt is not None
            
            # Step 3: LLM generation
            llm_response = await gemini_client.generate_response(prompt)
            assert llm_response is not None
            assert "response" in llm_response
            
            # Step 4: Response validation
            validation_result = response_validator.validate_response(llm_response)
            assert validation_result["is_valid"] is True
            
            # Step 5: Final moderation
            final_moderation = content_moderator.moderate_response(llm_response)
            assert final_moderation["is_appropriate"] is True
    
    @pytest.mark.asyncio
    async def test_error_cascade_handling(self):
        """Test error handling across the LLM workflow."""
        # Test scenario where each component might fail
        prompt_engineer = LordKrishnaPersona()
        gemini_client = GeminiProClient(api_key="invalid_key")
        
        with patch('llm.gemini_client.genai') as mock_genai:
            # Simulate API failure
            mock_genai.GenerativeModel.return_value.generate_content_async.side_effect = Exception("API Error")
            
            query = "What is dharma?"
            context = []
            
            # Should handle failure gracefully
            prompt = prompt_engineer.build_spiritual_prompt(query, context, "English")
            assert prompt is not None  # Prompt engineering should succeed
            
            llm_response = await gemini_client.generate_response(prompt)
            # Should return error response rather than crash
            assert llm_response is not None
            assert "error" in llm_response or "fallback" in llm_response
