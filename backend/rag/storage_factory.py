"""
Vector Storage Factory for Vimarsh
Task 8.7: Migrate local vector storage to Cosmos DB vector search

Factory pattern implementation to manage vector storage backends,
supporting both local Faiss storage (development) and Cosmos DB (production).
"""

import os
import logging
from typing import Union, Optional
from abc import ABC, abstractmethod

from .vector_storage import LocalVectorStorage, TextChunk
from .cosmos_vector_search import CosmosVectorSearch, SpiritualTextChunk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStorageInterface(ABC):
    """Abstract interface for vector storage implementations."""
    
    @abstractmethod
    async def add_chunks(self, chunks):
        """Add text chunks to storage."""
        pass
    
    @abstractmethod
    async def search(self, query_embedding, top_k: int = 5, filters: dict = None):
        """Search for similar chunks."""
        pass
    
    @abstractmethod
    async def get_chunk(self, chunk_id: str):
        """Get specific chunk by ID."""
        pass
    
    @abstractmethod
    async def delete_chunk(self, chunk_id: str):
        """Delete specific chunk."""
        pass


class LocalStorageAdapter(VectorStorageInterface):
    """Adapter for local Faiss storage to match interface."""
    
    def __init__(self, storage_path: str = "data/vector_storage"):
        self.storage = LocalVectorStorage(storage_path=storage_path)
        # Load existing index if available
        try:
            self.storage.load()
        except Exception as e:
            logger.info(f"No existing storage to load: {e}")
    
    async def add_chunks(self, chunks):
        """Add text chunks to local storage."""
        if isinstance(chunks, list):
            for chunk in chunks:
                self.storage.add_chunk(chunk)
        else:
            self.storage.add_chunk(chunks)
        self.storage.save()
    
    async def search(self, query_embedding, top_k: int = 5, filters: dict = None):
        """Search for similar chunks in local storage."""
        return self.storage.search(query_embedding, k=top_k)
    
    async def get_chunk(self, chunk_id: str):
        """Get specific chunk by ID from local storage."""
        return self.storage.get_chunk_by_id(chunk_id)
    
    async def delete_chunk(self, chunk_id: str):
        """Delete specific chunk from local storage."""
        success = self.storage.delete_chunk(chunk_id)
        if success:
            self.storage.save()
        return success


class CosmosStorageAdapter(VectorStorageInterface):
    """Adapter for Cosmos DB storage to match interface."""
    
    def __init__(self, endpoint: str = None, key: str = None):
        self.storage = CosmosVectorSearch(endpoint=endpoint, key=key)
    
    async def add_chunks(self, chunks):
        """Add text chunks to Cosmos DB storage."""
        if isinstance(chunks, list):
            spiritual_chunks = []
            for chunk in chunks:
                if isinstance(chunk, TextChunk):
                    spiritual_chunk = self._convert_text_chunk_to_spiritual(chunk)
                    spiritual_chunks.append(spiritual_chunk)
                else:
                    spiritual_chunks.append(chunk)
            return await self.storage.add_chunks(spiritual_chunks)
        else:
            if isinstance(chunks, TextChunk):
                chunks = self._convert_text_chunk_to_spiritual(chunks)
            return await self.storage.add_chunk(chunks)
    
    async def search(self, query_embedding, top_k: int = 5, filters: dict = None):
        """Search for similar chunks in Cosmos DB."""
        results = await self.storage.vector_search(
            query_vector=query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        # Convert results back to compatible format
        return [(result['chunk'], result['similarity_score']) for result in results]
    
    async def get_chunk(self, chunk_id: str):
        """Get specific chunk by ID from Cosmos DB."""
        return await self.storage.get_chunk(chunk_id)
    
    async def delete_chunk(self, chunk_id: str):
        """Delete specific chunk from Cosmos DB."""
        return await self.storage.delete_chunk(chunk_id)
    
    def _convert_text_chunk_to_spiritual(self, text_chunk: TextChunk) -> SpiritualTextChunk:
        """Convert TextChunk to SpiritualTextChunk for Cosmos DB."""
        return SpiritualTextChunk(
            id=text_chunk.id,
            text=text_chunk.text,
            source=text_chunk.source,
            chapter=text_chunk.chapter,
            verse=text_chunk.verse,
            sanskrit_terms=text_chunk.sanskrit_terms or [],
            embedding=text_chunk.embedding.tolist() if hasattr(text_chunk.embedding, 'tolist') else text_chunk.embedding
        )


class VectorStorageFactory:
    """
    Factory for creating vector storage instances based on configuration.
    Supports seamless switching between local and Cosmos DB storage.
    """
    
    @staticmethod
    def create_storage(
        storage_type: str = None,
        cosmos_endpoint: str = None,
        cosmos_key: str = None,
        local_storage_path: str = "data/vector_storage"
    ) -> VectorStorageInterface:
        """
        Create vector storage instance based on configuration.
        
        Args:
            storage_type: 'local' or 'cosmos' (if None, auto-detect from environment)
            cosmos_endpoint: Cosmos DB endpoint URL
            cosmos_key: Cosmos DB access key
            local_storage_path: Path for local storage
            
        Returns:
            Vector storage instance implementing VectorStorageInterface
        """
        # Auto-detect storage type if not specified
        if storage_type is None:
            storage_type = VectorStorageFactory._detect_storage_type(cosmos_endpoint, cosmos_key)
        
        if storage_type.lower() == 'cosmos':
            logger.info("Creating Cosmos DB vector storage")
            # Use environment variables if explicit values not provided
            endpoint = cosmos_endpoint or os.getenv('COSMOS_DB_ENDPOINT')
            key = cosmos_key or os.getenv('COSMOS_DB_KEY')
            return CosmosStorageAdapter(endpoint=endpoint, key=key)
        else:
            logger.info("Creating local vector storage")
            return LocalStorageAdapter(storage_path=local_storage_path)
    
    @staticmethod
    def _detect_storage_type(cosmos_endpoint: str = None, cosmos_key: str = None) -> str:
        """Auto-detect storage type based on environment and configuration."""
        
        # Check environment variables first
        env_endpoint = os.getenv('COSMOS_DB_ENDPOINT')
        env_key = os.getenv('COSMOS_DB_KEY')
        
        # Use provided values or fall back to environment
        effective_endpoint = cosmos_endpoint or env_endpoint
        effective_key = cosmos_key or env_key
        
        # Check Azure Functions environment
        is_azure_functions = os.getenv('AZURE_FUNCTIONS_ENVIRONMENT') is not None
        
        # Use Cosmos DB if:
        # 1. Credentials are available AND
        # 2. We're in Azure Functions environment OR explicitly configured
        if effective_endpoint and effective_key:
            if is_azure_functions:
                logger.info("Detected Azure Functions environment with Cosmos DB credentials - using Cosmos DB")
                return 'cosmos'
            else:
                logger.info("Cosmos DB credentials available but not in Azure Functions - using local storage for development")
                return 'local'
        else:
            logger.info("No Cosmos DB credentials available - using local storage")
            return 'local'
    
    @staticmethod
    def create_development_storage() -> VectorStorageInterface:
        """Create storage instance optimized for development."""
        return VectorStorageFactory.create_storage(storage_type='local')
    
    @staticmethod
    def create_production_storage(
        cosmos_endpoint: str = None,
        cosmos_key: str = None
    ) -> VectorStorageInterface:
        """Create storage instance optimized for production."""
        return VectorStorageFactory.create_storage(
            storage_type='cosmos',
            cosmos_endpoint=cosmos_endpoint,
            cosmos_key=cosmos_key
        )


# Global storage instance (lazy initialization)
_global_storage_instance = None

def get_vector_storage(
    storage_type: str = None,
    cosmos_endpoint: str = None,
    cosmos_key: str = None,
    force_recreate: bool = False
) -> VectorStorageInterface:
    """
    Get global vector storage instance with lazy initialization.
    
    Args:
        storage_type: 'local' or 'cosmos' (if None, auto-detect)
        cosmos_endpoint: Cosmos DB endpoint URL
        cosmos_key: Cosmos DB access key
        force_recreate: Force recreation of global instance
        
    Returns:
        Global vector storage instance
    """
    global _global_storage_instance
    
    if _global_storage_instance is None or force_recreate:
        _global_storage_instance = VectorStorageFactory.create_storage(
            storage_type=storage_type,
            cosmos_endpoint=cosmos_endpoint,
            cosmos_key=cosmos_key
        )
        logger.info(f"Initialized global vector storage: {type(_global_storage_instance).__name__}")
    
    return _global_storage_instance
