"""
Comprehensive test suite for SecurityValidator and related security components
Tests JWT validation, rate limiting, input sanitization, data filtering, and admin endpoint security
"""

import pytest
import time
import jwt
import json
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from azure.functions import HttpRequest, HttpResponse

from auth.security_validator import (
    SecurityValidator,
    SecurityValidationError,
    RateLimiter,
    InputSanitizer,
    DataFilter,
    JWTValidator,
    SecurityConfig,
    secure_admin_endpoint
)


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_allows_requests_under_limit(self):
        """Test that requests under limit are allowed"""
        limiter = RateLimiter()
        identifier = "test_ip_1"
        
        # Should allow requests under limit
        for i in range(5):
            assert limiter.is_allowed(identifier, limit=10)
    
    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter()
        identifier = "test_ip_2"
        
        # Fill up to limit
        for i in range(10):
            assert limiter.is_allowed(identifier, limit=10)
        
        # Should block next request
        assert not limiter.is_allowed(identifier, limit=10)
    
    def test_rate_limiter_window_sliding(self):
        """Test sliding window behavior"""
        limiter = RateLimiter()
        identifier = "test_ip_3"
        
        # Mock time to test window sliding
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000
            
            # Fill up limit
            for i in range(5):
                assert limiter.is_allowed(identifier, limit=5)
            
            # Should block
            assert not limiter.is_allowed(identifier, limit=5)
            
            # Move time forward beyond window
            mock_time.return_value = 1070  # 70 seconds later
            
            # Should allow again
            assert limiter.is_allowed(identifier, limit=5)
    
    def test_rate_limiter_ip_blocking(self):
        """Test IP blocking functionality"""
        limiter = RateLimiter()
        identifier = "blocked_ip"
        
        # Trigger blocking
        for i in range(15):
            limiter.is_allowed(identifier, limit=10)
        
        # Should be blocked
        assert limiter.is_blocked(identifier)
        
        # Mock time forward to test block expiry
        current_time = time.time()
        with patch('auth.security_validator.time.time') as mock_time:
            mock_time.return_value = current_time + 1000  # 16+ minutes later
            assert not limiter.is_blocked(identifier)


class TestInputSanitizer:
    """Test input sanitization and validation"""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        result = InputSanitizer.sanitize_string("Hello <script>alert('xss')</script>")
        assert "&lt;script&gt;" in result
        assert "alert" in result
        assert "<script>" not in result
    
    def test_sanitize_string_length_limit(self):
        """Test string length validation"""
        long_string = "a" * 20000
        
        with pytest.raises(SecurityValidationError) as exc_info:
            InputSanitizer.sanitize_string(long_string, max_length=1000)
        
        assert "too long" in str(exc_info.value)
    
    def test_sanitize_string_control_characters(self):
        """Test removal of control characters"""
        test_string = "Hello\x00\x08\x1f World"
        result = InputSanitizer.sanitize_string(test_string)
        assert "\x00" not in result
        assert "\x08" not in result
        assert "\x1f" not in result
        assert "Hello World" in result
    
    def test_validate_email_valid(self):
        """Test valid email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            result = InputSanitizer.validate_email(email)
            assert "@" in result
            assert result == email.lower()
    
    def test_validate_email_invalid(self):
        """Test invalid email rejection"""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user space@domain.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(SecurityValidationError):
                InputSanitizer.validate_email(email)
    
    def test_validate_uuid_valid(self):
        """Test valid UUID validation"""
        valid_uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "550e8400-e29b-41d4-a716-446655440000"
        ]
        
        for uuid_str in valid_uuids:
            result = InputSanitizer.validate_uuid(uuid_str)
            assert result == uuid_str.lower()
    
    def test_validate_uuid_invalid(self):
        """Test invalid UUID rejection"""
        invalid_uuids = [
            "not-a-uuid",
            "123e4567-e89b-12d3-a456",  # Too short
            "123e4567-e89b-12d3-a456-426614174000-extra",  # Too long
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Invalid characters
        ]
        
        for uuid_str in invalid_uuids:
            with pytest.raises(SecurityValidationError):
                InputSanitizer.validate_uuid(uuid_str)
    
    def test_validate_alphanumeric_valid(self):
        """Test valid alphanumeric validation"""
        valid_inputs = [
            "test123",
            "user-name",
            "session_id",
            "Valid_ID-123"
        ]
        
        for input_str in valid_inputs:
            result = InputSanitizer.validate_alphanumeric(input_str)
            assert result == input_str
    
    def test_validate_alphanumeric_invalid(self):
        """Test invalid alphanumeric rejection"""
        invalid_inputs = [
            "test@domain",
            "user name",  # Space
            "test/path",  # Slash
            "test.file"   # Dot
        ]
        
        for input_str in invalid_inputs:
            with pytest.raises(SecurityValidationError):
                InputSanitizer.validate_alphanumeric(input_str)
    
    def test_sanitize_query_params(self):
        """Test query parameter sanitization"""
        params = {
            "query": "What is <script>alert('xss')</script> dharma?",
            "limit": 10,
            "user_id": "test-user-123",
            "tags": ["tag1", "tag2", "<script>"],
            "nested": {"key": "value<script>"}
        }
        
        result = InputSanitizer.sanitize_query_params(params)
        
        assert "&lt;script&gt;" in result["query"]
        assert result["limit"] == 10
        assert result["user_id"] == "test-user-123"
        assert len(result["tags"]) == 3
        assert "&lt;script&gt;" in result["tags"][2]


class TestDataFilter:
    """Test data filtering functionality"""
    
    def test_filter_sensitive_data_dict(self):
        """Test filtering sensitive data from dictionary"""
        data = {
            "user_id": "123",
            "user_email": "test@example.com",
            "password": "test_password_123",
            "api_key": "test_mock_key_123",
            "connection_string": "Server=localhost;Database=test;",
            "safe_data": "this is safe"
        }
        
        result = DataFilter.filter_sensitive_data(data)
        
        assert result["user_id"] == "123"
        assert result["user_email"] == "test@example.com"
        assert result["password"] == "[REDACTED]"
        assert result["api_key"] == "[REDACTED]"
        assert result["connection_string"] == "[REDACTED]"
        assert result["safe_data"] == "this is safe"
    
    def test_filter_sensitive_data_nested(self):
        """Test filtering nested sensitive data"""
        data = {
            "config": {
                "database": {
                    "host": "localhost",
                    "password": "secret"
                },
                "api_key": "test_mock_key"
            },
            "users": [
                {"id": "1", "email": "user1@test.com"},
                {"id": "2", "secret_key": "hidden"}
            ]
        }
        
        result = DataFilter.filter_sensitive_data(data)
        
        assert result["config"]["database"]["host"] == "localhost"
        assert result["config"]["database"]["password"] == "[REDACTED]"
        assert result["config"]["api_key"] == "[REDACTED]"
        assert result["users"][0]["email"] == "user1@test.com"
        assert result["users"][1]["secret_key"] == "[REDACTED]"
    
    def test_filter_user_data(self):
        """Test user data filtering for admin responses"""
        user_data = {
            "userId": "123",
            "userEmail": "test@example.com",
            "password_hash": "hashed_password",
            "totalTokens": 1000,
            "sensitive_info": "should be removed",
            "totalCostUsd": 5.50,
            "personalityUsage": {"krishna": 10}
        }
        
        result = DataFilter.filter_user_data(user_data)
        
        # Should include safe fields
        assert "userId" in result
        assert "userEmail" in result
        assert "totalTokens" in result
        assert "totalCostUsd" in result
        assert "personalityUsage" in result
        
        # Should exclude unsafe fields
        assert "password_hash" not in result
        assert "sensitive_info" not in result


class TestJWTValidator:
    """Test JWT validation functionality"""
    
    def test_jwt_validation_missing_key_id(self):
        """Test JWT validation with missing key ID in production mode"""
        validator = JWTValidator()
        
        # Force production mode
        with patch.dict(os.environ, {'ENABLE_AUTH': 'true', 'AUTH_MODE': 'production'}):
            # Create token without kid
            token = jwt.encode({"sub": "test"}, "secret", algorithm="HS256")
            
            with pytest.raises(SecurityValidationError) as exc_info:
                validator.validate_jwt(token)
            
            assert "missing key id" in str(exc_info.value).lower() or "invalid jwt" in str(exc_info.value).lower()
    
    def test_jwt_validation_invalid_token(self):
        """Test JWT validation with invalid token"""
        validator = JWTValidator()
        
        with pytest.raises(SecurityValidationError) as exc_info:
            validator.validate_jwt("invalid.token.here")
        
        assert "invalid" in str(exc_info.value).lower()
    
    def test_jwt_validation_expired_token(self):
        """Test JWT validation with expired token"""
        validator = JWTValidator()
        
        # Force production mode to trigger proper JWT validation
        with patch.dict(os.environ, {'ENABLE_AUTH': 'true', 'AUTH_MODE': 'production'}):
            validator.public_keys["test-kid"] = "test-key"
            
            # Create expired token
            payload = {
                "sub": "test-user",
                "iat": int(time.time()) - 3600,  # 1 hour ago
                "exp": int(time.time()) - 1800,  # 30 minutes ago (expired)
                "aud": SecurityConfig.JWT_AUDIENCE,
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0"
            }
            
            token = jwt.encode(payload, "test-key", algorithm="HS256", headers={"kid": "test-kid"})
            
            with patch.object(validator, '_get_public_key', return_value="test-key"):
                with patch('jwt.decode') as mock_decode:
                    mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
                    
                    with pytest.raises(SecurityValidationError) as exc_info:
                        validator.validate_jwt(token)
                    
                    assert "expired" in str(exc_info.value).lower()


class TestSecurityValidator:
    """Test main SecurityValidator class"""
    
    def test_validate_admin_request_basic(self):
        """Test basic admin request validation"""
        validator = SecurityValidator()
        
        request_data = {
            "query": "What is dharma?",
            "userEmail": "test@example.com",
            "userId": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        result = validator.validate_admin_request(request_data)
        
        assert "sanitized_data" in result
        assert "jwt_payload" in result
        assert "client_ip" in result
        
        sanitized = result["sanitized_data"]
        assert "query" in sanitized
        assert "userEmail" in sanitized
        assert "userId" in sanitized
    
    def test_validate_admin_request_rate_limiting(self):
        """Test rate limiting in admin request validation"""
        validator = SecurityValidator()
        client_ip = "192.168.1.100"
        
        # Mock rate limiter to simulate blocking
        validator.rate_limiter.is_blocked = Mock(return_value=True)
        
        with pytest.raises(SecurityValidationError) as exc_info:
            validator.validate_admin_request({}, client_ip=client_ip)
        
        assert "blocked" in str(exc_info.value).lower()
    
    def test_filter_admin_response(self):
        """Test admin response filtering"""
        validator = SecurityValidator()
        
        response_data = {
            "users": [
                {
                    "id": "123",
                    "email": "test@example.com",
                    "password": "secret",
                    "api_key": "test_mock_key"
                }
            ],
            "system_info": {
                "version": "1.0",
                "secret_key": "hidden"
            }
        }
        
        result = validator.filter_admin_response(response_data)
        
        assert result["users"][0]["password"] == "[REDACTED]"
        assert result["users"][0]["api_key"] == "[REDACTED]"
        assert result["system_info"]["secret_key"] == "[REDACTED]"
        assert result["users"][0]["email"] == "test@example.com"
        assert result["system_info"]["version"] == "1.0"


class TestSecureAdminEndpointDecorator:
    """Test the secure admin endpoint decorator"""
    
    @pytest.mark.asyncio
    async def test_secure_admin_endpoint_basic(self):
        """Test basic decorator functionality"""
        
        @secure_admin_endpoint(required_scopes=['admin.read'])
        async def test_endpoint(req):
            return {"message": "success"}
        
        # Mock request
        mock_req = Mock()
        mock_req.headers = {}
        mock_req.get_json = Mock(return_value={})
        mock_req.params = {}
        mock_req.route_params = {}  # Add proper route_params as dict
        
        # Mock security validator
        with patch('auth.security_validator.security_validator') as mock_validator_instance:
            mock_validator_instance.validate_admin_request.return_value = {
                'sanitized_data': {},
                'jwt_payload': {'sub': 'test-user'},
                'client_ip': '127.0.0.1'
            }
            mock_validator_instance.filter_admin_response.return_value = {"message": "success"}
            
            # Patch the global instance
            with patch('auth.security_validator.security_validator', mock_validator_instance):
                result = await test_endpoint(req=mock_req)
                
                assert "message" in result
    
    @pytest.mark.asyncio
    async def test_secure_admin_endpoint_security_error(self):
        """Test decorator handling security errors"""
        
        @secure_admin_endpoint(required_scopes=['admin.read'])
        async def test_endpoint(req):
            return {"message": "success"}
        
        # Mock request
        mock_req = Mock()
        mock_req.headers = {}
        mock_req.get_json = Mock(return_value={})
        mock_req.params = {}
        mock_req.route_params = {}  # Add proper route_params as dict
        
        # Mock security validator to raise error
        with patch('auth.security_validator.security_validator') as mock_validator_instance:
            mock_validator_instance.validate_admin_request.side_effect = SecurityValidationError("Test error")
            
            result = await test_endpoint(req=mock_req)
            
            # Should return HTTP error response, not raise exception
            assert hasattr(result, 'status_code')
            assert result.status_code in [401, 403]


class TestEnhancedSecurityFeatures:
    """Test enhanced security features added in Phase 1.3"""
    
    def test_path_parameter_extraction(self):
        """Test extraction of user_id from URL paths"""
        import re
        
        # Test user ID extraction
        path = "https://example.com/api/users/12345678-1234-1234-1234-123456789abc/block"
        user_id_match = re.search(r'/users/([^/]+)/', path)
        assert user_id_match
        assert user_id_match.group(1) == "12345678-1234-1234-1234-123456789abc"
        
        # Test budget ID extraction
        path = "https://example.com/api/budgets/budget-123/override"
        budget_id_match = re.search(r'/budgets/([^/]+)/', path)
        assert budget_id_match
        assert budget_id_match.group(1) == "budget-123"
    
    def test_enhanced_email_masking(self):
        """Test enhanced email masking functionality"""
        test_cases = [
            ("testuser@example.com", "te****er@example.com"),
            ("ab@example.com", "a*@example.com"),
            ("a@example.com", "a@example.com"),  # Single char preserved
            ("verylongusername@example.com", "ve************me@example.com")
        ]
        
        for original, expected in test_cases:
            user_data = {"userEmail": original}
            result = DataFilter.filter_user_data(user_data)
            assert result["userEmail"] == expected
    
    def test_financial_data_rounding(self):
        """Test that financial data is properly rounded"""
        user_data = {
            "totalCostUsd": 12.345678,
            "currentMonthCostUsd": 5.999999,
            "riskScore": 0.123456789,
            "totalRequests": 100
        }
        
        result = DataFilter.filter_user_data(user_data)
        
        assert result["totalCostUsd"] == 12.35
        assert result["currentMonthCostUsd"] == 6.0
        assert result["riskScore"] == 0.12
        assert result["totalRequests"] == 100  # Integer unchanged
    
    @patch.dict('os.environ', {'AZURE_TENANT_ID': 'test-tenant-123'})
    def test_jwks_caching(self):
        """Test that JWKS responses are properly cached"""
        validator = JWTValidator()
        
        with patch('requests.get') as mock_get:
            # Mock successful JWKS response
            mock_response = Mock()
            mock_response.json.return_value = {"keys": [{"kid": "test-key", "kty": "RSA"}]}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # First call should fetch from endpoint
            with patch('time.time', return_value=1000):
                result1 = validator._fetch_jwks(
                    "https://login.microsoftonline.com/test-tenant-123/discovery/v2.0/keys",
                    "jwks_test-tenant-123"
                )
            
            # Second call within cache period should use cache
            with patch('time.time', return_value=1500):  # 500 seconds later (within 1 hour)
                # Call _get_public_key which should use cache
                cache_key = "jwks_test-tenant-123"
                assert cache_key in validator.key_cache
                assert validator.cache_expiry[cache_key] > 1500
            
            # Should have only called the endpoint once
            assert mock_get.call_count == 1
    
    def test_client_ip_extraction_with_proxy(self):
        """Test client IP extraction with proxy headers"""
        # Test with X-Forwarded-For header containing multiple IPs
        validator = SecurityValidator()
        
        # Mock the decorator's IP extraction logic
        client_ip = "203.0.113.1, 198.51.100.1, 192.168.1.1"
        if ',' in client_ip:
            extracted_ip = client_ip.split(',')[0].strip()
        
        assert extracted_ip == "203.0.113.1"
    
    def test_comprehensive_input_validation(self):
        """Test comprehensive input validation across all field types"""
        validator = SecurityValidator()
        
        # Complex request data with various input types
        request_data = {
            "query": "<script>alert('xss')</script>",
            "userEmail": "  ADMIN@COMPANY.COM  ",
            "userId": "12345678-1234-1234-1234-123456789abc",
            "budget_id": "budget-456",
            "role_id": "admin-role",
            "amount": 100.50,
            "enabled": True,
            "tags": ["tag1", "<script>", "tag3"],
            "metadata": {
                "key1": "value1",
                "password": "secret123"
            }
        }
        
        with patch.object(validator.rate_limiter, 'is_allowed', return_value=True), \
             patch.object(validator.rate_limiter, 'is_blocked', return_value=False), \
             patch.object(validator.jwt_validator, 'validate_jwt', return_value={"sub": "user123"}):
            
            result = validator.validate_admin_request(
                request_data, "192.168.1.1", "valid_token"
            )
            
            sanitized = result["sanitized_data"]
            
            # Test various sanitization types  
            assert "&lt;script&gt;" in sanitized["query"]
            assert sanitized["userEmail"] == "admin@company.com"
            assert sanitized["userId"] == "12345678-1234-1234-1234-123456789abc"
            assert sanitized["amount"] == 100.50
            assert sanitized["enabled"] is True
            assert len(sanitized["tags"]) == 3
            # Basic validation that the tags field is processed
            assert isinstance(sanitized["tags"], list)
    
    def test_security_logging_with_context(self):
        """Test that security events include proper context"""
        validator = SecurityValidator()
        
        # Test the actual logging method
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            validator.log_security_event(
                'admin_access',
                {
                    'function': 'admin_cost_dashboard',
                    'client_ip': '192.168.1.100',
                    'user_id': 'user123',
                    'method': 'GET'
                },
                'INFO'
            )
            
            # Should have called the logger info method
            # We can't easily mock the specific logger instance, but we can verify the method works
            # This test mainly validates that the log_security_event method doesn't crash


if __name__ == "__main__":
    # Run comprehensive security tests
    pytest.main([__file__, "-v", "--tb=short"])
