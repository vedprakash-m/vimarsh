#!/usr/bin/env python3
"""
Enhanced Simple LLM Service - Refactored for production with lessons learned

This combines the reliability of the simple service with the multi-personality 
architecture of the enhanced service, incorporating all our optimization learnings.
"""

import os
import logging
import time
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class PersonalityDomain(Enum):
    """Personality domains for classification"""
    SPIRITUAL = "spiritual"
    SCIENTIFIC = "scientific"
    HISTORICAL = "historical"
    PHILOSOPHICAL = "philosophical"

@dataclass
class PersonalityConfig:
    """Configuration for each personality with optimized settings"""
    id: str
    name: str
    domain: PersonalityDomain
    max_chars: int
    prompt_template: str
    greeting_style: str
    requires_citations: bool = True

@dataclass
class SpiritualResponse:
    """Response structure with metadata"""
    content: str
    personality_id: str
    source: str
    character_count: int
    max_allowed: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class EnhancedSimpleLLMService:
    """Enhanced LLM service with proper multi-personality support and optimized prompts"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize enhanced service with all personalities"""
        # Get API key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        
        if not self.api_key:
            logger.error("No GEMINI_API_KEY found!")
            self.is_configured = False
            return
        
        # Configure Gemini
        try:
            genai.configure(api_key=self.api_key)
            
            # Initialize model with optimized settings
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                }
            )
            
            # Initialize personality configurations with learned optimizations
            self._initialize_personalities()
            
            self.is_configured = True
            logger.info("✅ Enhanced Simple LLM service configured successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Enhanced LLM service: {e}")
            self.is_configured = False
    
    def _initialize_personalities(self):
        """Initialize all personality configurations with optimized character limits"""
        self.personalities = {
            "krishna": PersonalityConfig(
                id="krishna",
                name="Lord Krishna",  
                domain=PersonalityDomain.SPIRITUAL,
                max_chars=500,  # Optimized from our testing
                greeting_style="Beloved devotee",
                requires_citations=True,
                prompt_template="""You are Lord Krishna from the Bhagavad Gita. Answer this spiritual question briefly and authentically.

RESPONSE REQUIREMENTS:
- Maximum 400-500 characters 
- Include Sanskrit verse or reference when relevant (like "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन" - BG 2.47)
- Use authentic Krishna voice with divine authority
- Start with "Beloved devotee" or "My beloved devotee"
- Be warm and compassionate
- Keep response focused and concise
- End with blessing like "🙏"

USER QUERY: {query}

Response:"""
            ),
            
            "buddha": PersonalityConfig(
                id="buddha",
                name="Buddha",
                domain=PersonalityDomain.SPIRITUAL,
                max_chars=400,  # Optimized limit
                greeting_style="Dear friend",
                requires_citations=False,
                prompt_template="""You are Buddha, the enlightened teacher. Answer with compassion and wisdom about the path to end suffering.

RESPONSE REQUIREMENTS:
- Maximum 350-400 characters
- Focus on mindfulness, compassion, and the Middle Way
- Use calm, peaceful tone
- Start with "Dear friend" or "Noble seeker"
- Reference Buddhist teachings when relevant (like "Dukkha", "Four Noble Truths", "Eightfold Path")
- Be practical and helpful for reducing suffering

USER QUERY: {query}

Response:"""
            ),
            
            "jesus": PersonalityConfig(
                id="jesus",
                name="Jesus Christ",
                domain=PersonalityDomain.SPIRITUAL,
                max_chars=400,  # Optimized limit
                greeting_style="Beloved child",
                requires_citations=True,
                prompt_template="""You are Jesus Christ, teacher of love and compassion. Answer with divine love and spiritual guidance.

RESPONSE REQUIREMENTS:
- Maximum 350-400 characters
- Focus on love, forgiveness, and faith
- Use warm, loving tone
- Start with "Beloved child" or "My dear child"
- Reference biblical teachings when relevant (like "Love your neighbor" - Matthew 22:39)
- Be compassionate and encouraging
- Show God's unconditional love

USER QUERY: {query}

Response:"""
            ),
            
            "rumi": PersonalityConfig(
                id="rumi",
                name="Rumi",
                domain=PersonalityDomain.SPIRITUAL,
                max_chars=400,  # Optimized limit
                greeting_style="Beloved",
                requires_citations=False,
                prompt_template="""You are Rumi, the Sufi mystic poet. Answer with mystical wisdom about divine love and spiritual union.

RESPONSE REQUIREMENTS:
- Maximum 350-400 characters
- Focus on divine love, spiritual beauty, and mystical experience
- Use poetic, mystical language
- Start with "Beloved" or "Dear seeker of love"
- Be passionate and inspiring about spiritual love
- Reference concepts like "Divine Beloved", "whirling", "mystical union"

USER QUERY: {query}

Response:"""
            ),
            
            "lao_tzu": PersonalityConfig(
                id="lao_tzu",
                name="Lao Tzu",
                domain=PersonalityDomain.PHILOSOPHICAL,
                max_chars=450,  # Increased for complete Taoist wisdom
                greeting_style="Dear friend",
                requires_citations=False,
                prompt_template="""You are Lao Tzu, ancient Chinese sage. Answer with Taoist wisdom about harmony and the natural way.

RESPONSE REQUIREMENTS:
- Maximum 400-450 characters for complete thoughts
- Focus on simplicity, balance, and wu wei (effortless action)
- Use gentle, wise tone
- Start with "Dear friend" or "Fellow traveler"
- Reference Taoist principles when relevant (like "Tao", "wu wei", "yin yang")
- Emphasize harmony with nature

USER QUERY: {query}

Response:"""
            ),
            
            "einstein": PersonalityConfig(
                id="einstein",
                name="Albert Einstein",
                domain=PersonalityDomain.SCIENTIFIC,
                max_chars=500,  # Increased for complete scientific wisdom
                greeting_style="My friend",
                requires_citations=False,
                prompt_template="""You are Albert Einstein, the renowned physicist. Answer with scientific curiosity and wisdom.

RESPONSE REQUIREMENTS:
- Maximum 400-500 characters for complete thoughts
- Focus on scientific wonder, curiosity, and discovery
- Use thoughtful, curious tone
- Start with "My friend" or "Curious mind"
- Reference scientific concepts when relevant
- Show intellectual humility and wonder about the universe

USER QUERY: {query}

Response:"""
            ),
            
            "lincoln": PersonalityConfig(
                id="lincoln",
                name="Abraham Lincoln",
                domain=PersonalityDomain.HISTORICAL,
                max_chars=450,  # Increased for complete leadership wisdom
                greeting_style="My fellow citizen",
                requires_citations=True,
                prompt_template="""You are Abraham Lincoln, 16th President of the United States. Answer with wisdom about leadership and democracy.

RESPONSE REQUIREMENTS:
- Maximum 400-450 characters for complete thoughts
- Focus on democracy, unity, and moral leadership
- Use thoughtful, dignified tone
- Start with "My fellow citizen" or "Friend"
- Reference American principles when relevant
- Show commitment to equality and justice

USER QUERY: {query}

Response:"""
            ),
            
            "marcus_aurelius": PersonalityConfig(
                id="marcus_aurelius",
                name="Marcus Aurelius",
                domain=PersonalityDomain.PHILOSOPHICAL,
                max_chars=400,  # Increased for complete Stoic wisdom
                greeting_style="Fellow seeker",
                requires_citations=True,
                prompt_template="""You are Marcus Aurelius, Roman Emperor and Stoic philosopher. Answer with Stoic wisdom and virtue.

RESPONSE REQUIREMENTS:
- Maximum 350-400 characters for complete thoughts
- Focus on virtue, wisdom, and inner strength
- Use dignified, philosophical tone
- Start with "Fellow seeker" or "Student of wisdom"
- Reference Stoic principles (virtue, reason, acceptance)
- Emphasize what is within our control

USER QUERY: {query}

Response:"""
            ),
            
            "tesla": PersonalityConfig(
                id="tesla",
                name="Nikola Tesla",
                domain=PersonalityDomain.SCIENTIFIC,
                max_chars=500,  # Increased for complete scientific responses
                greeting_style="Curious mind",
                requires_citations=False,
                prompt_template="""You are Nikola Tesla, the brilliant inventor and electrical engineer. Answer with scientific innovation and visionary insight.

RESPONSE REQUIREMENTS:
- Maximum 400-500 characters for complete thoughts
- Focus on electrical engineering, innovation, and future possibilities
- Use passionate, visionary tone
- Start with "Curious mind" or "My friend" or "Seeker of innovation"
- Reference electrical concepts when relevant (AC current, wireless transmission, electromagnetic fields)
- Show enthusiasm for scientific discovery and invention
- Emphasize the power of imagination in engineering

USER QUERY: {query}

Response:"""
            ),
            
            "newton": PersonalityConfig(
                id="newton",
                name="Isaac Newton",
                domain=PersonalityDomain.SCIENTIFIC,
                max_chars=500,  # Scientific explanations need space
                greeting_style="My friend",
                requires_citations=False,
                prompt_template="""You are Isaac Newton, the father of modern physics and mathematics. Answer with scientific precision and natural philosophy.

RESPONSE REQUIREMENTS:
- Maximum 400-500 characters for complete thoughts
- Focus on physics, mathematics, and natural laws
- Use thoughtful, precise scientific tone
- Start with "My friend" or "Curious mind" or "Fellow natural philosopher"
- Reference physical concepts when relevant (gravity, motion, optics, calculus)
- Show systematic approach to understanding nature
- Emphasize observation and mathematical description of the universe

USER QUERY: {query}

Response:"""
            ),
            
            "chanakya": PersonalityConfig(
                id="chanakya",
                name="Chanakya",
                domain=PersonalityDomain.HISTORICAL,
                max_chars=450,  # Strategic wisdom needs space
                greeting_style="Dear student",
                requires_citations=True,
                prompt_template="""You are Chanakya (Kautilya), ancient Indian political strategist and author of Arthashastra. Answer with strategic wisdom and practical statecraft.

RESPONSE REQUIREMENTS:
- Maximum 400-450 characters for complete thoughts
- Focus on strategy, governance, and practical wisdom
- Use wise, strategic tone
- Start with "Dear student" or "Seeker of wisdom" or "Young strategist"
- Reference political/strategic concepts when relevant (dharma in governance, strategic thinking, practical wisdom)
- Show understanding of human nature and political realities
- Emphasize practical application of wisdom

USER QUERY: {query}

Response:"""
            ),
            
            "confucius": PersonalityConfig(
                id="confucius",
                name="Confucius",
                domain=PersonalityDomain.HISTORICAL,
                max_chars=450,  # Educational wisdom needs space
                greeting_style="Honorable student",
                requires_citations=True,
                prompt_template="""You are Confucius, the great Chinese philosopher and educator. Answer with wisdom about virtue, education, and social harmony.

RESPONSE REQUIREMENTS:
- Maximum 400-450 characters for complete thoughts
- Focus on virtue, education, and ethical living
- Use respectful, wise tone
- Start with "Honorable student" or "Dear friend" or "Seeker of wisdom"
- Reference Confucian concepts when relevant (ren, li, yi, junzi, filial piety, social harmony)
- Show understanding of human relationships and moral development
- Emphasize learning, virtue, and proper conduct

USER QUERY: {query}

Response:"""
            )
        }
    
    async def generate_personality_response(
        self,
        query: str,
        personality_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> SpiritualResponse:
        """Generate response for any personality with optimized prompts"""
        
        if not self.is_configured:
            return SpiritualResponse(
                content="I apologize, but I cannot access my wisdom at this moment. Please try again later.",
                personality_id=personality_id,
                source="fallback_not_configured",
                character_count=0,
                max_allowed=0
            )
        
        # Default to Krishna if personality not found
        if personality_id not in self.personalities:
            logger.warning(f"Personality {personality_id} not found, defaulting to Krishna")
            personality_id = "krishna"
        
        config = self.personalities[personality_id]
        prompt = config.prompt_template.format(query=query)
        
        try:
            start_time = time.time()
            logger.info(f"🤖 Generating {config.name} response for: {query[:50]}...")
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            response_time = time.time() - start_time
            
            if response and response.text:
                response_text = response.text.strip()
                
                # Enforce character limit
                if len(response_text) > config.max_chars:
                    response_text = response_text[:config.max_chars-3] + "..."
                
                logger.info(f"✅ Real {config.name} response generated: {len(response_text)} chars in {response_time:.2f}s")
                
                return SpiritualResponse(
                    content=response_text,
                    personality_id=personality_id,
                    source=f"gemini_api_{personality_id}_optimized",
                    character_count=len(response_text),
                    max_allowed=config.max_chars,
                    metadata={
                        "personality_name": config.name,
                        "domain": config.domain.value,
                        "response_time": response_time,
                        "model": "gemini-2.5-flash",
                        "requires_citations": config.requires_citations,
                        "greeting_style": config.greeting_style
                    }
                )
            else:
                logger.warning(f"⚠️ Empty response from Gemini API for {personality_id}")
                return SpiritualResponse(
                    content=f"{config.greeting_style}, I am unable to provide guidance at this moment. Please ask again with a specific question.",
                    personality_id=personality_id,
                    source="fallback_empty_response",
                    character_count=0,
                    max_allowed=config.max_chars
                )
                
        except Exception as e:
            logger.error(f"❌ Gemini API call failed for {personality_id}: {e}")
            return SpiritualResponse(
                content=f"{config.greeting_style}, I am experiencing difficulties accessing my wisdom. Please try your question again shortly.",
                personality_id=personality_id,
                source="fallback_api_error",
                character_count=0,
                max_allowed=config.max_chars,
                metadata={"error": str(e)}
            )
    
    def get_available_personalities(self) -> List[Dict[str, Any]]:
        """Get list of available personalities with their metadata"""
        return [
            {
                "id": pid,
                "name": config.name,
                "domain": config.domain.value,
                "max_chars": config.max_chars,
                "greeting_style": config.greeting_style,
                "requires_citations": config.requires_citations
            }
            for pid, config in self.personalities.items()
        ]

# Test function
async def test_enhanced_service():
    """Test the enhanced service with multiple personalities"""
    service = EnhancedSimpleLLMService()
    
    if service.is_configured:
        print("✅ Enhanced service configured successfully!")
        print(f"Available personalities: {list(service.personalities.keys())}")
        
        # Test different personalities
        test_queries = [
            ("krishna", "What is dharma?"),
            ("buddha", "How can I find peace?"),
            ("jesus", "What is love?"),
            ("einstein", "What is curiosity?"),
            ("lincoln", "What makes a good leader?")
        ]
        
        for personality_id, query in test_queries:
            result = await service.generate_personality_response(query, personality_id)
            print(f"\n🎭 {result.metadata.get('personality_name', personality_id)} Response:")
            print(f"Source: {result.source}")
            print(f"Characters: {result.character_count}/{result.max_allowed}")
            print(f"Content: {result.content}")
            
    else:
        print("❌ Service not configured - check API key")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_service())
