"""
Hybrid Search Service for Vimarsh RAG Enhancement

Implements BM25 + Dense Vector Fusion for improved retrieval quality.
Part of Phase 1 strategic pivot implementation.

Features:
- BM25 keyword search with TF-IDF scoring
- Dense vector semantic search integration
- Late fusion weighting with configurable parameters
- Personality-aware search with domain optimization
- Performance monitoring and optimization
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np
from collections import defaultdict
import math
import re

# Import existing services for integration
logger = logging.getLogger(__name__)

try:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from vector_database_service import VectorDatabaseService, PersonalityType, ContentType, SearchResult, VectorDocument
except ImportError as e:
    logging.warning(f"⚠️ Could not import vector database service: {e}")
    VectorDatabaseService = None
    PersonalityType = None
    ContentType = None
    SearchResult = None
    VectorDocument = None

logger = logging.getLogger(__name__)

@dataclass
class BM25Document:
    """Document representation for BM25 indexing"""
    id: str
    content: str
    personality: str
    content_type: str
    source: str
    terms: List[str] = field(default_factory=list)
    term_frequencies: Dict[str, int] = field(default_factory=dict)
    doc_length: int = 0
    citation: Optional[str] = None

@dataclass
class HybridSearchResult:
    """Result from hybrid search combining BM25 and vector scores"""
    document: Any  # Union of VectorDocument or BM25Document
    bm25_score: float
    vector_score: float
    hybrid_score: float
    rank_position: int
    search_method: str  # "bm25", "vector", "hybrid"
    personality_match: bool
    relevance_explanation: str

@dataclass
class HybridSearchConfig:
    """Configuration for hybrid search parameters"""
    # BM25 parameters
    k1: float = 1.2  # Term frequency saturation parameter
    b: float = 0.75  # Length normalization parameter
    
    # Fusion parameters
    vector_weight: float = 0.6  # Weight for dense vector scores
    bm25_weight: float = 0.4   # Weight for BM25 scores
    
    # Search parameters
    top_k_bm25: int = 50       # Top K for BM25 retrieval
    top_k_vector: int = 50     # Top K for vector retrieval
    final_top_k: int = 10      # Final results after fusion
    
    # Personality boost
    personality_boost: float = 1.2  # Boost for matching personality
    min_score_threshold: float = 0.1  # Minimum score to include

class HybridSearchService:
    """
    Hybrid Search Service implementing BM25 + Dense Vector Fusion
    
    This service enhances retrieval quality by combining:
    1. BM25 keyword search for exact term matching
    2. Dense vector search for semantic similarity
    3. Late fusion with configurable weighting
    4. Personality-aware scoring and filtering
    """
    
    def __init__(self, config: Optional[HybridSearchConfig] = None):
        self.config = config or HybridSearchConfig()
        self.vector_service = None
        self.bm25_index: Dict[str, BM25Document] = {}
        self.term_doc_freq: Dict[str, int] = defaultdict(int)
        self.avg_doc_length: float = 0.0
        self.total_docs: int = 0
        self.vocabulary: Set[str] = set()
        self.is_initialized = False
        
        logger.info("🔍 Hybrid Search Service initialized")
        
    async def initialize(self) -> bool:
        """Initialize the hybrid search service"""
        try:
            # Initialize vector database service
            if VectorDatabaseService:
                self.vector_service = VectorDatabaseService()
                # Vector service initialization handled separately
                logger.info("✅ Vector database service connected")
            
            # Build BM25 index from available content
            await self._build_bm25_index()
            
            self.is_initialized = True
            logger.info("✅ Hybrid Search Service fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Hybrid Search Service: {e}")
            return False
    
    async def _build_bm25_index(self):
        """Build BM25 index from existing content"""
        try:
            # Load content from local sources for BM25 indexing
            await self._load_content_for_indexing()
            
            # Calculate document statistics
            if self.total_docs > 0:
                self.avg_doc_length = sum(doc.doc_length for doc in self.bm25_index.values()) / self.total_docs
                logger.info(f"📚 BM25 index built: {self.total_docs} documents, avg length: {self.avg_doc_length:.1f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to build BM25 index: {e}")
    
    async def _load_content_for_indexing(self):
        """Load content from data sources for BM25 indexing"""
        try:
            # Load from local JSON files (same as SimpleRAGService)
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sources")
            
            personality_sources = {
                "krishna": ["bhagavad_gita_clean.jsonl"],
                "buddha": ["buddha_teachings.json"],
                "jesus": ["jesus_teachings.json"],
                "einstein": ["einstein_teachings.json"],
                "lincoln": ["lincoln_teachings.json"],
                "marcus_aurelius": ["marcus_aurelius_teachings.json"],
                "lao_tzu": ["lao_tzu_teachings.json"],
                "rumi": ["rumi_teachings.json"],
                "confucius": ["confucius_teachings.json"],
                "newton": ["newton_teachings.json"],
                "tesla": ["tesla_teachings.json"],
                "chanakya": ["chanakya_teachings.json"],
                "muhammad": ["muhammad_teachings.json"]
            }
            
            doc_id = 0
            total_length = 0
            
            for personality, files in personality_sources.items():
                for filename in files:
                    file_path = os.path.join(data_dir, filename)
                    
                    if not os.path.exists(file_path):
                        continue
                    
                    try:
                        if filename.endswith('.jsonl'):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        data = json.loads(line)
                                        doc = self._create_bm25_document(data, personality, str(doc_id))
                                        if doc:
                                            self._index_document(doc)
                                            total_length += doc.doc_length
                                            doc_id += 1
                        else:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if isinstance(data, list):
                                    for item in data:
                                        doc = self._create_bm25_document(item, personality, str(doc_id))
                                        if doc:
                                            self._index_document(doc)
                                            total_length += doc.doc_length
                                            doc_id += 1
                                elif isinstance(data, dict):
                                    doc = self._create_bm25_document(data, personality, str(doc_id))
                                    if doc:
                                        self._index_document(doc)
                                        total_length += doc.doc_length
                                        doc_id += 1
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Error loading {filename}: {e}")
            
            self.total_docs = len(self.bm25_index)
            
        except Exception as e:
            logger.error(f"❌ Failed to load content for indexing: {e}")
    
    def _create_bm25_document(self, data: Dict[str, Any], personality: str, doc_id: str) -> Optional[BM25Document]:
        """Create BM25Document from JSON data"""
        try:
            # Extract content
            content = ""
            if 'content' in data:
                content = data['content']
            elif 'text' in data:
                content = data['text']
            elif 'translation' in data:
                content = data['translation']
            else:
                return None
            
            # Extract source and citation info
            source = data.get('scripture', data.get('source', f"{personality.title()} Teachings"))
            verse = data.get('verse')
            citation = f"{source} {verse}" if verse else source
            
            # Process text into terms
            terms = self._tokenize_text(content)
            term_frequencies = self._calculate_term_frequencies(terms)
            
            return BM25Document(
                id=doc_id,
                content=content[:1000],  # Limit for performance
                personality=personality,
                content_type=data.get('content_type', 'teaching'),
                source=source,
                terms=terms,
                term_frequencies=term_frequencies,
                doc_length=len(terms),
                citation=citation
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Error creating BM25 document: {e}")
            return None
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text for BM25 indexing"""
        # Simple tokenization - can be enhanced with NLTK or spaCy
        text = text.lower()
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        terms = text.split()
        # Filter out very short terms
        terms = [term for term in terms if len(term) > 2]
        return terms
    
    def _calculate_term_frequencies(self, terms: List[str]) -> Dict[str, int]:
        """Calculate term frequencies for a document"""
        tf = defaultdict(int)
        for term in terms:
            tf[term] += 1
        return dict(tf)
    
    def _index_document(self, doc: BM25Document):
        """Index a document for BM25 search"""
        self.bm25_index[doc.id] = doc
        
        # Update vocabulary and document frequencies
        unique_terms = set(doc.terms)
        for term in unique_terms:
            self.term_doc_freq[term] += 1
            self.vocabulary.add(term)
    
    async def hybrid_search(
        self,
        query: str,
        personality: Optional[str] = None,
        content_types: Optional[List[str]] = None,
        top_k: Optional[int] = None
    ) -> List[HybridSearchResult]:
        """
        Perform hybrid search combining BM25 and vector search
        
        Args:
            query: Search query
            personality: Target personality for filtering
            content_types: Content types to filter
            top_k: Number of results to return
            
        Returns:
            List of hybrid search results with combined scores
        """
        if not self.is_initialized:
            logger.warning("⚠️ Hybrid search service not initialized")
            return []
        
        final_k = top_k or self.config.final_top_k
        
        try:
            # Step 1: BM25 keyword search
            bm25_results = await self._bm25_search(query, personality, self.config.top_k_bm25)
            
            # Step 2: Vector semantic search
            vector_results = await self._vector_search(query, personality, content_types, self.config.top_k_vector)
            
            # Step 3: Late fusion of results
            hybrid_results = self._fuse_results(bm25_results, vector_results, query, personality)
            
            # Step 4: Final ranking and filtering
            final_results = self._final_ranking(hybrid_results, final_k)
            
            logger.info(f"🔍 Hybrid search completed: {len(bm25_results)} BM25 + {len(vector_results)} vector → {len(final_results)} final")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Hybrid search failed: {e}")
            return []
    
    async def _bm25_search(self, query: str, personality: Optional[str], top_k: int) -> List[Tuple[str, float]]:
        """Perform BM25 keyword search"""
        try:
            query_terms = self._tokenize_text(query)
            scores = {}
            
            for doc_id, doc in self.bm25_index.items():
                # Filter by personality if specified
                if personality and doc.personality != personality:
                    continue
                
                score = self._calculate_bm25_score(query_terms, doc)
                if score > self.config.min_score_threshold:
                    scores[doc_id] = score
            
            # Sort by score and return top K
            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return sorted_results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ BM25 search failed: {e}")
            return []
    
    def _calculate_bm25_score(self, query_terms: List[str], doc: BM25Document) -> float:
        """Calculate BM25 score for a document"""
        score = 0.0
        
        for term in query_terms:
            if term in doc.term_frequencies:
                # Term frequency in document
                tf = doc.term_frequencies[term]
                
                # Document frequency
                df = self.term_doc_freq.get(term, 1)
                
                # IDF calculation
                idf = math.log((self.total_docs - df + 0.5) / (df + 0.5))
                
                # BM25 formula
                term_score = idf * (tf * (self.config.k1 + 1)) / (
                    tf + self.config.k1 * (1 - self.config.b + self.config.b * (doc.doc_length / self.avg_doc_length))
                )
                
                score += term_score
        
        return score
    
    async def _vector_search(
        self,
        query: str,
        personality: Optional[str],
        content_types: Optional[List[str]],
        top_k: int
    ) -> List[Any]:  # List of SearchResult when available
        """Perform vector semantic search"""
        try:
            if not self.vector_service:
                return []
            
            # Convert personality string to enum if needed
            personality_enum = None
            if personality and PersonalityType:
                try:
                    personality_enum = PersonalityType(personality)
                except ValueError:
                    logger.warning(f"⚠️ Unknown personality: {personality}")
            
            # Perform vector search
            results = await self.vector_service.semantic_search(
                query=query,
                personality=personality_enum,
                content_types=None,  # Handle content_types if needed
                top_k=top_k,
                min_relevance=0.1
            )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            return []
    
    def _fuse_results(
        self,
        bm25_results: List[Tuple[str, float]],
        vector_results: List[Any],  # List of SearchResult when available
        query: str,
        personality: Optional[str]
    ) -> List[HybridSearchResult]:
        """Fuse BM25 and vector search results using late fusion"""
        
        # Normalize scores to [0, 1] range
        normalized_bm25 = self._normalize_scores([score for _, score in bm25_results])
        normalized_vector = self._normalize_scores([result.relevance_score for result in vector_results])
        
        # Create document ID mapping
        bm25_docs = {doc_id: (score, idx) for idx, (doc_id, score) in enumerate(bm25_results)}
        vector_docs = {result.document.id: (result, idx) for idx, result in enumerate(vector_results)}
        
        # Collect all unique document IDs
        all_doc_ids = set(bm25_docs.keys()) | set(vector_docs.keys())
        
        hybrid_results = []
        
        for doc_id in all_doc_ids:
            # Get scores from both methods
            bm25_score = 0.0
            vector_score = 0.0
            document = None
            search_method = "none"
            
            if doc_id in bm25_docs:
                _, bm25_idx = bm25_docs[doc_id]
                bm25_score = normalized_bm25[bm25_idx] if bm25_idx < len(normalized_bm25) else 0.0
                document = self.bm25_index.get(doc_id)
                search_method = "bm25"
            
            if doc_id in vector_docs:
                vector_result, vector_idx = vector_docs[doc_id]
                vector_score = normalized_vector[vector_idx] if vector_idx < len(normalized_vector) else 0.0
                document = vector_result.document
                search_method = "vector" if search_method == "none" else "hybrid"
            
            if document is None:
                continue
            
            # Calculate hybrid score
            hybrid_score = (
                self.config.bm25_weight * bm25_score + 
                self.config.vector_weight * vector_score
            )
            
            # Apply personality boost
            personality_match = False
            if personality:
                doc_personality = getattr(document, 'personality', None)
                if doc_personality:
                    if isinstance(doc_personality, str):
                        personality_match = doc_personality == personality
                    else:
                        personality_match = doc_personality.value == personality
                    
                    if personality_match:
                        hybrid_score *= self.config.personality_boost
            
            # Create explanation
            explanation = f"BM25: {bm25_score:.3f}, Vector: {vector_score:.3f}, Combined: {hybrid_score:.3f}"
            if personality_match:
                explanation += " (personality boost applied)"
            
            hybrid_results.append(HybridSearchResult(
                document=document,
                bm25_score=bm25_score,
                vector_score=vector_score,
                hybrid_score=hybrid_score,
                rank_position=0,  # Will be set in final ranking
                search_method=search_method,
                personality_match=personality_match,
                relevance_explanation=explanation
            ))
        
        return hybrid_results
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to [0, 1] range using min-max normalization"""
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [(score - min_score) / (max_score - min_score) for score in scores]
    
    def _final_ranking(self, hybrid_results: List[HybridSearchResult], top_k: int) -> List[HybridSearchResult]:
        """Final ranking and filtering of hybrid results"""
        
        # Filter by minimum score threshold
        filtered_results = [
            result for result in hybrid_results 
            if result.hybrid_score >= self.config.min_score_threshold
        ]
        
        # Sort by hybrid score
        sorted_results = sorted(filtered_results, key=lambda x: x.hybrid_score, reverse=True)
        
        # Update rank positions
        for i, result in enumerate(sorted_results):
            result.rank_position = i + 1
        
        return sorted_results[:top_k]
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """Get search service statistics"""
        return {
            "initialized": self.is_initialized,
            "bm25_index_size": len(self.bm25_index),
            "vocabulary_size": len(self.vocabulary),
            "avg_doc_length": self.avg_doc_length,
            "total_docs": self.total_docs,
            "vector_service_available": self.vector_service is not None,
            "config": {
                "k1": self.config.k1,
                "b": self.config.b,
                "vector_weight": self.config.vector_weight,
                "bm25_weight": self.config.bm25_weight,
                "personality_boost": self.config.personality_boost
            }
        }

# Global instance for easy import
hybrid_search_service = HybridSearchService()
