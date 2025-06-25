"""
Citation Extraction and Verification System

This module handles extraction, validation, and verification of citations from
spiritual texts and AI-generated responses to ensure proper attribution and accuracy.
"""

import re
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Set
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class CitationType(Enum):
    """Types of citations supported"""
    BHAGAVAD_GITA = "bhagavad_gita"
    MAHABHARATA = "mahabharata"
    RAMAYANA = "ramayana"
    UPANISHADS = "upanishads"
    VEDAS = "vedas"
    PURANAS = "puranas"
    BRAHMA_SUTRAS = "brahma_sutras"
    UNKNOWN = "unknown"


class CitationFormat(Enum):
    """Standard citation formats"""
    CHAPTER_VERSE = "chapter_verse"  # e.g., "2.47"
    BOOK_SECTION = "book_section"    # e.g., "Book 5, Section 28"
    MANDALA_HYMN = "mandala_hymn"    # e.g., "Mandala 1, Hymn 3"
    GENERIC = "generic"              # General format


@dataclass
class Citation:
    """Represents a citation from spiritual texts"""
    source_type: CitationType
    reference: str  # e.g., "2.47", "Book 5, Section 28"
    text_excerpt: Optional[str] = None  # The actual quoted text
    full_reference: Optional[str] = None  # Full formatted citation
    format_type: CitationFormat = CitationFormat.GENERIC
    confidence: float = 1.0  # Confidence in citation accuracy (0.0-1.0)
    verified: bool = False  # Whether citation has been verified
    verification_notes: Optional[str] = None
    
    def __post_init__(self):
        if not self.full_reference:
            self.full_reference = f"{self.source_type.value.replace('_', ' ').title()} {self.reference}"


@dataclass
class CitationValidationResult:
    """Result of citation validation"""
    is_valid: bool
    confidence_score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    verified_citations: List[Citation] = field(default_factory=list)
    unverified_citations: List[Citation] = field(default_factory=list)


class CitationExtractor:
    """Extracts citations from text using pattern matching"""
    
    def __init__(self):
        # Citation patterns for different texts
        self.citation_patterns = {
            CitationType.BHAGAVAD_GITA: [
                r"bhagavad\s+gita\s+(\d+)\.(\d+)",
                r"gita\s+(\d+)\.(\d+)",
                r"chapter\s+(\d+)\s+verse\s+(\d+)",
                r"(\d+)\.(\d+)",  # Simple numerical reference in context
            ],
            CitationType.MAHABHARATA: [
                r"mahabharata\s+book\s+(\d+)[\s,]+section\s+(\d+)",
                r"book\s+(\d+)[\s,]+section\s+(\d+)",
                r"(\w+)\s+parva[\s,]+section\s+(\d+)",
                r"mahabharata\s+(\w+\s+parva)",
            ],
            CitationType.RAMAYANA: [
                r"ramayana\s+(\w+)\s+kanda[\s,]+sarga\s+(\d+)",
                r"(\w+)\s+kanda[\s,]+sarga\s+(\d+)",
                r"ramayana\s+book\s+(\d+)[\s,]+chapter\s+(\d+)",
            ],
            CitationType.UPANISHADS: [
                r"(\w+)\s+upanishad\s+(\d+)\.(\d+)",
                r"upanishads?\s+(\d+)\.(\d+)",
                r"(\w+)\s+upanishad",
            ],
            CitationType.VEDAS: [
                r"(rig|sama|yajur|atharva)\s+veda\s+mandala\s+(\d+)[\s,]+hymn\s+(\d+)",
                r"(rig|sama|yajur|atharva)\s+veda\s+(\d+)\.(\d+)",
                r"(rig|sama|yajur|atharva)\s+veda",
            ],
            CitationType.PURANAS: [
                r"(\w+)\s+purana\s+(\d+)\.(\d+)",
                r"puranas?\s+(\d+)\.(\d+)",
                r"(\w+)\s+purana",
            ],
            CitationType.BRAHMA_SUTRAS: [
                r"brahma\s+sutras?\s+(\d+)\.(\d+)\.(\d+)",
                r"sutras?\s+(\d+)\.(\d+)\.(\d+)",
            ]
        }
        
        # Context keywords that help identify citation types
        self.context_keywords = {
            CitationType.BHAGAVAD_GITA: ["krishna", "arjuna", "dharma", "yoga", "battlefield"],
            CitationType.MAHABHARATA: ["kurukshetra", "pandavas", "kauravas", "bhishma"],
            CitationType.RAMAYANA: ["rama", "sita", "hanuman", "lanka", "ravana"],
            CitationType.UPANISHADS: ["brahman", "atman", "moksha", "meditation"],
            CitationType.VEDAS: ["mantra", "hymn", "sacrifice", "agni", "soma"],
            CitationType.PURANAS: ["vishnu", "shiva", "brahma", "cosmic", "creation"],
            CitationType.BRAHMA_SUTRAS: ["vedanta", "philosophy", "commentary", "sankara"]
        }
    
    def extract_citations(self, text: str) -> List[Citation]:
        """
        Extract all citations from given text
        
        Args:
            text: Text to extract citations from
            
        Returns:
            List of Citation objects found in the text
        """
        citations = []
        text_lower = text.lower()
        
        # Try each citation type
        for citation_type, patterns in self.citation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                
                for match in matches:
                    citation = self._create_citation_from_match(
                        citation_type, match, text
                    )
                    if citation:
                        citations.append(citation)
        
        # Remove duplicates and sort by confidence
        citations = self._deduplicate_citations(citations)
        citations.sort(key=lambda c: c.confidence, reverse=True)
        
        return citations
    
    def _create_citation_from_match(self, citation_type: CitationType, 
                                   match: re.Match, text: str) -> Optional[Citation]:
        """Create a Citation object from a regex match"""
        try:
            groups = match.groups()
            
            if citation_type == CitationType.BHAGAVAD_GITA:
                if len(groups) >= 2:
                    reference = f"{groups[0]}.{groups[1]}"
                    format_type = CitationFormat.CHAPTER_VERSE
                else:
                    reference = groups[0] if groups else match.group()
                    format_type = CitationFormat.GENERIC
            
            elif citation_type == CitationType.MAHABHARATA:
                if len(groups) >= 2 and groups[0].isdigit():
                    reference = f"Book {groups[0]}, Section {groups[1]}"
                    format_type = CitationFormat.BOOK_SECTION
                else:
                    reference = groups[0] if groups else match.group()
                    format_type = CitationFormat.GENERIC
            
            elif citation_type == CitationType.VEDAS:
                if len(groups) >= 3:
                    reference = f"{groups[0].title()} Veda, Mandala {groups[1]}, Hymn {groups[2]}"
                    format_type = CitationFormat.MANDALA_HYMN
                else:
                    reference = match.group()
                    format_type = CitationFormat.GENERIC
            
            else:
                reference = match.group()
                format_type = CitationFormat.GENERIC
            
            # Calculate confidence based on context
            confidence = self._calculate_citation_confidence(citation_type, text, match)
            
            # Extract surrounding text as excerpt
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            text_excerpt = text[start:end].strip()
            
            return Citation(
                source_type=citation_type,
                reference=reference,
                text_excerpt=text_excerpt,
                format_type=format_type,
                confidence=confidence
            )
            
        except Exception as e:
            logger.warning(f"Failed to create citation from match: {e}")
            return None
    
    def _calculate_citation_confidence(self, citation_type: CitationType, 
                                     text: str, match: re.Match) -> float:
        """Calculate confidence score for a citation based on context"""
        confidence = 0.5  # Base confidence
        
        # Check for context keywords
        context_keywords = self.context_keywords.get(citation_type, [])
        text_lower = text.lower()
        
        keyword_matches = sum(1 for keyword in context_keywords if keyword in text_lower)
        context_boost = min(0.3, keyword_matches * 0.1)
        confidence += context_boost
        
        # Boost confidence for explicit source mentions
        match_text = match.group().lower()
        if citation_type.value.replace('_', ' ') in match_text:
            confidence += 0.2
        
        # Boost for standard formatting
        if re.match(r'\d+\.\d+$', match.group()):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _deduplicate_citations(self, citations: List[Citation]) -> List[Citation]:
        """Remove duplicate citations"""
        seen = set()
        unique_citations = []
        
        for citation in citations:
            key = (citation.source_type, citation.reference)
            if key not in seen:
                seen.add(key)
                unique_citations.append(citation)
        
        return unique_citations


class CitationVerifier:
    """Verifies citations against source texts"""
    
    def __init__(self, source_database: Optional[Dict] = None):
        """
        Initialize verifier with source database
        
        Args:
            source_database: Database of source texts for verification
        """
        self.source_database = source_database or self._load_default_sources()
        
        # Standard verse/section ranges for validation
        self.valid_ranges = {
            CitationType.BHAGAVAD_GITA: {
                "chapters": 18,
                "verses_per_chapter": {
                    1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47,
                    7: 30, 8: 28, 9: 34, 10: 42, 11: 55, 12: 20,
                    13: 35, 14: 27, 15: 20, 16: 24, 17: 28, 18: 78
                }
            },
            CitationType.MAHABHARATA: {
                "books": 18,
                "max_sections_per_book": 300  # Approximate
            }
        }
    
    def verify_citation(self, citation: Citation) -> CitationValidationResult:
        """
        Verify a single citation
        
        Args:
            citation: Citation to verify
            
        Returns:
            CitationValidationResult with verification details
        """
        issues = []
        suggestions = []
        is_valid = True
        confidence = citation.confidence
        
        # Basic format validation
        format_issues = self._validate_citation_format(citation)
        issues.extend(format_issues)
        
        # Range validation
        range_issues = self._validate_citation_range(citation)
        issues.extend(range_issues)
        
        # Content verification (if source database available)
        if self.source_database:
            content_issues = self._verify_citation_content(citation)
            issues.extend(content_issues)
        
        # Generate suggestions
        if issues:
            suggestions = self._generate_suggestions(citation, issues)
            is_valid = False
            confidence *= 0.7  # Reduce confidence for issues
        
        result = CitationValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            issues=issues,
            suggestions=suggestions
        )
        
        if is_valid:
            citation.verified = True
            result.verified_citations.append(citation)
        else:
            result.unverified_citations.append(citation)
        
        return result
    
    def verify_citations(self, citations: List[Citation]) -> CitationValidationResult:
        """
        Verify multiple citations
        
        Args:
            citations: List of citations to verify
            
        Returns:
            Combined CitationValidationResult
        """
        all_issues = []
        all_suggestions = []
        verified_citations = []
        unverified_citations = []
        total_confidence = 0.0
        
        for citation in citations:
            result = self.verify_citation(citation)
            
            all_issues.extend(result.issues)
            all_suggestions.extend(result.suggestions)
            verified_citations.extend(result.verified_citations)
            unverified_citations.extend(result.unverified_citations)
            total_confidence += result.confidence_score
        
        # Calculate overall validation result
        is_valid = len(unverified_citations) == 0
        overall_confidence = total_confidence / max(len(citations), 1)
        
        return CitationValidationResult(
            is_valid=is_valid,
            confidence_score=overall_confidence,
            issues=all_issues,
            suggestions=all_suggestions,
            verified_citations=verified_citations,
            unverified_citations=unverified_citations
        )
    
    def _validate_citation_format(self, citation: Citation) -> List[str]:
        """Validate citation format"""
        issues = []
        
        if citation.source_type == CitationType.BHAGAVAD_GITA:
            if not re.match(r'\d+\.\d+$', citation.reference):
                issues.append(f"Bhagavad Gita citation should be in format 'chapter.verse' (e.g., '2.47')")
        
        elif citation.source_type == CitationType.MAHABHARATA:
            if not re.search(r'book\s+\d+.*section\s+\d+', citation.reference.lower()):
                issues.append(f"Mahabharata citation should specify book and section")
        
        return issues
    
    def _validate_citation_range(self, citation: Citation) -> List[str]:
        """Validate citation is within valid ranges"""
        issues = []
        
        if citation.source_type == CitationType.BHAGAVAD_GITA:
            match = re.match(r'(\d+)\.(\d+)$', citation.reference)
            if match:
                chapter = int(match.group(1))
                verse = int(match.group(2))
                
                ranges = self.valid_ranges[CitationType.BHAGAVAD_GITA]
                if chapter < 1 or chapter > ranges["chapters"]:
                    issues.append(f"Bhagavad Gita chapter {chapter} is out of range (1-{ranges['chapters']})")
                elif chapter in ranges["verses_per_chapter"]:
                    max_verses = ranges["verses_per_chapter"][chapter]
                    if verse < 1 or verse > max_verses:
                        issues.append(f"Bhagavad Gita {chapter}.{verse} is out of range (chapter {chapter} has {max_verses} verses)")
        
        return issues
    
    def _verify_citation_content(self, citation: Citation) -> List[str]:
        """Verify citation content against source database"""
        issues = []
        
        # This would check against actual source text database
        # For now, we'll implement basic checks
        if not citation.text_excerpt:
            issues.append("No text excerpt available for content verification")
        
        return issues
    
    def _generate_suggestions(self, citation: Citation, issues: List[str]) -> List[str]:
        """Generate suggestions for fixing citation issues"""
        suggestions = []
        
        if citation.source_type == CitationType.BHAGAVAD_GITA:
            suggestions.append("Use format 'Bhagavad Gita X.Y' where X is chapter (1-18) and Y is verse number")
        
        if "out of range" in " ".join(issues):
            suggestions.append("Verify chapter and verse numbers against authentic source")
        
        if not citation.text_excerpt:
            suggestions.append("Include relevant text excerpt to support citation")
        
        return suggestions
    
    def _load_default_sources(self) -> Dict:
        """Load default source database (placeholder)"""
        # In production, this would load from actual source files
        return {}


class CitationFormatter:
    """Formats citations according to standard academic conventions"""
    
    def __init__(self):
        self.format_templates = {
            CitationType.BHAGAVAD_GITA: "Bhagavad Gita {reference}",
            CitationType.MAHABHARATA: "Mahabharata, {reference}",
            CitationType.RAMAYANA: "Ramayana, {reference}",
            CitationType.UPANISHADS: "{reference}",
            CitationType.VEDAS: "{reference}",
            CitationType.PURANAS: "{reference}",
            CitationType.BRAHMA_SUTRAS: "Brahma Sutras {reference}"
        }
    
    def format_citation(self, citation: Citation, style: str = "standard") -> str:
        """
        Format citation according to specified style
        
        Args:
            citation: Citation to format
            style: Formatting style ('standard', 'academic', 'simple')
            
        Returns:
            Formatted citation string
        """
        if style == "academic":
            return self._format_academic(citation)
        elif style == "simple":
            return citation.reference
        else:
            return self._format_standard(citation)
    
    def _format_standard(self, citation: Citation) -> str:
        """Standard format for spiritual text citations"""
        template = self.format_templates.get(citation.source_type, "{reference}")
        return template.format(reference=citation.reference)
    
    def _format_academic(self, citation: Citation) -> str:
        """Academic format with full details"""
        base = self._format_standard(citation)
        if citation.text_excerpt:
            return f"{base}: \"{citation.text_excerpt[:100]}...\""
        return base
    
    def format_citations_list(self, citations: List[Citation], style: str = "standard") -> str:
        """Format multiple citations as a list"""
        if not citations:
            return ""
        
        formatted = [self.format_citation(c, style) for c in citations]
        
        if len(formatted) == 1:
            return formatted[0]
        elif len(formatted) == 2:
            return f"{formatted[0]} and {formatted[1]}"
        else:
            return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"


class CitationManager:
    """Main manager class that orchestrates citation extraction and verification"""
    
    def __init__(self, source_database: Optional[Dict] = None):
        """
        Initialize citation manager
        
        Args:
            source_database: Optional source database for verification
        """
        self.extractor = CitationExtractor()
        self.verifier = CitationVerifier(source_database)
        self.formatter = CitationFormatter()
    
    def process_text_citations(self, text: str, verify: bool = True) -> Dict[str, Any]:
        """
        Complete citation processing pipeline
        
        Args:
            text: Text to process for citations
            verify: Whether to verify extracted citations
            
        Returns:
            Dictionary with extracted and verified citations
        """
        # Extract citations
        citations = self.extractor.extract_citations(text)
        
        # Verify citations if requested
        verification_result = None
        if verify and citations:
            verification_result = self.verifier.verify_citations(citations)
        
        # Format citations
        formatted_citations = [
            self.formatter.format_citation(c) for c in citations
        ]
        
        return {
            "citations": citations,
            "verification_result": verification_result,
            "formatted_citations": formatted_citations,
            "citation_count": len(citations),
            "verified_count": len(verification_result.verified_citations) if verification_result else 0,
            "issues": verification_result.issues if verification_result else [],
            "suggestions": verification_result.suggestions if verification_result else []
        }
    
    def validate_response_citations(self, response_text: str) -> CitationValidationResult:
        """
        Validate citations in an AI response
        
        Args:
            response_text: AI-generated response to validate
            
        Returns:
            CitationValidationResult with validation details
        """
        citations = self.extractor.extract_citations(response_text)
        
        if not citations:
            # No citations found - this might be an issue if response makes claims
            has_claims = any(phrase in response_text.lower() for phrase in [
                "scripture says", "gita teaches", "vedas state", "as written",
                "according to", "it is said", "the text states", "scriptures clearly state",
                "ancient wisdom teaches", "sacred texts", "holy books", "divine scriptures",
                "vedic wisdom", "scriptural authority", "as mentioned in", "as stated in"
            ])
            
            if has_claims:
                return CitationValidationResult(
                    is_valid=False,
                    confidence_score=0.3,
                    issues=["Response makes scriptural claims without citations"],
                    suggestions=["Add proper citations for all scriptural references"]
                )
            else:
                return CitationValidationResult(
                    is_valid=True,
                    confidence_score=1.0
                )
        
        return self.verifier.verify_citations(citations)
    
    def get_citation_statistics(self, citations: List[Citation]) -> Dict[str, Any]:
        """Get statistics about citations"""
        if not citations:
            return {"total": 0}
        
        by_type = {}
        by_confidence = {"high": 0, "medium": 0, "low": 0}
        verified_count = 0
        
        for citation in citations:
            # Count by type
            type_name = citation.source_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # Count by confidence
            if citation.confidence >= 0.8:
                by_confidence["high"] += 1
            elif citation.confidence >= 0.5:
                by_confidence["medium"] += 1
            else:
                by_confidence["low"] += 1
            
            # Count verified
            if citation.verified:
                verified_count += 1
        
        return {
            "total": len(citations),
            "by_type": by_type,
            "by_confidence": by_confidence,
            "verified": verified_count,
            "verification_rate": verified_count / len(citations) if citations else 0
        }


# Utility functions for easy integration

def extract_citations_from_text(text: str) -> List[Citation]:
    """
    Convenience function to extract citations from text
    
    Args:
        text: Text to extract citations from
        
    Returns:
        List of Citation objects
    """
    extractor = CitationExtractor()
    return extractor.extract_citations(text)


def verify_citations_accuracy(citations: List[Citation]) -> CitationValidationResult:
    """
    Convenience function to verify citation accuracy
    
    Args:
        citations: List of citations to verify
        
    Returns:
        CitationValidationResult
    """
    verifier = CitationVerifier()
    return verifier.verify_citations(citations)


def format_citations_standard(citations: List[Citation]) -> List[str]:
    """
    Convenience function to format citations in standard style
    
    Args:
        citations: List of citations to format
        
    Returns:
        List of formatted citation strings
    """
    formatter = CitationFormatter()
    return [formatter.format_citation(c) for c in citations]


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    manager = CitationManager()
    
    test_texts = [
        "As Lord Krishna teaches in Bhagavad Gita 2.47, you have the right to perform your actions but not to the fruits of your actions.",
        
        "The Mahabharata Book 5, Section 28 speaks of dharma and righteous duty in times of conflict.",
        
        "According to the Rig Veda Mandala 1, Hymn 3, the divine light illuminates all existence.",
        
        "The scripture says that meditation leads to enlightenment, but no specific citation is provided here."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n=== Test Text {i} ===")
        print(f"Text: {text}")
        
        result = manager.process_text_citations(text)
        
        print(f"Citations found: {result['citation_count']}")
        print(f"Verified: {result['verified_count']}")
        
        if result['formatted_citations']:
            print(f"Formatted citations: {', '.join(result['formatted_citations'])}")
        
        if result['issues']:
            print(f"Issues: {result['issues']}")
        
        if result['suggestions']:
            print(f"Suggestions: {result['suggestions']}")
