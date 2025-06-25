"""
Test suite for citation extraction and verification system

Tests all components including:
- Citation extraction from various spiritual texts
- Citation verification and validation
- Citation formatting
- Citation management and orchestration
"""

import pytest
from unittest.mock import Mock, patch

from .citation_system import (
    CitationManager,
    CitationExtractor,
    CitationVerifier,
    CitationFormatter,
    Citation,
    CitationType,
    CitationFormat,
    CitationValidationResult,
    extract_citations_from_text,
    verify_citations_accuracy,
    format_citations_standard
)


class TestCitation:
    """Test Citation data class"""
    
    def test_citation_creation(self):
        """Test creating a citation"""
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="2.47",
            text_excerpt="You have the right to perform your actions...",
            format_type=CitationFormat.CHAPTER_VERSE,
            confidence=0.9
        )
        
        assert citation.source_type == CitationType.BHAGAVAD_GITA
        assert citation.reference == "2.47"
        assert citation.format_type == CitationFormat.CHAPTER_VERSE
        assert citation.confidence == 0.9
        assert not citation.verified
        assert citation.full_reference == "Bhagavad Gita 2.47"
    
    def test_citation_auto_full_reference(self):
        """Test automatic full reference generation"""
        citation = Citation(
            source_type=CitationType.MAHABHARATA,
            reference="Book 5, Section 28"
        )
        
        assert citation.full_reference == "Mahabharata Book 5, Section 28"


class TestCitationExtractor:
    """Test citation extraction functionality"""
    
    def setUp(self):
        self.extractor = CitationExtractor()
    
    def test_bhagavad_gita_extraction(self):
        """Test extraction of Bhagavad Gita citations"""
        self.extractor = CitationExtractor()
        text = "As Lord Krishna teaches in Bhagavad Gita 2.47, you have the right to action but not to results."
        
        citations = self.extractor.extract_citations(text)
        
        assert len(citations) >= 1
        gita_citation = next((c for c in citations if c.source_type == CitationType.BHAGAVAD_GITA), None)
        assert gita_citation is not None
        assert "2.47" in gita_citation.reference
        assert gita_citation.format_type == CitationFormat.CHAPTER_VERSE
    
    def test_mahabharata_extraction(self):
        """Test extraction of Mahabharata citations"""
        self.extractor = CitationExtractor()
        text = "The Mahabharata Book 5, Section 28 speaks of dharma in times of conflict."
        
        citations = self.extractor.extract_citations(text)
        
        assert len(citations) >= 1
        maha_citation = next((c for c in citations if c.source_type == CitationType.MAHABHARATA), None)
        assert maha_citation is not None
        assert "Book 5" in maha_citation.reference
        assert "Section 28" in maha_citation.reference
    
    def test_vedas_extraction(self):
        """Test extraction of Vedas citations"""
        self.extractor = CitationExtractor()
        text = "According to the Rig Veda Mandala 1, Hymn 3, the divine light illuminates existence."
        
        citations = self.extractor.extract_citations(text)
        
        assert len(citations) >= 1
        veda_citation = next((c for c in citations if c.source_type == CitationType.VEDAS), None)
        assert veda_citation is not None
        assert "Rig Veda" in veda_citation.reference
    
    def test_multiple_citations_extraction(self):
        """Test extraction of multiple citations from single text"""
        self.extractor = CitationExtractor()
        text = """The Bhagavad Gita 2.47 teaches about action, while the Mahabharata Book 5, Section 28 
        discusses dharma. Additionally, the Rig Veda speaks of cosmic order."""
        
        citations = self.extractor.extract_citations(text)
        
        assert len(citations) >= 2
        
        # Should find different types
        types_found = {c.source_type for c in citations}
        assert CitationType.BHAGAVAD_GITA in types_found
        assert CitationType.MAHABHARATA in types_found
    
    def test_no_citations_found(self):
        """Test handling of text with no citations"""
        self.extractor = CitationExtractor()
        text = "This is spiritual guidance without any specific citations or references."
        
        citations = self.extractor.extract_citations(text)
        
        assert len(citations) == 0
    
    def test_confidence_calculation(self):
        """Test citation confidence calculation"""
        self.extractor = CitationExtractor()
        
        # Text with strong context should have higher confidence
        strong_context = "Lord Krishna teaches Arjuna in Bhagavad Gita 2.47 about dharma and yoga."
        weak_context = "Someone mentioned 2.47 somewhere."
        
        strong_citations = self.extractor.extract_citations(strong_context)
        weak_citations = self.extractor.extract_citations(weak_context)
        
        if strong_citations and weak_citations:
            assert strong_citations[0].confidence > weak_citations[0].confidence
    
    def test_deduplication(self):
        """Test citation deduplication"""
        self.extractor = CitationExtractor()
        text = "Gita 2.47 and Bhagavad Gita 2.47 both refer to the same verse."
        
        citations = self.extractor.extract_citations(text)
        
        # Should deduplicate similar citations
        gita_citations = [c for c in citations if c.source_type == CitationType.BHAGAVAD_GITA]
        references = [c.reference for c in gita_citations]
        
        # Should not have exact duplicates
        assert len(references) == len(set(references))


class TestCitationVerifier:
    """Test citation verification functionality"""
    
    def test_verifier_initialization(self):
        """Test verifier initialization"""
        verifier = CitationVerifier()
        
        assert verifier.source_database is not None
        assert verifier.valid_ranges is not None
        assert CitationType.BHAGAVAD_GITA in verifier.valid_ranges
    
    def test_valid_bhagavad_gita_citation(self):
        """Test verification of valid Bhagavad Gita citation"""
        verifier = CitationVerifier()
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="2.47",
            format_type=CitationFormat.CHAPTER_VERSE
        )
        
        result = verifier.verify_citation(citation)
        
        assert result.is_valid
        assert result.confidence_score > 0.5
        assert len(result.issues) == 0
        assert citation.verified
    
    def test_invalid_bhagavad_gita_citation_range(self):
        """Test verification of invalid Bhagavad Gita citation (out of range)"""
        verifier = CitationVerifier()
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="25.100",  # Invalid - Gita only has 18 chapters
            format_type=CitationFormat.CHAPTER_VERSE
        )
        
        result = verifier.verify_citation(citation)
        
        assert not result.is_valid
        assert len(result.issues) > 0
        assert any("out of range" in issue for issue in result.issues)
        assert not citation.verified
    
    def test_invalid_bhagavad_gita_citation_format(self):
        """Test verification of invalid Bhagavad Gita citation format"""
        verifier = CitationVerifier()
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="chapter two verse forty seven",  # Invalid format
            format_type=CitationFormat.GENERIC
        )
        
        result = verifier.verify_citation(citation)
        
        assert not result.is_valid
        assert len(result.issues) > 0
        assert any("format" in issue.lower() for issue in result.issues)
    
    def test_verify_multiple_citations(self):
        """Test verification of multiple citations"""
        verifier = CitationVerifier()
        citations = [
            Citation(
                source_type=CitationType.BHAGAVAD_GITA,
                reference="2.47",
                format_type=CitationFormat.CHAPTER_VERSE
            ),
            Citation(
                source_type=CitationType.BHAGAVAD_GITA,
                reference="25.100",  # Invalid
                format_type=CitationFormat.CHAPTER_VERSE
            )
        ]
        
        result = verifier.verify_citations(citations)
        
        assert not result.is_valid  # Overall invalid due to one invalid citation
        assert len(result.verified_citations) == 1
        assert len(result.unverified_citations) == 1
        assert len(result.issues) > 0
    
    def test_suggestion_generation(self):
        """Test generation of suggestions for fixing citations"""
        verifier = CitationVerifier()
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="invalid format",
            format_type=CitationFormat.GENERIC
        )
        
        result = verifier.verify_citation(citation)
        
        assert not result.is_valid
        assert len(result.suggestions) > 0
        assert any("format" in suggestion.lower() for suggestion in result.suggestions)


class TestCitationFormatter:
    """Test citation formatting functionality"""
    
    def test_formatter_initialization(self):
        """Test formatter initialization"""
        formatter = CitationFormatter()
        
        assert formatter.format_templates is not None
        assert CitationType.BHAGAVAD_GITA in formatter.format_templates
    
    def test_standard_formatting(self):
        """Test standard citation formatting"""
        formatter = CitationFormatter()
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="2.47"
        )
        
        formatted = formatter.format_citation(citation, "standard")
        
        assert "Bhagavad Gita" in formatted
        assert "2.47" in formatted
    
    def test_academic_formatting(self):
        """Test academic citation formatting"""
        formatter = CitationFormatter()
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="2.47",
            text_excerpt="You have the right to perform your actions but not to the fruits of your actions"
        )
        
        formatted = formatter.format_citation(citation, "academic")
        
        assert "Bhagavad Gita" in formatted
        assert "2.47" in formatted
        assert "You have the right" in formatted
    
    def test_simple_formatting(self):
        """Test simple citation formatting"""
        formatter = CitationFormatter()
        citation = Citation(
            source_type=CitationType.BHAGAVAD_GITA,
            reference="2.47"
        )
        
        formatted = formatter.format_citation(citation, "simple")
        
        assert formatted == "2.47"
    
    def test_format_citations_list(self):
        """Test formatting multiple citations as a list"""
        formatter = CitationFormatter()
        citations = [
            Citation(source_type=CitationType.BHAGAVAD_GITA, reference="2.47"),
            Citation(source_type=CitationType.BHAGAVAD_GITA, reference="4.7"),
            Citation(source_type=CitationType.MAHABHARATA, reference="Book 5, Section 28")
        ]
        
        formatted = formatter.format_citations_list(citations)
        
        assert "Bhagavad Gita 2.47" in formatted
        assert "Bhagavad Gita 4.7" in formatted
        assert "Mahabharata" in formatted
        assert " and " in formatted  # Should use proper list formatting
    
    def test_format_single_citation_list(self):
        """Test formatting single citation in list"""
        formatter = CitationFormatter()
        citations = [Citation(source_type=CitationType.BHAGAVAD_GITA, reference="2.47")]
        
        formatted = formatter.format_citations_list(citations)
        
        assert formatted == "Bhagavad Gita 2.47"
    
    def test_format_empty_citations_list(self):
        """Test formatting empty citations list"""
        formatter = CitationFormatter()
        
        formatted = formatter.format_citations_list([])
        
        assert formatted == ""


class TestCitationManager:
    """Test main citation manager functionality"""
    
    def test_manager_initialization(self):
        """Test manager initialization"""
        manager = CitationManager()
        
        assert manager.extractor is not None
        assert manager.verifier is not None
        assert manager.formatter is not None
    
    def test_process_text_citations_with_valid_citations(self):
        """Test processing text with valid citations"""
        manager = CitationManager()
        text = "As Lord Krishna teaches in Bhagavad Gita 2.47, dharma guides our actions."
        
        result = manager.process_text_citations(text)
        
        assert result["citation_count"] > 0
        assert result["verified_count"] > 0
        assert len(result["formatted_citations"]) > 0
        assert len(result["issues"]) == 0
    
    def test_process_text_citations_without_verification(self):
        """Test processing text without verification"""
        manager = CitationManager()
        text = "As stated in Bhagavad Gita 2.47, wisdom comes through practice."
        
        result = manager.process_text_citations(text, verify=False)
        
        assert result["citation_count"] > 0
        assert result["verification_result"] is None
        assert len(result["formatted_citations"]) > 0
    
    def test_validate_response_citations_with_citations(self):
        """Test validating response with proper citations"""
        manager = CitationManager()
        response = "Divine wisdom flows through devotion. As taught in Bhagavad Gita 2.47, focus on action, not results."
        
        result = manager.validate_response_citations(response)
        
        assert result.is_valid
        assert result.confidence_score > 0.5
        assert len(result.verified_citations) > 0
    
    def test_validate_response_citations_missing_citations(self):
        """Test validating response with missing citations"""
        manager = CitationManager()
        response = "The scripture says that meditation leads to enlightenment and divine realization."
        
        result = manager.validate_response_citations(response)
        
        assert not result.is_valid
        assert len(result.issues) > 0
        assert any("without citations" in issue for issue in result.issues)
    
    def test_validate_response_citations_no_claims(self):
        """Test validating response without scriptural claims"""
        manager = CitationManager()
        response = "Divine guidance comes through compassion and understanding in our daily practice."
        
        result = manager.validate_response_citations(response)
        
        assert result.is_valid
        assert result.confidence_score == 1.0
    
    def test_get_citation_statistics(self):
        """Test citation statistics generation"""
        manager = CitationManager()
        citations = [
            Citation(source_type=CitationType.BHAGAVAD_GITA, reference="2.47", confidence=0.9, verified=True),
            Citation(source_type=CitationType.BHAGAVAD_GITA, reference="4.7", confidence=0.8, verified=True),
            Citation(source_type=CitationType.MAHABHARATA, reference="Book 5", confidence=0.6, verified=False)
        ]
        
        stats = manager.get_citation_statistics(citations)
        
        assert stats["total"] == 3
        assert stats["by_type"]["bhagavad_gita"] == 2
        assert stats["by_type"]["mahabharata"] == 1
        assert stats["by_confidence"]["high"] == 2
        assert stats["by_confidence"]["medium"] == 1
        assert stats["verified"] == 2
        assert stats["verification_rate"] == 2/3
    
    def test_get_citation_statistics_empty(self):
        """Test citation statistics for empty list"""
        manager = CitationManager()
        
        stats = manager.get_citation_statistics([])
        
        assert stats["total"] == 0


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_extract_citations_from_text(self):
        """Test convenience function for citation extraction"""
        text = "Bhagavad Gita 2.47 teaches about action without attachment."
        
        citations = extract_citations_from_text(text)
        
        assert len(citations) > 0
        assert any(c.source_type == CitationType.BHAGAVAD_GITA for c in citations)
    
    def test_verify_citations_accuracy(self):
        """Test convenience function for citation verification"""
        citations = [
            Citation(source_type=CitationType.BHAGAVAD_GITA, reference="2.47"),
            Citation(source_type=CitationType.BHAGAVAD_GITA, reference="25.100")  # Invalid
        ]
        
        result = verify_citations_accuracy(citations)
        
        assert isinstance(result, CitationValidationResult)
        assert not result.is_valid
        assert len(result.verified_citations) == 1
        assert len(result.unverified_citations) == 1
    
    def test_format_citations_standard(self):
        """Test convenience function for citation formatting"""
        citations = [
            Citation(source_type=CitationType.BHAGAVAD_GITA, reference="2.47"),
            Citation(source_type=CitationType.MAHABHARATA, reference="Book 5, Section 28")
        ]
        
        formatted = format_citations_standard(citations)
        
        assert len(formatted) == 2
        assert "Bhagavad Gita 2.47" in formatted
        assert "Mahabharata" in formatted[1]


class TestIntegration:
    """Integration tests for complete citation workflow"""
    
    def test_complete_citation_workflow(self):
        """Test complete workflow from extraction to formatting"""
        manager = CitationManager()
        text = """My dear child, the path of righteousness is clearly described in our sacred texts. 
        As Lord Krishna teaches in Bhagavad Gita 2.47, you have the right to perform your 
        prescribed duties, but never to the fruits of your actions. Similarly, the 
        Mahabharata Book 5, Section 28 reminds us that dharma is the foundation of cosmic order."""
        
        # Extract and process citations
        result = manager.process_text_citations(text)
        
        assert result["citation_count"] >= 2
        assert result["verified_count"] >= 1
        assert len(result["formatted_citations"]) >= 2
        
        # Verify the citations are properly formatted
        formatted_text = "; ".join(result["formatted_citations"])
        assert "Bhagavad Gita" in formatted_text
        assert "Mahabharata" in formatted_text
        
        # Get statistics
        citations = result["citations"]
        stats = manager.get_citation_statistics(citations)
        
        assert stats["total"] >= 2
        assert stats["by_type"]["bhagavad_gita"] >= 1
        assert stats["by_type"]["mahabharata"] >= 1
    
    def test_ai_response_validation_workflow(self):
        """Test validation of AI-generated response"""
        manager = CitationManager()
        
        # Good response with proper citations
        good_response = """My beloved seeker, divine wisdom flows through devoted practice. 
        As taught in Bhagavad Gita 2.47, we must focus on righteous action without attachment 
        to results. This eternal principle guides us toward spiritual liberation."""
        
        result = manager.validate_response_citations(good_response)
        
        assert result.is_valid
        assert result.confidence_score >= 0.7
        assert len(result.verified_citations) > 0
        
        # Poor response with claims but no citations
        poor_response = """The scriptures clearly state that meditation is the highest practice.
        Ancient wisdom teaches us about the power of devotion and surrender."""
        
        result = manager.validate_response_citations(poor_response)
        
        assert not result.is_valid
        assert len(result.issues) > 0
        assert "without citations" in result.issues[0]
    
    def test_mixed_citation_quality(self):
        """Test handling of mixed quality citations"""
        manager = CitationManager()
        text = """Valid reference: Bhagavad Gita 2.47 teaches about karma yoga.
        Invalid reference: Bhagavad Gita 99.999 does not exist.
        Vague reference: some scripture mentions this somewhere."""
        
        result = manager.process_text_citations(text)
        
        # Should extract some citations but have validation issues
        assert result["citation_count"] >= 1
        assert len(result["issues"]) > 0
        assert result["verified_count"] < result["citation_count"]


# Example test runner
if __name__ == "__main__":
    # Run some basic tests
    print("Running citation system tests...")
    
    # Test extraction
    print("\n=== Testing Citation Extraction ===")
    extractor = CitationExtractor()
    test_text = "As Lord Krishna teaches in Bhagavad Gita 2.47, the wise work without attachment to results."
    citations = extractor.extract_citations(test_text)
    print(f"Extracted {len(citations)} citations:")
    for citation in citations:
        print(f"  - {citation.source_type.value}: {citation.reference} (confidence: {citation.confidence:.2f})")
    
    # Test verification
    print("\n=== Testing Citation Verification ===")
    verifier = CitationVerifier()
    for citation in citations:
        result = verifier.verify_citation(citation)
        print(f"  - {citation.reference}: {'VALID' if result.is_valid else 'INVALID'}")
        if result.issues:
            print(f"    Issues: {result.issues}")
    
    # Test formatting
    print("\n=== Testing Citation Formatting ===")
    formatter = CitationFormatter()
    for citation in citations:
        standard = formatter.format_citation(citation, "standard")
        academic = formatter.format_citation(citation, "academic")
        print(f"  - Standard: {standard}")
        print(f"  - Academic: {academic}")
    
    # Test complete workflow
    print("\n=== Testing Complete Workflow ===")
    manager = CitationManager()
    result = manager.process_text_citations(test_text)
    print(f"Citations: {result['citation_count']}")
    print(f"Verified: {result['verified_count']}")
    print(f"Formatted: {result['formatted_citations']}")
    
    print("\nCitation system tests completed!")
