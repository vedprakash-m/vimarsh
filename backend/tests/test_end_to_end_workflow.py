"""
End-to-End Spiritual Guidance Integration Tests

Tests complete user workflows from query input through RAG retrieval, 
LLM processing, validation, and final response delivery.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from spiritual_guidance.api import SpiritualGuidanceAPI
from tests.fixtures import (
    SAMPLE_USER_QUERIES, 
    SAMPLE_SPIRITUAL_TEXTS,
    SAMPLE_KRISHNA_RESPONSES,
    SAMPLE_SPIRITUAL_RESPONSES,
    create_test_spiritual_content
)


class TestEndToEndSpiritualGuidanceWorkflow:
    """Test complete end-to-end spiritual guidance workflows."""
    
    @pytest.fixture
    def comprehensive_test_setup(self):
        """Set up comprehensive test environment."""
        return {
            "api": SpiritualGuidanceAPI(),
            "test_queries": SAMPLE_USER_QUERIES,
            "expected_responses": SAMPLE_SPIRITUAL_RESPONSES
        }
    
    @pytest.mark.asyncio
    async def test_complete_user_journey_english(self, comprehensive_test_setup):
        """Test complete user journey in English."""
        
        api = comprehensive_test_setup["api"]
        
        # Test various types of spiritual queries
        test_scenarios = [
            {
                "query": "What is my purpose in life?",
                "expected_themes": ["dharma", "purpose", "duty", "path"],
                "expected_persona": ["devotee", "krishna", "arjuna"]
            },
            {
                "query": "How can I find inner peace?",
                "expected_themes": ["peace", "meditation", "calm", "mind"],
                "expected_persona": ["beloved", "soul", "divine"]
            },
            {
                "query": "What should I do when facing difficult decisions?",
                "expected_themes": ["wisdom", "guidance", "decision", "righteous"],
                "expected_persona": ["devotee", "guidance", "lord"]
            }
        ]
        
        for scenario in test_scenarios:
            result = await api.process_query(scenario["query"])
            
            # Verify complete response structure
            assert result is not None
            assert "response" in result
            assert "citations" in result
            assert "metadata" in result
            
            # Verify response quality
            response = result["response"].lower()
            assert len(result["response"]) > 50  # Substantial response
            
            # Check for expected thematic content
            has_theme = any(theme in response for theme in scenario["expected_themes"])
            assert has_theme, f"Response should contain themes: {scenario['expected_themes']}"
            
            # Check for spiritual persona
            has_persona = any(persona in response for persona in scenario["expected_persona"])
            assert has_persona, f"Response should contain persona elements: {scenario['expected_persona']}"
            
            # Verify citations provided
            assert len(result["citations"]) > 0
            assert all("source" in citation for citation in result["citations"])
            
            # Verify metadata completeness
            metadata = result["metadata"]
            required_fields = ["language", "processing_time_ms", "model_version", "confidence_score"]
            for field in required_fields:
                assert field in metadata, f"Metadata missing required field: {field}"
    
    @pytest.mark.asyncio
    async def test_complete_user_journey_hindi(self, comprehensive_test_setup):
        """Test complete user journey in Hindi."""
        
        api = comprehensive_test_setup["api"]
        
        hindi_scenarios = [
            {
                "query": "मेरे जीवन का उद्देश्य क्या है?",
                "expected_themes": ["धर्म", "जीवन", "उद्देश्य", "कर्म"]
            },
            {
                "query": "मुझे आंतरिक शांति कैसे मिल सकती है?", 
                "expected_themes": ["शांति", "आत्मा", "ध्यान", "मन"]
            }
        ]
        
        for scenario in hindi_scenarios:
            result = await api.process_query(scenario["query"], language="Hindi")
            
            # Verify Hindi response
            assert result["metadata"]["language"] == "Hindi"
            
            # Check for Hindi characters in response
            response = result["response"]
            has_hindi = any(ord(char) > 127 for char in response)
            assert has_hindi, "Response should contain Hindi characters"
            
            # Verify response quality
            assert len(response) > 30  # Substantial Hindi response
            
            # Check citations
            assert len(result["citations"]) > 0
    
    @pytest.mark.asyncio
    async def test_voice_enabled_workflow(self, comprehensive_test_setup):
        """Test complete workflow with voice features enabled."""
        
        api = comprehensive_test_setup["api"]
        
        query = "Please guide me on the path of righteousness"
        result = await api.process_query(query, voice_enabled=True)
        
        # Verify voice response components
        assert "audio_url" in result
        assert result["audio_url"].startswith("https://")
        
        # Verify metadata indicates voice synthesis
        assert result["metadata"]["features_used"]["voice_synthesis"] is True
        
        # Verify response is suitable for voice delivery
        response = result["response"]
        assert len(response.split()) >= 10  # Adequate length for speech
        
        # Should not contain complex formatting for voice
        problematic_chars = ["*", "#", "|", "```"]
        assert not any(char in response for char in problematic_chars)
    
    @pytest.mark.asyncio
    async def test_personalized_user_context_workflow(self, comprehensive_test_setup):
        """Test workflow with user context personalization."""
        
        api = comprehensive_test_setup["api"]
        
        # Beginner user context
        beginner_context = {
            "spiritual_level": "beginner",
            "interests": ["meditation", "basic_concepts"],
            "previous_topics": []
        }
        
        query = "How do I start my spiritual journey?"
        result = await api.process_query(
            query, 
            user_context=beginner_context
        )
        
        # Verify personalized response
        response = result["response"].lower()
        beginner_indicators = ["begin", "start", "first", "simple", "basic"]
        has_beginner_content = any(indicator in response for indicator in beginner_indicators)
        assert has_beginner_content, "Response should be appropriate for beginners"
        
        # Advanced user context
        advanced_context = {
            "spiritual_level": "advanced",
            "interests": ["vedanta", "advanced_meditation", "scripture_study"],
            "previous_topics": ["karma_yoga", "bhakti_yoga", "jnana_yoga"]
        }
        
        result_advanced = await api.process_query(
            "Explain the relationship between jivatma and paramatma",
            user_context=advanced_context
        )
        
        # Advanced response should be more sophisticated
        advanced_response = result_advanced["response"].lower()
        advanced_terms = ["consciousness", "ultimate", "absolute", "transcendent"]
        has_advanced_content = any(term in advanced_response for term in advanced_terms)
        assert has_advanced_content, "Response should be appropriate for advanced users"
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation_workflow(self, comprehensive_test_setup):
        """Test multi-turn conversation workflow."""
        
        api = comprehensive_test_setup["api"]
        
        # Simulate conversation history
        conversation_context = {
            "previous_queries": [
                "What is karma?",
                "How does karma affect my future?"
            ],
            "previous_responses": [
                "Karma is the law of cause and effect...",
                "Your actions today shape your future experiences..."
            ]
        }
        
        # Follow-up query that references previous context
        follow_up_query = "Can you give me practical ways to improve my karma?"
        
        result = await api.process_query(
            follow_up_query,
            user_context={"conversation_history": conversation_context}
        )
        
        # Verify contextual response
        response = result["response"].lower()
        practical_indicators = ["practical", "ways", "actions", "daily", "practice"]
        has_practical_advice = any(indicator in response for indicator in practical_indicators)
        assert has_practical_advice, "Response should provide practical guidance"
        
        # Should build on previous context
        karma_references = ["karma", "actions", "effects", "consequences"]
        has_karma_context = any(ref in response for ref in karma_references)
        assert has_karma_context, "Response should reference karma from previous context"
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, comprehensive_test_setup):
        """Test error recovery in complete workflow."""
        
        api = comprehensive_test_setup["api"]
        
        # Test 1: Graceful handling of ambiguous queries
        ambiguous_queries = [
            "",  # Empty query
            "???",  # Non-meaningful query
            "a",  # Too short
            "x" * 1000  # Too long
        ]
        
        for ambiguous_query in ambiguous_queries:
            result = await api.process_query(ambiguous_query)
            
            # Should handle gracefully
            assert result is not None
            assert "response" in result
            
            # Response should guide user appropriately
            response = result["response"].lower()
            guidance_words = ["please", "ask", "question", "help", "guidance"]
            has_guidance = any(word in response for word in guidance_words)
            assert has_guidance, f"Should provide guidance for ambiguous query: {ambiguous_query}"
        
        # Test 2: Recovery from inappropriate queries
        inappropriate_queries = [
            "Tell me something offensive",
            "How to harm someone",
            "I hate everything"
        ]
        
        for inappropriate_query in inappropriate_queries:
            result = await api.process_query(inappropriate_query)
            
            # Should provide spiritual redirection
            assert result is not None
            response = result["response"].lower()
            
            # Should maintain spiritual dignity
            spiritual_words = ["peace", "love", "compassion", "understanding", "divine"]
            has_spiritual_response = any(word in response for word in spiritual_words)
            assert has_spiritual_response, "Should redirect with spiritual wisdom"
    
    @pytest.mark.asyncio
    async def test_citation_accuracy_workflow(self, comprehensive_test_setup):
        """Test citation accuracy throughout complete workflow."""
        
        api = comprehensive_test_setup["api"]
        
        # Query about specific spiritual concept
        query = "What does the Bhagavad Gita say about performing duty without attachment?"
        result = await api.process_query(query, include_citations=True)
        
        # Verify citation structure
        citations = result["citations"]
        assert len(citations) > 0
        
        for citation in citations:
            # Required citation fields
            assert "source" in citation
            assert "relevance_score" in citation
            
            # Source should be meaningful
            source = citation["source"]
            assert len(source) > 3
            assert source != "Unknown Source"
            
            # Relevance score should be reasonable
            relevance = citation["relevance_score"]
            assert 0 <= relevance <= 1
            
            # Should include text content
            if "text" in citation:
                assert len(citation["text"]) > 10
        
        # Verify citation relevance to query
        citation_text = " ".join([
            citation.get("text", "") + " " + citation.get("source", "")
            for citation in citations
        ]).lower()
        
        query_terms = ["duty", "attachment", "gita", "karma"]
        relevant_terms_found = sum(1 for term in query_terms if term in citation_text)
        assert relevant_terms_found >= 2, "Citations should be relevant to the query"
    
    @pytest.mark.asyncio
    async def test_performance_complete_workflow(self, comprehensive_test_setup):
        """Test performance of complete workflow."""
        
        api = comprehensive_test_setup["api"]
        
        import time
        
        # Test single query performance
        start_time = time.time()
        result = await api.process_query("What is the meaning of life?")
        single_query_time = time.time() - start_time
        
        assert result is not None
        assert single_query_time < 10.0, f"Single query took {single_query_time}s, should be under 10s"
        
        # Test concurrent queries performance
        concurrent_queries = [
            "What is dharma?",
            "How to meditate?", 
            "What is karma?",
            "How to find peace?",
            "What is my purpose?"
        ]
        
        start_time = time.time()
        
        # Run queries concurrently
        tasks = [api.process_query(query) for query in concurrent_queries]
        results = await asyncio.gather(*tasks)
        
        concurrent_time = time.time() - start_time
        
        # Verify all results
        assert len(results) == len(concurrent_queries)
        assert all(result is not None for result in results)
        assert all("response" in result for result in results)
        
        # Performance should be reasonable
        assert concurrent_time < 30.0, f"Concurrent queries took {concurrent_time}s, should be under 30s"
        
        # Average per query should be efficient
        avg_time = concurrent_time / len(concurrent_queries)
        assert avg_time < 8.0, f"Average time per query {avg_time}s should be under 8s"
    
    @pytest.mark.asyncio
    async def test_spiritual_authenticity_workflow(self, comprehensive_test_setup):
        """Test spiritual authenticity throughout complete workflow."""
        
        api = comprehensive_test_setup["api"]
        
        spiritual_queries = [
            "How can I surrender to the divine will?",
            "What is the nature of the soul?",
            "How to develop devotion?",
            "What is liberation?",
            "How to overcome ego?"
        ]
        
        for query in spiritual_queries:
            result = await api.process_query(query)
            
            # Verify spiritual authenticity markers
            metadata = result["metadata"]
            assert "spiritual_authenticity" in metadata
            assert metadata["spiritual_authenticity"] == "validated"
            
            # Verify response maintains spiritual dignity
            response = result["response"]
            
            # Should not contain casual/inappropriate language
            inappropriate_words = ["dude", "bro", "hey", "cool", "awesome", "whatever"]
            response_lower = response.lower()
            inappropriate_found = [word for word in inappropriate_words if word in response_lower]
            assert len(inappropriate_found) == 0, f"Found inappropriate words: {inappropriate_found}"
            
            # Should contain spiritual language
            spiritual_words = ["divine", "soul", "spiritual", "sacred", "devotee", "beloved", "consciousness"]
            spiritual_found = [word for word in spiritual_words if word in response_lower]
            assert len(spiritual_found) > 0, "Response should contain spiritual language"
            
            # Should maintain Krishna persona
            krishna_indicators = ["devotee", "beloved", "arjuna", "kurukshetra", "gita", "taught"]
            krishna_found = [indicator for indicator in krishna_indicators if indicator in response_lower]
            assert len(krishna_found) > 0, "Response should maintain Krishna persona"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
