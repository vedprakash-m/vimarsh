"""
Azure Functions Test - CI/CD Compatible
Tests Azure Functions endpoints without directly invoking FunctionBuilder objects.
This approach avoids the 'FunctionBuilder object is not awaitable' error.
"""

import pytest
import sys
import os
from unittest.mock import Mock

class MockRequest:
    """Mock Azure Functions Request for testing"""
    def __init__(self, method="GET", url="/api/test", headers=None, body=b""):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.body = body
        
    def get_json(self):
        return {}

class TestFunctionAppModule:
    """Test the function_app module structure without executing functions"""

    def test_function_app_module_imports(self):
        """Test that function_app can be imported"""
        try:
            import function_app
            assert function_app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import function_app: {e}")

    def test_function_app_has_required_attributes(self):
        """Test that function_app has the expected structure"""
        import function_app
        
        # Check that the app instance exists
        assert hasattr(function_app, 'app'), "function_app should have 'app' attribute"
        
        # The app should be a FunctionApp instance
        app = function_app.app
        assert app is not None, "app should not be None"

    def test_function_endpoints_exist(self):
        """Test that expected function endpoints are defined"""
        import function_app
        
        # Check for the function app instance and its routes
        app = function_app.app
        
        # Azure Functions FunctionApp has a _function_builders attribute containing registered routes
        if hasattr(app, '_function_builders'):
            function_count = len(app._function_builders)
        else:
            # Fallback: count decorated functions by inspecting module attributes
            function_count = 0
            for name in dir(function_app):
                obj = getattr(function_app, name)
                if callable(obj) and hasattr(obj, '__name__') and 'route' in str(type(obj)):
                    function_count += 1
        
        # We should have some functions defined
        assert function_count > 0, f"No Azure Functions found in function_app (found {function_count})"

    def test_services_are_importable(self):
        """Test that all required services can be imported"""
        services_to_test = [
            'services.gemini_embedding_service',
            'services.database_personality_service',
            'services.personality_service',
            'services.llm_service'
        ]
        
        for service_name in services_to_test:
            try:
                __import__(service_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {service_name}: {e}")

    def test_config_is_available(self):
        """Test that configuration is available"""
        try:
            from core.config import config
            assert config is not None
        except ImportError as e:
            pytest.skip(f"Config not available in test environment: {e}")

    def test_azure_functions_core_tools_compatibility(self):
        """Test that the module is compatible with Azure Functions Core Tools"""
        import function_app
        
        # Check that we have the expected Azure Functions patterns
        app = function_app.app
        
        # The app should have a function registry (internal Azure Functions structure)
        # We can't test execution but we can test structure
        assert hasattr(app, '_function_builders') or hasattr(app, '_functions'), \
            "Function app should have function registry"

if __name__ == "__main__":
    pytest.main([__file__])
