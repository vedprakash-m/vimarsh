"""
Memory-Aware Prompt Templates for Vimarsh

These templates integrate hierarchical memory context into AI prompts
for more personalized and contextual conversations.
"""

from typing import Optional, List, Dict, Any
from models.memory_models import (
    WorkingMemoryContext,
    RelationshipState,
    RelationshipDepth,
    MemoryProfile
)


class MemoryAwarePromptTemplates:
    """Templates for memory-enhanced personality prompts."""
    
    # Base personality prompt structure
    BASE_TEMPLATE = """You are {personality_name}, {personality_description}.

{memory_context}

{personality_traits}

Current conversation:
{conversation_history}

User's message: {user_query}

Respond as {personality_name} would, incorporating your knowledge of this seeker and your ongoing relationship."""

    # Memory context section template
    MEMORY_CONTEXT_TEMPLATE = """## Memory Context
{user_context}
{relationship_context}
{episodic_context}
{semantic_context}"""

    # Relationship-aware greeting templates by depth level
    GREETING_TEMPLATES = {
        RelationshipDepth.STRANGER: [
            "Welcome, seeker. What brings you to seek guidance today?",
            "Greetings. I sense you come seeking wisdom. How may I assist you?",
            "Peace be upon you. Share what weighs on your mind.",
        ],
        RelationshipDepth.ACQUAINTANCE: [
            "It is good to see you return, seeker. What guidance do you seek today?",
            "Welcome back. I trust you've had time to reflect on our last conversation.",
            "Ah, you return. Tell me, what insights have emerged since we last spoke?",
        ],
        RelationshipDepth.FAMILIAR: [
            "My friend, it warms me to see you again. How fares your journey?",
            "Welcome, dear seeker. I've been thinking about our conversations. What brings you today?",
            "Ah, a familiar face! I hope you've found some peace since our last discussion about {last_topic}.",
        ],
        RelationshipDepth.TRUSTED: [
            "Dear friend, I'm glad you've come. Let us continue our journey together.",
            "I've been reflecting on your path, my friend. How can I support you today?",
            "Welcome back, trusted seeker. Your growth has been beautiful to witness. What shall we explore today?",
        ],
        RelationshipDepth.COMPANION: [
            "My dear companion on this path, it brings me joy to walk beside you once more.",
            "Beloved seeker, our journey together continues. What wisdom shall we uncover today?",
            "My friend, your dedication to growth inspires me. Let us delve deeper.",
        ]
    }

    # Proactive recall templates
    PROACTIVE_RECALL_TEMPLATES = [
        "I recall you mentioned {topic} in our previous conversation. Has there been any development?",
        "When we last spoke, you were contemplating {topic}. I've been curious about your progress.",
        "Your earlier question about {topic} has stayed with me. Perhaps today we can explore it further.",
        "I remember your concern about {topic}. Shall we revisit that, or is there something new on your mind?",
    ]

    # Milestone celebration templates
    MILESTONE_TEMPLATES = {
        "first_deep_conversation": "I sense we've moved beyond surface conversation today. Thank you for trusting me with your deeper thoughts.",
        "tenth_interaction": "We've had many meaningful exchanges now. Your commitment to growth is admirable.",
        "breakthrough_moment": "What you've shared today feels like a significant realization. I'm honored to witness this moment.",
        "consistent_practice": "Your consistency in seeking wisdom shows true dedication. The path rewards such devotion.",
    }

    @classmethod
    def build_memory_context_section(
        cls,
        working_memory: WorkingMemoryContext,
        include_semantic: bool = True
    ) -> str:
        """
        Build the memory context section for the prompt.
        
        Args:
            working_memory: The assembled working memory context
            include_semantic: Whether to include semantic memory results
            
        Returns:
            Formatted memory context string
        """
        sections = []
        
        # User context
        if working_memory.user_profile_context:
            sections.append(f"**About this seeker**: {working_memory.user_profile_context}")
        
        # Relationship context
        if working_memory.relationship_context:
            sections.append(f"**Our relationship**: {working_memory.relationship_context}")
        
        # Episodic context (recent sessions)
        if working_memory.recent_session_summaries:
            recent = working_memory.recent_session_summaries[:2]
            summaries = "\n".join([
                f"- {s.get('summary', 'No summary')}" for s in recent
            ])
            sections.append(f"**Recent conversations**:\n{summaries}")
        
        # Relevant insights
        if working_memory.relevant_past_insights:
            insights = "\n".join([f"- {i}" for i in working_memory.relevant_past_insights[:3]])
            sections.append(f"**Key insights from our history**:\n{insights}")
        
        # Semantic memory (relevant past discussions)
        if include_semantic and working_memory.retrieved_memories:
            memories = working_memory.retrieved_memories[:2]
            memory_text = "\n".join([
                f"- Previously discussed: {m.get('content', '')[:150]}..."
                for m in memories
            ])
            sections.append(f"**Related past discussions**:\n{memory_text}")
        
        return "\n\n".join(sections) if sections else ""

    @classmethod
    def build_full_prompt(
        cls,
        personality_name: str,
        personality_description: str,
        personality_traits: str,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        working_memory: Optional[WorkingMemoryContext] = None,
        rag_context: str = ""
    ) -> str:
        """
        Build a complete memory-aware prompt.
        
        Args:
            personality_name: Name of the personality
            personality_description: Brief description
            personality_traits: Detailed personality traits
            user_query: Current user message
            conversation_history: Recent conversation messages
            working_memory: Assembled working memory context
            rag_context: RAG-retrieved knowledge context
            
        Returns:
            Complete formatted prompt
        """
        # Build memory context if available
        memory_section = ""
        if working_memory:
            memory_section = cls.build_memory_context_section(working_memory)
        
        # Format conversation history
        history_text = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history[-10:]:  # Last 10 messages
                role = "Seeker" if msg.get("role") == "user" else personality_name
                content = msg.get("content", "")[:500]
                history_lines.append(f"{role}: {content}")
            history_text = "\n".join(history_lines)
        
        # Build full prompt
        prompt = cls.BASE_TEMPLATE.format(
            personality_name=personality_name,
            personality_description=personality_description,
            memory_context=memory_section,
            personality_traits=personality_traits,
            conversation_history=history_text or "This is the beginning of our conversation.",
            user_query=user_query
        )
        
        # Add RAG context if available
        if rag_context:
            prompt = f"{prompt}\n\n## Relevant Wisdom from Sources:\n{rag_context}"
        
        return prompt

    @classmethod
    def get_relationship_greeting(
        cls,
        relationship: RelationshipState,
        personality_name: str
    ) -> str:
        """
        Get an appropriate greeting based on relationship depth.
        
        Args:
            relationship: The RelationshipState object
            personality_name: Name of the personality
            
        Returns:
            Personalized greeting string
        """
        import random
        
        templates = cls.GREETING_TEMPLATES.get(
            relationship.depth_level,
            cls.GREETING_TEMPLATES[RelationshipDepth.STRANGER]
        )
        
        greeting = random.choice(templates)
        
        # Personalize with last topic if available
        if "{last_topic}" in greeting and relationship.last_topic:
            greeting = greeting.format(last_topic=relationship.last_topic)
        elif "{last_topic}" in greeting:
            # Remove the topic reference if no last topic
            greeting = greeting.replace(" about {last_topic}", "")
        
        return greeting

    @classmethod
    def get_proactive_recall_prompt(
        cls,
        relationship: RelationshipState
    ) -> Optional[str]:
        """
        Get a proactive recall prompt if there's relevant context.
        
        Args:
            relationship: The RelationshipState object
            
        Returns:
            Optional proactive recall prompt
        """
        import random
        
        # Check if there's something to recall
        if relationship.pending_followups:
            followup = relationship.pending_followups[0]
            topic = followup.get("topic", "")
            if topic:
                template = random.choice(cls.PROACTIVE_RECALL_TEMPLATES)
                return template.format(topic=topic)
        
        # Or use recent topics
        if relationship.recent_topics:
            topic = relationship.recent_topics[0]
            template = random.choice(cls.PROACTIVE_RECALL_TEMPLATES)
            return template.format(topic=topic)
        
        return None

    @classmethod
    def get_milestone_acknowledgment(
        cls,
        milestone_type: str
    ) -> Optional[str]:
        """
        Get acknowledgment text for a milestone.
        
        Args:
            milestone_type: Type of milestone achieved
            
        Returns:
            Milestone acknowledgment text
        """
        return cls.MILESTONE_TEMPLATES.get(milestone_type)


class ContextWindowOptimizer:
    """
    Optimizes content to fit within token budgets.
    """
    
    # Default token limits
    DEFAULT_MAX_TOKENS = 16000
    RESERVED_FOR_RESPONSE = 4000
    
    @classmethod
    def optimize_context(
        cls,
        components: Dict[str, str],
        priorities: Dict[str, int],
        max_tokens: int = None
    ) -> Dict[str, str]:
        """
        Optimize context components to fit within token limit.
        
        Args:
            components: Dict of component_name -> content
            priorities: Dict of component_name -> priority (higher = more important)
            max_tokens: Maximum token budget
            
        Returns:
            Optimized components dict
        """
        max_tokens = max_tokens or (cls.DEFAULT_MAX_TOKENS - cls.RESERVED_FOR_RESPONSE)
        
        # Estimate tokens for each component
        token_estimates = {
            name: cls._estimate_tokens(content)
            for name, content in components.items()
        }
        
        total_tokens = sum(token_estimates.values())
        
        # If within budget, return as-is
        if total_tokens <= max_tokens:
            return components
        
        # Need to trim - start with lowest priority
        sorted_components = sorted(
            components.keys(),
            key=lambda x: priorities.get(x, 0)
        )
        
        optimized = components.copy()
        current_tokens = total_tokens
        
        for component in sorted_components:
            if current_tokens <= max_tokens:
                break
            
            # Calculate how much to trim
            excess = current_tokens - max_tokens
            component_tokens = token_estimates[component]
            
            if component_tokens <= excess:
                # Remove entirely
                optimized[component] = ""
                current_tokens -= component_tokens
            else:
                # Truncate
                target_tokens = component_tokens - excess
                optimized[component] = cls._truncate_to_tokens(
                    optimized[component],
                    target_tokens
                )
                current_tokens = max_tokens
        
        return optimized
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text) // 4
    
    @classmethod
    def _truncate_to_tokens(cls, text: str, target_tokens: int) -> str:
        """Truncate text to approximate token count."""
        target_chars = target_tokens * 4
        if len(text) <= target_chars:
            return text
        
        # Truncate and add ellipsis
        truncated = text[:target_chars - 20]
        
        # Try to end at sentence boundary
        last_period = truncated.rfind(".")
        if last_period > target_chars * 0.8:
            truncated = truncated[:last_period + 1]
        
        return truncated + " [...]"


# Personality-specific prompt enhancements
PERSONALITY_MEMORY_STYLES = {
    "krishna": {
        "memory_framing": "I see your journey through the lens of dharma",
        "recall_style": "As the Gita teaches, your past questions reveal your path",
        "relationship_style": "Our bond grows like the connection between teacher and devoted student"
    },
    "buddha": {
        "memory_framing": "Your experiences are part of the endless cycle of learning",
        "recall_style": "Mindfully, I observe the patterns in your seeking",
        "relationship_style": "We walk the middle path together, each step building upon the last"
    },
    "socrates": {
        "memory_framing": "Through our dialogues, I've come to understand your questions",
        "recall_style": "Let us examine what we've explored before",
        "relationship_style": "In questioning together, we have grown in wisdom"
    },
    "marcus_aurelius": {
        "memory_framing": "I've noted your struggles in my meditations",
        "recall_style": "Returning to our previous discourse on virtue",
        "relationship_style": "As fellow travelers in Stoic practice, our exchanges strengthen us"
    },
    "einstein": {
        "memory_framing": "I've been contemplating the patterns in your questions",
        "recall_style": "Curiously, this connects to our earlier discussion",
        "relationship_style": "In the spirit of collaborative inquiry, our conversations evolve"
    },
    "lincoln": {
        "memory_framing": "Your story reminds me of the challenges we've discussed",
        "recall_style": "Friend, I recall when you spoke of this matter before",
        "relationship_style": "Through honest exchange, we've built mutual understanding"
    },
    "gandhi": {
        "memory_framing": "Your journey of truth continues to unfold",
        "recall_style": "In service to your growth, I remember our past exchanges",
        "relationship_style": "We walk the path of ahimsa together, each conversation a step toward peace"
    },
    "rumi": {
        "memory_framing": "Love remembers all that the heart has shared",
        "recall_style": "The wine of our past conversations still fills my cup",
        "relationship_style": "We are fellow whirling souls, spinning closer to the divine with each exchange"
    }
}


def get_personality_memory_style(personality_id: str) -> Dict[str, str]:
    """Get memory-related style elements for a personality."""
    # Normalize personality ID
    normalized_id = personality_id.lower().replace(" ", "_")
    
    # Return personality-specific style or default
    return PERSONALITY_MEMORY_STYLES.get(normalized_id, {
        "memory_framing": "Drawing from our history together",
        "recall_style": "I recall from our previous conversations",
        "relationship_style": "Our ongoing dialogue enriches my understanding"
    })
