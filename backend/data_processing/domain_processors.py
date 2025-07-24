#!/usr/bin/env python3
"""
Domain-Specific Text Processors for Vimarsh Multi-Personality Platform

This module provides specialized text processing for different personality domains:
- Spiritual: Sacred texts, scriptures, devotional content
- Scientific: Research papers, theories, technical documentation
- Historical: Speeches, letters, historical documents
- Philosophical: Philosophical works, treatises, meditations
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
import unicodedata

logger = logging.getLogger(__name__)


@dataclass
class ProcessedChunk:
    """Represents a processed text chunk with domain-specific metadata"""
    id: str
    text: str
    domain: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)
    key_terms: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    chunk_type: str = "paragraph"  # paragraph, verse, section, etc.
    
    def __post_init__(self):
        if not self.id:
            self.id = f"{self.domain}_{hash(self.text[:100])}_{datetime.now().timestamp()}"


@dataclass
class ProcessingResult:
    """Result of domain-specific text processing"""
    chunks: List[ProcessedChunk]
    metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class DomainProcessor(ABC):
    """Abstract base class for domain-specific text processors"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.domain = self.get_domain()
        
    @abstractmethod
    def get_domain(self) -> str:
        """Return the domain this processor handles"""
        pass
    
    @abstractmethod
    def process_text(self, text: str, source: str = "", metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process text and return domain-specific chunks"""
        pass
    
    @abstractmethod
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract domain-specific key terms"""
        pass
    
    @abstractmethod
    def calculate_quality_score(self, text: str) -> float:
        """Calculate quality score for the text"""
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        # Remove control characters
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into chunks with domain-aware boundaries"""
        # Default implementation - can be overridden by subclasses
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk = ' '.join(chunk_words)
            chunks.append(chunk)
            
        return chunks


class SpiritualProcessor(DomainProcessor):
    """Processor for spiritual and religious texts"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sacred_terms = {
            'hindu': ['dharma', 'karma', 'moksha', 'atman', 'brahman', 'yoga', 'mantra', 'puja', 'bhakti', 'jnana'],
            'buddhist': ['buddha', 'nirvana', 'sangha', 'dukkha', 'sutra', 'zen', 'mindfulness', 'meditation'],
            'christian': ['christ', 'gospel', 'prayer', 'faith', 'grace', 'salvation', 'holy spirit', 'trinity'],
            'islamic': ['allah', 'quran', 'islam', 'salat', 'zakat', 'hajj', 'ramadan', 'imam'],
            'general': ['divine', 'sacred', 'soul', 'spirit', 'transcendence', 'consciousness', 'awakening']
        }
        
        self.verse_patterns = [
            r'\d+\.\d+',  # Chapter.verse (e.g., 2.47)
            r'Chapter \d+, Verse \d+',
            r'Verse \d+',
            r'Shloka \d+'
        ]
    
    def get_domain(self) -> str:
        return "spiritual"
    
    def process_text(self, text: str, source: str = "", metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process spiritual text with verse-aware chunking"""
        cleaned_text = self.clean_text(text)
        chunks = []
        
        # Try to split by verses first
        verse_chunks = self._split_by_verses(cleaned_text)
        if not verse_chunks:
            # Fall back to paragraph-based chunking
            verse_chunks = self._split_by_paragraphs(cleaned_text)
        
        for i, chunk_text in enumerate(verse_chunks):
            if not chunk_text.strip():
                continue
                
            chunk = ProcessedChunk(
                id=f"spiritual_{i}_{hash(chunk_text[:50])}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata=metadata or {},
                citations=self._extract_citations(chunk_text),
                key_terms=self.extract_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type=self._determine_chunk_type(chunk_text)
            )
            chunks.append(chunk)
        
        return ProcessingResult(
            chunks=chunks,
            metadata={
                'total_chunks': len(chunks),
                'avg_quality': sum(c.quality_score for c in chunks) / len(chunks) if chunks else 0,
                'traditions_detected': self._detect_traditions(cleaned_text)
            },
            quality_metrics=self._calculate_overall_quality(chunks)
        )
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract spiritual key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for tradition, terms in self.sacred_terms.items():
            for term in terms:
                if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                    found_terms.append(term)
        
        return found_terms
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate quality score based on spiritual content indicators"""
        score = 0.0
        
        # Length factor
        word_count = len(text.split())
        if 10 <= word_count <= 500:
            score += 0.3
        
        # Sacred terms density
        key_terms = self.extract_key_terms(text)
        term_density = len(key_terms) / max(word_count, 1)
        score += min(0.4, term_density * 10)
        
        # Citation presence
        if self._extract_citations(text):
            score += 0.2
        
        # Coherence (simple heuristic)
        if self._has_coherent_structure(text):
            score += 0.1
        
        return min(1.0, score)
    
    def _split_by_verses(self, text: str) -> List[str]:
        """Split text by verse markers"""
        for pattern in self.verse_patterns:
            if re.search(pattern, text):
                # Split by verse pattern
                verses = re.split(f'({pattern})', text)
                chunks = []
                current_chunk = ""
                
                for part in verses:
                    if re.match(pattern, part):
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = part + " "
                    else:
                        current_chunk += part
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                return [c for c in chunks if c.strip()]
        
        return []
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract scripture citations"""
        citations = []
        for pattern in self.verse_patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        return citations
    
    def _determine_chunk_type(self, text: str) -> str:
        """Determine the type of spiritual chunk"""
        if any(re.search(pattern, text) for pattern in self.verse_patterns):
            return "verse"
        elif re.search(r'prayer|invocation|mantra', text.lower()):
            return "prayer"
        elif re.search(r'commentary|explanation|meaning', text.lower()):
            return "commentary"
        else:
            return "teaching"
    
    def _detect_traditions(self, text: str) -> List[str]:
        """Detect spiritual traditions in text"""
        text_lower = text.lower()
        traditions = []
        
        for tradition, terms in self.sacred_terms.items():
            if any(re.search(r'\b' + re.escape(term) + r'\b', text_lower) for term in terms):
                traditions.append(tradition)
        
        return traditions
    
    def _has_coherent_structure(self, text: str) -> bool:
        """Check if text has coherent structure"""
        # Simple heuristic: check for proper sentence structure
        sentences = re.split(r'[.!?]+', text)
        return len(sentences) >= 2 and all(len(s.strip()) > 10 for s in sentences[:3])
    
    def _calculate_overall_quality(self, chunks: List[ProcessedChunk]) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        if not chunks:
            return {}
        
        return {
            'avg_quality': sum(c.quality_score for c in chunks) / len(chunks),
            'min_quality': min(c.quality_score for c in chunks),
            'max_quality': max(c.quality_score for c in chunks),
            'chunks_with_citations': sum(1 for c in chunks if c.citations) / len(chunks),
            'avg_key_terms': sum(len(c.key_terms) for c in chunks) / len(chunks)
        }


class ScientificProcessor(DomainProcessor):
    """Processor for scientific texts and research papers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.scientific_terms = [
            'hypothesis', 'theory', 'experiment', 'data', 'analysis', 'research',
            'observation', 'evidence', 'method', 'conclusion', 'peer review',
            'quantum', 'relativity', 'evolution', 'genetics', 'molecule', 'atom'
        ]
        
        self.citation_patterns = [
            r'\([A-Za-z]+\s+et\s+al\.,?\s+\d{4}\)',  # (Einstein et al., 1905)
            r'\([A-Za-z]+,?\s+\d{4}\)',  # (Einstein, 1905)
            r'\[\d+\]',  # [1]
            r'doi:\s*[\d\.]+\/[\w\.\-\/]+'  # DOI
        ]
    
    def get_domain(self) -> str:
        return "scientific"
    
    def process_text(self, text: str, source: str = "", metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process scientific text with section-aware chunking"""
        cleaned_text = self.clean_text(text)
        chunks = []
        
        # Split by sections (Abstract, Introduction, Methods, etc.)
        section_chunks = self._split_by_sections(cleaned_text)
        if not section_chunks:
            section_chunks = self._split_by_paragraphs(cleaned_text)
        
        for i, chunk_text in enumerate(section_chunks):
            if not chunk_text.strip():
                continue
                
            chunk = ProcessedChunk(
                id=f"scientific_{i}_{hash(chunk_text[:50])}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata=metadata or {},
                citations=self._extract_citations(chunk_text),
                key_terms=self.extract_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type=self._determine_chunk_type(chunk_text)
            )
            chunks.append(chunk)
        
        return ProcessingResult(
            chunks=chunks,
            metadata={
                'total_chunks': len(chunks),
                'avg_quality': sum(c.quality_score for c in chunks) / len(chunks) if chunks else 0,
                'has_citations': any(c.citations for c in chunks),
                'scientific_fields': self._detect_fields(cleaned_text)
            },
            quality_metrics=self._calculate_overall_quality(chunks)
        )
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract scientific key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.scientific_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                found_terms.append(term)
        
        return found_terms
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate quality score for scientific content"""
        score = 0.0
        
        # Length factor
        word_count = len(text.split())
        if 50 <= word_count <= 1000:
            score += 0.2
        
        # Scientific terms density
        key_terms = self.extract_key_terms(text)
        term_density = len(key_terms) / max(word_count, 1)
        score += min(0.3, term_density * 20)
        
        # Citation presence
        citations = self._extract_citations(text)
        if citations:
            score += min(0.3, len(citations) * 0.1)
        
        # Technical language indicators
        if self._has_technical_language(text):
            score += 0.2
        
        return min(1.0, score)
    
    def _split_by_sections(self, text: str) -> List[str]:
        """Split by academic paper sections"""
        section_headers = [
            r'Abstract', r'Introduction', r'Methods?', r'Results?', 
            r'Discussion', r'Conclusion', r'References?', r'Acknowledgments?'
        ]
        
        pattern = r'\n\s*(' + '|'.join(section_headers) + r')\s*\n'
        if re.search(pattern, text, re.IGNORECASE):
            sections = re.split(pattern, text, flags=re.IGNORECASE)
            return [s.strip() for s in sections if s.strip()]
        
        return []
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract scientific citations"""
        citations = []
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        return citations
    
    def _determine_chunk_type(self, text: str) -> str:
        """Determine the type of scientific chunk"""
        text_lower = text.lower()
        
        if re.search(r'abstract', text_lower):
            return "abstract"
        elif re.search(r'method|procedure|experiment', text_lower):
            return "methodology"
        elif re.search(r'result|finding|data', text_lower):
            return "results"
        elif re.search(r'discussion|analysis|interpretation', text_lower):
            return "discussion"
        elif re.search(r'conclusion|summary', text_lower):
            return "conclusion"
        else:
            return "content"
    
    def _detect_fields(self, text: str) -> List[str]:
        """Detect scientific fields"""
        fields = {
            'physics': ['quantum', 'relativity', 'particle', 'energy', 'force'],
            'biology': ['evolution', 'genetics', 'cell', 'organism', 'species'],
            'chemistry': ['molecule', 'atom', 'reaction', 'compound', 'element'],
            'psychology': ['behavior', 'cognitive', 'mental', 'brain', 'mind']
        }
        
        text_lower = text.lower()
        detected_fields = []
        
        for field, terms in fields.items():
            if any(re.search(r'\b' + re.escape(term) + r'\b', text_lower) for term in terms):
                detected_fields.append(field)
        
        return detected_fields
    
    def _has_technical_language(self, text: str) -> bool:
        """Check for technical language indicators"""
        technical_indicators = [
            r'\b\d+\.\d+\b',  # Numbers with decimals
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\bp\s*<\s*0\.\d+',  # Statistical significance
            r'\b\w+\s*=\s*\d+',  # Equations
        ]
        
        return any(re.search(pattern, text) for pattern in technical_indicators)
    
    def _calculate_overall_quality(self, chunks: List[ProcessedChunk]) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        if not chunks:
            return {}
        
        return {
            'avg_quality': sum(c.quality_score for c in chunks) / len(chunks),
            'citation_coverage': sum(1 for c in chunks if c.citations) / len(chunks),
            'avg_key_terms': sum(len(c.key_terms) for c in chunks) / len(chunks),
            'technical_density': sum(1 for c in chunks if self._has_technical_language(c.text)) / len(chunks)
        }


class BaseDomainProcessor(ABC):
    """Base class for domain-specific text processors"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.chunk_size = 1000  # Default chunk size
        self.overlap_size = 100  # Default overlap
        
    @abstractmethod
    def process_text(self, text: str, source: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process text for the specific domain"""
        pass
    
    @abstractmethod
    def extract_citations(self, text: str) -> List[str]:
        """Extract domain-specific citations"""
        pass
    
    @abstractmethod
    def identify_key_terms(self, text: str) -> List[str]:
        """Identify domain-specific key terms"""
        pass
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but preserve punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/]', '', text)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, preserve_boundaries: List[str] = None) -> List[str]:
        """Chunk text while preserving important boundaries"""
        if preserve_boundaries is None:
            preserve_boundaries = ['\n\n', '. ', '! ', '? ']
        
        chunks = []
        current_chunk = ""
        
        sentences = re.split(r'([.!?]+\s+)', text)
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i] if i < len(sentences) else ""
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            
            full_sentence = sentence + punctuation
            
            if len(current_chunk) + len(full_sentence) <= self.chunk_size:
                current_chunk += full_sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = full_sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate basic quality score for text"""
        score = 100.0
        
        # Length check
        if len(text) < 50:
            score -= 30
        elif len(text) < 100:
            score -= 15
        
        # Readability check (simple)
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        if sentences > 0:
            avg_sentence_length = words / sentences
            if avg_sentence_length > 30:
                score -= 10
            elif avg_sentence_length < 5:
                score -= 15
        
        # Character diversity
        unique_chars = len(set(text.lower()))
        if unique_chars < 10:
            score -= 20
        
        return max(0.0, min(100.0, score))


class SpiritualTextProcessor(BaseDomainProcessor):
    """Processor for spiritual and religious texts"""
    
    def __init__(self):
        super().__init__("spiritual")
        self.sacred_terms = [
            'dharma', 'karma', 'moksha', 'nirvana', 'samsara', 'atman', 'brahman',
            'yoga', 'meditation', 'devotion', 'bhakti', 'jnana', 'seva', 'ahimsa',
            'compassion', 'wisdom', 'enlightenment', 'liberation', 'divine', 'sacred',
            'prayer', 'worship', 'faith', 'grace', 'blessing', 'soul', 'spirit'
        ]
        
    def process_text(self, text: str, source: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process spiritual text with verse and chapter awareness"""
        if metadata is None:
            metadata = {}
            
        cleaned_text = self.clean_text(text)
        
        # Check for verse structure
        has_verses = bool(re.search(r'\d+\.\d+|\d+:\d+|Chapter \d+|Verse \d+', cleaned_text))
        
        if has_verses:
            chunks = self._chunk_by_verses(cleaned_text)
        else:
            chunks = self.chunk_text(cleaned_text)
        
        processed_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk = ProcessedChunk(
                id=f"spiritual_{source}_{i}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata={
                    **metadata,
                    'has_verses': has_verses,
                    'chunk_index': i
                },
                citations=self.extract_citations(chunk_text),
                key_terms=self.identify_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type="verse" if has_verses else "paragraph"
            )
            processed_chunks.append(chunk)
        
        return ProcessingResult(
            chunks=processed_chunks,
            metadata={
                'total_chunks': len(processed_chunks),
                'has_verse_structure': has_verses,
                'domain': self.domain,
                'source': source
            },
            quality_metrics={
                'avg_quality': sum(c.quality_score for c in processed_chunks) / len(processed_chunks),
                'sacred_term_density': self._calculate_sacred_term_density(cleaned_text)
            }
        )
    
    def _chunk_by_verses(self, text: str) -> List[str]:
        """Chunk text by verses or chapters"""
        # Split by verse patterns
        verse_pattern = r'(\d+\.\d+|\d+:\d+|Chapter \d+|Verse \d+)'
        parts = re.split(verse_pattern, text)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(parts), 2):
            verse_marker = parts[i - 1] if i > 0 else ""
            content = parts[i] if i < len(parts) else ""
            
            verse_text = (verse_marker + " " + content).strip()
            
            if len(current_chunk) + len(verse_text) <= self.chunk_size:
                current_chunk += "\n" + verse_text if current_chunk else verse_text
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = verse_text
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract spiritual text citations"""
        citations = []
        
        # Bhagavad Gita style (2.47, BG 2.47)
        bg_citations = re.findall(r'(?:BG\s*)?(\d+\.\d+)', text)
        citations.extend([f"BG {cite}" for cite in bg_citations])
        
        # Chapter:Verse style
        chapter_verse = re.findall(r'(\d+:\d+)', text)
        citations.extend(chapter_verse)
        
        # Book references
        book_refs = re.findall(r'(Bhagavad Gita|Mahabharata|Ramayana|Upanishads|Vedas)', text, re.IGNORECASE)
        citations.extend(book_refs)
        
        return list(set(citations))
    
    def identify_key_terms(self, text: str) -> List[str]:
        """Identify spiritual key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.sacred_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        # Sanskrit terms (basic detection)
        sanskrit_pattern = r'\b[a-zA-Z]*(?:dharma|karma|yoga|moksha|atman|brahman)[a-zA-Z]*\b'
        sanskrit_terms = re.findall(sanskrit_pattern, text, re.IGNORECASE)
        found_terms.extend(sanskrit_terms)
        
        return list(set(found_terms))
    
    def _calculate_sacred_term_density(self, text: str) -> float:
        """Calculate density of sacred terms in text"""
        words = text.split()
        if not words:
            return 0.0
        
        sacred_count = sum(1 for word in words if word.lower() in [term.lower() for term in self.sacred_terms])
        return (sacred_count / len(words)) * 100


class ScientificTextProcessor(BaseDomainProcessor):
    """Processor for scientific texts and research papers"""
    
    def __init__(self):
        super().__init__("scientific")
        self.scientific_terms = [
            'theory', 'hypothesis', 'experiment', 'observation', 'data', 'analysis',
            'research', 'study', 'method', 'result', 'conclusion', 'evidence',
            'physics', 'chemistry', 'biology', 'mathematics', 'relativity',
            'quantum', 'energy', 'matter', 'force', 'field', 'particle',
            'equation', 'formula', 'principle', 'law', 'theorem'
        ]
        
    def process_text(self, text: str, source: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process scientific text with section awareness"""
        if metadata is None:
            metadata = {}
            
        cleaned_text = self.clean_text(text)
        
        # Check for academic structure
        has_sections = bool(re.search(r'Abstract|Introduction|Method|Results|Discussion|Conclusion', cleaned_text, re.IGNORECASE))
        
        if has_sections:
            chunks = self._chunk_by_sections(cleaned_text)
        else:
            chunks = self.chunk_text(cleaned_text)
        
        processed_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk = ProcessedChunk(
                id=f"scientific_{source}_{i}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata={
                    **metadata,
                    'has_sections': has_sections,
                    'chunk_index': i
                },
                citations=self.extract_citations(chunk_text),
                key_terms=self.identify_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type="section" if has_sections else "paragraph"
            )
            processed_chunks.append(chunk)
        
        return ProcessingResult(
            chunks=processed_chunks,
            metadata={
                'total_chunks': len(processed_chunks),
                'has_academic_structure': has_sections,
                'domain': self.domain,
                'source': source
            },
            quality_metrics={
                'avg_quality': sum(c.quality_score for c in processed_chunks) / len(processed_chunks),
                'scientific_term_density': self._calculate_scientific_term_density(cleaned_text)
            }
        )
    
    def _chunk_by_sections(self, text: str) -> List[str]:
        """Chunk text by academic sections"""
        section_pattern = r'(Abstract|Introduction|Method|Results|Discussion|Conclusion|References)'
        parts = re.split(section_pattern, text, flags=re.IGNORECASE)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(parts), 2):
            section_header = parts[i - 1] if i > 0 else ""
            content = parts[i] if i < len(parts) else ""
            
            section_text = (section_header + "\n" + content).strip()
            
            if len(current_chunk) + len(section_text) <= self.chunk_size:
                current_chunk += "\n\n" + section_text if current_chunk else section_text
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = section_text
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract scientific citations"""
        citations = []
        
        # Author-year format (Einstein, 1905)
        author_year = re.findall(r'\(([A-Za-z]+(?:\s+et\s+al\.)?),\s*(\d{4})\)', text)
        citations.extend([f"({author}, {year})" for author, year in author_year])
        
        # Numbered citations [1], [2]
        numbered = re.findall(r'\[(\d+)\]', text)
        citations.extend([f"[{num}]" for num in numbered])
        
        # DOI references
        dois = re.findall(r'doi:\s*([0-9\.]+/[A-Za-z0-9\.\-/]+)', text)
        citations.extend([f"doi:{doi}" for doi in dois])
        
        return list(set(citations))
    
    def identify_key_terms(self, text: str) -> List[str]:
        """Identify scientific key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.scientific_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _calculate_scientific_term_density(self, text: str) -> float:
        """Calculate density of scientific terms in text"""
        words = text.split()
        if not words:
            return 0.0
        
        scientific_count = sum(1 for word in words if word.lower() in [term.lower() for term in self.scientific_terms])
        return (scientific_count / len(words)) * 100
    
    def _calculate_overall_quality(self, chunks: List[ProcessedChunk]) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        if not chunks:
            return {}
        
        return {
            'avg_quality': sum(c.quality_score for c in chunks) / len(chunks),
            'citation_coverage': sum(1 for c in chunks if c.citations) / len(chunks),
            'avg_key_terms': sum(len(c.key_terms) for c in chunks) / len(chunks),
            'technical_density': sum(1 for c in chunks if self._has_technical_language(c.text)) / len(chunks)
        }


class HistoricalProcessor(DomainProcessor):
    """Processor for historical texts and documents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.historical_terms = [
            'history', 'historical', 'ancient', 'medieval', 'renaissance', 'revolution',
            'war', 'battle', 'empire', 'kingdom', 'dynasty', 'civilization',
            'century', 'decade', 'era', 'period', 'epoch', 'age',
            'president', 'king', 'queen', 'emperor', 'leader', 'general',
            'treaty', 'declaration', 'constitution', 'independence', 'freedom'
        ]
        
        self.date_patterns = [
            r'\b\d{1,4}\s*(?:CE|BCE|AD|BC)\b',  # 1500 CE, 500 BCE
            r'\b\d{3,4}s\b',  # 1800s, 500s
            r'\b\d{1,2}(?:st|nd|rd|th)\s+century\b',  # 19th century
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4}\b'  # July 4th, 1776
        ]
    
    def get_domain(self) -> str:
        return "historical"
    
    def process_text(self, text: str, source: str = "", metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process historical text with chronological awareness"""
        cleaned_text = self.clean_text(text)
        chunks = []
        
        # Split by paragraphs or chronological sections
        paragraphs = self._split_by_paragraphs(cleaned_text)
        
        for i, chunk_text in enumerate(paragraphs):
            if not chunk_text.strip():
                continue
                
            chunk = ProcessedChunk(
                id=f"historical_{i}_{hash(chunk_text[:50])}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata=metadata or {},
                citations=self._extract_citations(chunk_text),
                key_terms=self.extract_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type=self._determine_chunk_type(chunk_text)
            )
            chunks.append(chunk)
        
        return ProcessingResult(
            chunks=chunks,
            metadata={
                'total_chunks': len(chunks),
                'avg_quality': sum(c.quality_score for c in chunks) / len(chunks) if chunks else 0,
                'has_dates': any(self._extract_dates(c.text) for c in chunks),
                'time_periods': self._extract_time_periods(cleaned_text)
            },
            quality_metrics=self._calculate_overall_quality(chunks)
        )
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract historical key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.historical_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                found_terms.append(term)
        
        return found_terms
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate quality score for historical content"""
        score = 0.0
        
        # Length factor
        word_count = len(text.split())
        if 20 <= word_count <= 800:
            score += 0.2
        
        # Historical terms density
        key_terms = self.extract_key_terms(text)
        term_density = len(key_terms) / max(word_count, 1)
        score += min(0.3, term_density * 15)
        
        # Date presence
        dates = self._extract_dates(text)
        if dates:
            score += min(0.3, len(dates) * 0.1)
        
        # Proper nouns (likely historical figures/places)
        proper_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', text))
        if proper_nouns > 0:
            score += min(0.2, proper_nouns / max(word_count, 1) * 20)
        
        return min(1.0, score)
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract historical citations"""
        citations = []
        
        # Historical source patterns
        source_patterns = [
            r'according to ([A-Za-z\s]+)',  # According to Lincoln
            r'([A-Za-z\s]+) wrote',  # Lincoln wrote
            r'in ([A-Za-z\s]+)\'s ([A-Za-z\s]+)',  # in Lincoln's speech
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, text)
            citations.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        return citations
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return dates
    
    def _extract_time_periods(self, text: str) -> List[str]:
        """Extract historical time periods"""
        periods = []
        period_patterns = [
            r'\b(ancient|medieval|renaissance|industrial|modern)\s+(?:era|period|age|times)\b',
            r'\b(world war|civil war|cold war)\b',
            r'\b(\d{1,2}(?:st|nd|rd|th)\s+century)\b'
        ]
        
        for pattern in period_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            periods.extend(matches)
        
        return list(set(periods))
    
    def _determine_chunk_type(self, text: str) -> str:
        """Determine the type of historical chunk"""
        text_lower = text.lower()
        
        if any(date_pattern in text for date_pattern in self.date_patterns):
            return "chronological"
        elif re.search(r'speech|address|declaration|proclamation', text_lower):
            return "speech"
        elif re.search(r'letter|correspondence|diary', text_lower):
            return "document"
        elif re.search(r'battle|war|conflict', text_lower):
            return "military"
        else:
            return "narrative"
    
    def _calculate_overall_quality(self, chunks: List[ProcessedChunk]) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        if not chunks:
            return {}
        
        return {
            'avg_quality': sum(c.quality_score for c in chunks) / len(chunks),
            'date_coverage': sum(1 for c in chunks if self._extract_dates(c.text)) / len(chunks),
            'avg_key_terms': sum(len(c.key_terms) for c in chunks) / len(chunks),
            'proper_noun_density': sum(len(re.findall(r'\b[A-Z][a-z]+\b', c.text)) for c in chunks) / len(chunks)
        }


class PhilosophicalProcessor(DomainProcessor):
    """Processor for philosophical texts and treatises"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.philosophical_terms = [
            'philosophy', 'philosophical', 'ethics', 'morality', 'virtue', 'justice',
            'truth', 'knowledge', 'wisdom', 'reality', 'existence', 'being',
            'consciousness', 'mind', 'soul', 'spirit', 'reason', 'logic',
            'argument', 'premise', 'conclusion', 'syllogism', 'fallacy',
            'metaphysics', 'epistemology', 'ontology', 'phenomenology',
            'existentialism', 'idealism', 'materialism', 'dualism', 'monism'
        ]
        
        self.philosophers = [
            'socrates', 'plato', 'aristotle', 'kant', 'hegel', 'nietzsche',
            'descartes', 'spinoza', 'hume', 'locke', 'berkeley', 'mill',
            'russell', 'wittgenstein', 'sartre', 'camus', 'heidegger',
            'confucius', 'laozi', 'buddha', 'aquinas', 'augustine'
        ]
    
    def get_domain(self) -> str:
        return "philosophical"
    
    def process_text(self, text: str, source: str = "", metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process philosophical text with argument awareness"""
        cleaned_text = self.clean_text(text)
        chunks = []
        
        # Split by arguments or paragraphs
        paragraphs = self._split_by_arguments(cleaned_text)
        if not paragraphs:
            paragraphs = self._split_by_paragraphs(cleaned_text)
        
        for i, chunk_text in enumerate(paragraphs):
            if not chunk_text.strip():
                continue
                
            chunk = ProcessedChunk(
                id=f"philosophical_{i}_{hash(chunk_text[:50])}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata=metadata or {},
                citations=self._extract_citations(chunk_text),
                key_terms=self.extract_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type=self._determine_chunk_type(chunk_text)
            )
            chunks.append(chunk)
        
        return ProcessingResult(
            chunks=chunks,
            metadata={
                'total_chunks': len(chunks),
                'avg_quality': sum(c.quality_score for c in chunks) / len(chunks) if chunks else 0,
                'has_arguments': any(self._has_logical_structure(c.text) for c in chunks),
                'philosophers_mentioned': self._extract_philosophers(cleaned_text)
            },
            quality_metrics=self._calculate_overall_quality(chunks)
        )
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract philosophical key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.philosophical_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                found_terms.append(term)
        
        return found_terms
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate quality score for philosophical content"""
        score = 0.0
        
        # Length factor
        word_count = len(text.split())
        if 30 <= word_count <= 1000:
            score += 0.2
        
        # Philosophical terms density
        key_terms = self.extract_key_terms(text)
        term_density = len(key_terms) / max(word_count, 1)
        score += min(0.3, term_density * 12)
        
        # Logical structure
        if self._has_logical_structure(text):
            score += 0.3
        
        # Philosopher mentions
        philosophers = self._extract_philosophers(text)
        if philosophers:
            score += min(0.2, len(philosophers) * 0.1)
        
        return min(1.0, score)
    
    def _split_by_arguments(self, text: str) -> List[str]:
        """Split text by logical arguments"""
        # Look for argument markers
        argument_markers = [
            r'(?:therefore|thus|hence|consequently)',
            r'(?:if|when).*then',
            r'(?:premise|assumption).*:',
            r'(?:conclusion|it follows that)'
        ]
        
        for marker in argument_markers:
            if re.search(marker, text, re.IGNORECASE):
                # Split by argument structure
                parts = re.split(f'({marker})', text, flags=re.IGNORECASE)
                return [p.strip() for p in parts if p.strip()]
        
        return []
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract philosophical citations"""
        citations = []
        
        # Philosopher work patterns
        work_patterns = [
            r'([A-Za-z]+)\'s ([A-Za-z\s]+)',  # Kant's Critique
            r'in (?:the )?([A-Za-z\s]+) by ([A-Za-z]+)',  # in the Republic by Plato
            r'according to ([A-Za-z]+)',  # according to Aristotle
        ]
        
        for pattern in work_patterns:
            matches = re.findall(pattern, text)
            citations.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        return citations
    
    def _extract_philosophers(self, text: str) -> List[str]:
        """Extract philosopher names from text"""
        text_lower = text.lower()
        found_philosophers = []
        
        for philosopher in self.philosophers:
            if re.search(r'\b' + re.escape(philosopher) + r'\b', text_lower):
                found_philosophers.append(philosopher)
        
        return found_philosophers
    
    def _has_logical_structure(self, text: str) -> bool:
        """Check if text has logical argument structure"""
        logical_indicators = [
            r'(?:if|when).*then',
            r'(?:therefore|thus|hence|consequently)',
            r'(?:premise|assumption).*:',
            r'(?:conclusion|it follows that)',
            r'(?:because|since|given that)',
            r'(?:implies|entails|leads to)'
        ]
        
        return any(re.search(indicator, text, re.IGNORECASE) for indicator in logical_indicators)
    
    def _determine_chunk_type(self, text: str) -> str:
        """Determine the type of philosophical chunk"""
        text_lower = text.lower()
        
        if self._has_logical_structure(text):
            return "argument"
        elif re.search(r'definition|concept|meaning', text_lower):
            return "definition"
        elif re.search(r'example|instance|case', text_lower):
            return "example"
        elif any(philosopher in text_lower for philosopher in self.philosophers):
            return "commentary"
        else:
            return "exposition"
    
    def _calculate_overall_quality(self, chunks: List[ProcessedChunk]) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        if not chunks:
            return {}
        
        return {
            'avg_quality': sum(c.quality_score for c in chunks) / len(chunks),
            'argument_coverage': sum(1 for c in chunks if self._has_logical_structure(c.text)) / len(chunks),
            'avg_key_terms': sum(len(c.key_terms) for c in chunks) / len(chunks),
            'philosopher_mentions': sum(len(self._extract_philosophers(c.text)) for c in chunks) / len(chunks)
        }


class MultiDomainProcessor:
    """Main processor that coordinates domain-specific processing"""
    
    def __init__(self):
        """Initialize the multi-domain processor with all domain processors"""
        self.processors = {
            'spiritual': SpiritualProcessor(),
            'scientific': ScientificProcessor(),
            'historical': HistoricalProcessor(),
            'philosophical': PhilosophicalProcessor()
        }
        
        # Domain detection keywords
        self.domain_keywords = {
            'spiritual': ['dharma', 'karma', 'moksha', 'yoga', 'meditation', 'divine', 'sacred', 'prayer', 'soul', 'spirit', 'krishna', 'buddha', 'christ', 'allah'],
            'scientific': ['hypothesis', 'theory', 'experiment', 'data', 'research', 'quantum', 'relativity', 'evolution', 'molecule', 'equation'],
            'historical': ['history', 'century', 'war', 'battle', 'empire', 'revolution', 'ancient', 'medieval', 'president', 'king'],
            'philosophical': ['philosophy', 'ethics', 'virtue', 'justice', 'truth', 'wisdom', 'consciousness', 'existence', 'kant', 'plato']
        }
    
    def detect_domain(self, text: str) -> str:
        """
        Detect the most appropriate domain for the given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected domain string
        """
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    score += 1
            
            # Normalize by text length
            word_count = len(text_lower.split())
            domain_scores[domain] = score / max(word_count, 1) * 100
        
        # Return domain with highest score, default to spiritual
        if not domain_scores or max(domain_scores.values()) == 0:
            return 'spiritual'
        
        return max(domain_scores, key=domain_scores.get)
    
    def process_text(self, text: str, source: str = "", domain: str = None, 
                    metadata: Dict[str, Any] = None) -> ProcessingResult:
        """
        Process text using the appropriate domain processor.
        
        Args:
            text: Input text to process
            source: Source identifier
            domain: Target domain (auto-detected if None)
            metadata: Additional metadata
            
        Returns:
            ProcessingResult with domain-specific processing
        """
        if domain is None:
            domain = self.detect_domain(text)
        
        if domain not in self.processors:
            domain = 'spiritual'  # Default fallback
        
        processor = self.processors[domain]
        return processor.process_text(text, source, metadata)
    
    def get_processor(self, domain: str) -> DomainProcessor:
        """Get a specific domain processor"""
        return self.processors.get(domain, self.processors['spiritual'])
    
    def get_available_domains(self) -> List[str]:
        """Get list of available processing domains"""
        return list(self.processors.keys())


# Factory function for creating domain processors
def create_domain_processor(domain: str) -> DomainProcessor:
    """
    Create a domain-specific processor.
    
    Args:
        domain: Domain name (spiritual, scientific, historical, philosophical)
        
    Returns:
        Domain-specific processor instance
    """
    processors = {
        'spiritual': SpiritualProcessor,
        'scientific': ScientificProcessor,
        'historical': HistoricalProcessor,
        'philosophical': PhilosophicalProcessor
    }
    
    processor_class = processors.get(domain, SpiritualProcessor)
    return processor_class()


# Convenience function for processing text with automatic domain detection
def process_text_with_auto_domain(text: str, source: str = "") -> ProcessingResult:
    """
    Process text with automatic domain detection.
    
    Args:
        text: Input text
        source: Source identifier
        
    Returns:
        ProcessingResult with appropriate domain processing
    """
    processor = MultiDomainProcessor()
    return processor.process_text(text, source)


class HistoricalTextProcessor(BaseDomainProcessor):
    """Processor for historical texts and documents"""
    
    def __init__(self):
        super().__init__("historical")
        self.historical_terms = [
            'ancient', 'medieval', 'renaissance', 'revolution', 'empire', 'kingdom',
            'dynasty', 'war', 'battle', 'treaty', 'independence', 'colonial',
            'century', 'era', 'period', 'civilization', 'culture', 'society',
            'government', 'politics', 'democracy', 'republic', 'monarchy'
        ]
        
    def process_text(self, text: str, source: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process historical text with chronological awareness"""
        if metadata is None:
            metadata = {}
            
        cleaned_text = self.clean_text(text)
        
        # Check for chronological structure
        has_dates = bool(re.search(r'\b\d{1,4}\s*(CE|BCE|AD|BC)|\b\d{4}\b|\b\d{1,2}(?:st|nd|rd|th)\s+century', cleaned_text, re.IGNORECASE))
        
        chunks = self.chunk_text(cleaned_text)
        
        processed_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk = ProcessedChunk(
                id=f"historical_{source}_{i}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata={
                    **metadata,
                    'has_dates': has_dates,
                    'chunk_index': i
                },
                citations=self.extract_citations(chunk_text),
                key_terms=self.identify_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type="chronological" if has_dates else "narrative"
            )
            processed_chunks.append(chunk)
        
        return ProcessingResult(
            chunks=processed_chunks,
            metadata={
                'total_chunks': len(processed_chunks),
                'has_chronological_structure': has_dates,
                'domain': self.domain,
                'source': source
            },
            quality_metrics={
                'avg_quality': sum(c.quality_score for c in processed_chunks) / len(processed_chunks),
                'historical_term_density': self._calculate_historical_term_density(cleaned_text)
            }
        )
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract historical citations"""
        citations = []
        
        # Date references
        dates = re.findall(r'\b(\d{1,4}\s*(?:CE|BCE|AD|BC)|\d{4}|\d{1,2}(?:st|nd|rd|th)\s+century)', text, re.IGNORECASE)
        citations.extend(dates)
        
        # Historical sources
        sources = re.findall(r'according to ([A-Za-z\s]+)|([A-Za-z\s]+) wrote|in ([A-Za-z\s]+)\'s account', text, re.IGNORECASE)
        for source_match in sources:
            for source in source_match:
                if source.strip():
                    citations.append(f"source: {source.strip()}")
        
        return list(set(citations))
    
    def identify_key_terms(self, text: str) -> List[str]:
        """Identify historical key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.historical_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        # Proper nouns (likely historical figures/places)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        found_terms.extend([f"entity: {noun}" for noun in proper_nouns[:5]])  # Limit to first 5
        
        return list(set(found_terms))
    
    def _calculate_historical_term_density(self, text: str) -> float:
        """Calculate density of historical terms in text"""
        words = text.split()
        if not words:
            return 0.0
        
        historical_count = sum(1 for word in words if word.lower() in [term.lower() for term in self.historical_terms])
        return (historical_count / len(words)) * 100


class PhilosophicalTextProcessor(BaseDomainProcessor):
    """Processor for philosophical texts and treatises"""
    
    def __init__(self):
        super().__init__("philosophical")
        self.philosophical_terms = [
            'ethics', 'morality', 'virtue', 'justice', 'truth', 'knowledge',
            'wisdom', 'consciousness', 'existence', 'reality', 'metaphysics',
            'epistemology', 'logic', 'reason', 'argument', 'premise', 'conclusion',
            'philosophy', 'thought', 'mind', 'soul', 'being', 'essence', 'nature'
        ]
        
    def process_text(self, text: str, source: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process philosophical text with argument structure awareness"""
        if metadata is None:
            metadata = {}
            
        cleaned_text = self.clean_text(text)
        
        # Check for argument structure
        has_arguments = bool(re.search(r'(?:if|when)\s+.+,\s+then|therefore|thus|premise|conclusion', cleaned_text, re.IGNORECASE))
        
        chunks = self.chunk_text(cleaned_text)
        
        processed_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk = ProcessedChunk(
                id=f"philosophical_{source}_{i}",
                text=chunk_text,
                domain=self.domain,
                source=source,
                metadata={
                    **metadata,
                    'has_arguments': has_arguments,
                    'chunk_index': i
                },
                citations=self.extract_citations(chunk_text),
                key_terms=self.identify_key_terms(chunk_text),
                quality_score=self.calculate_quality_score(chunk_text),
                chunk_type="argument" if has_arguments else "exposition"
            )
            processed_chunks.append(chunk)
        
        return ProcessingResult(
            chunks=processed_chunks,
            metadata={
                'total_chunks': len(processed_chunks),
                'has_argument_structure': has_arguments,
                'domain': self.domain,
                'source': source
            },
            quality_metrics={
                'avg_quality': sum(c.quality_score for c in processed_chunks) / len(processed_chunks),
                'philosophical_term_density': self._calculate_philosophical_term_density(cleaned_text)
            }
        )
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract philosophical citations"""
        citations = []
        
        # Philosophical concepts
        concepts = re.findall(r'the concept of ([a-z\s]+)|the idea of ([a-z\s]+)|the notion of ([a-z\s]+)', text, re.IGNORECASE)
        for concept_match in concepts:
            for concept in concept_match:
                if concept.strip():
                    citations.append(f"concept: {concept.strip()}")
        
        # Logical arguments
        arguments = re.findall(r'(?:if|when)\s+([^,]+),\s+then\s+([^.]+)', text, re.IGNORECASE)
        for premise, conclusion in arguments:
            citations.append(f"argument: {premise.strip()} → {conclusion.strip()}")
        
        return list(set(citations))
    
    def identify_key_terms(self, text: str) -> List[str]:
        """Identify philosophical key terms"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.philosophical_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        # Philosophical schools/thinkers
        philosophers = re.findall(r'\b(Plato|Aristotle|Kant|Hegel|Nietzsche|Descartes|Hume|Locke|Spinoza)\b', text)
        found_terms.extend([f"philosopher: {phil}" for phil in philosophers])
        
        return list(set(found_terms))
    
    def _calculate_philosophical_term_density(self, text: str) -> float:
        """Calculate density of philosophical terms in text"""
        words = text.split()
        if not words:
            return 0.0
        
        philosophical_count = sum(1 for word in words if word.lower() in [term.lower() for term in self.philosophical_terms])
        return (philosophical_count / len(words)) * 100


class MultiDomainProcessor:
    """Main processor that coordinates domain-specific processors"""
    
    def __init__(self):
        self.processors = {
            'spiritual': SpiritualTextProcessor(),
            'scientific': ScientificTextProcessor(),
            'historical': HistoricalTextProcessor(),
            'philosophical': PhilosophicalTextProcessor()
        }
        
    def detect_domain(self, text: str) -> str:
        """Detect the most appropriate domain for the text"""
        domain_scores = {}
        
        for domain, processor in self.processors.items():
            key_terms = processor.identify_key_terms(text)
            domain_scores[domain] = len(key_terms)
        
        if not any(domain_scores.values()):
            return 'spiritual'  # Default domain
        
        return max(domain_scores, key=domain_scores.get)
    
    def process_text(self, text: str, source: str, domain: str = None, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process text using appropriate domain processor"""
        if domain is None:
            domain = self.detect_domain(text)
        
        if domain not in self.processors:
            domain = 'spiritual'  # Fallback to default
        
        processor = self.processors[domain]
        return processor.process_text(text, source, metadata)
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domains"""
        return list(self.processors.keys())
    
    def get_processor(self, domain: str) -> BaseDomainProcessor:
        """Get processor for specific domain"""
        return self.processors.get(domain, self.processors['spiritual'])


class DomainProcessorFactory:
    """Factory for creating domain-specific processors"""
    
    _processors = {
        'spiritual': SpiritualTextProcessor,
        'scientific': ScientificTextProcessor,
        'historical': HistoricalTextProcessor,
        'philosophical': PhilosophicalTextProcessor
    }
    
    @classmethod
    def create_processor(cls, domain: str, config: Dict[str, Any] = None) -> BaseDomainProcessor:
        """Create a processor for the specified domain"""
        if domain not in cls._processors:
            raise ValueError(f"Unknown domain: {domain}. Available domains: {list(cls._processors.keys())}")
        
        processor_class = cls._processors[domain]
        return processor_class()
    
    @classmethod
    def get_available_domains(cls) -> List[str]:
        """Get list of available domains"""
        return list(cls._processors.keys())
    
    @classmethod
    def detect_domain(cls, text: str) -> str:
        """Detect the most likely domain for the given text"""
        domain_scores = {}
        
        for domain in cls._processors:
            processor = cls.create_processor(domain)
            key_terms = processor.identify_key_terms(text)
            domain_scores[domain] = len(key_terms)
        
        if not any(domain_scores.values()):
            return 'spiritual'  # Default domain
        
        return max(domain_scores, key=domain_scores.get)