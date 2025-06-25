"""
Voice Parameter Adaptation Based on Content Type

This module adapts voice parameters (speed, pitch, tone, pauses) based on the type
and nature of spiritual content being spoken. Different content types require
different vocal characteristics for optimal delivery.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of spiritual content that require different voice parameters"""
    SCRIPTURE_QUOTE = "scripture_quote"           # Direct quotes from sacred texts
    PHILOSOPHICAL_TEACHING = "philosophical_teaching"  # Deep philosophical explanations
    PERSONAL_GUIDANCE = "personal_guidance"       # Personal spiritual advice
    PRAYER_MEDITATION = "prayer_meditation"       # Prayer or meditation instructions
    MANTRA_CHANT = "mantra_chant"                # Mantras and chants
    STORY_NARRATIVE = "story_narrative"          # Stories from scriptures
    CASUAL_CONVERSATION = "casual_conversation"   # General conversation
    CONSOLATION_COMFORT = "consolation_comfort"   # Comforting words for distress


class VoiceParameter(Enum):
    """Voice parameters that can be adapted"""
    SPEED = "speed"                    # Speech rate (words per minute)
    PITCH = "pitch"                    # Voice pitch/tone
    VOLUME = "volume"                  # Speaking volume
    PAUSE_DURATION = "pause_duration"  # Length of pauses between phrases
    EMPHASIS = "emphasis"              # Stress on important words
    INTONATION = "intonation"         # Rise and fall of voice
    REVERENCE_LEVEL = "reverence_level" # How reverent the delivery should be


@dataclass
class VoiceSettings:
    """Voice parameter settings for content delivery"""
    speed: float = 1.0           # 0.5 to 2.0 (relative to normal speed)
    pitch: float = 1.0           # 0.5 to 2.0 (relative to normal pitch)
    volume: float = 1.0          # 0.5 to 1.5 (relative to normal volume)
    pause_duration: float = 1.0  # 0.5 to 3.0 (relative to normal pauses)
    emphasis_strength: float = 1.0  # 0.5 to 2.0 (how much to emphasize key words)
    reverence_level: float = 1.0    # 0.5 to 2.0 (how reverent the delivery)
    pre_pause: float = 0.0          # Pause before speaking (in seconds)
    post_pause: float = 0.0         # Pause after speaking (in seconds)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for API usage"""
        return {
            "speed": self.speed,
            "pitch": self.pitch,
            "volume": self.volume,
            "pause_duration": self.pause_duration,
            "emphasis_strength": self.emphasis_strength,
            "reverence_level": self.reverence_level,
            "pre_pause": self.pre_pause,
            "post_pause": self.post_pause
        }
    
    def copy(self) -> 'VoiceSettings':
        """Create a copy of this VoiceSettings instance"""
        return VoiceSettings(
            speed=self.speed,
            pitch=self.pitch,
            volume=self.volume,
            pause_duration=self.pause_duration,
            emphasis_strength=self.emphasis_strength,
            reverence_level=self.reverence_level,
            pre_pause=self.pre_pause,
            post_pause=self.post_pause
        )


@dataclass
class ContentAnalysis:
    """Analysis of content characteristics"""
    content_type: ContentType
    confidence: float = 0.0
    sacred_terms: List[str] = field(default_factory=list)
    emotional_tone: str = "neutral"  # "compassionate", "authoritative", "consoling", etc.
    length_category: str = "medium"  # "short", "medium", "long"
    complexity_level: str = "medium" # "simple", "medium", "complex"
    contains_sanskrit: bool = False
    contains_citations: bool = False
    requires_emphasis: List[str] = field(default_factory=list)


class ContentAnalyzer:
    """Analyzes content to determine appropriate voice parameters"""
    
    def __init__(self):
        self.content_patterns = self._initialize_content_patterns()
        self.sacred_terms = self._initialize_sacred_terms()
        self.emotional_indicators = self._initialize_emotional_indicators()
        
    def _initialize_content_patterns(self) -> Dict[ContentType, List[str]]:
        """Initialize regex patterns for content type detection"""
        return {
            ContentType.SCRIPTURE_QUOTE: [
                r'"[^"]*"',  # Quoted text
                r'as (lord )?krishna says',
                r'in the bhagavad gita',
                r'the scripture states',
                r'according to the vedas',
                r'chapter \d+ verse \d+',
                r'gita \d+\.\d+'
            ],
            ContentType.PHILOSOPHICAL_TEACHING: [
                r'the nature of',
                r'consciousness',
                r'reality',
                r'existence',
                r'what is the meaning',
                r'philosophy',
                r'metaphysical',
                r'absolute truth',
                r'ultimate reality'
            ],
            ContentType.PERSONAL_GUIDANCE: [
                r'my dear child',
                r'beloved devotee',
                r'you should',
                r'i understand your',
                r'your path',
                r'guidance for you',
                r'in your situation',
                r'dear seeker'
            ],
            ContentType.PRAYER_MEDITATION: [
                r'let us pray',
                r'meditation',
                r'close your eyes',
                r'breathe',
                r'focus on',
                r'concentrate',
                r'inner peace',
                r'divine presence'
            ],
            ContentType.MANTRA_CHANT: [
                r'om|aum',
                r'hare krishna',
                r'mantra',
                r'chant',
                r'repeat',
                r'gayatri',
                r'mahamantra'
            ],
            ContentType.STORY_NARRATIVE: [
                r'once upon a time',
                r'there was',
                r'long ago',
                r'in ancient times',
                r'the story',
                r'it happened that',
                r'arjuna asked',
                r'krishna replied'
            ],
            ContentType.CONSOLATION_COMFORT: [
                r'do not worry',
                r'be at peace',
                r'comfort',
                r'solace',
                r'difficult time',
                r'suffering',
                r'pain',
                r'distress',
                r'troubled',
                r'fear not'
            ]
        }
    
    def _initialize_sacred_terms(self) -> List[str]:
        """Initialize list of sacred terms that require special treatment"""
        return [
            "krishna", "rama", "vishnu", "shiva", "brahma", "devi",
            "bhagavad gita", "mahabharata", "ramayana", "vedas", "upanishads",
            "dharma", "karma", "moksha", "atman", "brahman", "yoga",
            "om", "aum", "mantra", "yantra", "chakra", "prana"
        ]
    
    def _initialize_emotional_indicators(self) -> Dict[str, List[str]]:
        """Initialize emotional tone indicators"""
        return {
            "compassionate": [
                "dear child", "beloved", "understand", "comfort", "peace",
                "gentle", "loving", "care", "support"
            ],
            "authoritative": [
                "must", "should", "duty", "dharma", "righteous", "commanded",
                "law", "principle", "absolute", "truth"
            ],
            "consoling": [
                "worry not", "fear not", "peace", "comfort", "solace",
                "temporary", "pass", "overcome", "strength"
            ],
            "inspiring": [
                "potential", "achieve", "grow", "evolve", "transcend",
                "enlightenment", "liberation", "freedom"
            ],
            "teaching": [
                "learn", "understand", "realize", "wisdom", "knowledge",
                "insight", "comprehend", "grasp"
            ]
        }
    
    def analyze_content(self, content: str) -> ContentAnalysis:
        """Analyze content to determine characteristics"""
        content_lower = content.lower()
        
        # Determine content type
        content_type, confidence = self._determine_content_type(content_lower)
        
        # Identify sacred terms
        sacred_terms = [term for term in self.sacred_terms if term in content_lower]
        
        # Determine emotional tone
        emotional_tone = self._determine_emotional_tone(content_lower)
        
        # Analyze length and complexity
        length_category = self._categorize_length(content)
        complexity_level = self._assess_complexity(content)
        
        # Check for Sanskrit and citations
        contains_sanskrit = self._contains_sanskrit(content)
        contains_citations = self._contains_citations(content)
        
        # Find words requiring emphasis
        requires_emphasis = self._find_emphasis_words(content)
        
        return ContentAnalysis(
            content_type=content_type,
            confidence=confidence,
            sacred_terms=sacred_terms,
            emotional_tone=emotional_tone,
            length_category=length_category,
            complexity_level=complexity_level,
            contains_sanskrit=contains_sanskrit,
            contains_citations=contains_citations,
            requires_emphasis=requires_emphasis
        )
    
    def _determine_content_type(self, content: str) -> Tuple[ContentType, float]:
        """Determine the type of content and confidence level"""
        scores = {}
        
        for content_type, patterns in self.content_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches += 1
                    score += 1
            
            # Calculate confidence based on matches
            if matches > 0:
                scores[content_type] = min(1.0, score / len(patterns))
        
        if not scores:
            return ContentType.CASUAL_CONVERSATION, 0.5
        
        # Return type with highest score
        best_type = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[best_type]
        
        return best_type, confidence
    
    def _determine_emotional_tone(self, content: str) -> str:
        """Determine the emotional tone of the content"""
        tone_scores = {}
        
        for tone, indicators in self.emotional_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content)
            if score > 0:
                tone_scores[tone] = score
        
        if not tone_scores:
            return "neutral"
        
        return max(tone_scores.keys(), key=lambda k: tone_scores[k])
    
    def _categorize_length(self, content: str) -> str:
        """Categorize content by length"""
        word_count = len(content.split())
        
        if word_count < 20:
            return "short"
        elif word_count < 100:
            return "medium"
        else:
            return "long"
    
    def _assess_complexity(self, content: str) -> str:
        """Assess the complexity level of content"""
        # Simple heuristics for complexity
        complex_indicators = [
            "consciousness", "metaphysical", "ontological", "epistemological",
            "transcendental", "absolute", "ultimate reality", "phenomenological"
        ]
        
        content_lower = content.lower()
        complex_count = sum(1 for indicator in complex_indicators if indicator in content_lower)
        
        avg_word_length = sum(len(word) for word in content.split()) / max(len(content.split()), 1)
        
        if complex_count >= 2 or avg_word_length > 6:
            return "complex"
        elif complex_count >= 1 or avg_word_length > 5:
            return "medium"
        else:
            return "simple"
    
    def _contains_sanskrit(self, content: str) -> bool:
        """Check if content contains Sanskrit terms"""
        sanskrit_terms = [
            "dharma", "karma", "moksha", "atman", "brahman", "yoga",
            "mantra", "yantra", "chakra", "prana", "samsara", "nirvana",
            "om", "aum", "ahimsa", "satya", "tapas", "bhakti", "jnana"
        ]
        
        content_lower = content.lower()
        return any(term in content_lower for term in sanskrit_terms)
    
    def _contains_citations(self, content: str) -> bool:
        """Check if content contains scriptural citations"""
        citation_patterns = [
            r'bhagavad gita \d+\.\d+',
            r'chapter \d+ verse \d+',
            r'according to.*scripture',
            r'in the.*veda',
            r'upanishad'
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in citation_patterns)
    
    def _find_emphasis_words(self, content: str) -> List[str]:
        """Find words that should be emphasized"""
        emphasis_words = [
            "dharma", "karma", "truth", "divine", "sacred", "eternal",
            "absolute", "love", "compassion", "wisdom", "peace",
            "krishna", "god", "lord", "devotion", "surrender"
        ]
        
        content_lower = content.lower()
        found_words = []
        
        for word in emphasis_words:
            if word in content_lower:
                found_words.append(word)
        
        return found_words


class VoiceParameterAdapter:
    """Adapts voice parameters based on content analysis"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
        self.parameter_templates = self._initialize_parameter_templates()
        
    def _initialize_parameter_templates(self) -> Dict[ContentType, VoiceSettings]:
        """Initialize voice parameter templates for each content type"""
        return {
            ContentType.SCRIPTURE_QUOTE: VoiceSettings(
                speed=0.8,           # Slower for reverence
                pitch=0.9,           # Slightly lower pitch
                volume=1.1,          # Slightly louder
                pause_duration=1.5,  # Longer pauses
                emphasis_strength=1.3, # More emphasis
                reverence_level=2.0,   # Maximum reverence
                pre_pause=1.0,       # Pause before quote
                post_pause=1.0       # Pause after quote
            ),
            
            ContentType.PHILOSOPHICAL_TEACHING: VoiceSettings(
                speed=0.85,          # Deliberate pace
                pitch=1.0,           # Normal pitch
                volume=1.0,          # Normal volume
                pause_duration=1.3,  # Thoughtful pauses
                emphasis_strength=1.2, # Moderate emphasis
                reverence_level=1.5,   # High reverence
                pre_pause=0.5,
                post_pause=0.5
            ),
            
            ContentType.PERSONAL_GUIDANCE: VoiceSettings(
                speed=0.9,           # Slightly slower
                pitch=1.1,           # Warmer pitch
                volume=0.9,          # Softer
                pause_duration=1.2,  # Gentle pauses
                emphasis_strength=1.1, # Gentle emphasis
                reverence_level=1.3,   # Moderate reverence
                pre_pause=0.3,
                post_pause=0.3
            ),
            
            ContentType.PRAYER_MEDITATION: VoiceSettings(
                speed=0.7,           # Very slow and peaceful
                pitch=0.9,           # Lower, calming pitch
                volume=0.8,          # Quiet
                pause_duration=2.0,  # Long, meditative pauses
                emphasis_strength=0.8, # Gentle emphasis
                reverence_level=1.8,   # Very reverent
                pre_pause=1.5,       # Centering pause
                post_pause=2.0       # Contemplative pause
            ),
            
            ContentType.MANTRA_CHANT: VoiceSettings(
                speed=0.6,           # Slow and rhythmic
                pitch=1.0,           # Clear tone
                volume=1.0,          # Clear volume
                pause_duration=1.0,  # Rhythmic pauses
                emphasis_strength=1.5, # Strong emphasis on sacred sounds
                reverence_level=2.0,   # Maximum reverence
                pre_pause=1.0,
                post_pause=1.0
            ),
            
            ContentType.STORY_NARRATIVE: VoiceSettings(
                speed=1.0,           # Normal storytelling pace
                pitch=1.1,           # Engaging pitch
                volume=1.0,          # Normal volume
                pause_duration=0.8,  # Natural pauses
                emphasis_strength=1.2, # Dramatic emphasis
                reverence_level=1.2,   # Moderate reverence
                pre_pause=0.5,
                post_pause=0.5
            ),
            
            ContentType.CONSOLATION_COMFORT: VoiceSettings(
                speed=0.8,           # Slow and soothing
                pitch=1.0,           # Gentle pitch
                volume=0.9,          # Soft volume
                pause_duration=1.4,  # Comforting pauses
                emphasis_strength=0.9, # Gentle emphasis
                reverence_level=1.4,   # Compassionate reverence
                pre_pause=0.5,
                post_pause=0.8
            ),
            
            ContentType.CASUAL_CONVERSATION: VoiceSettings(
                speed=1.0,           # Normal speed
                pitch=1.0,           # Normal pitch
                volume=1.0,          # Normal volume
                pause_duration=1.0,  # Normal pauses
                emphasis_strength=1.0, # Normal emphasis
                reverence_level=1.0,   # Baseline reverence
                pre_pause=0.2,
                post_pause=0.2
            )
        }
    
    def adapt_parameters(self, content: str, user_preferences: Optional[Dict] = None) -> VoiceSettings:
        """
        Adapt voice parameters based on content analysis and user preferences
        
        Args:
            content: The text content to be spoken
            user_preferences: Optional user preferences to override defaults
            
        Returns:
            VoiceSettings with adapted parameters
        """
        # Analyze content
        analysis = self.analyzer.analyze_content(content)
        
        # Get base template
        base_settings = self.parameter_templates[analysis.content_type].copy()
        
        # Apply analysis-based adjustments
        adjusted_settings = self._apply_analysis_adjustments(base_settings, analysis)
        
        # Apply user preferences if provided
        if user_preferences:
            adjusted_settings = self._apply_user_preferences(adjusted_settings, user_preferences)
        
        logger.info(f"Adapted voice parameters for {analysis.content_type.value} content")
        
        return adjusted_settings
    
    def _apply_analysis_adjustments(self, settings: VoiceSettings, analysis: ContentAnalysis) -> VoiceSettings:
        """Apply adjustments based on content analysis"""
        
        # Adjust for length
        if analysis.length_category == "long":
            settings.speed *= 1.1  # Slightly faster for long content
            settings.pause_duration *= 0.9  # Shorter pauses
        elif analysis.length_category == "short":
            settings.pause_duration *= 1.2  # Longer pauses for short content
        
        # Adjust for complexity
        if analysis.complexity_level == "complex":
            settings.speed *= 0.9  # Slower for complex content
            settings.pause_duration *= 1.3  # More time to process
        elif analysis.complexity_level == "simple":
            settings.speed *= 1.1  # Can be faster for simple content
        
        # Adjust for Sanskrit terms
        if analysis.contains_sanskrit:
            settings.speed *= 0.85  # Slower for Sanskrit pronunciation
            settings.emphasis_strength *= 1.2  # Emphasize Sanskrit terms
            settings.reverence_level *= 1.1  # More reverent
        
        # Adjust for citations
        if analysis.contains_citations:
            settings.pause_duration *= 1.2  # Pause around citations
            settings.emphasis_strength *= 1.1  # Emphasize citations
        
        # Adjust for emotional tone
        if analysis.emotional_tone == "consoling":
            settings.speed *= 0.9  # Slower for consolation
            settings.volume *= 0.9  # Softer
            settings.pitch *= 0.95  # Lower pitch
        elif analysis.emotional_tone == "inspiring":
            settings.volume *= 1.1  # Louder for inspiration
            settings.emphasis_strength *= 1.2  # More emphasis
        
        return settings
    
    def _apply_user_preferences(self, settings: VoiceSettings, preferences: Dict) -> VoiceSettings:
        """Apply user-specific preferences"""
        
        # Speed preference
        if "speed_preference" in preferences:
            speed_multiplier = preferences["speed_preference"]  # 0.5 to 2.0
            settings.speed *= speed_multiplier
        
        # Volume preference
        if "volume_preference" in preferences:
            volume_multiplier = preferences["volume_preference"]  # 0.5 to 1.5
            settings.volume *= volume_multiplier
        
        # Pause preference
        if "pause_preference" in preferences:
            pause_multiplier = preferences["pause_preference"]  # 0.5 to 2.0
            settings.pause_duration *= pause_multiplier
        
        # Accessibility adjustments
        if preferences.get("accessibility_mode"):
            settings.speed *= 0.8  # Slower for accessibility
            settings.pause_duration *= 1.5  # Longer pauses
            settings.volume *= 1.1  # Slightly louder
        
        return settings
    
    def get_content_analysis(self, content: str) -> ContentAnalysis:
        """Get detailed content analysis"""
        return self.analyzer.analyze_content(content)
    
    def preview_voice_settings(self, content: str) -> Dict[str, Any]:
        """Preview voice settings that would be applied"""
        analysis = self.analyzer.analyze_content(content)
        settings = self.adapt_parameters(content)
        
        return {
            "content_analysis": {
                "type": analysis.content_type.value,
                "confidence": analysis.confidence,
                "emotional_tone": analysis.emotional_tone,
                "length": analysis.length_category,
                "complexity": analysis.complexity_level,
                "sacred_terms": analysis.sacred_terms,
                "contains_sanskrit": analysis.contains_sanskrit,
                "contains_citations": analysis.contains_citations,
                "emphasis_words": analysis.requires_emphasis
            },
            "voice_settings": settings.to_dict(),
            "recommendations": self._generate_recommendations(analysis, settings)
        }
    
    def _generate_recommendations(self, analysis: ContentAnalysis, settings: VoiceSettings) -> List[str]:
        """Generate recommendations for optimal delivery"""
        recommendations = []
        
        if analysis.content_type == ContentType.SCRIPTURE_QUOTE:
            recommendations.append("Pause before and after quotes for reverence")
            recommendations.append("Emphasize sacred terms with proper pronunciation")
        
        if analysis.contains_sanskrit:
            recommendations.append("Slow down for Sanskrit terms")
            recommendations.append("Use proper Sanskrit pronunciation")
        
        if analysis.emotional_tone == "consoling":
            recommendations.append("Use gentle, soothing tone")
            recommendations.append("Allow extra time for emotional processing")
        
        if analysis.complexity_level == "complex":
            recommendations.append("Allow pauses for comprehension")
            recommendations.append("Emphasize key philosophical concepts")
        
        if settings.reverence_level > 1.5:
            recommendations.append("Maintain divine dignity throughout")
            recommendations.append("Speak with appropriate spiritual gravitas")
        
        return recommendations


# Convenience functions for integration

def adapt_voice_for_content(content: str, user_preferences: Optional[Dict] = None) -> VoiceSettings:
    """
    Convenience function to adapt voice parameters for content
    
    Args:
        content: Text content to be spoken
        user_preferences: Optional user preferences
        
    Returns:
        VoiceSettings with adapted parameters
    """
    adapter = VoiceParameterAdapter()
    return adapter.adapt_parameters(content, user_preferences)


def analyze_spiritual_content(content: str) -> ContentAnalysis:
    """
    Convenience function to analyze spiritual content
    
    Args:
        content: Text content to analyze
        
    Returns:
        ContentAnalysis with detailed analysis
    """
    analyzer = ContentAnalyzer()
    return analyzer.analyze_content(content)


def preview_voice_adaptation(content: str) -> Dict[str, Any]:
    """
    Convenience function to preview voice adaptation
    
    Args:
        content: Text content to preview
        
    Returns:
        Dictionary with analysis and settings preview
    """
    adapter = VoiceParameterAdapter()
    return adapter.preview_voice_settings(content)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    print("=== Voice Parameter Adaptation Demo ===\n")
    
    adapter = VoiceParameterAdapter()
    
    test_contents = [
        # Scripture quote
        'As Lord Krishna says in Bhagavad Gita 2.47: "You have a right to perform your prescribed duty, but do not be attached to the results."',
        
        # Personal guidance
        "My dear child, I understand your struggles with finding your dharma. Let me guide you through this difficult time with compassion.",
        
        # Meditation instruction
        "Close your eyes, breathe deeply, and focus on the divine presence within. Let Om resonate through your being.",
        
        # Philosophical teaching
        "The nature of consciousness and its relationship to ultimate reality is a profound mystery that requires deep contemplation.",
        
        # Consolation
        "Do not worry, beloved devotee. This suffering is temporary, and through surrender, you will find eternal peace."
    ]
    
    for i, content in enumerate(test_contents, 1):
        print(f"Test Content {i}:")
        print(f"Content: {content[:80]}...")
        
        preview = adapter.preview_voice_settings(content)
        
        print(f"Content Type: {preview['content_analysis']['type']}")
        print(f"Emotional Tone: {preview['content_analysis']['emotional_tone']}")
        print(f"Complexity: {preview['content_analysis']['complexity']}")
        
        settings = preview['voice_settings']
        print(f"Voice Settings:")
        print(f"  Speed: {settings['speed']:.2f}")
        print(f"  Pitch: {settings['pitch']:.2f}")
        print(f"  Reverence: {settings['reverence_level']:.2f}")
        print(f"  Pause Duration: {settings['pause_duration']:.2f}")
        
        if preview['recommendations']:
            print("Recommendations:")
            for rec in preview['recommendations'][:2]:  # Show first 2
                print(f"  • {rec}")
        
        print("-" * 80 + "\n")
    
    print("Voice parameter adaptation demo completed!")
