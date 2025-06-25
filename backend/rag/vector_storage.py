"""
Local vector storage implementation using Faiss for development and testing.
Provides efficient vector similarity search for spiritual text chunks.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import faiss
from dataclasses import dataclass
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """Represents a chunk of spiritual text with metadata."""
    id: str
    text: str
    source: str
    chapter: Optional[str] = None
    verse: Optional[str] = None
    sanskrit_terms: List[str] = None
    embedding: Optional[np.ndarray] = None
    
    def __post_init__(self):
        if self.sanskrit_terms is None:
            self.sanskrit_terms = []

class LocalVectorStorage:
    """
    Local vector storage using Faiss for development and testing.
    Supports adding, searching, and persisting vector embeddings with metadata.
    """
    
    def __init__(self, dimension: int = 384, storage_path: str = "data/vector_storage"):
        """
        Initialize local vector storage.
        
        Args:
            dimension: Dimension of the embedding vectors
            storage_path: Path to store the vector index and metadata
        """
        self.dimension = dimension
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Faiss index (using IndexFlatIP for cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Store metadata for each vector
        self.chunks: List[TextChunk] = []
        self.id_to_index: Dict[str, int] = {}
        
        # Load existing data if available
        self._load_if_exists()
    
    def add_chunk(self, chunk: TextChunk) -> None:
        """
        Add a text chunk with its embedding to the vector storage.
        
        Args:
            chunk: TextChunk object with embedding
        """
        if chunk.embedding is None:
            raise ValueError("Chunk must have an embedding")
        
        if chunk.id in self.id_to_index:
            logger.warning(f"Chunk with ID {chunk.id} already exists, skipping")
            return
        
        # Normalize embedding for cosine similarity
        embedding = chunk.embedding.copy()
        faiss.normalize_L2(embedding.reshape(1, -1))
        
        # Add to Faiss index
        self.index.add(embedding.reshape(1, -1))
        
        # Store metadata
        index = len(self.chunks)
        self.chunks.append(chunk)
        self.id_to_index[chunk.id] = index
        
        logger.info(f"Added chunk {chunk.id} from {chunk.source}")
    
    def add_chunks(self, chunks: List[TextChunk]) -> None:
        """
        Add multiple text chunks to the vector storage.
        
        Args:
            chunks: List of TextChunk objects with embeddings
        """
        for chunk in chunks:
            self.add_chunk(chunk)
    
    def search(self, query_embedding: np.ndarray, k: int = 5, 
               source_filter: Optional[str] = None) -> List[Tuple[TextChunk, float]]:
        """
        Search for similar text chunks using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            k: Number of results to return
            source_filter: Optional filter by source text
            
        Returns:
            List of (chunk, similarity_score) tuples, sorted by similarity
        """
        if len(self.chunks) == 0:
            return []
        
        # Normalize query embedding
        query = query_embedding.copy()
        faiss.normalize_L2(query.reshape(1, -1))
        
        # Search in Faiss index
        scores, indices = self.index.search(query.reshape(1, -1), min(k * 2, len(self.chunks)))
        
        # Filter and format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # Faiss returns -1 for invalid indices
                break
            
            chunk = self.chunks[idx]
            
            # Apply source filter if specified
            if source_filter and chunk.source != source_filter:
                continue
            
            results.append((chunk, float(score)))
            
            if len(results) >= k:
                break
        
        return results
    
    def search_by_source(self, source: str, limit: int = 10) -> List[TextChunk]:
        """
        Get all chunks from a specific source.
        
        Args:
            source: Source text name
            limit: Maximum number of chunks to return
            
        Returns:
            List of chunks from the specified source
        """
        return [chunk for chunk in self.chunks if chunk.source == source][:limit]
    
    def search_by_sanskrit_term(self, term: str, k: int = 5) -> List[TextChunk]:
        """
        Search for chunks containing a specific Sanskrit term.
        
        Args:
            term: Sanskrit term to search for
            k: Number of results to return
            
        Returns:
            List of chunks containing the Sanskrit term
        """
        results = []
        for chunk in self.chunks:
            if term.lower() in [t.lower() for t in chunk.sanskrit_terms]:
                results.append(chunk)
                if len(results) >= k:
                    break
        
        return results
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[TextChunk]:
        """
        Retrieve a specific chunk by its ID.
        
        Args:
            chunk_id: Unique identifier of the chunk
            
        Returns:
            TextChunk if found, None otherwise
        """
        if chunk_id in self.id_to_index:
            index = self.id_to_index[chunk_id]
            return self.chunks[index]
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector storage.
        
        Returns:
            Dictionary with storage statistics
        """
        sources = {}
        total_sanskrit_terms = set()
        
        for chunk in self.chunks:
            sources[chunk.source] = sources.get(chunk.source, 0) + 1
            total_sanskrit_terms.update(chunk.sanskrit_terms)
        
        return {
            "total_chunks": len(self.chunks),
            "dimension": self.dimension,
            "sources": sources,
            "unique_sanskrit_terms": len(total_sanskrit_terms),
            "storage_path": str(self.storage_path)
        }
    
    def save(self) -> None:
        """Save the vector index and metadata to disk."""
        try:
            # Save Faiss index
            index_path = self.storage_path / "faiss_index.bin"
            faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            metadata_path = self.storage_path / "metadata.pkl"
            metadata = {
                "chunks": self.chunks,
                "id_to_index": self.id_to_index,
                "dimension": self.dimension
            }
            
            with open(metadata_path, "wb") as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Saved vector storage to {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Error saving vector storage: {e}")
            raise
    
    def load(self) -> None:
        """Load the vector index and metadata from disk."""
        try:
            index_path = self.storage_path / "faiss_index.bin"
            metadata_path = self.storage_path / "metadata.pkl"
            
            if not index_path.exists() or not metadata_path.exists():
                logger.info("No existing vector storage found")
                return
            
            # Load Faiss index
            self.index = faiss.read_index(str(index_path))
            
            # Load metadata
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            
            self.chunks = metadata["chunks"]
            self.id_to_index = metadata["id_to_index"]
            self.dimension = metadata["dimension"]
            
            logger.info(f"Loaded vector storage with {len(self.chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error loading vector storage: {e}")
            raise
    
    def _load_if_exists(self) -> None:
        """Load existing data if storage files exist."""
        index_path = self.storage_path / "faiss_index.bin"
        metadata_path = self.storage_path / "metadata.pkl"
        
        if index_path.exists() and metadata_path.exists():
            self.load()
    
    def clear(self) -> None:
        """Clear all data from the vector storage."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []
        self.id_to_index = {}
        logger.info("Cleared vector storage")
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a chunk from the vector storage.
        Note: This requires rebuilding the entire index.
        
        Args:
            chunk_id: ID of the chunk to delete
            
        Returns:
            True if chunk was deleted, False if not found
        """
        if chunk_id not in self.id_to_index:
            return False
        
        # Remove from metadata
        index_to_remove = self.id_to_index[chunk_id]
        del self.id_to_index[chunk_id]
        self.chunks.pop(index_to_remove)
        
        # Rebuild ID mapping
        self.id_to_index = {chunk.id: i for i, chunk in enumerate(self.chunks)}
        
        # Rebuild Faiss index
        self.index = faiss.IndexFlatIP(self.dimension)
        if self.chunks:
            embeddings = np.array([chunk.embedding for chunk in self.chunks])
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
        
        logger.info(f"Deleted chunk {chunk_id} and rebuilt index")
        return True

class MockEmbeddingGenerator:
    """
    Mock embedding generator for testing purposes.
    In production, this would be replaced with actual embedding models.
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        np.random.seed(42)  # For reproducible embeddings
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate a mock embedding for text.
        Uses a simple hash-based approach for consistency.
        """
        # Simple hash-based embedding for testing
        text_hash = hash(text)
        np.random.seed(abs(text_hash) % (2**31))
        
        embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)
        
        # Normalize to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts."""
        return [self.generate_embedding(text) for text in texts]

# Example usage and testing functions
def create_sample_chunks() -> List[TextChunk]:
    """Create sample text chunks for testing."""
    generator = MockEmbeddingGenerator()
    
    sample_texts = [
        {
            "id": "bg_2_47",
            "text": "You have a right to perform your prescribed duty, but do not claim entitlement to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
            "source": "Bhagavad Gita",
            "chapter": "2",
            "verse": "47",
            "sanskrit_terms": ["karma", "dharma", "yoga"]
        },
        {
            "id": "bg_18_66", 
            "text": "Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
            "source": "Bhagavad Gita",
            "chapter": "18",
            "verse": "66",
            "sanskrit_terms": ["sarva-dharman", "sharanagati", "moksha"]
        },
        {
            "id": "mb_1_1",
            "text": "Once there was a king named Shantanu who ruled over the kingdom of Hastinapura with great wisdom and compassion.",
            "source": "Mahabharata",
            "chapter": "1",
            "verse": "1",
            "sanskrit_terms": ["raja", "Shantanu", "Hastinapura"]
        }
    ]
    
    chunks = []
    for data in sample_texts:
        embedding = generator.generate_embedding(data["text"])
        chunk = TextChunk(
            id=data["id"],
            text=data["text"],
            source=data["source"],
            chapter=data["chapter"],
            verse=data["verse"],
            sanskrit_terms=data["sanskrit_terms"],
            embedding=embedding
        )
        chunks.append(chunk)
    
    return chunks

def demo_vector_storage():
    """Demonstrate vector storage functionality."""
    print("=== Vector Storage Demo ===")
    
    # Create storage
    storage = LocalVectorStorage(dimension=384)
    
    # Add sample chunks
    chunks = create_sample_chunks()
    storage.add_chunks(chunks)
    
    # Show statistics
    stats = storage.get_stats()
    print(f"\nStorage Stats: {stats}")
    
    # Search by embedding
    generator = MockEmbeddingGenerator()
    query_text = "What is my duty and how should I perform it?"
    query_embedding = generator.generate_embedding(query_text)
    
    print(f"\nSearching for: '{query_text}'")
    results = storage.search(query_embedding, k=3)
    
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   Source: {chunk.source} {chunk.chapter}:{chunk.verse}")
        print(f"   Text: {chunk.text[:100]}...")
        print(f"   Sanskrit terms: {chunk.sanskrit_terms}")
    
    # Search by Sanskrit term
    print(f"\nSearching for Sanskrit term: 'karma'")
    karma_chunks = storage.search_by_sanskrit_term("karma")
    for chunk in karma_chunks:
        print(f"   {chunk.source} {chunk.chapter}:{chunk.verse} - {chunk.text[:50]}...")
    
    # Save storage
    storage.save()
    print(f"\nSaved storage to {storage.storage_path}")
    
    return storage

if __name__ == "__main__":
    demo_vector_storage()
