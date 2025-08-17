"""
Conversation Memory Service for Multi-Personality Guidance

Handles conversation history storage, retrieval, and context management
for personalized guidance experiences.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Import proper conversation models
try:
    from models.conversation_models import (
        ConversationMessage, ConversationSession, MessageType, ConversationStatus,
        create_conversation_message, create_conversation_session
    )
    MODELS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Conversation models not available: {e}")
    MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Keep the local ConversationStatus enum for backward compatibility if models not available
if not MODELS_AVAILABLE:
    class ConversationStatus(Enum):
        """Status of a conversation"""
        ACTIVE = "active"
        PAUSED = "paused"
        COMPLETED = "completed"
        ARCHIVED = "archived"

@dataclass
class ConversationContext:
    """Context retrieved from conversation history"""
    conversation_id: str
    personality_id: str
    recent_messages: List[ConversationMessage]
    user_patterns: Dict[str, Any]
    session_duration: float
    total_interactions: int
    last_topics: List[str]
    personality_preferences: Dict[str, Any]

class ConversationMemoryService:
    """Service for managing conversation memory and context"""
    
    def __init__(self, database_service=None):
        """Initialize the conversation memory service"""
        # Import Phase 2 database service
        try:
            from services.phase2_database_service import phase2_db_service
            self.database_service = phase2_db_service
            logger.info("✅ Using Phase 2 database service for conversation memory")
        except ImportError:
            self.database_service = database_service
            logger.warning("🔶 Phase 2 database service not available, using provided service")
        
        self.session_cache = {}  # In-memory session cache
        self.context_window_size = 10  # Number of recent messages to consider
        self.max_session_duration = timedelta(hours=4)  # Auto-archive after 4 hours
        
        logger.info("✅ Conversation Memory Service initialized")
    
    async def start_conversation(
        self, 
        user_id: str, 
        personality_id: str, 
        session_id: Optional[str] = None
    ) -> str:
        """Start a new conversation or resume existing one"""
        
        # Generate conversation ID
        conversation_id = f"conv_{user_id}_{personality_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check for recent active conversation
        if session_id:
            existing_conv = await self._get_active_conversation(user_id, personality_id, session_id)
            if existing_conv:
                conversation_id = existing_conv
        
        # Initialize session in cache
        self.session_cache[conversation_id] = {
            "user_id": user_id,
            "personality_id": personality_id,
            "session_id": session_id,
            "started_at": datetime.now(),
            "status": ConversationStatus.ACTIVE,
            "message_count": 0,
            "topics": []
        }
        
        logger.info(f"🧠 Started conversation {conversation_id} for user {user_id} with {personality_id}")
        return conversation_id
    
    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        personality_id: str,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """Add a message to the conversation"""
        
        message_id = f"msg_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Convert message_type to MessageType enum if available
        if MODELS_AVAILABLE:
            if message_type == "user_query":
                msg_type = MessageType.USER_QUERY
            elif message_type == "personality_response":
                msg_type = MessageType.PERSONALITY_RESPONSE
            else:
                msg_type = MessageType.USER_QUERY  # Default fallback
                
            message = ConversationMessage(
                id=message_id,
                session_id=conversation_id,  # Use session_id for models compatibility
                user_id=user_id,
                personality_id=personality_id,
                message_type=msg_type,
                content=content,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
        else:
            # Fallback for when models not available - create simple dict
            message = {
                "id": message_id,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "personality_id": personality_id,
                "message_type": message_type,
                "content": content,
                "timestamp": datetime.now(),
                "metadata": metadata or {}
            }
        
        # Update session cache
        if conversation_id in self.session_cache:
            self.session_cache[conversation_id]["message_count"] += 1
            self.session_cache[conversation_id]["last_activity"] = datetime.now()
            
            # Extract topics from user queries
            if message_type == "user_query":
                topics = self._extract_topics(content)
                self.session_cache[conversation_id]["topics"].extend(topics)
        
        # Store in database if available
        if self.database_service:
            await self._store_message(message)
        
        logger.info(f"💬 Added {message_type} to conversation {conversation_id}")
        return message
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        include_system_messages: bool = False
    ) -> ConversationContext:
        """Get conversation context for enhanced responses"""
        
        # Get recent messages
        recent_messages = await self._get_recent_messages(
            conversation_id, 
            limit=self.context_window_size
        )
        
        # Get session info from cache
        session_info = self.session_cache.get(conversation_id, {})
        
        # Calculate session duration
        started_at = session_info.get("started_at", datetime.now())
        session_duration = (datetime.now() - started_at).total_seconds()
        
        # Extract user patterns
        user_patterns = await self._analyze_user_patterns(recent_messages)
        
        # Get personality preferences
        personality_id = session_info.get("personality_id", "krishna")
        personality_preferences = await self._get_personality_preferences(
            conversation_id, 
            personality_id
        )
        
        # Extract recent topics
        last_topics = list(set(session_info.get("topics", [])))[-5:]  # Last 5 unique topics
        
        context = ConversationContext(
            conversation_id=conversation_id,
            personality_id=personality_id,
            recent_messages=recent_messages,
            user_patterns=user_patterns,
            session_duration=session_duration,
            total_interactions=len(recent_messages),
            last_topics=last_topics,
            personality_preferences=personality_preferences
        )
        
        logger.info(f"🔍 Retrieved context for {conversation_id}: {len(recent_messages)} messages, {len(last_topics)} topics")
        return context
    
    async def get_contextual_prompt_enhancement(
        self,
        conversation_id: str,
        current_query: str,
        personality_id: str
    ) -> str:
        """Generate context-aware prompt enhancement"""
        
        context = await self.get_conversation_context(conversation_id)
        
        # Build context summary
        context_summary = []
        
        # Add recent topics
        if context.last_topics:
            topics_str = ", ".join(context.last_topics[-3:])  # Last 3 topics
            context_summary.append(f"Recent conversation topics: {topics_str}")
        
        # Add user patterns
        if context.user_patterns.get("preferred_style"):
            style = context.user_patterns["preferred_style"]
            context_summary.append(f"User prefers {style} responses")
        
        # Add conversation continuity
        if len(context.recent_messages) >= 2:
            last_response = [msg for msg in context.recent_messages if msg.message_type == "personality_response"]
            if last_response:
                last_msg = last_response[0].content[:100]
                context_summary.append(f"Building on previous guidance: {last_msg}...")
        
        # Create enhanced prompt
        if context_summary:
            enhancement = f"""
CONVERSATION CONTEXT:
{chr(10).join('- ' + item for item in context_summary)}

Continue this spiritual conversation naturally, acknowledging the context while addressing the new query.

CURRENT QUERY: {current_query}"""
            return enhancement
        
        return current_query
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old inactive sessions"""
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        for conv_id, session_info in list(self.session_cache.items()):
            last_activity = session_info.get("last_activity", session_info.get("started_at"))
            
            if last_activity and last_activity < cutoff_time:
                # Archive the conversation
                await self._archive_conversation(conv_id)
                del self.session_cache[conv_id]
                cleaned_count += 1
        
        logger.info(f"🧹 Cleaned up {cleaned_count} old conversations")
        return cleaned_count
    
    # Private helper methods
    
    async def _get_active_conversation(
        self, 
        user_id: str, 
        personality_id: str, 
        session_id: str
    ) -> Optional[str]:
        """Check for existing active conversation"""
        
        for conv_id, session_info in self.session_cache.items():
            if (session_info.get("user_id") == user_id and 
                session_info.get("personality_id") == personality_id and
                session_info.get("session_id") == session_id and
                session_info.get("status") == ConversationStatus.ACTIVE):
                
                # Check if session is still fresh (within 4 hours)
                started_at = session_info.get("started_at", datetime.now())
                if datetime.now() - started_at < self.max_session_duration:
                    return conv_id
        
        return None
    
    async def _store_message(self, message: ConversationMessage):
        """Store message in database"""
        if not self.database_service:
            return
        
        try:
            # Store using Phase 2 database service
            success = await self.database_service.store_conversation_message(message)
            if success:
                logger.info(f"💾 Message stored in database: {message.id}")
            else:
                logger.warning(f"⚠️ Failed to store message in database: {message.id}")
        except Exception as e:
            logger.error(f"❌ Failed to store message: {e}")
    
    async def _get_recent_messages(
        self, 
        conversation_id: str, 
        limit: int = 10
    ) -> List[ConversationMessage]:
        """Get recent messages from conversation"""
        
        if not self.database_service:
            return []
        
        try:
            # Extract user_id and personality_id from conversation_id
            # conversation_id format: conv_{user_id}_{personality_id}_{YYYYMMDD_HHMMSS}
            # Note: user_id might contain underscores, and timestamp has 2 parts separated by _
            parts = conversation_id.split('_')
            if len(parts) >= 5 and conversation_id.startswith('conv_'):
                # Last 2 parts are timestamp: YYYYMMDD_HHMMSS
                # Second-to-last-to-last part is personality_id
                # Everything between 'conv' and personality is user_id
                personality_id = parts[-3]  # chanakya
                user_id = '_'.join(parts[1:-3])  # test_user_001
                
                # Get recent messages from database
                messages = await self.database_service.get_recent_messages(
                    user_id, personality_id, limit
                )
                logger.info(f"📨 Retrieved {len(messages)} recent messages from database for {user_id}/{personality_id}")
                return messages
            else:
                logger.warning(f"⚠️ Invalid conversation_id format: {conversation_id} (expected conv_{{user}}_{{personality}}_{{timestamp}})")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to retrieve recent messages: {e}")
            return []
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from user message"""
        
        # Simple keyword extraction
        spiritual_keywords = {
            "dharma", "karma", "meditation", "peace", "love", "wisdom", 
            "suffering", "enlightenment", "prayer", "faith", "hope",
            "purpose", "meaning", "soul", "spirit", "divine", "god"
        }
        
        content_lower = content.lower()
        found_topics = []
        
        for keyword in spiritual_keywords:
            if keyword in content_lower:
                found_topics.append(keyword)
        
        return found_topics[:3]  # Max 3 topics per message
    
    async def _analyze_user_patterns(self, messages: List[ConversationMessage]) -> Dict[str, Any]:
        """Analyze user communication patterns"""
        
        patterns = {
            "message_length": "medium",
            "preferred_style": "balanced",
            "question_types": [],
            "engagement_level": "medium"
        }
        
        if not messages:
            return patterns
        
        # Analyze message lengths
        user_messages = [msg for msg in messages if msg.message_type == "user_query"]
        if user_messages:
            avg_length = sum(len(msg.content) for msg in user_messages) / len(user_messages)
            
            if avg_length < 50:
                patterns["message_length"] = "short"
                patterns["preferred_style"] = "concise"
            elif avg_length > 200:
                patterns["message_length"] = "long"
                patterns["preferred_style"] = "detailed"
        
        return patterns
    
    async def _get_personality_preferences(
        self, 
        conversation_id: str, 
        personality_id: str
    ) -> Dict[str, Any]:
        """Get personality-specific preferences for this conversation"""
        
        return {
            "response_style": "authentic",
            "citation_preference": "moderate",
            "interaction_tone": "warm"
        }
    
    async def _archive_conversation(self, conversation_id: str):
        """Archive old conversation"""
        
        if conversation_id in self.session_cache:
            self.session_cache[conversation_id]["status"] = ConversationStatus.ARCHIVED
            logger.info(f"📦 Archived conversation {conversation_id}")

# Global instance
conversation_memory_service = ConversationMemoryService()

# Test function
async def test_conversation_memory():
    """Test the conversation memory service"""
    
    print("🧪 Testing Conversation Memory Service")
    print("=" * 50)
    
    service = ConversationMemoryService()
    
    # Test conversation creation
    conv_id = await service.start_conversation("user123", "krishna", "session456")
    print(f"✅ Started conversation: {conv_id}")
    
    # Test message addition
    await service.add_message(
        conv_id, "user123", "krishna", "user_query", 
        "What is the meaning of dharma?",
        {"query_type": "philosophical"}
    )
    
    await service.add_message(
        conv_id, "user123", "krishna", "personality_response",
        "Beloved devotee, dharma is your righteous duty and the path of righteousness...",
        {"response_source": "enhanced_llm", "character_count": 85}
    )
    
    # Test context retrieval
    context = await service.get_conversation_context(conv_id)
    print(f"✅ Context retrieved: {context.total_interactions} interactions")
    print(f"   Topics: {context.last_topics}")
    print(f"   Session duration: {context.session_duration:.1f}s")
    
    # Test prompt enhancement
    enhanced_prompt = await service.get_contextual_prompt_enhancement(
        conv_id, "Tell me more about karma", "krishna"
    )
    print(f"✅ Enhanced prompt generated: {len(enhanced_prompt)} chars")
    
    print("🎉 Conversation Memory Service test completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_conversation_memory())
