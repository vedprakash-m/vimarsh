"""
Unified Security Validator for Vimarsh
Provides comprehensive security validation for all admin operations
Addresses JWT validation, input sanitization, rate limiting, and data filtering
"""

import logging
import re
import time
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from functools import wraps
import jwt
import hashlib
from collections import defaultdict
import html
from azure.functions import HttpResponse

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration constants"""
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per minute
    ADMIN_RATE_LIMIT = 50     # requests per minute for admin operations
    AUTH_RATE_LIMIT = 20      # requests per minute for auth operations
    
    # JWT validation
    JWT_ALGORITHM = "RS256"
    JWT_AUDIENCE = "vimarsh-admin"
    JWT_ISSUER_PATTERN = r"https://login\.microsoftonline\.com/[a-f0-9-]+/v2\.0"
    
    # Input validation
    MAX_INPUT_LENGTH = 10000
    MAX_QUERY_LENGTH = 1000
    MAX_EMAIL_LENGTH = 254
    
    # Sensitive data patterns
    SENSITIVE_PATTERNS = [
        r'(?i)(password|secret|key|token)',
        r'(?i)(api[_-]?key)',
        r'(?i)(connection[_-]?string)',
        r'(?i)(private[_-]?key)',
    ]
    
    # Allowed characters for different input types
    ALPHANUMERIC_PATTERN = r'^[a-zA-Z0-9_-]+$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'


class SecurityValidationError(Exception):
    """Raised when security validation fails"""
    def __init__(self, message: str, error_code: str = "SECURITY_VIOLATION"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class RateLimiter:
    """Rate limiting implementation with sliding window"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = defaultdict(list)
    
    def is_allowed(self, identifier: str, limit: int = SecurityConfig.DEFAULT_RATE_LIMIT, 
                   window_minutes: int = 1) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()
        window_start = now - (window_minutes * 60)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) >= limit:
            # Block IP temporarily
            self.blocked_ips[identifier].append(now)
            logger.warning(f"⚠️ Rate limit exceeded for {identifier}: {len(self.requests[identifier])} requests")
            return False
        
        # Record request
        self.requests[identifier].append(now)
        return True
    
    def is_blocked(self, identifier: str, block_duration_minutes: int = 15) -> bool:
        """Check if IP is temporarily blocked"""
        if identifier not in self.blocked_ips:
            return False
        
        now = time.time()
        block_cutoff = now - (block_duration_minutes * 60)
        
        # Clean old blocks
        self.blocked_ips[identifier] = [
            block_time for block_time in self.blocked_ips[identifier]
            if block_time > block_cutoff
        ]
        
        return len(self.blocked_ips[identifier]) > 0


class InputSanitizer:
    """Input sanitization and validation"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = SecurityConfig.MAX_INPUT_LENGTH) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise SecurityValidationError("Input must be a string")
        
        # Length check
        if len(value) > max_length:
            raise SecurityValidationError(f"Input too long: {len(value)} > {max_length}")
        
        # HTML escape
        sanitized = html.escape(value)
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate and sanitize email"""
        if not email:
            raise SecurityValidationError("Email is required")
        
        email = email.strip().lower()
        
        if len(email) > SecurityConfig.MAX_EMAIL_LENGTH:
            raise SecurityValidationError("Email too long")
        
        if not re.match(SecurityConfig.EMAIL_PATTERN, email):
            raise SecurityValidationError("Invalid email format")
        
        return email
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> str:
        """Validate UUID format"""
        if not uuid_str:
            raise SecurityValidationError("UUID is required")
        
        uuid_str = uuid_str.strip().lower()
        
        if not re.match(SecurityConfig.UUID_PATTERN, uuid_str):
            raise SecurityValidationError("Invalid UUID format")
        
        return uuid_str
    
    @staticmethod
    def validate_alphanumeric(value: str, field_name: str = "field") -> str:
        """Validate alphanumeric input"""
        if not value:
            raise SecurityValidationError(f"{field_name} is required")
        
        value = value.strip()
        
        if not re.match(SecurityConfig.ALPHANUMERIC_PATTERN, value):
            raise SecurityValidationError(f"Invalid {field_name}: only alphanumeric characters, hyphens, and underscores allowed")
        
        return value
    
    @staticmethod
    def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize query parameters"""
        sanitized = {}
        
        for key, value in params.items():
            # Sanitize key
            clean_key = InputSanitizer.sanitize_string(key, 50)
            
            if isinstance(value, str):
                # Sanitize string values
                sanitized[clean_key] = InputSanitizer.sanitize_string(
                    value, SecurityConfig.MAX_QUERY_LENGTH
                )
            elif isinstance(value, (int, float, bool)):
                # Allow numeric and boolean values
                sanitized[clean_key] = value
            elif isinstance(value, list):
                # Sanitize list items
                sanitized[clean_key] = [
                    InputSanitizer.sanitize_string(str(item), 100) 
                    for item in value[:10]  # Limit list size
                ]
            else:
                # Convert other types to string and sanitize
                sanitized[clean_key] = InputSanitizer.sanitize_string(str(value), 100)
        
        return sanitized


class DataFilter:
    """Filter sensitive data from responses"""
    
    @staticmethod
    def filter_sensitive_data(data: Any) -> Any:
        """Remove sensitive data from response"""
        if isinstance(data, dict):
            return DataFilter._filter_dict(data)
        elif isinstance(data, list):
            return [DataFilter.filter_sensitive_data(item) for item in data]
        else:
            return data
    
    @staticmethod
    def _filter_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive fields from dictionary"""
        filtered = {}
        
        for key, value in data.items():
            # Check if key contains sensitive patterns
            is_sensitive = any(
                re.search(pattern, key, re.IGNORECASE)
                for pattern in SecurityConfig.SENSITIVE_PATTERNS
            )
            
            # Additional sensitive field patterns
            sensitive_keywords = [
                'jwt', 'bearer', 'authorization', 'credentials', 'private',
                'internal', 'debug', 'trace', 'stack', 'error_detail'
            ]
            
            is_admin_sensitive = any(
                keyword in key.lower() for keyword in sensitive_keywords
            )
            
            if is_sensitive or is_admin_sensitive:
                filtered[key] = "[REDACTED]"
            elif isinstance(value, dict):
                filtered[key] = DataFilter._filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [DataFilter.filter_sensitive_data(item) for item in value]
            else:
                filtered[key] = value
        
        return filtered
    
    @staticmethod
    def filter_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter user data for admin responses with enhanced security"""
        # Only include safe fields for admin dashboard
        safe_fields = {
            'userId', 'userEmail', 'totalRequests', 'totalTokens', 
            'totalCostUsd', 'currentMonthTokens', 'currentMonthCostUsd',
            'lastRequest', 'avgTokensPerRequest', 'favoriteModel',
            'personalityUsage', 'qualityBreakdown', 'riskScore', 'isBlocked',
            'accountStatus', 'role', 'createdAt', 'lastActive'
        }
        
        filtered_data = {}
        for key, value in user_data.items():
            if key in safe_fields:
                # Additional filtering for specific fields
                if key == 'userEmail':
                    # Partially mask email for privacy
                    if isinstance(value, str) and '@' in value:
                        parts = value.split('@')
                        if len(parts[0]) > 3:
                            masked_local = parts[0][:2] + '*' * (len(parts[0]) - 4) + parts[0][-2:]
                        else:
                            masked_local = parts[0][:1] + '*' * (len(parts[0]) - 1)
                        filtered_data[key] = f"{masked_local}@{parts[1]}"
                    else:
                        filtered_data[key] = value
                elif key in ['riskScore', 'totalCostUsd', 'currentMonthCostUsd']:
                    # Round financial and risk data
                    if isinstance(value, (int, float)):
                        filtered_data[key] = round(value, 2)
                    else:
                        filtered_data[key] = value
                else:
                    filtered_data[key] = value
        
        return filtered_data
    
    @staticmethod
    def filter_system_data(system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter system health data for admin responses"""
        # Remove internal system details
        filtered = DataFilter.filter_sensitive_data(system_data)
        
        # Remove debug information
        debug_keys = ['debug', 'trace', 'internal', 'raw_data', 'stack_trace']
        for key in debug_keys:
            if key in filtered:
                del filtered[key]
        
        return filtered


class JWTValidator:
    """Unified JWT validation"""
    
    def __init__(self, public_keys: Dict[str, str] = None):
        self.public_keys = public_keys or {}
        self.key_cache = {}
        self.cache_expiry = {}
    
    def validate_jwt(self, token: str, required_scopes: List[str] = None) -> Dict[str, Any]:
        """Validate JWT token with comprehensive checks"""
        try:
            # Check if we're in development mode
            enable_auth = os.getenv("ENABLE_AUTH", "false").lower() == "true"
            auth_mode = os.getenv("AUTH_MODE", "development").lower()
            
            if not enable_auth or auth_mode == "development":
                return self._validate_development_jwt(token, required_scopes)
            
            # Production mode - full JWT validation
            return self._validate_production_jwt(token, required_scopes)
            
        except jwt.ExpiredSignatureError:
            raise SecurityValidationError("JWT token expired", "TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            raise SecurityValidationError(f"Invalid JWT token: {e}", "INVALID_JWT")
    
    def _validate_development_jwt(self, token: str, required_scopes: List[str] = None) -> Dict[str, Any]:
        """Validate JWT in development mode with relaxed validation"""
        try:
            # For development, we accept certain test tokens or decode without signature verification
            if token in ["dev-token", "admin-token", "test-token"]:
                return {
                    "sub": f"dev-{token}",
                    "email": f"dev@vimarsh.local",
                    "name": "Development User",
                    "scp": " ".join(required_scopes) if required_scopes else "admin.read admin.users admin.budget",
                    "iss": "https://login.microsoftonline.com/dev-tenant/v2.0",
                    "aud": SecurityConfig.JWT_AUDIENCE,
                    "iat": int(time.time()),
                    "exp": int(time.time()) + 3600
                }
            
            # Try to decode as JWT without signature verification
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Add required scopes if missing
            if required_scopes and 'scp' not in payload:
                payload['scp'] = " ".join(required_scopes)
            
            logger.info("✅ Development JWT validated (signature verification skipped)")
            return payload
            
        except Exception as e:
            logger.warning(f"⚠️ Development JWT validation failed: {e}")
            raise SecurityValidationError("Invalid development JWT", "INVALID_DEV_JWT")
    
    def _validate_production_jwt(self, token: str, required_scopes: List[str] = None) -> Dict[str, Any]:
        """Validate JWT in production mode with full signature verification"""
        # Parse header to get key ID
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        
        if not kid:
            raise SecurityValidationError("JWT missing key ID", "INVALID_JWT")
        
        # Get public key
        public_key = self._get_public_key(kid)
        
        # Validate token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[SecurityConfig.JWT_ALGORITHM],
            audience=SecurityConfig.JWT_AUDIENCE,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True
            }
        )
        
        # Validate issuer pattern
        issuer = payload.get('iss', '')
        if not re.match(SecurityConfig.JWT_ISSUER_PATTERN, issuer):
            raise SecurityValidationError("Invalid JWT issuer", "INVALID_ISSUER")
        
        # Validate required scopes
        if required_scopes:
            token_scopes = payload.get('scp', '').split()
            missing_scopes = set(required_scopes) - set(token_scopes)
            if missing_scopes:
                raise SecurityValidationError(
                    f"Missing required scopes: {missing_scopes}", 
                    "INSUFFICIENT_SCOPE"
                )
        
        # Additional security checks
        self._validate_token_claims(payload)
        
        return payload
    
    def _get_public_key(self, kid: str) -> str:
        """Get public key for JWT validation from Microsoft Entra ID JWKS endpoint"""
        if kid in self.public_keys:
            return self.public_keys[kid]
        
        # Get tenant ID from environment
        tenant_id = os.getenv("AZURE_TENANT_ID")
        if not tenant_id:
            logger.warning("⚠️ AZURE_TENANT_ID not configured, using development mode")
            # In development mode, return a placeholder that will be validated differently
            return "DEV_MODE_PLACEHOLDER"
        
        try:
            # Fetch JWKS from Microsoft Entra ID
            import requests
            jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
            
            # Check cache first
            cache_key = f"jwks_{tenant_id}"
            if cache_key in self.key_cache:
                cache_expiry = self.cache_expiry.get(cache_key, 0)
                if time.time() < cache_expiry:
                    jwks_data = self.key_cache[cache_key]
                else:
                    # Cache expired, fetch new keys
                    jwks_data = self._fetch_jwks(jwks_url, cache_key)
            else:
                jwks_data = self._fetch_jwks(jwks_url, cache_key)
            
            # Find the key with matching kid
            for key_data in jwks_data.get("keys", []):
                if key_data.get("kid") == kid:
                    # Convert JWK to PEM format
                    from jwt.algorithms import RSAAlgorithm
                    public_key = RSAAlgorithm.from_jwk(json.dumps(key_data))
                    self.public_keys[kid] = public_key
                    return public_key
            
            raise SecurityValidationError(f"Public key not found for kid: {kid}", "KEY_NOT_FOUND")
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch public key: {e}")
            raise SecurityValidationError("Public key retrieval failed", "KEY_FETCH_FAILED")
    
    def _fetch_jwks(self, jwks_url: str, cache_key: str) -> Dict[str, Any]:
        """Fetch JWKS from Microsoft endpoint with caching"""
        try:
            import requests
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            jwks_data = response.json()
            
            # Cache for 1 hour
            self.key_cache[cache_key] = jwks_data
            self.cache_expiry[cache_key] = time.time() + 3600
            
            logger.info(f"✅ Successfully fetched JWKS from {jwks_url}")
            return jwks_data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch JWKS: {e}")
            raise
    
    def _validate_token_claims(self, payload: Dict[str, Any]):
        """Additional validation of token claims"""
        # Check required claims
        required_claims = ['sub', 'iat', 'exp', 'aud', 'iss']
        missing_claims = [claim for claim in required_claims if claim not in payload]
        if missing_claims:
            raise SecurityValidationError(
                f"Missing required claims: {missing_claims}",
                "MISSING_CLAIMS"
            )
        
        # Validate subject
        sub = payload.get('sub')
        if not sub or len(sub) < 10:
            raise SecurityValidationError("Invalid subject claim", "INVALID_SUBJECT")
        
        # Check token age (not too old)
        iat = payload.get('iat', 0)
        now = time.time()
        if now - iat > 24 * 3600:  # 24 hours
            raise SecurityValidationError("Token too old", "TOKEN_TOO_OLD")


class SecurityValidator:
    """Main security validator combining all security checks"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.jwt_validator = JWTValidator()
        self.input_sanitizer = InputSanitizer()
        self.data_filter = DataFilter()
    
    def validate_admin_request(self, request_data: Dict[str, Any], 
                             client_ip: str = None, jwt_token: str = None,
                             required_scopes: List[str] = None) -> Dict[str, Any]:
        """Comprehensive validation for admin requests"""
        
        # Rate limiting
        if client_ip:
            if self.rate_limiter.is_blocked(client_ip):
                raise SecurityValidationError("IP temporarily blocked", "IP_BLOCKED")
            
            if not self.rate_limiter.is_allowed(client_ip, SecurityConfig.ADMIN_RATE_LIMIT):
                raise SecurityValidationError("Rate limit exceeded", "RATE_LIMIT_EXCEEDED")
        
        # JWT validation
        jwt_payload = None
        if jwt_token:
            jwt_payload = self.jwt_validator.validate_jwt(jwt_token, required_scopes)
        
        # Input sanitization
        sanitized_data = {}
        for key, value in request_data.items():
            if key == 'query' and isinstance(value, str):
                sanitized_data[key] = self.input_sanitizer.sanitize_string(
                    value, SecurityConfig.MAX_QUERY_LENGTH
                )
            elif key == 'userEmail' and isinstance(value, str):
                sanitized_data[key] = self.input_sanitizer.validate_email(value)
            elif key in ['userId', 'sessionId'] and isinstance(value, str):
                sanitized_data[key] = self.input_sanitizer.validate_uuid(value)
            elif isinstance(value, str):
                sanitized_data[key] = self.input_sanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized_data[key] = self.input_sanitizer.sanitize_query_params(value)
            else:
                sanitized_data[key] = value
        
        return {
            'sanitized_data': sanitized_data,
            'jwt_payload': jwt_payload,
            'client_ip': client_ip
        }
    
    def filter_admin_response(self, response_data: Any) -> Any:
        """Filter sensitive data from admin responses"""
        return self.data_filter.filter_sensitive_data(response_data)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          severity: str = "INFO"):
        """Log security-related events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': self.data_filter.filter_sensitive_data(details)
        }
        
        if severity == "ERROR":
            logger.error(f"🚨 Security Event: {json.dumps(log_entry)}")
        elif severity == "WARNING":
            logger.warning(f"⚠️ Security Event: {json.dumps(log_entry)}")
        else:
            logger.info(f"🔒 Security Event: {json.dumps(log_entry)}")


# Global security validator instance
security_validator = SecurityValidator()


def secure_admin_endpoint(required_scopes: List[str] = None, 
                         rate_limit: int = SecurityConfig.ADMIN_RATE_LIMIT):
    """Decorator for securing admin endpoints with comprehensive validation"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request information
            request = kwargs.get('req') or (args[0] if args else None)
            
            if not request:
                raise SecurityValidationError("Request object not found", "NO_REQUEST")
            
            # Get client IP
            client_ip = request.headers.get('X-Forwarded-For', 
                                          request.headers.get('X-Real-IP', 'unknown'))
            if ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            # Get JWT token
            auth_header = request.headers.get('Authorization', '')
            jwt_token = None
            if auth_header.startswith('Bearer '):
                jwt_token = auth_header[7:]
            
            # Get request data from multiple sources
            request_data = {}
            
            # JSON body data
            if hasattr(request, 'get_json'):
                try:
                    json_data = request.get_json()
                    if json_data:
                        request_data.update(json_data)
                except Exception:
                    pass
            
            # Query parameters
            if hasattr(request, 'params'):
                request_data.update(dict(request.params))
            
            # Route parameters
            if hasattr(request, 'route_params'):
                request_data.update(dict(request.route_params))
            
            # Path parameters (user_id, session_id, etc.)
            try:
                import re
                path = request.url
                # Extract user_id from paths like /users/{user_id}/block
                user_id_match = re.search(r'/users/([^/]+)/', path)
                if user_id_match:
                    request_data['user_id'] = user_id_match.group(1)
                
                # Extract other common path parameters
                budget_id_match = re.search(r'/budgets/([^/]+)/', path)
                if budget_id_match:
                    request_data['budget_id'] = budget_id_match.group(1)
                    
                role_id_match = re.search(r'/roles/([^/]+)/', path)
                if role_id_match:
                    request_data['role_id'] = role_id_match.group(1)
                    
            except Exception as e:
                logger.debug(f"Could not extract path parameters: {e}")
            
            try:
                # Validate request
                validation_result = security_validator.validate_admin_request(
                    request_data, client_ip, jwt_token, required_scopes
                )
                
                # Add validation result to request for use in endpoint
                if hasattr(request, 'route_params'):
                    request.route_params['security_context'] = validation_result
                else:
                    # Fallback - add to kwargs
                    kwargs['security_context'] = validation_result
                
                # Log security event before calling function
                security_validator.log_security_event(
                    'admin_request',
                    {
                        'function': func.__name__,
                        'method': request.method,
                        'client_ip': client_ip,
                        'user_id': (validation_result.get('jwt_payload') or {}).get('sub'),
                        'scopes': required_scopes,
                        'request_size': len(str(request_data))
                    }
                )
                
                # Call original function
                result = await func(*args, **kwargs)
                
                # Filter response data
                if isinstance(result, dict) and 'data' in result:
                    result['data'] = security_validator.filter_admin_response(result['data'])
                elif hasattr(result, 'get_body'):
                    # Handle HttpResponse objects
                    try:
                        body = result.get_body()
                        if body:
                            response_data = json.loads(body.decode())
                            filtered_data = security_validator.filter_admin_response(response_data)
                            result = HttpResponse(
                                json.dumps(filtered_data),
                                mimetype=result.mimetype,
                                status_code=result.status_code,
                                headers=dict(result.headers)
                            )
                    except Exception as filter_error:
                        logger.warning(f"⚠️ Could not filter response: {filter_error}")
                
                # Log successful access
                security_validator.log_security_event(
                    'admin_success',
                    {
                        'function': func.__name__,
                        'client_ip': client_ip,
                        'user_id': (validation_result.get('jwt_payload') or {}).get('sub'),
                        'response_code': getattr(result, 'status_code', 200)
                    }
                )
                
                return result
                
            except SecurityValidationError as e:
                # Log security violation
                security_validator.log_security_event(
                    'security_violation',
                    {
                        'function': func.__name__,
                        'client_ip': client_ip,
                        'error': e.error_code,
                        'message': e.message,
                        'method': request.method
                    },
                    'WARNING'
                )
                
                # Return proper error response
                from azure.functions import HttpResponse
                return HttpResponse(
                    json.dumps({
                        "error": "Security validation failed",
                        "code": e.error_code,
                        "message": e.message if os.getenv("AUTH_MODE") == "development" else "Access denied"
                    }),
                    status_code=403 if e.error_code in ["INSUFFICIENT_SCOPE", "IP_BLOCKED", "RATE_LIMIT_EXCEEDED"] else 401,
                    mimetype="application/json"
                )
                
            except Exception as e:
                # Log unexpected error
                security_validator.log_security_event(
                    'security_error',
                    {
                        'function': func.__name__,
                        'client_ip': client_ip,
                        'error': str(e)
                    },
                    'ERROR'
                )
                
                from azure.functions import HttpResponse
                return HttpResponse(
                    json.dumps({
                        "error": "Security processing failed",
                        "message": str(e) if os.getenv("AUTH_MODE") == "development" else "Internal error"
                    }),
                    status_code=500,
                    mimetype="application/json"
                )
        
        return wrapper
    return decorator
