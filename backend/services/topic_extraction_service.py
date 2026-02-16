"""
Topic Extraction Service for Vimarsh

Extracts key topics, themes, and emotional patterns from conversations
to support the hierarchical memory architecture.

Features:
- Topic extraction using Azure OpenAI
- Theme clustering and categorization
- Emotional arc tracking
- Key insight identification
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json
import re

# Azure OpenAI
try:
    from openai import AsyncAzureOpenAI
    from config.ai_models import AI_CONFIG
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class TopicExtractionService:
    """
    Service for extracting topics, themes, and patterns from conversations.
    """
    
    # Vimarsh domain categories
    DOMAIN_CATEGORIES = {
        "spiritual": ["dharma", "karma", "meditation", "enlightenment", "soul", "divine", "prayer", "faith"],
        "philosophical": ["ethics", "virtue", "wisdom", "truth", "existence", "meaning", "logic", "reasoning"],
        "leadership": ["governance", "strategy", "decision-making", "influence", "management", "delegation"],
        "scientific": ["physics", "mathematics", "nature", "discovery", "experiment", "theory", "innovation"],
        "literary": ["poetry", "art", "expression", "beauty", "creativity", "metaphor", "storytelling"],
        "psychological": ["mind", "consciousness", "emotion", "behavior", "trauma", "growth", "self-awareness"]
    }
    
    # Life concern categories
    LIFE_CONCERNS = [
        "career", "relationships", "family", "health", "finance", 
        "education", "purpose", "spirituality", "creativity", "loss",
        "transition", "self-improvement", "conflict", "anxiety", "motivation"
    ]
    
    def __init__(self):
        """Initialize the topic extraction service."""
        if AZURE_OPENAI_AVAILABLE and AI_CONFIG.azure_openai_chat_endpoint and AI_CONFIG.azure_openai_chat_api_key:
            self.client = AsyncAzureOpenAI(
                azure_endpoint=AI_CONFIG.azure_openai_chat_endpoint,
                api_key=AI_CONFIG.azure_openai_chat_api_key,
                api_version=AI_CONFIG.azure_openai_chat_api_version
            )
            self.deployment = AI_CONFIG.azure_openai_chat_deployment
            self.available = True
            logger.info("✅ Topic Extraction Service initialized with Azure OpenAI")
        else:
            self.client = None
            self.deployment = None
            self.available = False
            logger.warning("⚠️ Topic Extraction Service: Azure OpenAI not configured")
    
    async def _generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Azure OpenAI."""
        if not self.available or not self.client:
            return None
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing conversations and extracting structured insights. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Azure OpenAI generation failed: {e}")
            return None
    
    async def extract_conversation_topics(
        self,
        messages: List[Dict[str, Any]],
        personality_id: str
    ) -> Dict[str, Any]:
        """
        Extract topics and themes from a conversation.
        
        Args:
            messages: List of conversation messages with role and content
            personality_id: The personality in conversation
            
        Returns:
            Dict with topics, themes, life_concerns, and domain_relevance
        """
        if not self.available or not messages:
            return self._empty_extraction()
        
        try:
            # Format conversation for analysis
            conversation_text = self._format_conversation(messages)
            
            prompt = f"""Analyze this conversation between a user and {personality_id.replace('_', ' ').title()} for topic extraction.

Conversation:
{conversation_text}

Extract and return a JSON object with:
{{
    "main_topics": ["list of 3-5 main topics discussed"],
    "themes": ["recurring themes or patterns"],
    "life_concerns": ["primary life areas the user is exploring"],
    "emotional_journey": ["emotional states observed during conversation"],
    "key_questions": ["important questions the user asked"],
    "insights_shared": ["any wisdom or insights the personality shared"],
    "action_items": ["any commitments or actions mentioned"],
    "domain_relevance": {{"spiritual": 0.0, "philosophical": 0.0, "leadership": 0.0, "scientific": 0.0, "literary": 0.0, "psychological": 0.0}}
}}

For domain_relevance, score each from 0.0 to 1.0 based on how much the conversation relates to that domain.
Return ONLY valid JSON."""

            response_text = await self._generate_response(prompt)
            
            # Parse response
            result = self._parse_json_response(response_text)
            
            if result:
                logger.info(f"📊 Extracted {len(result.get('main_topics', []))} topics from conversation")
                return result
            
            return self._empty_extraction()
            
        except Exception as e:
            logger.error(f"❌ Topic extraction failed: {e}")
            return self._empty_extraction()
    
    async def extract_session_summary(
        self,
        messages: List[Dict[str, Any]],
        personality_id: str,
        session_duration_minutes: int = 0
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive session summary for episodic memory.
        
        Args:
            messages: Full conversation messages
            personality_id: The personality in conversation
            session_duration_minutes: How long the session lasted
            
        Returns:
            Dict with summary, key_insights, topics, emotional_arc, and reflection
        """
        if not self.available or not messages:
            return self._empty_summary()
        
        try:
            conversation_text = self._format_conversation(messages)
            
            prompt = f"""Create a session summary for this conversation between a user and {personality_id.replace('_', ' ').title()}.

Conversation ({session_duration_minutes} minutes):
{conversation_text}

Generate a JSON object with:
{{
    "summary": "A 2-3 sentence summary of what was discussed",
    "key_insights": ["3-5 key insights or teachings shared"],
    "main_topics": ["primary topics discussed"],
    "emotional_arc": {{
        "start": "emotional state at beginning",
        "middle": "emotional shift or pattern",
        "end": "emotional state at conclusion"
    }},
    "user_revelations": ["any personal information the user shared"],
    "questions_explored": ["main questions the user was exploring"],
    "guidance_given": ["key pieces of guidance offered"],
    "follow_up_themes": ["themes that could be explored in future sessions"],
    "reflection": "A brief reflection on the overall conversation quality and depth"
}}

Return ONLY valid JSON."""

            response_text = await self._generate_response(prompt)
            result = self._parse_json_response(response_text)
            
            if result:
                logger.info(f"📝 Generated session summary with {len(result.get('key_insights', []))} insights")
                return result
            
            return self._empty_summary()
            
        except Exception as e:
            logger.error(f"❌ Session summary generation failed: {e}")
            return self._empty_summary()
    
    async def detect_emotional_tone(
        self,
        message: str,
        context: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Detect the emotional tone of a message.
        
        Args:
            message: The message to analyze
            context: Optional conversation context
            
        Returns:
            Tuple of (emotion_label, confidence_score)
        """
        if not self.available:
            return ("neutral", 0.5)
        
        try:
            prompt = f"""Analyze the emotional tone of this message.
            
Message: "{message}"
{f'Context: {context}' if context else ''}

Respond with ONLY a JSON object:
{{
    "primary_emotion": "one of: curious, seeking, troubled, hopeful, grateful, peaceful, inspired, reflective, uncertain, determined, frustrated, joyful, sad, anxious, calm",
    "confidence": 0.0 to 1.0,
    "secondary_emotions": ["list of other emotions present"]
}}"""

            response_text = await self._generate_response(prompt)
            result = self._parse_json_response(response_text)
            
            if result:
                return (result.get("primary_emotion", "neutral"), result.get("confidence", 0.5))
            
            return ("neutral", 0.5)
            
        except Exception as e:
            logger.warning(f"⚠️ Emotional tone detection failed: {e}")
            return ("neutral", 0.5)
    
    async def identify_personal_revelations(
        self,
        message: str
    ) -> Dict[str, Any]:
        """
        Identify personal revelations in a user message for importance scoring.
        
        Args:
            message: The user's message
            
        Returns:
            Dict with revelation_detected, revelation_type, importance_boost
        """
        if not self.available:
            return {"revelation_detected": False, "importance_boost": 0.0}
        
        try:
            prompt = f"""Analyze if this message contains personal revelations.

Message: "{message}"

Return ONLY a JSON object:
{{
    "revelation_detected": true/false,
    "revelation_types": ["life_event", "emotional_struggle", "goal", "belief", "relationship", "health", "career", "family"],
    "sensitivity_level": "low", "medium", or "high",
    "importance_boost": 0.0 to 0.5 (how much this should boost memory importance)
}}"""

            response_text = await self._generate_response(prompt)
            result = self._parse_json_response(response_text)
            
            if result:
                return result
            
            return {"revelation_detected": False, "importance_boost": 0.0}
            
        except Exception as e:
            logger.warning(f"⚠️ Personal revelation detection failed: {e}")
            return {"revelation_detected": False, "importance_boost": 0.0}
    
    async def categorize_life_concerns(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Identify the primary life concerns from conversation history.
        
        Args:
            messages: Conversation messages
            
        Returns:
            List of life concern categories
        """
        if not self.available or not messages:
            return []
        
        try:
            # Extract user messages only
            user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
            combined_text = " ".join(user_messages)
            
            prompt = f"""Based on these user messages, identify the primary life concerns being explored.

User messages: "{combined_text[:2000]}"

Return ONLY a JSON array of the most relevant life concerns from this list:
{self.LIFE_CONCERNS}

Format: ["concern1", "concern2", "concern3"]
Maximum 5 concerns, ordered by relevance."""

            response_text = await self._generate_response(prompt)
            result = self._parse_json_response(response_text)
            
            if isinstance(result, list):
                # Validate against known categories
                valid_concerns = [c for c in result if c in self.LIFE_CONCERNS]
                return valid_concerns[:5]
            
            return []
            
        except Exception as e:
            logger.warning(f"⚠️ Life concern categorization failed: {e}")
            return []
    
    def calculate_domain_relevance(
        self,
        text: str,
        personality_id: str
    ) -> Dict[str, float]:
        """
        Calculate domain relevance scores based on keyword presence.
        
        This is a fast, non-LLM method for quick categorization.
        
        Args:
            text: The text to analyze
            personality_id: The personality in conversation
            
        Returns:
            Dict mapping domain names to relevance scores (0.0-1.0)
        """
        text_lower = text.lower()
        scores = {}
        
        for domain, keywords in self.DOMAIN_CATEGORIES.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            # Normalize by number of keywords
            scores[domain] = min(1.0, matches / (len(keywords) * 0.5))
        
        # Boost personality's primary domain
        personality_domain_map = {
            "krishna": "spiritual",
            "buddha": "spiritual",
            "jesus_christ": "spiritual",
            "rumi": "spiritual",
            "swami_vivekananda": "spiritual",
            "marcus_aurelius": "philosophical",
            "lao_tzu": "philosophical",
            "confucius": "philosophical",
            "aristotle": "philosophical",
            "plato": "philosophical",
            "socrates": "philosophical",
            "chanakya": "leadership",
            "abraham_lincoln": "leadership",
            "benjamin_franklin": "leadership",
            "george_washington": "leadership",
            "mahatma_gandhi": "leadership",
            "martin_luther_king_jr": "leadership",
            "albert_einstein": "scientific",
            "isaac_newton": "scientific",
            "nikola_tesla": "scientific",
            "archimedes": "scientific",
            "leonardo_da_vinci": "scientific",
            "rabindranath_tagore": "literary",
            "william_shakespeare": "literary",
            "sigmund_freud": "psychological"
        }
        
        primary_domain = personality_domain_map.get(personality_id)
        if primary_domain and primary_domain in scores:
            scores[primary_domain] = min(1.0, scores[primary_domain] + 0.3)
        
        return scores
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation messages for LLM analysis."""
        formatted = []
        for msg in messages[-20:]:  # Last 20 messages max
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "user":
                formatted.append(f"User: {content}")
            else:
                formatted.append(f"Personality: {content[:300]}...")  # Truncate long responses
        return "\n".join(formatted)
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        try:
            # Try direct JSON parse
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code blocks
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}',
            r'\[[\s\S]*\]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group(1) if '```' in pattern else match.group(0))
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _empty_extraction(self) -> Dict[str, Any]:
        """Return empty topic extraction result."""
        return {
            "main_topics": [],
            "themes": [],
            "life_concerns": [],
            "emotional_journey": [],
            "key_questions": [],
            "insights_shared": [],
            "action_items": [],
            "domain_relevance": {domain: 0.0 for domain in self.DOMAIN_CATEGORIES}
        }
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty session summary."""
        return {
            "summary": "",
            "key_insights": [],
            "main_topics": [],
            "emotional_arc": {"start": "", "middle": "", "end": ""},
            "user_revelations": [],
            "questions_explored": [],
            "guidance_given": [],
            "follow_up_themes": [],
            "reflection": ""
        }


# Singleton instance
_topic_extraction_service: Optional[TopicExtractionService] = None


def get_topic_extraction_service() -> TopicExtractionService:
    """Get or create the topic extraction service singleton."""
    global _topic_extraction_service
    if _topic_extraction_service is None:
        _topic_extraction_service = TopicExtractionService()
    return _topic_extraction_service
