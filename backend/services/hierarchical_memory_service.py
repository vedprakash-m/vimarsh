"""
Hierarchical Memory Service for Vimarsh

This service implements the 4-layer hierarchical memory architecture:
- Layer 1: Working Memory (active conversation + hot context, 16K tokens)
- Layer 2: Core Memory (user profile + personality relationships, persistent)
- Layer 3: Episodic Memory (session summaries + reflection insights, 90 days)
- Layer 4: Semantic Archive (full history with vector embeddings, 1 year)

Based on research from:
- MemGPT (UC Berkeley): Virtual memory management for LLMs
- Generative Agents (Stanford): Memory stream + reflection + importance scoring
- LangGraph: Persistent checkpointing with semantic retrieval
- Letta: Agentic context engineering
"""

import logging
import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json

# Azure Cosmos DB
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

# Azure OpenAI for embeddings (with Gemini fallback for generation)
try:
    from services.azure_openai_embedding_service import AzureOpenAIEmbeddingService
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

import google.generativeai as genai

# Local models
from models.memory_models import (
    MemoryProfile,
    RelationshipState,
    RelationshipDepth,
    ConversationMessage,
    SessionSummary,
    WorkingMemoryContext,
    MemorySearchQuery,
    MemorySearchResult,
    EmotionalTone,
    MemoryImportance
)

logger = logging.getLogger(__name__)


class HierarchicalMemoryService:
    """
    Core service for managing the 4-layer hierarchical memory system.
    
    Token Budgets:
    - Working Memory: 16K tokens total
    - Core Memory: 4K tokens (user profile + current relationship)
    - Episodic Memory: 8K tokens (session summaries + insights)
    - Semantic Archive: On-demand retrieval
    
    Persistence:
    - Cosmos DB containers: memory_profiles, conversation_history, 
      relationship_states, session_summaries
    """
    
    # Token budget configuration
    WORKING_MEMORY_MAX_TOKENS = 16000
    CORE_MEMORY_TOKEN_BUDGET = 4000
    EPISODIC_MEMORY_TOKEN_BUDGET = 8000
    RAG_CONTEXT_TOKEN_BUDGET = 4000
    
    # Retention configuration
    EPISODIC_MEMORY_RETENTION_DAYS = 90
    SEMANTIC_ARCHIVE_RETENTION_DAYS = 365
    
    # Importance scoring weights
    IMPORTANCE_WEIGHTS = {
        "emotional_intensity": 0.25,
        "novelty": 0.20,
        "personal_revelation": 0.25,
        "user_question": 0.15,
        "user_feedback": 0.15
    }
    
    # Memory decay parameters
    DECAY_RATE = 0.05  # 5% decay per day
    RECENCY_BOOST_WINDOW_HOURS = 24
    
    def __init__(self):
        """Initialize the hierarchical memory service."""
        self.cosmos_client: Optional[CosmosClient] = None
        self.database = None
        self.containers: Dict[str, Any] = {}
        
        # In-memory session cache for working memory
        self.working_memory_cache: Dict[str, WorkingMemoryContext] = {}
        
        # Initialize Gemini for embeddings and reflections
        self._init_gemini()
        
        # Initialize Cosmos DB connection
        self._init_cosmos_db()
        
        logger.info("🧠 HierarchicalMemoryService initialized")
    
    def _init_gemini(self) -> None:
        """Initialize Google Gemini for embeddings and reflection generation."""
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.embedding_model = "gemini-embedding-001"  # Migrated from deprecated text-embedding-004
            self.embedding_output_dimensionality = 768  # MRL dimension for Cosmos DB compatibility
            self.generation_model = genai.GenerativeModel("gemini-2.0-flash")
            logger.info("✅ Gemini initialized for memory service (embedding: gemini-embedding-001)")
        else:
            logger.warning("⚠️ Gemini API key not found - embeddings disabled")
            self.embedding_model = None
            self.embedding_output_dimensionality = 768
            self.generation_model = None
    
    def _init_cosmos_db(self) -> None:
        """Initialize Cosmos DB connection and containers."""
        try:
            endpoint = os.environ.get("COSMOS_ENDPOINT")
            key = os.environ.get("COSMOS_KEY")
            database_name = os.environ.get("COSMOS_DATABASE", "vimarsh-db")
            
            if not endpoint or not key:
                logger.warning("⚠️ Cosmos DB credentials not found - using in-memory only")
                return
            
            self.cosmos_client = CosmosClient(endpoint, key)
            self.database = self.cosmos_client.get_database_client(database_name)
            
            # Initialize containers
            container_configs = [
                ("memory_profiles", "/user_id"),
                ("conversation_history", "/user_id"),
                ("relationship_states", "/user_id"),
                ("session_summaries", "/user_id")
            ]
            
            for container_name, partition_key in container_configs:
                try:
                    self.containers[container_name] = self.database.get_container_client(container_name)
                    logger.info(f"✅ Container '{container_name}' connected")
                except Exception as e:
                    logger.warning(f"⚠️ Container '{container_name}' not found, will create on first use: {e}")
            
            logger.info("✅ Cosmos DB initialized for memory service")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {e}")
    
    # =========================================================================
    # LAYER 2: CORE MEMORY - User Profile & Relationship Management
    # =========================================================================
    
    async def get_or_create_memory_profile(self, user_id: str) -> MemoryProfile:
        """
        Get existing memory profile or create new one for first-time user.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            MemoryProfile object
        """
        try:
            if "memory_profiles" not in self.containers:
                logger.warning("Memory profiles container not available, returning new profile")
                return MemoryProfile.create_new(user_id)
            
            container = self.containers["memory_profiles"]
            
            # Query for existing profile
            query = "SELECT * FROM c WHERE c.user_id = @user_id"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                partition_key=user_id
            ))
            
            if items:
                logger.info(f"📖 Retrieved memory profile for user {user_id[:8]}...")
                return MemoryProfile.from_dict(items[0])
            else:
                # Create new profile
                profile = MemoryProfile.create_new(user_id)
                container.create_item(body=profile.to_dict())
                logger.info(f"🆕 Created new memory profile for user {user_id[:8]}...")
                return profile
                
        except Exception as e:
            logger.error(f"❌ Error getting/creating memory profile: {e}")
            return MemoryProfile.create_new(user_id)
    
    async def update_memory_profile(self, profile: MemoryProfile) -> bool:
        """
        Update an existing memory profile.
        
        Args:
            profile: The MemoryProfile to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if "memory_profiles" not in self.containers:
                return False
            
            profile.updated_at = datetime.utcnow()
            container = self.containers["memory_profiles"]
            container.upsert_item(body=profile.to_dict())
            logger.info(f"✅ Updated memory profile for user {profile.user_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating memory profile: {e}")
            return False
    
    async def get_or_create_relationship(
        self, 
        user_id: str, 
        personality_id: str
    ) -> RelationshipState:
        """
        Get existing relationship state or create new one.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            
        Returns:
            RelationshipState object
        """
        try:
            if "relationship_states" not in self.containers:
                return RelationshipState.create_new(user_id, personality_id)
            
            container = self.containers["relationship_states"]
            
            # Query for existing relationship
            query = """
                SELECT * FROM c 
                WHERE c.user_id = @user_id AND c.personality_id = @personality_id
            """
            parameters = [
                {"name": "@user_id", "value": user_id},
                {"name": "@personality_id", "value": personality_id}
            ]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                partition_key=user_id
            ))
            
            if items:
                logger.info(f"📖 Retrieved relationship: {user_id[:8]}... ↔ {personality_id}")
                return RelationshipState.from_dict(items[0])
            else:
                # Create new relationship
                relationship = RelationshipState.create_new(user_id, personality_id)
                container.create_item(body=relationship.to_dict())
                logger.info(f"🆕 Created new relationship: {user_id[:8]}... ↔ {personality_id}")
                return relationship
                
        except Exception as e:
            logger.error(f"❌ Error getting/creating relationship: {e}")
            return RelationshipState.create_new(user_id, personality_id)
    
    async def update_relationship(self, relationship: RelationshipState) -> bool:
        """
        Update an existing relationship state.
        
        Args:
            relationship: The RelationshipState to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if "relationship_states" not in self.containers:
                return False
            
            container = self.containers["relationship_states"]
            container.upsert_item(body=relationship.to_dict())
            logger.info(f"✅ Updated relationship: {relationship.user_id[:8]}... ↔ {relationship.personality_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating relationship: {e}")
            return False
    
    async def get_all_relationships(self, user_id: str) -> List[RelationshipState]:
        """
        Get all personality relationships for a user.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            List of RelationshipState objects
        """
        try:
            if "relationship_states" not in self.containers:
                return []
            
            container = self.containers["relationship_states"]
            query = "SELECT * FROM c WHERE c.user_id = @user_id"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                partition_key=user_id
            ))
            
            return [RelationshipState.from_dict(item) for item in items]
            
        except Exception as e:
            logger.error(f"❌ Error getting relationships: {e}")
            return []
    
    # =========================================================================
    # LAYER 4: SEMANTIC ARCHIVE - Conversation History Storage
    # =========================================================================
    
    async def store_message(
        self,
        user_id: str,
        personality_id: str,
        session_id: str,
        role: str,
        content: str,
        generate_embedding: bool = True
    ) -> ConversationMessage:
        """
        Store a conversation message in the semantic archive.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            session_id: The current session identifier
            role: "user" or "assistant"
            content: The message content
            generate_embedding: Whether to generate vector embedding
            
        Returns:
            The created ConversationMessage
        """
        try:
            # Create message
            message = ConversationMessage.create_new(
                user_id=user_id,
                personality_id=personality_id,
                session_id=session_id,
                role=role,
                content=content
            )
            
            # Calculate importance score
            message.importance_score, message.importance_factors = await self._calculate_importance(
                content, role
            )
            
            # Extract metadata
            message.metadata = await self._extract_message_metadata(content, role)
            
            # Generate embedding if enabled
            if generate_embedding and self.embedding_model:
                message.embedding = await self._generate_embedding(content)
            
            # Persist to Cosmos DB
            if "conversation_history" in self.containers:
                container = self.containers["conversation_history"]
                container.create_item(body=message.to_dict())
                logger.info(f"💾 Stored message: {role} in session {session_id[:8]}...")
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Error storing message: {e}")
            # Return message even if storage fails
            return ConversationMessage.create_new(
                user_id=user_id,
                personality_id=personality_id,
                session_id=session_id,
                role=role,
                content=content
            )
    
    async def get_recent_messages(
        self,
        user_id: str,
        personality_id: str,
        limit: int = 20
    ) -> List[ConversationMessage]:
        """
        Get recent messages for a user-personality pair.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of ConversationMessage objects (newest first)
        """
        try:
            if "conversation_history" not in self.containers:
                return []
            
            container = self.containers["conversation_history"]
            query = """
                SELECT * FROM c 
                WHERE c.user_id = @user_id 
                AND c.personality_id = @personality_id
                AND c.archived = false
                ORDER BY c.timestamp DESC
                OFFSET 0 LIMIT @limit
            """
            parameters = [
                {"name": "@user_id", "value": user_id},
                {"name": "@personality_id", "value": personality_id},
                {"name": "@limit", "value": limit}
            ]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                partition_key=user_id
            ))
            
            return [ConversationMessage.from_dict(item) for item in items]
            
        except Exception as e:
            logger.error(f"❌ Error getting recent messages: {e}")
            return []
    
    async def semantic_search(
        self,
        query: MemorySearchQuery
    ) -> List[MemorySearchResult]:
        """
        Perform semantic search across conversation history.
        
        Args:
            query: MemorySearchQuery with search parameters
            
        Returns:
            List of MemorySearchResult objects ranked by relevance
        """
        try:
            if "conversation_history" not in self.containers or not self.embedding_model:
                return []
            
            # Generate query embedding
            query_embedding = await self._generate_embedding(query.query_text)
            if not query_embedding:
                return []
            
            container = self.containers["conversation_history"]
            
            # Build query
            cosmos_query = """
                SELECT * FROM c 
                WHERE c.user_id = @user_id
                AND c.importance_score >= @min_importance
            """
            parameters = [
                {"name": "@user_id", "value": query.user_id},
                {"name": "@min_importance", "value": query.min_importance_score}
            ]
            
            if query.personality_id:
                cosmos_query += " AND c.personality_id = @personality_id"
                parameters.append({"name": "@personality_id", "value": query.personality_id})
            
            if not query.include_archived:
                cosmos_query += " AND c.archived = false"
            
            # Execute query
            items = list(container.query_items(
                query=cosmos_query,
                parameters=parameters,
                partition_key=query.user_id
            ))
            
            # Calculate similarity scores
            results = []
            for item in items:
                message = ConversationMessage.from_dict(item)
                if message.embedding:
                    similarity = self._cosine_similarity(query_embedding, message.embedding)
                    
                    # Calculate relevance score (similarity + importance + recency)
                    recency_score = self._calculate_recency_score(message.timestamp)
                    relevance = (
                        similarity * 0.5 +
                        message.importance_score * 0.3 +
                        recency_score * 0.2
                    )
                    
                    results.append(MemorySearchResult(
                        message=message,
                        similarity_score=similarity,
                        relevance_score=relevance,
                        context_snippet=message.content[:200]
                    ))
            
            # Sort by relevance and return top results
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results[:query.max_results]
            
        except Exception as e:
            logger.error(f"❌ Error in semantic search: {e}")
            return []
    
    # =========================================================================
    # LAYER 3: EPISODIC MEMORY - Session Summaries & Reflections
    # =========================================================================
    
    async def create_session(
        self,
        user_id: str,
        personality_id: str
    ) -> SessionSummary:
        """
        Create a new session summary.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            
        Returns:
            New SessionSummary object
        """
        session_id = str(uuid.uuid4())
        session = SessionSummary.create_new(user_id, personality_id, session_id)
        
        if "session_summaries" in self.containers:
            try:
                container = self.containers["session_summaries"]
                container.create_item(body=session.to_dict())
                logger.info(f"🆕 Created session {session_id[:8]}...")
            except Exception as e:
                logger.error(f"❌ Error creating session: {e}")
        
        return session
    
    async def end_session(
        self,
        session: SessionSummary,
        messages: List[ConversationMessage]
    ) -> SessionSummary:
        """
        End a session and generate summary with reflections.
        
        Args:
            session: The SessionSummary to finalize
            messages: List of messages from the session
            
        Returns:
            Updated SessionSummary with summary and insights
        """
        try:
            session.end_time = datetime.utcnow()
            session.duration_minutes = int(
                (session.end_time - session.start_time).total_seconds() / 60
            )
            session.message_count = len(messages)
            session.user_message_count = len([m for m in messages if m.role == "user"])
            session.assistant_message_count = len([m for m in messages if m.role == "assistant"])
            
            if messages:
                session.avg_importance_score = sum(m.importance_score for m in messages) / len(messages)
                
                # Extract topics and questions
                session.topics = await self._extract_topics(messages)
                session.questions_asked = [
                    m.content for m in messages 
                    if m.role == "user" and m.metadata.get("has_question", False)
                ]
                
                # Track emotional arc
                session.emotional_arc = await self._track_emotional_arc(messages)
                if session.emotional_arc:
                    session.starting_emotion = session.emotional_arc[0].get("tone")
                    session.ending_emotion = session.emotional_arc[-1].get("tone")
                
                # Generate summary
                session.summary = await self._generate_session_summary(messages, session)
                
                # Generate key insights
                session.key_insights = await self._extract_key_insights(messages, session)
                
                # Generate reflection
                session.reflection = await self._generate_reflection(session)
                session.reflection_generated_at = datetime.utcnow()
                
                # Generate follow-up suggestions
                session.suggested_followups = await self._generate_followup_suggestions(session)
            
            # Persist to Cosmos DB
            if "session_summaries" in self.containers:
                container = self.containers["session_summaries"]
                container.upsert_item(body=session.to_dict())
                logger.info(f"✅ Finalized session {session.session_id[:8]}...")
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Error ending session: {e}")
            return session
    
    async def get_recent_sessions(
        self,
        user_id: str,
        personality_id: Optional[str] = None,
        limit: int = 5
    ) -> List[SessionSummary]:
        """
        Get recent session summaries.
        
        Args:
            user_id: The user's unique identifier
            personality_id: Optional - filter by personality
            limit: Maximum number of sessions to return
            
        Returns:
            List of SessionSummary objects (newest first)
        """
        try:
            if "session_summaries" not in self.containers:
                return []
            
            container = self.containers["session_summaries"]
            
            if personality_id:
                query = """
                    SELECT * FROM c 
                    WHERE c.user_id = @user_id 
                    AND c.personality_id = @personality_id
                    ORDER BY c.start_time DESC
                    OFFSET 0 LIMIT @limit
                """
                parameters = [
                    {"name": "@user_id", "value": user_id},
                    {"name": "@personality_id", "value": personality_id},
                    {"name": "@limit", "value": limit}
                ]
            else:
                query = """
                    SELECT * FROM c 
                    WHERE c.user_id = @user_id
                    ORDER BY c.start_time DESC
                    OFFSET 0 LIMIT @limit
                """
                parameters = [
                    {"name": "@user_id", "value": user_id},
                    {"name": "@limit", "value": limit}
                ]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                partition_key=user_id
            ))
            
            return [SessionSummary.from_dict(item) for item in items]
            
        except Exception as e:
            logger.error(f"❌ Error getting recent sessions: {e}")
            return []
    
    # =========================================================================
    # LAYER 1: WORKING MEMORY - Context Assembly
    # =========================================================================
    
    async def assemble_working_memory(
        self,
        user_id: str,
        personality_id: str,
        session_id: str,
        current_query: str,
        current_messages: List[Dict[str, str]]
    ) -> WorkingMemoryContext:
        """
        Assemble working memory context for current conversation.
        
        This is the main entry point for getting context for AI response generation.
        Optimizes token budget across all memory layers.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            session_id: The current session identifier
            current_query: The user's current query
            current_messages: Recent messages in current conversation
            
        Returns:
            WorkingMemoryContext with assembled context
        """
        try:
            # Create working memory context
            context = WorkingMemoryContext(
                user_id=user_id,
                personality_id=personality_id,
                session_id=session_id
            )
            
            # 1. Load core memory (user profile + relationship)
            profile = await self.get_or_create_memory_profile(user_id)
            relationship = await self.get_or_create_relationship(user_id, personality_id)
            
            context.user_profile_context = self._build_profile_context(profile)
            context.relationship_context = self._build_relationship_context(relationship)
            context.core_memory_tokens = self._estimate_tokens(
                context.user_profile_context + context.relationship_context
            )
            
            # 2. Load episodic memory (recent sessions)
            recent_sessions = await self.get_recent_sessions(user_id, personality_id, limit=3)
            context.recent_session_summaries = [
                {"summary": s.summary, "topics": s.topics, "date": s.start_time.isoformat()}
                for s in recent_sessions if s.summary
            ]
            
            # Extract relevant insights
            all_insights = []
            for session in recent_sessions:
                all_insights.extend(session.key_insights)
            context.relevant_past_insights = all_insights[:5]
            
            context.episodic_memory_tokens = self._estimate_tokens(
                json.dumps(context.recent_session_summaries) + 
                " ".join(context.relevant_past_insights)
            )
            
            # 3. Semantic search for relevant past conversations
            if current_query and self.embedding_model:
                search_query = MemorySearchQuery(
                    user_id=user_id,
                    query_text=current_query,
                    personality_id=personality_id,
                    max_results=3,
                    min_importance_score=0.4
                )
                search_results = await self.semantic_search(search_query)
                context.retrieved_memories = [
                    {"content": r.message.content, "relevance": r.relevance_score}
                    for r in search_results
                ]
                context.semantic_memory_tokens = self._estimate_tokens(
                    " ".join([m["content"] for m in context.retrieved_memories])
                )
            
            # 4. Add current conversation messages
            context.current_messages = current_messages
            context.current_conversation_tokens = self._estimate_tokens(
                " ".join([m.get("content", "") for m in current_messages])
            )
            
            # 5. Calculate context quality score
            context.context_quality_score = self._calculate_context_quality(context)
            context.assembled_at = datetime.utcnow()
            
            # Cache in working memory
            cache_key = f"{user_id}:{session_id}"
            self.working_memory_cache[cache_key] = context
            
            logger.info(
                f"🧠 Assembled working memory: {context.get_total_tokens()} tokens, "
                f"quality={context.context_quality_score:.2f}"
            )
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Error assembling working memory: {e}")
            # Return minimal context on error
            return WorkingMemoryContext(
                user_id=user_id,
                personality_id=personality_id,
                session_id=session_id,
                current_messages=current_messages
            )
    
    def _build_profile_context(self, profile: MemoryProfile) -> str:
        """Build context string from user profile."""
        parts = []
        
        if profile.discovered_interests:
            parts.append(f"User interests: {', '.join(profile.discovered_interests[:5])}")
        
        if profile.recurring_themes:
            parts.append(f"Recurring themes: {', '.join(profile.recurring_themes[:5])}")
        
        life_context = profile.life_context
        if life_context.get("primary_concerns"):
            parts.append(f"Primary concerns: {', '.join(life_context['primary_concerns'][:3])}")
        
        comm_style = profile.communication_style
        if comm_style.get("depth") == "deep":
            parts.append("Prefers deep, thoughtful responses")
        elif comm_style.get("depth") == "surface":
            parts.append("Prefers concise, direct responses")
        
        return " | ".join(parts) if parts else ""
    
    def _build_relationship_context(self, relationship: RelationshipState) -> str:
        """Build context string from relationship state."""
        parts = []
        
        depth_descriptions = {
            RelationshipDepth.STRANGER: "This is a new seeker",
            RelationshipDepth.ACQUAINTANCE: "We have had a few conversations",
            RelationshipDepth.FAMILIAR: "This is a returning seeker I know well",
            RelationshipDepth.TRUSTED: "This is a trusted seeker with deep conversations",
            RelationshipDepth.COMPANION: "This is a long-term companion on the spiritual path"
        }
        parts.append(depth_descriptions.get(relationship.depth_level, ""))
        
        if relationship.key_themes:
            parts.append(f"Key themes: {', '.join(relationship.key_themes[:5])}")
        
        if relationship.last_topic:
            parts.append(f"Last discussed: {relationship.last_topic}")
        
        if relationship.pending_followups:
            followup = relationship.pending_followups[0]
            parts.append(f"Consider following up on: {followup.get('topic', '')}")
        
        return " | ".join(filter(None, parts))
    
    # =========================================================================
    # PHASE 4.1: PROACTIVE RECALL - AI References Past Conversations
    # =========================================================================
    
    async def get_proactive_recall(
        self,
        user_id: str,
        personality_id: str,
        current_query: str,
        current_context: Optional[WorkingMemoryContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze if the current query warrants proactive recall of past conversations.
        
        This enables the AI to naturally reference previous discussions, creating
        a more continuous and personalized experience.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            current_query: The user's current query
            current_context: Optional existing working memory context
            
        Returns:
            Dict with recall suggestions and reference points
        """
        recall_result = {
            "should_recall": False,
            "recall_type": None,
            "references": [],
            "suggested_opener": None,
            "confidence": 0.0
        }
        
        try:
            # Get relationship for continuity context
            relationship = await self.get_or_create_relationship(user_id, personality_id)
            
            # Get recent sessions for this personality
            recent_sessions = await self.get_recent_sessions(user_id, personality_id, limit=5)
            
            # Analyze query for recall triggers
            recall_triggers = await self._detect_recall_triggers(current_query, relationship)
            
            if not recall_triggers["has_trigger"]:
                return recall_result
            
            recall_result["should_recall"] = True
            recall_result["recall_type"] = recall_triggers["trigger_type"]
            recall_result["confidence"] = recall_triggers["confidence"]
            
            # Find relevant past memories based on trigger type
            if recall_triggers["trigger_type"] == "topic_continuation":
                references = await self._find_topic_continuations(
                    user_id, personality_id, current_query, recent_sessions
                )
            elif recall_triggers["trigger_type"] == "emotional_callback":
                references = await self._find_emotional_callbacks(
                    user_id, personality_id, current_query, recent_sessions
                )
            elif recall_triggers["trigger_type"] == "progress_reference":
                references = await self._find_progress_references(
                    user_id, personality_id, relationship, recent_sessions
                )
            elif recall_triggers["trigger_type"] == "time_based":
                references = await self._find_time_based_references(
                    user_id, personality_id, current_query, recent_sessions
                )
            else:
                references = []
            
            recall_result["references"] = references[:3]  # Limit to top 3
            
            # Generate suggested opener if we have references
            if references:
                recall_result["suggested_opener"] = await self._generate_recall_opener(
                    recall_triggers["trigger_type"],
                    references,
                    personality_id
                )
            
            logger.info(
                f"🔮 Proactive recall: type={recall_triggers['trigger_type']}, "
                f"refs={len(references)}, confidence={recall_triggers['confidence']:.2f}"
            )
            
            return recall_result
            
        except Exception as e:
            logger.error(f"❌ Error in proactive recall: {e}")
            return recall_result
    
    async def _detect_recall_triggers(
        self,
        query: str,
        relationship: RelationshipState
    ) -> Dict[str, Any]:
        """
        Detect if the query contains triggers for proactive recall.
        
        Trigger types:
        - topic_continuation: Query relates to previously discussed topics
        - emotional_callback: Similar emotional state as past conversation
        - progress_reference: User mentions progress or follow-up
        - time_based: Temporal reference (again, still, before, last time)
        """
        query_lower = query.lower()
        
        # Time-based triggers (highest priority)
        time_patterns = [
            (r"\blast time\b", 0.9),
            (r"\bremember when\b", 0.95),
            (r"\bwe discussed\b", 0.9),
            (r"\byou (said|mentioned|told)\b", 0.85),
            (r"\bagain\b", 0.6),
            (r"\bstill\b", 0.5),
            (r"\bbefore\b", 0.5),
            (r"\bcontinue\b", 0.7),
            (r"\bfollow up\b", 0.85),
            (r"\bback to\b", 0.7)
        ]
        
        for pattern, confidence in time_patterns:
            if re.search(pattern, query_lower):
                return {
                    "has_trigger": True,
                    "trigger_type": "time_based",
                    "confidence": confidence,
                    "matched_pattern": pattern
                }
        
        # Progress reference triggers
        progress_patterns = [
            (r"\bi('ve| have) (been|tried|started)\b", 0.8),
            (r"\bworking on\b", 0.7),
            (r"\bmaking progress\b", 0.85),
            (r"\bit('s| is) (getting|going)\b", 0.6),
            (r"\bupdate\b", 0.75),
            (r"\bsince (then|last|our)\b", 0.8)
        ]
        
        for pattern, confidence in progress_patterns:
            if re.search(pattern, query_lower):
                return {
                    "has_trigger": True,
                    "trigger_type": "progress_reference",
                    "confidence": confidence,
                    "matched_pattern": pattern
                }
        
        # Topic continuation (check against known themes)
        if relationship.key_themes:
            for theme in relationship.key_themes[:5]:
                if theme.lower() in query_lower:
                    return {
                        "has_trigger": True,
                        "trigger_type": "topic_continuation",
                        "confidence": 0.75,
                        "matched_theme": theme
                    }
        
        # Emotional callback detection
        emotional_patterns = [
            (r"\b(struggle|struggling)\b", "troubled", 0.7),
            (r"\b(anxious|anxiety|worried|worry)\b", "anxious", 0.75),
            (r"\b(confused|lost|uncertain)\b", "confused", 0.7),
            (r"\b(grateful|thankful|appreciate)\b", "grateful", 0.65),
            (r"\b(peaceful|calm|serene)\b", "peaceful", 0.6)
        ]
        
        for pattern, emotion, confidence in emotional_patterns:
            if re.search(pattern, query_lower):
                # Check if this emotion appeared in previous sessions
                if relationship.dominant_emotions and emotion in [e.lower() for e in relationship.dominant_emotions[:3]]:
                    return {
                        "has_trigger": True,
                        "trigger_type": "emotional_callback",
                        "confidence": confidence,
                        "matched_emotion": emotion
                    }
        
        return {"has_trigger": False, "trigger_type": None, "confidence": 0.0}
    
    async def _find_topic_continuations(
        self,
        user_id: str,
        personality_id: str,
        query: str,
        recent_sessions: List[SessionSummary]
    ) -> List[Dict[str, Any]]:
        """Find past conversations on the same topic."""
        references = []
        
        # Use semantic search to find related messages
        if self.embedding_model:
            search_query = MemorySearchQuery(
                user_id=user_id,
                query_text=query,
                personality_id=personality_id,
                max_results=5,
                min_importance_score=0.5
            )
            results = await self.semantic_search(search_query)
            
            for result in results:
                if result.relevance_score > 0.6:
                    references.append({
                        "type": "topic_continuation",
                        "content": result.message.content[:200],
                        "date": result.message.timestamp.isoformat(),
                        "relevance": result.relevance_score,
                        "session_id": result.message.session_id
                    })
        
        # Also check session topics
        for session in recent_sessions:
            if session.topics:
                # Check topic overlap
                query_words = set(query.lower().split())
                topic_match = any(
                    topic.lower() in query.lower() or 
                    any(word in topic.lower() for word in query_words)
                    for topic in session.topics
                )
                if topic_match and session.summary:
                    references.append({
                        "type": "session_topic",
                        "content": session.summary,
                        "date": session.start_time.isoformat(),
                        "topics": session.topics,
                        "session_id": session.session_id
                    })
        
        return references
    
    async def _find_emotional_callbacks(
        self,
        user_id: str,
        personality_id: str,
        query: str,
        recent_sessions: List[SessionSummary]
    ) -> List[Dict[str, Any]]:
        """Find past conversations with similar emotional patterns."""
        references = []
        
        # Detect current emotional tone
        current_tone = None
        emotion_keywords = {
            "troubled": ["struggle", "difficult", "pain", "hard"],
            "anxious": ["anxious", "worry", "nervous", "fear"],
            "confused": ["confused", "lost", "uncertain", "unsure"],
            "grateful": ["grateful", "thankful", "blessed"],
            "peaceful": ["peaceful", "calm", "content"]
        }
        
        query_lower = query.lower()
        for tone, keywords in emotion_keywords.items():
            if any(kw in query_lower for kw in keywords):
                current_tone = tone
                break
        
        if not current_tone:
            return references
        
        # Find sessions with similar emotional patterns
        for session in recent_sessions:
            if session.emotional_arc:
                session_emotions = [arc.get("tone") for arc in session.emotional_arc]
                if current_tone in session_emotions:
                    references.append({
                        "type": "emotional_callback",
                        "emotion": current_tone,
                        "content": session.summary or "Previous conversation",
                        "date": session.start_time.isoformat(),
                        "emotional_journey": f"{session.starting_emotion} → {session.ending_emotion}",
                        "session_id": session.session_id
                    })
        
        return references
    
    async def _find_progress_references(
        self,
        user_id: str,
        personality_id: str,
        relationship: RelationshipState,
        recent_sessions: List[SessionSummary]
    ) -> List[Dict[str, Any]]:
        """Find references to track user's progress."""
        references = []
        
        # Get pending follow-ups from relationship
        if relationship.pending_followups:
            for followup in relationship.pending_followups[:2]:
                references.append({
                    "type": "pending_followup",
                    "topic": followup.get("topic", ""),
                    "from_session": followup.get("session_id", ""),
                    "date": followup.get("created_at", ""),
                    "context": followup.get("context", "")
                })
        
        # Find sessions with suggestions for follow-up
        for session in recent_sessions:
            if session.suggested_followups:
                references.append({
                    "type": "suggested_followup",
                    "suggestions": session.suggested_followups,
                    "content": session.summary or "",
                    "date": session.start_time.isoformat(),
                    "session_id": session.session_id
                })
            
            # Check for key insights that might relate to progress
            if session.key_insights:
                references.append({
                    "type": "past_insight",
                    "insights": session.key_insights,
                    "content": session.summary or "",
                    "date": session.start_time.isoformat(),
                    "session_id": session.session_id
                })
        
        return references
    
    async def _find_time_based_references(
        self,
        user_id: str,
        personality_id: str,
        query: str,
        recent_sessions: List[SessionSummary]
    ) -> List[Dict[str, Any]]:
        """Find references based on temporal context."""
        references = []
        
        # For explicit "last time" references, get the most recent session
        if recent_sessions:
            last_session = recent_sessions[0]
            references.append({
                "type": "last_session",
                "content": last_session.summary or "Our previous conversation",
                "date": last_session.start_time.isoformat(),
                "topics": last_session.topics,
                "duration_minutes": last_session.duration_minutes,
                "session_id": last_session.session_id
            })
        
        # Use semantic search for "remember when" type queries
        if self.embedding_model and len(query) > 20:
            search_query = MemorySearchQuery(
                user_id=user_id,
                query_text=query,
                personality_id=personality_id,
                max_results=3,
                min_importance_score=0.6
            )
            results = await self.semantic_search(search_query)
            
            for result in results:
                if result.relevance_score > 0.65:
                    references.append({
                        "type": "semantic_match",
                        "content": result.message.content[:200],
                        "date": result.message.timestamp.isoformat(),
                        "relevance": result.relevance_score,
                        "session_id": result.message.session_id
                    })
        
        return references
    
    async def _generate_recall_opener(
        self,
        trigger_type: str,
        references: List[Dict[str, Any]],
        personality_id: str
    ) -> Optional[str]:
        """
        Generate a natural opener that references past conversation.
        
        Creates personality-appropriate ways to reference previous discussions.
        """
        if not references:
            return None
        
        ref = references[0]
        
        # Personality-specific recall styles
        personality_styles = {
            "krishna": {
                "topic_continuation": "Arjuna, I recall our previous discourse on {topic}...",
                "emotional_callback": "I sense this mirrors the journey we explored before...",
                "progress_reference": "Let us see how far you have traveled since our last meeting...",
                "time_based": "Indeed, as we discussed in our previous conversation..."
            },
            "buddha": {
                "topic_continuation": "This brings to mind our earlier contemplation on {topic}...",
                "emotional_callback": "This feeling you describe resonates with what we examined before...",
                "progress_reference": "I remember the seeds we planted in our last discourse...",
                "time_based": "As I recall from our previous sitting together..."
            },
            "marcus_aurelius": {
                "topic_continuation": "This matter connects to what we previously deliberated upon...",
                "emotional_callback": "These trials echo what you faced before, as I recall...",
                "progress_reference": "Let us assess your progress since our last counsel...",
                "time_based": "I remember well our previous discourse on this matter..."
            },
            "rumi": {
                "topic_continuation": "Ah, this melody echoes the song we sang before...",
                "emotional_callback": "Your heart speaks the same language as before, dear one...",
                "progress_reference": "The journey you began in our last meeting continues...",
                "time_based": "I carry the memory of our previous dance with these ideas..."
            }
        }
        
        # Default style for personalities not explicitly defined
        default_style = {
            "topic_continuation": "This relates to what we discussed previously about {topic}...",
            "emotional_callback": "I recall you experiencing similar feelings before...",
            "progress_reference": "Building on our previous conversation...",
            "time_based": "As we discussed in our last conversation..."
        }
        
        styles = personality_styles.get(personality_id, default_style)
        opener_template = styles.get(trigger_type, default_style["time_based"])
        
        # Fill in template variables
        topic = ref.get("topics", [None])[0] if ref.get("topics") else ref.get("topic", "this matter")
        opener = opener_template.format(topic=topic)
        
        return opener
    
    async def update_relationship_with_recall_usage(
        self,
        user_id: str,
        personality_id: str,
        recall_type: str,
        reference_used: Dict[str, Any]
    ) -> None:
        """
        Update relationship state to track recall usage patterns.
        
        This helps refine future proactive recall by learning what
        references resonate with the user.
        """
        try:
            relationship = await self.get_or_create_relationship(user_id, personality_id)
            
            # Initialize recall stats if not present
            if not hasattr(relationship, 'recall_stats') or not relationship.recall_stats:
                relationship.recall_stats = {
                    "total_recalls": 0,
                    "by_type": {},
                    "successful_topics": []
                }
            
            # Update stats
            relationship.recall_stats["total_recalls"] += 1
            
            if recall_type not in relationship.recall_stats["by_type"]:
                relationship.recall_stats["by_type"][recall_type] = 0
            relationship.recall_stats["by_type"][recall_type] += 1
            
            # Track successful topics
            if reference_used.get("topics"):
                for topic in reference_used["topics"][:2]:
                    if topic not in relationship.recall_stats["successful_topics"]:
                        relationship.recall_stats["successful_topics"].append(topic)
            
            # Keep list manageable
            relationship.recall_stats["successful_topics"] = \
                relationship.recall_stats["successful_topics"][-10:]
            
            await self.update_relationship(relationship)
            
        except Exception as e:
            logger.error(f"❌ Error updating recall stats: {e}")
    
    # =========================================================================
    # PHASE 4.2: MILESTONE DETECTION - Celebrate Relationship Growth
    # =========================================================================
    
    async def detect_milestones(
        self,
        user_id: str,
        personality_id: str,
        session: Optional[SessionSummary] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect and return any new milestones achieved in the relationship.
        
        Milestones celebrate the user's journey and growth with each personality,
        creating a sense of progress and deepening connection.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            session: Optional current session for context
            
        Returns:
            List of newly achieved milestones
        """
        new_milestones = []
        
        try:
            relationship = await self.get_or_create_relationship(user_id, personality_id)
            profile = await self.get_or_create_memory_profile(user_id)
            
            # Get already achieved milestone types
            achieved_types = {m.get("type") for m in relationship.milestones}
            
            # Check each milestone type
            milestone_checks = [
                self._check_first_conversation_milestone,
                self._check_returning_seeker_milestone,
                self._check_depth_milestone,
                self._check_time_invested_milestone,
                self._check_theme_explorer_milestone,
                self._check_emotional_breakthrough_milestone,
                self._check_anniversary_milestone,
                self._check_consistency_milestone,
            ]
            
            for check in milestone_checks:
                milestone = await check(relationship, profile, achieved_types, session)
                if milestone:
                    new_milestones.append(milestone)
                    # Add to relationship
                    relationship.milestones.append(milestone)
            
            # Update relationship if new milestones found
            if new_milestones:
                await self.update_relationship(relationship)
                logger.info(
                    f"🏆 New milestones detected: {[m['type'] for m in new_milestones]}"
                )
            
            return new_milestones
            
        except Exception as e:
            logger.error(f"❌ Error detecting milestones: {e}")
            return []
    
    async def _check_first_conversation_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for first conversation milestone."""
        if "first_conversation" in achieved:
            return None
        
        if relationship.interaction_count == 1:
            personality_names = {
                "krishna": "Lord Krishna",
                "buddha": "the Buddha",
                "marcus_aurelius": "Marcus Aurelius",
                "rumi": "Rumi",
                "confucius": "Confucius",
                "lao_tzu": "Lao Tzu"
            }
            name = personality_names.get(
                relationship.personality_id, 
                relationship.personality_id.replace("_", " ").title()
            )
            return {
                "type": "first_conversation",
                "date": datetime.utcnow().isoformat(),
                "title": "First Meeting",
                "description": f"You began your journey with {name}",
                "icon": "🌱",
                "celebration_message": f"Welcome, seeker. This is the beginning of your path with {name}."
            }
        return None
    
    async def _check_returning_seeker_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for returning seeker milestone (5 conversations)."""
        if "returning_seeker" in achieved:
            return None
        
        if relationship.interaction_count == 5:
            return {
                "type": "returning_seeker",
                "date": datetime.utcnow().isoformat(),
                "title": "Returning Seeker",
                "description": "You've returned for 5 meaningful conversations",
                "icon": "🔄",
                "celebration_message": "Your dedication to seeking wisdom shows. Each return deepens understanding."
            }
        return None
    
    async def _check_depth_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for relationship depth milestones."""
        depth_milestones = {
            RelationshipDepth.FAMILIAR: {
                "type": "familiar_bond",
                "title": "Familiar Bond",
                "description": "A meaningful connection has formed",
                "icon": "🤝",
                "celebration_message": "We have come to know each other well. Your trust honors this relationship."
            },
            RelationshipDepth.TRUSTED: {
                "type": "trusted_companion",
                "title": "Trusted Companion",
                "description": "Deep trust has been established",
                "icon": "💫",
                "celebration_message": "You have opened your heart deeply. Such trust creates space for true growth."
            },
            RelationshipDepth.COMPANION: {
                "type": "spiritual_companion",
                "title": "Spiritual Companion",
                "description": "A profound bond of understanding",
                "icon": "🕊️",
                "celebration_message": "We walk together on this path. Our connection transcends ordinary conversation."
            }
        }
        
        if relationship.depth_level in depth_milestones:
            milestone_data = depth_milestones[relationship.depth_level]
            if milestone_data["type"] not in achieved:
                return {
                    **milestone_data,
                    "date": datetime.utcnow().isoformat()
                }
        return None
    
    async def _check_time_invested_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for time invested milestones."""
        time_milestones = [
            (60, "hour_seeker", "Hour of Wisdom", "1 hour of seeking guidance", "⏰"),
            (300, "dedicated_seeker", "Dedicated Seeker", "5 hours of contemplation", "⌛"),
            (600, "devoted_student", "Devoted Student", "10 hours of learning", "📚"),
        ]
        
        for minutes, mtype, title, desc, icon in time_milestones:
            if mtype not in achieved and relationship.total_duration_minutes >= minutes:
                return {
                    "type": mtype,
                    "date": datetime.utcnow().isoformat(),
                    "title": title,
                    "description": desc,
                    "icon": icon,
                    "celebration_message": f"You have invested {minutes // 60} hour(s) in your spiritual growth. Time well spent."
                }
        return None
    
    async def _check_theme_explorer_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for theme exploration milestones."""
        if "theme_explorer" in achieved:
            return None
        
        if len(relationship.key_themes) >= 5:
            return {
                "type": "theme_explorer",
                "date": datetime.utcnow().isoformat(),
                "title": "Theme Explorer",
                "description": f"Explored 5+ life themes: {', '.join(relationship.key_themes[:3])}...",
                "icon": "🧭",
                "themes": relationship.key_themes[:5],
                "celebration_message": "Your curiosity spans many dimensions of life. A seeker of breadth and depth."
            }
        return None
    
    async def _check_emotional_breakthrough_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for emotional breakthrough milestone."""
        if "emotional_breakthrough" in achieved or not session:
            return None
        
        # Check if session shows emotional progression from troubled to peaceful/hopeful
        if session.emotional_arc and len(session.emotional_arc) >= 2:
            start_emotions = {"troubled", "confused", "anxious", "uncertain"}
            end_emotions = {"peaceful", "hopeful", "grateful", "inspired"}
            
            start_tone = session.emotional_arc[0].get("tone", "").lower()
            end_tone = session.emotional_arc[-1].get("tone", "").lower()
            
            if start_tone in start_emotions and end_tone in end_emotions:
                return {
                    "type": "emotional_breakthrough",
                    "date": datetime.utcnow().isoformat(),
                    "title": "Emotional Breakthrough",
                    "description": f"Journey from {start_tone} to {end_tone}",
                    "icon": "🌈",
                    "emotional_journey": f"{start_tone} → {end_tone}",
                    "celebration_message": "You came seeking with a heavy heart and found lightness. This is the power of wisdom."
                }
        return None
    
    async def _check_anniversary_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for anniversary milestones."""
        if not relationship.first_interaction:
            return None
        
        now = datetime.utcnow()
        days_since_first = (now - relationship.first_interaction).days
        
        anniversaries = [
            (30, "monthly_connection", "Month of Wisdom", "1 month of seeking together", "🌙"),
            (90, "seasonal_bond", "Seasonal Bond", "3 months of growth", "🍂"),
            (180, "half_year_journey", "Half-Year Journey", "6 months on the path", "☀️"),
            (365, "annual_companion", "Annual Companion", "1 year of wisdom seeking", "🎊"),
        ]
        
        for days, mtype, title, desc, icon in anniversaries:
            if mtype not in achieved and days_since_first >= days:
                return {
                    "type": mtype,
                    "date": now.isoformat(),
                    "title": title,
                    "description": desc,
                    "icon": icon,
                    "days_together": days_since_first,
                    "celebration_message": f"We have walked together for {days} days. Time deepens understanding."
                }
        return None
    
    async def _check_consistency_milestone(
        self,
        relationship: RelationshipState,
        profile: MemoryProfile,
        achieved: set,
        session: Optional[SessionSummary]
    ) -> Optional[Dict[str, Any]]:
        """Check for consistency milestones (regular engagement)."""
        if "consistent_seeker" in achieved:
            return None
        
        # Check if user has had at least 10 conversations with good engagement
        if relationship.interaction_count >= 10 and relationship.engagement_score >= 0.7:
            return {
                "type": "consistent_seeker",
                "date": datetime.utcnow().isoformat(),
                "title": "Consistent Seeker",
                "description": "10+ conversations with deep engagement",
                "icon": "🔥",
                "engagement_score": relationship.engagement_score,
                "celebration_message": "Consistency is the key to growth. Your regular practice shows true commitment."
            }
        return None
    
    async def get_all_milestones(
        self,
        user_id: str,
        personality_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all milestones for a user across all or specific personality.
        
        Args:
            user_id: The user's unique identifier
            personality_id: Optional filter by personality
            
        Returns:
            List of all achieved milestones
        """
        try:
            if personality_id:
                relationship = await self.get_or_create_relationship(user_id, personality_id)
                return relationship.milestones
            else:
                # Get all relationships
                relationships = await self.get_all_relationships(user_id)
                all_milestones = []
                for rel in relationships:
                    for milestone in rel.milestones:
                        milestone["personality_id"] = rel.personality_id
                        all_milestones.append(milestone)
                
                # Sort by date
                all_milestones.sort(
                    key=lambda m: m.get("date", ""),
                    reverse=True
                )
                return all_milestones
                
        except Exception as e:
            logger.error(f"❌ Error getting milestones: {e}")
            return []
    
    async def get_next_milestones(
        self,
        user_id: str,
        personality_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming milestones the user is close to achieving.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            
        Returns:
            List of upcoming milestones with progress
        """
        upcoming = []
        
        try:
            relationship = await self.get_or_create_relationship(user_id, personality_id)
            achieved_types = {m.get("type") for m in relationship.milestones}
            
            # Check interaction count milestones
            if "returning_seeker" not in achieved_types:
                progress = relationship.interaction_count / 5
                if progress >= 0.4:  # At least 40% progress
                    upcoming.append({
                        "type": "returning_seeker",
                        "title": "Returning Seeker",
                        "progress": min(progress, 0.99),
                        "remaining": f"{5 - relationship.interaction_count} more conversations",
                        "icon": "🔄"
                    })
            
            # Check time milestones
            if "hour_seeker" not in achieved_types:
                progress = relationship.total_duration_minutes / 60
                if progress >= 0.4:
                    upcoming.append({
                        "type": "hour_seeker",
                        "title": "Hour of Wisdom",
                        "progress": min(progress, 0.99),
                        "remaining": f"{60 - relationship.total_duration_minutes} minutes more",
                        "icon": "⏰"
                    })
            
            # Check theme exploration
            if "theme_explorer" not in achieved_types:
                progress = len(relationship.key_themes) / 5
                if progress >= 0.4:
                    upcoming.append({
                        "type": "theme_explorer",
                        "title": "Theme Explorer",
                        "progress": min(progress, 0.99),
                        "remaining": f"{5 - len(relationship.key_themes)} more themes to explore",
                        "icon": "🧭"
                    })
            
            return upcoming[:3]  # Return top 3 nearest milestones
            
        except Exception as e:
            logger.error(f"❌ Error getting next milestones: {e}")
            return []
    
    # =========================================================================
    # PHASE 4.4: PERSONALITY CROSS-REFERENCING
    # =========================================================================
    
    async def get_cross_personality_insights(
        self,
        user_id: str,
        current_personality_id: str,
        current_query: str
    ) -> List[Dict[str, Any]]:
        """
        Get relevant insights from conversations with other personalities.
        
        This enables a personality to reference wisdom shared by other guides,
        creating a cohesive multi-perspective experience while respecting
        personality boundaries.
        
        Args:
            user_id: The user's unique identifier
            current_personality_id: The current personality being consulted
            current_query: The user's current query
            
        Returns:
            List of relevant cross-personality insights
        """
        insights = []
        
        try:
            # Get user's profile to check cross-referencing preference
            profile = await self.get_or_create_memory_profile(user_id)
            
            # Check if user allows cross-personality memory
            if not profile.memory_preferences.get("cross_session_memory", True):
                return insights
            
            # Check if personality isolation is enabled
            if profile.memory_preferences.get("personality_memory_isolation", False):
                return insights
            
            # Get all relationships
            all_relationships = await self.get_all_relationships(user_id)
            
            # Filter out current personality
            other_relationships = [
                r for r in all_relationships 
                if r.personality_id != current_personality_id
            ]
            
            if not other_relationships:
                return insights
            
            # Extract topics from current query
            query_topics = await self._extract_query_topics(current_query)
            
            for relationship in other_relationships:
                # Check for theme overlap
                matching_themes = set(relationship.key_themes) & set(query_topics)
                
                if matching_themes:
                    # Get recent sessions with this personality
                    recent_sessions = await self.get_recent_sessions(
                        user_id, relationship.personality_id, limit=3
                    )
                    
                    for session in recent_sessions:
                        if session.key_insights:
                            for insight in session.key_insights[:1]:
                                insights.append({
                                    "source_personality": relationship.personality_id,
                                    "insight": insight,
                                    "matching_themes": list(matching_themes),
                                    "session_date": session.start_time.isoformat(),
                                    "relationship_depth": relationship.depth_level.name
                                })
            
            # Sort by relevance (more matching themes = more relevant)
            insights.sort(key=lambda x: len(x["matching_themes"]), reverse=True)
            
            logger.info(
                f"🔗 Found {len(insights)} cross-personality insights for {current_personality_id}"
            )
            
            return insights[:3]  # Return top 3 most relevant
            
        except Exception as e:
            logger.error(f"❌ Error getting cross-personality insights: {e}")
            return []
    
    async def _extract_query_topics(self, query: str) -> List[str]:
        """Extract topic keywords from a query."""
        topics = []
        query_lower = query.lower()
        
        topic_keywords = {
            "career": ["job", "work", "career", "business", "profession", "office", "boss"],
            "relationships": ["relationship", "family", "friend", "love", "marriage", "partner"],
            "spiritual": ["soul", "spirit", "meditation", "prayer", "faith", "divine", "god"],
            "health": ["health", "stress", "anxiety", "peace", "energy", "sleep", "body"],
            "purpose": ["purpose", "meaning", "life", "direction", "path", "goal", "destiny"],
            "emotions": ["feel", "emotion", "sad", "happy", "angry", "fear", "worry"],
            "growth": ["grow", "learn", "improve", "change", "better", "develop"],
            "decisions": ["decide", "choice", "choose", "dilemma", "option", "should"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in query_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    async def generate_cross_reference_prompt(
        self,
        insights: List[Dict[str, Any]],
        current_personality_id: str
    ) -> Optional[str]:
        """
        Generate a prompt segment for cross-referencing other personalities.
        
        Creates a natural way for the current personality to reference
        wisdom from other guides the user has consulted.
        """
        if not insights:
            return None
        
        # Personality-specific ways of referencing other guides
        reference_styles = {
            "krishna": "As {other} has wisely shared with you: \"{insight}\" - consider how this connects to what we discuss.",
            "buddha": "I recall that {other} once guided you with: \"{insight}\" - mindfully reflect on this perspective.",
            "marcus_aurelius": "Your counsel with {other} yielded this insight: \"{insight}\" - it may inform our deliberation.",
            "rumi": "The beloved {other} once whispered to your heart: \"{insight}\" - let this melody harmonize with our song.",
            "confucius": "{other} offered you this wisdom: \"{insight}\" - let us build upon this foundation.",
            "socrates": "In your dialogue with {other}, you explored: \"{insight}\" - how might this relate to our inquiry?"
        }
        
        default_style = "In your journey with {other}, you discovered: \"{insight}\" - this may be relevant here."
        
        personality_names = {
            "krishna": "Lord Krishna",
            "buddha": "the Buddha",
            "marcus_aurelius": "Marcus Aurelius",
            "rumi": "Rumi",
            "confucius": "Confucius",
            "socrates": "Socrates",
            "lao_tzu": "Lao Tzu",
            "aristotle": "Aristotle",
            "plato": "Plato",
            "gandhi": "Mahatma Gandhi"
        }
        
        style = reference_styles.get(current_personality_id, default_style)
        
        # Use the most relevant insight
        insight = insights[0]
        other_name = personality_names.get(
            insight["source_personality"],
            insight["source_personality"].replace("_", " ").title()
        )
        
        return style.format(other=other_name, insight=insight["insight"][:150])
    
    # =========================================================================
    # PHASE 4.3: MEMORY-DRIVEN SUGGESTIONS - Suggest Topics Based on Patterns
    # =========================================================================
    
    async def get_memory_suggestions(
        self,
        user_id: str,
        personality_id: str
    ) -> Dict[str, Any]:
        """
        Generate topic suggestions based on user's memory patterns.
        
        Analyzes past conversations to suggest relevant topics the user
        might want to explore or revisit.
        
        Args:
            user_id: The user's unique identifier
            personality_id: The personality identifier
            
        Returns:
            Dict with categorized suggestions
        """
        suggestions = {
            "continue_discussions": [],
            "unexplored_connections": [],
            "time_to_revisit": [],
            "based_on_growth": []
        }
        
        try:
            relationship = await self.get_or_create_relationship(user_id, personality_id)
            profile = await self.get_or_create_memory_profile(user_id)
            recent_sessions = await self.get_recent_sessions(user_id, personality_id, limit=10)
            
            # 1. Continue discussions (pending follow-ups)
            if relationship.pending_followups:
                for followup in relationship.pending_followups[:2]:
                    suggestions["continue_discussions"].append({
                        "topic": followup.get("topic", ""),
                        "context": followup.get("context", ""),
                        "suggested_question": self._generate_followup_question(followup),
                        "priority": "high"
                    })
            
            # 2. Unexplored connections between themes
            if len(relationship.key_themes) >= 3:
                theme_connections = self._find_unexplored_theme_connections(
                    relationship.key_themes,
                    recent_sessions
                )
                suggestions["unexplored_connections"] = theme_connections[:2]
            
            # 3. Time to revisit (topics discussed long ago)
            if recent_sessions:
                revisit_topics = await self._find_topics_to_revisit(
                    user_id, personality_id, recent_sessions
                )
                suggestions["time_to_revisit"] = revisit_topics[:2]
            
            # 4. Growth-based suggestions
            if session_insights := self._extract_growth_patterns(recent_sessions):
                suggestions["based_on_growth"] = session_insights[:2]
            
            logger.info(f"💡 Generated {sum(len(v) for v in suggestions.values())} suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error generating suggestions: {e}")
            return suggestions
    
    def _generate_followup_question(self, followup: Dict[str, Any]) -> str:
        """Generate a natural follow-up question from a pending topic."""
        topic = followup.get("topic", "your situation")
        templates = [
            f"How has your journey with {topic} been progressing?",
            f"What new insights have you had about {topic}?",
            f"Would you like to explore {topic} further today?",
            f"I recall we discussed {topic}. Has anything changed?"
        ]
        import random
        return random.choice(templates)
    
    def _find_unexplored_theme_connections(
        self,
        themes: List[str],
        sessions: List[SessionSummary]
    ) -> List[Dict[str, Any]]:
        """Find themes that haven't been connected in discussions."""
        connections = []
        
        # Create pairs of themes
        theme_pairs_discussed = set()
        for session in sessions:
            session_topics = session.topics or []
            for i, t1 in enumerate(session_topics):
                for t2 in session_topics[i+1:]:
                    theme_pairs_discussed.add((t1, t2))
                    theme_pairs_discussed.add((t2, t1))
        
        # Find unexplored pairs
        for i, t1 in enumerate(themes[:5]):
            for t2 in themes[i+1:5]:
                if (t1, t2) not in theme_pairs_discussed:
                    connections.append({
                        "themes": [t1, t2],
                        "suggestion": f"How might {t1} and {t2} be connected in your life?",
                        "type": "unexplored_connection"
                    })
        
        return connections
    
    async def _find_topics_to_revisit(
        self,
        user_id: str,
        personality_id: str,
        sessions: List[SessionSummary]
    ) -> List[Dict[str, Any]]:
        """Find topics discussed long ago that might be worth revisiting."""
        revisit_topics = []
        now = datetime.utcnow()
        
        # Look for sessions older than 2 weeks with meaningful topics
        for session in sessions:
            if not session.topics:
                continue
            
            days_ago = (now - session.start_time).days
            if days_ago >= 14:
                for topic in session.topics[:1]:
                    revisit_topics.append({
                        "topic": topic,
                        "last_discussed": session.start_time.isoformat(),
                        "days_ago": days_ago,
                        "suggestion": f"It's been {days_ago} days since we explored {topic}. Would you like to revisit this?",
                        "context": session.summary or ""
                    })
        
        return revisit_topics
    
    def _extract_growth_patterns(
        self,
        sessions: List[SessionSummary]
    ) -> List[Dict[str, Any]]:
        """Extract patterns that suggest areas for growth."""
        patterns = []
        
        # Analyze emotional arcs
        positive_endings = 0
        total_sessions = 0
        recurring_struggles = {}
        
        for session in sessions:
            if session.ending_emotion:
                total_sessions += 1
                if session.ending_emotion in ["peaceful", "hopeful", "grateful", "inspired"]:
                    positive_endings += 1
            
            # Track recurring struggles
            if session.starting_emotion in ["troubled", "confused", "anxious"]:
                for topic in session.topics[:2]:
                    recurring_struggles[topic] = recurring_struggles.get(topic, 0) + 1
        
        # Suggest based on patterns
        if positive_endings >= 3:
            patterns.append({
                "type": "positive_growth",
                "observation": "Your conversations often lead to peace and clarity",
                "suggestion": "Perhaps explore what helps you reach this state consistently?"
            })
        
        for topic, count in recurring_struggles.items():
            if count >= 2:
                patterns.append({
                    "type": "recurring_challenge",
                    "topic": topic,
                    "observation": f"{topic} seems to be a recurring area of challenge",
                    "suggestion": f"Would you like to go deeper on {topic} today?"
                })
        
        return patterns
    
    # =========================================================================
    # PHASE 4.5 & 4.6: GDPR COMPLIANCE - Export & Delete User Data
    # =========================================================================
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for GDPR compliance.
        
        Gathers all data associated with the user across all containers
        and returns it in a structured format suitable for download.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dict containing all user data
        """
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "profile": None,
            "relationships": [],
            "sessions": [],
            "messages": [],
            "statistics": {}
        }
        
        try:
            # Export memory profile
            profile = await self.get_or_create_memory_profile(user_id)
            export_data["profile"] = profile.to_dict()
            
            # Export all relationships
            relationships = await self.get_all_relationships(user_id)
            export_data["relationships"] = [r.to_dict() for r in relationships]
            
            # Export session summaries
            if "session_summaries" in self.containers:
                container = self.containers["session_summaries"]
                query = "SELECT * FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                export_data["sessions"] = items
            
            # Export conversation messages
            if "conversation_history" in self.containers:
                container = self.containers["conversation_history"]
                query = "SELECT * FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                # Remove embeddings to reduce file size
                for item in items:
                    item.pop("embedding", None)
                export_data["messages"] = items
            
            # Calculate statistics
            export_data["statistics"] = {
                "total_relationships": len(relationships),
                "total_sessions": len(export_data["sessions"]),
                "total_messages": len(export_data["messages"]),
                "total_milestones": sum(len(r.milestones) for r in relationships),
                "total_themes": len(set(
                    theme for r in relationships for theme in r.key_themes
                ))
            }
            
            logger.info(f"📦 Exported data for user {user_id[:8]}...")
            return export_data
            
        except Exception as e:
            logger.error(f"❌ Error exporting user data: {e}")
            return export_data
    
    async def delete_specific_memories(
        self,
        user_id: str,
        memory_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete specific conversation messages by ID.
        
        Allows users to selectively delete individual memories while
        preserving the rest of their data.
        
        Args:
            user_id: The user's unique identifier
            memory_ids: List of message IDs to delete
            
        Returns:
            Dict with deletion results
        """
        result = {
            "deleted": [],
            "failed": [],
            "not_found": []
        }
        
        try:
            if "conversation_history" not in self.containers:
                return result
            
            container = self.containers["conversation_history"]
            
            for memory_id in memory_ids:
                try:
                    # Verify the message belongs to the user
                    query = """
                        SELECT * FROM c 
                        WHERE c.id = @id AND c.user_id = @user_id
                    """
                    parameters = [
                        {"name": "@id", "value": memory_id},
                        {"name": "@user_id", "value": user_id}
                    ]
                    
                    items = list(container.query_items(
                        query=query,
                        parameters=parameters,
                        partition_key=user_id
                    ))
                    
                    if not items:
                        result["not_found"].append(memory_id)
                        continue
                    
                    # Delete the message
                    container.delete_item(item=memory_id, partition_key=user_id)
                    result["deleted"].append(memory_id)
                    
                except Exception as e:
                    logger.error(f"Failed to delete memory {memory_id}: {e}")
                    result["failed"].append(memory_id)
            
            logger.info(
                f"🗑️ Memory deletion: {len(result['deleted'])} deleted, "
                f"{len(result['failed'])} failed, {len(result['not_found'])} not found"
            )
            return result
            
        except Exception as e:
            logger.error(f"❌ Error deleting memories: {e}")
            return result
    
    async def delete_session(
        self,
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Delete an entire session and its messages.
        
        Args:
            user_id: The user's unique identifier
            session_id: The session ID to delete
            
        Returns:
            Dict with deletion results
        """
        result = {
            "session_deleted": False,
            "messages_deleted": 0
        }
        
        try:
            # Delete session summary
            if "session_summaries" in self.containers:
                container = self.containers["session_summaries"]
                try:
                    container.delete_item(item=session_id, partition_key=user_id)
                    result["session_deleted"] = True
                except Exception:
                    pass
            
            # Delete associated messages
            if "conversation_history" in self.containers:
                container = self.containers["conversation_history"]
                query = """
                    SELECT * FROM c 
                    WHERE c.user_id = @user_id AND c.session_id = @session_id
                """
                parameters = [
                    {"name": "@user_id", "value": user_id},
                    {"name": "@session_id", "value": session_id}
                ]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                
                for item in items:
                    try:
                        container.delete_item(item=item["id"], partition_key=user_id)
                        result["messages_deleted"] += 1
                    except Exception:
                        pass
            
            logger.info(
                f"🗑️ Session {session_id[:8]}... deleted with {result['messages_deleted']} messages"
            )
            return result
            
        except Exception as e:
            logger.error(f"❌ Error deleting session: {e}")
            return result
    
    async def delete_all_user_data(
        self,
        user_id: str,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Delete all user data (GDPR right to erasure).
        
        This is a destructive operation that removes all user data
        from all containers. Requires explicit confirmation.
        
        Args:
            user_id: The user's unique identifier
            confirm: Must be True to proceed with deletion
            
        Returns:
            Dict with deletion statistics
        """
        result = {
            "success": False,
            "profile_deleted": False,
            "relationships_deleted": 0,
            "sessions_deleted": 0,
            "messages_deleted": 0
        }
        
        if not confirm:
            result["error"] = "Deletion requires explicit confirmation"
            return result
        
        try:
            # Delete memory profile
            if "memory_profiles" in self.containers:
                container = self.containers["memory_profiles"]
                query = "SELECT c.id FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                
                for item in items:
                    container.delete_item(item=item["id"], partition_key=user_id)
                    result["profile_deleted"] = True
            
            # Delete all relationships
            if "relationship_states" in self.containers:
                container = self.containers["relationship_states"]
                query = "SELECT c.id FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                
                for item in items:
                    container.delete_item(item=item["id"], partition_key=user_id)
                    result["relationships_deleted"] += 1
            
            # Delete all sessions
            if "session_summaries" in self.containers:
                container = self.containers["session_summaries"]
                query = "SELECT c.id FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                
                for item in items:
                    container.delete_item(item=item["id"], partition_key=user_id)
                    result["sessions_deleted"] += 1
            
            # Delete all messages
            if "conversation_history" in self.containers:
                container = self.containers["conversation_history"]
                query = "SELECT c.id FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                
                for item in items:
                    container.delete_item(item=item["id"], partition_key=user_id)
                    result["messages_deleted"] += 1
            
            # Clear working memory cache
            cache_keys_to_remove = [
                key for key in self.working_memory_cache 
                if key.startswith(f"{user_id}:")
            ]
            for key in cache_keys_to_remove:
                del self.working_memory_cache[key]
            
            result["success"] = True
            logger.info(
                f"🗑️ Deleted all data for user {user_id[:8]}...: "
                f"{result['relationships_deleted']} relationships, "
                f"{result['sessions_deleted']} sessions, "
                f"{result['messages_deleted']} messages"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error deleting all user data: {e}")
            result["error"] = str(e)
            return result
    
    # =========================================================================
    # IMPORTANCE SCORING & ANALYSIS
    # =========================================================================
    
    async def _calculate_importance(
        self,
        content: str,
        role: str
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate importance score for a message.
        
        Factors:
        - Emotional intensity (detected sentiment strength)
        - Novelty (new topics or information)
        - Personal revelation (sharing personal details)
        - User question (seeking guidance)
        
        Returns:
            Tuple of (overall_score, factor_breakdown)
        """
        factors = {}
        
        # Emotional intensity (simple keyword-based for now)
        emotional_words = [
            "struggle", "pain", "joy", "grateful", "confused", "lost",
            "breakthrough", "realized", "understand", "fear", "hope",
            "love", "hate", "anxious", "peaceful", "angry", "sad"
        ]
        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        factors["emotional_intensity"] = min(emotional_count / 5, 1.0)
        
        # Novelty (approximated by content length and question marks)
        factors["novelty"] = min(len(content) / 500, 1.0) * 0.5 + 0.5
        
        # Personal revelation (I statements, personal pronouns)
        personal_patterns = [
            r"\bI (am|feel|think|believe|want|need|have|was|did)\b",
            r"\bmy (life|family|job|relationship|problem|situation)\b",
            r"\bI've been\b", r"\bI'm going through\b"
        ]
        personal_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE))
            for pattern in personal_patterns
        )
        factors["personal_revelation"] = min(personal_count / 3, 1.0)
        
        # User question (for user messages)
        if role == "user":
            question_indicators = ["?", "how", "what", "why", "should", "can", "help"]
            question_count = sum(1 for q in question_indicators if q in content.lower())
            factors["user_question"] = min(question_count / 3, 1.0)
        else:
            factors["user_question"] = 0.0
        
        # User feedback (placeholder - would be updated based on explicit feedback)
        factors["user_feedback"] = 0.5
        
        # Calculate weighted average
        total_score = sum(
            factors[key] * self.IMPORTANCE_WEIGHTS.get(key, 0.2)
            for key in factors
        )
        
        return total_score, factors
    
    async def _extract_message_metadata(
        self,
        content: str,
        role: str
    ) -> Dict[str, Any]:
        """Extract metadata from message content."""
        metadata = {
            "topics": [],
            "emotional_tone": None,
            "has_question": "?" in content,
            "has_personal_revelation": False,
            "referenced_sources": []
        }
        
        # Simple topic extraction (could be enhanced with NLP)
        topic_keywords = {
            "career": ["job", "work", "career", "business", "profession"],
            "relationships": ["relationship", "family", "friend", "love", "marriage"],
            "spiritual": ["soul", "spirit", "meditation", "prayer", "faith"],
            "health": ["health", "stress", "anxiety", "peace", "energy"],
            "purpose": ["purpose", "meaning", "life", "direction", "path"]
        }
        
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                metadata["topics"].append(topic)
        
        # Simple emotional tone detection
        emotion_patterns = {
            "seeking": ["how", "what should", "help me", "guidance"],
            "troubled": ["struggle", "difficult", "pain", "confused"],
            "grateful": ["thank", "grateful", "appreciate", "blessed"],
            "curious": ["wonder", "curious", "interesting", "learn"]
        }
        
        for emotion, patterns in emotion_patterns.items():
            if any(p in content_lower for p in patterns):
                metadata["emotional_tone"] = emotion
                break
        
        # Check for personal revelation
        personal_indicators = ["I feel", "I am", "I've been", "my life", "my family"]
        metadata["has_personal_revelation"] = any(
            p.lower() in content_lower for p in personal_indicators
        )
        
        return metadata
    
    # =========================================================================
    # REFLECTION & INSIGHT GENERATION
    # =========================================================================
    
    async def _generate_session_summary(
        self,
        messages: List[ConversationMessage],
        session: SessionSummary
    ) -> str:
        """Generate a summary of the session using AI."""
        if not self.generation_model:
            return self._generate_simple_summary(messages)
        
        try:
            # Build conversation text
            conversation_text = "\n".join([
                f"{m.role.upper()}: {m.content[:300]}" 
                for m in messages[:10]
            ])
            
            prompt = f"""Summarize this spiritual guidance conversation in 2-3 sentences.
Focus on: the seeker's main concern, guidance given, and any insights or progress.

Conversation:
{conversation_text}

Summary:"""
            
            response = await self.generation_model.generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"⚠️ AI summary failed, using simple summary: {e}")
            return self._generate_simple_summary(messages)
    
    def _generate_simple_summary(self, messages: List[ConversationMessage]) -> str:
        """Generate a simple summary without AI."""
        user_messages = [m for m in messages if m.role == "user"]
        if not user_messages:
            return "Brief conversation"
        
        first_query = user_messages[0].content[:100]
        return f"Conversation about: {first_query}..."
    
    async def _extract_key_insights(
        self,
        messages: List[ConversationMessage],
        session: SessionSummary
    ) -> List[str]:
        """Extract key insights from the session."""
        # Get high-importance messages
        high_importance = [m for m in messages if m.importance_score > 0.6]
        
        insights = []
        for msg in high_importance[:3]:
            if msg.role == "assistant":
                # Extract key sentence from guidance
                sentences = msg.content.split(".")
                if sentences:
                    insights.append(sentences[0].strip() + ".")
        
        return insights
    
    async def _generate_reflection(self, session: SessionSummary) -> str:
        """Generate deeper reflection on the session."""
        if not self.generation_model:
            return ""
        
        try:
            prompt = f"""Based on this conversation summary, generate a brief reflection (1-2 sentences) on the seeker's journey and growth potential.

Summary: {session.summary}
Topics: {', '.join(session.topics)}
Emotional journey: {session.starting_emotion} → {session.ending_emotion}

Reflection:"""
            
            response = await self.generation_model.generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Reflection generation failed: {e}")
            return ""
    
    async def _generate_followup_suggestions(
        self,
        session: SessionSummary
    ) -> List[str]:
        """Generate follow-up suggestions for next conversation."""
        if not session.topics:
            return []
        
        # Simple suggestion generation based on topics
        suggestions = []
        topic_followups = {
            "career": "How is your work situation evolving?",
            "relationships": "Have you reflected more on your relationships?",
            "spiritual": "Have you tried the meditation practice we discussed?",
            "health": "How have you been managing your well-being?",
            "purpose": "What new insights have you had about your path?"
        }
        
        for topic in session.topics[:2]:
            if topic in topic_followups:
                suggestions.append(topic_followups[topic])
        
        return suggestions
    
    async def _extract_topics(
        self,
        messages: List[ConversationMessage]
    ) -> List[str]:
        """Extract main topics from messages."""
        all_topics = []
        for msg in messages:
            if msg.metadata and msg.metadata.get("topics"):
                all_topics.extend(msg.metadata["topics"])
        
        # Deduplicate while preserving order
        seen = set()
        unique_topics = []
        for topic in all_topics:
            if topic not in seen:
                seen.add(topic)
                unique_topics.append(topic)
        
        return unique_topics
    
    async def _track_emotional_arc(
        self,
        messages: List[ConversationMessage]
    ) -> List[Dict[str, Any]]:
        """Track emotional arc across messages."""
        arc = []
        for msg in messages:
            if msg.role == "user" and msg.metadata.get("emotional_tone"):
                arc.append({
                    "timestamp": msg.timestamp.isoformat(),
                    "tone": msg.metadata["emotional_tone"]
                })
        return arc
    
    # =========================================================================
    # EMBEDDING & SIMILARITY
    # =========================================================================
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using Gemini."""
        if not self.embedding_model:
            return None
        
        try:
            result = genai.embed_content(
                model=f"models/{self.embedding_model}",
                content=text[:2000],  # Limit text length
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.warning(f"⚠️ Embedding generation failed: {e}")
            return None
    
    def _cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        if not embedding1 or not embedding2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_recency_score(self, timestamp: datetime) -> float:
        """Calculate recency score with exponential decay."""
        now = datetime.utcnow()
        age_days = (now - timestamp).total_seconds() / 86400
        
        # Apply exponential decay
        return max(0, 1.0 - (self.DECAY_RATE * age_days))
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimate: ~4 characters per token for English
        return len(text) // 4
    
    def _calculate_context_quality(self, context: WorkingMemoryContext) -> float:
        """Calculate quality score for assembled context."""
        score = 0.0
        
        # Has user profile context
        if context.user_profile_context:
            score += 0.2
        
        # Has relationship context
        if context.relationship_context:
            score += 0.2
        
        # Has recent session summaries
        if context.recent_session_summaries:
            score += 0.2
        
        # Has relevant insights
        if context.relevant_past_insights:
            score += 0.2
        
        # Has retrieved memories
        if context.retrieved_memories:
            score += 0.2
        
        return min(score, 1.0)
    
    async def cleanup_old_memories(self, user_id: str) -> Dict[str, int]:
        """
        Clean up old memories based on retention policies.
        
        Returns:
            Dict with counts of archived/deleted items
        """
        stats = {"archived": 0, "deleted": 0}
        
        try:
            now = datetime.utcnow()
            
            # Archive old conversation messages (> 90 days)
            if "conversation_history" in self.containers:
                container = self.containers["conversation_history"]
                archive_cutoff = now - timedelta(days=self.EPISODIC_MEMORY_RETENTION_DAYS)
                
                query = """
                    SELECT * FROM c 
                    WHERE c.user_id = @user_id 
                    AND c.archived = false
                    AND c.timestamp < @cutoff
                """
                parameters = [
                    {"name": "@user_id", "value": user_id},
                    {"name": "@cutoff", "value": archive_cutoff.isoformat()}
                ]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                
                for item in items:
                    item["archived"] = True
                    item["archive_date"] = now.isoformat()
                    container.upsert_item(body=item)
                    stats["archived"] += 1
                
                # Delete very old messages (> 1 year)
                delete_cutoff = now - timedelta(days=self.SEMANTIC_ARCHIVE_RETENTION_DAYS)
                
                query = """
                    SELECT * FROM c 
                    WHERE c.user_id = @user_id 
                    AND c.archived = true
                    AND c.archive_date < @cutoff
                """
                parameters = [
                    {"name": "@user_id", "value": user_id},
                    {"name": "@cutoff", "value": delete_cutoff.isoformat()}
                ]
                
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id
                ))
                
                for item in items:
                    container.delete_item(item=item["id"], partition_key=user_id)
                    stats["deleted"] += 1
            
            logger.info(f"🧹 Memory cleanup: {stats['archived']} archived, {stats['deleted']} deleted")
            
        except Exception as e:
            logger.error(f"❌ Error in memory cleanup: {e}")
        
        return stats


# Singleton instance
_memory_service_instance: Optional[HierarchicalMemoryService] = None


def get_memory_service() -> HierarchicalMemoryService:
    """Get or create the singleton memory service instance."""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = HierarchicalMemoryService()
    return _memory_service_instance
