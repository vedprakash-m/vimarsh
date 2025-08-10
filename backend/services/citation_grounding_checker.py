"""
Citation Grounding Checker for Vimarsh RAG Quality Enhancement

Validates citation accuracy and prevents hallucination by checking
if cited sources actually support the generated responses.

Part of Phase 1 strategic pivot implementation.

Features:
- String overlap validation between citations and responses
- Source authenticity verification
- Citation precision scoring
- Hallucination detection heuristics
- Real-time grounding assessment
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class CitationValidationLevel(Enum):
    """Levels of citation validation strictness"""
    BASIC = "basic"           # Simple string overlap
    MODERATE = "moderate"     # Semantic similarity
    STRICT = "strict"         # Exact quote matching

@dataclass
class CitationValidation:
    """Result of citation validation"""
    citation: str
    response_text: str
    is_valid: bool
    confidence_score: float
    validation_method: str
    supporting_evidence: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    overlap_percentage: float = 0.0

@dataclass
class GroundingReport:
    """Comprehensive grounding analysis report"""
    response_id: str
    total_citations: int
    valid_citations: int
    invalid_citations: int
    overall_precision: float
    confidence_level: str
    citation_validations: List[CitationValidation] = field(default_factory=list)
    hallucination_risk: str = "low"
    recommendation: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class CitationGroundingChecker:
    """
    Citation Grounding Checker Service
    
    Validates that AI-generated responses are properly grounded in
    the cited sources to prevent hallucination and ensure authenticity.
    """
    
    def __init__(self, validation_level: CitationValidationLevel = CitationValidationLevel.MODERATE):
        self.validation_level = validation_level
        self.source_cache: Dict[str, str] = {}
        self.validation_cache: Dict[str, CitationValidation] = {}
        self.precision_threshold = 0.7  # Minimum precision for passing
        self.overlap_threshold = 0.3    # Minimum text overlap
        
        # Load source texts for validation
        self._load_source_texts()
        
        logger.info(f"🔍 Citation Grounding Checker initialized (level: {validation_level.value})")
    
    def _load_source_texts(self):
        """Load source texts for citation validation"""
        try:
            # Load the same source files used for RAG
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sources")
            
            source_files = {
                "Bhagavad Gita": "bhagavad_gita_clean.jsonl",
                "Buddha Teachings": "buddha_teachings.json",
                "Jesus Teachings": "jesus_teachings.json",
                "Einstein Teachings": "einstein_teachings.json",
                "Lincoln Teachings": "lincoln_teachings.json",
                "Marcus Aurelius": "marcus_aurelius_teachings.json",
                "Lao Tzu": "lao_tzu_teachings.json",
                "Rumi": "rumi_teachings.json",
                "Confucius": "confucius_teachings.json",
                "Newton": "newton_teachings.json",
                "Tesla": "tesla_teachings.json",
                "Chanakya": "chanakya_teachings.json"
            }
            
            for source_name, filename in source_files.items():
                file_path = os.path.join(data_dir, filename)
                if os.path.exists(file_path):
                    self._load_source_file(source_name, file_path)
            
            logger.info(f"📚 Loaded {len(self.source_cache)} source texts for validation")
            
        except Exception as e:
            logger.error(f"❌ Failed to load source texts: {e}")
    
    def _load_source_file(self, source_name: str, file_path: str):
        """Load a single source file into cache"""
        try:
            if file_path.endswith('.jsonl'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self._cache_source_content(data, source_name)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            self._cache_source_content(item, source_name)
                    elif isinstance(data, dict):
                        self._cache_source_content(data, source_name)
        
        except Exception as e:
            logger.warning(f"⚠️ Error loading {file_path}: {e}")
    
    def _cache_source_content(self, data: Dict[str, Any], source_name: str):
        """Cache source content for citation validation"""
        try:
            # Extract content
            content = ""
            if 'content' in data:
                content = data['content']
            elif 'text' in data:
                content = data['text']
            elif 'translation' in data:
                content = data['translation']
            
            if content:
                # Create cache key from source and verse/chapter info
                verse = data.get('verse', '')
                chapter = data.get('chapter', '')
                
                if verse:
                    cache_key = f"{source_name} {verse}"
                elif chapter:
                    cache_key = f"{source_name} Chapter {chapter}"
                else:
                    cache_key = f"{source_name} - {content[:50]}..."
                
                self.source_cache[cache_key.lower()] = content
                
        except Exception as e:
            logger.warning(f"⚠️ Error caching source content: {e}")
    
    async def validate_response_grounding(
        self,
        response_text: str,
        citations: List[str],
        response_id: Optional[str] = None
    ) -> GroundingReport:
        """
        Validate that a response is properly grounded in its citations
        
        Args:
            response_text: The AI-generated response
            citations: List of citations provided with the response
            response_id: Optional ID for tracking
            
        Returns:
            GroundingReport with validation results
        """
        response_id = response_id or f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            citation_validations = []
            valid_count = 0
            
            for citation in citations:
                validation = await self._validate_single_citation(citation, response_text)
                citation_validations.append(validation)
                
                if validation.is_valid:
                    valid_count += 1
            
            # Calculate overall metrics
            total_citations = len(citations)
            invalid_count = total_citations - valid_count
            overall_precision = valid_count / total_citations if total_citations > 0 else 0.0
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(overall_precision)
            
            # Assess hallucination risk
            hallucination_risk = self._assess_hallucination_risk(overall_precision, citation_validations)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_precision, citation_validations)
            
            report = GroundingReport(
                response_id=response_id,
                total_citations=total_citations,
                valid_citations=valid_count,
                invalid_citations=invalid_count,
                overall_precision=overall_precision,
                confidence_level=confidence_level,
                citation_validations=citation_validations,
                hallucination_risk=hallucination_risk,
                recommendation=recommendation
            )

            logger.info(f"🔍 Citation validation completed: {valid_count}/{total_citations} valid (precision: {overall_precision:.2%})")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Citation validation failed: {e}")
            return GroundingReport(
                response_id=response_id,
                total_citations=len(citations),
                valid_citations=0,
                invalid_citations=len(citations),
                overall_precision=0.0,
                confidence_level="error",
                hallucination_risk="high",
                recommendation="Validation failed - manual review required"
            )
    
    async def _validate_single_citation(self, citation: str, response_text: str) -> CitationValidation:
        """Validate a single citation against the response text"""
        
        # Check cache first
        cache_key = f"{citation}|{hash(response_text) % 10000}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            # Find matching source content
            source_content = self._find_source_content(citation)
            
            if not source_content:
                validation = CitationValidation(
                    citation=citation,
                    response_text=response_text,
                    is_valid=False,
                    confidence_score=0.0,
                    validation_method="source_not_found",
                    concerns=["Citation source not found in knowledge base"]
                )
            else:
                validation = self._perform_validation(citation, response_text, source_content)
            
            # Cache result
            self.validation_cache[cache_key] = validation
            return validation
            
        except Exception as e:
            logger.warning(f"⚠️ Citation validation error: {e}")
            return CitationValidation(
                citation=citation,
                response_text=response_text,
                is_valid=False,
                confidence_score=0.0,
                validation_method="validation_error",
                concerns=[f"Validation error: {str(e)}"]
            )
    
    def _find_source_content(self, citation: str) -> Optional[str]:
        """Find source content for a citation"""
        citation_lower = citation.lower()
        
        # Try exact match first
        if citation_lower in self.source_cache:
            return self.source_cache[citation_lower]
        
        # Try partial matches
        for cached_citation, content in self.source_cache.items():
            if self._citation_matches(citation_lower, cached_citation):
                return content
        
        return None
    
    def _citation_matches(self, target_citation: str, cached_citation: str) -> bool:
        """Check if two citations refer to the same source"""
        # Extract key components (book name, chapter, verse)
        target_parts = self._extract_citation_parts(target_citation)
        cached_parts = self._extract_citation_parts(cached_citation)
        
        # Check for overlap in key components
        if target_parts['book'] and cached_parts['book']:
            if target_parts['book'] in cached_parts['book'] or cached_parts['book'] in target_parts['book']:
                # Check verse/chapter match if available
                if target_parts['verse'] and cached_parts['verse']:
                    return target_parts['verse'] == cached_parts['verse']
                elif target_parts['chapter'] and cached_parts['chapter']:
                    return target_parts['chapter'] == cached_parts['chapter']
                else:
                    return True  # Book match is sufficient if no verse/chapter
        
        return False
    
    def _extract_citation_parts(self, citation: str) -> Dict[str, Optional[str]]:
        """Extract book, chapter, and verse from citation"""
        parts = {'book': None, 'chapter': None, 'verse': None}
        
        # Common patterns for spiritual texts
        patterns = [
            r'(bhagavad gita|gita)\s*(\d+\.\d+)',
            r'(.*?)\s+(\d+):(\d+)',
            r'(.*?)\s+(\d+\.\d+)',
            r'(.*?)\s+chapter\s+(\d+)',
            r'(.*?)\s+(\d+)',
        ]
        
        citation_clean = citation.lower().strip()
        
        for pattern in patterns:
            match = re.search(pattern, citation_clean)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    parts['book'] = groups[0].strip()
                    if ':' in groups[1]:
                        chapter, verse = groups[1].split(':')
                        parts['chapter'] = chapter
                        parts['verse'] = verse
                    elif '.' in groups[1]:
                        parts['verse'] = groups[1]
                    else:
                        parts['chapter'] = groups[1]
                break
        
        # Fallback: just extract the book name
        if not parts['book']:
            parts['book'] = citation_clean.split()[0] if citation_clean else None
        
        return parts
    
    def _perform_validation(self, citation: str, response_text: str, source_content: str) -> CitationValidation:
        """Perform the actual validation between citation source and response"""
        
        if self.validation_level == CitationValidationLevel.BASIC:
            return self._basic_validation(citation, response_text, source_content)
        elif self.validation_level == CitationValidationLevel.MODERATE:
            return self._moderate_validation(citation, response_text, source_content)
        else:  # STRICT
            return self._strict_validation(citation, response_text, source_content)
    
    def _basic_validation(self, citation: str, response_text: str, source_content: str) -> CitationValidation:
        """Basic validation using simple string overlap"""
        
        # Tokenize texts
        response_words = set(self._tokenize_text(response_text.lower()))
        source_words = set(self._tokenize_text(source_content.lower()))
        
        # Calculate overlap
        overlap_words = response_words.intersection(source_words)
        overlap_percentage = len(overlap_words) / len(response_words) if response_words else 0.0
        
        # Determine validity
        is_valid = overlap_percentage >= self.overlap_threshold
        confidence_score = min(overlap_percentage * 2, 1.0)  # Scale to 0-1
        
        supporting_evidence = list(overlap_words)[:5]  # Top 5 overlapping words
        concerns = []
        
        if not is_valid:
            concerns.append(f"Low text overlap: {overlap_percentage:.1%} (threshold: {self.overlap_threshold:.1%})")
        
        return CitationValidation(
            citation=citation,
            response_text=response_text,
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_method="basic_overlap",
            supporting_evidence=supporting_evidence,
            concerns=concerns,
            overlap_percentage=overlap_percentage
        )
    
    def _moderate_validation(self, citation: str, response_text: str, source_content: str) -> CitationValidation:
        """Moderate validation with phrase matching and semantic similarity"""
        
        # Start with basic validation
        basic_result = self._basic_validation(citation, response_text, source_content)
        
        # Add phrase-level validation
        phrase_score = self._calculate_phrase_similarity(response_text, source_content)
        
        # Combine scores
        combined_score = (basic_result.confidence_score + phrase_score) / 2
        
        # Enhanced validity check
        is_valid = combined_score >= 0.5 and basic_result.overlap_percentage >= 0.2
        
        # Enhanced evidence
        supporting_evidence = basic_result.supporting_evidence
        if phrase_score > 0.3:
            common_phrases = self._find_common_phrases(response_text, source_content)
            supporting_evidence.extend(common_phrases[:3])
        
        concerns = basic_result.concerns.copy()
        if phrase_score < 0.3:
            concerns.append(f"Low phrase similarity: {phrase_score:.1%}")
        
        return CitationValidation(
            citation=citation,
            response_text=response_text,
            is_valid=is_valid,
            confidence_score=combined_score,
            validation_method="moderate_semantic",
            supporting_evidence=supporting_evidence,
            concerns=concerns,
            overlap_percentage=basic_result.overlap_percentage
        )
    
    def _strict_validation(self, citation: str, response_text: str, source_content: str) -> CitationValidation:
        """Strict validation requiring exact quote matches"""
        
        # Start with moderate validation
        moderate_result = self._moderate_validation(citation, response_text, source_content)
        
        # Check for exact quote matches
        exact_matches = self._find_exact_quotes(response_text, source_content)
        has_exact_match = len(exact_matches) > 0
        
        # Strict validation requires exact matches for high confidence
        if has_exact_match:
            confidence_score = min(moderate_result.confidence_score + 0.3, 1.0)
            is_valid = True
        else:
            confidence_score = moderate_result.confidence_score * 0.7  # Penalize lack of exact matches
            is_valid = moderate_result.is_valid and confidence_score >= 0.7
        
        supporting_evidence = moderate_result.supporting_evidence.copy()
        concerns = moderate_result.concerns.copy()
        
        if has_exact_match:
            supporting_evidence.extend([f"Exact quote: {match}" for match in exact_matches[:2]])
        else:
            concerns.append("No exact quotes found from source")
        
        return CitationValidation(
            citation=citation,
            response_text=response_text,
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_method="strict_exact_match",
            supporting_evidence=supporting_evidence,
            concerns=concerns,
            overlap_percentage=moderate_result.overlap_percentage
        )
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Simple text tokenization"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        # Filter out very short words
        return [word for word in words if len(word) > 2]
    
    def _calculate_phrase_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on common phrases (3+ words)"""
        # Extract phrases of 3+ words
        phrases1 = self._extract_phrases(text1, min_length=3)
        phrases2 = self._extract_phrases(text2, min_length=3)
        
        if not phrases1 or not phrases2:
            return 0.0
        
        # Find common phrases
        common_phrases = set(phrases1).intersection(set(phrases2))
        
        # Calculate similarity
        similarity = len(common_phrases) / min(len(phrases1), len(phrases2))
        return similarity
    
    def _extract_phrases(self, text: str, min_length: int = 3) -> List[str]:
        """Extract phrases of minimum length from text"""
        words = self._tokenize_text(text)
        phrases = []
        
        for i in range(len(words) - min_length + 1):
            phrase = ' '.join(words[i:i + min_length])
            phrases.append(phrase)
        
        return phrases
    
    def _find_common_phrases(self, text1: str, text2: str) -> List[str]:
        """Find common phrases between two texts"""
        phrases1 = set(self._extract_phrases(text1, min_length=3))
        phrases2 = set(self._extract_phrases(text2, min_length=3))
        
        common = phrases1.intersection(phrases2)
        return list(common)
    
    def _find_exact_quotes(self, response_text: str, source_content: str, min_quote_length: int = 10) -> List[str]:
        """Find exact quotes from source in response"""
        exact_matches = []
        
        # Look for sequences of words that appear exactly in both texts
        response_words = self._tokenize_text(response_text)
        source_words = self._tokenize_text(source_content)
        
        for i in range(len(response_words) - 2):
            for length in range(3, min(8, len(response_words) - i + 1)):
                phrase = ' '.join(response_words[i:i + length])
                if len(phrase) >= min_quote_length:
                    source_text_clean = ' '.join(source_words)
                    if phrase in source_text_clean:
                        exact_matches.append(phrase)
        
        return list(set(exact_matches))  # Remove duplicates
    
    def _determine_confidence_level(self, precision: float) -> str:
        """Determine confidence level based on precision"""
        if precision >= 0.9:
            return "very_high"
        elif precision >= 0.7:
            return "high"
        elif precision >= 0.5:
            return "medium"
        elif precision >= 0.3:
            return "low"
        else:
            return "very_low"
    
    def _assess_hallucination_risk(self, precision: float, validations: List[CitationValidation]) -> str:
        """Assess risk of hallucination based on validation results"""
        if precision >= 0.8:
            return "low"
        elif precision >= 0.6:
            return "medium"
        elif precision >= 0.4:
            # Check for specific red flags
            red_flags = sum(1 for v in validations if "not found" in ' '.join(v.concerns))
            if red_flags > len(validations) * 0.5:
                return "high"
            else:
                return "medium"
        else:
            return "high"
    
    def _generate_recommendation(self, precision: float, validations: List[CitationValidation]) -> str:
        """Generate actionable recommendation based on validation results"""
        if precision >= 0.9:
            return "Excellent citation quality - response is well-grounded"
        elif precision >= 0.7:
            return "Good citation quality - minor improvements possible"
        elif precision >= 0.5:
            return "Moderate citation quality - review specific citations for accuracy"
        elif precision >= 0.3:
            return "Poor citation quality - significant revision needed"
        else:
            return "Very poor citation quality - response should be regenerated"
    
    async def batch_validate(self, responses: List[Dict[str, Any]]) -> List[GroundingReport]:
        """Validate multiple responses in batch"""
        reports = []
        
        for response_data in responses:
            report = await self.validate_response_grounding(
                response_text=response_data.get('response', ''),
                citations=response_data.get('citations', []),
                response_id=response_data.get('id')
            )
            reports.append(report)
        
        return reports
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation service statistics"""
        return {
            "validation_level": self.validation_level.value,
            "source_texts_loaded": len(self.source_cache),
            "validation_cache_size": len(self.validation_cache),
            "precision_threshold": self.precision_threshold,
            "overlap_threshold": self.overlap_threshold
        }

# Global instance for easy import
citation_grounding_checker = CitationGroundingChecker()
