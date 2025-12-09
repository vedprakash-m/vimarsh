"""
Tests for Hierarchical Memory Service

Comprehensive test suite for the 4-layer memory architecture.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import uuid

# Import the modules to test
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


class TestMemoryModels:
    """Test memory data models."""
    
    def test_memory_profile_create_new(self):
        """TEST_MEM_008: Memory profile creates on first user interaction."""
        user_id = "test_user_123"
        profile = MemoryProfile.create_new(user_id)
        
        assert profile.user_id == user_id
        assert profile.id is not None
        assert profile.created_at is not None
        assert profile.total_sessions == 0
        assert profile.total_messages == 0
        assert profile.memory_preferences["cross_session_memory"] is True
    
    def test_memory_profile_to_dict(self):
        """Test profile serialization."""
        user_id = "test_user_123"
        profile = MemoryProfile.create_new(user_id)
        profile.discovered_interests = ["meditation", "career"]
        
        data = profile.to_dict()
        
        assert data["user_id"] == user_id
        assert data["discovered_interests"] == ["meditation", "career"]
        assert data["_partition_key"] == user_id
    
    def test_memory_profile_from_dict(self):
        """Test profile deserialization."""
        data = {
            "id": "test_id",
            "user_id": "test_user",
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-01-15T12:00:00",
            "communication_style": {"depth": "deep"},
            "discovered_interests": ["philosophy"],
            "recurring_themes": ["purpose"],
            "life_context": {},
            "personality_relationship_summary": {},
            "memory_preferences": {},
            "total_sessions": 5,
            "total_messages": 50
        }
        
        profile = MemoryProfile.from_dict(data)
        
        assert profile.user_id == "test_user"
        assert profile.total_sessions == 5
        assert profile.discovered_interests == ["philosophy"]
    
    def test_relationship_state_create_new(self):
        """TEST_MEM_009: Relationship state initializes for new personality."""
        user_id = "test_user"
        personality_id = "krishna"
        
        relationship = RelationshipState.create_new(user_id, personality_id)
        
        assert relationship.user_id == user_id
        assert relationship.personality_id == personality_id
        assert relationship.depth_level == RelationshipDepth.STRANGER
        assert relationship.interaction_count == 0
        assert relationship.first_interaction is not None
    
    def test_relationship_depth_calculation(self):
        """Test relationship depth level calculation."""
        relationship = RelationshipState.create_new("user", "krishna")
        
        # Stranger
        assert relationship.calculate_depth_level() == RelationshipDepth.STRANGER
        
        # Acquaintance
        relationship.interaction_count = 5
        assert relationship.calculate_depth_level() == RelationshipDepth.ACQUAINTANCE
        
        # Familiar
        relationship.interaction_count = 15
        assert relationship.calculate_depth_level() == RelationshipDepth.FAMILIAR
        
        # Trusted
        relationship.interaction_count = 30
        assert relationship.calculate_depth_level() == RelationshipDepth.TRUSTED
        
        # Companion
        relationship.interaction_count = 60
        relationship.trust_score = 0.8
        assert relationship.calculate_depth_level() == RelationshipDepth.COMPANION
    
    def test_relationship_update_after_interaction(self):
        """Test relationship updates after interaction."""
        relationship = RelationshipState.create_new("user", "buddha")
        
        relationship.update_after_interaction(
            duration_minutes=15,
            topics=["meditation", "mindfulness"],
            emotional_state="peaceful"
        )
        
        assert relationship.interaction_count == 1
        assert relationship.total_duration_minutes == 15
        assert relationship.last_topic == "meditation"
        assert relationship.last_emotional_state == "peaceful"
        assert "meditation" in relationship.recent_topics
        assert "mindfulness" in relationship.key_themes
    
    def test_conversation_message_create_new(self):
        """Test message creation."""
        message = ConversationMessage.create_new(
            user_id="user",
            personality_id="krishna",
            session_id="session_123",
            role="user",
            content="What is dharma?"
        )
        
        assert message.user_id == "user"
        assert message.role == "user"
        assert message.content == "What is dharma?"
        assert message.importance_score == 0.5
        assert message.archived is False
    
    def test_session_summary_create_new(self):
        """Test session summary creation."""
        session = SessionSummary.create_new(
            user_id="user",
            personality_id="krishna",
            session_id="session_123"
        )
        
        assert session.user_id == "user"
        assert session.personality_id == "krishna"
        assert session.start_time is not None
        assert session.message_count == 0
    
    def test_working_memory_token_management(self):
        """TEST_MEM_002: Working memory maintains 16K token budget."""
        context = WorkingMemoryContext(
            user_id="user",
            personality_id="krishna",
            session_id="session_123"
        )
        
        assert context.max_tokens == 16000
        assert context.get_total_tokens() == 0
        assert context.get_available_tokens() == 16000
        
        # Add some content
        context.core_memory_tokens = 2000
        context.episodic_memory_tokens = 3000
        context.current_conversation_tokens = 4000
        
        assert context.get_total_tokens() == 9000
        assert context.get_available_tokens() == 7000
    
    def test_working_memory_to_prompt_context(self):
        """Test working memory context string generation."""
        context = WorkingMemoryContext(
            user_id="user",
            personality_id="krishna",
            session_id="session_123"
        )
        
        context.user_profile_context = "Interested in meditation"
        context.relationship_context = "Returning seeker"
        context.recent_session_summaries = [
            {"summary": "Discussed meditation techniques"}
        ]
        
        prompt_context = context.to_prompt_context()
        
        assert "User Context" in prompt_context
        assert "meditation" in prompt_context
        assert "Relationship" in prompt_context
    
    def test_memory_search_query(self):
        """Test search query creation."""
        query = MemorySearchQuery(
            user_id="user",
            query_text="meditation techniques",
            personality_id="buddha",
            max_results=5
        )
        
        assert query.user_id == "user"
        assert query.query_text == "meditation techniques"
        assert query.max_results == 5
        assert query.min_importance_score == 0.3


@pytest.mark.skip(reason="Hierarchical memory service uses Gemini API - migration to Azure OpenAI pending")
class TestHierarchicalMemoryService:
    """Test the hierarchical memory service."""
    
    @pytest.fixture
    def mock_memory_service(self):
        """Create a mock memory service."""
        with patch('services.hierarchical_memory_service.CosmosClient'), \
             patch('services.hierarchical_memory_service.genai'):
            from services.hierarchical_memory_service import HierarchicalMemoryService
            service = HierarchicalMemoryService()
            return service
    
    @pytest.mark.asyncio
    async def test_importance_scoring(self, mock_memory_service):
        """TEST_MEM_006: Importance scoring calculates correct scores (0-1 range)."""
        # Emotional content
        score, factors = await mock_memory_service._calculate_importance(
            "I'm struggling with deep pain and confusion about my life purpose",
            "user"
        )
        
        assert 0 <= score <= 1
        assert "emotional_intensity" in factors
        assert factors["emotional_intensity"] > 0
        
        # Simple greeting
        score2, factors2 = await mock_memory_service._calculate_importance(
            "Hello",
            "user"
        )
        
        assert score2 < score  # Emotional content should have higher score
    
    @pytest.mark.asyncio
    async def test_message_metadata_extraction(self, mock_memory_service):
        """Test message metadata extraction."""
        metadata = await mock_memory_service._extract_message_metadata(
            "How do I find peace in my stressful job? I feel lost.",
            "user"
        )
        
        assert metadata["has_question"] is True
        assert "career" in metadata["topics"] or "health" in metadata["topics"]
        assert metadata["emotional_tone"] in ["troubled", "seeking", None]
    
    @pytest.mark.asyncio
    async def test_token_estimation(self, mock_memory_service):
        """TEST_MEM_017: Token counting accurate for context assembly."""
        text = "This is a test message with some content."
        tokens = mock_memory_service._estimate_tokens(text)
        
        # Rough estimate: ~4 chars per token
        expected = len(text) // 4
        assert tokens == expected
    
    def test_cosine_similarity(self, mock_memory_service):
        """Test cosine similarity calculation."""
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [1.0, 0.0, 0.0]
        
        similarity = mock_memory_service._cosine_similarity(embedding1, embedding2)
        assert similarity == pytest.approx(1.0, abs=0.001)
        
        # Orthogonal vectors
        embedding3 = [0.0, 1.0, 0.0]
        similarity2 = mock_memory_service._cosine_similarity(embedding1, embedding3)
        assert similarity2 == pytest.approx(0.0, abs=0.001)
    
    def test_recency_score(self, mock_memory_service):
        """Test recency score with decay."""
        now = datetime.utcnow()
        
        # Recent message
        recent_score = mock_memory_service._calculate_recency_score(now)
        assert recent_score == pytest.approx(1.0, abs=0.01)
        
        # 10-day old message
        old_date = now - timedelta(days=10)
        old_score = mock_memory_service._calculate_recency_score(old_date)
        assert old_score < recent_score
        assert old_score == pytest.approx(0.5, abs=0.1)  # With 5% daily decay


class TestMemoryIsolation:
    """Test memory isolation between users and personalities."""
    
    def test_user_memory_isolation(self):
        """TEST_MEM_014: Memory isolation between different users verified."""
        profile1 = MemoryProfile.create_new("user_1")
        profile2 = MemoryProfile.create_new("user_2")
        
        profile1.discovered_interests = ["meditation"]
        profile2.discovered_interests = ["science"]
        
        assert profile1.user_id != profile2.user_id
        assert profile1.discovered_interests != profile2.discovered_interests
        assert profile1.to_dict()["_partition_key"] != profile2.to_dict()["_partition_key"]
    
    def test_personality_memory_isolation(self):
        """TEST_MEM_015: Memory isolation between personalities for same user verified."""
        user_id = "test_user"
        
        rel_krishna = RelationshipState.create_new(user_id, "krishna")
        rel_buddha = RelationshipState.create_new(user_id, "buddha")
        
        rel_krishna.key_themes = ["dharma", "duty"]
        rel_buddha.key_themes = ["mindfulness", "middle_way"]
        
        assert rel_krishna.personality_id != rel_buddha.personality_id
        assert rel_krishna.key_themes != rel_buddha.key_themes


@pytest.mark.skip(reason="Hierarchical memory service uses Gemini API - migration to Azure OpenAI pending")
class TestContextQuality:
    """Test context quality calculation."""
    
    def test_context_quality_empty(self):
        """Test quality score with no context."""
        from services.hierarchical_memory_service import HierarchicalMemoryService
        
        context = WorkingMemoryContext(
            user_id="user",
            personality_id="krishna",
            session_id="session"
        )
        
        with patch.object(HierarchicalMemoryService, '__init__', lambda x: None):
            service = HierarchicalMemoryService()
            quality = service._calculate_context_quality(context)
        
        assert quality == 0.0
    
    def test_context_quality_full(self):
        """Test quality score with full context."""
        from services.hierarchical_memory_service import HierarchicalMemoryService
        
        context = WorkingMemoryContext(
            user_id="user",
            personality_id="krishna",
            session_id="session"
        )
        context.user_profile_context = "Test profile"
        context.relationship_context = "Test relationship"
        context.recent_session_summaries = [{"summary": "Test"}]
        context.relevant_past_insights = ["Insight 1"]
        context.retrieved_memories = [{"content": "Memory"}]
        
        with patch.object(HierarchicalMemoryService, '__init__', lambda x: None):
            service = HierarchicalMemoryService()
            quality = service._calculate_context_quality(context)
        
        assert quality == 1.0


class TestPromptTemplates:
    """Test memory-aware prompt templates."""
    
    def test_greeting_by_depth(self):
        """Test greetings vary by relationship depth."""
        from services.prompt_templates import MemoryAwarePromptTemplates
        
        # Stranger greeting
        stranger_rel = RelationshipState.create_new("user", "krishna")
        stranger_greeting = MemoryAwarePromptTemplates.get_relationship_greeting(
            stranger_rel, "Krishna"
        )
        assert stranger_greeting is not None
        assert len(stranger_greeting) > 0
        
        # Companion greeting
        companion_rel = RelationshipState.create_new("user", "krishna")
        companion_rel.depth_level = RelationshipDepth.COMPANION
        companion_greeting = MemoryAwarePromptTemplates.get_relationship_greeting(
            companion_rel, "Krishna"
        )
        assert companion_greeting is not None
        assert companion_greeting != stranger_greeting
    
    def test_proactive_recall_with_topic(self):
        """Test proactive recall prompt generation."""
        from services.prompt_templates import MemoryAwarePromptTemplates
        
        relationship = RelationshipState.create_new("user", "buddha")
        relationship.recent_topics = ["meditation practice"]
        
        recall = MemoryAwarePromptTemplates.get_proactive_recall_prompt(relationship)
        
        assert recall is not None
        assert "meditation practice" in recall
    
    def test_memory_context_section_building(self):
        """Test building memory context section."""
        from services.prompt_templates import MemoryAwarePromptTemplates
        
        context = WorkingMemoryContext(
            user_id="user",
            personality_id="krishna",
            session_id="session"
        )
        context.user_profile_context = "Interested in dharma"
        context.relationship_context = "Returning seeker"
        
        section = MemoryAwarePromptTemplates.build_memory_context_section(context)
        
        assert "dharma" in section
        assert "seeker" in section.lower()


class TestContextWindowOptimizer:
    """Test context window optimization."""
    
    def test_optimization_within_budget(self):
        """Test no changes when within budget."""
        from services.prompt_templates import ContextWindowOptimizer
        
        components = {
            "system": "Short prompt",
            "memory": "Brief memory"
        }
        priorities = {"system": 100, "memory": 50}
        
        optimized = ContextWindowOptimizer.optimize_context(
            components, priorities, max_tokens=1000
        )
        
        assert optimized["system"] == "Short prompt"
        assert optimized["memory"] == "Brief memory"
    
    def test_optimization_over_budget(self):
        """Test truncation when over budget."""
        from services.prompt_templates import ContextWindowOptimizer
        
        components = {
            "high_priority": "Important content",
            "low_priority": "A" * 4000  # Long content
        }
        priorities = {"high_priority": 100, "low_priority": 10}
        
        optimized = ContextWindowOptimizer.optimize_context(
            components, priorities, max_tokens=500
        )
        
        # High priority should be preserved
        assert optimized["high_priority"] == "Important content"
        # Low priority should be truncated or removed
        assert len(optimized["low_priority"]) < len(components["low_priority"])


class TestPersonalityMemoryStyles:
    """Test personality-specific memory styles."""
    
    def test_krishna_memory_style(self):
        """Test Krishna-specific memory style."""
        from services.prompt_templates import get_personality_memory_style
        
        style = get_personality_memory_style("krishna")
        
        assert "dharma" in style.get("memory_framing", "").lower()
    
    def test_unknown_personality_default(self):
        """Test fallback for unknown personality."""
        from services.prompt_templates import get_personality_memory_style
        
        style = get_personality_memory_style("unknown_personality")
        
        assert "memory_framing" in style
        assert "recall_style" in style
        assert "relationship_style" in style


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
