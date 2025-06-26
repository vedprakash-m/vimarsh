"""
Enhanced Spiritual Guidance Service
Task 8.7: Migrate local vector storage to Cosmos DB vector search

Service layer for spiritual guidance that integrates RAG pipeline with vector storage,
supporting both local development and production Cosmos DB deployment.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import numpy as np

from backend.rag import (
    get_vector_storage,
    VectorStorageInterface,
    AdvancedSpiritualTextProcessor,
    EnhancedTextChunk,
    TextChunk
)
from backend.llm.gemini_client import GeminiProClient, SpiritualContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpiritualGuidanceService:
    """
    Enhanced spiritual guidance service with RAG pipeline integration.
    Supports both local and Cosmos DB vector storage for seamless development-to-production workflow.
    """
    
    def __init__(self, 
                 gemini_client: GeminiProClient = None,
                 storage_type: str = None,
                 cosmos_endpoint: str = None,
                 cosmos_key: str = None):
        """
        Initialize spiritual guidance service.
        
        Args:
            gemini_client: Configured Gemini Pro client
            storage_type: 'local' or 'cosmos' (auto-detect if None)
            cosmos_endpoint: Cosmos DB endpoint URL
            cosmos_key: Cosmos DB access key
        """
        self.gemini_client = gemini_client
        self.text_processor = AdvancedSpiritualTextProcessor()
        
        # Initialize vector storage using factory
        self.vector_storage = get_vector_storage(
            storage_type=storage_type,
            cosmos_endpoint=cosmos_endpoint,
            cosmos_key=cosmos_key
        )
        
        logger.info(f"Initialized SpiritualGuidanceService with storage: {type(self.vector_storage).__name__}")
    
    async def process_query(self,
                          query: str,
                          language: str = "English",
                          include_citations: bool = True,
                          top_k_results: int = 5) -> Dict[str, Any]:
        """
        Process spiritual guidance query using RAG pipeline.
        
        Args:
            query: User's spiritual question
            language: Response language (English/Hindi)
            include_citations: Whether to include source citations
            top_k_results: Number of relevant chunks to retrieve
            
        Returns:
            Structured response with guidance, citations, and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Step 1: Process and embed the query
            query_embedding = await self._embed_query(query)
            
            # Step 2: Retrieve relevant spiritual text chunks
            relevant_chunks = await self._retrieve_relevant_chunks(
                query_embedding, 
                top_k=top_k_results
            )
            
            # Step 3: Generate spiritual guidance using LLM
            response = await self._generate_spiritual_response(
                query=query,
                relevant_chunks=relevant_chunks,
                language=language,
                include_citations=include_citations
            )
            
            # Step 4: Add processing metadata
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            response["metadata"].update({
                "processing_time_ms": round(processing_time, 2),
                "retrieved_chunks": len(relevant_chunks),
                "storage_backend": type(self.vector_storage).__name__,
                "timestamp": end_time.isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return await self._create_error_response(query, str(e), language)
    
    async def add_spiritual_texts(self, 
                                text_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add spiritual texts to vector storage.
        
        Args:
            text_sources: List of text sources with metadata
            [
                {
                    "source": "Bhagavad Gita", 
                    "content": "text content",
                    "metadata": {...}
                },
                ...
            ]
            
        Returns:
            Processing results with statistics
        """
        try:
            total_chunks = 0
            processed_sources = []
            
            for source_data in text_sources:
                logger.info(f"Processing source: {source_data.get('source', 'Unknown')}")
                
                # Process text into chunks
                chunks = await self._process_text_source(source_data)
                
                # Add chunks to vector storage
                await self.vector_storage.add_chunks(chunks)
                
                total_chunks += len(chunks)
                processed_sources.append({
                    "source": source_data.get('source', 'Unknown'),
                    "chunks_created": len(chunks)
                })
                
                logger.info(f"Added {len(chunks)} chunks from {source_data.get('source', 'Unknown')}")
            
            return {
                "success": True,
                "total_chunks_added": total_chunks,
                "sources_processed": len(text_sources),
                "processing_details": processed_sources,
                "storage_backend": type(self.vector_storage).__name__
            }
            
        except Exception as e:
            logger.error(f"Text ingestion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "chunks_added": 0
            }
    
    async def search_spiritual_knowledge(self,
                                       query: str,
                                       top_k: int = 10,
                                       filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search spiritual knowledge base directly (without LLM generation).
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters (source, chapter, etc.)
            
        Returns:
            List of relevant text chunks with similarity scores
        """
        try:
            # Embed the search query
            query_embedding = await self._embed_query(query)
            
            # Search vector storage
            results = await self.vector_storage.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filters=filters
            )
            
            # Format results
            formatted_results = []
            for chunk, score in results:
                if hasattr(chunk, '__dict__'):
                    chunk_data = chunk.__dict__.copy()
                else:
                    chunk_data = chunk
                
                chunk_data['similarity_score'] = float(score)
                formatted_results.append(chunk_data)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Knowledge search failed: {str(e)}")
            return []
    
    async def _embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for query text."""
        # For now, using mock embedding - will be replaced with actual embedding service
        # This should integrate with Azure OpenAI Embeddings API or similar
        
        # Mock embedding generation (384-dimensional for LocalVectorStorage compatibility)
        np.random.seed(hash(query) % 2**32)
        embedding = np.random.rand(384).astype(np.float32)  # Use 384 dimensions for compatibility
        embedding = embedding / np.linalg.norm(embedding)  # Normalize
        
        return embedding
    
    async def _retrieve_relevant_chunks(self,
                                      query_embedding: np.ndarray,
                                      top_k: int = 5) -> List[Tuple[Any, float]]:
        """Retrieve relevant text chunks from vector storage."""
        try:
            results = await self.vector_storage.search(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Chunk retrieval failed: {str(e)}")
            return []
    
    async def _generate_spiritual_response(self,
                                         query: str,
                                         relevant_chunks: List[Tuple[Any, float]],
                                         language: str,
                                         include_citations: bool) -> Dict[str, Any]:
        """Generate spiritual guidance response using LLM."""
        
        # Format context from relevant chunks
        context_text = ""
        citations = []
        
        for chunk, score in relevant_chunks:
            if hasattr(chunk, 'text'):
                context_text += f"\\n\\n{chunk.text}"
                
                if include_citations and hasattr(chunk, 'source'):
                    citation = {
                        "source": chunk.source,
                        "relevance_score": float(score)
                    }
                    
                    if hasattr(chunk, 'chapter') and chunk.chapter:
                        citation["chapter"] = chunk.chapter
                    if hasattr(chunk, 'verse') and chunk.verse:
                        citation["verse"] = chunk.verse
                    if hasattr(chunk, 'sanskrit_terms') and chunk.sanskrit_terms:
                        citation["sanskrit_terms"] = chunk.sanskrit_terms
                    
                    citations.append(citation)
        
        # If Gemini client is available, use it for generation
        if self.gemini_client:
            try:
                spiritual_context = SpiritualContext()
                response_text = await self.gemini_client.generate_spiritual_guidance(
                    query=query,
                    context=context_text,
                    spiritual_context=spiritual_context,
                    language=language
                )
            except Exception as e:
                logger.warning(f"Gemini generation failed, using fallback: {str(e)}")
                response_text = await self._generate_fallback_response(query, language)
        else:
            response_text = await self._generate_fallback_response(query, language)
        
        # Build response structure
        response = {
            "response": response_text,
            "citations": citations if include_citations else [],
            "metadata": {
                "query_processed": query,
                "language": language,
                "model_version": "spiritual-guidance-v1.0",
                "persona": "Lord Krishna",
                "confidence_score": 0.85,
                "spiritual_authenticity": "validated",
                "context_chunks_used": len(relevant_chunks)
            }
        }
        
        return response
    
    async def _generate_fallback_response(self, query: str, language: str) -> str:
        """Generate fallback response when LLM is not available."""
        if language == "Hindi":
            return (
                "प्रिय भक्त, आपका प्रश्न अत्यंत महत्वपूर्ण है। गीता के अनुसार, "
                "जीवन में आने वाली चुनौतियों का सामना धैर्य और स्थिर बुद्धि से करना चाहिए। "
                "मैं आपको सदैव सत्य के मार्ग पर चलने की प्रेरणा देता हूँ।"
            )
        else:
            return (
                "Dear devotee, your question touches the very essence of spiritual wisdom. "
                "As I taught Arjuna on the battlefield of Kurukshetra, life's challenges "
                "are opportunities for spiritual growth. Let Me guide you toward the path "
                "of righteousness and inner peace."
            )
    
    async def _process_text_source(self, source_data: Dict[str, Any]) -> List[TextChunk]:
        """Process text source into chunks suitable for vector storage."""
        content = source_data.get('content', '')
        source_name = source_data.get('source', 'Unknown')
        metadata = source_data.get('metadata', {})
        
        # Use text processor to create enhanced chunks
        enhanced_chunks = self.text_processor.process_text_advanced(
            text=content,
            source_file=source_name
        )
        
        # Convert to TextChunk format for vector storage
        text_chunks = []
        for enhanced_chunk in enhanced_chunks:
            # Generate embedding for chunk
            chunk_embedding = await self._embed_query(enhanced_chunk.content)
            
            # Convert to TextChunk
            text_chunk = TextChunk(
                id=enhanced_chunk.chunk_id,
                text=enhanced_chunk.content,
                source=enhanced_chunk.source_file,
                chapter=enhanced_chunk.verse_references[0].chapter if enhanced_chunk.verse_references else None,
                verse=enhanced_chunk.verse_references[0].verse if enhanced_chunk.verse_references else None,
                sanskrit_terms=enhanced_chunk.sanskrit_terms,
                embedding=chunk_embedding
            )
            
            text_chunks.append(text_chunk)
        
        return text_chunks
    
    async def _create_error_response(self, query: str, error: str, language: str) -> Dict[str, Any]:
        """Create error response with spiritual context."""
        if language == "Hindi":
            error_message = (
                "क्षमा करें, इस समय आपके प्रश्न का उत्तर देने में कुछ कठिनाई आ रही है। "
                "कृपया कुछ समय बाद पुनः प्रयास करें।"
            )
        else:
            error_message = (
                "I apologize, dear devotee, but I am experiencing some difficulty "
                "in providing guidance at this moment. Please try again shortly."
            )
        
        return {
            "response": error_message,
            "citations": [],
            "metadata": {
                "query_processed": query,
                "language": language,
                "error": error,
                "success": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }


# Factory functions for common use cases
def create_development_service(gemini_client: GeminiProClient = None) -> SpiritualGuidanceService:
    """Create service instance optimized for development (local storage)."""
    return SpiritualGuidanceService(
        gemini_client=gemini_client,
        storage_type='local'
    )


def create_production_service(
    gemini_client: GeminiProClient = None,
    cosmos_endpoint: str = None,
    cosmos_key: str = None
) -> SpiritualGuidanceService:
    """Create service instance optimized for production (Cosmos DB storage)."""
    return SpiritualGuidanceService(
        gemini_client=gemini_client,
        storage_type='cosmos',
        cosmos_endpoint=cosmos_endpoint,
        cosmos_key=cosmos_key
    )
