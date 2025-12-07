#!/usr/bin/env python3
"""
Test Suite for Azure OpenAI Embedding Service Migration

Tests the migration from Gemini text-embedding-004 to Azure OpenAI text-embedding-3-large.
Validates 768-dimensional output, L2 normalization, and API compatibility.

Run with: pytest test_azure_embedding_migration.py -v
"""

import os
import sys
import math
import pytest
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the service
try:
    from services.azure_openai_embedding_service import (
        AzureOpenAIEmbeddingService,
        EmbeddingResult
    )
    AZURE_SERVICE_AVAILABLE = True
except ImportError:
    AZURE_SERVICE_AVAILABLE = False


class TestAzureOpenAIConfiguration:
    """Test Azure OpenAI embedding service configuration and initialization"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_service_initializes_with_text_embedding_3_large(self):
        """TEST_AZURE_001: AzureOpenAIEmbeddingService initializes with text-embedding-3-large"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        assert service.model_name == "text-embedding-3-large"
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_default_dimensionality_is_768(self):
        """TEST_AZURE_002: Default output dimensionality is 768 for Cosmos DB compatibility"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        assert service.output_dimensionality == 768
        assert service.dimension == 768
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_native_dimensionality_is_3072(self):
        """Verify native dimensionality is 3072 (truncated to 768)"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        assert service.native_dimensionality == 3072
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_azure_endpoint_configured(self):
        """TEST_AZURE_003: Azure OpenAI endpoint is properly configured"""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_EMBEDDING_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_EMBEDDING_API_KEY': 'test-key'
        }):
            service = AzureOpenAIEmbeddingService(test_mode=False)
            assert service.endpoint == 'https://test.openai.azure.com/'


class TestAzureEmbeddingGeneration:
    """Test Azure OpenAI embedding generation functionality"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_generate_embedding_returns_768_dimensions(self):
        """TEST_AZURE_004: Embedding generation returns 768-dimensional vectors"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        result = service.generate_embedding("Test text for embedding")
        
        assert isinstance(result, EmbeddingResult)
        assert len(result.embedding) == 768
        assert result.dimension == 768
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_embeddings_are_normalized(self):
        """TEST_AZURE_005: Embeddings are L2-normalized (Azure OpenAI automatic)"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        result = service.generate_embedding("Test normalization")
        
        # Check L2 norm is approximately 1.0
        magnitude = math.sqrt(sum(x * x for x in result.embedding))
        assert abs(magnitude - 1.0) < 0.01, f"Magnitude {magnitude} is not normalized"
        assert result.normalized == True
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_dimension_truncation_works(self):
        """TEST_AZURE_006: Dimension truncation from 3072 to 768 works correctly"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        
        # Mock full 3072-dim response
        mock_embedding = [0.1] * 3072
        with patch.object(service, '_call_azure_api', return_value=mock_embedding):
            result = service.generate_embedding("Test truncation")
            assert len(result.embedding) == 768
            assert result.dimension == 768


class TestBatchEmbeddingGeneration:
    """Test batch embedding generation"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    @pytest.mark.asyncio
    async def test_batch_embedding_processes_multiple_texts(self):
        """TEST_AZURE_007: Batch embedding generation processes multiple texts"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        texts = [
            "First text for embedding",
            "Second text for embedding",
            "Third text for embedding"
        ]
        
        results = await service.generate_embeddings_batch(texts)
        assert len(results) == 3
        assert all(len(r.embedding) == 768 for r in results)
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    @pytest.mark.asyncio
    async def test_batch_size_limit_respected(self):
        """Verify batch size limit (100 for Azure OpenAI) is respected"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        assert service.max_batch_size == 100


class TestErrorHandling:
    """Test error handling and retry logic"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_retry_logic_on_rate_limit(self):
        """TEST_AZURE_008: Retry logic works correctly on rate limit errors"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        
        # Mock rate limit error on first call, success on second
        with patch.object(service, '_call_azure_api') as mock_call:
            mock_call.side_effect = [
                Exception("Rate limit exceeded"),
                [0.1] * 768
            ]
            
            with patch('time.sleep'):  # Skip actual sleep
                result = service.generate_embedding("Test retry", max_retries=5)
                assert len(result.embedding) == 768
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_exponential_backoff_implemented(self):
        """Verify exponential backoff is implemented for retries"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        assert service.retry_base_delay == 1.0
        assert service.retry_multiplier == 2.0


class TestRAGIntegration:
    """Test integration with Enhanced RAG Service V6"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_rag_service_uses_azure_openai(self):
        """TEST_AZURE_009: Enhanced RAG Service V6 uses Azure OpenAI for embeddings"""
        try:
            from services.enhanced_rag_service_v6 import EnhancedRAGServiceV6
            
            with patch.dict(os.environ, {
                'AZURE_OPENAI_EMBEDDING_ENDPOINT': 'https://test.openai.azure.com/',
                'AZURE_OPENAI_EMBEDDING_API_KEY': 'test-key'
            }):
                service = EnhancedRAGServiceV6(test_mode=True)
                # Verify Azure OpenAI embedding service is used
                assert hasattr(service, 'embedding_service')
        except ImportError:
            pytest.skip("Enhanced RAG Service V6 not available")


class TestCostTracking:
    """Test cost tracking and monitoring"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_cost_calculation_correct(self):
        """TEST_AZURE_010: Cost tracking calculates expected $0.13/1M tokens"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        
        # Test with 1000 tokens
        tokens = 1000
        expected_cost = tokens * (0.13 / 1_000_000)
        calculated_cost = service.calculate_cost(tokens)
        
        assert abs(calculated_cost - expected_cost) < 0.0001


class TestVectorSearch:
    """Test vector search compatibility"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_embeddings_compatible_with_cosmos_db(self):
        """TEST_AZURE_011: Embeddings are compatible with Cosmos DB vector search"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        result = service.generate_embedding("Test Cosmos DB compatibility")
        
        # Verify format
        assert isinstance(result.embedding, list)
        assert all(isinstance(x, float) for x in result.embedding)
        assert len(result.embedding) == 768
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_similarity_search_quality(self):
        """TEST_AZURE_012: Vector similarity search maintains quality (MTEB 64.6)"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        
        # Generate embeddings for similar texts
        result1 = service.generate_embedding("The quick brown fox jumps")
        result2 = service.generate_embedding("A fast brown fox is jumping")
        result3 = service.generate_embedding("The weather is sunny today")
        
        # Calculate cosine similarity
        def cosine_similarity(v1, v2):
            dot_product = sum(a * b for a, b in zip(v1, v2))
            return dot_product  # Already normalized
        
        sim_12 = cosine_similarity(result1.embedding, result2.embedding)
        sim_13 = cosine_similarity(result1.embedding, result3.embedding)
        
        # Similar texts should have higher similarity than dissimilar
        assert sim_12 > sim_13


class TestMetadataTracking:
    """Test embedding metadata tracking"""
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_embedding_metadata_includes_model(self):
        """Verify embedding result includes model metadata"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        result = service.generate_embedding("Test metadata")
        
        assert result.model == "text-embedding-3-large"
        assert result.dimension == 768
        assert hasattr(result, 'timestamp')
    
    @pytest.mark.skipif(not AZURE_SERVICE_AVAILABLE, reason="Azure OpenAI service not available")
    def test_embedding_metadata_includes_provider(self):
        """Verify embedding result includes provider metadata"""
        service = AzureOpenAIEmbeddingService(test_mode=True)
        result = service.generate_embedding("Test provider")
        
        assert result.provider == "Azure OpenAI"


# Integration test markers
pytestmark = pytest.mark.integration


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
