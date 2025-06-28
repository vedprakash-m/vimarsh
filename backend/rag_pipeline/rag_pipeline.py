"""
RAG Pipeline Main Class

Comprehensive RAG pipeline implementation that integrates document loading,
text processing, and vector storage for spiritual guidance.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import asyncio

from .document_loader import SpiritualDocumentLoader, DocumentMetadata
from .text_processor import SpiritualTextProcessor, TextChunk
from .vector_storage import LocalVectorStorage

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG (Retrieval-Augmented Generation) pipeline for spiritual texts.
    
    Integrates document loading, text processing, and vector storage to provide
    a complete RAG workflow for spiritual guidance applications.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize RAG pipeline with configuration.
        
        Args:
            config: Configuration dictionary for pipeline components
        """
        self.config = config or {}
        
        # Initialize components
        self.document_loader = SpiritualDocumentLoader()
        self.text_processor = SpiritualTextProcessor(
            chunk_size=self.config.get('chunk_size', 1000),
            overlap_size=self.config.get('overlap_size', 200)
        )
        self.vector_storage = LocalVectorStorage(
            embedding_model=self.config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
            storage_path=self.config.get('storage_path', './vector_storage')
        )
        
        self.is_initialized = False
        self._document_cache: Dict[str, List[TextChunk]] = {}
    
    async def initialize(self) -> bool:
        """
        Initialize the RAG pipeline components.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize vector storage
            await self.vector_storage.initialize()
            
            self.is_initialized = True
            logger.info("RAG Pipeline initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            return False
    
    async def load_documents(self, source_path: Union[str, Path], 
                           force_reload: bool = False) -> List[TextChunk]:
        """
        Load documents from source path and process them.
        
        Args:
            source_path: Path to document(s) to load
            force_reload: Force reload even if cached
            
        Returns:
            List of processed text chunks
        """
        source_key = str(source_path)
        
        # Check cache first
        if not force_reload and source_key in self._document_cache:
            logger.info(f"Using cached documents for {source_path}")
            return self._document_cache[source_key]
        
        try:
            # Load documents
            documents = await self.document_loader.load_documents(source_path)
            
            # Process all documents
            all_chunks = []
            for doc_path, content, metadata in documents:
                chunks = await self.text_processor.process_text(content, metadata)
                all_chunks.extend(chunks)
            
            # Cache results
            self._document_cache[source_key] = all_chunks
            
            logger.info(f"Loaded and processed {len(all_chunks)} chunks from {source_path}")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Failed to load documents from {source_path}: {e}")
            return []
    
    async def add_documents_to_storage(self, chunks: List[TextChunk], 
                                     collection_name: str = "spiritual_texts") -> bool:
        """
        Add processed document chunks to vector storage.
        
        Args:
            chunks: List of text chunks to add
            collection_name: Name of the storage collection
            
        Returns:
            bool: True if successful
        """
        if not self.is_initialized:
            logger.warning("Pipeline not initialized, initializing now...")
            if not await self.initialize():
                return False
        
        try:
            return await self.vector_storage.add_documents(chunks, collection_name)
            
        except Exception as e:
            logger.error(f"Failed to add documents to storage: {e}")
            return False
    
    async def search_similar(self, query: str, top_k: int = 5, 
                           collection_name: str = "spiritual_texts",
                           filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar text chunks based on query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            collection_name: Storage collection to search
            filters: Optional filters for search
            
        Returns:
            List of search results with scores and metadata
        """
        if not self.is_initialized:
            logger.warning("Pipeline not initialized, initializing now...")
            if not await self.initialize():
                return []
        
        try:
            return await self.vector_storage.search_similar(
                query=query,
                top_k=top_k,
                collection_name=collection_name,
                filters=filters
            )
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    async def process_query(self, query: str, context_limit: int = 3) -> Dict[str, Any]:
        """
        Complete RAG query processing workflow.
        
        Args:
            query: User query
            context_limit: Maximum number of context chunks to retrieve
            
        Returns:
            Dictionary with retrieved context and metadata
        """
        try:
            # Search for relevant chunks
            search_results = await self.search_similar(
                query=query,
                top_k=context_limit
            )
            
            # Format context
            context_chunks = []
            citations = []
            
            for result in search_results:
                chunk_data = result.get('chunk', {})
                metadata = result.get('metadata', {})
                
                context_chunks.append({
                    'content': chunk_data.get('content', ''),
                    'metadata': metadata,
                    'score': result.get('score', 0.0)
                })
                
                # Extract citation info
                if 'source' in metadata:
                    citations.append({
                        'source': metadata['source'],
                        'chapter': metadata.get('chapter'),
                        'verse': metadata.get('verse'),
                        'score': result.get('score', 0.0)
                    })
            
            return {
                'query': query,
                'context': context_chunks,
                'citations': citations,
                'total_results': len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return {
                'query': query,
                'context': [],
                'citations': [],
                'error': str(e)
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline statistics and health information.
        
        Returns:
            Dictionary with pipeline statistics
        """
        stats = {
            'initialized': self.is_initialized,
            'cached_documents': len(self._document_cache),
            'total_cached_chunks': sum(len(chunks) for chunks in self._document_cache.values()),
            'config': self.config
        }
        
        if self.is_initialized:
            try:
                storage_stats = await self.vector_storage.get_statistics()
                stats.update(storage_stats)
            except Exception as e:
                stats['storage_error'] = str(e)
        
        return stats
    
    async def reset_cache(self):
        """Reset document cache."""
        self._document_cache.clear()
        logger.info("Document cache reset")
    
    async def shutdown(self):
        """Shutdown pipeline and cleanup resources."""
        try:
            await self.vector_storage.shutdown()
            self._document_cache.clear()
            self.is_initialized = False
            logger.info("RAG Pipeline shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during pipeline shutdown: {e}")


# Pipeline factory function
def create_rag_pipeline(config: Optional[Dict[str, Any]] = None) -> RAGPipeline:
    """
    Factory function to create a configured RAG pipeline.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured RAGPipeline instance
    """
    return RAGPipeline(config)


# Pipeline recovery and error handling
class RAGPipelineError(Exception):
    """Base exception for RAG pipeline errors."""
    pass


class DocumentLoadingError(RAGPipelineError):
    """Exception for document loading errors."""
    pass


class ProcessingError(RAGPipelineError):
    """Exception for text processing errors."""
    pass


class StorageError(RAGPipelineError):
    """Exception for vector storage errors."""
    pass
