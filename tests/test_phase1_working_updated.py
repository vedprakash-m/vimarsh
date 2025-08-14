#!/usr/bin/env python3
"""
Simple working tests for Phase 1 completion - Database-Oriented Personality System
"""

import asyncio
import pytest
import sys
import os

# Add backend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestPhase1Completion:
    """Test that Phase 1 fixes are working with database-oriented personality system"""
    
    def test_imports_working(self):
        """Test that critical imports work"""
        # Test LLM service import
        from services.llm_service import LLMService
        assert LLMService is not None
        
        # Test database personality service import
        from services.database_driven_personality_service import DatabasePersonalityService
        assert DatabasePersonalityService is not None
        
        # Test enhanced LLM wrapper import
        from services.enhanced_llm_wrapper import EnhancedLLMWrapper
        assert EnhancedLLMWrapper is not None
        
        # Test function app import
        import function_app
        assert function_app is not None
        
        print("✅ All critical imports working")
    
    @pytest.mark.asyncio
    async def test_llm_service_basic_functionality(self):
        """Test that LLM service generates responses with database personalities"""
        from services.llm_service import LLMService
        
        service = LLMService()
        response = await service.generate_personality_response(
            "What is dharma?", 
            personality_id="krishna"
        )
        
        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 50
        assert hasattr(response, 'source')
        assert response.source in ['database', 'fallback']
        
        # Check for spiritual content
        content_lower = response.content.lower()
        spiritual_terms = ['dharma', 'krishna', 'spiritual', 'duty', 'righteous']
        assert any(term in content_lower for term in spiritual_terms)
        
        print("✅ LLM service working with database personalities")
    
    @pytest.mark.asyncio  
    async def test_database_personality_service(self):
        """Test that database personality service works"""
        from services.database_driven_personality_service import DatabasePersonalityService
        
        service = DatabasePersonalityService()
        
        # Test getting personality template
        template = await service.get_personality_template("krishna")
        assert template is not None
        assert hasattr(template, 'name')
        assert hasattr(template, 'system_prompt')
        
        # Test fallback behavior
        fallback_template = await service.get_personality_template("nonexistent")
        assert fallback_template is not None
        assert fallback_template.name == "Krishna (Fallback)"
        
        print("✅ Database personality service working")
    
    @pytest.mark.asyncio
    async def test_different_spiritual_queries(self):
        """Test LLM service with different types of spiritual queries"""
        from services.llm_service import LLMService
        
        service = LLMService()
        queries = [
            "How can I find inner peace?",
            "What does Krishna teach about suffering?", 
            "I feel lost in life. What should I do?"
        ]
        
        for query in queries:
            response = await service.generate_personality_response(
                query, 
                personality_id="krishna"
            )
            assert response is not None
            assert len(response.content) > 30
            assert hasattr(response, 'source')
            
        print("✅ Multiple spiritual queries working")
    
    @pytest.mark.asyncio
    async def test_enhanced_llm_wrapper(self):
        """Test enhanced LLM wrapper with database templates"""
        from services.enhanced_llm_wrapper import EnhancedLLMWrapper
        
        wrapper = EnhancedLLMWrapper()
        
        # Test personality-based generation
        response = await wrapper.generate_personality_response(
            "What is the purpose of life?",
            personality_id="krishna"
        )
        
        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 30
        assert hasattr(response, 'metadata')
        
        print("✅ Enhanced LLM wrapper working")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
