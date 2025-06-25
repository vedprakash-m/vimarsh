"""
Comprehensive tests for the local vector storage implementation.
Tests Faiss-based vector storage functionality for spiritual text chunks.
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from typing import List

from .vector_storage import (
    LocalVectorStorage, 
    TextChunk, 
    MockEmbeddingGenerator,
    create_sample_chunks
)

class TestTextChunk:
    """Test the TextChunk dataclass."""
    
    def test_text_chunk_creation(self):
        """Test creating a text chunk with all fields."""
        chunk = TextChunk(
            id="test_1",
            text="Test spiritual text",
            source="Test Scripture",
            chapter="1",
            verse="1",
            sanskrit_terms=["dharma", "karma"],
            embedding=np.array([0.1, 0.2, 0.3])
        )
        
        assert chunk.id == "test_1"
        assert chunk.text == "Test spiritual text"
        assert chunk.source == "Test Scripture"
        assert chunk.chapter == "1"
        assert chunk.verse == "1"
        assert chunk.sanskrit_terms == ["dharma", "karma"]
        assert np.array_equal(chunk.embedding, np.array([0.1, 0.2, 0.3]))
    
    def test_text_chunk_defaults(self):
        """Test text chunk with default values."""
        chunk = TextChunk(
            id="test_2",
            text="Test text",
            source="Test Source"
        )
        
        assert chunk.chapter is None
        assert chunk.verse is None
        assert chunk.sanskrit_terms == []
        assert chunk.embedding is None

class TestMockEmbeddingGenerator:
    """Test the mock embedding generator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = MockEmbeddingGenerator(dimension=384)
    
    def test_embedding_generation(self):
        """Test generating embeddings for text."""
        text = "Test spiritual text about dharma"
        embedding = self.generator.generate_embedding(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
        assert embedding.dtype == np.float32
        
        # Test that embedding is normalized (unit length)
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-6
    
    def test_embedding_consistency(self):
        """Test that same text produces same embedding."""
        text = "Consistent text"
        embedding1 = self.generator.generate_embedding(text)
        embedding2 = self.generator.generate_embedding(text)
        
        assert np.array_equal(embedding1, embedding2)
    
    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings."""
        text1 = "First text about karma"
        text2 = "Second text about dharma"
        
        embedding1 = self.generator.generate_embedding(text1)
        embedding2 = self.generator.generate_embedding(text2)
        
        assert not np.array_equal(embedding1, embedding2)
    
    def test_batch_embedding_generation(self):
        """Test generating embeddings for multiple texts."""
        texts = ["Text one", "Text two", "Text three"]
        embeddings = self.generator.generate_embeddings(texts)
        
        assert len(embeddings) == 3
        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (384,)

class TestLocalVectorStorage:
    """Test the local vector storage implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalVectorStorage(
            dimension=384, 
            storage_path=self.temp_dir
        )
        self.generator = MockEmbeddingGenerator(dimension=384)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_chunk(self, id_suffix: str, text: str, source: str = "Test Source") -> TextChunk:
        """Helper to create a test chunk with embedding."""
        embedding = self.generator.generate_embedding(text)
        return TextChunk(
            id=f"test_{id_suffix}",
            text=text,
            source=source,
            chapter="1",
            verse=id_suffix,
            sanskrit_terms=["test_term"],
            embedding=embedding
        )
    
    def test_storage_initialization(self):
        """Test vector storage initialization."""
        assert self.storage.dimension == 384
        assert self.storage.storage_path == Path(self.temp_dir)
        assert len(self.storage.chunks) == 0
        assert len(self.storage.id_to_index) == 0
    
    def test_add_single_chunk(self):
        """Test adding a single chunk to storage."""
        chunk = self.create_test_chunk("1", "Test spiritual text")
        
        self.storage.add_chunk(chunk)
        
        assert len(self.storage.chunks) == 1
        assert "test_1" in self.storage.id_to_index
        assert self.storage.id_to_index["test_1"] == 0
        assert self.storage.index.ntotal == 1
    
    def test_add_multiple_chunks(self):
        """Test adding multiple chunks to storage."""
        chunks = [
            self.create_test_chunk("1", "First text"),
            self.create_test_chunk("2", "Second text"),
            self.create_test_chunk("3", "Third text")
        ]
        
        self.storage.add_chunks(chunks)
        
        assert len(self.storage.chunks) == 3
        assert len(self.storage.id_to_index) == 3
        assert self.storage.index.ntotal == 3
    
    def test_add_duplicate_chunk(self):
        """Test adding a chunk with duplicate ID."""
        chunk1 = self.create_test_chunk("1", "First text")
        chunk2 = self.create_test_chunk("1", "Duplicate ID text")
        
        self.storage.add_chunk(chunk1)
        self.storage.add_chunk(chunk2)  # Should be skipped
        
        assert len(self.storage.chunks) == 1
        assert self.storage.chunks[0].text == "First text"
    
    def test_add_chunk_without_embedding(self):
        """Test adding a chunk without embedding raises error."""
        chunk = TextChunk(
            id="no_embedding",
            text="Text without embedding",
            source="Test Source"
        )
        
        with pytest.raises(ValueError, match="Chunk must have an embedding"):
            self.storage.add_chunk(chunk)
    
    def test_search_similar_chunks(self):
        """Test searching for similar chunks."""
        # Add test chunks
        chunks = [
            self.create_test_chunk("1", "Text about spiritual dharma"),
            self.create_test_chunk("2", "Story about karma and action"),
            self.create_test_chunk("3", "Philosophy of yoga and meditation")
        ]
        self.storage.add_chunks(chunks)
        
        # Search with similar query
        query_embedding = self.generator.generate_embedding("What is dharma?")
        results = self.storage.search(query_embedding, k=2)
        
        assert len(results) <= 2
        for chunk, score in results:
            assert isinstance(chunk, TextChunk)
            assert isinstance(score, float)
            assert 0 <= score <= 1  # Cosine similarity range
    
    def test_search_empty_storage(self):
        """Test searching in empty storage."""
        query_embedding = self.generator.generate_embedding("Test query")
        results = self.storage.search(query_embedding, k=5)
        
        assert results == []
    
    def test_search_with_source_filter(self):
        """Test searching with source filter."""
        chunks = [
            self.create_test_chunk("1", "Bhagavad Gita text", "Bhagavad Gita"),
            self.create_test_chunk("2", "Mahabharata text", "Mahabharata"),
            self.create_test_chunk("3", "Another Bhagavad Gita text", "Bhagavad Gita")
        ]
        self.storage.add_chunks(chunks)
        
        query_embedding = self.generator.generate_embedding("spiritual text")
        results = self.storage.search(query_embedding, k=5, source_filter="Bhagavad Gita")
        
        assert len(results) <= 2
        for chunk, score in results:
            assert chunk.source == "Bhagavad Gita"
    
    def test_search_by_source(self):
        """Test searching chunks by source."""
        chunks = [
            self.create_test_chunk("1", "Text 1", "Source A"),
            self.create_test_chunk("2", "Text 2", "Source B"),
            self.create_test_chunk("3", "Text 3", "Source A")
        ]
        self.storage.add_chunks(chunks)
        
        source_a_chunks = self.storage.search_by_source("Source A")
        
        assert len(source_a_chunks) == 2
        for chunk in source_a_chunks:
            assert chunk.source == "Source A"
    
    def test_search_by_sanskrit_term(self):
        """Test searching chunks by Sanskrit term."""
        chunks = [
            TextChunk("1", "Text with dharma", "Source", sanskrit_terms=["dharma", "karma"], 
                     embedding=self.generator.generate_embedding("text1")),
            TextChunk("2", "Text with yoga", "Source", sanskrit_terms=["yoga", "moksha"],
                     embedding=self.generator.generate_embedding("text2")),
            TextChunk("3", "Text with dharma again", "Source", sanskrit_terms=["dharma", "artha"],
                     embedding=self.generator.generate_embedding("text3"))
        ]
        self.storage.add_chunks(chunks)
        
        dharma_chunks = self.storage.search_by_sanskrit_term("dharma")
        
        assert len(dharma_chunks) == 2
        for chunk in dharma_chunks:
            assert "dharma" in chunk.sanskrit_terms
    
    def test_get_chunk_by_id(self):
        """Test retrieving chunk by ID."""
        chunk = self.create_test_chunk("123", "Test text")
        self.storage.add_chunk(chunk)
        
        retrieved = self.storage.get_chunk_by_id("test_123")
        assert retrieved is not None
        assert retrieved.id == "test_123"
        assert retrieved.text == "Test text"
        
        not_found = self.storage.get_chunk_by_id("nonexistent")
        assert not_found is None
    
    def test_get_stats(self):
        """Test getting storage statistics."""
        chunks = [
            self.create_test_chunk("1", "Text 1", "Source A"),
            self.create_test_chunk("2", "Text 2", "Source B"),
            self.create_test_chunk("3", "Text 3", "Source A")
        ]
        
        # Add Sanskrit terms
        chunks[0].sanskrit_terms = ["dharma", "karma"]
        chunks[1].sanskrit_terms = ["yoga"]
        chunks[2].sanskrit_terms = ["dharma", "moksha"]
        
        self.storage.add_chunks(chunks)
        stats = self.storage.get_stats()
        
        assert stats["total_chunks"] == 3
        assert stats["dimension"] == 384
        assert stats["sources"]["Source A"] == 2
        assert stats["sources"]["Source B"] == 1
        assert stats["unique_sanskrit_terms"] == 4  # dharma, karma, yoga, moksha
    
    def test_save_and_load(self):
        """Test saving and loading storage."""
        # Add some chunks
        chunks = create_sample_chunks()
        self.storage.add_chunks(chunks)
        
        # Save storage
        self.storage.save()
        
        # Create new storage and load
        new_storage = LocalVectorStorage(
            dimension=384,
            storage_path=self.temp_dir
        )
        new_storage.load()
        
        # Verify loaded data
        assert len(new_storage.chunks) == len(chunks)
        assert len(new_storage.id_to_index) == len(chunks)
        assert new_storage.index.ntotal == len(chunks)
        
        # Test that we can still search
        query_embedding = self.generator.generate_embedding("test query")
        results = new_storage.search(query_embedding, k=2)
        assert len(results) > 0
    
    def test_load_nonexistent_files(self):
        """Test loading when storage files don't exist."""
        empty_storage = LocalVectorStorage(
            dimension=384,
            storage_path=self.temp_dir + "_empty"
        )
        
        # Should not raise error
        empty_storage.load()
        assert len(empty_storage.chunks) == 0
    
    def test_clear_storage(self):
        """Test clearing all data from storage."""
        chunks = create_sample_chunks()
        self.storage.add_chunks(chunks)
        
        assert len(self.storage.chunks) > 0
        
        self.storage.clear()
        
        assert len(self.storage.chunks) == 0
        assert len(self.storage.id_to_index) == 0
        assert self.storage.index.ntotal == 0
    
    def test_delete_chunk(self):
        """Test deleting a chunk from storage."""
        chunks = [
            self.create_test_chunk("1", "Text 1"),
            self.create_test_chunk("2", "Text 2"),
            self.create_test_chunk("3", "Text 3")
        ]
        self.storage.add_chunks(chunks)
        
        # Delete middle chunk
        deleted = self.storage.delete_chunk("test_2")
        
        assert deleted is True
        assert len(self.storage.chunks) == 2
        assert "test_2" not in self.storage.id_to_index
        assert self.storage.index.ntotal == 2
        
        # Verify remaining chunks are accessible
        assert self.storage.get_chunk_by_id("test_1") is not None
        assert self.storage.get_chunk_by_id("test_3") is not None
    
    def test_delete_nonexistent_chunk(self):
        """Test deleting a non-existent chunk."""
        chunk = self.create_test_chunk("1", "Text 1")
        self.storage.add_chunk(chunk)
        
        deleted = self.storage.delete_chunk("nonexistent")
        
        assert deleted is False
        assert len(self.storage.chunks) == 1

class TestIntegration:
    """Integration tests for the complete vector storage workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = MockEmbeddingGenerator(dimension=384)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete workflow: create, add, search, save, load."""
        # Create storage
        storage = LocalVectorStorage(dimension=384, storage_path=self.temp_dir)
        
        # Create and add sample chunks
        sample_chunks = create_sample_chunks()
        storage.add_chunks(sample_chunks)
        
        # Test search
        query_embedding = self.generator.generate_embedding("What is duty and action?")
        results = storage.search(query_embedding, k=2)
        
        assert len(results) > 0
        
        # Save storage
        storage.save()
        
        # Create new storage instance and load
        new_storage = LocalVectorStorage(dimension=384, storage_path=self.temp_dir)
        
        # Verify auto-loading on initialization
        assert len(new_storage.chunks) == len(sample_chunks)
        
        # Test search in loaded storage
        new_results = new_storage.search(query_embedding, k=2)
        assert len(new_results) == len(results)
        
        # Verify similar results (embeddings should be identical)
        for (chunk1, score1), (chunk2, score2) in zip(results, new_results):
            assert chunk1.id == chunk2.id
            assert abs(score1 - score2) < 1e-6

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
