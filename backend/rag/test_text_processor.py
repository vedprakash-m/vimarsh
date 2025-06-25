"""
Tests for Advanced Spiritual Text Processing

Comprehensive tests for enhanced chunking strategy with verse boundary preservation
and Sanskrit term handling.
"""

import pytest
import tempfile
from pathlib import Path
import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.text_processor import (
    AdvancedSpiritualTextProcessor, 
    EnhancedTextChunk, 
    VerseReference, 
    TextType
)


class TestAdvancedSpiritualTextProcessor:
    """Tests for AdvancedSpiritualTextProcessor"""
    
    def setup_method(self):
        self.processor = AdvancedSpiritualTextProcessor()
    
    def test_identify_text_type(self):
        """Test text type identification"""
        # Bhagavad Gita
        gita_content = "The Bhagavad Gita teaches Krishna's wisdom to Arjuna on the battlefield"
        assert self.processor.identify_text_type(gita_content, "gita.txt") == TextType.BHAGAVAD_GITA
        
        # Mahabharata
        mb_content = "The great epic Mahabharata tells of the Pandavas and their struggles"
        assert self.processor.identify_text_type(mb_content, "mahabharata.txt") == TextType.MAHABHARATA
        
        # Srimad Bhagavatam
        sb_content = "Srimad Bhagavatam describes the pastimes of Krishna"
        assert self.processor.identify_text_type(sb_content, "bhagavatam.txt") == TextType.SRIMAD_BHAGAVATAM
        
        # Unknown
        unknown_content = "Some random text without spiritual indicators"
        assert self.processor.identify_text_type(unknown_content, "random.txt") == TextType.UNKNOWN
    
    def test_extract_sanskrit_terms_by_category(self):
        """Test Sanskrit term extraction by category"""
        text = """Krishna teaches Arjuna about dharma and karma in the Bhagavad Gita. 
        Through bhakti yoga and meditation, one can achieve moksha."""
        
        terms = self.processor.extract_sanskrit_terms(text)
        
        # Should find core concepts
        assert 'core_concepts' in terms
        assert 'dharma' in terms['core_concepts']
        assert 'karma' in terms['core_concepts']
        assert 'bhakti' in terms['core_concepts']
        assert 'yoga' in terms['core_concepts']
        assert 'moksha' in terms['core_concepts']
        
        # Should find deities
        assert 'deities' in terms
        assert 'Krishna' in terms['deities']
        assert 'Arjuna' in terms['deities']
        
        # Should find texts
        assert 'texts' in terms
        assert 'Gita' in terms['texts'] or 'Bhagavad Gita' in terms['texts']
    
    def test_extract_verse_references_gita(self):
        """Test verse reference extraction for Bhagavad Gita"""
        text = """Chapter 2: The Yoga of Knowledge

2.47 You have the right to perform your prescribed duty, but not to the fruits of action.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure."""
        
        refs = self.processor.extract_verse_references(text, TextType.BHAGAVAD_GITA)
        
        assert len(refs) >= 2
        # Should find 2.47 and 2.48
        verse_numbers = [(ref.chapter, ref.verse) for ref in refs if ref.chapter and ref.verse]
        assert ('2', '47') in verse_numbers
        assert ('2', '48') in verse_numbers
    
    def test_extract_verse_references_mahabharata(self):
        """Test verse reference extraction for Mahabharata"""
        text = """Book 1 contains the Adi Parva. In Book 5 Section 28, we find important teachings."""
        
        refs = self.processor.extract_verse_references(text, TextType.MAHABHARATA)
        
        # Should find at least one book/section reference
        assert len(refs) >= 1
        book_sections = [(ref.book, ref.section) for ref in refs if ref.book and ref.section]
        assert ('5', '28') in book_sections
    
    def test_extract_semantic_tags(self):
        """Test semantic tag extraction"""
        text = """Krishna teaches about duty and righteousness, explaining how devotion and 
        meditation lead to divine knowledge and detachment from material world."""
        
        tags = self.processor.extract_semantic_tags(text)
        
        expected_tags = {
            'duty_dharma', 'devotion_bhakti', 'knowledge_jnana', 
            'meditation_dhyana', 'detachment', 'divine_nature', 'material_world'
        }
        
        found_tags = set(tags)
        # Should find most of the expected tags
        assert len(found_tags.intersection(expected_tags)) >= 5
    
    def test_calculate_chunk_quality(self):
        """Test chunk quality calculation"""
        # High quality chunk with good content
        high_quality_chunk = EnhancedTextChunk(
            content="Krishna teaches Arjuna about dharma and karma in this profound verse about duty and righteousness.",
            chunk_id="test_001",
            source_file="test.txt",
            text_type=TextType.BHAGAVAD_GITA,
            verse_references=[VerseReference(TextType.BHAGAVAD_GITA, chapter="2", verse="47")],
            sanskrit_terms=['Krishna', 'Arjuna', 'dharma', 'karma'],
            semantic_tags=['duty_dharma', 'divine_nature'],
            chunk_metadata={}
        )
        
        quality = self.processor.calculate_chunk_quality(high_quality_chunk)
        assert quality > 1.5  # Should be high quality
        
        # Low quality chunk
        low_quality_chunk = EnhancedTextChunk(
            content="Short.",
            chunk_id="test_002",
            source_file="test.txt",
            text_type=TextType.UNKNOWN,
            verse_references=[],
            sanskrit_terms=[],
            semantic_tags=[],
            chunk_metadata={}
        )
        
        low_quality = self.processor.calculate_chunk_quality(low_quality_chunk)
        assert low_quality < 1.0  # Should be low quality
    
    def test_preserve_verse_boundaries_gita(self):
        """Test verse boundary preservation for Gita"""
        text = """Chapter 2: The Yoga of Knowledge

2.47 You have the right to perform your prescribed duty, but not to the fruits of action.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure.

2.49 Far inferior indeed is mere action to the yoga of wisdom, O Arjuna."""
        
        chunks = self.processor.preserve_verse_boundaries(text, TextType.BHAGAVAD_GITA)
        
        # Should split at verse boundaries
        assert len(chunks) >= 3
        # Each chunk should contain verse content
        verse_chunks = [chunk for chunk in chunks if '2.47' in chunk or '2.48' in chunk or '2.49' in chunk]
        assert len(verse_chunks) >= 3
    
    def test_intelligent_chunk_splitting(self):
        """Test intelligent chunk splitting with size limits"""
        # Long text that needs splitting
        long_text = """Chapter 2: The Yoga of Knowledge

2.47 You have the right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.

2.49 Far inferior indeed is mere action to the yoga of wisdom, O Arjuna. Seek refuge in wisdom. Pitiable are those who are motivated by the fruits of action."""
        
        chunks = self.processor.intelligent_chunk_splitting(long_text, TextType.BHAGAVAD_GITA, max_chunk_size=200)
        
        # Should split into multiple chunks
        assert len(chunks) > 1
        # Each chunk should be within size limit (with some tolerance for sentence boundaries)
        for chunk in chunks:
            assert len(chunk) <= 250  # Allow some tolerance
    
    def test_process_text_advanced_full_pipeline(self):
        """Test complete advanced processing pipeline"""
        test_content = """Chapter 2: The Yoga of Knowledge

2.47 You have the right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.

2.49 Far inferior indeed is mere action to the yoga of wisdom, O Arjuna. Seek refuge in wisdom. Pitiable are those who are motivated by the fruits of action."""
        
        chunks = self.processor.process_text_advanced(test_content, "bhagavad_gita_test.txt")
        
        assert len(chunks) > 0
        
        for chunk in chunks:
            # Verify chunk structure
            assert isinstance(chunk, EnhancedTextChunk)
            assert chunk.chunk_id
            assert chunk.source_file == "bhagavad_gita_test.txt"
            assert chunk.text_type == TextType.BHAGAVAD_GITA
            assert isinstance(chunk.sanskrit_terms, list)
            assert isinstance(chunk.semantic_tags, list)
            assert isinstance(chunk.verse_references, list)
            assert chunk.quality_score > 0
            
            # Should have found some Sanskrit terms
            if 'Arjuna' in chunk.content or 'Krishna' in chunk.content:
                assert len(chunk.sanskrit_terms) > 0
    
    def test_export_chunks_for_vector_storage(self):
        """Test chunk export functionality"""
        chunk = EnhancedTextChunk(
            content="Test content with Krishna and dharma",
            chunk_id="test_001",
            source_file="test.txt",
            text_type=TextType.BHAGAVAD_GITA,
            verse_references=[VerseReference(TextType.BHAGAVAD_GITA, chapter="2", verse="47")],
            sanskrit_terms=['Krishna', 'dharma'],
            semantic_tags=['divine_nature'],
            chunk_metadata={'test': True}
        )
        
        exported = self.processor.export_chunks_for_vector_storage([chunk])
        
        assert len(exported) == 1
        export_data = exported[0]
        
        assert export_data['content'] == chunk.content
        assert export_data['chunk_id'] == chunk.chunk_id
        assert export_data['text_type'] == 'bhagavad_gita'
        assert export_data['sanskrit_terms'] == ['Krishna', 'dharma']
        assert export_data['semantic_tags'] == ['divine_nature']
    
    def test_filter_high_quality_chunks(self):
        """Test quality-based chunk filtering"""
        chunks = [
            EnhancedTextChunk(
                content="High quality content with Krishna teaching dharma to Arjuna",
                chunk_id="high_001",
                source_file="test.txt",
                text_type=TextType.BHAGAVAD_GITA,
                verse_references=[VerseReference(TextType.BHAGAVAD_GITA, chapter="2", verse="47")],
                sanskrit_terms=['Krishna', 'dharma', 'Arjuna'],
                semantic_tags=['divine_nature', 'duty_dharma'],
                chunk_metadata={}
            ),
            EnhancedTextChunk(
                content="Low quality.",
                chunk_id="low_001",
                source_file="test.txt",
                text_type=TextType.UNKNOWN,
                verse_references=[],
                sanskrit_terms=[],
                semantic_tags=[],
                chunk_metadata={}
            )
        ]
        
        # Calculate quality scores
        for chunk in chunks:
            chunk.quality_score = self.processor.calculate_chunk_quality(chunk)
        
        # Filter high quality chunks
        high_quality = self.processor.filter_high_quality_chunks(chunks, min_quality=1.2)
        
        # Should keep only the high quality chunk
        assert len(high_quality) == 1
        assert high_quality[0].chunk_id == "high_001"
    
    def test_verse_reference_string_formatting(self):
        """Test verse reference string formatting"""
        # Bhagavad Gita reference
        gita_ref = VerseReference(TextType.BHAGAVAD_GITA, chapter="2", verse="47")
        assert str(gita_ref) == "Bhagavad Gita 2.47"
        
        # Mahabharata reference
        mb_ref = VerseReference(TextType.MAHABHARATA, book="5", section="28")
        assert str(mb_ref) == "Mahabharata Book 5, Section 28"
        
        # Srimad Bhagavatam reference
        sb_ref = VerseReference(TextType.SRIMAD_BHAGAVATAM, book="10", chapter="14", verse="23")
        assert str(sb_ref) == "Srimad Bhagavatam 10.14.23"


class TestTextTypeEnum:
    """Tests for TextType enum"""
    
    def test_text_type_values(self):
        """Test TextType enum values"""
        assert TextType.BHAGAVAD_GITA.value == "bhagavad_gita"
        assert TextType.MAHABHARATA.value == "mahabharata"
        assert TextType.SRIMAD_BHAGAVATAM.value == "srimad_bhagavatam"
        assert TextType.UNKNOWN.value == "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
