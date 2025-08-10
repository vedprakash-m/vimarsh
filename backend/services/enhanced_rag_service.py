"""
RAG Integration Service for Vimarsh Phase 1 Enhancements

Integrates the new hybrid search and citation grounding services
with the existing RAG pipeline to provide enhanced quality and accuracy.

This service acts as the bridge between:
1. Existing SimpleRAGServi                # Use vector database service
                vector_results = await self.vector_service.semantic_search(
                    query=query,
                    personality=personality,
                    top_k=5
                )d VectorDatabaseService
2. New HybridSearchService (BM25 + vector fusion)
3. New CitationGroundingChecker (citation validation)

Part of Phase 1 strategic pivot implementation.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Import existing services
try:
    from services.rag_service import SimpleRAGService
except ImportError:
    try:
        from rag_service import SimpleRAGService
    except ImportError:
        SimpleRAGService = None

try:
    from services.vector_database_service import VectorDatabaseService
except ImportError:
    try:
        from vector_database_service import VectorDatabaseService
    except ImportError:
        VectorDatabaseService = None

# Import Phase 1 enhancement services
try:
    from services.hybrid_search_service import HybridSearchService
except ImportError:
    try:
        from hybrid_search_service import HybridSearchService
    except ImportError:
        HybridSearchService = None

try:
    from services.citation_grounding_checker import CitationGroundingChecker, CitationValidationLevel
except ImportError:
    try:
        from citation_grounding_checker import CitationGroundingChecker, CitationValidationLevel
    except ImportError:
        CitationGroundingChecker = None
        CitationValidationLevel = None

logger = logging.getLogger(__name__)

@dataclass
class EnhancedRAGResult:
    """Enhanced RAG result with quality metrics"""
    response_text: str
    citations: List[str]
    search_method: str  # "simple", "hybrid", "fallback"
    retrieval_score: float
    citation_precision: float
    confidence_level: str
    hallucination_risk: str
    response_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGQualityMetrics:
    """Quality metrics for RAG responses"""
    total_queries: int = 0
    successful_responses: int = 0
    hybrid_search_usage: int = 0
    citation_validations: int = 0
    avg_response_time: float = 0.0
    avg_citation_precision: float = 0.0
    high_quality_responses: int = 0  # Citation precision >= 0.7

class EnhancedRAGService:
    """
    Enhanced RAG Service with Hybrid Search and Citation Grounding
    
    Provides improved retrieval quality and citation validation while
    maintaining compatibility with existing Vimarsh RAG infrastructure.
    """
    
    def __init__(self):
        self.simple_rag = None
        self.vector_service = None
        self.hybrid_search = None
        self.citation_checker = None
        
        self.quality_metrics = RAGQualityMetrics()
        self.fallback_enabled = True
        self.hybrid_search_enabled = True
        self.citation_validation_enabled = True
        
        # Quality thresholds
        self.min_citation_precision = 0.7
        self.min_retrieval_score = 0.3
        
        logger.info("🚀 Initializing Enhanced RAG Service...")
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all RAG services with fallback handling"""
        
        # Initialize existing services
        try:
            if SimpleRAGService:
                self.simple_rag = SimpleRAGService()
                logger.info("✅ Simple RAG Service initialized")
            else:
                logger.warning("⚠️ Simple RAG Service not available")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Simple RAG: {e}")
        
        try:
            if VectorDatabaseService:
                self.vector_service = VectorDatabaseService()
                logger.info("✅ Vector Database Service initialized")
            else:
                logger.warning("⚠️ Vector Database Service not available")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vector Database: {e}")
        
        # Initialize new enhanced services
        try:
            if HybridSearchService:
                self.hybrid_search = HybridSearchService()
                logger.info("✅ Hybrid Search Service initialized")
            else:
                logger.warning("⚠️ Hybrid Search Service not available")
                self.hybrid_search_enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Hybrid Search: {e}")
            self.hybrid_search_enabled = False
        
        try:
            if CitationGroundingChecker and CitationValidationLevel:
                self.citation_checker = CitationGroundingChecker(CitationValidationLevel.MODERATE)
                logger.info("✅ Citation Grounding Checker initialized")
            else:
                logger.warning("⚠️ Citation Grounding Checker not available")
                self.citation_validation_enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Citation Checker: {e}")
            self.citation_validation_enabled = False
        
        # Log service status
        services_status = {
            "simple_rag": self.simple_rag is not None,
            "vector_service": self.vector_service is not None,
            "hybrid_search": self.hybrid_search is not None and self.hybrid_search_enabled,
            "citation_checker": self.citation_checker is not None and self.citation_validation_enabled
        }
        
        logger.info(f"📊 Service initialization status: {services_status}")
    
    async def enhanced_retrieve_and_generate(
        self,
        query: str,
        personality: Optional[str] = None,
        context: Optional[str] = None,
        enable_citation_validation: bool = True
    ) -> EnhancedRAGResult:
        """
        Enhanced RAG retrieval and generation with quality improvements
        
        Args:
            query: User query
            personality: Target personality for responses
            context: Additional context for generation
            enable_citation_validation: Whether to validate citations
            
        Returns:
            EnhancedRAGResult with quality metrics
        """
        start_time = datetime.now()
        
        try:
            self.quality_metrics.total_queries += 1
            
            # Step 1: Enhanced Retrieval
            retrieval_result = await self._enhanced_retrieval(query, personality)
            
            # Step 2: Response Generation (using existing RAG)
            generation_result = await self._generate_response(
                query, retrieval_result, personality, context
            )
            
            # Step 3: Citation Validation (if enabled)
            validation_result = None
            if enable_citation_validation and self.citation_validation_enabled:
                validation_result = await self._validate_citations(
                    generation_result['response'], 
                    generation_result['citations']
                )
                self.quality_metrics.citation_validations += 1
            
            # Step 4: Compile Enhanced Result
            response_time = (datetime.now() - start_time).total_seconds()
            
            enhanced_result = EnhancedRAGResult(
                response_text=generation_result['response'],
                citations=generation_result['citations'],
                search_method=retrieval_result['method'],
                retrieval_score=retrieval_result['score'],
                citation_precision=validation_result['precision'] if validation_result else 0.0,
                confidence_level=validation_result['confidence'] if validation_result else "unknown",
                hallucination_risk=validation_result['risk'] if validation_result else "unknown",
                response_time=response_time,
                metadata={
                    'personality': personality,
                    'retrieval_details': retrieval_result.get('details', {}),
                    'validation_details': validation_result.get('details', {}) if validation_result else {}
                }
            )
            
            # Update quality metrics
            self._update_quality_metrics(enhanced_result)
            
            logger.info(f"✅ Enhanced RAG completed: {response_time:.2f}s, precision: {enhanced_result.citation_precision:.1%}")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced RAG failed: {e}")
            
            # Fallback to simple RAG if available
            if self.fallback_enabled and self.simple_rag:
                return await self._fallback_rag(query, personality, context, start_time)
            else:
                raise
    
    async def _enhanced_retrieval(self, query: str, personality: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced retrieval using hybrid search with fallback"""
        
        # Try hybrid search first if available
        if self.hybrid_search_enabled and self.hybrid_search:
            try:
                hybrid_results = await self.hybrid_search.hybrid_search(
                    query=query,
                    personality=personality,
                    top_k=10
                )
                
                if hybrid_results:
                    self.quality_metrics.hybrid_search_usage += 1
                    
                    # Calculate average retrieval score
                    avg_score = sum(r.hybrid_score for r in hybrid_results) / len(hybrid_results)
                    
                    return {
                        'method': 'hybrid',
                        'results': hybrid_results,
                        'score': avg_score,
                        'details': {
                            'result_count': len(hybrid_results),
                            'top_score': hybrid_results[0].hybrid_score,
                            'search_method': 'BM25+Vector'
                        }
                    }
                
            except Exception as e:
                logger.warning(f"⚠️ Hybrid search failed, falling back: {e}")
        
        # Fallback to vector search
        if self.vector_service:
            try:
                vector_results = await self.vector_service.semantic_search(
                    query=query,
                    personality=personality,
                    top_k=10
                )
                
                if vector_results:
                    avg_score = sum(r.relevance_score for r in vector_results) / len(vector_results)
                    
                    return {
                        'method': 'vector',
                        'results': vector_results,
                        'score': avg_score,
                        'details': {
                            'result_count': len(vector_results),
                            'top_score': vector_results[0].relevance_score,
                            'search_method': 'Vector'
                        }
                    }
                
            except Exception as e:
                logger.warning(f"⚠️ Vector search failed: {e}")
        
        # Final fallback: simple retrieval
        return {
            'method': 'simple',
            'results': [],
            'score': 0.0,
            'details': {'search_method': 'Fallback'}
        }
    
    async def _generate_response(
        self, 
        query: str, 
        retrieval_result: Dict[str, Any], 
        personality: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using existing RAG services"""
        
        try:
            if self.simple_rag:
                # Use existing SimpleRAGService for response generation
                rag_response = self.simple_rag.generate_rag_response(
                    query=query,
                    personality=personality or "krishna",
                    max_context_items=3
                )
                
                return {
                    'response': rag_response.response,
                    'citations': rag_response.citations,
                    'context': ' '.join(rag_response.context_chunks)
                }
            else:
                # Basic response if no RAG service available
                return {
                    'response': f"I understand you're asking about: {query}",
                    'citations': [],
                    'context': ''
                }
                
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            return {
                'response': "I apologize, but I'm unable to provide a detailed response at this time.",
                'citations': [],
                'context': ''
            }
    
    async def _validate_citations(self, response: str, citations: List[str]) -> Dict[str, Any]:
        """Validate citations using citation grounding checker"""
        
        try:
            if self.citation_checker and citations:
                validation_report = await self.citation_checker.validate_response_grounding(
                    response_text=response,
                    citations=citations
                )
                
                return {
                    'precision': validation_report.overall_precision,
                    'confidence': validation_report.confidence_level,
                    'risk': validation_report.hallucination_risk,
                    'details': {
                        'valid_citations': validation_report.valid_citations,
                        'total_citations': validation_report.total_citations,
                        'recommendation': validation_report.recommendation
                    }
                }
            else:
                return {
                    'precision': 0.0,
                    'confidence': 'unknown',
                    'risk': 'unknown',
                    'details': {}
                }
                
        except Exception as e:
            logger.warning(f"⚠️ Citation validation failed: {e}")
            return {
                'precision': 0.0,
                'confidence': 'error',
                'risk': 'unknown',
                'details': {'error': str(e)}
            }
    
    async def _fallback_rag(
        self, 
        query: str, 
        personality: Optional[str], 
        context: Optional[str],
        start_time: datetime
    ) -> EnhancedRAGResult:
        """Fallback to simple RAG when enhanced services fail"""
        
        try:
            if self.simple_rag:
                simple_response = self.simple_rag.generate_rag_response(
                    query=query,
                    personality=personality or "krishna",
                    max_context_items=3
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                return EnhancedRAGResult(
                    response_text=simple_response.response,
                    citations=simple_response.citations,
                    search_method="fallback",
                    retrieval_score=0.5,  # Default fallback score
                    citation_precision=0.0,
                    confidence_level="low",
                    hallucination_risk="medium",
                    response_time=response_time,
                    metadata={'fallback_reason': 'enhanced_services_unavailable'}
                )
            else:
                raise Exception("No fallback RAG service available")
                
        except Exception as e:
            logger.error(f"❌ Fallback RAG failed: {e}")
            raise
    
    def _update_quality_metrics(self, result: EnhancedRAGResult):
        """Update quality metrics based on result"""
        
        self.quality_metrics.successful_responses += 1
        
        if result.search_method == "hybrid":
            self.quality_metrics.hybrid_search_usage += 1
        
        # Update running averages
        total = self.quality_metrics.successful_responses
        
        # Update average response time
        self.quality_metrics.avg_response_time = (
            (self.quality_metrics.avg_response_time * (total - 1) + result.response_time) / total
        )
        
        # Update average citation precision
        if result.citation_precision > 0:
            self.quality_metrics.avg_citation_precision = (
                (self.quality_metrics.avg_citation_precision * (total - 1) + result.citation_precision) / total
            )
        
        # Track high quality responses
        if result.citation_precision >= self.min_citation_precision:
            self.quality_metrics.high_quality_responses += 1
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current quality metrics"""
        
        total = self.quality_metrics.total_queries
        success_rate = self.quality_metrics.successful_responses / total if total > 0 else 0.0
        hybrid_usage_rate = self.quality_metrics.hybrid_search_usage / total if total > 0 else 0.0
        high_quality_rate = self.quality_metrics.high_quality_responses / total if total > 0 else 0.0
        
        return {
            "total_queries": total,
            "successful_responses": self.quality_metrics.successful_responses,
            "success_rate": success_rate,
            "hybrid_search_usage": self.quality_metrics.hybrid_search_usage,
            "hybrid_usage_rate": hybrid_usage_rate,
            "citation_validations": self.quality_metrics.citation_validations,
            "avg_response_time": self.quality_metrics.avg_response_time,
            "avg_citation_precision": self.quality_metrics.avg_citation_precision,
            "high_quality_responses": self.quality_metrics.high_quality_responses,
            "high_quality_rate": high_quality_rate,
            "service_status": {
                "simple_rag": self.simple_rag is not None,
                "vector_service": self.vector_service is not None,
                "hybrid_search": self.hybrid_search_enabled,
                "citation_checker": self.citation_validation_enabled,
                "fallback_enabled": self.fallback_enabled
            }
        }
    
    async def batch_enhance_responses(self, queries: List[Dict[str, Any]]) -> List[EnhancedRAGResult]:
        """Process multiple queries with enhanced RAG"""
        
        results = []
        
        for query_data in queries:
            try:
                result = await self.enhanced_retrieve_and_generate(
                    query=query_data.get('query', ''),
                    personality=query_data.get('personality'),
                    context=query_data.get('context'),
                    enable_citation_validation=query_data.get('validate_citations', True)
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Batch processing failed for query: {e}")
                
                # Add error result
                error_result = EnhancedRAGResult(
                    response_text="Error processing query",
                    citations=[],
                    search_method="error",
                    retrieval_score=0.0,
                    citation_precision=0.0,
                    confidence_level="error",
                    hallucination_risk="high",
                    response_time=0.0,
                    metadata={'error': str(e)}
                )
                results.append(error_result)
        
        return results

# Global instance for easy import
enhanced_rag_service = EnhancedRAGService()
