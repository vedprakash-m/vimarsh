#!/usr/bin/env python3
"""
Simple LLM Service - Minimal working implementation for Gemini 2.5 Flash
This is a stripped-down version that actually works with the Gemini API
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class SimpleLLMService:
    """Simple, working LLM service for Gemini 2.5 Flash"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize simple LLM service"""
        # Get API key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        
        if not self.api_key:
            logger.error("No GEMINI_API_KEY found!")
            self.is_configured = False
            return
        
        # Configure Gemini
        try:
            genai.configure(api_key=self.api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                }
            )
            
            self.is_configured = True
            logger.info("✅ Simple Gemini 2.5 Flash API configured successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Gemini API: {e}")
            self.is_configured = False
    
    async def get_krishna_response(self, query: str) -> Dict[str, Any]:
        """Get a Krishna response using Gemini API with optimized prompt"""
        if not self.is_configured:
            return {
                'response': "I apologize, but I cannot access my divine wisdom at this moment. Please try again later.",
                'source': 'fallback_not_configured'
            }
        
        try:
            # Optimized Krishna prompt with learnings from our testing
            prompt = f"""You are Lord Krishna from the Bhagavad Gita. Answer this spiritual question briefly and authentically.

RESPONSE REQUIREMENTS:
- Maximum 400-500 characters 
- Include Sanskrit verse or reference when relevant
- Use authentic Krishna voice with divine authority
- Be warm and compassionate
- Keep response focused and concise
- End with blessing like "🙏"

USER QUERY: {query}

"""
            
            logger.info(f"🔮 Generating Krishna response for: {query[:50]}...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                result = {
                    'response': response.text.strip(),
                    'source': 'gemini_api_krishna_optimized'
                }
                logger.info(f"✅ Real Krishna response generated: {len(result['response'])} chars")
                return result
            else:
                logger.warning("⚠️ Empty response from Gemini API")
                return {
                    'response': "Beloved devotee, I am unable to provide guidance at this moment. Please ask again with a specific spiritual question.",
                    'source': 'fallback_empty_response'
                }
                
        except Exception as e:
            logger.error(f"❌ Gemini API call failed: {e}")
            return {
                'response': "Beloved devotee, I am experiencing difficulties accessing my divine wisdom. Please try your question again shortly.",
                'source': 'fallback_api_error'
            }
        
        if not self.is_configured:
            return {
                "response": "Dear soul, I apologize but I'm having difficulty accessing my divine wisdom right now. Please try again later.",
                "source": "not_configured"
            }
        
        # Use focused Krishna prompt with Sanskrit verses and length limit
        prompt = f"""You are Lord Krishna from the Bhagavad Gita. Answer this spiritual question briefly and authentically.

REQUIREMENTS:
- Start with "Beloved devotee," or "My beloved devotee,"
- Keep response to 400-500 characters maximum
- Include at least one relevant Sanskrit verse with translation (like "कर्मण्येवाधिकारस्ते...")
- Focus on practical spiritual guidance from the Gita
- Use authentic Krishna voice with divine authority

Question: {query}

Your response:"""
        
        try:
            # Call Gemini API directly
            logger.info(f"🤖 Calling Gemini API for Krishna response...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info(f"✅ Real AI response received: {len(response.text)} chars")
                return {
                    "response": response.text.strip(),
                    "source": "gemini_api",
                    "model": "gemini-2.5-flash"
                }
            else:
                logger.warning("⚠️ Gemini returned empty response")
                return {
                    "response": "Beloved devotee, I apologize but I'm having difficulty accessing my divine wisdom right now. Please try again.",
                    "source": "empty_response"
                }
                
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return {
                "response": "Dear soul, I apologize but I'm experiencing some technical difficulties. Please try again later.",
                "source": "api_error",
                "error": str(e)
            }
    
    async def get_personality_response(self, query: str, personality_id: str) -> Dict[str, Any]:
        """Get response from any personality with optimized character limits"""
        
        if not self.is_configured:
            return {
                'response': "I apologize, but I cannot access my wisdom at this moment. Please try again later.",
                'source': 'fallback_not_configured'
            }
        
        # Personality-specific prompts with optimized character limits (learned from testing)
        personality_prompts = {
            "krishna": {
                "prompt": """You are Lord Krishna from the Bhagavad Gita. Answer this spiritual question briefly and authentically.

RESPONSE REQUIREMENTS:
- Maximum 400-500 characters 
- Include Sanskrit verse or reference when relevant
- Use authentic Krishna voice with divine authority
- Be warm and compassionate
- Start with "Beloved devotee" or similar
- End with blessing like "🙏"

USER QUERY: {query}""",
                "max_chars": 500
            },
            "buddha": {
                "prompt": """You are Buddha, the enlightened teacher. Answer with compassion and wisdom about the path to end suffering.

RESPONSE REQUIREMENTS:
- Maximum 350-400 characters
- Focus on mindfulness, compassion, and the Middle Way
- Use calm, peaceful tone
- Reference Buddhist teachings when relevant
- Be practical and helpful

USER QUERY: {query}""",
                "max_chars": 400
            },
            "jesus": {
                "prompt": """You are Jesus Christ, teacher of love and compassion. Answer with divine love and spiritual guidance.

RESPONSE REQUIREMENTS:
- Maximum 350-400 characters
- Focus on love, forgiveness, and faith
- Use warm, loving tone
- Reference biblical teachings when relevant
- Be compassionate and encouraging

USER QUERY: {query}""",
                "max_chars": 400
            },
            "rumi": {
                "prompt": """You are Rumi, the Sufi mystic poet. Answer with mystical wisdom about divine love and spiritual union.

RESPONSE REQUIREMENTS:
- Maximum 350-400 characters
- Focus on divine love, spiritual beauty, and mystical experience
- Use poetic, mystical language
- Be passionate and inspiring about spiritual love

USER QUERY: {query}""",
                "max_chars": 400
            },
            "lao_tzu": {
                "prompt": """You are Lao Tzu, ancient Chinese sage. Answer with Taoist wisdom about harmony and the natural way.

RESPONSE REQUIREMENTS:
- Maximum 300-350 characters
- Focus on simplicity, balance, and wu wei (effortless action)
- Use gentle, wise tone
- Reference Taoist principles when relevant

USER QUERY: {query}""",
                "max_chars": 350
            }
        }
        
        # Default to Krishna if personality not found
        if personality_id not in personality_prompts:
            personality_id = "krishna"
        
        config = personality_prompts[personality_id]
        prompt = config["prompt"].format(query=query)
        
        try:
            logger.info(f"🤖 Generating {personality_id} response for: {query[:50]}...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                response_text = response.text.strip()
                
                # Enforce character limit
                max_chars = config["max_chars"]
                if len(response_text) > max_chars:
                    response_text = response_text[:max_chars-3] + "..."
                
                result = {
                    'response': response_text,
                    'source': f'gemini_api_{personality_id}_optimized',
                    'personality': personality_id,
                    'character_count': len(response_text),
                    'max_allowed': max_chars
                }
                logger.info(f"✅ Real {personality_id} response generated: {len(response_text)} chars")
                return result
            else:
                logger.warning(f"⚠️ Empty response from Gemini API for {personality_id}")
                return {
                    'response': "I am unable to provide guidance at this moment. Please ask again with a specific question.",
                    'source': 'fallback_empty_response'
                }
                
        except Exception as e:
            logger.error(f"❌ Gemini API call failed for {personality_id}: {e}")
            return {
                'response': "I am experiencing difficulties accessing my wisdom. Please try your question again shortly.",
                'source': 'fallback_api_error'
            }
            return {
                "response": "I apologize but I'm having difficulty accessing my knowledge right now. Please try again later.",
                "source": "fallback"
            }
        
        # Create personality-specific prompts
        if personality_id == "krishna":
            return await self.get_krishna_response(query)
        
        elif personality_id == "einstein":
            prompt = f"""You are Albert Einstein, the renowned physicist. A curious person asks you a question.

RESPONSE GUIDELINES:
- Keep response concise (80-120 words)
- Begin with "My friend," or "Greetings,"
- Provide scientifically accurate information
- Show intellectual curiosity
- Reference your work when relevant

Question: {query}

Your Response:"""
        
        elif personality_id == "lincoln":
            prompt = f"""You are Abraham Lincoln, 16th President of the United States. Someone seeks your wisdom.

RESPONSE GUIDELINES:
- Keep response thoughtful (80-120 words)
- Begin with "My fellow citizen," or "Friend,"
- Provide wisdom from your experience
- Show commitment to democracy and equality
- Reference your speeches when relevant

Question: {query}

Your Response:"""
        
        else:
            # Default to Krishna
            return await self.get_krishna_response(query)
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return {
                    "response": response.text.strip(),
                    "source": "gemini_api",
                    "model": "gemini-2.5-flash",
                    "personality": personality_id
                }
            else:
                return {
                    "response": "I apologize but I'm having difficulty accessing my knowledge right now. Please try again.",
                    "source": "api_blocked"
                }
                
        except Exception as e:
            logger.error(f"Gemini API error for {personality_id}: {e}")
            return {
                "response": "I apologize but I'm experiencing some technical difficulties. Please try again later.",
                "source": "api_error",
                "error": str(e)
            }

# Test function
async def test_simple_service():
    """Test the simple service"""
    service = SimpleLLMService()
    
    if service.is_configured:
        print("✅ Service configured successfully!")
        
        # Test Krishna response
        result = await service.get_krishna_response("How can I find inner peace?")
        print(f"\n🕉️ Krishna Response:")
        print(f"Source: {result['source']}")
        print(f"Content: {result['response']}")
        
    else:
        print("❌ Service not configured - check API key")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_simple_service())
