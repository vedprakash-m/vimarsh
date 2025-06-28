"""
Local Vector Storage for Development

Provides local vector storage using FAISS for development and testing
before migrating to Azure Cosmos DB in production.
"""

import logging
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import time
from datetime import datetime

try:
    import faiss
except ImportError:
    faiss = None
    logging.warning("FAISS not available. Install with: pip install faiss-cpu")

from .text_processor import TextChunk

# Import CosmosVectorSearch for production use
try:
    from ..rag.cosmos_vector_search import CosmosVectorSearch
except ImportError:
    # Fallback for development when cosmos module not available
    class CosmosVectorSearch:
        """Mock CosmosVectorSearch for development."""
        def __init__(self, *args, **kwargs):
            self.is_connected = False
        
        def similarity_search(self, *args, **kwargs):
            return []

logger = logging.getLogger(__name__)


@dataclass
class VectorMetadata:
    """Metadata for stored vectors"""
    chunk_id: str
    source_file: str
    content_preview: str  # First 100 chars
    vector_dimension: int
    storage_timestamp: str
    chunk_metadata: Dict[str, Any]


class LocalVectorStorage:
    """
    Local vector storage implementation using FAISS for development.
    This will be replaced with Azure Cosmos DB vector search in production.
    """
    
    def __init__(self, storage_path: str = "data/vectors", dimension: int = 384):
        """
        Initialize local vector storage
        
        Args:
            storage_path: Local directory to store vector data
            dimension: Vector dimension (default 384 for sentence-transformers)
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.dimension = dimension
        self.index = None
        self.metadata_store = {}
        
        # FAISS index configuration
        self.index_file = self.storage_path / "faiss_index.bin"
        self.metadata_file = self.storage_path / "metadata.json"
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        if faiss is None:
            logger.error("FAISS not available. Vector storage disabled.")
            return
        
        try:
            if self.index_file.exists() and self.metadata_file.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_file))
                
                # Load metadata
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata_data = json.load(f)
                    self.metadata_store = {
                        k: VectorMetadata(**v) for k, v in metadata_data.items()
                    }
                
                logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine similarity)
                logger.info(f"Created new FAISS index with dimension {self.dimension}")
                
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")
            # Create fresh index
            self.index = faiss.IndexFlatIP(self.dimension)
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        if faiss is None or self.index is None:
            return
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            metadata_data = {
                k: asdict(v) for k, v in self.metadata_store.items()
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_data, f, indent=2, ensure_ascii=False)
            
            logger.debug("Saved vector index and metadata")
            
        except Exception as e:
            logger.error(f"Failed to save vector index: {e}")
    
    def add_chunks(self, chunks: List[TextChunk], embeddings: np.ndarray):
        """
        Add text chunks with their embeddings to the vector store
        
        Args:
            chunks: List of TextChunk objects
            embeddings: Numpy array of embeddings (shape: [n_chunks, dimension])
        """
        if faiss is None or self.index is None:
            logger.error("Vector storage not available")
            return
        
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("Number of chunks must match number of embeddings")
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store metadata
        current_time = datetime.now().isoformat()
        for i, chunk in enumerate(chunks):
            metadata = VectorMetadata(
                chunk_id=chunk.chunk_id,
                source_file=chunk.source_file or "unknown",
                content_preview=chunk.content[:100].replace('\n', ' '),
                vector_dimension=self.dimension,
                storage_timestamp=current_time,
                chunk_metadata=chunk.metadata
            )
            self.metadata_store[chunk.chunk_id] = metadata
        
        # Save to disk
        self._save_index()
        
        logger.info(f"Added {len(chunks)} chunks to vector store. Total vectors: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, k: int = 10, 
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar chunks using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            k: Number of top results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of (chunk_id, similarity_score, metadata) tuples
        """
        if faiss is None or self.index is None:
            logger.error("Vector storage not available")
            return []
        
        if self.index.ntotal == 0:
            logger.warning("No vectors in index")
            return []
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query_embedding)
        
        # Search
        similarities, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
            
            # Find chunk_id for this index
            chunk_id = None
            for cid, metadata in self.metadata_store.items():
                # We need to track index positions better - for now use order
                if list(self.metadata_store.keys()).index(cid) == idx:
                    chunk_id = cid
                    break
            
            if chunk_id and chunk_id in self.metadata_store:
                metadata = self.metadata_store[chunk_id]
                
                # Apply filters if specified
                if filter_metadata:
                    match = True
                    for key, value in filter_metadata.items():
                        if key in metadata.chunk_metadata:
                            if metadata.chunk_metadata[key] != value:
                                match = False
                                break
                    if not match:
                        continue
                
                results.append((
                    chunk_id,
                    float(similarity),
                    asdict(metadata)
                ))
        
        return results
    
    def get_chunk_content(self, chunk_id: str) -> Optional[str]:
        """
        Get the full content of a chunk by ID
        Note: This is a limitation of the current design - we only store previews.
        In production, full content would be stored in Cosmos DB.
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            Chunk content if found, None otherwise
        """
        # For now, return the preview
        # In a real implementation, we'd store full content separately
        if chunk_id in self.metadata_store:
            return self.metadata_store[chunk_id].content_preview + "..."
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage statistics
        """
        if faiss is None or self.index is None:
            return {"error": "Vector storage not available"}
        
        # Analyze metadata
        source_files = {}
        text_types = {}
        total_chunks = len(self.metadata_store)
        
        for metadata in self.metadata_store.values():
            # Count by source file
            source_files[metadata.source_file] = source_files.get(metadata.source_file, 0) + 1
            
            # Count by text type
            text_type = metadata.chunk_metadata.get('chunk_type', 'unknown')
            text_types[text_type] = text_types.get(text_type, 0) + 1
        
        return {
            "total_vectors": self.index.ntotal,
            "total_chunks": total_chunks,
            "dimension": self.dimension,
            "source_files": source_files,
            "chunk_types": text_types,
            "storage_path": str(self.storage_path),
            "index_size_mb": self.index_file.stat().st_size / (1024*1024) if self.index_file.exists() else 0
        }
    
    def clear(self):
        """Clear all stored vectors and metadata"""
        if faiss is None:
            return
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata_store = {}
        
        # Remove files
        if self.index_file.exists():
            self.index_file.unlink()
        if self.metadata_file.exists():
            self.metadata_file.unlink()
        
        logger.info("Cleared vector storage")
    
    def export_for_production(self, output_path: str):
        """
        Export data in format suitable for Azure Cosmos DB migration
        
        Args:
            output_path: Path to save export data
        """
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_chunks": len(self.metadata_store),
                "dimension": self.dimension
            },
            "chunks": []
        }
        
        for chunk_id, metadata in self.metadata_store.items():
            export_data["chunks"].append({
                "chunk_id": chunk_id,
                "metadata": asdict(metadata)
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(self.metadata_store)} chunks to {output_path}")


class MockEmbeddingGenerator:
    """
    Mock embedding generator for testing when real embeddings are not available
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        np.random.seed(42)  # For reproducible results
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate mock embeddings for texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of mock embeddings
        """
        # Generate deterministic mock embeddings based on text hash
        embeddings = []
        for text in texts:
            # Use hash of text to generate reproducible random embedding
            text_hash = hash(text) % (2**31)
            np.random.seed(text_hash)
            embedding = np.random.randn(self.dimension)
            embeddings.append(embedding)
        
        return np.array(embeddings, dtype=np.float32)
