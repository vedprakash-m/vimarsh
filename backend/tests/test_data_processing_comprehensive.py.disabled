"""
Comprehensive Data Processing Tests for Vimarsh AI Agent

This module provides comprehensive testing for data processing, text preprocessing,
vector embedding, and data validation functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any
import numpy as np
from pathlib import Path

from data_processing.text_processor import SpiritualTextProcessor
from data_processing.embeddings import EmbeddingGenerator
from data_processing.validators import DataValidator, SpiritualContentValidator
from data_processing.chunking import SemanticChunker
from tests.fixtures import SAMPLE_BHAGAVAD_GITA_VERSES, SAMPLE_SPIRITUAL_TEXTS


class TestSpiritualTextProcessor:
    """Test spiritual text processing functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.processor = SpiritualTextProcessor()
        
    def test_sanskrit_text_processing(self):
        """Test Sanskrit text preprocessing."""
        sanskrit_text = "श्रीभगवानुवाच। कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"
        
        processed = self.processor.process_sanskrit_text(sanskrit_text)
        
        assert processed.original_text == sanskrit_text
        assert processed.normalized_text is not None
        assert processed.contains_sanskrit is True
        assert len(processed.sanskrit_terms) > 0
        
    def test_verse_boundary_detection(self):
        """Test verse boundary detection in spiritual texts."""
        gita_text = """श्रीभगवानुवाच।
        कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
        मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥२.४७॥
        
        योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।"""
        
        verses = self.processor.detect_verse_boundaries(gita_text)
        
        assert len(verses) >= 2
        assert any("कर्मण्येवाधिकारस्ते" in verse for verse in verses)
        assert any("योगस्थः कुरु कर्माणि" in verse for verse in verses)
        
    def test_cultural_term_preservation(self):
        """Test preservation of cultural and spiritual terms."""
        text = "The concept of dharma, karma, and moksha are central to Hindu philosophy."
        
        processed = self.processor.process_english_text(text)
        
        # Verify important terms are preserved and marked
        assert 'dharma' in processed.preserved_terms
        assert 'karma' in processed.preserved_terms
        assert 'moksha' in processed.preserved_terms
        
    def test_text_cleaning_and_normalization(self):
        """Test text cleaning and normalization."""
        messy_text = "  This is a   text with  extra    spaces\n\nand newlines\t\tand tabs.  "
        
        cleaned = self.processor.clean_and_normalize(messy_text)
        
        assert cleaned == "This is a text with extra spaces and newlines and tabs."
        assert "  " not in cleaned  # No double spaces
        assert not cleaned.startswith(" ")  # No leading space
        assert not cleaned.endswith(" ")  # No trailing space
        
    def test_metadata_extraction(self):
        """Test metadata extraction from spiritual texts."""
        gita_text = "Bhagavad Gita Chapter 2, Verse 47: कर्मण्येवाधिकारस्ते..."
        
        metadata = self.processor.extract_metadata(gita_text)
        
        assert metadata.source == "Bhagavad Gita"
        assert metadata.chapter == 2
        assert metadata.verse == 47
        assert metadata.text_type == "verse"
        
    def test_multilingual_processing(self):
        """Test processing of multilingual content."""
        multilingual_text = """
        English: You have a right to perform your duties.
        Sanskrit: कर्मण्येवाधिकारस्ते
        Hindi: तुम्हारा केवल कर्म पर अधिकार है।
        """
        
        processed = self.processor.process_multilingual_text(multilingual_text)
        
        assert 'English' in processed.languages_detected
        assert 'Sanskrit' in processed.languages_detected
        assert 'Hindi' in processed.languages_detected
        assert len(processed.language_segments) == 3


class TestEmbeddingGenerator:
    """Test embedding generation functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.generator = EmbeddingGenerator(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
    def test_single_text_embedding(self):
        """Test embedding generation for single text."""
        text = "What is the meaning of dharma in Hindu philosophy?"
        
        embedding = self.generator.generate_embedding(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 384  # MiniLM-L6-v2 dimension
        assert not np.isnan(embedding).any()
        assert not np.isinf(embedding).any()
        
    def test_batch_embedding_generation(self):
        """Test batch embedding generation."""
        texts = [
            "What is dharma?",
            "Explain karma yoga",
            "What is moksha?",
            "How to attain inner peace?"
        ]
        
        embeddings = self.generator.generate_batch_embeddings(texts)
        
        assert embeddings.shape == (4, 384)
        assert not np.isnan(embeddings).any()
        
        # Test similarity - similar texts should have higher cosine similarity
        dharma_embedding = embeddings[0]
        moksha_embedding = embeddings[2]
        similarity = np.dot(dharma_embedding, moksha_embedding) / (
            np.linalg.norm(dharma_embedding) * np.linalg.norm(moksha_embedding)
        )
        assert 0.0 <= similarity <= 1.0
        
    def test_embedding_consistency(self):
        """Test embedding consistency for same text."""
        text = "The path of righteous action leads to liberation."
        
        embedding1 = self.generator.generate_embedding(text)
        embedding2 = self.generator.generate_embedding(text)
        
        # Should be identical for same text
        np.testing.assert_array_almost_equal(embedding1, embedding2, decimal=6)
        
    def test_sanskrit_text_embedding(self):
        """Test embedding generation for Sanskrit text."""
        sanskrit_text = "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन"
        
        embedding = self.generator.generate_embedding(sanskrit_text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 384
        assert not np.isnan(embedding).any()
        
    def test_embedding_normalization(self):
        """Test embedding normalization."""
        text = "Test text for normalization"
        
        embedding = self.generator.generate_embedding(text, normalize=True)
        
        # Normalized embedding should have unit length
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-6
        
    def test_multilingual_embedding_quality(self):
        """Test embedding quality for multilingual content."""
        texts = {
            'english': "You have a right to perform your duties",
            'sanskrit': "कर्मण्येवाधिकारस्ते",
            'hindi': "तुम्हारा केवल कर्म पर अधिकार है"
        }
        
        embeddings = {}
        for lang, text in texts.items():
            embeddings[lang] = self.generator.generate_embedding(text)
            
        # All languages discussing same concept should have some similarity
        en_sa_sim = np.dot(embeddings['english'], embeddings['sanskrit'])
        en_hi_sim = np.dot(embeddings['english'], embeddings['hindi'])
        
        assert en_sa_sim > 0.3  # Reasonable similarity threshold
        assert en_hi_sim > 0.4  # Higher similarity for related languages


class TestSemanticChunker:
    """Test semantic chunking functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.chunker = SemanticChunker(
            chunk_size=512,
            overlap_size=50,
            respect_boundaries=True
        )
        
    def test_verse_aware_chunking(self):
        """Test chunking that respects verse boundaries."""
        text = """Bhagavad Gita Chapter 2

        Verse 47: कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
        Translation: You have a right to perform your duties...
        
        Verse 48: योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।
        Translation: Be steadfast in yoga and perform your duties..."""
        
        chunks = self.chunker.chunk_text(text)
        
        assert len(chunks) >= 1
        # Verify verses are not split inappropriately
        for chunk in chunks:
            # A chunk shouldn't start mid-verse
            if "Translation:" in chunk.text:
                assert chunk.text.count("Translation:") == chunk.text.count("Verse")
                
    def test_semantic_coherence(self):
        """Test semantic coherence in chunks."""
        long_text = SAMPLE_SPIRITUAL_TEXTS["bhagavad_gita"]  # Long spiritual text
        
        chunks = self.chunker.chunk_text(long_text)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.text) <= 600  # Reasonable chunk size
            assert len(chunk.text) >= 100  # Not too small
            assert chunk.start_pos >= 0
            assert chunk.end_pos > chunk.start_pos
            
    def test_chunk_overlap_verification(self):
        """Test chunk overlap functionality."""
        text = "A" * 1000 + "B" * 1000 + "C" * 1000  # Simple test text
        
        chunks = self.chunker.chunk_text(text)
        
        if len(chunks) > 1:
            # Verify overlap between consecutive chunks
            for i in range(len(chunks) - 1):
                current_chunk = chunks[i]
                next_chunk = chunks[i + 1]
                
                # There should be some overlap
                current_end = current_chunk.text[-50:]  # Last 50 chars
                next_start = next_chunk.text[:50]       # First 50 chars
                
                # Check for any common content
                overlap_found = any(word in next_start for word in current_end.split() if len(word) > 3)
                assert overlap_found or current_chunk.end_pos >= next_chunk.start_pos - 50
                
    def test_metadata_preservation(self):
        """Test metadata preservation during chunking."""
        text_with_metadata = """Bhagavad Gita Chapter 18, Verse 66
        सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।
        अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥
        
        Translation: Abandon all varieties of dharma and surrender unto Me alone..."""
        
        chunks = self.chunker.chunk_text(text_with_metadata, preserve_metadata=True)
        
        for chunk in chunks:
            if "Chapter 18" in chunk.text:
                assert chunk.metadata.chapter == 18
                assert chunk.metadata.verse == 66
                assert chunk.metadata.source == "Bhagavad Gita"


class TestDataValidator:
    """Test data validation functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.validator = DataValidator()
        
    def test_text_quality_validation(self):
        """Test text quality validation."""
        high_quality_text = """The Bhagavad Gita teaches us about dharma, 
        the righteous path of action. Krishna advises Arjuna to perform 
        his duties without attachment to results."""
        
        validation_result = self.validator.validate_text_quality(high_quality_text)
        
        assert validation_result.is_valid is True
        assert validation_result.quality_score > 0.8
        assert len(validation_result.issues) == 0
        
    def test_sanskrit_validation(self):
        """Test Sanskrit text validation."""
        valid_sanskrit = "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन"
        invalid_sanskrit = "कर्मण्y#@#$%^&*"
        
        valid_result = self.validator.validate_sanskrit(valid_sanskrit)
        assert valid_result.is_valid is True
        
        invalid_result = self.validator.validate_sanskrit(invalid_sanskrit)
        assert invalid_result.is_valid is False
        assert len(invalid_result.issues) > 0
        
    def test_spiritual_content_validation(self):
        """Test spiritual content validation."""
        appropriate_content = """Krishna teaches about selfless action 
        and devotion to duty in the Bhagavad Gita."""
        
        inappropriate_content = "This is not spiritual content at all."
        
        appropriate_result = self.validator.validate_spiritual_content(appropriate_content)
        assert appropriate_result.is_spiritual is True
        assert appropriate_result.relevance_score > 0.7
        
        inappropriate_result = self.validator.validate_spiritual_content(inappropriate_content)
        assert inappropriate_result.is_spiritual is False
        
    def test_citation_validation(self):
        """Test citation format validation."""
        valid_citations = [
            "Bhagavad Gita 2.47",
            "Mahabharata Book 5, Section 28",
            "Srimad Bhagavatam Canto 1, Chapter 2, Verse 11"
        ]
        
        invalid_citations = [
            "Random source",
            "Gita 2.47.5.6",
            "Book without chapter"
        ]
        
        for citation in valid_citations:
            result = self.validator.validate_citation(citation)
            assert result.is_valid is True
            
        for citation in invalid_citations:
            result = self.validator.validate_citation(citation)
            assert result.is_valid is False
            
    def test_data_completeness_validation(self):
        """Test data completeness validation."""
        complete_data = {
            'text': 'Sample spiritual text',
            'source': 'Bhagavad Gita 2.47',
            'language': 'English',
            'chapter': 2,
            'verse': 47
        }
        
        incomplete_data = {
            'text': 'Sample text',
            'source': None,
            'language': 'English'
        }
        
        complete_result = self.validator.validate_data_completeness(complete_data)
        assert complete_result.is_complete is True
        
        incomplete_result = self.validator.validate_data_completeness(incomplete_data)
        assert incomplete_result.is_complete is False
        assert 'source' in incomplete_result.missing_fields


class TestSpiritualContentValidator:
    """Test specialized spiritual content validation."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.validator = SpiritualContentValidator()
        
    def test_authenticity_scoring(self):
        """Test authenticity scoring of spiritual content."""
        authentic_content = """Krishna speaks to Arjuna about the eternal nature 
        of the soul and the importance of performing one's dharma without attachment 
        to the fruits of action, as described in the Bhagavad Gita."""
        
        score = self.validator.calculate_authenticity_score(authentic_content)
        
        assert 0.8 <= score <= 1.0
        
    def test_reverence_assessment(self):
        """Test reverence level assessment."""
        reverent_content = """Lord Krishna graciously imparts divine wisdom 
        to guide souls on the path of righteousness and liberation."""
        
        irreverent_content = "Krishna just told Arjuna to do his job."
        
        reverent_score = self.validator.assess_reverence_level(reverent_content)
        irreverent_score = self.validator.assess_reverence_level(irreverent_content)
        
        assert reverent_score > irreverent_score
        assert reverent_score > 0.7
        
    def test_scriptural_grounding_check(self):
        """Test scriptural grounding verification."""
        grounded_content = """The Bhagavad Gita, Chapter 2, Verse 47 states: 
        "You have a right to perform your prescribed duties, but never to the fruits of action."""
        
        ungrounded_content = "I think Krishna probably meant that work is important."
        
        grounded_result = self.validator.check_scriptural_grounding(grounded_content)
        ungrounded_result = self.validator.check_scriptural_grounding(ungrounded_content)
        
        assert grounded_result.is_grounded is True
        assert len(grounded_result.sources_cited) > 0
        assert ungrounded_result.is_grounded is False
        
    def test_cultural_sensitivity_check(self):
        """Test cultural sensitivity assessment."""
        sensitive_content = """The sacred teachings of the Bhagavad Gita 
        offer profound insights into the nature of duty and spiritual growth."""
        
        insensitive_content = "Hindu myths tell us about some god named Krishna."
        
        sensitive_result = self.validator.assess_cultural_sensitivity(sensitive_content)
        insensitive_result = self.validator.assess_cultural_sensitivity(insensitive_content)
        
        assert sensitive_result.is_sensitive is True
        assert insensitive_result.is_sensitive is False
        assert len(insensitive_result.issues) > 0
