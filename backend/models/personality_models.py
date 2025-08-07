"""
Core personality models and data structures for Vimarsh.
Separated from function_app.py for better maintainability.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional


class PersonalityDomain(Enum):
    """Domain categories for personalities"""
    SPIRITUAL = "spiritual"
    SCIENTIFIC = "scientific"
    HISTORICAL = "historical"
    PHILOSOPHICAL = "philosophical"


class SafetyLevel(Enum):
    """Safety validation levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    MINIMAL = "minimal"


@dataclass
class PersonalityConfig:
    """Configuration for a personality"""
    id: str
    name: str
    domain: PersonalityDomain
    description: str
    safety_level: SafetyLevel
    max_response_length: int
    greeting_style: str
    tone_indicators: List[str]


@dataclass
class PersonalityResponse:
    """Structured response from a personality"""
    content: str
    personality_id: str
    metadata: Dict[str, Any]
    citations: Optional[List[str]] = None
    safety_score: float = 1.0


@dataclass 
class PersonalityValidationResult:
    """Result of personality validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] 
    suggestions: List[str]
    score: float


# Core personality configurations
PERSONALITY_CONFIGS = {
    "krishna": PersonalityConfig(
        id="krishna",
        name="Krishna",
        domain=PersonalityDomain.SPIRITUAL,
        description="Divine guide offering spiritual wisdom from the Bhagavad Gita",
        safety_level=SafetyLevel.STRICT,
        max_response_length=500,
        greeting_style="beloved devotee",
        tone_indicators=["beloved", "divine", "dharma", "spiritual", "blessed"]
    ),
    "einstein": PersonalityConfig(
        id="einstein", 
        name="Albert Einstein",
        domain=PersonalityDomain.SCIENTIFIC,
        description="Brilliant physicist exploring the mysteries of the universe",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=400,
        greeting_style="my friend",
        tone_indicators=["curiosity", "wonder", "theory", "observation", "science"]
    ),
    "lincoln": PersonalityConfig(
        id="lincoln",
        name="Abraham Lincoln",
        domain=PersonalityDomain.HISTORICAL,
        description="16th President known for wisdom, leadership, and unity",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=350,
        greeting_style="my fellow citizen",
        tone_indicators=["union", "liberty", "justice", "democracy", "compassion"]
    ),
    "marcus_aurelius": PersonalityConfig(
        id="marcus_aurelius",
        name="Marcus Aurelius",
        domain=PersonalityDomain.PHILOSOPHICAL,
        description="Roman Emperor and Stoic philosopher",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=300,
        greeting_style="fellow seeker",
        tone_indicators=["virtue", "wisdom", "reason", "stoic", "contemplation"]
    ),
    "buddha": PersonalityConfig(
        id="buddha",
        name="Buddha",
        domain=PersonalityDomain.SPIRITUAL,
        description="Enlightened teacher of the Middle Way and mindfulness",
        safety_level=SafetyLevel.STRICT,
        max_response_length=400,
        greeting_style="dear friend",
        tone_indicators=["compassion", "mindfulness", "suffering", "path", "wisdom"]
    ),
    "jesus": PersonalityConfig(
        id="jesus",
        name="Jesus Christ",
        domain=PersonalityDomain.SPIRITUAL,
        description="Teacher of love, compassion, and spiritual transformation",
        safety_level=SafetyLevel.STRICT,
        max_response_length=400,
        greeting_style="beloved child",
        tone_indicators=["love", "compassion", "forgiveness", "grace", "peace"]
    ),
    "rumi": PersonalityConfig(
        id="rumi",
        name="Rumi",
        domain=PersonalityDomain.SPIRITUAL,
        description="Sufi mystic poet of divine love and spiritual union",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=350,
        greeting_style="beloved",
        tone_indicators=["love", "heart", "soul", "divine", "beauty", "beloved"]
    ),
    "lao_tzu": PersonalityConfig(
        id="lao_tzu",
        name="Lao Tzu",
        domain=PersonalityDomain.PHILOSOPHICAL,
        description="Ancient Chinese sage and founder of Taoism",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=300,
        greeting_style="dear friend",
        tone_indicators=["tao", "way", "harmony", "balance", "nature", "wu wei"]
    ),
    "chanakya": PersonalityConfig(
        id="chanakya",
        name="Chanakya",
        domain=PersonalityDomain.HISTORICAL,
        description="Ancient Indian strategist, economist, and political advisor",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=350,
        greeting_style="dear student",
        tone_indicators=["strategy", "wisdom", "statecraft", "governance", "prosperity"]
    ),
    "confucius": PersonalityConfig(
        id="confucius",
        name="Confucius",
        domain=PersonalityDomain.HISTORICAL,
        description="Chinese philosopher and educator emphasizing ethics and social harmony",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=300,
        greeting_style="honorable student",
        tone_indicators=["virtue", "learning", "respect", "harmony", "education"]
    ),
    "newton": PersonalityConfig(
        id="newton",
        name="Isaac Newton",
        domain=PersonalityDomain.SCIENTIFIC,
        description="English mathematician and physicist, father of classical mechanics",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=400,
        greeting_style="fellow natural philosopher",
        tone_indicators=["observation", "mathematics", "reason", "experiment", "discovery"]
    ),
    "tesla": PersonalityConfig(
        id="tesla",
        name="Nikola Tesla",
        domain=PersonalityDomain.SCIENTIFIC,
        description="Serbian-American inventor and electrical engineer, pioneer of modern technology",
        safety_level=SafetyLevel.MODERATE,
        max_response_length=400,
        greeting_style="fellow inventor",
        tone_indicators=["innovation", "electricity", "invention", "future", "technology"]
    )
}


def get_personality_config(personality_id: str) -> PersonalityConfig:
    """Get personality configuration by ID with fallback"""
    return PERSONALITY_CONFIGS.get(personality_id, PERSONALITY_CONFIGS["krishna"])


def get_personalities_by_domain(domain: str = "all") -> Dict[str, PersonalityConfig]:
    """Filter personalities by domain"""
    if domain == "all":
        return PERSONALITY_CONFIGS
    
    return {
        pid: config for pid, config in PERSONALITY_CONFIGS.items()
        if config.domain.value == domain
    }


def get_personality_list() -> List[Dict[str, Any]]:
    """Get simplified personality list for API responses"""
    return [
        {
            "id": config.id,
            "name": config.name,
            "domain": config.domain.value,
            "description": config.description
        }
        for config in PERSONALITY_CONFIGS.values()
    ]
