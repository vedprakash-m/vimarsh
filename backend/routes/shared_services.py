"""
Shared service context for all route blueprints.

Centralizes service initialization logic that was previously inline in function_app.py.
All blueprints import services from here instead of re-initializing them.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Centralized AI config
# ──────────────────────────────────────────────
try:
    from config.ai_models import AI_CONFIG
    azure_chat_deployment = AI_CONFIG.azure_openai_chat_deployment
except ImportError:
    azure_chat_deployment = "vimarsh-chat-gpt5mini"

# ──────────────────────────────────────────────
# Service availability flags & instances
# ──────────────────────────────────────────────
personality_models_available = False
personality_service_available = False
database_personality_available = False
memory_service_available = False
enhanced_llm_available = False
enhanced_rag_available = False
hierarchical_memory_available = False
engagement_available = False
user_services_available = False

optimized_personality_service = None
safety_service = None
admin_service = None
conversation_memory_service = None
enhanced_llm_service = None
enhanced_rag_service = None
database_personality_service = None
hierarchical_memory_service = None
engagement_service_instance = None
achievement_service_instance = None
preferences_service = None
data_export_service = None
analytics_service = None
PERSONALITY_CONFIGS = None

# ──────────────────────────────────────────────
# Service Initialization
# ──────────────────────────────────────────────

# 1. Database Personality Service
try:
    from services.database_personality_service import DatabasePersonalityService
    database_personality_service = DatabasePersonalityService()
    database_personality_available = True
    logger.info("✅ Database-driven personality service initialized")
except Exception as e:
    logger.warning(f"⚠️ Database personality service failed: {e}")

# 2. Personality Service
try:
    from models.personality_models import PERSONALITY_CONFIGS as _CONFIGS
    from services.personality_service import PersonalityService
    PERSONALITY_CONFIGS = _CONFIGS
    personality_models_available = True
    optimized_personality_service = PersonalityService()
    personality_service_available = True
    logger.info("✅ Personality service initialized")
except Exception as e:
    logger.warning(f"⚠️ Personality service failed: {e}")

# 3. Enhanced LLM Service
try:
    from services.enhanced_llm_wrapper import enhanced_llm_service as _llm
    enhanced_llm_service = _llm
    enhanced_llm_available = True
    logger.info("✅ Enhanced LLM service loaded")
except Exception as e:
    logger.warning(f"⚠️ Enhanced LLM service failed: {e}")

# 4. Enhanced RAG Service
try:
    from services.enhanced_rag_service_v6 import EnhancedRAGService
    enhanced_rag_available = True
    # Initialized lazily in blueprints
    logger.info("✅ Enhanced RAG service available")
except Exception as e:
    logger.warning(f"⚠️ Enhanced RAG service unavailable: {e}")

# 5. Conversation Memory & Preferences
try:
    from services.conversation_memory_service import ConversationMemoryService
    from services.preferences_service import preferences_service as _prefs
    preferences_service = _prefs
    conversation_memory_service = ConversationMemoryService(preferences_service=preferences_service)
    memory_service_available = True
    logger.info("✅ Conversation memory service initialized")
except Exception as e:
    logger.warning(f"⚠️ Conversation memory service failed: {e}")

# 6. Hierarchical Memory Service
try:
    from services.hierarchical_memory_service import get_memory_service
    hierarchical_memory_service = get_memory_service()
    hierarchical_memory_available = True
    logger.info("✅ Hierarchical memory service initialized")
except Exception as e:
    logger.warning(f"⚠️ Hierarchical memory service failed: {e}")

# 7. Safety Service
try:
    from services.safety_service import SafetyService
    safety_service = SafetyService()
    logger.info("✅ Safety service initialized")
except Exception as e:
    logger.warning(f"⚠️ Safety service failed: {e}")

# 8. Admin Service
try:
    from services.admin_service import AdminService
    admin_service = AdminService()
    logger.info("✅ Admin service initialized")
except Exception as e:
    logger.warning(f"⚠️ Admin service failed: {e}")

# 9. Engagement & Achievement Services
try:
    from engagement.engagement_service import get_engagement_service
    from engagement.achievement_service import get_achievement_service
    engagement_service_instance = get_engagement_service()
    achievement_service_instance = get_achievement_service()
    engagement_available = True
    logger.info("🏆 Engagement and achievement services initialized")
except Exception as e:
    logger.warning(f"⚠️ Engagement services failed: {e}")

# 10. Analytics & Data Export
try:
    from services.analytics_service import analytics_service as _analytics
    from services.data_export_service import data_export_service as _export
    analytics_service = _analytics
    data_export_service = _export
    user_services_available = True
    logger.info("📊 Analytics and data export services loaded")
except Exception as e:
    logger.warning(f"⚠️ Analytics/Export services failed: {e}")


# ──────────────────────────────────────────────
# Personality Data
# ──────────────────────────────────────────────
FALLBACK_PERSONALITIES = {
    "krishna": {"name": "Krishna", "domain": "spiritual", "description": "Divine guide offering spiritual wisdom from the Bhagavad Gita"},
    "buddha": {"name": "Buddha", "domain": "spiritual", "description": "Enlightened teacher of the Middle Way and mindfulness"},
    "jesus_christ": {"name": "Jesus Christ", "domain": "spiritual", "description": "Teacher of love, compassion, and spiritual transformation"},
    "rumi": {"name": "Rumi", "domain": "spiritual", "description": "Sufi mystic poet of divine love and spiritual union"},
    "albert_einstein": {"name": "Albert Einstein", "domain": "scientific", "description": "Brilliant physicist exploring the mysteries of the universe"},
    "isaac_newton": {"name": "Isaac Newton", "domain": "scientific", "description": "English mathematician and physicist, father of classical mechanics"},
    "nikola_tesla": {"name": "Nikola Tesla", "domain": "scientific", "description": "Serbian-American inventor and electrical engineer"},
    "leonardo_da_vinci": {"name": "Leonardo da Vinci", "domain": "scientific", "description": "Renaissance polymath, inventor, scientist, and visionary artist"},
    "archimedes": {"name": "Archimedes", "domain": "scientific", "description": "Ancient Greek mathematician, physicist, engineer, and inventor"},
    "marcus_aurelius": {"name": "Marcus Aurelius", "domain": "philosophical", "description": "Roman Emperor and Stoic philosopher"},
    "lao_tzu": {"name": "Lao Tzu", "domain": "philosophical", "description": "Ancient Chinese sage and founder of Taoism"},
    "socrates": {"name": "Socrates", "domain": "philosophical", "description": "Ancient Greek philosopher, father of Western philosophy"},
    "plato": {"name": "Plato", "domain": "philosophical", "description": "Student of Socrates, founded the Academy in Athens"},
    "aristotle": {"name": "Aristotle", "domain": "philosophical", "description": "Student of Plato, systematic approach to logic and ethics"},
    "sigmund_freud": {"name": "Sigmund Freud", "domain": "philosophical", "description": "Founder of psychoanalysis, explored human psychology"},
    "abraham_lincoln": {"name": "Abraham Lincoln", "domain": "leadership", "description": "16th President known for wisdom, leadership, and unity"},
    "chanakya": {"name": "Chanakya", "domain": "leadership", "description": "Ancient Indian strategist, economist, and political advisor"},
    "confucius": {"name": "Confucius", "domain": "philosophical", "description": "Chinese philosopher and educator emphasizing ethics and social harmony"},
    "benjamin_franklin": {"name": "Benjamin Franklin", "domain": "leadership", "description": "Founding Father, diplomat, inventor, and polymath"},
    "martin_luther_king_jr": {"name": "Martin Luther King Jr.", "domain": "leadership", "description": "Civil rights leader and advocate for social justice"},
    "george_washington": {"name": "George Washington", "domain": "leadership", "description": "First US President, military leader, and statesman"},
    "mahatma_gandhi": {"name": "Mahatma Gandhi", "domain": "leadership", "description": "Independence leader and advocate of non-violence"},
    "swami_vivekananda": {"name": "Swami Vivekananda", "domain": "spiritual", "description": "Spiritual teacher who introduced Vedanta to the West"},
    "william_shakespeare": {"name": "William Shakespeare", "domain": "literary", "description": "Greatest playwright and poet in English literature"},
    "rabindranath_tagore": {"name": "Rabindranath Tagore", "domain": "literary", "description": "Nobel Prize winner, poet, philosopher, and writer"},
}


def get_cors_headers() -> Dict[str, str]:
    """Get standard CORS headers for all responses"""
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://vimarsh.vedmishra.com",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


async def get_personality_list():
    """Get list of all available personalities (database-first approach)"""
    if database_personality_available and database_personality_service:
        try:
            return await database_personality_service.get_personality_list()
        except Exception as e:
            logger.warning(f"⚠️ Database personality service failed: {e}")

    return [
        {
            "id": pid,
            "name": config["name"],
            "description": config["description"],
            "domain": config["domain"],
            "active": True,
        }
        for pid, config in FALLBACK_PERSONALITIES.items()
    ]


async def get_personalities_by_domain(domain=None):
    """Get personalities filtered by domain (database-first approach)"""
    if database_personality_available and database_personality_service:
        try:
            return await database_personality_service.get_all_personalities(domain)
        except Exception as e:
            logger.warning(f"⚠️ Database personality service failed: {e}")

    if domain and domain != "all":
        return {k: v for k, v in FALLBACK_PERSONALITIES.items() if v["domain"] == domain}
    return FALLBACK_PERSONALITIES


async def get_personality_config(personality_id):
    """Get a specific personality configuration (database-first approach)"""
    if database_personality_available and database_personality_service:
        try:
            return await database_personality_service.get_personality_config(personality_id)
        except Exception as e:
            logger.warning(f"⚠️ Database personality config failed: {e}")

    if personality_models_available and PERSONALITY_CONFIGS:
        return PERSONALITY_CONFIGS.get(personality_id)
    return None


def extract_user_from_request(req) -> Optional[Dict[str, Any]]:
    """Extract authenticated user info from request Authorization header."""
    from auth import verify_token, get_user_from_token

    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.replace("Bearer ", "")
    return get_user_from_token(token)
