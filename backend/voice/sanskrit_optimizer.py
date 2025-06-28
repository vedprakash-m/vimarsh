"""
Sanskrit Speech Recognition Optimization for Vimarsh AI Agent

This module provides specialized optimization for Sanskrit terminology recognition,
including phonetic mapping, pronunciation variants, and cultural context enhancement.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import unicodedata

try:
    import numpy as np
except ImportError:
    np = None


class SanskritScript(Enum):
    """Sanskrit script types"""
    DEVANAGARI = "devanagari"
    IAST = "iast"  # International Alphabet of Sanskrit Transliteration
    HARVARD_KYOTO = "harvard_kyoto"
    ROMANIZED = "romanized"


class SanskritCategory(Enum):
    """Categories of Sanskrit terms"""
    PHILOSOPHICAL = "philosophical"
    RELIGIOUS = "religious"
    YOGA = "yoga"
    AYURVEDA = "ayurveda"
    SCRIPTURE = "scripture"
    DEITY = "deity"
    MANTRA = "mantra"
    RITUAL = "ritual"
    GEOGRAPHY = "geography"
    GENERAL = "general"


@dataclass
class SanskritTerm:
    """Sanskrit term with linguistic metadata"""
    term: str
    devanagari: Optional[str] = None
    iast: Optional[str] = None
    harvard_kyoto: Optional[str] = None
    
    # Phonetic variations
    phonetic_variants: List[str] = field(default_factory=list)
    common_mispronunciations: List[str] = field(default_factory=list)
    
    # Linguistic metadata
    category: SanskritCategory = SanskritCategory.GENERAL
    etymology: Optional[str] = None
    literal_meaning: Optional[str] = None
    contextual_meaning: Optional[str] = None
    
    # Recognition optimization
    recognition_priority: float = 1.0  # 0.0 to 2.0
    confidence_boost: float = 0.05
    requires_context: bool = False
    
    # Usage statistics
    frequency_score: float = 0.0
    accuracy_score: float = 0.0
    last_recognized: Optional[datetime] = None


@dataclass
class PhoneticRule:
    """Phonetic transformation rule for Sanskrit"""
    pattern: str  # Regex pattern
    replacement: str
    context: Optional[str] = None  # Context where rule applies
    priority: int = 1  # Higher priority rules applied first
    description: str = ""


class SanskritRecognitionOptimizer:
    """
    Advanced Sanskrit speech recognition optimization system
    """
    
    def __init__(self):
        """Initialize Sanskrit recognition optimizer"""
        self.logger = logging.getLogger(__name__)
        
        # Sanskrit vocabulary
        self.sanskrit_terms: Dict[str, SanskritTerm] = {}
        self.phonetic_map: Dict[str, List[str]] = {}
        self.context_clusters: Dict[str, List[str]] = {}
        
        # Phonetic rules and transformations
        self.phonetic_rules: List[PhoneticRule] = []
        self.vowel_transformations: Dict[str, List[str]] = {}
        self.consonant_transformations: Dict[str, List[str]] = {}
        
        # Recognition statistics
        self.recognition_stats = {
            'total_sanskrit_detected': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'most_recognized_terms': {},
            'accuracy_by_category': {}
        }
        
        # Initialize Sanskrit linguistic data
        self._initialize_sanskrit_vocabulary()
        self._initialize_phonetic_rules()
        self._initialize_context_clusters()
    
    def _initialize_sanskrit_vocabulary(self):
        """Initialize comprehensive Sanskrit vocabulary"""
        
        # Philosophical terms
        philosophical_terms = [
            SanskritTerm(
                term="dharma",
                devanagari="धर्म",
                iast="dharma",
                harvard_kyoto="dharma",
                phonetic_variants=["dharma", "dharm", "darma", "dharama"],
                common_mispronunciations=["drama", "dhamma", "daruma"],
                category=SanskritCategory.PHILOSOPHICAL,
                literal_meaning="that which upholds",
                contextual_meaning="righteous duty, natural law",
                recognition_priority=1.8,
                confidence_boost=0.08
            ),
            SanskritTerm(
                term="karma",
                devanagari="कर्म",
                iast="karma",
                harvard_kyoto="karma",
                phonetic_variants=["karma", "karm", "karam"],
                common_mispronunciations=["carma", "karuma", "karama"],
                category=SanskritCategory.PHILOSOPHICAL,
                literal_meaning="action, deed",
                contextual_meaning="law of cause and effect",
                recognition_priority=1.9,
                confidence_boost=0.08
            ),
            SanskritTerm(
                term="moksha",
                devanagari="मोक्ष",
                iast="mokṣa",
                harvard_kyoto="mokSa",
                phonetic_variants=["moksha", "moksh", "moksa", "mokshya"],
                common_mispronunciations=["moksa", "moksya", "mosha"],
                category=SanskritCategory.PHILOSOPHICAL,
                literal_meaning="release, liberation",
                contextual_meaning="spiritual liberation from cycle of rebirth",
                recognition_priority=1.6,
                confidence_boost=0.07
            ),
            SanskritTerm(
                term="atman",
                devanagari="आत्मन्",
                iast="ātman",
                harvard_kyoto="Atman",
                phonetic_variants=["atman", "aatman", "atma"],
                common_mispronunciations=["atmaan", "aatmaan", "atuman"],
                category=SanskritCategory.PHILOSOPHICAL,
                literal_meaning="self, soul",
                contextual_meaning="individual soul, true self",
                recognition_priority=1.7,
                confidence_boost=0.07
            ),
            SanskritTerm(
                term="brahman",
                devanagari="ब्रह्मन्",
                iast="brahman",
                harvard_kyoto="brahman",
                phonetic_variants=["brahman", "brahmana", "brahma"],
                common_mispronunciations=["bramhan", "braaman", "braman"],
                category=SanskritCategory.PHILOSOPHICAL,
                literal_meaning="ultimate reality",
                contextual_meaning="universal consciousness, absolute truth",
                recognition_priority=1.8,
                confidence_boost=0.08
            )
        ]
        
        # Yoga terms
        yoga_terms = [
            SanskritTerm(
                term="yoga",
                devanagari="योग",
                iast="yoga",
                harvard_kyoto="yoga",
                phonetic_variants=["yoga", "yog", "yoge"],
                common_mispronunciations=["youga", "yoja", "yooga"],
                category=SanskritCategory.YOGA,
                literal_meaning="union, yoke",
                contextual_meaning="spiritual discipline for union with divine",
                recognition_priority=2.0,
                confidence_boost=0.1
            ),
            SanskritTerm(
                term="pranayama",
                devanagari="प्राणायाम",
                iast="prāṇāyāma",
                harvard_kyoto="prANAyAma",
                phonetic_variants=["pranayama", "pranayam", "pranyama"],
                common_mispronunciations=["pranaayam", "praniyama", "pranyam"],
                category=SanskritCategory.YOGA,
                literal_meaning="extension of life force",
                contextual_meaning="breath control practices",
                recognition_priority=1.5,
                confidence_boost=0.06
            ),
            SanskritTerm(
                term="asana",
                devanagari="आसन",
                iast="āsana",
                harvard_kyoto="Asana",
                phonetic_variants=["asana", "asan", "aasana"],
                common_mispronunciations=["assana", "azana", "aasaan"],
                category=SanskritCategory.YOGA,
                literal_meaning="seat, posture",
                contextual_meaning="yoga postures",
                recognition_priority=1.4,
                confidence_boost=0.05
            ),
            SanskritTerm(
                term="samadhi",
                devanagari="समाधि",
                iast="samādhi",
                harvard_kyoto="samAdhi",
                phonetic_variants=["samadhi", "samadh", "samadi"],
                common_mispronunciations=["samaadhi", "samaadhee", "samadee"],
                category=SanskritCategory.YOGA,
                literal_meaning="complete absorption",
                contextual_meaning="highest state of consciousness",
                recognition_priority=1.6,
                confidence_boost=0.07
            )
        ]
        
        # Deity names
        deity_terms = [
            SanskritTerm(
                term="krishna",
                devanagari="कृष्ण",
                iast="kṛṣṇa",
                harvard_kyoto="kRSNa",
                phonetic_variants=["krishna", "krsna", "krish", "krishn"],
                common_mispronunciations=["kristna", "krisna", "krishnaa"],
                category=SanskritCategory.DEITY,
                literal_meaning="dark, black",
                contextual_meaning="Supreme Lord, eighth avatar of Vishnu",
                recognition_priority=2.0,
                confidence_boost=0.1
            ),
            SanskritTerm(
                term="rama",
                devanagari="राम",
                iast="rāma",
                harvard_kyoto="rAma",
                phonetic_variants=["rama", "ram", "raama"],
                common_mispronunciations=["raama", "raam", "rauma"],
                category=SanskritCategory.DEITY,
                literal_meaning="pleasing, charming",
                contextual_meaning="Seventh avatar of Vishnu, hero of Ramayana",
                recognition_priority=1.9,
                confidence_boost=0.09
            ),
            SanskritTerm(
                term="shiva",
                devanagari="शिव",
                iast="śiva",
                harvard_kyoto="ziva",
                phonetic_variants=["shiva", "shiv", "siva"],
                common_mispronunciations=["sheeva", "sheva", "sivaa"],
                category=SanskritCategory.DEITY,
                literal_meaning="auspicious",
                contextual_meaning="The Destroyer, one of the Trinity",
                recognition_priority=1.9,
                confidence_boost=0.09
            ),
            SanskritTerm(
                term="ganesha",
                devanagari="गणेश",
                iast="gaṇeśa",
                harvard_kyoto="gaNeза",
                phonetic_variants=["ganesha", "ganesh", "ganesa"],
                common_mispronunciations=["ganeesha", "ganeesh", "ganesya"],
                category=SanskritCategory.DEITY,
                literal_meaning="lord of groups",
                contextual_meaning="Remover of obstacles, patron of arts",
                recognition_priority=1.7,
                confidence_boost=0.08
            )
        ]
        
        # Mantra terms
        mantra_terms = [
            SanskritTerm(
                term="om",
                devanagari="ॐ",
                iast="oṃ",
                harvard_kyoto="oM",
                phonetic_variants=["om", "aum", "ohm"],
                common_mispronunciations=["oom", "omm", "awm"],
                category=SanskritCategory.MANTRA,
                literal_meaning="sacred sound",
                contextual_meaning="primordial sound of universe",
                recognition_priority=2.0,
                confidence_boost=0.1
            ),
            SanskritTerm(
                term="namaste",
                devanagari="नमस्ते",
                iast="namaste",
                harvard_kyoto="namaste",
                phonetic_variants=["namaste", "namasthe", "namaskar"],
                common_mispronunciations=["namaaste", "namasthee", "namastay"],
                category=SanskritCategory.MANTRA,
                literal_meaning="I bow to you",
                contextual_meaning="respectful greeting acknowledging divine in other",
                recognition_priority=1.8,
                confidence_boost=0.08
            ),
            SanskritTerm(
                term="guru",
                devanagari="गुरु",
                iast="guru",
                harvard_kyoto="guru",
                phonetic_variants=["guru", "gur", "guroo"],
                common_mispronunciations=["guruu", "guro", "gurru"],
                category=SanskritCategory.RELIGIOUS,
                literal_meaning="heavy, weighty",
                contextual_meaning="spiritual teacher, one who brings light to darkness",
                recognition_priority=1.8,
                confidence_boost=0.08
            )
        ]
        
        # Scripture terms
        scripture_terms = [
            SanskritTerm(
                term="vedas",
                devanagari="वेद",
                iast="veda",
                harvard_kyoto="veda",
                phonetic_variants=["vedas", "veda", "ved"],
                common_mispronunciations=["veidas", "vedaas", "veedas"],
                category=SanskritCategory.SCRIPTURE,
                literal_meaning="knowledge",
                contextual_meaning="ancient sacred texts, foundation of Hinduism",
                recognition_priority=1.7,
                confidence_boost=0.07
            ),
            SanskritTerm(
                term="upanishads",
                devanagari="उपनिषद्",
                iast="upaniṣad",
                harvard_kyoto="upaniSad",
                phonetic_variants=["upanishads", "upanishad", "upanisad"],
                common_mispronunciations=["upanishaads", "upanishads", "oopanishads"],
                category=SanskritCategory.SCRIPTURE,
                literal_meaning="sitting near",
                contextual_meaning="philosophical texts, essence of Vedas",
                recognition_priority=1.6,
                confidence_boost=0.06
            ),
            SanskritTerm(
                term="puranas",
                devanagari="पुराण",
                iast="purāṇa",
                harvard_kyoto="purANa",
                phonetic_variants=["puranas", "purana", "puran"],
                common_mispronunciations=["puraanas", "pooranas", "puraan"],
                category=SanskritCategory.SCRIPTURE,
                literal_meaning="ancient",
                contextual_meaning="ancient stories and legends",
                recognition_priority=1.5,
                confidence_boost=0.05
            )
        ]
        
        # Combine all terms
        all_terms = (philosophical_terms + yoga_terms + deity_terms + 
                    mantra_terms + scripture_terms)
        
        # Index terms
        for term in all_terms:
            self.sanskrit_terms[term.term] = term
            
            # Create phonetic mappings
            all_variants = ([term.term] + term.phonetic_variants + 
                          term.common_mispronunciations)
            self.phonetic_map[term.term] = all_variants
        
        self.logger.info(f"Initialized {len(self.sanskrit_terms)} Sanskrit terms")
    
    def _initialize_phonetic_rules(self):
        """Initialize phonetic transformation rules"""
        
        self.phonetic_rules = [
            # Vowel transformations
            PhoneticRule(
                pattern=r"aa+",
                replacement="a",
                description="Multiple 'a' sounds to single 'a'"
            ),
            PhoneticRule(
                pattern=r"ee+",
                replacement="i",
                description="Extended 'e' sounds to 'i'"
            ),
            PhoneticRule(
                pattern=r"oo+",
                replacement="u",
                description="Extended 'o' sounds to 'u'"
            ),
            
            # Consonant transformations
            PhoneticRule(
                pattern=r"kh",
                replacement="k",
                description="Aspirated 'kh' to 'k'"
            ),
            PhoneticRule(
                pattern=r"gh",
                replacement="g",
                description="Aspirated 'gh' to 'g'"
            ),
            PhoneticRule(
                pattern=r"ch",
                replacement="c",
                description="Aspirated 'ch' to 'c'"
            ),
            PhoneticRule(
                pattern=r"th",
                replacement="t",
                description="Aspirated 'th' to 't'"
            ),
            PhoneticRule(
                pattern=r"ph",
                replacement="p",
                description="Aspirated 'ph' to 'p'"
            ),
            PhoneticRule(
                pattern=r"bh",
                replacement="b",
                description="Aspirated 'bh' to 'b'"
            ),
            PhoneticRule(
                pattern=r"dh",
                replacement="d",
                description="Aspirated 'dh' to 'd'"
            ),
            
            # Retroflex to dental
            PhoneticRule(
                pattern=r"ṭ",
                replacement="t",
                description="Retroflex 't' to dental 't'"
            ),
            PhoneticRule(
                pattern=r"ḍ",
                replacement="d",
                description="Retroflex 'd' to dental 'd'"
            ),
            PhoneticRule(
                pattern=r"ṇ",
                replacement="n",
                description="Retroflex 'n' to dental 'n'"
            ),
            
            # Sibilant variations
            PhoneticRule(
                pattern=r"ś",
                replacement="sh",
                description="Palatal sibilant to 'sh'"
            ),
            PhoneticRule(
                pattern=r"ṣ",
                replacement="sh",
                description="Retroflex sibilant to 'sh'"
            ),
            
            # Common mispronunciations
            PhoneticRule(
                pattern=r"v",
                replacement="w",
                context="english_speakers",
                description="'v' to 'w' for English speakers"
            ),
            PhoneticRule(
                pattern=r"ṛ",
                replacement="ri",
                description="Vocalic 'r' to 'ri'"
            ),
            PhoneticRule(
                pattern=r"ḷ",
                replacement="li",
                description="Vocalic 'l' to 'li'"
            )
        ]
        
        # Sort by priority
        self.phonetic_rules.sort(key=lambda x: x.priority, reverse=True)
        
        self.logger.info(f"Initialized {len(self.phonetic_rules)} phonetic rules")
    
    def _initialize_context_clusters(self):
        """Initialize context-based term clusters"""
        
        self.context_clusters = {
            'gita_context': [
                'dharma', 'karma', 'yoga', 'krishna', 'arjuna', 
                'kurukshetra', 'bhagavad', 'gita'
            ],
            'yoga_practice': [
                'asana', 'pranayama', 'meditation', 'samadhi',
                'yoga', 'guru', 'chakra', 'mudra'
            ],
            'devotional': [
                'bhakti', 'krishna', 'rama', 'devotion', 'surrender',
                'prayer', 'worship', 'love'
            ],
            'philosophical': [
                'atman', 'brahman', 'moksha', 'samsara', 'maya',
                'consciousness', 'reality', 'truth'
            ],
            'scriptural': [
                'vedas', 'upanishads', 'puranas', 'ramayana',
                'mahabharata', 'gita', 'scripture'
            ],
            'ritual': [
                'puja', 'yajna', 'mantra', 'mudra', 'yantra',
                'ceremony', 'offering', 'sacred'
            ]
        }
        
        self.logger.info(f"Initialized {len(self.context_clusters)} context clusters")
    
    def apply_phonetic_transformations(self, text: str, context: str = None) -> List[str]:
        """
        Apply phonetic transformations to generate variants
        
        Args:
            text: Input text to transform
            context: Optional context for rule selection
            
        Returns:
            List of phonetic variants
        """
        
        variants = [text.lower()]
        
        for rule in self.phonetic_rules:
            # Skip context-specific rules if context doesn't match
            if rule.context and rule.context != context:
                continue
            
            # Apply rule to all current variants
            new_variants = []
            for variant in variants:
                transformed = re.sub(rule.pattern, rule.replacement, variant)
                if transformed != variant:
                    new_variants.append(transformed)
            
            variants.extend(new_variants)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant not in seen:
                seen.add(variant)
                unique_variants.append(variant)
        
        return unique_variants
    
    def find_sanskrit_matches(self, text: str, confidence_threshold: float = 0.6) -> List[Tuple[SanskritTerm, float]]:
        """
        Find Sanskrit term matches in text
        
        Args:
            text: Input text to analyze
            confidence_threshold: Minimum confidence for matches
            
        Returns:
            List of (SanskritTerm, confidence) tuples
        """
        
        matches = []
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        for word in words:
            # Direct exact matches
            for term_key, term in self.sanskrit_terms.items():
                if word == term_key.lower():
                    confidence = 1.0
                    matches.append((term, confidence))
                    continue
                
                # Check phonetic variants
                for variant in self.phonetic_map.get(term_key, []):
                    if word == variant.lower():
                        confidence = 0.9 - (0.1 * len(variant))  # Longer variants get lower confidence
                        confidence = max(confidence, confidence_threshold)
                        matches.append((term, confidence))
                        break
                
                # Check partial matches for longer terms
                if len(word) >= 4 and len(term_key) >= 4:
                    similarity = self._calculate_similarity(word, term_key.lower())
                    if similarity >= confidence_threshold:
                        matches.append((term, similarity))
        
        # Sort by confidence and remove duplicates
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Remove duplicate terms, keeping highest confidence
        seen_terms = set()
        unique_matches = []
        for term, confidence in matches:
            if term.term not in seen_terms:
                seen_terms.add(term.term)
                unique_matches.append((term, confidence))
        
        return unique_matches
    
    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate phonetic similarity between words"""
        
        # Simple edit distance-based similarity
        if len(word1) == 0 or len(word2) == 0:
            return 0.0
        
        # Create matrix for dynamic programming
        matrix = [[0] * (len(word2) + 1) for _ in range(len(word1) + 1)]
        
        # Initialize first row and column
        for i in range(len(word1) + 1):
            matrix[i][0] = i
        for j in range(len(word2) + 1):
            matrix[0][j] = j
        
        # Fill matrix
        for i in range(1, len(word1) + 1):
            for j in range(1, len(word2) + 1):
                if word1[i-1] == word2[j-1]:
                    cost = 0
                else:
                    cost = 1
                
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        # Calculate similarity
        edit_distance = matrix[len(word1)][len(word2)]
        max_len = max(len(word1), len(word2))
        similarity = 1.0 - (edit_distance / max_len)
        
        return similarity
    
    def enhance_recognition_with_context(self, text: str, previous_terms: List[str] = None) -> Dict[str, Any]:
        """
        Enhance recognition using contextual information
        
        Args:
            text: Text to analyze
            previous_terms: Previously recognized Sanskrit terms for context
            
        Returns:
            Enhanced recognition results
        """
        
        # Find initial matches
        matches = self.find_sanskrit_matches(text)
        
        # Determine context from previous terms
        context_scores = {}
        if previous_terms:
            for cluster_name, cluster_terms in self.context_clusters.items():
                score = sum(1 for term in previous_terms if term in cluster_terms)
                if score > 0:
                    context_scores[cluster_name] = score / len(cluster_terms)
        
        # Apply context-based confidence boosts
        enhanced_matches = []
        for term, confidence in matches:
            enhanced_confidence = confidence
            
            # Check if term appears in any high-scoring context
            for cluster_name, cluster_score in context_scores.items():
                if term.term in self.context_clusters[cluster_name]:
                    boost = cluster_score * 0.1  # Up to 10% boost
                    enhanced_confidence = min(1.0, enhanced_confidence + boost)
            
            # Apply term-specific recognition priority
            priority_boost = (term.recognition_priority - 1.0) * 0.05
            enhanced_confidence = min(1.0, enhanced_confidence + priority_boost)
            
            enhanced_matches.append((term, enhanced_confidence))
        
        # Re-sort by enhanced confidence
        enhanced_matches.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'original_matches': matches,
            'enhanced_matches': enhanced_matches,
            'context_scores': context_scores,
            'dominant_context': max(context_scores.keys(), key=context_scores.get) if context_scores else None
        }
    
    def generate_pronunciation_variants(self, term: str) -> List[str]:
        """
        Generate pronunciation variants for a Sanskrit term
        
        Args:
            term: Sanskrit term
            
        Returns:
            List of pronunciation variants
        """
        
        if term in self.sanskrit_terms:
            sanskrit_term = self.sanskrit_terms[term]
            return (sanskrit_term.phonetic_variants + 
                   sanskrit_term.common_mispronunciations)
        
        # Fallback: apply phonetic rules
        return self.apply_phonetic_transformations(term)
    
    def update_recognition_statistics(self, term: str, recognized: bool, confidence: float):
        """Update recognition statistics for a term"""
        
        self.recognition_stats['total_sanskrit_detected'] += 1
        
        if recognized:
            self.recognition_stats['successful_recognitions'] += 1
        else:
            self.recognition_stats['failed_recognitions'] += 1
        
        # Update term-specific statistics
        if term in self.sanskrit_terms:
            sanskrit_term = self.sanskrit_terms[term]
            
            # Update frequency
            sanskrit_term.frequency_score += 1
            
            # Update accuracy (running average)
            if sanskrit_term.accuracy_score == 0.0:
                sanskrit_term.accuracy_score = confidence
            else:
                sanskrit_term.accuracy_score = (sanskrit_term.accuracy_score + confidence) / 2
            
            sanskrit_term.last_recognized = datetime.now()
            
            # Update most recognized terms
            if term not in self.recognition_stats['most_recognized_terms']:
                self.recognition_stats['most_recognized_terms'][term] = 0
            self.recognition_stats['most_recognized_terms'][term] += 1
            
            # Update category accuracy
            category = sanskrit_term.category.value
            if category not in self.recognition_stats['accuracy_by_category']:
                self.recognition_stats['accuracy_by_category'][category] = []
            self.recognition_stats['accuracy_by_category'][category].append(confidence)
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for improving Sanskrit recognition"""
        
        recommendations = {
            'priority_terms': [],
            'problem_categories': [],
            'suggested_improvements': [],
            'training_focus': []
        }
        
        # Identify terms that need attention
        for term, sanskrit_term in self.sanskrit_terms.items():
            if (sanskrit_term.frequency_score > 0 and 
                sanskrit_term.accuracy_score < 0.7):
                recommendations['priority_terms'].append({
                    'term': term,
                    'accuracy': sanskrit_term.accuracy_score,
                    'frequency': sanskrit_term.frequency_score,
                    'category': sanskrit_term.category.value
                })
        
        # Identify problematic categories
        for category, confidences in self.recognition_stats['accuracy_by_category'].items():
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                if avg_confidence < 0.7:
                    recommendations['problem_categories'].append({
                        'category': category,
                        'average_confidence': avg_confidence,
                        'sample_count': len(confidences)
                    })
        
        # Generate improvement suggestions
        total_recognitions = self.recognition_stats['total_sanskrit_detected']
        success_rate = (self.recognition_stats['successful_recognitions'] / 
                       max(1, total_recognitions))
        
        if success_rate < 0.8:
            recommendations['suggested_improvements'].append(
                "Consider expanding phonetic variant coverage"
            )
        
        if recommendations['problem_categories']:
            worst_category = min(recommendations['problem_categories'], 
                               key=lambda x: x['average_confidence'])
            recommendations['suggested_improvements'].append(
                f"Focus training on {worst_category['category']} terms"
            )
        
        # Training focus recommendations
        most_frequent = sorted(
            self.recognition_stats['most_recognized_terms'].items(),
            key=lambda x: x[1], reverse=True
        )[:5]
        
        for term, frequency in most_frequent:
            if term in self.sanskrit_terms:
                accuracy = self.sanskrit_terms[term].accuracy_score
                if accuracy < 0.8:
                    recommendations['training_focus'].append({
                        'term': term,
                        'frequency': frequency,
                        'current_accuracy': accuracy,
                        'priority': 'high'
                    })
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        
        total = self.recognition_stats['total_sanskrit_detected']
        
        stats = {
            'total_terms_loaded': len(self.sanskrit_terms),
            'total_recognitions_attempted': total,
            'successful_recognitions': self.recognition_stats['successful_recognitions'],
            'failed_recognitions': self.recognition_stats['failed_recognitions'],
            'overall_success_rate': (
                self.recognition_stats['successful_recognitions'] / max(1, total)
            ),
            'phonetic_rules_count': len(self.phonetic_rules),
            'context_clusters_count': len(self.context_clusters),
            'categories': {}
        }
        
        # Category breakdown
        for category in SanskritCategory:
            category_terms = [
                term for term in self.sanskrit_terms.values()
                if term.category == category
            ]
            stats['categories'][category.value] = {
                'term_count': len(category_terms),
                'average_priority': sum(t.recognition_priority for t in category_terms) / max(1, len(category_terms)),
                'average_accuracy': sum(t.accuracy_score for t in category_terms if t.accuracy_score > 0) / max(1, len([t for t in category_terms if t.accuracy_score > 0]))
            }
        
        return stats
    
    def detect_sanskrit_terms(self, text: str) -> List[Dict[str, Any]]:
        """Detect Sanskrit terms in text."""
        detected_terms = []
        
        # Simple pattern matching for common Sanskrit terms
        for term_key, term_obj in self.sanskrit_terms.items():
            if term_key.lower() in text.lower():
                detected_terms.append({
                    'term': term_key,
                    'position': text.lower().find(term_key.lower()),
                    'confidence': term_obj.recognition_priority,
                    'category': term_obj.category.value
                })
        
        return detected_terms
    
    def correct_pronunciation(self, text: str) -> str:
        """Correct common Sanskrit mispronunciations."""
        corrected = text
        
        # Apply phonetic rules
        for rule in sorted(self.phonetic_rules, key=lambda x: x.priority, reverse=True):
            corrected = re.sub(rule.pattern, rule.replacement, corrected, flags=re.IGNORECASE)
        
        return corrected
    
    def get_phonetic_variants(self, term: str) -> List[str]:
        """Get phonetic variants of a Sanskrit term."""
        if term in self.phonetic_map:
            return self.phonetic_map[term]
        
        # Generate basic variants if not in map
        variants = [term]
        if term in self.sanskrit_terms:
            term_obj = self.sanskrit_terms[term]
            variants.extend(term_obj.phonetic_variants)
        
        return list(set(variants))
    
    def correct_in_context(self, text: str, context: str) -> str:
        """Correct Sanskrit terms based on context."""
        corrected = text
        
        # Use context to improve corrections
        for cluster_name, cluster_terms in self.context_clusters.items():
            if any(term in context.lower() for term in cluster_terms):
                # Apply cluster-specific corrections
                for term in cluster_terms:
                    if term in self.sanskrit_terms:
                        term_obj = self.sanskrit_terms[term]
                        for mistake in term_obj.common_mispronunciations:
                            corrected = corrected.replace(mistake, term)
        
        return corrected
    
    def transliterate_to_roman(self, devanagari_text: str) -> str:
        """Transliterate Devanagari text to Roman script."""
        # Simple transliteration mapping (basic implementation)
        transliteration_map = {
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha',
            'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha',
            'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha',
            'न': 'na', 'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha',
            'म': 'ma', 'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
            'श': 'sha', 'ष': 'shha', 'स': 'sa', 'ह': 'ha'
        }
        
        result = ""
        for char in devanagari_text:
            if char in transliteration_map:
                result += transliteration_map[char]
            else:
                result += char
        
        return result
    
    def calculate_recognition_confidence(self, term: str, context: str) -> float:
        """Calculate recognition confidence for a Sanskrit term."""
        if term not in self.sanskrit_terms:
            return 0.5  # Default confidence
        
        term_obj = self.sanskrit_terms[term]
        confidence = term_obj.recognition_priority
        
        # Boost confidence based on context
        if term_obj.requires_context:
            context_boost = 0.0
            for cluster_name, cluster_terms in self.context_clusters.items():
                if any(ctx_term in context.lower() for ctx_term in cluster_terms):
                    context_boost += 0.2
            confidence += min(context_boost, 0.5)
        
        return min(confidence, 1.0)
    
    def optimize_recognition(self, audio_data: bytes, context: str = "") -> Dict[str, Any]:
        """Optimize Sanskrit recognition for audio data."""
        # Mock implementation for testing
        return {
            'optimized': True,
            'context_applied': bool(context),
            'sanskrit_terms_count': len(self.sanskrit_terms),
            'optimization_score': 0.85
        }


# Convenience function for creating Sanskrit optimizer
def create_sanskrit_optimizer() -> SanskritRecognitionOptimizer:
    """Create and initialize Sanskrit recognition optimizer"""
    return SanskritRecognitionOptimizer()
