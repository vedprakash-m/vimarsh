"""
Semantic Chunking for Spiritual Texts

This module provides intelligent chunking functionality that respects
spiritual text boundaries, preserves context, and optimizes for vector
storage and retrieval in the Vimarsh system.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class ChunkingStrategy(Enum):
    """Different strategies for text chunking"""
    FIXED_SIZE = "fixed_size"
    VERSE_BOUNDARY = "verse_boundary"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    PARAGRAPH_BASED = "paragraph_based"
    HYBRID = "hybrid"


class TextType(Enum):
    """Types of spiritual texts"""
    BHAGAVAD_GITA = "bhagavad_gita"
    MAHABHARATA = "mahabharata"
    SRIMAD_BHAGAVATAM = "srimad_bhagavatam"
    UPANISHADS = "upanishads"
    VEDAS = "vedas"
    GENERAL_SPIRITUAL = "general_spiritual"


@dataclass
class ChunkMetadata:
    """Metadata for text chunks"""
    chunk_id: str
    source_text: str
    text_type: TextType
    chapter: Optional[str] = None
    verse_range: Optional[str] = None
    themes: List[str] = field(default_factory=list)
    sanskrit_terms: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    word_count: int = 0
    character_count: int = 0
    overlap_with: List[str] = field(default_factory=list)


@dataclass
class TextChunk:
    """Represents a chunk of spiritual text"""
    content: str
    metadata: ChunkMetadata
    embedding: Optional[np.ndarray] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def text(self) -> str:
        """Alias for content for backward compatibility."""
        return self.content


class SemanticChunker:
    """
    Intelligent chunking system for spiritual texts
    
    This chunker understands spiritual text structure and creates
    semantically coherent chunks that preserve meaning and context.
    """
    
    def __init__(self, 
                 chunk_size: int = 512,
                 overlap_size: int = 50,
                 strategy: ChunkingStrategy = ChunkingStrategy.HYBRID,
                 preserve_verses: bool = True,
                 respect_boundaries: bool = None):  # Added for backward compatibility
        """
        Initialize semantic chunker
        
        Args:
            chunk_size: Target chunk size in tokens
            overlap_size: Overlap between chunks in tokens
            strategy: Chunking strategy to use
            preserve_verses: Whether to preserve verse boundaries
            respect_boundaries: Alias for preserve_verses (for backward compatibility)
        """
        # Handle backward compatibility
        if respect_boundaries is not None:
            preserve_verses = respect_boundaries
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.strategy = strategy
        self.preserve_verses = preserve_verses
        
        # Text patterns for different spiritual texts
        self.verse_patterns = {
            TextType.BHAGAVAD_GITA: [
                r'Chapter\s+(\d+).*?Verse\s+(\d+)',
                r'(\d+)\.(\d+)',
                r'BG\s+(\d+)\.(\d+)'
            ],
            TextType.MAHABHARATA: [
                r'Book\s+(\d+).*?Section\s+(\d+)',
                r'MBh\s+(\d+)\.(\d+)'
            ],
            TextType.SRIMAD_BHAGAVATAM: [
                r'Canto\s+(\d+).*?Chapter\s+(\d+).*?Verse\s+(\d+)',
                r'SB\s+(\d+)\.(\d+)\.(\d+)'
            ]
        }
        
        # Sanskrit term patterns for preservation
        self.sanskrit_patterns = [
            r'\b(?:dharma|karma|moksha|samsara|atman|brahman|yoga|bhakti|jnana)\b',
            r'\b(?:Krishna|Arjuna|Vishnu|Shiva|Brahma)\b',
            r'\b(?:Om|Aum|Namaste|Pranaam)\b'
        ]
        
        # Spiritual themes for categorization
        self.theme_keywords = {
            'duty_and_righteousness': ['dharma', 'duty', 'righteous', 'obligation', 'responsibility'],
            'action_and_karma': ['karma', 'action', 'deed', 'work', 'effort'],
            'devotion_and_love': ['bhakti', 'devotion', 'love', 'surrender', 'worship'],
            'knowledge_and_wisdom': ['jnana', 'knowledge', 'wisdom', 'understanding', 'truth'],
            'meditation_and_yoga': ['yoga', 'meditation', 'concentration', 'contemplation'],
            'liberation_and_moksha': ['moksha', 'liberation', 'freedom', 'release', 'salvation'],
            'divine_nature': ['divine', 'god', 'supreme', 'absolute', 'eternal'],
            'suffering_and_attachment': ['suffering', 'attachment', 'pain', 'sorrow', 'desire']
        }
        
        self.processed_chunks = 0
        self.total_characters = 0
        
        logger.info(f"SemanticChunker initialized: {chunk_size} tokens, {strategy.value} strategy")
    
    def chunk_text(self, text: str, 
                   source_id: str = "unknown", 
                   text_type: TextType = TextType.GENERAL_SPIRITUAL) -> List[TextChunk]:
        """
        Chunk text using semantic analysis
        
        Args:
            text: Input text to chunk
            source_id: Identifier for the source text (default: "unknown")
            text_type: Type of spiritual text
            
        Returns:
            List of TextChunk objects
        """
        try:
            # Preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Apply chunking strategy
            if self.strategy == ChunkingStrategy.VERSE_BOUNDARY:
                chunks = self._chunk_by_verses(cleaned_text, source_id, text_type)
            elif self.strategy == ChunkingStrategy.SEMANTIC_SIMILARITY:
                chunks = self._chunk_by_semantics(cleaned_text, source_id, text_type)
            elif self.strategy == ChunkingStrategy.PARAGRAPH_BASED:
                chunks = self._chunk_by_paragraphs(cleaned_text, source_id, text_type)
            elif self.strategy == ChunkingStrategy.HYBRID:
                chunks = self._chunk_hybrid(cleaned_text, source_id, text_type)
            else:  # FIXED_SIZE
                chunks = self._chunk_fixed_size(cleaned_text, source_id, text_type)
            
            # Post-process chunks
            processed_chunks = self._post_process_chunks(chunks)
            
            self.processed_chunks += len(processed_chunks)
            self.total_characters += len(text)
            
            logger.info(f"Created {len(processed_chunks)} chunks from {len(text)} characters")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Chunking error: {e}")
            # Fallback to simple chunking
            return self._chunk_fixed_size(text, source_id, text_type)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for chunking"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Preserve verse markers
        text = re.sub(r'(\d+\.\d+)', r'\n\1', text)
        
        return text.strip()
    
    def _chunk_by_verses(self, text: str, source_id: str, text_type: TextType) -> List[TextChunk]:
        """Chunk text respecting verse boundaries"""
        chunks = []
        patterns = self.verse_patterns.get(text_type, [])
        
        if not patterns:
            # Fallback to paragraph-based if no verse patterns
            return self._chunk_by_paragraphs(text, source_id, text_type)
        
        # Find verse boundaries
        verse_matches = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            verse_matches.extend(matches)
        
        if not verse_matches:
            return self._chunk_by_paragraphs(text, source_id, text_type)
        
        # Sort by position
        verse_matches.sort(key=lambda x: x.start())
        
        # Create chunks between verse boundaries
        current_chunk = ""
        current_start = 0
        
        for i, match in enumerate(verse_matches):
            # Add text before this verse
            verse_text = text[current_start:match.end()]
            
            if len(current_chunk + verse_text) <= self.chunk_size * 4:  # Rough token estimate
                current_chunk += verse_text
            else:
                if current_chunk.strip():
                    chunk = self._create_chunk(current_chunk, source_id, text_type, i)
                    chunks.append(chunk)
                current_chunk = verse_text
            
            current_start = match.end()
        
        # Add remaining text
        if current_chunk.strip():
            chunk = self._create_chunk(current_chunk, source_id, text_type, len(chunks))
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_semantics(self, text: str, source_id: str, text_type: TextType) -> List[TextChunk]:
        """Chunk text based on semantic similarity (simplified version)"""
        # For now, use paragraph-based chunking with semantic analysis
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_themes = set()
        
        for i, paragraph in enumerate(paragraphs):
            paragraph_themes = self._extract_themes(paragraph)
            
            # Check if themes are compatible
            if (not current_themes or 
                current_themes.intersection(paragraph_themes) or
                len(current_chunk + paragraph) <= self.chunk_size * 4):
                
                current_chunk += paragraph + "\n\n"
                current_themes.update(paragraph_themes)
            else:
                # Create chunk and start new one
                if current_chunk.strip():
                    chunk = self._create_chunk(current_chunk, source_id, text_type, len(chunks))
                    chunks.append(chunk)
                
                current_chunk = paragraph + "\n\n"
                current_themes = paragraph_themes
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(current_chunk, source_id, text_type, len(chunks))
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_paragraphs(self, text: str, source_id: str, text_type: TextType) -> List[TextChunk]:
        """Chunk text by paragraph boundaries"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= self.chunk_size * 4:  # Rough token estimate
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunk = self._create_chunk(current_chunk, source_id, text_type, len(chunks))
                    chunks.append(chunk)
                current_chunk = paragraph + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(current_chunk, source_id, text_type, len(chunks))
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_hybrid(self, text: str, source_id: str, text_type: TextType) -> List[TextChunk]:
        """Hybrid chunking combining multiple strategies"""
        # Start with verse-based if verses are detected
        if self.preserve_verses and text_type in self.verse_patterns:
            verse_chunks = self._chunk_by_verses(text, source_id, text_type)
            if len(verse_chunks) > 1:
                return verse_chunks
        
        # Fall back to semantic chunking
        return self._chunk_by_semantics(text, source_id, text_type)
    
    def _chunk_fixed_size(self, text: str, source_id: str, text_type: TextType) -> List[TextChunk]:
        """Simple fixed-size chunking with overlap"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.overlap_size):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk = self._create_chunk(chunk_text, source_id, text_type, len(chunks))
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, content: str, source_id: str, text_type: TextType, index: int) -> TextChunk:
        """Create a TextChunk with metadata"""
        chunk_id = f"{source_id}_chunk_{index:04d}"
        
        # Extract metadata
        themes = self._extract_themes(content)
        sanskrit_terms = self._extract_sanskrit_terms(content)
        verse_info = self._extract_verse_info(content, text_type)
        quality_score = self._calculate_quality_score(content)
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            source_text=source_id,
            text_type=text_type,
            chapter=verse_info.get('chapter'),
            verse_range=verse_info.get('verse_range'),
            themes=list(themes),
            sanskrit_terms=sanskrit_terms,
            quality_score=quality_score,
            word_count=len(content.split()),
            character_count=len(content)
        )
        
        return TextChunk(content=content.strip(), metadata=metadata)
    
    def _extract_themes(self, text: str) -> set:
        """Extract spiritual themes from text"""
        text_lower = text.lower()
        themes = set()
        
        for theme, keywords in self.theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.add(theme)
        
        return themes
    
    def _extract_sanskrit_terms(self, text: str) -> List[str]:
        """Extract Sanskrit terms from text"""
        terms = []
        
        for pattern in self.sanskrit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.extend(matches)
        
        return list(set(terms))  # Remove duplicates
    
    def _extract_verse_info(self, text: str, text_type: TextType) -> Dict[str, str]:
        """Extract verse/chapter information"""
        info = {}
        patterns = self.verse_patterns.get(text_type, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    info['chapter'] = groups[0]
                    info['verse_range'] = groups[1]
                    if len(groups) >= 3:
                        info['verse_range'] = f"{groups[1]}.{groups[2]}"
                break
        
        return info
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate quality score for chunk"""
        score = 0.0
        
        # Length score (optimal around 300-500 chars)
        length = len(content)
        if 200 <= length <= 600:
            score += 0.3
        elif 100 <= length <= 800:
            score += 0.2
        else:
            score += 0.1
        
        # Sanskrit terms presence
        sanskrit_count = len(self._extract_sanskrit_terms(content))
        score += min(0.2, sanskrit_count * 0.05)
        
        # Theme diversity
        themes = self._extract_themes(content)
        score += min(0.3, len(themes) * 0.1)
        
        # Structural completeness (sentences, paragraphs)
        if content.count('.') >= 1:
            score += 0.1
        if '\n' in content:
            score += 0.1
        
        return min(1.0, score)
    
    def _post_process_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """Post-process chunks for quality and overlaps"""
        processed = []
        
        for i, chunk in enumerate(chunks):
            # Add overlap information
            if i > 0:
                chunk.metadata.overlap_with.append(chunks[i-1].metadata.chunk_id)
            if i < len(chunks) - 1:
                chunk.metadata.overlap_with.append(chunks[i+1].metadata.chunk_id)
            
            # Quality filtering
            if chunk.metadata.quality_score >= 0.3 or len(chunk.content) >= 100:
                processed.append(chunk)
            else:
                logger.debug(f"Filtered low-quality chunk: {chunk.metadata.chunk_id}")
        
        return processed
    
    def get_chunking_stats(self) -> Dict[str, Any]:
        """Get chunking statistics"""
        return {
            "processed_chunks": self.processed_chunks,
            "total_characters": self.total_characters,
            "average_chunk_size": self.total_characters / max(1, self.processed_chunks),
            "chunk_size_limit": self.chunk_size,
            "overlap_size": self.overlap_size,
            "strategy": self.strategy.value,
            "preserve_verses": self.preserve_verses
        }
    
    def reset_stats(self):
        """Reset chunking statistics"""
        self.processed_chunks = 0
        self.total_characters = 0


# Convenience functions
def create_semantic_chunker(text_type: TextType = TextType.GENERAL_SPIRITUAL) -> SemanticChunker:
    """Create SemanticChunker with default settings for text type"""
    if text_type in [TextType.BHAGAVAD_GITA, TextType.MAHABHARATA]:
        return SemanticChunker(
            chunk_size=400,
            overlap_size=50,
            strategy=ChunkingStrategy.VERSE_BOUNDARY,
            preserve_verses=True
        )
    else:
        return SemanticChunker(
            chunk_size=512,
            overlap_size=50,
            strategy=ChunkingStrategy.HYBRID,
            preserve_verses=True
        )


def chunk_spiritual_text(text: str, 
                        source_id: str,
                        text_type: TextType = TextType.GENERAL_SPIRITUAL) -> List[TextChunk]:
    """Quick text chunking function"""
    chunker = create_semantic_chunker(text_type)
    return chunker.chunk_text(text, source_id, text_type)
