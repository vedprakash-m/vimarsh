"""
Vector Storage Migration Tests
Task 8.7: Migrate local vector storage to Cosmos DB vector search

Comprehensive tests for vector storage migration, factory pattern,
and enhanced spiritual guidance service integration.
"""

import pytest
import asyncio
import numpy as np
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import logging

from backend.rag import (
    VectorStorageFactory,
    VectorStorageInterface,
    LocalStorageAdapter,
    CosmosStorageAdapter,
    get_vector_storage,
    TextChunk,
    SpiritualTextChunk
)
from backend.spiritual_guidance.enhanced_service import (
    SpiritualGuidanceService,
    create_development_service,
    create_production_service
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestVectorStorageFactory:
    """Test vector storage factory functionality."""
    
    def test_create_local_storage(self):
        """Test creating local storage instance."""
        storage = VectorStorageFactory.create_storage(storage_type='local')
        assert isinstance(storage, LocalStorageAdapter)
    
    @patch('backend.rag.storage_factory.CosmosStorageAdapter')
    def test_create_cosmos_storage(self, mock_cosmos):
        """Test creating Cosmos DB storage instance."""
        mock_cosmos.return_value = Mock(spec=VectorStorageInterface)
        
        storage = VectorStorageFactory.create_storage(
            storage_type='cosmos',
            cosmos_endpoint='https://test.documents.azure.com:443/',
            cosmos_key='test-key'
        )
        
        mock_cosmos.assert_called_once_with(
            endpoint='https://test.documents.azure.com:443/',
            key='test-key'
        )
    
    @patch.dict('os.environ', {
        'COSMOS_DB_ENDPOINT': 'https://env.documents.azure.com:443/',
        'COSMOS_DB_KEY': 'env-key',
        'AZURE_FUNCTIONS_ENVIRONMENT': 'true'
    })
    @patch('backend.rag.storage_factory.CosmosStorageAdapter')
    def test_auto_detect_cosmos_in_azure_functions(self, mock_cosmos):
        """Test auto-detection of Cosmos DB in Azure Functions environment."""
        mock_cosmos.return_value = Mock(spec=VectorStorageInterface)
        
        storage = VectorStorageFactory.create_storage()
        
        mock_cosmos.assert_called_once_with(
            endpoint='https://env.documents.azure.com:443/',
            key='env-key'
        )
    
    @patch.dict('os.environ', {
        'COSMOS_DB_ENDPOINT': 'https://env.documents.azure.com:443/',
        'COSMOS_DB_KEY': 'env-key'
    }, clear=True)
    def test_auto_detect_local_in_development(self):
        """Test auto-detection of local storage in development environment."""
        storage = VectorStorageFactory.create_storage()
        assert isinstance(storage, LocalStorageAdapter)


class TestLocalStorageAdapter:
    """Test local storage adapter functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalStorageAdapter(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_add_and_search_chunk(self):
        """Test adding and searching chunks in local storage."""
        # Create test chunk
        chunk = TextChunk(
            id="test-chunk-1",
            text="Test spiritual text content",
            source="Test Source",
            embedding=np.random.rand(384).astype(np.float32)  # Use 384 dimensions for LocalVectorStorage
        )
        
        # Add chunk
        await self.storage.add_chunks(chunk)
        
        # Search for similar chunks
        query_embedding = np.random.rand(384).astype(np.float32)  # Use 384 dimensions
        results = await self.storage.search(query_embedding, top_k=1)
        
        assert len(results) == 1
        found_chunk, score = results[0]
        assert found_chunk.id == "test-chunk-1"
        assert found_chunk.text == "Test spiritual text content"
    
    @pytest.mark.asyncio
    async def test_add_multiple_chunks(self):
        """Test adding multiple chunks at once."""
        chunks = [
            TextChunk(
                id=f"chunk-{i}",
                text=f"Spiritual text {i}",
                source="Test Source",
                embedding=np.random.rand(384).astype(np.float32)  # Use 384 dimensions
            )
            for i in range(3)
        ]
        
        await self.storage.add_chunks(chunks)
        
        # Search and verify all chunks are stored
        query_embedding = np.random.rand(384).astype(np.float32)  # Use 384 dimensions
        results = await self.storage.search(query_embedding, top_k=5)
        
        assert len(results) == 3
        chunk_ids = {chunk.id for chunk, _ in results}
        assert chunk_ids == {"chunk-0", "chunk-1", "chunk-2"}
    
    @pytest.mark.asyncio
    async def test_get_chunk_by_id(self):
        """Test retrieving specific chunk by ID."""
        chunk = TextChunk(
            id="specific-chunk",
            text="Specific spiritual content",
            source="Bhagavad Gita",
            chapter="2",
            verse="47",
            embedding=np.random.rand(384).astype(np.float32)  # Use 384 dimensions
        )
        
        await self.storage.add_chunks(chunk)
        
        # Retrieve chunk by ID
        retrieved = await self.storage.get_chunk("specific-chunk")
        
        assert retrieved is not None
        assert retrieved.id == "specific-chunk"
        assert retrieved.text == "Specific spiritual content"
        assert retrieved.chapter == "2"
        assert retrieved.verse == "47"
    
    @pytest.mark.asyncio
    async def test_delete_chunk(self):
        """Test deleting chunk from storage."""
        chunk = TextChunk(
            id="delete-me",
            text="Temporary content",
            source="Test",
            embedding=np.random.rand(384).astype(np.float32)  # Use 384 dimensions
        )
        
        await self.storage.add_chunks(chunk)
        
        # Verify chunk exists
        retrieved = await self.storage.get_chunk("delete-me")
        assert retrieved is not None
        
        # Delete chunk
        success = await self.storage.delete_chunk("delete-me")
        assert success
        
        # Verify chunk is deleted
        retrieved = await self.storage.get_chunk("delete-me")
        assert retrieved is None


class TestCosmosStorageAdapter:
    """Test Cosmos DB storage adapter functionality."""
    
    def setup_method(self):
        """Set up test environment with mocked Cosmos DB."""
        self.mock_cosmos = Mock()
        self.mock_cosmos.add_chunk = AsyncMock(return_value=True)
        self.mock_cosmos.add_chunks = AsyncMock(return_value=[True, True])
        self.mock_cosmos.vector_search = AsyncMock(return_value=[
            {
                'chunk': SpiritualTextChunk(
                    id='test-1',
                    text='Test content',
                    source='Test Source',
                    embedding=[0.1] * 768
                ),
                'similarity_score': 0.85
            }
        ])
        self.mock_cosmos.get_chunk = AsyncMock(return_value=SpiritualTextChunk(
            id='test-1',
            text='Test content',
            source='Test Source'
        ))
        self.mock_cosmos.delete_chunk = AsyncMock(return_value=True)
        
        # Create adapter with mocked Cosmos DB
        self.adapter = CosmosStorageAdapter()
        self.adapter.storage = self.mock_cosmos
    
    @pytest.mark.asyncio
    async def test_add_single_chunk(self):
        """Test adding single chunk to Cosmos DB."""
        chunk = TextChunk(
            id="cosmos-test-1",
            text="Cosmos test content",
            source="Test Source",
            embedding=np.random.rand(768).astype(np.float32)
        )
        
        result = await self.adapter.add_chunks(chunk)
        
        self.mock_cosmos.add_chunk.assert_called_once()
        # Verify the chunk was converted to SpiritualTextChunk
        args, kwargs = self.mock_cosmos.add_chunk.call_args
        spiritual_chunk = args[0]
        assert isinstance(spiritual_chunk, SpiritualTextChunk)
        assert spiritual_chunk.id == "cosmos-test-1"
        assert spiritual_chunk.text == "Cosmos test content"
    
    @pytest.mark.asyncio
    async def test_search_chunks(self):
        """Test searching chunks in Cosmos DB."""
        query_embedding = np.random.rand(768).astype(np.float32)
        
        results = await self.adapter.search(query_embedding, top_k=5)
        
        self.mock_cosmos.vector_search.assert_called_once_with(
            query_vector=query_embedding.tolist(),
            top_k=5,
            filters=None
        )
        
        assert len(results) == 1
        chunk, score = results[0]
        assert isinstance(chunk, SpiritualTextChunk)
        assert score == 0.85
    
    @pytest.mark.asyncio
    async def test_get_chunk_by_id(self):
        """Test retrieving chunk by ID from Cosmos DB."""
        result = await self.adapter.get_chunk("test-1")
        
        self.mock_cosmos.get_chunk.assert_called_once_with("test-1")
        assert isinstance(result, SpiritualTextChunk)
        assert result.id == "test-1"
    
    @pytest.mark.asyncio
    async def test_delete_chunk(self):
        """Test deleting chunk from Cosmos DB."""
        result = await self.adapter.delete_chunk("test-1")
        
        self.mock_cosmos.delete_chunk.assert_called_once_with("test-1")
        assert result is True


class TestSpiritualGuidanceService:
    """Test enhanced spiritual guidance service."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock Gemini client
        self.mock_gemini = Mock()
        self.mock_gemini.generate_spiritual_guidance = AsyncMock(
            return_value="Test spiritual guidance response"
        )
        
        # Create service with local storage
        self.service = SpiritualGuidanceService(
            gemini_client=self.mock_gemini,
            storage_type='local'
        )
        
        # Replace vector storage with test instance
        self.service.vector_storage = LocalStorageAdapter(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_process_query_complete_flow(self):
        """Test complete query processing flow."""
        # Add test data to storage
        test_chunk = TextChunk(
            id="gita-2-47",
            text="You have a right to perform your prescribed duty, but not to the fruits of action.",
            source="Bhagavad Gita",
            chapter="2",
            verse="47",
            sanskrit_terms=["karma", "dharma"],
            embedding=np.random.rand(384).astype(np.float32)  # Use 384 dimensions
        )
        
        await self.service.vector_storage.add_chunks(test_chunk)
        
        # Process query
        response = await self.service.process_query(
            query="What is my duty in life?",
            language="English",
            include_citations=True
        )
        
        # Verify response structure
        assert "response" in response
        assert "citations" in response
        assert "metadata" in response
        
        # Verify citations
        assert len(response["citations"]) > 0
        citation = response["citations"][0]
        assert citation["source"] == "Bhagavad Gita"
        assert citation["chapter"] == "2"
        assert citation["verse"] == "47"
        
        # Verify metadata
        metadata = response["metadata"]
        assert "processing_time_ms" in metadata
        assert "retrieved_chunks" in metadata
        assert "storage_backend" in metadata
        assert metadata["language"] == "English"
    
    @pytest.mark.asyncio
    async def test_add_spiritual_texts(self):
        """Test adding spiritual texts to storage."""
        text_sources = [
            {
                "source": "Bhagavad Gita Chapter 1",
                "content": (
                    "Dhritarashtra said: O Sanjaya, after my sons and the sons of Pandu "
                    "assembled in the place of pilgrimage at Kurukshetra, desiring to fight, "
                    "what did they do? (1.1)"
                ),
                "metadata": {"chapter": "1", "verses": "1"}
            }
        ]
        
        result = await self.service.add_spiritual_texts(text_sources)
        
        assert result["success"] is True
        assert result["total_chunks_added"] > 0
        assert result["sources_processed"] == 1
        assert len(result["processing_details"]) == 1
    
    @pytest.mark.asyncio
    async def test_search_spiritual_knowledge(self):
        """Test direct knowledge search."""
        # Add test chunk
        test_chunk = TextChunk(
            id="test-search",
            text="The soul is neither born, and nor does it die.",
            source="Bhagavad Gita",
            chapter="2",
            verse="20",
            embedding=np.random.rand(384).astype(np.float32)  # Use 384 dimensions
        )
        
        await self.service.vector_storage.add_chunks(test_chunk)
        
        # Search knowledge
        results = await self.service.search_spiritual_knowledge(
            query="What is the nature of the soul?",
            top_k=5
        )
        
        assert len(results) > 0
        result = results[0]
        assert "similarity_score" in result
        assert result["text"] == "The soul is neither born, and nor does it die."
        assert result["source"] == "Bhagavad Gita"
    
    @pytest.mark.asyncio
    async def test_fallback_response_english(self):
        """Test fallback response generation in English."""
        # Create service without Gemini client
        service = SpiritualGuidanceService(storage_type='local')
        service.vector_storage = LocalStorageAdapter(storage_path=self.temp_dir)
        
        response = await service.process_query(
            query="Test query",
            language="English"
        )
        
        assert "Dear devotee" in response["response"]
        assert response["metadata"]["language"] == "English"
    
    @pytest.mark.asyncio
    async def test_fallback_response_hindi(self):
        """Test fallback response generation in Hindi."""
        # Create service without Gemini client
        service = SpiritualGuidanceService(storage_type='local')
        service.vector_storage = LocalStorageAdapter(storage_path=self.temp_dir)
        
        response = await service.process_query(
            query="Test query",
            language="Hindi"
        )
        
        assert "प्रिय भक्त" in response["response"]
        assert response["metadata"]["language"] == "Hindi"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in service."""
        # Create service with broken storage
        service = SpiritualGuidanceService(storage_type='local')
        service.vector_storage = Mock()
        service.vector_storage.search = AsyncMock(side_effect=Exception("Storage error"))
        
        response = await service.process_query("Test query")
        
        assert response["metadata"]["success"] is False
        assert "error" in response["metadata"]
        assert "difficulty" in response["response"]


class TestFactoryFunctions:
    """Test factory functions for service creation."""
    
    def test_create_development_service(self):
        """Test development service creation."""
        service = create_development_service()
        
        assert isinstance(service, SpiritualGuidanceService)
        assert isinstance(service.vector_storage, LocalStorageAdapter)
    
    @patch('backend.spiritual_guidance.enhanced_service.get_vector_storage')
    def test_create_production_service(self, mock_get_storage):
        """Test production service creation."""
        mock_storage = Mock(spec=VectorStorageInterface)
        mock_get_storage.return_value = mock_storage
        
        service = create_production_service(
            cosmos_endpoint='https://test.documents.azure.com:443/',
            cosmos_key='test-key'
        )
        
        assert isinstance(service, SpiritualGuidanceService)
        mock_get_storage.assert_called_once_with(
            storage_type='cosmos',
            cosmos_endpoint='https://test.documents.azure.com:443/',
            cosmos_key='test-key'
        )


class TestGlobalStorageInstance:
    """Test global storage instance management."""
    
    def teardown_method(self):
        """Reset global instance."""
        import backend.rag.storage_factory
        backend.rag.storage_factory._global_storage_instance = None
    
    def test_global_instance_lazy_initialization(self):
        """Test lazy initialization of global storage instance."""
        storage1 = get_vector_storage(storage_type='local')
        storage2 = get_vector_storage(storage_type='local')
        
        assert storage1 is storage2  # Same instance
        assert isinstance(storage1, LocalStorageAdapter)
    
    def test_global_instance_force_recreate(self):
        """Test forcing recreation of global storage instance."""
        storage1 = get_vector_storage(storage_type='local')
        storage2 = get_vector_storage(storage_type='local', force_recreate=True)
        
        assert storage1 is not storage2  # Different instances
        assert isinstance(storage2, LocalStorageAdapter)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
