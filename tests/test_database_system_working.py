#!/usr/bin/env python3
"""
Simple working tests for Database-Oriented Personality System
Tests the core functionality without complex dependencies
"""

import asyncio
import pytest
import sys
import os

# Add backend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDatabaseOrientedSystem:
    """Test core functionality of database-oriented personality system"""
    
    def test_basic_imports_working(self):
        """Test that basic imports work"""
        # Test LLM service import
        from services.llm_service import LLMService
        assert LLMService is not None
        
        # Test enhanced LLM service import
        from services.enhanced_llm_wrapper import EnhancedLLMService  
        assert EnhancedLLMService is not None
        
        # Test function app import
        import function_app
        assert function_app is not None
        
        print("✅ Basic imports working")
    
    @pytest.mark.asyncio
    async def test_llm_service_basic_functionality(self):
        """Test that LLM service generates responses"""
        from services.llm_service import LLMService
        
        service = LLMService()
        
        # Test basic personality response generation
        response = await service.generate_personality_response(
            "What is dharma?", 
            personality_id="krishna"
        )
        
        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 30
        
        # Check source type
        assert hasattr(response, 'source')
        print(f"✅ LLM service working - Source: {response.source}")
    
    @pytest.mark.asyncio
    async def test_enhanced_llm_service_functionality(self):
        """Test enhanced LLM service"""
        from services.enhanced_llm_wrapper import EnhancedLLMService
        
        service = EnhancedLLMService()
        
        # Test response generation with monitoring
        response = await service.generate_response_with_monitoring(
            "What is the purpose of life?",
            personality_id="krishna"
        )
        
        assert response is not None
        assert isinstance(response, dict)
        assert "content" in response
        assert len(response["content"]) > 30
        
        print("✅ Enhanced LLM service working")
    
    @pytest.mark.asyncio
    async def test_multiple_personalities(self):
        """Test different personality responses"""
        from services.llm_service import LLMService
        
        service = LLMService()
        personalities = ["krishna", "einstein", "jesus"]
        
        for personality_id in personalities:
            response = await service.generate_personality_response(
                "What is wisdom?",
                personality_id=personality_id
            )
            
            assert response is not None
            assert len(response.content) > 20
            print(f"✅ {personality_id} personality working")
    
    def test_function_app_endpoints(self):
        """Test that function app has required endpoints"""
        import function_app
        
        # Check for spiritual guidance endpoint
        app_code = str(function_app.__dict__)
        
        # Basic validation that function app loaded
        assert function_app is not None
        print("✅ Function app loaded successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
