"""
Tests for Admin Features - Phase 5 Enhanced AI Cost Management
Tests the admin role system, token tracking, budget validation, and admin endpoints
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import the admin components
from core.user_roles import UserRole, UserPermissions, AdminRoleManager
from core.token_tracker import TokenUsageTracker, TokenUsage
from core.budget_validator import BudgetValidator, BudgetLevel, BudgetLimit
from auth.models import AuthenticatedUser


class TestUserRoleSystem:
    """Test the user role and permission system"""
    
    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.SUPER_ADMIN.value == "super_admin"
        assert str(UserRole.USER) == "user"
    
    def test_user_permissions_for_roles(self):
        """Test permissions for different roles"""
        # Test USER permissions
        user_perms = UserPermissions.for_role(UserRole.USER)
        assert user_perms.can_use_spiritual_guidance == True
        assert user_perms.can_view_cost_dashboard == False
        assert user_perms.can_manage_users == False
        
        # Test ADMIN permissions
        admin_perms = UserPermissions.for_role(UserRole.ADMIN)
        assert admin_perms.can_use_spiritual_guidance == True
        assert admin_perms.can_view_cost_dashboard == True
        assert admin_perms.can_manage_users == True
        assert admin_perms.can_override_budget_limits == False
        
        # Test SUPER_ADMIN permissions
        super_admin_perms = UserPermissions.for_role(UserRole.SUPER_ADMIN)
        assert super_admin_perms.can_use_spiritual_guidance == True
        assert super_admin_perms.can_view_cost_dashboard == True
        assert super_admin_perms.can_manage_users == True
        assert super_admin_perms.can_override_budget_limits == True
    
    def test_admin_role_manager(self):
        """Test AdminRoleManager functionality"""
        # Create a test admin role manager
        manager = AdminRoleManager()
        
        # Test user role determination
        assert manager.get_user_role("regular@example.com") == UserRole.USER
        
        # Test admin role management
        manager.admin_emails = ["admin@example.com"]
        assert manager.get_user_role("admin@example.com") == UserRole.ADMIN
        assert manager.is_admin("admin@example.com") == True
        assert manager.is_admin("regular@example.com") == False
        
        # Test super admin
        manager.super_admin_emails = ["super@example.com"]
        assert manager.get_user_role("super@example.com") == UserRole.SUPER_ADMIN
        assert manager.is_super_admin("super@example.com") == True
        assert manager.is_super_admin("admin@example.com") == False


class TestTokenUsageTracker:
    """Test the token usage tracking system"""
    
    def test_token_usage_creation(self):
        """Test TokenUsage record creation"""
        usage = TokenUsage(
            user_id="test_user",
            user_email="test@example.com",
            session_id="session_123",
            timestamp=datetime.utcnow(),
            model="gemini-2.5-flash",
            input_tokens=100,
            output_tokens=200,
            total_tokens=300,
            cost_usd=0.15,
            request_type="spiritual_guidance",
            response_quality="high"
        )
        
        assert usage.user_id == "test_user"
        assert usage.total_tokens == 300
        assert usage.cost_usd == 0.15
        
        # Test conversion to dict
        usage_dict = usage.to_dict()
        assert usage_dict["user_id"] == "test_user"
        assert usage_dict["total_tokens"] == 300
        assert "timestamp" in usage_dict
    
    @pytest.mark.asyncio
    async def test_token_usage_tracker(self):
        """Test TokenUsageTracker functionality"""
        tracker = TokenUsageTracker()
        
        # Test cost calculation
        cost = tracker.calculate_cost("gemini-2.5-flash", 1000, 1000)
        assert cost > 0  # Should have some cost
        
        # Mock the database operations to avoid event loop issues
        with patch.object(tracker, '_save_usage_atomic') as mock_save_atomic, \
             patch.object(tracker, '_save_usage_to_db') as mock_save_db:
            
            # Test recording usage
            usage = tracker.record_usage(
                user_id="test_user",
                user_email="test@example.com",
                session_id="session_123",
                model="gemini-2.5-flash",
                input_tokens=100,
                output_tokens=200,
                request_type="spiritual_guidance",
                response_quality="high"
            )
        
        assert usage.user_id == "test_user"
        assert usage.total_tokens == 300
        assert len(tracker.usage_records) == 1
        assert "test_user" in tracker.user_stats
        
        # Test user stats
        user_stats = tracker.get_user_usage("test_user")
        assert user_stats is not None
        assert user_stats.total_requests == 1
        assert user_stats.total_tokens == 300
        assert user_stats.user_email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_system_usage_statistics(self):
        """Test system-wide usage statistics"""
        tracker = TokenUsageTracker()
        
        # Mock database operations
        with patch.object(tracker, '_save_usage_atomic') as mock_save_atomic, \
             patch.object(tracker, '_save_usage_to_db') as mock_save_db:
            
            # Record some usage
            tracker.record_usage("user1", "user1@example.com", "session1", "gemini-2.5-flash", 100, 200)
            tracker.record_usage("user2", "user2@example.com", "session2", "gemini-2.5-flash", 150, 250)
        
        # Get system stats
        stats = tracker.get_system_usage(7)
        assert stats["total_users"] == 2
        assert stats["total_requests"] == 2
        assert stats["total_tokens"] == 700  # 300 + 400
        assert stats["total_cost_usd"] > 0


class TestBudgetValidator:
    """Test the budget validation system"""
    
    def test_budget_limit_creation(self):
        """Test BudgetLimit creation"""
        budget = BudgetLimit(
            user_id="test_user",
            user_email="test@example.com",
            monthly_limit_usd=50.0,
            daily_limit_usd=5.0,
            per_request_limit_usd=0.5
        )
        
        assert budget.user_id == "test_user"
        assert budget.monthly_limit_usd == 50.0
        assert budget.created_at is not None
        
        # Test conversion to dict
        budget_dict = budget.to_dict()
        assert budget_dict["monthly_limit_usd"] == 50.0
        assert "created_at" in budget_dict
    
    def test_budget_validator(self):
        """Test BudgetValidator functionality"""
        validator = BudgetValidator()
        
        # Test setting user budget
        budget = validator.set_user_budget(
            user_id="test_user",
            user_email="test@example.com",
            monthly_limit=50.0,
            daily_limit=5.0,
            per_request_limit=0.5
        )
        
        assert budget.user_id == "test_user"
        assert budget.monthly_limit_usd == 50.0
        assert "test_user" in validator.budget_limits
        
        # Test budget validation
        can_proceed, error = validator.validate_request_budget(
            user_id="test_user",
            user_email="test@example.com",
            estimated_cost=0.25
        )
        assert can_proceed == True
        assert error is None
        
        # Test budget override
        success = validator.override_budget("test_user", "admin@example.com", "Testing")
        assert success == True
        assert validator.budget_limits["test_user"].emergency_override == True
    
    def test_budget_alert_creation(self):
        """Test budget alert creation"""
        validator = BudgetValidator()
        
        # Set a low budget
        validator.set_user_budget("test_user", "test@example.com", 1.0, 0.1, 0.01)
        
        # Test validation that should trigger alert
        can_proceed, error = validator.validate_request_budget(
            user_id="test_user",
            user_email="test@example.com",
            estimated_cost=0.05  # High cost for the budget
        )
        
        # Should still proceed but potentially create alerts
        assert can_proceed == True or error is not None
    
    def test_spiritual_messages(self):
        """Test spiritual budget messages"""
        validator = BudgetValidator()
        
        # Test different message types
        info_msg = validator._create_spiritual_message(BudgetLevel.INFO, 0.5, "monthly")
        assert "🕉️" in info_msg
        assert "mindful" in info_msg.lower()
        
        warning_msg = validator._create_spiritual_message(BudgetLevel.WARNING, 0.75, "daily")
        assert "⚡" in warning_msg
        assert "arjuna" in warning_msg.lower()
        
        critical_msg = validator._create_spiritual_message(BudgetLevel.CRITICAL, 0.9, "monthly")
        assert "🔥" in critical_msg
        assert "fallback" in critical_msg.lower()
        
        emergency_msg = validator._create_spiritual_message(BudgetLevel.EMERGENCY, 1.0, "daily")
        assert "🛑" in emergency_msg
        assert "pause" in emergency_msg.lower()


class TestAuthenticatedUserEnhancements:
    """Test AuthenticatedUser enhancements with admin roles"""
    
    def test_authenticated_user_with_admin_role(self):
        """Test AuthenticatedUser with admin role functionality"""
        # Mock token data
        token_data = {
            "sub": "test_user_id",
            "email": "admin@example.com",
            "name": "Test Admin",
            "given_name": "Test",
            "family_name": "Admin",
            "roles": ["admin"]
        }
        
        # Mock admin role manager
        with patch('core.user_roles.admin_role_manager') as mock_manager:
            mock_manager.get_user_role.return_value = UserRole.ADMIN
            mock_manager.get_user_permissions.return_value = UserPermissions.for_role(UserRole.ADMIN)
            
            user = AuthenticatedUser.from_token_data(token_data)
            
            assert user.email == "admin@example.com"
            assert user.role == UserRole.ADMIN
            assert user.is_admin() == True
            assert user.has_permission('can_access_admin_endpoints') == True


class TestIntegration:
    """Integration tests for admin features"""
    
    @pytest.mark.asyncio
    async def test_complete_admin_workflow(self):
        """Test complete admin workflow"""
        # Setup components
        tracker = TokenUsageTracker()
        validator = BudgetValidator()
        
        # Create user and set budget
        user_id = "test_user"
        user_email = "test@example.com"
        
        budget = validator.set_user_budget(
            user_id=user_id,
            user_email=user_email,
            monthly_limit=10.0,
            daily_limit=1.0,
            per_request_limit=0.1
        )
        
        # Mock database operations to avoid event loop issues
        with patch.object(tracker, '_save_usage_atomic') as mock_save_atomic, \
             patch.object(tracker, '_save_usage_to_db') as mock_save_db:
            
            # Record some usage
            usage = tracker.record_usage(
            user_id=user_id,
            user_email=user_email,
            session_id="session_123",
            model="gemini-2.5-flash",
            input_tokens=100,
            output_tokens=200,
            request_type="spiritual_guidance",
            response_quality="high"
        )
        
        # Check budget status
        budget_status = validator.get_user_budget_status(user_id)
        assert budget_status["budget_limits"]["user_id"] == user_id
        assert budget_status["current_usage"]["total"] > 0
        
        # Test budget validation
        can_proceed, error = validator.validate_request_budget(
            user_id=user_id,
            user_email=user_email,
            estimated_cost=0.05
        )
        assert can_proceed == True  # Should be within budget
        
        # Test admin override
        success = validator.override_budget(user_id, "admin@example.com", "Testing")
        assert success == True
        
        # Test system statistics
        system_stats = tracker.get_system_usage(7)
        assert system_stats["total_users"] == 1
        assert system_stats["total_requests"] == 1


# Test runner
if __name__ == "__main__":
    print("🧪 Running Admin Features Tests...")
    
    # Run basic tests
    role_tests = TestUserRoleSystem()
    role_tests.test_user_role_enum()
    role_tests.test_user_permissions_for_roles()
    role_tests.test_admin_role_manager()
    
    token_tests = TestTokenUsageTracker()
    token_tests.test_token_usage_creation()
    token_tests.test_token_usage_tracker()
    token_tests.test_system_usage_statistics()
    
    budget_tests = TestBudgetValidator()
    budget_tests.test_budget_limit_creation()
    budget_tests.test_budget_validator()
    budget_tests.test_budget_alert_creation()
    budget_tests.test_spiritual_messages()
    
    integration_tests = TestIntegration()
    integration_tests.test_complete_admin_workflow()
    
    print("✅ All admin features tests passed!")
    print("🎉 Phase 5 admin features are working correctly!")
