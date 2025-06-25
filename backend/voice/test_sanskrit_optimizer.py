"""
Unit Tests for Sanskrit Recognition Optimization

This module contains comprehensive tests for the Sanskrit speech recognition
optimization functionality in the Vimarsh AI Agent.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from .sanskrit_optimizer import (
    SanskritRecognitionOptimizer,
    SanskritTerm,
    SanskritCategory,
    SanskritScript,
    PhoneticRule,
    create_sanskrit_optimizer
)


class TestSanskritTerm:
    """Test SanskritTerm class"""
    
    def test_basic_term_creation(self):
        """Test basic Sanskrit term creation"""
        term = SanskritTerm(
            term="dharma",
            devanagari="धर्म",
            iast="dharma",
            phonetic_variants=["dharma", "dharm", "darma"],
            category=SanskritCategory.PHILOSOPHICAL
        )
        
        assert term.term == "dharma"
        assert term.devanagari == "धर्म"
        assert term.iast == "dharma"
        assert "dharma" in term.phonetic_variants
        assert term.category == SanskritCategory.PHILOSOPHICAL
    
    def test_term_with_metadata(self):
        """Test Sanskrit term with full metadata"""
        term = SanskritTerm(
            term="yoga",
            devanagari="योग",
            literal_meaning="union, yoke",
            contextual_meaning="spiritual discipline",
            recognition_priority=2.0,
            confidence_boost=0.1,
            category=SanskritCategory.YOGA
        )
        
        assert term.literal_meaning == "union, yoke"
        assert term.contextual_meaning == "spiritual discipline"
        assert term.recognition_priority == 2.0
        assert term.confidence_boost == 0.1
        assert term.category == SanskritCategory.YOGA


class TestPhoneticRule:
    """Test PhoneticRule class"""
    
    def test_basic_rule(self):
        """Test basic phonetic rule"""
        rule = PhoneticRule(
            pattern=r"aa+",
            replacement="a",
            description="Multiple 'a' sounds to single 'a'"
        )
        
        assert rule.pattern == r"aa+"
        assert rule.replacement == "a"
        assert rule.priority == 1
        assert rule.context is None
    
    def test_context_rule(self):
        """Test context-specific phonetic rule"""
        rule = PhoneticRule(
            pattern=r"v",
            replacement="w",
            context="english_speakers",
            priority=2,
            description="'v' to 'w' for English speakers"
        )
        
        assert rule.context == "english_speakers"
        assert rule.priority == 2


class TestSanskritRecognitionOptimizer:
    """Test SanskritRecognitionOptimizer class"""
    
    @pytest.fixture
    def optimizer(self):
        """Create Sanskrit optimizer for testing"""
        return SanskritRecognitionOptimizer()
    
    def test_initialization(self, optimizer):
        """Test optimizer initialization"""
        assert len(optimizer.sanskrit_terms) > 0
        assert len(optimizer.phonetic_rules) > 0
        assert len(optimizer.context_clusters) > 0
        assert isinstance(optimizer.recognition_stats, dict)
    
    def test_sanskrit_vocabulary_loading(self, optimizer):
        """Test Sanskrit vocabulary loading"""
        # Check that key terms are loaded
        assert 'dharma' in optimizer.sanskrit_terms
        assert 'karma' in optimizer.sanskrit_terms
        assert 'yoga' in optimizer.sanskrit_terms
        assert 'krishna' in optimizer.sanskrit_terms
        assert 'om' in optimizer.sanskrit_terms
        
        # Check term properties
        dharma_term = optimizer.sanskrit_terms['dharma']
        assert dharma_term.category == SanskritCategory.PHILOSOPHICAL
        assert dharma_term.devanagari == "धर्म"
        assert len(dharma_term.phonetic_variants) > 0
    
    def test_phonetic_rules_loading(self, optimizer):
        """Test phonetic rules loading"""
        rules = optimizer.phonetic_rules
        
        # Should have various types of rules
        patterns = [rule.pattern for rule in rules]
        assert any("aa+" in pattern for pattern in patterns)
        assert any("kh" in pattern for pattern in patterns)
        assert any("ś" in pattern for pattern in patterns)
        
        # Rules should be sorted by priority
        priorities = [rule.priority for rule in rules]
        assert priorities == sorted(priorities, reverse=True)
    
    def test_context_clusters_loading(self, optimizer):
        """Test context clusters loading"""
        clusters = optimizer.context_clusters
        
        # Check key clusters exist
        assert 'gita_context' in clusters
        assert 'yoga_practice' in clusters
        assert 'devotional' in clusters
        assert 'philosophical' in clusters
        
        # Check cluster contents
        assert 'dharma' in clusters['gita_context']
        assert 'yoga' in clusters['yoga_practice']
        assert 'krishna' in clusters['devotional']
        assert 'atman' in clusters['philosophical']
    
    def test_phonetic_transformations(self, optimizer):
        """Test phonetic transformations"""
        text = "dharma"
        variants = optimizer.apply_phonetic_transformations(text)
        
        assert text in variants
        assert len(variants) >= 1
        
        # Test with elongated vowels
        text = "dhaarma"
        variants = optimizer.apply_phonetic_transformations(text)
        assert "dharma" in variants
    
    def test_context_phonetic_transformations(self, optimizer):
        """Test context-specific phonetic transformations"""
        text = "vishnu"
        variants_default = optimizer.apply_phonetic_transformations(text)
        variants_english = optimizer.apply_phonetic_transformations(text, "english_speakers")
        
        # English speakers context might have different variants
        assert len(variants_english) >= len(variants_default)
    
    def test_direct_sanskrit_matches(self, optimizer):
        """Test direct Sanskrit term matching"""
        text = "What is dharma according to Krishna?"
        matches = optimizer.find_sanskrit_matches(text)
        
        # Should find dharma and krishna
        found_terms = [match[0].term for match in matches]
        assert 'dharma' in found_terms
        assert 'krishna' in found_terms
        
        # Check confidence scores
        for term, confidence in matches:
            assert 0.0 <= confidence <= 1.0
    
    def test_phonetic_variant_matches(self, optimizer):
        """Test matching phonetic variants"""
        text = "What is dharm and karm?"
        matches = optimizer.find_sanskrit_matches(text)
        
        found_terms = [match[0].term for match in matches]
        assert 'dharma' in found_terms
        assert 'karma' in found_terms
    
    def test_similarity_matching(self, optimizer):
        """Test similarity-based matching"""
        # Test with slightly misspelled terms
        text = "What is dharama?"  # Common mispronunciation
        matches = optimizer.find_sanskrit_matches(text, confidence_threshold=0.5)
        
        if matches:
            found_terms = [match[0].term for match in matches]
            # Should still find dharma with lower confidence
            assert any('dharma' in term for term in found_terms)
    
    def test_context_enhancement(self, optimizer):
        """Test context-based recognition enhancement"""
        text = "dharma and karma"
        previous_terms = ['gita', 'krishna', 'arjuna']  # Gita context
        
        result = optimizer.enhance_recognition_with_context(text, previous_terms)
        
        assert 'original_matches' in result
        assert 'enhanced_matches' in result
        assert 'context_scores' in result
        assert 'dominant_context' in result
        
        # Should identify Gita context
        assert result['dominant_context'] == 'gita_context'
        
        # Enhanced matches should have higher confidence
        original_dharma_conf = None
        enhanced_dharma_conf = None
        
        for term, conf in result['original_matches']:
            if term.term == 'dharma':
                original_dharma_conf = conf
                break
        
        for term, conf in result['enhanced_matches']:
            if term.term == 'dharma':
                enhanced_dharma_conf = conf
                break
        
        if original_dharma_conf and enhanced_dharma_conf:
            assert enhanced_dharma_conf >= original_dharma_conf
    
    def test_pronunciation_variants_generation(self, optimizer):
        """Test pronunciation variants generation"""
        variants = optimizer.generate_pronunciation_variants('dharma')
        
        assert 'dharma' in variants
        assert 'dharm' in variants
        assert len(variants) > 1
        
        # Test unknown term
        unknown_variants = optimizer.generate_pronunciation_variants('unknown_term')
        assert len(unknown_variants) >= 1
    
    def test_recognition_statistics_update(self, optimizer):
        """Test recognition statistics updates"""
        initial_total = optimizer.recognition_stats['total_sanskrit_detected']
        initial_success = optimizer.recognition_stats['successful_recognitions']
        
        # Update with successful recognition
        optimizer.update_recognition_statistics('dharma', True, 0.9)
        
        assert optimizer.recognition_stats['total_sanskrit_detected'] == initial_total + 1
        assert optimizer.recognition_stats['successful_recognitions'] == initial_success + 1
        
        # Check term-specific updates
        dharma_term = optimizer.sanskrit_terms['dharma']
        assert dharma_term.frequency_score > 0
        assert dharma_term.accuracy_score > 0
        assert dharma_term.last_recognized is not None
    
    def test_recognition_statistics_failure(self, optimizer):
        """Test recognition statistics for failures"""
        initial_failed = optimizer.recognition_stats['failed_recognitions']
        
        # Update with failed recognition
        optimizer.update_recognition_statistics('unknown_term', False, 0.2)
        
        assert optimizer.recognition_stats['failed_recognitions'] == initial_failed + 1
    
    def test_optimization_recommendations(self, optimizer):
        """Test optimization recommendations"""
        # Add some statistics
        optimizer.update_recognition_statistics('dharma', True, 0.6)  # Low accuracy
        optimizer.update_recognition_statistics('karma', True, 0.9)   # High accuracy
        
        recommendations = optimizer.get_optimization_recommendations()
        
        assert 'priority_terms' in recommendations
        assert 'problem_categories' in recommendations
        assert 'suggested_improvements' in recommendations
        assert 'training_focus' in recommendations
        
        # Should identify dharma as needing attention
        priority_terms = [item['term'] for item in recommendations['priority_terms']]
        assert 'dharma' in priority_terms
    
    def test_comprehensive_statistics(self, optimizer):
        """Test comprehensive statistics"""
        stats = optimizer.get_statistics()
        
        assert 'total_terms_loaded' in stats
        assert 'total_recognitions_attempted' in stats
        assert 'overall_success_rate' in stats
        assert 'categories' in stats
        
        # Check category breakdown
        assert SanskritCategory.PHILOSOPHICAL.value in stats['categories']
        assert SanskritCategory.YOGA.value in stats['categories']
        assert SanskritCategory.DEITY.value in stats['categories']
        
        for category_stats in stats['categories'].values():
            assert 'term_count' in category_stats
            assert 'average_priority' in category_stats
    
    def test_similarity_calculation(self, optimizer):
        """Test similarity calculation method"""
        # Test identical strings
        similarity = optimizer._calculate_similarity("dharma", "dharma")
        assert similarity == 1.0
        
        # Test completely different strings
        similarity = optimizer._calculate_similarity("dharma", "xyz")
        assert similarity < 0.5
        
        # Test similar strings
        similarity = optimizer._calculate_similarity("dharma", "dharama")
        assert 0.5 < similarity < 1.0
        
        # Test empty strings
        similarity = optimizer._calculate_similarity("", "dharma")
        assert similarity == 0.0


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_create_sanskrit_optimizer(self):
        """Test creating Sanskrit optimizer"""
        optimizer = create_sanskrit_optimizer()
        
        assert isinstance(optimizer, SanskritRecognitionOptimizer)
        assert len(optimizer.sanskrit_terms) > 0
        assert len(optimizer.phonetic_rules) > 0


# Integration tests
class TestSanskritOptimizerIntegration:
    """Integration tests for Sanskrit optimizer"""
    
    def test_full_recognition_workflow(self):
        """Test complete recognition workflow"""
        optimizer = create_sanskrit_optimizer()
        
        # Test spiritual query
        text = "Please explain dharma yoga according to Krishna in the Bhagavad Gita"
        
        # Find initial matches
        matches = optimizer.find_sanskrit_matches(text)
        assert len(matches) > 0
        
        # Extract terms for context
        recognized_terms = [match[0].term for match in matches]
        
        # Enhance with context
        enhanced = optimizer.enhance_recognition_with_context(text, recognized_terms)
        
        assert len(enhanced['enhanced_matches']) >= len(enhanced['original_matches'])
        
        # Update statistics
        for term, confidence in enhanced['enhanced_matches']:
            optimizer.update_recognition_statistics(term.term, True, confidence)
        
        # Get recommendations
        recommendations = optimizer.get_optimization_recommendations()
        assert isinstance(recommendations, dict)
    
    def test_error_handling(self):
        """Test error handling in recognition"""
        optimizer = create_sanskrit_optimizer()
        
        # Test with empty text
        matches = optimizer.find_sanskrit_matches("")
        assert len(matches) == 0
        
        # Test with non-Sanskrit text
        matches = optimizer.find_sanskrit_matches("This is plain English text")
        # Should not find any matches or very low confidence matches
        high_confidence_matches = [m for m in matches if m[1] > 0.8]
        assert len(high_confidence_matches) == 0
    
    def test_multilingual_context(self):
        """Test handling of multilingual context"""
        optimizer = create_sanskrit_optimizer()
        
        # Mix of English and Sanskrit terms
        text = "The concept of dharma is central to yoga philosophy"
        matches = optimizer.find_sanskrit_matches(text)
        
        # Should find dharma and yoga
        found_terms = [match[0].term for match in matches]
        assert 'dharma' in found_terms
        assert 'yoga' in found_terms
        
        # Should not match English words
        english_words = ['concept', 'central', 'philosophy']
        for word in english_words:
            assert word not in found_terms
    
    def test_performance_with_large_text(self):
        """Test performance with larger text blocks"""
        optimizer = create_sanskrit_optimizer()
        
        # Large text with multiple Sanskrit terms
        large_text = """
        The Bhagavad Gita teaches us about dharma, karma, and yoga.
        Krishna explains to Arjuna the path of bhakti and the nature of atman.
        Through meditation and pranayama, one can achieve samadhi.
        The Vedas and Upanishads contain the wisdom of the ancient gurus.
        Om Namah Shivaya is a powerful mantra for spiritual practice.
        """ * 10  # Repeat to make it larger
        
        import time
        start_time = time.time()
        
        matches = optimizer.find_sanskrit_matches(large_text)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete in reasonable time (less than 1 second)
        assert processing_time < 1.0
        
        # Should find multiple terms
        assert len(matches) > 10
        
        # Should find high-confidence matches
        high_confidence = [m for m in matches if m[1] > 0.8]
        assert len(high_confidence) > 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
