"""
Test suite for unified authentication service.
Validates both development and production authentication modes.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt
import json

# Import our unified auth service
from auth.unified_auth_service import UnifiedAuthService, AuthenticationMode
from auth.models import AuthenticatedUser, ProfileConfigurations
from core.user_roles import UserRole, UserPermissions


class TestUnifiedAuthService:
    """Test cases for UnifiedAuthService"""
    
    def setup_method(self):
        """Setup for each test"""
        self.auth_service = UnifiedAuthService(mode=AuthenticationMode.DEVELOPMENT)
    
    def test_development_mode_initialization(self):
        """Test service initialization in development mode"""
        service = UnifiedAuthService(mode=AuthenticationMode.DEVELOPMENT)
        assert service.mode == AuthenticationMode.DEVELOPMENT
        assert not service.is_enabled  # Auth disabled in dev by default
    
    def test_production_mode_initialization(self):
        """Test service initialization in production mode"""
        service = UnifiedAuthService(mode=AuthenticationMode.PRODUCTION)
        assert service.mode == AuthenticationMode.PRODUCTION
        assert service.is_enabled  # Auth always enabled in production
    
    def test_create_development_user(self):
        """Test creation of development user"""
        user = self.auth_service._create_development_user()
        
        assert isinstance(user, AuthenticatedUser)
        assert user.email == "dev@vimarsh.local"
        assert user.role == UserRole.ADMIN
        assert user.is_admin()
        assert user.has_permission("can_access_admin_endpoints")
    
    def test_development_token_validation(self):
        """Test development token validation"""
        # Test with valid dev token
        user = self.auth_service._validate_development_token("dev-token")
        assert user is not None
        assert user.email == "dev@vimarsh.local"
        
        # Test with admin token
        user = self.auth_service._validate_development_token("admin-token")
        assert user is not None
        assert user.email == "admin@vimarsh.local"
        
        # Test with invalid token
        user = self.auth_service._validate_development_token("invalid-token")
        assert user is None
    
    def test_jwt_token_validation_in_dev(self):
        """Test JWT token validation in development mode"""
        # Create a test JWT token
        test_payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "roles": ["user"]
        }
        
        # Create unsigned JWT (dev mode doesn't verify signature)
        test_token = jwt.encode(test_payload, "secret", algorithm="HS256")
        
        user = self.auth_service._validate_development_token(test_token)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    @patch('requests.get')
    def test_production_token_validation(self, mock_get):
        """Test production token validation against Microsoft Entra ID"""
        # Setup mock JWKS response
        mock_jwks = {
            "keys": [{
                "kid": "test-key-id",
                "kty": "RSA",
                "use": "sig",
                "n": "test-n",
                "e": "AQAB"
            }]
        }
        mock_get.return_value.json.return_value = mock_jwks
        mock_get.return_value.raise_for_status.return_value = None
        
        # Create production service
        prod_service = UnifiedAuthService(mode=AuthenticationMode.PRODUCTION)
        
        with patch.dict(os.environ, {
            "AZURE_TENANT_ID": "test-tenant-id",
            "AZURE_CLIENT_ID": "test-client-id"
        }):
            # Test with invalid token (will fail validation)
            user = prod_service._validate_production_token("invalid-token")
            assert user is None
    
    def test_authenticate_request_disabled_auth(self):
        """Test request authentication when auth is disabled"""
        mock_request = Mock()
        
        # Auth disabled
        self.auth_service.is_enabled = False
        user = self.auth_service.authenticate_request(mock_request)
        
        assert user is not None
        assert user.email == "dev@vimarsh.local"
        assert user.is_admin()
    
    def test_authenticate_request_enabled_auth(self):
        """Test request authentication when auth is enabled"""
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer dev-token"}
        
        # Auth enabled
        self.auth_service.is_enabled = True
        user = self.auth_service.authenticate_request(mock_request)
        
        assert user is not None
        assert user.email == "dev@vimarsh.local"
    
    def test_authenticate_request_no_token(self):
        """Test request authentication with no token"""
        mock_request = Mock()
        mock_request.headers = {}
        
        # Auth enabled but no token
        self.auth_service.is_enabled = True
        user = self.auth_service.authenticate_request(mock_request)
        
        assert user is None
    
    def test_token_caching(self):
        """Test token caching functionality"""
        # First call should cache the result
        user1 = self.auth_service._validate_development_token("dev-token")
        
        # Second call should return cached result
        user2 = self.auth_service._validate_development_token("dev-token")
        
        assert user1 is not None
        assert user2 is not None
        assert user1.email == user2.email
    
    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        # Cache a token
        self.auth_service._validate_development_token("dev-token")
        assert len(self.auth_service._token_cache) > 0
        
        # Clear cache
        self.auth_service.clear_cache()
        assert len(self.auth_service._token_cache) == 0
    
    def test_auth_decorator_creation(self):
        """Test creation of authentication decorators"""
        # Test regular auth decorator
        auth_decorator = self.auth_service.create_auth_decorator(require_admin=False)
        assert callable(auth_decorator)
        
        # Test admin auth decorator
        admin_decorator = self.auth_service.create_auth_decorator(require_admin=True)
        assert callable(admin_decorator)
    
    def test_extensible_user_model(self):
        """Test the extensible user model functionality"""
        # Test Vimarsh-specific profile configuration
        token_data = {
            "sub": "test-user-123",
            "email": "test@vimarsh.local",
            "name": "Test User",
            "spiritual_preferences": ["meditation", "yoga"],
            "meditation_level": "intermediate"
        }
        
        user = AuthenticatedUser.from_token_data(
            token_data, 
            ProfileConfigurations.VIMARSH_CONFIG
        )
        
        assert user.profile["spiritual_preferences"] == ["meditation", "yoga"]
        assert user.profile["meditation_level"] == "intermediate"
        assert "guidance_history" in user.profile  # Required field with default
    
    def test_generic_profile_configuration(self):
        """Test generic profile configuration"""
        token_data = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "name": "Test User",
            "language": "English",
            "profile_id": "test-user-123"  # Required field
        }
        
        user = AuthenticatedUser.from_token_data(
            token_data,
            ProfileConfigurations.GENERIC_CONFIG
        )
        
        assert user.profile["language"] == "English"
        assert user.profile["profile_id"] == "test-user-123"  # Required field
    
    def test_user_permissions(self):
        """Test user permission system"""
        # Create user with admin role - mock the admin role manager
        from core.user_roles import UserRole, UserPermissions
        
        token_data = {
            "sub": "admin-123",
            "email": "admin@vimarsh.local",
            "name": "Admin User",
            "roles": ["admin"]
        }
        
        # Mock the admin role manager to return admin role
        with patch('core.user_roles.admin_role_manager') as mock_admin_manager:
            mock_admin_manager.get_user_role.return_value = UserRole.ADMIN
            mock_admin_manager.get_user_permissions.return_value = UserPermissions.for_role(UserRole.ADMIN)
            
            user = AuthenticatedUser.from_token_data(token_data)
            
            # Admin should have admin permissions
            assert user.is_admin()
            assert user.user_permissions.can_access_admin_endpoints
            assert user.user_permissions.can_manage_users
    
    def test_user_attributes(self):
        """Test custom user attributes"""
        user = AuthenticatedUser(
            id="test-123",
            email="test@example.com",
            name="Test User"
        )
        
        # Set custom attribute
        user.set_attribute("favorite_scripture", "Bhagavad Gita")
        assert user.get_attribute("favorite_scripture") == "Bhagavad Gita"
        
        # Test default value
        assert user.get_attribute("nonexistent", "default") == "default"
    
    def test_user_serialization(self):
        """Test user serialization to dictionary"""
        user = AuthenticatedUser(
            id="test-123",
            email="test@example.com",
            name="Test User"
        )
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == "test-123"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["role"] == "user"
        assert "created_at" in user_dict


if __name__ == "__main__":
    # Run basic tests
    test_suite = TestUnifiedAuthService()
    test_suite.setup_method()
    
    print("🧪 Running unified auth service tests...")
    
    try:
        test_suite.test_development_mode_initialization()
        print("✅ Development mode initialization test passed")
        
        test_suite.test_create_development_user()
        print("✅ Development user creation test passed")
        
        test_suite.test_development_token_validation()
        print("✅ Development token validation test passed")
        
        test_suite.test_extensible_user_model()
        print("✅ Extensible user model test passed")
        
        test_suite.test_user_permissions()
        print("✅ User permissions test passed")
        
        print("🎉 All basic tests passed! Unified auth service is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
