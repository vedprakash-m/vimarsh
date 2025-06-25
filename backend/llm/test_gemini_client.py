"""
Comprehensive tests for the Gemini Pro API client.
Tests spiritual safety configuration and content validation.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from .gemini_client import (
    GeminiProClient,
    SpiritualSafetyConfig,
    SpiritualContext,
    SafetyLevel,
    GeminiResponse,
    create_development_client,
    create_production_client,
    create_testing_client
)

class TestSpiritualSafetyConfig:
    """Test the spiritual safety configuration."""
    
    def test_safety_config_creation(self):
        """Test creating a safety configuration."""
        config = SpiritualSafetyConfig(
            safety_level=SafetyLevel.STRICT,
            allowed_contexts=[SpiritualContext.GUIDANCE, SpiritualContext.TEACHING],
            require_citations=True,
            block_personal_predictions=True,
            max_response_length=800
        )
        
        assert config.safety_level == SafetyLevel.STRICT
        assert len(config.allowed_contexts) == 2
        assert config.require_citations is True
        assert config.block_personal_predictions is True
        assert config.max_response_length == 800
    
    def test_safety_config_to_dict(self):
        """Test converting safety config to dictionary."""
        config = SpiritualSafetyConfig(
            safety_level=SafetyLevel.MODERATE,
            allowed_contexts=[SpiritualContext.GUIDANCE]
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["safety_level"] == "moderate"
        assert config_dict["allowed_contexts"] == ["guidance"]
        assert "require_citations" in config_dict
        assert "block_personal_predictions" in config_dict

class TestGeminiResponse:
    """Test the Gemini response structure."""
    
    def test_gemini_response_creation(self):
        """Test creating a Gemini response."""
        response = GeminiResponse(
            content="This is a spiritual response",
            safety_ratings={"test": "passed"},
            finish_reason="STOP",
            usage_metadata={"tokens": 100},
            response_time=1.5,
            spiritual_context=SpiritualContext.GUIDANCE,
            safety_passed=True
        )
        
        assert response.content == "This is a spiritual response"
        assert response.safety_ratings["test"] == "passed"
        assert response.finish_reason == "STOP"
        assert response.response_time == 1.5
        assert response.spiritual_context == SpiritualContext.GUIDANCE
        assert response.safety_passed is True
        assert response.warnings == []  # Default empty list
    
    def test_gemini_response_with_warnings(self):
        """Test creating a Gemini response with warnings."""
        warnings = ["Content may lack citations", "Response too long"]
        response = GeminiResponse(
            content="Test content",
            safety_ratings={},
            finish_reason="STOP",
            usage_metadata={},
            response_time=1.0,
            warnings=warnings
        )
        
        assert response.warnings == warnings

class TestGeminiProClient:
    """Test the Gemini Pro client functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock API key for testing
        self.test_api_key = "test-api-key"
        
        # Create test safety config
        self.test_config = SpiritualSafetyConfig(
            safety_level=SafetyLevel.MODERATE,
            allowed_contexts=[SpiritualContext.GUIDANCE, SpiritualContext.TEACHING],
            require_citations=False,  # Relaxed for testing
            max_response_length=500
        )
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_client_initialization(self, mock_model, mock_configure):
        """Test client initialization with API key and config."""
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        # Verify API configuration
        mock_configure.assert_called_once_with(api_key=self.test_api_key)
        
        # Verify model initialization
        mock_model.assert_called_once()
        
        # Verify client properties
        assert client.api_key == self.test_api_key
        assert client.safety_config == self.test_config
    
    @patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'env-api-key'})
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_client_initialization_from_env(self, mock_model, mock_configure):
        """Test client initialization with API key from environment."""
        client = GeminiProClient()
        
        mock_configure.assert_called_once_with(api_key='env-api-key')
        assert client.api_key == 'env-api-key'
    
    def test_client_initialization_no_api_key(self):
        """Test client initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GOOGLE_AI_API_KEY must be provided"):
                GeminiProClient()
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_default_safety_config(self, mock_model, mock_configure):
        """Test client creates default safety config when none provided."""
        client = GeminiProClient(api_key=self.test_api_key)
        
        assert client.safety_config.safety_level == SafetyLevel.STRICT
        assert client.safety_config.require_citations is True
        assert client.safety_config.block_personal_predictions is True
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_spiritual_system_prompt_creation(self, mock_model, mock_configure):
        """Test creating spiritual system prompts for different contexts."""
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        # Test guidance context
        guidance_prompt = client._create_spiritual_system_prompt(SpiritualContext.GUIDANCE)
        assert "Lord Krishna" in guidance_prompt
        assert "practical spiritual guidance" in guidance_prompt
        
        # Test teaching context
        teaching_prompt = client._create_spiritual_system_prompt(SpiritualContext.TEACHING)
        assert "explain concepts clearly" in teaching_prompt.lower()
        
        # Test philosophy context
        philosophy_prompt = client._create_spiritual_system_prompt(SpiritualContext.PHILOSOPHY)
        assert "philosophical discussion" in philosophy_prompt.lower()
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_content_validation(self, mock_model, mock_configure):
        """Test spiritual content validation."""
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        # Test content with citations (good)
        good_content = "According to Bhagavad Gita chapter 2, verse 47, you should perform your duty without attachment."
        warnings = client._validate_spiritual_content(good_content, SpiritualContext.GUIDANCE)
        assert len(warnings) == 0
        
        # Test content without citations (if required)
        config_with_citations = SpiritualSafetyConfig(
            safety_level=SafetyLevel.STRICT,
            allowed_contexts=[SpiritualContext.GUIDANCE],
            require_citations=True
        )
        client_strict = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=config_with_citations
        )
        
        no_citation_content = "You should just do your best in life."
        warnings = client_strict._validate_spiritual_content(no_citation_content, SpiritualContext.GUIDANCE)
        assert any("lacks scriptural citations" in w for w in warnings)
        
        # Test content with personal predictions
        prediction_content = "You will find success in the future and your life will improve."
        warnings = client._validate_spiritual_content(prediction_content, SpiritualContext.GUIDANCE)
        assert any("personal predictions" in w for w in warnings)
        
        # Test content with medical advice
        medical_content = "This spiritual practice will cure your illness and heal your disease."
        warnings = client._validate_spiritual_content(medical_content, SpiritualContext.GUIDANCE)
        assert any("medical advice" in w for w in warnings)
        
        # Test content that's too long
        long_content = "a" * 600  # Exceeds test config max of 500
        warnings = client._validate_spiritual_content(long_content, SpiritualContext.GUIDANCE)
        assert any("exceeds maximum length" in w for w in warnings)
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_generate_response_success(self, mock_model, mock_configure):
        """Test successful response generation."""
        # Mock the generative model
        mock_response = Mock()
        mock_response.text = "This is a spiritual response about dharma from Bhagavad Gita."
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].finish_reason = Mock()
        mock_response.candidates[0].finish_reason.name = "STOP"
        mock_response.candidates[0].safety_ratings = []
        mock_response.prompt_feedback = None
        
        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        # Generate response
        response = client.generate_response(
            "What is dharma?",
            context=SpiritualContext.GUIDANCE
        )
        
        # Verify response
        assert response.content == "This is a spiritual response about dharma from Bhagavad Gita."
        assert response.finish_reason == "STOP"
        assert response.spiritual_context == SpiritualContext.GUIDANCE
        assert response.response_time > 0
        assert response.safety_passed is True  # Should pass validation
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_generate_response_with_validation_warnings(self, mock_model, mock_configure):
        """Test response generation with content validation warnings."""
        # Mock the generative model with problematic content
        mock_response = Mock()
        mock_response.text = "You will definitely find happiness in the future."  # Personal prediction
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].finish_reason = Mock()
        mock_response.candidates[0].finish_reason.name = "STOP"
        mock_response.candidates[0].safety_ratings = []
        mock_response.prompt_feedback = None
        
        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        # Generate response
        response = client.generate_response(
            "What will happen to me?",
            context=SpiritualContext.GUIDANCE
        )
        
        # Verify response has warnings
        assert len(response.warnings) > 0
        assert any("personal predictions" in w for w in response.warnings)
        assert response.safety_passed is False  # Should fail validation
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_generate_response_api_error(self, mock_model, mock_configure):
        """Test response generation with API error."""
        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = Exception("API Error")
        mock_model.return_value = mock_model_instance
        
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        # Generate response
        response = client.generate_response(
            "Test question",
            context=SpiritualContext.GUIDANCE
        )
        
        # Verify error response
        assert response.finish_reason == "ERROR"
        assert response.safety_passed is False
        assert any("API Error" in w for w in response.warnings)
        assert "unable to provide a response" in response.content.lower()
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_test_connection_success(self, mock_model, mock_configure):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].finish_reason = Mock()
        mock_response.candidates[0].finish_reason.name = "STOP"
        mock_response.candidates[0].safety_ratings = []
        mock_response.prompt_feedback = None
        
        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        assert client.test_connection() is True
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_test_connection_failure(self, mock_model, mock_configure):
        """Test failed connection test."""
        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = Exception("Connection failed")
        mock_model.return_value = mock_model_instance
        
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        assert client.test_connection() is False
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_get_model_info(self, mock_model, mock_configure):
        """Test getting model information."""
        client = GeminiProClient(
            api_key=self.test_api_key,
            safety_config=self.test_config
        )
        
        info = client.get_model_info()
        
        assert info["model_name"] == "gemini-pro"
        assert "safety_config" in info
        assert info["api_configured"] is True
        assert "supported_contexts" in info
        assert len(info["supported_contexts"]) == len(SpiritualContext)

class TestClientFactories:
    """Test the client factory functions."""
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_create_development_client(self, mock_model, mock_configure):
        """Test creating development client."""
        client = create_development_client(api_key="test-key")
        
        assert client.safety_config.safety_level == SafetyLevel.MODERATE
        assert client.safety_config.require_citations is False
        assert client.safety_config.max_response_length == 1200
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_create_production_client(self, mock_model, mock_configure):
        """Test creating production client."""
        client = create_production_client(api_key="test-key")
        
        assert client.safety_config.safety_level == SafetyLevel.STRICT
        assert client.safety_config.require_citations is True
        assert client.safety_config.max_response_length == 800
        assert len(client.safety_config.allowed_contexts) == 4  # Limited contexts
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_create_testing_client(self, mock_model, mock_configure):
        """Test creating testing client."""
        client = create_testing_client(api_key="test-key")
        
        assert client.safety_config.safety_level == SafetyLevel.MINIMAL
        assert client.safety_config.require_citations is False
        assert client.safety_config.block_personal_predictions is False
        assert client.safety_config.require_reverent_tone is False
        assert client.safety_config.max_response_length == 1500

class TestSafetyFeatures:
    """Test comprehensive safety features."""
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_safety_settings_mapping(self, mock_model, mock_configure):
        """Test mapping of spiritual safety levels to Gemini safety settings."""
        # Test strict settings
        strict_config = SpiritualSafetyConfig(
            safety_level=SafetyLevel.STRICT,
            allowed_contexts=[SpiritualContext.GUIDANCE]
        )
        client = GeminiProClient(api_key="test", safety_config=strict_config)
        settings = client._get_safety_settings()
        
        # Should have safety settings for all harm categories
        assert len(settings) == 4
        
        # Test moderate settings
        moderate_config = SpiritualSafetyConfig(
            safety_level=SafetyLevel.MODERATE,
            allowed_contexts=[SpiritualContext.GUIDANCE]
        )
        client_moderate = GeminiProClient(api_key="test", safety_config=moderate_config)
        moderate_settings = client_moderate._get_safety_settings()
        
        assert len(moderate_settings) == 4
    
    @patch('gemini_client.genai.configure')
    @patch('gemini_client.genai.GenerativeModel')
    def test_irreverent_language_detection(self, mock_model, mock_configure):
        """Test detection of irreverent language."""
        config = SpiritualSafetyConfig(
            safety_level=SafetyLevel.STRICT,
            allowed_contexts=[SpiritualContext.GUIDANCE],
            require_reverent_tone=True
        )
        client = GeminiProClient(api_key="test", safety_config=config)
        
        # Test irreverent content
        irreverent_content = "This spiritual stuff is damn stupid and nonsense."
        warnings = client._validate_spiritual_content(irreverent_content, SpiritualContext.GUIDANCE)
        
        assert any("irreverent language" in w for w in warnings)
        
        # Test reverent content
        reverent_content = "The sacred teachings of Krishna guide us with wisdom and compassion."
        warnings = client._validate_spiritual_content(reverent_content, SpiritualContext.GUIDANCE)
        
        # Should not trigger irreverent language warning (though may have other warnings)
        assert not any("irreverent language" in w for w in warnings)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
