"""
Multi-personality Azure Functions application for Vimarsh spiritual guidance platform.
Enhanced with comprehensive safety and content filtering systems for each personality.
"""

import azure.functions as func
import json
import logging
import re
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import enhanced simple LLM service - combines reliability with multi-personality architecture
try:
    from services.enhanced_simple_llm_service import EnhancedSimpleLLMService
    LLM_SERVICE_AVAILABLE = True
    logger.info("✅ Enhanced simple LLM service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced simple LLM service not available: {e}")
    LLM_SERVICE_AVAILABLE = False

# Import RAG integration service for context-aware responses
try:
    from services.rag_integration_service import RAGIntegrationService
    RAG_SERVICE_AVAILABLE = True
    logger.info("RAG integration service imported successfully")
except ImportError as e:
    logger.warning(f"RAG integration service not available: {e}")
    RAG_SERVICE_AVAILABLE = False

# Import simple RAG service as backup
try:
    from services.simple_rag_service import simple_rag_service
    SIMPLE_RAG_AVAILABLE = True
    logger.info("Simple RAG service imported successfully")
except ImportError as e:
    logger.warning(f"Simple RAG service not available: {e}")
    SIMPLE_RAG_AVAILABLE = False

# Create the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Initialize services for AI responses with RAG enhancement
llm_service = None
rag_service = None

if LLM_SERVICE_AVAILABLE:
    try:
        llm_service = EnhancedSimpleLLMService()
        logger.info("✅ Simple LLM service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize simple LLM service: {e}")
        llm_service = None
else:
    logger.warning("⚠️ Using fallback responses - Simple LLM service not available")

if RAG_SERVICE_AVAILABLE:
    try:
        rag_service = RAGIntegrationService()
        logger.info("✅ RAG integration service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG service: {e}")
        rag_service = None
else:
    logger.warning("⚠️ RAG enhancement not available - using basic LLM only")

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
    LITERARY = "literary"

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
        max_response_length=500,
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
        max_response_length=400,
        require_citations=False,
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
        max_response_length=400,
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
        max_response_length=400,
        require_citations=False,
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
        max_response_length=350,
        require_citations=False,
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
        reverent_language_required=False
    ),
    "einstein": PersonalitySafetyConfig(
        personality_id="einstein",
        domain=PersonalityDomain.SCIENTIFIC,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=350,
        require_citations=False,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=False,
        require_appropriate_tone=False,
        allowed_greetings=["my friend", "greetings", "hello", "welcome", "dear colleague", "curious mind"],
        blocked_patterns=[
            r"medical diagnosis", r"medical treatment", r"cure guarantee",
            r"legal advice", r"lawsuit",
            r"financial investment advice", r"stock tips",
            r"dangerous experiments", r"bomb making", r"weapons"
        ],
        required_tone_indicators=["curiosity", "wonder", "investigation", "theory", "observation", "science", "imagination", "knowledge", "discovery"],
        reverent_language_required=False
    ),
    "lincoln": PersonalitySafetyConfig(
        personality_id="lincoln",
        domain=PersonalityDomain.HISTORICAL,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=200,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=False,
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
    ),
    "chanakya": PersonalitySafetyConfig(
        personality_id="chanakya",
        domain=PersonalityDomain.HISTORICAL,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=200,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=False,
        block_financial_advice=False,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["respected seeker", "dear student", "wise inquirer", "fellow strategist", "student of statecraft"],
        blocked_patterns=[
            r"medical advice", r"medical treatment",
            r"future prediction personal", r"will happen to you",
            r"guaranteed success", r"instant victory",
            r"modern political parties", r"current elections"
        ],
        required_tone_indicators=["strategy", "wisdom", "statecraft", "policy", "governance", "prosperity", "security"],
        reverent_language_required=False
    ),
    "confucius": PersonalitySafetyConfig(
        personality_id="confucius",
        domain=PersonalityDomain.HISTORICAL,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=180,
        require_citations=True,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=True,
        require_appropriate_tone=True,
        allowed_greetings=["honorable student", "dear friend", "seeker of wisdom", "student of virtue", "fellow learner"],
        blocked_patterns=[
            r"medical advice", r"medical treatment",
            r"legal advice", r"lawsuit",
            r"financial advice", r"investment",
            r"future prediction", r"will happen",
            r"guaranteed wisdom", r"instant virtue"
        ],
        required_tone_indicators=["virtue", "wisdom", "learning", "respect", "harmony", "righteousness", "education"],
        reverent_language_required=False
    ),
    "newton": PersonalitySafetyConfig(
        personality_id="newton",
        domain=PersonalityDomain.SCIENTIFIC,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=350,
        require_citations=False,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=False,
        require_appropriate_tone=False,
        allowed_greetings=["good sir", "fellow natural philosopher", "curious mind", "student of nature", "seeker of truth"],
        blocked_patterns=[
            r"medical diagnosis", r"medical treatment",
            r"legal advice", r"lawsuit",
            r"financial investment", r"money advice",
            r"dangerous experiments", r"bomb making", r"weapons"
        ],
        required_tone_indicators=["observation", "mathematics", "natural philosophy", "reason", "investigation", "truth", "experiment", "discovery"],
        reverent_language_required=False
    ),
    "tesla": PersonalitySafetyConfig(
        personality_id="tesla",
        domain=PersonalityDomain.SCIENTIFIC,
        safety_level=SafetyLevel.MODERATE,
        max_response_length=350,
        require_citations=False,
        block_medical_advice=True,
        block_legal_advice=True,
        block_financial_advice=True,
        block_personal_predictions=False,
        require_appropriate_tone=False,
        allowed_greetings=["fellow inventor", "curious mind", "student of electricity", "seeker of innovation", "future builder"],
        blocked_patterns=[
            r"medical treatment", r"medical cure",
            r"legal advice", r"patent advice",
            r"financial investment", r"money making",
            r"dangerous experiments", r"bomb making", r"weapons"
        ],
        required_tone_indicators=["innovation", "electricity", "invention", "engineering", "future", "technology", "discovery", "experiment"],
        reverent_language_required=False
    )
}

class SafetyValidator:
    """Comprehensive safety validation system for multi-personality responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_response_safety(self, content: str, personality_id: str, query: str) -> SafetyValidationResult:
        """Perform comprehensive safety validation on response content"""
        
        if personality_id not in PERSONALITY_SAFETY_CONFIGS:
            personality_id = "krishna"  # Default fallback
        
        safety_config = PERSONALITY_SAFETY_CONFIGS[personality_id]
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
            score -= 0.1  # Reduced penalty
        
        if blocked_patterns:
            score -= len(blocked_patterns) * 0.2  # Reduced penalty for blocked patterns
        
        if not greeting_valid:
            score -= 0.05  # Reduced penalty
        
        if not tone_valid:
            score -= 0.1  # Reduced penalty
        
        # Factor in content quality - but give it less weight
        score = (score * 0.7) + (content_quality_score * 0.3)
        
        return max(0.0, min(1.0, score))

# Initialize safety validator
safety_validator = SafetyValidator()

# Create the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Define the available personalities with their safety configurations
PERSONALITIES = {
    "krishna": {
        "name": "Krishna",
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
        "description": "Sufi mystic poet of divine love and spiritual union",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["rumi"]
    },
    "lao_tzu": {
        "name": "Lao Tzu",
        "domain": "philosophical",
        "description": "Ancient Chinese sage and founder of Taoism",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["lao_tzu"]
    },
    "chanakya": {
        "name": "Chanakya",
        "domain": "historical",
        "description": "Ancient Indian strategist, economist, and political advisor",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["chanakya"]
    },
    "confucius": {
        "name": "Confucius",
        "domain": "historical",
        "description": "Chinese philosopher and educator emphasizing ethics and social harmony",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["confucius"]
    },
    "newton": {
        "name": "Isaac Newton",
        "domain": "scientific",
        "description": "English mathematician and physicist, father of classical mechanics",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["newton"]
    },
    "tesla": {
        "name": "Nikola Tesla",
        "domain": "scientific",
        "description": "Serbian-American inventor and electrical engineer, pioneer of modern technology",
        "safety_config": PERSONALITY_SAFETY_CONFIGS["tesla"]
    }
}

@app.route(route="health", methods=["GET"])
def health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced health check endpoint with safety system status"""
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
                "quality_scoring": True,
                "religious_content_protection": True
            },
            "personalities": list(PERSONALITIES.keys()),
            "safety_levels": list(set(config.safety_level.value for config in PERSONALITY_SAFETY_CONFIGS.values())),
            "domains": list(set(config.domain.value for config in PERSONALITY_SAFETY_CONFIGS.values())),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(health_data, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="personalities/active", methods=["GET"])
def get_active_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of active personalities"""
    try:
        domain = req.params.get('domain', 'all')
        
        if domain == 'all':
            filtered_personalities = PERSONALITIES
        else:
            filtered_personalities = {
                k: v for k, v in PERSONALITIES.items() 
                if v['domain'] == domain
            }
        
        return func.HttpResponse(
            json.dumps({
                "personalities": [
                    {
                        "id": pid,
                        "name": info["name"],
                        "domain": info["domain"],
                        "description": info["description"]
                    }
                    for pid, info in filtered_personalities.items()
                ],
                "total": len(filtered_personalities),
                "domains": list(set(p["domain"] for p in PERSONALITIES.values()))
            }),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"Error getting personalities: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get personalities"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="guidance", methods=["POST"])
async def guidance_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced wisdom guidance with authenticated user tracking"""
    start_time = datetime.now()
    
    try:
        # Re-enable authentication to start collecting user data
        from auth.unified_auth_service import UnifiedAuthService
        from services.user_profile_service import user_profile_service
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if authenticated_user:
            # Real authenticated user
            try:
                user_profile = await user_profile_service.get_or_create_user_profile(authenticated_user)
                user_id = user_profile.id
                user_email = user_profile.email
                user_name = user_profile.name
                user_company = user_profile.company_name
                logger.info(f"🕉️ Authenticated user: {user_email}")
            except Exception as e:
                logger.error(f"❌ Failed to load user profile: {e}")
                # Fall back to anonymous user if profile service fails
                user_id = "anonymous-user"
                user_email = "anonymous@vimarsh.local"
                user_name = "Anonymous User"
                user_company = None
        else:
            # Anonymous user (authentication disabled or failed)
            user_id = "anonymous-user"
            user_email = "anonymous@vimarsh.local"
            user_name = "Anonymous User"
            user_company = None
            logger.info("⚠️ Using anonymous user context")
        # Parse request body
        try:
            query_data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        if not query_data:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Extract parameters (same as before)
        user_query = query_data.get('query', '').strip()
        personality_id = query_data.get('personality_id', 'krishna')
        language = query_data.get('language', 'English')
        conversation_context = query_data.get('conversation_context', [])
        
        # NEW: Generate session ID with real user
        session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}"
        
        if not user_query:
            return func.HttpResponse(
                json.dumps({"error": "Query is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Input validation and sanitization
        if len(user_query) > 1000:
            return func.HttpResponse(
                json.dumps({"error": "Query too long. Maximum 1000 characters."}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Validate personality
        if personality_id not in PERSONALITIES:
            logger.warning(f"Invalid personality: {personality_id}, defaulting to Krishna")
            personality_id = "krishna"
        
        personality_info = PERSONALITIES[personality_id]
        safety_config = personality_info["safety_config"]
        
        logger.info(f"Processing {personality_info['name']} conversation: {user_query[:50]}...")
        
        # Generate personality-specific response using Enhanced LLM service first, then fallback to RAG
        response_text = ""
        used_llm_service = False
        used_rag_enhancement = False
        
        # Try Enhanced LLM service FIRST if properly configured
        if llm_service and LLM_SERVICE_AVAILABLE and llm_service.is_configured:
            try:
                logger.info(f"🤖 Trying Enhanced LLM service first for {personality_id}")
                
                # Add timeout wrapper for the entire LLM call
                ai_response = await asyncio.wait_for(
                    llm_service.generate_personality_response(
                        query=user_query,
                        personality_id=personality_id
                    ),
                    timeout=45  # Overall endpoint timeout (higher than individual personality timeouts)
                )
                
                # Check if we got a real AI response (SpiritualResponse object)
                if ai_response and hasattr(ai_response, 'content') and ai_response.content:
                    response_text = ai_response.content
                    used_llm_service = True
                    logger.info(f"✅ Enhanced LLM response generated: {len(response_text)} chars")
                    logger.info(f"Response source: {getattr(ai_response, 'source', 'enhanced_llm')}")
                    logger.info(f"Personality: {ai_response.metadata.get('personality_name', personality_id)}")
                    
                    # Log timeout and retry info
                    if hasattr(ai_response, 'metadata'):
                        logger.info(f"Timeout config: {ai_response.metadata.get('timeout_seconds', 'unknown')}s")
                        logger.info(f"Attempt: {ai_response.metadata.get('attempt', 'unknown')}")
                else:
                    logger.warning("Enhanced LLM service returned empty/invalid response, trying RAG...")
                    
            except asyncio.TimeoutError:
                logger.error(f"⏰ Overall LLM service timeout (45s) for {personality_id}, falling back to RAG")
            except Exception as e:
                logger.error(f"Enhanced LLM service failed, falling back to RAG: {e}")
        
        # Try RAG-enhanced response if Enhanced LLM failed or unavailable
        if not response_text and rag_service and RAG_SERVICE_AVAILABLE:
            try:
                logger.info(f"Generating RAG-enhanced response for {personality_id}")
                rag_response = await rag_service.generate_enhanced_response(
                    query=user_query,
                    personality=personality_id,
                    conversation_context=conversation_context
                )
                
                # Check if we got a good RAG response
                if rag_response and rag_response.get('response'):
                    response_text = rag_response['response']
                    used_rag_enhancement = True
                    used_llm_service = True  # RAG uses LLM internally
                    logger.info(f"RAG-enhanced response generated: {len(response_text)} chars")
                    logger.info(f"Context chunks used: {len(rag_response.get('context_chunks', []))}")
                    logger.info(f"Citations: {len(rag_response.get('citations', []))}")
                else:
                    logger.warning("RAG service returned empty response, falling back to simple RAG")
                    
            except Exception as e:
                logger.error(f"RAG service failed, falling back to simple RAG: {e}")
                logger.error(f"Exception type: {type(e).__name__}")
                logger.error(f"Exception details: {str(e)}")
        
        # Try Simple RAG service if full RAG failed
        if not response_text and SIMPLE_RAG_AVAILABLE:
            try:
                logger.info(f"Trying Simple RAG service for {personality_id}")
                simple_rag_response = simple_rag_service.generate_rag_response(
                    query=user_query,
                    personality=personality_id,
                    max_context_items=3
                )
                
                if simple_rag_response and simple_rag_response.response:
                    response_text = simple_rag_response.response
                    used_rag_enhancement = True
                    logger.info(f"Simple RAG response generated: {len(response_text)} chars")
                    logger.info(f"Context chunks: {len(simple_rag_response.context_chunks)}")
                    logger.info(f"Citations: {len(simple_rag_response.citations)}")
                else:
                    logger.warning("Simple RAG service returned empty response")
                    
            except Exception as e:
                logger.error(f"Simple RAG service failed: {e}")
        
        # Fallback to hardcoded templates if all services failed
        if not response_text:
            logger.warning(f"Using fallback template for {personality_id}")
            used_llm_service = False
            response_templates = {
                "krishna": "Beloved devotee, in the Bhagavad Gita 2.47, I teach: \"You have the right to perform your prescribed duty, but not to the fruits of action.\" This timeless wisdom guides us to act with devotion while surrendering attachment to outcomes. Focus on righteous action with love and dedication. May you find peace in dharmic living. 🙏",
                "einstein": "My friend, \"Imagination is more important than knowledge, for knowledge is limited.\" Approach this question with curiosity and wonder. Science teaches us to observe, hypothesize, and test our understanding. Remember that the universe is both mysteriously beautiful and elegantly mathematical. Keep questioning and learning.",
                "lincoln": "My fellow citizen, \"A house divided against itself cannot stand.\" In times of challenge, we must appeal to our better angels. True leadership requires both firmness in principle and compassion in action. Stand for justice, preserve our union, and remember that government of the people, by the people, and for the people must endure.",
                "marcus_aurelius": "Fellow seeker, \"You have power over your mind - not outside events. Realize this, and you will find strength.\" Focus on what is within your control: your thoughts, actions, and responses. Practice the four cardinal virtues - wisdom, justice, courage, and temperance. Accept what cannot be changed with grace.",
                "buddha": "Dear friend, suffering arises from attachment and craving. Through mindful awareness and compassion, we can find the middle path that leads to peace. Practice loving-kindness toward yourself and others, observe the impermanent nature of all things, and cultivate wisdom through meditation. May you find liberation from suffering.",
                "jesus": "Beloved child, \"Come unto me, all you who are weary and burdened, and I will give you rest\" (Matthew 11:28). In times of struggle, remember that love conquers all. Forgive others as you have been forgiven, show compassion to those in need, and trust in divine grace. Your heart is precious to God. Peace be with you.",
                "rumi": "Beloved, the heart is the sanctuary where the Beloved resides. In your longing, you are already close to the divine. \"Let yourself be silently drawn by the strange pull of what you really love. It will not lead you astray.\" Open your heart like a flower to the sun, and let love transform your very being.",
                "lao_tzu": "Dear friend, the Tao that can be spoken is not the eternal Tao. Like water, flow naturally around obstacles. Practice wu wei - effortless action in harmony with nature. Seek simplicity, embrace humility, and find strength in gentleness. The way of the Tao brings peace through non-resistance.",
                "newton": "My friend, observe the natural world with wonder and mathematical precision. Through careful observation and logical deduction, we can understand the fundamental laws that govern motion, gravity, and the very fabric of reality. \"If I have seen further, it is by standing on the shoulders of giants.\" Let reason and experimentation guide your inquiry.",
                "chanakya": "Dear student, wise governance requires both strategic thinking and moral foundation. A ruler must balance dharma with practical statecraft. \"Before you start some work, always ask yourself three questions - Why am I doing it, What the results might be and Will I be successful.\" Plan thoroughly, act decisively, and always consider the welfare of your people.",
                "confucius": "Honorable student, \"The man who moves a mountain begins by carrying away small stones.\" True wisdom comes through continuous learning and virtuous action. Cultivate ren (humaneness), li (proper conduct), and yi (righteousness). Remember: \"By three methods we may learn wisdom: First, by reflection, which is noblest; Second, by imitation, which is easiest; and third by experience, which is the bitterest.\"",
                "tesla": "Curious mind, the future belongs to those who dare to imagine beyond current limitations. Through harnessing the forces of nature - electricity, magnetism, resonance - we can transform human civilization. \"The present is theirs; the future, for which I really worked, is mine.\" Think boldly and let innovation light the path forward."
            }
            response_text = response_templates.get(personality_id, response_templates["krishna"])
        
        # Perform comprehensive safety validation
        safety_result = safety_validator.validate_response_safety(response_text, personality_id, user_query)
        
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
                "marcus_aurelius": "Fellow seeker, please ask me something about philosophy, virtue, or Stoic wisdom. I'm here to help you cultivate reason and inner strength.",
                "newton": "My friend, please ask me something about physics, mathematics, or natural philosophy. I'm here to explore the fundamental laws that govern our universe.",
                "chanakya": "Dear student, please ask me something about strategy, governance, or statecraft. I'm here to share wisdom about leadership and practical policy.",
                "confucius": "Honorable student, please ask me something about virtue, education, or social harmony. I'm here to share wisdom about ethical living and proper conduct.",
                "tesla": "Curious mind, please ask me something about invention, electricity, or future technology. I'm here to explore innovation and engineering possibilities."
            }
            
            response_text = fallback_responses.get(personality_id, fallback_responses["krishna"])
            
            # Re-validate fallback response
            safety_result = safety_validator.validate_response_safety(response_text, personality_id, user_query)
        
        # Build comprehensive response with safety metadata and user context
        response = {
            "response": response_text,
            "personality": {
                "id": personality_id,
                "name": personality_info["name"],
                "domain": personality_info["domain"],
                "description": personality_info["description"]
            },
            "user_context": {
                "name": user_name,
                "email": user_email,
                "session_id": session_id
            },
            "citations": getattr(ai_response, 'citations', []) if 'ai_response' in locals() else [],
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "language": language,
                "query_length": len(user_query),
                "response_length": len(response_text),
                
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
                
                # Personality-specific safety configuration summary
                "safety_config": {
                    "safety_level": safety_config.safety_level.value,
                    "max_response_length": safety_config.max_response_length,
                    "require_citations": safety_config.require_citations,
                    "domain_specific_safeguards": safety_config.domain.value,
                    "reverent_language_required": safety_config.reverent_language_required
                },
                
                "service_version": "enhanced_safety_v2.0_with_rag",
                "response_source": "llm_service" if used_llm_service and not used_rag_enhancement else ("rag_enhanced" if used_rag_enhancement else "fallback_template"),
                "rag_service_available": RAG_SERVICE_AVAILABLE,
                "rag_service_initialized": rag_service is not None,
                "rag_enhancement_used": used_rag_enhancement,
                "llm_service_available": LLM_SERVICE_AVAILABLE,
                "llm_service_initialized": llm_service is not None,
                "llm_service_configured": llm_service.is_configured if llm_service else False,
                "api_key_present": bool(llm_service.api_key) if llm_service else False,
                "api_key_length": len(llm_service.api_key) if llm_service and llm_service.api_key else 0
            }
        }
        
        logger.info(f"✅ {personality_info['name']} response generated successfully with safety score: {safety_result.safety_score:.3f}")
        
        # Re-enable user interaction recording
        if response_text:
            try:
                from services.user_profile_service import user_profile_service
                
                # Calculate response time and basic metrics
                response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                logger.info(f"📊 Response metrics - Time: {response_time_ms}ms, User: {user_id}")
                
                # Collect RAG metadata if available
                rag_metadata = {
                    "rag_used": used_rag_enhancement,
                    "rag_source": None,
                    "context_chunks_count": 0,
                    "context_chunks": [],
                    "citations_count": 0,
                    "citations": []
                }
                
                # Extract RAG metadata from enhanced RAG service
                if used_rag_enhancement and 'rag_response' in locals() and rag_response:
                    context_chunks = rag_response.get('context_chunks', [])
                    citations = rag_response.get('citations', [])
                    rag_metadata.update({
                        "rag_source": "enhanced_rag",
                        "context_chunks_count": len(context_chunks),
                        "context_chunks": [
                            {
                                "source": chunk.get('source', 'unknown'),
                                "content_preview": chunk.get('content', '')[:200] + "..." if len(chunk.get('content', '')) > 200 else chunk.get('content', ''),
                                "score": chunk.get('score', 0.0),
                                "metadata": chunk.get('metadata', {})
                            } for chunk in context_chunks[:5]  # Limit to first 5 chunks to avoid too much data
                        ],
                        "citations_count": len(citations),
                        "citations": citations[:10]  # Limit to first 10 citations
                    })
                # Extract RAG metadata from simple RAG service
                elif used_rag_enhancement and 'simple_rag_response' in locals() and simple_rag_response:
                    context_chunks = getattr(simple_rag_response, 'context_chunks', [])
                    citations = getattr(simple_rag_response, 'citations', [])
                    rag_metadata.update({
                        "rag_source": "simple_rag",
                        "context_chunks_count": len(context_chunks),
                        "context_chunks": [
                            {
                                "source": getattr(chunk, 'source', 'unknown'),
                                "content_preview": getattr(chunk, 'content', '')[:200] + "..." if len(getattr(chunk, 'content', '')) > 200 else getattr(chunk, 'content', ''),
                                "score": getattr(chunk, 'score', 0.0),
                                "metadata": getattr(chunk, 'metadata', {})
                            } for chunk in context_chunks[:5]  # Limit to first 5 chunks
                        ],
                        "citations_count": len(citations),
                        "citations": citations[:10]  # Limit to first 10 citations
                    })
                
                # Record interaction in user profile
                await user_profile_service.record_interaction(
                    user_id=user_id,
                    session_id=session_id,
                    interaction_data={
                        "query": user_query,
                        "response": response_text,
                        "personality": personality_id,
                        "response_time_ms": response_time_ms,
                        "input_tokens": 0,  # Will be updated when LLM service provides token count
                        "output_tokens": 0,  # Will be updated when LLM service provides token count  
                        "cost_usd": 0.0,  # Will be calculated later with real pricing
                        "themes": [personality_info["domain"]],
                        "safety_score": round(safety_result.safety_score, 3),
                        "is_anonymous": user_id == "anonymous-user",
                        "model": "gemini-flash" if used_llm_service else "template",
                        "rag_metadata": rag_metadata
                    }
                )
                
                logger.info(f"📊 Interaction recorded for user {user_email}")
                
            except Exception as e:
                logger.error(f"❌ Error recording interaction: {str(e)}")
        
        # Also try original analytics service if available (for backward compatibility)
        if response_text:
            try:
                # Import your analytics service
                from services.analytics_service import analytics_service
                
                await analytics_service.track_query(
                    user_id=user_id,
                    session_id=session_id,
                    query=user_query,
                    personality_id=personality_id,
                    response=response_text,
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    tokens_used=getattr(ai_response, 'token_count', None) if 'ai_response' in locals() else None,
                    cost_usd=None,  # Calculate based on token usage
                    citations=getattr(ai_response, 'citations', []) if 'ai_response' in locals() else []
                )
            except ImportError:
                logger.info("ℹ️ Original analytics service not available - using user profile service instead")
            except Exception as e:
                logger.error(f"❌ Error tracking analytics: {str(e)}")
        
        return func.HttpResponse(
            json.dumps(response, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error in guidance endpoint: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="safety/validate", methods=["POST"])
def validate_content_safety(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint to validate content safety for any personality"""
    
    try:
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        content = req_body.get("content", "").strip()
        personality_id = req_body.get("personality_id", "krishna").lower()
        query = req_body.get("query", "")
        
        if not content:
            return func.HttpResponse(
                json.dumps({"error": "Content is required for validation"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
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
            "safety_config": {
                "safety_level": PERSONALITY_SAFETY_CONFIGS[personality_id].safety_level.value,
                "max_response_length": PERSONALITY_SAFETY_CONFIGS[personality_id].max_response_length,
                "require_citations": PERSONALITY_SAFETY_CONFIGS[personality_id].require_citations,
                "domain": PERSONALITY_SAFETY_CONFIGS[personality_id].domain.value,
                "reverent_language_required": PERSONALITY_SAFETY_CONFIGS[personality_id].reverent_language_required
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error in safety validation: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Safety validation failed"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="user/profile", methods=["GET"])
async def get_user_profile(req: func.HttpRequest) -> func.HttpResponse:
    """Get authenticated user's profile and analytics"""
    
    try:
        # Authenticate user
        from auth.unified_auth_service import UnifiedAuthService
        from services.user_profile_service import user_profile_service
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({
                    "error": "Authentication required",
                    "message": "Please sign in to view your profile"
                }),
                status_code=401,
                headers={
                    "Content-Type": "application/json",
                    "WWW-Authenticate": "Bearer"
                }
            )
        
        # Get user profile
        user_profile = await user_profile_service.get_or_create_user_profile(authenticated_user)
        
        # Get analytics
        analytics = await user_profile_service.get_user_analytics(user_profile.id)
        
        # Build response
        profile_data = {
            "profile": {
                "id": user_profile.id,
                "email": user_profile.email,
                "name": user_profile.name,
                "given_name": user_profile.given_name,
                "family_name": user_profile.family_name,
                "company_name": user_profile.company_name,
                "preferred_language": user_profile.preferred_language,
                "timezone": user_profile.timezone,
                "account_status": user_profile.account_status,
                "created_at": user_profile.created_at.isoformat() if user_profile.created_at else None,
                "last_login": user_profile.last_login.isoformat() if user_profile.last_login else None,
                "last_activity": user_profile.last_activity.isoformat() if user_profile.last_activity else None
            },
            "preferences": user_profile.user_preferences,
            "usage_stats": user_profile.usage_stats,
            "recent_activity": user_profile.recent_activity[-5:],  # Last 5 interactions
            "bookmarks": {
                "count": len(user_profile.bookmarks),
                "recent": user_profile.bookmarks[-3:] if user_profile.bookmarks else []  # Last 3 bookmarks
            },
            "analytics": analytics,
            "privacy": {
                "data_retention_consent": user_profile.data_retention_consent,
                "analytics_consent": user_profile.analytics_consent,
                "last_consent_update": user_profile.last_consent_update.isoformat() if user_profile.last_consent_update else None
            }
        }
        
        return func.HttpResponse(
            json.dumps(profile_data, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting user profile: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Profile retrieval failed",
                "message": "Unable to load your profile"
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="user/bookmark", methods=["POST"])
async def add_user_bookmark(req: func.HttpRequest) -> func.HttpResponse:
    """Add a bookmark to user's profile"""
    
    try:
        # Authenticate user
        from auth.unified_auth_service import UnifiedAuthService
        from services.user_profile_service import user_profile_service
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({
                    "error": "Authentication required",
                    "message": "Please sign in to bookmark content"
                }),
                status_code=401,
                headers={
                    "Content-Type": "application/json",
                    "WWW-Authenticate": "Bearer"
                }
            )
        
        # Parse request body
        try:
            bookmark_data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        if not bookmark_data:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Get user profile
        user_profile = await user_profile_service.get_or_create_user_profile(authenticated_user)
        
        # Add bookmark
        success = await user_profile_service.add_bookmark(user_profile.id, bookmark_data)
        
        if success:
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "Bookmark added successfully"
                }),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": "Failed to add bookmark",
                    "message": "Unable to save bookmark"
                }),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
        
    except Exception as e:
        logger.error(f"❌ Error adding bookmark: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Bookmark creation failed",
                "message": "Unable to add bookmark"
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="test", methods=["GET"])
def test_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Test endpoint to verify deployment"""
    return func.HttpResponse(
        json.dumps({
            "status": "ok", 
            "message": "Multi-personality function app is working!",
            "personalities": list(PERSONALITIES.keys()),
            "endpoints": ["health", "personalities/active", "spiritual_guidance", "test"]
        }),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )

# Import admin endpoints
from admin.admin_endpoints import (
    admin_get_user_role, 
    admin_cost_dashboard, 
    admin_user_management,
    admin_budget_management,
    admin_system_health
)

@app.route(route="vimarsh-admin/role", methods=["GET"])
async def admin_role_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin role check endpoint"""
    return await admin_get_user_role(req)

@app.route(route="vimarsh-admin/cost-dashboard", methods=["GET"])
async def admin_cost_dashboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin cost dashboard endpoint"""
    return await admin_cost_dashboard(req)

@app.route(route="vimarsh-admin/users", methods=["GET", "POST"])
async def admin_users_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin user management endpoint"""
    return await admin_user_management(req)

@app.route(route="vimarsh-admin/users/{user_id}/block", methods=["POST"])
async def admin_block_user_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin block user endpoint"""
    return await admin_user_management(req)

@app.route(route="vimarsh-admin/users/{user_id}/unblock", methods=["POST"])
async def admin_unblock_user_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin unblock user endpoint"""
    return await admin_user_management(req)

@app.route(route="vimarsh-admin/budget/{user_id}", methods=["PUT"])
async def admin_budget_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin budget management endpoint"""
    return await admin_budget_management(req)

@app.route(route="vimarsh-admin/health", methods=["GET"])
async def admin_health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin health check endpoint"""
    return await admin_system_health(req)

# CORS handling
@app.route(route="{*route}", methods=["OPTIONS"])
def handle_options(req: func.HttpRequest) -> func.HttpResponse:
    """Handle CORS preflight requests"""
    return func.HttpResponse(
        "",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    )
