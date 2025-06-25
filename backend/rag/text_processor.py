"""
Advanced Text Processing for Spiritual Texts

Enhanced chunking strategy that preserves verse boundaries and Sanskrit terms
with specialized handling for different types of spiritual literature.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import unicodedata
from enum import Enum

logger = logging.getLogger(__name__)


class TextType(Enum):
    """Types of spiritual texts with different processing strategies"""
    BHAGAVAD_GITA = "bhagavad_gita"
    MAHABHARATA = "mahabharata"
    SRIMAD_BHAGAVATAM = "srimad_bhagavatam"
    UPANISHADS = "upanishads"
    VEDAS = "vedas"
    PURANAS = "puranas"
    UNKNOWN = "unknown"


@dataclass
class VerseReference:
    """Represents a specific verse reference in spiritual text"""
    text_type: TextType
    book: Optional[str] = None
    chapter: Optional[str] = None
    verse: Optional[str] = None
    section: Optional[str] = None
    
    def __str__(self) -> str:
        """Format verse reference for citation"""
        if self.text_type == TextType.BHAGAVAD_GITA:
            return f"Bhagavad Gita {self.chapter}.{self.verse}"
        elif self.text_type == TextType.MAHABHARATA:
            return f"Mahabharata Book {self.book}, Section {self.section}"
        elif self.text_type == TextType.SRIMAD_BHAGAVATAM:
            return f"Srimad Bhagavatam {self.book}.{self.chapter}.{self.verse}"
        else:
            parts = [str(self.text_type.value)]
            if self.book: parts.append(f"Book {self.book}")
            if self.chapter: parts.append(f"Chapter {self.chapter}")
            if self.verse: parts.append(f"Verse {self.verse}")
            return " ".join(parts)


@dataclass
class EnhancedTextChunk:
    """Enhanced text chunk with comprehensive metadata"""
    content: str
    chunk_id: str
    source_file: str
    text_type: TextType
    verse_references: List[VerseReference]
    sanskrit_terms: List[str]
    semantic_tags: List[str]
    chunk_metadata: Dict[str, Any]
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'content': self.content,
            'chunk_id': self.chunk_id,
            'source_file': self.source_file,
            'text_type': self.text_type.value,
            'verse_references': [
                {
                    'text_type': ref.text_type.value,
                    'book': ref.book,
                    'chapter': ref.chapter,
                    'verse': ref.verse,
                    'section': ref.section
                } for ref in self.verse_references
            ],
            'sanskrit_terms': self.sanskrit_terms,
            'semantic_tags': self.semantic_tags,
            'chunk_metadata': self.chunk_metadata,
            'quality_score': self.quality_score
        }


class AdvancedSpiritualTextProcessor:
    """
    Advanced text processor with enhanced chunking strategies
    specifically designed for different types of spiritual literature.
    """
    
    def __init__(self):
        # Enhanced Sanskrit term patterns with phonetic variations
        self.sanskrit_patterns = {
            'core_concepts': [
                r'\b(?:dharma|karma|moksha|samsara|bhakti|yoga|atman|brahman|nirvana)\b',
                r'\b(?:ahimsa|tapas|seva|sadhana|sannyasa|grihasta|brahmacharya)\b',
                r'\b(?:puja|yajna|japa|kirtan|satsang|darshan|prasadam?)\b'
            ],
            'deities': [
                r'\b(?:Krishna|Krsna|Arjuna|Bhagavan|Vishnu|Visnu|Shiva|Siva)\b',
                r'\b(?:Rama|Hanuman|Ganesha|Ganesa|Durga|Lakshmi|Laksmi)\b',
                r'\b(?:Brahma|Indra|Varuna|Agni|Vayu|Surya)\b'
            ],
            'texts': [
                r'\b(?:Gita|Bhagavad[- ]?Gita|Mahabharata|Bharata)\b',
                r'\b(?:Bhagavatam|Bhagavata[- ]?Purana|Srimad[- ]?Bhagavatam)\b',
                r'\b(?:Upanishads?|Vedas?|Rig[- ]?Veda|Sama[- ]?Veda|Yajur[- ]?Veda|Atharva[- ]?Veda)\b',
                r'\b(?:Ramayana|Puranas?|Tantras?)\b'
            ],
            'philosophy': [
                r'\b(?:advaita|dvaita|vishishtadvaita|sankhya|vedanta)\b',
                r'\b(?:maya|lila|rasa|bhava|prema|vairagya)\b',
                r'\b(?:guna|rajas|sattva|tamas|prakriti|purusha)\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.sanskrit_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        
        # Text type specific verse patterns
        self.verse_patterns = {
            TextType.BHAGAVAD_GITA: [
                r'(\d+)\.(\d+)',  # Chapter.Verse
                r'Chapter\s+(\d+)',  # Chapter headers
                r'Verse\s+(\d+)'  # Verse headers
            ],
            TextType.MAHABHARATA: [
                r'Book\s+(\d+).*?Section\s+(\d+)',  # Book X Section Y
                r'Book\s+(\d+)\s+Section\s+(\d+)',  # Book X Section Y (direct)
                r'Vana\s+Parva',  # Parva names
                r'Sabha\s+Parva',
                r'Adi\s+Parva'
            ],
            TextType.SRIMAD_BHAGAVATAM: [
                r'Canto\s+(\d+).*?Chapter\s+(\d+).*?Verse\s+(\d+)',  # Full reference
                r'(\d+)\.(\d+)\.(\d+)'  # Canto.Chapter.Verse
            ]
        }
        
        # Semantic tagging patterns
        self.semantic_patterns = {
            'duty_dharma': [r'\b(?:duty|dharma|righteousness|obligation)\b'],
            'action_karma': [r'\b(?:action|karma|deed|work|activity)\b'],
            'devotion_bhakti': [r'\b(?:devotion|bhakti|love|worship|surrender)\b'],
            'knowledge_jnana': [r'\b(?:knowledge|wisdom|jnana|understanding|realization)\b'],
            'meditation_dhyana': [r'\b(?:meditation|dhyana|contemplation|focus)\b'],
            'detachment': [r'\b(?:detachment|renunciation|vairagya|non-attachment)\b'],
            'divine_nature': [r'\b(?:divine|god|supreme|absolute|eternal|infinite)\b'],
            'material_world': [r'\b(?:material|world|maya|illusion|temporary)\b']
        }
        
        self.compiled_semantic_patterns = {
            tag: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for tag, patterns in self.semantic_patterns.items()
        }
    
    def identify_text_type(self, content: str, filename: str) -> TextType:
        """Identify the type of spiritual text"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        combined = f"{content_lower} {filename_lower}"
        
        # Check for specific text patterns
        if any(term in combined for term in ['bhagavad gita', 'gita', 'krishna arjuna']):
            return TextType.BHAGAVAD_GITA
        elif any(term in combined for term in ['mahabharata', 'bharata', 'pandava']):
            return TextType.MAHABHARATA
        elif any(term in combined for term in ['srimad bhagavatam', 'bhagavatam', 'bhagavata purana']):
            return TextType.SRIMAD_BHAGAVATAM
        elif any(term in combined for term in ['upanishad', 'isa upanishad', 'mundaka']):
            return TextType.UPANISHADS
        elif any(term in combined for term in ['rig veda', 'sama veda', 'yajur veda', 'atharva veda', 'vedic']):
            return TextType.VEDAS
        elif any(term in combined for term in ['purana', 'vishnu purana', 'shiva purana']):
            return TextType.PURANAS
        else:
            return TextType.UNKNOWN
    
    def extract_sanskrit_terms(self, text: str) -> Dict[str, List[str]]:
        """Extract Sanskrit terms by category"""
        terms_by_category = {}
        
        for category, patterns in self.compiled_patterns.items():
            terms = []
            for pattern in patterns:
                matches = pattern.findall(text)
                terms.extend(matches)
            
            # Remove duplicates and normalize
            terms = list(set(term.strip() for term in terms if term.strip()))
            if terms:
                terms_by_category[category] = terms
        
        return terms_by_category
    
    def extract_verse_references(self, text: str, text_type: TextType) -> List[VerseReference]:
        """Extract verse references based on text type"""
        references = []
        
        if text_type not in self.verse_patterns:
            return references
        
        patterns = self.verse_patterns[text_type]
        lines = text.split('\n')
        
        for line in lines:
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    
                    if text_type == TextType.BHAGAVAD_GITA and len(groups) >= 2:
                        references.append(VerseReference(
                            text_type=text_type,
                            chapter=groups[0],
                            verse=groups[1]
                        ))
                    elif text_type == TextType.MAHABHARATA and len(groups) >= 2:
                        references.append(VerseReference(
                            text_type=text_type,
                            book=groups[0],
                            section=groups[1]
                        ))
                    elif text_type == TextType.SRIMAD_BHAGAVATAM and len(groups) >= 3:
                        references.append(VerseReference(
                            text_type=text_type,
                            book=groups[0],
                            chapter=groups[1],
                            verse=groups[2]
                        ))
        
        return references
    
    def extract_semantic_tags(self, text: str) -> List[str]:
        """Extract semantic tags based on content themes"""
        tags = []
        text_lower = text.lower()
        
        for tag, patterns in self.compiled_semantic_patterns.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    tags.append(tag)
                    break  # Found this tag, move to next
        
        return tags
    
    def calculate_chunk_quality(self, chunk: EnhancedTextChunk) -> float:
        """Calculate quality score for a text chunk"""
        score = 1.0
        
        # Sanskrit term density (bonus for authentic content)
        total_terms = sum(len(terms) for terms in chunk.sanskrit_terms)
        word_count = len(chunk.content.split())
        if word_count > 0:
            term_density = total_terms / word_count
            score += min(term_density * 2, 0.5)  # Max bonus of 0.5
        
        # Verse reference bonus
        if chunk.verse_references:
            score += 0.2
        
        # Semantic tag bonus (shows thematic coherence)
        score += len(chunk.semantic_tags) * 0.1
        
        # Content length penalty/bonus (prefer moderate length)
        if 100 <= len(chunk.content) <= 1000:
            score += 0.1
        elif len(chunk.content) < 50:
            score -= 0.3
        elif len(chunk.content) > 2000:
            score -= 0.2
        
        return min(score, 2.0)  # Cap at 2.0
    
    def preserve_verse_boundaries(self, text: str, text_type: TextType) -> List[str]:
        """Split text while preserving verse boundaries"""
        if text_type not in self.verse_patterns:
            # Fallback to paragraph splitting
            return [p.strip() for p in text.split('\n\n') if p.strip()]
        
        patterns = self.verse_patterns[text_type]
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        
        for line in lines:
            is_boundary = False
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_boundary = True
                    break
            
            if is_boundary and current_chunk:
                # Save current chunk
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
        
        return chunks
    
    def intelligent_chunk_splitting(self, text: str, text_type: TextType, 
                                   max_chunk_size: int = 800) -> List[str]:
        """Intelligently split text based on content structure"""
        # First, split by verse boundaries
        verse_chunks = self.preserve_verse_boundaries(text, text_type)
        
        final_chunks = []
        
        for chunk in verse_chunks:
            if len(chunk) <= max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Need to split further while preserving meaning
                # Split by sentences, then combine to fit max size
                sentences = re.split(r'[.!?]+', chunk)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    if len(current_chunk + sentence) <= max_chunk_size:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            final_chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    final_chunks.append(current_chunk.strip())
        
        return final_chunks
    
    def process_text_advanced(self, text: str, source_file: str, 
                            max_chunk_size: int = 800) -> List[EnhancedTextChunk]:
        """Advanced text processing with enhanced chunking strategy"""
        logger.info(f"Processing {source_file} with advanced chunking strategy")
        
        # Preprocess text
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Identify text type
        text_type = self.identify_text_type(text, source_file)
        logger.info(f"Identified text type: {text_type.value}")
        
        # Split into chunks intelligently
        chunk_texts = self.intelligent_chunk_splitting(text, text_type, max_chunk_size)
        
        enhanced_chunks = []
        
        for i, chunk_text in enumerate(chunk_texts):
            # Extract metadata
            sanskrit_terms = self.extract_sanskrit_terms(chunk_text)
            verse_references = self.extract_verse_references(chunk_text, text_type)
            semantic_tags = self.extract_semantic_tags(chunk_text)
            
            # Create enhanced chunk
            chunk = EnhancedTextChunk(
                content=chunk_text,
                chunk_id=f"{Path(source_file).stem}_{text_type.value}_{i:04d}",
                source_file=source_file,
                text_type=text_type,
                verse_references=verse_references,
                sanskrit_terms=[term for terms in sanskrit_terms.values() for term in terms],
                semantic_tags=semantic_tags,
                chunk_metadata={
                    'chunk_index': i,
                    'total_chunks': len(chunk_texts),
                    'character_count': len(chunk_text),
                    'word_count': len(chunk_text.split()),
                    'sanskrit_by_category': sanskrit_terms,
                    'verse_count': len(verse_references),
                    'processing_version': '2.0'
                }
            )
            
            # Calculate quality score
            chunk.quality_score = self.calculate_chunk_quality(chunk)
            
            enhanced_chunks.append(chunk)
        
        logger.info(f"Created {len(enhanced_chunks)} enhanced chunks from {source_file}")
        return enhanced_chunks
    
    def export_chunks_for_vector_storage(self, chunks: List[EnhancedTextChunk]) -> List[Dict[str, Any]]:
        """Export chunks in format suitable for vector storage"""
        return [chunk.to_dict() for chunk in chunks]
    
    def filter_high_quality_chunks(self, chunks: List[EnhancedTextChunk], 
                                 min_quality: float = 1.0) -> List[EnhancedTextChunk]:
        """Filter chunks based on quality score"""
        return [chunk for chunk in chunks if chunk.quality_score >= min_quality]
