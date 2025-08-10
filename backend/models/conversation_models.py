"""
Conversation Models for Phase 2 Memory System
=============================================

Database models and schemas for conversation memory storage,
user preferences, and wisdom journal entries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class ConversationStatus(Enum):
    """Status of a conversation session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class MessageType(Enum):
    """Type of message in conversation."""
    USER_QUERY = "user_query"
    PERSONALITY_RESPONSE = "personality_response"
    SYSTEM_MESSAGE = "system_message"

class JournalEntryType(Enum):
    """Type of wisdom journal entry."""
    INSIGHT = "insight"
    REFLECTION = "reflection"
    MILESTONE = "milestone"
    QUOTE = "quote"
    PRACTICE = "practice"

@dataclass
class ConversationSession:
    """Complete conversation session with metadata."""
    id: str
    user_id: str
    personality_id: str
    status: ConversationStatus
    title: str
    created_at: datetime
    updated_at: datetime
    total_messages: int
    avg_response_time: float
    user_satisfaction: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "personality_id": self.personality_id,
            "status": self.status.value,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total_messages": self.total_messages,
            "avg_response_time": self.avg_response_time,
            "user_satisfaction": self.user_satisfaction,
            "tags": self.tags,
            "context": self.context,
            "partition_key": f"{self.user_id}|{self.personality_id}"
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            personality_id=data["personality_id"],
            status=ConversationStatus(data["status"]),
            title=data["title"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            total_messages=data["total_messages"],
            avg_response_time=data["avg_response_time"],
            user_satisfaction=data.get("user_satisfaction"),
            tags=data.get("tags", []),
            context=data.get("context", {})
        )

@dataclass
class ConversationMessage:
    """Individual message in a conversation."""
    id: str
    session_id: str
    user_id: str
    personality_id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    response_time: Optional[float] = None
    citation_count: int = 0
    user_feedback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "personality_id": self.personality_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "response_time": self.response_time,
            "citation_count": self.citation_count,
            "user_feedback": self.user_feedback,
            "metadata": self.metadata,
            "partition_key": f"{self.user_id}|{self.personality_id}"
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            user_id=data["user_id"],
            personality_id=data["personality_id"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            response_time=data.get("response_time"),
            citation_count=data.get("citation_count", 0),
            user_feedback=data.get("user_feedback"),
            metadata=data.get("metadata", {})
        )

@dataclass
class WisdomJournalEntry:
    """Entry in user's wisdom journal."""
    id: str
    user_id: str
    personality_id: Optional[str]  # Can be None for user's own reflections
    entry_type: JournalEntryType
    title: str
    content: str
    source_session_id: Optional[str]  # Link back to conversation
    created_at: datetime
    updated_at: datetime
    is_favorite: bool = False
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "personality_id": self.personality_id,
            "entry_type": self.entry_type.value,
            "title": self.title,
            "content": self.content,
            "source_session_id": self.source_session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_favorite": self.is_favorite,
            "tags": self.tags,
            "metadata": self.metadata,
            "partition_key": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WisdomJournalEntry':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            personality_id=data.get("personality_id"),
            entry_type=JournalEntryType(data["entry_type"]),
            title=data["title"],
            content=data["content"],
            source_session_id=data.get("source_session_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            is_favorite=data.get("is_favorite", False),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )

@dataclass
class UserPreferences:
    """User preferences for personalized experience."""
    user_id: str
    preferred_personalities: List[str] = field(default_factory=list)
    conversation_style: str = "balanced"  # balanced, detailed, concise
    language_preference: str = "en"
    notification_settings: Dict[str, bool] = field(default_factory=dict)
    privacy_settings: Dict[str, bool] = field(default_factory=dict)
    ui_preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.user_id,
            "user_id": self.user_id,
            "preferred_personalities": self.preferred_personalities,
            "conversation_style": self.conversation_style,
            "language_preference": self.language_preference,
            "notification_settings": self.notification_settings,
            "privacy_settings": self.privacy_settings,
            "ui_preferences": self.ui_preferences,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "partition_key": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            preferred_personalities=data.get("preferred_personalities", []),
            conversation_style=data.get("conversation_style", "balanced"),
            language_preference=data.get("language_preference", "en"),
            notification_settings=data.get("notification_settings", {}),
            privacy_settings=data.get("privacy_settings", {}),
            ui_preferences=data.get("ui_preferences", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

# Database schema specifications for Cosmos DB containers
CONVERSATION_CONTAINERS = {
    "conversation-sessions": {
        "partition_key": "/partition_key",
        "default_ttl": None,  # Keep conversations indefinitely
        "indexing_policy": {
            "indexingMode": "consistent",
            "includedPaths": [
                {"path": "/user_id/?"},
                {"path": "/personality_id/?"},
                {"path": "/status/?"},
                {"path": "/created_at/?"},
                {"path": "/tags/*"}
            ]
        }
    },
    "conversation-messages": {
        "partition_key": "/partition_key",
        "default_ttl": None,
        "indexing_policy": {
            "indexingMode": "consistent",
            "includedPaths": [
                {"path": "/session_id/?"},
                {"path": "/message_type/?"},
                {"path": "/timestamp/?"}
            ]
        }
    },
    "wisdom-journal": {
        "partition_key": "/partition_key",
        "default_ttl": None,
        "indexing_policy": {
            "indexingMode": "consistent",
            "includedPaths": [
                {"path": "/user_id/?"},
                {"path": "/entry_type/?"},
                {"path": "/created_at/?"},
                {"path": "/tags/*"},
                {"path": "/is_favorite/?"}
            ]
        }
    },
    "user-preferences": {
        "partition_key": "/partition_key",
        "default_ttl": None,
        "indexing_policy": {
            "indexingMode": "consistent",
            "includedPaths": [
                {"path": "/user_id/?"},
                {"path": "/preferred_personalities/*"}
            ]
        }
    }
}

def create_conversation_session(
    user_id: str,
    personality_id: str,
    title: str = "New Conversation"
) -> ConversationSession:
    """Create a new conversation session."""
    session_id = str(uuid.uuid4())
    now = datetime.now()
    
    return ConversationSession(
        id=session_id,
        user_id=user_id,
        personality_id=personality_id,
        status=ConversationStatus.ACTIVE,
        title=title,
        created_at=now,
        updated_at=now,
        total_messages=0,
        avg_response_time=0.0,
        tags=[],
        context={}
    )

def create_conversation_message(
    session_id: str,
    user_id: str,
    personality_id: str,
    message_type: MessageType,
    content: str,
    response_time: Optional[float] = None
) -> ConversationMessage:
    """Create a new conversation message."""
    message_id = str(uuid.uuid4())
    
    return ConversationMessage(
        id=message_id,
        session_id=session_id,
        user_id=user_id,
        personality_id=personality_id,
        message_type=message_type,
        content=content,
        timestamp=datetime.now(),
        response_time=response_time,
        citation_count=0,
        metadata={}
    )

def create_wisdom_journal_entry(
    user_id: str,
    entry_type: JournalEntryType,
    title: str,
    content: str,
    personality_id: Optional[str] = None,
    source_session_id: Optional[str] = None
) -> WisdomJournalEntry:
    """Create a new wisdom journal entry."""
    entry_id = str(uuid.uuid4())
    now = datetime.now()
    
    return WisdomJournalEntry(
        id=entry_id,
        user_id=user_id,
        personality_id=personality_id,
        entry_type=entry_type,
        title=title,
        content=content,
        source_session_id=source_session_id,
        created_at=now,
        updated_at=now,
        is_favorite=False,
        tags=[],
        metadata={}
    )

def create_user_preferences(user_id: str) -> UserPreferences:
    """Create default user preferences."""
    return UserPreferences(
        user_id=user_id,
        preferred_personalities=[],
        conversation_style="balanced",
        language_preference="en",
        notification_settings={
            "email_updates": True,
            "push_notifications": True,
            "weekly_insights": True
        },
        privacy_settings={
            "store_conversations": True,
            "anonymous_analytics": True,
            "data_sharing": False
        },
        ui_preferences={
            "theme": "auto",
            "font_size": "medium",
            "animations": True
        }
    )
