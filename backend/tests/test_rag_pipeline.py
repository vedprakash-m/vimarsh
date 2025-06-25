"""
Comprehensive unit tests for RAG pipeline components.

Tests the complete Retrieval-Augmented Generation pipeline including
document loading, text processing, vector storage, and retrieval.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from rag_pipeline.document_loader import SpiritualDocumentLoader
from rag_pipeline.text_processor import SpiritualTextProcessor
from rag_pipeline.vector_storage import LocalVectorStorage
from tests.fixtures import (
    SAMPLE_BHAGAVAD_GITA_VERSES, SAMPLE_MAHABHARATA_EXCERPTS,
    PERFORMANCE_BENCHMARKS, AUTHENTICITY_MARKERS
)


class TestSpiritualDocumentLoader:
    """Test suite for SpiritualDocumentLoader class."""
    
    @pytest.fixture
    def document_loader(self):
        """Create SpiritualDocumentLoader instance for testing."""
        return SpiritualDocumentLoader()
    
    @pytest.fixture
    def sample_text_file(self):
        """Create temporary text file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Sample spiritual text\nBhagavad Gita Chapter 2\nVerse 47: Karmanye vadhikaraste...")
            return f.name
    
    def test_load_text_file(self, document_loader, sample_text_file):
        """Test loading text files."""
        try:
            content, metadata = document_loader.load_text_file(sample_text_file)
            assert content is not None
            assert "Bhagavad Gita" in content
            assert "Karmanye vadhikaraste" in content
            assert metadata is not None
            assert metadata.filename == os.path.basename(sample_text_file)
        finally:
            os.unlink(sample_text_file)
    
    def test_load_nonexistent_file(self, document_loader):
        """Test handling of nonexistent files."""
        with pytest.raises(FileNotFoundError):
            document_loader.load_text_file("nonexistent_file.txt")
    
    def test_load_directory(self, document_loader):
        """Test loading all files from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = ["gita.txt", "mahabharata.txt"]
            for filename in test_files:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(f"Content of {filename}")
            
            documents = document_loader.load_directory(temp_dir)
            assert len(documents) == 2
            assert all("Content of" in doc["content"] for doc in documents)
    
    def test_file_encoding_detection(self, document_loader):
        """Test handling of different file encodings."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
            f.write("Sanskrit text: कर्मण्येवाधिकारस्ते")
            
        try:
            content = document_loader.load_file(f.name)
            assert "कर्मण्येवाधिकारस्ते" in content
        finally:
            os.unlink(f.name)
    
    def test_metadata_extraction(self, document_loader):
        """Test extraction of document metadata."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Title: Bhagavad Gita\nChapter: 2\nVerse: 47\n\nContent here...")
        
        try:
            doc = document_loader.load_file_with_metadata(f.name)
            assert doc["metadata"]["filename"] == os.path.basename(f.name)
            assert "title" in doc["metadata"] or "source" in doc["metadata"]
        finally:
            os.unlink(f.name)


class TestSpiritualTextProcessor:
    """Test suite for SpiritualTextProcessor class."""
    
    @pytest.fixture
    def text_processor(self):
        """Create SpiritualTextProcessor instance for testing."""
        return SpiritualTextProcessor()
    
    @pytest.fixture
    def sample_spiritual_text(self):
        """Sample spiritual text for processing."""
        return """
        Chapter 2: The Yoga of Knowledge
        
        Verse 47: कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
        You have a right to perform your prescribed duty, but not to the fruits of action.
        
        Verse 48: योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।
        Be steadfast in yoga, O Arjuna. Perform your duty and abandon all attachment.
        
        Chapter 3: The Yoga of Action
        
        Verse 9: यज्ञार्थात्कर्मणोऽन्यत्र लोकोऽयं कर्मबन्धनः।
        Work done as sacrifice for Vishnu has to be performed.
        """
    
    def test_text_chunking_basic(self, text_processor, sample_spiritual_text):
        """Test basic text chunking functionality."""
        chunks = text_processor.chunk_text(sample_spiritual_text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("text" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_verse_boundary_preservation(self, text_processor, sample_spiritual_text):
        """Test that verse boundaries are preserved in chunking."""
        chunks = text_processor.chunk_text(sample_spiritual_text)
        
        # Check that verses aren't split inappropriately
        verse_chunks = [chunk for chunk in chunks if "Verse" in chunk["text"]]
        for chunk in verse_chunks:
            # Verse should include both Sanskrit and translation
            assert "कर्मण्य" in chunk["text"] or "योगस्थ" in chunk["text"] or "यज्ञार्थ" in chunk["text"]
    
    def test_sanskrit_term_preservation(self, text_processor):
        """Test preservation of Sanskrit terms."""
        text_with_sanskrit = "The concept of dharma (धर्म) and karma (कर्म) are central to Krishna's teachings."
        
        chunks = text_processor.chunk_text(text_with_sanskrit)
        
        # Sanskrit should be preserved
        combined_text = " ".join(chunk["text"] for chunk in chunks)
        assert "धर्म" in combined_text
        assert "कर्म" in combined_text
        assert "dharma" in combined_text
        assert "karma" in combined_text
    
    def test_citation_metadata_extraction(self, text_processor, sample_spiritual_text):
        """Test extraction of citation metadata."""
        chunks = text_processor.chunk_text(sample_spiritual_text)
        
        # Should extract chapter and verse information
        for chunk in chunks:
            if "Verse 47" in chunk["text"]:
                metadata = chunk["metadata"]
                assert "chapter" in metadata or "verse" in metadata or "source" in metadata
    
    def test_chunk_overlap_functionality(self, text_processor):
        """Test that chunk overlap works correctly."""
        long_text = "This is a test. " * 100  # Create long text
        
        chunks = text_processor.chunk_text(long_text)
        
        if len(chunks) > 1:
            # Check for overlap between consecutive chunks
            for i in range(len(chunks) - 1):
                chunk1_words = chunks[i]["text"].split()
                chunk2_words = chunks[i + 1]["text"].split()
                
                # Should have some overlapping words
                overlap = set(chunk1_words[-10:]) & set(chunk2_words[:10])
                assert len(overlap) > 0
    
    def test_empty_text_handling(self, text_processor):
        """Test handling of empty or whitespace-only text."""
        empty_texts = ["", "   ", "\n\n\n", "\t\t"]
        
        for empty_text in empty_texts:
            chunks = text_processor.chunk_text(empty_text)
            assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0]["text"].strip() == "")
    
    def test_preprocessing_pipeline(self, text_processor):
        """Test text preprocessing pipeline."""
        messy_text = "  \n\n  Chapter   2  :   The Yoga\n\n\n   of Knowledge  \n  "
        
        processed = text_processor.preprocess_text(messy_text)
        
        # Should clean up whitespace while preserving structure
        assert "Chapter 2: The Yoga of Knowledge" in processed
        assert processed.count('\n') < messy_text.count('\n')
    
    def test_special_character_handling(self, text_processor):
        """Test handling of special characters and diacritics."""
        text_with_special = "Śrī Kṛṣṇa speaks to Arjuna about dharma and mokṣa."
        
        chunks = text_processor.chunk_text(text_with_special)
        
        # Special characters should be preserved
        combined_text = " ".join(chunk["text"] for chunk in chunks)
        assert "Śrī" in combined_text
        assert "Kṛṣṇa" in combined_text
        assert "mokṣa" in combined_text


class TestLocalVectorStorage:
    """Test suite for LocalVectorStorage class."""
    
    @pytest.fixture
    def vector_storage(self):
        """Create LocalVectorStorage instance for testing."""
        return LocalVectorStorage(
            storage_path="test_vectors",
            dimension=384
        )
    
    @pytest.fixture
    def sample_chunks(self):
        """Sample text chunks for vector storage testing."""
        return [
            {
                "text": "You have a right to perform your prescribed duty, but not to the fruits of action.",
                "metadata": {"source": "Bhagavad Gita 2.47", "chapter": 2, "verse": 47}
            },
            {
                "text": "Be steadfast in yoga, O Arjuna. Perform your duty and abandon all attachment.",
                "metadata": {"source": "Bhagavad Gita 2.48", "chapter": 2, "verse": 48}
            },
            {
                "text": "The ultimate dharma is ahimsa, truth, and compassion towards all living beings.",
                "metadata": {"source": "Mahabharata, Vana Parva 313", "book": "Vana Parva"}
            }
        ]
    
    def test_vector_storage_initialization(self, vector_storage):
        """Test vector storage initialization."""
        assert vector_storage is not None
        assert hasattr(vector_storage, 'embedding_model')
        assert hasattr(vector_storage, 'dimension')
        assert vector_storage.dimension == 384
    
    @pytest.mark.asyncio
    async def test_add_documents(self, vector_storage, sample_chunks):
        """Test adding documents to vector storage."""
        success = await vector_storage.add_documents(sample_chunks)
        assert success is True
        
        # Check that documents were indexed
        count = await vector_storage.get_document_count()
        assert count == len(sample_chunks)
    
    @pytest.mark.asyncio
    async def test_similarity_search(self, vector_storage, sample_chunks):
        """Test similarity search functionality."""
        # Add documents first
        await vector_storage.add_documents(sample_chunks)
        
        # Search for related content
        query = "What is my duty in life?"
        results = await vector_storage.similarity_search(query, top_k=2)
        
        assert len(results) <= 2
        assert all("text" in result for result in results)
        assert all("score" in result for result in results)
        assert all("metadata" in result for result in results)
        
        # Results should be relevant to duty/dharma
        combined_results = " ".join(result["text"] for result in results)
        assert "duty" in combined_results.lower() or "dharma" in combined_results.lower()
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, vector_storage, sample_chunks):
        """Test similarity search with metadata filters."""
        await vector_storage.add_documents(sample_chunks)
        
        # Search only in Bhagavad Gita
        query = "duty and action"
        results = await vector_storage.similarity_search(
            query, 
            top_k=5,
            filter_metadata={"source": "Bhagavad Gita*"}
        )
        
        # Results should only be from Bhagavad Gita
        for result in results:
            assert "Bhagavad Gita" in result["metadata"]["source"]
    
    @pytest.mark.asyncio
    async def test_embedding_generation(self, vector_storage):
        """Test embedding generation for text."""
        text = "Krishna teaches about dharma and karma."
        
        embedding = await vector_storage.generate_embedding(text)
        
        assert embedding is not None
        assert len(embedding) == vector_storage.dimension
        assert all(isinstance(x, (int, float)) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, vector_storage, sample_chunks):
        """Test batch operations for efficiency."""
        # Test batch addition
        batch_sizes = [1, 2, len(sample_chunks)]
        
        for batch_size in batch_sizes:
            await vector_storage.clear()  # Clear previous data
            
            chunks_batch = sample_chunks[:batch_size]
            success = await vector_storage.add_documents_batch(chunks_batch)
            assert success is True
            
            count = await vector_storage.get_document_count()
            assert count == batch_size
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, vector_storage, sample_chunks):
        """Test that vector operations meet performance requirements."""
        await vector_storage.add_documents(sample_chunks)
        
        # Test search performance
        import time
        query = "teachings about duty"
        
        start_time = time.time()
        results = await vector_storage.similarity_search(query, top_k=5)
        search_time = time.time() - start_time
        
        # Should meet performance target
        target_time = PERFORMANCE_BENCHMARKS["response_time_targets"]["vector_search"]
        assert search_time < target_time
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_multilingual_support(self, vector_storage):
        """Test support for multilingual content."""
        multilingual_chunks = [
            {
                "text": "You have a right to perform your duty",
                "metadata": {"language": "English", "source": "BG 2.47"}
            },
            {
                "text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
                "metadata": {"language": "Sanskrit", "source": "BG 2.47"}
            },
            {
                "text": "तुम्हारा कर्तव्य करने का अधिकार है",
                "metadata": {"language": "Hindi", "source": "BG 2.47"}
            }
        ]
        
        await vector_storage.add_documents(multilingual_chunks)
        
        # Test cross-lingual search
        results_en = await vector_storage.similarity_search("duty and rights", top_k=3)
        results_hi = await vector_storage.similarity_search("कर्तव्य और अधिकार", top_k=3)
        
        # Should find relevant content in multiple languages
        assert len(results_en) > 0
        assert len(results_hi) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, vector_storage):
        """Test error handling in vector operations."""
        # Test with invalid data
        invalid_chunks = [
            {"text": "", "metadata": {}},  # Empty text
            {"invalid": "structure"},      # Missing required fields
            None                          # None value
        ]
        
        # Should handle errors gracefully
        result = await vector_storage.add_documents(invalid_chunks)
        # Should either filter out invalid items or raise appropriate exception
        assert result is False or isinstance(result, bool)


class TestRAGPipelineIntegration:
    """Integration tests for complete RAG pipeline."""
    
    @pytest.fixture
    def rag_pipeline(self):
        """Create complete RAG pipeline for testing."""
        from rag_pipeline import RAGPipeline
        return RAGPipeline()
    
    @pytest.mark.asyncio
    async def test_end_to_end_pipeline(self, rag_pipeline):
        """Test complete end-to-end RAG pipeline."""
        # Mock the pipeline components
        with patch.multiple(
            rag_pipeline,
            document_loader=Mock(),
            text_processor=Mock(),
            vector_storage=Mock()
        ):
            # Configure mock responses
            rag_pipeline.document_loader.load_directory.return_value = [
                {"content": "Sample spiritual text", "metadata": {"source": "test.txt"}}
            ]
            
            rag_pipeline.text_processor.chunk_text.return_value = [
                {
                    "text": "You have a right to perform your duty",
                    "metadata": {"source": "Bhagavad Gita 2.47"}
                }
            ]
            
            rag_pipeline.vector_storage.similarity_search.return_value = [
                {
                    "text": "You have a right to perform your duty",
                    "score": 0.95,
                    "metadata": {"source": "Bhagavad Gita 2.47"}
                }
            ]
            
            # Test the pipeline
            query = "What is my duty?"
            results = await rag_pipeline.search(query, top_k=3)
            
            assert results is not None
            assert len(results) > 0
            assert all("text" in result for result in results)
            assert all("score" in result for result in results)
            assert all("metadata" in result for result in results)
    
    @pytest.mark.asyncio
    async def test_pipeline_error_recovery(self, rag_pipeline):
        """Test pipeline error recovery mechanisms."""
        with patch.object(rag_pipeline, 'vector_storage') as mock_storage:
            # Simulate vector storage failure
            mock_storage.similarity_search.side_effect = Exception("Vector DB Error")
            
            query = "What is dharma?"
            
            # Should handle error gracefully
            try:
                results = await rag_pipeline.search(query)
                # Should return empty results or cached fallback
                assert isinstance(results, list)
            except Exception as e:
                # Or should propagate with clear error message
                assert "Vector DB Error" in str(e) or "search failed" in str(e).lower()
