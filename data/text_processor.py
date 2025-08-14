"""
Multi-Domain Text Processor for Vimarsh AI Agent

Comprehensive text processing capabilities for multiple domains including
spiritual, scientific, historical, and philosophical content with domain-specific
handling, Sanskrit text support, verse-aware chunking, and cultural preservation.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import unicodedata

# Import the multi-domain processors
from .domain_processors import (
    MultiDomainProcessor, 
    ProcessedChunk, 
    ProcessingResult,
    DomainProcessorFactory
)

logger = logging.getLogger(__name__)

@dataclass
class TextMetadata:
    """Metadata extracted from spiritual text."""
    source: Optional[str] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None
    text_type: Optional[str] = None
    line_count: int = 0
    word_count: int = 0
    character_count: int = 0
    chapter_reference: Optional[str] = None
    contains_sanskrit: bool = False
    sanskrit_terms_count: int = 0


class EnhancedTextProcessor:
    """
    Enhanced text processor that combines spiritual text processing with multi-domain support.
    
    This class extends the original spiritual text processor to handle multiple domains
    while maintaining backward compatibility for spiritual content processing.
    """
    
    def __init__(self):
        """Initialize the enhanced text processor with multi-domain support."""
        # Initialize the multi-domain processor
        self.multi_domain_processor = MultiDomainProcessor()
        
        # Initialize the spiritual processor for backward compatibility
        self.spiritual_processor = SpiritualTextProcessor()
    
    def process_text_with_domain(self, text: str, source: str = "", domain: str = None, 
                                metadata: Dict[str, Any] = None) -> ProcessingResult:
        """
        Process text using domain-specific processors.
        
        Args:
            text: Input text to process
            source: Source identifier for the text
            domain: Target domain (spiritual, scientific, historical, philosophical)
            metadata: Additional metadata for processing
            
        Returns:
            ProcessingResult with domain-specific chunks and metadata
        """
        return self.multi_domain_processor.process_text(text, source, domain, metadata)
    
    def detect_domain(self, text: str) -> str:
        """
        Detect the most appropriate domain for the given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected domain string
        """
        return self.multi_domain_processor.detect_domain(text)
    
    def get_available_domains(self) -> List[str]:
        """Get list of available processing domains."""
        return self.multi_domain_processor.get_available_domains()
    
    def chunk_text_by_domain(self, text: str, domain: str, chunk_size: int = 1000, 
                           overlap: int = 100) -> List[ProcessedChunk]:
        """
        Chunk text using domain-specific strategies.
        
        Args:
            text: Input text to chunk
            domain: Processing domain
            chunk_size: Target chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of processed chunks with domain-specific metadata
        """
        processor = self.multi_domain_processor.get_processor(domain)
        result = processor.process_text(text, "unknown", {"chunk_size": chunk_size, "overlap": overlap})
        return result.chunks
    
    def validate_content_for_domain(self, text: str, domain: str) -> Dict[str, Any]:
        """
        Validate if content is appropriate for the specified domain.
        
        Args:
            text: Text to validate
            domain: Target domain
            
        Returns:
            Validation results with quality metrics
        """
        processor = self.multi_domain_processor.get_processor(domain)
        result = processor.process_text(text, "validation", {})
        
        return {
            'is_valid': result.quality_metrics.get('avg_quality', 0) > 50,
            'quality_score': result.quality_metrics.get('avg_quality', 0),
            'key_terms_found': len(result.chunks[0].key_terms) if result.chunks else 0,
            'domain_confidence': result.quality_metrics.get('avg_quality', 0) / 100,
            'warnings': result.warnings,
            'errors': result.errors
        }


class SpiritualTextProcessor:
    """
    Advanced text processor specifically designed for spiritual and religious content.
    
    Handles Sanskrit Unicode, verse boundaries, cultural terminology preservation,
    and maintains spiritual context during preprocessing.
    """
    
    def __init__(self):
        """Initialize the spiritual text processor with cultural patterns."""
        # Sanskrit/Devanagari Unicode ranges
        self.sanskrit_patterns = {
            'devanagari': r'[\u0900-\u097F]+',
            'vedic_extensions': r'[\u1CD0-\u1CFF]+',
            'combining_marks': r'[\u0300-\u036F]+',
        }
        
        # Spiritual terminology to preserve
        self.sacred_terms = {
            'english': [
                'dharma', 'karma', 'moksha', 'samsara', 'atman', 'brahman',
                'yoga', 'yogi', 'guru', 'ashram', 'mantra', 'meditation',
                'krishna', 'arjuna', 'vishnu', 'shiva', 'devi', 'gita',
                'upanishad', 'vedas', 'purana', 'bhagavatam', 'mahabharata'
            ],
            'sanskrit': [
                'श्री', 'भगवान्', 'अर्जुन', 'कृष्ण', 'धर्म', 'कर्म', 'योग',
                'आत्मा', 'ब्रह्म', 'मोक्ष', 'संसार', 'गुरु', 'मन्त्र'
            ]
        }
        
        # Verse and chapter patterns
        self.structural_patterns = {
            'chapter': r'(?:Chapter|अध्याय)\s*(\d+)',
            'verse': r'(?:Verse|श्लोक)\s*(\d+)',
            'section': r'(?:Section|खण्ड)\s*(\d+)',
            'canto': r'(?:Canto|स्कन्द)\s*(\d+)'
        }
    
    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode text while preserving Sanskrit/Devanagari.
        
        Args:
            text: Input text with potential Unicode issues
            
        Returns:
            Normalized text with proper Sanskrit preservation
        """
        # Normalize to NFC form (canonical decomposition + canonical composition)
        normalized = unicodedata.normalize('NFC', text)
        
        # Remove excessive whitespace but preserve spiritual formatting
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r'\n\s*\n\s*\n+', '\n\n', normalized)
        
        return normalized.strip()
    
    def preserve_sacred_terms(self, text: str) -> str:
        """
        Ensure sacred terms are properly preserved and not corrupted.
        
        Args:
            text: Input text
            
        Returns:
            Text with protected sacred terminology
        """
        # Create a mapping for case-insensitive preservation
        preserved_text = text
        
        for lang, terms in self.sacred_terms.items():
            for term in terms:
                # Case-insensitive replacement while preserving original case
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                preserved_text = pattern.sub(term, preserved_text)
        
        return preserved_text
    
    def extract_structural_info(self, text: str) -> Dict[str, Any]:
        """
        Extract structural information like chapter, verse numbers.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with structural metadata
        """
        structure = {
            'chapters': [],
            'verses': [],
            'sections': [],
            'cantos': []
        }
        
        for struct_type, pattern in self.structural_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if struct_type == 'chapter':
                    structure['chapters'].append(int(match.group(1)))
                elif struct_type == 'verse':
                    structure['verses'].append(int(match.group(1)))
                elif struct_type == 'section':
                    structure['sections'].append(int(match.group(1)))
                elif struct_type == 'canto':
                    structure['cantos'].append(int(match.group(1)))
        
        return structure
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text while preserving spiritual context.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        # Normalize Unicode
        cleaned = self.normalize_unicode(text)
        
        # Preserve sacred terms
        cleaned = self.preserve_sacred_terms(cleaned)
        
        # Remove unnecessary punctuation but preserve important marks
        # Keep colons for verse references, preserve Sanskrit punctuation
        cleaned = re.sub(r'[^\w\s\u0900-\u097F\u1CD0-\u1CFF:.;,!?()-]', '', cleaned)
        
        # Normalize spacing around punctuation
        cleaned = re.sub(r'\s*([:.;,!?])\s*', r'\1 ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def segment_by_verses(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by verse boundaries for spiritual texts.
        
        Args:
            text: Input spiritual text
            
        Returns:
            List of verse segments with metadata
        """
        verses = []
        
        # Split by common verse patterns
        verse_pattern = r'(?:(?:Chapter|अध्याय)\s*\d+[.,:]?\s*)?(?:Verse|श्लोक)\s*(\d+)[.,:]?\s*([^(?:Verse|श्लोक)]*?)(?=(?:Verse|श्लोक)|\Z)'
        
        matches = re.finditer(verse_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            verse_num = match.group(1)
            verse_text = match.group(2).strip()
            
            if verse_text:
                verses.append({
                    'verse_number': int(verse_num),
                    'text': verse_text,
                    'type': 'verse',
                    'metadata': self.extract_structural_info(match.group(0))
                })
        
        # If no verses found, return as single segment
        if not verses:
            verses.append({
                'verse_number': 1,
                'text': text,
                'type': 'text_block',
                'metadata': self.extract_structural_info(text)
            })
        
        return verses
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
        """
        Intelligent chunking that respects verse boundaries and spiritual structure.
        
        Args:
            text: Input text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks with metadata
        """
        # First try to segment by verses
        verses = self.segment_by_verses(text)
        chunks = []
        
        current_chunk = ""
        current_metadata = {}
        chunk_id = 0
        
        for verse in verses:
            verse_text = verse['text']
            
            # If verse fits in current chunk
            if len(current_chunk) + len(verse_text) <= chunk_size:
                current_chunk += verse_text + " "
                current_metadata.update(verse['metadata'])
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'metadata': current_metadata,
                        'type': 'verse_chunk'
                    })
                    chunk_id += 1
                
                # Start new chunk
                current_chunk = verse_text + " "
                current_metadata = verse['metadata'].copy()
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'id': chunk_id,
                'text': current_chunk.strip(),
                'metadata': current_metadata,
                'type': 'verse_chunk'
            })
        
        return chunks
    
    def process_text(self, text: str, preserve_structure: bool = True) -> str:
        """
        Main text processing pipeline.
        
        Args:
            text: Raw input text
            preserve_structure: Whether to preserve verse/chapter structure
            
        Returns:
            Processed text
        """
        # Clean the text
        processed = self.clean_text(text)
        
        # Extract and preserve structural information if requested
        if preserve_structure:
            structure = self.extract_structural_info(processed)
            logger.debug(f"Extracted structure: {structure}")
        
        logger.info(f"Processed text: {len(text)} -> {len(processed)} characters")
        return processed
    
    def validate_spiritual_content(self, text: str) -> Dict[str, Any]:
        """
        Validate that content appears to be legitimate spiritual text.
        
        Args:
            text: Text to validate
            
        Returns:
            Validation results with quality metrics
        """
        validation = {
            'is_spiritual': False,
            'confidence': 0.0,
            'detected_traditions': [],
            'sacred_term_count': 0,
            'structural_elements': 0
        }
        
        # Count sacred terms
        sacred_count = 0
        for terms in self.sacred_terms.values():
            for term in terms:
                sacred_count += len(re.findall(re.escape(term), text, re.IGNORECASE))
        
        validation['sacred_term_count'] = sacred_count
        
        # Check for structural elements
        structure = self.extract_structural_info(text)
        structural_count = sum(len(v) for v in structure.values())
        validation['structural_elements'] = structural_count
        
        # Calculate confidence
        text_length = len(text.split())
        if text_length > 0:
            sacred_density = sacred_count / text_length
            structure_density = structural_count / max(text_length / 100, 1)  # Per 100 words
            
            # Combine metrics for confidence score
            validation['confidence'] = min(1.0, (sacred_density * 10 + structure_density * 5))
            validation['is_spiritual'] = validation['confidence'] > 0.1
        
        # Detect traditions based on terminology
        if re.search(r'\b(?:krishna|gita|mahabharata|dharma|karma)\b', text, re.IGNORECASE):
            validation['detected_traditions'].append('hinduism')
        if re.search(r'\b(?:buddha|sangha|nirvana|dharma)\b', text, re.IGNORECASE):
            validation['detected_traditions'].append('buddhism')
        
        return validation
    
    def process_sanskrit_text(self, text: str) -> 'SanskritProcessingResult':
        """
        Process Sanskrit text with comprehensive analysis.
        
        Args:
            text: Sanskrit text to process
            
        Returns:
            SanskritProcessingResult with detailed analysis
        """
        from dataclasses import dataclass
        
        @dataclass
        class SanskritProcessingResult:
            original_text: str
            normalized_text: str
            contains_sanskrit: bool
            sanskrit_terms: List[str]
            devanagari_count: int
            transliteration: Optional[str] = None
        
        # Normalize the text
        normalized = self.normalize_unicode(text)
        
        # Check for Sanskrit/Devanagari content
        contains_sanskrit = bool(re.search(self.sanskrit_patterns['devanagari'], text))
        
        # Extract Sanskrit terms
        sanskrit_terms = re.findall(self.sanskrit_patterns['devanagari'], text)
        
        # Count Devanagari characters
        devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
        
        return SanskritProcessingResult(
            original_text=text,
            normalized_text=normalized,
            contains_sanskrit=contains_sanskrit,
            sanskrit_terms=sanskrit_terms,
            devanagari_count=devanagari_count
        )
    
    def detect_verse_boundaries(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect verse boundaries in spiritual texts.
        
        Args:
            text: Spiritual text with verses
            
        Returns:
            List of verse segments with metadata
        """
        verses = []
        
        # Pattern for verse numbers like ॥२.४७॥ or (2.47)
        verse_pattern = r'(?:॥(\d+)\.(\d+)॥|\((\d+)\.(\d+)\)|Verse\s+(\d+)\.(\d+))'
        
        # Split text by verse boundaries
        segments = re.split(verse_pattern, text)
        
        current_chapter = 1
        current_verse = 1
        
        for i, segment in enumerate(segments):
            if segment and segment.strip():
                # Check if this segment contains verse numbers
                verse_match = re.search(verse_pattern, segment)
                if verse_match:
                    groups = verse_match.groups()
                    if groups[0] and groups[1]:  # ॥च.व॥ format
                        current_chapter = int(groups[0])
                        current_verse = int(groups[1])
                    elif groups[2] and groups[3]:  # (च.व) format
                        current_chapter = int(groups[2])
                        current_verse = int(groups[3])
                    elif groups[4] and groups[5]:  # Verse च.व format
                        current_chapter = int(groups[4])
                        current_verse = int(groups[5])
                
                # Clean text content
                content = re.sub(verse_pattern, '', segment).strip()
                if content:
                    verses.append({
                        'chapter': current_chapter,
                        'verse': current_verse,
                        'text': content,
                        'contains_sanskrit': bool(re.search(self.sanskrit_patterns['devanagari'], content)),
                        'word_count': len(content.split())
                    })
                    current_verse += 1
        
        return verses
    
    def process_english_text(self, text: str) -> 'ProcessedText':
        """Process English text and preserve spiritual terms."""
        # Extract spiritual terms (using basic term detection)
        preserved_terms = []
        spiritual_terms = ['dharma', 'karma', 'moksha', 'yoga', 'guru', 'ashram', 'mantra', 'meditation', 'enlightenment']
        for term in spiritual_terms:
            if term.lower() in text.lower():
                preserved_terms.append(term)
        
        # Basic processing using existing clean_text method
        preprocessed = self.clean_text(text)
        
        # Create result object
        result = ProcessedText(text=preprocessed, preserved_terms=preserved_terms)
        return result
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text using clean_text method."""
        return self.clean_text(text)
    
    def clean_and_normalize(self, text: str) -> str:
        """Clean and normalize text by removing extra whitespace."""
        import re
        # Remove extra whitespace, newlines, and tabs
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
    
    def extract_metadata(self, text: str) -> TextMetadata:
        """Extract metadata from spiritual text."""
        # Basic metadata
        lines = text.split('\n')
        line_count = len(lines)
        word_count = len(text.split())
        character_count = len(text)
        
        # Initialize metadata object
        metadata = TextMetadata(
            line_count=line_count,
            word_count=word_count,
            character_count=character_count
        )
        
        # Look for chapter information
        chapter_reference = None
        for line in lines[:10]:  # Check first 10 lines
            if 'chapter' in line.lower() or 'adhyaya' in line.lower():
                chapter_reference = line.strip()
                metadata.chapter_reference = chapter_reference
                break
        
        # Extract source, chapter, and verse from text
        import re
        
        # Look for Bhagavad Gita references
        if 'bhagavad gita' in text.lower() or 'gita' in text.lower():
            metadata.source = "Bhagavad Gita"
            metadata.text_type = "verse"
            
            # Extract chapter number
            chapter_match = re.search(r'chapter\s*(\d+)', text.lower())
            if chapter_match:
                metadata.chapter = int(chapter_match.group(1))
            
            # Extract verse number  
            verse_match = re.search(r'verse\s*(\d+)', text.lower())
            if verse_match:
                metadata.verse = int(verse_match.group(1))
        
        # Look for Mahabharata references
        elif 'mahabharata' in text.lower():
            metadata.source = "Mahabharata"
            metadata.text_type = "section"
        
        # Look for Srimad Bhagavatam references
        elif 'bhagavatam' in text.lower() or 'srimad' in text.lower():
            metadata.source = "Srimad Bhagavatam"
            metadata.text_type = "verse"
        
        # Check for Sanskrit content
        sanskrit_matches = re.findall(self.sanskrit_patterns['devanagari'], text)
        metadata.contains_sanskrit = len(sanskrit_matches) > 0
        metadata.sanskrit_terms_count = len(sanskrit_matches)
        
        return metadata


# Helper class for process_english_text result  
class ProcessedText:
    """Result object for processed text with preserved terms."""
    def __init__(self, text: str, preserved_terms: List[str]):
        self.text = text
        self.preserved_terms = preserved_terms


# Factory function for creating the appropriate processor
def create_text_processor(domain: str = None) -> EnhancedTextProcessor:
    """
    Create a text processor instance.
    
    Args:
        domain: Optional domain hint for optimization
        
    Returns:
        EnhancedTextProcessor instance with multi-domain support
    """
    return EnhancedTextProcessor()


# Convenience functions for backward compatibility
def process_spiritual_text(text: str, preserve_structure: bool = True) -> str:
    """Process spiritual text using the enhanced processor."""
    processor = create_text_processor()
    return processor.spiritual_processor.process_text(text, preserve_structure)


def chunk_spiritual_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
    """Chunk spiritual text using verse-aware chunking."""
    processor = create_text_processor()
    return processor.spiritual_processor.chunk_text(text, chunk_size, overlap)


def process_multi_domain_text(text: str, source: str = "", domain: str = None) -> ProcessingResult:
    """
    Process text using multi-domain capabilities.
    
    Args:
        text: Input text
        source: Source identifier
        domain: Target domain (auto-detected if None)
        
    Returns:
        ProcessingResult with domain-specific processing
    """
    processor = create_text_processor()
    return processor.process_text_with_domain(text, source, domain)
