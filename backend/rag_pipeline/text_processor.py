"""
Spiritual Text Processor

Handles text chunking, preprocessing, and indexing for spiritual texts
with special attention to preserving verse boundaries and Sanskrit terminology.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import unicodedata

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a processed chunk of spiritual text"""
    content: str
    metadata: Dict[str, Any]
    chapter: Optional[str] = None
    verse_range: Optional[str] = None
    sanskrit_terms: List[str] = None
    chunk_id: str = None
    source_file: str = None
    
    def __post_init__(self):
        if self.sanskrit_terms is None:
            self.sanskrit_terms = []


class SpiritualTextProcessor:
    """
    Processes spiritual texts for RAG pipeline with special handling for:
    - Verse boundary preservation
    - Sanskrit term identification and preservation
    - Chapter and section organization
    - Cultural context preservation
    """
    
    def __init__(self):
        # Sanskrit term patterns (common spiritual terms)
        self.sanskrit_patterns = [
            r'\b(?:dharma|karma|moksha|samsara|bhakti|yoga|atman|brahman)\b',
            r'\b(?:Krishna|Arjuna|Bhagavan|Gita|Mahabharata|Vedas?)\b',
            r'\b(?:mantra|yantra|tantra|guru|ashrama|varna)\b',
            r'\b(?:puja|yajna|japa|tapas|seva|ahimsa)\b',
            # Devanagari unicode range for Sanskrit text
            r'[\u0900-\u097F]+',
        ]
        
        # Verse boundary patterns
        self.verse_patterns = [
            r'^\d+\.\d+',  # Chapter.Verse (e.g., "2.47")
            r'^Chapter\s+\d+',  # Chapter headers
            r'^Verse\s+\d+',  # Verse headers
            r'^\d+\.',  # Simple verse numbering
        ]
        
        # Compile patterns for efficiency
        self.compiled_sanskrit_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sanskrit_patterns]
        self.compiled_verse_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in self.verse_patterns]
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text while preserving spiritual and cultural elements
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Preprocessed text with normalized Unicode and cleaned formatting
        """
        # Normalize Unicode (important for Sanskrit text)
        text = unicodedata.normalize('NFKC', text)
        
        # Remove excessive whitespace but preserve paragraph breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Clean up common OCR artifacts while preserving Sanskrit
        # Be careful not to remove diacritics
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        return text.strip()
    
    def extract_sanskrit_terms(self, text: str) -> List[str]:
        """
        Extract Sanskrit terms and spiritual vocabulary from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of identified Sanskrit terms
        """
        terms = []
        for pattern in self.compiled_sanskrit_patterns:
            matches = pattern.findall(text)
            terms.extend(matches)
        
        # Remove duplicates and normalize
        terms = list(set(term.strip() for term in terms if term.strip()))
        return terms
    
    def identify_verse_boundaries(self, text: str) -> List[Tuple[int, str]]:
        """
        Identify verse boundaries in spiritual text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (position, verse_id) tuples marking verse boundaries
        """
        boundaries = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.compiled_verse_patterns:
                match = pattern.search(line)
                if match:
                    boundaries.append((i, match.group().strip()))
                    break
        
        return boundaries
    
    def chunk_by_verses(self, text: str, max_chunk_size: int = 1000) -> List[TextChunk]:
        """
        Chunk text by verse boundaries, respecting spiritual structure
        
        Args:
            text: Text to chunk
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of TextChunk objects
        """
        lines = text.split('\n')
        boundaries = self.identify_verse_boundaries(text)
        chunks = []
        
        if not boundaries:
            # Fallback to paragraph-based chunking if no verses found
            return self.chunk_by_paragraphs(text, max_chunk_size)
        
        current_chunk = []
        current_size = 0
        current_verse_start = None
        current_verse_end = None
        
        boundary_positions = {pos: verse_id for pos, verse_id in boundaries}
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline
            
            # Check if this line starts a new verse
            if i in boundary_positions:
                # Save current chunk if it exists and is not empty
                if current_chunk and current_size > 0:
                    chunk_content = '\n'.join(current_chunk)
                    verse_range = f"{current_verse_start}-{current_verse_end}" if current_verse_end else current_verse_start
                    
                    chunks.append(TextChunk(
                        content=chunk_content,
                        metadata={
                            'chunk_type': 'verse',
                            'size': current_size,
                            'line_count': len(current_chunk)
                        },
                        verse_range=verse_range,
                        sanskrit_terms=self.extract_sanskrit_terms(chunk_content)
                    ))
                
                # Start new chunk
                current_chunk = [line]
                current_size = line_size
                current_verse_start = boundary_positions[i]
                current_verse_end = current_verse_start
            else:
                # Add to current chunk if within size limit
                if current_size + line_size <= max_chunk_size:
                    current_chunk.append(line)
                    current_size += line_size
                else:
                    # Current chunk is full, save it
                    if current_chunk:
                        chunk_content = '\n'.join(current_chunk)
                        verse_range = f"{current_verse_start}-{current_verse_end}" if current_verse_end else current_verse_start
                        
                        chunks.append(TextChunk(
                            content=chunk_content,
                            metadata={
                                'chunk_type': 'verse',
                                'size': current_size,
                                'line_count': len(current_chunk)
                            },
                            verse_range=verse_range,
                            sanskrit_terms=self.extract_sanskrit_terms(chunk_content)
                        ))
                    
                    # Start new chunk with current line
                    current_chunk = [line]
                    current_size = line_size
                    # Keep verse tracking
        
        # Handle remaining chunk
        if current_chunk and current_size > 0:
            chunk_content = '\n'.join(current_chunk)
            verse_range = f"{current_verse_start}-{current_verse_end}" if current_verse_end else current_verse_start
            
            chunks.append(TextChunk(
                content=chunk_content,
                metadata={
                    'chunk_type': 'verse',
                    'size': current_size,
                    'line_count': len(current_chunk)
                },
                verse_range=verse_range,
                sanskrit_terms=self.extract_sanskrit_terms(chunk_content)
            ))
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, max_chunk_size: int = 1000) -> List[TextChunk]:
        """
        Fallback chunking by paragraphs when verse structure is not clear
        
        Args:
            text: Text to chunk
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of TextChunk objects
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            paragraph_size = len(paragraph) + 2  # +2 for paragraph break
            
            if current_size + paragraph_size <= max_chunk_size:
                current_chunk.append(paragraph)
                current_size += paragraph_size
            else:
                # Save current chunk
                if current_chunk:
                    chunk_content = '\n\n'.join(current_chunk)
                    chunks.append(TextChunk(
                        content=chunk_content,
                        metadata={
                            'chunk_type': 'paragraph',
                            'size': current_size,
                            'paragraph_count': len(current_chunk)
                        },
                        sanskrit_terms=self.extract_sanskrit_terms(chunk_content)
                    ))
                
                # Start new chunk
                current_chunk = [paragraph]
                current_size = paragraph_size
        
        # Handle remaining chunk
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunks.append(TextChunk(
                content=chunk_content,
                metadata={
                    'chunk_type': 'paragraph',
                    'size': current_size,
                    'paragraph_count': len(current_chunk)
                },
                sanskrit_terms=self.extract_sanskrit_terms(chunk_content)
            ))
        
        return chunks
    
    def process_text(self, text: str, source_file: str = None, max_chunk_size: int = 1000) -> List[TextChunk]:
        """
        Main processing pipeline for spiritual texts
        
        Args:
            text: Raw text to process
            source_file: Source file name for metadata
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of processed TextChunk objects
        """
        logger.info(f"Processing text from {source_file or 'unknown source'}")
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Chunk text by verses (preferred) or paragraphs (fallback)
        chunks = self.chunk_by_verses(processed_text, max_chunk_size)
        
        # Add metadata and generate IDs
        for i, chunk in enumerate(chunks):
            chunk.chunk_id = f"{source_file or 'unknown'}_{i:04d}"
            chunk.source_file = source_file
            
            # Add global metadata
            chunk.metadata.update({
                'processing_timestamp': None,  # Will be set when stored
                'sanskrit_term_count': len(chunk.sanskrit_terms),
                'has_sanskrit': bool(chunk.sanskrit_terms)
            })
        
        logger.info(f"Created {len(chunks)} chunks from {source_file or 'text'}")
        return chunks
    
    def extract_chapter_info(self, text: str) -> Dict[str, Any]:
        """
        Extract chapter and section information from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with chapter information
        """
        chapter_info = {
            'chapters': [],
            'total_verses': 0,
            'structure': 'unknown'
        }
        
        # Look for chapter patterns
        chapter_pattern = re.compile(r'^Chapter\s+(\d+)', re.IGNORECASE | re.MULTILINE)
        chapters = chapter_pattern.findall(text)
        
        if chapters:
            chapter_info['chapters'] = [int(ch) for ch in chapters]
            chapter_info['structure'] = 'chapter-based'
        
        # Count verses
        verse_boundaries = self.identify_verse_boundaries(text)
        chapter_info['total_verses'] = len(verse_boundaries)
        
        return chapter_info
    
    def chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[TextChunk]:
        """
        Chunk text into meaningful segments for RAG processing.
        
        Args:
            text: Text to chunk
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of TextChunk objects
        """
        return self.process_text(text, max_chunk_size=max_chunk_size)
