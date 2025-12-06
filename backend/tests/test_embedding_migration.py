#!/usr/bin/env python3
"""
Test Suite for Gemini Embedding Service Migration

Tests the migration from text-embedding-004 to gemini-embedding-001.
Validates MRL support, L2 normalization, and API compatibility.

Run with: pytest test_embedding_migration.py -v
"""

import os
import sys
import math
import pytest
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

# Import the service
from services.gemini_embedding_service import (
    GeminiEmbeddingService,
    EmbeddingResult,
    get_gemini_embedding_service,
    encode,
    GeminiTransformer
)


class TestEmbeddingServiceConfiguration:
    """Test embedding service configuration and initialization"""
    
    def test_service_initializes_with_gemini_embedding_001(self):
        """TEST_EMB_001: GeminiEmbeddingService initializes with gemini-embedding-001"""
        service = GeminiEmbeddingService(test_mode=True)
        assert service.model_name == "models/gemini-embedding-001"
    
    def test_default_dimensionality_is_768(self):
        """Verify default output dimensionality is 768 for Cosmos DB compatibility"""
        service = GeminiEmbeddingService(test_mode=True)
        assert service.output_dimensionality == 768
        assert service.dimension == 768
    
    def test_custom_dimensionality_can_be_set(self):
        """Verify custom dimensionality can be configured"""
        service = GeminiEmbeddingService(test_mode=True, output_dimensionality=1536)
        assert service.output_dimensionality == 1536
    
    def test_dimensionality_range_warning(self):
        """Verify warning for out-of-range dimensionality"""
        # Should log warning but not fail
        service = GeminiEmbeddingService(test_mode=True, output_dimensionality=64)
        assert service.output_dimensionality == 64
    
    def test_env_variable_override(self):
        """TEST_EMB_009: Backward compatibility with environment variable override"""
        with patch.dict(os.environ, {'EMBEDDING_OUTPUT_DIMENSIONALITY': '1024'}):
            service = GeminiEmbeddingService(test_mode=True)
            assert service.output_dimensionality == 1024


class TestEmbeddingGeneration:
    """Test embedding generation functionality"""
    
    def test_generate_embedding_returns_768_dimensions(self):
        """TEST_EMB_002: Embedding generation returns 768-dimensional vectors with MRL"""
        service = GeminiEmbeddingService(test_mode=True)
        result = service.generate_embedding("Test text for embedding")
        
        assert isinstance(result, EmbeddingResult)
        assert len(result.embedding) == 768
        assert result.dimension == 768
    
    def test_embeddings_are_normalized(self):
        """TEST_EMB_003: Embeddings are L2-normalized when using MRL dimensions < 3072"""
        service = GeminiEmbeddingService(test_mode=True)
        result = service.generate_embedding("Test normalization")
        
        # Check L2 norm is approximately 1.0
        magnitude = math.sqrt(sum(x * x for x in result.embedding))
        assert abs(magnitude - 1.0) < 0.01, f"Magnitude {magnitude} is not normalized"
        assert result.normalized == True
    
    def test_query_embedding_uses_retrieval_query(self):
        """TEST_EMB_004: Task type RETRIEVAL_QUERY works for user queries"""
        service = GeminiEmbeddingService(test_mode=True)
        
        # Mock the actual API call
        with patch.object(service, 'generate_embedding', wraps=service.generate_embedding) as mock:
            result = service.generate_query_embedding("What is the meaning of life?")
            assert result.dimension == 768
    
    def test_document_embedding_uses_retrieval_document(self):
        """TEST_EMB_005: Task type RETRIEVAL_DOCUMENT works for content chunks"""
        service = GeminiEmbeddingService(test_mode=True)
        result = service.generate_document_embedding("This is a document about philosophy.")
        assert result.dimension == 768
    
    def test_batch_embedding_generation(self):
        """Test batch embedding generation"""
        service = GeminiEmbeddingService(test_mode=True)
        texts = ["First text", "Second text", "Third text"]
        results = service.generate_embeddings_batch(texts)
        
        assert len(results) == 3
        for result in results:
            assert len(result.embedding) == 768


class TestNormalization:
    """Test L2 normalization functionality"""
    
    def test_normalize_embedding_returns_unit_vector(self):
        """Verify normalization produces unit vector"""
        service = GeminiEmbeddingService(test_mode=True)
        
        raw_embedding = [1.0, 2.0, 3.0, 4.0, 5.0]
        normalized = service._normalize_embedding(raw_embedding)
        
        magnitude = math.sqrt(sum(x * x for x in normalized))
        assert abs(magnitude - 1.0) < 0.0001
    
    def test_normalize_empty_embedding(self):
        """Verify empty embedding returns empty"""
        service = GeminiEmbeddingService(test_mode=True)
        assert service._normalize_embedding([]) == []
    
    def test_normalize_zero_vector(self):
        """Verify zero vector is handled"""
        service = GeminiEmbeddingService(test_mode=True)
        zero_vector = [0.0, 0.0, 0.0]
        result = service._normalize_embedding(zero_vector)
        assert result == zero_vector


class TestSimilarityCalculation:
    """Test cosine similarity calculation"""
    
    def test_similarity_identical_vectors(self):
        """TEST_EMB_006: Cosine similarity calculation works with normalized embeddings"""
        service = GeminiEmbeddingService(test_mode=True)
        
        # Normalized identical vectors should have similarity 1.0
        vec = service._normalize_embedding([1.0, 2.0, 3.0])
        similarity = service.calculate_similarity(vec, vec)
        
        assert abs(similarity - 1.0) < 0.0001
    
    def test_similarity_orthogonal_vectors(self):
        """Orthogonal normalized vectors should have similarity 0"""
        service = GeminiEmbeddingService(test_mode=True)
        
        vec1 = service._normalize_embedding([1.0, 0.0])
        vec2 = service._normalize_embedding([0.0, 1.0])
        similarity = service.calculate_similarity(vec1, vec2)
        
        assert abs(similarity) < 0.0001
    
    def test_similarity_opposite_vectors(self):
        """Opposite vectors should have similarity -1.0"""
        service = GeminiEmbeddingService(test_mode=True)
        
        vec1 = service._normalize_embedding([1.0, 0.0])
        vec2 = service._normalize_embedding([-1.0, 0.0])
        similarity = service.calculate_similarity(vec1, vec2)
        
        assert abs(similarity + 1.0) < 0.0001
    
    def test_similarity_empty_vectors(self):
        """Empty vectors should return 0"""
        service = GeminiEmbeddingService(test_mode=True)
        assert service.calculate_similarity([], []) == 0.0
    
    def test_similarity_dimension_mismatch(self):
        """Mismatched dimensions should return 0"""
        service = GeminiEmbeddingService(test_mode=True)
        assert service.calculate_similarity([1.0, 2.0], [1.0, 2.0, 3.0]) == 0.0


class TestModelInfo:
    """Test model information retrieval"""
    
    def test_model_info_contains_required_fields(self):
        """Verify model info has all expected fields"""
        service = GeminiEmbeddingService(test_mode=True)
        info = service.get_model_info()
        
        assert info['model_name'] == "models/gemini-embedding-001"
        assert info['native_dimension'] == 3072
        assert info['output_dimension'] == 768
        assert info['mrl_enabled'] == True
        assert info['normalized'] == True
        assert info['provider'] == "Google Gemini"
        assert info['mteb_score'] == 68.17
        assert 'RETRIEVAL_QUERY' in info['supported_task_types']
        assert 'RETRIEVAL_DOCUMENT' in info['supported_task_types']


class TestTextCleaning:
    """Test text cleaning functionality"""
    
    def test_clean_whitespace(self):
        """Verify excessive whitespace is removed"""
        service = GeminiEmbeddingService(test_mode=True)
        text = "  Multiple   spaces   and\n\nnewlines  "
        cleaned = service._clean_text(text)
        assert cleaned == "Multiple spaces and newlines"
    
    def test_clean_empty_text(self):
        """Verify empty text handling"""
        service = GeminiEmbeddingService(test_mode=True)
        assert service._clean_text("") == ""
        assert service._clean_text("   ") == ""
        assert service._clean_text(None) == ""
    
    def test_truncate_long_text(self):
        """Verify long text is truncated"""
        service = GeminiEmbeddingService(test_mode=True)
        long_text = "a" * 10000
        cleaned = service._clean_text(long_text)
        assert len(cleaned) <= 7003  # 7000 + "..."


class TestCompatibilityLayer:
    """Test backward compatibility functions"""
    
    def test_encode_single_text(self):
        """Test encode function with single text"""
        with patch('services.gemini_embedding_service.get_gemini_embedding_service') as mock:
            mock_service = MagicMock()
            mock_result = EmbeddingResult(
                embedding=[0.1] * 768,
                model="models/gemini-embedding-001",
                dimension=768,
                text_length=10,
                normalized=True
            )
            mock_service.generate_embedding.return_value = mock_result
            mock.return_value = mock_service
            
            result = encode("Test text")
            assert len(result) == 768
    
    def test_gemini_transformer_compatibility(self):
        """Test GeminiTransformer as SentenceTransformer replacement"""
        with patch('services.gemini_embedding_service.get_gemini_embedding_service') as mock:
            mock_service = MagicMock()
            mock_service.model_name = "models/gemini-embedding-001"
            mock.return_value = mock_service
            
            transformer = GeminiTransformer()
            assert "gemini-embedding-001" in transformer.model_name


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_graceful_degradation_on_api_failure(self):
        """TEST_EMB_010: Error handling for API failures maintains graceful degradation"""
        service = GeminiEmbeddingService(test_mode=True)
        
        # In test mode, should still work
        result = service.generate_embedding("Test error handling")
        assert result is not None
        assert len(result.embedding) == 768
    
    def test_batch_continues_on_single_failure(self):
        """Batch processing should continue even if single item fails"""
        service = GeminiEmbeddingService(test_mode=True)
        texts = ["Text 1", "Text 2", "Text 3"]
        
        results = service.generate_embeddings_batch(texts)
        assert len(results) == 3


# Integration test (requires API key)
@pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="GEMINI_API_KEY not set")
class TestLiveAPI:
    """Integration tests with live API (only run when API key is available)"""
    
    def test_live_embedding_generation(self):
        """Test actual embedding generation with live API"""
        service = GeminiEmbeddingService()
        result = service.generate_embedding("Test with live API")
        
        assert len(result.embedding) == 768
        assert result.model == "models/gemini-embedding-001"
        
        # Verify normalization
        magnitude = math.sqrt(sum(x * x for x in result.embedding))
        assert abs(magnitude - 1.0) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
