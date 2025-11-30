"""
Memory Models for Vimarsh Hierarchical Memory Architecture

This module defines the data models for the 4-layer hierarchical memory system:
- Layer 1: Working Memory (active conversation + hot context)
- Layer 2: Core Memory (user profile + personality relationships)
- Layer 3: Episodic Memory (session summaries + reflection insights)
- Layer 4: Semantic Archive (full history with vector embeddings)

Based on research from:
- MemGPT (UC Berkeley): Virtual memory management for LLMs
- Generative Agents (Stanford): Memory stream + reflection + importance scoring
- LangGraph: Persistent checkpointing with semantic retrieval
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class RelationshipDepth(Enum):
    """Relationship depth levels between user and personality."""
    STRANGER = 1        # First few interactions
    ACQUAINTANCE = 2    # 5-10 conversations
    FAMILIAR = 3        # Regular engagement, knows preferences
    TRUSTED = 4         # Deep conversations, shares personal challenges
    COMPANION = 5       # Long-term relationship, proactive guidance


class MemoryImportance(Enum):
    """Importance levels for memory items."""
    LOW = 1             # Casual conversation, greetings
    MEDIUM = 2          # Standard guidance interactions
    HIGH = 3            # Personal revelations, key insights
    CRITICAL = 4        # Major life events, breakthrough moments


class EmotionalTone(Enum):
    """Emotional tone categories for tracking emotional arc."""
    CURIOUS = "curious"
    SEEKING = "seeking"
    TROUBLED = "troubled"
    HOPEFUL = "hopeful"
    GRATEFUL = "grateful"
    PEACEFUL = "peaceful"
    INSPIRED = "inspired"
    REFLECTIVE = "reflective"
    UNCERTAIN = "uncertain"
    DETERMINED = "determined"


@dataclass
class MemoryProfile:
    """
    Layer 2: Core Memory - User's persistent profile across all conversations.
    
    Stored in Cosmos DB 'memory_profiles' container with partition key /user_id.
    """
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Communication preferences learned over time
    communication_style: Dict[str, Any] = field(default_factory=lambda: {
        "formality": "balanced",      # formal, balanced, casual
        "depth": "moderate",          # surface, moderate, deep
        "response_length": "medium",  # brief, medium, detailed
        "language_preference": "en"
    })
    
    # Discovered interests and themes
    discovered_interests: List[str] = field(default_factory=list)
    recurring_themes: List[str] = field(default_factory=list)
    
    # Life context (anonymized, user-shared)
    life_context: Dict[str, Any] = field(default_factory=lambda: {
        "life_stage": None,           # student, professional, parent, retired
        "primary_concerns": [],       # career, relationships, spiritual_growth
        "goals": []                   # what they're working toward
    })
    
    # Per-personality relationship summaries (brief, for context)
    personality_relationship_summary: Dict[str, str] = field(default_factory=dict)
    
    # Preferences for memory features
    memory_preferences: Dict[str, Any] = field(default_factory=lambda: {
        "cross_session_memory": True,
        "personality_memory_isolation": True,
        "proactive_recall": True,
        "memory_dashboard_enabled": True
    })
    
    # Metadata
    total_sessions: int = 0
    total_messages: int = 0
    last_active: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Cosmos DB storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "communication_style": self.communication_style,
            "discovered_interests": self.discovered_interests,
            "recurring_themes": self.recurring_themes,
            "life_context": self.life_context,
            "personality_relationship_summary": self.personality_relationship_summary,
            "memory_preferences": self.memory_preferences,
            "total_sessions": self.total_sessions,
            "total_messages": self.total_messages,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "_partition_key": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryProfile":
        """Create from Cosmos DB document."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            communication_style=data.get("communication_style", {}),
            discovered_interests=data.get("discovered_interests", []),
            recurring_themes=data.get("recurring_themes", []),
            life_context=data.get("life_context", {}),
            personality_relationship_summary=data.get("personality_relationship_summary", {}),
            memory_preferences=data.get("memory_preferences", {}),
            total_sessions=data.get("total_sessions", 0),
            total_messages=data.get("total_messages", 0),
            last_active=datetime.fromisoformat(data["last_active"]) if data.get("last_active") else None
        )
    
    @classmethod
    def create_new(cls, user_id: str) -> "MemoryProfile":
        """Create a new memory profile for a first-time user."""
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=now,
            updated_at=now
        )


@dataclass
class RelationshipState:
    """
    Layer 2: Core Memory - Tracks relationship between user and specific personality.
    
    Stored in Cosmos DB 'relationship_states' container with partition key /user_id.
    """
    id: str
    user_id: str
    personality_id: str
    
    # Relationship depth tracking
    depth_level: RelationshipDepth = RelationshipDepth.STRANGER
    interaction_count: int = 0
    total_duration_minutes: int = 0
    
    # Relationship quality metrics
    trust_score: float = 0.5  # 0-1 scale
    engagement_score: float = 0.5  # 0-1 scale
    
    # Key themes discussed with this personality
    key_themes: List[str] = field(default_factory=list)
    recent_topics: List[str] = field(default_factory=list)
    
    # Emotional patterns tracked over time
    dominant_emotions: List[str] = field(default_factory=list)  # Most common emotional states
    
    # Milestones achieved
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    # Example: {"type": "first_deep_conversation", "date": "2025-01-15", "description": "..."}
    
    # Last interaction context for continuity
    last_interaction: Optional[datetime] = None
    last_topic: Optional[str] = None
    last_emotional_state: Optional[str] = None
    
    # Pending follow-ups (things the personality might proactively mention)
    pending_followups: List[Dict[str, Any]] = field(default_factory=list)
    
    # Proactive recall statistics (Phase 4.1)
    recall_stats: Dict[str, Any] = field(default_factory=lambda: {
        "total_recalls": 0,
        "by_type": {},
        "successful_topics": []
    })
    
    # Timestamps
    first_interaction: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Cosmos DB storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "personality_id": self.personality_id,
            "depth_level": self.depth_level.value,
            "interaction_count": self.interaction_count,
            "total_duration_minutes": self.total_duration_minutes,
            "trust_score": self.trust_score,
            "engagement_score": self.engagement_score,
            "key_themes": self.key_themes,
            "recent_topics": self.recent_topics,
            "dominant_emotions": self.dominant_emotions,
            "milestones": self.milestones,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "last_topic": self.last_topic,
            "last_emotional_state": self.last_emotional_state,
            "pending_followups": self.pending_followups,
            "recall_stats": self.recall_stats,
            "first_interaction": self.first_interaction.isoformat() if self.first_interaction else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "_partition_key": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationshipState":
        """Create from Cosmos DB document."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            personality_id=data["personality_id"],
            depth_level=RelationshipDepth(data.get("depth_level", 1)),
            interaction_count=data.get("interaction_count", 0),
            total_duration_minutes=data.get("total_duration_minutes", 0),
            trust_score=data.get("trust_score", 0.5),
            engagement_score=data.get("engagement_score", 0.5),
            key_themes=data.get("key_themes", []),
            recent_topics=data.get("recent_topics", []),
            dominant_emotions=data.get("dominant_emotions", []),
            milestones=data.get("milestones", []),
            last_interaction=datetime.fromisoformat(data["last_interaction"]) if data.get("last_interaction") else None,
            last_topic=data.get("last_topic"),
            last_emotional_state=data.get("last_emotional_state"),
            pending_followups=data.get("pending_followups", []),
            recall_stats=data.get("recall_stats", {"total_recalls": 0, "by_type": {}, "successful_topics": []}),
            first_interaction=datetime.fromisoformat(data["first_interaction"]) if data.get("first_interaction") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )
    
    @classmethod
    def create_new(cls, user_id: str, personality_id: str) -> "RelationshipState":
        """Create a new relationship state for first interaction."""
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            personality_id=personality_id,
            first_interaction=now,
            updated_at=now
        )
    
    def calculate_depth_level(self) -> RelationshipDepth:
        """Calculate relationship depth based on interaction metrics."""
        if self.interaction_count < 3:
            return RelationshipDepth.STRANGER
        elif self.interaction_count < 10:
            return RelationshipDepth.ACQUAINTANCE
        elif self.interaction_count < 25:
            return RelationshipDepth.FAMILIAR
        elif self.interaction_count < 50 or self.trust_score < 0.7:
            return RelationshipDepth.TRUSTED
        else:
            return RelationshipDepth.COMPANION
    
    def update_after_interaction(
        self, 
        duration_minutes: int,
        topics: List[str],
        emotional_state: Optional[str] = None
    ) -> None:
        """Update relationship state after an interaction."""
        self.interaction_count += 1
        self.total_duration_minutes += duration_minutes
        self.last_interaction = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if topics:
            self.last_topic = topics[0] if topics else None
            # Add new topics to recent_topics (keep last 10)
            self.recent_topics = (topics + self.recent_topics)[:10]
            # Update key themes (deduplicated, keep top 20)
            all_themes = set(self.key_themes + topics)
            self.key_themes = list(all_themes)[:20]
        
        if emotional_state:
            self.last_emotional_state = emotional_state
        
        # Recalculate depth level
        self.depth_level = self.calculate_depth_level()


@dataclass
class ConversationMessage:
    """
    Layer 4: Semantic Archive - Individual message in conversation history.
    
    Stored in Cosmos DB 'conversation_history' container with partition key /user_id.
    """
    id: str
    user_id: str
    personality_id: str
    session_id: str
    
    # Message content
    role: str  # "user" or "assistant"
    content: str
    
    # Timing
    timestamp: datetime
    
    # Importance scoring (0-1)
    importance_score: float = 0.5
    importance_factors: Dict[str, float] = field(default_factory=dict)
    # Example: {"emotional_intensity": 0.7, "novelty": 0.5, "user_feedback": 0.8}
    
    # Vector embedding for semantic search (768 dimensions for Gemini)
    embedding: Optional[List[float]] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=lambda: {
        "topics": [],
        "emotional_tone": None,
        "has_question": False,
        "has_personal_revelation": False,
        "referenced_sources": []
    })
    
    # Retention
    archived: bool = False
    archive_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Cosmos DB storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "personality_id": self.personality_id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "importance_score": self.importance_score,
            "importance_factors": self.importance_factors,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "archived": self.archived,
            "archive_date": self.archive_date.isoformat() if self.archive_date else None,
            "_partition_key": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMessage":
        """Create from Cosmos DB document."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            personality_id=data["personality_id"],
            session_id=data["session_id"],
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            importance_score=data.get("importance_score", 0.5),
            importance_factors=data.get("importance_factors", {}),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
            archived=data.get("archived", False),
            archive_date=datetime.fromisoformat(data["archive_date"]) if data.get("archive_date") else None
        )
    
    @classmethod
    def create_new(
        cls,
        user_id: str,
        personality_id: str,
        session_id: str,
        role: str,
        content: str
    ) -> "ConversationMessage":
        """Create a new conversation message."""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            personality_id=personality_id,
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )


@dataclass
class SessionSummary:
    """
    Layer 3: Episodic Memory - Summary of a conversation session.
    
    Stored in Cosmos DB 'session_summaries' container with partition key /user_id.
    """
    id: str
    user_id: str
    personality_id: str
    session_id: str
    
    # Session timing
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: int = 0
    
    # Session summary
    summary: str = ""  # AI-generated summary of the conversation
    
    # Key insights extracted
    key_insights: List[str] = field(default_factory=list)
    
    # Topics discussed
    topics: List[str] = field(default_factory=list)
    
    # Questions asked by user
    questions_asked: List[str] = field(default_factory=list)
    
    # Emotional arc tracking
    emotional_arc: List[Dict[str, Any]] = field(default_factory=list)
    # Example: [{"timestamp": "...", "tone": "seeking"}, {"timestamp": "...", "tone": "grateful"}]
    starting_emotion: Optional[str] = None
    ending_emotion: Optional[str] = None
    
    # Reflection (deeper insight generated after session)
    reflection: Optional[str] = None
    reflection_generated_at: Optional[datetime] = None
    
    # Metrics
    message_count: int = 0
    user_message_count: int = 0
    assistant_message_count: int = 0
    avg_importance_score: float = 0.5
    
    # Follow-up suggestions
    suggested_followups: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Cosmos DB storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "personality_id": self.personality_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes,
            "summary": self.summary,
            "key_insights": self.key_insights,
            "topics": self.topics,
            "questions_asked": self.questions_asked,
            "emotional_arc": self.emotional_arc,
            "starting_emotion": self.starting_emotion,
            "ending_emotion": self.ending_emotion,
            "reflection": self.reflection,
            "reflection_generated_at": self.reflection_generated_at.isoformat() if self.reflection_generated_at else None,
            "message_count": self.message_count,
            "user_message_count": self.user_message_count,
            "assistant_message_count": self.assistant_message_count,
            "avg_importance_score": self.avg_importance_score,
            "suggested_followups": self.suggested_followups,
            "_partition_key": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionSummary":
        """Create from Cosmos DB document."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            personality_id=data["personality_id"],
            session_id=data["session_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            duration_minutes=data.get("duration_minutes", 0),
            summary=data.get("summary", ""),
            key_insights=data.get("key_insights", []),
            topics=data.get("topics", []),
            questions_asked=data.get("questions_asked", []),
            emotional_arc=data.get("emotional_arc", []),
            starting_emotion=data.get("starting_emotion"),
            ending_emotion=data.get("ending_emotion"),
            reflection=data.get("reflection"),
            reflection_generated_at=datetime.fromisoformat(data["reflection_generated_at"]) if data.get("reflection_generated_at") else None,
            message_count=data.get("message_count", 0),
            user_message_count=data.get("user_message_count", 0),
            assistant_message_count=data.get("assistant_message_count", 0),
            avg_importance_score=data.get("avg_importance_score", 0.5),
            suggested_followups=data.get("suggested_followups", [])
        )
    
    @classmethod
    def create_new(
        cls,
        user_id: str,
        personality_id: str,
        session_id: str
    ) -> "SessionSummary":
        """Create a new session summary."""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            personality_id=personality_id,
            session_id=session_id,
            start_time=datetime.utcnow()
        )


@dataclass
class WorkingMemoryContext:
    """
    Layer 1: Working Memory - Assembled context for current conversation.
    
    This is an in-memory structure used during conversation, not persisted directly.
    Token budget: 16K tokens total.
    """
    user_id: str
    personality_id: str
    session_id: str
    
    # Token budget management
    max_tokens: int = 16000
    current_token_count: int = 0
    
    # Core memory segment (from MemoryProfile) - 4K token budget
    user_profile_context: str = ""
    relationship_context: str = ""
    core_memory_tokens: int = 0
    
    # Episodic memory segment (from SessionSummaries) - 8K token budget
    recent_session_summaries: List[Dict[str, Any]] = field(default_factory=list)
    relevant_past_insights: List[str] = field(default_factory=list)
    episodic_memory_tokens: int = 0
    
    # Retrieved semantic memories - on-demand allocation
    retrieved_memories: List[Dict[str, Any]] = field(default_factory=list)
    semantic_memory_tokens: int = 0
    
    # Current conversation messages (most recent)
    current_messages: List[Dict[str, Any]] = field(default_factory=list)
    current_conversation_tokens: int = 0
    
    # RAG context (personality-specific knowledge)
    rag_context: str = ""
    rag_tokens: int = 0
    
    # Metadata
    assembled_at: Optional[datetime] = None
    context_quality_score: float = 0.0  # 0-1 score of context relevance
    
    def get_total_tokens(self) -> int:
        """Calculate total tokens used."""
        return (
            self.core_memory_tokens +
            self.episodic_memory_tokens +
            self.semantic_memory_tokens +
            self.current_conversation_tokens +
            self.rag_tokens
        )
    
    def get_available_tokens(self) -> int:
        """Calculate remaining token budget."""
        return self.max_tokens - self.get_total_tokens()
    
    def to_prompt_context(self) -> str:
        """Convert working memory to prompt context string."""
        sections = []
        
        if self.user_profile_context:
            sections.append(f"## User Context\n{self.user_profile_context}")
        
        if self.relationship_context:
            sections.append(f"## Our Relationship\n{self.relationship_context}")
        
        if self.recent_session_summaries:
            summaries_text = "\n".join([
                f"- {s.get('summary', '')}" for s in self.recent_session_summaries[:3]
            ])
            sections.append(f"## Recent Conversations\n{summaries_text}")
        
        if self.relevant_past_insights:
            insights_text = "\n".join([f"- {i}" for i in self.relevant_past_insights[:5]])
            sections.append(f"## Relevant Past Insights\n{insights_text}")
        
        if self.retrieved_memories:
            memories_text = "\n".join([
                f"- {m.get('content', '')[:200]}..." for m in self.retrieved_memories[:3]
            ])
            sections.append(f"## Related Past Discussions\n{memories_text}")
        
        return "\n\n".join(sections)


@dataclass  
class MemorySearchQuery:
    """Query parameters for semantic memory search."""
    user_id: str
    query_text: str
    personality_id: Optional[str] = None  # None = search all personalities
    max_results: int = 10
    min_importance_score: float = 0.3
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_archived: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "query_text": self.query_text,
            "personality_id": self.personality_id,
            "max_results": self.max_results,
            "min_importance_score": self.min_importance_score,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
            "include_archived": self.include_archived
        }


@dataclass
class MemorySearchResult:
    """Result from semantic memory search."""
    message: ConversationMessage
    similarity_score: float
    relevance_score: float  # Combined score of similarity + importance + recency
    context_snippet: str  # Surrounding context
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message.to_dict(),
            "similarity_score": self.similarity_score,
            "relevance_score": self.relevance_score,
            "context_snippet": self.context_snippet
        }
