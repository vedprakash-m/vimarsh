#!/usr/bin/env python3
"""
Enhanced RAG Service - Phase 6 Implementation

This service implements the complete enhanced RAG pipeline with:
1. Vector similarity search using our 24,799 embeddings
2. Personality-aware content retrieval
3. Context-aware response generation with citations
4. Hybrid search (text + vector) capabilities
5. Quality scoring and confidence assessment

Integrates with the existing Cosmos DB vector database created in Phase 5.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import azure.cosmos.cosmos_client as cosmos_client
try:
    import google.generativeai as genai
except ImportError:
    genai = None
try:
    import numpy as np
except ImportError:
    np = None
from collections import defaultdict

# Import centralized AI model configuration
try:
    from config.ai_models import AI_CONFIG as global_ai_config
except ImportError:
    # Fallback if config not available
    from dataclasses import dataclass
    @dataclass
    class FallbackConfig:
        gemini_generation_model: str = "models/gemini-2.5-flash"
        gemini_embedding_model: str = "models/text-embedding-004"
    global_ai_config = FallbackConfig()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a content chunk with embedding and metadata"""
    id: str
    personality_id: str
    content: str
    source: str
    token_count: int
    embedding: Optional[List[float]] = None
    similarity_score: float = 0.0
    quality_score: float = 0.0
    chunk_index: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGContext:
    """Context retrieved from vector database for RAG"""
    query: str
    personality_id: str
    relevant_chunks: List[ContentChunk]
    total_chunks_searched: int
    avg_similarity_score: float
    retrieval_method: str
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @property
    def citations(self) -> List[str]:
        """Extract unique citations from relevant chunks"""
        citations: set[str] = set()
        for chunk in self.relevant_chunks:
            if chunk.source and chunk.source != "unknown":
                citations.add(chunk.source)
        return sorted(list(citations))
    
    @property
    def content_passages(self) -> List[str]:
        """Extract content passages for context"""
        return [chunk.content for chunk in self.relevant_chunks]

@dataclass
class EnhancedRAGResponse:
    """Enhanced response with RAG context and confidence scoring"""
    content: str
    personality_id: str
    query: str
    rag_context: Optional[RAGContext] = None
    confidence_score: float = 0.0
    content_backed: bool = False
    response_source: str = "enhanced_rag"
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EnhancedRAGService:
    """Enhanced RAG service with vector search and personality-aware responses"""
    
    def __init__(self):
        """Initialize the enhanced RAG service"""
        # Environment setup - use standardized connection string
        self.cosmos_connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING', '')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        
        # More graceful error handling for environment variables
        if not self.cosmos_connection_string:
            logger.error("❌ AZURE_COSMOS_CONNECTION_STRING not set")
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING is required")
        
        if not self.gemini_api_key:
            logger.error("❌ GEMINI_API_KEY not set")
            raise ValueError("GEMINI_API_KEY is required")
        
        logger.info("✅ Environment variables loaded successfully")
        
        # Cosmos DB setup with error handling
        try:
            self.client = cosmos_client.CosmosClient.from_connection_string(self.cosmos_connection_string)
            self.database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            self.container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'personality_vectors')  # Correct: underscore
            self.database = self.client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            logger.info(f"✅ Cosmos DB connected: {self.database_name}/{self.container_name}")
        except Exception as e:
            logger.error(f"❌ Cosmos DB connection failed: {str(e)}")
            raise ValueError(f"Cosmos DB initialization failed: {str(e)}")
        
        # Configure Gemini AI with error handling
        try:
            if genai:
                genai.configure(api_key=self.gemini_api_key)
                logger.info("✅ Gemini AI configured successfully")
            else:
                logger.warning("⚠️ Google Generative AI not available, using fallback responses")
                raise ValueError("Google Generative AI package not available")
        except Exception as e:
            logger.error(f"❌ Gemini AI configuration failed: {str(e)}")
            raise ValueError(f"Gemini AI initialization failed: {str(e)}")
        self.embedding_model = global_ai_config.gemini_embedding_model
        self.generation_model = global_ai_config.gemini_generation_model
        
        # Cache for embeddings to avoid regeneration
        self._embedding_cache: Dict[str, List[float]] = {}
        
        logger.info("✅ Enhanced RAG Service initialized successfully")
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        if query in self._embedding_cache:
            return self._embedding_cache[query]
        
        try:
            if not genai:
                logger.warning("⚠️ Gemini AI not available for embeddings")
                return []
            
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"  # Different task type for queries
            )
            embedding = result.get('embedding', [])
            if embedding:
                self._embedding_cache[query] = embedding
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate query embedding: {e}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(a * a for a in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"❌ Error calculating cosine similarity: {e}")
            return 0.0
    
    async def vector_search(self, query: str, personality_id: str, top_k: int = 5) -> List[ContentChunk]:
        """Perform vector similarity search"""
        try:
            # Generate query embedding
            query_embedding = await self.generate_query_embedding(query)
            if not query_embedding:
                logger.warning("⚠️ Failed to generate query embedding, falling back to keyword search")
                return await self.keyword_search(query, personality_id, top_k)
            
            # Query for chunks with embeddings for the specific personality
            cosmos_query = '''
            SELECT c.id, c.personality, c.content, c.source, c.source_metadata, c.domain,
                   c.embedding, c.source_type, c.chunk_metadata
            FROM c 
            WHERE c.personality = @personality_id 
            AND IS_DEFINED(c.embedding)
            '''
            
            parameters: List[Dict[str, Any]] = [{"name": "@personality_id", "value": personality_id}]
            
            chunks = list(self.container.query_items(
                query=cosmos_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            logger.info(f"📊 Found {len(chunks)} chunks with embeddings for {personality_id}")
            
            # Calculate similarities
            content_chunks: List[ContentChunk] = []
            for chunk_data in chunks:
                try:
                    chunk_embedding = chunk_data.get('embedding', [])
                    if chunk_embedding:
                        similarity = self.cosine_similarity(query_embedding, chunk_embedding)
                        
                        # Extract content - support both field names for compatibility
                        content = chunk_data.get('content', '') or chunk_data.get('chunk_text', '')
                        
                        # Create a more descriptive source reference
                        source_ref = chunk_data.get('source', 'unknown')
                        title = chunk_data.get('title', '')
                        chapter = chunk_data.get('chapter', '')
                        source_metadata = chunk_data.get('source_metadata', {})
                        domain = chunk_data.get('domain', '')
                        
                        # Build a better source reference from the actual data structure
                        source = chunk_data.get('source', '')
                        if source:
                            source_ref = source
                        elif domain:
                            source_ref = f"{domain} content"
                        else:
                            source_ref = "Unknown source"
                        
                        chunk = ContentChunk(
                            id=chunk_data['id'],
                            personality_id=chunk_data['personality'],  # Using the correct field name
                            content=content,
                            source=source_ref,
                            token_count=len(content.split()),  # Rough estimate
                            embedding=chunk_embedding,
                            similarity_score=similarity,
                            chunk_index=source_metadata.get('chunk_index'),  # From source_metadata
                            metadata={
                                'domain': domain,
                                'source_type': chunk_data.get('source_type', ''),
                                'source_metadata': source_metadata,
                                'chunk_metadata': chunk_data.get('chunk_metadata', {})
                            }
                        )
                        content_chunks.append(chunk)
                        
                except Exception as chunk_error:
                    logger.warning(f"⚠️ Error processing chunk {chunk_data.get('id', 'unknown')}: {chunk_error}")
                    continue
            
            # Sort by similarity and return top_k
            content_chunks.sort(key=lambda x: x.similarity_score, reverse=True)
            top_chunks = content_chunks[:top_k]
            
            logger.info(f"🎯 Vector search returned {len(top_chunks)} top chunks")
            if top_chunks:
                logger.info(f"📈 Similarity scores: {[f'{c.similarity_score:.3f}' for c in top_chunks]}")
            
            return top_chunks
            
        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            # Fallback to keyword search
            return await self.keyword_search(query, personality_id, top_k)
    
    async def keyword_search(self, query: str, personality_id: str, top_k: int = 5) -> List[ContentChunk]:
        """Fallback keyword search when vector search fails"""
        try:
            # Simple keyword matching in content fields (supporting both field names)
            query_terms = query.lower().split()
            
            cosmos_query = '''
            SELECT c.id, c.personality_id, c.content, c.chunk_text, c.source, c.source_metadata, c.domain,
                   c.source_type, c.chunk_metadata
            FROM c 
            WHERE c.personality_id = @personality_id 
            AND IS_DEFINED(c.embedding)
            '''
            
            parameters: List[Dict[str, Any]] = [{"name": "@personality_id", "value": personality_id}]
            
            chunks = list(self.container.query_items(
                query=cosmos_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Score chunks based on keyword matches (supporting both field names)
            scored_chunks: List[ContentChunk] = []
            for chunk_data in chunks:
                content = (chunk_data.get('content', '') or chunk_data.get('chunk_text', '')).lower()
                score = sum(content.count(term) for term in query_terms)
                
                if score > 0:  # Only include chunks with keyword matches
                    # Create source reference using the actual data structure
                    source_metadata = chunk_data.get('source_metadata', {})
                    domain = chunk_data.get('domain', '')
                    source = chunk_data.get('source', '')
                    
                    if source:
                        source_ref = source
                    elif domain:
                        source_ref = f"{domain} content"
                    else:
                        source_ref = "Unknown source"
                    
                    chunk = ContentChunk(
                        id=chunk_data['id'],
                        personality_id=chunk_data.get('personality_id', chunk_data.get('personality', '')),  # Support both field names
                        content=chunk_data.get('content', '') or chunk_data.get('chunk_text', ''),  # Support both content fields
                        source=source_ref,
                        token_count=len((chunk_data.get('content', '') or chunk_data.get('chunk_text', '')).split()),  # Support both fields
                        similarity_score=float(score) / len(query_terms),  # Normalized score
                        chunk_index=source_metadata.get('chunk_index'),
                        metadata={
                            'domain': domain,
                            'source_type': chunk_data.get('source_type', ''),
                            'source_metadata': source_metadata,
                            'chunk_metadata': chunk_data.get('chunk_metadata', {})
                        }
                    )
                    scored_chunks.append(chunk)
            
            # Sort by score and return top_k
            scored_chunks.sort(key=lambda x: x.similarity_score, reverse=True)
            top_chunks = scored_chunks[:top_k]
            
            logger.info(f"🔍 Keyword search returned {len(top_chunks)} chunks for '{query}'")
            return top_chunks
            
        except Exception as e:
            logger.error(f"❌ Keyword search failed: {e}")
            return []
    
    async def retrieve_context(self, query: str, personality_id: str, method: str = "vector") -> RAGContext:
        """Retrieve relevant context for the query"""
        try:
            if method == "vector":
                relevant_chunks = await self.vector_search(query, personality_id, top_k=5)
                retrieval_method = "vector_similarity"
            else:
                relevant_chunks = await self.keyword_search(query, personality_id, top_k=5)
                retrieval_method = "keyword_matching"
            
            # Calculate average similarity score
            avg_similarity = 0.0
            if relevant_chunks:
                avg_similarity = sum(chunk.similarity_score for chunk in relevant_chunks) / len(relevant_chunks)
            
            # Create RAG context
            rag_context = RAGContext(
                query=query,
                personality_id=personality_id,
                relevant_chunks=relevant_chunks,
                total_chunks_searched=len(relevant_chunks),
                avg_similarity_score=avg_similarity,
                retrieval_method=retrieval_method
            )
            
            logger.info(f"📚 Retrieved context: {len(relevant_chunks)} chunks, avg similarity: {avg_similarity:.3f}")
            return rag_context
            
        except Exception as e:
            logger.error(f"❌ Context retrieval failed: {e}")
            # Return empty context
            return RAGContext(
                query=query,
                personality_id=personality_id,
                relevant_chunks=[],
                total_chunks_searched=0,
                avg_similarity_score=0.0,
                retrieval_method="failed"
            )
    
    async def generate_enhanced_response(self, query: str, personality_id: str, context: str = "") -> EnhancedRAGResponse:
        """Generate enhanced response using RAG context"""
        try:
            # Step 1: Retrieve relevant context
            rag_context = await self.retrieve_context(query, personality_id)
            
            # Step 2: Prepare context for generation
            context_passages = []
            if rag_context.relevant_chunks:
                context_passages = [
                    f"Source: {chunk.source}\nContent: {chunk.content[:500]}..."
                    for chunk in rag_context.relevant_chunks[:3]  # Top 3 chunks
                ]
            
            # Step 3: Create enhanced prompt with context
            personality_context = f"You are {personality_id} providing spiritual guidance."
            
            if context_passages:
                context_text = "\n\n".join(context_passages)
                enhanced_prompt = f"""
{personality_context}

Based on the following relevant spiritual content:

{context_text}

Please respond to this question in character as {personality_id}:
{query}

Provide a thoughtful response that draws from the relevant content while maintaining your unique personality and perspective. Include relevant citations if you reference specific sources.
"""
            else:
                enhanced_prompt = f"""
{personality_context}

Please respond to this question in character as {personality_id}:
{query}

{context if context else ""}
"""
            
            # Step 4: Generate response using Gemini
            try:
                model = genai.GenerativeModel(self.generation_model)
                response = model.generate_content(enhanced_prompt)
                
                if response and response.text:
                    content = response.text.strip()
                    content_backed = len(rag_context.relevant_chunks) > 0
                    
                    # Calculate confidence score based on context quality
                    confidence_score = min(1.0, rag_context.avg_similarity_score * 1.2) if content_backed else 0.5
                    
                    enhanced_response = EnhancedRAGResponse(
                        content=content,
                        personality_id=personality_id,
                        query=query,
                        rag_context=rag_context,
                        confidence_score=confidence_score,
                        content_backed=content_backed,
                        response_source="enhanced_rag_gemini",
                        metadata={
                            "chunks_used": len(rag_context.relevant_chunks),
                            "avg_similarity": rag_context.avg_similarity_score,
                            "retrieval_method": rag_context.retrieval_method,
                            "citations": rag_context.citations
                        }
                    )
                    
                    logger.info(f"✅ Generated enhanced RAG response: {len(content)} chars, confidence: {confidence_score:.3f}")
                    return enhanced_response
                    
                else:
                    raise Exception("No response generated from Gemini")
                    
            except Exception as generation_error:
                logger.error(f"❌ Response generation failed: {generation_error}")
                
                # Check if it's a quota exceeded error
                error_str = str(generation_error).lower()
                if "quota" in error_str or "429" in error_str:
                    fallback_content = f"I'm currently experiencing high demand and have temporarily reached my AI processing capacity. As {personality_id}, I'd be happy to provide you with traditional wisdom instead. Please try again later or ask a simpler question."
                    error_type = "quota_exceeded"
                else:
                    fallback_content = f"I apologize, but I'm having difficulty accessing my knowledge base right now. As {personality_id}, I'd be happy to help once the connection is restored."
                    error_type = "generation_failed"
                
                return EnhancedRAGResponse(
                    content=fallback_content,
                    personality_id=personality_id,
                    query=query,
                    rag_context=rag_context,
                    confidence_score=0.1,
                    content_backed=False,
                    response_source="fallback",
                    metadata={"error": error_type}
                )
                
        except Exception as e:
            logger.error(f"❌ Enhanced response generation failed: {e}")
            # Return basic fallback
            return EnhancedRAGResponse(
                content="I apologize, but I'm currently unable to provide a response. Please try again.",
                personality_id=personality_id,
                query=query,
                confidence_score=0.0,
                content_backed=False,
                response_source="error_fallback",
                metadata={"error": str(e)}
            )

# Export the service
enhanced_rag_service = EnhancedRAGService()

async def main():
    """Test the enhanced RAG service"""
    service = EnhancedRAGService()
    
    # Test query
    test_query = "How can I find inner peace?"
    test_personality = "krishna"
    
    print(f"🧪 Testing Enhanced RAG Service")
    print(f"Query: {test_query}")
    print(f"Personality: {test_personality}")
    
    response = await service.generate_enhanced_response(test_query, test_personality)
    
    print(f"\n✅ Response Generated:")
    print(f"Content: {response.content[:200]}...")
    print(f"Confidence: {response.confidence_score:.3f}")
    print(f"Content Backed: {response.content_backed}")
    print(f"Citations: {response.rag_context.citations if response.rag_context else []}")

if __name__ == "__main__":
    asyncio.run(main())
