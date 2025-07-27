"""
Direct test runner for security validator (without pytest dependency)
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from auth.security_validator import (
    SecurityValidator,
    SecurityValidationError,
    RateLimiter,
    InputSanitizer,
    DataFilter,
    SecurityConfig
)


def test_rate_limiter():
    """Test rate limiting functionality"""
    print("🔄 Testing RateLimiter...")
    
    limiter = RateLimiter()
    identifier = "test_ip"
    
    # Test allows requests under limit
    for i in range(5):
        assert limiter.is_allowed(identifier, limit=10), f"Request {i} should be allowed"
    
    # Fill up to limit
    for i in range(5):
        limiter.is_allowed(identifier, limit=10)
    
    # Should block next request
    assert not limiter.is_allowed(identifier, limit=10), "Request over limit should be blocked"
    
    print("✅ RateLimiter tests passed")


def test_input_sanitizer():
    """Test input sanitization"""
    print("🔄 Testing InputSanitizer...")
    
    # Test basic sanitization
    result = InputSanitizer.sanitize_string("Hello <script>alert('xss')</script>")
    assert "&lt;script&gt;" in result, "XSS script should be escaped"
    assert "<script>" not in result, "Raw script tags should not remain"
    
    # Test length validation
    try:
        InputSanitizer.sanitize_string("a" * 20000, max_length=1000)
        assert False, "Long string should raise error"
    except SecurityValidationError as e:
        assert "too long" in str(e), "Error should mention length"
    
    # Test email validation
    valid_email = InputSanitizer.validate_email("Test@Example.COM")
    assert valid_email == "test@example.com", "Email should be normalized"
    
    try:
        InputSanitizer.validate_email("invalid-email")
        assert False, "Invalid email should raise error"
    except SecurityValidationError:
        pass  # Expected
    
    # Test UUID validation
    valid_uuid = InputSanitizer.validate_uuid("123E4567-E89B-12D3-A456-426614174000")
    assert valid_uuid == "123e4567-e89b-12d3-a456-426614174000", "UUID should be normalized"
    
    try:
        InputSanitizer.validate_uuid("not-a-uuid")
        assert False, "Invalid UUID should raise error"
    except SecurityValidationError:
        pass  # Expected
    
    print("✅ InputSanitizer tests passed")


def test_data_filter():
    """Test data filtering"""
    print("🔄 Testing DataFilter...")
    
    # Test sensitive data filtering
    data = {
        "user_id": "123",
        "password": "secret123",
        "api_key": "sk-1234567890",
        "safe_data": "this is safe"
    }
    
    result = DataFilter.filter_sensitive_data(data)
    
    assert result["user_id"] == "123", "Safe data should remain"
    assert result["password"] == "[REDACTED]", "Password should be redacted"
    assert result["api_key"] == "[REDACTED]", "API key should be redacted"
    assert result["safe_data"] == "this is safe", "Safe data should remain"
    
    # Test nested filtering
    nested_data = {
        "config": {
            "database": {
                "host": "localhost",
                "password": "secret"
            }
        }
    }
    
    result = DataFilter.filter_sensitive_data(nested_data)
    assert result["config"]["database"]["host"] == "localhost", "Safe nested data should remain"
    assert result["config"]["database"]["password"] == "[REDACTED]", "Nested password should be redacted"
    
    print("✅ DataFilter tests passed")


def test_security_validator():
    """Test main SecurityValidator"""
    print("🔄 Testing SecurityValidator...")
    
    validator = SecurityValidator()
    
    # Test basic request validation
    request_data = {
        "query": "What is dharma?",
        "userEmail": "test@example.com",
        "userId": "123e4567-e89b-12d3-a456-426614174000"
    }
    
    result = validator.validate_admin_request(request_data)
    
    assert "sanitized_data" in result, "Result should contain sanitized data"
    assert "jwt_payload" in result, "Result should contain JWT payload"
    assert "client_ip" in result, "Result should contain client IP"
    
    sanitized = result["sanitized_data"]
    assert "query" in sanitized, "Query should be sanitized"
    assert sanitized["userEmail"] == "test@example.com", "Email should be validated"
    
    # Test response filtering
    response_data = {
        "users": [
            {
                "id": "123",
                "password": "secret",
                "safe_field": "safe_value"
            }
        ]
    }
    
    filtered = validator.filter_admin_response(response_data)
    assert filtered["users"][0]["password"] == "[REDACTED]", "Password should be filtered"
    assert filtered["users"][0]["safe_field"] == "safe_value", "Safe field should remain"
    
    print("✅ SecurityValidator tests passed")


async def run_all_tests():
    """Run all security tests"""
    print("🚀 Starting Security Validator Tests")
    print("=" * 50)
    
    tests = [
        test_rate_limiter,
        test_input_sanitizer,
        test_data_filter,
        test_security_validator
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All security validator tests PASSED!")
        return 0
    else:
        print("❌ Some security validator tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
