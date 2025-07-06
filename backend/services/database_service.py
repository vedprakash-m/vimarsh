"""
Simple database service for spiritual texts storage and retrieval.
Implements local JSON storage for development and Cosmos DB for production.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class SpiritualText:
    """Represents a spiritual text document"""
    id: str
    title: str
    content: str
    source: str  # e.g., "Bhagavad Gita", "Mahabharata", "Srimad Bhagavatam"
    chapter: Optional[str] = None
    verse: Optional[str] = None
    category: str = "general"  # e.g., "dharma", "karma", "devotion"
    language: str = "English"
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class Conversation:
    """Represents a user conversation for audit and improvement"""
    id: str
    userId: str
    userEmail: str
    sessionId: str
    timestamp: str
    question: str
    response: str
    citations: List[str]
    personality: str = "krishna"  # Default personality
    metadata: Dict[str, Any] = None
    type: str = "conversation"
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class UsageRecord:
    """Represents usage tracking for admin analytics"""
    id: str
    userId: str
    userEmail: str
    sessionId: str
    timestamp: str
    model: str
    inputTokens: int
    outputTokens: int
    totalTokens: int
    costUsd: float
    requestType: str  # 'spiritual_guidance', 'rag_query', etc.
    responseQuality: str  # 'high', 'medium', 'low', 'fallback'
    personality: str = "krishna"
    type: str = "usage_tracking"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class UserStats:
    """Represents aggregated user statistics"""
    id: str
    userId: str
    userEmail: str
    totalRequests: int
    totalTokens: int
    totalCostUsd: float
    currentMonthTokens: int
    currentMonthCostUsd: float
    lastRequest: Optional[str]
    avgTokensPerRequest: float
    favoriteModel: str
    personalityUsage: Dict[str, int]  # personality -> count
    qualityBreakdown: Dict[str, int]  # quality -> count
    riskScore: float = 0.0  # For abuse detection
    isBlocked: bool = False
    blockReason: Optional[str] = None
    type: str = "user_stats"
    updatedAt: str = None
    
    def __post_init__(self):
        if self.updatedAt is None:
            self.updatedAt = datetime.now().isoformat()

@dataclass
class PersonalityConfig:
    """Represents personality configuration and associated books"""
    id: str
    personalityName: str  # "krishna", "buddha", "jesus", etc.
    displayName: str  # "Lord Krishna", "Buddha", "Jesus Christ"
    description: str
    systemPrompt: str
    associatedBooks: List[str]  # List of book/source IDs
    vectorNamespace: str  # For vector DB partitioning
    isActive: bool = True
    type: str = "personality_config"
    createdAt: str = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.now().isoformat()

@dataclass
class EnhancedSpiritualText:
    """Enhanced spiritual text with personality association"""
    id: str
    title: str
    content: str
    source: str
    chapter: Optional[str] = None
    verse: Optional[str] = None
    category: str = "general"
    language: str = "English"
    personality: str = "krishna"  # Associated personality
    embedding: Optional[List[float]] = None  # Vector embedding
    vectorNamespace: str = "krishna"  # For vector DB partitioning
    type: str = "spiritual_text"
    createdAt: str = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.now().isoformat()
        if self.vectorNamespace is None:
            self.vectorNamespace = self.personality

class DatabaseService:
    """Database service aligned with production Cosmos DB setup"""
    
    def __init__(self):
        # Production Cosmos DB configuration
        self.cosmos_db_name = "vimarsh-db"  # Production DB name
        self.spiritual_texts_container = "spiritual-texts"  # Production container
        self.conversations_container = "conversations"  # Production container
        
        # Local development storage paths
        self.storage_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vimarsh-db')
        self.spiritual_texts_path = os.path.join(self.storage_path, 'spiritual-texts.json')
        self.conversations_path = os.path.join(self.storage_path, 'conversations.json')
        
        self.is_cosmos_enabled = self._check_cosmos_config()
        
        if not self.is_cosmos_enabled:
            self._init_local_storage()
    
    def _check_cosmos_config(self) -> bool:
        """Check if Cosmos DB is configured"""
        cosmos_conn = os.getenv('AZURE_COSMOS_CONNECTION_STRING', '')
        return cosmos_conn and cosmos_conn != 'dev-mode-local-storage'
    
    def _init_local_storage(self):
        """Initialize local JSON storage with production-aligned structure"""
        # Create vimarsh-db directory structure
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize spiritual-texts container
        if not os.path.exists(self.spiritual_texts_path):
            initial_texts = [
                SpiritualText(
                    id="bg_2_47",
                    title="On Duty Without Attachment",
                    content="You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself to be the cause of the results of your activities, and never be attached to not doing your duty.",
                    source="Bhagavad Gita",
                    chapter="2",
                    verse="47",
                    category="dharma"
                ),
                SpiritualText(
                    id="bg_6_19",
                    title="Steady Mind in Meditation",
                    content="As a lamp in a windless place does not waver, so the transcendentalist, whose mind is controlled, remains always steady in his meditation on the transcendent Self.",
                    source="Bhagavad Gita",
                    chapter="6",
                    verse="19",
                    category="meditation"
                ),
                SpiritualText(
                    id="bg_12_6_7",
                    title="Devotion and Surrender",
                    content="But those who worship Me, giving up all their activities unto Me and being devoted to Me without deviation, engaged in devotional service and always meditating upon Me, having fixed their minds upon Me, O son of Pritha—for them I am the swift deliverer from the ocean of birth and death.",
                    source="Bhagavad Gita",
                    chapter="12",
                    verse="6-7",
                    category="devotion"
                ),
                SpiritualText(
                    id="bg_2_14",
                    title="Accepting Pleasure and Pain",
                    content="O son of Kunti, the nonpermanent appearance of happiness and distress, and their disappearance in due course, are like the appearance and disappearance of winter and summer seasons. They arise from sense perception, O scion of Bharata, and one must learn to tolerate them without being disturbed.",
                    source="Bhagavad Gita",
                    chapter="2",
                    verse="14",
                    category="equanimity"
                ),
                SpiritualText(
                    id="bg_2_20",
                    title="Eternal Nature of the Soul",
                    content="For the soul there is neither birth nor death nor, having once been, does he ever cease to be. He is unborn, eternal, permanent, and primeval. He is not slain when the body is slain.",
                    source="Bhagavad Gita",
                    chapter="2",
                    verse="20",
                    category="soul"
                )
            ]
            
            self._save_to_local_file(self.spiritual_texts_path, [asdict(text) for text in initial_texts])
            logger.info(f"✅ Initialized spiritual-texts container with {len(initial_texts)} texts")
        
        # Initialize conversations container
        if not os.path.exists(self.conversations_path):
            self._save_to_local_file(self.conversations_path, [])
            logger.info(f"✅ Initialized conversations container")
    
    def _load_from_local_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from local JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_to_local_file(self, file_path: str, data: List[Dict[str, Any]]):
        """Save data to local JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_spiritual_text(self, text_id: str) -> Optional[SpiritualText]:
        """Get a specific spiritual text by ID"""
        if self.is_cosmos_enabled:
            return self._get_from_cosmos(text_id)
        else:
            return self._get_from_local(text_id)
    
    def _get_from_local(self, text_id: str) -> Optional[SpiritualText]:
        """Get spiritual text from local storage"""
        data = self._load_from_local_file(self.spiritual_texts_path)
        for item in data:
            if item.get('id') == text_id:
                return SpiritualText(**item)
        return None
    
    def search_spiritual_texts(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[SpiritualText]:
        """Search spiritual texts by content or category"""
        if self.is_cosmos_enabled:
            return self._search_in_cosmos(query, category, limit)
        else:
            return self._search_in_local(query, category, limit)
    
    def _search_in_local(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[SpiritualText]:
        """Search in local storage"""
        data = self._load_from_local_file(self.spiritual_texts_path)
        results = []
        
        query_lower = query.lower()
        
        for item in data:
            # Check category filter
            if category and item.get('category') != category:
                continue
            
            # Search in content, title, or source
            if (query_lower in item.get('content', '').lower() or
                query_lower in item.get('title', '').lower() or
                query_lower in item.get('source', '').lower()):
                results.append(SpiritualText(**item))
            
            if len(results) >= limit:
                break
        
        return results
    
    def add_spiritual_text(self, text: SpiritualText) -> bool:
        """Add a new spiritual text"""
        if self.is_cosmos_enabled:
            return self._add_to_cosmos(text)
        else:
            return self._add_to_local(text)
    
    def _add_to_local(self, text: SpiritualText) -> bool:
        """Add spiritual text to local storage"""
        try:
            data = self._load_from_local_file(self.spiritual_texts_path)
            data.append(asdict(text))
            self._save_to_local_file(self.spiritual_texts_path, data)
            logger.info(f"✅ Added spiritual text: {text.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add spiritual text: {e}")
            return False
    
    def get_all_spiritual_texts(self) -> List[SpiritualText]:
        """Get all spiritual texts"""
        if self.is_cosmos_enabled:
            return self._get_all_from_cosmos()
        else:
            return self._get_all_from_local()
    
    def _get_all_from_local(self) -> List[SpiritualText]:
        """Get all spiritual texts from local storage"""
        data = self._load_from_local_file(self.spiritual_texts_path)
        return [SpiritualText(**item) for item in data]
    
    def get_texts_by_category(self, category: str) -> List[SpiritualText]:
        """Get texts by category"""
        if self.is_cosmos_enabled:
            return self._get_category_from_cosmos(category)
        else:
            return self._get_category_from_local(category)
    
    def _get_category_from_local(self, category: str) -> List[SpiritualText]:
        """Get texts by category from local storage"""
        data = self._load_from_local_file(self.spiritual_texts_path)
        return [SpiritualText(**item) for item in data if item.get('category') == category]
    
    # =======================
    # CONVERSATION MANAGEMENT
    # =======================
    
    async def save_conversation(self, conversation: Conversation) -> bool:
        """Save user conversation for audit and improvement"""
        try:
            if self.is_cosmos_enabled:
                # Save to Cosmos DB conversations container
                return await self._save_to_cosmos(self.conversations_container, conversation)
            else:
                # Save to local JSON for development
                return self._save_conversation_local(conversation)
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False
    
    async def get_user_conversations(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """Get conversations for a specific user"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.userId = '{user_id}' AND c.type = 'conversation' ORDER BY c.timestamp DESC OFFSET {offset} LIMIT {limit}"
                return await self._query_cosmos(self.conversations_container, query, Conversation)
            else:
                return self._get_user_conversations_local(user_id, limit, offset)
        except Exception as e:
            logger.error(f"Failed to get user conversations: {e}")
            return []
    
    async def get_session_conversations(self, session_id: str) -> List[Conversation]:
        """Get all conversations for a session"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.sessionId = '{session_id}' AND c.type = 'conversation' ORDER BY c.timestamp ASC"
                return await self._query_cosmos(self.conversations_container, query, Conversation)
            else:
                return self._get_session_conversations_local(session_id)
        except Exception as e:
            logger.error(f"Failed to get session conversations: {e}")
            return []
    
    async def get_conversations_by_personality(self, personality: str, limit: int = 100) -> List[Conversation]:
        """Get conversations for a specific personality"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.personality = '{personality}' AND c.type = 'conversation' ORDER BY c.timestamp DESC OFFSET 0 LIMIT {limit}"
                return await self._query_cosmos(self.conversations_container, query, Conversation)
            else:
                return self._get_conversations_by_personality_local(personality, limit)
        except Exception as e:
            logger.error(f"Failed to get conversations by personality: {e}")
            return []
    
    async def flag_abusive_user(self, user_id: str, reason: str) -> bool:
        """Flag user for abusive behavior"""
        try:
            # Update user stats to mark as blocked
            user_stats = await self.get_user_stats(user_id)
            if user_stats:
                user_stats.isBlocked = True
                user_stats.blockReason = reason
                user_stats.riskScore = 1.0
                return await self.save_user_stats(user_stats)
            return False
        except Exception as e:
            logger.error(f"Failed to flag abusive user: {e}")
            return False
    
    # =======================
    # USAGE TRACKING & ADMIN
    # =======================
    
    async def save_usage_record(self, usage: UsageRecord) -> bool:
        """Save usage record for admin analytics"""
        try:
            if self.is_cosmos_enabled:
                return await self._save_to_cosmos(self.conversations_container, usage)
            else:
                return self._save_usage_record_local(usage)
        except Exception as e:
            logger.error(f"Failed to save usage record: {e}")
            return False
    
    async def save_user_stats(self, stats: UserStats) -> bool:
        """Save/update user statistics"""
        try:
            if self.is_cosmos_enabled:
                return await self._save_to_cosmos(self.conversations_container, stats)
            else:
                return self._save_user_stats_local(stats)
        except Exception as e:
            logger.error(f"Failed to save user stats: {e}")
            return False
    
    async def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """Get user statistics"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.userId = '{user_id}' AND c.type = 'user_stats'"
                results = await self._query_cosmos(self.conversations_container, query, UserStats)
                return results[0] if results else None
            else:
                return self._get_user_stats_local(user_id)
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return None
    
    async def get_usage_records(self, days: int = 30, limit: int = 1000) -> List[UsageRecord]:
        """Get usage records for admin analytics"""
        try:
            if self.is_cosmos_enabled:
                # Get records from last N days
                cutoff_date = datetime.now() - timedelta(days=days)
                query = f"SELECT * FROM c WHERE c.type = 'usage_tracking' AND c.timestamp >= '{cutoff_date.isoformat()}' ORDER BY c.timestamp DESC OFFSET 0 LIMIT {limit}"
                return await self._query_cosmos(self.conversations_container, query, UsageRecord)
            else:
                return self._get_usage_records_local(days, limit)
        except Exception as e:
            logger.error(f"Failed to get usage records: {e}")
            return []
    
    async def get_top_users(self, limit: int = 10) -> List[UserStats]:
        """Get top users by usage"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.type = 'user_stats' ORDER BY c.totalCostUsd DESC OFFSET 0 LIMIT {limit}"
                return await self._query_cosmos(self.conversations_container, query, UserStats)
            else:
                return self._get_top_users_local(limit)
        except Exception as e:
            logger.error(f"Failed to get top users: {e}")
            return []
    
    async def get_blocked_users(self) -> List[UserStats]:
        """Get list of blocked users"""
        try:
            if self.is_cosmos_enabled:
                query = "SELECT * FROM c WHERE c.type = 'user_stats' AND c.isBlocked = true"
                return await self._query_cosmos(self.conversations_container, query, UserStats)
            else:
                return self._get_blocked_users_local()
        except Exception as e:
            logger.error(f"Failed to get blocked users: {e}")
            return []
    
    # =======================
    # PERSONALITY & BOOKS
    # =======================
    
    async def save_personality_config(self, config: PersonalityConfig) -> bool:
        """Save personality configuration"""
        try:
            if self.is_cosmos_enabled:
                return await self._save_to_cosmos(self.conversations_container, config)
            else:
                return self._save_personality_config_local(config)
        except Exception as e:
            logger.error(f"Failed to save personality config: {e}")
            return False
    
    async def get_personality_config(self, personality_name: str) -> Optional[PersonalityConfig]:
        """Get personality configuration"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.personalityName = '{personality_name}' AND c.type = 'personality_config'"
                results = await self._query_cosmos(self.conversations_container, query, PersonalityConfig)
                return results[0] if results else None
            else:
                return self._get_personality_config_local(personality_name)
        except Exception as e:
            logger.error(f"Failed to get personality config: {e}")
            return None
    
    async def get_all_personalities(self) -> List[PersonalityConfig]:
        """Get all active personalities"""
        try:
            if self.is_cosmos_enabled:
                query = "SELECT * FROM c WHERE c.type = 'personality_config' AND c.isActive = true"
                return await self._query_cosmos(self.conversations_container, query, PersonalityConfig)
            else:
                return self._get_all_personalities_local()
        except Exception as e:
            logger.error(f"Failed to get all personalities: {e}")
            return []
    
    async def save_enhanced_spiritual_text(self, text: EnhancedSpiritualText) -> bool:
        """Save enhanced spiritual text with personality association"""
        try:
            if self.is_cosmos_enabled:
                return await self._save_to_cosmos(self.spiritual_texts_container, text)
            else:
                return self._save_enhanced_text_local(text)
        except Exception as e:
            logger.error(f"Failed to save enhanced spiritual text: {e}")
            return False
    
    async def get_texts_by_personality(self, personality: str, limit: int = 100) -> List[EnhancedSpiritualText]:
        """Get spiritual texts for a specific personality"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.personality = '{personality}' AND c.type = 'spiritual_text' OFFSET 0 LIMIT {limit}"
                return await self._query_cosmos(self.spiritual_texts_container, query, EnhancedSpiritualText)
            else:
                return self._get_texts_by_personality_local(personality, limit)
        except Exception as e:
            logger.error(f"Failed to get texts by personality: {e}")
            return []
    
    async def get_texts_by_vector_namespace(self, namespace: str, limit: int = 100) -> List[EnhancedSpiritualText]:
        """Get texts by vector namespace for RAG"""
        try:
            if self.is_cosmos_enabled:
                query = f"SELECT * FROM c WHERE c.vectorNamespace = '{namespace}' AND c.type = 'spiritual_text' OFFSET 0 LIMIT {limit}"
                return await self._query_cosmos(self.spiritual_texts_container, query, EnhancedSpiritualText)
            else:
                return self._get_texts_by_namespace_local(namespace, limit)
        except Exception as e:
            logger.error(f"Failed to get texts by namespace: {e}")
            return []
    
    # =======================
    # HELPER METHODS
    # =======================
    
    async def _save_to_cosmos(self, container: str, item: Any) -> bool:
        """Save item to Cosmos DB container"""
        try:
            # Convert dataclass to dict
            item_dict = asdict(item)
            
            # TODO: Implement actual Cosmos DB save
            # For now, this is a placeholder
            logger.info(f"📊 Saving {item.type} to {container}: {item.id}")
            return True
        except Exception as e:
            logger.error(f"Cosmos DB save failed: {e}")
            return False
    
    async def _query_cosmos(self, container: str, query: str, model_class: type) -> List[Any]:
        """Query Cosmos DB and return typed results"""
        try:
            # TODO: Implement actual Cosmos DB query
            # For now, return empty list
            logger.info(f"🔍 Querying {container}: {query}")
            return []
        except Exception as e:
            logger.error(f"Cosmos DB query failed: {e}")
            return []
    
    # =======================
    # LOCAL STORAGE METHODS (Development)
    # =======================
    
    def _save_conversation_local(self, conversation: Conversation) -> bool:
        """Save conversation to local conversations.json"""
        try:
            # Load existing conversations
            conversations = self._load_from_local_file(self.conversations_path)
            
            # Add new conversation
            conversations.append(asdict(conversation))
            
            # Save back to file
            self._save_to_local_file(self.conversations_path, conversations)
            
            logger.info(f"💾 Saved conversation locally: {conversation.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation locally: {e}")
            return False
    
    def _save_usage_record_local(self, usage: UsageRecord) -> bool:
        """Save usage record to local conversations.json"""
        try:
            # Load existing data
            data = self._load_from_local_file(self.conversations_path)
            
            # Add new usage record
            data.append(asdict(usage))
            
            # Save back to file
            self._save_to_local_file(self.conversations_path, data)
            
            logger.info(f"💾 Saved usage record locally: {usage.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save usage record locally: {e}")
            return False
    
    def _save_user_stats_local(self, stats: UserStats) -> bool:
        """Save user stats to local conversations.json"""
        try:
            # Load existing data
            data = self._load_from_local_file(self.conversations_path)
            
            # Remove any existing stats for this user
            data = [item for item in data if not (item.get('userId') == stats.userId and item.get('type') == 'user_stats')]
            
            # Add new stats
            data.append(asdict(stats))
            
            # Save back to file
            self._save_to_local_file(self.conversations_path, data)
            
            logger.info(f"💾 Saved user stats locally: {stats.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save user stats locally: {e}")
            return False
    
    def _save_personality_config_local(self, config: PersonalityConfig) -> bool:
        """Save personality config to local conversations.json"""
        try:
            # Load existing data
            data = self._load_from_local_file(self.conversations_path)
            
            # Remove any existing config for this personality
            data = [item for item in data if not (item.get('personalityName') == config.personalityName and item.get('type') == 'personality_config')]
            
            # Add new config
            data.append(asdict(config))
            
            # Save back to file
            self._save_to_local_file(self.conversations_path, data)
            
            logger.info(f"💾 Saved personality config locally: {config.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save personality config locally: {e}")
            return False
    
    # TODO: Implement remaining local methods for development
    def _get_user_conversations_local(self, user_id: str, limit: int, offset: int) -> List[Conversation]:
        """Get user conversations from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            conversations = [Conversation(**item) for item in data 
                           if item.get('userId') == user_id and item.get('type') == 'conversation']
            # Sort by timestamp descending
            conversations.sort(key=lambda x: x.timestamp, reverse=True)
            return conversations[offset:offset+limit]
        except Exception as e:
            logger.error(f"Failed to get user conversations locally: {e}")
            return []
    
    def _get_session_conversations_local(self, session_id: str) -> List[Conversation]:
        """Get session conversations from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            conversations = [Conversation(**item) for item in data 
                           if item.get('sessionId') == session_id and item.get('type') == 'conversation']
            # Sort by timestamp ascending
            conversations.sort(key=lambda x: x.timestamp)
            return conversations
        except Exception as e:
            logger.error(f"Failed to get session conversations locally: {e}")
            return []
    
    def _get_conversations_by_personality_local(self, personality: str, limit: int) -> List[Conversation]:
        """Get conversations by personality from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            conversations = [Conversation(**item) for item in data 
                           if item.get('personality') == personality and item.get('type') == 'conversation']
            # Sort by timestamp descending
            conversations.sort(key=lambda x: x.timestamp, reverse=True)
            return conversations[:limit]
        except Exception as e:
            logger.error(f"Failed to get conversations by personality locally: {e}")
            return []
    
    def _get_usage_records_local(self, days: int, limit: int) -> List[UsageRecord]:
        """Get usage records from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            cutoff_date = datetime.now() - timedelta(days=days)
            records = [UsageRecord(**item) for item in data 
                      if item.get('type') == 'usage_tracking' and 
                      datetime.fromisoformat(item.get('timestamp', '')) >= cutoff_date]
            # Sort by timestamp descending
            records.sort(key=lambda x: x.timestamp, reverse=True)
            return records[:limit]
        except Exception as e:
            logger.error(f"Failed to get usage records locally: {e}")
            return []
    
    def _get_user_stats_local(self, user_id: str) -> Optional[UserStats]:
        """Get user stats from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            for item in data:
                if item.get('userId') == user_id and item.get('type') == 'user_stats':
                    return UserStats(**item)
            return None
        except Exception as e:
            logger.error(f"Failed to get user stats locally: {e}")
            return None
    
    def _get_top_users_local(self, limit: int) -> List[UserStats]:
        """Get top users from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            stats = [UserStats(**item) for item in data if item.get('type') == 'user_stats']
            # Sort by total cost descending
            stats.sort(key=lambda x: x.totalCostUsd, reverse=True)
            return stats[:limit]
        except Exception as e:
            logger.error(f"Failed to get top users locally: {e}")
            return []
    
    def _get_blocked_users_local(self) -> List[UserStats]:
        """Get blocked users from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            return [UserStats(**item) for item in data 
                   if item.get('type') == 'user_stats' and item.get('isBlocked') == True]
        except Exception as e:
            logger.error(f"Failed to get blocked users locally: {e}")
            return []
    
    def _get_personality_config_local(self, personality_name: str) -> Optional[PersonalityConfig]:
        """Get personality config from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            for item in data:
                if item.get('personalityName') == personality_name and item.get('type') == 'personality_config':
                    return PersonalityConfig(**item)
            return None
        except Exception as e:
            logger.error(f"Failed to get personality config locally: {e}")
            return None
    
    def _get_all_personalities_local(self) -> List[PersonalityConfig]:
        """Get all personalities from local storage"""
        try:
            data = self._load_from_local_file(self.conversations_path)
            return [PersonalityConfig(**item) for item in data 
                   if item.get('type') == 'personality_config' and item.get('isActive') == True]
        except Exception as e:
            logger.error(f"Failed to get all personalities locally: {e}")
            return []
    
    def _save_enhanced_text_local(self, text: EnhancedSpiritualText) -> bool:
        """Save enhanced text to local spiritual-texts.json"""
        try:
            # Load existing spiritual texts
            data = self._load_from_local_file(self.spiritual_texts_path)
            
            # Add new enhanced text
            data.append(asdict(text))
            
            # Save back to file
            self._save_to_local_file(self.spiritual_texts_path, data)
            
            logger.info(f"💾 Saved enhanced spiritual text locally: {text.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save enhanced text locally: {e}")
            return False
    
    def _get_texts_by_personality_local(self, personality: str, limit: int) -> List[EnhancedSpiritualText]:
        """Get texts by personality from local storage"""
        try:
            data = self._load_from_local_file(self.spiritual_texts_path)
            texts = [EnhancedSpiritualText(**item) for item in data 
                    if item.get('personality') == personality and item.get('type') == 'spiritual_text']
            return texts[:limit]
        except Exception as e:
            logger.error(f"Failed to get texts by personality locally: {e}")
            return []
    
    def _get_texts_by_namespace_local(self, namespace: str, limit: int) -> List[EnhancedSpiritualText]:
        """Get texts by namespace from local storage"""
        try:
            data = self._load_from_local_file(self.spiritual_texts_path)
            texts = [EnhancedSpiritualText(**item) for item in data 
                    if item.get('vectorNamespace') == namespace and item.get('type') == 'spiritual_text']
            return texts[:limit]
        except Exception as e:
            logger.error(f"Failed to get texts by namespace locally: {e}")
            return []

# Global database service instance aligned with production setup
# Database: vimarsh-db
# Containers: spiritual-texts, conversations
db_service = DatabaseService()
