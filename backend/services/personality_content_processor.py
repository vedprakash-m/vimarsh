"""
Personality Content Processor - Phase 4 Implementation

This service processes the acquired personality sources into chunks suitable for RAG.
Handles text extraction, chunking, metadata assignment, and prepares content for vector embedding.
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a processed content chunk"""
    id: str
    personality_id: str
    source_id: str
    chunk_text: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    quality_score: float = 0.0
    relevance_score: float = 0.0
    
    # Processing info
    token_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "personality_id": self.personality_id,
            "source_id": self.source_id,
            "chunk_text": self.chunk_text,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "relevance_score": self.relevance_score,
            "token_count": self.token_count,
            "created_at": self.created_at
        }

@dataclass
class ProcessingResult:
    """Result of content processing"""
    personality_id: str
    total_sources: int
    total_chunks: int
    total_tokens: int
    average_quality_score: float
    processing_time_seconds: float
    chunks: List[ContentChunk] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class PersonalityContentProcessor:
    """Processes personality content into chunks for RAG"""
    
    def __init__(self):
        self.sources_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sources")
        self.personalities_dir = os.path.join(self.sources_dir, "personalities")
        self.registry_path = os.path.join(self.sources_dir, "personality_content_registry.json")
        
        # Chunking parameters
        self.chunk_size = 1000  # tokens per chunk
        self.chunk_overlap = 200  # overlap between chunks
        
        # Domain-specific chunking strategies
        self.chunking_strategies = {
            "literary": self._chunk_by_literary_structure,
            "philosophical": self._chunk_by_argument_concept,
            "scientific": self._chunk_by_theorem_principle,
            "historical": self._chunk_by_chronology_event,
            "spiritual": self._chunk_by_teaching_verse
        }
    
    def process_all_personalities(self) -> Dict[str, ProcessingResult]:
        """Process content for all personalities"""
        logger.info("Starting content processing for all personalities")
        
        # Load registry to get personality list
        registry = self._load_registry()
        if not registry:
            logger.error("Could not load personality registry")
            return {}
        
        results = {}
        total_start_time = datetime.now()
        
        for personality_id in registry.get("personalities", {}).keys():
            logger.info(f"Processing content for {personality_id}")
            result = self.process_personality(personality_id)
            results[personality_id] = result
            
            if result.errors:
                logger.warning(f"Errors processing {personality_id}: {result.errors}")
        
        total_time = (datetime.now() - total_start_time).total_seconds()
        
        # Generate summary
        total_chunks = sum(r.total_chunks for r in results.values())
        total_tokens = sum(r.total_tokens for r in results.values())
        
        logger.info(f"""
        Content Processing Complete:
        - Personalities: {len(results)}
        - Total chunks: {total_chunks}
        - Total tokens: {total_tokens}
        - Processing time: {total_time:.2f}s
        """)
        
        return results
    
    def process_personality(self, personality_id: str) -> ProcessingResult:
        """Process content for a specific personality"""
        start_time = datetime.now()
        
        # Load registry to get sources for this personality
        registry = self._load_registry()
        if not registry or personality_id not in registry.get("personalities", {}):
            return ProcessingResult(
                personality_id=personality_id,
                total_sources=0,
                total_chunks=0,
                total_tokens=0,
                average_quality_score=0.0,
                processing_time_seconds=0.0,
                errors=[f"Personality {personality_id} not found in registry"]
            )
        
        personality_data = registry["personalities"][personality_id]
        sources = personality_data.get("sources", [])
        domain = personality_data.get("domain", "philosophical")
        
        all_chunks = []
        errors = []
        total_tokens = 0
        
        for source in sources:
            try:
                chunks = self._process_source(source, personality_id, domain)
                all_chunks.extend(chunks)
                total_tokens += sum(chunk.token_count for chunk in chunks)
                logger.info(f"Processed {source['source_id']}: {len(chunks)} chunks")
            except Exception as e:
                error_msg = f"Error processing {source.get('source_id', 'unknown')}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Calculate quality metrics
        quality_scores = [chunk.quality_score for chunk in all_chunks if chunk.quality_score > 0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = ProcessingResult(
            personality_id=personality_id,
            total_sources=len(sources),
            total_chunks=len(all_chunks),
            total_tokens=total_tokens,
            average_quality_score=avg_quality,
            processing_time_seconds=processing_time,
            chunks=all_chunks,
            errors=errors
        )
        
        # Save processed chunks
        self._save_chunks(personality_id, all_chunks)
        
        return result
    
    def _process_source(self, source: Dict[str, Any], personality_id: str, domain: str) -> List[ContentChunk]:
        """Process a single source file into chunks"""
        file_path = source.get("file_path")
        source_id = source.get("source_id")
        
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Read content
        content = self._read_file_content(file_path)
        if not content:
            raise ValueError(f"Could not read content from {file_path}")
        
        # Get chunking strategy for domain
        chunking_function = self.chunking_strategies.get(domain, self._chunk_by_semantic_paragraphs)
        
        # Create chunks
        chunks = chunking_function(content, source, personality_id)
        
        # Post-process chunks (quality scoring, token counting)
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i
            chunk.token_count = self._estimate_token_count(chunk.chunk_text)
            chunk.quality_score = self._calculate_quality_score(chunk)
        
        return chunks
    
    def _read_file_content(self, file_path: str) -> str:
        """Read content from file, handling various formats"""
        try:
            # Handle PDF files (basic extraction)
            if file_path.endswith('.pdf'):
                # For now, we'll skip PDF processing 
                # Could be enhanced with PyPDF2 or similar
                logger.warning(f"PDF processing not implemented for {file_path}")
                return ""
            
            # Handle text files
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean content
            content = self._clean_text(content)
            return content
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove project gutenberg headers/footers
        text = re.sub(r'\*\*\* START OF.*?\*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* END OF.*?\*\*\*', '', text, flags=re.DOTALL)
        
        # Remove excessive dashes and underscores
        text = re.sub(r'-{5,}', '---', text)
        text = re.sub(r'_{5,}', '___', text)
        
        return text.strip()
    
    def _chunk_by_semantic_paragraphs(self, content: str, source: Dict[str, Any], personality_id: str) -> List[ContentChunk]:
        """Default chunking strategy - by semantic paragraphs"""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph would exceed chunk size
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if self._estimate_token_count(potential_chunk) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk = self._create_chunk(current_chunk, source, personality_id, chunk_id)
                chunks.append(chunk)
                chunk_id += 1
                
                # Start new chunk with overlap
                current_chunk = self._get_overlap_text(current_chunk) + paragraph
            else:
                current_chunk = potential_chunk
        
        # Add final chunk
        if current_chunk:
            chunk = self._create_chunk(current_chunk, source, personality_id, chunk_id)
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_literary_structure(self, content: str, source: Dict[str, Any], personality_id: str) -> List[ContentChunk]:
        """Literary chunking - by chapters, scenes, stanzas"""
        # Look for chapter markers
        chapter_pattern = r'(?:CHAPTER|Chapter|ACT|Act|SCENE|Scene)\s+[IVXLCDM]+|\d+'
        chapters = re.split(chapter_pattern, content)
        
        chunks = []
        chunk_id = 0
        
        for i, chapter in enumerate(chapters):
            if not chapter.strip():
                continue
            
            # Further split long chapters
            if self._estimate_token_count(chapter) > self.chunk_size * 2:
                sub_chunks = self._chunk_by_semantic_paragraphs(chapter, source, personality_id)
                for sub_chunk in sub_chunks:
                    sub_chunk.id = self._generate_chunk_id(source["source_id"], personality_id, chunk_id)
                    sub_chunk.metadata.update({
                        "chapter_index": i,
                        "content_type": "literary_section"
                    })
                    chunks.append(sub_chunk)
                    chunk_id += 1
            else:
                chunk = self._create_chunk(chapter, source, personality_id, chunk_id)
                chunk.metadata.update({
                    "chapter_index": i,
                    "content_type": "literary_chapter"
                })
                chunks.append(chunk)
                chunk_id += 1
        
        return chunks
    
    def _chunk_by_argument_concept(self, content: str, source: Dict[str, Any], personality_id: str) -> List[ContentChunk]:
        """Philosophical chunking - by arguments and concepts"""
        # Look for philosophical markers
        argument_markers = [
            r'(?:Therefore|Thus|Hence|Consequently|It follows that)',
            r'(?:First|Second|Third|Finally|In conclusion)',
            r'(?:Proposition|Theorem|Axiom|Principle)\s+\d+',
            r'(?:Question|Problem|Issue):\s*'
        ]
        
        # For now, use semantic paragraphs with philosophical metadata
        chunks = self._chunk_by_semantic_paragraphs(content, source, personality_id)
        
        for chunk in chunks:
            # Add philosophical markers
            chunk.metadata.update({
                "content_type": "philosophical_argument",
                "has_argument_markers": any(re.search(marker, chunk.chunk_text, re.IGNORECASE) 
                                          for marker in argument_markers)
            })
        
        return chunks
    
    def _chunk_by_theorem_principle(self, content: str, source: Dict[str, Any], personality_id: str) -> List[ContentChunk]:
        """Scientific chunking - by theorems and principles"""
        # Look for scientific structure
        science_markers = [
            r'(?:Theorem|Principle|Law|Hypothesis|Experiment)\s+\d*',
            r'(?:Proof|Demonstration|Method):',
            r'(?:Figure|Diagram|Table)\s+\d+'
        ]
        
        chunks = self._chunk_by_semantic_paragraphs(content, source, personality_id)
        
        for chunk in chunks:
            chunk.metadata.update({
                "content_type": "scientific_principle",
                "has_formal_structure": any(re.search(marker, chunk.chunk_text, re.IGNORECASE) 
                                          for marker in science_markers)
            })
        
        return chunks
    
    def _chunk_by_chronology_event(self, content: str, source: Dict[str, Any], personality_id: str) -> List[ContentChunk]:
        """Historical chunking - by chronology and events"""
        # Look for dates and events
        date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b|\b\d{4}\b'
        
        chunks = self._chunk_by_semantic_paragraphs(content, source, personality_id)
        
        for chunk in chunks:
            dates = re.findall(date_pattern, chunk.chunk_text)
            chunk.metadata.update({
                "content_type": "historical_event",
                "dates_mentioned": dates,
                "has_chronological_markers": len(dates) > 0
            })
        
        return chunks
    
    def _chunk_by_teaching_verse(self, content: str, source: Dict[str, Any], personality_id: str) -> List[ContentChunk]:
        """Spiritual chunking - by teachings and verses"""
        # Look for verse structures
        verse_pattern = r'(?:Verse|Chapter|Shloka)\s+\d+'
        
        chunks = self._chunk_by_semantic_paragraphs(content, source, personality_id)
        
        for chunk in chunks:
            verses = re.findall(verse_pattern, chunk.chunk_text, re.IGNORECASE)
            chunk.metadata.update({
                "content_type": "spiritual_teaching",
                "verses_mentioned": verses,
                "has_verse_structure": len(verses) > 0
            })
        
        return chunks
    
    def _create_chunk(self, content: str, source: Dict[str, Any], personality_id: str, chunk_id: int) -> ContentChunk:
        """Create a ContentChunk object"""
        chunk_uuid = self._generate_chunk_id(source["source_id"], personality_id, chunk_id)
        
        return ContentChunk(
            id=chunk_uuid,
            personality_id=personality_id,
            source_id=source["source_id"],
            chunk_text=content.strip(),
            chunk_index=chunk_id,
            metadata={
                "source_title": source.get("title", ""),
                "source_author": source.get("author", ""),
                "source_type": source.get("source_type", ""),
                "domain": source.get("domain", ""),
                "file_path": source.get("file_path", "")
            }
        )
    
    def _generate_chunk_id(self, source_id: str, personality_id: str, chunk_id: int) -> str:
        """Generate unique chunk ID"""
        content = f"{source_id}_{personality_id}_{chunk_id}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough approximation: ~1.3 tokens per word
        words = len(text.split())
        return int(words * 1.3)
    
    def _calculate_quality_score(self, chunk: ContentChunk) -> float:
        """Calculate quality score for chunk"""
        text = chunk.chunk_text
        
        # Base score
        score = 0.5
        
        # Length scoring (prefer chunks with good length)
        if 200 <= len(text) <= 2000:
            score += 0.2
        
        # Coherence indicators
        if '. ' in text and len(text.split('. ')) >= 2:  # Multiple sentences
            score += 0.1
        
        # Avoid chunks that are mostly formatting
        alpha_ratio = sum(c.isalpha() for c in text) / len(text) if text else 0
        score += alpha_ratio * 0.2
        
        # Penalty for very short or very long chunks
        if len(text) < 100:
            score -= 0.3
        elif len(text) > 3000:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text for next chunk"""
        words = text.split()
        if len(words) <= self.chunk_overlap:
            return text
        
        # Take last N words as overlap
        overlap_words = words[-self.chunk_overlap:]
        return ' '.join(overlap_words) + " "
    
    def _load_registry(self) -> Optional[Dict[str, Any]]:
        """Load personality content registry"""
        try:
            if os.path.exists(self.registry_path):
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
        return None
    
    def _save_chunks(self, personality_id: str, chunks: List[ContentChunk]):
        """Save processed chunks to JSON file"""
        output_dir = os.path.join(self.sources_dir, "processed_chunks")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{personality_id}_chunks.json")
        
        chunks_data = {
            "personality_id": personality_id,
            "total_chunks": len(chunks),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "chunks": [chunk.to_dict() for chunk in chunks]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunks_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(chunks)} chunks for {personality_id} to {output_file}")
        except Exception as e:
            logger.error(f"Error saving chunks for {personality_id}: {e}")

# Utility function for external use
def process_all_personality_content():
    """Process content for all personalities - main entry point"""
    processor = PersonalityContentProcessor()
    return processor.process_all_personalities()

if __name__ == "__main__":
    # Run processing when called directly
    logging.basicConfig(level=logging.INFO)
    results = process_all_personality_content()
    
    # Print summary
    for personality_id, result in results.items():
        print(f"{personality_id}: {result.total_chunks} chunks, {result.total_tokens} tokens")
