"""
Data Validators for Vimarsh AI Agent

Comprehensive validation system for spiritual content, data quality,
and cultural appropriateness.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import unicodedata

logger = logging.getLogger(__name__)


class DataValidator:
    """
    General data validation for text content and metadata.
    """
    
    def __init__(self):
        """Initialize the data validator."""
        self.min_text_length = 10
        self.max_text_length = 100000
        self.required_metadata_fields = ['filename', 'source']
    
    def validate_text_format(self, text: str) -> Dict[str, Any]:
        """
        Validate text format and basic quality.
        
        Args:
            text: Text to validate
            
        Returns:
            Validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        # Check length
        text_length = len(text.strip())
        validation['metrics']['length'] = text_length
        
        if text_length < self.min_text_length:
            validation['is_valid'] = False
            validation['errors'].append(f"Text too short: {text_length} < {self.min_text_length}")
        
        if text_length > self.max_text_length:
            validation['is_valid'] = False
            validation['errors'].append(f"Text too long: {text_length} > {self.max_text_length}")
        
        # Check for excessive repetition
        words = text.split()
        if len(words) > 10:
            unique_words = len(set(words))
            repetition_ratio = unique_words / len(words)
            validation['metrics']['repetition_ratio'] = repetition_ratio
            
            if repetition_ratio < 0.3:
                validation['warnings'].append(f"High repetition detected: {repetition_ratio:.2f}")
        
        # Check encoding issues
        try:
            text.encode('utf-8')
        except UnicodeEncodeError as e:
            validation['is_valid'] = False
            validation['errors'].append(f"Unicode encoding error: {e}")
        
        return validation
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate metadata completeness and format.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'completeness': 0.0
        }
        
        # Check required fields
        missing_fields = []
        for field in self.required_metadata_fields:
            if field not in metadata or not metadata[field]:
                missing_fields.append(field)
        
        if missing_fields:
            validation['is_valid'] = False
            validation['errors'].append(f"Missing required fields: {missing_fields}")
        
        # Calculate completeness
        total_possible_fields = ['filename', 'source', 'language', 'source_tradition', 'text_type', 'author']
        present_fields = sum(1 for field in total_possible_fields if field in metadata and metadata[field])
        validation['completeness'] = present_fields / len(total_possible_fields)
        
        return validation


class SpiritualContentValidator:
    """
    Specialized validator for spiritual and religious content.
    
    Ensures cultural appropriateness, authenticity, and reverence.
    """
    
    def __init__(self):
        """Initialize the spiritual content validator."""
        # Sacred terms that should be handled with care
        self.sacred_terms = {
            'hindu': [
                'krishna', 'vishnu', 'shiva', 'brahma', 'devi', 'gita', 'upanishad',
                'vedas', 'dharma', 'karma', 'moksha', 'samsara', 'yoga', 'guru',
                'atman', 'brahman', 'om', 'aum', 'mantra'
            ],
            'buddhist': [
                'buddha', 'dharma', 'sangha', 'nirvana', 'bodhisattva', 'karma',
                'meditation', 'mindfulness', 'enlightenment'
            ],
            'general_spiritual': [
                'divine', 'sacred', 'holy', 'blessed', 'prayer', 'worship',
                'spiritual', 'soul', 'spirit', 'transcendent'
            ]
        }
        
        # Inappropriate language patterns
        self.inappropriate_patterns = [
            r'\b(?:damn|hell|shit|fuck|bitch)\b',  # Profanity
            r'\b(?:stupid|dumb|idiotic)\s+(?:god|divine|sacred)',  # Disrespectful combinations
            r'(?:bullshit|nonsense)\s+(?:religion|spiritual|sacred)',  # Dismissive language
        ]
        
        # Positive spiritual indicators
        self.positive_indicators = [
            'wisdom', 'compassion', 'love', 'peace', 'devotion', 'reverence',
            'enlightenment', 'truth', 'virtue', 'righteousness', 'divine'
        ]
    
    def validate_cultural_appropriateness(self, text: str) -> Dict[str, Any]:
        """
        Validate cultural appropriateness and respectfulness.
        
        Args:
            text: Text to validate
            
        Returns:
            Validation results with cultural assessment
        """
        validation = {
            'is_appropriate': True,
            'cultural_score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        text_lower = text.lower()
        
        # Check for inappropriate language
        for pattern in self.inappropriate_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                validation['is_appropriate'] = False
                validation['issues'].append(f"Inappropriate language detected: {matches}")
        
        # Calculate positive indicators
        positive_count = 0
        for indicator in self.positive_indicators:
            positive_count += len(re.findall(r'\b' + re.escape(indicator) + r'\b', text_lower))
        
        # Calculate cultural score
        text_words = len(text.split())
        if text_words > 0:
            validation['cultural_score'] = min(1.0, positive_count / text_words * 10)
        
        # Recommendations
        if validation['cultural_score'] < 0.1:
            validation['recommendations'].append("Consider adding more positive spiritual language")
        
        return validation
    
    def validate_authenticity(self, text: str, claimed_source: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate authenticity markers for spiritual texts.
        
        Args:
            text: Text content
            claimed_source: Claimed source (e.g., "Bhagavad Gita")
            
        Returns:
            Authenticity validation results
        """
        validation = {
            'authenticity_score': 0.0,
            'detected_sources': [],
            'confidence': 0.0,
            'warnings': []
        }
        
        text_lower = text.lower()
        
        # Check for source-specific indicators
        source_indicators = {
            'bhagavad_gita': ['krishna', 'arjuna', 'gita', 'kurukshetra', 'dharma'],
            'mahabharata': ['pandava', 'kaurava', 'bharata', 'yudhishthira', 'bhima'],
            'upanishads': ['atman', 'brahman', 'upanishad', 'vedanta'],
            'vedas': ['veda', 'hymn', 'sacrifice', 'fire', 'soma']
        }
        
        for source, indicators in source_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in text_lower:
                    score += 1
            
            if score > 0:
                validation['detected_sources'].append({
                    'source': source,
                    'score': score / len(indicators)
                })
        
        # Calculate overall authenticity score
        if validation['detected_sources']:
            validation['authenticity_score'] = max(s['score'] for s in validation['detected_sources'])
        
        # Check claimed source consistency
        if claimed_source:
            claimed_lower = claimed_source.lower()
            if 'gita' in claimed_lower or 'bhagavad' in claimed_lower:
                expected_source = 'bhagavad_gita'
            elif 'mahabharata' in claimed_lower:
                expected_source = 'mahabharata'
            elif 'upanishad' in claimed_lower:
                expected_source = 'upanishads'
            elif 'veda' in claimed_lower:
                expected_source = 'vedas'
            else:
                expected_source = None
            
            if expected_source:
                found_expected = any(s['source'] == expected_source for s in validation['detected_sources'])
                if not found_expected:
                    validation['warnings'].append(f"Content doesn't match claimed source: {claimed_source}")
        
        return validation
    
    def validate_reverence_level(self, text: str) -> Dict[str, Any]:
        """
        Validate the reverence and dignity level of spiritual content.
        
        Args:
            text: Text to validate
            
        Returns:
            Reverence assessment
        """
        validation = {
            'reverence_score': 0.0,
            'tone_assessment': 'neutral',
            'suggestions': []
        }
        
        text_lower = text.lower()
        
        # Reverent language indicators
        reverent_terms = [
            'divine', 'sacred', 'holy', 'blessed', 'revered', 'venerable',
            'eternal', 'infinite', 'supreme', 'almighty', 'transcendent'
        ]
        
        # Casual/informal indicators (potentially problematic)
        casual_terms = [
            'dude', 'bro', 'hey', 'cool', 'awesome', 'whatever',
            'like', 'totally', 'basically', 'literally'
        ]
        
        # Count reverent language
        reverent_count = 0
        for term in reverent_terms:
            reverent_count += len(re.findall(r'\b' + re.escape(term) + r'\b', text_lower))
        
        # Count casual language
        casual_count = 0
        for term in casual_terms:
            casual_count += len(re.findall(r'\b' + re.escape(term) + r'\b', text_lower))
        
        # Calculate reverence score
        text_words = len(text.split())
        if text_words > 0:
            reverent_ratio = reverent_count / text_words
            casual_ratio = casual_count / text_words
            
            validation['reverence_score'] = max(0.0, min(1.0, reverent_ratio * 10 - casual_ratio * 5))
        
        # Assess tone
        if validation['reverence_score'] > 0.7:
            validation['tone_assessment'] = 'highly_reverent'
        elif validation['reverence_score'] > 0.4:
            validation['tone_assessment'] = 'reverent'
        elif validation['reverence_score'] > 0.2:
            validation['tone_assessment'] = 'neutral'
        elif casual_count > 0:
            validation['tone_assessment'] = 'casual'
        else:
            validation['tone_assessment'] = 'neutral'
        
        # Suggestions
        if validation['reverence_score'] < 0.3:
            validation['suggestions'].append("Consider using more reverent and dignified language")
        if casual_count > 0:
            validation['suggestions'].append("Remove casual/informal language for spiritual content")
        
        return validation
    
    def comprehensive_validation(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive spiritual content validation.
        
        Args:
            text: Text content
            metadata: Optional metadata
            
        Returns:
            Complete validation results
        """
        results = {
            'overall_valid': True,
            'overall_score': 0.0,
            'validations': {}
        }
        
        # Run all validations
        results['validations']['cultural'] = self.validate_cultural_appropriateness(text)
        results['validations']['authenticity'] = self.validate_authenticity(
            text, metadata.get('source') if metadata else None
        )
        results['validations']['reverence'] = self.validate_reverence_level(text)
        
        # Calculate overall score
        scores = [
            results['validations']['cultural']['cultural_score'],
            results['validations']['authenticity']['authenticity_score'],
            results['validations']['reverence']['reverence_score']
        ]
        results['overall_score'] = sum(scores) / len(scores)
        
        # Determine overall validity
        results['overall_valid'] = (
            results['validations']['cultural']['is_appropriate'] and
            results['overall_score'] > 0.3
        )
        
        return results
