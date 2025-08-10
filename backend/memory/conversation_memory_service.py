"""
Conversation Memory Service - Phase 2 Implementation
====================================================

Advanced memory system providing per-user-per-personality conversation storage,
semantic memory management, and privacy-compliant data handling.

Features:
- Per-user-per-personality memory isolation
- Episodic memory (conversation milestones)
- Semantic memory (evolving user principles)
- Memory compression with rolling summaries
- Privacy safeguards and PII scrubbing
- Cross-conversation semantic search

Architecture:
- Partition key isolation: user_id|personality_id
- Memory types: episodic, semantic, compressed
- Storage limits: 1KB active + 25KB archived per personality
- Privacy: Automated PII detection and scrubbing
"""

import json
import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Azure Cosmos DB imports
try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceNotFoundError
    cosmos_available = True
except ImportError:
    cosmos_available = False
    CosmosClient = None
    PartitionKey = None
    print("⚠️ Cosmos DB SDK not available - using in-memory storage")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memory stored in the system."""
    EPISODIC = "episodic"        # Specific conversation events
    SEMANTIC = "semantic"        # Learned principles and preferences
    COMPRESSED = "compressed"    # Rolling summaries of older conversations
    MILESTONE = "milestone"      # Important conversation moments

@dataclass
class MemoryEntry:
    """Individual memory entry with metadata."""
    id: str
    user_id: str
    personality_id: str
    memory_type: MemoryType
    content: str
    importance_score: float
    created_at: datetime
    last_accessed: datetime
    tags: List[str]
    context: Dict[str, Any]
    compressed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary for storage."""
        data = asdict(self)
        data['memory_type'] = self.memory_type.value
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create memory entry from dictionary."""
        data['memory_type'] = MemoryType(data['memory_type'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)

@dataclass
class ConversationSummary:
    """Summary of a conversation for memory compression."""
    conversation_id: str
    user_id: str
    personality_id: str
    summary: str
    key_insights: List[str]
    topics_discussed: List[str]
    emotional_tone: str
    importance_score: float
    created_at: datetime
    message_count: int

class PIIDetector:
    """Privacy-first PII detection and scrubbing system."""
    
    def __init__(self):
        # Enhanced regex patterns for common PII with better coverage
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            # Enhanced phone pattern to catch more formats including business numbers
            'phone': re.compile(r'\b(?:\d{3}[-.]?\d{3}[-.]?\d{4}|\d{3}[-.]?[A-Z]{4}[-.]?[A-Z]{3}|555-[A-Z]{4}-[A-Z]{3})\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            # Enhanced credit card pattern to catch partial numbers and references
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}|\d{4}(?:\s*ending\s*in\s*|\s*\*+\s*)\d{4}|ending\s+in\s+\d{4}|card\s+(?:number\s+)?(?:ending\s+in\s+)?\d{4})\b', re.IGNORECASE),
            'address': re.compile(r'\b\d+\s+[A-Za-z\s]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b', re.IGNORECASE)
        }
    
    def detect_pii(self, text: str) -> List[Dict[str, str]]:
        """Detect PII in text and return matches with types."""
        detected_pii = []
        for pii_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                detected_pii.append({
                    'type': pii_type,
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        return detected_pii
    
    def scrub_pii(self, text: str) -> str:
        """Remove PII from text, replacing with generic placeholders."""
        scrubbed_text = text
        replacements = {
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'ssn': '[SSN_REDACTED]',
            'credit_card': '[CARD_REDACTED]',
            'address': '[ADDRESS_REDACTED]'
        }
        
        for pii_type, pattern in self.patterns.items():
            scrubbed_text = pattern.sub(replacements[pii_type], scrubbed_text)
        
        return scrubbed_text

class MemoryCompressor:
    """Intelligent memory compression for storage optimization with improved scalability."""
    
    def __init__(self, max_active_size: int = 2048, max_archived_size: int = 51200):
        self.max_active_size = max_active_size  # 2KB active memory (increased)
        self.max_archived_size = max_archived_size  # 50KB archived memory (increased)
        self.compression_threshold = 20  # Compress when more than 20 memories (was 10)
    
    def should_compress(self, memories: List[MemoryEntry]) -> bool:
        """Determine if memory compression is needed with improved thresholds."""
        if len(memories) < self.compression_threshold:
            return False
        
        total_size = sum(len(m.content.encode('utf-8')) for m in memories)
        return total_size > self.max_active_size or len(memories) > 50
    
    def compress_memories(self, memories: List[MemoryEntry]) -> List[MemoryEntry]:
        """Compress older memories into summaries."""
        if not memories:
            return []
        
        # Sort by last accessed date (oldest first)
        sorted_memories = sorted(memories, key=lambda m: m.last_accessed)
        
        # Keep recent high-importance memories active
        active_memories = []
        compress_candidates = []
        
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for memory in sorted_memories:
            if (memory.last_accessed > cutoff_date and 
                memory.importance_score > 0.7):
                active_memories.append(memory)
            else:
                compress_candidates.append(memory)
        
        # Compress candidates into summary memories
        if compress_candidates:
            compressed_memory = self._create_compressed_summary(compress_candidates)
            active_memories.append(compressed_memory)
        
        return active_memories
    
    def _create_compressed_summary(self, memories: List[MemoryEntry]) -> MemoryEntry:
        """Create a compressed summary from multiple memories."""
        # Extract key themes and insights
        all_content = " ".join([m.content for m in memories])
        all_tags = list(set([tag for m in memories for tag in m.tags]))
        
        # Create summary (simplified - in production would use LLM)
        summary = f"Summary of {len(memories)} memories: " + all_content[:200] + "..."
        
        # Use first memory's metadata as base
        base_memory = memories[0]
        
        return MemoryEntry(
            id=str(uuid.uuid4()),
            user_id=base_memory.user_id,
            personality_id=base_memory.personality_id,
            memory_type=MemoryType.COMPRESSED,
            content=summary,
            importance_score=max(m.importance_score for m in memories),
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            tags=all_tags,
            context={
                'compressed_from': len(memories),
                'original_memories': [m.id for m in memories],
                'date_range': {
                    'start': min(m.created_at for m in memories).isoformat(),
                    'end': max(m.created_at for m in memories).isoformat()
                }
            },
            compressed=True
        )

class ConversationMemoryService:
    """
    Advanced conversation memory system for personalized spiritual guidance.
    
    Provides per-user-per-personality memory with privacy safeguards,
    automatic compression, and semantic search capabilities.
    """
    
    def __init__(self, cosmos_client: Optional[Any] = None, database_name: str = "vimarsh-db"):
        self.cosmos_client = cosmos_client
        self.database_name = database_name
        self.container_name = "conversation-memory"
        
        # Initialize components
        self.pii_detector = PIIDetector()
        self.compressor = MemoryCompressor()
        
        # In-memory storage for development/testing
        self.memory_store: Dict[str, List[MemoryEntry]] = {}
        
        # Initialize database connection
        self._initialize_database()
        
        logger.info("🧠 Conversation Memory Service initialized")
    
    def _initialize_database(self) -> None:
        """Initialize Cosmos DB container for memory storage."""
        self.container = None  # Initialize container attribute
        
        if not cosmos_available or not self.cosmos_client:
            logger.warning("⚠️ Using in-memory storage - Cosmos DB not available")
            return
        
        try:
            # Get or create database
            database = self.cosmos_client.create_database_if_not_exists(self.database_name)
            
            # Create container with partition key for user-personality isolation
            container = database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/partition_key"),
                offer_throughput=400
            )
            
            self.container = container
            logger.info(f"✅ Memory container initialized: {self.container_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {str(e)}")
            logger.info("📝 Falling back to in-memory storage")
            self.container = None
    
    def _get_partition_key(self, user_id: str, personality_id: str) -> str:
        """Generate partition key for user-personality isolation."""
        return f"{user_id}|{personality_id}"
    
    def _calculate_importance_score(self, content: str, context: Dict[str, Any]) -> float:
        """Calculate importance score for memory prioritization."""
        score = 0.5  # Base score
        
        # Increase score for longer, more detailed content
        if len(content) > 100:
            score += 0.1
        if len(content) > 300:
            score += 0.1
        
        # Increase score for emotional content
        emotional_keywords = ['feel', 'emotion', 'happy', 'sad', 'anxious', 'peaceful', 'grateful']
        if any(keyword in content.lower() for keyword in emotional_keywords):
            score += 0.2
        
        # Increase score for spiritual insights
        spiritual_keywords = ['wisdom', 'insight', 'understanding', 'growth', 'peace', 'purpose']
        if any(keyword in content.lower() for keyword in spiritual_keywords):
            score += 0.2
        
        # Increase score for questions (shows engagement)
        if '?' in content:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content for categorization."""
        tags = []
        
        # Topic-based tags
        topics = {
            'relationships': ['love', 'relationship', 'family', 'friend'],
            'career': ['work', 'job', 'career', 'profession'],
            'spirituality': ['spiritual', 'meditation', 'prayer', 'divine'],
            'health': ['health', 'wellness', 'exercise', 'healing'],
            'growth': ['growth', 'learning', 'development', 'improvement'],
            'emotions': ['emotion', 'feeling', 'mood', 'anxiety', 'peace']
        }
        
        content_lower = content.lower()
        for topic, keywords in topics.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(topic)
        
        # Sentiment tags
        if any(word in content_lower for word in ['happy', 'joy', 'grateful', 'blessed']):
            tags.append('positive')
        if any(word in content_lower for word in ['sad', 'anxious', 'worried', 'struggling']):
            tags.append('challenging')
        
        return tags
    
    async def store_conversation_memory(
        self,
        user_id: str,
        personality_id: str,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a new memory entry with privacy safeguards."""
        try:
            # Scrub PII from content
            scrubbed_content = self.pii_detector.scrub_pii(content)
            
            # Create memory entry
            memory_entry = MemoryEntry(
                id=str(uuid.uuid4()),
                user_id=user_id,
                personality_id=personality_id,
                memory_type=memory_type,
                content=scrubbed_content,
                importance_score=self._calculate_importance_score(scrubbed_content, context or {}),
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                tags=self._extract_tags(scrubbed_content),
                context=context or {},
                compressed=False
            )
            
            # Store in database or memory
            if self.container:
                await self._store_in_cosmos(memory_entry)
            else:
                await self._store_in_memory(memory_entry)
            
            # Check if compression is needed
            await self._check_and_compress_memory(user_id, personality_id)
            
            logger.info(f"💾 Stored memory for {user_id}|{personality_id}: {memory_entry.id}")
            return memory_entry.id
            
        except Exception as e:
            logger.error(f"❌ Failed to store memory: {str(e)}")
            raise
    
    async def _store_in_cosmos(self, memory_entry: MemoryEntry) -> None:
        """Store memory entry in Cosmos DB."""
        partition_key = self._get_partition_key(memory_entry.user_id, memory_entry.personality_id)
        
        document = memory_entry.to_dict()
        document['partition_key'] = partition_key
        
        self.container.create_item(body=document)
    
    async def _store_in_memory(self, memory_entry: MemoryEntry) -> None:
        """Store memory entry in in-memory storage."""
        partition_key = self._get_partition_key(memory_entry.user_id, memory_entry.personality_id)
        
        if partition_key not in self.memory_store:
            self.memory_store[partition_key] = []
        
        self.memory_store[partition_key].append(memory_entry)
    
    async def retrieve_memories(
        self,
        user_id: str,
        personality_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """Retrieve memories for a specific user-personality combination."""
        try:
            partition_key = self._get_partition_key(user_id, personality_id)
            
            if self.container:
                memories = await self._retrieve_from_cosmos(partition_key, memory_types, limit, min_importance)
            else:
                memories = await self._retrieve_from_memory(partition_key, memory_types, limit, min_importance)
            
            # Update last accessed time
            for memory in memories:
                memory.last_accessed = datetime.now()
            
            logger.info(f"🔍 Retrieved {len(memories)} memories for {user_id}|{personality_id}")
            return memories
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve memories: {str(e)}")
            return []
    
    async def _retrieve_from_cosmos(
        self,
        partition_key: str,
        memory_types: Optional[List[MemoryType]],
        limit: int,
        min_importance: float
    ) -> List[MemoryEntry]:
        """Retrieve memories from Cosmos DB."""
        query = f"SELECT * FROM c WHERE c.partition_key = @partition_key"
        parameters = [{"name": "@partition_key", "value": partition_key}]
        
        if memory_types:
            type_values = [t.value for t in memory_types]
            query += f" AND c.memory_type IN ({','.join(['@type' + str(i) for i in range(len(type_values))])})"
            for i, t in enumerate(type_values):
                parameters.append({"name": f"@type{i}", "value": t})
        
        if min_importance > 0:
            query += " AND c.importance_score >= @min_importance"
            parameters.append({"name": "@min_importance", "value": min_importance})
        
        query += " ORDER BY c.last_accessed DESC"
        
        items = list(self.container.query_items(
            query=query,
            parameters=parameters,
            max_item_count=limit
        ))
        
        return [MemoryEntry.from_dict(item) for item in items]
    
    async def _retrieve_from_memory(
        self,
        partition_key: str,
        memory_types: Optional[List[MemoryType]],
        limit: int,
        min_importance: float
    ) -> List[MemoryEntry]:
        """Retrieve memories from in-memory storage."""
        if partition_key not in self.memory_store:
            return []
        
        memories = self.memory_store[partition_key]
        
        # Filter by memory types
        if memory_types:
            memories = [m for m in memories if m.memory_type in memory_types]
        
        # Filter by importance
        memories = [m for m in memories if m.importance_score >= min_importance]
        
        # Sort by last accessed (most recent first)
        memories.sort(key=lambda m: m.last_accessed, reverse=True)
        
        return memories[:limit]
    
    async def _check_and_compress_memory(self, user_id: str, personality_id: str) -> None:
        """Check if memory compression is needed and perform if necessary."""
        try:
            memories = await self.retrieve_memories(user_id, personality_id, limit=1000)
            
            if self.compressor.should_compress(memories):
                compressed_memories = self.compressor.compress_memories(memories)
                
                # Replace memories with compressed version
                await self._replace_memories(user_id, personality_id, compressed_memories)
                
                logger.info(f"🗜️ Compressed {len(memories)} memories to {len(compressed_memories)} for {user_id}|{personality_id}")
        
        except Exception as e:
            logger.error(f"❌ Memory compression failed: {str(e)}")
    
    async def _replace_memories(
        self,
        user_id: str,
        personality_id: str,
        new_memories: List[MemoryEntry]
    ) -> None:
        """Replace all memories for a user-personality with new compressed memories."""
        partition_key = self._get_partition_key(user_id, personality_id)
        
        if self.container:
            # Delete existing memories (in production, would use bulk operations)
            query = "SELECT c.id FROM c WHERE c.partition_key = @partition_key"
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@partition_key", "value": partition_key}]
            ))
            
            for item in items:
                self.container.delete_item(item=item['id'], partition_key=partition_key)
            
            # Store new memories
            for memory in new_memories:
                await self._store_in_cosmos(memory)
        else:
            # Replace in-memory storage
            self.memory_store[partition_key] = new_memories
    
    async def search_memories(
        self,
        user_id: str,
        personality_id: str,
        query: str,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """Search memories using enhanced text matching with compound term support."""
        try:
            all_memories = await self.retrieve_memories(user_id, personality_id, limit=1000)
            
            # Enhanced search algorithm
            query_lower = query.lower()
            query_words = query_lower.split()
            matching_memories = []
            
            for memory in all_memories:
                content_lower = memory.content.lower()
                tags_lower = ' '.join(memory.tags).lower()
                
                # Calculate relevance score
                relevance_score = 0.0
                
                # Exact phrase match (highest priority)
                if query_lower in content_lower:
                    relevance_score += 2.0
                
                # Individual word matching
                for word in query_words:
                    if word in content_lower:
                        relevance_score += 0.5
                    # Partial word matching for compound terms
                    elif any(word in content_word for content_word in content_lower.split()):
                        relevance_score += 0.3
                
                # Tag matching
                for tag in memory.tags:
                    if any(word in tag.lower() for word in query_words):
                        relevance_score += 0.8
                    elif query_lower in tag.lower():
                        relevance_score += 1.2
                
                # Context matching
                context_text = ' '.join(str(v) for v in memory.context.values() if isinstance(v, str))
                if query_lower in context_text.lower():
                    relevance_score += 0.4
                
                # Word overlap bonus
                query_words_set = set(query_words)
                content_words_set = set(content_lower.split())
                overlap = len(query_words_set.intersection(content_words_set))
                if overlap > 0:
                    relevance_score += overlap * 0.2
                
                # Compound term handling (e.g., "space time")
                if len(query_words) > 1:
                    compound_matches = 0
                    content_words = content_lower.split()
                    for i in range(len(content_words) - len(query_words) + 1):
                        window = ' '.join(content_words[i:i + len(query_words)])
                        if all(word in window for word in query_words):
                            compound_matches += 1
                    relevance_score += compound_matches * 0.6
                
                if relevance_score > 0:
                    memory.context['relevance_score'] = relevance_score
                    matching_memories.append(memory)
            
            # Sort by relevance score
            matching_memories.sort(
                key=lambda m: m.context.get('relevance_score', 0),
                reverse=True
            )
            
            logger.info(f"🔍 Found {len(matching_memories)} memories matching '{query}' for {user_id}|{personality_id}")
            return matching_memories[:limit]
            
        except Exception as e:
            logger.error(f"❌ Memory search failed: {str(e)}")
            return []
    
    async def get_memory_statistics(self, user_id: str, personality_id: str) -> Dict[str, Any]:
        """Get comprehensive memory statistics for a user-personality combination."""
        try:
            memories = await self.retrieve_memories(user_id, personality_id, limit=1000)
            
            if not memories:
                return {
                    'total_memories': 0,
                    'total_size_bytes': 0,
                    'memory_types': {},
                    'tags': {},
                    'average_importance': 0.0,
                    'oldest_memory': None,
                    'newest_memory': None
                }
            
            # Calculate statistics
            total_size = sum(len(m.content.encode('utf-8')) for m in memories)
            memory_type_counts = {}
            tag_counts = {}
            
            for memory in memories:
                # Count memory types
                memory_type = memory.memory_type.value
                memory_type_counts[memory_type] = memory_type_counts.get(memory_type, 0) + 1
                
                # Count tags
                for tag in memory.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            stats = {
                'total_memories': len(memories),
                'total_size_bytes': total_size,
                'total_size_kb': round(total_size / 1024, 2),
                'memory_types': memory_type_counts,
                'tags': tag_counts,
                'average_importance': round(sum(m.importance_score for m in memories) / len(memories), 2),
                'oldest_memory': min(memories, key=lambda m: m.created_at).created_at.isoformat(),
                'newest_memory': max(memories, key=lambda m: m.created_at).created_at.isoformat(),
                'compressed_memories': sum(1 for m in memories if m.compressed),
                'storage_efficiency': {
                    'within_active_limit': total_size <= 1024,
                    'within_archived_limit': total_size <= 25600,
                    'compression_needed': total_size > 1024
                }
            }
            
            logger.info(f"📊 Memory statistics calculated for {user_id}|{personality_id}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate memory statistics: {str(e)}")
            return {}
    
    async def delete_user_memories(self, user_id: str, personality_id: Optional[str] = None) -> int:
        """Delete memories for a user (optionally for specific personality)."""
        try:
            deleted_count = 0
            
            if personality_id:
                # Delete for specific personality
                partition_key = self._get_partition_key(user_id, personality_id)
                deleted_count = await self._delete_partition_memories(partition_key)
            else:
                # Delete for all personalities of the user
                if self.container:
                    # Query for all user memories across personalities
                    query = "SELECT c.partition_key FROM c WHERE STARTSWITH(c.partition_key, @user_prefix)"
                    user_prefix = f"{user_id}|"
                    
                    items = list(self.container.query_items(
                        query=query,
                        parameters=[{"name": "@user_prefix", "value": user_prefix}]
                    ))
                    
                    for item in items:
                        count = await self._delete_partition_memories(item['partition_key'])
                        deleted_count += count
                else:
                    # Delete from in-memory storage
                    user_prefix = f"{user_id}|"
                    keys_to_delete = [k for k in self.memory_store.keys() if k.startswith(user_prefix)]
                    
                    for key in keys_to_delete:
                        deleted_count += len(self.memory_store[key])
                        del self.memory_store[key]
            
            logger.info(f"🗑️ Deleted {deleted_count} memories for user {user_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to delete memories: {str(e)}")
            return 0
    
    async def _delete_partition_memories(self, partition_key: str) -> int:
        """Delete all memories for a specific partition key."""
        if self.container:
            query = "SELECT c.id FROM c WHERE c.partition_key = @partition_key"
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@partition_key", "value": partition_key}]
            ))
            
            for item in items:
                self.container.delete_item(item=item['id'], partition_key=partition_key)
            
            return len(items)
        else:
            if partition_key in self.memory_store:
                count = len(self.memory_store[partition_key])
                del self.memory_store[partition_key]
                return count
            return 0

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_memory_service():
        """Test the conversation memory service."""
        print("🧪 Testing Conversation Memory Service...")
        
        # Initialize service
        memory_service = ConversationMemoryService()
        
        # Test data
        user_id = "test_user_123"
        personality_id = "krishna"
        
        # Test storing memories
        print("\n📝 Testing memory storage...")
        
        memories_to_store = [
            ("I'm struggling with anxiety about my career path. How can I find peace?", MemoryType.EPISODIC),
            ("The guidance about focusing on dharma really resonated with me.", MemoryType.SEMANTIC),
            ("I meditated for 20 minutes today and felt more centered.", MemoryType.MILESTONE),
            ("My email is john@example.com and my phone is 555-123-4567", MemoryType.EPISODIC)  # Test PII scrubbing
        ]
        
        stored_ids = []
        for content, memory_type in memories_to_store:
            memory_id = await memory_service.store_conversation_memory(
                user_id=user_id,
                personality_id=personality_id,
                content=content,
                memory_type=memory_type,
                context={"test": True}
            )
            stored_ids.append(memory_id)
            print(f"  ✅ Stored memory: {memory_id[:8]}...")
        
        # Test retrieving memories
        print("\n🔍 Testing memory retrieval...")
        retrieved_memories = await memory_service.retrieve_memories(user_id, personality_id)
        
        for memory in retrieved_memories:
            print(f"  📋 {memory.memory_type.value}: {memory.content[:50]}...")
            print(f"     Tags: {memory.tags}, Importance: {memory.importance_score}")
        
        # Test memory search
        print("\n🔍 Testing memory search...")
        search_results = await memory_service.search_memories(user_id, personality_id, "anxiety career")
        
        for memory in search_results:
            relevance = memory.context.get('relevance_score', 0)
            print(f"  🎯 Relevance {relevance}: {memory.content[:50]}...")
        
        # Test memory statistics
        print("\n📊 Testing memory statistics...")
        stats = await memory_service.get_memory_statistics(user_id, personality_id)
        
        print(f"  📈 Total memories: {stats['total_memories']}")
        print(f"  💾 Total size: {stats['total_size_kb']} KB")
        print(f"  🏷️ Tags: {stats['tags']}")
        print(f"  ⭐ Average importance: {stats['average_importance']}")
        print(f"  🗜️ Storage efficiency: {stats['storage_efficiency']}")
        
        # Test PII detection
        print("\n🔒 Testing PII detection...")
        test_text = "My email is john@example.com and my phone is 555-123-4567"
        pii_detector = PIIDetector()
        detected_pii = pii_detector.detect_pii(test_text)
        scrubbed_text = pii_detector.scrub_pii(test_text)
        
        print(f"  🔍 Original: {test_text}")
        print(f"  🛡️ Scrubbed: {scrubbed_text}")
        print(f"  📋 Detected PII: {detected_pii}")
        
        print("\n🎉 Conversation Memory Service testing completed!")
    
    # Run tests
    asyncio.run(test_memory_service())
