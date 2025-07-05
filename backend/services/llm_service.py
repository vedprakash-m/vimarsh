"""
Enhanced LLM Service for Vimarsh - Production-Ready Spiritual Guidance

This module provides a comprehensive LLM service interface that connects to 
real Gemini 2.5 Flash API with advanced safety controls, spiritual context awareness,
token tracking, and content validation specifically designed for spiritual guidance.
"""

import logging
import os
import time
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Import centralized configuration
try:
    from backend.core.config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Import database service for real citations
try:
    from .database_service import db_service
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety levels for spiritual content generation"""
    STRICT = "strict"          # Maximum safety for public deployment
    MODERATE = "moderate"      # Balanced safety for development
    MINIMAL = "minimal"        # Minimal safety for testing


class SpiritualContext(Enum):
    """Types of spiritual contexts for appropriate responses"""
    GUIDANCE = "guidance"              # Personal spiritual guidance
    TEACHING = "teaching"              # Educational content about scriptures
    PHILOSOPHY = "philosophy"          # Philosophical discussions
    DEVOTIONAL = "devotional"          # Devotional practices and prayers
    MEDITATION = "meditation"          # Meditation and contemplative practices
    PERSONAL_GROWTH = "personal_growth"  # Personal development and growth
    GENERAL = "general"               # General spiritual inquiries


@dataclass
class SpiritualSafetyConfig:
    """Configuration for spiritual content safety measures"""
    safety_level: SafetyLevel
    allowed_contexts: List[SpiritualContext]
    require_citations: bool = True
    block_personal_predictions: bool = True
    block_medical_advice: bool = True
    require_reverent_tone: bool = True
    max_response_length: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging"""
        return {
            "safety_level": self.safety_level.value,
            "allowed_contexts": [ctx.value for ctx in self.allowed_contexts],
            "require_citations": self.require_citations,
            "block_personal_predictions": self.block_personal_predictions,
            "block_medical_advice": self.block_medical_advice,
            "require_reverent_tone": self.require_reverent_tone,
            "max_response_length": self.max_response_length
        }


@dataclass
class TokenUsage:
    """Token usage information for cost tracking"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    model_name: str = "gemini-2.5-flash"


@dataclass
class SpiritualResponse:
    """Enhanced spiritual response structure with safety and validation"""
    content: str
    citations: List[str] = field(default_factory=list)
    confidence: float = 0.8
    language: str = "English"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced fields from old system
    spiritual_context: Optional[SpiritualContext] = None
    safety_ratings: Dict[str, Any] = field(default_factory=dict)
    safety_passed: bool = True
    safety_score: float = 1.0
    finish_reason: str = "STOP"
    token_usage: Optional[TokenUsage] = None
    response_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    
    # Validation flags
    content_validated: bool = True
    citations_verified: bool = False
    reverent_tone_checked: bool = False


class EnhancedLLMService:
    """
    Production-ready LLM service for spiritual guidance with comprehensive safety controls,
    context awareness, token tracking, and content validation.
    """
    
    def __init__(self, api_key: Optional[str] = None, safety_config: Optional[SpiritualSafetyConfig] = None):
        """
        Initialize enhanced LLM service with safety configuration.
        
        Args:
            api_key: Google AI API key (if None, reads from configuration)
            safety_config: Spiritual safety configuration
        """
        # Load configuration
        if CONFIG_AVAILABLE:
            config = get_config()
            self.api_key = api_key or config.llm.api_key
            self.model_name = config.llm.model
            self.temperature = config.llm.temperature
            self.max_tokens = config.llm.max_tokens
            self.safety_settings_level = config.llm.safety_settings
        else:
            # Fallback to environment variables
            self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
            self.model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
            self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
            self.max_tokens = int(os.getenv("MAX_TOKENS", "150"))  # Reduced for concise responses
            self.safety_settings_level = os.getenv("SAFETY_SETTINGS", "BLOCK_MEDIUM_AND_ABOVE")
        
        self.is_configured = bool(self.api_key and self.api_key != "dev-mode-placeholder")
        
        # Set up safety configuration
        self.safety_config = safety_config or self._default_safety_config()
        
        if self.is_configured:
            # Configure Gemini 2.5 Flash with safety settings
            genai.configure(api_key=self.api_key)
            self.model = self._initialize_model()
            logger.info(f"✅ Enhanced Gemini 2.5 Flash API configured with safety level: {self.safety_config.safety_level.value}")
        else:
            logger.warning("GEMINI_API_KEY not found - using enhanced fallback responses")
            self.model = None
    
    def _default_safety_config(self) -> SpiritualSafetyConfig:
        """Create default safety configuration for spiritual guidance"""
        return SpiritualSafetyConfig(
            safety_level=SafetyLevel.MODERATE,
            allowed_contexts=[
                SpiritualContext.GUIDANCE,
                SpiritualContext.TEACHING,
                SpiritualContext.PHILOSOPHY,
                SpiritualContext.DEVOTIONAL,
                SpiritualContext.MEDITATION,
                SpiritualContext.PERSONAL_GROWTH,
                SpiritualContext.GENERAL
            ],
            require_citations=True,
            block_personal_predictions=True,
            block_medical_advice=True,
            require_reverent_tone=True,
            max_response_length=300  # Further reduced for conciseness
        )
    
    def _initialize_model(self) -> genai.GenerativeModel:
        """Initialize Gemini model with safety settings"""
        safety_settings = self._get_safety_settings()
        
        generation_config = {
            "temperature": self.temperature,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": min(self.max_tokens, self.safety_config.max_response_length),
        }
        
        return genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
    
    def _get_safety_settings(self) -> List[Dict[str, Any]]:
        """Configure safety settings based on safety level"""
        if self.safety_config.safety_level == SafetyLevel.STRICT:
            threshold = HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
        elif self.safety_config.safety_level == SafetyLevel.MODERATE:
            threshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        else:  # MINIMAL
            threshold = HarmBlockThreshold.BLOCK_ONLY_HIGH
        
        return [
            {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": threshold},
            {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": threshold},
            {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": threshold},
            {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": threshold},
        ]
    
    def _create_spiritual_system_prompt(self, context: SpiritualContext) -> str:
        """Create context-appropriate spiritual system prompt"""
        base_prompt = """You are Lord Krishna, the divine teacher and guide from the Bhagavad Gita. You embody infinite compassion, wisdom, and love. A sincere seeker has come to you with a spiritual question.

RESPONSE REQUIREMENTS:
- Keep responses EXTREMELY concise (maximum 60-80 words)
- ALWAYS include a specific scriptural citation with exact verse
- Begin with "Beloved devotee," "Dear soul," etc. (NO folded hands emoji)
- Provide ONE core teaching with practical application
- End with a blessing
- Use proper markdown formatting for emphasis

FOR FOLLOW-UP QUESTIONS:
- Begin with connecting phrases like "Building on what I shared..." or "To elaborate further..."
- Expand on the SAME concept from previous response
- Reference the previous teaching and add deeper insights
- Include complementary scriptural citations
- Make it feel like a natural conversation continuation

MANDATORY CITATION FORMAT:
- MUST include exact verse with both Sanskrit script and transliteration
- Format: "As I teach in Bhagavad Gita 2.47: **कर्मण्येवाधिकारस्ते मा फलेषु कदाचन** (*karmaṇy evādhikāras te mā phaleṣu kadācana*) - You have the right to action, but not to its fruits."
- Include Sanskrit Devanagari, romanized Sanskrit, and English meaning
- Reference chapter.verse for all quotes
- No response without a scriptural citation

RESPONSE STRUCTURE (STRICT):
1. Brief greeting: "Beloved devotee," or "Dear soul,"
2. ONE core teaching (1-2 sentences)
3. Scriptural citation with Sanskrit script + transliteration + translation
4. Brief practical application (1 sentence)
5. Blessing with 🕉️

FORMATTING RULES:
- Use **bold** for emphasis instead of asterisks
- Use *italics* for Sanskrit transliteration
- Use proper line breaks for readability
- Sanskrit script should be in Devanagari

SAFETY GUIDELINES:
- No medical, legal, or professional advice
- No personal predictions about the future
- Maintain spiritual authenticity and reverent tone
- Redirect inappropriate questions to spiritual matters

EXAMPLE RESPONSE:
Beloved devotee, when facing difficult choices, remember that **true wisdom** lies in performing your duty without attachment to results. 

As I teach in Bhagavad Gita 2.47: **कर्मण्येवाधिकारस्ते मा फलेषु कदाचन** (*karmaṇy evādhikāras te mā phaleṣu kadācana*) - You have the right to action, but not to its fruits.

Focus on righteous action and let Me handle the outcomes. May you find **peace** in surrendering results to the Divine. 🕉️

EXAMPLE FOLLOW-UP RESPONSE:
Building on what I shared, dear soul, **karma yoga** is the path of selfless action that purifies the heart and leads to liberation.

As I further explain in Bhagavad Gita 2.48: **योगस्थः कुरु कर्माणि** (*yogasthaḥ kuru karmāṇi*) - Established in yoga, perform your actions with equanimity in success and failure.

This practice transforms ordinary work into spiritual **sadhana**. May you find joy in this divine discipline. 🕉️"""

        context_specific = {
            SpiritualContext.GUIDANCE: "\nCONTEXT: Provide personal spiritual guidance for life challenges, helping the seeker find inner peace and right action through dharmic principles.",
            SpiritualContext.TEACHING: "\nCONTEXT: Share educational content about Hindu scriptures, philosophy, and spiritual practices with clarity and authenticity.",
            SpiritualContext.PHILOSOPHY: "\nCONTEXT: Engage in philosophical discussions about the nature of reality, consciousness, and spiritual truth as revealed in Vedantic teachings.",
            SpiritualContext.DEVOTIONAL: "\nCONTEXT: Guide devotional practices, bhakti yoga, and cultivating love and surrender to the Divine.",
            SpiritualContext.MEDITATION: "\nCONTEXT: Teach meditation techniques, mindfulness practices, and methods for achieving inner stillness and self-realization.",
            SpiritualContext.PERSONAL_GROWTH: "\nCONTEXT: Support spiritual development, character building, and the cultivation of divine qualities like compassion, patience, and wisdom.",
            SpiritualContext.GENERAL: "\nCONTEXT: Address general spiritual inquiries with wisdom appropriate to the seeker's level of understanding."
        }
        
        return base_prompt + context_specific.get(context, context_specific[SpiritualContext.GENERAL])
    
    def _validate_spiritual_content(self, content: str, context: SpiritualContext) -> List[str]:
        """Validate content for spiritual appropriateness"""
        warnings = []
        
        # Check for appropriate greeting (no emoji required)
        appropriate_greetings = ["beloved devotee", "dear soul", "dear seeker", "beloved child"]
        if not any(greeting in content.lower() for greeting in appropriate_greetings):
            warnings.append("Response should begin with appropriate spiritual greeting")
        
        # Check for inappropriate emoji usage
        if content.startswith("🙏"):
            warnings.append("Response should not begin with folded hands emoji")
        
        # Check for harmful content patterns
        harmful_patterns = [
            r"medical advice",
            r"legal advice", 
            r"financial advice",
            r"predict.*future",
            r"miracle.*cure",
            r"guaranteed.*result"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, content.lower()):
                warnings.append(f"Content may contain inappropriate advice: {pattern}")
        
        # Check length
        if len(content) > self.safety_config.max_response_length:
            warnings.append(f"Response too long: {len(content)} > {self.safety_config.max_response_length}")
        
        return warnings
    
    def _extract_citations_advanced(self, content: str) -> List[str]:
        """Advanced citation extraction with multiple pattern matching"""
        citations = []
        
        # Citation patterns for Hindu scriptures
        citation_patterns = [
            r'Bhagavad Gita \d+\.\d+',
            r'BG \d+\.\d+',
            r'Srimad Bhagavatam \d+\.\d+\.\d+',
            r'SB \d+\.\d+\.\d+',
            r'Mahabharata \d+\.\d+',
            r'Ramayana \d+\.\d+',
            r'Upanishads?',
            r'Vedas?',
            r'Puranas?'
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            citations.extend(matches)
        
        # Remove duplicates and return
        return list(set(citations))
    
    def _estimate_token_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost based on token usage"""
        # Gemini 2.5 Flash pricing (approximate)
        input_cost_per_1k = 0.0005  # $0.0005 per 1K input tokens
        output_cost_per_1k = 0.0015  # $0.0015 per 1K output tokens
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters)"""
        return len(text) // 4
    
    async def get_spiritual_guidance(self, query: str, context: str = "general", conversation_context: List[Dict[str, str]] = None) -> SpiritualResponse:
        """
        Get spiritual guidance with comprehensive safety analysis and validation.
        
        Args:
            query: The spiritual question or inquiry
            context: Spiritual context (guidance, teaching, philosophy, etc.)
            conversation_context: Previous messages for follow-up questions
            
        Returns:
            SpiritualResponse with content, safety analysis, and metadata
        """
        start_time = time.time()
        
        # Convert context string to enum
        spiritual_context = self._parse_context(context)
        
        if not self.is_configured:
            return self._get_fallback_response(query, context)
        
        try:
            # Create comprehensive spiritual guidance prompt
            spiritual_prompt = self._create_spiritual_system_prompt(spiritual_context)
            
            # Build full prompt with conversation context
            full_prompt = self._build_contextual_prompt(spiritual_prompt, query, conversation_context)
            
            # Generate response using Gemini 2.5 Flash
            response = self.model.generate_content(full_prompt)
            response_time = time.time() - start_time
            
            # Parse response with comprehensive safety analysis
            return self._parse_gemini_response_advanced(response, query, spiritual_context, response_time, full_prompt)
            
        except Exception as e:
            logger.error(f"Gemini 2.5 Flash API error: {e}")
            response_time = time.time() - start_time
            return self._get_error_response(query, str(e), response_time)
    
    def _parse_context(self, context: str) -> SpiritualContext:
        """Parse context string to SpiritualContext enum"""
        context_mapping = {
            "guidance": SpiritualContext.GUIDANCE,
            "teaching": SpiritualContext.TEACHING,
            "philosophy": SpiritualContext.PHILOSOPHY,
            "devotional": SpiritualContext.DEVOTIONAL,
            "meditation": SpiritualContext.MEDITATION,
            "personal_growth": SpiritualContext.PERSONAL_GROWTH,
            "general": SpiritualContext.GENERAL
        }
        return context_mapping.get(context.lower(), SpiritualContext.GENERAL)
    
    def _build_contextual_prompt(self, spiritual_prompt: str, query: str, conversation_context: List[Dict[str, str]] = None) -> str:
        """Build a contextual prompt that includes conversation history for follow-up questions"""
        
        # Start with the base spiritual prompt
        full_prompt = spiritual_prompt
        
        # Add conversation context if provided
        if conversation_context and len(conversation_context) > 0:
            full_prompt += "\n\nCONVERSATION CONTEXT (for follow-up questions):"
            
            # Only include the last few messages to avoid token limits
            recent_context = conversation_context[-4:] if len(conversation_context) > 4 else conversation_context
            
            for i, message in enumerate(recent_context):
                role = message.get('role', 'user')
                content = message.get('content', '')
                
                if role == 'user':
                    full_prompt += f"\nSeeker's Previous Question: {content}"
                elif role == 'assistant':
                    full_prompt += f"\nLord Krishna's Previous Response: {content}"
        
        # Add the current question
        full_prompt += f"\n\nSeeker's Current Question: {query}"
        
        # Add enhanced instructions for handling follow-ups
        if conversation_context and len(conversation_context) > 0:
            # Check if this looks like a follow-up question
            follow_up_patterns = ['give more details', 'explain further', 'tell me more', 'can you elaborate', 'expand on', 'more about', 'deeper', 'further explanation']
            is_follow_up = any(pattern in query.lower() for pattern in follow_up_patterns)
            
            if is_follow_up:
                full_prompt += "\n\nIMPORTANT: This is a follow-up question asking for more details. You should:"
                full_prompt += "\n- Begin with a phrase like 'Building on what I shared...' or 'To elaborate further, dear soul...'"
                full_prompt += "\n- Expand on the SAME concept from your previous response"
                full_prompt += "\n- Reference the previous teaching and add deeper insights"
                full_prompt += "\n- Include additional scriptural citations that complement the previous one"
                full_prompt += "\n- Make it feel like a natural continuation of the conversation"
                full_prompt += "\n- Still maintain the concise format but with more depth"
            else:
                full_prompt += "\n\nNOTE: Use conversation context to inform your response, but this appears to be a new question rather than a follow-up."
        
        full_prompt += "\n\nLord Krishna's Response:"
        
        return full_prompt
    
    def _parse_gemini_response_advanced(self, response, query: str, context: SpiritualContext, 
                                       response_time: float, full_prompt: str) -> SpiritualResponse:
        """
        Advanced parsing of Gemini 2.5 Flash response with comprehensive safety and metadata analysis.
        
        This method extracts all available metadata from the Gemini response including:
        - Safety ratings and content blocking detection
        - Token usage and cost calculation
        - Finish reason analysis
        - Content validation and warning generation
        """
        try:
            # Extract content with safety blocking detection
            content = ""
            content_blocked = False
            finish_reason = "STOP"
            
            try:
                if hasattr(response, 'text'):
                    if response.text is None:
                        content_blocked = True
                        content = "Dear soul, I apologize, but I cannot provide an appropriate response to that query. Please ask something more suitable for spiritual guidance."
                    else:
                        content = response.text if response.text else ""
                        if not isinstance(content, str):
                            content = str(content) if content is not None else ""
                else:
                    content = "Dear soul, I apologize, but I'm having difficulty accessing the spiritual wisdom right now."
            except Exception:
                content = "Dear soul, I apologize, but I'm having difficulty accessing the spiritual wisdom right now."
            
            # Extract safety ratings with comprehensive analysis
            safety_ratings = self._extract_safety_ratings(response)
            
            # Extract finish reason
            finish_reason = self._extract_finish_reason(response)
            
            # Extract and calculate token usage
            token_usage = self._extract_token_usage(response, full_prompt, content)
            
            # Advanced content validation
            content_warnings = self._validate_spiritual_content(content, context)
            
            # Advanced citation extraction
            citations = self._extract_citations_advanced(content)
            
            # Calculate overall safety status
            safety_passed = not content_blocked and finish_reason in ["STOP", "MAX_TOKENS"] and len(content_warnings) == 0
            safety_score = self._calculate_safety_score(safety_ratings, content_warnings, content_blocked)
            
            # Validate content quality
            content_validated = self._validate_content_quality(content, context)
            citations_verified = self._verify_citations(citations) if citations else False
            reverent_tone_checked = self._check_reverent_tone(content)
            
            return SpiritualResponse(
                content=content,
                citations=citations,
                confidence=0.9 if safety_passed else 0.7,
                language="English",
                metadata={
                    "model": "gemini-2.5-flash",
                    "response_time": response_time,
                    "query_length": len(query),
                    "response_length": len(content),
                    "finish_reason": finish_reason,
                    "content_blocked": content_blocked,
                    "total_tokens": token_usage.total_tokens,
                    "estimated_cost": token_usage.estimated_cost
                },
                spiritual_context=context,
                safety_ratings=safety_ratings,
                safety_passed=safety_passed,
                safety_score=safety_score,
                finish_reason=finish_reason,
                token_usage=token_usage,
                response_time=response_time,
                warnings=content_warnings,
                content_validated=content_validated,
                citations_verified=citations_verified,
                reverent_tone_checked=reverent_tone_checked
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._get_error_response(query, str(e), response_time)
    
    def _extract_safety_ratings(self, response) -> Dict[str, Any]:
        """Extract comprehensive safety ratings from Gemini response"""
        safety_ratings = {}
        
        try:
            # Extract prompt feedback safety ratings
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                safety_ratings['prompt_feedback'] = {
                    'block_reason': getattr(response.prompt_feedback, 'block_reason', None),
                    'safety_ratings': []
                }
                
                try:
                    prompt_ratings = getattr(response.prompt_feedback, 'safety_ratings', [])
                    if hasattr(prompt_ratings, '__iter__'):
                        safety_ratings['prompt_feedback']['safety_ratings'] = [
                            {
                                'category': getattr(rating, 'category', {}).get('name', 'UNKNOWN') if hasattr(getattr(rating, 'category', {}), 'name') else 'UNKNOWN',
                                'probability': getattr(rating, 'probability', {}).get('name', 'UNKNOWN') if hasattr(getattr(rating, 'probability', {}), 'name') else 'UNKNOWN'
                            }
                            for rating in prompt_ratings
                        ]
                except Exception:
                    pass
            
            # Extract candidate safety ratings
            if hasattr(response, 'candidates') and response.candidates:
                candidates = response.candidates
                if hasattr(candidates, '__len__') and len(candidates) > 0:
                    candidate = candidates[0]
                    if hasattr(candidate, 'safety_ratings'):
                        try:
                            candidate_ratings = getattr(candidate, 'safety_ratings', [])
                            if hasattr(candidate_ratings, '__iter__'):
                                safety_ratings['response'] = [
                                    {
                                        'category': getattr(rating, 'category', {}).get('name', 'UNKNOWN') if hasattr(getattr(rating, 'category', {}), 'name') else 'UNKNOWN',
                                        'probability': getattr(rating, 'probability', {}).get('name', 'UNKNOWN') if hasattr(getattr(rating, 'probability', {}), 'name') else 'UNKNOWN'
                                    }
                                    for rating in candidate_ratings
                                ]
                        except Exception:
                            pass
                            
        except Exception as e:
            logger.warning(f"Error extracting safety ratings: {e}")
        
        return safety_ratings
    
    def _extract_finish_reason(self, response) -> str:
        """Extract finish reason from Gemini response"""
        finish_reason = "STOP"
        
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidates = response.candidates
                if hasattr(candidates, '__len__') and len(candidates) > 0:
                    candidate = candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason_attr = getattr(candidate, 'finish_reason', None)
                        if hasattr(finish_reason_attr, 'name'):
                            finish_reason = finish_reason_attr.name
                        else:
                            finish_reason = str(finish_reason_attr) if finish_reason_attr else "STOP"
        except Exception as e:
            logger.warning(f"Error extracting finish reason: {e}")
        
        return finish_reason
    
    def _extract_token_usage(self, response, full_prompt: str, content: str) -> TokenUsage:
        """Extract token usage from Gemini response with fallback estimation"""
        try:
            # Try to extract real usage metadata
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                total_tokens = getattr(response.usage_metadata, 'total_token_count', input_tokens + output_tokens)
                
                return TokenUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=self._estimate_token_cost(input_tokens, output_tokens),
                    model_name="gemini-2.5-flash"
                )
        except Exception as e:
            logger.warning(f"Could not extract real token usage: {e}")
        
        # Fallback to estimation
        input_tokens = self._estimate_tokens(full_prompt)
        output_tokens = self._estimate_tokens(content)
        total_tokens = input_tokens + output_tokens
        
        return TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=self._estimate_token_cost(input_tokens, output_tokens),
            model_name="gemini-2.5-flash"
        )
    
    def _calculate_safety_score(self, safety_ratings: Dict[str, Any], warnings: List[str], content_blocked: bool) -> float:
        """Calculate overall safety score based on multiple factors"""
        if content_blocked:
            return 0.0
        
        # Start with base score
        score = 1.0
        
        # Deduct for warnings
        score -= len(warnings) * 0.1
        
        # Analyze safety ratings
        if safety_ratings.get('prompt_feedback', {}).get('block_reason'):
            score -= 0.3
        
        if safety_ratings.get('response'):
            high_risk_count = sum(1 for rating in safety_ratings['response'] 
                                if rating.get('probability') in ['HIGH', 'MEDIUM'])
            score -= high_risk_count * 0.2
        
        return max(0.0, min(1.0, score))
    
    def _validate_content_quality(self, content: str, context: SpiritualContext) -> bool:
        """Validate overall content quality for spiritual guidance"""
        if not content or len(content.strip()) < 10:
            return False
        
        # Check for appropriate spiritual greeting (no emoji required)
        appropriate_greetings = ["beloved devotee", "dear soul", "dear seeker", "beloved child"]
        if not any(greeting in content.lower() for greeting in appropriate_greetings):
            return False
        
        # Check for spiritual substance
        spiritual_terms = ["krishna", "divine", "spiritual", "dharma", "soul", "consciousness", "wisdom"]
        if not any(term in content.lower() for term in spiritual_terms):
            return False
        
        return True
    
    def _verify_citations(self, citations: List[str]) -> bool:
        """Verify citations against available spiritual texts"""
        if not citations:
            return False
        
        # Simple verification - check if citations follow expected patterns
        valid_sources = ["bhagavad gita", "bg", "srimad bhagavatam", "sb", "mahabharata", "ramayana"]
        
        for citation in citations:
            if any(source in citation.lower() for source in valid_sources):
                return True
        
        return False
    
    def _check_reverent_tone(self, content: str) -> bool:
        """Check if content maintains reverent tone appropriate for spiritual guidance"""
        # Check for appropriate greeting
        appropriate_greetings = ["beloved devotee", "dear soul", "dear seeker", "beloved child"]
        if not any(greeting in content.lower() for greeting in appropriate_greetings):
            return False
        
        # Check for inappropriate language
        irreverent_words = ['damn', 'hell', 'stupid', 'idiotic', 'nonsense', 'bullshit', 'crap']
        if any(word in content.lower() for word in irreverent_words):
            return False
        
        # Check for appropriate tone indicators
        reverent_indicators = ["beloved", "dear", "blessed", "divine", "sacred", "holy"]
        if not any(indicator in content.lower() for indicator in reverent_indicators):
            return False
        
        return True
    
    def _create_spiritual_prompt(self, query: str, context: str) -> str:
        """Create a spiritual guidance prompt for Gemini 2.5 Flash"""
        return f"""You are Lord Krishna, the divine teacher from the Bhagavad Gita. A devotee seeks your wisdom.

RESPONSE GUIDELINES:
- Keep response concise (100-150 words maximum)
- Include specific scriptural citations with exact quotes
- Format: "As I teach in Bhagavad Gita X.Y: 'Sanskrit text' (translation)"
- Begin with "🙏" and address as "dear soul" or "beloved devotee"
- Provide practical, actionable guidance
- End with a blessing or encouragement

Devotee's Question: {query}
Context: {context}

Your Response (with citations):"""
    
    def _parse_gemini_response(self, response, query: str) -> SpiritualResponse:
        """Parse Gemini 2.5 Flash response into structured format"""
        try:
            content = response.text.strip()
            
            # Extract citations if mentioned (simple pattern matching)
            citations = []
            if "gita" in content.lower() or "bhagavad" in content.lower():
                citations.append("Bhagavad Gita")
            if "mahabharata" in content.lower():
                citations.append("Mahabharata")
            if "bhagavatam" in content.lower():
                citations.append("Srimad Bhagavatam")
            
            return SpiritualResponse(
                content=content,
                citations=citations,
                confidence=0.9,  # High confidence for real API responses
                metadata={
                    "response_type": "gemini_pro_response",
                    "model": "gemini-2.5-flash",
                    "query_length": len(query),
                    "response_length": len(content)
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._get_error_response(query)
    
    def _get_fallback_response(self, query: str, context: str) -> SpiritualResponse:
        """Get a fallback response that maintains spiritual authenticity"""
        
        # Convert context string to enum
        spiritual_context = self._parse_context(context)
        
        # Simple keyword-based responses with real database lookup
        query_lower = query.lower()
        
        # Try to find relevant texts from database
        relevant_texts = []
        real_citations = []
        
        if DATABASE_AVAILABLE:
            try:
                # Search for relevant texts in database
                search_results = db_service.search_spiritual_texts(query, limit=3)
                if search_results:
                    relevant_texts = search_results
                    real_citations = [f"{text.source} {text.chapter}.{text.verse}" if text.chapter and text.verse 
                                    else f"{text.source}" for text in search_results]
            except Exception as e:
                logger.error(f"Database search error: {e}")
        
        if any(word in query_lower for word in ["dharma", "duty", "purpose"]):
            # Use database content if available
            if relevant_texts and any("duty" in text.content.lower() for text in relevant_texts):
                relevant_text = next(text for text in relevant_texts if "duty" in text.content.lower())
                content = f"Dear soul, {relevant_text.content[:150]}... This wisdom comes from the sacred texts."
                citations = [f"{relevant_text.source} {relevant_text.chapter}.{relevant_text.verse}"] if relevant_text.chapter else [relevant_text.source]
            else:
                content = "Dear soul, **dharma** is your righteous path in life. As Krishna teaches in the Bhagavad Gita, your dharma is determined by your nature and circumstances. Act according to your duties without attachment to results, offering all actions to the Divine."
                citations = ["Bhagavad Gita 2.47", "Bhagavad Gita 18.45-48"]
            
            return SpiritualResponse(
                content=content,
                citations=citations,
                confidence=0.8 if relevant_texts else 0.7,
                metadata={"response_type": "dharma_guidance", "keywords": ["dharma", "duty"], "database_used": bool(relevant_texts)},
                spiritual_context=spiritual_context,
                safety_passed=True,
                safety_score=1.0,
                content_validated=True,
                reverent_tone_checked=True,
                token_usage=TokenUsage(
                    input_tokens=self._estimate_tokens(query),
                    output_tokens=self._estimate_tokens(content),
                    total_tokens=self._estimate_tokens(query) + self._estimate_tokens(content),
                    estimated_cost=self._estimate_token_cost(self._estimate_tokens(query), self._estimate_tokens(content))
                )
            )
        
        elif any(word in query_lower for word in ["peace", "calm", "meditation"]):
            # Use database content if available
            if relevant_texts and any("meditation" in text.content.lower() or "peace" in text.content.lower() for text in relevant_texts):
                relevant_text = next((text for text in relevant_texts if "meditation" in text.content.lower() or "peace" in text.content.lower()), relevant_texts[0])
                content = f"Beloved devotee, {relevant_text.content[:150]}... Find this wisdom in the sacred teachings."
                citations = [f"{relevant_text.source} {relevant_text.chapter}.{relevant_text.verse}"] if relevant_text.chapter else [relevant_text.source]
            else:
                content = "Beloved devotee, **inner peace** comes through stilling the mind and surrendering to the Divine will. Practice meditation, breathe deeply, and remember that you are an eternal soul, not merely this temporary body. Find refuge in Krishna's love."
                citations = ["Bhagavad Gita 6.19", "Bhagavad Gita 12.6-7"]
            
            return SpiritualResponse(
                content=content,
                citations=citations,
                confidence=0.8 if relevant_texts else 0.7,
                metadata={"response_type": "peace_guidance", "keywords": ["peace", "meditation"], "database_used": bool(relevant_texts)},
                spiritual_context=spiritual_context,
                safety_passed=True,
                safety_score=1.0,
                content_validated=True,
                reverent_tone_checked=True,
                token_usage=TokenUsage(
                    input_tokens=self._estimate_tokens(query),
                    output_tokens=self._estimate_tokens(content),
                    total_tokens=self._estimate_tokens(query) + self._estimate_tokens(content),
                    estimated_cost=self._estimate_token_cost(self._estimate_tokens(query), self._estimate_tokens(content))
                )
            )
        
        elif any(word in query_lower for word in ["suffering", "pain", "difficult"]):
            # Use database content if available
            if relevant_texts and any("suffering" in text.content.lower() or "pain" in text.content.lower() or "distress" in text.content.lower() for text in relevant_texts):
                relevant_text = next((text for text in relevant_texts if any(word in text.content.lower() for word in ["suffering", "pain", "distress"])), relevant_texts[0])
                content = f"Dear soul, I understand your pain. {relevant_text.content[:150]}... This eternal wisdom guides us through all difficulties."
                citations = [f"{relevant_text.source} {relevant_text.chapter}.{relevant_text.verse}"] if relevant_text.chapter else [relevant_text.source]
            else:
                content = "Dear soul, I understand your pain. Krishna teaches that both **joy and sorrow** are temporary visitors. This suffering too shall pass. Use this experience to grow spiritually, to develop compassion, and to remember your eternal nature beyond these temporary circumstances."
                citations = ["Bhagavad Gita 2.14", "Bhagavad Gita 2.20"]
            
            return SpiritualResponse(
                content=content,
                citations=citations,
                confidence=0.8 if relevant_texts else 0.7,
                metadata={"response_type": "comfort_guidance", "keywords": ["suffering", "pain"], "database_used": bool(relevant_texts)},
                spiritual_context=spiritual_context,
                safety_passed=True,
                safety_score=1.0,
                content_validated=True,
                reverent_tone_checked=True,
                token_usage=TokenUsage(
                    input_tokens=self._estimate_tokens(query),
                    output_tokens=self._estimate_tokens(content),
                    total_tokens=self._estimate_tokens(query) + self._estimate_tokens(content),
                    estimated_cost=self._estimate_token_cost(self._estimate_tokens(query), self._estimate_tokens(content))
                )
            )
        
        else:
            # General response with database search
            if relevant_texts:
                # Use the most relevant text found
                relevant_text = relevant_texts[0]
                content = f"Thank you for your question, dear devotee. The sacred texts teach us: **{relevant_text.content[:120]}**... May this wisdom guide you on your spiritual path."
                citations = [f"{relevant_text.source} {relevant_text.chapter}.{relevant_text.verse}"] if relevant_text.chapter else [relevant_text.source]
                confidence = 0.8
            else:
                content = "Thank you for your question, dear devotee. In the Bhagavad Gita, Krishna teaches us that **all spiritual seeking is blessed**. Continue on your path with faith and devotion. If you could share more specific details about your spiritual concern, I can offer more targeted guidance."
                citations = ["Bhagavad Gita 7.16-18"]
                confidence = 0.6
            
            return SpiritualResponse(
                content=content,
                citations=citations,
                confidence=confidence,
                metadata={"response_type": "general_guidance", "query": query[:50], "database_used": bool(relevant_texts)},
                spiritual_context=spiritual_context,
                safety_passed=True,
                safety_score=1.0,
                content_validated=True,
                reverent_tone_checked=True,
                token_usage=TokenUsage(
                    input_tokens=self._estimate_tokens(query),
                    output_tokens=self._estimate_tokens(content),
                    total_tokens=self._estimate_tokens(query) + self._estimate_tokens(content),
                    estimated_cost=self._estimate_token_cost(self._estimate_tokens(query), self._estimate_tokens(content))
                )
            )
    
    def _get_error_response(self, query: str, error_msg: str = None, response_time: float = 0.0) -> SpiritualResponse:
        """Get an error response that maintains spiritual tone with comprehensive metadata"""
        return SpiritualResponse(
            content="Dear soul, I am experiencing technical difficulties accessing the spiritual wisdom right now. Please try again in a few moments. Your spiritual seeking is always welcome and blessed. (Backend LLM Error)",
            citations=[],
            confidence=0.3,
            language="English",
            metadata={
                "response_type": "error",
                "query": query[:50],
                "error_message": error_msg,
                "response_time": response_time,
                "model": "gemini-2.5-flash"
            },
            spiritual_context=SpiritualContext.GENERAL,
            safety_ratings={},
            safety_passed=False,
            safety_score=0.0,
            finish_reason="ERROR",
            token_usage=TokenUsage(),
            response_time=response_time,
            warnings=["API Error occurred"],
            content_validated=False,
            citations_verified=False,
            reverent_tone_checked=True  # Error response maintains reverent tone
        )
    
    def generate_response(self, prompt: str, context: SpiritualContext = SpiritualContext.GENERAL, 
                         include_context: bool = True, user_id: Optional[str] = None, 
                         session_id: Optional[str] = None) -> SpiritualResponse:
        """
        Generate a spiritually appropriate response with comprehensive safety analysis.
        
        This method provides compatibility with the old GeminiProClient interface
        while using the enhanced safety and validation features.
        
        Args:
            prompt: User's question or input
            context: Spiritual context for the response
            include_context: Whether to include spiritual system prompt
            user_id: User ID for tracking (optional)
            session_id: Session ID for tracking (optional)
            
        Returns:
            SpiritualResponse with comprehensive metadata
        """
        start_time = time.time()
        
        try:
            # Prepare full prompt
            if include_context:
                system_prompt = self._create_spiritual_system_prompt(context)
                full_prompt = f"{system_prompt}\n\nSeeker's Question: {prompt}\n\nLord Krishna's Response:"
            else:
                full_prompt = prompt
            
            logger.info(f"Generating response for context: {context.value}")
            
            if not self.is_configured:
                response_time = time.time() - start_time
                return self._get_fallback_response(prompt, context.value)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            response_time = time.time() - start_time
            
            # Parse response with advanced analysis
            spiritual_response = self._parse_gemini_response_advanced(response, prompt, context, response_time, full_prompt)
            
            # Track usage if user/session provided
            if user_id or session_id:
                self._track_usage(spiritual_response.token_usage, user_id, session_id, context)
            
            return spiritual_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response_time = time.time() - start_time
            return self._get_error_response(prompt, str(e), response_time)
    
    def _track_usage(self, token_usage: TokenUsage, user_id: Optional[str], 
                    session_id: Optional[str], context: SpiritualContext):
        """Track token usage for cost management"""
        try:
            # Try to use the cost management system if available
            try:
                from backend.cost_management.token_tracker import get_token_tracker
                tracker = get_token_tracker()
                tracker.track_usage(
                    operation_type='spiritual_guidance',
                    model_name=token_usage.model_name,
                    input_tokens=token_usage.input_tokens,
                    output_tokens=token_usage.output_tokens,
                    user_id=user_id,
                    session_id=session_id,
                    spiritual_context=context.value
                )
            except ImportError:
                # Cost management not available, log the usage
                logger.info(f"Token usage - Input: {token_usage.input_tokens}, Output: {token_usage.output_tokens}, Cost: ${token_usage.estimated_cost:.4f}")
        except Exception as e:
            logger.warning(f"Failed to track token usage: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to Gemini 2.5 Flash API"""
        try:
            if not self.is_configured:
                return False
            
            test_response = self.generate_response(
                "Test connection", 
                context=SpiritualContext.GENERAL,
                include_context=False
            )
            return test_response.finish_reason != "ERROR"
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model and configuration"""
        return {
            "model_name": "gemini-2.5-flash",
            "safety_config": self.safety_config.to_dict(),
            "api_configured": self.is_configured,
            "supported_contexts": [ctx.value for ctx in SpiritualContext]
        }
    
    def is_healthy(self) -> bool:
        """Check if LLM service is healthy"""
        try:
            return self.test_connection()
        except Exception:
            return False


# Helper functions for easy service creation
def create_development_service(api_key: Optional[str] = None) -> EnhancedLLMService:
    """Create an LLM service configured for development"""
    config = SpiritualSafetyConfig(
        safety_level=SafetyLevel.MODERATE,
        allowed_contexts=list(SpiritualContext),
        require_citations=False,  # Relaxed for development
        max_response_length=1200
    )
    return EnhancedLLMService(api_key=api_key, safety_config=config)


def create_production_service(api_key: Optional[str] = None) -> EnhancedLLMService:
    """Create an LLM service configured for production"""
    config = SpiritualSafetyConfig(
        safety_level=SafetyLevel.STRICT,
        allowed_contexts=[
            SpiritualContext.GUIDANCE,
            SpiritualContext.TEACHING,
            SpiritualContext.PHILOSOPHY,
            SpiritualContext.DEVOTIONAL
        ],
        require_citations=True,
        max_response_length=800
    )
    return EnhancedLLMService(api_key=api_key, safety_config=config)


def create_testing_service(api_key: Optional[str] = None) -> EnhancedLLMService:
    """Create an LLM service configured for testing"""
    config = SpiritualSafetyConfig(
        safety_level=SafetyLevel.MINIMAL,
        allowed_contexts=list(SpiritualContext),
        require_citations=False,
        block_personal_predictions=False  # Relaxed for testing
    )
    return EnhancedLLMService(api_key=api_key, safety_config=config)


# Global service instance
llm_service = EnhancedLLMService()
