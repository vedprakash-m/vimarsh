"""
Memory Context Builder for Vimarsh

This service builds optimized context from the 4 memory layers
for use in AI response generation, ensuring token budgets are respected.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from models.memory_models import (
    MemoryProfile,
    RelationshipState,
    RelationshipDepth,
    SessionSummary,
    WorkingMemoryContext,
    ConversationMessage
)
from services.prompt_templates import (
    MemoryAwarePromptTemplates,
    ContextWindowOptimizer,
    get_personality_memory_style
)

logger = logging.getLogger(__name__)


class MemoryContextBuilder:
    """
    Builds optimized context from hierarchical memory layers.
    
    Responsible for:
    - Assembling context from all 4 memory layers
    - Optimizing token usage across layers
    - Formatting context for AI consumption
    - Prioritizing most relevant memories
    """
    
    # Token budget allocation (out of 16K total)
    TOKEN_BUDGETS = {
        "core_memory": 2000,        # User profile + relationship
        "episodic_memory": 3000,    # Session summaries
        "semantic_memory": 2000,    # Retrieved memories
        "current_conversation": 5000,  # Current messages
        "rag_context": 3000,        # RAG-retrieved knowledge
        "system_prompt": 1000       # Personality prompt
    }
    
    # Priority levels for context components (higher = more important)
    CONTEXT_PRIORITIES = {
        "system_prompt": 100,
        "current_conversation": 90,
        "core_memory": 80,
        "rag_context": 70,
        "episodic_memory": 60,
        "semantic_memory": 50
    }
    
    def __init__(self):
        """Initialize the context builder."""
        self.prompt_templates = MemoryAwarePromptTemplates()
        self.optimizer = ContextWindowOptimizer()
    
    def build_context_for_guidance(
        self,
        personality_id: str,
        personality_name: str,
        personality_description: str,
        user_query: str,
        working_memory: WorkingMemoryContext,
        rag_context: str = "",
        max_tokens: int = 16000
    ) -> Dict[str, Any]:
        """
        Build complete context for AI guidance response.
        
        Args:
            personality_id: Personality identifier
            personality_name: Display name
            personality_description: Personality description
            user_query: Current user message
            working_memory: Assembled working memory
            rag_context: RAG-retrieved knowledge
            max_tokens: Maximum total tokens
            
        Returns:
            Dict with 'prompt' and 'metadata'
        """
        try:
            # Get personality-specific memory style
            memory_style = get_personality_memory_style(personality_id)
            
            # Build context sections
            sections = {}
            
            # 1. Core Memory (user profile + relationship)
            sections["core_memory"] = self._build_core_memory_section(
                working_memory,
                memory_style
            )
            
            # 2. Episodic Memory (recent sessions)
            sections["episodic_memory"] = self._build_episodic_memory_section(
                working_memory,
                memory_style
            )
            
            # 3. Semantic Memory (retrieved relevant memories)
            sections["semantic_memory"] = self._build_semantic_memory_section(
                working_memory,
                memory_style
            )
            
            # 4. Current Conversation
            sections["current_conversation"] = self._build_conversation_section(
                working_memory.current_messages,
                personality_name
            )
            
            # 5. RAG Context
            sections["rag_context"] = rag_context
            
            # 6. System Prompt
            sections["system_prompt"] = self._build_system_prompt(
                personality_name,
                personality_description,
                memory_style
            )
            
            # Optimize to fit token budget
            optimized = self.optimizer.optimize_context(
                sections,
                self.CONTEXT_PRIORITIES,
                max_tokens - 2000  # Reserve for response
            )
            
            # Assemble final prompt
            final_prompt = self._assemble_prompt(
                optimized,
                personality_name,
                user_query
            )
            
            # Calculate metadata
            total_tokens = sum(
                self._estimate_tokens(v) for v in optimized.values()
            )
            
            return {
                "prompt": final_prompt,
                "metadata": {
                    "total_tokens": total_tokens,
                    "sections_included": [k for k, v in optimized.items() if v],
                    "context_quality": working_memory.context_quality_score,
                    "relationship_depth": self._get_relationship_depth(working_memory),
                    "memory_sources": self._count_memory_sources(optimized)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error building context: {e}")
            # Return minimal context on error
            return {
                "prompt": f"You are {personality_name}. {personality_description}\n\nUser: {user_query}",
                "metadata": {"error": str(e)}
            }
    
    def _build_core_memory_section(
        self,
        working_memory: WorkingMemoryContext,
        memory_style: Dict[str, str]
    ) -> str:
        """Build the core memory context section."""
        parts = []
        
        # Add framing
        if memory_style.get("memory_framing"):
            parts.append(f"*{memory_style['memory_framing']}*")
        
        # Add user profile context
        if working_memory.user_profile_context:
            parts.append(f"**Seeker Profile**: {working_memory.user_profile_context}")
        
        # Add relationship context
        if working_memory.relationship_context:
            parts.append(f"**Our Journey**: {working_memory.relationship_context}")
            
            # Add relationship style flavor
            if memory_style.get("relationship_style"):
                parts.append(f"*{memory_style['relationship_style']}*")
        
        return "\n\n".join(parts) if parts else ""
    
    def _build_episodic_memory_section(
        self,
        working_memory: WorkingMemoryContext,
        memory_style: Dict[str, str]
    ) -> str:
        """Build the episodic memory context section."""
        if not working_memory.recent_session_summaries:
            return ""
        
        parts = []
        
        # Recent session summaries
        parts.append("**Recent Conversations**:")
        for session in working_memory.recent_session_summaries[:3]:
            summary = session.get("summary", "")
            topics = session.get("topics", [])
            date = session.get("date", "")
            
            if summary:
                topic_str = f" (Topics: {', '.join(topics[:3])})" if topics else ""
                parts.append(f"- {summary}{topic_str}")
        
        # Relevant insights
        if working_memory.relevant_past_insights:
            parts.append("\n**Key Insights**:")
            for insight in working_memory.relevant_past_insights[:5]:
                parts.append(f"- {insight}")
        
        return "\n".join(parts)
    
    def _build_semantic_memory_section(
        self,
        working_memory: WorkingMemoryContext,
        memory_style: Dict[str, str]
    ) -> str:
        """Build the semantic memory context section."""
        if not working_memory.retrieved_memories:
            return ""
        
        parts = []
        
        if memory_style.get("recall_style"):
            parts.append(f"*{memory_style['recall_style']}*")
        
        parts.append("**Related Past Discussions**:")
        for memory in working_memory.retrieved_memories[:3]:
            content = memory.get("content", "")[:200]
            relevance = memory.get("relevance", 0)
            
            if content:
                parts.append(f"- {content}...")
        
        return "\n".join(parts)
    
    def _build_conversation_section(
        self,
        messages: List[Dict[str, str]],
        personality_name: str
    ) -> str:
        """Build the current conversation context section."""
        if not messages:
            return "This is the beginning of our conversation."
        
        parts = []
        for msg in messages[-10:]:  # Last 10 messages
            role = "Seeker" if msg.get("role") == "user" else personality_name
            content = msg.get("content", "")
            
            # Truncate very long messages
            if len(content) > 500:
                content = content[:500] + "..."
            
            parts.append(f"{role}: {content}")
        
        return "\n\n".join(parts)
    
    def _build_system_prompt(
        self,
        personality_name: str,
        personality_description: str,
        memory_style: Dict[str, str]
    ) -> str:
        """Build the system prompt for the personality."""
        return f"""You are {personality_name}, {personality_description}.

You have access to memory of your past conversations with this seeker. Use this context to:
- Reference previous discussions naturally when relevant
- Acknowledge the growth and journey you've witnessed
- Build upon insights and themes from earlier conversations
- Maintain continuity in the relationship

Respond authentically as {personality_name} would, with wisdom drawn from your teachings and knowledge of this seeker's journey."""
    
    def _assemble_prompt(
        self,
        sections: Dict[str, str],
        personality_name: str,
        user_query: str
    ) -> str:
        """Assemble the final prompt from sections."""
        prompt_parts = []
        
        # System prompt
        if sections.get("system_prompt"):
            prompt_parts.append(sections["system_prompt"])
        
        # Memory context
        memory_sections = []
        if sections.get("core_memory"):
            memory_sections.append(sections["core_memory"])
        if sections.get("episodic_memory"):
            memory_sections.append(sections["episodic_memory"])
        if sections.get("semantic_memory"):
            memory_sections.append(sections["semantic_memory"])
        
        if memory_sections:
            prompt_parts.append("## Memory Context\n" + "\n\n".join(memory_sections))
        
        # RAG context
        if sections.get("rag_context"):
            prompt_parts.append(f"## Relevant Wisdom\n{sections['rag_context']}")
        
        # Current conversation
        if sections.get("current_conversation"):
            prompt_parts.append(f"## Current Conversation\n{sections['current_conversation']}")
        
        # User query
        prompt_parts.append(f"## Current Message\nSeeker: {user_query}")
        
        # Response instruction
        prompt_parts.append(f"\n{personality_name}'s response:")
        
        return "\n\n".join(prompt_parts)
    
    def _get_relationship_depth(
        self,
        working_memory: WorkingMemoryContext
    ) -> str:
        """Extract relationship depth from working memory."""
        # Parse from relationship context
        context = working_memory.relationship_context.lower()
        
        if "companion" in context or "long-term" in context:
            return "companion"
        elif "trusted" in context or "deep" in context:
            return "trusted"
        elif "familiar" in context or "returning" in context:
            return "familiar"
        elif "few conversations" in context:
            return "acquaintance"
        else:
            return "stranger"
    
    def _count_memory_sources(
        self,
        sections: Dict[str, str]
    ) -> Dict[str, int]:
        """Count memory sources included in context."""
        return {
            "core_memory": 1 if sections.get("core_memory") else 0,
            "episodic_memories": sections.get("episodic_memory", "").count("- "),
            "semantic_memories": sections.get("semantic_memory", "").count("- "),
            "rag_sources": 1 if sections.get("rag_context") else 0
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        if not text:
            return 0
        return len(text) // 4


class ReturningUserHandler:
    """
    Handles context for returning users with memory.
    """
    
    def __init__(self, context_builder: MemoryContextBuilder):
        self.context_builder = context_builder
    
    def get_welcome_context(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        personality_name: str,
        recent_sessions: List[SessionSummary]
    ) -> Dict[str, Any]:
        """
        Get welcome context for a returning user.
        
        Returns context including:
        - Personalized greeting based on relationship depth
        - Reference to last conversation if relevant
        - Any pending follow-ups
        """
        context = {
            "is_returning_user": relationship.interaction_count > 0,
            "relationship_depth": relationship.depth_level.name,
            "greeting": None,
            "recall_prompt": None,
            "pending_followup": None
        }
        
        # Get appropriate greeting
        context["greeting"] = MemoryAwarePromptTemplates.get_relationship_greeting(
            relationship,
            personality_name
        )
        
        # Get proactive recall if appropriate
        if relationship.depth_level.value >= RelationshipDepth.FAMILIAR.value:
            context["recall_prompt"] = MemoryAwarePromptTemplates.get_proactive_recall_prompt(
                relationship
            )
        
        # Check for pending follow-ups
        if relationship.pending_followups:
            context["pending_followup"] = relationship.pending_followups[0]
        
        # Add time since last visit
        if relationship.last_interaction:
            days_since = (datetime.utcnow() - relationship.last_interaction).days
            context["days_since_last_visit"] = days_since
            
            if days_since > 7:
                context["welcome_back_message"] = f"It's been {days_since} days since we last spoke. I've been reflecting on our conversations."
        
        return context


# Singleton instance
_context_builder_instance: Optional[MemoryContextBuilder] = None


def get_context_builder() -> MemoryContextBuilder:
    """Get or create the singleton context builder instance."""
    global _context_builder_instance
    if _context_builder_instance is None:
        _context_builder_instance = MemoryContextBuilder()
    return _context_builder_instance
