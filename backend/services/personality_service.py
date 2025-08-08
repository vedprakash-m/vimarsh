"""
Personality service for generating responses.
Enhanced with LLM integration for dynamic responses.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PersonalityService:
    """Service for generating personality-specific responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._response_templates = self._load_response_templates()
        self._llm_service = None
        self._initialize_llm_service()
    
    def _initialize_llm_service(self):
        """Initialize LLM service if available"""
        try:
            from services.llm_service import LLMService
            self._llm_service = LLMService()
            self.logger.info("✅ LLM service initialized successfully")
        except ImportError as e:
            self.logger.warning(f"⚠️ LLM service not available, using templates: {e}")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM service initialization failed, using templates: {e}")
    
    def _run_async_llm_call(self, query: str, personality_id: str):
        """Helper method to run async LLM call in a new event loop"""
        if not self._llm_service:
            return None
            
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                self._llm_service.generate_personality_response(
                    query=query,
                    personality_id=personality_id
                )
            )
        finally:
            loop.close()
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Load personality-specific response templates"""
        return {
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
    
    def generate_response(
        self, 
        query: str, 
        personality_id: str, 
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Generate a personality-specific response to a query.
        
        Args:
            query: User's question or input
            personality_id: ID of the personality to respond as
            language: Response language (currently only English supported)
            
        Returns:
            Dict with response content and metadata
        """
        try:
            self.logger.info(f"Generating {personality_id} response for query: {query[:50]}...")
            
            # Try LLM service first, fallback to templates
            if self._llm_service:
                try:
                    # Use helper method to handle async call
                    llm_response = self._run_async_llm_call(query, personality_id)
                    
                    if llm_response and hasattr(llm_response, 'content') and llm_response.content:
                        self.logger.info(f"✅ LLM service generated response for {personality_id}")
                        return {
                            "content": llm_response.content,
                            "metadata": {
                                "timestamp": datetime.now().isoformat(),
                                "personality_id": personality_id,
                                "query_length": len(query),
                                "response_length": len(llm_response.content),
                                "service_version": "llm_enhanced_v1.0",
                                "response_source": "llm_service",
                                "language": language,
                                "character_count": getattr(llm_response, 'character_count', 0),
                                "max_allowed": getattr(llm_response, 'max_allowed', 0)
                            }
                        }
                    else:
                        self.logger.warning(f"⚠️ LLM service returned empty response for {personality_id}, using template")
                        
                except Exception as llm_error:
                    self.logger.warning(f"⚠️ LLM service failed for {personality_id}: {llm_error}, using template")
            
            # Fallback to template response
            self.logger.info(f"📝 Using template response for {personality_id}")
            template_response = self._get_template_response(personality_id, query)
            return {
                "content": template_response,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "personality_id": personality_id,
                    "query_length": len(query),
                    "response_length": len(template_response),
                    "service_version": "template_v1.0",
                    "response_source": "template_fallback",
                    "language": language
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error generating response for {personality_id}: {str(e)}")
            fallback_msg = f"I apologize, but I'm having difficulty responding right now. Please try again."
            return {
                "content": fallback_msg,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "personality_id": personality_id,
                    "error": str(e),
                    "response_source": "error_fallback",
                    "service_version": "error_v1.0"
                }
            }
    
    def _get_template_response(self, personality_id: str, query: str) -> str:
        """Get template-based response for a personality"""
        template = self._response_templates.get(personality_id)
        if not template:
            # Fallback to krishna template
            template = self._response_templates["krishna"]
            self.logger.warning(f"No template found for {personality_id}, using Krishna fallback")
        
        return template
    
    def get_available_personalities(self) -> List[str]:
        """Get list of available personality IDs"""
        return list(self._response_templates.keys())
    
    def validate_personality(self, personality_id: str) -> bool:
        """Check if personality ID is valid"""
        return personality_id in self._response_templates
