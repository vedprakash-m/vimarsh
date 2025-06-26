"""
Cosmos DB Vector Search Implementation for Vimarsh
Task 8.7: Migrate local vector storage to Cosmos DB vector search

This module provides Cosmos DB vector search functionality replacing the local Faiss storage.
Supports efficient vector similarity search for spiritual text chunks with Azure Cosmos DB.
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import numpy as np
from pathlib import Path

# Azure Cosmos DB imports
try:
    from azure.cosmos import CosmosClient, exceptions, PartitionKey
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
    from azure.identity import DefaultAzureCredential
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    logging.warning("Azure Cosmos DB SDK not available - using mock implementation")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SpiritualTextChunk:
    """
    Represents a chunk of spiritual text with metadata for Cosmos DB storage.
    Includes vector embedding and spiritual context information.
    """
    id: str
    text: str
    source: str
    chapter: Optional[str] = None
    verse: Optional[str] = None
    sanskrit_terms: List[str] = None
    embedding: Optional[List[float]] = None
    
    # Spiritual metadata
    spiritual_theme: Optional[str] = None
    dharmic_context: Optional[str] = None
    character_speaker: Optional[str] = None
    
    # Technical metadata
    chunk_size: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.sanskrit_terms is None:
            self.sanskrit_terms = []
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.chunk_size is None and self.text:
            self.chunk_size = len(self.text)
    
    def to_cosmos_document(self) -> Dict[str, Any]:
        """Convert to Cosmos DB document format"""
        doc = asdict(self)
        # Ensure embedding is a list for Cosmos DB vector search
        if isinstance(self.embedding, np.ndarray):
            doc['embedding'] = self.embedding.tolist()
        return doc
    
    @classmethod
    def from_cosmos_document(cls, doc: Dict[str, Any]) -> 'SpiritualTextChunk':
        """Create instance from Cosmos DB document"""
        return cls(**doc)


class CosmosVectorSearch:
    """
    Cosmos DB Vector Search implementation for spiritual guidance.
    Provides efficient vector similarity search with spiritual context awareness.
    """
    
    def __init__(self, 
                 endpoint: str = None,
                 key: str = None,
                 database_name: str = "vimarsh",
                 container_name: str = "spiritual-texts",
                 embedding_dimension: int = 768):
        """
        Initialize Cosmos DB vector search client.
        
        Args:
            endpoint: Cosmos DB endpoint URL
            key: Cosmos DB access key
            database_name: Name of the Cosmos database
            container_name: Name of the container for spiritual texts
            embedding_dimension: Dimension of embedding vectors
        """
        self.endpoint = endpoint or os.getenv('COSMOS_DB_ENDPOINT')
        self.key = key or os.getenv('COSMOS_DB_KEY')
        self.database_name = database_name
        self.container_name = container_name
        self.embedding_dimension = embedding_dimension
        
        # Initialize clients
        self.client = None
        self.async_client = None
        self.database = None
        self.container = None
        
        # Connection state
        self.is_connected = False
        self.connection_error = None
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection to Cosmos DB"""
        try:
            if not COSMOS_AVAILABLE:
                logger.warning("Azure Cosmos DB SDK not available - using mock mode")
                return
            
            if not self.endpoint or not self.key:
                logger.warning("Cosmos DB credentials not provided - using mock mode")
                return
            
            # Initialize sync client
            self.client = CosmosClient(self.endpoint, self.key)
            
            # Get database and container references
            self.database = self.client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            
            # Test connection
            self._test_connection()
            
            self.is_connected = True
            logger.info(f"✅ Connected to Cosmos DB: {self.database_name}/{self.container_name}")
            
        except Exception as e:
            self.connection_error = str(e)
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            logger.info("🔄 Falling back to mock mode for development")
    
    def _test_connection(self):
        """Test Cosmos DB connection"""
        if not self.container:
            raise Exception("Container not initialized")
        
        # Try to read container properties
        self.container.read()
        logger.info("✅ Cosmos DB connection test successful")
    
    async def _get_async_client(self):
        """Get or create async Cosmos client"""
        if not self.async_client and COSMOS_AVAILABLE and self.endpoint and self.key:
            self.async_client = AsyncCosmosClient(self.endpoint, self.key)
        return self.async_client
    
    def add_chunk(self, chunk: SpiritualTextChunk) -> bool:
        """
        Add a spiritual text chunk to Cosmos DB.
        
        Args:
            chunk: SpiritualTextChunk with embedding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_connected:
                logger.warning(f"Not connected to Cosmos DB - storing chunk {chunk.id} in mock mode")
                return self._mock_add_chunk(chunk)
            
            if not chunk.embedding:
                raise ValueError("Chunk must have an embedding")
            
            # Convert to Cosmos document
            document = chunk.to_cosmos_document()
            
            # Add partition key (source)
            document['source'] = chunk.source
            
            # Insert into Cosmos DB
            self.container.create_item(body=document)
            
            logger.info(f"✅ Added chunk {chunk.id} from {chunk.source} to Cosmos DB")
            return True
            
        except exceptions.CosmosResourceExistsError:
            logger.warning(f"⚠️ Chunk {chunk.id} already exists in Cosmos DB")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to add chunk {chunk.id}: {e}")
            return False
    
    def add_chunks(self, chunks: List[SpiritualTextChunk]) -> int:
        """
        Add multiple chunks to Cosmos DB.
        
        Args:
            chunks: List of SpiritualTextChunk objects
            
        Returns:
            Number of chunks successfully added
        """
        successful = 0
        for chunk in chunks:
            if self.add_chunk(chunk):
                successful += 1
        
        logger.info(f"✅ Added {successful}/{len(chunks)} chunks to Cosmos DB")
        return successful
    
    def search(self, 
               query_embedding: Union[np.ndarray, List[float]], 
               k: int = 5,
               source_filter: Optional[str] = None,
               similarity_threshold: float = 0.7) -> List[Tuple[SpiritualTextChunk, float]]:
        """
        Search for similar spiritual text chunks using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            k: Number of results to return
            source_filter: Optional filter by source text
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            if not self.is_connected:
                return self._mock_search(query_embedding, k, source_filter)
            
            # Convert numpy array to list if needed
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Build vector search query
            query = self._build_vector_search_query(query_embedding, k, source_filter)
            
            # Execute query
            results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # Convert results to chunks with similarity scores
            chunks_with_scores = []
            for result in results:
                if 'similarity' in result and result['similarity'] >= similarity_threshold:
                    chunk = SpiritualTextChunk.from_cosmos_document(result)
                    chunks_with_scores.append((chunk, result['similarity']))
            
            logger.info(f"🔍 Found {len(chunks_with_scores)} similar chunks")
            return chunks_with_scores
            
        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            return []
    
    def _build_vector_search_query(self, 
                                   query_embedding: List[float], 
                                   k: int, 
                                   source_filter: Optional[str]) -> str:
        """Build Cosmos DB vector search query"""
        # Base vector search query using Cosmos DB vector search syntax
        base_query = f"""
        SELECT TOP {k} c.id, c.text, c.source, c.chapter, c.verse, c.sanskrit_terms,
               c.spiritual_theme, c.dharmic_context, c.character_speaker,
               c.chunk_size, c.created_at, c.updated_at,
               VectorDistance(c.embedding, {json.dumps(query_embedding)}) as similarity
        FROM c
        """
        
        # Add source filter if specified
        if source_filter:
            base_query += f" WHERE c.source = '{source_filter}'"
        
        # Order by similarity (descending for higher similarity first)
        base_query += " ORDER BY similarity DESC"
        
        return base_query
    
    def search_by_source(self, source: str, limit: int = 10) -> List[SpiritualTextChunk]:
        """
        Get chunks from a specific spiritual source.
        
        Args:
            source: Source text name (e.g., 'bhagavad_gita')
            limit: Maximum number of chunks
            
        Returns:
            List of text chunks from the source
        """
        try:
            if not self.is_connected:
                return self._mock_search_by_source(source, limit)
            
            query = f"""
            SELECT TOP {limit} * FROM c
            WHERE c.source = @source
            ORDER BY c.chapter, c.verse
            """
            
            results = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@source", "value": source}],
                partition_key=source
            ))
            
            chunks = [SpiritualTextChunk.from_cosmos_document(result) for result in results]
            logger.info(f"📚 Retrieved {len(chunks)} chunks from {source}")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Failed to search by source {source}: {e}")
            return []
    
    def get_chunk_by_id(self, chunk_id: str, source: str = None) -> Optional[SpiritualTextChunk]:
        """
        Retrieve a specific chunk by ID.
        
        Args:
            chunk_id: Unique chunk identifier
            source: Source partition key (optional)
            
        Returns:
            SpiritualTextChunk if found, None otherwise
        """
        try:
            if not self.is_connected:
                return self._mock_get_chunk_by_id(chunk_id)
            
            if source:
                # Direct read with partition key
                result = self.container.read_item(item=chunk_id, partition_key=source)
            else:
                # Cross-partition query
                query = "SELECT * FROM c WHERE c.id = @id"
                results = list(self.container.query_items(
                    query=query,
                    parameters=[{"name": "@id", "value": chunk_id}],
                    enable_cross_partition_query=True
                ))
                result = results[0] if results else None
            
            if result:
                return SpiritualTextChunk.from_cosmos_document(result)
            return None
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"⚠️ Chunk {chunk_id} not found")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get chunk {chunk_id}: {e}")
            return None
    
    def delete_chunk(self, chunk_id: str, source: str) -> bool:
        """
        Delete a chunk from Cosmos DB.
        
        Args:
            chunk_id: Chunk identifier
            source: Source partition key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_connected:
                logger.warning(f"Not connected - mock deleting chunk {chunk_id}")
                return True
            
            self.container.delete_item(item=chunk_id, partition_key=source)
            logger.info(f"🗑️ Deleted chunk {chunk_id} from {source}")
            return True
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"⚠️ Chunk {chunk_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete chunk {chunk_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dictionary with collection stats
        """
        try:
            if not self.is_connected:
                return self._mock_get_stats()
            
            # Count total documents
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count_result = list(self.container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))
            total_count = count_result[0] if count_result else 0
            
            # Count by source
            source_query = "SELECT c.source, COUNT(1) as count FROM c GROUP BY c.source"
            source_results = list(self.container.query_items(
                query=source_query,
                enable_cross_partition_query=True
            ))
            
            by_source = {result['source']: result['count'] for result in source_results}
            
            stats = {
                'total_chunks': total_count,
                'by_source': by_source,
                'database': self.database_name,
                'container': self.container_name,
                'embedding_dimension': self.embedding_dimension,
                'connected': self.is_connected
            }
            
            logger.info(f"📊 Collection stats: {total_count} total chunks")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {'error': str(e), 'connected': False}
    
    # Mock implementations for development/testing
    def _mock_add_chunk(self, chunk: SpiritualTextChunk) -> bool:
        """Mock implementation for adding chunks"""
        logger.info(f"🔧 Mock: Added chunk {chunk.id} from {chunk.source}")
        return True
    
    def _mock_search(self, query_embedding, k, source_filter) -> List[Tuple[SpiritualTextChunk, float]]:
        """Mock implementation for search"""
        logger.info(f"🔧 Mock: Searching for {k} similar chunks")
        return []
    
    def _mock_search_by_source(self, source: str, limit: int) -> List[SpiritualTextChunk]:
        """Mock implementation for source search"""
        logger.info(f"🔧 Mock: Searching {source} for {limit} chunks")
        return []
    
    def _mock_get_chunk_by_id(self, chunk_id: str) -> Optional[SpiritualTextChunk]:
        """Mock implementation for get by ID"""
        logger.info(f"🔧 Mock: Getting chunk {chunk_id}")
        return None
    
    def _mock_get_stats(self) -> Dict[str, Any]:
        """Mock implementation for stats"""
        return {
            'total_chunks': 0,
            'by_source': {},
            'database': self.database_name,
            'container': self.container_name,
            'embedding_dimension': self.embedding_dimension,
            'connected': False,
            'mode': 'mock'
        }
    
    def close(self):
        """Close Cosmos DB connections"""
        try:
            if self.async_client:
                # Note: async client close would need to be awaited
                pass
            logger.info("🔌 Cosmos DB connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")


# Global instance for easy access
_cosmos_vector_search = None

def get_vector_search(endpoint: str = None, 
                     key: str = None,
                     database_name: str = "vimarsh",
                     container_name: str = "spiritual-texts") -> CosmosVectorSearch:
    """
    Get or create global Cosmos DB vector search instance.
    
    Args:
        endpoint: Cosmos DB endpoint
        key: Cosmos DB key
        database_name: Database name
        container_name: Container name
        
    Returns:
        CosmosVectorSearch instance
    """
    global _cosmos_vector_search
    
    if _cosmos_vector_search is None:
        _cosmos_vector_search = CosmosVectorSearch(
            endpoint=endpoint,
            key=key,
            database_name=database_name,
            container_name=container_name
        )
    
    return _cosmos_vector_search


if __name__ == "__main__":
    # Simple test
    cosmos = get_vector_search()
    stats = cosmos.get_stats()
    print(f"Cosmos DB Vector Search initialized: {stats}")
