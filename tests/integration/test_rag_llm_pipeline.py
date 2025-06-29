"""
Integration tests for the complete RAG-LLM pipeline
Tests real component interactions with minimal external dependencies
"""

import pytest
import asyncio
from unittest.mock import patch, Mock

from backend.rag_pipeline.rag_service import RAGService
from backend.llm_integration.spiritual_guidance import SpiritualGuidanceService
from backend.rag_pipeline.vector_storage import LocalVectorStorage


class TestRAGLLMIntegration:
    """Integration tests for RAG-LLM pipeline"""
    
    @pytest.fixture
    def test_documents(self):
        """Sample spiritual text documents for testing"""
        return [
            {
                "id": "bg_2_47",
                "text": "Your right is to perform duty only, never to the fruits thereof. Let not the fruits of action be your motive, nor be your attachment to inaction.",
                "citation": "Bhagavad Gita 2.47",
                "metadata": {"chapter": 2, "verse": 47}
            },
            {
                "id": "bg_2_48", 
                "text": "Perform action, O Arjuna, being steadfast in yoga and abandoning attachment. Be even-minded in success and failure.",
                "citation": "Bhagavad Gita 2.48",
                "metadata": {"chapter": 2, "verse": 48}
            }
        ]
    
    @pytest.fixture
    def vector_store(self, test_documents):
        """Create vector store with test documents"""
        store = LocalVectorStorage(embedding_model="all-MiniLM-L6-v2")
        
        # Add test documents
        for doc in test_documents:
            store.add_document(
                doc_id=doc["id"],
                text=doc["text"],
                metadata=doc["metadata"]
            )
        
        return store
    
    @pytest.fixture
    def rag_service(self, vector_store):
        """Create RAG service with test vector store"""
        return RAGService(vector_store=vector_store)
    
    @pytest.mark.integration
    async def test_end_to_end_guidance_generation(self, rag_service, test_documents):
        """Test complete pipeline from query to guidance"""
        with patch('backend.llm_integration.llm_service.gemini_client') as mock_client:
            # Mock LLM response
            mock_response = Mock()
            mock_response.text = (
                "According to Lord Krishna in the Bhagavad Gita, your dharma or duty "
                "should be performed without attachment to results. As stated in verse 2.47, "
                "focus on righteous action rather than the fruits thereof."
            )
            mock_client.generate_content.return_value = mock_response
            
            # Create guidance service
            guidance_service = SpiritualGuidanceService(
                rag_pipeline=rag_service,
                llm_service=Mock()  # Will be mocked above
            )
            
            query = "What should I focus on when doing my duty?"
            response = await guidance_service.get_guidance(query)
            
            assert response.success is True
            assert "Bhagavad Gita" in response.text
            assert len(response.citations) > 0
            assert "2.47" in str(response.citations)
    
    @pytest.mark.integration
    async def test_context_retrieval_accuracy(self, rag_service):
        """Test RAG retrieval accuracy for spiritual queries"""
        query = "How should I approach my duties?"
        
        contexts = await rag_service.retrieve_context(query, top_k=2)
        
        assert len(contexts) == 2
        assert all("duty" in context["text"].lower() or "action" in context["text"].lower() 
                  for context in contexts)
        assert all(context["relevance_score"] > 0.5 for context in contexts)
    
    @pytest.mark.integration
    async def test_citation_preservation(self, rag_service):
        """Test that citations are properly preserved through the pipeline"""
        query = "What does Krishna say about attachment?"
        
        contexts = await rag_service.retrieve_context(query, top_k=1)
        
        assert len(contexts) >= 1
        context = contexts[0]
        assert "citation" in context
        assert "Bhagavad Gita" in context["citation"]
        assert context["citation"].count(".") >= 1  # Has chapter.verse format
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_concurrent_requests(self, rag_service):
        """Test pipeline performance under concurrent load"""
        queries = [
            "What is dharma?",
            "How to overcome attachment?", 
            "What is the path to moksha?",
            "How should I face difficulties?"
        ]
        
        # Run concurrent queries
        tasks = [
            rag_service.retrieve_context(query, top_k=1) 
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == len(queries)
        assert all(len(result) >= 1 for result in results)
        assert all(result[0]["relevance_score"] > 0.3 for result in results)


class TestVoiceIntegrationPipeline:
    """Integration tests for voice interface pipeline"""
    
    @pytest.mark.integration
    @patch('backend.voice_interface.tts_service.google_tts_client')
    @patch('backend.voice_interface.stt_service.google_stt_client')
    async def test_voice_to_voice_pipeline(self, mock_stt, mock_tts):
        """Test complete voice input to voice output pipeline"""
        # Mock STT
        mock_stt.recognize.return_value = "What is dharma according to Krishna?"
        
        # Mock TTS
        mock_tts.synthesize_speech.return_value = b"audio_data"
        
        from backend.voice_interface.voice_pipeline import VoicePipeline
        
        pipeline = VoicePipeline()
        
        # Simulate audio input
        audio_input = b"mock_audio_input"
        
        result = await pipeline.process_voice_query(audio_input, language="en")
        
        assert result.success is True
        assert result.text_response is not None
        assert result.audio_response is not None
        assert len(result.audio_response) > 0
    
    @pytest.mark.integration
    async def test_multilingual_response_generation(self):
        """Test response generation in multiple languages"""
        from backend.llm_integration.spiritual_guidance import SpiritualGuidanceService
        
        # Mock dependencies for this focused test
        with patch('backend.llm_integration.llm_service.gemini_client') as mock_client:
            mock_response = Mock()
            mock_response.text = "धर्म का अर्थ है नैतिकता और न्याय।"  # Hindi response
            mock_client.generate_content.return_value = mock_response
            
            guidance_service = SpiritualGuidanceService(
                rag_pipeline=Mock(),
                llm_service=Mock()
            )
            
            query = "What is dharma?"
            response = await guidance_service.get_guidance(query, language="hi")
            
            assert response.success is True
            assert "धर्म" in response.text  # Hindi word for dharma
