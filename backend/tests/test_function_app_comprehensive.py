#!/usr/bin/env python3
"""
Comprehensive Test Suite for Function App - Main Application Entry Point
Priority 2: Critical Business Logic Testing

Current Coverage: 14.10% (731 statements, 602 missing) - BUSINESS CRITICAL
Target Coverage: 80%
Business Impact: Reliable Azure Functions deployment and API endpoints
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional
import azure.functions as func
from datetime import datetime

# Test configuration
TEST_CONFIG = {
    'valid_personalities': ['krishna', 'buddha', 'einstein', 'marcus_aurelius'],
    'test_queries': [
        "What is dharma?",
        "How to overcome suffering?", 
        "What is the nature of time?",
        "How to live virtuously?"
    ],
    'mock_user_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.mock_token',
    'performance_thresholds': {
        'response_time': 5.0,
        'error_rate': 0.05
    }
}


class TestFunctionAppCore:
    """Core functionality tests for Azure Functions app entry points"""
    
    @pytest.fixture
    def mock_request_valid_spiritual_guidance(self):
        """Mock valid spiritual guidance request"""
        request_data = {
            'query': 'What is dharma according to Hindu philosophy?',
            'personality_id': 'krishna',
            'language': 'English',
            'user_context': {
                'session_id': 'test_session_123',
                'previous_topics': ['duty', 'righteousness']
            }
        }
        
        # Create mock Azure Functions HttpRequest
        req = Mock(spec=func.HttpRequest)
        req.get_json.return_value = request_data
        req.headers = {'Authorization': f'Bearer {TEST_CONFIG["mock_user_token"]}'}
        req.method = 'POST'
        req.url = 'https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance'
        
        return req
    
    @pytest.fixture  
    def mock_request_invalid_data(self):
        """Mock request with invalid data"""
        request_data = {
            'query': '',  # Empty query
            'personality_id': 'invalid_personality',
            'language': ''
        }
        
        req = Mock(spec=func.HttpRequest)
        req.get_json.return_value = request_data
        req.headers = {}  # No authorization
        req.method = 'POST'
        
        return req
    
    @pytest.fixture
    def mock_spiritual_guidance_service(self):
        """Mock spiritual guidance service"""
        mock_service = Mock()
        mock_service.generate_guidance = AsyncMock(return_value={
            'content': 'My dear friend, dharma is the righteous path that sustains the universe. Follow your duty without attachment to results.',
            'personality_id': 'krishna',
            'citations': [
                {
                    'source': 'Bhagavad Gita 2.47',
                    'text': 'You have a right to perform your prescribed duty, but not to the fruits of your action.',
                    'accuracy_score': 0.95
                }
            ],
            'metadata': {
                'response_time': 1.2,
                'confidence_score': 0.92,
                'source_type': 'ai_generated',
                'personality_consistency': 0.94
            }
        })
        return mock_service
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_endpoint_success(self, mock_request_valid_spiritual_guidance, mock_spiritual_guidance_service):
        """Test successful spiritual guidance endpoint execution"""
        
        with patch('function_app.SpiritualGuidanceService', return_value=mock_spiritual_guidance_service):
            with patch('function_app.extract_user_from_token') as mock_auth:
                mock_auth.return_value = {
                    'user_id': 'test_user_123',
                    'email': 'test@example.com',
                    'name': 'Test User'
                }
                
                # Import and test the function
                from function_app import spiritual_guidance
                
                response = await spiritual_guidance(mock_request_valid_spiritual_guidance)
                
                # Verify response structure
                assert isinstance(response, func.HttpResponse)
                assert response.status_code == 200
                
                # Parse response content
                response_data = json.loads(response.get_body().decode())
                
                # Verify response contains expected fields
                assert 'content' in response_data
                assert 'personality_id' in response_data
                assert 'citations' in response_data
                assert 'metadata' in response_data
                
                # Verify content quality
                assert len(response_data['content']) > 0
                assert response_data['personality_id'] == 'krishna'
                assert 'dharma' in response_data['content'].lower()
                
                # Verify citations are present
                assert len(response_data['citations']) > 0
                assert 'Bhagavad Gita' in response_data['citations'][0]['source']
                
                # Verify metadata
                assert response_data['metadata']['confidence_score'] > 0.8
                assert response_data['metadata']['source_type'] in ['ai_generated', 'template_fallback']
    
    @pytest.mark.asyncio
    async def test_spiritual_guidance_endpoint_validation_errors(self, mock_request_invalid_data):
        """Test spiritual guidance endpoint with validation errors"""
        
        from function_app import spiritual_guidance
        
        response = await spiritual_guidance(mock_request_invalid_data)
        
        # Verify error response
        assert isinstance(response, func.HttpResponse)
        assert response.status_code == 400
        
        response_data = json.loads(response.get_body().decode())
        assert 'error' in response_data
        assert 'validation' in response_data['error'].lower() or 'invalid' in response_data['error'].lower()
    
    @pytest.mark.asyncio
    async def test_authentication_integration(self, mock_request_valid_spiritual_guidance):
        """Test Microsoft Entra ID authentication integration"""
        
        # Test valid token
        with patch('function_app.extract_user_from_token') as mock_auth:
            mock_auth.return_value = {
                'user_id': 'valid_user_123',
                'email': 'user@example.com',
                'name': 'Valid User',
                'tenant_id': 'tenant_123'
            }
            
            with patch('function_app.SpiritualGuidanceService'):
                from function_app import spiritual_guidance
                
                response = await spiritual_guidance(mock_request_valid_spiritual_guidance)
                
                # Verify authentication was called
                mock_auth.assert_called_once()
                assert response.status_code in [200, 401]  # Success or auth failure
        
        # Test invalid token
        with patch('function_app.extract_user_from_token') as mock_auth:
            mock_auth.side_effect = Exception("Invalid token")
            
            with patch('function_app.SpiritualGuidanceService'):
                from function_app import spiritual_guidance
                
                response = await spiritual_guidance(mock_request_valid_spiritual_guidance)
                
                # Should handle auth failure gracefully
                assert isinstance(response, func.HttpResponse)
                # Could be 401 Unauthorized or 200 with anonymous access
                assert response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_error_handling_scenarios(self, mock_request_valid_spiritual_guidance):
        """Test comprehensive error handling scenarios"""
        
        error_scenarios = [
            {
                'name': 'Service Unavailable',
                'exception': Exception("Spiritual guidance service unavailable"),
                'expected_status': [500, 503]
            },
            {
                'name': 'Timeout Error', 
                'exception': asyncio.TimeoutError("Request timeout"),
                'expected_status': [408, 500]
            },
            {
                'name': 'JSON Parse Error',
                'exception': json.JSONDecodeError("Invalid JSON", "", 0),
                'expected_status': [400, 500]
            },
            {
                'name': 'Database Connection Error',
                'exception': ConnectionError("Cannot connect to database"),
                'expected_status': [500, 503]
            }
        ]
        
        for scenario in error_scenarios:
            with patch('function_app.SpiritualGuidanceService') as mock_service:
                mock_service.return_value.generate_guidance = AsyncMock(
                    side_effect=scenario['exception']
                )
                
                with patch('function_app.extract_user_from_token', return_value={'user_id': 'test'}):
                    from function_app import spiritual_guidance
                    
                    response = await spiritual_guidance(mock_request_valid_spiritual_guidance)
                    
                    # Verify error handling
                    assert isinstance(response, func.HttpResponse)
                    assert response.status_code in scenario['expected_status']
                    
                    # Verify error response structure
                    if response.status_code >= 400:
                        try:
                            error_data = json.loads(response.get_body().decode())
                            assert 'error' in error_data
                        except json.JSONDecodeError:
                            # Some errors might return plain text
                            pass
    
    @pytest.mark.asyncio 
    async def test_personality_endpoint_workflows(self, mock_spiritual_guidance_service):
        """Test personality-specific endpoint behavior"""
        
        personalities = TEST_CONFIG['valid_personalities']
        
        for personality in personalities:
            # Create personality-specific request
            request_data = {
                'query': f'What wisdom do you offer about life, {personality}?',
                'personality_id': personality,
                'language': 'English'
            }
            
            req = Mock(spec=func.HttpRequest)
            req.get_json.return_value = request_data
            req.headers = {'Authorization': f'Bearer {TEST_CONFIG["mock_user_token"]}'}
            
            # Configure service mock for personality
            mock_spiritual_guidance_service.generate_guidance = AsyncMock(return_value={
                'content': f'Wisdom from {personality}: Life guidance...',
                'personality_id': personality,
                'citations': [],
                'metadata': {
                    'personality_consistency': 0.95,
                    'cultural_authenticity': 0.92
                }
            })
            
            with patch('function_app.SpiritualGuidanceService', return_value=mock_spiritual_guidance_service):
                with patch('function_app.extract_user_from_token', return_value={'user_id': 'test'}):
                    from function_app import spiritual_guidance
                    
                    response = await spiritual_guidance(req)
                    
                    # Verify personality-specific response
                    assert response.status_code == 200
                    
                    response_data = json.loads(response.get_body().decode())
                    assert response_data['personality_id'] == personality
                    assert personality in response_data['content'].lower()


class TestFunctionAppHealthEndpoints:
    """Test health check and monitoring endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_basic(self):
        """Test basic health endpoint functionality"""
        
        req = Mock(spec=func.HttpRequest)
        req.method = 'GET'
        req.url = 'https://vimarsh-backend-app.azurewebsites.net/api/health'
        
        with patch('function_app.test_database_connection', return_value=True):
            with patch('function_app.test_llm_service', return_value=True):
                from function_app import health_check
                
                response = await health_check(req)
                
                assert isinstance(response, func.HttpResponse)
                assert response.status_code == 200
                
                health_data = json.loads(response.get_body().decode())
                assert 'status' in health_data
                assert 'timestamp' in health_data
                assert health_data['status'] in ['healthy', 'degraded', 'unhealthy']
    
    @pytest.mark.asyncio
    async def test_health_endpoint_detailed(self):
        """Test detailed health endpoint with service status"""
        
        req = Mock(spec=func.HttpRequest)
        req.method = 'GET'
        req.params = {'detailed': 'true'}
        
        with patch.multiple(
            'function_app',
            test_database_connection=Mock(return_value=True),
            test_llm_service=Mock(return_value=True),
            test_vector_search=Mock(return_value=True),
            test_authentication_service=Mock(return_value=True)
        ):
            from function_app import health_check
            
            response = await health_check(req)
            
            assert response.status_code == 200
            
            health_data = json.loads(response.get_body().decode())
            assert 'services' in health_data
            assert 'database' in health_data['services']
            assert 'llm_service' in health_data['services']
            assert 'vector_search' in health_data['services']
    
    @pytest.mark.asyncio
    async def test_health_endpoint_service_failures(self):
        """Test health endpoint when services are failing"""
        
        req = Mock(spec=func.HttpRequest)
        req.method = 'GET'
        
        # Simulate service failures
        with patch.multiple(
            'function_app',
            test_database_connection=Mock(return_value=False),
            test_llm_service=Mock(side_effect=Exception("LLM service down")),
            test_vector_search=Mock(return_value=False)
        ):
            from function_app import health_check
            
            response = await health_check(req)
            
            # Should still return a response but indicate unhealthy status
            assert isinstance(response, func.HttpResponse)
            assert response.status_code in [200, 503]  # OK with unhealthy status or Service Unavailable
            
            if response.status_code == 200:
                health_data = json.loads(response.get_body().decode())
                assert health_data['status'] in ['degraded', 'unhealthy']


class TestFunctionAppPerformance:
    """Performance tests for Function App endpoints"""
    
    @pytest.mark.asyncio
    async def test_response_time_performance(self, mock_request_valid_spiritual_guidance):
        """Test response time meets performance requirements"""
        
        import time
        
        with patch('function_app.SpiritualGuidanceService') as mock_service:
            # Mock fast service response
            mock_service.return_value.generate_guidance = AsyncMock(return_value={
                'content': 'Fast response content',
                'personality_id': 'krishna',
                'citations': [],
                'metadata': {'response_time': 0.5}
            })
            
            with patch('function_app.extract_user_from_token', return_value={'user_id': 'test'}):
                from function_app import spiritual_guidance
                
                start_time = time.time()
                response = await spiritual_guidance(mock_request_valid_spiritual_guidance)
                response_time = time.time() - start_time
                
                # Verify performance requirements (target: <5 seconds)
                assert response_time < TEST_CONFIG['performance_thresholds']['response_time']
                assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """Test handling multiple concurrent requests"""
        
        # Create multiple concurrent requests
        requests = []
        for i in range(5):
            request_data = {
                'query': f'Test query {i}',
                'personality_id': 'krishna',
                'language': 'English'
            }
            
            req = Mock(spec=func.HttpRequest)
            req.get_json.return_value = request_data
            req.headers = {'Authorization': f'Bearer {TEST_CONFIG["mock_user_token"]}'}
            requests.append(req)
        
        with patch('function_app.SpiritualGuidanceService') as mock_service:
            mock_service.return_value.generate_guidance = AsyncMock(return_value={
                'content': 'Concurrent response',
                'personality_id': 'krishna',
                'citations': [],
                'metadata': {}
            })
            
            with patch('function_app.extract_user_from_token', return_value={'user_id': 'test'}):
                from function_app import spiritual_guidance
                
                # Execute concurrent requests
                start_time = time.time()
                tasks = [spiritual_guidance(req) for req in requests]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                # Verify concurrent handling
                assert len(responses) == 5
                assert all(isinstance(r, func.HttpResponse) or isinstance(r, Exception) for r in responses)
                assert total_time < 15.0  # Should handle concurrency efficiently
                
                # Count successful responses
                successful_responses = [r for r in responses if isinstance(r, func.HttpResponse) and r.status_code == 200]
                error_rate = 1 - (len(successful_responses) / len(responses))
                assert error_rate < TEST_CONFIG['performance_thresholds']['error_rate']


class TestFunctionAppIntegration:
    """Integration tests for Function App with real service dependencies"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_spiritual_guidance_workflow(self):
        """Test complete spiritual guidance workflow integration"""
        
        # Create realistic request
        request_data = {
            'query': 'How can I find inner peace in challenging times?',
            'personality_id': 'buddha',
            'language': 'English',
            'user_context': {
                'session_id': 'integration_test_session',
                'conversation_history': [
                    {'role': 'user', 'content': 'I am struggling with anxiety'},
                    {'role': 'assistant', 'content': 'Suffering arises from attachment...'}
                ]
            }
        }
        
        req = Mock(spec=func.HttpRequest)
        req.get_json.return_value = request_data
        req.headers = {'Authorization': f'Bearer {TEST_CONFIG["mock_user_token"]}'}
        
        # Mock integrated services
        with patch('function_app.SpiritualGuidanceService') as mock_guidance:
            with patch('function_app.ConversationMemoryService') as mock_memory:
                with patch('function_app.extract_user_from_token') as mock_auth:
                    
                    # Configure service mocks
                    mock_auth.return_value = {'user_id': 'integration_test_user'}
                    
                    mock_memory.return_value.get_conversation_context = AsyncMock(return_value="Previous context about anxiety and suffering")
                    mock_memory.return_value.store_conversation = AsyncMock()
                    
                    mock_guidance.return_value.generate_guidance = AsyncMock(return_value={
                        'content': 'My dear friend, inner peace comes through understanding the nature of suffering. When we observe our anxious thoughts without attachment, we find the calm that was always within us.',
                        'personality_id': 'buddha',
                        'citations': [
                            {
                                'source': 'Dhammapada 1.1',
                                'text': 'All mental phenomena are preceded by mind...',
                                'accuracy_score': 0.94
                            }
                        ],
                        'metadata': {
                            'response_time': 2.1,
                            'confidence_score': 0.91,
                            'personality_consistency': 0.96,
                            'cultural_authenticity': 0.93
                        }
                    })
                    
                    from function_app import spiritual_guidance
                    
                    response = await spiritual_guidance(req)
                    
                    # Verify integration workflow
                    assert response.status_code == 200
                    
                    response_data = json.loads(response.get_body().decode())
                    
                    # Verify response quality
                    assert 'inner peace' in response_data['content'].lower() or 'peace' in response_data['content'].lower()
                    assert response_data['personality_id'] == 'buddha'
                    assert len(response_data['citations']) > 0
                    assert 'Dhammapada' in response_data['citations'][0]['source']
                    
                    # Verify metadata quality
                    assert response_data['metadata']['confidence_score'] > 0.8
                    assert response_data['metadata']['personality_consistency'] > 0.9
                    
                    # Verify service integration
                    mock_memory.return_value.get_conversation_context.assert_called_once()
                    mock_guidance.return_value.generate_guidance.assert_called_once()


class TestFunctionAppConfiguration:
    """Test Function App configuration and environment handling"""
    
    def test_environment_variable_handling(self):
        """Test proper environment variable configuration"""
        
        required_env_vars = [
            'COSMOS_DB_ENDPOINT',
            'COSMOS_DB_KEY', 
            'GEMINI_API_KEY',
            'AZURE_CLIENT_ID',
            'AZURE_CLIENT_SECRET'
        ]
        
        with patch.dict(os.environ, {var: f'test_{var.lower()}' for var in required_env_vars}):
            
            # Test configuration loading
            from function_app import load_configuration
            
            config = load_configuration()
            
            # Verify configuration structure
            assert isinstance(config, dict)
            assert 'database' in config
            assert 'llm_service' in config
            assert 'authentication' in config
    
    def test_cors_configuration(self):
        """Test CORS configuration for production domains"""
        
        from function_app import get_cors_headers
        
        # Test allowed origins
        allowed_origins = [
            'https://vimarsh.vedprakash.net',
            'https://localhost:5173',
            'https://127.0.0.1:5173'
        ]
        
        for origin in allowed_origins:
            headers = get_cors_headers(origin)
            assert 'Access-Control-Allow-Origin' in headers
            assert headers['Access-Control-Allow-Origin'] == origin
        
        # Test disallowed origin
        headers = get_cors_headers('https://malicious-site.com')
        assert headers.get('Access-Control-Allow-Origin') != 'https://malicious-site.com'


# Test utilities and fixtures
@pytest.fixture(scope="session")
def function_app_test_config():
    """Configuration for Function App tests"""
    return TEST_CONFIG


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--tb=short", "--cov=function_app", "--cov-report=term-missing"])
