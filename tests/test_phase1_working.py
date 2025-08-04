#!/usr/bin/env python3
"""
Simple working tests for Phase 1 completion
"""

import asyncio
import pytest
import sys
import os

# Add backend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestPhase1Completion:
    """Test that Phase 1 fixes are working"""
    
    def test_imports_working(self):
        """Test that critical imports work"""
        # Test LLM service import
        from services.llm_service import llm_service
        assert llm_service is not None
        
        # Test error handling import
        from core.error_handling import error_handler, ErrorCategory
        assert error_handler is not None
        assert ErrorCategory.LLM_ERROR is not None
        
        # Test function app import
        import function_app
        assert function_app is not None
    
    @pytest.mark.asyncio
    async def test_llm_service_basic_functionality(self):
        """Test that LLM service generates responses"""
        from services.llm_service import llm_service
        
        response = await llm_service.get_spiritual_guidance(
            "What is dharma?", 
            personality_id="krishna"
        )
        
        assert response is not None
        assert len(response.content) > 50
        assert response.confidence > 0
        assert isinstance(response.citations, list)
        assert "dharma" in response.content.lower()
    
    def test_error_handling_basic_functionality(self):
        """Test that error handling works"""
        from core.error_handling import error_handler, ErrorCategory
        
        # Test error handling
        error_info = error_handler.handle_error(Exception("Test error"), ErrorCategory.LLM_ERROR)
        assert error_info.category == ErrorCategory.LLM_ERROR
        assert error_info.message == "Test error"
        
        # Test fallback response
        fallback = error_handler.get_simple_fallback_response(ErrorCategory.LLM_ERROR)
        assert len(fallback) > 20
        assert "🙏" in fallback
    
    @pytest.mark.asyncio
    async def test_different_spiritual_queries(self):
        """Test LLM service with different types of spiritual queries"""
        from services.llm_service import llm_service
        
        queries = [
            "How can I find inner peace?",
            "What does Krishna teach about suffering?", 
            "I feel lost in life. What should I do?"
        ]
        
        for query in queries:
            response = await llm_service.get_spiritual_guidance(
                query, 
                personality_id="krishna"
            )
            assert response is not None
            assert len(response.content) > 30
            assert response.confidence > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
