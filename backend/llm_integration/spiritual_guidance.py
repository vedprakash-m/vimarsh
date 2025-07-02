"""
Spiritual Guidance Service - Combines LLM and RAG for spiritual guidance
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Robust import handling with graceful fallbacks
try:
    from .llm_service import LLMService, LLMResponse
    from ..rag_pipeline.rag_service import RAGService, RAGResponse
    from ..llm.gemini_client import SpiritualContext, SafetyLevel
except (ImportError, ValueError):
    # Fallback to absolute imports
    try:
        from llm_service import LLMService, LLMResponse
        from rag_pipeline.rag_service import RAGService, RAGResponse
        from llm.gemini_client import SpiritualContext, SafetyLevel
    except ImportError:
        # Final fallback - create mock classes
        class LLMService:
            def generate_response(self, *args, **kwargs): 
                return {"text": "Mock response", "citations": []}
        
        class LLMResponse:
            def __init__(self, text="", **kwargs):
                self.text = text
        
        class RAGService:
            def retrieve_context(self, *args, **kwargs): return []
        
        class RAGResponse:
            def __init__(self, text="", **kwargs):
                self.text = text
        
        class SpiritualContext:
            REVERENT = "reverent"
            GUIDANCE = "guidance"
        
        class SafetyLevel:
            HIGH = "high"
            MODERATE = "moderate"
            LOW = "low"

logger = logging.getLogger(__name__)


@dataclass
class SpiritualGuidanceResponse:
    """Response from spiritual guidance service"""
    query: str
    guidance: str
    relevant_sources: List[str]
    confidence_score: float
    metadata: Dict[str, Any]


class SpiritualGuidanceService:
    """
    Complete spiritual guidance service combining RAG and LLM.
    
    Provides contextual spiritual guidance by retrieving relevant
    spiritual texts and generating personalized responses.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize spiritual guidance service"""
        self.config = config or {}
        self.llm_service = LLMService(config.get('llm_config', {}))
        self.rag_service = RAGService(config.get('rag_config', {}))
        
    def provide_guidance(
        self,
        query: str,
        context: SpiritualContext = SpiritualContext.GUIDANCE,
        safety_level: SafetyLevel = SafetyLevel.MODERATE
    ) -> SpiritualGuidanceResponse:
        """
        Provide spiritual guidance for a query.
        
        Args:
            query: The spiritual question or topic
            context: Type of spiritual context
            safety_level: Safety level for response generation
            
        Returns:
            SpiritualGuidanceResponse with guidance and sources
        """
        try:
            # First, retrieve relevant spiritual texts
            rag_response = self.rag_service.search(
                query=query,
                top_k=3,
                similarity_threshold=0.7
            )
            
            # Build context from retrieved sources
            sources_context = []
            for chunk in rag_response.results:
                if hasattr(chunk, 'content'):
                    sources_context.append(chunk.content)
                elif isinstance(chunk, str):
                    sources_context.append(chunk)
            
            # Create enhanced prompt with context
            enhanced_prompt = self._build_guidance_prompt(
                query, sources_context, context
            )
            
            # Generate guidance using LLM
            llm_response = self.llm_service.generate_response(
                prompt=enhanced_prompt,
                context=context,
                safety_level=safety_level
            )
            
            return SpiritualGuidanceResponse(
                query=query,
                guidance=llm_response.content,
                relevant_sources=sources_context,
                confidence_score=self._calculate_confidence(
                    rag_response, llm_response
                ),
                metadata={
                    'rag_results_count': len(rag_response.results),
                    'relevance_scores': rag_response.relevance_scores,
                    'llm_metadata': llm_response.metadata,
                    'context': context.value,
                    'safety_level': safety_level.value
                }
            )
            
        except Exception as e:
            logger.error(f"Spiritual guidance service error: {e}")
            raise
            
    def _build_guidance_prompt(
        self,
        query: str,
        sources: List[str],
        context: SpiritualContext
    ) -> str:
        """Build enhanced prompt with retrieved sources"""
        
        context_intro = {
            SpiritualContext.GUIDANCE: "Provide compassionate spiritual guidance",
            SpiritualContext.TEACHING: "Explain the spiritual teaching",
            SpiritualContext.PHILOSOPHY: "Discuss the philosophical aspects",
            SpiritualContext.DEVOTIONAL: "Guide devotional practice",
            SpiritualContext.MEDITATION: "Provide meditation guidance"
        }.get(context, "Respond to the spiritual inquiry")
        
        prompt = f"""
{context_intro} for the following question:

Question: {query}

Based on these relevant spiritual texts:
"""
        
        for i, source in enumerate(sources, 1):
            prompt += f"\n{i}. {source[:500]}..."
            
        prompt += f"""

Please provide a thoughtful, compassionate response that draws wisdom from these sources while addressing the specific question. Focus on practical guidance that can help the person on their spiritual journey.
"""
        
        return prompt
        
    def _calculate_confidence(
        self,
        rag_response: RAGResponse,
        llm_response: LLMResponse
    ) -> float:
        """Calculate confidence score for the guidance"""
        
        # Base confidence from RAG relevance
        if rag_response.relevance_scores:
            avg_relevance = sum(rag_response.relevance_scores) / len(rag_response.relevance_scores)
        else:
            avg_relevance = 0.5
            
        # Adjust for number of sources
        source_factor = min(len(rag_response.results) / 3, 1.0)
        
        # Combine factors
        confidence = (avg_relevance * 0.7) + (source_factor * 0.3)
        
        return min(confidence, 1.0)
        
    def is_healthy(self) -> bool:
        """Check if spiritual guidance service is healthy"""
        return (
            self.llm_service.is_healthy() and 
            self.rag_service.is_healthy()
        )
