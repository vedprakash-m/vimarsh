"""
Integration Tests for User Settings API Endpoints
Tests all 5 user-related API endpoints with authentication, validation, and error handling
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import azure.functions as func

from services.preferences_service import PreferencesService
from services.data_export_service import DataExportService
from engagement.engagement_service import EngagementService
from services.analytics_service import AnalyticsService


class TestUserAPIEndpoints:
    """Test suite for user-related API endpoints"""
    
    @pytest.fixture
    def preferences_service(self):
        """Create PreferencesService instance"""
        return PreferencesService()
    
    @pytest.fixture
    def data_export_service(self):
        """Create mock DataExportService"""
        service = Mock(spec=DataExportService)
        service.export_user_data = AsyncMock(return_value={
            "metadata": {
                "export_version": "1.0",
                "timestamp": "2025-12-07T00:00:00Z",
                "total_containers": 5,
                "total_items": 10
            },
            "data": {}
        })
        service.delete_user_data = AsyncMock(return_value={
            "deleted_containers": 5,
            "total_items_deleted": 10
        })
        return service
    
    @pytest.fixture
    def engagement_service(self):
        """Create mock EngagementService"""
        service = Mock(spec=EngagementService)
        service.get_journey_stats = Mock(return_value={
            "current_streak": 5,
            "longest_streak": 10,
            "total_conversations": 50,
            "achievements_unlocked": 3,
            "wisdom_level": "Student",
            "domain_exploration": {}
        })
        return service
    
    @pytest.fixture
    def analytics_service(self):
        """Create mock AnalyticsService"""
        service = Mock(spec=AnalyticsService)
        service.get_ai_usage_summary = AsyncMock(return_value={
            "monthly_cost_usd": 1.50,
            "usage_percentage": 15.0,
            "status": "well_within_limits",
            "total_conversations": 50,
            "total_tokens": 100000,
            "trend": {
                "previous_month_cost": 1.20,
                "change_percentage": 25.0,
                "direction": "up"
            }
        })
        return service
    
    @pytest.fixture
    def valid_token(self):
        """Sample valid JWT token"""
        return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test_token"
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID"""
        return "test_user_123"
    
    @pytest.fixture
    def mock_user_info(self, sample_user_id):
        """Sample user info from token"""
        return {
            "sub": sample_user_id,
            "oid": sample_user_id,
            "preferred_username": "testuser@example.com",
            "email": "testuser@example.com",
            "name": "Test User"
        }


class TestGetUserProfile(TestUserAPIEndpoints):
    """Test GET /api/user/profile endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_profile_success(
        self,
        preferences_service,
        engagement_service,
        analytics_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test successful profile retrieval"""
        # Setup preferences
        prefs = {
            "experience_preferences": {
                "conversation_style": "balanced",
                "language": "en"
            },
            "notification_preferences": {
                "daily_wisdom_enabled": True
            },
            "memory_preferences": {
                "remember_conversations": True
            }
        }
        preferences_service.update_preferences(sample_user_id, prefs)
        
        # Mock request
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Import and patch get_user_from_token
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.preferences_service', preferences_service):
                with patch('function_app.get_engagement_service', return_value=engagement_service):
                    with patch('function_app.analytics_service', analytics_service):
                        from function_app import get_user_profile
                        
                        response = await get_user_profile(req)
        
        # Verify response
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert body["user_id"] == sample_user_id
        assert body["email"] == "testuser@example.com"
        assert "preferences" in body
        assert "journey_stats" in body
        assert "ai_usage" in body
    
    @pytest.mark.asyncio
    async def test_get_profile_missing_authorization(self):
        """Test profile retrieval without authorization header"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {}
        
        from function_app import get_user_profile
        response = await get_user_profile(req)
        
        assert response.status_code == 401
        body = json.loads(response.get_body().decode())
        assert "error" in body
    
    @pytest.mark.asyncio
    async def test_get_profile_invalid_token(self, valid_token):
        """Test profile retrieval with invalid token"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch('function_app.get_user_from_token', return_value=None):
            from function_app import get_user_profile
            response = await get_user_profile(req)
        
        assert response.status_code == 401
        body = json.loads(response.get_body().decode())
        assert "error" in body
    
    @pytest.mark.asyncio
    async def test_get_profile_missing_user_id(self, valid_token):
        """Test profile retrieval with token missing user ID"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Mock user info without sub or oid
        mock_user_info = {"email": "test@example.com"}
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            from function_app import get_user_profile
            response = await get_user_profile(req)
        
        assert response.status_code == 400
        body = json.loads(response.get_body().decode())
        assert "error" in body


class TestUpdateUserPreferences(TestUserAPIEndpoints):
    """Test PATCH /api/user/preferences endpoint"""
    
    @pytest.mark.asyncio
    async def test_update_preferences_success(
        self,
        preferences_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test successful preferences update"""
        # Mock request
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        req.get_json = Mock(return_value={
            "experience_preferences": {
                "conversation_style": "detailed",
                "language": "hi"
            }
        })
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.preferences_service', preferences_service):
                from function_app import update_user_preferences
                response = await update_user_preferences(req)
        
        # Verify response
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert body["success"] is True
        assert "preferences" in body
        assert body["preferences"]["experience_preferences"]["conversation_style"] == "detailed"
    
    @pytest.mark.asyncio
    async def test_update_preferences_validation_error(
        self,
        preferences_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test preferences update with validation error"""
        # Mock request with invalid data
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        req.get_json = Mock(return_value={
            "experience_preferences": {
                "conversation_style": "invalid_style"  # Invalid value
            }
        })
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.preferences_service', preferences_service):
                from function_app import update_user_preferences
                response = await update_user_preferences(req)
        
        # Should return validation error
        assert response.status_code == 400
        body = json.loads(response.get_body().decode())
        assert "error" in body
        assert "validation" in body["error"].lower()
    
    @pytest.mark.asyncio
    async def test_update_preferences_invalid_json(
        self,
        valid_token,
        mock_user_info
    ):
        """Test preferences update with invalid JSON"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        req.get_json = Mock(side_effect=ValueError("Invalid JSON"))
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            from function_app import update_user_preferences
            response = await update_user_preferences(req)
        
        assert response.status_code == 400
        body = json.loads(response.get_body().decode())
        assert "Invalid JSON" in body["error"]
    
    @pytest.mark.asyncio
    async def test_update_preferences_max_favorites_validation(
        self,
        preferences_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test validation of max 5 favorite personalities"""
        # Mock request with too many favorites
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        req.get_json = Mock(return_value={
            "experience_preferences": {
                "favorite_personalities": ["krishna", "einstein", "buddha", "rumi", "shakespeare", "tagore"]  # 6 personalities
            }
        })
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.preferences_service', preferences_service):
                from function_app import update_user_preferences
                response = await update_user_preferences(req)
        
        # Should return validation error
        assert response.status_code == 400
        body = json.loads(response.get_body().decode())
        assert "error" in body


class TestGetUsageSummary(TestUserAPIEndpoints):
    """Test GET /api/user/usage-summary endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_usage_summary_success(
        self,
        analytics_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test successful usage summary retrieval"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.analytics_service', analytics_service):
                from function_app import get_usage_summary
                response = await get_usage_summary(req)
        
        # Verify response
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert "monthly_cost_usd" in body
        assert "usage_percentage" in body
        assert "status" in body
        assert "trend" in body
    
    @pytest.mark.asyncio
    async def test_get_usage_summary_missing_authorization(self):
        """Test usage summary without authorization"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {}
        
        from function_app import get_usage_summary
        response = await get_usage_summary(req)
        
        assert response.status_code == 401


class TestExportUserData(TestUserAPIEndpoints):
    """Test POST /api/user/export endpoint"""
    
    @pytest.mark.asyncio
    async def test_export_data_success(
        self,
        data_export_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test successful data export"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.data_export_service', data_export_service):
                from function_app import export_user_data
                response = await export_user_data(req)
        
        # Verify response
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert "metadata" in body
        assert "data" in body
        
        # Verify Content-Disposition header
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]
    
    @pytest.mark.asyncio
    async def test_export_data_includes_metadata(
        self,
        data_export_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test that export includes proper metadata"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.data_export_service', data_export_service):
                from function_app import export_user_data
                response = await export_user_data(req)
        
        body = json.loads(response.get_body().decode())
        metadata = body["metadata"]
        
        assert "export_version" in metadata
        assert "timestamp" in metadata
        assert "total_containers" in metadata
        assert "total_items" in metadata


class TestDeleteUserAccount(TestUserAPIEndpoints):
    """Test DELETE /api/user/account endpoint"""
    
    @pytest.mark.asyncio
    async def test_delete_account_success(
        self,
        data_export_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test successful account deletion"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.data_export_service', data_export_service):
                from function_app import delete_user_account
                response = await delete_user_account(req)
        
        # Verify response
        assert response.status_code == 200
        
        body = json.loads(response.get_body().decode())
        assert body["success"] is True
        assert "deletion_summary" in body
        assert "deleted_containers" in body["deletion_summary"]
    
    @pytest.mark.asyncio
    async def test_delete_account_missing_authorization(self):
        """Test account deletion without authorization"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {}
        
        from function_app import delete_user_account
        response = await delete_user_account(req)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_delete_account_cascade_deletion(
        self,
        data_export_service,
        valid_token,
        sample_user_id,
        mock_user_info
    ):
        """Test that account deletion cascades to all containers"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.data_export_service', data_export_service):
                from function_app import delete_user_account
                response = await delete_user_account(req)
        
        # Verify data_export_service.delete_user_data was called
        data_export_service.delete_user_data.assert_called_once_with(sample_user_id)


class TestAuthenticationCommon(TestUserAPIEndpoints):
    """Test common authentication patterns across all endpoints"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint_name", [
        "get_user_profile",
        "update_user_preferences",
        "get_usage_summary",
        "export_user_data",
        "delete_user_account"
    ])
    async def test_endpoints_require_bearer_token(self, endpoint_name):
        """Test that all endpoints require Bearer token"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": "NotBearer invalid"}
        
        # Import endpoint function
        from function_app import get_user_profile, update_user_preferences, get_usage_summary, export_user_data, delete_user_account
        
        endpoints = {
            "get_user_profile": get_user_profile,
            "update_user_preferences": update_user_preferences,
            "get_usage_summary": get_usage_summary,
            "export_user_data": export_user_data,
            "delete_user_account": delete_user_account
        }
        
        endpoint_func = endpoints[endpoint_name]
        response = await endpoint_func(req)
        
        assert response.status_code == 401
        body = json.loads(response.get_body().decode())
        assert "error" in body
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint_name", [
        "get_user_profile",
        "update_user_preferences",
        "get_usage_summary",
        "export_user_data",
        "delete_user_account"
    ])
    async def test_endpoints_handle_expired_token(self, endpoint_name, valid_token):
        """Test that all endpoints handle expired tokens"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Mock get_user_from_token to return None (expired/invalid token)
        with patch('function_app.get_user_from_token', return_value=None):
            # Import endpoint function
            from function_app import get_user_profile, update_user_preferences, get_usage_summary, export_user_data, delete_user_account
            
            endpoints = {
                "get_user_profile": get_user_profile,
                "update_user_preferences": update_user_preferences,
                "get_usage_summary": get_usage_summary,
                "export_user_data": export_user_data,
                "delete_user_account": delete_user_account
            }
            
            endpoint_func = endpoints[endpoint_name]
            response = await endpoint_func(req)
        
        assert response.status_code == 401
        body = json.loads(response.get_body().decode())
        assert "error" in body


class TestErrorHandling(TestUserAPIEndpoints):
    """Test error handling across all endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_profile_service_error(
        self,
        valid_token,
        mock_user_info
    ):
        """Test profile endpoint handles service errors"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Mock service to raise exception
        mock_prefs_service = Mock()
        mock_prefs_service.get_preferences = Mock(side_effect=Exception("DB error"))
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.preferences_service', mock_prefs_service):
                from function_app import get_user_profile
                response = await get_user_profile(req)
        
        assert response.status_code == 500
        body = json.loads(response.get_body().decode())
        assert "error" in body
    
    @pytest.mark.asyncio
    async def test_export_data_service_error(
        self,
        valid_token,
        mock_user_info
    ):
        """Test export endpoint handles service errors"""
        req = Mock(spec=func.HttpRequest)
        req.headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Mock service to raise exception
        mock_export_service = Mock()
        mock_export_service.export_user_data = AsyncMock(side_effect=Exception("Export failed"))
        
        with patch('function_app.get_user_from_token', return_value=mock_user_info):
            with patch('function_app.data_export_service', mock_export_service):
                from function_app import export_user_data
                response = await export_user_data(req)
        
        assert response.status_code == 500
        body = json.loads(response.get_body().decode())
        assert "error" in body
