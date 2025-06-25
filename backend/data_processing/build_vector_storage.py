"""
Vector Storage Builder for Spiritual Text Chunks

This script builds the local vector storage by processing the chunked spiritual texts
and generating embeddings using sentence transformers.
"""

import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
import numpy as np

# Import our modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from rag.vector_storage import LocalVectorStorage, TextChunk
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStorageBuilder:
    """
    Builds vector storage from processed spiritual text chunks.
    """
    
    def __init__(self, processed_data_dir: str, vector_storage_path: str):
        """
        Initialize the vector storage builder.
        
        Args:
            processed_data_dir: Directory containing processed text chunks
            vector_storage_path: Path for vector storage
        """
        self.processed_data_dir = Path(processed_data_dir)
        self.vector_storage_path = vector_storage_path
        
        # Initialize components
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_storage = LocalVectorStorage(
            dimension=384,  # sentence-transformers default
            storage_path=vector_storage_path
        )
        
        logger.info(f"VectorStorageBuilder initialized: {processed_data_dir} -> {vector_storage_path}")
    
    def load_processed_chunks(self) -> List[Dict[str, Any]]:
        """
        Load all processed text chunks from JSON files.
        
        Returns:
            List of chunk dictionaries
        """
        all_chunks = []
        
        # Find all processed JSON files
        json_files = list(self.processed_data_dir.glob("*_processed.json"))
        
        if not json_files:
            logger.warning(f"No processed JSON files found in {self.processed_data_dir}")
            return []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                
                chunks = doc_data.get('chunks', [])
                logger.info(f"Loaded {len(chunks)} chunks from {json_file.name}")
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {str(e)}")
        
        logger.info(f"Total chunks loaded: {len(all_chunks)}")
        return all_chunks
    
    def convert_to_text_chunks(self, chunk_dicts: List[Dict[str, Any]]) -> List[TextChunk]:
        """
        Convert chunk dictionaries to TextChunk objects.
        
        Args:
            chunk_dicts: List of chunk dictionaries from JSON
            
        Returns:
            List of TextChunk objects
        """
        text_chunks = []
        
        for chunk_dict in chunk_dicts:
            try:
                # Extract verse information
                verse_refs = chunk_dict.get('verse_references', [])
                chapter = None
                verse = None
                
                if verse_refs:
                    # Use the first verse reference
                    ref = verse_refs[0]
                    chapter = ref.get('chapter')
                    verse = ref.get('verse')
                
                # Create TextChunk
                text_chunk = TextChunk(
                    id=chunk_dict['chunk_id'],
                    text=chunk_dict['content'],
                    source=chunk_dict['source_file'],
                    chapter=chapter,
                    verse=verse,
                    sanskrit_terms=chunk_dict.get('sanskrit_terms', [])
                )
                
                text_chunks.append(text_chunk)
                
            except Exception as e:
                logger.error(f"Failed to convert chunk {chunk_dict.get('chunk_id', 'unknown')}: {str(e)}")
        
        logger.info(f"Converted {len(text_chunks)} text chunks")
        return text_chunks
    
    def generate_embeddings_for_chunks(self, text_chunks: List[TextChunk]) -> List[TextChunk]:
        """
        Generate embeddings for all text chunks.
        
        Args:
            text_chunks: List of TextChunk objects
            
        Returns:
            List of TextChunk objects with embeddings
        """
        logger.info("Generating embeddings for chunks...")
        
        # Extract texts for batch embedding generation
        texts = [chunk.text for chunk in text_chunks]
        
        # Generate embeddings in batch
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(text_chunks, embeddings):
            chunk.embedding = embedding
        
        logger.info(f"Generated embeddings for {len(text_chunks)} chunks")
        return text_chunks
    
    def build_vector_storage(self) -> Dict[str, Any]:
        """
        Build the complete vector storage from processed chunks.
        
        Returns:
            Summary of the build process
        """
        try:
            # Load processed chunks
            chunk_dicts = self.load_processed_chunks()
            if not chunk_dicts:
                raise ValueError("No processed chunks found")
            
            # Convert to TextChunk objects
            text_chunks = self.convert_to_text_chunks(chunk_dicts)
            
            # Generate embeddings
            text_chunks_with_embeddings = self.generate_embeddings_for_chunks(text_chunks)
            
            # Add to vector storage
            logger.info("Adding chunks to vector storage...")
            self.vector_storage.add_chunks(text_chunks_with_embeddings)
            
            # Save the vector storage
            logger.info("Saving vector storage...")
            self.vector_storage.save()
            
            # Get statistics
            stats = self.vector_storage.get_stats()
            
            build_summary = {
                "success": True,
                "total_chunks": len(text_chunks_with_embeddings),
                "vector_storage_path": self.vector_storage_path,
                "stats": stats
            }
            
            logger.info(f"Vector storage build complete: {build_summary['total_chunks']} chunks")
            return build_summary
            
        except Exception as e:
            logger.error(f"Vector storage build failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_chunks": 0
            }
    
    def test_vector_search(self, query: str = "What is dharma?", k: int = 3) -> List[Dict[str, Any]]:
        """
        Test the vector search functionality.
        
        Args:
            query: Test query
            k: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)[0]
            
            # Search
            results = self.vector_storage.search(query_embedding, k=k)
            
            # Format results
            formatted_results = []
            for chunk, score in results:
                formatted_results.append({
                    "chunk_id": chunk.id,
                    "text": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                    "source": chunk.source,
                    "chapter": chunk.chapter,
                    "verse": chunk.verse,
                    "score": float(score),
                    "sanskrit_terms": chunk.sanskrit_terms
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search test failed: {str(e)}")
            return []


def main():
    """Main function for building vector storage."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Define paths
    script_dir = Path(__file__).parent
    processed_data_dir = script_dir.parent / "data" / "processed"
    vector_storage_path = str(script_dir.parent / "data" / "vectors")
    
    # Create builder
    builder = VectorStorageBuilder(str(processed_data_dir), vector_storage_path)
    
    # Build vector storage
    print("\n=== Building Vector Storage ===")
    results = builder.build_vector_storage()
    
    if results["success"]:
        print(f"✅ Success! Built vector storage with {results['total_chunks']} chunks")
        print(f"📁 Storage path: {results['vector_storage_path']}")
        print(f"📊 Statistics: {results['stats']}")
        
        # Test search
        print("\n=== Testing Vector Search ===")
        test_results = builder.test_vector_search("What is the nature of duty?")
        
        if test_results:
            print("🔍 Test query: 'What is the nature of duty?'")
            print("📋 Top results:")
            for i, result in enumerate(test_results, 1):
                print(f"\n{i}. Score: {result['score']:.3f}")
                print(f"   Source: {Path(result['source']).name}")
                print(f"   Location: Chapter {result['chapter']}, Verse {result['verse']}")
                print(f"   Text: {result['text']}")
                if result['sanskrit_terms']:
                    print(f"   Sanskrit terms: {result['sanskrit_terms']}")
        else:
            print("❌ Vector search test failed")
    
    else:
        print(f"❌ Failed to build vector storage: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
