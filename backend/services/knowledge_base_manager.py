"""
Knowledge Base Manager for Vimarsh Multi-Personality Platform

This service manages personality-specific knowledge bases including:
- Personality-partitioned vector storage
- Multi-domain embedding strategies
- Cross-personality knowledge retrieval
- Content-personality association
- Knowledge base versioning and updates
- RAG optimization for different domains
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Optional numpy import - gracefully handle missing numpy
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None  # Will cause AttributeError if used, alerting developer

# Optional dependency for vector embeddings (heavy package, only for production)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    # Stub implementation for CI/CD and development
    class SentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name
        
        def encode(self, texts, **kwargs):
            """Return dummy embeddings for CI/CD"""
            if isinstance(texts, str):
                texts = [texts]
            # Return dummy 384-dimensional embeddings (all-MiniLM-L6-v2 dimension)
            import random
            return [[random.random() for _ in range(384)] for _ in texts]
    
    SENTENCE_TRANSFORMERS_AVAILABLE = False
import json
import os

# Import domain processors
try:
    from data_processing.domain_processors import DomainProcessorFactory, ProcessedChunk, ProcessingResult
    DOMAIN_PROCESSORS_AVAILABLE = True
except ImportError:
    try:
        from backend.data_processing.domain_processors import DomainProcessorFactory, ProcessedChunk, ProcessingResult
        DOMAIN_PROCESSORS_AVAILABLE = True
    except ImportError:
        DOMAIN_PROCESSORS_AVAILABLE = False

# Import services
try:
    from database_service import DatabaseService
    from personality_service import personality_service, PersonalityProfile
    DATABASE_AVAILABLE = True
except ImportError:
    try:
        from .database_service import DatabaseService
        from .personality_service import personality_service, PersonalityProfile
        DATABASE_AVAILABLE = True
    except ImportError:
        DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeChunk:
    """Represents a knowledge chunk with embeddings and metadata"""
    id: str
    text: str
    embedding: List[float]
    personality_id: str
    domain: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)
    key_terms: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class RetrievalResult:
    """Result of knowledge retrieval"""
    chunks: List[KnowledgeChunk]
    query: str
    personality_id: str
    similarity_scores: List[float]
    total_results: int
    retrieval_time: float


@dataclass
class KnowledgeBaseStats:
    """Statistics for a knowledge base"""
    personality_id: str
    total_chunks: int
    domains: Dict[str, int]  # domain -> count
    sources: Dict[str, int]  # source -> count
    avg_quality_score: float
    last_updated: str
    embedding_model: str


class KnowledgeBaseManager:
    """Manages personality-specific knowledge bases with vector storage"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        self.db_service = db_service or DatabaseService()
        
        # Initialize embedding model (optional dependency)
        self.embedding_model_name = "all-MiniLM-L6-v2"
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.info(f"✅ Initialized embedding model: {self.embedding_model_name}")
            else:
                logger.warning(f"⚠️ Using stub embedding model (sentence_transformers not available)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding model: {e}")
            self.embedding_model = None
            self.embedding_dim = 384
        
        # Domain-specific embedding strategies
        self.domain_strategies = {
            'spiritual': {'weight_sacred_terms': 1.5, 'preserve_verses': True},
            'scientific': {'weight_technical_terms': 1.3, 'preserve_equations': True},
            'historical': {'weight_dates': 1.2, 'preserve_quotes': True},
            'philosophical': {'weight_logical_terms': 1.4, 'preserve_arguments': True}
        }
        
        # In-memory cache for embeddings
        self.embedding_cache = {}
        self.cache_size_limit = 1000
    
    # ==========================================
    # KNOWLEDGE BASE CREATION AND MANAGEMENT
    # ==========================================
    
    async def create_knowledge_base(
        self,
        personality_id: str,
        content_items: List[Dict[str, Any]]
    ) -> bool:
        """Create knowledge base for a personality from content items"""
        try:
            logger.info(f"🔧 Creating knowledge base for personality: {personality_id}")
            
            # Get personality info
            personality = await personality_service.get_personality(personality_id)
            if not personality:
                raise ValueError(f"Personality {personality_id} not found")
            
            total_chunks = 0
            
            for content_item in content_items:
                chunks_added = await self.add_content_to_knowledge_base(
                    personality_id=personality_id,
                    content=content_item['content'],
                    source=content_item['source'],
                    domain=personality.domain.value,
                    metadata=content_item.get('metadata', {})
                )
                total_chunks += chunks_added
            
            logger.info(f"✅ Created knowledge base for {personality_id} with {total_chunks} chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create knowledge base for {personality_id}: {e}")
            return False
    
    async def add_content_to_knowledge_base(
        self,
        personality_id: str,
        content: str,
        source: str,
        domain: str,
        metadata: Dict[str, Any] = None
    ) -> int:
        """Add content to personality's knowledge base"""
        try:
            if not DOMAIN_PROCESSORS_AVAILABLE:
                logger.warning("Domain processors not available, using basic processing")
                return await self._add_content_basic(personality_id, content, source, domain, metadata)
            
            # Process content using domain-specific processor
            processing_result = DomainProcessorFactory.process_text_for_domain(
                text=content,
                domain=domain,
                source=source,
                metadata=metadata or {}
            )
            
            chunks_added = 0
            
            for processed_chunk in processing_result.chunks:
                # Generate embedding
                embedding = await self._generate_embedding(processed_chunk.text, domain)
                if embedding is None:
                    continue
                
                # Create knowledge chunk
                knowledge_chunk = KnowledgeChunk(
                    id=f"{personality_id}_{processed_chunk.id}",
                    text=processed_chunk.text,
                    embedding=embedding,
                    personality_id=personality_id,
                    domain=domain,
                    source=source,
                    metadata=processed_chunk.metadata,
                    citations=processed_chunk.citations,
                    key_terms=processed_chunk.key_terms,
                    quality_score=processed_chunk.quality_score
                )
                
                # Store in database
                success = await self._store_knowledge_chunk(knowledge_chunk)
                if success:
                    chunks_added += 1
            
            logger.info(f"✅ Added {chunks_added} chunks to {personality_id} knowledge base")
            return chunks_added
            
        except Exception as e:
            logger.error(f"❌ Failed to add content to knowledge base: {e}")
            return 0
    
    async def _add_content_basic(
        self,
        personality_id: str,
        content: str,
        source: str,
        domain: str,
        metadata: Dict[str, Any] = None
    ) -> int:
        """Basic content addition without domain processors"""
        try:
            # Simple chunking
            chunks = self._simple_chunk_text(content)
            chunks_added = 0
            
            for i, chunk_text in enumerate(chunks):
                # Generate embedding
                embedding = await self._generate_embedding(chunk_text, domain)
                if embedding is None:
                    continue
                
                # Create knowledge chunk
                knowledge_chunk = KnowledgeChunk(
                    id=f"{personality_id}_{source}_{i}",
                    text=chunk_text,
                    embedding=embedding,
                    personality_id=personality_id,
                    domain=domain,
                    source=source,
                    metadata=metadata or {},
                    quality_score=75.0  # Default score
                )
                
                # Store in database
                success = await self._store_knowledge_chunk(knowledge_chunk)
                if success:
                    chunks_added += 1
            
            return chunks_added
            
        except Exception as e:
            logger.error(f"❌ Basic content addition failed: {e}")
            return 0
    
    def _simple_chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Simple text chunking"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    # ==========================================
    # EMBEDDING GENERATION
    # ==========================================
    
    async def _generate_embedding(self, text: str, domain: str) -> Optional[List[float]]:
        """Generate embedding for text with domain-specific optimization"""
        try:
            if not self.embedding_model:
                logger.warning("Embedding model not available")
                return None
            
            # Check cache
            cache_key = f"{domain}_{hash(text)}"
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
            
            # Generate embedding
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            embedding_list = embedding.tolist()
            
            # Apply domain-specific weighting if needed
            if domain in self.domain_strategies:
                embedding_list = self._apply_domain_weighting(embedding_list, text, domain)
            
            # Cache the result
            if len(self.embedding_cache) < self.cache_size_limit:
                self.embedding_cache[cache_key] = embedding_list
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            return None
    
    def _apply_domain_weighting(self, embedding: List[float], text: str, domain: str) -> List[float]:
        """Apply domain-specific weighting to embeddings"""
        # This is a simplified implementation
        # In practice, you might want more sophisticated domain adaptation
        strategy = self.domain_strategies.get(domain, {})
        
        # For now, just return the original embedding
        # Future enhancement: implement domain-specific weighting
        return embedding
    
    # ==========================================
    # KNOWLEDGE RETRIEVAL
    # ==========================================
    
    async def retrieve_knowledge(
        self,
        query: str,
        personality_id: str,
        k: int = 10,
        similarity_threshold: float = 0.7,
        domain_filter: Optional[str] = None
    ) -> RetrievalResult:
        """Retrieve relevant knowledge chunks for a query"""
        start_time = datetime.now()
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query, domain_filter or "general")
            if not query_embedding:
                return RetrievalResult(
                    chunks=[],
                    query=query,
                    personality_id=personality_id,
                    similarity_scores=[],
                    total_results=0,
                    retrieval_time=0.0
                )
            
            # Get knowledge chunks for personality
            all_chunks = await self._get_personality_chunks(personality_id, domain_filter)
            
            if not all_chunks:
                return RetrievalResult(
                    chunks=[],
                    query=query,
                    personality_id=personality_id,
                    similarity_scores=[],
                    total_results=0,
                    retrieval_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Calculate similarities
            similarities = []
            for chunk in all_chunks:
                similarity = self._calculate_cosine_similarity(query_embedding, chunk.embedding)
                similarities.append(similarity)
            
            # Filter by threshold and sort
            filtered_results = [
                (chunk, sim) for chunk, sim in zip(all_chunks, similarities)
                if sim >= similarity_threshold
            ]
            
            filtered_results.sort(key=lambda x: x[1], reverse=True)
            
            # Take top k results
            top_results = filtered_results[:k]
            
            retrieval_time = (datetime.now() - start_time).total_seconds()
            
            return RetrievalResult(
                chunks=[chunk for chunk, _ in top_results],
                query=query,
                personality_id=personality_id,
                similarity_scores=[sim for _, sim in top_results],
                total_results=len(filtered_results),
                retrieval_time=retrieval_time
            )
            
        except Exception as e:
            logger.error(f"❌ Knowledge retrieval failed: {e}")
            return RetrievalResult(
                chunks=[],
                query=query,
                personality_id=personality_id,
                similarity_scores=[],
                total_results=0,
                retrieval_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"❌ Similarity calculation failed: {e}")
            return 0.0
    
    # ==========================================
    # DATABASE OPERATIONS
    # ==========================================
    
    async def _store_knowledge_chunk(self, chunk: KnowledgeChunk) -> bool:
        """Store knowledge chunk in database"""
        try:
            # Convert to dict for storage
            chunk_dict = asdict(chunk)
            chunk_dict['type'] = 'knowledge_chunk'
            
            # Store in conversations container (for now)
            data = self.db_service._load_from_local_file(self.db_service.conversations_path)
            data.append(chunk_dict)
            self.db_service._save_to_local_file(self.db_service.conversations_path, data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store knowledge chunk: {e}")
            return False
    
    async def _get_personality_chunks(
        self,
        personality_id: str,
        domain_filter: Optional[str] = None
    ) -> List[KnowledgeChunk]:
        """Get all knowledge chunks for a personality"""
        try:
            data = self.db_service._load_from_local_file(self.db_service.conversations_path)
            
            chunks = []
            for item in data:
                if (item.get('type') == 'knowledge_chunk' and 
                    item.get('personality_id') == personality_id):
                    
                    # Apply domain filter if specified
                    if domain_filter and item.get('domain') != domain_filter:
                        continue
                    
                    # Convert back to KnowledgeChunk
                    chunk_data = {k: v for k, v in item.items() if k != 'type'}
                    chunk = KnowledgeChunk(**chunk_data)
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Failed to get personality chunks: {e}")
            return []
    
    # ==========================================
    # KNOWLEDGE BASE STATISTICS
    # ==========================================
    
    async def get_knowledge_base_stats(self, personality_id: str) -> Optional[KnowledgeBaseStats]:
        """Get statistics for a personality's knowledge base"""
        try:
            chunks = await self._get_personality_chunks(personality_id)
            
            if not chunks:
                return None
            
            # Calculate statistics
            domains = {}
            sources = {}
            total_quality = 0.0
            
            for chunk in chunks:
                # Domain counts
                domains[chunk.domain] = domains.get(chunk.domain, 0) + 1
                
                # Source counts
                sources[chunk.source] = sources.get(chunk.source, 0) + 1
                
                # Quality scores
                total_quality += chunk.quality_score
            
            avg_quality = total_quality / len(chunks) if chunks else 0.0
            
            # Find most recent update
            last_updated = max(chunk.created_at for chunk in chunks) if chunks else datetime.now().isoformat()
            
            return KnowledgeBaseStats(
                personality_id=personality_id,
                total_chunks=len(chunks),
                domains=domains,
                sources=sources,
                avg_quality_score=avg_quality,
                last_updated=last_updated,
                embedding_model=self.embedding_model_name
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get knowledge base stats: {e}")
            return None
    
    # ==========================================
    # CROSS-PERSONALITY RETRIEVAL
    # ==========================================
    
    async def cross_personality_search(
        self,
        query: str,
        domains: List[str] = None,
        k: int = 10,
        similarity_threshold: float = 0.6
    ) -> Dict[str, RetrievalResult]:
        """Search across multiple personalities and domains"""
        try:
            # Get all active personalities
            personalities = await personality_service.get_active_personalities()
            
            results = {}
            
            for personality in personalities:
                # Apply domain filter
                if domains and personality.domain.value not in domains:
                    continue
                
                # Retrieve knowledge for this personality
                result = await self.retrieve_knowledge(
                    query=query,
                    personality_id=personality.id,
                    k=k,
                    similarity_threshold=similarity_threshold
                )
                
                if result.chunks:
                    results[personality.id] = result
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Cross-personality search failed: {e}")
            return {}
    
    # ==========================================
    # KNOWLEDGE BASE MAINTENANCE
    # ==========================================
    
    async def update_knowledge_base(
        self,
        personality_id: str,
        content_updates: List[Dict[str, Any]]
    ) -> bool:
        """Update knowledge base with new content"""
        try:
            chunks_added = 0
            
            for update in content_updates:
                added = await self.add_content_to_knowledge_base(
                    personality_id=personality_id,
                    content=update['content'],
                    source=update['source'],
                    domain=update.get('domain', 'general'),
                    metadata=update.get('metadata', {})
                )
                chunks_added += added
            
            logger.info(f"✅ Updated knowledge base for {personality_id} with {chunks_added} new chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update knowledge base: {e}")
            return False
    
    async def delete_personality_knowledge_base(self, personality_id: str) -> bool:
        """Delete all knowledge chunks for a personality"""
        try:
            data = self.db_service._load_from_local_file(self.db_service.conversations_path)
            
            # Filter out chunks for this personality
            filtered_data = [
                item for item in data
                if not (item.get('type') == 'knowledge_chunk' and 
                       item.get('personality_id') == personality_id)
            ]
            
            self.db_service._save_to_local_file(self.db_service.conversations_path, filtered_data)
            
            logger.info(f"✅ Deleted knowledge base for personality: {personality_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete knowledge base: {e}")
            return False


# Global knowledge base manager instance
knowledge_base_manager = KnowledgeBaseManager()