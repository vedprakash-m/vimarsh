"""
RAG Integration Service for Multi-Personality Spiritual Guidance

Integrates vector database search with LLM generation to provide context-aware
spiritual guidance with proper citations and personality-specific responses.
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from vector_database_service import VectorDatabaseService, PersonalityType, ContentType, SearchResult
    from enhanced_simple_llm_service import EnhancedSimpleLLMService, SpiritualResponse
except ImportError:
    # Handle import issues gracefully
    logging.warning("⚠️ Could not import vector database or LLM services")
    VectorDatabaseService = None
    PersonalityType = None
    ContentType = None
    SearchResult = None
    EnhancedSimpleLLMService = None
    SpiritualResponse = None

logger = logging.getLogger(__name__)

@dataclass
class RAGContext:
    """Context retrieved from vector database for RAG"""
    relevant_passages: List[str]
    citations: List[str]
    sources: List[str]
    personality_contexts: Dict[str, List[str]]
    total_passages: int
    avg_relevance_score: float
    search_query: str
    retrieved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class EnhancedSpiritualResponse:
    """Enhanced spiritual response with RAG context"""
    content: str
    personality_id: str
    source: str
    character_count: int
    max_allowed: int
    rag_context: Optional[RAGContext] = None
    has_rag_context: bool = False
    context_relevance_score: float = 0.0
    citations_included: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class RAGIntegrationService:
    """Service that integrates vector search with LLM generation"""
    
    def __init__(self):
        self.vector_db = VectorDatabaseService() if VectorDatabaseService else None
        self.llm_service = EnhancedSimpleLLMService() if EnhancedSimpleLLMService else None
        self.is_available = self.vector_db is not None and self.llm_service is not None
        
        if not self.is_available:
            logger.warning("⚠️ RAG Integration Service not fully available - missing dependencies")
        else:
            logger.info("✅ RAG Integration Service initialized successfully")
    
    async def generate_rag_enhanced_response(
        self,
        query: str,
        personality_id: str,
        language: str = "English",
        context_limit: int = 3,
        min_relevance: float = 0.3,
        include_cross_personality: bool = False
    ) -> EnhancedSpiritualResponse:
        """Generate spiritually-guided response enhanced with RAG context"""
        
        if not self.is_available:
            logger.warning("⚠️ RAG service not available, falling back to basic LLM")
            return await self._fallback_response(query, personality_id)
        
        try:
            # Step 1: Retrieve relevant context from vector database
            rag_context = await self._retrieve_spiritual_context(
                query=query,
                personality_id=personality_id,
                context_limit=context_limit,
                min_relevance=min_relevance,
                include_cross_personality=include_cross_personality
            )
            
            # Step 2: Generate enhanced prompt with context
            enhanced_prompt = self._create_rag_enhanced_prompt(
                query=query,
                personality_id=personality_id,
                rag_context=rag_context,
                language=language
            )
            
            # Step 3: Generate LLM response with enhanced context
            llm_response = await self._generate_contextual_response(
                enhanced_prompt=enhanced_prompt,
                personality_id=personality_id,
                rag_context=rag_context
            )
            
            # Step 4: Post-process response with citations
            final_response = self._add_citations_to_response(
                llm_response=llm_response,
                rag_context=rag_context,
                personality_id=personality_id
            )
            
            logger.info(f"✅ RAG-enhanced response generated: {len(final_response.content)} chars, "
                       f"{len(final_response.citations_included)} citations")
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ RAG enhancement failed: {e}")
            return await self._fallback_response(query, personality_id)
    
    async def _retrieve_spiritual_context(
        self,
        query: str,
        personality_id: str,
        context_limit: int,
        min_relevance: float,
        include_cross_personality: bool
    ) -> RAGContext:
        """Retrieve relevant spiritual context from vector database"""
        
        try:
            # Convert personality string to enum
            personality_enum = PersonalityType(personality_id)
            
            # Primary search: Same personality
            primary_results = await self.vector_db.semantic_search(
                query=query,
                personality=personality_enum,
                content_types=None,  # All content types
                top_k=context_limit,
                min_relevance=min_relevance
            )
            
            all_results = primary_results
            
            # Secondary search: Cross-personality if enabled and primary results are insufficient
            if include_cross_personality and len(primary_results) < context_limit:
                remaining_slots = context_limit - len(primary_results)
                
                cross_personality_results = await self.vector_db.semantic_search(
                    query=query,
                    personality=None,  # Search all personalities
                    content_types=None,
                    top_k=remaining_slots * 2,  # Get more to filter out same personality
                    min_relevance=min_relevance * 0.8  # Slightly lower threshold
                )
                
                # Filter out same personality results
                filtered_cross_results = [
                    result for result in cross_personality_results
                    if result.document.personality != personality_enum
                ][:remaining_slots]
                
                all_results.extend(filtered_cross_results)
            
            # Extract context information
            relevant_passages = []
            citations = []
            sources = []
            personality_contexts = {}
            
            for result in all_results:
                doc = result.document
                
                # Add passage content
                relevant_passages.append(doc.content)
                
                # Add citation
                if doc.citation:
                    citations.append(doc.citation)
                elif doc.verse and doc.source:
                    citations.append(f"{doc.source} {doc.verse}")
                else:
                    citations.append(f"{doc.source}")
                
                # Add source
                sources.append(doc.source)
                
                # Group by personality
                personality_key = doc.personality.value
                if personality_key not in personality_contexts:
                    personality_contexts[personality_key] = []
                personality_contexts[personality_key].append(doc.content[:200])
            
            # Calculate average relevance
            avg_relevance = (
                sum(result.relevance_score for result in all_results) / len(all_results)
                if all_results else 0.0
            )
            
            context = RAGContext(
                relevant_passages=relevant_passages,
                citations=citations,
                sources=sources,
                personality_contexts=personality_contexts,
                total_passages=len(relevant_passages),
                avg_relevance_score=avg_relevance,
                search_query=query
            )
            
            logger.info(f"🔍 Retrieved {len(relevant_passages)} relevant passages "
                       f"(avg relevance: {avg_relevance:.3f})")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Context retrieval failed: {e}")
            return RAGContext(
                relevant_passages=[],
                citations=[],
                sources=[],
                personality_contexts={},
                total_passages=0,
                avg_relevance_score=0.0,
                search_query=query
            )
    
    def _create_rag_enhanced_prompt(
        self,
        query: str,
        personality_id: str,
        rag_context: RAGContext,
        language: str
    ) -> str:
        """Create enhanced prompt with RAG context"""
        
        # Get personality-specific prompt template
        personality_prompts = {
            "krishna": "You are Lord Krishna, the divine teacher of the Bhagavad Gita. Respond with compassion, wisdom, and divine love.",
            "buddha": "You are Buddha, the Enlightened One. Respond with mindfulness, compassion, and teachings on the path to liberation.",
            "jesus": "You are Jesus Christ. Respond with love, forgiveness, and teachings about salvation and divine grace.",
            "einstein": "You are Albert Einstein. Respond with scientific wisdom, curiosity, and insights about the universe.",
            "lincoln": "You are Abraham Lincoln. Respond with wisdom about leadership, unity, and moral courage.",
            "marcus_aurelius": "You are Marcus Aurelius. Respond with Stoic wisdom about virtue, duty, and inner strength.",
            "rumi": "You are Rumi, the mystical poet. Respond with love, spiritual poetry, and insights about divine union.",
            "lao_tzu": "You are Lao Tzu. Respond with Taoist wisdom about the natural way and effortless action.",
            "newton": "You are Isaac Newton. Respond with scientific methodology and insights about natural laws.",
            "chanakya": "You are Chanakya. Respond with strategic wisdom about governance and practical philosophy.",
            "confucius": "You are Confucius. Respond with wisdom about virtue, proper conduct, and social harmony.",
            "tesla": "You are Nikola Tesla. Respond with visionary insights about innovation and the future."
        }
        
        base_prompt = personality_prompts.get(personality_id, personality_prompts["krishna"])
        
        # Add context if available
        if rag_context.total_passages > 0:
            context_section = "\n\nRELEVANT SPIRITUAL CONTEXT:\n"
            for i, (passage, citation) in enumerate(zip(
                rag_context.relevant_passages[:3],  # Limit to top 3
                rag_context.citations[:3]
            )):
                context_section += f"\n[Context {i+1}] From {citation}:\n{passage[:300]}...\n"
            
            enhanced_prompt = f"""{base_prompt}

{context_section}

IMPORTANT INSTRUCTIONS:
- Draw wisdom from the provided spiritual context when relevant
- Include specific citations when referencing the sacred texts
- Maintain your authentic voice and personality
- Provide practical, compassionate guidance
- Keep response under 800 characters for optimal readability

USER QUESTION: {query}

Response (with citations when referencing texts):"""
        else:
            # Fallback without context
            enhanced_prompt = f"""{base_prompt}

USER QUESTION: {query}

Response:"""
        
        return enhanced_prompt
    
    async def _generate_contextual_response(
        self,
        enhanced_prompt: str,
        personality_id: str,
        rag_context: RAGContext
    ) -> Any:
        """Generate LLM response with enhanced context"""
        
        try:
            # Use the existing LLM service but with our enhanced prompt
            # We'll temporarily override the prompt template
            original_template = None
            if hasattr(self.llm_service, 'personalities') and personality_id in self.llm_service.personalities:
                original_template = self.llm_service.personalities[personality_id].prompt_template
                self.llm_service.personalities[personality_id].prompt_template = enhanced_prompt
            
            # Generate response
            response = await self.llm_service.generate_personality_response(
                query="",  # Query is already in the enhanced prompt
                personality_id=personality_id
            )
            
            # Restore original template
            if original_template and hasattr(self.llm_service, 'personalities'):
                self.llm_service.personalities[personality_id].prompt_template = original_template
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Contextual response generation failed: {e}")
            # Fallback to basic LLM service
            return await self.llm_service.generate_personality_response(
                query=enhanced_prompt.split("USER QUESTION:")[-1].split("Response")[0].strip(),
                personality_id=personality_id
            )
    
    def _add_citations_to_response(
        self,
        llm_response: Any,
        rag_context: RAGContext,
        personality_id: str
    ) -> EnhancedSpiritualResponse:
        """Add proper citations to the LLM response"""
        
        content = llm_response.content
        citations_included = []
        
        # Extract citations that are likely referenced in the response
        for citation in rag_context.citations:
            # Simple heuristic: if response mentions key terms from citation
            citation_terms = citation.lower().split()
            content_lower = content.lower()
            
            # Check if citation terms appear in response
            if any(term in content_lower for term in citation_terms if len(term) > 3):
                citations_included.append(citation)
        
        # If no automatic citations detected but we have context, add a general reference
        if not citations_included and rag_context.total_passages > 0:
            unique_sources = list(set(rag_context.sources))
            if len(unique_sources) == 1:
                citations_included = [f"Referenced from {unique_sources[0]}"]
            else:
                citations_included = [f"Referenced from {', '.join(unique_sources[:2])}"]
        
        # Create enhanced response
        enhanced_response = EnhancedSpiritualResponse(
            content=content,
            personality_id=personality_id,
            source=f"rag_enhanced_{llm_response.source}",
            character_count=len(content),
            max_allowed=llm_response.max_allowed,
            rag_context=rag_context,
            has_rag_context=rag_context.total_passages > 0,
            context_relevance_score=rag_context.avg_relevance_score,
            citations_included=citations_included,
            metadata={
                **llm_response.metadata,
                "rag_enabled": True,
                "context_passages": rag_context.total_passages,
                "avg_relevance": rag_context.avg_relevance_score,
                "generation_method": "rag_enhanced"
            }
        )
        
        return enhanced_response
    
    async def _fallback_response(
        self,
        query: str,
        personality_id: str
    ) -> EnhancedSpiritualResponse:
        """Fallback response when RAG is not available"""
        
        try:
            if self.llm_service:
                basic_response = await self.llm_service.generate_personality_response(
                    query=query,
                    personality_id=personality_id
                )
                
                return EnhancedSpiritualResponse(
                    content=basic_response.content,
                    personality_id=personality_id,
                    source=f"fallback_{basic_response.source}",
                    character_count=len(basic_response.content),
                    max_allowed=basic_response.max_allowed,
                    rag_context=None,
                    has_rag_context=False,
                    context_relevance_score=0.0,
                    citations_included=[],
                    metadata={
                        **basic_response.metadata,
                        "rag_enabled": False,
                        "generation_method": "fallback_basic_llm"
                    }
                )
            else:
                # Ultimate fallback - hardcoded response
                fallback_content = "I apologize, but I cannot access my spiritual wisdom at this moment. Please try again later, and I will guide you with divine knowledge."
                
                return EnhancedSpiritualResponse(
                    content=fallback_content,
                    personality_id=personality_id,
                    source="hardcoded_fallback",
                    character_count=len(fallback_content),
                    max_allowed=800,
                    rag_context=None,
                    has_rag_context=False,
                    context_relevance_score=0.0,
                    citations_included=[],
                    metadata={
                        "rag_enabled": False,
                        "generation_method": "hardcoded_fallback"
                    }
                )
                
        except Exception as e:
            logger.error(f"❌ Fallback response failed: {e}")
            # Final emergency fallback
            emergency_content = "Divine guidance is temporarily unavailable. Please seek wisdom through meditation and self-reflection."
            
            return EnhancedSpiritualResponse(
                content=emergency_content,
                personality_id=personality_id,
                source="emergency_fallback",
                character_count=len(emergency_content),
                max_allowed=800,
                rag_context=None,
                has_rag_context=False,
                context_relevance_score=0.0,
                citations_included=[],
                metadata={
                    "rag_enabled": False,
                    "generation_method": "emergency_fallback",
                    "error": str(e)
                }
            )
    
    async def get_rag_health_status(self) -> Dict[str, Any]:
        """Get health status of RAG components"""
        
        try:
            vector_db_health = None
            llm_service_health = None
            
            if self.vector_db:
                stats = await self.vector_db.get_database_stats()
                vector_db_health = {
                    "available": True,
                    "total_documents": stats.total_documents,
                    "embedding_coverage": (
                        stats.total_embeddings_generated / stats.total_documents * 100
                        if stats.total_documents > 0 else 0
                    ),
                    "storage_size_mb": stats.storage_size_mb
                }
            else:
                vector_db_health = {"available": False, "error": "Service not initialized"}
            
            if self.llm_service and hasattr(self.llm_service, 'is_configured'):
                llm_service_health = {
                    "available": True,
                    "configured": self.llm_service.is_configured,
                    "model": "gemini-2.5-flash"
                }
            else:
                llm_service_health = {"available": False, "error": "Service not initialized"}
            
            overall_health = "healthy" if self.is_available else "degraded"
            
            return {
                "overall_status": overall_health,
                "rag_available": self.is_available,
                "vector_database": vector_db_health,
                "llm_service": llm_service_health,
                "last_checked": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ RAG health check failed: {e}")
            return {
                "overall_status": "error",
                "rag_available": False,
                "error": str(e),
                "last_checked": datetime.utcnow().isoformat()
            }
