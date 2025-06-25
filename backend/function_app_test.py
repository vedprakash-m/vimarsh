"""
Unit tests for Azure Functions spiritual guidance API endpoints.

Tests cover the main Azure Functions HTTP triggers including health checks,
spiritual guidance processing, and language support endpoints.
"""

import json
import pytest
import azure.functions as func
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function app
import function_app


class TestHealthCheck:
    """Test cases for health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check response."""
        # Create mock request
        req = Mock(spec=func.HttpRequest)
        
        # Call the function
        response = await function_app.health_check_impl(req)
        
        # Assertions
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        # Parse response body
        response_data = json.loads(response.get_body().decode())
        assert response_data["status"] == "healthy"
        assert response_data["service"] == "vimarsh-spiritual-guidance"
        assert "timestamp" in response_data
        assert "version" in response_data
    
    @pytest.mark.asyncio
    async def test_health_check_exception_handling(self):
        """Test health check handles exceptions gracefully."""
        # Mock something that will cause an exception in the try block but not error handling
        with patch('function_app.os.getenv') as mock_getenv:
            mock_getenv.side_effect = Exception("Test exception")
            
            req = Mock(spec=func.HttpRequest)
            response = await function_app.health_check_impl(req)
            
            assert response.status_code == 500
            response_data = json.loads(response.get_body().decode())
            assert response_data["status"] == "unhealthy"
            assert "error" in response_data


class TestSpiritualGuidance:
    """Test cases for spiritual guidance endpoint."""
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_valid_request_english(self):
        """Test valid spiritual guidance request in English."""
        # Create mock request with valid body
        req = Mock(spec=func.HttpRequest)
        req.get_body.return_value = json.dumps({
            "query": "How can I find inner peace?",
            "language": "English",
            "include_citations": True,
            "voice_enabled": False
        }).encode()
        req.get_json.return_value = {
            "query": "How can I find inner peace?",
            "language": "English",
            "include_citations": True,
            "voice_enabled": False
        }
        req.headers = {}
        
        # Call the function
        response = await function_app.spiritual_guidance_impl(req)
        
        # Assertions
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        # Parse response body
        response_data = json.loads(response.get_body().decode())
        assert "response" in response_data
        assert "citations" in response_data
        assert "metadata" in response_data
        assert response_data["metadata"]["language"] == "English"
        assert response_data["metadata"]["persona"] == "Lord Krishna"
        assert len(response_data["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_valid_request_hindi(self):
        """Test valid spiritual guidance request in Hindi."""
        req = Mock(spec=func.HttpRequest)
        req.get_body.return_value = json.dumps({
            "query": "मुझे आंतरिक शांति कैसे मिल सकती है?",
            "language": "Hindi",
            "include_citations": True
        }).encode()
        req.get_json.return_value = {
            "query": "मुझे आंतरिक शांति कैसे मिल सकती है?",
            "language": "Hindi",
            "include_citations": True
        }
        req.headers = {}
        
        response = await function_app.spiritual_guidance_impl(req)
        
        assert response.status_code == 200
        response_data = json.loads(response.get_body().decode())
        assert response_data["metadata"]["language"] == "Hindi"
        assert "प्रिय भक्त" in response_data["response"]  # Hindi greeting
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_empty_body(self):
        """Test spiritual guidance with empty request body."""
        req = Mock(spec=func.HttpRequest)
        req.get_body.return_value = None
        
        response = await function_app.spiritual_guidance_impl(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Invalid request"
        assert "body is required" in response_data["message"]
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_invalid_json(self):
        """Test spiritual guidance with invalid JSON."""
        req = Mock(spec=func.HttpRequest)
        req.get_body.return_value = b"invalid json"
        req.get_json.return_value = None
        
        response = await function_app.spiritual_guidance_impl(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Invalid request"
        assert "Invalid JSON" in response_data["message"]
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_empty_query(self):
        """Test spiritual guidance with empty query."""
        req = Mock(spec=func.HttpRequest)
        req.get_body.return_value = json.dumps({
            "query": "",
            "language": "English"
        }).encode()
        req.get_json.return_value = {
            "query": "",
            "language": "English"
        }
        
        response = await function_app.spiritual_guidance_impl(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert "Query parameter is required" in response_data["message"]
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_invalid_language(self):
        """Test spiritual guidance with invalid language."""
        req = Mock(spec=func.HttpRequest)
        req.get_body.return_value = json.dumps({
            "query": "Test question",
            "language": "Spanish"
        }).encode()
        req.get_json.return_value = {
            "query": "Test question",
            "language": "Spanish"
        }
        
        response = await function_app.spiritual_guidance_impl(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert "Language must be 'English' or 'Hindi'" in response_data["message"]
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_with_voice_enabled(self):
        """Test spiritual guidance with voice output enabled."""
        req = Mock(spec=func.HttpRequest)
        req.get_body.return_value = json.dumps({
            "query": "What is dharma?",
            "language": "English",
            "voice_enabled": True
        }).encode()
        req.get_json.return_value = {
            "query": "What is dharma?",
            "language": "English",
            "voice_enabled": True
        }
        req.headers = {}
        
        response = await function_app.spiritual_guidance_impl(req)
        
        assert response.status_code == 200
        response_data = json.loads(response.get_body().decode())
        assert "audio_url" in response_data
        assert response_data["audio_url"].endswith(".mp3")


class TestSupportedLanguages:
    """Test cases for supported languages endpoint."""
    
    @pytest.mark.asyncio
    async def test_supported_languages_success(self):
        """Test successful languages endpoint response."""
        req = Mock(spec=func.HttpRequest)
        
        response = await function_app.supported_languages_impl(req)
        
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        assert "languages" in response_data
        assert "default_language" in response_data
        assert len(response_data["languages"]) == 2
        
        # Check English language entry
        english = next(lang for lang in response_data["languages"] if lang["code"] == "English")
        assert english["name"] == "English"
        assert english["native_name"] == "English"
        assert "text" in english["supported_features"]
        
        # Check Hindi language entry
        hindi = next(lang for lang in response_data["languages"] if lang["code"] == "Hindi")
        assert hindi["name"] == "Hindi"
        assert hindi["native_name"] == "हिन्दी"
        assert "voice" in hindi["supported_features"]


class TestGenerateSpiritualResponse:
    """Test cases for the internal response generation function."""
    
    @pytest.mark.asyncio
    async def test_generate_response_english(self):
        """Test spiritual response generation in English."""
        response = await function_app._generate_spiritual_response(
            "How can I find peace?", "English", True, False
        )
        
        assert "response" in response
        assert "citations" in response
        assert "metadata" in response
        assert response["metadata"]["language"] == "English"
        assert response["metadata"]["persona"] == "Lord Krishna"
        assert len(response["response"]) > 0
        assert "Dear devotee" in response["response"]
    
    @pytest.mark.asyncio
    async def test_generate_response_hindi(self):
        """Test spiritual response generation in Hindi."""
        response = await function_app._generate_spiritual_response(
            "शांति कैसे मिले?", "Hindi", True, False
        )
        
        assert response["metadata"]["language"] == "Hindi"
        assert "प्रिय भक्त" in response["response"]
        assert len(response["citations"]) > 0
        assert response["citations"][0]["source"] == "भगवद्गीता"
    
    @pytest.mark.asyncio
    async def test_generate_response_without_citations(self):
        """Test spiritual response generation without citations."""
        response = await function_app._generate_spiritual_response(
            "What is dharma?", "English", False, False
        )
        
        assert "response" in response
        assert response["citations"] == []
        assert response["metadata"]["language"] == "English"
    
    @pytest.mark.asyncio
    async def test_generate_response_with_voice(self):
        """Test spiritual response generation with voice enabled."""
        response = await function_app._generate_spiritual_response(
            "What is karma?", "English", True, True
        )
        
        assert "audio_url" in response
        assert response["audio_url"].startswith("https://")
        assert response["audio_url"].endswith(".mp3")


class TestCORSHandler:
    """Test cases for CORS options handler."""
    
    @pytest.mark.asyncio
    async def test_options_handler(self):
        """Test CORS preflight request handling."""
        req = Mock(spec=func.HttpRequest)
        
        response = await function_app.handle_options_impl(req)
        
        assert response.status_code == 204
        assert response.get_body() == b""
        
        # Check CORS headers (these would be in response.headers in actual implementation)
        # Note: The exact header checking depends on the Azure Functions framework


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
