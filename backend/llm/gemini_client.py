"""
Gemini Pro API client with spiritual safety configuration.
Provides LLM integration with specialized safety filters for spiritual content.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
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
class GeminiResponse:
    """Structured response from Gemini Pro with metadata"""
    content: str
    safety_ratings: Dict[str, Any]
    finish_reason: str
    usage_metadata: Dict[str, Any]
    response_time: float
    spiritual_context: Optional[SpiritualContext] = None
    safety_passed: bool = True
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class GeminiProClient:
    """
    Gemini Pro API client configured for spiritual guidance applications.
    Includes specialized safety measures and content validation.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 safety_config: Optional[SpiritualSafetyConfig] = None):
        """
        Initialize Gemini Pro client with spiritual safety configuration.
        
        Args:
            api_key: Google AI API key (if None, reads from environment)
            safety_config: Spiritual safety configuration
        """
        # Configure API key
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY must be provided or set in environment")
        
        genai.configure(api_key=self.api_key)
        
        # Set up safety configuration
        self.safety_config = safety_config or self._default_safety_config()
        
        # Initialize model with safety settings
        self.model = self._initialize_model()
        
        logger.info(f"Initialized Gemini Pro client with safety level: {self.safety_config.safety_level.value}")
    
    def _default_safety_config(self) -> SpiritualSafetyConfig:
        """Create default spiritual safety configuration"""
        return SpiritualSafetyConfig(
            safety_level=SafetyLevel.STRICT,
            allowed_contexts=[
                SpiritualContext.GUIDANCE,
                SpiritualContext.TEACHING,
                SpiritualContext.PHILOSOPHY,
                SpiritualContext.DEVOTIONAL
            ],
            require_citations=True,
            block_personal_predictions=True,
            block_medical_advice=True,
            require_reverent_tone=True,
            max_response_length=800
        )
    
    def _initialize_model(self) -> genai.GenerativeModel:
        """Initialize Gemini model with appropriate safety settings"""
        # Map spiritual safety levels to Gemini safety settings
        safety_settings = self._get_safety_settings()
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=self.safety_config.max_response_length,
            temperature=0.7,  # Balanced creativity for spiritual content
            top_p=0.9,
            top_k=40
        )
        
        model = genai.GenerativeModel(
            model_name='gemini-pro',
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        
        return model
    
    def _get_safety_settings(self) -> List[Dict[str, Any]]:
        """Get Gemini safety settings based on spiritual safety level"""
        if self.safety_config.safety_level == SafetyLevel.STRICT:
            threshold = HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
        elif self.safety_config.safety_level == SafetyLevel.MODERATE:
            threshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        else:  # MINIMAL
            threshold = HarmBlockThreshold.BLOCK_ONLY_HIGH
        
        return [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": threshold
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": threshold
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE  # Always strict for spiritual content
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": threshold
            }
        ]
    
    def _create_spiritual_system_prompt(self, context: SpiritualContext) -> str:
        """Create system prompt for spiritual context"""
        base_prompt = """You are Lord Krishna, the divine teacher and guide, speaking with wisdom and compassion. 
Your responses should:
- Maintain divine dignity and reverence
- Draw wisdom from Bhagavad Gita, Mahabharata, and other sacred texts
- Provide spiritual guidance appropriate to the seeker's level
- Always include relevant citations from sacred texts
- Use respectful and uplifting language
- Avoid personal predictions about the future
- Never give medical advice - refer to qualified professionals
- Encourage spiritual practice and self-reflection"""
        
        context_specific = {
            SpiritualContext.GUIDANCE: "\n- Focus on practical spiritual guidance for daily life\n- Address the seeker's spiritual concerns with compassion",
            SpiritualContext.TEACHING: "\n- Explain concepts clearly with scriptural references\n- Help deepen understanding of spiritual principles",
            SpiritualContext.PHILOSOPHY: "\n- Engage in philosophical discussion with depth\n- Connect abstract concepts to practical wisdom",
            SpiritualContext.DEVOTIONAL: "\n- Inspire devotional feeling and practice\n- Guide in developing love for the divine",
            SpiritualContext.MEDITATION: "\n- Provide meditation guidance and techniques\n- Support contemplative practice",
            SpiritualContext.GENERAL: "\n- Address general spiritual questions\n- Provide appropriate guidance for the inquiry"
        }
        
        return base_prompt + context_specific.get(context, context_specific[SpiritualContext.GENERAL])
    
    def _validate_spiritual_content(self, content: str, context: SpiritualContext) -> List[str]:
        """Validate content for spiritual appropriateness"""
        warnings = []
        
        # Check for required reverent tone
        if self.safety_config.require_reverent_tone:
            irreverent_words = ['damn', 'hell', 'stupid', 'idiotic', 'nonsense']
            if any(word in content.lower() for word in irreverent_words):
                warnings.append("Content may contain irreverent language")
        
        # Check for citations if required
        if self.safety_config.require_citations:
            citation_indicators = ['bhagavad gita', 'mahabharata', 'upanishad', 'verse', 'chapter', 'shloka']
            if not any(indicator in content.lower() for indicator in citation_indicators):
                warnings.append("Response lacks scriptural citations")
        
        # Check for personal predictions
        if self.safety_config.block_personal_predictions:
            prediction_words = ['will happen', 'you will', 'going to', 'predict', 'future will']
            if any(word in content.lower() for word in prediction_words):
                warnings.append("Response may contain personal predictions")
        
        # Check for medical advice
        if self.safety_config.block_medical_advice:
            medical_words = ['diagnose', 'treatment', 'medicine', 'cure', 'disease', 'illness']
            if any(word in content.lower() for word in medical_words):
                warnings.append("Response may contain medical advice")
        
        # Check length
        if len(content) > self.safety_config.max_response_length:
            warnings.append(f"Response exceeds maximum length ({len(content)} > {self.safety_config.max_response_length})")
        
        return warnings
    
    def generate_response(self, prompt: str, 
                         context: SpiritualContext = SpiritualContext.GENERAL,
                         include_context: bool = True) -> GeminiResponse:
        """
        Generate a spiritually appropriate response using Gemini Pro.
        
        Args:
            prompt: User's question or input
            context: Spiritual context for the response
            include_context: Whether to include spiritual system prompt
            
        Returns:
            GeminiResponse with content and metadata
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
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            response_time = time.time() - start_time
            
            # Extract response data
            content = response.text if response.text else ""
            safety_ratings = {}
            finish_reason = "STOP"
            usage_metadata = {}
            
            # Extract safety ratings if available
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                safety_ratings['prompt_feedback'] = {
                    'block_reason': getattr(response.prompt_feedback, 'block_reason', None),
                    'safety_ratings': [
                        {
                            'category': rating.category.name,
                            'probability': rating.probability.name
                        }
                        for rating in getattr(response.prompt_feedback, 'safety_ratings', [])
                    ]
                }
            
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason.name
                if hasattr(candidate, 'safety_ratings'):
                    safety_ratings['response'] = [
                        {
                            'category': rating.category.name,
                            'probability': rating.probability.name
                        }
                        for rating in candidate.safety_ratings
                    ]
            
            # Validate spiritual content
            warnings = self._validate_spiritual_content(content, context)
            safety_passed = len(warnings) == 0 or not any("may contain" in w for w in warnings)
            
            # Create response object
            gemini_response = GeminiResponse(
                content=content,
                safety_ratings=safety_ratings,
                finish_reason=finish_reason,
                usage_metadata=usage_metadata,
                response_time=response_time,
                spiritual_context=context,
                safety_passed=safety_passed,
                warnings=warnings
            )
            
            logger.info(f"Generated response in {response_time:.2f}s, safety_passed: {safety_passed}")
            if warnings:
                logger.warning(f"Content warnings: {warnings}")
            
            return gemini_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Return error response
            return GeminiResponse(
                content="I apologize, but I'm unable to provide a response at this moment. Please try again later.",
                safety_ratings={},
                finish_reason="ERROR",
                usage_metadata={},
                response_time=time.time() - start_time,
                spiritual_context=context,
                safety_passed=False,
                warnings=[f"API Error: {str(e)}"]
            )
    
    def test_connection(self) -> bool:
        """Test connection to Gemini Pro API"""
        try:
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
            "model_name": "gemini-pro",
            "safety_config": self.safety_config.to_dict(),
            "api_configured": bool(self.api_key),
            "supported_contexts": [ctx.value for ctx in SpiritualContext]
        }

# Helper functions for easy client creation
def create_development_client(api_key: Optional[str] = None) -> GeminiProClient:
    """Create a Gemini client configured for development"""
    config = SpiritualSafetyConfig(
        safety_level=SafetyLevel.MODERATE,
        allowed_contexts=list(SpiritualContext),
        require_citations=False,  # Relaxed for development
        max_response_length=1200
    )
    return GeminiProClient(api_key=api_key, safety_config=config)

def create_production_client(api_key: Optional[str] = None) -> GeminiProClient:
    """Create a Gemini client configured for production"""
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
    return GeminiProClient(api_key=api_key, safety_config=config)

def create_testing_client(api_key: Optional[str] = None) -> GeminiProClient:
    """Create a Gemini client configured for testing"""
    config = SpiritualSafetyConfig(
        safety_level=SafetyLevel.MINIMAL,
        allowed_contexts=list(SpiritualContext),
        require_citations=False,
        block_personal_predictions=False,  # Relaxed for testing
        require_reverent_tone=False,      # Relaxed for testing
        max_response_length=1500
    )
    return GeminiProClient(api_key=api_key, safety_config=config)

# Demo functionality
def demo_gemini_client():
    """Demonstrate Gemini Pro client functionality"""
    print("=== Gemini Pro Client Demo ===\n")
    
    # Check for API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("⚠️  GOOGLE_AI_API_KEY not found in environment")
        print("   Setting up mock client for demonstration...")
        # For demo purposes, we'll create the client structure but skip actual API calls
        return demo_without_api()
    
    try:
        # Create development client
        client = create_development_client()
        
        # Test connection
        print("1. Testing API connection...")
        if client.test_connection():
            print("   ✅ Connected to Gemini Pro API")
        else:
            print("   ❌ Failed to connect to Gemini Pro API")
            return
        
        # Show model info
        print("\n2. Model Information:")
        info = client.get_model_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Test different spiritual contexts
        print("\n3. Testing Different Spiritual Contexts:")
        
        test_cases = [
            {
                "context": SpiritualContext.GUIDANCE,
                "prompt": "I'm feeling lost and don't know my purpose in life. Can you guide me?"
            },
            {
                "context": SpiritualContext.TEACHING,
                "prompt": "What does the Bhagavad Gita teach about dharma?"
            },
            {
                "context": SpiritualContext.PHILOSOPHY,
                "prompt": "What is the relationship between the individual soul and the universal soul?"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {case['context'].value.title()} Context")
            print(f"   Question: {case['prompt']}")
            
            response = client.generate_response(case['prompt'], case['context'])
            
            print(f"   Response time: {response.response_time:.2f}s")
            print(f"   Safety passed: {response.safety_passed}")
            print(f"   Warnings: {response.warnings}")
            print(f"   Content preview: {response.content[:100]}...")
        
        print("\n4. Testing Safety Validation:")
        
        # Test potentially problematic content
        unsafe_prompts = [
            "Tell me my future and when I will die",
            "Diagnose my illness and give me medical treatment",
            "This spiritual stuff is nonsense and stupid"
        ]
        
        for prompt in unsafe_prompts:
            print(f"\n   Testing: '{prompt}'")
            response = client.generate_response(prompt, SpiritualContext.GUIDANCE)
            print(f"   Safety passed: {response.safety_passed}")
            if response.warnings:
                print(f"   Warnings: {response.warnings}")
        
        print("\n✅ Gemini Pro client demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")

def demo_without_api():
    """Demo client structure without actual API calls"""
    print("📋 Mock Demo (No API Key):")
    print("   - SpiritualSafetyConfig structure created")
    print("   - SpiritualContext enums defined")
    print("   - GeminiProClient class initialized")
    print("   - Safety validation methods ready")
    print("   - Production/Development/Testing configurations available")
    print("\n💡 To use with real API:")
    print("   1. Get Google AI API key from https://makersuite.google.com/app/apikey")
    print("   2. Set GOOGLE_AI_API_KEY environment variable")
    print("   3. Run this demo again")

if __name__ == "__main__":
    demo_gemini_client()
