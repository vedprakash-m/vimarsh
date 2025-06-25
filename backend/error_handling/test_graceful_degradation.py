"""
Test suite for the graceful degradation system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from graceful_degradation import (
    GracefulDegradationManager, ServiceType, DegradationLevel, ServiceHealth,
    FallbackResponse, LLMFallbackStrategy, VectorSearchFallbackStrategy,
    ContentModerationFallbackStrategy, ExpertReviewFallbackStrategy,
    handle_service_failure, handle_multiple_failures, get_system_health
)


class TestServiceHealth:
    """Test cases for ServiceHealth"""
    
    def test_service_health_creation(self):
        """Test ServiceHealth creation and default values"""
        health = ServiceHealth(ServiceType.LLM_SERVICE)
        
        assert health.service_type == ServiceType.LLM_SERVICE
        assert health.is_healthy is True
        assert health.error_count == 0
        assert health.degradation_level == DegradationLevel.FULL_SERVICE
        assert isinstance(health.last_check, datetime)
    
    def test_service_health_with_data(self):
        """Test ServiceHealth with specific data"""
        health = ServiceHealth(
            service_type=ServiceType.DATABASE,
            is_healthy=False,
            error_count=5,
            response_time=2.5
        )
        
        assert health.service_type == ServiceType.DATABASE
        assert health.is_healthy is False
        assert health.error_count == 5
        assert health.response_time == 2.5


class TestFallbackResponse:
    """Test cases for FallbackResponse"""
    
    def test_fallback_response_creation(self):
        """Test FallbackResponse creation"""
        response = FallbackResponse(
            content="Test response",
            confidence=0.8,
            source="test_source",
            limitations=["Limited feature A"],
            suggestions=["Try again later"]
        )
        
        assert response.content == "Test response"
        assert response.confidence == 0.8
        assert response.source == "test_source"
        assert "Limited feature A" in response.limitations
        assert "Try again later" in response.suggestions


class TestLLMFallbackStrategy:
    """Test cases for LLM fallback strategy"""
    
    def setup_method(self):
        self.strategy = LLMFallbackStrategy()
    
    def test_is_applicable(self):
        """Test if strategy is applicable for LLM failures"""
        assert self.strategy.is_applicable([ServiceType.LLM_SERVICE], {})
        assert not self.strategy.is_applicable([ServiceType.DATABASE], {})
        assert self.strategy.is_applicable([ServiceType.LLM_SERVICE, ServiceType.DATABASE], {})
    
    @pytest.mark.asyncio
    async def test_execute_spiritual_question(self):
        """Test execution with spiritual question"""
        context = {"user_query": "What is the meaning of life according to spiritual teachings?"}
        
        response = await self.strategy.execute(context)
        
        assert isinstance(response, FallbackResponse)
        assert response.confidence == 0.6
        assert response.source == "static_knowledge_base"
        assert "Advanced AI capabilities temporarily unavailable" in response.limitations
        assert len(response.suggestions) > 0
        assert "spiritual" in response.content.lower() or "gita" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_execute_meditation_query(self):
        """Test execution with meditation-related query"""
        context = {"user_query": "How should I meditate for inner peace?"}
        
        response = await self.strategy.execute(context)
        
        assert response.metadata["category"] == "meditation_guidance"
        assert "meditat" in response.content.lower() or "breath" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_execute_life_guidance(self):
        """Test execution with life guidance query"""
        context = {"user_query": "I'm facing problems in life, please help me"}
        
        response = await self.strategy.execute(context)
        
        assert response.metadata["category"] == "life_guidance"
        assert any(word in response.content.lower() for word in ["life", "challenge", "difficulty", "divine", "growth", "wisdom"])


class TestVectorSearchFallbackStrategy:
    """Test cases for vector search fallback strategy"""
    
    def setup_method(self):
        self.strategy = VectorSearchFallbackStrategy()
    
    def test_is_applicable(self):
        """Test if strategy is applicable for vector search failures"""
        assert self.strategy.is_applicable([ServiceType.VECTOR_SEARCH], {})
        assert not self.strategy.is_applicable([ServiceType.LLM_SERVICE], {})
    
    @pytest.mark.asyncio
    async def test_execute_karma_query(self):
        """Test execution with karma-related query"""
        context = {"user_query": "Tell me about karma in the Bhagavad Gita"}
        
        response = await self.strategy.execute(context)
        
        assert isinstance(response, FallbackResponse)
        assert response.confidence == 0.4
        assert response.source == "keyword_based_search"
        # The response should contain the karma verse (which mentions actions, not specifically "karma")
        assert "2.47" in response.content  # Bhagavad Gita verse reference
        assert "actions" in response.content.lower() or "karma" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_execute_unknown_query(self):
        """Test execution with query that doesn't match keywords"""
        context = {"user_query": "Tell me about something completely unrelated"}
        
        response = await self.strategy.execute(context)
        
        # Should fall back to wisdom verse - check for knowledge/transcendental concepts
        assert "4.38" in response.content  # Wisdom verse reference
        assert any(word in response.content.lower() for word in ["wisdom", "knowledge", "transcendental"])
    
    @pytest.mark.asyncio
    async def test_execute_multiple_keywords(self):
        """Test execution with multiple matching keywords"""
        context = {"user_query": "How does karma relate to dharma and meditation?"}
        
        response = await self.strategy.execute(context)
        
        # Should include multiple relevant verses
        assert any(keyword in response.content for keyword in ["karma", "dharma", "meditation"])


class TestContentModerationFallbackStrategy:
    """Test cases for content moderation fallback strategy"""
    
    def setup_method(self):
        self.strategy = ContentModerationFallbackStrategy()
    
    def test_is_applicable(self):
        """Test if strategy is applicable for content moderation failures"""
        assert self.strategy.is_applicable([ServiceType.CONTENT_MODERATION], {})
        assert not self.strategy.is_applicable([ServiceType.LLM_SERVICE], {})
    
    @pytest.mark.asyncio
    async def test_execute_clean_content(self):
        """Test execution with clean content"""
        context = {"content": "This is a perfectly normal spiritual question"}
        
        response = await self.strategy.execute(context)
        
        assert response.confidence == 0.3
        assert response.source == "basic_content_filter"
        assert "temporarily limited" in response.content
        assert response.metadata["flagged_words"] == []
    
    @pytest.mark.asyncio
    async def test_execute_flagged_content(self):
        """Test execution with potentially inappropriate content"""
        context = {"content": "This content contains inappropriate and harmful language"}
        
        response = await self.strategy.execute(context)
        
        assert "sensitive content" in response.content
        assert len(response.metadata["flagged_words"]) > 0
        assert "inappropriate" in response.metadata["flagged_words"]


class TestExpertReviewFallbackStrategy:
    """Test cases for expert review fallback strategy"""
    
    def setup_method(self):
        self.strategy = ExpertReviewFallbackStrategy()
    
    def test_is_applicable(self):
        """Test if strategy is applicable for expert review failures"""
        assert self.strategy.is_applicable([ServiceType.EXPERT_REVIEW], {})
        assert not self.strategy.is_applicable([ServiceType.DATABASE], {})
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """Test execution of expert review fallback"""
        context = {"user_query": "Some spiritual question"}
        
        response = await self.strategy.execute(context)
        
        assert response.confidence == 0.5
        assert response.source == "pre_validated_content"
        assert "expert review system is temporarily unavailable" in response.content
        assert "not validated by spiritual scholars" in response.limitations[1]


class TestGracefulDegradationManager:
    """Test cases for GracefulDegradationManager"""
    
    def setup_method(self):
        self.manager = GracefulDegradationManager()
    
    def test_initialization(self):
        """Test manager initialization"""
        assert len(self.manager.service_health) == len(ServiceType)
        assert len(self.manager.degradation_strategies) > 0
        
        # Check all services are initially healthy
        for health in self.manager.service_health.values():
            assert health.is_healthy is True
            assert health.degradation_level == DegradationLevel.FULL_SERVICE
    
    def test_update_service_health_failure(self):
        """Test updating service health on failure"""
        error = Exception("Test error")
        
        self.manager._update_service_health(
            ServiceType.LLM_SERVICE,
            is_healthy=False,
            error=error
        )
        
        health = self.manager.service_health[ServiceType.LLM_SERVICE]
        assert health.is_healthy is False
        assert health.error_count == 1
        assert health.last_error == "Test error"
    
    def test_update_service_health_recovery(self):
        """Test updating service health on recovery"""
        # First, make service unhealthy
        self.manager._update_service_health(ServiceType.LLM_SERVICE, is_healthy=False)
        
        # Then recover
        self.manager._update_service_health(ServiceType.LLM_SERVICE, is_healthy=True)
        
        health = self.manager.service_health[ServiceType.LLM_SERVICE]
        assert health.is_healthy is True
        assert health.error_count == 0  # Should be decremented
    
    def test_assess_degradation_level_single_failure(self):
        """Test degradation level assessment with single service failure"""
        # Non-critical service failure
        level = self.manager._assess_degradation_level([ServiceType.VOICE_PROCESSING])
        assert level == DegradationLevel.MINOR_DEGRADATION
        
        # Critical service failure
        level = self.manager._assess_degradation_level([ServiceType.LLM_SERVICE])
        assert level == DegradationLevel.MAJOR_DEGRADATION
    
    def test_assess_degradation_level_multiple_failures(self):
        """Test degradation level assessment with multiple failures"""
        # Multiple non-critical failures
        level = self.manager._assess_degradation_level([
            ServiceType.VOICE_PROCESSING,
            ServiceType.CONTENT_MODERATION,
            ServiceType.EXPERT_REVIEW
        ])
        assert level == DegradationLevel.MAJOR_DEGRADATION
        
        # Critical + vector search failure
        level = self.manager._assess_degradation_level([
            ServiceType.LLM_SERVICE,
            ServiceType.VECTOR_SEARCH
        ])
        assert level == DegradationLevel.EMERGENCY_MODE
    
    @pytest.mark.asyncio
    async def test_handle_service_failure_llm(self):
        """Test handling LLM service failure"""
        context = {"user_query": "What is dharma?"}
        error = Exception("LLM service unavailable")
        
        response = await self.manager.handle_service_failure(
            ServiceType.LLM_SERVICE,
            context,
            error
        )
        
        assert isinstance(response, FallbackResponse)
        assert "temporarily limited" in response.content
        health = self.manager.service_health[ServiceType.LLM_SERVICE]
        assert health.is_healthy is False
        assert health.error_count == 1
    
    @pytest.mark.asyncio
    async def test_handle_multiple_failures(self):
        """Test handling multiple service failures"""
        failed_services = [ServiceType.LLM_SERVICE, ServiceType.VECTOR_SEARCH]
        context = {"user_query": "Tell me about meditation"}
        
        response = await self.manager.handle_multiple_failures(failed_services, context)
        
        assert isinstance(response, FallbackResponse)
        assert response.source in ["combined_fallback_strategies", "emergency_static_response"]
        
        # Check that services are marked as unhealthy
        for service in failed_services:
            health = self.manager.service_health[service]
            assert health.is_healthy is False
    
    @pytest.mark.asyncio
    async def test_emergency_fallback(self):
        """Test emergency fallback when all strategies fail"""
        context = {"user_query": "Any question"}
        
        response = await self.manager._emergency_fallback(context)
        
        assert response.confidence == 0.2
        assert response.source == "emergency_static_response"
        assert "emergency mode" in response.content
        assert "Bhagavad Gita directly" in response.content
    
    def test_combine_responses(self):
        """Test combining multiple fallback responses"""
        responses = [
            FallbackResponse(
                content="Response 1",
                confidence=0.6,
                source="source1",
                limitations=["Limitation 1"],
                suggestions=["Suggestion 1"]
            ),
            FallbackResponse(
                content="Response 2",
                confidence=0.8,
                source="source2",
                limitations=["Limitation 2"],
                suggestions=["Suggestion 2", "Suggestion 1"]  # Duplicate
            )
        ]
        
        combined = self.manager._combine_responses(
            responses,
            [ServiceType.LLM_SERVICE, ServiceType.VECTOR_SEARCH]
        )
        
        assert combined.content == "Response 2"  # Higher confidence response
        assert combined.confidence == 0.8 * 0.8  # Reduced for combination
        assert combined.source == "combined_fallback_strategies"
        assert len(combined.limitations) == 2
        assert len(combined.suggestions) == 2  # Duplicates removed
    
    def test_get_system_health_status_healthy(self):
        """Test system health status when all services are healthy"""
        status = self.manager.get_system_health_status()
        
        assert status["overall_health"] == "healthy"
        assert status["degradation_level"] == DegradationLevel.FULL_SERVICE.value
        assert len(status["active_degradations"]) == 0
        assert len(status["services"]) == len(ServiceType)
    
    def test_get_system_health_status_degraded(self):
        """Test system health status when services are degraded"""
        # Make some services unhealthy
        self.manager._update_service_health(ServiceType.LLM_SERVICE, is_healthy=False)
        self.manager._update_service_health(ServiceType.VECTOR_SEARCH, is_healthy=False)
        
        status = self.manager.get_system_health_status()
        
        assert status["overall_health"] == "degraded"
        assert status["degradation_level"] == DegradationLevel.EMERGENCY_MODE.value
        assert len(status["active_degradations"]) == 2
        assert len(status["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_attempt_service_recovery(self):
        """Test service recovery attempt"""
        # Make service unhealthy first
        self.manager._update_service_health(ServiceType.LLM_SERVICE, is_healthy=False)
        
        # Attempt recovery multiple times
        for i in range(3):
            recovered = await self.manager.attempt_service_recovery(ServiceType.LLM_SERVICE)
            if i < 2:
                assert recovered is False
            else:
                assert recovered is True
        
        # Check service is marked as healthy after recovery
        health = self.manager.service_health[ServiceType.LLM_SERVICE]
        assert health.is_healthy is True


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @pytest.mark.asyncio
    async def test_handle_service_failure_function(self):
        """Test handle_service_failure convenience function"""
        context = {"user_query": "Test query"}
        error = Exception("Test error")
        
        response = await handle_service_failure(ServiceType.LLM_SERVICE, context, error)
        
        assert isinstance(response, FallbackResponse)
    
    @pytest.mark.asyncio
    async def test_handle_multiple_failures_function(self):
        """Test handle_multiple_failures convenience function"""
        failed_services = [ServiceType.LLM_SERVICE, ServiceType.DATABASE]
        context = {"user_query": "Test query"}
        
        response = await handle_multiple_failures(failed_services, context)
        
        assert isinstance(response, FallbackResponse)
    
    def test_get_system_health_function(self):
        """Test get_system_health convenience function"""
        status = get_system_health()
        
        assert isinstance(status, dict)
        assert "overall_health" in status
        assert "services" in status


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def setup_method(self):
        self.manager = GracefulDegradationManager()
    
    @pytest.mark.asyncio
    async def test_cascading_failure_scenario(self):
        """Test cascading failure scenario"""
        context = {"user_query": "How can I find peace through meditation?"}
        
        # Start with LLM failure
        response1 = await self.manager.handle_service_failure(
            ServiceType.LLM_SERVICE, context
        )
        assert "temporarily limited" in response1.content
        
        # Add vector search failure
        response2 = await self.manager.handle_multiple_failures(
            [ServiceType.LLM_SERVICE, ServiceType.VECTOR_SEARCH], context
        )
        assert response2.confidence <= response1.confidence
        
        # Add content moderation failure (should trigger emergency mode)
        response3 = await self.manager.handle_multiple_failures(
            [ServiceType.LLM_SERVICE, ServiceType.VECTOR_SEARCH, ServiceType.CONTENT_MODERATION],
            context
        )
        assert response3.source in ["combined_fallback_strategies", "emergency_static_response"]
    
    @pytest.mark.asyncio
    async def test_recovery_scenario(self):
        """Test service recovery scenario"""
        # Create failures
        self.manager._update_service_health(ServiceType.LLM_SERVICE, is_healthy=False)
        self.manager._update_service_health(ServiceType.VECTOR_SEARCH, is_healthy=False)
        
        # Check degraded status
        status_before = self.manager.get_system_health_status()
        assert status_before["overall_health"] == "degraded"
        
        # Attempt recovery
        llm_recovered = await self.manager.attempt_service_recovery(ServiceType.LLM_SERVICE)
        vector_recovered = await self.manager.attempt_service_recovery(ServiceType.VECTOR_SEARCH)
        
        # Should recover after 3 attempts each (as per implementation)
        for _ in range(2):
            await self.manager.attempt_service_recovery(ServiceType.LLM_SERVICE)
            await self.manager.attempt_service_recovery(ServiceType.VECTOR_SEARCH)
        
        # Check recovered status
        status_after = self.manager.get_system_health_status()
        assert status_after["overall_health"] == "healthy"
        assert len(status_after["active_degradations"]) == 0


if __name__ == "__main__":
    pytest.main([__file__])
