"""
RAG Service - Phase 6b Implementation

This service provides basic RAG functionality using local JSON files
until the full vector database migration is complete. It provides:
- Content loading from existing JSON files
- Simple text matching for spiritual guidance
- Multi-personality content organization
- Basic citation support

This is an interim solution to enable RAG integration immediately
while the full vector database migration is being prepared.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class SpiritualContent:
    """Simple structure for spiritual content"""
    id: str
    personality: str
    content: str
    source: str
    verse: Optional[str] = None
    chapter: Optional[int] = None
    content_type: str = "teaching"
    citation: Optional[str] = None
    
    def get_citation(self) -> str:
        """Get proper citation for this content"""
        if self.citation:
            return self.citation
        elif self.verse and self.source:
            return f"{self.source} {self.verse}"
        else:
            return self.source

@dataclass
class RAGSearchResult:
    """Search result from RAG service"""
    content: SpiritualContent
    relevance_score: float
    match_type: str  # 'exact', 'partial', 'semantic'

@dataclass
class RAGResponse:
    """Complete RAG response with context"""
    response: str
    context_chunks: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    personality_used: str = "krishna"
    sources_consulted: List[str] = field(default_factory=list)
    total_context_length: int = 0

class SimpleRAGService:
    """Simple RAG service using local JSON files"""
    
    def __init__(self):
        self.content_by_personality: Dict[str, List[SpiritualContent]] = {}
        self.all_content: List[SpiritualContent] = []
        self.is_loaded = False
        
        # Personality mapping
        self.personality_sources = {
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
        
        # Load content on initialization
        self._load_content()
    
    def _load_content(self):
        """Load spiritual content from local JSON files"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sources")
            
            for personality, files in self.personality_sources.items():
                personality_content = []
                
                for filename in files:
                    file_path = os.path.join(data_dir, filename)
                    
                    if not os.path.exists(file_path):
                        logger.warning(f"File not found: {file_path}")
                        continue
                    
                    try:
                        if filename.endswith('.jsonl'):
                            # Handle JSONL files (like Bhagavad Gita)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        data = json.loads(line)
                                        content = self._create_content_from_data(data, personality)
                                        if content:
                                            personality_content.append(content)
                                            self.all_content.append(content)
                        
                        else:
                            # Handle JSON files
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                
                                if isinstance(data, list):
                                    for item in data:
                                        content = self._create_content_from_data(item, personality)
                                        if content:
                                            personality_content.append(content)
                                            self.all_content.append(content)
                                elif isinstance(data, dict):
                                    content = self._create_content_from_data(data, personality)
                                    if content:
                                        personality_content.append(content)
                                        self.all_content.append(content)
                    
                    except Exception as e:
                        logger.error(f"Error loading {filename}: {e}")
                
                self.content_by_personality[personality] = personality_content
                logger.info(f"Loaded {len(personality_content)} items for {personality}")
            
            self.is_loaded = True
            logger.info(f"Simple RAG service loaded {len(self.all_content)} total spiritual texts")
            
        except Exception as e:
            logger.error(f"Failed to load RAG content: {e}")
            self.is_loaded = False
    
    def _create_content_from_data(self, data: Dict[str, Any], personality: str) -> Optional[SpiritualContent]:
        """Create SpiritualContent from JSON data"""
        try:
            # Handle different data formats
            content_text = ""
            source = ""
            verse = None
            chapter = None
            citation = None
            content_type = "teaching"
            
            # Extract content based on data structure
            if 'content' in data:
                content_text = data['content']
            elif 'text' in data:
                content_text = data['text']
            elif 'translation' in data:
                content_text = data['translation']
            else:
                # Skip if no content found
                return None
            
            # Extract source information
            if 'scripture' in data:
                source = data['scripture']
            elif 'source' in data:
                source = data['source']
            else:
                source = f"{personality.title()} Teachings"
            
            # Extract verse/chapter information
            if 'verse' in data:
                verse = data['verse']
            if 'chapter' in data:
                chapter = data['chapter']
            
            # Create citation
            if verse:
                citation = f"{source} {verse}"
            elif chapter:
                citation = f"{source} Chapter {chapter}"
            else:
                citation = source
            
            # Determine content type
            if 'content_type' in data:
                content_type = data['content_type']
            
            return SpiritualContent(
                id=data.get('id', f"{personality}_{len(self.all_content)}"),
                personality=personality,
                content=content_text[:2000],  # Limit content length
                source=source,
                verse=verse,
                chapter=chapter,
                content_type=content_type,
                citation=citation
            )
            
        except Exception as e:
            logger.error(f"Error creating content from data: {e}")
            return None
    
    def search_content(
        self, 
        query: str, 
        personality: Optional[str] = None, 
        max_results: int = 5
    ) -> List[RAGSearchResult]:
        """Search for relevant content"""
        if not self.is_loaded:
            logger.warning("RAG service not loaded")
            return []
        
        query_lower = query.lower()
        results = []
        
        # Determine content to search
        if personality and personality in self.content_by_personality:
            search_content = self.content_by_personality[personality]
        else:
            search_content = self.all_content
        
        # Search through content
        for content in search_content:
            score = 0.0
            match_type = "none"
            
            content_lower = content.content.lower()
            
            # Exact phrase matching
            if query_lower in content_lower:
                score = 0.9
                match_type = "exact"
            else:
                # Word matching
                query_words = query_lower.split()
                content_words = content_lower.split()
                
                matches = 0
                for word in query_words:
                    if any(word in content_word for content_word in content_words):
                        matches += 1
                
                if matches > 0:
                    score = matches / len(query_words) * 0.7
                    match_type = "partial"
            
            # Add relevance boost for personality match
            if personality and content.personality == personality:
                score *= 1.2
            
            if score > 0.1:  # Minimum threshold
                results.append(RAGSearchResult(
                    content=content,
                    relevance_score=score,
                    match_type=match_type
                ))
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:max_results]
    
    def generate_rag_response(
        self,
        query: str,
        personality: str = "krishna",
        max_context_items: int = 3
    ) -> RAGResponse:
        """Generate a RAG-enhanced response"""
        try:
            # Search for relevant content
            search_results = self.search_content(query, personality, max_context_items)
            
            if not search_results:
                # Fallback to any personality if no specific content found
                search_results = self.search_content(query, None, max_context_items)
            
            # Build context
            context_chunks = []
            citations = []
            sources_consulted = []
            
            for result in search_results:
                content = result.content
                
                # Add content chunk (first 300 chars)
                chunk = content.content[:300]
                if len(content.content) > 300:
                    chunk += "..."
                context_chunks.append(chunk)
                
                # Add citation
                citation = content.get_citation()
                if citation not in citations:
                    citations.append(citation)
                
                # Add source
                if content.source not in sources_consulted:
                    sources_consulted.append(content.source)
            
            # Generate basic response (this will be enhanced with LLM integration)
            if context_chunks:
                response = f"Based on the sacred texts, particularly {sources_consulted[0] if sources_consulted else 'the scriptures'}: {context_chunks[0][:200]}..."
            else:
                response = "I understand your question, but I couldn't find specific relevant passages in the sacred texts at this moment."
            
            return RAGResponse(
                response=response,
                context_chunks=context_chunks,
                citations=citations,
                personality_used=personality,
                sources_consulted=sources_consulted,
                total_context_length=sum(len(chunk) for chunk in context_chunks)
            )
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return RAGResponse(
                response="I apologize, but I encountered an issue accessing the sacred texts. Please try again.",
                personality_used=personality
            )
    
    def get_personality_stats(self) -> Dict[str, int]:
        """Get statistics about loaded content per personality"""
        return {
            personality: len(content_list) 
            for personality, content_list in self.content_by_personality.items()
        }
    
    def get_total_content_count(self) -> int:
        """Get total number of loaded content items"""
        return len(self.all_content)

# Global instance
simple_rag_service = SimpleRAGService()
