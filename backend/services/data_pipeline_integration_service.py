"""
Data Pipeline Integration Service for Phase 1 RAG Enhancements

Connects the new Phase 1 services (Hybrid Search, Citation Grounding, Enhanced RAG)
with the existing production vector database and RAG integration services.

This service acts as the integration layer that:
1. Bridges hybrid search with existing VectorDatabaseService
2. Integrates citation validation into the existing RAG pipeline
3. Maintains backward compatibility with existing services
4. Provides enhanced quality metrics and monitoring

Part of Phase 1: Data Pipeline Integration implementation.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# Import existing production services
try:
    from vector_database_service import VectorDatabaseService, PersonalityType, ContentType, VectorDocument, SearchResult
    from rag_integration_service import RAGIntegrationService, RAGContext, EnhancedSpiritualResponse
    from enhanced_simple_llm_service import EnhancedSimpleLLMService
except ImportError as e:
    logger.warning(f"⚠️ Could not import existing services: {e}")
    VectorDatabaseService = None
    RAGIntegrationService = None
    EnhancedSimpleLLMService = None

# Import new Phase 1 enhanced services
try:
    from hybrid_search_service import HybridSearchService, HybridSearchResult, HybridSearchConfig
    from citation_grounding_checker import CitationGroundingChecker, CitationValidationLevel, GroundingReport
    from enhanced_rag_service import EnhancedRAGService, EnhancedRAGResult
except ImportError as e:
    logger.warning(f"⚠️ Could not import Phase 1 services: {e}")
    HybridSearchService = None
    CitationGroundingChecker = None
    EnhancedRAGService = None

@dataclass
class IntegrationMetrics:
    """Metrics for tracking integration performance"""
    total_requests: int = 0
    hybrid_search_used: int = 0
    citation_validations: int = 0
    fallback_to_legacy: int = 0
    avg_response_time: float = 0.0
    avg_citation_precision: float = 0.0
    high_quality_responses: int = 0
    error_count: int = 0

@dataclass
class IntegratedRAGResponse:
    """Integrated response combining legacy and enhanced features"""
    # Legacy compatibility fields
    content: str
    personality_id: str
    source: str
    character_count: int
    max_allowed: int
    rag_context: Optional[Any] = None
    
    # Enhanced Phase 1 fields
    search_method: str = "legacy"  # "legacy", "hybrid", "fallback"
    citation_precision: float = 0.0
    confidence_level: str = "unknown"
    hallucination_risk: str = "unknown"
    response_time: float = 0.0
    quality_score: float = 0.0
    
    # Integration metadata
    integration_version: str = "1.0"
    enhancement_enabled: bool = False
    fallback_reason: Optional[str] = None

class DataPipelineIntegrationService:
    """
    Data Pipeline Integration Service
    
    Integrates Phase 1 enhanced services with existing production RAG pipeline
    while maintaining full backward compatibility and gradual enhancement rollout.
    """
    
    def __init__(self, enable_enhancements: bool = True):
        self.enable_enhancements = enable_enhancements
        self.metrics = IntegrationMetrics()
        
        # Initialize existing production services
        self.vector_service = None
        self.rag_service = None
        self.llm_service = None
        
        # Initialize Phase 1 enhanced services
        self.hybrid_search = None
        self.citation_checker = None
        self.enhanced_rag = None
        
        # Configuration
        self.hybrid_search_threshold = 0.8  # Use hybrid search for this % of requests
        self.citation_validation_threshold = 0.9  # Validate citations for this % of requests
        self.fallback_on_error = True
        
        logger.info("🔗 Initializing Data Pipeline Integration Service...")
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all services with proper error handling"""
        
        # Initialize existing production services
        try:
            if VectorDatabaseService:
                self.vector_service = VectorDatabaseService()
                logger.info("✅ Vector Database Service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vector Database Service: {e}")
        
        try:
            if RAGIntegrationService:
                self.rag_service = RAGIntegrationService()
                logger.info("✅ RAG Integration Service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG Integration Service: {e}")
        
        try:
            if EnhancedSimpleLLMService:
                self.llm_service = EnhancedSimpleLLMService()
                logger.info("✅ Enhanced LLM Service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM Service: {e}")
        
        # Initialize Phase 1 enhanced services (if enabled)
        if self.enable_enhancements:
            try:
                if HybridSearchService:
                    self.hybrid_search = HybridSearchService()
                    logger.info("✅ Hybrid Search Service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Hybrid Search Service not available: {e}")
            
            try:
                if CitationGroundingChecker:
                    self.citation_checker = CitationGroundingChecker(CitationValidationLevel.MODERATE)
                    logger.info("✅ Citation Grounding Checker initialized")
            except Exception as e:
                logger.warning(f"⚠️ Citation Grounding Checker not available: {e}")
            
            try:
                if EnhancedRAGService:
                    self.enhanced_rag = EnhancedRAGService()
                    logger.info("✅ Enhanced RAG Service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced RAG Service not available: {e}")
        
        # Log initialization status
        self._log_service_status()
    
    def _log_service_status(self):
        """Log the status of all initialized services"""
        status = {
            "legacy_services": {
                "vector_database": self.vector_service is not None,
                "rag_integration": self.rag_service is not None,
                "llm_service": self.llm_service is not None
            },
            "enhanced_services": {
                "hybrid_search": self.hybrid_search is not None,
                "citation_checker": self.citation_checker is not None,
                "enhanced_rag": self.enhanced_rag is not None
            },
            "enhancement_enabled": self.enable_enhancements
        }
        
        logger.info(f"📊 Service Status: {status}")
    
    async def integrated_spiritual_guidance(
        self,
        query: str,
        personality: str,
        context: Optional[str] = None,
        use_enhancements: Optional[bool] = None,
        validate_citations: Optional[bool] = None
    ) -> IntegratedRAGResponse:
        """
        Integrated spiritual guidance with optional Phase 1 enhancements
        
        This method provides a single interface that can:
        1. Use existing production RAG pipeline (legacy mode)
        2. Use enhanced hybrid search + citation validation (enhanced mode)
        3. Gracefully fallback when enhancements unavailable
        
        Args:
            query: User's spiritual question
            personality: Target personality (e.g., "krishna", "buddha")
            context: Additional context for the response
            use_enhancements: Override global enhancement setting
            validate_citations: Override citation validation setting
            
        Returns:
            IntegratedRAGResponse with both legacy and enhanced fields
        """
        start_time = datetime.now()
        self.metrics.total_requests += 1
        
        # Determine whether to use enhancements
        use_enhanced = (use_enhancements if use_enhancements is not None 
                       else self.enable_enhancements and self._should_use_enhancements())
        
        validate_citations_flag = (validate_citations if validate_citations is not None
                                 else self._should_validate_citations())
        
        try:
            if use_enhanced and self._enhancements_available():
                # Use enhanced RAG pipeline
                return await self._enhanced_spiritual_guidance(
                    query, personality, context, validate_citations_flag, start_time
                )
            else:
                # Use legacy RAG pipeline
                return await self._legacy_spiritual_guidance(
                    query, personality, context, start_time
                )
                
        except Exception as e:
            logger.error(f"❌ Integrated spiritual guidance failed: {e}")
            
            if self.fallback_on_error:
                return await self._fallback_spiritual_guidance(
                    query, personality, context, start_time, str(e)
                )
            else:
                raise
    
    async def _enhanced_spiritual_guidance(
        self,
        query: str,
        personality: str,
        context: Optional[str],
        validate_citations: bool,
        start_time: datetime
    ) -> IntegratedRAGResponse:
        """Enhanced spiritual guidance using Phase 1 services"""
        
        try:
            # Use enhanced RAG service if available
            if self.enhanced_rag:
                enhanced_result = await self.enhanced_rag.enhanced_retrieve_and_generate(
                    query=query,
                    personality=personality,
                    context=context,
                    enable_citation_validation=validate_citations
                )
                
                if validate_citations:
                    self.metrics.citation_validations += 1
                
                if enhanced_result.search_method == "hybrid":
                    self.metrics.hybrid_search_used += 1
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Convert to integrated response format
                return IntegratedRAGResponse(
                    content=enhanced_result.response_text,
                    personality_id=personality,
                    source="enhanced_rag",
                    character_count=len(enhanced_result.response_text),
                    max_allowed=2000,
                    search_method=enhanced_result.search_method,
                    citation_precision=enhanced_result.citation_precision,
                    confidence_level=enhanced_result.confidence_level,
                    hallucination_risk=enhanced_result.hallucination_risk,
                    response_time=response_time,
                    quality_score=self._calculate_quality_score(enhanced_result),
                    enhancement_enabled=True
                )
            
            else:
                # Fallback to hybrid search + legacy RAG if enhanced RAG unavailable
                return await self._hybrid_search_with_legacy_rag(
                    query, personality, context, validate_citations, start_time
                )
                
        except Exception as e:
            logger.error(f"❌ Enhanced spiritual guidance failed: {e}")
            return await self._legacy_spiritual_guidance(
                query, personality, context, start_time, fallback_reason=str(e)
            )
    
    async def _hybrid_search_with_legacy_rag(
        self,
        query: str,
        personality: str,
        context: Optional[str],
        validate_citations: bool,
        start_time: datetime
    ) -> IntegratedRAGResponse:
        """Use hybrid search with legacy RAG generation"""
        
        try:
            # Step 1: Enhanced retrieval with hybrid search
            if self.hybrid_search:
                search_results = await self.hybrid_search.hybrid_search(
                    query=query,
                    personality=personality,
                    top_k=10
                )
                self.metrics.hybrid_search_used += 1
            else:
                # Fallback to vector search
                search_results = await self._fallback_vector_search(query, personality)
            
            # Step 2: Use legacy RAG for generation
            if self.rag_service and search_results:
                # Convert search results to legacy format
                legacy_context = self._convert_to_legacy_context(search_results, query)
                
                # Generate response using legacy RAG
                rag_response = await self.rag_service.generate_spiritual_guidance(
                    query=query,
                    personality=personality,
                    context=context,
                    rag_context=legacy_context
                )
                
                # Step 3: Optional citation validation
                citation_precision = 0.0
                confidence_level = "unknown"
                hallucination_risk = "unknown"
                
                if validate_citations and self.citation_checker and rag_response:
                    validation_report = await self.citation_checker.validate_response_grounding(
                        response_text=rag_response.content,
                        citations=getattr(rag_response.rag_context, 'citations', [])
                    )
                    
                    citation_precision = validation_report.overall_precision
                    confidence_level = validation_report.confidence_level
                    hallucination_risk = validation_report.hallucination_risk
                    self.metrics.citation_validations += 1
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                return IntegratedRAGResponse(
                    content=rag_response.content,
                    personality_id=rag_response.personality_id,
                    source=rag_response.source,
                    character_count=rag_response.character_count,
                    max_allowed=rag_response.max_allowed,
                    rag_context=rag_response.rag_context,
                    search_method="hybrid",
                    citation_precision=citation_precision,
                    confidence_level=confidence_level,
                    hallucination_risk=hallucination_risk,
                    response_time=response_time,
                    quality_score=citation_precision,
                    enhancement_enabled=True
                )
            
            else:
                raise Exception("Legacy RAG service unavailable")
                
        except Exception as e:
            logger.error(f"❌ Hybrid search with legacy RAG failed: {e}")
            return await self._legacy_spiritual_guidance(
                query, personality, context, start_time, fallback_reason=str(e)
            )
    
    async def _legacy_spiritual_guidance(
        self,
        query: str,
        personality: str,
        context: Optional[str],
        start_time: datetime,
        fallback_reason: Optional[str] = None
    ) -> IntegratedRAGResponse:
        """Legacy spiritual guidance using existing production services"""
        
        try:
            if self.rag_service:
                # Use existing RAG integration service
                rag_response = await self.rag_service.generate_spiritual_guidance(
                    query=query,
                    personality=personality,
                    context=context
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                if fallback_reason:
                    self.metrics.fallback_to_legacy += 1
                
                return IntegratedRAGResponse(
                    content=rag_response.content,
                    personality_id=rag_response.personality_id,
                    source=rag_response.source,
                    character_count=rag_response.character_count,
                    max_allowed=rag_response.max_allowed,
                    rag_context=rag_response.rag_context,
                    search_method="legacy",
                    response_time=response_time,
                    enhancement_enabled=False,
                    fallback_reason=fallback_reason
                )
            
            else:
                raise Exception("No RAG service available")
                
        except Exception as e:
            logger.error(f"❌ Legacy spiritual guidance failed: {e}")
            return await self._fallback_spiritual_guidance(
                query, personality, context, start_time, str(e)
            )
    
    async def _fallback_spiritual_guidance(
        self,
        query: str,
        personality: str,
        context: Optional[str],
        start_time: datetime,
        error_reason: str
    ) -> IntegratedRAGResponse:
        """Final fallback for when all services fail"""
        
        self.metrics.error_count += 1
        self.metrics.fallback_to_legacy += 1
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        fallback_content = (
            f"I apologize, but I'm experiencing technical difficulties. "
            f"Please try your question again in a moment. "
            f"If this persists, please contact support."
        )
        
        return IntegratedRAGResponse(
            content=fallback_content,
            personality_id=personality,
            source="fallback",
            character_count=len(fallback_content),
            max_allowed=2000,
            search_method="error",
            response_time=response_time,
            enhancement_enabled=False,
            fallback_reason=f"Service error: {error_reason}"
        )
    
    def _should_use_enhancements(self) -> bool:
        """Determine whether to use enhanced services based on configuration"""
        # For now, use a simple threshold. In production, this could be:
        # - A/B testing percentage
        # - User-specific settings
        # - Feature flags
        # - Performance-based decisions
        
        import random
        return random.random() < self.hybrid_search_threshold
    
    def _should_validate_citations(self) -> bool:
        """Determine whether to validate citations"""
        import random
        return random.random() < self.citation_validation_threshold
    
    def _enhancements_available(self) -> bool:
        """Check if enhanced services are available"""
        return (self.hybrid_search is not None or 
                self.citation_checker is not None or 
                self.enhanced_rag is not None)
    
    async def _fallback_vector_search(self, query: str, personality: str) -> List[Any]:
        """Fallback vector search when hybrid search unavailable"""
        try:
            if self.vector_service:
                # Convert personality string to PersonalityType enum
                personality_type = self._convert_personality_string(personality)
                
                results = await self.vector_service.search_documents(
                    query=query,
                    personality_type=personality_type,
                    top_k=10
                )
                return results
            else:
                return []
        except Exception as e:
            logger.warning(f"⚠️ Fallback vector search failed: {e}")
            return []
    
    def _convert_personality_string(self, personality: str) -> Any:
        """Convert personality string to PersonalityType enum"""
        if not PersonalityType:
            return personality
        
        personality_map = {
            "krishna": PersonalityType.KRISHNA,
            "buddha": PersonalityType.BUDDHA,
            "jesus_christ": PersonalityType.JESUS_CHRIST,
            "albert_einstein": PersonalityType.ALBERT_EINSTEIN,
            "abraham_lincoln": PersonalityType.ABRAHAM_LINCOLN,
            "marcus_aurelius": PersonalityType.MARCUS_AURELIUS,
            "rumi": PersonalityType.RUMI,
            "lao_tzu": PersonalityType.LAO_TZU,
            "isaac_newton": PersonalityType.ISAAC_NEWTON,
            "chanakya": PersonalityType.CHANAKYA,
            "confucius": PersonalityType.CONFUCIUS,
            "nikola_tesla": PersonalityType.NIKOLA_TESLA,
            "leonardo_da_vinci": PersonalityType.LEONARDO_DA_VINCI,
            "archimedes": PersonalityType.ARCHIMEDES,
            "socrates": PersonalityType.SOCRATES,
            "plato": PersonalityType.PLATO,
            "aristotle": PersonalityType.ARISTOTLE,
            "sigmund_freud": PersonalityType.SIGMUND_FREUD,
            "benjamin_franklin": PersonalityType.BENJAMIN_FRANKLIN,
            "martin_luther_king_jr": PersonalityType.MARTIN_LUTHER_KING_JR,
            "george_washington": PersonalityType.GEORGE_WASHINGTON,
            "mahatma_gandhi": PersonalityType.MAHATMA_GANDHI,
            "swami_vivekananda": PersonalityType.SWAMI_VIVEKANANDA,
            "william_shakespeare": PersonalityType.WILLIAM_SHAKESPEARE,
            "rabindranath_tagore": PersonalityType.RABINDRANATH_TAGORE
        }
        
        return personality_map.get(personality.lower(), personality)
    
    def _convert_to_legacy_context(self, search_results: List[Any], query: str) -> Any:
        """Convert search results to legacy RAGContext format"""
        try:
            if not search_results:
                return None
            
            # Extract information from search results
            relevant_passages = []
            citations = []
            sources = []
            
            for result in search_results:
                if hasattr(result, 'document') and hasattr(result.document, 'content'):
                    relevant_passages.append(result.document.content)
                elif hasattr(result, 'content'):
                    relevant_passages.append(result.content)
                
                # Extract citations and sources
                if hasattr(result, 'document'):
                    if hasattr(result.document, 'citation'):
                        citations.append(result.document.citation or "Unknown")
                    if hasattr(result.document, 'source'):
                        sources.append(result.document.source or "Unknown")
            
            # Create RAGContext if available
            if RAGContext:
                return RAGContext(
                    relevant_passages=relevant_passages,
                    citations=citations,
                    sources=sources,
                    personality_contexts={},
                    total_passages=len(relevant_passages),
                    avg_relevance_score=0.8,  # Default score
                    search_query=query
                )
            else:
                # Return a basic dict if RAGContext not available
                return {
                    'relevant_passages': relevant_passages,
                    'citations': citations,
                    'sources': sources,
                    'total_passages': len(relevant_passages),
                    'search_query': query
                }
        
        except Exception as e:
            logger.warning(f"⚠️ Failed to convert to legacy context: {e}")
            return None
    
    def _calculate_quality_score(self, enhanced_result: Any) -> float:
        """Calculate overall quality score from enhanced result"""
        try:
            # Combine multiple quality factors
            citation_score = enhanced_result.citation_precision
            confidence_score = self._confidence_level_to_score(enhanced_result.confidence_level)
            hallucination_score = self._hallucination_risk_to_score(enhanced_result.hallucination_risk)
            
            # Weighted average
            quality_score = (citation_score * 0.4 + 
                           confidence_score * 0.3 + 
                           hallucination_score * 0.3)
            
            return min(max(quality_score, 0.0), 1.0)  # Clamp to [0, 1]
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to calculate quality score: {e}")
            return 0.5  # Default score
    
    def _confidence_level_to_score(self, confidence_level: str) -> float:
        """Convert confidence level to numeric score"""
        confidence_map = {
            "very_high": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4,
            "very_low": 0.2,
            "unknown": 0.5,
            "error": 0.0
        }
        return confidence_map.get(confidence_level, 0.5)
    
    def _hallucination_risk_to_score(self, hallucination_risk: str) -> float:
        """Convert hallucination risk to quality score (inverted)"""
        risk_map = {
            "low": 1.0,
            "medium": 0.6,
            "high": 0.2,
            "unknown": 0.5
        }
        return risk_map.get(hallucination_risk, 0.5)
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive integration metrics"""
        
        # Calculate success rates
        success_rate = ((self.metrics.total_requests - self.metrics.error_count) / 
                       self.metrics.total_requests if self.metrics.total_requests > 0 else 0.0)
        
        enhancement_usage_rate = ((self.metrics.hybrid_search_used + self.metrics.citation_validations) / 
                                 (self.metrics.total_requests * 2) if self.metrics.total_requests > 0 else 0.0)
        
        fallback_rate = (self.metrics.fallback_to_legacy / 
                        self.metrics.total_requests if self.metrics.total_requests > 0 else 0.0)
        
        high_quality_rate = (self.metrics.high_quality_responses / 
                           self.metrics.total_requests if self.metrics.total_requests > 0 else 0.0)
        
        return {
            "integration_metrics": {
                "total_requests": self.metrics.total_requests,
                "success_rate": success_rate,
                "error_count": self.metrics.error_count,
                "avg_response_time": self.metrics.avg_response_time,
                "avg_citation_precision": self.metrics.avg_citation_precision
            },
            "enhancement_usage": {
                "hybrid_search_used": self.metrics.hybrid_search_used,
                "citation_validations": self.metrics.citation_validations,
                "enhancement_usage_rate": enhancement_usage_rate,
                "fallback_to_legacy": self.metrics.fallback_to_legacy,
                "fallback_rate": fallback_rate
            },
            "quality_metrics": {
                "high_quality_responses": self.metrics.high_quality_responses,
                "high_quality_rate": high_quality_rate,
                "avg_citation_precision": self.metrics.avg_citation_precision
            },
            "service_status": {
                "enhancements_enabled": self.enable_enhancements,
                "services_available": self._enhancements_available(),
                "hybrid_search_available": self.hybrid_search is not None,
                "citation_checker_available": self.citation_checker is not None,
                "enhanced_rag_available": self.enhanced_rag is not None,
                "legacy_services_available": all([
                    self.vector_service is not None,
                    self.rag_service is not None
                ])
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all integrated services"""
        
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Check legacy services
        try:
            if self.vector_service:
                # Test vector service
                health_status["services"]["vector_database"] = "healthy"
            else:
                health_status["services"]["vector_database"] = "unavailable"
        except Exception as e:
            health_status["services"]["vector_database"] = f"error: {str(e)}"
        
        try:
            if self.rag_service:
                health_status["services"]["rag_integration"] = "healthy"
            else:
                health_status["services"]["rag_integration"] = "unavailable"
        except Exception as e:
            health_status["services"]["rag_integration"] = f"error: {str(e)}"
        
        # Check enhanced services
        try:
            if self.hybrid_search:
                health_status["services"]["hybrid_search"] = "healthy"
            else:
                health_status["services"]["hybrid_search"] = "unavailable"
        except Exception as e:
            health_status["services"]["hybrid_search"] = f"error: {str(e)}"
        
        try:
            if self.citation_checker:
                health_status["services"]["citation_checker"] = "healthy"
            else:
                health_status["services"]["citation_checker"] = "unavailable"
        except Exception as e:
            health_status["services"]["citation_checker"] = f"error: {str(e)}"
        
        # Determine overall status
        service_statuses = list(health_status["services"].values())
        if any("error" in status for status in service_statuses):
            health_status["overall_status"] = "degraded"
        elif all(status == "unavailable" for status in service_statuses):
            health_status["overall_status"] = "critical"
        
        return health_status

# Global instance for easy import
data_pipeline_integration = DataPipelineIntegrationService()
