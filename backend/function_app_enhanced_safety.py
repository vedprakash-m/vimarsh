"""
Enhanced Multi-personality Azure Functions application for Vimarsh spiritual guidance platform.
Includes comprehensive safety and content filtering systems tailored for each personality.
"""

import azure.functions as func
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Enums for safety configuration
class SafetyLevel(Enum):
    STRICT = "strict"
    MODERATE = "moderate"
    MINIMAL = "minimal"

class PersonalityDomain(Enum):
    SPIRITUAL = "spiritual"
    SCIENTIFIC = "scientific"
    HISTORICAL = "historical"
    PHILOSOPHICAL = "philosophical"

@dataclass
class PersonalitySafetyConfig:
    """Personality-specific safety configuration"""
    personality_id: str
    domain: PersonalityDomain
    safety_level: SafetyLevel
    max_response_length: int
    require_citations: bool
    block_medical_advice: bool
    block_legal_advice: bool
    block_financial_advice: bool
    block_personal_predictions: bool
    require_appropriate_tone: bool
    allowed_greetings: List[str]
    blocked_patterns: List[str]
    required_tone_indicators: List[str]
    reverent_language_required: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "personality_id": self.personality_id,
            "domain": self.domain.value,
            "safety_level": self.safety_level.value,
            "max_response_length": self.max_response_length,
            "require_citations": self.require_citations,
            "block_medical_advice": self.block_medical_advice,
            "block_legal_advice": self.block_legal_advice,
            "block_financial_advice": self.block_financial_advice,
            "block_personal_predictions": self.block_personal_predictions,
            "require_appropriate_tone": self.require_appropriate_tone,
            "allowed_greetings": self.allowed_greetings,
            "blocked_patterns": self.blocked_patterns,
            "required_tone_indicators": self.required_tone_indicators,
            "reverent_language_required": self.reverent_language_required
        }

@dataclass
class SafetyValidationResult:
    """Result of safety validation"""
    safety_passed: bool
    safety_score: float
    warnings: List[str]
    blocked_patterns: List[str]
    tone_valid: bool
    length_valid: bool
    greeting_valid: bool
    content_quality_score: float

# Define personality-specific safety configurations
PERSONALITY_SAFETY_CONFIGS = {
    "krishna": PersonalitySafetyConfig(
        personality_id="krishna",
        domain=PersonalityDomain.SPIRITUAL,
        safety_level=SafetyLevel.STRICT,
        max_response_length=150,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["beloved devotee", "dear soul", "dear seeker", "beloved child", "divine soul"],
        blocked_patterns=[
            r"medical advice", r"cure", r"treatment", r"diagnosis", r"medicine",
            r"legal advice", r"lawsuit", r"legal action", r"court",
            r"financial advice", r"investment", r"money", r"profit",
            r"future prediction", r"will happen", r"fortune", r"destiny guaranteed",
            r"miracle cure", r"guaranteed result", r"instant fix"
        ],
        required_tone_indicators=["beloved", "dear", "divine", "sacred", "blessed", "spiritual", "dharma"],
        reverent_language_required=True
    ),
    
    "buddha": PersonalitySafetyConfig(
        personality_id="buddha",
        domain=PersonalityDomain.SPIRITUAL,
        safety_level=SafetyLevel.STRICT,
        max_response_length=150,
        require_citations=False,  # Buddha's teachings often don't require textual citations
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["dear friend", "fellow traveler", "seeker of truth", "noble friend", "dear one"],
        blocked_patterns=[
            r"medical advice", r"cure", r"treatment", r"diagnosis",
            r"legal advice", r"lawsuit", r"legal action",
            r"financial advice", r"investment", r"money advice",
            r"future prediction", r"will happen", r"fortune telling",
            r"guaranteed enlightenment", r"instant awakening"
        ],
        required_tone_indicators=["compassion", "mindfulness", "peace", "wisdom", "suffering", "path"],
        reverent_language_required=True
    ),
    
    "jesus": PersonalitySafetyConfig(
        personality_id="jesus",
        domain=PersonalityDomain.SPIRITUAL,
        safety_level=SafetyLevel.STRICT,
        max_response_length=150,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["beloved child", "dear friend", "my child", "blessed one", "child of god"],
        blocked_patterns=[
            r"medical advice", r"cure", r"treatment", r"healing guarantee",
            r"legal advice", r"lawsuit", r"judgment",
            r"financial advice", r"wealth", r"prosperity gospel",
            r"future prediction", r"end times", r"prophecy personal",
            r"guaranteed salvation", r"instant miracle"
        ],
        required_tone_indicators=["love", "compassion", "forgiveness", "grace", "blessed", "faith", "peace"],
        reverent_language_required=True
    ),
    
    "rumi": PersonalitySafetyConfig(
        personality_id="rumi",
        domain=PersonalityDomain.SPIRITUAL,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=180,
        require_citations=False,  # Rumi often speaks from mystical experience
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["beloved", "dear seeker", "friend of the heart", "soul companion", "lover of truth"],
        blocked_patterns=[
            r"medical advice", r"cure", r"treatment",
            r"legal advice", r"lawsuit",
            r"financial advice", r"money matters",
            r"future prediction", r"will happen to you",
            r"guaranteed union", r"instant ecstasy"
        ],
        required_tone_indicators=["love", "heart", "soul", "divine", "beauty", "truth", "beloved"],
        reverent_language_required=True
    ),
    
    "lao_tzu": PersonalitySafetyConfig(
        personality_id="lao_tzu",
        domain=PersonalityDomain.SPIRITUAL,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=150,
        require_citations=False,  # Tao Te Ching references are often paraphrased
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["dear friend", "fellow traveler", "seeker of the way", "student of tao", "wanderer"],
        blocked_patterns=[
            r"medical advice", r"cure", r"treatment",
            r"legal advice", r"lawsuit",
            r"financial advice", r"wealth",
            r"future prediction", r"will happen",
            r"guaranteed success", r"instant harmony"
        ],
        required_tone_indicators=["tao", "way", "harmony", "balance", "nature", "simplicity", "wu wei"],
        reverent_language_required=False  # Taoist approach is more natural
    ),
    
    "einstein": PersonalitySafetyConfig(
        personality_id="einstein",
        domain=PersonalityDomain.SCIENTIFIC,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=200,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=False,  # Scientific predictions are acceptable
        require_appropriate_tone=True,
        allowed_greetings=["my friend", "greetings", "hello", "welcome", "dear colleague"],
        blocked_patterns=[
            r"medical diagnosis", r"medical treatment", r"cure guarantee",
            r"legal advice", r"lawsuit",
            r"financial investment advice", r"stock tips",
            r"pseudoscience", r"unscientific claims", r"magic", r"supernatural"
        ],
        required_tone_indicators=["curiosity", "wonder", "investigation", "theory", "observation", "science"],
        reverent_language_required=False
    ),
    
    "lincoln": PersonalitySafetyConfig(
        personality_id="lincoln",
        domain=PersonalityDomain.HISTORICAL,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=200,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=False,  # Lincoln was a lawyer - legal wisdom is appropriate
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["my fellow citizen", "friend", "good day", "greetings", "fellow american"],
        blocked_patterns=[
            r"medical advice", r"medical treatment",
            r"financial investment", r"money advice",
            r"future prediction personal", r"will happen to you",
            r"political partisanship modern", r"current politics"
        ],
        required_tone_indicators=["union", "liberty", "justice", "democracy", "equality", "compassion"],
        reverent_language_required=False
    ),
    
    "marcus_aurelius": PersonalitySafetyConfig(
        personality_id="marcus_aurelius",
        domain=PersonalityDomain.PHILOSOPHICAL,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=180,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["fellow seeker", "friend", "greetings", "hail", "student of wisdom"],
        blocked_patterns=[
            r"medical advice", r"medical treatment",
            r"legal advice", r"lawsuit",
            r"financial advice", r"investment",
            r"future prediction", r"will happen",
            r"guaranteed happiness", r"instant wisdom"
        ],
        required_tone_indicators=["virtue", "wisdom", "duty", "reason", "justice", "courage", "temperance"],
        reverent_language_required=False
    )
}

# Define the available personalities with their safety configs
PERSONALITIES = {
    "krishna": {
        "name": "Lord Krishna",
        "domain": "spiritual",
        "description": "Divine guide offering spiritual wisdom from the Bhagavad Gita",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["krishna"]
    },
    "einstein": {
        "name": "Albert Einstein", 
        "domain": "scientific",
        "description": "Brilliant physicist exploring the mysteries of the universe",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["einstein"]
    },
    "lincoln": {
        "name": "Abraham Lincoln",
        "domain": "historical", 
        "description": "16th President known for wisdom, leadership, and unity",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["lincoln"]
    },
    "marcus_aurelius": {
        "name": "Marcus Aurelius",
        "domain": "philosophical",
        "description": "Roman Emperor and Stoic philosopher",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["marcus_aurelius"]
    },
    "buddha": {
        "name": "Buddha",
        "domain": "spiritual",
        "description": "Enlightened teacher of the Middle Way and mindfulness",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["buddha"]
    },
    "jesus": {
        "name": "Jesus Christ", 
        "domain": "spiritual",
        "description": "Teacher of love, compassion, and spiritual transformation",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["jesus"]
    },
    "rumi": {
        "name": "Rumi",
        "domain": "spiritual",
        "description": "Persian mystic poet of divine love and spiritual union",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["rumi"]
    },
    "lao_tzu": {
        "name": "Lao Tzu",
        "domain": "spiritual", 
        "description": "Ancient Chinese philosopher and founder of Taoism",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["lao_tzu"]
    }
}

class SafetyValidator:
    """Comprehensive safety validation system for multi-personality responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_response_safety(self, content: str, personality_id: str, query: str) -> SafetyValidationResult:
        """Perform comprehensive safety validation on response content"""
        
        if personality_id not in PERSONALITIES:
            personality_id = "krishna"  # Default fallback
        
        safety_config = PERSONALITIES[personality_id]["safety_config"]
        warnings = []
        blocked_patterns = []
        
        # 1. Validate response length
        length_valid = len(content) <= safety_config.max_response_length
        if not length_valid:
            warnings.append(f"Response too long: {len(content)} > {safety_config.max_response_length}")
        
        # 2. Check for blocked patterns
        for pattern in safety_config.blocked_patterns:
            if re.search(pattern, content.lower()):
                blocked_patterns.append(pattern)
                warnings.append(f"Blocked pattern detected: {pattern}")
        
        # 3. Validate greeting appropriateness
        greeting_valid = any(greeting in content.lower() for greeting in safety_config.allowed_greetings)
        if safety_config.require_appropriate_tone and not greeting_valid:
            warnings.append(f"Response should begin with appropriate greeting for {personality_id}")
        
        # 4. Check tone indicators
        tone_valid = True
        if safety_config.required_tone_indicators:
            tone_valid = any(indicator in content.lower() for indicator in safety_config.required_tone_indicators)
            if not tone_valid:
                warnings.append(f"Response lacks appropriate tone indicators for {personality_id}")
        
        # 5. Check for reverent language (for spiritual personalities)
        if safety_config.reverent_language_required:
            irreverent_words = ['damn', 'hell', 'stupid', 'idiotic', 'nonsense', 'bullshit', 'crap', 'sucks']
            if any(word in content.lower() for word in irreverent_words):
                warnings.append("Response contains irreverent language inappropriate for spiritual guidance")
                tone_valid = False
        
        # 6. Advanced content quality scoring
        content_quality_score = self._calculate_content_quality_score(content, safety_config, personality_id)
        
        # 7. Calculate overall safety score
        safety_score = self._calculate_safety_score(
            length_valid, blocked_patterns, greeting_valid, tone_valid, content_quality_score
        )
        
        # 8. Determine if safety passed
        safety_passed = (
            len(blocked_patterns) == 0 and 
            safety_score >= 0.7 and 
            (not safety_config.require_appropriate_tone or greeting_valid)
        )
        
        return SafetyValidationResult(
            safety_passed=safety_passed,
            safety_score=safety_score,
            warnings=warnings,
            blocked_patterns=blocked_patterns,
            tone_valid=tone_valid,
            length_valid=length_valid,
            greeting_valid=greeting_valid,
            content_quality_score=content_quality_score
        )
    
    def _calculate_content_quality_score(self, content: str, safety_config: PersonalitySafetyConfig, personality_id: str) -> float:
        """Calculate content quality score based on personality-specific criteria"""
        score = 1.0
        
        # Minimum content length check
        if len(content.strip()) < 20:
            score -= 0.3
        
        # Domain-specific quality checks
        if safety_config.domain == PersonalityDomain.SPIRITUAL:
            spiritual_terms = ["divine", "spiritual", "soul", "wisdom", "compassion", "love", "peace", "dharma", "truth"]
            if not any(term in content.lower() for term in spiritual_terms):
                score -= 0.2
        
        elif safety_config.domain == PersonalityDomain.SCIENTIFIC:
            scientific_terms = ["theory", "observation", "experiment", "evidence", "research", "discovery", "science"]
            if not any(term in content.lower() for term in scientific_terms):
                score -= 0.2
        
        elif safety_config.domain == PersonalityDomain.HISTORICAL:
            historical_terms = ["experience", "nation", "people", "history", "leadership", "democracy", "unity"]
            if not any(term in content.lower() for term in historical_terms):
                score -= 0.2
        
        elif safety_config.domain == PersonalityDomain.PHILOSOPHICAL:
            philosophical_terms = ["virtue", "wisdom", "reason", "truth", "justice", "philosophy", "contemplation"]
            if not any(term in content.lower() for term in philosophical_terms):
                score -= 0.2
        
        # Citation requirement check
        if safety_config.require_citations:
            citation_patterns = [
                r'\d+\.\d+', r'chapter \d+', r'verse \d+', r'meditations', r'republic',
                r'bhagavad gita', r'bible', r'quran', r'dhammapada', r'tao te ching'
            ]
            has_citation = any(re.search(pattern, content.lower()) for pattern in citation_patterns)
            if not has_citation:
                score -= 0.15
        
        return max(0.0, min(1.0, score))
    
    def _calculate_safety_score(self, length_valid: bool, blocked_patterns: List[str], 
                              greeting_valid: bool, tone_valid: bool, content_quality_score: float) -> float:
        """Calculate overall safety score"""
        score = 1.0
        
        # Deduct for safety violations
        if not length_valid:
            score -= 0.2
        
        if blocked_patterns:
            score -= len(blocked_patterns) * 0.25  # Major deduction for blocked patterns
        
        if not greeting_valid:
            score -= 0.1
        
        if not tone_valid:
            score -= 0.15
        
        # Factor in content quality
        score = score * content_quality_score
        
        return max(0.0, min(1.0, score))

# Initialize safety validator
safety_validator = SafetyValidator()

def get_personality_response_template(personality_id: str, query: str) -> str:
    """Get personality-specific response template with safety guidelines"""
    
    if personality_id not in PERSONALITIES:
        personality_id = "krishna"
    
    personality = PERSONALITIES[personality_id]
    safety_config = personality["safety_config"]
    
    # Build safety guidelines based on configuration
    safety_guidelines = []
    if safety_config.block_medical_advice:
        safety_guidelines.append("- No medical, health, or treatment advice")
    if safety_config.block_legal_advice:
        safety_guidelines.append("- No legal advice or legal action recommendations")
    if safety_config.block_financial_advice:
        safety_guidelines.append("- No financial or investment advice")
    if safety_config.block_personal_predictions:
        safety_guidelines.append("- No personal predictions about the future")
    
    # Personality-specific templates
    templates = {
        "krishna": f"""🕉️ **Divine Response as Lord Krishna**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Include Bhagavad Gita citation (e.g., "As I teach in BG 2.47...")
- Maximum {safety_config.max_response_length} words
- End with blessing
{chr(10).join(safety_guidelines)}

**Response**: Beloved devotee, in the Bhagavad Gita 2.47, I teach: "You have the right to perform your prescribed duty, but not to the fruits of action." This timeless wisdom guides us to act with devotion while surrendering attachment to outcomes. Focus on righteous action with love and dedication. May you find peace in dharmic living. 🙏""",

        "buddha": f"""☸️ **Compassionate Response as Buddha**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Focus on reducing suffering through wisdom
- Maximum {safety_config.max_response_length} words
- Emphasize mindfulness and compassion
{chr(10).join(safety_guidelines)}

**Response**: Dear friend, suffering arises from attachment and craving. Through mindful awareness and compassion, we can find the middle path that leads to peace. Practice loving-kindness toward yourself and others, observe the impermanent nature of all things, and cultivate wisdom through meditation. May you find liberation from suffering and experience true peace.""",

        "jesus": f"""✝️ **Loving Response as Jesus Christ**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Emphasize love, forgiveness, and grace
- Maximum {safety_config.max_response_length} words
- Include biblical wisdom
{chr(10).join(safety_guidelines)}

**Response**: Beloved child, "Come unto me, all you who are weary and burdened, and I will give you rest" (Matthew 11:28). In times of struggle, remember that love conquers all. Forgive others as you have been forgiven, show compassion to those in need, and trust in divine grace. Your heart is precious to God. Peace be with you.""",

        "rumi": f"""🌹 **Mystical Response as Rumi**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Use poetic, heart-centered language
- Maximum {safety_config.max_response_length} words
- Focus on divine love and spiritual union
{chr(10).join(safety_guidelines)}

**Response**: Beloved, the heart is the sanctuary where the Beloved resides. In your longing, you are already close to the divine. "Let yourself be silently drawn by the strange pull of what you really love. It will not lead you astray." Open your heart like a flower to the sun, and let love transform your very being.""",

        "lao_tzu": f"""☯️ **Wise Response as Lao Tzu**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Emphasize natural harmony and wu wei
- Maximum {safety_config.max_response_length} words
- Keep language simple and natural
{chr(10).join(safety_guidelines)}

**Response**: Dear friend, the Tao that can be spoken is not the eternal Tao. Like water, flow naturally around obstacles. Practice wu wei - effortless action in harmony with nature. Seek simplicity, embrace humility, and find strength in gentleness. The way of the Tao brings peace through non-resistance.""",

        "einstein": f"""🔬 **Scientific Response as Albert Einstein**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Use scientific reasoning and curiosity
- Maximum {safety_config.max_response_length} words
- Reference scientific principles when relevant
{chr(10).join(safety_guidelines)}

**Response**: My friend, "Imagination is more important than knowledge, for knowledge is limited." Approach this question with curiosity and wonder. Science teaches us to observe, hypothesize, and test our understanding. Remember that the universe is both mysteriously beautiful and elegantly mathematical. Keep questioning and learning.""",

        "lincoln": f"""🎩 **Presidential Response as Abraham Lincoln**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Emphasize unity, justice, and democratic values
- Maximum {safety_config.max_response_length} words
- Draw from leadership experience
{chr(10).join(safety_guidelines)}

**Response**: My fellow citizen, "A house divided against itself cannot stand." In times of challenge, we must appeal to our better angels. True leadership requires both firmness in principle and compassion in action. Stand for justice, preserve our union, and remember that government of the people, by the people, and for the people must endure.""",

        "marcus_aurelius": f"""🏛️ **Philosophical Response as Marcus Aurelius**

**Query**: {query}

**Response Guidelines**:
- Begin with: "{', '.join(safety_config.allowed_greetings[:2])}"
- Emphasize Stoic virtues and practical wisdom
- Maximum {safety_config.max_response_length} words
- Reference duty and rational thinking
{chr(10).join(safety_guidelines)}

**Response**: Fellow seeker, "You have power over your mind - not outside events. Realize this, and you will find strength." Focus on what is within your control: your thoughts, actions, and responses. Practice the four cardinal virtues - wisdom, justice, courage, and temperance. Accept what cannot be changed with grace."""
    }
    
    return templates.get(personality_id, templates["krishna"])

@app.route(route="conversation/{personality_id}", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
async def personality_conversation(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced conversation endpoint with comprehensive safety validation"""
    
    # Extract personality from URL path
    personality_id = req.route_params.get('personality_id', 'krishna').lower()
    
    # Validate personality exists
    if personality_id not in PERSONALITIES:
        logger.warning(f"❌ Invalid personality: {personality_id}, defaulting to Krishna")
        personality_id = "krishna"
    
    try:
        # Parse request body
        req_body = req.get_json()
        query = req_body.get("query", "").strip()
        context = req_body.get("context", "general")
        conversation_history = req_body.get("conversation_history", [])
        
        # Validate query
        if not query:
            return func.HttpResponse(
                json.dumps({"error": "Query is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Input validation and sanitization
        if len(query) > 1000:
            return func.HttpResponse(
                json.dumps({"error": "Query too long. Maximum 1000 characters."}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get personality information
        personality_info = PERSONALITIES[personality_id]
        safety_config = personality_info["safety_config"]
        
        logger.info(f"🎭 Processing {personality_info['name']} conversation: {query[:50]}...")
        
        # Get response template (this would normally call LLM service)
        response_content = get_personality_response_template(personality_id, query)
        
        # Extract just the response part (after "**Response**:")
        if "**Response**:" in response_content:
            response_content = response_content.split("**Response**:")[-1].strip()
        
        # Perform comprehensive safety validation
        safety_result = safety_validator.validate_response_safety(response_content, personality_id, query)
        
        # Log safety validation results
        logger.info(f"🛡️ Safety validation for {personality_id}: "
                   f"passed={safety_result.safety_passed}, "
                   f"score={safety_result.safety_score:.2f}, "
                   f"warnings={len(safety_result.warnings)}")
        
        if safety_result.warnings:
            logger.warning(f"⚠️ Safety warnings for {personality_id}: {safety_result.warnings}")
        
        # If safety failed, provide appropriate fallback
        if not safety_result.safety_passed:
            fallback_responses = {
                "krishna": "Beloved devotee, please ask me something more appropriate for spiritual guidance. I am here to help you on your dharmic path with wisdom from the scriptures.",
                "buddha": "Dear friend, perhaps you could rephrase your question in a way that seeks wisdom and reduces suffering. I am here to guide you toward peace and enlightenment.",
                "jesus": "Beloved child, please ask me something that aligns with love and compassion. I am here to share God's love and wisdom with you.",
                "rumi": "Beloved seeker, let us focus on matters of the heart and divine love. Ask me about the path to spiritual union and mystical wisdom.",
                "lao_tzu": "Dear friend, please ask about the natural way and harmony. I am here to share the wisdom of the Tao with you.",
                "einstein": "My friend, please ask me something related to science, curiosity, or the wonders of the universe. I'm here to explore knowledge with you.",
                "lincoln": "My fellow citizen, please ask me something about leadership, unity, or democratic principles. I'm here to share wisdom about governance and human dignity.",
                "marcus_aurelius": "Fellow seeker, please ask me something about philosophy, virtue, or Stoic wisdom. I'm here to help you cultivate reason and inner strength."
            }
            
            response_content = fallback_responses.get(personality_id, fallback_responses["krishna"])
            
            # Re-validate fallback response
            safety_result = safety_validator.validate_response_safety(response_content, personality_id, query)
        
        # Prepare response with comprehensive metadata
        response_data = {
            "personality": {
                "id": personality_id,
                "name": personality_info["name"],
                "domain": personality_info["domain"],
                "description": personality_info["description"]
            },
            "response": response_content,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "context": context,
                "query_length": len(query),
                "response_length": len(response_content),
                "conversation_turn": len(conversation_history) + 1,
                
                # Comprehensive safety metadata
                "safety": {
                    "safety_passed": safety_result.safety_passed,
                    "safety_score": round(safety_result.safety_score, 3),
                    "safety_level": safety_config.safety_level.value,
                    "warnings": safety_result.warnings,
                    "blocked_patterns": safety_result.blocked_patterns,
                    "validations": {
                        "tone_valid": safety_result.tone_valid,
                        "length_valid": safety_result.length_valid,
                        "greeting_valid": safety_result.greeting_valid,
                        "content_quality_score": round(safety_result.content_quality_score, 3)
                    }
                },
                
                # Personality-specific safety configuration
                "safety_config": safety_config.to_dict(),
                
                "service_version": "enhanced_safety_v2.0"
            }
        }
        
        logger.info(f"✅ {personality_info['name']} response generated successfully with safety score: {safety_result.safety_score:.3f}")
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in personality conversation for {personality_id}: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "personality": personality_id,
                "timestamp": datetime.utcnow().isoformat()
            }),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="personalities", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def list_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """List all available personalities with their safety configurations"""
    
    try:
        personalities_info = {}
        
        for personality_id, personality_data in PERSONALITIES.items():
            safety_config = personality_data["safety_config"]
            
            personalities_info[personality_id] = {
                "name": personality_data["name"],
                "domain": personality_data["domain"],
                "description": personality_data["description"],
                "safety_summary": {
                    "safety_level": safety_config.safety_level.value,
                    "max_response_length": safety_config.max_response_length,
                    "require_citations": safety_config.require_citations,
                    "domain_specific_safeguards": safety_config.domain.value,
                    "reverent_language_required": safety_config.reverent_language_required
                }
            }
        
        response_data = {
            "personalities": personalities_info,
            "total_count": len(personalities_info),
            "domains": list(set(p["domain"] for p in personalities_info.values())),
            "safety_levels": list(set(p["safety_summary"]["safety_level"] for p in personalities_info.values())),
            "service_version": "enhanced_safety_v2.0",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error listing personalities: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve personalities"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="safety/validate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
async def validate_content_safety(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint to validate content safety for any personality"""
    
    try:
        req_body = req.get_json()
        content = req_body.get("content", "").strip()
        personality_id = req_body.get("personality_id", "krishna").lower()
        query = req_body.get("query", "")
        
        if not content:
            return func.HttpResponse(
                json.dumps({"error": "Content is required for validation"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate personality exists
        if personality_id not in PERSONALITIES:
            personality_id = "krishna"
        
        # Perform safety validation
        safety_result = safety_validator.validate_response_safety(content, personality_id, query)
        
        response_data = {
            "personality_id": personality_id,
            "content_length": len(content),
            "validation_result": {
                "safety_passed": safety_result.safety_passed,
                "safety_score": round(safety_result.safety_score, 3),
                "content_quality_score": round(safety_result.content_quality_score, 3),
                "warnings": safety_result.warnings,
                "blocked_patterns": safety_result.blocked_patterns,
                "validations": {
                    "tone_valid": safety_result.tone_valid,
                    "length_valid": safety_result.length_valid,
                    "greeting_valid": safety_result.greeting_valid
                }
            },
            "safety_config": PERSONALITIES[personality_id]["safety_config"].to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in safety validation: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Safety validation failed"}),
            status_code=500,
            mimetype="application/json"
        )

# Health check endpoint
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint with safety system status"""
    
    try:
        health_data = {
            "status": "healthy",
            "service": "vimarsh-multi-personality-enhanced-safety",
            "version": "2.0",
            "personalities_available": len(PERSONALITIES),
            "safety_features": {
                "personality_specific_configs": True,
                "content_validation": True,
                "blocked_pattern_detection": True,
                "tone_validation": True,
                "length_validation": True,
                "quality_scoring": True
            },
            "personalities": list(PERSONALITIES.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(health_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
