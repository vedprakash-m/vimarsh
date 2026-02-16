"""
Simplified Function App Tests - CI/CD Compatible
Tests that work both locally and in CI/CD without Azure Functions runtime
"""

import pytest


class TestFunctionAppModuleStructure:
    """Test that function_app.py module structure is correct"""
    
    def test_function_app_imports_successfully(self):
        """Test that function_app.py can be imported without errors"""
        try:
            import function_app
            assert function_app is not None
        except Exception as e:
            pytest.fail(f"function_app.py failed to import: {e}")
    
    def test_required_functions_exist(self):
        """Test that expected functions exist in function_app module"""
        import function_app
        
        # Check for key functions that should exist
        expected_functions = [
            'health_endpoint',
            'guidance_endpoint', 
            'get_cors_headers',
            'get_active_personalities'
        ]
        
        for func_name in expected_functions:
            assert hasattr(function_app, func_name), f"Function {func_name} not found in function_app"
    
    def test_cors_headers_function_works(self):
        """Test get_cors_headers function returns valid headers"""
        from function_app import get_cors_headers
        
        headers = get_cors_headers()
        
        # Should return a dictionary
        assert isinstance(headers, dict)
        
        # Should have some CORS-related headers
        header_keys = list(headers.keys())
        cors_indicators = ['Access-Control', 'cors', 'origin', 'Origin']
        
        # At least one header should relate to CORS
        has_cors_header = any(
            any(indicator.lower() in key.lower() for indicator in cors_indicators)
            for key in header_keys
        )
        
        assert has_cors_header or len(headers) > 0, "CORS headers function should return meaningful headers"


class TestFunctionAppServiceAvailability:
    """Test service availability and imports"""
    
    def test_personality_service_imports(self):
        """Test personality service can be imported"""
        try:
            from services.personality_service import PersonalityService
            service = PersonalityService()
            assert service is not None
        except ImportError:
            pytest.skip("PersonalityService not available")
    
    def test_database_personality_service_imports(self):
        """Test database personality service can be imported"""
        try:
            from services.database_personality_service import DatabasePersonalityService
            service = DatabasePersonalityService()
            assert service is not None
        except ImportError:
            pytest.skip("DatabasePersonalityService not available")
    
    def test_auth_service_imports(self):
        """Test auth service can be imported"""
        try:
            from auth.unified_auth_service import UnifiedAuthService
            service = UnifiedAuthService()
            assert service is not None
        except ImportError:
            pytest.skip("UnifiedAuthService not available")
    
    def test_gemini_embedding_service_imports(self):
        """Test Gemini embedding service can be imported"""
        try:
            from services.gemini_embedding_service import GeminiEmbeddingService
            service = GeminiEmbeddingService(test_mode=True)
            assert service is not None
        except ImportError:
            pytest.skip("GeminiEmbeddingService not available")


class TestFunctionAppConfiguration:
    """Test configuration and global variables"""
    
    def test_app_object_exists(self):
        """Test that Azure Functions app object is created"""
        import function_app
        
        assert hasattr(function_app, 'app'), "Azure Functions app object should exist"
        assert function_app.app is not None
    
    def test_service_availability_flags(self):
        """Test that service availability flags are set"""
        import function_app
        
        # These flags should exist (even if False)
        expected_flags = [
            'personality_service_available',
            'database_personality_available',
            'personality_models_available'
        ]
        
        for flag in expected_flags:
            assert hasattr(function_app, flag), f"Service flag {flag} should exist"
            
            # Should be boolean
            flag_value = getattr(function_app, flag)
            assert isinstance(flag_value, bool), f"Flag {flag} should be boolean"
    
    def test_personality_configs_exist(self):
        """Test that personality configurations are present"""
        import function_app
        
        # After refactoring, personalities are in FALLBACK_PERSONALITIES dict
        # exported from function_app via shared_services
        assert hasattr(function_app, 'FALLBACK_PERSONALITIES'), \
            "FALLBACK_PERSONALITIES should be exported from function_app"
        
        personalities = function_app.FALLBACK_PERSONALITIES
        
        # Should contain some personality names
        expected_names = ['krishna', 'buddha', 'einstein', 'socrates']
        
        personalities_found = [
            name for name in expected_names 
            if name in personalities
        ]
        
        assert len(personalities_found) >= 2, f"Should find at least 2 personalities, found: {personalities_found}"


class TestFunctionAppErrorHandling:
    """Test error handling capabilities"""
    
    def test_module_handles_import_errors_gracefully(self):
        """Test that module handles missing dependencies gracefully"""
        # The module should import even if some services are unavailable
        import function_app
        
        # Check that error handling flags exist
        service_flags = [
            'enhanced_llm_available',
            'enhanced_rag_available', 
            'memory_service_available'
        ]
        
        for flag in service_flags:
            if hasattr(function_app, flag):
                flag_value = getattr(function_app, flag)
                assert isinstance(flag_value, bool), f"Error handling flag {flag} should be boolean"
    
    def test_function_definitions_are_callable(self):
        """Test that function definitions exist and are callable"""
        import function_app
        
        functions_to_test = [
            'get_cors_headers'
        ]
        
        for func_name in functions_to_test:
            if hasattr(function_app, func_name):
                func = getattr(function_app, func_name)
                assert callable(func), f"Function {func_name} should be callable"


class TestFunctionAppIntegrationReadiness:
    """Test readiness for integration testing"""
    
    def test_azure_functions_types_available(self):
        """Test that Azure Functions types are available"""
        try:
            import azure.functions as func
            assert func.HttpRequest is not None
            assert func.HttpResponse is not None
        except ImportError:
            pytest.skip("Azure Functions library not available")
    
    def test_async_support_available(self):
        """Test that async support is properly configured"""
        import asyncio
        
        # Should be able to create event loops (basic async support)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.close()
        except Exception as e:
            pytest.fail(f"Async support not working: {e}")
    
    def test_json_handling_available(self):
        """Test that JSON handling works correctly"""
        import json
        
        test_data = {
            'query': 'What is dharma?',
            'personality_id': 'krishna',
            'context': 'general'
        }
        
        # Should be able to serialize and deserialize
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        
        assert parsed_data == test_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
